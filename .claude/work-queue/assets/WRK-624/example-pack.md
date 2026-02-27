# Example Pack: WRK-624

## Example 1: Route A Chore (Standard)
- **ID**: WRK-999
- **Complexity**: simple
- **Plan**: 3 bullet points in body
- **Review**: Self-review only
- **Closure**: `close-item.sh WRK-999`

## Example 2: Route B Feature (Standard)
- **ID**: WRK-888
- **Complexity**: medium
- **Plan**: Numbered steps in body
- **Review**: Claude, Codex, Gemini synthesis
- **Closure**: `close-item.sh WRK-888 <sha>`

## Example 3: Route C Architecture (Hardened)
- **ID**: WRK-777
- **Complexity**: complex
- **Plan**: `specs/wrk/WRK-777/plan.md`
- **Resource Pack**: `assets/WRK-777/resource-pack.md`
- **Review**: Per-phase (Explore, Implement, Test)
- **HTML Artifact**: `assets/WRK-777/review.html`

## Example 4: Legacy Migration
- **ID**: WRK-111
- **Status**: `complete` (in `pending/`)
- **Action**: `migrate-queue.py` moves to `done/`, updates status to `done`.

## Example 5: Stale Detection
- **ID**: WRK-222
- **Status**: `working`
- **Age**: 14 days
- **Action**: `remediation-report.py` flags it as stale.
