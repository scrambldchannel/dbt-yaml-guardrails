# Hook family: `fix-legacy-yaml` (mechanical rewrites for deprecated YAML)

**Purpose:** This spec defines the **normative** mechanical rewrites for legacy keys in dbt **property YAML** (v1: **`tests` → `data_tests`**) that align with **`resource-keys.md`** § **Legacy / deprecated** and the `*_LEGACY_KEY_MESSAGES` / `*_COLUMN_LEGACY_KEY_MESSAGES` maps in **`resource_keys.py`**. It does **not** replace validation: teams still use **`*-allowed-keys`**, **`*-allowed-column-keys`**, and other families for policy and allowlists.

**Delivery:** Rewrites are invoked only through the **opt-in** **`--fix-legacy-yaml`** flag (default **`false`**) on **`*-allowed-keys`** and **`*-allowed-column-keys`**, as specified in **[`allowed-keys.md`](allowed-keys.md)** and **[`allowed-column-keys.md`](allowed-column-keys.md)**. **v1** implements **`tests` → `data_tests`** only, at the declaration sites in **§ v1** below. There is no separate console script or pre-commit hook id for rewrites. Future transforms (`tags` / `meta`) are not implemented yet.

Umbrella packaging and the family list live in **[`../hooks.md`](../hooks.md)**.

---

## Design principles

+ **Complement validators, do not replace them.** The rewrite applies **mechanical, syntax-level** edits **before** validation when **`--fix-legacy-yaml` is** **`true`**. Allowlists, **`--required`**, and policy remain the job of **`*-allowed-keys`** and related hooks.
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

If an entry (resource row or column row) already contains **`data_tests`**, the rewrite **must not** silently merge an existing **`tests`** block with **`data_tests`** in v1. **Recommended behavior:** report a **shape / policy** error to stderr and **skip** rewriting that node, with a message that both keys are present. Exact wording is left to the implementation; the spec only requires “no blind merge in v1.”

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

A future version of this family’s spec **SHOULD** name **exact merge rules** and add fixtures before implementation. The **`fix-legacy-yaml`** v1 **must** document that **`tags` / `meta` moves** are out of scope so users do not expect them from the first release.

---

## CLI contract (v1)

**Flag:** **`--fix-legacy-yaml`** with an explicit boolean; default **`false`**. Exposed **only** on the six **`*-allowed-keys`** property-YAML console scripts (**`model`**, **`macro`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**) and on shipped **`*-allowed-column-keys`** hooks (**`model`**, **`seed`**, **`snapshot`**). Not on **`catalog-allowed-keys`** or **`dbt-project-allowed-keys`** (see **[`allowed-keys.md`](allowed-keys.md)**). **When `true`:** perform the v1 rewrites (this spec), **write** the file when renames apply, then run the **hook’s** normal validation. **When `false`:** do **not** rewrite; only validate. Full detail: **[`allowed-keys.md`](allowed-keys.md)** § **Pattern**, **[`allowed-column-keys.md`](allowed-column-keys.md)** § **Pattern**.

**Pre-commit:** add **`args: ['--fix-legacy-yaml', 'true']`** (or the project’s spelling for boolean flags) to the relevant **`id`** stanzas for **`model-allowed-keys`**, **`seed-allowed-keys`**, etc.

---

## Exit codes (v1)

Use the **`*-allowed-keys`** and **`*-allowed-column-keys`** exit code tables; failures in the fix phase are **`1`**. See **[`allowed-keys.md`](allowed-keys.md)** and **[`allowed-column-keys.md`](allowed-column-keys.md)**.

---

## Relationship to `*-allowed-keys` and `*-allowed-column-keys`

+ After a **successful** rewrite, **`data_tests`** is allowlisted; **`tests` should** no longer appear in those positions, so validators should stop emitting legacy **tests** messages for the rewritten nodes on the next run.
+ The **rewrite** (this spec) **does not** print the same **stderr** lines as the validators. When **`--fix-legacy-yaml` is** **`true`**, the hook first **edits** the file (when applicable) **then** runs validation; the validator remains the **source of truth** for *whether* a key is allowed **after** the file state is updated. **MUST NOT** attempt to duplicate the validator’s “Suggested violation detail” text byte-for-byte in the **rewrite** layer; reuse **`resource_keys.py`** messaging only in **validation** code paths.

---

## Tests (when implemented)

+ **Shared** rewrite logic (e.g. under **`hook_families/fix_legacy_yaml/`** per **[`project-spec.md`](../project-spec.md)**) **SHOULD** be covered by unit tests: before/after YAML for **models** (top-level and `columns:`), **seeds**, **snapshots**; a case with **both** `tests` and `data_tests` must assert **conflict** behavior; idempotence (second **`true` run** is a no-op).
+ **Integration:** **`*-allowed-keys`** and **`*-allowed-column-keys`** with **`--fix-legacy-yaml` true** **SHOULD** assert the same rewrite outcomes on disk **then** validation (no legacy **`tests`** left where in scope) **when** the file is otherwise valid.

---

## Changelog of this spec

+ **Initial** — v1 `tests` → `data_tests` only; **Future** `tags` / `meta` section reserved.
+ **Rename** — The family and spec file were named **`fix-legacy-yaml`**; code lives under **`hook_families/fix_legacy_yaml/`** in the repository.
+ **Integrated-only delivery** — **`--fix-legacy-yaml`** (default **`false`**) on **`*-allowed-keys`** and **`*-allowed-column-keys`**; the standalone `fix-legacy-yaml` console entry point and pre-commit hook were **removed** in favor of the integrated flag only.
