# WRK-1016 Plan — Gemini View

**Verdict: MAJOR**

## Findings

1. **Missing cross-review step in Phase 3** — Plan omits mandatory `scripts/review/cross-review.sh <file> all` step. Route B requires cross-review before completion.

2. **Incomplete slimming scope** — Phase 2 only targets `CLAUDE.md` files. The ≤20-line limit applies to all adapter files: `AGENTS.md`, `GEMINI.md`, `CODEX.md`. These must also be audited and slimmed if over limit.

3. **Python runtime rule violation** — Step 12 calls `verify-gate-evidence.py` without `uv run`. Per `.claude/rules/python-runtime.md`, all Python scripts must be run via `uv run --no-project python <script>`.

## Resolution Required
- Add AGENTS.md/GEMINI.md/CODEX.md to slimming scope in Phase 2
- Add cross-review step to Phase 3
- Fix verify-gate-evidence.py invocation to use `uv run`
