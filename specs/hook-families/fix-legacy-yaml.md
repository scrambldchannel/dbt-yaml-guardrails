# Hook family: `fix-legacy-yaml` (mechanical rewrites for deprecated YAML)

**Purpose:** This spec defines the **normative** mechanical rewrites for legacy keys in dbt **property YAML** — **v1:** **`tests` → `data_tests`**; **v2:** top-level **`meta` / `tags` → `config.meta` / `config.tags`** on resource entries — aligned with **`resource-keys.md`** § **Legacy / deprecated** and the `*_LEGACY_KEY_MESSAGES` / `*_COLUMN_LEGACY_KEY_MESSAGES` maps in **`resource_keys.py`**. It does **not** replace validation: teams still use **`*-allowed-keys`**, **`*-allowed-column-keys`**, and other families for policy and allowlists.

**Delivery:** Rewrites are invoked only through the **opt-in** **`--fix-legacy-yaml`** flag (default **`false`**) on **`*-allowed-keys`** and **`*-allowed-column-keys`**, as specified in **[`allowed-keys.md`](allowed-keys.md)** and **[`allowed-column-keys.md`](allowed-column-keys.md)**. When **`true`**, the implementation runs **v1** then **v2** (see below). There is no separate console script or pre-commit hook id for rewrites. For **`source-allowed-keys`**, v1 rewrites on **`tables:`** and nested **`columns:`** are **gated** by the same **`--check-source-tables`** / **`--check-source-table-columns`** flags as validation (see **`allowed-keys.md`** **§ Nested keys (`sources:` → `tables:` and `columns:`)**). **Future:** v2-style moves for **`meta` / `tags`** on **table** or **column** rows under **sources**; other column-level transforms.

Umbrella packaging and the family list live in **[`../hooks.md`](../hooks.md)**.

---

## Design principles

+ **Complement validators, do not replace them.** The rewrite applies **mechanical, syntax-level** edits **before** validation when **`--fix-legacy-yaml` is** **`true`**. Allowlists, **`--required`**, and policy remain the job of **`*-allowed-keys`** and related hooks.
+ **Deterministic and idempotent** where possible: running the fixer twice on the same file should not change the file a second time (or should be a no-op after the first run).
+ **Property YAML** for these rewrites (same file scope and loader expectations as **[`yaml-handling.md`](../yaml-handling.md)** § **dbt property YAML** and **`load_property_yaml`**). Do **not** target **`dbt_project.yml`**, **`catalogs.yml`**, or manifest-only files unless a later spec explicitly extends scope.
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

**Only these uses of `tests` / `data_tests` are in scope for v1:** In dbt **property YAML**, the places this family treats as the real data-test declaration fields for rename are:

1. **On the resource entry** — a direct key on each dict under **`models:`**, **`seeds:`**, **`snapshots:`**, **`macros:`**, **`exposures:`**, or **`sources:`** (alongside `name`, `config`, `columns`, …), and
2. **On each column object** — a direct key on each item in that entry’s **`columns:`** list, for **model, seed, and snapshot** only (the resource types that expose `columns:` at this level in the references this project follows).
3. **Under `sources:`** — a direct key on each **table** dict under **`sources: → (each source) → tables:`** and (when enabled) on each **column** dict under **`… → columns:`** for a **source table** — **only** when using **`source-allowed-keys`** and the **nested rewrites** are not suppressed by the CLI: **`--check-source-tables` true** is required to rewrite (and check) table rows; **both** that and **`--check-source-table-columns` true** are required to rewrite (and check) those column dicts. When a flag is **false**, the implementation does **not** treat **`tests`** on that nested level as the v1 rename target (it does not rename there).

A key named `tests` elsewhere (e.g. under **`config:`**, under **`catalogs:`**, in **`dbt_project.yml`**, or an odd indentation path) is **not** treated as the same semantic field and is **out of scope** for rename here unless it is one of the sites above (see **Keys left unchanged** and the table).

### Where the rewrite applies (v1)

| Resource section (property YAML) | `tests` on the **resource entry** (sibling to `name`, `config`, …) | `tests` on each **item in `columns:`** (model / seed / snapshot only) |
| --- | --- | --- |
| `models:` | yes | yes |
| `seeds:` | yes | yes |
| `snapshots:` | yes | yes |
| `macros:` | yes | n/a (no `columns:` on macro entries) |
| `exposures:` | yes | n/a |
| `sources:` | yes (resource row) | **yes** for **table** rows when **`--check-source-tables` true**; for **source-table column** dicts when **both** nested flags are **true** (see (3) above). Otherwise the nested level is not rewritten by v1. |

- **In scope in v1:** the declaration sites in the **Only these uses** block above — resource-entry **`tests`** on all six property list types, column-level **`tests`** for **model, seed, snapshot** where the table says “yes,” and (with **`source-allowed-keys`**) nested **table** / **source-table column** sites when the corresponding **CLI flags** enable both validation and the fix for that level.
- **Out of scope in v1 (non-exhaustive):** **`tests`** on nested source paths when the **`source-allowed-keys`** flag for that level is **false**; **`dbt_project.yml`**; any **`tests`** key that is not at one of the in-scope sites above; **`model-allowed-keys`**, **`macro-allowed-keys`**, etc. (non-**`source`**) do **not** run nested **sources** rewrites on mixed property files.

### Conflict policy (v1)

If an entry (resource row or column row) already contains **`data_tests`**, the rewrite **must not** silently merge an existing **`tests`** block with **`data_tests`** in v1. **Recommended behavior:** report a **shape / policy** error to stderr and **skip** rewriting that node, with a message that both keys are present. Exact wording is left to the implementation; the spec only requires “no blind merge in v1.”

### Keys left unchanged in v1

- Any key named **`tests`** that is **not** at an in-scope declaration site (see **Only these uses** above) — the tool **does not** treat it as the data-test field and **does not** rename it to **`data_tests`** in v1.
- **`config:`**-internal keys and the rest of the document structure not listed in the v1 table.
- The implementation **SHOULD** document behavior for odd paths (mis-indentation, duplicate keys, etc.).

---

## v2: top-level `meta` and `tags` → `config` (resource entries)

**Goal:** Move top-level **`meta`** and **`tags`** on each **resource entry** into **`config.meta`** and **`config.tags`**, matching the legacy messages in **`resource_keys.py`** for **model, macro, seed, snapshot, exposure, source**.

**Where:** Each list item under **`models:`**, **`macros:`**, **`seeds:`**, **`snapshots:`**, **`exposures:`**, and **`sources:`**. **Not** column dicts, **`tables:`** / nested source columns, **`catalogs:`**, or **`dbt_project.yml`**.

**Merge and conflict (v2):**

+ If **`config`** is **absent:** create a **`config`** mapping whose first keys are **`meta`** and/or **`tags`** (in that order if both are moved), inserted at the **original** position of the leftmost of **`meta`** / **`tags`** among top-level siblings (key order preserved among remaining top-level keys).
+ If **`config`** **exists** and is a **mapping:** **append** **`meta`** / **`tags`** into it (new keys at the end of **`config`**) when the top-level keys are present.
+ If **`config`** is present but **not** a mapping (e.g. **`config: null`**): **fail** for that entry (no move).
+ If top-level **`meta`** (or **`tags`**) is present **and** **`config.meta`** (or **`config.tags`**) already exists: **conflict** — do **not** merge; report an error for that entry and **do not write** the file if any entry in the document conflicts (atomicity: preflight all resource rows before applying any move).

**Order of operations when `true`:** Run **v1** (`tests` → `data_tests`) first, then **v2** (`meta` / `tags`). If **v1** reports conflicts, fail before **v2**. If **v2** preflight finds any conflict, fail without writing (in-memory **v1** edits are not persisted).

### Hooks in scope (v2)

The **six** property **`*-allowed-keys`** CLIs that ship **`--fix-legacy-yaml`**, and the **document-wide** rewrite on the same property YAML files when using **`*-allowed-column-keys`**. **Not** **`catalog-allowed-keys`** or **`dbt-project-allowed-keys`**.

### Spec examples (target shape for `meta` and `tags`)

**Normative for this file:** Examples that depict the **fixed** shape **MUST** show **`meta` and `tags` under `config`**. Before/after pairs **MAY** show legacy top-level keys only in the “before” half.

```yaml
# After v2 rewrite, resource entries for in-scope types match:
models:
  - name: my_model
    description: "…"
    config:
      meta: { owner: analytics }
      tags: [ nightly ]
    # … other allowed keys, e.g. data_tests, columns, …
```

Column-level **`meta` / `tags`** (directly on a column or under column **`config:`**) are **unchanged** by v2; a later spec may extend moves for column rows.

---

## CLI contract

**Flag:** **`--fix-legacy-yaml`** with an explicit boolean; default **`false`**. Exposed **only** on the six **`*-allowed-keys`** property-YAML console scripts (**`model`**, **`macro`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**) and on shipped **`*-allowed-column-keys`** hooks (**`model`**, **`seed`**, **`snapshot`**). Not on **`catalog-allowed-keys`** or **`dbt-project-allowed-keys`** (see **[`allowed-keys.md`](allowed-keys.md)**). **When `true`:** perform **v1** and **v2** rewrites (this spec), **write** the file when at least one change applies and there are no conflicts, then run the **hook’s** normal validation. **When `false`:** do **not** rewrite; only validate. Full detail: **[`allowed-keys.md`](allowed-keys.md)** § **Pattern**, **[`allowed-column-keys.md`](allowed-column-keys.md)** § **Pattern**.

**Pre-commit:** add **`args: ['--fix-legacy-yaml', 'true']`** (or the project’s spelling for boolean flags) to the relevant **`id`** stanzas for **`model-allowed-keys`**, **`seed-allowed-keys`**, etc.

---

## Exit codes

Use the **`*-allowed-keys`** and **`*-allowed-column-keys`** exit code tables; failures in the fix phase are **`1`**. See **[`allowed-keys.md`](allowed-keys.md)** and **[`allowed-column-keys.md`](allowed-column-keys.md)**.

---

## Relationship to `*-allowed-keys` and `*-allowed-column-keys`

+ After a **successful** rewrite, **`data_tests`** is allowlisted; **`tests` should** no longer appear in those positions, so validators should stop emitting legacy **tests** messages for the rewritten nodes on the next run. Likewise, top-level **`meta` / `tags`** on resource entries should only appear under **`config`**, so legacy messages for those top-level keys should not fire on the next run.
+ The **rewrite** (this spec) **does not** print the same **stderr** lines as the validators. When **`--fix-legacy-yaml` is** **`true`**, the hook first **edits** the file (when applicable) **then** runs validation; the validator remains the **source of truth** for *whether* a key is allowed **after** the file state is updated. **MUST NOT** attempt to duplicate the validator’s “Suggested violation detail” text byte-for-byte in the **rewrite** layer; reuse **`resource_keys.py`** messaging only in **validation** code paths.

---

## Tests

+ **Shared** rewrite logic under **`hook_families/fix_legacy_yaml/`** per **[`project-spec.md`](../project-spec.md)**: v1 and v2 behaviors; **both** `tests` and `data_tests` (conflict); v2 **meta** + existing **`config.meta`** (conflict); idempotence (second **`true` run** is a no-op) for `tests` and for `meta` / `tags`.
+ **Integration:** **`*-allowed-keys`** and **`*-allowed-column-keys`** with **`--fix-legacy-yaml` true** assert rewrite outcomes on disk **then** validation when the file is otherwise valid.

---

## Changelog of this spec

+ **Initial** — v1 `tests` → `data_tests` only; **Future** `tags` / `meta` section reserved.
+ **Rename** — The family and spec file were named **`fix-legacy-yaml`**; code lives under **`hook_families/fix_legacy_yaml/`** in the repository.
+ **Integrated-only delivery** — **`--fix-legacy-yaml`** (default **`false`**) on **`*-allowed-keys`** and **`*-allowed-column-keys`**; the standalone `fix-legacy-yaml` console entry point and pre-commit hook were **removed** in favor of the integrated flag only.
+ **Examples for v2 `meta` / `tags`** — spec YAML that depicts the post-rewrite shape **MUST** show **`meta` and `tags` under `config`** (see **§ v2**).
+ **v2** — top-level **`meta` / `tags`** → **`config`** on resource entries; conflict if **`config.meta` / `config.tags`** already set; `config` must be a mapping; apply after v1; atomic preflight.
