---
name: Kaggle ROGII Wellbore Geology Prediction (2026)
description: Active 13-week Kaggle competition project. Public sibling repo at github.com/vamseeachanta/kaggle-rogii-2026 (data on /mnt/ace/kaggle-rogii-2026/) — predict TVT along horizontal wellbores, RMSE metric, $50k prize pool, deadline 2026-08-05. Issues #1–#8 drive phase plan.
type: project
originSessionId: ec40ba65-385e-48da-98c7-8cf5a6f30e44
---
User is participating in the Kaggle [ROGII - Wellbore Geology Prediction](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction) competition (Kaggle username `aceengineer`, separate from GitHub `vamseeachanta`). Open to team merging.

**Why:** $50k prize pool with strong domain fit (digitalmodel/wellbore expertise). Kicked off 2026-05-05 with the user direction "we will participate in this competition." Three months to first podium attempt.

**How to apply:**

Repo and storage:
- GitHub: <https://github.com/vamseeachanta/kaggle-rogii-2026> (PUBLIC since 2026-05-06 per user direction; competitors can see the roadmap and decisions).
- Local repo: `/mnt/local-analysis/workspace-hub/kaggle-rogii-2026/` (nested in workspace-hub for navigation/consistency since 2026-05-07; independent .git, gitignored from hub root, agent-context firewalled by per-repo `.claude/` + `CLAUDE.md`).
- Data: `/mnt/ace/kaggle-rogii-2026/data/raw/` — gitignored, ~1.33 GB, 2,327 files. `data/{raw,interim,processed}` in the repo are symlinks. Reproducible via `scripts/download_data.sh` after `scripts/bootstrap_data_dir.sh`.
- Kaggle CLI auth: OAuth via `kaggle auth login` (lands at `~/.kaggle/credentials.json`, not the legacy `kaggle.json`).

Task and data shape:
- Predict TVT (True Vertical Thickness, ft) along the evaluation zone of horizontal wells. Sequence-completion problem along measured depth — `TVT_input` has NaN over the eval zone, model continues the trace. Metric: RMSE.
- 773 train wells, ~200 hidden test wells. Median ~6,400 rows/well at ~1 ft MD spacing. Eval zone = 72.7% of every well (heel-only `TVT_input`).
- Per well: `MD, X, Y, Z, GR, TVT_input` + paired typewell with `TVT, GR, Geology`. Train-only "answer-leaking" features: formation-top depths `ANCC, ASTNU, ASTNL, EGFDU, EGFDL, BUDA` — use only as auxiliary supervision, not as inputs at inference.
- TVT is in the typewell's depth frame (~+11,500 ft); Z is in TVD (~−9,400 ft). Different reference frames; alignment maps Z(MD) → TVT(MD).

Submission:
- Code Competition: Kaggle Notebook only, ≤9 h CPU/GPU, internet disabled at submit. Pretrained models must be uploaded as Kaggle Datasets first.
- CLI submit: `kaggle competitions submit -c rogii-wellbore-geology-prediction -k aceengineer/<kernel> -v <ver> -f submission.csv -m "..."`. Kernel must be in `COMPLETE` state first; first runs may queue 10+ min on free tier.
- Identity verification done 2026-05-06.

Empirical findings to date:
- **Carry-forward floor: 11.53 ft RMSE** on a 10-well train sample (notebooks/00_baseline_carry_forward.ipynb).
- **Phase 1 v1 NEGATIVE result**: typewell-only correlation = 297.86 ft RMSE, lost on 0/10 wells. Causes: static anchor + GR signature ambiguity within typewell. See `docs/decisions.md` 2026-05-05 entry.

Issue-driven phase plan (correct mapping after parallel-create reverse-numbering, verified 2026-05-06):
- [#1](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/1) Phase 1 v2 — Heel-as-reference DTW (T2, plan-review)
- [#2](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/2) Phase 2 — Offset-well features + pad-aware CV (T3, plan-review)
- [#3](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/3) Phase 0.5 — Linear extrapolation baseline (T1, **plan-approved**)
- [#4](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/4) Phase 3 — GBDT regressor (T2, plan deferred)
- [#5](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/5) Research — public datasets + prior art (T2, plan-review, **GATING**)
- [#6](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/6) Submit carry-forward kernel to leaderboard (T1, plan-review)
- [#7](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/7) Phase 4 — Sequence model w/ regime aux head (T3, plan deferred)
- [#8](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/8) Phase 5 — Ensembling + submission packaging (T2, plan deferred)
- [#9](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/9) BUG — Kaggle path-detection infinite loop (T1, plan-review)

Cross-repo (research-and-data gating phase per user direction 2026-05-06):
- [vamseeachanta/llm-wiki#40](https://github.com/vamseeachanta/llm-wiki/issues/40) — reservoir-engineering literature ingest (T3, plan-review, **GATING**). Plan in kaggle-rogii-2026/docs/plans/.
- [vamseeachanta/worldenergydata#392](https://github.com/vamseeachanta/worldenergydata/issues/392) — public well-log dataset ingest (T3 expected, plan to draft, **GATING**). Plan to live in worldenergydata/docs/plans/ per that repo's mature workflow.
- [vamseeachanta/workspace-hub#2651](https://github.com/vamseeachanta/workspace-hub/issues/2651) — PPTX → PDF on ace-linux-2 (T1, cross-machine).

**Strategic gating-phase pattern (user-directed, 2026-05-06):** [#5](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/5), [llm-wiki#40](https://github.com/vamseeachanta/llm-wiki/issues/40), [worldenergydata#392](https://github.com/vamseeachanta/worldenergydata/issues/392) form Wave 1 — research-and-data substrate that must execute to user satisfaction before [#4](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/4)/[#7](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/7)/[#8](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/8) plan-drafting starts. [#1](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/1)/[#2](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/2) plans exist but their existing drafts may need revision after Wave 1 lands. T1 unblockers ([#9](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/9), [#3](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/3), [#6](https://github.com/vamseeachanta/kaggle-rogii-2026/issues/6)) run in Wave 2 in parallel.

Planning roadmap: `kaggle-rogii-2026/docs/plans/PLANNING-ROADMAP.md` is the canonical dependency-and-sequencing document. Update it whenever the wave/gating structure changes.

Timeline: started 2026-05-05; entry + team-merger deadline 2026-07-29; final submission 2026-08-05.

When the user references "the Kaggle comp," "ROGII," "wellbore geology," or "TVT prediction," they mean this project.
