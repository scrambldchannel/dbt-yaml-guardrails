# Hook family: `dbt-yaml-legacy` (mechanical rewrites for deprecated YAML)

**Purpose:** A **separate** tool from the **validation** families (`*-allowed-keys`, `*-allowed-config-keys`, …). It **rewrites** dbt **property YAML** to replace patterns that the validator flags as **legacy** (see **`resource-keys.md`** § **Legacy / deprecated** and the `*_LEGACY_KEY_MESSAGES` maps in **`resource_keys.py`**) with the **supported** spelling or location.

**Status:** **`dbt-yaml-legacy`** is **shipped** as a single console script and pre-commit hook (**`id: dbt-yaml-legacy`**). **v1** renames **`tests` → `data_tests`** only, at the declaration sites in **§ v1** below. Future transforms (`tags` / `meta`) are not implemented yet.

Umbrella packaging and the family list live in **[`../hooks.md`](../hooks.md)**.

---

## Design principles

+ **Complement validators, do not replace them.** The **`dbt-yaml-legacy`** process applies **mechanical, syntax-level** rewrites. Teams still use **`model-allowed-keys`**, **`seed-allowed-keys`**, and related hooks to enforce allowlists, **`--required`**, and policy.
+ **Deterministic and idempotent** where possible: running the fixer twice on the same file should not change the file a second time (or should be a no-op after the first run).
+ **Property YAML only in v1** (same file scope and loader expectations as **[`yaml-handling.md`](../yaml-handling.md)** § **dbt property YAML** and **`load_property_yaml`**). Do **not** target **`dbt_project.yml`**, **`catalogs.yml`**, or manifest-only files in the first version unless a later spec explicitly extends scope.
+ **Round-trip** should preserve **comments and formatting** as far as a mature YAML library allows. The implementation **SHOULD** use **ruamel.yaml** (already a project dependency) for any load → edit → write cycle; document the exact APIs in this spec or **`project-spec.md`** when the feature lands.

### Key order (non-negotiable unless explicitly excepted)

Any implementation that **edits and writes** property YAML for this family **MUST** preserve the **document order of keys** in every mapping the tool mutates, and **SHOULD** preserve key order (and, where the library allows it, the overall structure) for the rest of the file. **Siblings must not be re-sorted** for readability, normalization, or “canonical” ordering.

- A **rename** (e.g. v1: **`tests` → `data_tests`**) must **not** change the key’s **rank** among its siblings: the new key name replaces the old one **in place**, leaving all other key order unchanged.
- **v1** defines **no** case where key order is intentionally changed; a future spec version that needs reordering **must** call it out in its own **Exceptions** subsection.

Rationale: **ruamel.yaml** is chosen in part so ordered mappings round-trip; violating key order would churn diffs and break team conventions. If a write path ever uses a different stack, it still **MUST** meet the same key-order contract.

---

## v1: `tests` → `data_tests` (only)

**Goal:** Rename the legacy key **`tests`** to **`data_tests`** only at the declaration sites below, matching dbt’s property docs and the messages emitted by **`*-allowed-keys`** and column checks (see **`resource_keys.py`** / **`resource-keys.md`** and the `*_LEGACY_KEY_MESSAGES` / `*_COLUMN_LEGACY_KEY_MESSAGES` entries for **`tests`**).

**Target key spelling (required):** The output key is always exactly **`data_tests`**: all **lowercase** ASCII, one underscore between `data` and `tests` (not camelCase `dataTests`, not `Data_Tests`, not any other casing). The legacy key matched for replacement is exactly **`tests`** with the same spelling rules.

**Only these uses of `tests` / `data_tests` are in scope for v1:** In dbt **property YAML**, the **only** places this family treats as the real data-test declaration fields are:

1. **On the resource entry** — a direct key on each dict under **`models:`**, **`seeds:`**, **`snapshots:`**, **`macros:`**, **`exposures:`**, or **`sources:`** (alongside `name`, `config`, `columns`, …), and
2. **On each column object** — a direct key on each item in that entry’s **`columns:`** list, for **model, seed, and snapshot** only (the resource types that expose `columns:` at this level in the references this project follows).

There is **no third** in-scope location in v1. A key named `tests` elsewhere (e.g. under **`config:`**, under **`catalogs:`**, under source **`tables:` → column dicts**, **`dbt_project.yml`**, or an odd indentation path) is **not** treated as the same semantic field and is **out of scope** for rename here (see **Keys left unchanged** and the table).

### Where the rewrite applies (v1)

| Resource section (property YAML) | `tests` on the **resource entry** (sibling to `name`, `config`, …) | `tests` on each **item in `columns:`** (model / seed / snapshot only) |
| --- | --- | --- |
| `models:` | yes | yes |
| `seeds:` | yes | yes |
| `snapshots:` | yes | yes |
| `macros:` | yes | n/a (no `columns:` on macro entries) |
| `exposures:` | yes | n/a |
| `sources:` | yes | **out of scope in v1** (column tests live under `tables: → [table] → columns:`; defer to a later spec version) |

- **In scope in v1:** the two declaration sites in the **Only these uses** block above — resource-entry **`tests`**, and column-level **`tests`** for **model, seed, snapshot** where the table says “yes.”
- **Out of scope in v1 (non-exhaustive):** `sources: … → tables: … → columns: … → tests`; **`dbt_project.yml`**; any **`tests`** key that is not at one of the two in-scope sites above.

### Conflict policy (v1)

If an entry (resource row or column row) already contains **`data_tests`**, the rewrite **must not** silently merge an existing **`tests`** block with **`data_tests`** in v1. **Recommended behavior:** report a **shape / policy** error to stderr and **skip** rewriting that node (or exit non-zero in **check** mode; see **Exit codes**), with a message that both keys are present. Exact wording is left to the implementation; the spec only requires “no blind merge in v1.”

### Keys left unchanged in v1

- Any key named **`tests`** that is **not** at an in-scope declaration site (see **Only these uses** above) — the tool **does not** treat it as the data-test field and **does not** rename it to **`data_tests`** in v1.
- **`config:`**-internal keys and the rest of the document structure not listed in the v1 table.
- The implementation **SHOULD** document behavior for odd paths (mis-indentation, duplicate keys, etc.).

---

## Future: top-level `tags` and `meta` (not v1)

These are **not** in v1 because they require **nesting** under `config:`, not a simple key rename.

| Legacy pattern | Target | Notes for a future spec / release |
| --- | --- | --- |
| Top-level `tags` on a resource entry | `config.tags` | Must **create** or **merge** into a `config` mapping. If `config` already has `tags`, define merge (replace, union, or fail). |
| Top-level `meta` on a resource entry | `config.meta` | If `config.meta` already exists, need **deep merge** of mapping values or a defined conflict policy; if both sides set the same sub-key, do not guess silently. |

A future version of this family’s spec **SHOULD** name **exact merge rules** and add fixtures before implementation. The **`dbt-yaml-legacy`** v1 **must** document that **`tags` / `meta` moves** are out of scope so users do not expect them from the first release.

---

## Proposed CLI contract (v1, summary)

+ **Name:** e.g. **`dbt-yaml-legacy`** (console script; single entry for all rewrites in this family, with optional **`--only tests`**-style scoping in a later spec if more transforms ship).
+ **Positional / file list:** one or more paths; typically YAML files. Behavior for directories (recursive glob) is **implementation-defined** but **SHOULD** match team expectations documented in **[`HOOKS.md`](../../HOOKS.md)** when the hook is shipped.
+ **Modes (choose one set of names in implementation; this spec is agnostic to exact flags):**
  - **Check / dry-run:** do not write; print planned changes or a summary; exit **`1`** if any file **would** change, **`0`** if no changes needed (for CI and pre-commit “fail if not fixed” workflows).
  - **Write / in-place:** apply **`tests` → `data_tests`** in place; exit **`0`** on success, **`1`** on unrecoverable parse error or on conflict cases as defined above.
+ **No `--required` / `--forbidden`**; this is not a validator family.

**Pre-commit (future):** When shipped, add **`types: [yaml]`** and resource-path **`files:`** patterns aligned with other property-YAML hooks, unless the project standardizes a single broad pattern.

---

## Exit codes (v1, target)

| Code | Meaning |
| --- | --- |
| **`0`** | Check mode: no rewrites needed. Write mode: all targeted files written successfully, or no applicable keys found. |
| **`1`** | At least one file would be changed (check mode) or failed to parse / failed to write / unhandled conflict (write mode) — see implementation notes. |
| **`2`** | Invalid CLI usage (e.g. mutually exclusive flags), reserved for the Typer/CLI layer. |

(Exact **check-mode** “would change = exit 1” convention **SHOULD** match **`HOOKS.md`** examples and **`testing-strategy.md`** once implemented.)

---

## Relationship to `*-allowed-keys`

+ After a successful run of the **`tests` → `data_tests`** rewrite, **`data_tests`** is on the allowlist; **`tests` should** no longer appear in those positions, so **`*-allowed-keys`** and column checks should stop emitting legacy **tests** messages for the rewritten nodes.
+ This family **does not** emit the same **stderr** lines as **`*-allowed-keys`**; it either **modifies** files (write mode) or **reports** that changes are needed (check mode). **MUST NOT** attempt to duplicate the validator’s “Suggested violation detail” text byte-for-byte; the validator remains the **source of truth** for *whether* a key is allowed.

---

## Tests (when implemented)

+ Mirror **`tests/hook_families/`** under a package such as **`hook_families/dbt_yaml_legacy/`** (exact name to align with **[`project-spec.md`](../project-spec.md)**).
+ **Fixtures:** before/after YAML for **models** (top-level and `columns:`), **seeds**, **snapshots**; a case with **both** `tests` and `data_tests` must assert the **conflict** behavior; idempotence (second run is a no-op).

---

## Changelog of this spec

+ **Initial** — v1 `tests` → `data_tests` only; **Future** `tags` / `meta` section reserved.
