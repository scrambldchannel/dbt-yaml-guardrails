# Hook family: `config` → `meta` keys (planned)

Hooks in this family validate **keys on the mapping at `config.meta`** (nested under each resource entry’s **`config`**, where **`meta`** is present). dbt Core treats **`meta`** as an **arbitrary** key–value dictionary—there is **no Fusion-style built-in allowlist** in Core. This family lets **projects supply their own optional allowlist** via the CLI; there is **no** default allowlist in **`resource-keys.md`** (unlike **`*-allowed-keys`**).

## CLI contract (aligned with **`allowed-keys.md`** where applicable)

Hooks **SHOULD** use the same comma-separated parsing and trimming for flags as **`allowed-keys.md`**, and the same **exit code** pattern (**`0`** / **`1`** / **`2`**).

+ **`--required`** — comma-separated keys that **must** be present on **`config.meta`** for each resource entry the hook targets (after resolving **`config`**; if **`meta`** is missing or not a mapping, treat per **`yaml-handling.md`** § Errors). Default: none.

+ **`--forbidden`** — comma-separated keys that **must not** appear under **`config.meta`** (checked in addition to any allowlist rule below).

+ **`--allowed`** (optional) — comma-separated keys that **may** appear under **`config.meta`**.

### When **`--allowed` is omitted**

Only **`--required`** and **`--forbidden`** apply: there is **no** “unknown key” rule unless/until a hook documents one (e.g. only enforce presence/absence of listed keys).

### When **`--allowed` is provided**

1. Compute **effective allow** = (**`--allowed`** ∪ **`--required`**). Keys listed in **`--required`** do **not** need to be repeated in **`--allowed`**; they are **implicitly** part of the allowlist.
2. Any key **present** on **`config.meta`** that is **not** in **effective allow** is a violation (**forbidden** in the sense of “not permitted”).
3. Apply **`--forbidden`** as well: a key in **`--forbidden`** is a violation **even if** it appears in **`--allowed`** or **`--required`** (explicit deny wins), so teams can block mistakes without reshaping the allowlist.

**Skipping:** If a resource has no **`config`**, or **`config`** has no **`meta`**, behavior **SHOULD** be specified per hook (e.g. skip vs treat as missing **`meta`** when **`--required`** is non-empty); document that choice when each hook ships.

**Status:** Not yet implemented. Each resource type will get its own hook (e.g. **`model-config-meta-keys`**), with implementation-specific wiring for which YAML path is walked.

**Related:** **[`../hooks.md`](../hooks.md)** (umbrella), **[`../yaml-handling.md`](../yaml-handling.md)** (parsing; how **`config`** and **`meta`** are represented after load), **[`allowed-keys.md`](allowed-keys.md)** (reference for flag shape and exit codes).
