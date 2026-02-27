# WRK-327 Plan: OrcaFlex Modular HTML Reporting

> Route C spec for `.claude/work-queue/pending/WRK-327.md`

## Problem
OrcaFlex lacked a config-driven, section-modular HTML report equivalent to OrcaWave reporting, limiting standardized result delivery.

## Implementation Plan
1. Build report package with orchestrator, config, and eight section renderers.
2. Ensure section enable/disable through YAML or in-memory config.
3. Keep output self-contained with inline styles/scripts plus Plotly CDN only.
4. Add tests for section rendering, builder orchestration, and integration path.
5. Wire QA summary section to WRK-325 artifacts.

## Deliverables
- `src/digitalmodel/orcaflex/reporting/*`
- `docs/domains/orcaflex/examples/report_config_template.yml`
- `tests/orcaflex/reporting/test_orcaflex_reporting.py`

## Validation
- `uv run pytest -q tests/orcaflex/reporting/test_orcaflex_reporting.py`
- Verify generated HTML has no Bootstrap dependency and includes Plotly CDN.

## Cross-Review Log
| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| P1 | 2026-02-24 | Claude | MAJOR | Test coverage and self-contained output criteria not fully satisfied. | yes |
| P2 | 2026-02-26 | Codex | APPROVE | Added tests and removed Bootstrap dependency; criteria now satisfied. | n/a |
| P3 | 2026-02-26 | Gemini | MINOR | Independent CLI review deferred (local CLI timeout); no remaining major gaps observed in validated path. | deferred |
