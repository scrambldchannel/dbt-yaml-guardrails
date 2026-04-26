# Hook family: `*-allowed-column-keys`

**Direct keys on each column entry** (each item in a resource's `columns:` list) in dbt property YAML (Fusion-oriented). This family is **distinct** from **`*-allowed-keys`** (top-level keys on the resource entry) and from **`*-allowed-config-keys`** (keys under the resource's `config:` mapping). **`*-allowed-keys`** with **`--check-columns` default `true`** **also** enforces the **same** default column-key allowlists; this family is the place for **`--required` / `--forbidden` on column keys** and for workflows that only run column checks. Umbrella packaging and the family index live in **[`../hooks.md`](../hooks.md)**.

**Status:** Spec written; **not yet shipped**. Default allowlist tables and constants (`MODEL_COLUMN_ALLOWED_KEYS`, `SEED_COLUMN_ALLOWED_KEYS`, `SNAPSHOT_COLUMN_ALLOWED_KEYS`) already live in **`resource_keys.py`** and **`resource-keys.md`** § **Column keys**, defined for the **`--check-columns`** extension of **`*-allowed-keys`**.

**Allowlist stability:** Column key allowlists target **dbt Fusion and the latest dbt Core versions** (1.10+). The allowed sets may grow as dbt formalises new column-level properties. When dbt deprecates or renames a column key, add it to **Legacy / deprecated** in **`resource-keys.md`** § **Column keys** and a matching `*_COLUMN_LEGACY_KEY_MESSAGES` entry; do not remove it from the allowlist immediately.

---

## Purpose

Projects want to enforce which **direct keys** may appear on each column entry, use **`--required`** to mandate keys like `description` on every column, or use **`--forbidden`** to ban legacy keys. The **`--check-columns`** extension of **`*-allowed-keys`** provides the default allowlist check but intentionally omits `--required` / `--forbidden` for column keys (see **`hook-families/allowed-keys.md`** § **Nested keys (`columns:`) and `--check-columns`**). This family fills that gap.

**v1 scope:** validate only **direct keys on each column entry** (one segment; no dot paths into `config`, `meta`, `constraints`, or other sub-mappings inside a column). Nested policy (e.g. which keys exist under column-level `config:` or `meta:`) stays with dedicated families.

---

## Relationship to other families

| Family | Validates |
| --- | --- |
| **`*-allowed-keys`** | Top-level keys on the **resource entry** (e.g. `name`, `config`, `columns`). When **`--check-columns`** is `true` (default), also **direct keys on each column entry** using the same default allowlists as this family. |
| **`*-allowed-column-keys`** (this spec) | **Direct keys on each column entry** (keys on each item in `columns:`). Adds `--required` / `--forbidden` for column keys; default allowlist is identical to `--check-columns`. |
| **`*-allowed-config-keys`** | Top-level keys inside the **resource-level `config:`** mapping. |
| **`*-allowed-meta-keys`** | Key names under **`config.meta`** on the resource entry. |

**Overlap with `*-allowed-keys --check-columns`:** Running both on the same file and entry with default settings **may** emit **two** stderr lines for the same disallowed column key (one per hook). Implementations **MUST NOT** deduplicate or suppress violations across hooks. Each hook is responsible for reporting the violations it is configured to find, independently of what other hooks are running. **Recommended practice:** teams that adopt `*-allowed-column-keys` for granular column-key control (e.g. `--required description`) should consider passing `--check-columns false` on the corresponding `*-allowed-keys` hooks to avoid duplicate output for the same keys. Document this in **`HOOKS.md`** when this family ships.

---

## Exit codes

| Code | Meaning |
| --- | --- |
| **`0`** | Every processed file passed. Files with no target section, or with `columns:` absent or an empty list, are skipped (no violation). |
| **`1`** | At least one column key violation (disallowed / required / forbidden / legacy), a parse / shape error (see **Shape errors** below), or a failure in the **`--fix-legacy-yaml`** phase (conflict, write error, or parse error from the round-trip pass — see **`fix-legacy-yaml.md`** and **`allowed-keys.md`** § **Pattern**). |
| **`2`** | Invalid CLI usage. Do **not** list **`name`** in **`--required`**: `name` is always required on every real column entry; listing it is redundant and SHOULD be rejected with exit `2`, analogous to `name` in `*-allowed-keys --required`. |

---

## Pattern: `*-allowed-column-keys` (shared design)

**CLI contract** (mirrors `*-allowed-config-keys`, adapted for column entries):

+ **`--required`** — comma-separated column keys that **must** appear on every column entry. Default: none. Do **not** list `name` in `--required` (see **Exit codes §2** above). If `columns:` is absent on a resource entry there are no column entries to check — no missing-key violation is reported for that entry.
+ **Allowed keys are fixed** per resource: only the documented default set in **`resource-keys.md`** § **Column keys** for that resource type, implemented as `*_COLUMN_ALLOWED_KEYS` in `resource_keys.py`. These **MUST** mirror the spec tables.
+ **`--forbidden`** — comma-separated column keys that **must not** appear on any column entry, even when otherwise allowlisted (stricter team policy; e.g. `--forbidden tests` to actively reject the legacy alias rather than rely on the allowlist alone).
+ **`--fix-legacy-yaml`** — **one** boolean option; default **`false`**. **Opt-in** mechanical rewrites of legacy property-YAML keys **before** column-key validation, as defined in **[`fix-legacy-yaml.md`](fix-legacy-yaml.md)** (**v1:** **`tests` → `data_tests`** on resource and column rows where in scope; **v2:** top-level resource **`meta` / `tags` → `config`**). When **`true`**, behavior matches **`--fix-legacy-yaml`** on **`*-allowed-keys`**: **ruamel** round-trip load, **apply** rewrites **in place** (write when changes occur), **re-read**, then run the usual **`*-allowed-column-keys`** checks. When **`false`**, **validation only**. **Document-wide:** the rewrite applies to the **entire** property YAML file, not only `columns:` rows, so a column-only hook with **`--fix-legacy-yaml` true** may also fix **resource-level** keys in the same file (same rationale as **`*-allowed-keys`**). Shipped hooks **§ Shipped CLIs** (**`model-`**, **`seed-`**, **`snapshot-allowed-column-keys`**) are **in scope** for the non–no-op rewrite; the same **conflict and exit** rules as **`fix-legacy-yaml.md`** and **`hook-families/allowed-keys.md`** apply.

**Parsing rules:**

+ If a resource entry has **no** `columns:` key, or `columns:` is an **empty list**, skip silently — no violation is reported for that entry. This includes the case where `--required` keys are set: absence of `columns:` does not trigger missing-key violations. *(This behaviour may be revisited in a future version if teams need to enforce that every resource declares at least one column.)*
+ If `columns:` is present but **`null`** or not a list, that is a **shape error** (exit `1`) — message: `{resource_kind} '{resource_name}': columns must be a list`.
+ If a column entry is **`null`** or not a mapping, that is a **shape error** (exit `1`) — message: `{resource_kind} '{resource_name}': column at index {i} must be a mapping`.
+ If a column entry is missing `name`, that is a **shape error** (exit `1`) — message: `{resource_kind} '{resource_name}': column at index {i} is missing 'name'`. Indices are **0-based**.
+ Validation applies to **direct keys** of each column mapping only (v1); values are not inspected.

**Legacy column keys:** If a key on a column entry appears in **`resource-keys.md`** § **Column keys — Legacy / deprecated** for that resource, implementations **SHOULD** emit an actionable violation message using the **Suggested violation detail** from that row (e.g. `Rename to \`data_tests\`…` for `tests`), consistent with other families.

**stderr for column key violations:** Use `column '<name>': <detail>` as the infix after the resource label — e.g.:

```
path/to/schema.yml: model 'my_model': column 'id': disallowed key 'bad_key'
path/to/schema.yml: model 'my_model': column 'id': missing required key 'description'
```

This is the same format used by **`*-allowed-keys --check-columns`**, so violation lines from both hooks are directly comparable.

**Hook identity:** name hooks `{resource}-allowed-column-keys` (e.g. `model-allowed-column-keys`, `seed-allowed-column-keys`). `id` and `entry` match the console script in `pyproject.toml`.

**Implementation reuse:** **SHOULD** share the column-validation helper (`_nested_column_violations`) already in `allowed_keys_core.py`, adding `--required` / `--forbidden` support. A new `allowed_column_keys/` subpackage mirrors the layout of `allowed_config_keys/`. Allowlist constants are imported from `resource_keys.py` (no separate `resource_column_keys.py` needed — column constants already live there).

**Pre-commit:** `language: python`, `entry:` matches hook id, `types: [yaml]` — align `.pre-commit-hooks.yaml` and `[project.scripts]` when shipped.

---

## Shipped CLIs

Only resources whose entry has a `columns:` list at the **top level of the entry** are in scope for v1:

| Hook id | Resource list | `resource-keys.md` anchor |
| --- | --- | --- |
| **`model-allowed-column-keys`** | `models:` | § Models — Column keys (`MODEL_COLUMN_ALLOWED_KEYS`) |
| **`seed-allowed-column-keys`** | `seeds:` | § Seeds — Column keys (`SEED_COLUMN_ALLOWED_KEYS`) |
| **`snapshot-allowed-column-keys`** | `snapshots:` | § Snapshots — Column keys (`SNAPSHOT_COLUMN_ALLOWED_KEYS`) |

**Out of scope (v1):**

+ **`macro-allowed-column-keys`**, **`exposure-allowed-column-keys`**: macro and exposure entries have no `columns:` list. These hooks do **not exist** — there is no no-op version. **General policy:** hooks in this family are only shipped for resource types that have a `columns:` list at the resource entry level. For resources without `columns:`, the hook is simply absent rather than added as a no-op. This applies to all future additions to this family.
+ **`source-allowed-column-keys`**: **not** shipped. Source table **`columns:`** are validated as **top-level** keys on each column dict by the **`source-allowed-keys`** **id** and **`--check-source-table-columns`** (see **`allowed-keys.md`**, **`resource-keys.md`** § **Source table — column keys**). The **`*-allowed-column-keys`** family remains **model / seed / snapshot** only. A **dedicated, more targeted** `source-allowed-column-keys` (or `source-table-allowed-column-keys`–style) **id** may be added in a **future** release to carry **`--required` / `--forbidden` for column** keys under `sources: → … → tables:`, which is **out of scope** for **`source-allowed-keys`**; it is not **required** for the allowlists in **`resource-keys.md`**.
+ **Analyses, unit tests**: out of scope until corresponding entry-level hooks are added.

---

## Allowlists in `resource-keys.md`

Column key allowlists and legacy maps already exist in **`resource-keys.md`** § **Column keys** for each resource and as constants in **`resource_keys.py`**:

+ `MODEL_COLUMN_ALLOWED_KEYS` / `MODEL_COLUMN_LEGACY_KEY_MESSAGES`
+ `SEED_COLUMN_ALLOWED_KEYS` / `SEED_COLUMN_LEGACY_KEY_MESSAGES`
+ `SNAPSHOT_COLUMN_ALLOWED_KEYS` / `SNAPSHOT_COLUMN_LEGACY_KEY_MESSAGES`

When the dbt column-property surface evolves, update both the `resource-keys.md` table **and** the matching constant in `resource_keys.py`. No separate `resource_column_keys.py` is needed.

---

## Related

+ **[`fix-legacy-yaml.md`](fix-legacy-yaml.md)** — **`tests` → `data_tests`** and top-level **`meta` / `tags` → `config`** rewrites; **`--fix-legacy-yaml`** on this family and on **`*-allowed-keys`** (see each spec’s **Pattern**).
+ **[`allowed-keys.md`](allowed-keys.md)** — top-level resource keys and `--check-columns` (default column key check without `--required`/`--forbidden`).
+ **[`allowed-config-keys.md`](allowed-config-keys.md)** — keys under the resource-level `config:` mapping.
+ **[`allowed-meta-keys.md`](allowed-meta-keys.md)** — key names under `config.meta`.
+ **[`../resource-keys.md`](../resource-keys.md)** — column key allowlist tables (§ Column keys for each resource).
+ **[`../yaml-handling.md`](../yaml-handling.md)** — loading, skip vs error, stderr.
+ **[`../hooks.md`](../hooks.md)** — packaging index.
