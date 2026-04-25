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

#### Canonical way to run the adversarial wave (#2323)

```bash
scripts/review/plan-review-fanout.sh docs/plans/YYYY-MM-DD-issue-NNN-slug.md
```

This wraps Claude + Codex + Gemini in parallel under the shared stance contract
at `scripts/review/plan-review-prompt.md`. It writes one per-provider artifact
plus a `-disagreement.md` summarizing verdict splits + per-provider unique
findings. Per-provider invocation shape is tuned to each CLI's known quirks
(Codex and Gemini get INLINE plan body; Claude gets an `@`-path reference;
Gemini runs from `cwd=/tmp` to dodge the `.gemini/agents/*.md` permissionMode
validation bug). Single-provider failure does not abort the other two — the
failing provider's artifact records `UNAVAILABLE`.

Flags:

- `--providers=claude,codex,gemini` — subset of providers (comma-separated).
- `--output-dir=<dir>` — override the default `scripts/review/results/` sink
  (useful for batch / worktree / test runs).

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
| 2046 | planning-compliance-audit | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | 2026-04-09 | plan-approved | T2 | Audit agent compliance with planning workflow; 2026-04-21 fresh Codex MAJOR (marker contradiction + discovery gap + narrow stale-review heuristic) + Gemini MINOR; user retained approval with pending remediation |
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
| 2203 | pre-push-worktree-aware-tier1-gate | `docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md` | 2026-04-21 | draft | T2 | Harness plan to make pre-push classification worktree-aware so workspace-hub-only pushes are not blocked by unrelated sibling-repo failures |
| 2225 | acma-codes-source-registration-and-initial-indexing | `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md` | 2026-04-11 | completed | T2 | Closed after implementation plus host-side completion follow-up; historical review artifacts remain partial but this is no longer a pending cross-review item |
| 2226 | ocimf-csa-ledger-provenance-backfill | `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md` | 2026-04-11 | completed | T2 | Closed and implemented via commit `f37a542cf`; historical review artifacts remain partial but this is no longer a pending cross-review item |
| 2239 | automate-weekly-hermes-cross-machine-parity-review | `docs/plans/2026-04-12-issue-2239-automate-weekly-hermes-cross-machine-parity-review.md` | 2026-04-12 | completed | T2 | Weekly parity automation plan: cron script, YAML task, dated artifact output, and follow-on issue guidance |
| 2240 | macos-hermes-parity-install-config-and-tool-alignment | `docs/plans/2026-04-12-issue-2240-macos-hermes-parity-install-config-and-tool-alignment.md` | 2026-04-12 | completed | T2 | macOS workstation parity plan: registry/readiness coverage, Hermes path resolution, and documented platform-specific drift |
| 2227 | ocimf-tandem-csa-z276-wiki-promotion | `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` | 2026-04-12 | plan-review | T2 | Canonical bounded wiki-promotion plan for OCIMF Tandem Mooring, CSA Z276.1-20, CSA Z276.18, and a narrow provenance-grounded update to ocimf-meg4; 2026-04-21 rolled back from plan-approved after fresh Codex MAJOR (wiki/standards/ path contradiction + TDD spec gap + prereq matrix underspecified) |
| 2245 | acma-summary-classification-unblock | `docs/plans/2026-04-12-issue-2245-acma-summary-classification-unblock.md` | 2026-04-12 | plan-approved | T2 | Bounded summary/classification artifact preparation to unblock #2227 without broad ACMA processing |
| 2249 | index-level-other-bucket-bounded-context-packs | `docs/plans/2026-04-13-issue-2249-index-level-other-bucket-bounded-context-packs.md` | 2026-04-13 | adversarial-reviewed | T2 | Bounded triage plan to decompose the 44,705 index-level `other` records into context-recovery packs |
| 2250 | reconcile-stale-intelligence-summary-artifacts | `docs/plans/2026-04-13-issue-2250-reconcile-stale-intelligence-summary-artifacts.md` | 2026-04-13 | adversarial-reviewed | T2 | Control-plane drift remediation plan for stale convenience summaries versus canonical ledgers |
| 2280 | weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop | `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` | 2026-04-14 | draft | T2 | Parent governance plan defining weekly skills-maintenance audit rules, child implementation split, and cron artifact contract |
| 2281 | implement-v1-weekly-audit-for-existing-skills-curation-workflow | `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md` | 2026-04-14 | completed | T2 | Closed and implemented; no longer a pending cross-review item |
| 2282 | lock-classification-and-ranking-policy-for-weekly-skills-audit | `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md` | 2026-04-14 | completed | T2 | Follow-up policy plan defining deterministic classification, ranking, carry-forward, and escalation rules for weekly skills audit output |
| 2289 | bypass-rollback-recovery | `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` | 2026-04-21 | draft (v10 — external v9 review landed; approval-binding provenance, remediation classification, and audit/TDD precision tightened, but a fresh rerun is still required) | T1 | Policy-only plan choosing an advisor-only bypass handling mechanism (no auto-revert) plus canonical verdict taxonomy, timestamp normalization/tie-break rules, scenario matrix, audit contract, and TRUST-ARCHITECTURE cross-reference. Follow-on implementation tracked in #2445. |
| 2269 | openfoam-v2312-baseline-workflow-and-validation | `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md` | 2026-04-15 | plan-review | T2 | Canonical OpenFOAM ESI v2312 baseline workflow, smoke-case manifest, and deterministic validation contract for dev-secondary; 2026-04-21 rolled back from plan-approved after fresh Codex MAJOR (python3 vs uv run policy violation + unverified bootstrap path + ambiguous wrapper/runner contract) |
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
| 2311 | stage-transition-stale-reference-cleanup | `docs/plans/2026-04-17-issue-2311-stage-transition-stale-reference-cleanup.md` | 2026-04-17 | plan-approved | T2 | User-approved 2026-04-24; bounded stale-reference cleanup and targeted regression coverage may proceed under approved-plan/TDD gates |
| 2312 | lifecycle-script-authority-cleanup | `docs/plans/2026-04-17-issue-2312-lifecycle-script-authority-cleanup.md` | 2026-04-17 | draft | T2 | Bounded plan to replace deleted lifecycle-script guidance in current templates/docs with GitHub + .planning + refresh-helper authority |
| 2320 | skill-usage-audit | `docs/plans/2026-04-17-issue-2320-skill-usage-audit.md` | 2026-04-17 | implemented | T2 | Skill invocation scanner and baseline report merged into main during branch hygiene; original PR #2354 branch content preserved via merge. |
| 2332 | provider-audit-python3-runtime-cleanup | `docs/plans/2026-04-22-issue-2332-provider-audit-python3-runtime-cleanup.md` | 2026-04-22 | draft | T2 | Bounded plan to convert provider-audit python3 debt into ranked hotspots, explicit exceptions, and a first uv-run remediation wave |
| 2333 | provider-audit-drift-classification-expansion | `docs/plans/2026-04-22-issue-2333-provider-audit-drift-classification-expansion.md` | 2026-04-22 | draft | T2 | Bounded plan to separate true stale-path debt from generated-site, sibling-repo, symbolic, and transient drift families |
| 2321 | plugin-consolidation | `docs/plans/2026-04-17-issue-2321-plugin-consolidation.md` | 2026-04-17 | superseded | T2 | SPLIT into #2358 (docs + repo-tree overlap) and #2359 (semantic-scholar-mcp fix); central `git mv` mechanism was impossible (targets are plugin-owned, not repo-tracked) |
| 2322 | rule-promotion | `docs/plans/2026-04-17-issue-2322-rule-promotion.md` | 2026-04-17 | implemented | T2 | Promote two binary-checkable prose rules to Level-2 scripts (no-abs-paths, harness-file-size); third script deferred to follow-up. |

| 2323 | cross-ai-review-fanout | `docs/plans/2026-04-17-issue-2323-cross-ai-review-fanout.md` | 2026-04-17 | plan-review | T2 | Single-command plan-review fan-out across Claude/Codex/Gemini with disagreement report artifact |
| 2324 | memory-md-curation | `docs/plans/2026-04-17-issue-2324-memory-md-curation.md` | 2026-04-17 | implemented | T1 | Scope re-resolved to single-machine, non-git-tracked auto-memory; 2 orphans promoted, 1 resolved entry archived; report at `docs/reports/memory-curation-2026-04.md` |
| 2334 | validator-summary-done-min | `docs/plans/2026-04-17-issue-2334-validator-summary-done-min.md` | 2026-04-17 | plan-approved | T1 | User-approved via GH GUI after 3 review waves (Claude APPROVE rev-3; Codex sandbox unavailable rev-3). Lower `--summary-done-min` default 0.55 → 0.13 with docstring calibration note. |
| 2342+2343 | demo-detail-pages | `docs/plans/2026-04-17-issue-2342-2343-demo-detail-pages.md` | 2026-04-17 | plan-approved (v4-lite, self-approved 2026-04-19) | T2 | 3 review rounds: v1 MAJOR, v2 MAJOR, v3 Claude MINOR / Codex MAJOR. v4-lite fixes all 3 Codex MAJORs inline (nav/footer includes, CI→local-npm-test, actual sha256sum). 3 accepted follow-up items (Node engine pin, GH Actions workflow, apex sitemap backfill). Two-commit structure: Commit 1 = jumper retrofit + sitemap backfill; Commit 2 = Demos 1-4 + infra. Ready for implementation. Blocks Week 3 cold-email outreach. |
| 43 | wrk-1107-provider-assessment | `docs/plans/2026-04-19-issue-43-wrk-1107-provider-assessment.md` | 2026-04-19 | closed — rescoped to #2376 + #2377 | T2 | v1 Claude MINOR (10 absorbed). v2 Codex MAJOR (7) + Gemini MAJOR (2 genuine). Plan file preserved as historical artifact. |
| 43 (v3) | issue-43-v3 | `docs/plans/2026-04-20-issue-43-v3.md` | 2026-04-20 | closed — rescoped to #2376 + #2377 | T2 | v3 took all 3 v3 reviewers to MAJOR (triangulated convergence: fabricated schema fields `next_gap_seconds`/`gate_bypass`/`e.type`, broken session-analysis.sh jq merge, fictional routing-rules precedence, no Gemini data in corpus). Issue #43 closed 2026-04-20 in favor of corpus-honest split: #2376 (2-dim × 2-provider subset) + #2377 (upstream event emitters). Plan file preserved as historical artifact. |
| 2344 | capability-summary-pdf | `docs/plans/2026-04-19-issue-2344-capability-summary-pdf.md` | 2026-04-19 | plan-approved | T2 | v1 round-1 review: Claude MINOR, Codex REQUEST-CHANGES (4 MAJORs: non-reproducible render, Chrome-drift, font-portability, vercel immutable-cache). v2 reclassifies T1→T2: adds committed `scripts/gtm/render-capability-summary-pdf.sh` with pinned Chrome 147 assert + 6 post-render gates (1-page, Letter 612×792, Inter embedded via pdffonts, em-dash credentials, proof-point), vendors Inter WOFF2 locally to kill Google Fonts race, versioned public filename `capability-summary-v1.pdf` to work with `/assets/(.*)` 1-year immutable cache, sidecar `capability-summary.pdf.meta` records renderer version + sha256. Rollback corrected (no more "browsers sniff" claim — `X-Content-Type-Options: nosniff` site-wide). CTA wiring still deferred but now explicitly tracked as filed follow-up (not silently dropped). v2 round-2: Codex MAJOR caught past-tense artifact-claim drift (plan claimed scripts/assets committed that did not exist). v3 tense-audit (commit `d868a5d6c`) rewrites plan prose as PRESCRIBED/EXISTING, adds per-file WOFF2 SHA256 sidecars + OFL LICENSE, extends `.pdf.meta` with `git_sha` + `source_html_sha256`, adds version-bump policy. Round-3 Claude APPROVE (verdict at `scripts/review/results/2026-04-20-v3-plan-2344-claude.md`). Plan-approved 2026-04-20. |
| 2346 | prospect-data-pipeline | `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` | 2026-04-19 | plan-approved | T2 | v3.1 (2026-04-20) round-2 Claude review minor-fix pass (verdict MINOR, non-blocking per `scripts/review/results/2026-04-20-v2-plan-2346-claude.md`). Fixes: (D1) line 135 gating-mechanism table aligned with Files-to-Change — `/prospects/<hash>/index.html` → `/private/<hash>/<slug>.html` for internal path consistency with `robots.txt Disallow: /private/` + `X-Robots-Tag` header; (D2) sidecar enum + prose reconciled — line 459 prose states "all fallbacks F1-F5 are logged" and schema enum at line 472 expanded to `["F1","F2","F3","F4","F5"]` (full audit-trail completeness, subsumes TRIVIAL D5 on F4 rationale); (D3) new "Cross-repo deploy dependency" Risks subsection documents `aceengineer-website/` as a nested separate git repo requiring two distinct pushes (workspace-hub + aceengineer-website), Vercel auto-rebuild on the aceengineer-website push, and cross-repo rollback path; acceptance criteria 622-623 reclassified as post-deploy verification. TRIVIAL D6 applied: line 434 "four authorized fallbacks" rephrased as "five authorized fallbacks (F1 refuse + F2-F5 fix-paths)". v3 base retained all round-1 fixes (Codex MAJOR × 7, Claude CHANGES-REQUESTED × 3 MAJOR + 4 MINOR): Q5 canonical-vessel citation pins; executable draft-07 JSON-Schema; dual delivery state machine; private-log sidecar; canonical-fixture path isolation; gated URL plumbing; #2342/#2343 upstream sequencing; gitignore coverage. Ready for plan-approval decision. |
| 2367 | pdf-cta-wiring | `docs/plans/2026-04-20-issue-2367-pdf-cta-wiring.md` | 2026-04-20 | draft (v4) | T1 | #2344 follow-up. Wires Download-PDF CTA into `aceengineer-website/content/demos/index.html` hero + 4 methodology pages' `.method-cta` blocks, each linking to `capability-summary-v1.pdf` (gallery uses `{{ rootPath }}assets/…`; methodology pages use raw `../../assets/…` to match surrounding body style). Class `btn-info btn-lg` with `download` attribute; copy `"Download Capability Summary (PDF, 1 page)"`. 5-file additive HTML edit; methodology files are one-line-minified so implementation uses string-landmark Edits. Single `aceengineer-website` commit. **Both sequencing predecessors cleared 2026-04-20:** #2344 at `aceengineer-website` main `6f16cbd` (PDF live, 314 972 bytes, SHA256 `84b3febd2b…`, 1 page Letter); #2342+#2343 Commit 2 at `1b4adf1`. Runtime verification gates (`pdf_asset_exists_at_target`, `pdf_is_one_page`) retained as regression guards, not sequencing gates. Cross-repo: commits push to aceengineer-website remote. v2 defaults (approver objects): CTA copy, method-cta placement, hero gallery placement, detail-pages as separate follow-up. Review history: Claude r1 MINOR (8 findings → v2); Claude r2 APPROVE; Codex r1 silent-dropped; Codex r2 REQUEST-CHANGES (F1 1-page gate + F2 structural placement, reconstructed artifact → v3); Claude r3 MINOR (G1 missing v2-codex artifact, G2 regex ambiguity, G4 stale sequencing → v4); Codex r3 REQUEST-CHANGES (stale sequencing → v4). |
| 2348 | scanner-tos-triage | `docs/plans/2026-04-19-issue-2348-scanner-tos-triage.md` | 2026-04-19 | plan-approved | T2 | v3 (2026-04-20) integrates user answers to 3 design Qs: **Q9 (dead sources: REMOVE)** — `google`, `google_direct`, `rigzone` deleted from `SOURCE_RATE_LIMITS` + `SOURCE_ALLOWED_DOMAINS` (scanner.py:146-163); dead scrape functions + dispatcher calls removed; final `SOURCE_ALLOWLIST = {"indeed", "linkedin", "career_page", "example-board"}`; `TOS_REVIEW.md` REMOVED appendix. **Q10 (approver: owner-only)** — dual-path "counsel OR owner" collapsed to owner-only (user = Vamsee Achanta, business owner of ACE Engineer); sign-off = committed `Owner approved: <YYYY-MM-DD>` line per source. **Q11 (LinkedIn: KEEP)** — highest-volume source (584); robots.txt likely DENIES; reconciliation via doc-driven owner-override mechanism (`_OWNER_OVERRIDE_SOURCES` parsed from `TOS_REVIEW.md` at import — revocable by removing the block); API/RSS documented as deferred alternates. New TDD tests: `test_allowlist_contains_exactly_3_sources`, `test_tos_review_md_has_owner_signoff_per_source`, `test_owner_override_bypasses_disallow`. New risk on robots-vs-owner-directive conflict. Unpause checklist rewritten for 3-source reality. Round-2 review to dispatch after v3 commit. |
| 2357 | sitemap-www-backfill | `docs/plans/2026-04-21-issue-2357-sitemap-www-backfill.md` | 2026-04-21 | draft | T1 | Canonical local plan artifact for the follow-up sitemap host-normalization issue after #2391. Normalizes all `aceengineer-website/sitemap.xml` `<loc>` entries from apex to `www`, adds regression coverage for zero apex-host entries, and records current governance drift: live GitHub label may read `status:plan-approved`, but no local `.planning/plan-approved/2357.md` marker exists yet. |
| 2392 | wiki-coverage-gap-detector | `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` | 2026-04-20 | draft (v4 re-file in progress) | T2 | Reopened 2026-04-21 after #2405. Fresh Codex+Gemini v4 reviews still MAJOR; current blockers include source-vs-wiki normalization, join-bearing optional-input semantics, page-class boundary, scheduled-task/report distribution, duplicate doc_key handling, and unresolved-domain behavior. |
| 2393 | embeddings-index-l2-l3 | `docs/plans/2026-04-20-issue-2393-embeddings-index-l2-l3.md` | 2026-04-20 | **closed — rescoped to #2402 + #2403** | T3 | Split after v1 MAJOR×2: #2403 (model-selection spike) + #2402 (build+query with single authoritative tier). Plan preserved as historical. |
| 2394 | retrieval-augmented-planner | `docs/plans/2026-04-20-issue-2394-retrieval-augmented-planner.md` | 2026-04-20 | **closed — blocked by #2405** | T2 | 3 iter cross-review all MAJOR. Real defects carried forward: single classify_identity() helper, distinct BYPASSED outcome + git trailer, hard-dep mocking strategy, define all helpers in pseudocode, list-comprehension not set-sub. Plan + 7 review artifacts preserved. |
| 2395 | ecfr-ingestion | `docs/plans/2026-04-20-issue-2395-ecfr-ingestion.md` | 2026-04-20 | **closed — blocked by #2405** | T3 | 3 iter cross-review all MAJOR. Real defects carried forward (production-breaking): desync-repair must handle older parts not just current; natural_key needs str() coercion; eCFR rate limit is 16/min not 60/min (4× over spec); NFS atomicity fallback; scripts/data/doc_intelligence/ already exists; regulatory/CLAUDE.md schema-validated. Plan + 7 review artifacts preserved. |
| 2396 | doc-intel-mcp-server | `docs/plans/2026-04-20-issue-2396-doc-intel-mcp-server.md` | 2026-04-20 | **closed — rescoped to #2400 + #2401 + #2404** | T3 | Split after v1 MAJOR×2 (scope creep: title=3 tools, plan=5): #2400 (core 3 tools), #2401 (multi-agent registration), #2404 (audit log + hardened allowlist). Plan preserved as historical. |
| 2400 | mcp-server-core | — | 2026-04-20 | filed (no plan yet) | T2 | Successor of #2396 — MCP core 3 tools matching original title; sha256 enforcement; threat model; read-only behavioral tests. Plan to be drafted. |
| 2401 | mcp-multi-agent-registration | — | 2026-04-20 | filed (no plan yet) | T1 | Successor of #2396 — Claude + Gemini + Hermes registration. Depends on #2400. Plan to be drafted. |
| 2402 | embeddings-build-index | — | 2026-04-20 | filed (no plan yet) | T2 | Successor of #2393 — build+query with single authoritative tier; depends on #2403. Plan to be drafted. |
| 2403 | embeddings-model-selection-spike | `docs/plans/2026-04-20-issue-2403-embeddings-model-selection-spike.md` | 2026-04-20 | plan-review (iter-1 dispatched) | T2 | v1 plan drafted. Spike: ≥50-query eval set, per-model measurement JSON, decision doc. Cost cap $5. Blocks #2402. Cross-review in flight. |
| 2404 | mcp-audit-allowlist | — | 2026-04-20 | filed (no plan yet) | T2 | Successor of #2396 — audit log tier-3 + hardened allowlist (traversal/injection defense) + retention. Depends on #2400. Plan to be drafted. |
| 2405 | cross-review-sandbox-repo-access | `docs/plans/2026-04-20-issue-2405-cross-review-sandbox-repo-access.md` | 2026-04-20 | plan-review (v2 — iter-2 dispatched) | T2 | **Meta-issue**. v1 Codex+Gemini MAJOR (Class A real defects + Class B self-circular "unverified"). v2 fixes Class A: tier corrected to tier-3 transient; cache+dispatch-log removed; AC-test gaps filled; regex/allowlist consistent; SHA hashes payload not plan; partial-gh-failure test added; §3 Identity for payload; threat model covers symlink + private-metadata-to-third-party-provider. Class B accepted as self-circular — resolves at implementation. Blocks re-file of #2392/#2394/#2395. |
| 2391 | sitemap-404-fix | `docs/plans/2026-04-20-issue-2391-sitemap-404-fix.md` | 2026-04-20 | draft (v5) | T1 | Detected during #2342+#2343 Commit 1 deploy verification: `https://www.aceengineer.com/sitemap.xml` returns 404 because `aceengineer-website/build.js` never copies `sitemap.xml` into `dist/` (Vercel's `outputDirectory`). Plan picks **Option A** (extend `build.js` with a `copySitemap()` function mirroring `copyAssets()`, ~8 added lines); **rejects Option B on fitness** — per [Vercel Rewrites docs](https://vercel.com/docs/routing/rewrites), rewrites support same-app and external-origin rewrites only, NOT arbitrary repo-root files outside `outputDirectory`; serving sitemap.xml via B would require including it in `outputDirectory` (=Option A), a [Vercel Function](https://vercel.com/docs/functions), or an external-origin proxy — each strictly more complex than a build-time copy. Defers **Option C** (auto-generate from `dist/` listing) as a follow-up. Also updates `robots.txt` to advertise the `www.` host instead of apex to remove an unnecessary 301 hop. **v5 architectural change from v4: decoupled #2391 from #2357** — deploy-gate removed per Codex round-4 P1 argument that a live 404 fix should not be blocked on a separate editorial cleanup; accept bounded 301-hop canonicalization window until #2357 lands independently. Also v5: auto-memory citations annotated (unanimous P3); acceptance split into technical-must-pass vs process follow-ups (Codex P2); regression check narrowed from `dist/*.html` file-count to change-surface invariants (Codex P2). Review history: v3 → round-2 (Codex REQUEST-CHANGES F1/F2/F3 + Claude MINOR); v4 → Claude round-3 MINOR; v5 → round-4 Claude APPROVE / Gemini MINOR / Codex MAJOR. Cross-repo discipline: two distinct pushes (aceengineer-website for the fix; workspace-hub for plan/governance). |
| 2397 | canonical-folder-structure-and-refactor-contract | `docs/plans/2026-04-20-issue-2397-canonical-folder-structure-and-refactor-contract.md` | 2026-04-20 | draft | T2 | Canonical tier-1 repo anatomy contract, drift inventory, migration matrix, and future guardrail design |
| 1525 | workspace-hub-mission-control-plane-contract | `docs/plans/2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md` | 2026-04-21 | draft | T2 | First approval packet for canonicalizing workspace-hub mission, non-goals, tier-1 repo roles, and the current llm-wiki control-plane stance without pre-deciding #2398 |
| 2398 | llm-wiki-spinout-vs-embedded-architecture | `docs/plans/2026-04-20-issue-2398-llm-wiki-spinout-vs-embedded-architecture.md` | 2026-04-20 | draft | T2 | Strategy plan comparing embedded vs standalone vs hybrid llm-wiki boundaries for the repo ecosystem |
| 2399 | next-model-release-readiness-contract | `docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md` | 2026-04-20 | draft | T2 | Control-plane readiness contract, smoke/eval battery, and upgrade playbook for future model/provider releases |
| 2408 | workspace-hub-model-release-readiness-contract-and-upgrade-playbook | `docs/plans/2026-04-20-issue-2408-workspace-hub-model-release-readiness-contract-and-upgrade-playbook.md` | 2026-04-20 | draft | T2 | Narrowed child issue for workspace-hub-only readiness contract, upgrade playbook, and discoverability anchors |
| 2406 | codex-stdin-hang-fix | `docs/plans/2026-04-20-issue-2406-codex-stdin-hang-fix.md` | 2026-04-20 | plan-review (v3-final, iter-3/3) | T2 | Infra bug. `scripts/review/submit-to-codex.sh` hangs on "Reading additional input from stdin..." for substantial plan files. Root cause: positional-argv prompt delivery while codex falls back to reading stdin when it's a non-tty inherited pipe. Fix: pipe prompt via stdin, use `-` positional per CLI help contract; runtime version probe hard-fails (new exit 7) on older codex — no silent argv fallback. T26–T33 regression tests + 24 000-char deterministic fixture. Iter-1 MAJOR×2 → v2. Iter-2 Codex MAJOR Class A (fallback reintroduced bug, README ambiguity, operating-model cites, T27 newline, exit-3/5/6 AC→test, probe-cache state) → v3 hard-fail + full AC↔test traceability + T31–T33. Iter-3 Codex MAJOR caught 2 P1 internal-consistency contradictions (Files-to-Change + Risks still referenced argv fallback that v3 Pseudocode removed) → v3-final cleanup edits propagated hard-fail wording everywhere; AC cleanly separated test-backed vs release-gate. Iter-3 Gemini MAJOR pure Class B (self-circular). Cap reached; approval-ready. |
| 2407 | dependabot-triage-aceengineer-website | `docs/plans/2026-04-20-issue-2407-dependabot-triage.md` | 2026-04-20 | draft | T2 | Triage plan (NOT fix plan) for 29 open dependabot alerts on `vamseeachanta/aceengineer-website`: 1 critical (pbkdf2 GHSA-v62p-rq8g-8h59), 15 high, 12 medium, 1 low (qs GHSA-w7fw-mjwx-w883). Evidence check reveals all 29 alerts target `ref/py_react_sql/client/yarn.lock` — a subtree **deleted from `main` in commit `06f38714`** and absent from current `git/trees/main?recursive=1`; root `package.json` deps (`clean-css`, `jest`, `jest-environment-jsdom`, `posthtml`, `posthtml-expressions`, `posthtml-include`, `purgecss`) have **zero intersection** with the vuln list. Primary hypothesis: orphan-path — dismiss-with-rationale via `gh api -X PATCH dependabot/alerts/N state=dismissed`. Deliverable = classified 29-row triage table at `docs/security/aceengineer-website-vuln-triage-2026-04-20.md` + fix-cadence decision + follow-up implementation issue filed cross-referencing #2407. Cross-repo: triage doc in workspace-hub, any lockfile/package-json edits (if hypothesis rejected) land in aceengineer-website. Rollback trivial — docs-only. Adversarial review deferred per caller. |
| 2417 | repo-ecosystem-autoresearch-runner | `docs/plans/2026-04-20-issue-2417-repo-ecosystem-autoresearch-runner.md` | 2026-04-20 | draft | T2 | Generalize `skill-autoresearch-nightly.sh` into a reusable runner for skills + agents + templates + workflow-config targets while preserving keep/revert safety and wrapper compatibility |
| 2437 | workspace-hub-prune | `docs/plans/2026-04-21-issue-2437-workspace-hub-prune.md` | 2026-04-21 | plan-approved | T1 | Prune dangling WRK→GSD migration refs from `baseline-check.yml` (lines 52-64) and `.pre-commit-config.yaml` (lines 12-18); delete 2 orphan stubs under `scripts/work-queue/`. Cross-review: Claude APPROVE, Codex MAJOR→fixed (9 edits), Gemini APPROVE. Approved 2026-04-21; marker at `.planning/plan-approved/2437.md`. Child of #2424. |
| 2433 | worldenergydata-ci | `docs/plans/2026-04-21-issue-2433-worldenergydata-ci.md` | 2026-04-21 | plan-approved | T2 | Cross-repo CI fix on `vamseeachanta/worldenergydata`: extend `tests/conftest.py` `pytest_ignore_collect` to skip 22 broken test files (21 files + 1 dir), apply black reformats to 15 files, soften type-check to `continue-on-error: true`. Unblocks worldenergydata Dependabot PRs #329-#333. Claude MAJOR→fixed, Codex MAJOR→fixed, Gemini REJECT→Class-B attestation resolved (12 edits). Approved 2026-04-21; marker at `.planning/plan-approved/2433.md`. Child of #2424. |
| 2441 | digitalmodel-pylife-dep | `docs/plans/2026-04-21-issue-2441-digitalmodel-pylife-dep.md` | 2026-04-21 | plan-review | T1 | Cross-repo dep fix on `vamseeachanta/digitalmodel`: add `pylife>=2.2,<3.0` to `[project.dependencies]` in `digitalmodel/pyproject.toml`, regenerate `uv.lock`, add smoke import test at `tests/fatigue/test_package_imports.py`. Root cause: unconditional `from pylife.materiallaws.woehlercurve import WoehlerCurve` at `src/digitalmodel/fatigue/sn_curves.py:15` with pylife absent from deps (confirmed via failing run 24579096595, 10x ModuleNotFoundError). Path A chosen over Path B (guard import) — rationale in plan. Wave 2 cross-review pending. Child of #2424. |
| 2442 | assethold-python-tests | `docs/plans/2026-04-21-issue-2442-assethold-python-tests.md` | 2026-04-21 | plan-review | T2 | Cross-repo CI unblock on `vamseeachanta/assethold` (HIGH priority — never-green 7 months). 3-phase remediation: P1 (quote `DATABASE_URL: "sqlite:///:memory:"` ×2, bump `actions/upload-artifact@v3→v4` ×3 + `codeql upload-sarif@v2→v3`), P2 (fix `requirements.txt`→`requirements-consolidated.txt` ×3 sites — issue body under-counted at 1, verify `assetutilities` sibling-dep resolution), P3 (deferred matrix hardening). 9 fix sites total. Fork-config debt claim DISPROVEN — zero `samdansk2` refs in workflows. Wave 2 cross-review pending. Child of #2424. |
| 2443 | achantas-data-markdown-lint | `docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md` | 2026-04-21 | draft (v5 — external r4 review landed; python runtime, floor-rule exception wording, artifact traceability, and status maturity tightened, but fresh rerun still returns MAJOR) | T1 | Cross-repo CI add on `vamseeachanta/achantas-data` (docs-heavy hybrid, 495 .md vs 12 .py tracked). Add `markdownlint-cli2-action@v16` + `lycheeverse/lychee-action@v2` workflows plus lenient `.markdownlint.jsonc` config (disables MD013/MD033/MD041, keeps MD025 enabled with constrained overrides). First canonical markdown+link-check pair in the ecosystem — no sibling template existed. Issue body repo-shape claim corrected (NOT pure docs-only; idle `pyproject.toml`+`src/`+`tests/` scaffolding exists). |
| 2444 | aceengineer-admin-ci | `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md` | 2026-04-21 | draft (v6 — external r4/r5 reviews landed; status/review-state consistency, verifier artifact inventory, lockfile wording, and TDD working-directory context tightened, but a fresh post-v6 rerun is still required) | T1 | Cross-repo CI add on `vamseeachanta/aceengineer-admin`. Single new workflow adapted from `digitalmodel/.github/workflows/workflow-automation-tests.yml` (uv-native, matrix 3.11+3.12 on ubuntu-latest). Issue body test-count corrected: 12 test files (not 1); 10 under `tests/knowledge/` depend on `[knowledge-semantic]` extra — deferred behind first-run bootstrap. v6 keeps the hybrid lockfile policy and requires a truly fresh external rerun after historical `r4`/`r5` reviews. |
| 2459 | assethold-post-smoke-ci-hardening | `docs/plans/2026-04-22-issue-2459-assethold-post-smoke-ci-hardening.md` | 2026-04-22 | draft (hardened 2026-04-23 — CI-parity coverage evidence, temporary mypy-narrowing tradeoff framing, verifier-in-CI enforcement, and no-import/follow-up proofs added; still not approval-ready) | T2 | Post-#2448 CI hardening plan to align lint scope with maintained surfaces, repair the concrete watchlist/path-utils type blockers now visible after smoke passes, enforce the workflow verifier in CI, and explicitly record likely next coverage debt rather than implying immediate full-green CI. |
| 2460 | tier1-indexing-and-code-placement-contract | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` | 2026-04-22 | completed | T2 | Canonical contract for trusted tier-1 routing surfaces, derived per-repo checklist, daily freshness rule, and child-issue linkage for #2461-#2465. Approved after r16 Claude MINOR, Codex MINOR, Gemini APPROVE; implemented, validated, pushed to `main`, and closed completed on 2026-04-23. Follow-up contract decisions are locked for child issues #2461-#2465. |
| 2461 | assetutilities-routing-and-source-hygiene | `docs/plans/2026-04-22-issue-2461-assetutilities-routing-and-source-hygiene.md` | 2026-04-22 | draft | T2 | Assetutilities tier-1 routing/hygiene remediation plan: current README + docs/README + operator map + registry shape + removal of tracked backup artifacts; implementation blocked on #2460 contract lock and still needs non-Claude cross-review artifacts. |
| 2462 | digitalmodel-repo-wide-routing-surfaces | `docs/plans/2026-04-22-issue-2462-digitalmodel-repo-wide-routing-surfaces.md` | 2026-04-22 | draft | T2 | Digitalmodel repo-wide routing/index plan beyond the OrcaWave/OrcaFlex slice: docs/README, repo-wide operator map, canonical registry, and README/ROADMAP/domain-doc drift cleanup; strongest repo-specific execution candidate once #2460 contract is locked. |
| 2463 | aceengineer-website-canonical-routing-and-legacy-ref-cleanup | `docs/plans/2026-04-22-issue-2463-aceengineer-website-canonical-routing-and-legacy-ref-cleanup.md` | 2026-04-22 | draft | T2 | aceengineer-website routing-surface cleanup plan: repo-specific AGENTS routing section, docs/README, operator map, and GitHub-Pages/deploy.yml legacy-ref cleanup; still needs Codex/Gemini cross-review artifacts. |
| 2464 | workspace-hub-curated-routing-index | `docs/plans/2026-04-22-issue-2464-workspace-hub-curated-routing-index.md` | 2026-04-22 | draft | T2 | Workspace-hub control-plane routing plan: add curated tier-1 routing index, demote CONTENT_INDEX to raw inventory, link discoverability surfaces, and remove literal root-noise artifacts; currently only Claude self-review exists. |
| 2465 | daily-tier1-indexing-freshness-audit | `docs/plans/2026-04-22-issue-2465-daily-tier1-indexing-freshness-audit.md` | 2026-04-22 | plan-approved | T2 | User-approved daily freshness audit plan for the tier-1 routing contract: contract doc + local-safe cron script + schedule-tasks entry + cadence registration + regression tests; Codex/Gemini artifacts are UNAVAILABLE placeholders, so execution must preserve the r2 Claude/post-r2 constraints. |
| 2452 | worldenergydata-flake8-debt-first-wave | `docs/plans/2026-04-23-issue-2452-worldenergydata-flake8-debt-first-wave.md` | 2026-04-23 | plan-approved | T3 | User-approved worldenergydata lint-remediation umbrella/decomposition packet; r4 review returned Codex MINOR and Gemini APPROVE, with #2467 no lint-gate weakening, #2468 durable inventory ownership, and #2469 full main-branch `Lint` proof. Implementation may proceed under approved-plan gates. |
| 2438 | aceengineer-brand-identity-logo-resolution | `docs/plans/2026-04-23-issue-2438-aceengineer-brand-identity-logo-resolution.md` | 2026-04-23 | completed | T2 | Implemented and closed in `aceengineer-website` commit `47694fc`: canonical SVG/PNG logo assets, brand hierarchy doc, content-to-dist brand cleanup, legacy HTML/test/docs contract handling, and regression checks. |
| 2475 | licensed-load-run-proof-protocol | `docs/plans/2026-04-23-issue-2475-licensed-load-run-proof-protocol.md` | 2026-04-23 | plan-approved | T2 | User explicitly waived broken Codex/Gemini review-runner issue for #2475/#2476 on 2026-04-24. Approved to define licensed-win-1 native load/run proof protocol, self-contained prompt, evidence manifest, and failure classification before executing solver proof. |
| 2476 | llm-wiki-semantic-equivalence-contract | `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md` | 2026-04-23 | plan-approved | T2 | User explicitly waived broken Codex/Gemini review-runner issue for #2475/#2476 on 2026-04-24. Approved to define durable llm-wiki semantic-equivalence contract and fixture expansion cookbook before broadening structure-family proof coverage. |
| 510 | fix-20-test-failures | `docs/plans/2026-04-24-issue-510-fix-20-test-failures.md` | 2026-04-24 | plan-approved | T1 | OrcaFlex test-drift repair from overnight batch (digitalmodel subrepo). Renames `VariableDataSources`→`VariableData` + `SolidFrictionCoefficients`→`FrictionCoefficients` in 2 test files, fixes `docs/modules/orcaflex/`→`docs/domains/orcaflex/` path drift in 1 test file, anchors `TEST_EXAMPLES_DIR` to repo-root in 1 test file. Zero src/ edits. Review artifacts: `scripts/review/results/2026-04-24-plan-510-{claude,codex,gemini,adversarial,disagreement}.md`. Plan-scope-covered failures resolved; out-of-scope failures (builder_registry, orcaflex_cli, schema_compat, mooring_tension, test_batch_parallel_conversion stats-bug, 3 fixture-scoping ERRORs) remain for follow-ups per adversarial review D1. |
| 511 | orcaflex-campaign-spec-generation | `docs/plans/2026-04-24-issue-511-orcaflex-campaign-spec-generation.md` | 2026-04-24 | working | T2 | OrcaFlex parametric sweep mechanism + spec_only emission mode (digitalmodel subrepo). Phase 2 architecture blueprint at `docs/plans/2026-04-24-issue-511-blueprint-phase2.md`. 8 atomic TDD slices + 3 review fixes on digitalmodel branch `issue-511-campaign-spec-generation` (PR vamseeachanta/digitalmodel#533). User-locked decisions A1+B1+C1: full_factorial-only Literal, water_depths optional with at-least-one-axis model_validator, manifest.yml in scope. Path 1 design deviation (TDD-surfaced compat-shim blind spot, user-approved): canonical dumped-shape paths + bounds-checked list-index in `_set_nested_safe`. Test deltas: schema +22 (57→79), full orcaflex +31P with zero new failures vs #510 post-fix baseline. Review chain: `pr-review-toolkit:code-reviewer` 1 MAJOR (silent typo absorption) + 2 MINOR (alias shadowing, validate() crash on dotted keys) all fixed before push; 4 lower-priority MINOR deferred to follow-ups. Review artifacts: `scripts/review/results/2026-04-24-plan-511-{claude,codex,gemini,adversarial,disagreement}.md`. |
| 2480 | llm-wiki-e2e-smoke-test | `docs/plans/2026-04-24-issue-2480-llm-wiki-e2e-smoke-test.md` | 2026-04-24 | completed | T2 | Implemented and closed in commit `3f9a31954`: fixture tree + `test_e2e_smoke.py` (5 passed + 1 MCP-capability-gated skip) + scripts/data/llm-wiki/README.md. Regression suite green (15 passed, 1 skipped). Plan deviations documented (bypass network-coupled ingest CLI; distractor topic avoids single-doc IDF-zero). Nightly CI wiring intentionally deferred per user — pending #2366/#2465 audit-cadence landing. |
| 2481 | calc-output-citation-contract | `docs/plans/2026-04-24-issue-2481-calc-output-citation-contract.md` | 2026-04-24 | completed | T3 | Implemented and closed. workspace-hub side in commit `bd11f33bf`: contract doc, agent rule, worked example, #2471 forward-adopt frontmatter on dnv-os-e301.md + ocimf-meg4.md. digitalmodel side cherry-picked to `digitalmodel/main` as `c3be1472` (origin `8fc2f427` on issue-511 branch, not reverted). 8 smoke checks pass including fail-closed on missing page / frontmatter mismatch / wrong-root with `code_id` in every error. D1/D2/D3 decisions locked. Follow-ups: swap resolver to MCP when #2400 ships; migrate `mooring_design.py` Field defaults to call registry. |
| 2487 | inventory-readiness-spine | `docs/plans/2026-04-25-issue-2487-inventory-readiness-spine.md` | 2026-04-25 | plan-approved | T2 | User approved after v6 adversarial re-review. Ready for Codex TDD implementation of the machine-checkable raw-data to GTM readiness matrix and provider dispatch board. |
| 2482 | llm-wiki-gtm-boundary | `docs/plans/2026-04-24-issue-2482-llm-wiki-gtm-boundary.md` | 2026-04-24 | completed | T2 | Implemented and closed in commit `f7e905a05`: `docs/governance/llm-wiki-to-gtm-boundary.md` policy doc (allow/deny, 30-publisher enumeration, sanitization contract, 8 classification exercises), `knowledge/_archive/README.md` convention, quarantine of `knowledge-to-website-pipeline.md` → `knowledge/_archive/...`, #2022 closed as superseded, cross-issue pointers on #2463/#2390/#2485. Review chain: v1 MAJOR 5/4 → v2 MINOR(2MajSev) → v3 MINOR(1Maj+4Min) → v4 MINOR(0Maj+4Min) → v5 MAJOR 3/6 → v6 scope-split; 5 review artifacts retained at `scripts/review/results/2026-04-24-plan-2482-claude*.md`. Mechanical enforcement deferred to #2485. |
| 2485 | llm-wiki-gtm-boundary-enforcement | (plan pending; tracker issue only) | 2026-04-24 | tracker | T3 | Sibling of #2482. Mechanical enforcement layer (linter + ledger + pre-commit hook + yq/Python impl) rescoped out of #2482 governance doc. Design inherited from #2482 plan v2-v5 + review artifacts. Open design questions: `signoff_sha` semantics, concurrent ledger edits, revocation/expiry, missing-ledger-file behavior. Planning deferred until #2482 policy lands. |
| 2486 | v2-periodic-skill-ecosystem-housekeeping-audit | `docs/plans/2026-04-24-issue-2486-v2-periodic-skill-ecosystem-housekeeping-audit.md` | 2026-04-24 | plan-approved (implementation ready) | T2 | Extends existing deterministic weekly `skills-curation` loop with deterministic content-quality, grouping/taxonomy, size, waiver, trend, and local-only follow-up-candidate signals; initial MAJOR findings incorporated, Codex r2 MINOR + Gemini r2 MINOR incorporated, no remaining MAJOR blockers; user approved [#2486](https://github.com/vamseeachanta/workspace-hub/issues/2486). |
| 2488 | reconcile-untracked-active-skill-files-before-loss | `docs/plans/2026-04-25-issue-2488-reconcile-untracked-active-skill-files-before-loss.md` | 2026-04-25 | draft | T3 | Bounded skills-housekeeping plan to surface filesystem-only active skills, disposition loss-risk skill files, preserve mirror counting, and keep weekly audit local-only. |
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
