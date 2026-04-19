"""dbt property YAML loading and shape normalization.

Behavior is specified in ``specs/yaml-handling.md``. :func:`load_property_yaml`
covers document-level parsing; :func:`extract_model_entries` normalizes ``models:``.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Literal, TypeAlias

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

# ---------------------------------------------------------------------------
# Outcomes: one path produces at most one of these (per processing step).
# ---------------------------------------------------------------------------

SKIP_EMPTY_OR_WHITESPACE = "empty_or_whitespace"
SKIP_NO_MODELS_SECTION = "no_models_section"
SKIP_NO_MACROS_SECTION = "no_macros_section"
SKIP_NO_SEEDS_SECTION = "no_seeds_section"
SKIP_NO_SNAPSHOTS_SECTION = "no_snapshots_section"
SKIP_NO_EXPOSURES_SECTION = "no_exposures_section"


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
class ModelEntriesSkip:
    """No ``models:`` section — not an error (hook should ignore the file)."""

    path: Path
    reason: str


@dataclass(frozen=True)
class ModelEntriesResult:
    """Normalized model entries under ``models:``."""

    path: Path
    """Map ``name`` -> model object (mapping). Order is first occurrence in the list."""

    by_name: Mapping[str, Mapping[str, Any]]


ModelEntriesOutcome: TypeAlias = ModelEntriesResult | ModelEntriesSkip | ParseError


@dataclass(frozen=True)
class MacroEntriesSkip:
    """No ``macros:`` section — not an error (hook should ignore the file)."""

    path: Path
    reason: str


@dataclass(frozen=True)
class MacroEntriesResult:
    """Normalized macro entries under ``macros:``."""

    path: Path
    """Map ``name`` -> macro object (mapping). Order is first occurrence in the list."""

    by_name: Mapping[str, Mapping[str, Any]]


MacroEntriesOutcome: TypeAlias = MacroEntriesResult | MacroEntriesSkip | ParseError


@dataclass(frozen=True)
class SeedEntriesSkip:
    """No ``seeds:`` section — not an error (hook should ignore the file)."""

    path: Path
    reason: str


@dataclass(frozen=True)
class SeedEntriesResult:
    """Normalized seed entries under ``seeds:``."""

    path: Path
    by_name: Mapping[str, Mapping[str, Any]]


SeedEntriesOutcome: TypeAlias = SeedEntriesResult | SeedEntriesSkip | ParseError


@dataclass(frozen=True)
class SnapshotEntriesSkip:
    """No ``snapshots:`` section — not an error (hook should ignore the file)."""

    path: Path
    reason: str


@dataclass(frozen=True)
class SnapshotEntriesResult:
    """Normalized snapshot entries under ``snapshots:``."""

    path: Path
    by_name: Mapping[str, Mapping[str, Any]]


SnapshotEntriesOutcome: TypeAlias = (
    SnapshotEntriesResult | SnapshotEntriesSkip | ParseError
)


@dataclass(frozen=True)
class ExposureEntriesSkip:
    """No ``exposures:`` section — not an error (hook should ignore the file)."""

    path: Path
    reason: str


@dataclass(frozen=True)
class ExposureEntriesResult:
    """Normalized exposure entries under ``exposures:``."""

    path: Path
    by_name: Mapping[str, Mapping[str, Any]]


ExposureEntriesOutcome: TypeAlias = (
    ExposureEntriesResult | ExposureEntriesSkip | ParseError
)


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
    top-level ``version:`` validation. Does not inspect ``models:`` / ``macros:`` shape
    (see :func:`extract_model_entries`, :func:`extract_macro_entries`).
    """
    read = _read_text(path)
    if isinstance(read, (ParseSkip, ParseError)):
        return read
    return _parse_yaml_documents(read, path)


def extract_model_entries(success: ParseSuccess) -> ModelEntriesOutcome:
    """Normalize ``success.root`` ``models:`` into a map keyed by model ``name``.

    If there is no ``models`` key, returns :class:`ModelEntriesSkip` (per
    ``specs/yaml-handling.md`` — file ignored for model hooks). Otherwise
    ``models`` must be a list of mappings, each with a non-empty string ``name``;
    duplicate ``name`` values are an error.

    Callers must pass only a :class:`ParseSuccess` (after handling
    :class:`ParseSkip` / :class:`ParseError` from :func:`load_property_yaml`).
    """
    path = success.path
    root = success.root

    if "models" not in root:
        return ModelEntriesSkip(path, SKIP_NO_MODELS_SECTION)

    raw_models = root["models"]
    if raw_models is None:
        return ParseError(path, "models must be a list, not null")
    if not isinstance(raw_models, list):
        return ParseError(
            path,
            f"models must be a list, got {type(raw_models).__name__}",
        )

    by_name: dict[str, dict[str, Any]] = {}
    for idx, item in enumerate(raw_models):
        if not isinstance(item, MutableMapping):
            return ParseError(
                path,
                f"models[{idx}] must be a mapping, got {type(item).__name__}",
            )
        if "name" not in item:
            return ParseError(path, f"models[{idx}] is missing required key 'name'")
        raw_name = item["name"]
        if not isinstance(raw_name, str) or not raw_name.strip():
            return ParseError(
                path,
                f"models[{idx}].name must be a non-empty string, got {raw_name!r}",
            )
        name = raw_name.strip()
        if name in by_name:
            return ParseError(path, f"Duplicate model name {name!r}")
        by_name[name] = dict(item)

    return ModelEntriesResult(path, by_name)


def iter_model_entries(
    by_name: Mapping[str, Mapping[str, Any]],
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    """Yield ``(name, entry)`` in stable key order (sorted by *name*) for reporting.

    Hooks should use this when emitting violations so ordering matches
    ``yaml-handling.md`` § Errors (path, then resource name, …).
    """
    for name in sorted(by_name):
        yield name, by_name[name]


def extract_macro_entries(success: ParseSuccess) -> MacroEntriesOutcome:
    """Normalize ``success.root`` ``macros:`` into a map keyed by macro ``name``.

    If there is no ``macros`` key, returns :class:`MacroEntriesSkip`. Otherwise
    ``macros`` must be a list of mappings, each with a non-empty string ``name``;
    duplicate ``name`` values are an error.

    Callers must pass only a :class:`ParseSuccess` (after handling
    :class:`ParseSkip` / :class:`ParseError` from :func:`load_property_yaml`).
    """
    path = success.path
    root = success.root

    if "macros" not in root:
        return MacroEntriesSkip(path, SKIP_NO_MACROS_SECTION)

    raw = root["macros"]
    if raw is None:
        return ParseError(path, "macros must be a list, not null")
    if not isinstance(raw, list):
        return ParseError(
            path,
            f"macros must be a list, got {type(raw).__name__}",
        )

    by_name: dict[str, dict[str, Any]] = {}
    for idx, item in enumerate(raw):
        if not isinstance(item, MutableMapping):
            return ParseError(
                path,
                f"macros[{idx}] must be a mapping, got {type(item).__name__}",
            )
        if "name" not in item:
            return ParseError(path, f"macros[{idx}] is missing required key 'name'")
        raw_name = item["name"]
        if not isinstance(raw_name, str) or not raw_name.strip():
            return ParseError(
                path,
                f"macros[{idx}].name must be a non-empty string, got {raw_name!r}",
            )
        name = raw_name.strip()
        if name in by_name:
            return ParseError(path, f"Duplicate macro name {name!r}")
        by_name[name] = dict(item)

    return MacroEntriesResult(path, by_name)


def iter_macro_entries(
    by_name: Mapping[str, Mapping[str, Any]],
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    """Yield ``(name, entry)`` in stable key order (sorted by *name*) for reporting."""
    for name in sorted(by_name):
        yield name, by_name[name]


def _extract_named_list_by_name(
    success: ParseSuccess,
    *,
    section_key: str,
    label: str,
) -> ParseError | Literal["skip"] | dict[str, dict[str, Any]]:
    """Parse ``root[section_key]`` as a list of mappings with ``name``; return ``by_name`` or outcome."""
    path = success.path
    root = success.root
    if section_key not in root:
        return "skip"

    raw = root[section_key]
    if raw is None:
        return ParseError(path, f"{section_key} must be a list, not null")
    if not isinstance(raw, list):
        return ParseError(
            path,
            f"{section_key} must be a list, got {type(raw).__name__}",
        )

    by_name: dict[str, dict[str, Any]] = {}
    for idx, item in enumerate(raw):
        if not isinstance(item, MutableMapping):
            return ParseError(
                path,
                f"{label}[{idx}] must be a mapping, got {type(item).__name__}",
            )
        if "name" not in item:
            return ParseError(path, f"{label}[{idx}] is missing required key 'name'")
        raw_name = item["name"]
        if not isinstance(raw_name, str) or not raw_name.strip():
            return ParseError(
                path,
                f"{label}[{idx}].name must be a non-empty string, got {raw_name!r}",
            )
        name = raw_name.strip()
        if name in by_name:
            return ParseError(path, f"Duplicate {label[:-1]} name {name!r}")
        by_name[name] = dict(item)

    return by_name


def extract_seed_entries(success: ParseSuccess) -> SeedEntriesOutcome:
    """Normalize ``success.root`` ``seeds:`` into a map keyed by seed ``name``."""
    r = _extract_named_list_by_name(
        success,
        section_key="seeds",
        label="seeds",
    )
    if r == "skip":
        return SeedEntriesSkip(success.path, SKIP_NO_SEEDS_SECTION)
    if isinstance(r, ParseError):
        return r
    return SeedEntriesResult(success.path, r)


def iter_seed_entries(
    by_name: Mapping[str, Mapping[str, Any]],
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    for name in sorted(by_name):
        yield name, by_name[name]


def extract_snapshot_entries(success: ParseSuccess) -> SnapshotEntriesOutcome:
    """Normalize ``success.root`` ``snapshots:`` into a map keyed by snapshot ``name``."""
    r = _extract_named_list_by_name(
        success,
        section_key="snapshots",
        label="snapshots",
    )
    if r == "skip":
        return SnapshotEntriesSkip(success.path, SKIP_NO_SNAPSHOTS_SECTION)
    if isinstance(r, ParseError):
        return r
    return SnapshotEntriesResult(success.path, r)


def iter_snapshot_entries(
    by_name: Mapping[str, Mapping[str, Any]],
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    for name in sorted(by_name):
        yield name, by_name[name]


def extract_exposure_entries(success: ParseSuccess) -> ExposureEntriesOutcome:
    """Normalize ``success.root`` ``exposures:`` into a map keyed by exposure ``name``."""
    r = _extract_named_list_by_name(
        success,
        section_key="exposures",
        label="exposures",
    )
    if r == "skip":
        return ExposureEntriesSkip(success.path, SKIP_NO_EXPOSURES_SECTION)
    if isinstance(r, ParseError):
        return r
    return ExposureEntriesResult(success.path, r)


def iter_exposure_entries(
    by_name: Mapping[str, Mapping[str, Any]],
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    for name in sorted(by_name):
        yield name, by_name[name]
