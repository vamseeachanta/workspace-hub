# Follow-up prompt — recover Codex adversarial readiness artifact

Context: In the 2026-04-29 credit-burn approval-readiness batch for workspace-hub, the Codex lane logged useful adversarial findings in `logs/night-runs/ace1-codex-readiness-review-20260429.log` but failed to write the requested artifact `docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/codex-adversarial-readiness.md` because the Codex sandbox could not create/write via its normal tools.

Bounded task:
1. Read `logs/night-runs/ace1-codex-readiness-review-20260429.log` and extract the Codex final verdict/finding summary only.
2. Cross-check against the existing local artifacts:
   - `docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/adversarial-readiness-review.md`
   - `docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/approval-pack-elements-2540-2544.md`
   - `docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/approval-pack-additional-5.md`
3. Write one recovery artifact at `docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/codex-adversarial-readiness-recovered.md`.

Rules:
- Do not mutate GitHub labels, comments, issue state, or approval markers.
- Do not implement any issue.
- Do not relaunch the original Codex session or launch duplicate review sessions.
- Treat legal sanity gates as mandatory for raw data, client-derived context, standards extracts, public artifacts, and llm-wiki promotion.
- If the log lacks enough detail to reconstruct per-issue rows, say so explicitly and write only the recoverable summary.

Expected output schema:
- Executive verdict
- Recoverable Codex findings
- Gaps caused by failed artifact write
- Next actions to reach honest promotion readiness
