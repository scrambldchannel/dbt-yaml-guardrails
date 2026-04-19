"""dbt property YAML loading and shape normalization.

Behavior is specified in ``specs/yaml-handling.md``. Phases 1+ implement
``load_property_yaml`` and related helpers; this module defines the public
contract (types and entry points) for future hook CLIs.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

# ---------------------------------------------------------------------------
# Outcomes: one path produces at most one of these (per processing step).
# ---------------------------------------------------------------------------


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
# Public API (implementations added in later phases)
# ---------------------------------------------------------------------------


def load_property_yaml(path: Path) -> ParseFileOutcome:
    """Read *path*, parse YAML with ``ruamel.yaml``, apply rules in ``yaml-handling.md``.

    Covers: UTF-8 + BOM, empty skip, single document, duplicate keys, root mapping,
    optional top-level ``version:`` (see spec § Parsing).

    Not implemented in Phase 0.
    """
    raise NotImplementedError("Phase 1+; see specs/yaml-handling.md § Parsing")


def extract_model_entries(success: ParseSuccess) -> ModelEntriesOutcome:
    """Normalize ``success.root`` ``models:`` into a map keyed by model ``name``.

    Callers must pass only a :class:`ParseSuccess` (after handling
    :class:`ParseSkip` / :class:`ParseError` from :func:`load_property_yaml`).
    See ``specs/yaml-handling.md`` § dbt shape.

    Not implemented in Phase 0.
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
