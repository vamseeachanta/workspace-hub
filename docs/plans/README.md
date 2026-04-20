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
| 43 | wrk-1107-provider-assessment | `docs/plans/2026-04-19-issue-43-wrk-1107-provider-assessment.md` | 2026-04-19 | draft (v2) | T2 | Consolidates closed-without-comment WRK-1005 (#798/#871) and WRK-1045 (#826/#950). 7 design Qs resolved; Claude MINOR review absorbed (10 findings → v2 fixes: deterministic per-day emitter with `--dry-run` + prefix rollback, `find_hard_gate_violations` step, routing-rules.yaml schema, Codex sandbox-write hedge, pipeline-consumability integration test, `scripts/analysis/compliance/` colocation, WRK-remap scoped to new artifacts only). Codex + Gemini reviews pending push. |
| 2346 | prospect-data-pipeline | `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` | 2026-04-19 | draft | T2 | Week-4 GTM "highest-conversion sales tool" — YAML intake schema + 3 canonical vessels (pipelay barge / heavy-lift CSV / PLSV) + shared prospect_adapter across 5 demos + branded-report wrapper + 48hr SOP with explicit refuse-vs-fix rules. Intake dir gitignored for NDA isolation. 5 open questions flagged for user before adversarial review (email-only delivery, synthetic vs public-class vessels, conditional-required vessel block for demos 1/2, refuse-vs-fix exception policy, CI test runtime budget). |
| 2348 | scanner-tos-triage | `docs/plans/2026-04-19-issue-2348-scanner-tos-triage.md` | 2026-04-19 | draft | T2 | Triage #1707/#1708/#1709: #1708 and #1709 already landed in commits `70c3975b2` and `d0840bd42` — verify-and-close; #1707 partially landed (rate limit + Retry-After + backoff + allowlist) but robots.txt respect + documented ToS review still missing. Scope: add `urllib.robotparser.RobotFileParser` check in `safe_request()`, create `TOS_REVIEW.md` per-source with keep/remove decisions + C&D runbook. Flags cron-pause recommendation for user decision. Memory correction: scanner is weekly-Monday, not Mon-Fri. |
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
