# 20-Issue Adversarial Planning Review Pack

Repo: `vamseeachanta/workspace-hub`
Date: 2026-04-15
Purpose: Prepare a single overnight Claude pass that performs planning-only work on 20 GitHub issues so they can be surfaced for approval and then executed tomorrow.

## Hard rules

- Planning and adversarial review only. No implementation.
- Do not modify source code, tests, production scripts, or operational machine state.
- Allowed write paths:
  - `docs/plans/`
  - `scripts/review/results/`
  - `docs/reports/`
- Forbidden write paths:
  - `src/`
  - `tests/`
  - runtime scripts outside `scripts/review/results/`
  - `.planning/plan-approved/`
- Do not create approval markers.
- Do not apply `status:plan-approved`.
- For issues already in `status:plan-review`, refresh/review the canonical plan and tighten it until it is approval-ready or explicitly blocked.
- For issues without a canonical plan, draft the plan first, then run adversarial planning review.

## Target queue (20 issues)

### A. Existing plan-review queue — review/tighten
1. #2045 — Onboard all agents to strict issue planning workflow
   - Plan: `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md`
2. #2046 — Audit compliance of strict issue planning workflow after rollout
   - Plan: `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md`
3. #2105 — chore(knowledge): define freshness cadences and staleness signals for intelligence assets
   - Plan: `docs/plans/2026-04-13-issue-2105-freshness-cadences-and-staleness-signals.md`
4. #2129 — chore(harness): automate issue-state drift and redundancy audit across GitHub + analysis artifacts
   - Plan: `docs/plans/2026-04-11-issue-2129-issue-state-drift-redundancy-audit.md`
5. #2206 — feat(knowledge): validate single-source-of-truth pyramid conformance across intelligence assets and execution workflows
   - Plan: missing; draft required
6. #2207 — feat(doc-intel): define standards/codes provenance + reuse contract for llm-wiki promotion
   - Plan: missing; draft required
7. #2209 — chore(knowledge): define durable-vs-transient knowledge boundary across wikis, issues, registries, and session artifacts
   - Plan: missing; draft required
8. #2216 — feat(naval-architecture): integrate /mnt/ace/acma-codes into llm-wiki and repo intelligence ecosystem
   - Plan: `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md`
9. #2227 — feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis
   - Plan: `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md`
10. #2229 — feat(windows-parity): validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live
    - Plan: `docs/plans/2026-04-13-issue-2229-licensed-win-1-live-validation.md`
11. #2269 — feat(openfoam): standardize ESI v2312 baseline workflow and validation
    - Plan: `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md`
12. #2270 — feat(blender): standardize headless baseline workflow and smoke render validation
    - Plan: missing; draft required
13. #2271 — feat(ecosystem): harden shared-skill propagation for engineering portability
    - Plan: missing; draft required
14. #2272 — test(portability): add repeatable OpenFOAM and Blender smoke verification
    - Plan: missing; draft required

### B. Newly staged planning candidates — draft + adversarial review
15. #2291 — fix(cron-health): harden failure detection and align task evidence contracts
    - Plan: `docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md`
16. #2292 — fix(queue-refresh): restore weekly queue refresh evidence and cron execution
    - Plan: `docs/plans/2026-04-15-issue-2292-queue-refresh-evidence-and-cron-execution.md`
17. #2293 — fix(wiki-ingest): make nightly ingest idempotent and push-status truthful
    - Plan: `docs/plans/2026-04-15-issue-2293-wiki-ingest-idempotent-and-push-status-truthful.md`
18. #2235 — chore(plans): add retention metadata section to issue plan template
    - Plan: missing; draft required
19. #2236 — chore(workflow): add post-closure promotion step to issue-planning-mode
    - Plan: missing; draft required
20. #2255 — feat(governance): reconcile GitHub plan-approval labels with local marker ledger
    - Plan: missing; draft required

## Expected per-issue outputs

For each issue in the queue:
1. Read live GitHub issue body/comments/labels and verify issue is still open.
2. Search repo context and prior plans before editing.
3. If canonical plan file is missing, create `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md` and update `docs/plans/README.md`.
4. Run adversarial planning review and save artifacts under `scripts/review/results/`.
5. Update the plan with review synthesis and explicit approval-readiness status.
6. Post a concise GitHub planning/review comment.
7. Ensure issue label state is accurate for planning status (`status:plan-review` if still under review; no execution approval).

## Morning goal

By morning, the queue should cleanly separate into:
- approval-ready plans for user review
- needs-revision plans with explicit blockers
- missing-scope / dependency issues that should not be executed tomorrow
