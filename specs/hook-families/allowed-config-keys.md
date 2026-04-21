# Hook family: `*-allowed-config-keys`

**Top-level keys of the `config` mapping** on each resource entry in dbt property YAML (Fusion-oriented). This is **not** the same as **`*-allowed-keys`** (keys on the resource object itself, e.g. `name`, `description`, `config` as a key name) or **`*-allowed-meta-keys`** (key **names** under `config.meta`). Umbrella packaging and the family index live in **[`../hooks.md`](../hooks.md)**.

**Status:** **`model-allowed-config-keys`** is **shipped**; other resource hooks **TBD**. Default allowlist tables are in **`resource-config-keys.md`**; **`MODEL_CONFIG_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/hook_families/allowed_config_keys/resource_config_keys.py`** **must** mirror those tables (same policy as **`*-allowed-keys`**: default allowlist is **Fusion-supported / documented cross-adapter keys** plus the **documented adapter-specific union** in **`resource-config-keys.md`**—detecting which adapter a project uses is **not** required).

---

## Purpose

Projects want to enforce which **direct children** of **`config:`** may appear on each model, seed, snapshot, exposure, macro, etc., using the **same allowlist policy as `*-allowed-keys`**: the **default** frozen allowlist contains **Fusion-supported keys** for that resource’s `config`, plus **adapter-specific keys** documented in the **union** tables in **`resource-config-keys.md`** (hooks do **not** need to know the active adapter). Nothing Core-only or legacy belongs in the default set except where listed as legacy. Unknown keys under **`config`** are violations unless allowlisted; keys that Core still tolerates but Fusion does not treat as first-class **SHOULD** appear only in **`resource-config-keys.md`** § **Legacy / deprecated** (with **Suggested violation detail**), not in the default allowlist.

**v1 scope:** validate **only top-level keys inside `config`** (each key is one segment; no dot paths into nested mappings inside `config`). Nested policy (e.g. which sub-keys exist under `meta`) stays with **`*-allowed-meta-keys`** and **`*-meta-accepted-values`**.

---

## Relationship to other families

| Family | Validates |
| --- | --- |
| **`*-allowed-keys`** | Top-level keys on the **resource entry** (e.g. `models: [].`… keys like `name`, `config`, `columns`). |
| **`*-allowed-config-keys`** (this spec) | Keys **inside** the **`config`** mapping when it is present and is a mapping. |
| **`*-allowed-meta-keys`** | Key **names** on **`config.meta`** (when **`meta`** is a mapping). |
| **`*-meta-accepted-values`** | A **value** at one dot path under **`meta`** (string leaf in v1). |

The **`config`** allowlist **SHOULD** include **`meta`** if your project allows metadata on the node; **`*-allowed-meta-keys`** then constrains **which keys exist under** **`meta`**. If **`meta`** is forbidden at the **`config`** level, treat that as a **`*-allowed-config-keys`** / **`--forbidden`** policy.

### V1 is only about `config` (not other top-level keys)

**Yes — v1 is enough.** Resource shapes differ: e.g. an exposure’s **`owner`** is **top-level** on the entry, not under **`config`**. This family **only** validates keys **inside** the **`config`** mapping. Top-level keys on the node (including **`owner`**, **`depends_on`**, **`type`**, …) stay with **`*-allowed-keys`** and **`resource-keys.md`** § Models / Exposures / … — not **`*-allowed-config-keys`**.

### Is `config` a valid top-level key for every v1 resource type?

**Yes** for each resource targeted by the planned hooks (**`models:`**, **`seeds:`**, **`snapshots:`**, **`macros:`**, **`exposures:`**): **`config`** is a normal, documented top-level key on the property object (see **`resource-keys.md`** tables and dbt property docs). An entry may **omit** **`config`** entirely; this family then treats **`config`** as an empty mapping (see **§ Pattern**). Other dbt lists (e.g. **`sources:`**, **`unit_tests:`**) are **out of scope for v1** of this family; revisit if we add hooks for those shapes later.

---

## Exit codes

**SHOULD** match **`*-allowed-keys`** (see **`hook-families/allowed-keys.md`**), with one difference for **`2`**:

+ **`0`** — success; files with no target section or empty file are skipped per **`yaml-handling.md`**.
+ **`1`** — at least one violation (unknown/forbidden/required key under **`config`**, legacy key detail, or parse/shape error).
+ **`2`** — invalid CLI usage (e.g. malformed flags, empty tokens after parse—align with the shared validation core and **`yaml-handling.md`** as implemented). **There is no** **`--required`** denylist analogous to forbidding **`name`** on **`*-allowed-keys`**: every allowlisted key under **`config`** is **optional by default**; nothing is always present in a way that makes **`--required`** redundant for a specific key.

---

## Pattern: `*-allowed-config-keys` (shared design)

**CLI contract** (same shape as **`*-allowed-keys`**):

+ **`--required`** — comma-separated keys that **must** appear on **`config`** for each validated entry. Default: none. If **`config`** is missing or empty, missing keys are reported the same way as missing top-level keys when **`meta`** is treated empty in **`*-allowed-meta-keys`** (required keys are “missing”). Unlike **`*-allowed-keys`**, there is **no** special case (like forbidding **`name`**) for redundant **`--required`** entries: every key under **`config`** in the allowlist is **optional** unless the user lists it in **`--required`**.
+ **Allowed keys are fixed** for that hook’s resource: **only** the documented default set in **`resource-config-keys.md`** for the matching **§** (e.g. **Models — default keys under `config`** **and** **Adapter-specific (union across adapters — models)**)—same rule as **`*-allowed-keys`** § Pattern (**`hook-families/allowed-keys.md`**). The default allowlist **MUST NOT** include Core-only or deprecated keys; those belong **only** in § **Legacy / deprecated** (if listed at all).
+ **`--forbidden`** — optional comma-separated keys that **must not** appear under **`config`**, even when otherwise allowlisted (stricter team policy).

**Parsing rules:**

+ If the resource entry has **no** **`config`** key, treat **`config`** as an **empty** mapping for purposes of **`--required`** and unknown-key checks (same idea as empty **`meta`** in **`*-allowed-meta-keys`**).
+ If **`config`** is present but **`null`**, not a mapping, or wrong shape, that is a **per-resource shape error** (**`1`**), with a clear message (see **`yaml-handling.md`**).
+ Validation applies to **keys** of the **`config`** mapping only (v1); values are not inspected except for shape of **`config`** itself.

**Legacy keys:** If a key under **`config`** appears in **`resource-config-keys.md`** § **Legacy / deprecated** for that resource’s config table, implementations **SHOULD** emit a violation whose message is **actionable** and **SHOULD** include the **Suggested violation detail** from that row, mirroring **`*-allowed-keys`** § Pattern. Keys that are neither in the documented default allowlist (including the adapter union) nor listed as legacy continue to use generic **disallowed key** wording (see **`yaml-handling.md`** § Errors).

**Hook identity:** name hooks **`{resource}-allowed-config-keys`** (e.g. **`model-allowed-config-keys`**, **`seed-allowed-config-keys`**). **`id`** and **`entry`** match the console script in **`pyproject.toml`**.

**Implementation reuse:** **SHOULD** share one validation core with **`*-allowed-keys`** where practical (same violation row sorting, same CSV flag parsing), differing only in: which YAML path is walked (`entry["config"]` vs top-level entry keys), and which allowlist / legacy map is used.

**Pre-commit:** **`language: python`**, **`entry:`** matches hook id, **`types: [yaml]`** — align **`.pre-commit-hooks.yaml`** and **`[project.scripts]`** when shipped.

---

## Allowlists in `resource-config-keys.md`

Each resource type that gets a shipped hook **MUST** gain a subsection under **`resource-config-keys.md`** documenting:

+ **Default keys allowed under `config`** — **Fusion-supported keys** plus the **adapter-specific union** in **`resource-config-keys.md`**, parallel to **`resource-keys.md`** § **Models** / **Seeds** / … for **`*-allowed-keys`** (Fusion-oriented; **must** mirror the frozen constant in code, e.g. **`MODEL_CONFIG_ALLOWED_KEYS`**).
+ **Legacy / deprecated** (reference only — not allowlisted) — keys that may still appear in older Core YAML or with warnings; **Suggested violation detail** for stderr; **not** part of the default allowlist.

Naming convention for headings: **“Models — default keys under `config`”** (or **“Model config keys”**—keep one style across resources).

Implementations **MUST** keep code allowlists in sync with **`resource-config-keys.md`** when extending this family.

Each row in the default allowlist **SHOULD** be justified with links to Fusion / dbt config reference material (and JSON schema where published). Core-only keys **MUST NOT** appear in the default table—only in **Legacy / deprecated** if we document them.

---

## Shipped CLIs

| Hook id | Resource list | `resource-config-keys.md` anchor |
| --- | --- | --- |
| **`model-allowed-config-keys`** | **`models:`** | Models — default keys under `config` + Adapter-specific (models) |

## Planned CLIs

Same remaining resources as the **`*-allowed-keys`** wave (**`macro`**, **`seed`**, **`snapshot`**, **`exposure`**):

| Hook id | Resource list | `resource-config-keys.md` anchor |
| --- | --- | --- |
| **`macro-allowed-config-keys`** | **`macros:`** | Macro config keys |
| **`seed-allowed-config-keys`** | **`seeds:`** | Seed config keys |
| **`snapshot-allowed-config-keys`** | **`snapshots:`** | Snapshot config keys |
| **`exposure-allowed-config-keys`** | **`exposures:`** | Exposure config keys |

**Sources**, **analyses**, **unit tests**, and other targets are **out of scope for v1** unless added explicitly later (same pattern as **`*-allowed-keys`** § 6).

---

## Related

+ **[`allowed-keys.md`](allowed-keys.md)** — top-level resource keys.
+ **[`allowed-meta-keys.md`](allowed-meta-keys.md)** — keys under **`config.meta`**.
+ **[`../resource-config-keys.md`](../resource-config-keys.md)** — default keys under **`config`** per resource type.
+ **[`../resource-keys.md`](../resource-keys.md)** — top-level keys on each resource entry (**`*-allowed-keys`**).
+ **[`../yaml-handling.md`](../yaml-handling.md)** — loading, skip vs error, stderr.
+ **[`../hooks.md`](../hooks.md)** — packaging index.
