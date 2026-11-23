# Batch Closure Board — 2026-04-09

## Closure Table

| Issue | Title | GH State | Landed Commits (local) | Recommended Status | Why |
|-------|-------|----------|------------------------|--------------------|-----|
| **#1839** | Workflow hard-stops & session governance | OPEN | `e69473081` checkpoint model, `fdb7c5cf0` runtime enforcement + parity, `76c7af5ce` hook integration | **Keep open** | Phases 1-2b complete (governor model, runtime limits, PreToolUse hook wired). Phases 3-4 remain: session-start-routine skill restoration, session-corpus-audit skill, Hermes orchestration, gate transitions. Also outstanding: TDD gate enforcement, REVIEW_GATE_STRICT=1 default, gateway systemd service. |
| **#1857** | Rolling 1-week agent work queue | CLOSED | `2c5b76752` queue system, `22eec69c1` refresh hardening, `fdb7c5cf0` parity checks | **Already closed** | Queue built, refresh hardened, validation added. Closure is correct. |
| **#1858** | Economics facade (worldenergydata → field-dev) | OPEN | `b4246bf9` facade, `689fadfd` review fixes, `71578748` cost/DCF/carbon, `e27cdf18` workflow wiring, `4bc8cf51` workflow review fixes (all digitalmodel) | **Close now** | All 8 original checklist items done per comment trail. Final item (workflow.py wiring) landed as `e27cdf18`. Code review findings addressed. 206 tests passing. |
| **#1859** | Naval-arch vessel/hull integration | OPEN | `81da910a` vessel fleet adapter, `197fc901` review fixes (digitalmodel) | **Close now** | Core adapter shipped: ship_data.py, curves_of_form.py, 18 new tests, 108 passing. Cross-review verdict MINOR (no MAJOR). Remaining checklist items explicitly tracked as follow-ups: #2059, #2062, #2063, #1853, #1850. Scope boundaries documented and met. |
| **#1861** | SubseaIQ benchmark bridge | OPEN | `aaf90c8e` scaffold, `526e2352` junk-value hardening (digitalmodel) | **Keep open** | Only scaffold built (benchmarks.py + normalize.py, 27 tests). Of 4 major scope sections — Concept Selection, Cost Benchmarking, Architecture Patterns, Timeline Benchmarks — only Architecture Patterns is partially addressed (tieback distance, trees/project stats). Concept selection decision tree, cost curves, and timeline distributions all remain. |

## Issues to close now (ordered)

1. **#1858** — All 8 checklist items done, workflow integration landed, code review addressed. No remaining scope.
2. **#1859** — Core adapter complete, follow-up issues already created for remaining scope (#2059, #2062, #2063). Clean boundary.

## What to work next (ordered)

1. **#1861** — SubseaIQ benchmark bridge. Scaffold is in place; next: concept selection benchmarks (decision tree, probability matrix by water depth band) and cost benchmarking (unit cost curves cross-validated against 71 sanctioned projects).
2. **#1839 Phase 3** — Restore session-start-routine and session-corpus-audit skills. These are prerequisite for Phase 4 (Hermes orchestration).
3. **#1839 Phase 4** — Hermes gate transitions and session metrics. Depends on Phase 3.
