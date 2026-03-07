# WRK-1019 Plan Cross-Review Input

**WRK**: WRK-1019 — repo-portfolio-steering skill
**Review type**: Stage 6 Plan Cross-Review
**Plan artifact**: specs/wrk/WRK-1019/plan.md
**Stage 5 decisions applied**:
- L3 capability research deferred to WRK-1020 (skill is L1+L2 only)
- portfolio-signals.yaml committed to git (auditable, not gitignored)
- 30-day lookback window for provider activity

## Key design decisions to evaluate

1. **Composition pattern**: skill is a thin layer over official plugins; does NOT embed logic
2. **L1+L2 only scope**: queue balance + per-provider activity from portfolio-signals.yaml
3. **compute-balance.py** reads INDEX.md (L1) + portfolio-signals.yaml (L2, pre-computed)
4. **11 TDD tests** covering all acceptance criteria
5. **WRK-1020 spin-off** delivers: update-portfolio-signals.sh cron + L3 capability signals

## Review checklist

- [ ] Plan scope is achievable without L3 (L1+L2 sufficient for steering signal)
- [ ] portfolio-signals.yaml schema is clear and extensible for WRK-1020 additions
- [ ] Test suite covers all 8 ACs adequately; no gaps
- [ ] Session-start integration is non-invasive (delegate, not embed)
- [ ] compute-balance.py responsibilities are clearly bounded
- [ ] No unresolved P1 findings
