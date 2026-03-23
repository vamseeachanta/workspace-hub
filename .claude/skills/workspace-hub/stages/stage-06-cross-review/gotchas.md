# Stage 06: Cross-Review — Gotchas

## Operational Lessons (WRK-690)
- Explicit signal emission required (not just artifact presence); shared scripts must log lifecycle signals.
- User-review stages emit both stage signal AND browser-open signal (not collapsed).
- Keep close/archive signals distinct; emit `close_or_archive` aggregation for weekly reporting.
- Multi-agent: out-of-scope side effects are non-blocking; document under `Out-of-Scope Side Effects`.

## Edge Cases
- Codex quota fallback: when quota exhausted OR >=2 Codex reviews exist, auto-substitutes Claude Opus.
- Review iteration cap is 3/3 — no further review passes after cap reached.
