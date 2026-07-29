---
name: reference_dynacard_module_map_digitalmodel
description: "Where dynacard/sucker-rod-pump diagnostics live in digitalmodel, and the honesty caveats on its accuracy claims"
metadata: 
  node_type: memory
  type: reference
  originSessionId: bef7bcd3-75db-455f-8193-f247ec2c5754
  modified: 2026-07-27T16:47:14.718Z
---

Dynacard (sucker rod pump) diagnostics live at `digitalmodel/src/digitalmodel/marine_ops/artificial_lift/dynacard/` — NOT under `production_engineering/`. Installed CLI entry point `dynacard` → `…dynacard.cli:main` (declared in `pyproject.toml`). Verified 2026-07-27.

- ~6,635 LOC across 24 core modules; ~9,347 LOC including `visualization/` and `benchmark/`.
- Two physics solvers: `physics.py` (Gibbs, frequency-domain FFT) and `finite_difference.py` (time-domain PDE). `solver.py::DynacardWorkflow.compare_solvers()` returns `stroke_diff_pct` / `load_rmse_pct` — solver disagreement is itself a useful diagnostic signal.
- `diagnostics.py::PumpDiagnostics` classifies 18 failure modes from Bezerra vertical-projection features, with confidence + top-3 differential. If `data/dynacard_classifier.json` is missing it silently falls back to `_classify_legacy()` threshold rules (`model_version="legacy"`) — a broken model yields plausible output, not an error.
- Marketing copy: `docs/marketing/dynacard-ai-diagnostics-brochure.md`.
- Worked troubleshooting catalog (symptom + ranked actions + metrics per mode) generated at `docs/api/artificial-lift/dynacard-troubleshooting.json` — found riding on the `agent-worktrees/dm-1575-plan` branch (that issue is OpenFOAM; the file is unrelated cargo).

**Two caveats before quoting this to a client:**
1. The advertised **89.4% is `cross_val_score` on 100% synthetic training data** (`training.py:144`, over `card_generators.generate_training_dataset()`); confirmed as `"cv_accuracy": 0.8944` inside the shipped model JSON. The brochure places it beside Bezerra's "98.87% on 6,101 real cards", which is a *literature result for the feature-extraction method*, not for this classifier. Don't let the two be conflated.
2. The **real-card benchmark is unimplemented**: `benchmark/runner.py` imports `test_set_builder` in a `try/except ModuleNotFoundError` that sets `LabelledCard = None`, and no `test_set_builder.py` exists in `src/` (only in `tests/`). So the classifier has never been scored against a labelled real card.
   Symptom visible in the generated catalog: every fault saturates at confidence 1.0 while the healthy baseline scores only 0.5852 (vs TUBING_MOVEMENT 0.41) — classic memorization of its own generator. Prefer the geometric `area_vs_healthy_pct` metric over the model's confidence when talking to field engineers.

Real (anonymized) card data on hand: `tests/marine_ops/artificial_lift/test_data/` — 5 wells from historical KBR and Oxy Cipher projects, with tapered rod strings, deviated surveys, and surface cards including noise and harmonics. These are the natural labelling candidates to close caveat 2.

Related: [[feedback_small_calcs_into_digitalmodel_domains]], [[reference_digitalmodel_python_env_venv]], [[feedback_public_by_default_client_custom_private]]
