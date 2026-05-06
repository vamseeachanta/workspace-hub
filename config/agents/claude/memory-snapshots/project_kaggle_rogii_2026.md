---
name: Kaggle ROGII Wellbore Geology Prediction (2026)
description: Active 13-week Kaggle competition project. Sibling repo at /mnt/local-analysis/kaggle-rogii-2026/ — predict TVT along horizontal wellbores, RMSE metric, $50k prize pool, deadline 2026-08-05.
type: project
originSessionId: ec40ba65-385e-48da-98c7-8cf5a6f30e44
---
User is participating in the Kaggle [ROGII - Wellbore Geology Prediction](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction) competition. Open to team merging.

**Why:** $50k prize pool with strong domain fit (digitalmodel/wellbore expertise). Kicked off 2026-05-05 with the user direction "we will participate in this competition" and "Let us start work." Three months to first podium attempt.

**How to apply:**
- Repo location: `/mnt/local-analysis/kaggle-rogii-2026/` (sibling to workspace-hub, not nested). Standalone git project.
- Data location: `/mnt/local-analysis/kaggle-rogii-2026/data/raw/` — gitignored, ~1.33 GB, 2,327 files. Reproducible via `scripts/download_data.sh` (uses `uv run --with kaggle`).
- Manual prerequisites the user owns (Claude cannot do these): accept competition rules on Kaggle, drop API token at `~/.kaggle/kaggle.json`, identity-verify before submitting.
- Task: predict TVT (True Vertical Thickness, ft) along the evaluation zone of horizontal wells. Sequence-completion problem along measured depth — `TVT_input` has NaN over the eval zone, model continues the trace. Metric: RMSE.
- Key features per well: `MD`, `X`, `Y`, `Z`, `GR`, `TVT_input`, plus a paired typewell with `TVT`, `GR`, `Geology` for log correlation.
- Train-only "answer-leaking" features: formation-top depths `ANCC`, `ASTNU`, `ASTNL`, `EGFDU`, `EGFDL`, `BUDA`. Use only as auxiliary supervision, not as inputs at inference.
- Submission: Kaggle Notebook only, ≤9 h CPU/GPU, internet disabled at submit. Pretrained models must be uploaded as Kaggle Datasets first.
- Timeline: started 2026-05-05; entry/team-merger deadline 2026-07-29; final submission 2026-08-05.
- Decisions log: `docs/decisions.md` in the repo. Spec captured offline at `docs/competition-overview.md`.

When the user references "the Kaggle comp," "ROGII," "wellbore geology," or "TVT prediction," they mean this project.
