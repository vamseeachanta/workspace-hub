# Session handoff: simulation study workflow (#3894), review pack (#3892), agy lane (#3896)

**Date:** 2026-09-27
**Host:** ace-win-1 (Windows workspace)
**Scope:** public-safe summary. The client campaign details are in the client wiki's own handoff, `analysis/notes/session-handoff-workflow-review-2026-09-27.md` in the private client repository.

## State

| Item | State | Evidence |
|---|---|---|
| #3894 epic: solver-neutral simulation study workflow | Plan r4 is on `origin/main`, labelled `status:plan-review`, **not approved, nothing implemented** | `docs/plans/2026-09-25-issue-3894-simulation-study-workflow.md` (commits 228f6063e, 1707e1cc9, 181fab58d, 5334ffe23, plus L17 in this handoff's commit) |
| #3894 reviews | r1 and r2: Claude MAJOR and Codex MAJOR in both rounds. r3 was applied as inline patches. r4 folds in the campaign lessons L1–L17. | Review artifacts are local only: `scripts/review/results/2026-09-25-plan-3894-*` and `…-r2/` (gitignored) |
| #3894 owner decisions | 11-card local board, **not yet decided** | `output/simulation-workflow/decisions/simulation-workflow-decisions-local.html` under the workspace root, local only; the saved export goes to the Downloads folder as `simulation-workflow-decisions.json` |
| #3892 review-pack standard | Open, not approved. The generator prototype sits outside any repo (`output/human-review-pack/review_pack.py` under the workspace root), and one client adapter uses it. | #3892 comment linking #3891 |
| #3891 physical-realism rule | Draft PR from a parallel session; not this session's | |
| #3896 agy review lane | Filed. A controlled pair (20 KB rc=0 with output; 41 KB rc=126) shows the Windows argv limit sits below the wrapper's cap, and fan-out records the failure as "UNAVAILABLE rc=0". | #3896 |

## Lesson added at close (L17)

A time-accurate cost estimate must come from the actual mesh's cell Courant field, not from the wave-period rule alone. On a mesh built for local time stepping, the step pinned at about 0.005 s (max cell Co 5) against a 0.04 s target. The projection went from 1–2 days to 40–98 days per condition, and a proposed pilot was abandoned for that mesh. L17 and test 25 are in the plan.

## Next steps (owner-gated)

1. The owner decides the #3894 board (G01 approve, G02 sequencing, G03 two-provider consensus, A01–A08).
2. After approval, file the wave child issues W0a–W6. W0b (ITTC, Maki and Holtrop–Mennen citation pages) gates W2.
3. Fix #3896 before the next T3 plan review from Windows, or run agy reviews from Linux.

## External actions this session took

- **Issues created:** workspace-hub #3892, #3894 and #3896, and private client-repo #389.
- **Comments posted:** on #3892 and #3894.
- **Plan commits to `origin/main`:** built through a temporary index, because another session's untracked `docs/reports/2026-09-25-machine-equality-matrix.html` blocks `git pull` in the shared checkout. The working tree was not touched.
- **Cross-session messages:** exchanged with the CFD lane-owner session.
- **Not done:** no merge, no deploy, no publication, no solver action.
