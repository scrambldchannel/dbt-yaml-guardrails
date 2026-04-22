# Hook family: `*-meta-accepted-values`

Hooks in this family are named **`{resource}-meta-accepted-values`** (e.g. **`model-meta-accepted-values`**). Like **`*-allowed-meta-keys`**, the **`config`** wrapper is **implied**: validation applies to a **single key path** under **`config.meta`** (dot-separated path relative to **`meta`**). This family constrains the **value** at that path to a **fixed set of allowed strings** supplied on the CLI—not **which keys** may exist on **`meta`** (see **`allowed-meta-keys.md`** for key-name policy). The leaf may be a **single string** or a **YAML sequence of strings** (e.g. multiple domains or owners); **§ Leaf value typing** defines behavior. Other scalar types and comparison rules remain **future extensions** where noted.

**Status:** **`model`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**, and **`macro`** **`*-meta-accepted-values`** CLIs are **shipped**. Implementations should mirror **`yaml-handling.md`**, **`allowed-meta-keys.md`** stderr conventions, and per-resource wiring used elsewhere.

### Why this family is simpler than nested `*-allowed-meta-keys`

Both use **dot paths** under **`meta`**, but this family only checks **one path** per hook run: **presence** (unless **`--optional`**), **leaf shape** (string or sequence of strings), and **membership** in **`--values`** for each string. It does **not** implement a **global** rule over “what may exist anywhere under **`meta`**.”

By contrast, extending **`*-allowed-meta-keys`** with dot paths—especially with **`--allowed`**—requires defining how **“unknown”** keys work **inside nested mappings** (flattened paths, prefix rules, etc.). That is **spec-heavy** and easy to get wrong.

**Implementation priority (this repository):** Ship **`*-meta-accepted-values`** **first**. Implement **shared dot-path navigation** (and tests) here; reuse or align it when **§ Future: nested key paths** in **`allowed-meta-keys.md`** is fully specified and implemented **later**.

---

## Purpose

Projects often need **enum-like** rules on metadata, for example:

+ A **domain** field must be one of **`sales`**, **`hr`**, or **`finance`**, and must be **present** on every model (or **`domain`** may be a **list** of those strings—every element must be allowed).
+ **`owner.name`** must be one of **`annemarie`**, **`trevor`**, or **`alex`**, where **`owner`** is a mapping under **`meta`** and **`name`** is a string field.

Each hook invocation checks **one** path and **one** accepted-value list. To enforce several paths (e.g. **`domain`** and **`owner.name`**), add **multiple hook entries** in pre-commit **`hooks:`** with different **`args`**.

---

## Key path (`--key`)

+ **`--key`** is a **dot-separated path** of mapping keys **under `config.meta`**. Segments are **not** interpreted as array indices; this spec targets **mapping** navigation only.
+ Examples:
  + **`domain`** → value at **`meta["domain"]`**.
  + **`owner.name`** → value at **`meta["owner"]["name"]`** after **`meta["owner"]`** is confirmed to be a **mapping**.
+ Path is **relative to `meta`** only—do **not** prefix with **`meta.`** or **`config.`** in the flag value.

If a segment exists but is **not** a mapping when further segments remain, that is a **shape error** for that resource (violation with a clear message).

---

## Accepted values apply to **leaf** paths only

**`--values`** is evaluated against the **value at the final segment of `--key`**—the **leaf** of that path. This hook **does not** recurse into nested mappings under that key to find more strings to check; **no** “deep” or multi-field sweep of **`meta`** is implied.

+ If **`--key`** ends at a **mapping** (e.g. **`owner: { name: alex }`** and **`--key`** is **`owner`**), the leaf is **not** a string or string list → **type violation** (see **§ Leaf value typing**). To enforce an allowlist on **`name`**, extend the path so the leaf is a scalar: **`--key owner.name`**.
+ If **`--key`** ends at a **sequence of strings** (e.g. **`owner: [alex, annemarie]`** and **`--key owner`**), **`--values`** applies to **each** element; each element is a **leaf** string in that list.
+ Policy **must** be expressed in terms of **leaf** paths: one **`--key`** per terminal field you care about (or one per list-valued field), **not** by expecting a single **`--key`** to validate **inner** keys of an object at that path.

---

## Accepted values (`--values`)

+ **`--values`** is a **comma-separated** list of **allowed string values** for each **string** at the leaf (see **§ Leaf value typing**).
+ Parsing **SHOULD** match **`*-allowed-keys`** / **`*-allowed-meta-keys`**: trim whitespace around commas and each token; drop empty tokens after split.
+ Comparison is **string equality** between each trimmed string and the allowlist tokens. Default: **case-sensitive** unless a future flag documents otherwise.

---

## Required vs optional (`--optional`)

+ By default, the value at **`--key`** is **required**: if the path is **absent** (missing **`meta`**, missing intermediate key, or missing leaf), that is a **violation**.
+ If **`--optional`** is passed, a **missing** path is **not** a violation. If the path is **present**, the leaf value **must** still be one of **`--values`**.
+ Represent in Typer as a boolean flag: **`--optional`** / no flag (default **required**). In **`pre-commit` `args`**, use **`- --optional`** when the key is optional.

**Note:** “Optional” here means **“presence of the path is optional”**, not “value may be outside the list.”

---

## CLI contract

Hooks **SHOULD** use the same **exit code** pattern as **`allowed-keys.md`** (**`0`** / **`1`** / **`2`** where applicable).

| Flag | Required | Meaning |
| --- | --- | --- |
| **`--key`** | yes | Dot path under **`meta`** (see **§ Key path**). |
| **`--values`** | yes | Comma-separated allowed **string** values for the leaf (each string in a sequence is checked separately). |
| **`--optional`** | no | If set, missing path is OK; if path exists, value must match **`--values`**. |

**Invalid CLI** (e.g. missing **`--key`** or **`--values`**, or empty **`--values`** after parsing) **SHOULD** exit **`2`** with a message on stderr.

---

## Validation rules (per resource entry)

For each targeted resource in each file:

1. Resolve **`config.meta`**; if missing or **`meta`** is null / non-mapping, treat as **no meta** (see below).
2. Walk **`--key`** segment by segment from **`meta`**. Any intermediate value that is not a mapping when more segments remain → **violation** (bad shape).
3. **Leaf:**
   + If the leaf is **missing** and the key is **required** → **violation** (“missing required …” or similar).
   + If **missing** and **`--optional`** → **pass** for this rule.
   + If **present**, the leaf **must** be a **YAML string** or a **YAML sequence of strings** (see **§ Leaf value typing**). Any other type → **violation** (wrong type).
   + If **present** and a string, the value (after trim) **must** be in the **`--values`** set → otherwise **violation** (“value not allowed” or similar).
   + If **present** and a sequence, **each** element **must** be a **string**; each trimmed element **must** be in **`--values`** → otherwise **violation** (per-element message, e.g. index or value).

**Skipping files:** Same as other meta hooks: if there is **no** section for this resource type (e.g. no **`models:`**), **skip** the file without error.

---

## Leaf value typing

### String leaf

+ The leaf at **`--key`** **MAY** be a **YAML string** (in Python terms: **`str`** after load). Compare to each token in **`--values`** after **trimming** the leaf (allowlist tokens are already trimmed per **§ Accepted values**).

### Sequence of strings

+ The leaf **MAY** instead be a **YAML sequence** (flow or block list) whose **every element** is a **YAML string** (in Python terms: **`str`** after load—e.g. `ruamel.yaml` **`CommentedSeq`** of strings). **Each** element is **trimmed** and **must** be **in** **`--values`**; report **which** element failed (e.g. **index** and **value**) when useful.
+ **Empty sequences** are allowed: every element (zero of them) is vacuously in the allowlist.
+ **Nested sequences** (sequences of non-strings) or **mixed-type** sequences (e.g. string then integer) → **violation** for the non‑element(s) that are not strings.

### Other types (still out of scope)

+ **Mappings** at the leaf, **non-string scalars** (booleans, integers, floats, nulls), and **non-sequence** collections **MUST** be reported as a **type violation** (not silently coerced). Teams should **quote** values in YAML as strings when they need this hook (e.g. **`domain: "1"`** not **`domain: 1`** until a later spec version supports numbers).

### Future extensions (not v1 — **aim to specify later**)

+ **Booleans / integers / floats** — define stable equality vs **`--values`** (stringify, locale, canonical forms) and update this spec before implementations claim support.
+ **Case-insensitive** matching — optional **`--ignore-case`** (or similar) once string behavior is stable.

---

## Shipped CLIs

Each hook targets one top-level list, same pattern as **`*-allowed-meta-keys`**.

| Hook id | Resource list | Status |
| --- | --- | --- |
| **`model-meta-accepted-values`** | **`models:`** | **Shipped** |
| **`seed-meta-accepted-values`** | **`seeds:`** | **Shipped** |
| **`snapshot-meta-accepted-values`** | **`snapshots:`** | **Shipped** |
| **`exposure-meta-accepted-values`** | **`exposures:`** | **Shipped** |
| **`source-meta-accepted-values`** | **`sources:`** | **Shipped** |
| **`macro-meta-accepted-values`** | **`macros:`** | **Shipped** |

**Pre-commit:** **`language: python`**, **`entry:`** matches hook id, **`types: [yaml]`** — align **`.pre-commit-hooks.yaml`** and **`[project.scripts]`** for each shipped hook.

---

## Example `pre-commit` snippets

The snippets below are **`hooks:`** stanzas only. A full **`repos:`** / **`rev:`** example for this repository is in **[`HOOKS.md`](../../HOOKS.md)**; **`rev:`** must be **`v`** plus **`[project] version`** in **`pyproject.toml`** (currently **`v0.4.0`**).

**Required `domain` ∈ {sales, hr, finance}:**

```yaml
- id: model-meta-accepted-values
  args:
    - --key
    - domain
    - --values
    - sales,hr,finance
```

**Required `owner.name` ∈ {annemarie, trevor, alex}:**

```yaml
- id: model-meta-accepted-values
  args:
    - --key
    - owner.name
    - --values
    - annemarie,trevor,alex
```

**Optional `domain` (if present, must be in list):**

```yaml
- id: model-meta-accepted-values
  args:
    - --key
    - domain
    - --values
    - sales,hr,finance
    - --optional
```

---

## Clarifications and future extensions

1. **Multiple paths in one process** — out of scope for v1; use multiple hook stanzas.
2. **Non-string scalars at the leaf** — deferred; see **§ Leaf value typing** (Future extensions).

If anything in this spec conflicts with **`yaml-handling.md`**, **`yaml-handling.md`** wins for parse/skip/error behavior.

---

## Related

+ **[`allowed-meta-keys.md`](allowed-meta-keys.md)** — key **names** on **`meta`** (top-level today; nested paths **future**—see that spec).
+ **[`../hooks.md`](../hooks.md)** — packaging index.
+ **[`../yaml-handling.md`](../yaml-handling.md)** — loading and errors.
