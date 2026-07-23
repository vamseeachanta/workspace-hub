> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-23
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_non_required_checks_hide_regressions.md

---
name: feedback_non_required_checks_hide_regressions
description: "Required-checks-green ≠ nothing broke; a content-deleting change can break tests in a NON-required CI job that doesn't block merge — verify by whole-suite or content-grep, not just --required"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad5ef142-80b1-4f1e-b3bc-4d162ec58029
---

**"All required checks pass" does NOT mean "nothing broke." A change that DELETES or replaces content can break tests living in a NON-required CI job, which does not block the merge — so the regression lands on main silently.** (Incident 2026-07-13, worldenergydata C10.)

**Why:** merging worldenergydata #1001 (C10 decision-A redirect: replaced `reports/capabilities/index.html` 31.5KB overview with a redirect stub) broke 2 tests in `test_buckskin_v50_report.py` that `split()` on `id="validation"` (IndexError). Those tests run in the `domain-tests` matrix, which is **not a required check** — so #1001's required checks were all green and I merged, turning main CI red. Only surfaced when a later PR (#1013) inherited the red job.

**How to apply:**
- When a change **deletes/replaces content** (redirect stubs, file removals, section removals, schema field drops), don't verify by `gh pr checks --required` alone. Either (a) grep the repo for tests that READ the changed file/path and run them, or (b) run the whole suite / the full `domain-tests` (non-required) matrix before merging.
- `gh pr checks <N>` (no `--required`) shows ALL checks incl. non-required — scan for `fail`/`skipping` there, not just the required subset. A non-required `fail` is still a real regression you own.
- Redirect-stub / page-collapse PRs specifically: search for tests asserting the OLD page's sections (`grep -rl '<the removed id/section>' tests/`) and update them in the SAME PR.
- Owning it: if you caused it, fix it (I replaced the 2 obsolete tests with a redirect-stub guard in the next PR that touched the file). See [[feedback_delete_branch_closes_stacked_child_pr]], [[feedback_narrow_grep_false_dead_before_deletion]], [[project_hf_backed_website_capability_surfaces]].
