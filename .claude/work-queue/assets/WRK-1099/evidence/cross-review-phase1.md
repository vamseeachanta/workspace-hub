# WRK-1099 Cross-Review — Phase 1 (Plan)

Route A — single review pass.

## Providers
- **Claude**: REQUEST_CHANGES
- **Codex**: REQUEST_CHANGES (quota exhausted; Claude Opus fallback)
- **Gemini**: APPROVE

## P1 Findings (must fix)
- **TDD violation**: tests listed as step 6 after implementation — reordered in plan (tests now step 1)

## P2 Findings (addressed)
- `--subcategory` without `--category` undefined — plan updated: filters across all categories
- Hostname normalization: use `hostname -s`; cache as `THIS_HOST` once at top

## P3 Findings (deferred)
- ALL_CAPS array naming — consistent with existing script style; deferred

## Verdict after fixes: APPROVE TO PROCEED
All P1/P2 findings addressed in plan update.
