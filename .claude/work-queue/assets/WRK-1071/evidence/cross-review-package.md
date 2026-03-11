# WRK-1071 Cross-Review Package

## Summary

| Provider | Verdict | Findings |
|----------|---------|----------|
| Claude | MINOR | 0 new (post-synthesis) |
| Codex | MAJOR → RESOLVED | 5 findings, all resolved in v1.1 |
| Gemini | MINOR → RESOLVED | 4 findings, all resolved in v1.1 |

## Resolution Table

| Finding | Source | Severity | Resolution |
|---------|--------|----------|------------|
| worldenergydata dep not auto-activated | Codex+Gemini | P1 | Moved to [dependency-groups].benchmark |
| tests/benchmarks/ conftest not scoped | Codex | P1 | Benchmarks kept in tests/performance/ |
| Cron literal `<REPO_ROOT>` | Codex | P1 | Changed to $WORKSPACE_HUB + explicit PATH |
| TDD tests miss edge cases | Codex | P2 | Expanded to 8 tests |
| digitalmodel whole-dir collect | Codex | P2 | Explicit file targeting in runner |
| CP bench function names | Gemini | P2 | 4 functions matching route names |
| uv from workspace root | Gemini | P2 | cd into repo dir before uv run |
| Cron PATH missing uv | Gemini | P2 | PATH=$HOME/.local/bin:$PATH injected |

All MAJOR findings resolved. Plan approved as v1.1.
