# Supplied plugin inventory contract

`plugin_inventory.py` provides `parse_inventory(payload, *, input_format)` and
`format_inventory(payload, *, input_format)`. Both take supplied text and perform
no collection, file access, path resolution, process execution or publication.
The format must be explicitly selected. The existing audit's inline `plugins`
mapping in `claude-plugin-audit.sh` is the structural starting point; this parser
adds strict validation and explicit incomplete evidence. It is not integrated
with that audit, live collection or scheduled parity reporting.

## Installed JSON

`input_format="installed-json"` accepts a JSON object with a required `plugins`
object. Each key is a plugin ID; each value is a nonempty array of installation
objects. The optional top-level `version` is the installed-envelope revision:
only the integer `2` is supported by this contract. An absent revision uses the
same mapping shape. Other revisions require a separately reviewed adapter.
This revision number is a format selector, not a measured quantity.

```json
{
  "version": 2,
  "plugins": {
    "alpha@sample": [
      {
        "version": "fixture-a",
        "scope": "user",
        "enabled": true,
        "installPath": "plugins/alpha"
      }
    ]
  }
}
```

These are synthetic contract examples, not operational inventory. Plugin IDs and
scopes are nonempty, printable strings without whitespace. Scopes are preserved
as opaque labels, including labels unknown to this module. Installation version
and path are nonempty printable strings without surrounding whitespace; internal
spaces and Unicode are preserved. Paths are opaque input data, never normalized,
expanded or checked. Enabled state must be a JSON boolean when known.

`version`, `enabled` and `installPath` may be absent or `null`. Each remains `null`
in the output and makes the inventory `partial`. The parser never assumes an
installed plugin is enabled. A missing ID or scope is rejected because the
installation cannot be identified. An explicit empty `plugins` object is a
complete empty inventory; a missing or mistyped `plugins` member is rejected.
Other metadata is ignored, although duplicate object keys and nonfinite JSON
constants anywhere in the document are rejected.

## Captured list text

`input_format="captured-list"` accepts only the following narrow grammar. It does
not promise compatibility with arbitrary provider releases or terminal output.
This example defines the accepted spelling, indentation, marker and status
symbols; no provider command is run or required to test it.

```text
Installed plugins:

  ❯ alpha@sample
    Version: fixture-a
    Scope: user
    Status: ✔ enabled
    Path: plugins/alpha
```

The header is required. Each record starts with two spaces, `❯`, one space and
its ID. Each field starts with four spaces, its exact name, a colon and a space.
Field order and record order may vary. `Scope` is required; `Version`, `Status`
and `Path` may be omitted and then have the same unknown semantics as JSON.
Status is exactly `✔ enabled` or `✘ disabled`. Blank lines and CRLF line endings
are accepted. Values are validated and preserved as in JSON. Unknown lines,
fields, repeated fields, status spellings, terminal escapes and trailing notices
are rejected rather than silently discarded. A header without records is
incomplete, not empty. The sole empty-list sentinel is `No plugins installed.`
with optional surrounding whitespace. Arbitrary text and JSON supplied under the
wrong format selector are rejected.

## Identity, output and diagnostics

An identity is `(plugin_id, scope)`. The same ID in distinct scopes remains
separate. Repeated identity pairs are rejected even if the records agree; this
contract cannot disambiguate multiple installations within the same scope.
A future consumer needing that distinction must extend the identity contract.

`parse_inventory` returns an object with `status` (`complete` or `partial`) and
`plugins`. Each record contains exactly `plugin_id`, `version`, `scope`, `enabled`
and `install_path`. Complete means that the supplied supported structure contains
all these values, not that a collection succeeded, is current or proves parity.
An incomplete installation is retained; it never becomes an empty inventory.

Records sort by ID then scope using Unicode code-point order. The formatter uses
sorted JSON keys, compact separators, unescaped Unicode and a trailing newline.
Equivalent reordered input therefore produces byte-identical UTF-8 output.
Literal expected output in the regression suite is hand-written from the examples
and this ordering rule, independently of the formatter implementation.

`InventoryError` contains only a fixed rule name and writes nothing to output:

| Rule | Rejection |
|---|---|
| `inventory.input` | Payload is not text |
| `inventory.format` | Unsupported format selector |
| `inventory.json` | Invalid JSON or a nonfinite constant |
| `inventory.duplicate-key` | Repeated JSON object key |
| `inventory.shape` | Unsupported envelope revision or mapping shape |
| `inventory.record` | Invalid identity, field type or field value |
| `inventory.duplicate` | Repeated identity within a scope |
| `inventory.text` | Unsupported captured-list syntax |
| `inventory.incomplete` | Captured header without records |

Consumers must handle rejection as invalid evidence. Error messages contain no
input values or paths. Returned records intentionally contain supplied values;
publication and redaction are the caller's responsibility.

## Regression check

Run the focused suite with pytest, without cache output:

```sh
uv run --no-project --with pytest python -m pytest tests/maintenance/test_plugin_inventory.py -q -rA -p no:cacheprovider
```

Fixtures use only synthetic labels and relative paths. Expected values follow
literal examples or direct enumeration, rather than values calculated by the
parser under test. No provider CLI, network, scheduler or package operation is
part of parsing or its tests. Pytest itself is supplied by the test environment.

## Plan-lite

- Scope will remain limited to the supplied-evidence parser and deterministic
  formatter in `plugin_inventory.py`, this accepted-input contract and the
  synthetic offline suite in `tests/maintenance/test_plugin_inventory.py`.
- Acceptance will require the focused regression command above to pass, including
  distinct plugin scopes, deterministic ordering and rule-only diagnostics.
  Literal expected outputs and cross-format comparisons will check the contract;
  direct file checks will cover syntax, register, secrets and whitespace.
- Live collection, provider-release compatibility and scheduled parity-report
  integration will require separate work; this slice will not establish them.
