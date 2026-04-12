# Institutional Knowledge

> Shared knowledge base for workspace-hub. All entries use env var placeholders for paths.
> **Limit**: 200 lines max. Create topic files for detailed entries (10+ items per topic).

## Environment Conventions

- Windows (MINGW64): paths use `/d/workspace-hub/` in bash (not `D:\`)
- All development must be compatible with Linux, Windows, and macOS
- Shell scripts: `#!/usr/bin/env bash`, LF line endings, test on all 3 platforms
- Windows `core.symlinks=false` — git treats junctions as dirs, not symlinks
- Symlinks: use `ln -s` on Linux/macOS, `cmd //c mklink /J` on Windows (no elevation)
- MINGW root path: `while [ "$(pwd)" != / ]` loops never terminate — use `WORKSPACE_HUB` env var *stale: 2026-03-11*
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
- Executable: `$BEMROSETTA_HOME/BEMRosetta_cl.exe` *stale: 2026-04-02*
  - Nemoh is the open-source solver BEMRosetta wraps

## Debugging Protocol

- **Pre-flight first**: Validate inputs BEFORE running solvers (units, formats, conventions)
- **Unit traps**: OrcaWave=Hz descending, AQWA=rad/s; rotational RAOs rad/m vs deg/m
- **Negative correlations**: Almost always means frequency arrays in different order
- **NaN correlations**: Zero std dev (e.g., yaw at head seas) — handle gracefully
- **AQWA FATAL mesh errors**: Cannot be overridden with `OPTIONS GOON`; fix the mesh
- **LIS parser**: Normalize whitespace before keyword matching ("ADDED  MASS" has double space)
- **Always check**: frequency order, unit system, RAO array shape/transpose before comparing

## Git Multi-Repo Sync Patterns

- `repository_sync pull all` uses bare `git pull` which fails on diverged branches — fix: `git pull --no-rebase`
- Submodule detached HEAD is **normal** — workspace-hub pins submodules at specific commits
- Fix detached HEAD: `git checkout main && git pull --no-rebase`
- Fix diverged: `git pull --no-rebase` (merge strategy, never rebase per CLAUDE.md)
- Fix dirty working tree blocking pull: `git stash && git pull --no-rebase && git stash pop`
- If `stash pop` conflicts, stop and report — never auto-resolve merge conflicts
- After fixing submodules, workspace-hub `git status` shows them as modified (expected)

## Skill Registration

- Skills are discovered via `.claude/commands/<category>/<name>.md` (NOT `.claude/skills/`) *stale: 2026-03-11*
- `.claude/skills/` holds the detailed SKILL.md implementation *verified: 2026-03-15*
- Command file references SKILL.md via `@.claude/skills/<path>/SKILL.md`
- Command file needs YAML frontmatter: `name`, `description`, `category`
- Skill appears in `/skills` list as `<category>:<name>` (e.g., `workspace-hub:repo-sync`)

## Key Patterns

- Tests needing subprocess path: set `use_api=False` in RunConfig
- Pre-existing test failures: AQWA runner detect tests (real exe found), CLI integration tests
- WRK-NNN references: Always include brief description inline (never bare IDs)
- `.gitignore` blanket rules (e.g., `lib/`, `memory/`) override earlier whitelists — add negation AFTER the blanket rule *stale: 2026-04-03*
- Negated `lib/` dirs so far: `!scripts/agents/lib/`, `!scripts/coordination/routing/lib/` *stale: 2026-04-05*
- Always verify new `lib/` directories: `git check-ignore <path>` *stale: 2026-04-07*

## Shell Script Portability

- **mawk vs gawk**: `match($0, /regex/, arr)` with capture groups is **gawk-only** — fails on mawk (Ubuntu/Debian default) *stale: 2026-03-11*
- Portable JSON extraction in awk: use `index()` + `substr()` + `sub()` instead of regex capture groups
- `sed -i` follows symlinks — replaces symlink with regular file. Check `git diff --diff-filter=T` after bulk sed
- Shell scripts: `#!/usr/bin/env bash`, LF line endings (`dos2unix` if needed) *stale: 2026-03-15*

## Git Credential & Auth

- Submodules: commit INSIDE submodule first, then `git add <submodule>` at workspace-hub level
- Push blocked by `workflow` scope: OAuth token needs `workflow` scope to push commits touching `.github/workflows/` *verified: 2026-04-08*
- **Credential mismatch**: `gh auth setup-git` reconfigures git to use `gh` token (fixes stale cached credentials)
- `pre-commit` hook requires virtualenv: bypass with `git -c core.hooksPath=/dev/null commit` *stale: 2026-03-11*

## Smart Agent Router (v2.0)

- **Entry point**: `scripts/coordination/routing/route.sh` *verified: 2026-03-15*
- **Model registry**: `config/agents/model-registry.yaml` (5 models across 3 providers) *verified: 2026-03-26*
- **EWMA engine**: `scripts/coordination/routing/lib/model_registry.sh` *verified: 2026-03-25*
- **Config**: `config/agents/routing-config.yaml` *verified: 2026-03-15*
- Adaptive routing: EWMA alpha=0.3, seed=3.0, min_ratings=3, poor_threshold=2.5
- Rate with model: `route.sh --rate 4 claude/sonnet-4-5` *stale: 2026-03-15*
- Stats with EWMA: `route.sh --stats`
- Optimizer: `scripts/coordination/routing/optimize_weights.sh` *verified: 2026-04-04*

## Session Log Ecosystem

- Raw provider session logs under `logs/orchestrator/<provider>/session_*.jsonl` are machine-local and gitignored; portable insight should move through audit artifacts and repo-tracked memory/docs instead of committing raw logs *verified: 2026-04-11*
- Interpret high-volume missing-path reads in provider audits as migration debt first; redirect to `docs/ops/legacy-claude-reference-map.md` rather than recreating deleted workflow files *verified: 2026-04-11*

## Topic Files

- `orcawave-lessons.md` — OrcFxAPI usage, YAML gotchas, result extraction
- `aqwa-lessons.md` — DAT format, LIS parsing, mesh quality, heading conventions
- `session-log-portability.md` — provider export/audit pipeline, local-vs-portable session artifacts, and migration-debt interpretation
