# Hook family: `config` → `meta` key allowlists (planned)

Hooks in this family will validate **keys on the mapping at `config.meta`** (nested under each resource entry’s **`config`**, where present), using a **fixed allowlist per resource type** plus optional **`--required`** / **`--forbidden`** flags, analogous to **[`allowed-keys.md`](allowed-keys.md)** but scoped to **`meta`** instead of top-level resource keys.

**Status:** Not yet implemented. When added, each resource type will get its own hook (e.g. `model-config-meta-allowed-keys`), with **`resource-keys.md`** (or a dedicated doc) as the allowlist source for **meta** keys per **§**, and implementation constants alongside **`resource_keys.py`** or a sibling module.

**Related:** **[`../hooks.md`](../hooks.md)** (umbrella), **[`../yaml-handling.md`](../yaml-handling.md)** (parsing; how **`config`** and **`meta`** are represented after load), **[`allowed-keys.md`](allowed-keys.md)** (pattern for the top-level key family).
