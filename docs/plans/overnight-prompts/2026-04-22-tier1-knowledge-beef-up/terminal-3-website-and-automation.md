You are working in `/mnt/local-analysis/workspace-hub`.

Overnight planning-only run. Do NOT implement source code. Your job is to make the website-routing + sustaining-automation portion of the repo-ecosystem wave more execution-ready by tomorrow.

Owned issues
- #2463 — `chore(aceengineer-website): canonical routing surfaces and legacy product-doc reference cleanup`
- #2465 — `feat(automation): daily tier-1 indexing freshness audit and scorecard refresh`

Mission
1. Tighten or create canonical plans for #2463 and #2465.
2. Keep the website-routing cleanup sharply scoped and evidence-based.
3. Turn the freshness-audit issue into a concrete, self-contained daily maintenance plan that supports the wider llm-wiki / tier-1 ecosystem.
4. Leave behind one summary artifact for tomorrow's operator.

Mandatory stance
- Planning and adversarial review only.
- No implementation inside `aceengineer-website/`, no cronjob creation, no runtime script changes.
- No user questions.
- Do not create approval markers.
- Do not add `status:plan-approved`.

Owned write paths
- `docs/plans/2026-04-22-issue-2463-*.md` (create if missing or patch if present)
- `docs/plans/2026-04-22-issue-2465-*.md` (create if missing or patch if present)
- `docs/plans/README.md` (ONLY rows for #2463 and #2465)
- `docs/reports/2026-04-23-terminal-3-website-automation-summary.md`
- `scripts/review/results/*2463*`
- `scripts/review/results/*2465*`

Forbidden write paths
- any plan/review artifact for #2390, #2460, #2461, #2462, #2464
- `.planning/plan-approved/**`
- `aceengineer-website/**`
- `scripts/cron/**`
- `tests/**`

Read-first sources
- `AGENTS.md`
- `docs/plans/2026-04-22-overnight-tier1-knowledge-beef-up-pack.md`
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`
- `docs/reports/tier-1-indexing-freshness-latest.md`
- live GitHub issue bodies/comments for #2463 and #2465

Internal workflow
1. Planner
   - Verify live issue state for #2463 and #2465.
   - Verify whether canonical plan files already exist.
2. Reviewer
   - For #2463, hunt for stale assumptions about the website repo structure and overbroad cleanup scope.
   - For #2465, ensure the daily audit remains local-safe, self-contained, and tied to canonical routing surfaces rather than noisy inventories.
3. Implementer
   - Create or patch the two plans.
   - Generate/refresh review artifacts under `scripts/review/results/`.
   - Post concise GitHub comments on #2463 and #2465 describing plan state and blockers.
4. Tester
   - Verify `docs/plans/README.md` rows are accurate and only your two rows changed.
   - Verify you did not accidentally create live cron jobs or implementation scripts.
5. Synthesizer
   - Write `docs/reports/2026-04-23-terminal-3-website-automation-summary.md` with:
     - What changed per issue
     - Whether #2465 is ready to become tomorrow's sustaining-loop work
     - Remaining blockers
     - Suggested morning sequence across #2463 and #2465

Validation expectations
- If a plan is missing, create it from template.
- Keep both issues planning-only and non-destructive.
- Use the current scorecard + freshness report as evidence, but do not overclaim readiness beyond that evidence.
- Make the relationship between website routing cleanup and the broader repo-ecosystem knowledge layer explicit where useful.

Output requirements
- Do not commit.
- Do not push.
- Print a concise completion summary listing exact files changed, exact issue comments posted, and exact blockers still open.