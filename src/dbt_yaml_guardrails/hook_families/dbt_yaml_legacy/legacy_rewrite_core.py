"""Round-trip property YAML and rewrite legacy ``tests`` to ``data_tests``.

``specs/hook-families/dbt-yaml-legacy.md`` (v1).
"""

from __future__ import annotations

from collections.abc import MutableMapping
from io import StringIO
from pathlib import Path
from typing import Any, Literal, Union

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError

from dbt_yaml_guardrails.yaml_handling import (
    ParseError,
    ParseSkip,
    _read_text,
    _validate_top_level_version,
    _yaml_loader,
)

# Resource list keys from ``dbt-yaml-legacy.md`` v1; ``sources`` has no column rewrites in v1.
_RESOURCE_LIST_KEYS: tuple[str, ...] = (
    "models",
    "seeds",
    "snapshots",
    "macros",
    "exposures",
    "sources",
)

# Column-level ``tests`` rewrites: model, seed, snapshot only.
_COLUMN_KEYS: frozenset[str] = frozenset({"models", "seeds", "snapshots"})


def load_property_yaml_roundtrip(path: Path) -> Union[ParseError, ParseSkip, Any]:
    """Load one property YAML document as a round-trip object graph (``CommentedMap`` root).

    Same I/O, single-document, root-mapping, and ``version:`` rules as
    :func:`dbt_yaml_guardrails.yaml_handling.load_property_yaml`, but the root is **not** converted to a
    plain :class:`dict` so keys and comments can be written back.
    """
    read = _read_text(path)
    if isinstance(read, (ParseSkip, ParseError)):
        return read
    text = read
    assert isinstance(text, str)
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
    return root


def _rename_tests_key(
    m: MutableMapping[str, Any],
) -> Union[Literal["renamed", "unchanged", "conflict"]]:
    """Rename key ``tests`` to ``data_tests`` in a single mapping, preserving key order.

    If both ``tests`` and ``data_tests`` are present, the mapping is not modified
    and ``conflict`` is returned.
    """
    if "tests" not in m:
        return "unchanged"
    if "data_tests" in m:
        return "conflict"
    if isinstance(m, CommentedMap):
        pos = list(m.keys()).index("tests")
        value = m.pop("tests")
        m.insert(pos, "data_tests", value)
    else:
        new_keys: list[tuple[str, Any]] = []
        for k, v in m.items():
            nk = "data_tests" if k == "tests" else k
            new_keys.append((nk, v))
        m.clear()
        for nk, v in new_keys:
            m[nk] = v
    return "renamed"


def _context_label(section: str, item: MutableMapping[str, Any]) -> str:
    name = item.get("name")
    if isinstance(name, str) and name:
        return f"{section} '{name}'"
    return section


def rewrite_tests_to_data_tests_v1(
    root: Any,
    path: Path,
) -> tuple[int, list[str]]:
    """Apply v1 rewrites. Returns ``(rename_count, conflict_messages)``."""
    renames = 0
    conflicts: list[str] = []
    if not isinstance(root, MutableMapping):
        return 0, []

    path_s = str(path).replace("\\", "/")

    for section in _RESOURCE_LIST_KEYS:
        if section not in root:
            continue
        block = root[section]
        if block is None:
            continue
        if not isinstance(block, list):
            continue
        for item in block:
            if not isinstance(item, MutableMapping):
                continue
            ctx = _context_label(section, item)
            res = _rename_tests_key(item)
            if res == "renamed":
                renames += 1
            elif res == "conflict":
                conflicts.append(
                    f"{path_s}: {ctx}: 'tests' and 'data_tests' both present, skipping this entry"
                )
            if section in _COLUMN_KEYS:
                cols = item.get("columns")
                if not isinstance(cols, list):
                    continue
                for i, col in enumerate(cols):
                    if not isinstance(col, MutableMapping):
                        continue
                    cres = _rename_tests_key(col)
                    if cres == "renamed":
                        renames += 1
                    elif cres == "conflict":
                        cname = col.get("name")
                        ctag = (
                            f"column {cname!r}"
                            if isinstance(cname, str)
                            else f"column at index {i}"
                        )
                        conflicts.append(
                            f"{path_s}: {ctx}: {ctag}: 'tests' and 'data_tests' both present, "
                            f"skipping this column"
                        )
    return renames, conflicts


def write_roundtrip(path: Path, root: Any) -> str | None:
    """Write *root* to *path* with the round-trip dumper. Returns an error string or None."""
    try:
        y = YAML(typ="rt")
        y.allow_duplicate_keys = False
        # Match common dbt property YAML: indent block sequences under a key (e.g. ``models:\n  - name:``)
        # instead of ruamel’s default (``models:\n- name:``), which looks like "broken" indentation.
        y.indent(mapping=2, sequence=4, offset=2)
        with path.open("w", encoding="utf-8", newline="") as fh:
            y.dump(root, fh)
    except OSError as exc:
        return f"Cannot write file: {exc}"
    return None
