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
| 2045 | agent-planning-onboarding | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | 2026-04-09 | plan-approved | T2 | Onboard all agents to strict planning workflow |
| 2046 | planning-compliance-audit | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | 2026-04-09 | adversarial-reviewed | T2 | Audit agent compliance with planning workflow |
| 2047 | planning-enforcement-escalation | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | 2026-04-09 | draft | T2 | Stronger enforcement if audit fails; depends on #2046 |
| 2018 | agent-bypass-resistance-technical-gates | `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` | 2026-04-13 | plan-approved | T3 | Parent enforcement plan mapping landed gates, remaining bypass gaps, and bounded follow-on slices |
| 2024 | gmail-extract-and-act-pipeline | `docs/plans/2026-04-13-issue-2024-gmail-extract-and-act-pipeline.md` | 2026-04-13 | draft | T3 | T3 plan for replacing raw email archiving with structured extraction, thread state, and delete/reactivation workflow |
| 2127 | make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement | `docs/plans/2026-04-11-issue-2127-make-plan-approval-gate-honor-force-plan-gate-strict-and-disable-enforcement.md` | 2026-04-11 | plan-approved | T2 | Runtime plan gate ignores documented enforcement env contract; plan covers hook, tests, and governance docs |
| 2128 | install-hooks-pre-push-chain-drift | `docs/plans/2026-04-11-issue-2128-install-hooks-pre-push-chain-drift.md` | 2026-04-11 | plan-approved | T2 | Wire enforcement-env and require-review-on-push into install-hooks pre-push chain; fix dead-code drift guard |
| 2205 | multi-machine-llm-wiki-resource-doc-intelligence-operating-model | `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` | 2026-04-11 | plan-approved | T3 | Parent operating-model plan defining pyramid, information flow, and child issue tree for llm-wikis + resource/document intelligence |
| 2096 | intelligence-accessibility-map | `docs/plans/2026-04-13-issue-2096-intelligence-accessibility-map.md` | 2026-04-13 | plan-approved | T2 | Bounded completion/validation plan for the existing intelligence accessibility map deliverable |
| 2104 | canonical-entry-points-for-ecosystem-intelligence | `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md` | 2026-04-11 | plan-review | T2 | Three-tier entry-point navigation for intelligence ecosystem; 1 new file + section additions to docs/README.md and 10+ existing files |
| 2216 | acma-codes-llm-wiki-repo-intelligence-integration | `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` | 2026-04-11 | plan-approved | T2 | Integrate /mnt/ace/acma-codes (OCIMF, API, CSA) into intelligence ecosystem; recommends 4-way follow-on split |
| 2229 | licensed-win-1-live-validation | `docs/plans/2026-04-13-issue-2229-licensed-win-1-live-validation.md` | 2026-04-13 | plan-approved | T2 | Canonical local plan for live Windows validation of NightlyReadiness and MemoryBridgeSync on `licensed-win-1` |
| 2136 | intelligence-accessibility-registry-with-machine-reachability | `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md` | 2026-04-11 | plan-review | T2 | Machine-readable meta-registry of intelligence assets with reachability, query commands, and freshness metadata |
| 2105 | freshness-cadences-and-staleness-signals | `docs/plans/2026-04-13-issue-2105-freshness-cadences-and-staleness-signals.md` | 2026-04-13 | plan-approved | T2 | Bounded plan to lock the canonical freshness/staleness artifact and implementation slice for weekly review consumption |
| 2208 | intelligence-retrieval-contract-for-github-issue-workflows | `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md` | 2026-04-11 | completed | T2 | Retrieval contract defining minimum intelligence sources per workflow stage and issue class, evidence placement, and measurable checks |
| 2225 | acma-codes-source-registration-and-initial-indexing | `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md` | 2026-04-11 | plan-review | T2 | Register /mnt/ace/acma-codes as mounted source, Phase A indexing, initial dedup assessment; follow-on #1 from #2216 |
| 2226 | ocimf-csa-ledger-provenance-backfill | `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md` | 2026-04-11 | plan-review | T2 | Backfill OCIMF/CSA ledger entries and provenance aliases from indexed acma-codes; 11 new entries + 2 updates; follow-on #2 from #2216 |
| 2239 | automate-weekly-hermes-cross-machine-parity-review | `docs/plans/2026-04-12-issue-2239-automate-weekly-hermes-cross-machine-parity-review.md` | 2026-04-12 | completed | T2 | Weekly parity automation plan: cron script, YAML task, dated artifact output, and follow-on issue guidance |
| 2240 | macos-hermes-parity-install-config-and-tool-alignment | `docs/plans/2026-04-12-issue-2240-macos-hermes-parity-install-config-and-tool-alignment.md` | 2026-04-12 | completed | T2 | macOS workstation parity plan: registry/readiness coverage, Hermes path resolution, and documented platform-specific drift |
| 2227 | ocimf-tandem-csa-z276-wiki-promotion | `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` | 2026-04-12 | plan-approved | T2 | Canonical bounded wiki-promotion plan for OCIMF Tandem Mooring, CSA Z276.1-20, CSA Z276.18, and a narrow provenance-grounded update to ocimf-meg4 |
| 2245 | acma-summary-classification-unblock | `docs/plans/2026-04-12-issue-2245-acma-summary-classification-unblock.md` | 2026-04-12 | plan-approved | T2 | Bounded summary/classification artifact preparation to unblock #2227 without broad ACMA processing |
| 2249 | index-level-other-bucket-bounded-context-packs | `docs/plans/2026-04-13-issue-2249-index-level-other-bucket-bounded-context-packs.md` | 2026-04-13 | adversarial-reviewed | T2 | Bounded triage plan to decompose the 44,705 index-level `other` records into context-recovery packs |
| 2250 | reconcile-stale-intelligence-summary-artifacts | `docs/plans/2026-04-13-issue-2250-reconcile-stale-intelligence-summary-artifacts.md` | 2026-04-13 | adversarial-reviewed | T2 | Control-plane drift remediation plan for stale convenience summaries versus canonical ledgers |

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
