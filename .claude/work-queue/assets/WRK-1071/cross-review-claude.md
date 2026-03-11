# WRK-1071 Cross-Review — Claude (Stage 6 Plan Synthesis)

## Verdict: MINOR

Plan v1.1 resolves all MAJOR findings from Codex and Gemini.

## Synthesis of findings

| Finding | Source | Status |
|---------|--------|--------|
| worldenergydata optional-dev dep not auto-activated | Codex+Gemini | RESOLVED — moved to `[dependency-groups].benchmark` |
| tests/benchmarks/ conftest issue for worldenergydata | Codex | RESOLVED — benchmarks kept in `tests/performance/` |
| Cron `<REPO_ROOT>` placeholder — literal fail | Codex | RESOLVED — using `$WORKSPACE_HUB` + explicit PATH |
| TDD tests missing bootstrap, invalid-repo, new-bench cases | Codex | RESOLVED — 8 tests vs original 5 |
| digitalmodel whole-dir collect pulls in generic benchmarks | Codex | RESOLVED — explicit file targeting |
| CP bench function names mismatched route names | Gemini | RESOLVED — 4 separate bench functions, one per route |
| uv must cd into repo dir before run | Gemini | RESOLVED — `cd <dir> && uv run` pattern |
| Cron PATH for uv not in cron PATH | Gemini | RESOLVED — explicit PATH injection |

## Residual risks (acceptable)

- Benchmark variance across runs: 20% threshold + `--benchmark-min-rounds=5` mitigates
- Baseline keys use `repo::bench_name` qualified format to avoid collision — verify in implementation
