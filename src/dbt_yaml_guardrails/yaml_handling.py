"""dbt property YAML loading and shape normalization.

Behavior is specified in ``specs/yaml-handling.md``. Phases 1–3 (document-level)
implement :func:`load_property_yaml`; model extraction is Phase 4–5.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, TypeAlias

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

# ---------------------------------------------------------------------------
# Outcomes: one path produces at most one of these (per processing step).
# ---------------------------------------------------------------------------

SKIP_EMPTY_OR_WHITESPACE = "empty_or_whitespace"


@dataclass(frozen=True)
class ParseSkip:
    """No work for this path — not an error.

    Examples: empty/whitespace-only file; file lacks the hook's target section
    (e.g. no ``models:`` for model hooks). See ``specs/yaml-handling.md`` § Parsing
    and § dbt shape.
    """

    path: Path
    reason: str


@dataclass(frozen=True)
class ParseError:
    """This path cannot be processed — fatal for that file.

    Examples: invalid YAML, unsupported multi-document stream, bad top-level
    ``version:``, duplicate mapping keys. See ``specs/yaml-handling.md``.
    """

    path: Path
    message: str


@dataclass(frozen=True)
class ParseSuccess:
    """YAML loaded and document-level checks passed; ``root`` is the top-level mapping."""

    path: Path
    root: Mapping[str, Any]


ParseFileOutcome: TypeAlias = ParseSuccess | ParseSkip | ParseError


@dataclass(frozen=True)
class ModelEntriesResult:
    """Normalized model entries under ``models:`` (Phase 5)."""

    path: Path
    """Map ``name`` -> model object (mapping). Order is insertion order."""

    by_name: Mapping[str, Mapping[str, Any]]


ModelEntriesOutcome: TypeAlias = ModelEntriesResult | ParseError


# ---------------------------------------------------------------------------
# YAML loading (Phases 1–3: I/O + single document + root + version)
# ---------------------------------------------------------------------------


def _yaml_loader() -> YAML:
    y = YAML(typ="rt")
    y.allow_duplicate_keys = False
    return y


def _read_text(path: Path) -> ParseError | ParseSkip | str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return ParseError(path, f"Cannot read file: {exc}")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return ParseError(path, f"File is not valid UTF-8: {exc}")

    if text.startswith("\ufeff"):
        text = text[1:]

    if not text.strip():
        return ParseSkip(path, SKIP_EMPTY_OR_WHITESPACE)

    return text


def _parse_yaml_documents(text: str, path: Path) -> ParseFileOutcome:
    loader = _yaml_loader()
    try:
        documents = list(loader.load_all(StringIO(text)))
    except YAMLError as exc:
        return ParseError(path, f"Invalid YAML: {exc}")

    if len(documents) != 1:
        return ParseError(
            path,
            f"Expected exactly one YAML document, found {len(documents)}",
        )

    root = documents[0]
    if root is None:
        return ParseError(path, "YAML document is empty")

    if not isinstance(root, MutableMapping):
        return ParseError(
            path,
            f"Expected a mapping at the document root, got {type(root).__name__}",
        )

    verr = _validate_top_level_version(root, path)
    if verr is not None:
        return verr

    # Plain dict preserves key order for callers and tests.
    return ParseSuccess(path, dict(root))


def _validate_top_level_version(
    root: Mapping[str, Any],
    path: Path,
) -> ParseError | None:
    if "version" not in root:
        return None
    value = root["version"]
    if isinstance(value, int) and not isinstance(value, bool) and value == 2:
        return None
    if isinstance(value, str) and value == "2":
        return None
    return ParseError(
        path,
        f"Top-level version must be integer 2 or string '2', got {value!r}",
    )


def load_property_yaml(path: Path) -> ParseFileOutcome:
    """Read *path* and return a parsed top-level mapping or skip/error.

    Implements ``specs/yaml-handling.md`` § Parsing (UTF-8, BOM, empty skip,
    ``ruamel.yaml``, single document, duplicate keys, invalid YAML) and
    top-level ``version:`` validation. Does not inspect ``models:`` shape
    (see :func:`extract_model_entries`).
    """
    read = _read_text(path)
    if isinstance(read, (ParseSkip, ParseError)):
        return read
    return _parse_yaml_documents(read, path)


def extract_model_entries(success: ParseSuccess) -> ModelEntriesOutcome:
    """Normalize ``success.root`` ``models:`` into a map keyed by model ``name``.

    Callers must pass only a :class:`ParseSuccess` (after handling
    :class:`ParseSkip` / :class:`ParseError` from :func:`load_property_yaml`).
    See ``specs/yaml-handling.md`` § dbt shape.

    Not implemented (Phases 4–5).
    """
    raise NotImplementedError("Phase 4–5; see specs/yaml-handling.md § dbt shape")


def iter_model_entries(
    by_name: Mapping[str, Mapping[str, Any]],
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    """Yield ``(name, entry)`` in stable key order (sorted by *name*) for reporting.

    Hooks should use this when emitting violations so ordering matches
    ``yaml-handling.md`` § Errors (path, then resource name, …).
    """
    for name in sorted(by_name):
        yield name, by_name[name]
