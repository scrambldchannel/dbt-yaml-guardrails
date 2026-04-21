# Hook family: `*-tags-accepted-values`

Hooks are named **`{resource}-tags-accepted-values`** (e.g. **`model-tags-accepted-values`**). They validate **`config.tags`** on each resource entry in dbt property YAML: when **`tags` appear**, **every** tag string must be in the allowlist from **`--values`**. Value shape (string vs sequence) matches **`*-meta-accepted-values`** § **Sequence of strings** / string leaf, but **no path flag**—only **`config.tags`**.

**User story:** restrict tags to a **project-defined vocabulary**—not to require tags on every resource. If **`config`** or **`tags`** is absent, the hook **passes**. This family intentionally has **no** “required tags” or “optional tags” flags: **`--values`** is the only behavioral flag besides entry-point arguments.

**Status:** **Spec only** — implementation, **`[project.scripts]`**, **`.pre-commit-hooks.yaml`**, and **`HOOKS.md`** entries ship in a later change once the open questions below are resolved.

---

## Purpose

Teams often want **only** tags from a fixed vocabulary (e.g. **`pii`**, **`finance`**, **`nightly`**) when they declare tags in property YAML. This family enforces that **`config.tags`** uses **only** allowed tokens—whether written as a **single string** (one tag) or a **YAML list of strings**. Resources **without** **`config.tags`** in that file are not failed by this hook.

---

## Validation target (fixed)

+ **Only** **`config.tags`** is validated. Do **not** walk **`meta`**, **`columns`**, or other keys.
+ Resolve **`config`** on each entry like other **`config*`** hooks (see **`yaml-handling.md`**). If **`config`** is missing, treat as **no **`config`** object** (see **§ Missing `config` and `tags`**).
+ Read **`tags`** from **`config["tags"]`** when **`config`** is a mapping.

**Rationale:** Fusion-oriented config key allowlists already list **`tags`** under **`config`** per resource type in **`resource-config-keys.md`**. Top-level **`tags`** on a resource entry (if it appears in some projects) is **out of scope for v1** unless we explicitly extend this spec—see **§ Open questions**.

---

## Tag value shape

The value at **`config.tags`** **MUST** be handled consistently with **`*-meta-accepted-values`** for list-like metadata:

+ **Single string** — one tag; trim and require membership in **`--values`**.
+ **YAML sequence of strings** — each element trimmed; **each** must be in **`--values`**.
+ **Empty sequence** (`tags: []`) — vacuously valid (all zero tags are in the allowlist).
+ **Other types** (mapping, number, boolean, null as the **`tags`** value, nested sequences) → **type violation** with a clear message.

---

## Flags

The only policy flag is **`--values`** (comma-separated allowlist; trim tokens; drop empties—same parsing as **`*-meta-accepted-values`**). No **`--optional`**, **`--required`**-style, or “force tags to exist” flags: **mandatory tagging is out of scope** for this family.

| Flag | Required | Meaning |
| --- | --- | --- |
| **`--values`** | yes | Allowed tag strings. Every tag that appears under **`config.tags`** (when present) must be in this set. |

**Invalid CLI** (e.g. empty **`--values`** after parsing) **SHOULD** exit **`2`**, same as **`*-meta-accepted-values`**.

Exit codes for violations **SHOULD** match **`allowed-keys.md`** / **`meta-accepted-values.md`** (**`0`** / **`1`** / **`2`**).

---

## Missing `config` and **`tags`**

If there is nothing to validate, the hook **passes**:

+ No **`config`** key on the entry → **pass**.
+ **`config`** present, **`tags`** key absent → **pass**.
+ **`config.tags`** present → validate shape (**§ Tag value shape**) and allowlist (**`--values`**).

**Note:** Hooks only see **property YAML as parsed per file**; they do not merge **`dbt_project.yml`** or SQL **`config()`** blocks. Tags applied only elsewhere are **invisible** here—this hook only constrains tags **declared** in **`config.tags`** in the file when that key exists.

---

## Resource coverage (planned)

Mirror other config-facing families unless scoped down:

| Hook id | Resource list | Status |
| --- | --- | --- |
| **`model-tags-accepted-values`** | **`models:`** | Spec only |
| **`seed-tags-accepted-values`** | **`seeds:`** | Spec only |
| **`snapshot-tags-accepted-values`** | **`snapshots:`** | Spec only |
| **`exposure-tags-accepted-values`** | **`exposures:`** | Spec only |
| **`macro-tags-accepted-values`** | **`macros:`** | Spec only |

---

## Relationship to other families

| Family | Difference |
| --- | --- |
| **`*-allowed-config-keys`** | Ensures **`tags`** **may** appear as a **key** under **`config`**; it does **not** constrain **values** inside **`tags`**. |
| **`*-meta-accepted-values`** | **`--key`** path under **`meta`**; **`--values`**; optional **`--optional`** for path presence. **`*-tags-accepted-values`** has **only** **`--values`**; **`config.tags`** presence is never enforced. |
| **Nested tags** (columns, tests) | **`*-tags-accepted-values`** does **not** validate **`columns[].config.tags`**, **`data_tests[].…config.tags`**, or other nested **`tags`** in v1—only **`config.tags`** on the resource entry. |

---

## Open questions (need maintainer / contributor decisions)

1. **Top-level `tags`** — Some dbt property examples use **`tags`** beside **`name`** (not only under **`config`**). Should v1 also validate **top-level** **`tags`** on each entry, **`config.tags`**, **or** both? (Validating both could **double-count** if teams duplicate—need a rule.)
2. **Macro parity** — Ship **`macro-tags-accepted-values`** in the **same** milestone as **`model`**–**`exposure`**, or defer like **`macro-meta-accepted-values`**?

---

## Related

+ **`meta-accepted-values.md`** — Path-based value allowlists under **`meta`**.
+ **`resource-config-keys.md`** — **`tags`** as a **`config`** key per resource type.
+ **`yaml-handling.md`** — Parsing, **`config`**, stderr conventions.
