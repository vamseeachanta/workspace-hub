# Plan for #2437: Prune workspace-hub baseline-check.yml + .pre-commit-config.yaml orphans from WRK→GSD migration

> **Status:** adversarial-reviewed
> **Complexity:** T1
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2437
> **Review artifacts:** `scripts/review/results/20260421T155649Z-2026-04-21-issue-2437-workspace-hub-prune.md-plan-{claude,codex,gemini}.md`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.github/workflows/baseline-check.yml` — lines 52-64 reference four deleted scripts under `scripts/agents/tests/` and `scripts/work-queue/tests/` that no longer exist (entire `scripts/agents/` directory is absent)
- Found: `.pre-commit-config.yaml` — lines 13-18 define a `validate-work-queue-state` hook pointing to `scripts/work-queue/validate-queue-state.sh` which does not exist
- Found: `scripts/work-queue/whats-next.sh` (72 lines) and `scripts/work-queue/verify-gate-evidence.py` (43 lines) — orphan stubs re-added in commit `29a66f2b7` without surrounding infrastructure
- Gap: `scripts/agents/` directory does not exist at all — all four test scripts referenced by baseline-check.yml are missing
- Gap: `scripts/work-queue/tests/` directory does not exist — the `test-user-review-evidence-writers.sh` script is missing
- Gap: `scripts/work-queue/validate-queue-state.sh` does not exist — the pre-commit hook entry is dangling

### Standards

Not applicable — this is an infrastructure prune issue, not an engineering-calculation issue.

### LLM Wiki pages consulted

No relevant wiki pages — this is a CI/hook configuration cleanup.

### Documents consulted

- `docs/ops/legacy-claude-reference-map.md` — confirms `scripts/work-queue/verify-gate-evidence.py` and `scripts/work-queue/whats-next.sh` are listed as historical/legacy paths (Sections 1 and 2) with documented redirects to current workflow surfaces
- `docs/plans/README.md` — confirmed no existing plan for #2437; parent #2424 meta-issue is documented as the CI audit umbrella
- Issue #2437 body — investigation verdict: INTENTIONAL deletion (high confidence); commit `d98492a7b` shape (10,996 deletions + 478 additions on 2026-03-25) confirms large-scale WRK→GSD migration
- Issue #2424 (parent) — open meta-issue tracking 6-of-7 ecosystem repos with red main CI; workspace-hub is one of the six

### Gaps identified

- No new code needs to be written — this is a deletion/removal plan
- The only "gap" is the absence of the dead references themselves after the prune

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21T15:50:36Z via `gh issue view`):
- `#2437` — OPEN — "chore(ci-health): prune workspace-hub baseline-check.yml + .pre-commit-config.yaml orphans from WRK→GSD migration" — labels: `cat:infrastructure`, `status:plan-approved`
- `#2424` — OPEN — "chore(ci-health): cross-repo CI audit — 6 of 7 ecosystem repos have red main CI"

**File existence** (verified 2026-04-21T15:50:36Z):
- EXISTS: `.github/workflows/baseline-check.yml`
- EXISTS: `.pre-commit-config.yaml`
- EXISTS: `scripts/work-queue/whats-next.sh` (72 lines)
- EXISTS: `scripts/work-queue/verify-gate-evidence.py` (43 lines)
- EXISTS: `docs/ops/legacy-claude-reference-map.md`
- MISSING: `scripts/agents/` (entire directory)
- MISSING: `scripts/work-queue/tests/`
- MISSING: `scripts/work-queue/validate-queue-state.sh`

**Line excerpts** (baseline-check.yml lines 52-64 — the dangling references):
```
      - name: Run shell tests (task-agents routing)
        run: |
          echo "Running shell-based routing tests..."
          bash scripts/agents/tests/test-task-agents-routing.sh

      - name: Run Stage 5 gate integration tests (WRK-1017)
        run: |
          echo "Running Stage 5 gate integration tests..."
          # Groups 1-3 only (no --sim; activation-sim requires config swap)
          bash scripts/agents/tests/test-plan-gate.sh --group 1
          bash scripts/agents/tests/test-plan-gate.sh --group 2
          bash scripts/agents/tests/test-plan-gate.sh --group 3
          bash scripts/work-queue/tests/test-user-review-evidence-writers.sh
```

**Line excerpts** (.pre-commit-config.yaml lines 13-18 — the dangling hook):
```
      - id: validate-work-queue-state
        name: validate work queue state
        entry: bash scripts/work-queue/validate-queue-state.sh
        language: system
        files: '^\.claude/work-queue/.*|^scripts/work-queue/.*|^docs/work-queue-workflow\.md$'
```

**CI status** (verified 2026-04-21T15:50:36Z via `gh run list`):
- Last 3 runs on main: all `completed` / `failure` (29 consecutive days of failure since 2026-03-25)

**Gap proofs**:
- `ls scripts/agents/ 2>&1` → "No such file or directory" — confirms all 4 referenced test scripts are missing
- `ls scripts/work-queue/tests/ 2>&1` → "No such file or directory" — confirms test-user-review-evidence-writers.sh is missing
- `ls scripts/work-queue/validate-queue-state.sh 2>&1` → "No such file or directory" — confirms pre-commit hook target is missing

**Migration commit shape** (`git log --oneline --stat d98492a7b -1`):
- `d98492a7b chore(sync): auto-sync 2026-03-25` — 478 additions, 10,996 deletions across 11,490 files

<!-- Verification: count distinct sources above: (1) issue #2437 body, (2) baseline-check.yml content, (3) .pre-commit-config.yaml content, (4) legacy-claude-reference-map.md, (5) commit d98492a7b shape, (6) GH CI run history. Current count: 6 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2437-workspace-hub-prune.md` |
| CI workflow (edit) | `.github/workflows/baseline-check.yml` |
| Pre-commit config (edit) | `.pre-commit-config.yaml` |
| Orphan stub 1 (delete) | `scripts/work-queue/whats-next.sh` |
| Orphan stub 2 (delete) | `scripts/work-queue/verify-gate-evidence.py` |
| Plan review — Claude | `scripts/review/results/20260421T155649Z-2026-04-21-issue-2437-workspace-hub-prune.md-plan-claude.md` |
| Plan review — Codex | `scripts/review/results/20260421T155649Z-2026-04-21-issue-2437-workspace-hub-prune.md-plan-codex.md` |
| Plan review — Gemini | `scripts/review/results/20260421T155649Z-2026-04-21-issue-2437-workspace-hub-prune.md-plan-gemini.md` |

---

## Deliverable

Baseline Testing CI workflow and pre-commit configuration will reference only scripts that exist, eliminating missing-script failures caused by WRK-era references and removing two orphan stub files that serve no current purpose. Remaining failures (if any) will be triaged under #2424.

---

## Pseudocode

Trivial — see files to change.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.github/workflows/baseline-check.yml` | Remove lines 52-64: the "Run shell tests (task-agents routing)" step (lines 52-55) and the "Run Stage 5 gate integration tests (WRK-1017)" step (lines 57-64). Both reference scripts under `scripts/agents/tests/` and `scripts/work-queue/tests/` that were deleted in the WRK→GSD migration and no longer exist. |
| Modify | `.pre-commit-config.yaml` | Remove lines 12-18: line 12 is the `- repo: local` header, lines 13-18 are the `validate-work-queue-state` hook body. The entire block references `scripts/work-queue/validate-queue-state.sh` (does not exist). |
| Delete | `scripts/work-queue/whats-next.sh` | 72-line orphan stub re-added in `29a66f2b7` without surrounding infrastructure. Listed as historical in `docs/ops/legacy-claude-reference-map.md` Section 2. No live caller. |
| Delete | `scripts/work-queue/verify-gate-evidence.py` | 43-line orphan stub re-added in `29a66f2b7` without surrounding infrastructure. Listed as historical in `docs/ops/legacy-claude-reference-map.md` Section 1. No live caller. |
| Update | `docs/plans/README.md` | Add index row for this plan. |

**Out of scope (recommend filing as follow-on issues under #2424 — advisory, not blocking #2437 closure):**
- `chore(ci-health): audit .planning/templates/ orphan refs from WRK→GSD migration` — the templates directory contains 10 files that may reference deleted WRK-era paths; this will require a separate audit plan
- `chore(ci-health): triage tests/work-queue/ — port to GSD or delete` — the directory contains 33 test files totaling significant code; deciding whether to port, archive, or delete requires its own scoping exercise

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| No dangling workflow refs | Workflow no longer references removed script paths | `grep -rn 'scripts/work-queue\|scripts/agents' .github/workflows/ .pre-commit-config.yaml` | Empty output (exit 1 — no matches) |
| YAML validity — workflow | Edited workflow file is valid YAML | `yamllint .github/workflows/baseline-check.yml` or `python -c "import yaml; yaml.safe_load(open('.github/workflows/baseline-check.yml'))"` | Exit 0, no parse errors |
| YAML validity — pre-commit | Edited pre-commit config is valid YAML | `yamllint .pre-commit-config.yaml` or `python -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml'))"` | Exit 0, no parse errors |
| Pre-commit passes | `pre-commit run --all-files` does not error on the removed hook | Run pre-commit locally | Exit 0 (for the removed hook — other hooks pass/fail independently) |
| Orphan stubs gone | `scripts/work-queue/` directory will be empty or absent after deleting both stubs | `ls scripts/work-queue/` | Empty directory or "No such file or directory" |
| Zero callers for orphan stubs | No live code references the deleted scripts | `grep -rn 'whats-next.sh\|verify-gate-evidence.py' .` | Only doc-only references in `docs/ops/legacy-claude-reference-map.md` (no executable callers) |
| CI workflow passes | Baseline Testing workflow runs to completion without "file not found" errors on the two modified steps | Push to main after edits | All remaining workflow steps (Python tests, lint, governance) pass or fail on their own merits — not on missing-script errors |

---

## Acceptance Criteria

- [ ] `.github/workflows/baseline-check.yml` no longer references any path under `scripts/agents/` or `scripts/work-queue/tests/`
- [ ] `.pre-commit-config.yaml` no longer references `scripts/work-queue/validate-queue-state.sh`
- [ ] `scripts/work-queue/whats-next.sh` and `scripts/work-queue/verify-gate-evidence.py` are deleted
- [ ] If `scripts/work-queue/` directory is empty after deletion, the directory itself will be removed
- [ ] Baseline Testing CI workflow completes without missing-script failures on the next push to main
- [ ] `pre-commit run --all-files` does not error on the removed `validate-work-queue-state` hook
- [ ] `docs/plans/README.md` index updated with a row for this plan
- [ ] Commit uses conventional format: `chore(ci-health): prune dangling WRK-era refs from baseline-check.yml and .pre-commit-config.yaml (#2437)`
- [ ] Follow-on issues filed as children of #2424 (advisory — not blocking #2437 closure):
  - `chore(ci-health): audit .planning/templates/ orphan refs from WRK→GSD migration`
  - `chore(ci-health): triage tests/work-queue/ — port to GSD or delete`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE (5 P3s) | Line-range discrepancy for .pre-commit-config.yaml; no grep evidence for zero callers; no YAML validity check in TDD; README.md index not in acceptance criteria; follow-on issue draft titles missing |
| Codex | MAJOR (1 P1, 4 P2s) | P1: TDD strategy too weak (relies on "next push to main"); P2: Deliverable overstates "green"; P2: review artifacts listed as existing; P2: follow-on issue titles ambiguous; P3: governance state inconsistency |
| Gemini | APPROVE | No changes needed |

**Overall result:** CONDITIONAL APPROVE — all Codex P1/P2s and Claude P3s addressed in this revision

Revisions made based on review:
- [Codex P1] Strengthened TDD Test List with 4 explicit pre-merge local verification checks: `grep` for dangling refs, `yamllint` for both YAML files, `grep` for zero callers of orphan stubs
- [Codex P2] Deliverable reworded: "eliminating missing-script failures" instead of "restoring to green"; remaining failures triaged under #2424
- [Codex P2] Artifact Map review paths marked as "(planned — will be generated during review)"
- [Codex P2] Follow-on issue draft titles added inline in Out of Scope and Acceptance Criteria; clarified as advisory (not blocking #2437 closure)
- [Codex P3] Added governance state inconsistency note to Risks section explaining pre-existing `status:plan-approved` label
- [Claude P3] Reconciled .pre-commit-config.yaml line range: line 12 is `- repo: local` header, lines 13-18 are hook body
- [Claude P3] Added `grep -rn 'whats-next.sh|verify-gate-evidence.py'` zero-callers check to TDD Test List
- [Claude P3] Added `yamllint` / `python yaml.safe_load` YAML validity checks to TDD Test List
- [Claude P3] Added `docs/plans/README.md` index update to Acceptance Criteria
- [Claude P3] Pre-specified follow-on issue titles in Out of Scope and Acceptance Criteria

---

## Risks and Open Questions

- **Risk (LOW):** Removing the two CI test steps may mask the fact that those test capabilities are permanently lost. Mitigation: the tests tested WRK-era scripts that are intentionally deleted; no current code depends on them. If equivalent GSD-era test coverage is desired, it will be a separate issue.
- **Risk (LOW):** The `scripts/work-queue/` directory may contain other files added between now and implementation. Mitigation: at implementation time, verify the directory contents before deleting the directory itself.
- **Risk (LOW):** The pre-commit hook removal means no local validation of `.claude/work-queue/` files. Mitigation: `.claude/work-queue/` is itself a WRK-era artifact; the GSD workflow does not use it. If work-queue validation is needed in the future, it will be built under the GSD model.
- **Note (governance):** Issue #2437 carries `status:plan-approved` from the planning workflow while this plan document was still in `draft` status. This is a pre-existing label applied before the adversarial review round; the label will be reconciled (confirmed or re-applied) as the plan moves through the standard planning workflow. Canonical self-approval prohibition: `CLAUDE.md` line 12 — "Batch agents: only act on `status:plan-approved` issues; never self-approve."
- **Note (halt behavior per issue comment addendum):** After adversarial review completes and `status:plan-review` is applied (Step 7 of session-entry prompt), the agent must post a comment with the plan link + label-swap command on #2437, then **end the session**. No spin-polling. Per `.claude/skills/coordination/issue-planning-mode/SKILL.md:84` — "STOP — do NOT write any implementation code."
- **Open (for follow-on issues):** `.planning/templates/` contains ~10 files that may reference deleted WRK-era paths. Auditing these is deferred to a **follow-on child issue of #2424** (title: `chore(ci-health): audit .planning/templates/ orphan refs from WRK→GSD migration`). Do NOT silently drop these — file the follow-on issue before closing #2437.
- **Open (for follow-on issues):** `tests/work-queue/` contains ~33 test files. Disposition deferred to a **follow-on child issue of #2424** (title: `chore(ci-health): triage tests/work-queue/ — port to GSD or delete`).

---

## Complexity: T1

**T1** — trivial prune of known-dead references with clear verification. Four files touched (two edits, two deletes), no new code written, acceptance = CI green + pre-commit passes.
