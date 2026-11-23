We are in /mnt/local-analysis/workspace-hub.

Mission:
Use the 10 stage-2 execution packs to draft follow-up/refinement issue text for items that should be split, refined, or corrected before implementation.

Primary focus issues:
- #2053 remaining production_rate scope
- #2055 equipment-count data source/scoping gap
- #2062 title/scope refinement
- #2057 cleanup reconciliation follow-up
- #2056 threshold regression / stale docs follow-up if closure should be split

Write exactly one persisted artifact:
- `docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-3-followup-issue-drafts.md`

Constraints:
1. Claude only.
2. Do NOT create GitHub issues.
3. Do NOT mutate production code.
4. Do NOT ask the user questions.

Required structure:
1. Which issues need follow-up and why
2. Draft issue titles
3. Draft issue bodies
4. Suggested labels
5. Dependency map
6. Final recommendation on what to split vs keep

Verification:
- produce at least 3 complete draft issue bodies
- include concrete file paths and acceptance criteria in each
