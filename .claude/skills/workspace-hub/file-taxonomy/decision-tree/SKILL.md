---
name: file-taxonomy-decision-tree
description: 'Sub-skill of file-taxonomy: Decision Tree.'
version: 1.6.0
category: workspace
type: reference
scripts_exempt: true
---

# Decision Tree

## Decision Tree


1. Is it human-readable output (HTML, PDF, Markdown report)? → `reports/<domain>/`
2. Is it raw computation (arrays, matrices, intermediate data)? → `results/<domain>/`
3. Is it a benchmark comparison vs reference? → `reports/benchmarks/<domain>/`
4. Is it validated ground truth / reference data? → `data/<domain>/`
5. Is it only used by tests? → `tests/<domain>/fixtures/`
6. Is it ephemeral / reproducible from source? → `cache/` (gitignored, never committed)
7. Is it a design spec (pre-build)? → `specs/wrk/WRK-NNN/` or `specs/repos/<repo>/`
8. Is it documentation of how something works? → `docs/modules/<domain>/` or `docs/domains/<domain>/`
9. Is it a how-to guide? → `docs/guides/`
10. Is it runtime config (YAML/JSON consumed by the app)? → `config/<domain>/`
11. Is it an exploratory analysis script? → `scripts/analysis/<domain>/`
12. Is it a Jupyter notebook? → `notebooks/<domain>/` (NEVER in `src/`)
13. Is it benchmark data / input files for runtime? → `data/inputs/<domain>/`
14. Is it a provider prompt template (Codex/Gemini)? → `.codex/prompts/` or `.gemini/prompts/`
15. Is it a shell test harness for agent/orchestration scripts? → `scripts/agents/tests/`
16. Is it a SQL query or HTML template loaded at runtime by a Python package? → keep in `src/<pkg>/<domain>/` as a **package resource**; declare in `pyproject.toml` `[tool.setuptools.package-data]`; do NOT put at `config/`
17. Is it a markdown doc found inside `src/`? → move to `docs/domains/<domain>/` — markdown is NEVER a package resource
