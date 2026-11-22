# Codex model-pin checker

The checker rejects unexpected root `model` keys in tracked Codex configuration.
Python's standard-library `tomllib` decides document structure; line scanning is
used only for diagnostic locations. The existing root/profile distinction and
empty production allowlist are preserved.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Document parsing, diagnostics and exception maintenance for reproducible checks. |

## Scope and parsing

Run `bash scripts/enforcement/check-codex-model-pin.sh` from within the Git
repository. Git and Python with `tomllib` are required (Python 3.11 or later,
per the [standard-library documentation](https://docs.python.org/3.11/library/tomllib.html)).

Git enumerates tracked paths matching `.codex/config.toml`,
`.codex/agents/*.toml` and `config/agents/codex/*.toml`. Git pathspec wildcards
also match nested paths. The current working files are read; this is neither a
staged-blob check nor a check of untracked or user configuration.

Parsing follows [TOML v1.0.0](https://toml.io/en/v1.0.0), particularly Keys,
String, Array, Table, Inline Table and Array of Tables. Comments and strings
containing the text `model` do not define keys. A decoded root `model` key is
rejected regardless of its value's type: `model.name = "x"` and `[model]`
also create that root key. `profiles.x.model = "x"` and a `model` assignment
under `[profiles.x]` do not create a root pin. This preserves the policy encoded
in `test_non_pins_pass`; it does not validate the complete Codex schema.

Invalid TOML (including a BOM before the first key) and unreadable UTF-8 files
fail the check. Parser exception contents are withheld. Pin diagnostics include
the file, key and reason, with a best-effort line and value. A `?` location and
`<parsed root assignment>` mean parsing found a root key whose source location
could not be established by the diagnostic scanner. Locations never decide the
result.

## Exit codes

The following statuses preserve the existing checker header's interface.

| Exit code | Meaning |
| --- | --- |
| 0 | No unexpected root pins or stale exceptions; also returned by `--help`. |
| 1 | Unexpected pin, invalid TOML, stale exception, read error or Git failure. |
| 2 | Unsupported command arguments. |

Table 1. Exit-code contract tested in disposable Git repositories.

## Exceptions and inventory

`ALLOWLIST` in the checker is the sole exception list. A proposed exception will
name an exact repository-relative path, carry a documented maintainer decision,
and include a test with a tracked root pin. Each entry must match the tracked
configuration set and still contain a root `model` key. A missing tracked path
or a file without that key is a stale entry and fails the check. An invalid or
unreadable exception also fails; it cannot establish a valid exception.

The separate `Allowlisted pin inventory:` section lists only successfully
parsed exceptions with root pins, even when another file fails. It reports
`(none)` when no valid exception exists. Failure diagnostics remain outside
that inventory; an empty inventory alone does not establish a passing check.

To retire an exception, remove its root pin and its `ALLOWLIST` entry together,
then run the tests and checker. Removing only the pin leaves a stale exception;
removing only the entry exposes an unexpected pin.

At the inspected base, the allowlist is empty and the batch, explorer and worker
role configurations have no root pins. Their historical smaller-model decision
in issue 4087 is not
reopened or decided by this change. Future exceptions will appear in the
inventory rather than being silently accepted.

## Worked example

In a disposable repository, track `.codex/config.toml` containing:

```toml
matrix = [
 [1, 2],
]
model = "x"
```

The Array and Table rules of TOML v1.0.0 place `model` in the root table:
the array closes before the assignment. With no exceptions or other configs,
the command above produces:

```text
check-codex-model-pin: .codex/config.toml:?: model = <parsed root assignment> (unexpected top-level pin)
check-codex-model-pin: Allowlisted pin inventory:
  (none)
```

Exit code: `1`, from the unexpected-pin row in Table 1. The fixture
`test_toml_fixture_matrix[nested-array]` exercises this input. The fallback
location illustrates why parsing, rather than diagnostic scanning, governs
acceptance.

Run the checker tests with `python -m pytest tests/enforcement/test_check_codex_model_pin.py`.
Each matrix row records its expected status, message and structural reasoning.
