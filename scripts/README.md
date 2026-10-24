# Scripts Directory

> Organized by discipline for discoverability.

## Entry Points

| Script | Description |
|--------|-------------|
| `workspace` | Main workspace CLI |
| `repository_sync` | Repository synchronization |
| `setup-claude-env.sh` | Claude environment setup |
| `operations/compliance/check_governance.sh` | WRK/spec governance checks |
| `operations/compliance/audit_skill_symlink_policy.sh` | Skills link-only governance check |

## Discipline Directories

| Directory | Purpose |
|-----------|---------|
| `_core/` | Foundation utilities (bash, cli helpers) |
| `ai/` | AI tools and assessments |
| `coordination/` | Workspace coordination, routing, context |
| `data/` | Data processing and batch tools |
| `development/` | Development workflows, testing, AI review |
| `operations/` | Infrastructure, compliance, monitoring |
| `_archive/` | Deprecated scripts |

## Usage

Most scripts should be run from the workspace root:

```bash
./scripts/workspace --help
./scripts/repository_sync --help
```

## Repair-tool conventions

**Byte-preserving repairs capture bytes.** A token-only or name-only repair must
retain every unrelated byte, including CRLF, mixed endings, a UTF-8 BOM and an
absent final newline. Capture subprocess output in binary mode, decode explicitly
only for the transformation, and write bytes. UTF-8 with `surrogateescape` permits
undecodable bytes to round-trip; `utf-8-sig` removes a BOM during decoding and is
unsuitable when that signature must remain.
[Python 3.11 UTF-8 signature codec](https://docs.python.org/3.11/library/codecs.html#module-encodings.utf_8_sig)
documents that signature handling.

[Python 3.11 subprocess, Frequently Used Arguments](https://docs.python.org/3.11/library/subprocess.html#frequently-used-arguments)
specifies conversion of output line endings to LF when text mode is enabled by
`text`, `universal_newlines`, `encoding` or `errors`.
[Python 3.11 open](https://docs.python.org/3.11/library/functions.html#open)
describes newline translation and `surrogateescape`.
[Git show, Description](https://git-scm.com/docs/git-show) specifies plain blob
contents; use a blob revision rather than a commit's formatted diff.

```python
raw = subprocess.run(
    ["git", "show", f"{revision}:{relative_path}"],
    capture_output=True, check=True,
).stdout
text = raw.decode("utf-8", errors="surrogateescape")
repaired = text.replace("old", "new")  # substitute only the authorized token
output.write_bytes(repaired.encode("utf-8", errors="surrogateescape"))
```

Worked example: the three lines are `A`, `old`, `Z`, each terminated by CRLF.
Replacing only `old` with `new` gives the following hand calculation. ASCII maps
`A` to `41`, `old` to `6f 6c 64`, `new` to `6e 65 77`, and `Z` to `5a`;
CR and LF are `0d` and `0a`. These are literal byte fixture definitions, also
exercised in `tests/readiness/test_byte_capture_preservation.py`.

| Stage | Bytes | Hex |
|---|---|---|
| Input | `b"A\r\nold\r\nZ\r\n"` | `41 0d 0a 6f 6c 64 0d 0a 5a 0d 0a` |
| Wrong: `text=True`, replace, encode | `b"A\nnew\nZ\n"` | `41 0a 6e 65 77 0a 5a 0a` |
| Right: binary capture, explicit decode, replace, encode | `b"A\r\nnew\r\nZ\r\n"` | `41 0d 0a 6e 65 77 0d 0a 5a 0d 0a` |

Shell command substitution is also unsuitable for copying file content:
[Bash, Command Substitution](https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html)
specifies deletion of trailing newline characters. It does not by itself remove
embedded carriage returns. Use file redirection or a binary pipe instead of a
`$(...)` round-trip when unrelated bytes must survive.

The [capture inventory](../docs/reports/byte-capture-inventory.html) records
syntax candidates, with unresolved contracts marked `NOT_EVALUATED`. Regenerate
it using `scripts/quality/byte_capture_audit.py --report <report>
--local-map <external-map>`. The external lookup contains repository paths and
source digests; it must remain outside the repository. Every displayed file uses
an opaque code, including filenames that contain restricted identifiers.

`tests/quality/test_byte_capture_audit.py` checks the reviewed byte utilities
against `config/quality/byte-capture-allowlist.json`. Exceptions bind an exact AST
call and a nonempty reason; new or changed text captures and stale exceptions
fail. The pointer repair's metadata-only subprocess calls are the current
exceptions. Add new byte-preservation contracts to `BYTE_PRESERVING` during
review, with independent byte fixtures. Arbitrary command construction and
interprocedural data flow still require manual review.
