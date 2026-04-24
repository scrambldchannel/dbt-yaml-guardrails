"""dbt property YAML loading and shape normalization.

Behavior is specified in ``specs/yaml-handling.md``. :func:`load_property_yaml` and :func:`load_dbt_project_yaml` cover
document-level parsing; :func:`extract_model_entries` and friends normalize
per-resource top-level lists (``models:``, ``sources:``, ``catalogs:``, …).
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
SKIP_NO_SOURCES_SECTION = "no_sources_section"
SKIP_NO_CATALOGS_SECTION = "no_catalogs_section"


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


@dataclass(frozen=True)
class SourceEntriesSkip:
    """No ``sources:`` section — not an error (hook should ignore the file)."""

    path: Path
    reason: str


@dataclass(frozen=True)
class SourceEntriesResult:
    """Normalized source entries under ``sources:`` (each list item; keyed by ``name``)."""

    path: Path
    by_name: Mapping[str, Mapping[str, Any]]


SourceEntriesOutcome: TypeAlias = SourceEntriesResult | SourceEntriesSkip | ParseError


@dataclass(frozen=True)
class CatalogEntriesSkip:
    """No ``catalogs:`` section — not an error (hook should ignore the file)."""

    path: Path
    reason: str


@dataclass(frozen=True)
class CatalogEntriesResult:
    """Normalized catalog entries under ``catalogs:`` (each list item; keyed by ``name``)."""

    path: Path
    by_name: Mapping[str, Mapping[str, Any]]


CatalogEntriesOutcome: TypeAlias = (
    CatalogEntriesResult | CatalogEntriesSkip | ParseError
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


def _parse_dbt_project_documents(text: str, path: Path) -> ParseFileOutcome:
    """Load one YAML document; root must be a mapping. No property-``version: 2`` rule."""
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
    """Read a dbt property YAML file and return a parse outcome.

    Implements ``specs/yaml-handling.md`` § Parsing (UTF-8, BOM, empty skip,
    ``ruamel.yaml``, single document, duplicate keys, invalid YAML) and
    top-level ``version:`` validation. Does not inspect resource list shape
    (``models:``, ``sources:``, ``macros:``, …); use the ``extract_*_entries`` functions.

    Args:
        path: Path to the YAML file.

    Returns:
        :class:`ParseSuccess` with the document root mapping, :class:`ParseSkip`
        for empty/whitespace-only input, or :class:`ParseError` on I/O or
        parse failure.
    """
    read = _read_text(path)
    if isinstance(read, (ParseSkip, ParseError)):
        return read
    return _parse_yaml_documents(read, path)


def load_dbt_project_yaml(path: Path) -> ParseFileOutcome:
    """Read a ``dbt_project.yml`` and return a parse outcome.

    Same encoding, BOM, empty skip, single document, and duplicate key rules as
    :func:`load_property_yaml`, but does **not** require top-level
    ``version: 2`` (the project ``version`` key is a separate config; see
    ``specs/yaml-handling.md`` § dbt project file).

    Args:
        path: Path to the YAML file.

    Returns:
        :class:`ParseSuccess` with the document root, :class:`ParseSkip` for
        empty input, or :class:`ParseError` on failure.
    """
    read = _read_text(path)
    if isinstance(read, (ParseSkip, ParseError)):
        return read
    return _parse_dbt_project_documents(read, path)


def extract_model_entries(success: ParseSuccess) -> ModelEntriesOutcome:
    """Normalize ``success.root["models"]`` into a map keyed by model ``name``.

    If there is no ``models`` key, returns :class:`ModelEntriesSkip` (per
    ``specs/yaml-handling.md`` — file ignored for model hooks). Otherwise
    ``models`` must be a list of mappings, each with a non-empty string ``name``;
    duplicate ``name`` values are an error.

    Args:
        success: Result of :func:`load_property_yaml` after discarding
            :class:`ParseSkip` / :class:`ParseError`.

    Returns:
        :class:`ModelEntriesResult` with ``by_name``, :class:`ModelEntriesSkip`
        if there is no ``models:`` section, or :class:`ParseError` on bad shape.
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
    """Yield ``(name, entry)`` in stable key order (sorted by name) for reporting.

    Hooks should use this when emitting violations so ordering matches
    ``yaml-handling.md`` § Errors (path, then resource name, …).

    Args:
        by_name: Map from model name to model entry dict.

    Yields:
        ``(name, entry)`` tuples in sorted name order.
    """
    for name in sorted(by_name):
        yield name, by_name[name]


def extract_macro_entries(success: ParseSuccess) -> MacroEntriesOutcome:
    """Normalize ``success.root["macros"]`` into a map keyed by macro ``name``.

    If there is no ``macros`` key, returns :class:`MacroEntriesSkip`. Otherwise
    ``macros`` must be a list of mappings, each with a non-empty string ``name``;
    duplicate ``name`` values are an error.

    Args:
        success: Result of :func:`load_property_yaml` after discarding
            :class:`ParseSkip` / :class:`ParseError`.

    Returns:
        :class:`MacroEntriesResult` with ``by_name``, :class:`MacroEntriesSkip`
        if there is no ``macros:`` section, or :class:`ParseError` on bad shape.
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
    """Yield ``(name, entry)`` in stable key order (sorted by name) for reporting.

    Args:
        by_name: Map from macro name to macro entry dict.

    Yields:
        ``(name, entry)`` tuples in sorted name order.
    """
    for name in sorted(by_name):
        yield name, by_name[name]


def _extract_named_list_by_name(
    success: ParseSuccess,
    *,
    section_key: str,
    label: str,
    duplicate_name_kind: str | None = None,
) -> ParseError | Literal["skip"] | dict[str, dict[str, Any]]:
    """Parse ``root[section_key]`` as a list of mappings with a string ``name``.

    Args:
        success: Loaded YAML document.
        section_key: Top-level key (e.g. ``\"seeds\"``).
        label: Human-readable plural for error messages (e.g. ``\"seeds\"``).
        duplicate_name_kind: Word used in the duplicate-name error (e.g. ``\"source\"``
            for ``sources``; default is *label* with the last character removed, which
            works for *seeds*, *snapshots*, *exposures* but not *sources*).

    Returns:
        ``\"skip\"`` if *section_key* is absent, a :class:`ParseError` on bad
        shape, or a ``by_name`` dict on success.
    """
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
            kind = (
                duplicate_name_kind if duplicate_name_kind is not None else label[:-1]
            )
            return ParseError(path, f"Duplicate {kind} name {name!r}")
        by_name[name] = dict(item)

    return by_name


def extract_seed_entries(success: ParseSuccess) -> SeedEntriesOutcome:
    """Normalize ``success.root["seeds"]`` into a map keyed by seed ``name``.

    Args:
        success: Result of :func:`load_property_yaml` after discarding
            :class:`ParseSkip` / :class:`ParseError`.

    Returns:
        :class:`SeedEntriesResult`, :class:`SeedEntriesSkip` if there is no
        ``seeds:`` section, or :class:`ParseError` on bad shape.
    """
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
    """Yield ``(name, entry)`` in sorted name order (see :func:`iter_model_entries`).

    Args:
        by_name: Map from seed name to seed entry dict.

    Yields:
        ``(name, entry)`` tuples in sorted name order.
    """
    for name in sorted(by_name):
        yield name, by_name[name]


def extract_snapshot_entries(success: ParseSuccess) -> SnapshotEntriesOutcome:
    """Normalize ``success.root["snapshots"]`` into a map keyed by snapshot ``name``.

    Args:
        success: Result of :func:`load_property_yaml` after discarding
            :class:`ParseSkip` / :class:`ParseError`.

    Returns:
        :class:`SnapshotEntriesResult`, :class:`SnapshotEntriesSkip` if there
        is no ``snapshots:`` section, or :class:`ParseError` on bad shape.
    """
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
    """Yield ``(name, entry)`` in sorted name order (see :func:`iter_model_entries`).

    Args:
        by_name: Map from snapshot name to snapshot entry dict.

    Yields:
        ``(name, entry)`` tuples in sorted name order.
    """
    for name in sorted(by_name):
        yield name, by_name[name]


def extract_exposure_entries(success: ParseSuccess) -> ExposureEntriesOutcome:
    """Normalize ``success.root["exposures"]`` into a map keyed by exposure ``name``.

    Args:
        success: Result of :func:`load_property_yaml` after discarding
            :class:`ParseSkip` / :class:`ParseError`.

    Returns:
        :class:`ExposureEntriesResult`, :class:`ExposureEntriesSkip` if there
        is no ``exposures:`` section, or :class:`ParseError` on bad shape.
    """
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
    """Yield ``(name, entry)`` in sorted name order (see :func:`iter_model_entries`).

    Args:
        by_name: Map from exposure name to exposure entry dict.

    Yields:
        ``(name, entry)`` tuples in sorted name order.
    """
    for name in sorted(by_name):
        yield name, by_name[name]


def extract_source_entries(success: ParseSuccess) -> SourceEntriesOutcome:
    """Normalize ``success.root["sources"]`` into a map keyed by source ``name``.

    If there is no ``sources`` key, returns :class:`SourceEntriesSkip`. Otherwise
    ``sources`` must be a list of mappings, each with a non-empty string ``name``;
    duplicate ``name`` values are an error. Nested ``tables:`` and other keys are
    left on each entry as-is; only the list shape and per-entry ``name`` are
    validated here.

    Args:
        success: Result of :func:`load_property_yaml` after discarding
            :class:`ParseSkip` / :class:`ParseError`.

    Returns:
        :class:`SourceEntriesResult`, :class:`SourceEntriesSkip` if there is no
        ``sources:`` section, or :class:`ParseError` on bad shape.
    """
    r = _extract_named_list_by_name(
        success,
        section_key="sources",
        label="sources",
        duplicate_name_kind="source",
    )
    if r == "skip":
        return SourceEntriesSkip(success.path, SKIP_NO_SOURCES_SECTION)
    if isinstance(r, ParseError):
        return r
    return SourceEntriesResult(success.path, r)


def iter_source_entries(
    by_name: Mapping[str, Mapping[str, Any]],
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    """Yield ``(name, entry)`` in sorted name order (see :func:`iter_model_entries`).

    Args:
        by_name: Map from source name to source entry dict.

    Yields:
        ``(name, entry)`` tuples in sorted name order.
    """
    for name in sorted(by_name):
        yield name, by_name[name]


def extract_catalog_entries(success: ParseSuccess) -> CatalogEntriesOutcome:
    """Normalize ``success.root["catalogs"]`` into a map keyed by catalog ``name``.

    If there is no ``catalogs`` key, returns :class:`CatalogEntriesSkip`. Otherwise
    ``catalogs`` must be a list of mappings, each with a non-empty string ``name``;
    duplicate ``name`` values are an error. Nested ``write_integrations:`` and
    other keys are left on each entry as-is; only the list shape and per-entry
    ``name`` are validated here.

    Args:
        success: Result of :func:`load_property_yaml` after discarding
            :class:`ParseSkip` / :class:`ParseError`.

    Returns:
        :class:`CatalogEntriesResult`, :class:`CatalogEntriesSkip` if there is no
        ``catalogs:`` section, or :class:`ParseError` on bad shape.
    """
    r = _extract_named_list_by_name(
        success,
        section_key="catalogs",
        label="catalogs",
    )
    if r == "skip":
        return CatalogEntriesSkip(success.path, SKIP_NO_CATALOGS_SECTION)
    if isinstance(r, ParseError):
        return r
    return CatalogEntriesResult(success.path, r)


def iter_catalog_entries(
    by_name: Mapping[str, Mapping[str, Any]],
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    """Yield ``(name, entry)`` in sorted name order (see :func:`iter_model_entries`).

    Args:
        by_name: Map from catalog name to catalog entry dict.

    Yields:
        ``(name, entry)`` tuples in sorted name order.
    """
    for name in sorted(by_name):
        yield name, by_name[name]
