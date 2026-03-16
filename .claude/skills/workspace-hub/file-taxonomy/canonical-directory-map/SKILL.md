---
name: file-taxonomy-canonical-directory-map
description: 'Sub-skill of file-taxonomy: Canonical Directory Map.'
version: 1.6.0
category: workspace
type: reference
scripts_exempt: true
---

# Canonical Directory Map

## Canonical Directory Map


| File Type | Canonical Dir | Rule |
|-----------|--------------|------|
| Structured reports (HTML, PDF, Markdown) | `reports/<domain>/` | Timestamped filenames for archives |
| Raw computation output (arrays, matrices) | `results/<domain>/` | Machine-readable; intermediate data |
| Benchmark comparisons | `reports/benchmarks/<domain>/` | method_vs_reference naming pattern |
| Validated reference data | `data/<domain>/` | Ground truth; version-controlled |
| Test fixtures | `tests/<domain>/fixtures/` | Input data for tests only |
| Cache / temp | `cache/` (gitignored) | Ephemeral; never committed |
| Coverage | `reports/coverage/` | HTML in htmlcov/; XML at reports/coverage/coverage.xml |
| Specs / design docs | `specs/wrk/WRK-NNN/` or `specs/repos/<repo>/` | Pre-build; Route C only |
| Reference docs | `docs/modules/<domain>/` | Post-build; explains how it works |
| Guides | `docs/guides/` | How-to for humans; stable prose |
| Runtime config (user-facing YAML/JSON) | `config/<domain>/` | Never output; env-specific overrides only |
| Package-internal config (not user-facing) | `src/<pkg>/<module>/config/` | Exception: only when config is truly internal to the package |
| Root-level build/test config | `.` (repo root) | pyproject.toml, pytest.ini, Makefile, .gitignore only |
| Analysis scripts (exploratory) | `scripts/analysis/<domain>/` | Not `src/`; exploratory scripts only |
| Jupyter notebooks | `notebooks/<domain>/` | Never committed to `src/` or `tests/` |
| Runtime input files | `data/inputs/<domain>/` | YAML/CSV/JSON inputs consumed at runtime |
| Test benchmarks | `tests/benchmarks/<domain>/` | Benchmark comparisons; single canonical location |
| Provider prompt templates | `.codex/prompts/` or `.gemini/prompts/` | Provider-specific; supplement skills |
| Agent/orchestration test scripts | `scripts/agents/tests/` | Shell test harnesses; `test-*.sh` naming |
| Agent capability profiles | `config/agents/` | model-registry, provider-capabilities, ai-agents-registry |
