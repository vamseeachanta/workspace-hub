# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Foundation Sprint

**Shipped:** 2026-03-30
**Phases:** 6 | **Plans:** 21 | **Timeline:** 5 days (2026-03-25 → 2026-03-29)

### What Was Built
- 3 new digitalmodel calculation modules (OBS, wall thickness, spectral fatigue) with standards traceability manifests and 90.5% test coverage
- EIA/BSEE/SODIR data pipelines with Parquet output, staleness monitoring, and email alerting
- aceengineer.com GTM: interactive calculators, pricing page, GA4 tracking, Schema.org SEO
- Enterprise sales funnel: case studies, calculator→case study CTAs, contact form lead qualification, GitHub Issues prospect pipeline
- Nightly 4-domain research automation with Haiku/Sonnet model selection, validation, and 90-day pruning
- digitalmodel library-first vision, tiered development roadmap, README trimmed from 650→81 lines

### What Worked
- **GSD framework velocity:** 6 phases / 21 plans in 5 days — discuss→plan→execute→verify pipeline kept momentum high
- **TDD discipline:** Red-green-refactor across all calculation modules caught edge cases early (zero submerged weight → inf utilisation)
- **Standards traceability manifests:** Pydantic schema + CI validation ensured every function maps to its standard clause
- **Worktree isolation:** Phase 06 executed in git worktree without blocking main branch work
- **One-file-per-standard pattern:** Clean module boundaries in digitalmodel (dnv_rp_f109.py, asme_b31_4.py, etc.)

### What Was Inefficient
- **No REQUIREMENTS.md created:** Milestone predates requirement tracking — couldn't do formal gap analysis at completion
- **Phase 05 progress tracking stale:** STATE.md showed "1/2 plans complete" but both plans were actually done
- **Backlog phases counted in total_phases:** roadmap analyze reports 11 phases (6 active + 5 backlog) which inflates metrics

### Patterns Established
- NamedTuple result types for engineering checks (utilisation, is_stable, details)
- manifest.yaml per calculation module for CI-validatable standards traceability
- `var` for browser compatibility in aceengineer.com JavaScript (matching existing codebase)
- funnel_step GA4 event type for measuring conversion progression (distinct from generic cta_click)
- 60h staleness threshold for weekday-only cron schedules (avoids Monday false positives)

### Key Lessons
1. **Create REQUIREMENTS.md at milestone start** — without it, milestone audit and gap analysis are impossible
2. **Keep STATE.md progress in sync** — stale progress entries erode trust in the tracking system
3. **Separate backlog from active phase counts** — metrics should reflect deliverable scope, not parking lot items
4. **Standards-first engineering pays off** — every calculation traces to a clause, making verification straightforward

### Cost Observations
- Model mix: ~60% sonnet (execution), ~25% haiku (research), ~15% opus (planning/review)
- Sessions: ~12 sessions across 5 days
- Notable: Worktree parallelization and wave-based plan execution kept wall-clock time low relative to output volume

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Timeline | Phases | Plans | Key Change |
|-----------|----------|--------|-------|------------|
| v1.0 | 5 days | 6 | 21 | GSD framework inaugural run — established all patterns |

### Cumulative Quality

| Milestone | Verification | Coverage | Modules Shipped |
|-----------|-------------|----------|-----------------|
| v1.0 | Phase 02 formally verified (7/7 truths, 56 tests) | 90.5% (digitalmodel) | 3 calc modules + 3 data adapters |

### Top Lessons (Verified Across Milestones)

1. Create REQUIREMENTS.md at milestone start — validated by v1.0 gap in audit coverage
2. TDD + standards traceability manifests = high-confidence engineering modules
