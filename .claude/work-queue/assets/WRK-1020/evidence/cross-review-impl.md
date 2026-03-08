# WRK-1020 Implementation Cross-Review (Stage 13)

Reviewed: `scripts/cron/update_portfolio_signals.py` + `update-portfolio-signals.sh` + `tests/skills/test_update_portfolio_signals.py`

## Summary

| Provider | Verdict | P1 | P2 |
|---|---|---|---|
| Claude | APPROVE (after fixes) | 1 | 3 |
| Codex | APPROVE (after fixes) | 1 | 1 |
| Gemini | APPROVE (after fixes) | 1 | 2 |

## P1 Findings and Resolutions

| ID | Finding | Resolution |
|---|---|---|
| CL-P1 | `lookback_days: 30` hardcoded in write_output | FIXED — `lookback_days` param added; flows from CLI arg |
| CX-P1 | `lstrip("https://")` strips chars not prefix; domain check too loose | FIXED — `re.sub(r'^https?://', '')` + exact host match |
| GM-P1 | `merge_signals` truncates new signals when existing is full | FIXED — new signals prepended before existing |

## P2 Findings and Resolutions

| ID | Finding | Resolution |
|---|---|---|
| CL-P2-1 | URL lstrip bug (same root as CX-P1) | FIXED same fix |
| CL-P2-2 | `source_verified` always False even when verification passes | FIXED — set True after filter_official_sources returns non-empty |
| CL-P2-3 | Docstring says "Returns {}" but raises ValueError | FIXED — docstring updated |
| CX-P2 | Stale signals not pruned on carry-forward paths | NOTED — prune only runs on successful query path; carry-forward preserves prior as-is (by design for stability) |
| GM-P2-1 | `datetime.fromisoformat` Python <3.11 compat | NOTED — repo runs Python 3.11 per .python-version; accepted |
| GM-P2-2 | `yaml.dump` vs `yaml.safe_dump` | FIXED — changed to `yaml.safe_dump` |

## Overall Verdict: APPROVE

All P1s resolved. 34/34 tests pass post-fix.
