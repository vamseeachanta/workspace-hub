---
name: digitalmodel-uv-compile-bytecode
description: digitalmodel sets compile-bytecode=true in both uv.toml and pyproject.toml — likely root cause of silent multi-minute uv sync finalize stalls.
type: project
originSessionId: 20bbbf35-b8fa-4295-a1b2-59fd2252ff45
---
Setting both `compile-bytecode = true` (in `uv.toml:15`) and `compile = true` (in `[tool.uv]` of `pyproject.toml:346`) caused uv to recompile `.pyc` files for ~100 dependencies post-install, including heavy native packages (scipy, pandas, pyvista, geopandas, pyarrow, h5py, argon2-cffi, pygmt, cx-Oracle, pymssql).

**Why:** Symptom observed 2026-05-02 during /whats-next dispatch — uv sync PID stayed alive >18s after install completed (no further output). Hypothesized as the cause in #2606 plan and fixed via flip to `false` in digitalmodel#567 (squash-merged 2026-05-03 20:27Z).

**How to apply:**
- If `uv sync` in digitalmodel hangs at finalize phase again, FIRST verify these 2 settings are still `false`. Drift is the most likely cause.
- Trade-off: slightly slower first-import per package (one-time cost, amortized) in exchange for fast sync exit.
- Secondary hypothesis (not verified): editable workspace dep `assetutilities` at `../assetutilities` may have a build hook that doesn't exit. If primary fix doesn't resolve, file a follow-up to investigate.

**Status:** Fix landed. User must verify `uv sync` exits cleanly post-merge — if it still hangs, secondary hypothesis is in play.
