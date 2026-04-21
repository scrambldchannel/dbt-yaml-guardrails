# Hook family: `*-tags-accepted-values`

Hooks are named **`{resource}-tags-accepted-values`** (e.g. **`model-tags-accepted-values`**). They validate **`config.tags`** on each resource entry in dbt property YAML: **every** tag string must appear in a project-defined allowlist from **`--values`**. Behavior is intentionally parallel to **`*-meta-accepted-values`** when the meta path points at a **string list** (see **`meta-accepted-values.md`** § **Sequence of strings**), but **no path or key** is configured—**`tags`** is always **`config.tags`**, relative to each entry’s **`config`** mapping.

**Status:** **Spec only** — implementation, **`[project.scripts]`**, **`.pre-commit-hooks.yaml`**, and **`HOOKS.md`** entries ship in a later change once the open questions below are resolved.

---

## Purpose

Teams often want **only** tags from a fixed vocabulary (e.g. **`pii`**, **`finance`**, **`nightly`**) on models, seeds, snapshots, exposures, or macros. This family enforces that **`config.tags`** contains **only** allowed tokens, whether written as a **single string** (one tag) or a **YAML list of strings**.

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
+ **Empty sequence** (`tags: []`) — vacuously valid (all zero tags are allowed), unless a future flag requires “at least one tag.”
+ **Other types** (mapping, number, boolean, null as the **`tags`** value, nested sequences) → **type violation** with a clear message.

---

## Flags

Parsing and semantics align with **`*-meta-accepted-values`** for **`--values`** and **`--optional`**:

| Flag | Required | Meaning |
| --- | --- | --- |
| **`--values`** | yes | Comma-separated allowlist (trim tokens; drop empties). Every tag on the resource must be in this set. |
| **`--optional`** | no | If **unset** (default), **`tags`** is **required** when the policy applies—see **§ Missing `config` and `tags`**. If **set**, a **missing **`tags`** key** (or no usable **`config`**) is **not** a violation; when **`tags`** **is** present, it must still satisfy shape + allowlist rules. |

**Invalid CLI** (e.g. empty **`--values`** after parsing) **SHOULD** exit **`2`**, same as **`*-meta-accepted-values`**.

Exit codes for violations **SHOULD** match **`allowed-keys.md`** / **`meta-accepted-values.md`** (**`0`** / **`1`** / **`2`**).

---

## Missing `config` and `tags`

Behavior must be explicit so CI is predictable:

| Situation | **`--optional` unset** | **`--optional` set** |
| --- | --- | --- |
| No **`config`** key on entry | **Violation** — tags required for this hook’s policy | **Pass** (no tags to check) |
| **`config`** present, **`tags`** absent | **Violation** — missing **`tags`** | **Pass** |
| **`config.tags` present** | Validate shape + allowlist | Validate shape + allowlist |

If this feels too strict for **`--optional` unset** (“require **`config`** to exist”), we may instead treat “no **`config`**” like “no **`tags`**” — **§ Open questions**.

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
| **`*-meta-accepted-values`** | Arbitrary dot path under **`meta`**; **`--key`** required. **`*-tags-accepted-values`** is **only** **`config.tags`**, no path flag. |

---

## Open questions (need maintainer / contributor decisions)

1. **Top-level `tags`** — Some dbt property examples use **`tags`** beside **`name`** (not only under **`config`**). Should v1 also validate **top-level** **`tags`** on each entry, **`config.tags`**, **or** both? (Validating both could **double-count** if teams duplicate—need a rule.)
2. **Strictness when `config` is missing** — Should “missing **`config`**” with **`--optional` unset** be a **violation**, or should we only require **`tags`** when **`config`** exists?
3. **Minimum tag count** — Is **`tags: []`** always OK, or do some projects need **“at least one tag from `--values`”** (a separate flag or hook in the future)?
4. **Macro parity** — Ship **`macro-tags-accepted-values`** in the **same** milestone as **`model`**–**`exposure`**, or defer like **`macro-meta-accepted-values`**?

---

## Related

+ **`meta-accepted-values.md`** — Path-based value allowlists under **`meta`**.
+ **`resource-config-keys.md`** — **`tags`** as a **`config`** key per resource type.
+ **`yaml-handling.md`** — Parsing, **`config`**, stderr conventions.
