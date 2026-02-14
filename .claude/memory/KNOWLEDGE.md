# Institutional Knowledge

> Shared knowledge base for workspace-hub. All entries use env var placeholders for paths.
> **Limit**: 200 lines max. Create topic files for detailed entries (10+ items per topic).

## Environment Conventions

- Windows (MINGW64): paths use `/d/workspace-hub/` in bash (not `D:\`)
- All development must be compatible with Linux, Windows, and macOS
- Shell scripts: `#!/usr/bin/env bash`, LF line endings, test on all 3 platforms
- Windows `core.symlinks=false` — git treats junctions as dirs, not symlinks
- Symlinks: use `ln -s` on Linux/macOS, `cmd //c mklink /J` on Windows (no elevation)
- MINGW root path: `while [ "$(pwd)" != / ]` loops never terminate — use `WORKSPACE_HUB` env var
- Never commit symlinks to git cross-platform — use runtime linking + `.gitignore`

## Tool/Solver Quick Reference

- **OrcFxAPI**: See `orcawave-lessons.md` for detailed API usage
  - `.frequencies` returns **Hz** (not rad/s) in **descending** order
  - `displacementRAOs` shape: `(nheading, nfreq, 6)` — complex values
  - Rotational RAOs in **radians/m** — convert with `np.degrees()` for deg/m
- **AQWA**: See `aqwa-lessons.md` for DAT format and LIS parsing
  - Elements must use `QPPL DIFF` (not just `QPPL`) for diffraction
  - `OPTIONS GOON` continues past non-fatal errors but NOT mesh FATAL errors
  - Executable: `$AQWA_HOME/bin/winx64/Aqwa.exe` (set `AQWA_HOME` env var)
- **BEMRosetta**: CLI does mesh conversion only (`-mesh` mode)
  - Executable: `$BEMROSETTA_HOME/BEMRosetta_cl.exe`
  - Nemoh is the open-source solver BEMRosetta wraps

## Debugging Protocol

- **Pre-flight first**: Validate inputs BEFORE running solvers (units, formats, conventions)
- **Unit traps**: OrcaWave=Hz descending, AQWA=rad/s; rotational RAOs rad/m vs deg/m
- **Negative correlations**: Almost always means frequency arrays in different order
- **NaN correlations**: Zero std dev (e.g., yaw at head seas) — handle gracefully
- **AQWA FATAL mesh errors**: Cannot be overridden with `OPTIONS GOON`; fix the mesh
- **LIS parser**: Normalize whitespace before keyword matching ("ADDED  MASS" has double space)
- **Always check**: frequency order, unit system, RAO array shape/transpose before comparing

## Key Patterns

- Tests needing subprocess path: set `use_api=False` in RunConfig
- Pre-existing test failures: AQWA runner detect tests (real exe found), CLI integration tests
- WRK-NNN references: Always include brief description inline (never bare IDs)
- `.gitignore` blanket rules (e.g., `memory/`) override earlier whitelists — add negation AFTER the blanket rule too

## Topic Files

- `orcawave-lessons.md` — OrcFxAPI usage, YAML gotchas, result extraction
- `aqwa-lessons.md` — DAT format, LIS parsing, mesh quality, heading conventions
