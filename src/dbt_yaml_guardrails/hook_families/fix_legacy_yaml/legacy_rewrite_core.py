"""Round-trip property YAML and rewrite legacy property keys.

``specs/hook-families/fix-legacy-yaml.md`` — v1 ``tests`` → ``data_tests``; v2 top-level
``meta`` / ``tags`` → ``config``.
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

# Resource list keys (resource entries) for rewrites. Nested ``sources`` → ``tables`` / ``columns``
# ``tests`` → ``data_tests`` runs only when integration passes the ``check_source_tables`` /
# ``check_source_table_columns`` flags (see ``rewrite_tests_to_data_tests_v1``).
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


def _source_table_label(trow: MutableMapping[str, Any], index: int) -> str:
    tname = trow.get("name")
    if isinstance(tname, str) and tname:
        return f"table '{tname}'"
    return f"table at index {index}"


def rewrite_tests_to_data_tests_v1(
    root: Any,
    path: Path,
    *,
    check_source_tables: bool = False,
    check_source_table_columns: bool = False,
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
            if section == "sources" and check_source_tables:
                tables = item.get("tables")
                if not isinstance(tables, list):
                    continue
                for ti, trow in enumerate(tables):
                    if not isinstance(trow, MutableMapping):
                        continue
                    tlab = _source_table_label(trow, ti)
                    tres = _rename_tests_key(trow)
                    if tres == "renamed":
                        renames += 1
                    elif tres == "conflict":
                        conflicts.append(
                            f"{path_s}: {ctx}: {tlab}: 'tests' and 'data_tests' both present, "
                            f"skipping this entry"
                        )
                    if not check_source_table_columns:
                        continue
                    tcols = trow.get("columns")
                    if not isinstance(tcols, list):
                        continue
                    for ci, col in enumerate(tcols):
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
                                else f"column at index {ci}"
                            )
                            conflicts.append(
                                f"{path_s}: {ctx}: {tlab}: {ctag}: 'tests' and 'data_tests' both present, "
                                f"skipping this column"
                            )
    return renames, conflicts


def _mapping_insert(
    m: MutableMapping[str, Any],
    key: str,
    value: Any,
) -> None:
    """Set *key* on *m*; use ``CommentedMap.insert`` at end when available."""
    if isinstance(m, CommentedMap) and key not in m:
        m.insert(len(m), key, value)  # type: ignore[call-arg]
    else:
        m[key] = value


def _conflicts_for_top_level_meta_and_tags(
    item: MutableMapping[str, Any],
    path_s: str,
    ctx: str,
) -> list[str]:
    """Read-only: whether moving top-level ``meta`` / ``tags`` would fail (no mutation)."""
    to_move: list[str] = [k for k in ("meta", "tags") if k in item]
    if not to_move:
        return []
    if "config" in item:
        raw_cfg = item["config"]
        if raw_cfg is None or not isinstance(raw_cfg, MutableMapping):
            return [
                f"{path_s}: {ctx}: `config` is not a mapping, cannot move top-level `meta`/`tags`"
            ]
        cfg = raw_cfg
        for key in to_move:
            if key in cfg:
                return [
                    f"{path_s}: {ctx}: top-level '{key}' and `config.{key}` both present, "
                    f"skipping this entry"
                ]
    return []


def _apply_top_level_meta_and_tags_for_entry(
    item: MutableMapping[str, Any],
) -> int:
    """Move top-level ``meta`` / ``tags`` into ``config``. Call only if preflight is clean for *item*.

    Returns change count.
    """
    to_move: list[str] = [k for k in ("meta", "tags") if k in item]
    if not to_move:
        return 0
    if "config" in item:
        raw_cfg = item["config"]
        if raw_cfg is None or not isinstance(raw_cfg, MutableMapping):
            return 0
        cfg: MutableMapping[str, Any] = raw_cfg
        ch = 0
        for key in to_move:
            value = item.pop(key)
            _mapping_insert(cfg, key, value)
            ch += 1
        return ch

    old_keys = list(item.keys()) if isinstance(item, CommentedMap) else list(item)
    ins_at = min(old_keys.index(k) for k in to_move)
    to_pop = sorted(
        to_move,
        key=lambda k: -old_keys.index(k),
    )
    vals: dict[str, Any] = {}
    for k in to_pop:
        vals[k] = item.pop(k)
    new_cfg = CommentedMap()
    for k in ("meta", "tags"):
        if k in vals:
            new_cfg[k] = vals[k]
    if isinstance(item, CommentedMap):
        item.insert(ins_at, "config", new_cfg)  # type: ignore[call-arg]
    else:
        item["config"] = new_cfg
    return len(to_move)


def rewrite_top_level_meta_tags_to_config(
    root: Any,
    path: Path,
) -> tuple[int, list[str]]:
    """Move top-level resource ``meta`` / ``tags`` into ``config`` (see fix-legacy-yaml v2)."""
    if not isinstance(root, MutableMapping):
        return 0, []

    path_s = str(path).replace("\\", "/")
    all_conflicts: list[str] = []
    to_apply: list[MutableMapping[str, Any]] = []

    for section in _RESOURCE_LIST_KEYS:
        if section not in root:
            continue
        block = root[section]
        if block is None or not isinstance(block, list):
            continue
        for item in block:
            if not isinstance(item, MutableMapping):
                continue
            ctx = _context_label(section, item)
            c = _conflicts_for_top_level_meta_and_tags(item, path_s, ctx)
            if c:
                all_conflicts.extend(c)
            else:
                if any(k in item for k in ("meta", "tags")):
                    to_apply.append(item)
    if all_conflicts:
        return 0, all_conflicts

    renames = 0
    for item in to_apply:
        renames += _apply_top_level_meta_and_tags_for_entry(item)
    return renames, []


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
