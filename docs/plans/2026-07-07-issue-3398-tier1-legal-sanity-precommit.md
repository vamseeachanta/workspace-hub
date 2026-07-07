# Plan for #3398: Tier-1 legal-sanity precommit wiring

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-07
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3398
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-07-06-plan-3398-codex.md | scripts/review/results/2026-07-06-plan-3398-disagreement.md

---

## Resource Intelligence Summary

Execution mode for implementation: `single-lane` for the first implementation pass. Although eventual file changes span sibling repos, the edits are coupled through one scanner contract and one readiness check, so serialization is safer than parallel writes.

### Existing repo code

- Found: `scripts/readiness/nightly-readiness.sh:615-637` implements `R-PRECOMMIT` by iterating `tier1_repos` from `scripts/readiness/harness-config.yaml`, checking sibling repos under `${WORKSPACE_HUB}/../${repo}`, and grepping each `.pre-commit-config.yaml` for `legal-sanity-scan`.
- Found: `scripts/readiness/harness-config.yaml:22-26` lists tier-1 repos: `assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`. On this host, `assetutilities`, `digitalmodel`, and `worldenergydata` exist as siblings; `assethold` is absent and is skipped by the current readiness logic.
- Found: `scripts/legal/legal-sanity-scan.sh:16-18` sets `WORKSPACE_ROOT` to the `workspace-hub` checkout, and `scripts/legal/legal-sanity-scan.sh:263-269` resolves `--repo=<name>` as `$WORKSPACE_ROOT/$TARGET_REPO`. That fails for the current sibling topology.
- Found: `../digitalmodel/.pre-commit-config.yaml` has a `legal-sanity-scan` hook, but its entry is `../scripts/legal/legal-sanity-scan.sh`, which is nested-checkout oriented and does not exist from the `digitalmodel` sibling checkout.
- Found: `../assetutilities/.pre-commit-config.yaml` and `../worldenergydata/.pre-commit-config.yaml` parse as YAML but do not contain `legal-sanity-scan`.
- Found: `scripts/readiness/remediate-harness.sh:97-101` tells operators to copy `digitalmodel`'s precommit config, which would currently reproduce the stale nested-only legal hook entry.
- Found: `../worldenergydata/.legal-deny-list.yaml` exists. `../assetutilities/.legal-deny-list.yaml` does not exist, so assetutilities will rely on the global deny list unless a separate issue adds a local deny list.
- Gap: no test currently proves `legal-sanity-scan.sh --repo=<bare-name>` works for sibling tier-1 checkouts.

### Standards

| Standard | Status | Source |
|---|---|---|
| Control-plane contract | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` requires repo control-plane surfaces such as hooks and adapters to be discoverable and consistent. |
| Enforcement gradient | applicable | `.claude/rules/patterns.md` places pre-commit hooks at Level 3 and readiness scripts at Level 2; both need test-backed behavior. |
| Parallel-first execution | applicable | `docs/standards/PARALLEL_FIRST_EXECUTION.md` supports single-lane execution when write surfaces are coupled. |
| Legal scanning reference | applicable but stale | `.claude/docs/legal-scanning.md` documents CP-stream hook wiring for `digitalmodel`, `client-d`, and `mkt-a`, but not `assetutilities` or `worldenergydata`, and it assumes nested/submodule path semantics. |

### LLM Wiki pages consulted

- No relevant wiki pages. This is a harness/legal-scan integration issue.

### Documents consulted

- Issue [#3398](https://github.com/vamseeachanta/workspace-hub/issues/3398) - reports `R-PRECOMMIT` failing for `assetutilities` and `worldenergydata`.
- `docs/plans/README.md` - confirms planning, review, approval, and index requirements.
- `.claude/docs/legal-scanning.md` - describes intended legal-sanity precommit behavior and current documented hook shape.
- `scripts/data/drive-index-search/search.py "R-HOOKS R-PRECOMMIT legal-sanity pre-commit" --json --caller plan-resource-intel` - returned no relevant drive-file hits; no off-repo document evidence is used.

### Gaps identified

- `assetutilities` lacks a `legal-sanity-scan` pre-commit hook entry.
- `worldenergydata` lacks a `legal-sanity-scan` pre-commit hook entry.
- The existing `digitalmodel` hook entry is path-stale for sibling checkout topology.
- `legal-sanity-scan.sh --repo=<bare-name>` fails when the target repo is a sibling rather than a child/submodule under `workspace-hub`.
- `R-PRECOMMIT` currently checks for the string `legal-sanity-scan` only; it does not verify that the hook entry can resolve the scanner path or repo path.
- The scanner currently accepts raw `--repo=*` values without a fail-closed basename/traversal contract.
- The remediation script points operators at a stale donor config pattern.

### Evidence

**Issue status** (verified 2026-07-07 via `gh issue view 3398`):
- `#3398` - OPEN - `chore(harness): add legal-sanity precommit entries for assetutilities and worldenergydata`; labels include `status:needs-plan` and `lane:codex`.

**File existence** (verified 2026-07-07):
- EXISTS: `scripts/legal/legal-sanity-scan.sh`
- EXISTS: `scripts/readiness/nightly-readiness.sh`
- EXISTS: `scripts/readiness/harness-config.yaml`
- EXISTS: `../assetutilities/.pre-commit-config.yaml`
- EXISTS: `../worldenergydata/.pre-commit-config.yaml`
- EXISTS: `../digitalmodel/.pre-commit-config.yaml`
- EXISTS: `../worldenergydata/.legal-deny-list.yaml`
- MISSING: `../assetutilities/.legal-deny-list.yaml`
- ABSENT CHECKOUT: `../assethold`

**Line excerpts**:

```text
scripts/readiness/nightly-readiness.sh:615-637
check_r_precommit() {
  ...
  local repo_dir="${WORKSPACE_HUB}/../${repo}"
  [[ -d "$repo_dir" ]] || continue
  local pc="${repo_dir}/.pre-commit-config.yaml"
  ...
  if ! grep -q "legal-sanity-scan" "$pc" 2>/dev/null; then
    issues_local+=("${repo}:legal-sanity-scan.sh entry missing")
  fi
}
```

```text
scripts/legal/legal-sanity-scan.sh:263-269
if [[ -n "$TARGET_REPO" ]]; then
  repo_path="$WORKSPACE_ROOT/$TARGET_REPO"
  if [[ ! -d "$repo_path" ]]; then
    echo "ERROR: Repository not found: $repo_path" >&2
    exit 2
  fi
```

```text
../digitalmodel/.pre-commit-config.yaml
- id: legal-sanity-scan
  entry: ../scripts/legal/legal-sanity-scan.sh
  args: [--repo=digitalmodel]
```

**Reproduction proofs**:

```text
$ bash scripts/readiness/nightly-readiness.sh 2>&1 | tail -60
FAIL R-PRECOMMIT: assetutilities:legal-sanity-scan.sh entry missing worldenergydata:legal-sanity-scan.sh entry missing
--- Readiness: 2/24 checks failed
```

```text
$ python -c "import yaml, pathlib; ... safe_load(... .pre-commit-config.yaml)"
assetutilities .pre-commit-config.yaml repos 5
worldenergydata .pre-commit-config.yaml repos 11
digitalmodel .pre-commit-config.yaml repos 16
```

```text
$ bash scripts/legal/legal-sanity-scan.sh --repo=assetutilities --diff-only
ERROR: Repository not found: <workspace-hub>/assetutilities

$ bash scripts/legal/legal-sanity-scan.sh --repo=worldenergydata --diff-only
ERROR: Repository not found: <workspace-hub>/worldenergydata
```

```text
$ bash scripts/legal/legal-sanity-scan.sh --repo=../worldenergydata --diff-only
RESULT: PASS - no violations found

$ bash scripts/legal/legal-sanity-scan.sh --repo=../assetutilities --diff-only
RESULT: PASS - no violations found
```

The `--repo=../...` commands above are diagnostic only. The implementation must reject traversal-like repo arguments and make bare names such as `--repo=worldenergydata` resolve safely.

```text
$ Test-Path ../digitalmodel/../scripts/legal/legal-sanity-scan.sh
False
$ Test-Path ../digitalmodel/../workspace-hub/scripts/legal/legal-sanity-scan.sh
True
```

Reproduced at: 2026-07-07. Failure mode observed matches issue claim: YES, with an additional runtime-path defect discovered during reproduction.

Source count: 10 distinct sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-07-issue-3398-tier1-legal-sanity-precommit.md` |
| Scanner tests | `scripts/legal/tests/` or `tests/legal/` focused test file for `legal-sanity-scan.sh` path resolution |
| Readiness tests | `tests/work-queue/test-harness-readiness.sh` or `tests/readiness/` focused readiness regression |
| Scanner implementation | `scripts/legal/legal-sanity-scan.sh` |
| Readiness implementation | `scripts/readiness/nightly-readiness.sh` |
| Sibling config | `../assetutilities/.pre-commit-config.yaml` |
| Sibling config | `../worldenergydata/.pre-commit-config.yaml` |
| Sibling config audit/update | `../digitalmodel/.pre-commit-config.yaml` |
| Docs | `.claude/docs/legal-scanning.md` |
| Plan index | `docs/plans/README.md` |
| Plan review - Codex | `scripts/review/results/2026-07-06-plan-3398-codex.md` |
| Plan review - Disagreement | `scripts/review/results/2026-07-06-plan-3398-disagreement.md` |

---

## Deliverable

Tier-1 sibling repos present on this machine will have runtime-valid legal-sanity precommit wiring, and `R-PRECOMMIT` will pass because the hook entries are both declared and executable under the sibling checkout topology.

---

## Pseudocode

```text
function resolve_target_repo(target_repo):
    if target_repo is empty:
        return WORKSPACE_ROOT
    reject target_repo unless it is a bare repo name matching [A-Za-z0-9._-]+
    reject target_repo containing /, \, .., drive prefixes, or absolute path syntax
    candidates = [
        WORKSPACE_ROOT / target_repo,
        WORKSPACE_ROOT / ".." / target_repo,
    ]
    for candidate in candidates:
        canonical = realpath(candidate)
        if canonical is an existing directory and canonical basename == target_repo:
            return canonical candidate
    fail with a message listing attempted candidates

function check_r_precommit:
    for repo in harness tier1_repos:
        repo_dir = WORKSPACE_HUB / ".." / repo
        skip absent checkout
        require .pre-commit-config.yaml
        parse the legal-sanity-scan hook block
        require hook id, entry, language, args, and pass_filenames contract
        resolve hook entry relative to repo_dir and require it exists/executably invokes the scanner
        require args use a bare --repo=<repo> matching the repo being checked
        fail R-PRECOMMIT if the hook is declared but dead
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/legal/legal-sanity-scan.sh` | Resolve `--repo=<bare-name>` against sibling checkouts when nested/submodule path is absent. |
| Modify | `scripts/readiness/nightly-readiness.sh` | Make `R-PRECOMMIT` validate the actual hook entry path/args instead of only grepping for `legal-sanity-scan`. |
| Modify | `scripts/readiness/remediate-harness.sh` | Replace stale "copy digitalmodel config" guidance with the new sibling-safe legal hook contract. |
| Modify | `tests/work-queue/test-harness-readiness.sh` or add focused Python tests | Preserve existing `R-PRECOMMIT` missing-entry failure and add pass/fail cases for executable hook entries. |
| Add/modify | `scripts/legal/tests/` or `tests/legal/` | Add regression for sibling repo resolution using temporary workspace/repo fixtures. |
| Modify | `../assetutilities/.pre-commit-config.yaml` | Add local legal-sanity hook entry. |
| Modify | `../worldenergydata/.pre-commit-config.yaml` | Add local legal-sanity hook entry. |
| Modify | `../digitalmodel/.pre-commit-config.yaml` | Update existing legal-sanity hook entry if needed so it works from sibling topology. |
| Modify | `.claude/docs/legal-scanning.md` | Document sibling checkout hook entry and the newly covered tier-1 repos. |
| Update | `docs/plans/README.md` | Add this plan to the index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_legal_sanity_repo_resolution_supports_sibling_checkout` | `--repo=worldenergydata` can resolve a sibling repo when `workspace-hub/worldenergydata` is absent. | Temporary parent with copied `workspace-hub/scripts/legal/legal-sanity-scan.sh`, minimal global deny list, initialized sibling `worldenergydata/` git repo, and no real-checkout dependency. | Scanner exits 0 in `--diff-only` mode and reports the sibling canonical path. |
| `test_legal_sanity_repo_rejects_traversal_arguments` | `--repo` is fail-closed for traversal and absolute path attempts. | `--repo=../worldenergydata`, POSIX absolute-path-like values, Windows-drive-like values, and names containing separators. | Exit 2 before scanning; error does not scan outside the allowed candidate roots. |
| `test_legal_sanity_repo_resolution_reports_attempted_paths` | Missing bare-name repo errors are actionable and do not silently pass. | Missing `--repo=does-not-exist`. | Exit 2 with attempted nested and sibling bare-name paths. |
| `T10` existing shell test | Missing legal hook entry still fails `R-PRECOMMIT`. | Sibling `assetutilities` with config lacking legal hook. | `R-PRECOMMIT` fails. |
| `test_r_precommit_fails_dead_legal_hook_entry` | A grep-visible but non-existent legal hook entry cannot pass readiness. | Temp sibling repo with `id: legal-sanity-scan` but `entry: ../scripts/legal/legal-sanity-scan.sh` that does not exist. | `R-PRECOMMIT` fails with dead-entry detail. |
| `test_r_precommit_passes_when_present_siblings_have_executable_legal_hook_entries` | `R-PRECOMMIT` passes when present tier-1 siblings have legal hook entries that resolve from each repo root and use bare `--repo=<repo>` args. | Temp siblings for `assetutilities` and `worldenergydata` with sibling-safe legal hook entries. | `R-PRECOMMIT` line starts with `OK`. |
| `test_tier1_precommit_configs_parse_after_hook_insert` | Modified sibling configs remain valid YAML. | Real `assetutilities`, `worldenergydata`, and updated `digitalmodel` precommit configs. | PyYAML parses all files. |
| `test_remediate_harness_no_stale_digitalmodel_copy_guidance` | Remediation guidance cannot recreate the stale nested-only hook path. | `scripts/readiness/remediate-harness.sh`. | Text no longer instructs copying digitalmodel config; it names the sibling-safe hook entry contract. |

---

## Acceptance Criteria

- [ ] Tests are written first and fail for the current sibling-resolution and missing-hook states.
- [ ] `uv run pytest <focused legal/readiness tests> -q` and/or `bash tests/work-queue/test-harness-readiness.sh` pass after implementation.
- [ ] `bash scripts/legal/legal-sanity-scan.sh --repo=assetutilities --diff-only` passes from `workspace-hub`.
- [ ] `bash scripts/legal/legal-sanity-scan.sh --repo=worldenergydata --diff-only` passes from `workspace-hub`.
- [ ] `bash ../workspace-hub/scripts/legal/legal-sanity-scan.sh --repo=assetutilities --diff-only` passes from the `assetutilities` sibling checkout.
- [ ] `bash ../workspace-hub/scripts/legal/legal-sanity-scan.sh --repo=worldenergydata --diff-only` passes from the `worldenergydata` sibling checkout.
- [ ] A validation command parses each touched `.pre-commit-config.yaml`, resolves the `legal-sanity-scan` hook entry from that repo root, verifies the entry exists, verifies args include bare `--repo=<repo>`, and runs the hook command in `--diff-only` mode.
- [ ] `bash scripts/readiness/nightly-readiness.sh` no longer fails `R-PRECOMMIT` on ace-win-2.
- [ ] `assetutilities`, `worldenergydata`, and any touched `digitalmodel` changes are committed and pushed to their owning repositories, with issue comments posted where appropriate.
- [ ] `bash scripts/legal/legal-sanity-scan.sh --diff-only` passes in `workspace-hub`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex r1 | MAJOR | Readiness validation was optional/grep-only; ACs did not execute actual precommit hook wiring; temp fixture isolation was underspecified; resolver lacked traversal validation; remediation guidance would recreate stale config. |
| Codex r2 | UNAVAILABLE | Codex CLI stdin regression/timeout after the r1 plan patch; no usable review signal. The r1 MAJOR findings remain the latest substantive review evidence. |

**Overall result:** FAIL - re-draft required before approval.

Revisions made based on review:
- Made `R-PRECOMMIT` hook-entry validation mandatory and added `scripts/readiness/nightly-readiness.sh` to the change set.
- Added fail-closed `--repo` basename/traversal validation to the scanner contract and tests.
- Specified scanner fixture isolation by copying the scanner into a temporary `workspace-hub/scripts/legal/` tree.
- Added actual `.pre-commit-config.yaml` hook-entry parse/resolve/run acceptance criteria.
- Added `scripts/readiness/remediate-harness.sh` to prevent stale remediation guidance from recreating the defect.
- Recorded the second Codex attempt as unavailable; no approval-state movement because no no-MAJOR review exists.

---

## Risks and Open Questions

- **Risk:** editing sibling repo precommit configs without scanner resolution would produce hooks that look present but fail at runtime. This plan makes scanner resolution a required part of the issue.
- **Risk:** assetutilities lacks a local `.legal-deny-list.yaml`. The hook can still use the global deny list, but a local deny-list follow-up may be needed if assetutilities has repo-specific legal terms.
- **Risk:** full-repo legal scans may expose historical violations. The implementation should validate `--diff-only` first and avoid changing hook scan breadth without explicit review.
- **Open:** whether to update `digitalmodel` in this same issue or file a separate follow-up if reviewers consider it out of scope. Recommendation: include the path-only update here because it is the same runtime legal-hook contract and avoids leaving a known broken hook.

---

## Complexity: T2

**T2** - multi-file, multi-repo harness/config work with tests and a discovered runtime path-resolution defect.
