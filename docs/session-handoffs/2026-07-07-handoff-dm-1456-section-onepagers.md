# Session handoff — dm#1456 section one-pagers COMPLETE; riser wave-4 PR #1459 blocked on units contract

**Date:** 2026-07-07 (session started 2026-07-06 late)
**Machine:** ace-linux-1 · **Model:** Fable 5 · **Lane:** lane:claude

## Completed this session

### dm#1456 — 10 section one-pager PDF gaps ✅ DONE end-to-end
- Gate honored: issue was `status:plan-review` at session start → plan presented → **owner approved in-session** → label flipped with approval recorded ([#1456 comment](https://github.com/vamseeachanta/digitalmodel/issues/1456)).
- **PR [#1460](https://github.com/vamseeachanta/digitalmodel/pull/1460) MERGED (owner-run), issue CLOSED, content-verified on origin/main** by `git cat-file` (squash-merge; reachability not trusted).
- Landed: 10 `kind="section"` SPECS entries + Cairo-verified PDFs; inventory/spec regenerated (`pdf_gaps: []`); 3 ratchet tests now LIVE on main:
  - section↔SPECS **bijection** (escape hatch `onepager_exempt: []` in `capabilities-clusters.yml`, empty by design)
  - **pdf-committed-on-disk** (< 2 MB) — the real closure of the pdf_gaps hole
  - **standards-grounding** — every std token grep-matched to a file the section links (#1391 mechanized)
- **Grounding test caught 2 legacy overclaims on first run** (both corrected in-PR, PDFs rebuilt scoped): `sec-structural` "IACS UR S11" (grounded only in naval-architecture's `hull_girder_strength.py`), `sec-artificial-lift` "API 11E" (in the dynacard engine — `gear_box_loading.py` — but not linked from the section).
- Revamp-lane note: link `gear_box_loading.py` from `#artificial-lift` → the API 11E citation can return.
- Worktree `.worktrees/wt-1456` + local branch removed; lane clean.

### Load-bearing facts confirmed (for future capabilities lanes)
- Grounding resolution = **section hrefs on index.html** (GitHub blob/tree URLs → repo paths + relative pages), NOT inventory `explorers` (empty for fatigue).
- Local sparse worktrees must add `src/digitalmodel examples docs/domains/references/field_development docs/domains/articles data/vessels` for grounding greps to match CI's full checkout.
- dm CI lint = `ruff check` via quality-gates (pyproject config); E402 is enforced.
- Scoped `build_onepagers.py <ids>` emits PDFs only for section-kind (zero api/ churn), ~50 KB each.

## NOT done / blocked — riser wave-4 PR #1459

- [PR #1459](https://github.com/vamseeachanta/digitalmodel/pull/1459) (schedule-assembly, #1458) is **red on `tests-contracts`**: the #1447 units contract flags `top_tension_factor` (schedule_assembly.py:182, bare-float field, vocabulary word "tension", no unit suffix). It is **dimensionless** (API RP 16Q TTF) → suffix would be wrong, allowlist frozen.
- **Recommended fix** (posted as [PR comment](https://github.com/vamseeachanta/digitalmodel/pull/1459#issuecomment-4901840324)): rename to `ttf` (regex-clean, standard abbreviation). 3 usages: schedule_assembly.py:182/:210 + tests/drilling_riser/test_schedule_assembly.py:144. All other checks green.
- **Why untouched:** the `wt-1458` worktree vanished BETWEEN two commands mid-diagnosis → a parallel session is ACTIVE on that lane. Never trample; diagnosis handed over via the PR comment.

## Repo states at exit

| Repo | State |
|---|---|
| digitalmodel main | #1460 merged + verified; open PRs: #1459 (red, other lane), #1457 (chore) |
| workspace-hub (ace-linux-1) | **main WEDGED: 8 ahead / 22 behind origin** (equality-wedge pattern; recovery playbook in memory `feedback_equality_wedge_vs_drift_recovery` — needs owner OK, destructive). Pre-existing dirty: `.claude/memory/*` bridge files + `.claude/state/candidates/*` (other machinery's, untouched) |
| This handoff | pushed on branch `docs/handoff-2026-07-07-dm-1456` (docs-only PR; local main not deepened) |

## External actions
None sent (no emails, no publishes). GitHub-only: PR #1460 (merged by owner), issue comments on #1456, diagnosis comment on #1459.

## Next steps (one at a time)
1. **Merge #1459 after the `ttf` rename lands** — wave-4 lane owns it; if that session went dark, a fresh session may land the rename once `git -C /mnt/local-analysis/digitalmodel worktree list` is stable and no new pushes hit `feat/schedule-assembly-1458`.
2. Then per riser memory: wave-5 wiki PR.
3. workspace-hub equality wedge on ace-linux-1 needs the documented recovery (owner-gated).
