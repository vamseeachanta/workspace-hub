# Empty scan targets and retired scan evidence

The resolver defect described in issue #3935 can produce an empty scan target
despite a successful process status. The scanner has since been removed.
Its historical results do not establish coverage or publication readiness.
The applicable method is [manual final-report verification](../FINAL_REPORT_VERIFICATION.md).

## Revision history

| Revision | Date | What changed and why |
|---|---|---|
| Initial | 2026-10-22 | Record the empty-target derivation, retirement regressions and the remaining evidence limits. |

## Basis and scope

- Issue #3935 identifies the incompatible resolver and caller contracts.
- Related issues #3804, #3871 and #3933 describe the same failure in named,
  sibling and registered-root lookup.
- The historical script at the parent of commit `d6f08dd9c` documents
  `--repo=<name>`, `--all` and `LEGAL_SCAN_REPO_ROOTS` as its interfaces.
- The retirement decision dated 2026-10-03, recorded in
  `FINAL_REPORT_VERIFICATION.md` and issue #3936, supersedes runtime repairs.
  It also rejects old scanner results as evidence.

No scanner, resolver, identifier gate or automatic review receipt is introduced
by this example. Engineering equations, empirical coefficients and numerical
acceptance limits do not apply to this software contract.

## Worked example: the incompatible contracts

**Inputs.** A requested directory exists. An earlier resolver prints its result;
a later definition replaces it and only assigns a variable. The caller captures
standard output using command substitution. The following shell example uses
synthetic content in a supplied temporary directory:

```bash
: "${TMPDIR:?Set a temporary directory before running this example}"
requested="$TMPDIR/legal-scan-example/registered root"
mkdir -p "$requested"

resolve_repo_path() { printf '%s\n' "$1"; }
resolve_repo_path() { RESOLVED_REPO_PATH="$1"; }
captured="$(resolve_repo_path "$requested")"

if [[ -d "$requested" && -z "$captured" ]]; then
  printf 'requested directory: exists\n'
  printf 'captured directory: empty\n'
  printf 'scan coverage: NOT_EVALUATED\n'
fi
```

**Method.** The later function body contains no output operation. Its standard
output is therefore the empty string. Command substitution captures that empty
string; assigning a variable inside the substitution does not supply standard
output. The existence of the requested directory does not change this result.

**Answer.** The output is:

```text
requested directory: exists
captured directory: empty
scan coverage: NOT_EVALUATED
```

The resolved-directory eligibility condition is `nonempty(path) AND is_directory(path)`.
The first term is false, so the condition is false regardless of the second term.
There is no established scan coverage. A successful resolver exit or a historical
PASS message cannot change that conclusion. This is a hand derivation from the
two function bodies, independent of scanner implementation or fixture results.

## Regression coverage after retirement

`tests/legal/test_legal_scan_resolver_retirement.py` checks the legacy forms:

| Input | Required observation |
|---|---|
| Named, empty or missing `--repo` argument | Retired entry point is absent; invocation cannot report success or PASS. |
| `--all` with absent or empty registration | No successful empty-target scan evidence. |
| `--all` or named lookup with an existing registered root | Registration cannot revive the removed entry point. |
| `--all` with missing or mixed existing/missing roots | No fallback PASS; synthetic input remains unchanged. |

The temporary registered directory contains a synthetic input file. The tests
check its contents and the complete temporary file set after invocation. They
check entry-point absence before executing the shell, so a restored scanner
fails the regression without being run against repository data. Tests do not
depend on a particular shell error number.

`tests/legal/test_identifier_gate_retirement.py` also checks hook command entries
and arguments independently of their IDs, and workflow run commands in both
`.yml` and `.yaml` files. Existing independent secret-check assertions remain.

These are retirement regressions. They do not test a working resolver, content
matching, Windows path translation or deployed copies in other repositories.
Those runtime checks are **NOT_EVALUATED** because their executable was removed.

## Manual final-report example

**Inputs.** An outgoing report has a historical empty-path PASS log and an
attachment that has not been reviewed.

**Method.** Identify the audience, destination and exact artifact set. Review
the actual report and attachment for rights, qualification and the applicable
independent secret checks, using the existing final-report checklist. Exclude
the historical scanner result from the supporting evidence.

**Answer.** Record `needs-review` while the attachment or required evidence is
unreviewed. Scan coverage remains `NOT_EVALUATED`. A `verified` manual verdict
requires review of the complete current artifact set; a removed scanner's exit
status supplies no substitute. A code-only change without an outgoing report
uses the policy's `not-applicable: no report` disposition and reports its actual
test results separately.

## Remaining work

Runtime resolver repair is superseded by retirement. Any future scanner design
would require a separate scope decision, a single resolver contract, nonempty
existing-directory validation and explicit handling of no eligible targets.
No issue closure, cross-repository deployment or publication clearance follows
from these local tests.
