# Hook family: `*-allowed-meta-keys` (planned)

Hooks in this family are named **`{resource}-allowed-meta-keys`** (e.g. **`model-allowed-meta-keys`**). The **`config`** wrapper is **implied** by the family name: each hook validates **keys on the `meta` mapping** nested under that resource entry’s **`config`** (i.e. **`config.meta`** in property YAML—do not repeat **`config`** in the hook id).

dbt Core treats **`meta`** as an **arbitrary** key–value dictionary—there is **no Fusion-style built-in allowlist** in Core. This family lets **projects supply their own optional allowlist** via the CLI; there is **no** default allowlist in **`resource-keys.md`** (unlike **`*-allowed-keys`**).

## CLI contract (aligned with **`allowed-keys.md`** where applicable)

Hooks **SHOULD** use the same comma-separated parsing and trimming for flags as **`allowed-keys.md`**, and the same **exit code** pattern (**`0`** / **`1`** / **`2`**).

+ **`--required`** — comma-separated keys that **must** be present on **`meta`** (under **`config`**) for each resource entry the hook targets. If **`config`** or **`meta`** is missing or **`meta`** is not a mapping, treat per **`yaml-handling.md`** § Errors. Default: none.

+ **`--forbidden`** — comma-separated keys that **must not** appear under **`meta`** (checked in addition to any allowlist rule below).

+ **`--allowed`** (optional) — comma-separated keys that **may** appear under **`meta`**.

### When **`--allowed` is omitted**

Only **`--required`** and **`--forbidden`** apply: there is **no** “unknown key” rule unless/until a hook documents one (e.g. only enforce presence/absence of listed keys).

### When **`--allowed` is provided**

1. Compute **effective allow** = (**`--allowed`** ∪ **`--required`**). Keys listed in **`--required`** do **not** need to be repeated in **`--allowed`**; they are **implicitly** part of the allowlist.
2. Any key **present** on **`meta`** that is **not** in **effective allow** is a violation (**forbidden** in the sense of “not permitted”).
3. Apply **`--forbidden`** as well: a key in **`--forbidden`** is a violation **even if** it appears in **`--allowed`** or **`--required`** (explicit deny wins), so teams can block mistakes without reshaping the allowlist.

**Skipping:** If a resource has no **`config`**, or **`config`** has no **`meta`**, behavior **SHOULD** be specified per hook (e.g. skip vs treat as missing **`meta`** when **`--required`** is non-empty); document that choice when each hook ships.

## Implementation reuse (shared validation core)

The **`*-allowed-keys`** family uses **`violations_for_entries`** in **`allowed_keys_core.py`** with a **fixed allowlist** per resource type. **`config.meta`** rules differ (optional **`--allowed`**, no default allowlist, **forbidden** precedence), so implementations **SHOULD** use a **separate** function—e.g. **`violations_for_meta_keys`**—that encodes the **§ CLI contract** above (including **effective allow** when **`--allowed`** is set). File walking, stderr formatting, and sort order **SHOULD** stay consistent with **`yaml-handling.md`** § Errors and the patterns in **`allowed_keys_core.py`**, but the **key-check loop** for meta is its own entry point.

**Future consolidation:** A single shared abstraction for “key policy on a mapping” might replace parallel **`violations_for_entries`** and **`violations_for_meta_keys`** later; that is **optional** and not required for the first shipped hook.

**Status:** Not yet implemented. Each resource type will get its own hook (e.g. **`model-allowed-meta-keys`**), with implementation-specific wiring for which YAML path is walked.

**Related:** **[`../hooks.md`](../hooks.md)** (umbrella), **[`../yaml-handling.md`](../yaml-handling.md)** (parsing; how **`config`** and **`meta`** are represented after load), **[`allowed-keys.md`](allowed-keys.md)** (reference for flag shape and exit codes).
