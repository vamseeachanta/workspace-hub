# Claude Agent-Team Prompt: Execute #2205 — Operating Model

> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2205
> **Plan:** `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md`
> **Status:** plan-approved (label confirmed on GitHub)
> **Complexity:** T3
> **Date:** 2026-04-11

---

## Self-Contained Context

### What #2205 is

Define a **parent operating-model document** that establishes the single-source-of-truth pyramid, cross-machine information-flow rules, scope boundaries, and dependency order for llm-wikis, resource intelligence, document intelligence, and issue workflows.

This is an **architecture-only** deliverable. It does not implement registries, enforcement hooks, schemas, or retrieval mechanics — those belong to child issues.

### What already exists

| Artifact | Path | Role |
|---|---|---|
| llm-wiki assets | `knowledge/wikis/engineering/wiki/` | Active repo-tracked wiki pages |
| Weekly ecosystem review | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | Freshness/accessibility questions |
| Document-intelligence audit | `docs/assessments/document-intelligence-audit.md` | 7-phase pipeline, registry, ledger |
| Holistic resource intelligence | `docs/document-intelligence/holistic-resource-intelligence.md` | Multi-source architecture framing |
| Approved plan for #2205 | `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` | Full plan with decisions locked |
| Review — Claude | `scripts/review/results/2026-04-11-plan-2205-claude.md` | MAJOR (addressed in revisions) |
| Review — Codex | `scripts/review/results/2026-04-11-plan-2205-codex.md` | MINOR |
| Review — Gemini | `scripts/review/results/2026-04-11-plan-2205-gemini.md` | MINOR |

### Architectural decisions already locked in the plan

1. **Canonical document identity**: content-based `doc_key` (sha256 / content hash). Paths are aliases.
2. **Single-source-of-truth pyramid** (6 layers): Source documents > Registry/provenance > Durable knowledge > Entry-point > Execution-state > Transient session.
3. **Owner map**: each layer owns exactly one concern; must-not-own boundaries are explicit.
4. **Allowed flows**: source -> registry -> durable knowledge -> entry-point -> execution-state. Transient -> durable only via explicit promotion.
5. **Forbidden flows**: llm-wikis reparsing when registry evidence exists; GitHub issues acting as durable knowledge; transient artifacts becoming canonical without promotion; entry-points inventing provenance; path-only identity creating duplicates.
6. **Named exceptions**: audit/provenance lookbacks may read across layers; degraded/offline mode uses cached registry with availability marking.
7. **Degraded/offline fallback**: git-tracked metadata is minimal cross-machine truth; shared derived artifacts preferred when reachable; local caches are read-through only.
8. **Unified artifact registry**: required as architectural concept; concrete schema delegated to #2207 and #2136.

---

## Issue Tree — All Related and Child Issue Links

### Parent

| Issue | Title | Status |
|---|---|---|
| **#2205** | multi-machine llm-wiki + resource/document intelligence operating model | `plan-approved` |

### Input / upstream issues (consume, do not redefine)

| Issue | Title | Classification | Contribution |
|---|---|---|---|
| #2034 | engineering LLM wiki seed + incremental ingest pipeline | input / upstream producer | existing llm-wiki ingest/seed capability |
| #1563 | consolidated data/resource intelligence feature | input / upstream program | broader data/resource-intelligence umbrella |
| #1575 | holistic document/resource intelligence architecture | input / upstream architecture | multi-source resource-intelligence framing |

### Child issues (implementation scoped under #2205)

| Issue | Title | Status | Must not redefine |
|---|---|---|---|
| #2206 | conformance checks against approved pyramid | `plan-approved` | the pyramid itself |
| #2207 | standards/codes provenance + reuse contract | `plan-approved` | parent ownership model or workflow policy |
| #2208 | intelligence retrieval contract for issue workflows | OPEN (no plan yet) | provenance schema or pyramid ownership |
| #2209 | durable-vs-transient knowledge boundary policy | `plan-approved` | provenance schema or accessibility registry design |

### Downstream consumers

| Issue | Title | Classification | Contribution |
|---|---|---|---|
| #2089 | weekly ecosystem execution/intelligence review | downstream consumer | weekly verification/health checks against approved model |
| #2096 | intelligence accessibility map | child implementation | accessibility inventory/map |
| #2104 | canonical entry points for ecosystem intelligence | child implementation | canonical entry-point design |
| #2136 | intelligence accessibility registry with machine reachability | child implementation | machine-readable accessibility registry |

### Dependency order

```
#2205 (this issue — parent operating model)
  -> #2207 (provenance + reuse contract)
  -> #2209 (durable/transient boundary policy)
  -> #2096 (accessibility map)
  -> #2104 (canonical entry points)
  -> #2136 (accessibility registry)
  -> #2208 (workflow retrieval contract)
  -> #2206 (conformance checks)
  -> #2089 (weekly review consumption/verification)
```

---

## Agent-Team Roles (Single Claude Run)

This execution uses three sequential roles inside **one Claude session**. Do not spawn separate sessions.

### Role 1: Researcher

**Purpose:** Read all source material and verify that every locked decision from the plan has supporting evidence.

**Actions:**
1. Read the approved plan at `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md`
2. Read `docs/document-intelligence/holistic-resource-intelligence.md`
3. Read `docs/assessments/document-intelligence-audit.md`
4. Read `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
5. Read `knowledge/wikis/engineering/wiki/index.md`
6. Read `knowledge/wikis/engineering/wiki/entities/llm-wiki-tool.md`
7. Verify existence of: `data/document-index/registry.yaml`, `data/document-index/standards-transfer-ledger.yaml`, `config/workstations/registry.yaml`
8. Scan `scripts/data/document-index/` and `scripts/data/doc_intelligence/` and `scripts/knowledge/` for existing implementations
9. Check all three review artifacts in `scripts/review/results/2026-04-11-plan-2205-*.md`

**Exit gate:** Summarize findings in a scratchpad comment. Confirm no new gaps that would invalidate locked decisions. If a critical gap is found, STOP and report to user before writing.

### Role 2: Writer

**Purpose:** Create the parent operating-model document using locked decisions from the plan.

**Actions:**
1. Create `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
2. The document must be **normative, not just descriptive** and contain these sections:
   - **Purpose and scope** — what #2205 defines and what it delegates
   - **Single-source-of-truth pyramid** — all 6 layers, owner map, must-not-own boundaries
   - **Canonical document identity** — doc_key rule, path-as-alias semantics
   - **Allowed information flows** — directional flow rules between layers
   - **Forbidden information flows** — explicit anti-patterns
   - **Named exceptions** — audit lookbacks, degraded/offline behavior
   - **Cross-machine access model** — git metadata vs shared artifacts vs local cache
   - **Unified artifact registry (architectural requirement)** — concept only, schema delegated
   - **Issue tree and dependency order** — full table of inputs, children, consumers with guardrails
   - **Scope boundaries** — what each child may implement and must not redefine
   - **Discoverability** — cross-links to existing intelligence docs and issues
   - **Open questions** — true residuals only
3. Update `docs/plans/README.md` only if the #2205 row status needs changing

**Exit gate:** All acceptance criteria checkboxes from the plan must be satisfiable by the written document. Self-verify each criterion before proceeding to Role 3.

### Role 3: Reviewer

**Purpose:** Self-review the deliverable against the plan, adversarial findings, and acceptance criteria.

**Actions:**
1. Re-read the written operating-model document end-to-end
2. Check each success criterion (SC-1 through SC-10, listed below)
3. Verify no scope creep: the document must NOT contain registry schemas, enforcement hook implementations, retrieval-enforcement mechanics, or llm-wiki implementation details
4. Verify each layer in the pyramid has exactly one owner (no overlap, no gaps)
5. Verify allowed/forbidden flows are directional and non-circular
6. Verify child issues are classified correctly and guardrails are explicit
7. Verify cross-links to existing docs are present and paths resolve to real files
8. If any check fails: fix it in the document, then re-verify

**Review questions (from adversarial reviews):**
- Is the parent/child scope split clean?
- Is canonical identity explicit enough?
- Are owner map and flow rules enforceable?
- Are degraded/offline semantics clear?
- Is the unified artifact registry question resolved at the correct level?
- Is the issue tree classification clear enough to prevent duplication?

**Exit gate:** Assign final verdict: APPROVE / MINOR / MAJOR. Apply `status:plan-review` label ONLY if verdict is APPROVE or MINOR. If verdict is MAJOR, STOP — see Blocker Behavior below.

---

## Allowed Write Paths (Exhaustive)

Only these paths may be created or modified during execution:

| Action | Path | Reason |
|---|---|---|
| **Create** | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | Primary deliverable |
| **Update** | `docs/plans/README.md` | Update status row for #2205 if needed |
| **Update** | `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` | Add completion notes if needed |
| **Update** | `scripts/review/results/2026-04-11-plan-2205-*.md` | Refresh review artifacts if re-reviewed |
| **Update** | GitHub issue #2205 (comment only) | Post execution summary |

**Forbidden writes:**
- No changes to any file under `data/`, `config/`, `knowledge/`, `.claude/`, or `tests/`
- No changes to scripts under `scripts/data/`, `scripts/knowledge/`, `scripts/enforcement/`
- No creation of new GitHub issues (child issues #2206-#2209 already exist)
- No changes to any child issue labels or content
- No modifications to enforcement hooks or CI configuration
- No code (Python, shell, YAML schemas) — this is a documentation-only deliverable

---

## Hard Planning-Gate Constraints

1. **Plan must be approved before execution.** The `status:plan-approved` label must exist on #2205 before any writes. (Confirmed: label is present as of 2026-04-11.)
2. **Never self-approve.** The implementing agent must not apply `status:plan-approved` to any issue. Only the user may approve plans.
3. **No implementation beyond architecture.** #2205 produces a document, not code. If you find yourself writing Python, YAML schemas, or shell scripts, STOP — you have left scope.
4. **No child-issue scope absorption.** Do not implement anything that belongs to #2206, #2207, #2208, or #2209. Refer to the "Must not redefine" column in the issue tree.
5. **Respect dependency order.** Do not make decisions that belong to downstream issues. State architectural requirements and delegate specifics.
6. **Pre-commit enforcement.** `scripts/enforcement/require-plan-approval.sh --strict` will block commits without an approval marker. Verify `.planning/plan-approved/2205.md` exists before committing.
7. **Do not self-merge or push to main without user confirmation.** Commit locally; let the user decide when to push.

---

## Exact Success Criteria

Each criterion maps to a plan acceptance criterion. **All must be met.**

| # | Criterion | Verification method |
|---|---|---|
| SC-1 | Parent operating-model doc exists at `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | File exists on disk |
| SC-2 | Doc defines the single-source-of-truth pyramid and assigns one owner per layer | Section present; 6 layers listed; no ownership overlap between layers |
| SC-3 | Doc defines allowed information flow across layers, including named audit/provenance exceptions and multi-machine behavior | Allowed-flows section + exceptions section both present and non-empty |
| SC-4 | Doc defines canonical document identity expectations and degraded/offline fallback behavior | Identity section + fallback section both present with concrete rules |
| SC-5 | Doc explicitly states what stays in #2205 versus what is delegated to child issues | Scope-boundaries section present with per-child delegation table |
| SC-6 | Existing related issues (#2096, #2104, #2136, #2089, #2034, #1563, #1575) classified as inputs, child work, or downstream consumers | Issue-tree table present with all 7 issues and correct classification |
| SC-7 | New child issues (#2206-#2209) linked with explicit dependency order and rationale | Dependency-order section + guardrails table present |
| SC-8 | Doc justifies its canonical location and discoverability from existing intelligence docs/issues | Discoverability section present with cross-links to real files |
| SC-9 | Plan review artifacts exist under `scripts/review/results/` | Already satisfied (3 files exist); refresh if re-reviewed |
| SC-10 | No scope creep: doc contains no registry schemas, enforcement hooks, or implementation details | Manual review during Role 3; any violation = MAJOR |

---

## Exact Step-by-Step Execution Plan

```
PHASE A — RESEARCH (Role 1: Researcher)
────────────────────────────────────────
Step 1   Read approved plan for #2205
Step 2   Read all 6 source documents:
           - docs/document-intelligence/holistic-resource-intelligence.md
           - docs/assessments/document-intelligence-audit.md
           - docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md
           - knowledge/wikis/engineering/wiki/index.md
           - knowledge/wikis/engineering/wiki/entities/llm-wiki-tool.md
           - docs/plans/README.md
Step 3   Verify existence of registry/script paths:
           - data/document-index/registry.yaml
           - data/document-index/standards-transfer-ledger.yaml
           - config/workstations/registry.yaml
           - scripts/data/document-index/
           - scripts/data/doc_intelligence/
           - scripts/knowledge/
Step 4   Read 3 review artifacts:
           - scripts/review/results/2026-04-11-plan-2205-claude.md
           - scripts/review/results/2026-04-11-plan-2205-codex.md
           - scripts/review/results/2026-04-11-plan-2205-gemini.md
Step 5   Summarize findings; confirm no blocking gaps

         ┌─────────────────────────────────────────────────┐
         │ EXIT GATE: If critical gap found, STOP and      │
         │ report to user before any writes                │
         └─────────────────────────────────────────────────┘

PHASE B — WRITE (Role 2: Writer)
────────────────────────────────
Step 6   Create operating-model doc with all 12 required sections
Step 7   Self-verify all 10 success criteria (SC-1 through SC-10) against draft
Step 8   Update docs/plans/README.md status row if needed

         ┌─────────────────────────────────────────────────┐
         │ EXIT GATE: All SC-1 through SC-10 must be       │
         │ satisfiable by the written document             │
         └─────────────────────────────────────────────────┘

PHASE C — REVIEW (Role 3: Reviewer)
────────────────────────────────────
Step 9   Re-read operating-model doc end-to-end
Step 10  Check each success criterion as a checklist
Step 11  Check for scope creep (no schemas, no hooks, no code)
Step 12  Check pyramid ownership (no overlap, no gaps)
Step 13  Check flow directionality (no circular claims)
Step 14  Check cross-links resolve to real files
Step 15  Fix any failures found in steps 9-14, then re-verify
Step 16  Assign final verdict: APPROVE / MINOR / MAJOR

         ┌─────────────────────────────────────────────────┐
         │ EXIT GATE: See status:plan-review rule and      │
         │ blocker behavior below                          │
         └─────────────────────────────────────────────────┘

PHASE D — POST-EXECUTION
─────────────────────────
Step 17  Post summary comment on GitHub issue #2205 including:
           - final deliverable summary
           - pyramid / information-flow / identity decisions
           - issue tree and dependency order
           - review verdict summary
           - residual risks/open questions
           - parent artifact path + plan path + review paths
           - child issue links
           - explicit request for user review
Step 18  Commit with message referencing #2205
```

---

## Rule: When to Apply `status:plan-review`

### For the parent issue (#2205)

`#2205` already has `status:plan-approved`. Do NOT change this label. The execution goal is to **complete the approved plan**, not to re-enter plan-review.

### For child issues (#2206-#2209)

Apply `status:plan-review` to a child issue when **ALL** of these are true:
1. A complete plan exists in `docs/plans/` for that issue
2. Adversarial review has been completed (2+ providers, artifacts saved to `scripts/review/results/`)
3. All MAJOR findings have been addressed in revisions
4. The final self-review verdict is APPROVE or MINOR
5. The plan has been posted as a comment on the GitHub issue

**Never apply `status:plan-review` if:**
- Any MAJOR finding remains unresolved
- The plan has not been posted to the issue
- Adversarial review was not completed
- You are the implementing agent (never self-approve for implementation)

### For this execution run specifically

This run does NOT plan child issues. If child issues need planning, that is separate work. This run only executes the already-approved #2205 parent deliverable.

---

## Blocker Behavior: MAJOR Verdict at Final Review

If Role 3 (Reviewer) assigns a **MAJOR** verdict after completing steps 9-15:

1. **Do NOT commit the document.**
2. **Do NOT post a completion comment on GitHub.**
3. **Do NOT apply any status labels.**
4. Document the MAJOR findings in a comment at the bottom of the operating-model draft.
5. Report to the user with:
   - What was written
   - Which success criteria failed
   - What the MAJOR findings are
   - Recommended revisions
6. **STOP and wait for user guidance.**

The user will either:
- Approve proceeding despite MAJOR findings (explicit override)
- Request specific revisions
- Request a re-run of the full execution

**No autonomous recovery from MAJOR is permitted.**

---

## Commit Message Template

When all checks pass and the deliverable is ready:

```
feat(knowledge): add operating-model for llm-wiki + resource/doc intelligence (#2205)

Define single-source-of-truth pyramid, cross-machine information-flow
rules, scope boundaries, and dependency order for the intelligence
ecosystem. Architecture-only — implementation delegated to child
issues #2206-#2209.
```

---

## What This Prompt Does NOT Cover

- Implementation of any child issue (#2206, #2207, #2208, #2209)
- Registry schema design (belongs to #2207, #2136)
- Enforcement hooks or conformance scripts (belongs to #2206)
- Retrieval contract mechanics (belongs to #2208)
- Boundary policy details (belongs to #2209)
- Weekly review updates (belongs to #2089)
- Any code, YAML schemas, or script changes
