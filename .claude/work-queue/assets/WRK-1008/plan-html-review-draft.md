# WRK-1008 Plan — Final Review Confirmation

## Plan Summary

Harden `scripts/review/submit-to-codex.sh` against confirmed transport failures,
timeout/no-output classifications, and renderer/validator issues. Add comprehensive
regression tests and enforce strict exit-code contracts for orchestrator callers.

## Key Decisions

- Deterministic exit code mapping: QUOTA/TIMEOUT/TRANSPORT/GENERIC
- NO_OUTPUT fallback allowed only for exits 0 or 5 (genuine model no-output)
- Renderer: uv-first with python3 fallback on uv failure
- grep -Eqi replaces rg in non-interactive bash scripts
- MAJOR/MINOR verdict normalization in render-structured-review.py

## Confirmation

confirmed_by: orchestrator-claude
confirmed_at: 2026-03-04T00:00:00Z
decision: passed
