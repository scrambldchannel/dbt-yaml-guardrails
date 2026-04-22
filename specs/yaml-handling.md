# YAML Handling

Examples use **models** for brevity; the same rules apply to every supported dbt resource type, and *model* means an entry under the section the hook validates.

Hook-specific CLIs and flags live in the relevant **`hook-families/*.md`** spec (indexed from **`hooks.md`**). Default **allowed-key sets** per resource type for **`*-allowed-keys`** are documented in **`resource-keys.md`** and implemented in **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** (see **`resource-keys.md`** § **Models** for `model-allowed-keys`, § **Sources** default subsection for `source-allowed-keys`). Default **keys under `config`** for **`*-allowed-config-keys`** are in **`resource-config-keys.md`**, implemented in **`src/dbt_yaml_guardrails/hook_families/allowed_config_keys/resource_config_keys.py`** (see **[`hook-families/allowed-config-keys.md`](hook-families/allowed-config-keys.md)**). Product boundaries are in **`scope.md`**.

## Files

+ Use pre-commit's built-in file selection criteria to choose which files to parse and accept `yaml` and `yml` extensions
+ Concrete **`files`** / **`types`** patterns for each hook belong in that hook’s **family** spec under **`hook-families/`** (see **`hooks.md`** § Hook families)

## Parsing

+ Parse with **`ruamel.yaml`**: **preserve key order** on load (and on any future emit). If the loader reports **duplicate mapping keys** in a mapping, or the document otherwise implies the same key twice for one block, treat that as an error
+ The expectation is that users would configure pre-commit such that only resource-type-specific YAML files are passed into the hook; if a file does not contain the **expected resource section** (e.g. a hook that validates `models` entries is given a file with only `sources:`), that file should be ignored
+ Invalid YAML should raise an error
+ **Encoding:** files are read as **UTF-8**; a leading **UTF-8 BOM** is allowed and should be stripped before parsing
+ **Empty or whitespace-only files:** ignore (no violations, no error) so hooks behave when given sparse path lists
+ **Multi-document YAML** (stream with `---`): **unsupported** — if more than one document is present, raise an error
+ Top-level `version:` is **optional** (aligned with dbt Core v1.5+ resource YAML). If it is present, the value must be **`2`**, either as the **integer** `2` or the **string** `2` (YAML may yield either); values such as `2.0`, booleans, or other strings should raise an error
+ Top-level `version` is **document metadata**: hooks that validate **keys on each resource entry** (e.g. each dict under `models:`) do **not** count `version` toward those allowed/required key rules—the checks above still apply to the top-level mapping only

## dbt shape

A file may include several top-level resource keys (`models:`, `sources:`, …); each hook reads only its target section and ignores the others (this is not “one resource type per file”).

Resource types differ in shape (e.g. **`sources:`** with nested **`tables:`** vs a flat list of **`models:`** entries). Each hook’s spec must say **which node** it validates; the “named entry → dict keyed by `name`” rule applies **only** where that structure matches the target resource.

+ Add each named entry under the target resource section to a dict with that entry's name as the key (e.g. each item under `models:` keyed by its `name`; the analogous pattern for other resource types)
+ Duplicate names within the same resource section should raise an error
+ Duplicate top-level sections for the same resource type should raise an error
+ Each resource type should appear at most once at the top level of the document (e.g. a single `models:` list, a single `sources:` list)
+ If a hook is only checking one resource type, ignore entries for other resource types when parsing
+ For **`sources:`**, **`extract_source_entries`** and **`iter_source_entries`** in **`src/dbt_yaml_guardrails/yaml_handling.py`** build the same name-keyed map as for other list-shaped resources; nested **`tables:`** and other fields stay on each source entry (not expanded into separate top-level resource rows at this layer)

## Errors

These rules apply to **every** hook’s CLI unless that hook’s family spec in **`hook-families/`** (or **`hooks.md`**) explicitly overrides them.

+ Emit all violations to **stderr**
+ Use a **non-zero** exit code if there is at least one **key violation** or **YAML / parse / shape error** for a file that was not skipped (skipped empty files and files without the hook’s target section do not count as failures). **Zero** only when every processed file passes under that rule
+ **Numeric exit codes** for `*-allowed-keys` CLIs (e.g. **`0`**, **`1`**, **`2`**) are defined in **`hook-families/allowed-keys.md`**; this section defines **stderr** and **non-zero vs zero** semantics
+ Print messages in a **stable** order: file path, then resource name (or declared identifier), then key or rule id
+ Show every violation for each resource entry (per model, per source, etc., according to the hook’s target type)
+ Example line shape for an **unknown** disallowed key (exact wording may vary): `path/to/schema.yml: model 'my_model': disallowed key 'foo'`. For **legacy** keys (see **`resource-keys.md`** § Legacy / deprecated for top-level keys; **`resource-config-keys.md`** for keys under **`config`**; **`hook-families/allowed-keys.md`** / **`hook-families/allowed-config-keys.md`** § Pattern), messages **SHOULD** point to the replacement name or **`config`** location instead of using only this generic form
