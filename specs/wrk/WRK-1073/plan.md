# WRK-1073 Plan — Repo Onboarding Maps

## Mission
Give every AI agent an instant orientation to any tier-1 repo through AGENTS.md files and a hub-level repo-map.yaml.

## Phase 1 — AGENTS.md files (5 repos, ≤20 lines each)

Write concise onboarding files at each repo root:
- `assetutilities/AGENTS.md`: shared utilities — project config, calculations, CLI; entry: `src/assetutilities/engine.py`; test: `uv run python -m pytest tests/ --noconftest`
- `digitalmodel/AGENTS.md`: engineering digital twin — asset integrity, cathodic protection, GIS, hydrodynamics; entry: `src/digitalmodel/engine.py`; test: `PYTHONPATH=src uv run python -m pytest`; deps: assetutilities
- `worldenergydata/AGENTS.md`: global energy market data — BSEE, EIA, drilling, economics; test: `PYTHONPATH='src:../assetutilities/src' uv run python -m pytest --noconftest`; deps: assetutilities
- `assethold/AGENTS.md`: asset portfolio financial analysis — fundamentals, options; entry: `src/assethold/engine.py`; test: `uv run python -m pytest tests/ --noconftest`; deps: assetutilities
- `OGManufacturing/AGENTS.md`: oil & gas manufacturing — drilling, surveillance; test: `uv run python -m pytest tests/`

## Phase 2 — Generator + repo-map.yaml

- `scripts/onboarding/generate-repo-map.py` — parses AGENTS.md + pyproject.toml for each repo
- Outputs `config/onboarding/repo-map.yaml` with: name, path, purpose, test_command, primary_modules[], depends_on[], maturity
- Run generator; validate output is parseable YAML with all 5 repos

## Phase 3 — Session-start integration

- Update session-start SKILL.md: when active WRK `target_repos` field is set, load matching entries from `config/onboarding/repo-map.yaml` and include in context

## Phase 4 — Codex cross-review

- Write review input file; submit via `scripts/review/submit-to-codex.sh`
- Resolve any MAJOR findings before closing

## Test Strategy

Generator script self-validates: run it and assert repo-map.yaml is valid YAML containing all 5 repos with required keys (name, path, purpose, test_command, primary_modules, depends_on, maturity).
