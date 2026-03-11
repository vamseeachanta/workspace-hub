# WRK-1016 Plan — Claude View

## Summary
Audit all settings files across the workspace-hub ecosystem and apply ≥5 concrete improvements for peak agent + human productivity.

## Route: B (Medium)

## Phase 1: Full Inventory & Audit (read-only)
1. List all `.claude/settings.json` across hub + submodules (size, mtime)
2. Measure hook latency: `time bash .claude/hooks/<hook>.sh < /dev/null` — flag >2s
3. Count lines in all `CLAUDE.md`/`AGENTS.md`/`CODEX.md`/`GEMINI.md` — flag >20
4. Review hub `settings.json` permissions allow/deny for gaps and overly-broad wildcards
5. Review `pyproject.toml` tool sections in tier-1 repos (assetutilities, digitalmodel, worldenergydata, assethold, OGManufacturing)
6. Plugin gap analysis: enabled plugins vs `anthropics/claude-plugins-official` catalogue

## Phase 2: Apply ≥5 Concrete Improvements
1. Slim `.claude/global/CLAUDE.md`: 35→≤20 lines; migrate excess to `.claude/docs/`
2. Slim tier-1 CLAUDE.md files: assetutilities(31), digitalmodel(31), worldenergydata(54), assethold(31) → ≤20 each
3. Permissions hardening: add deny patterns for `sudo:*`, `ssh:*`, `curl:*` if not already present; tighten wildcards
4. Slow hook remediation: profile any hook >2s; add `2>/dev/null || true` or optimize
5. pyproject.toml canonical baseline: apply `[tool.pytest.ini_options]` and `[tool.ruff]` to tier-1 repos

## Phase 3: Evidence & Capture
- verify-gate-evidence.py WRK-1016 → PASS
- Commit all changes; regenerate INDEX.md
- Comprehensive-learning entry: canonical settings baseline

## Test Strategy
- Before/after line counts asserted ≤20 for all slimmed files
- Hook latency table (before/after)
- Gate evidence verified (PASS)
- Legal scan passes on all changed files

## Verdict: APPROVE
This plan is well-scoped, incremental, and directly addresses known compliance violations. Risk is low — all changes are in config/doc files with no production code impact.
