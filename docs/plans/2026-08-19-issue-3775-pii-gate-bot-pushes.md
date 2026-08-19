# Plan for #3775: security(ci): the Client-PII Gate is on: pull_request and cannot see bot pushes to main

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-08-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3775
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-19-plan-3775-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.github/workflows/legal-client-pii-gate.yml` — `on: pull_request` only; no `push:` or `schedule:` trigger. Confirmed present on `origin/main` as of 2026-08-19.
- Found: `.github/workflows/kanban-reconcile.yml:89-92` — commits and pushes via `git push origin "HEAD:$GITHUB_REF_NAME"` using the default `GITHUB_TOKEN`. Comment in workflow explicitly states the anti-loop split: `"the board push keeps using the default GITHUB_TOKEN so bot pushes do not retrigger CI"`.
- Found: `scripts/cron/lib/git-safe.sh:243` — `git push origin main` (via `git_q`) used by cron scripts; also uses `GITHUB_TOKEN` in CI context.
- Found: `scripts/legal/check-client-pii.py:52` — `DEFAULT_MAP` references `config/agents/.client-codename-map.local.yaml` (gitignored). The script takes file paths, not directories — a directory argument `config/ai-tools/` scans nothing and exits clean (confirmed by issue body reproduction).
- Found: 15 board and config files currently flagged by the local client-PII scan (per issue body evidence table): `boards/repo-workspace-hub.yaml`, `boards/repo-workspace-hub-naval-architecture.yaml`, `boards/repo-digitalmodel-subsea.yaml`, and 12 others.
- Found: `scripts/legal/check-client-pii.py` — `--base-ref` mode scans changed files diff. For a scheduled scan of main, the scan must enumerate tracked files, not a diff.

### Standards

| Standard | Status | Source |
|---|---|---|
| N/A — CI workflow fix, not engineering calculation | N/A | N/A |

### LLM Wiki pages consulted

- No relevant wiki pages for a CI workflow security fix.

### Documents consulted

- Issue [#3768](https://github.com/vamseeachanta/workspace-hub/issues/3768) — OPEN — `bug(dispatch): dispatch.py --write commits raw issue titles` — the writer fix. `#3775` is the gate fix; both are needed.
- Issue [#3755](https://github.com/vamseeachanta/workspace-hub/issues/3755) — upstream root cause: workspace-hub's own public issue titles carry the identifiers. This issue does NOT close #3755 scope.
- Issue [#3770](https://github.com/vamseeachanta/workspace-hub/issues/3770) — OPEN — `kanban cron mirrors 595 cards from private repos` — separate writer with the same root gap.
- Issue [#3095](https://github.com/vamseeachanta/workspace-hub/issues/3095) — parent security epic; this issue (#3775) is a sub-issue.
- `docs/plans/` — searched for "3775", "pii-gate", "bot-push", "client-pii" — no prior plan found for this issue.

### Gaps identified

**Critical design gap — `on: push` does NOT work for GITHUB_TOKEN bot pushes:**
GitHub's CI anti-loop mechanism suppresses `on: push` workflow triggers when the push was made by a workflow using the default `GITHUB_TOKEN`. This means adding `on: push:` to `legal-client-pii-gate.yml` would still miss bot pushes from `kanban-reconcile.yml`, `commit-learning-artifacts.sh`, and `auto-sync` — the exact writers this issue targets. A `schedule:` trigger (nightly scan of main's current state) is required instead of, or in addition to, a `push:` trigger.

**Script gap — directory argument exits clean:**
`check-client-pii.py` takes file paths. Passing a directory exits 0 (scans nothing). The scheduled scan job must explicitly enumerate tracked files rather than passing directories. Additionally, the script should error on a directory argument to prevent this silent failure class from recurring.

**Secret gap — scheduled scan requires the secret on main branch:**
`LEGAL_CLIENT_MAP` is provisioned as a repo secret and available to all branches. A `schedule:` trigger runs against the default branch (main) with secrets available. No provisioning gap for scheduled use.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-08-19 via `gh issue view`):
- `#3775` — OPEN — security(ci): the Client-PII Gate is on: pull_request and cannot see bot pushes to main
- `#3768` — OPEN — bug(dispatch): dispatch.py commits raw issue titles (related writer fix)
- `#3770` — OPEN — kanban cron mirrors 595 cards from private repos (related writer)
- `#3755` — OPEN — PII in 83+ tracked files (upstream root)

**File existence** (`ls` verified 2026-08-19):
- EXISTS: `.github/workflows/legal-client-pii-gate.yml`
- EXISTS: `.github/workflows/kanban-reconcile.yml`
- EXISTS: `scripts/legal/check-client-pii.py`
- MISSING (this plan creates): `.github/workflows/legal-client-pii-main-scan.yml` (new scheduled workflow)

**Line excerpts** (`grep -n` verified 2026-08-19):
```
# legal-client-pii-gate.yml
on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened, edited]
# No push: or schedule: trigger present.

# kanban-reconcile.yml:89-92
git commit -m "chore: reconcile kanban board"
if git push origin "HEAD:$GITHUB_REF_NAME"
# Comment confirms GITHUB_TOKEN is intentional for anti-loop
```

**Gap proofs:**
- `grep -c "^on:" .github/workflows/legal-client-pii-gate.yml` → `1`; `grep -A5 "^on:" ...` → confirms `pull_request:` only.
- GitHub's documented behavior: `GITHUB_TOKEN` pushes suppress `on: push` triggers to prevent loops — confirmed by kanban-reconcile.yml's own comment `"so bot pushes do not retrigger CI"`.
- `ls .github/workflows/legal-client-pii-main-scan.yml` → `No such file or directory` → confirms gap to fill.

**Reproduction proofs:**
N/A — the defect is a CI configuration gap (structural absence), not a runtime crash. The issue body reproduces the consequence: 15 files flagged by local scan while CI reports no failures on main.

<!-- Verification: distinct sources consulted: (1) .github/workflows/legal-client-pii-gate.yml, (2) .github/workflows/kanban-reconcile.yml, (3) scripts/legal/check-client-pii.py, (4) issue #3768, (5) issue #3755. Count: 5 ≥ 3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-08-19-issue-3775-pii-gate-bot-pushes.md |
| New scheduled workflow | `.github/workflows/legal-client-pii-main-scan.yml` |
| Script fix (directory guard) | `scripts/legal/check-client-pii.py` |
| Tests | `tests/legal/test_client_pii_directory_guard.py` |
| Plan review — Claude | scripts/review/results/2026-08-19-plan-3775-claude.md |
| Plan review — Codex | scripts/review/results/2026-08-19-plan-3775-codex.md |
| Plan review — Agy | scripts/review/results/2026-08-19-plan-3775-agy.md |

---

## Deliverable

A new `legal-client-pii-main-scan.yml` workflow with a `schedule:` trigger (nightly, on main) that enumerates and scans all tracked files in the repo for client identifiers — catching bot pushes the PR gate cannot see. The `check-client-pii.py` script will error loudly on a directory argument rather than scanning nothing.

---

## Pseudocode

```
# legal-client-pii-main-scan.yml
on:
  schedule:
    - cron: "0 6 * * *"   # nightly at 06:00 UTC — after bot cron windows
  workflow_dispatch:       # allow manual trigger for audit runs

jobs:
  client-pii-main-scan:
    steps:
      - checkout (full history: fetch-depth: 0)
      - install uv
      - materialize LEGAL_CLIENT_MAP from secret (strict mode if set, degrade-open if not)
      - enumerate all tracked files:
          git ls-files | grep -v ".gitignore patterns" | sort > /tmp/tracked-files.txt
      - run check-client-pii.py --files-from /tmp/tracked-files.txt --strict
          (new flag: reads file paths from stdin/file, not argv — avoids directory-as-path gotcha)
      - on failure: post job summary with flagged paths (values withheld), exit 1
      - on pass: post job summary "PASS — N files scanned, 0 violations"

# check-client-pii.py changes
def main():
    for path in args.files:
        if os.path.isdir(path):
            print(f"ERROR: {path} is a directory — pass file paths, not directories",
                  file=sys.stderr)
            sys.exit(2)   # exit 2 = usage error (distinct from 1 = found violation)
    # ... existing scan logic
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.github/workflows/legal-client-pii-main-scan.yml` | Scheduled nightly scan of main branch (catches bot pushes) |
| Modify | `scripts/legal/check-client-pii.py` | Refuse directory arguments with exit 2 instead of silently scanning nothing |
| Create | `tests/legal/test_client_pii_directory_guard.py` | TDD: confirm directory arg exits 2, file arg works normally |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_directory_arg_exits_nonzero` | directory argument is refused | `check-client-pii.py <dir>` | exit 2 with stderr message |
| `test_file_arg_scans_normally` | file argument scans as before | `check-client-pii.py <clean file>` | exit 0 |
| `test_file_arg_with_match_exits_nonzero` | file with planted identifier is detected | file containing a banned term | exit 1 |
| `test_empty_files_from_arg` | `--files-from` with empty file list exits 0 | empty file list | exit 0 (no files = no violation; log count) |

---

## Acceptance Criteria

- [ ] `legal-client-pii-main-scan.yml` exists and has a `schedule:` trigger that fires on the main branch
- [ ] Running the scheduled workflow manually (`workflow_dispatch`) against the current state of main reports each flagged file (values withheld from logs)
- [ ] `check-client-pii.py <directory>` exits 2 with a diagnostic message — never exits 0 on directory input
- [ ] All TDD tests pass: `uv run --with pytest pytest tests/legal/test_client_pii_directory_guard.py -v`
- [ ] The PR gate (`legal-client-pii-gate.yml`) is NOT modified — this issue is additive; the PR gate remains for human PRs
- [ ] The `LEGAL_CLIENT_MAP` secret is referenced correctly in the new workflow (same pattern as existing gate)
- [ ] The new workflow appears in the Actions tab and runs without configuration error on manual dispatch

---

## Risks and Open Questions

- **Risk:** The `schedule:` workflow scans all tracked files nightly but posts the result as a job summary — it does NOT prevent the push that introduced a violation (retrospective, not blocking). This is the correct trade-off: the alternative (blocking bot pushes) requires a PAT and changes the anti-loop behavior the kanban writer explicitly relies on. The fix closes the visibility gap; writer fixes (#3768, #3770) close the source gap.
- **Risk:** The nightly scan will fire against the 15 currently-flagged files from day one, producing a failing run. The fix and the writer remediation (#3768, #3770) should land together, or the new workflow should note the pre-existing state in its first run comment.
- **Risk:** `--files-from` flag is a new API surface on `check-client-pii.py`. Must verify it does not break the existing `--base-ref` invocation used by the PR gate workflow.
- **Open:** Should the scheduled scan create a GitHub issue on failure (for visibility), or is a failing workflow run + job summary sufficient? Recommend job summary only for now; escalation pattern can be added in a follow-on.
- **Open:** The `workflow_dispatch` trigger allows manual audits — is this sufficient for on-demand scanning, or should there be a `gh workflow run` wrapper in the scripts/? Recommend noting in the workflow's comment block; no script needed now.

---

## Complexity: T2

Two files to change (new workflow + script modification), one test file to create. No new modules; workflow structure follows the existing PR gate. The directory-argument fix in `check-client-pii.py` is a one-function change. T2 because of the multi-file scope and the behavioral subtlety around GITHUB_TOKEN anti-loop semantics that must be handled correctly in the workflow trigger choice.
