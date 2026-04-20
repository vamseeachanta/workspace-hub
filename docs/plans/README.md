# Issue Planning Workflow — Onboarding Guide and Plan Index

This document is the single onboarding reference for the mandatory issue planning workflow.
All agents (Claude, Codex, Gemini, Hermes) must follow this workflow for every GitHub issue.

## Why Planning Is Mandatory

Historical data shows that agents skipping the planning step produced incorrect implementations, wasted tokens, and created rework. The planning workflow catches problems before implementation begins, when they are cheapest to fix.

- **Plan review** answers: "Is this the right thing to build?"
- **Cross-review** answers: "Was the right thing built correctly?"

Both are required. Neither replaces the other.

## The Workflow (Step by Step)

```
1. INTAKE           — Read issue, classify complexity (T1/T2/T3)
2. RESOURCE INTEL   — Search existing code, standards, documents, prior plans
3. DRAFT PLAN       — Copy template, fill all sections, save to docs/plans/
4. ADVERSARIAL REVIEW — Route to 2+ AI providers; revise if MAJOR verdict
5. POST TO GITHUB   — Comment plan on issue, label status:plan-review
6. HARD STOP        — Wait for user approval (never self-approve)
7. USER APPROVES    — Swap label to status:plan-approved
8. IMPLEMENT        — TDD: tests first, then code, then full suite
9. CLOSE            — Commit, push, post summary, close issue
```

### Step 1: Intake

- Read the full issue body — scope, acceptance criteria, references
- Classify complexity:
  - **T1** (trivial): config, typo, single-file fix — brief plan, still requires approval
  - **T2** (standard): new module, multiple files, tests — full workflow
  - **T3** (complex): multi-module, architecture, standards — full workflow + subagents

### Step 2: Resource Intelligence

Before writing anything, search all available sources. The retrieval contract (#2208) defines minimum requirements by issue class.

**Universal minimum (ALL issues):**
- **Prior plans**: `docs/plans/` directory and this index
- **Existing code**: search relevant repos in affected paths for prior implementations
- **Recent issues**: related open/closed issues that may overlap or conflict
- **Intelligence entry points**: `docs/document-intelligence/README.md` (when available per #2104) or `docs/document-intelligence/data-intelligence-map.md`

**Issue-class-specific additions:**

| Issue class | Labels / triggers | Additional required sources |
|---|---|---|
| **General** | Default (no specific class match) | Universal minimum is sufficient |
| **Engineering** | `cat:engineering`, `cat:engineering-calculations`, `cat:engineering-methodology` | `standards-transfer-ledger.yaml`, `code-registry.yaml`, relevant domain wiki under `knowledge/wikis/`, `online-resource-registry.yaml` |
| **Data Pipeline** | `cat:data-pipeline` | `registry.yaml`, pipeline config, `resource-intelligence-maturity.yaml` |
| **Documentation** | `cat:documentation` | Governance docs in target directory, `CONTROL_PLANE_CONTRACT.md`, durable-vs-transient boundary policy (#2209) |
| **Harness/Infra** | `cat:harness` | `CONTROL_PLANE_CONTRACT.md`, `config/agents/` settings, `.claude/rules/` |
| **Knowledge/Intelligence** | Issues under #2205 tree, or touching `knowledge/`, `docs/document-intelligence/` | Operating model (#2205), sibling contracts (#2207, #2209), accessibility map (#2096), accessibility registry (when available per #2136) |

If classification is ambiguous or unlabeled, default to **General**. If an issue matches multiple classes, consult the **union** of all matching bundles.

**Evidence requirements:**
- ≥3 distinct sources must be listed in the plan's Resource Intelligence Summary (issue body counts as 1)
- Each source must cite a specific file path, issue number, or registry entry
- Each source must state a concrete finding — not vague claims like "searched the repo"
- The Gaps sub-section must list what must be built from scratch

Full retrieval contract specification: `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md`

### Step 3: Draft Plan

1. Copy the template: `docs/plans/_template-issue-plan.md`
2. Save as: `docs/plans/YYYY-MM-DD-issue-NNN-slug.md`
3. Fill all required sections (see "Required Sections" below)
4. Add a row to the Index table in this file

### Step 4: Adversarial Review

Route the plan to at least 2 other AI providers. Each gives a verdict:
- **APPROVE** — plan is sound
- **MINOR** — small issues, can proceed after fixing
- **MAJOR** — significant issues, must revise and re-review

Save review artifacts to `scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md`.

### Step 5: Post and Label

1. Post the completed plan as a GitHub issue comment
2. Apply label: `gh issue edit NNN --add-label "status:plan-review"`
3. **STOP** — do NOT write any implementation code

### Step 6: User Approval

The user (never the implementing agent) approves the plan:
- `gh issue edit NNN --remove-label "status:plan-review" --add-label "status:plan-approved"`
- Creates marker: `.planning/plan-approved/NNN.md`

### Step 7: Implement (TDD)

Only after `status:plan-approved` label exists:
1. Write tests first — confirm they fail
2. Implement minimum code to pass tests
3. Run full test suite — confirm no regressions
4. Self-review against approved plan

### Step 8: Close

- Conventional commit referencing the issue number
- Push to remote
- Post summary comment on issue: what was done, test results, review verdicts
- Close the issue

**Retrieval evidence at closeout** (per #2208 contract):
- The close comment must include a "Sources consumed" line listing intelligence assets that materially informed implementation (≥1 item)
- The close comment should include a "Promotion candidates" line: "none" or specific findings worth promoting from transient (L5) to durable knowledge (L3) per #2209 Section 7

### Retrieval Evidence at Review Time

Adversarial review artifacts (`scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md`) should include a Retrieval Adequacy assessment:

| Check | What the reviewer verifies |
|---|---|
| Resource Intelligence Summary non-empty, ≥3 sources | Plan contains adequate evidence |
| Issue-class-specific sources checked | Obvious sources for the issue class were not missed |
| Evidence is specific | Plan cites file paths and concrete findings, not vague claims |

Reviewers should note a retrieval verdict: `adequate` or `insufficient` with specific gaps.

## Batch / Overnight Sessions

When the user is not present:
- Draft plans and label `status:plan-review` — do NOT implement
- Only implement issues already labeled `status:plan-approved`
- User reviews results the next morning

## Status Meanings

| Status | Meaning |
|---|---|
| draft | Plan file exists locally but has not yet completed adversarial review |
| adversarial-reviewed | Frontier-model review passed; ready to post for user review |
| plan-review | Posted to GitHub; waiting for user approval |
| plan-approved | User approved; ready for implementation or batch execution |
| superseded | Replaced by a newer version of the plan |
| completed | Issue implemented and closed |

## Required Sections in Each Plan

Every plan file must include (see `_template-issue-plan.md` for full format):

1. **Resource Intelligence Summary** — evidence contract: ≥3 sources with specific paths/findings, issue-class-appropriate sources, gaps identified (see template and #2208 contract)
2. **Artifact Map** — paths to plan, tests, implementation, review files
3. **Deliverable** — one sentence: what will exist after this issue is done
4. **Pseudocode** — 5-15 lines per function (T2/T3); "trivial" note for T1
5. **Files to Change** — action, path, reason for each file
6. **TDD Test List** — one row per test with name, verification, input, output
7. **Acceptance Criteria** — checkboxes for all verification steps
8. **Adversarial Review Summary** — provider, verdict, key findings
9. **Risks and Open Questions** — what could go wrong, what needs user input
10. **Complexity** — T1, T2, or T3 with justification

## Enforcement

- **PreToolUse hook**: `.claude/hooks/plan-approval-gate.sh` blocks writes without approval marker
- **Pre-commit hook**: `scripts/enforcement/require-plan-approval.sh --strict` blocks commits without approval
- **Labels**: `status:plan-review` (orange) and `status:plan-approved` (green) exist on the repo

## Key References

| Resource | Path |
|---|---|
| Plan template | `docs/plans/_template-issue-plan.md` |
| Planning skill | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Engineering workflow | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` |
| Hard-stop policy | `docs/standards/HARD-STOP-POLICY.md` |
| Review artifacts | `scripts/review/results/` |

---

## Plan Index

| Issue # | Title / Slug | Plan File | Date | Status | Complexity | Notes |
|---|---|---|---|---|---|---|
| 1963 | email-infrastructure-cluster-a | `docs/plans/2026-04-09-issue-1963-email-infrastructure-cluster-a.md` | 2026-04-09 | draft | T3 | Cluster A architecture plan anchored by #1963 |
| 2045 | agent-planning-onboarding | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | 2026-04-09 | plan-review | T2 | Onboard all agents to strict planning workflow |
| 2046 | planning-compliance-audit | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | 2026-04-09 | plan-review | T2 | Audit agent compliance with planning workflow |
| 2047 | planning-enforcement-escalation | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | 2026-04-09 | draft | T2 | Stronger enforcement if audit fails; depends on #2046 |
| 2018 | agent-bypass-resistance-technical-gates | `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` | 2026-04-13 | plan-review | T3 | Parent enforcement plan mapping landed gates, remaining bypass gaps, and bounded follow-on slices |
| 2024 | gmail-extract-and-act-pipeline | `docs/plans/2026-04-13-issue-2024-gmail-extract-and-act-pipeline.md` | 2026-04-13 | draft | T3 | T3 plan for replacing raw email archiving with structured extraction, thread state, and delete/reactivation workflow |
| 2127 | make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement | `docs/plans/2026-04-11-issue-2127-make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement.md` | 2026-04-11 | plan-approved | T2 | Runtime plan gate ignores documented enforcement env contract; plan covers hook, tests, and governance docs |
| 2128 | install-hooks-pre-push-chain-drift | `docs/plans/2026-04-11-issue-2128-install-hooks-pre-push-chain-drift.md` | 2026-04-11 | plan-approved | T2 | Wire enforcement-env and require-review-on-push into install-hooks pre-push chain; fix dead-code drift guard |
| 2129 | issue-state-drift-redundancy-audit | `docs/plans/2026-04-11-issue-2129-issue-state-drift-redundancy-audit.md` | 2026-04-11 | plan-review | T3 | Automated hygiene audit plan for stale artifacts, duplicates, stale premises, and parent/child drift; fresh 2026-04-15 Claude/Codex/Gemini review returned MAJOR so revision is required before approval |
| 2205 | multi-machine-llm-wiki-resource-doc-intelligence-operating-model | `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` | 2026-04-11 | plan-approved | T3 | Parent operating-model plan defining pyramid, information flow, and child issue tree for llm-wikis + resource/document intelligence |
| 2096 | intelligence-accessibility-map | `docs/plans/2026-04-13-issue-2096-intelligence-accessibility-map.md` | 2026-04-13 | plan-approved | T2 | Bounded completion/validation plan for the existing intelligence accessibility map deliverable |
| 2104 | canonical-entry-points-for-ecosystem-intelligence | `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md` | 2026-04-11 | completed | T2 | Closed and implemented via commits `b7a4b4885` + `3af234ecc`; historical review artifacts remain partial but this is no longer a pending cross-review item |
| 2216 | acma-codes-llm-wiki-repo-intelligence-integration | `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` | 2026-04-11 | plan-review | T2 | Rolled back from premature approval after fresh 2026-04-14 Codex+Gemini MAJOR reviews; plan must be rewritten against current live repo state before any approval step |
| 2229 | licensed-win-1-live-validation | `docs/plans/2026-04-13-issue-2229-licensed-win-1-live-validation.md` | 2026-04-13 | plan-review | T2 | Rolled back from premature approval after fresh 2026-04-14/15 Codex+Gemini+Claude MAJOR reviews; plan must be rewritten around real scheduler-triggered evidence, Windows approval-marker semantics, and explicit MemoryBridgeSync side-effect contracts before approval |
| 2136 | intelligence-accessibility-registry-with-machine-reachability | `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md` | 2026-04-11 | completed | T2 | Closed and implemented via commit `942c9e3a4`; historical review artifacts remain partial but this is no longer a pending cross-review item |
| 2105 | freshness-cadences-and-staleness-signals | `docs/plans/2026-04-13-issue-2105-freshness-cadences-and-staleness-signals.md` | 2026-04-13 | plan-review | T2 | Rolled back from premature approval after fresh 2026-04-14/15 Codex+Gemini+Claude MAJOR reviews; plan must be rewritten to resolve threshold-vocabulary collisions, scanner-scope decisions, missing #2207/#2209 retrieval, and source-of-truth precedence before approval |
| 2208 | intelligence-retrieval-contract-for-github-issue-workflows | `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md` | 2026-04-11 | completed | T2 | Retrieval contract defining minimum intelligence sources per workflow stage and issue class, evidence placement, and measurable checks |
| 2225 | acma-codes-source-registration-and-initial-indexing | `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md` | 2026-04-11 | completed | T2 | Closed after implementation plus host-side completion follow-up; historical review artifacts remain partial but this is no longer a pending cross-review item |
| 2226 | ocimf-csa-ledger-provenance-backfill | `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md` | 2026-04-11 | completed | T2 | Closed and implemented via commit `f37a542cf`; historical review artifacts remain partial but this is no longer a pending cross-review item |
| 2239 | automate-weekly-hermes-cross-machine-parity-review | `docs/plans/2026-04-12-issue-2239-automate-weekly-hermes-cross-machine-parity-review.md` | 2026-04-12 | completed | T2 | Weekly parity automation plan: cron script, YAML task, dated artifact output, and follow-on issue guidance |
| 2240 | macos-hermes-parity-install-config-and-tool-alignment | `docs/plans/2026-04-12-issue-2240-macos-hermes-parity-install-config-and-tool-alignment.md` | 2026-04-12 | completed | T2 | macOS workstation parity plan: registry/readiness coverage, Hermes path resolution, and documented platform-specific drift |
| 2227 | ocimf-tandem-csa-z276-wiki-promotion | `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` | 2026-04-12 | plan-review | T2 | Canonical bounded wiki-promotion plan for OCIMF Tandem Mooring, CSA Z276.1-20, CSA Z276.18, and a narrow provenance-grounded update to ocimf-meg4 |
| 2245 | acma-summary-classification-unblock | `docs/plans/2026-04-12-issue-2245-acma-summary-classification-unblock.md` | 2026-04-12 | plan-approved | T2 | Bounded summary/classification artifact preparation to unblock #2227 without broad ACMA processing |
| 2249 | index-level-other-bucket-bounded-context-packs | `docs/plans/2026-04-13-issue-2249-index-level-other-bucket-bounded-context-packs.md` | 2026-04-13 | adversarial-reviewed | T2 | Bounded triage plan to decompose the 44,705 index-level `other` records into context-recovery packs |
| 2250 | reconcile-stale-intelligence-summary-artifacts | `docs/plans/2026-04-13-issue-2250-reconcile-stale-intelligence-summary-artifacts.md` | 2026-04-13 | adversarial-reviewed | T2 | Control-plane drift remediation plan for stale convenience summaries versus canonical ledgers |
| 2280 | weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop | `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` | 2026-04-14 | draft | T2 | Parent governance plan defining weekly skills-maintenance audit rules, child implementation split, and cron artifact contract |
| 2281 | implement-v1-weekly-audit-for-existing-skills-curation-workflow | `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md` | 2026-04-14 | completed | T2 | Closed and implemented; no longer a pending cross-review item |
| 2282 | lock-classification-and-ranking-policy-for-weekly-skills-audit | `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md` | 2026-04-14 | completed | T2 | Follow-up policy plan defining deterministic classification, ranking, carry-forward, and escalation rules for weekly skills audit output |
| 2269 | openfoam-v2312-baseline-workflow-and-validation | `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` | 2026-04-15 | plan-review | T2 | Canonical OpenFOAM ESI v2312 baseline workflow, smoke-case manifest, and deterministic validation contract for dev-secondary |
| 2293 | wiki-ingest-idempotent-and-push-status-truthful | `docs/plans/2026-04-15-issue-2293-wiki-ingest-idempotent-and-push-status-truthful.md` | 2026-04-15 | draft | T2 | Bounded plan to make nightly wiki-ingest duplicate handling idempotent and push-status logging truthful |
| 2292 | queue-refresh-evidence-and-cron-execution | `docs/plans/2026-04-15-issue-2292-queue-refresh-evidence-and-cron-execution.md` | 2026-04-15 | draft | T2 | Bounded plan to restore queue-refresh cron evidence and distinguish pre-start failure from runtime failure |
| 2291 | cron-health-hardening-and-task-evidence-contracts | `docs/plans/2026-04-15-issue-2291-cron-health-hardening-and-task-evidence-contracts.md` | 2026-04-15 | draft | T2 | Bounded fix plan for cron-health false greens / false missing states and task evidence-contract drift |
| 2290 | deduplicate-7-exact-copy-skills-and-reconcile-3-dev-ops-leaf-collisions | `docs/plans/2026-04-15-issue-2290-deduplicate-7-exact-copy-skills-and-reconcile-3-dev-ops-leaf-collisions.md` | 2026-04-15 | completed | T2 | Closed and implemented; no longer a pending cross-review item |
| 2294 | salvage-2290-follow-on-learnings-for-regression-coverage-and-github-code-review-scope | `docs/plans/2026-04-15-issue-2294-salvage-2290-follow-on-learnings-for-regression-coverage-and-github-code-review-scope.md` | 2026-04-15 | draft | T2 | Bounded salvage plan to selectively promote stronger #2290 regression checks and review whether any alternate github-code-review guidance is worth importing without duplicating adjacent GitHub skills |
| 2206 | pyramid-conformance-checks | `docs/plans/2026-04-16-issue-2206-pyramid-conformance-checks.md` | 2026-04-16 | draft | T1 | Reconciliation plan — deliverable already exists; validates conformance checks against acceptance criteria |
| 2207 | standards-codes-provenance-reuse-contract | `docs/plans/2026-04-16-issue-2207-standards-codes-provenance-reuse-contract.md` | 2026-04-16 | draft | T1 | Reconciliation plan — deliverable already exists; validates provenance contract against acceptance criteria |
| 2209 | durable-vs-transient-knowledge-boundary | `docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md` | 2026-04-16 | draft | T1 | Reconciliation plan — deliverable already exists; validates boundary policy against acceptance criteria |
| 2235 | add-retention-metadata-section-to-plan-template | `docs/plans/2026-04-16-issue-2235-add-retention-metadata-section-to-plan-template.md` | 2026-04-16 | draft | T1 | Add retention section to plan template aligned with #2209 |
| 2236 | add-post-closure-promotion-step-to-issue-planning-mode | `docs/plans/2026-04-16-issue-2236-add-post-closure-promotion-step-to-issue-planning-mode.md` | 2026-04-16 | draft | T1 | Add post-closure promotion step to planning workflow per #2209/#2208 |
| 2255 | reconcile-github-plan-approval-labels-with-local-marker-ledger | `docs/plans/2026-04-16-issue-2255-reconcile-github-plan-approval-labels-with-local-marker-ledger.md` | 2026-04-16 | draft | T2 | Automate reconciliation between GitHub labels and local approval markers |
| 2270 | blender-headless-baseline-workflow-and-smoke-render-validation | `docs/plans/2026-04-16-issue-2270-blender-headless-baseline-workflow-and-smoke-render-validation.md` | 2026-04-16 | draft | T2 | Blender headless baseline workflow, smoke render, and validation contract for dev-secondary |
| 2271 | harden-shared-skill-propagation-for-engineering-portability | `docs/plans/2026-04-16-issue-2271-harden-shared-skill-propagation-for-engineering-portability.md` | 2026-04-16 | draft | T2 | Harden shared-skill propagation with dry-run safety and regression tests |
| 2272 | repeatable-openfoam-and-blender-smoke-verification | `docs/plans/2026-04-16-issue-2272-repeatable-openfoam-and-blender-smoke-verification.md` | 2026-04-16 | draft | T2 | Unified smoke verification for OpenFOAM and Blender baselines; depends on #2269 and #2270 |
| 1878 | restore-index-metadata | `docs/plans/2026-04-16-issue-1878-restore-index-metadata.md` | 2026-04-16 | completed | T2 | Closed via ops run 2026-04-16; 100% content_type, 16.1% summary_done; follow-ups #2305-#2309 |
| 2308 | gotcha-refresh | `docs/plans/2026-04-16-issue-2308-gotcha-refresh.md` | 2026-04-16 | completed | T1 | Closed 2026-04-17 — commits f90c34311 + 11c0861d5 + 8c9d73690 |
| 2306 | maturity-yaml-additive | `docs/plans/2026-04-17-issue-2306-maturity-yaml-additive.md` | 2026-04-17 | completed | T1 | Closed 2026-04-17 — commit a13da73df |
| 2307 | accessibility-registry-declaration | `docs/plans/2026-04-17-issue-2307-accessibility-registry-declaration.md` | 2026-04-17 | completed | T1 | Closed 2026-04-17 — commit 25d90339c |
| 2305 | conference-batch-baseline | `docs/plans/2026-04-17-issue-2305-conference-batch-baseline.md` | 2026-04-17 | completed | T1 | Closed 2026-04-17 by decision — commit ba4ad9954; successor #2325 filed |
| 2309 | summary-fields-split | `docs/plans/2026-04-17-issue-2309-summary-fields-split.md` | 2026-04-17 | completed | T2 | Closed 2026-04-17 — code in auto-sync `91e17adf4`, live re-enrichment showed 87.90% summary_file_exists vs 16.13% summary_done |
| 2311 | stage-transition-stale-reference-cleanup | `docs/plans/2026-04-17-issue-2311-stage-transition-stale-reference-cleanup.md` | 2026-04-17 | draft | T2 | Bounded plan to confine deleted stage-transition script names to intentional legacy/history surfaces and add targeted regression coverage |
| 2312 | lifecycle-script-authority-cleanup | `docs/plans/2026-04-17-issue-2312-lifecycle-script-authority-cleanup.md` | 2026-04-17 | draft | T2 | Bounded plan to replace deleted lifecycle-script guidance in current templates/docs with GitHub + .planning + refresh-helper authority |
| 2320 | skill-usage-audit | `docs/plans/2026-04-17-issue-2320-skill-usage-audit.md` | 2026-04-17 | plan-review | T2 | Claude MINOR + Codex MAJOR + Gemini MAJOR — 90d vs 15d retention, provider-schema gap; needs revision before approval |
| 2321 | plugin-consolidation | `docs/plans/2026-04-17-issue-2321-plugin-consolidation.md` | 2026-04-17 | superseded | T2 | SPLIT into #2358 (docs + repo-tree overlap) and #2359 (semantic-scholar-mcp fix); central `git mv` mechanism was impossible (targets are plugin-owned, not repo-tracked) |
| 2322 | rule-promotion | `docs/plans/2026-04-17-issue-2322-rule-promotion.md` | 2026-04-17 | plan-review | T2 | Promote three binary-checkable prose rules in `.claude/rules/*.md` to Level-2 scripts under `scripts/enforcement/` |
| 2323 | cross-ai-review-fanout | `docs/plans/2026-04-17-issue-2323-cross-ai-review-fanout.md` | 2026-04-17 | plan-review | T2 | Single-command plan-review fan-out across Claude/Codex/Gemini with disagreement report artifact |
| 2324 | memory-md-curation | `docs/plans/2026-04-17-issue-2324-memory-md-curation.md` | 2026-04-17 | implemented | T1 | Scope re-resolved to single-machine, non-git-tracked auto-memory; 2 orphans promoted, 1 resolved entry archived; report at `docs/reports/memory-curation-2026-04.md` |
| 2334 | validator-summary-done-min | `docs/plans/2026-04-17-issue-2334-validator-summary-done-min.md` | 2026-04-17 | plan-approved | T1 | User-approved via GH GUI after 3 review waves (Claude APPROVE rev-3; Codex sandbox unavailable rev-3). Lower `--summary-done-min` default 0.55 → 0.13 with docstring calibration note. |
| 2342+2343 | demo-detail-pages | `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` | 2026-04-17 | plan-approved (v4-lite, self-approved 2026-04-19) | T2 | 3 review rounds: v1 MAJOR, v2 MAJOR, v3 Claude MINOR / Codex MAJOR. v4-lite fixes all 3 Codex MAJORs inline (nav/footer includes, CI→local-npm-test, actual sha256sum). 3 accepted follow-up items (Node engine pin, GH Actions workflow, apex sitemap backfill). Two-commit structure: Commit 1 = jumper retrofit + sitemap backfill; Commit 2 = Demos 1-4 + infra. Ready for implementation. Blocks Week 3 cold-email outreach. |
| 43 | wrk-1107-provider-assessment | `docs/plans/2026-04-19-issue-43-wrk-1107-provider-assessment.md` | 2026-04-19 | closed — rescoped to #2376 + #2377 | T2 | v1 Claude MINOR (10 absorbed). v2 Codex MAJOR (7) + Gemini MAJOR (2 genuine). Plan file preserved as historical artifact. |
| 43 (v3) | issue-43-v3 | `docs/plans/2026-04-20-issue-43-v3.md` | 2026-04-20 | closed — rescoped to #2376 + #2377 | T2 | v3 took all 3 v3 reviewers to MAJOR (triangulated convergence: fabricated schema fields `next_gap_seconds`/`gate_bypass`/`e.type`, broken session-analysis.sh jq merge, fictional routing-rules precedence, no Gemini data in corpus). Issue #43 closed 2026-04-20 in favor of corpus-honest split: #2376 (2-dim × 2-provider subset) + #2377 (upstream event emitters). Plan file preserved as historical artifact. |
| 2344 | capability-summary-pdf | `docs/plans/2026-04-19-issue-2344-capability-summary-pdf.md` | 2026-04-19 | plan-approved | T2 | v1 round-1 review: Claude MINOR, Codex REQUEST-CHANGES (4 MAJORs: non-reproducible render, Chrome-drift, font-portability, vercel immutable-cache). v2 reclassifies T1→T2: adds committed `scripts/gtm/render-capability-summary-pdf.sh` with pinned Chrome 147 assert + 6 post-render gates (1-page, Letter 612×792, Inter embedded via pdffonts, em-dash credentials, proof-point), vendors Inter WOFF2 locally to kill Google Fonts race, versioned public filename `capability-summary-v1.pdf` to work with `/assets/(.*)` 1-year immutable cache, sidecar `capability-summary.pdf.meta` records renderer version + sha256. Rollback corrected (no more "browsers sniff" claim — `X-Content-Type-Options: nosniff` site-wide). CTA wiring still deferred but now explicitly tracked as filed follow-up (not silently dropped). v2 round-2: Codex MAJOR caught past-tense artifact-claim drift (plan claimed scripts/assets committed that did not exist). v3 tense-audit (commit `d868a5d6c`) rewrites plan prose as PRESCRIBED/EXISTING, adds per-file WOFF2 SHA256 sidecars + OFL LICENSE, extends `.pdf.meta` with `git_sha` + `source_html_sha256`, adds version-bump policy. Round-3 Claude APPROVE (verdict at `scripts/review/results/2026-04-20-v3-plan-2344-claude.md`). Plan-approved 2026-04-20. |
| 2346 | prospect-data-pipeline | `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` | 2026-04-19 | draft (v3.1) | T2 | v3.1 (2026-04-20) round-2 Claude review minor-fix pass (verdict MINOR, non-blocking per `scripts/review/results/2026-04-20-v2-plan-2346-claude.md`). Fixes: (D1) line 135 gating-mechanism table aligned with Files-to-Change — `/prospects/<hash>/index.html` → `/private/<hash>/<slug>.html` for internal path consistency with `robots.txt Disallow: /private/` + `X-Robots-Tag` header; (D2) sidecar enum + prose reconciled — line 459 prose states "all fallbacks F1-F5 are logged" and schema enum at line 472 expanded to `["F1","F2","F3","F4","F5"]` (full audit-trail completeness, subsumes TRIVIAL D5 on F4 rationale); (D3) new "Cross-repo deploy dependency" Risks subsection documents `aceengineer-website/` as a nested separate git repo requiring two distinct pushes (workspace-hub + aceengineer-website), Vercel auto-rebuild on the aceengineer-website push, and cross-repo rollback path; acceptance criteria 622-623 reclassified as post-deploy verification. TRIVIAL D6 applied: line 434 "four authorized fallbacks" rephrased as "five authorized fallbacks (F1 refuse + F2-F5 fix-paths)". v3 base retained all round-1 fixes (Codex MAJOR × 7, Claude CHANGES-REQUESTED × 3 MAJOR + 4 MINOR): Q5 canonical-vessel citation pins; executable draft-07 JSON-Schema; dual delivery state machine; private-log sidecar; canonical-fixture path isolation; gated URL plumbing; #2342/#2343 upstream sequencing; gitignore coverage. Ready for plan-approval decision. |
| 2367 | pdf-cta-wiring | `docs/plans/2026-04-20-issue-2367-pdf-cta-wiring.md` | 2026-04-20 | draft | T1 | #2344 follow-up. Wires Download-PDF CTA into `aceengineer-website/content/demos/index.html` + 4 methodology pages (`compound-engineering`, `enforcement`, `orchestrator-worker`, `multi-agent-parity`), each linking to `{{ rootPath }}assets/capability-summary-v1.pdf`. 5-file additive HTML edit, single `aceengineer-website` commit. **Sequenced AFTER #2344 implementation** (PDF asset must exist on disk) **AND AFTER #2342+#2343 Commit 2** (gallery file conflict avoidance). Cross-repo: commits push to aceengineer-website remote, not workspace-hub. Open questions for user: CTA button copy; methodology-page placement (inside `method-cta` block vs TOC sidebar). Adversarial review not yet dispatched. |
| 2348 | scanner-tos-triage | `docs/plans/2026-04-19-issue-2348-scanner-tos-triage.md` | 2026-04-19 | plan-approved | T2 | v3 (2026-04-20) integrates user answers to 3 design Qs: **Q9 (dead sources: REMOVE)** — `google`, `google_direct`, `rigzone` deleted from `SOURCE_RATE_LIMITS` + `SOURCE_ALLOWED_DOMAINS` (scanner.py:146-163); dead scrape functions + dispatcher calls removed; final `SOURCE_ALLOWLIST = {"indeed", "linkedin", "career_page", "example-board"}`; `TOS_REVIEW.md` REMOVED appendix. **Q10 (approver: owner-only)** — dual-path "counsel OR owner" collapsed to owner-only (user = Vamsee Achanta, business owner of ACE Engineer); sign-off = committed `Owner approved: <YYYY-MM-DD>` line per source. **Q11 (LinkedIn: KEEP)** — highest-volume source (584); robots.txt likely DENIES; reconciliation via doc-driven owner-override mechanism (`_OWNER_OVERRIDE_SOURCES` parsed from `TOS_REVIEW.md` at import — revocable by removing the block); API/RSS documented as deferred alternates. New TDD tests: `test_allowlist_contains_exactly_3_sources`, `test_tos_review_md_has_owner_signoff_per_source`, `test_owner_override_bypasses_disallow`. New risk on robots-vs-owner-directive conflict. Unpause checklist rewritten for 3-source reality. Round-2 review to dispatch after v3 commit. |
| 2392 | wiki-coverage-gap-detector | `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` | 2026-04-20 | **closed — blocked by #2405 (review-sandbox infra)** | T2 | 3 iter cross-review all MAJOR. Real defects carried forward to re-file post #2405: sha256 enforcement, wiki doc_key extraction mechanism, classify_discipline definition, L3-eligibility heuristic definition, #2360 consistency, code-registry.yaml path. Plan + 7 review artifacts preserved. |
| 2393 | embeddings-index-l2-l3 | `docs/plans/2026-04-20-issue-2393-embeddings-index-l2-l3.md` | 2026-04-20 | **closed — rescoped to #2402 + #2403** | T3 | Split after v1 MAJOR×2: #2403 (model-selection spike) + #2402 (build+query with single authoritative tier). Plan preserved as historical. |
| 2394 | retrieval-augmented-planner | `docs/plans/2026-04-20-issue-2394-retrieval-augmented-planner.md` | 2026-04-20 | **closed — blocked by #2405** | T2 | 3 iter cross-review all MAJOR. Real defects carried forward: single classify_identity() helper, distinct BYPASSED outcome + git trailer, hard-dep mocking strategy, define all helpers in pseudocode, list-comprehension not set-sub. Plan + 7 review artifacts preserved. |
| 2395 | ecfr-ingestion | `docs/plans/2026-04-20-issue-2395-ecfr-ingestion.md` | 2026-04-20 | **closed — blocked by #2405** | T3 | 3 iter cross-review all MAJOR. Real defects carried forward (production-breaking): desync-repair must handle older parts not just current; natural_key needs str() coercion; eCFR rate limit is 16/min not 60/min (4× over spec); NFS atomicity fallback; scripts/data/doc_intelligence/ already exists; regulatory/CLAUDE.md schema-validated. Plan + 7 review artifacts preserved. |
| 2396 | doc-intel-mcp-server | `docs/plans/2026-04-20-issue-2396-doc-intel-mcp-server.md` | 2026-04-20 | **closed — rescoped to #2400 + #2401 + #2404** | T3 | Split after v1 MAJOR×2 (scope creep: title=3 tools, plan=5): #2400 (core 3 tools), #2401 (multi-agent registration), #2404 (audit log + hardened allowlist). Plan preserved as historical. |
| 2400 | mcp-server-core | — | 2026-04-20 | filed (no plan yet) | T2 | Successor of #2396 — MCP core 3 tools matching original title; sha256 enforcement; threat model; read-only behavioral tests. Plan to be drafted. |
| 2401 | mcp-multi-agent-registration | — | 2026-04-20 | filed (no plan yet) | T1 | Successor of #2396 — Claude + Gemini + Hermes registration. Depends on #2400. Plan to be drafted. |
| 2402 | embeddings-build-index | — | 2026-04-20 | filed (no plan yet) | T2 | Successor of #2393 — build+query with single authoritative tier; depends on #2403. Plan to be drafted. |
| 2403 | embeddings-model-selection-spike | — | 2026-04-20 | filed (no plan yet) | T2 | Successor of #2393 — rubric + decision doc on BGE-M3 vs Voyage vs text-embedding-3-large. Plan to be drafted. |
| 2404 | mcp-audit-allowlist | — | 2026-04-20 | filed (no plan yet) | T2 | Successor of #2396 — audit log tier-3 + hardened allowlist (traversal/injection defense) + retention. Depends on #2400. Plan to be drafted. |
| 2405 | cross-review-sandbox-repo-access | — | 2026-04-20 | filed (no plan yet) | T2 | **Meta-issue** from 2026-04-20 review-cycle post-mortem. Cross-review sandbox has no repo/gh access → reviewers cannot verify "live-state" claims the prompt mandates → every plan returns MAJOR regardless of quality. **Blocks re-filing of #2392/#2394/#2395** with fresh iteration budget. Plan to be drafted. |
| 2391 | sitemap-404-fix | `docs/plans/2026-04-20-issue-2391-sitemap-404-fix.md` | 2026-04-20 | draft | T1 | Detected during #2342+#2343 Commit 1 deploy verification: `https://www.aceengineer.com/sitemap.xml` returns 404 because `aceengineer-website/build.js` never copies `sitemap.xml` into `dist/` (Vercel's `outputDirectory`). Plan picks **Option A** (extend `build.js` with a `copySitemap()` function mirroring `copyAssets()`, ~8 added lines); explicitly rejects **Option B** (Vercel rewrites cannot serve arbitrary repo-root files outside `dist/`); defers **Option C** (auto-generate from `dist/` listing) as a follow-up. Also updates `robots.txt` to advertise the `www.` host instead of apex to remove an unnecessary 301 hop. **#2357 apex→www backfill kept separate** — bundling would enlarge blast radius and force re-review of another open plan; #2357 lands as a follow-up PR. Cross-repo discipline noted: two distinct pushes (aceengineer-website for the fix; workspace-hub for plan/governance). Adversarial review not yet dispatched per caller instruction. |
| 2397 | canonical-folder-structure-and-refactor-contract | `docs/plans/2026-04-20-issue-2397-canonical-folder-structure-and-refactor-contract.md` | 2026-04-20 | draft | T2 | Canonical tier-1 repo anatomy contract, drift inventory, migration matrix, and future guardrail design |
| 2398 | llm-wiki-spinout-vs-embedded-architecture | `docs/plans/2026-04-20-issue-2398-llm-wiki-spinout-vs-embedded-architecture.md` | 2026-04-20 | draft | T2 | Strategy plan comparing embedded vs standalone vs hybrid llm-wiki boundaries for the repo ecosystem |
| 2399 | next-model-release-readiness-contract | `docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md` | 2026-04-20 | draft | T2 | Control-plane readiness contract, smoke/eval battery, and upgrade playbook for future model/provider releases |
## Entry Format

Add one row per plan:

```
| 1234 | short-slug | `docs/plans/2026-04-08-issue-1234-short-slug.md` | 2026-04-08 | plan-review | T2 | notes |
```

## Notes for Agents

- All plans go in `docs/plans/` — never in `.hermes/plans/` or `.planning/phases/`
- Keep this README updated whenever a new plan is created or its status changes
- Batch execution agents must only act on issues marked `status:plan-approved`
- If a plan is revised materially, update the row and mark the older version `superseded`
- Never self-approve a plan — the user or a designated operator must approve
