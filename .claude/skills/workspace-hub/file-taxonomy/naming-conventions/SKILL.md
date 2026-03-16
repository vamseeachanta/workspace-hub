---
name: file-taxonomy-naming-conventions
description: 'Sub-skill of file-taxonomy: Naming Conventions.'
version: 1.6.0
category: workspace
type: reference
scripts_exempt: true
---

# Naming Conventions

## Naming Conventions


| Pattern | Example | Rule |
|---------|---------|------|
| Timestamped reports | `spar_fatigue_2026-02-18.html` | ISO date suffix for archives |
| Domain-scoped results | `results/fatigue/spar_sn_curves.npy` | Domain subdir always present |
| Benchmark files | `reports/benchmarks/wamit/ellipsoid_vs_wamit.html` | method_vs_reference |
| Coverage | `reports/coverage/coverage.xml` | Singular fixed name, gitignored |
| Fixtures | `tests/bsee/fixtures/cost_sample.yaml` | Domain-matched to src/ |
| Config | `config/analysis/bsee_config.yaml` | Domain-scoped; never at root except pyproject/pytest.ini |
| Analysis scripts | `scripts/analysis/production/decline_study.py` | Not in src/ |
| Notebooks | `notebooks/bsee/well_production_eda.ipynb` | Domain subdir required |
| Input data | `data/inputs/metocean/jonswap_params.yaml` | Runtime inputs; separate from test fixtures |
| Internal config dir | `src/<pkg>/<domain>/config/` | **Singular** `config/` — NEVER `configs/` (plural) |
