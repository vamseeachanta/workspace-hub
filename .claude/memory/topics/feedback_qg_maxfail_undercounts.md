> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-08
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_qg_maxfail_undercounts.md

---
name: Quality Gates --maxfail truncates failure counts
description: digitalmodel Quality Gates CLI runs pytest with --maxfail=20 and the artifact's output_tail JSON wraps to ~8.6 KB; the reported "N failures" is the ceiling, not the count
type: feedback
originSessionId: f0b82690-86aa-4409-8f19-0896e0cba0cb
---
digitalmodel's Quality Gates CI runs `pytest --maxfail=20` and the workflow CLI (`digitalmodel.workflows.automation.quality_gates_cli`) wraps pytest stdout into a JSON `output_tail` field truncated to ~8.6 KB. The headline "N failures" in the artifact is the maxfail ceiling, not the true failure count.

**Why:** verified 2026-05-02 on main `60d59565`. CI reported "20 failed, 3000 passed". Local repro on the same SHA without `--maxfail` captured **184 unique FAILED + 60 unique ERROR = 244 broken tests** before the run was killed mid-collection. The CI report under-stated reality by ~12×.

**How to apply:**
- When triaging digitalmodel CI failures, NEVER trust the artifact's failure count as the true count. Re-run locally with `--maxfail=999 --tb=line` from a fresh worktree at the CI SHA before estimating scope.
- When opening followup issues for "close #X to fix CI", verify the close is actually load-bearing — it usually isn't. The "X tests this PR fixes" / "Y tests CI shows red" ratio can be 4% or worse, so closure does not green Quality Gates.
- The truncation is fixable: one-line change to upload full `pytest --tb=short` log as a separate artifact instead of JSON-wrapping the tail. Adjacent CI hygiene issue, not blocked by anything.
- Concrete failure topology on `60d59565`: 77 marine_ops, 33 solvers, 25 hydrodynamics, 20 infrastructure (FAILED) + 36 infrastructure, 13 solvers, 5 orcawave, 3 hydrodynamics, 3 data_systems (ERROR). Most clusters share root causes — bucket counts predict number of root-cause classes, not number of independent bugs.

**Don't apply when:** CI runs `pytest --maxfail=999` or no maxfail (rare in this repo); the artifact uploads full pytest log alongside JSON metric (not yet implemented).

**Cross-references:** `feedback_attestation_enables_contradiction_detection.md` (this is the kind of contradiction attestation enables), `feedback_commit_attestation_narrow_scope.md` (closing #2580 attests narrowly to 10 tests, not "QG green").
