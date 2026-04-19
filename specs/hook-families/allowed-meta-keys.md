# Hook family: `*-allowed-meta-keys`

Hooks in this family are named **`{resource}-allowed-meta-keys`** (e.g. **`model-allowed-meta-keys`**). The **`config`** wrapper is **implied** by the family name: each hook validates **keys on the `meta` mapping** nested under that resource entry’s **`config`** (i.e. **`config.meta`** in property YAML—do not repeat **`config`** in the hook id).

dbt Core treats **`meta`** as an **arbitrary** key–value dictionary—there is **no Fusion-style built-in allowlist** in Core. This family lets **projects supply their own optional allowlist** via the CLI; there is **no** default allowlist in **`resource-keys.md`** (unlike **`*-allowed-keys`**).

**Shipped behavior today:** **`--required`**, **`--forbidden`**, and **`--allowed`** each list **top-level key names** on **`meta`** only (single segment per token, no **`.`**). **Nested paths** are a **future extension**—see **§ Future: nested key paths (dot notation)**.

## CLI contract (aligned with **`allowed-keys.md`** where applicable)

Hooks **SHOULD** use the same comma-separated parsing and trimming for flags as **`allowed-keys.md`**, and the same **exit code** pattern (**`0`** / **`1`** / **`2`**).

+ **`--required`** — comma-separated **top-level key names** that **must** be present on **`meta`** (under **`config`**) for each resource entry the hook targets. If **`config`** or **`meta`** is missing or **`meta`** is not a mapping, treat per **`yaml-handling.md`** § Errors. Default: none.

+ **`--forbidden`** — comma-separated **top-level key names** that **must not** appear under **`meta`** (checked in addition to any allowlist rule below).

+ **`--allowed`** (optional) — comma-separated **top-level key names** that **may** appear under **`meta`**.

### When **`--allowed` is omitted**

Only **`--required`** and **`--forbidden`** apply: there is **no** “unknown key” rule unless/until a hook documents one (e.g. only enforce presence/absence of listed keys).

### When **`--allowed` is provided**

1. Compute **effective allow** = (**`--allowed`** ∪ **`--required`**). Keys listed in **`--required`** do **not** need to be repeated in **`--allowed`**; they are **implicitly** part of the allowlist.
2. Any key **present** on **`meta`** that is **not** in **effective allow** is a violation (**forbidden** in the sense of “not permitted”).
3. Apply **`--forbidden`** as well: a key in **`--forbidden`** is a violation **even if** it appears in **`--allowed`** or **`--required`** (explicit deny wins), so teams can block mistakes without reshaping the allowlist.

**Skipping:** If a resource has no **`config`**, or **`config`** has no **`meta`**, treat **`meta`** as an **empty** key set for validation (so **`--required`** keys are reported missing; **`--forbidden`** / allowlist rules see no keys present). Shipped hooks in this family follow this behavior.

### Future: nested key paths (dot notation)

**Not part of the shipped CLI yet**—document here so future work stays aligned with **`meta-keys-accepted-values.md`**.

A later revision **may** allow each token in **`--required`**, **`--forbidden`**, and **`--allowed`** to be a **dot-separated path** relative to **`meta`**, using the **same path rules** as **`--key`** in **[`meta-keys-accepted-values.md`](meta-keys-accepted-values.md)** § **Key path** (e.g. **`owner.name`**, **`owner.email`**—segments walk nested **mappings** only; no array indices).

Before implementations ship this:

1. Extend **§ When `--allowed` is provided** for **nested** keys: how **“unknown key”** applies to inner mappings (flattened paths vs only top-level keys on **`meta`**).
2. Define **required** / **forbidden** at a path when intermediate mappings are missing or wrong type.
3. Align **stderr** / **sort keys** with **`yaml-handling.md`** § Errors.

Until then, parsers and docs **MUST** treat tokens as **single-segment** top-level keys only.

## 1. Shipped CLIs (same contract)

Each hook validates **keys on `config.meta`** for entries under one top-level list (`models:`, `seeds:`, `snapshots:`, `exposures:`, or `macros:`). The CLI **`id`** / console script name matches the hook id (e.g. **`model-allowed-meta-keys`**).

| Hook id | Resource list |
| --- | --- |
| **`model-allowed-meta-keys`** | **`models:`** |
| **`seed-allowed-meta-keys`** | **`seeds:`** |
| **`snapshot-allowed-meta-keys`** | **`snapshots:`** |
| **`exposure-allowed-meta-keys`** | **`exposures:`** |
| **`macro-allowed-meta-keys`** | **`macros:`** |

**Pre-commit (shipped):** **`language: python`**, **`entry:`** matches the hook id, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** **`--required`**, **`--forbidden`**, and optional **`--allowed`** as in **§ CLI contract** above. **`--allowed`**: omit the flag for “no allowlist mode”; pass **`--allowed`** (with a comma-separated list, possibly empty) to enable allowlist mode (**`--allowed` absent** vs **present** is distinct in Typer).

**Implementation:** **`violations_for_meta_keys`**, **`collect_violation_rows_for_resource_meta_paths`**, and **`run_allowed_meta_keys_cli`** in **`src/dbt_yaml_guardrails/hook_families/allowed_meta_keys/allowed_meta_keys_core.py`**, with thin per-resource modules under the same package.

## Implementation reuse (shared validation core)

The **`*-allowed-keys`** family uses **`violations_for_entries`** in **`allowed_keys_core.py`** with a **fixed allowlist** per resource type. **`config.meta`** rules differ (optional **`--allowed`**, no default allowlist, **forbidden** precedence), so implementations **SHOULD** use a **separate** function—e.g. **`violations_for_meta_keys`**—that encodes the **§ CLI contract** above (including **effective allow** when **`--allowed`** is set). File walking, stderr formatting, and sort order **SHOULD** stay consistent with **`yaml-handling.md`** § Errors and the patterns in **`allowed_keys_core.py`**, but the **key-check loop** for meta is its own entry point.

**Future consolidation:** A single shared abstraction for “key policy on a mapping” might replace parallel **`violations_for_entries`** and **`violations_for_meta_keys`** later; that is **optional** and not required for the first shipped hook.

**Status:** **`model-allowed-meta-keys`**, **`seed-allowed-meta-keys`**, **`snapshot-allowed-meta-keys`**, **`exposure-allowed-meta-keys`**, and **`macro-allowed-meta-keys`** are shipped with the same CLI shape and per-resource wiring.

**Related:** **[`../hooks.md`](../hooks.md)** (umbrella), **[`../yaml-handling.md`](../yaml-handling.md)** (parsing; how **`config`** and **`meta`** are represented after load), **[`allowed-keys.md`](allowed-keys.md)** (reference for flag shape and exit codes), **[`meta-keys-accepted-values.md`](meta-keys-accepted-values.md)** (dot paths under **`meta`**; value allowlists).
