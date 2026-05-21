> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-21
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_ci_baseline_red_not_pr_broken.md

---
name: feedback-ci-baseline-red-not-pr-broken
description: Pre-existing main-branch CI failures can falsely implicate a PR — always check upstream baseline before assuming your PR caused the red state.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 51bb2baf-ddde-4427-8c87-f5ce8bfa1400
---

When a PR shows red CI, do not assume the failures are caused by the PR. Pre-existing main-branch CI failures will inherit to every new PR, creating false-positive panic and triggering unnecessary investigations into the wrong subsystem.

**Why:** 2026-05-15 PR #413 in worldenergydata showed 3 test failures (`test_repo_structure_contract` complaining about `logs/dashboard_audit.jsonl`, two NDBC metocean integration tests). My PR only touched `data/modules/vessel_fleet/` — completely unrelated subsystems. Verification via `gh run list --branch main` confirmed main itself had been red since PR #410 merge — at least 2 prior commits. The failures were pre-existing repo-structure-contract drift + likely-external-API-flakiness, not regressions from PR #413. Without checking baseline, the natural assumption ("CI is red, my PR did something") would have wasted ~30 min investigating vessel_fleet code that wasn't the cause.

**How to apply:**

1. When a PR shows red CI, **before** assuming PR-caused regression, run:
   ```bash
   gh run list --repo <owner>/<repo> --branch main --workflow CI --limit 3 --json conclusion,headSha,displayTitle
   ```
2. If the 2-3 most recent main runs are also failing: **the failures predate your PR**. Investigate baseline-fix scope separately.
3. If main is green and PR is red: now it's plausibly your PR. Continue normal failure-triage.
4. Document the baseline state in the PR description so reviewers don't repeat the investigation.

**Distinction from related memories:**

- [[feedback_qg_maxfail_undercounts]] — local QG-style runs underreport failures vs CI. This new memory is the inverse symptom: CI-red can falsely implicate a PR. Both teach: don't trust the surface signal; trace it to its actual source.
- [[feedback_mock_vs_live_invocation_divergence]] — mocked tests pass while live tests fail. This new memory: CI tests fail for unrelated reasons. Both fall under "verify the failure mode, not just the failure flag."

**Operational rule for admin-merge decisions:** if the user authorizes admin-merge despite red CI, document the baseline-red state explicitly in the merge-justification comment. Per [[feedback_admin_flag_vs_rulesets_api]] the ruleset-API toggle is the mechanic; the *justification* should always cite "baseline-red since commit X" if applicable.
