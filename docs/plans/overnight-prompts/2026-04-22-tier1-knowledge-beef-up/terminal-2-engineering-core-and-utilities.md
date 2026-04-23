You are working in `/mnt/local-analysis/workspace-hub`.

Overnight planning-only run. Do NOT implement source code. Your job is to make the engineering-core repo-routing wave more approval-ready for tomorrow.

Owned issues
- #2461 — `chore(assetutilities): canonical routing surfaces and source-hygiene cleanup for tier-1 issue work`
- #2462 — `feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex`

Mission
1. Tighten or create canonical plans for #2461 and #2462.
2. Make both plans evidence-driven using the tier-1 scorecard and live repo references.
3. Leave behind one summary artifact that clearly ranks which repo should execute first and why.

Mandatory stance
- Planning and adversarial review only.
- No implementation inside `assetutilities/` or `digitalmodel/`.
- No user questions.
- Do not create approval markers.
- Do not add `status:plan-approved`.

Owned write paths
- `docs/plans/2026-04-22-issue-2461-*.md` (create if missing or patch if present)
- `docs/plans/2026-04-22-issue-2462-*.md` (create if missing or patch if present)
- `docs/plans/README.md` (ONLY rows for #2461 and #2462)
- `docs/reports/2026-04-23-terminal-2-engineering-routing-summary.md`
- `scripts/review/results/*2461*`
- `scripts/review/results/*2462*`

Forbidden write paths
- any plan/review artifact for #2390, #2460, #2463, #2464, #2465
- `.planning/plan-approved/**`
- `assetutilities/src/**`
- `digitalmodel/src/**`
- `assetutilities/tests/**`
- `digitalmodel/tests/**`

Read-first sources
- `AGENTS.md`
- `docs/plans/2026-04-22-overnight-tier1-knowledge-beef-up-pack.md`
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`
- live GitHub issue bodies/comments for #2461 and #2462
- referenced repo docs in issue evidence sections (read-only only)

Internal workflow
1. Planner
   - Verify live issue state for #2461 and #2462.
   - Verify whether canonical plan files already exist.
2. Reviewer
   - Hunt for weak artifact maps, unbounded scope, stale file-path claims, and under-specified acceptance criteria.
   - Ensure #2461 stays focused on routing/hygiene and #2462 stays focused on repo-wide routing surfaces beyond the OrcaWave/OrcaFlex slice.
3. Implementer
   - Create or patch the two plans.
   - Generate/refresh review artifacts under `scripts/review/results/`.
   - Post concise GitHub comments on #2461 and #2462 describing plan state and blockers.
4. Tester
   - Verify `docs/plans/README.md` rows are accurate and only your two rows changed.
   - Verify no accidental edits touched nested engineering repos.
5. Synthesizer
   - Write `docs/reports/2026-04-23-terminal-2-engineering-routing-summary.md` with:
     - What changed per issue
     - Which issue is the best first execution candidate
     - Shared blocker patterns across digitalmodel and assetutilities
     - Suggested morning dispatch order

Validation expectations
- If a plan is missing, create it from template.
- Use concrete evidence paths from the live issues and scorecard.
- Prefer conservative truth over optimistic readiness claims.
- Explicitly call out any dependency on #2460 contract language if the repo-specific plan assumes it.

Output requirements
- Do not commit.
- Do not push.
- Print a concise completion summary listing exact files changed, exact issue comments posted, and exact blockers still open.