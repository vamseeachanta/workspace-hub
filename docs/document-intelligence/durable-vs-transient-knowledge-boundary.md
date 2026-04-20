# Durable vs Transient Knowledge Boundary

> **Issue:** [#2209](https://github.com/vamseeachanta/workspace-hub/issues/2209)
> **Parent:** [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) — LLM-Wiki + Resource/Document Intelligence Operating Model (amended 2026-04-19: Sections 2, 3, 8.1)
> **Sibling:** [#2207](https://github.com/vamseeachanta/workspace-hub/issues/2207) — Standards/Codes Provenance + Reuse Contract
> **Sibling:** [#2206](https://github.com/vamseeachanta/workspace-hub/issues/2206) — Pyramid Conformance Checks
> **Status:** Normative — approved boundary policy for durable vs transient knowledge (revised 2026-04-19 per parent amendments)
> **Date:** 2026-04-11 (revised 2026-04-19)
> **Scope:** Policy only. Implementation delegated to follow-on issues.

---

## 1. Purpose and Scope

### What this document defines

This is the **durable-vs-transient knowledge boundary policy** for the workspace-hub intelligence ecosystem. It establishes:

- Classification of major artifact classes onto the six-layer pyramid (L1–L6) defined by #2205
- Ownership statements for each artifact class: what it is for, what it is not for
- Allowed bridge and sync directions between durable and transient layers
- Promotion rules: when and how a transient artifact graduates to durable knowledge (L3)
- Retention and expiration guidance for transient artifacts
- Anti-patterns that blur the boundary
- Guardrails to prevent boundary drift
- Recommended follow-on implementation surfaces

This policy uses only the six layers declared in #2205 Section 2. It does not invent "between layers", "adjacent to a layer", or "hybrid layer" classifications — those are explicitly forbidden by #2205 Section 2 "Forbidden inventions."

### What this document does NOT define

| Out of scope | Owner |
|---|---|
| The parent pyramid model, layer ownership, or information flow rules | #2205 (parent operating model) |
| Provenance schema, `doc_key` definition, or reuse-vs-reparse rules | #2207 (provenance contract) |
| Conformance validation scripts or linters | #2206 |
| Retrieval contract for issue workflows | #2208 |
| Unified registry file format or query interface | #2136 |
| Wiki frontmatter required-set (authority lives in per-wiki `CLAUDE.md` per parent Section 8.1) | Per-wiki `knowledge/wikis/*/CLAUDE.md` |

This policy specializes the parent model for the durable/transient boundary. It does not redefine it.

---

## 2. Relationship to Parent Operating Model (#2205)

This document inherits from the [parent operating model](llm-wiki-resource-doc-intelligence-operating-model.md) and operates under its constraints. The parent was amended 2026-04-19 ([summary comment](https://github.com/vamseeachanta/workspace-hub/issues/2205#issuecomment-4277238819)) to resolve three patterns surfaced by the 2026-04-17 cross-provider review. This revision adopts those amendments.

| Parent rule | How this policy applies it |
|---|---|
| **Layer 3 — Durable knowledge** owns distilled reusable knowledge and conceptual synthesis | This policy defines what qualifies as "durable" and the criteria for admission to L3 |
| **Layer 5 — Execution state** owns scope, ownership, approval state, delivery tracking | This policy makes explicit that L5 artifacts are execution-bound with respect to domain knowledge — they track execution, not truth |
| **Layer 6 — Transient session** owns handoffs, research notes, working context | This policy defines retention, expiration, and promotion rules for L6 artifacts |
| **L6→L3 promotion flow** requires "explicit promotion decision" | This policy specifies the concrete criteria and process for that promotion |
| **L5→L3 promotion flow** for post-issue validated findings | This policy defines when issue-derived findings deserve promotion and when they should remain in execution state |
| **Ownership invariant**: every artifact belongs to exactly one layer | This policy classifies every artifact class into exactly one of L1–L6 |
| **Most-durable-owner rule**: assign to the lowest-numbered layer whose ownership covers the artifact's primary purpose | This policy applies this rule to classify borderline artifacts |
| **Section 2 worked examples** (added 2026-04-19) | Binding for the classifications in Section 4: recurring operational outputs are L5 individually with synthesized findings flowing to L3; normative architecture docs are L3; plans are L5; review artifacts are L5; session handoffs are L6 |
| **Forbidden inventions** (Section 2, added 2026-04-19) | This policy does not use "between L_n and L_m", "L_n-adjacent", or "hybrid layer" classifications anywhere |
| **Section 3 identity namespace** (amended 2026-04-19) | All `doc_key` references in this document use the `<algorithm>:<hex>` namespaced form |
| **Section 3 `merged_at` rename** (amended 2026-04-19) | Any provenance timestamp referenced in this document uses `merged_at`, not `discovered` |
| **Section 8.1 L3 Frontmatter Schema Authority** (added 2026-04-19) | Per-wiki `CLAUDE.md` is the binding authority for L3 frontmatter. This document declares *additional* fields on top of the parent baseline floor; it does not prescribe a stand-alone required-set |

### Conflict resolution

If this policy is found to conflict with the parent operating model, the parent takes precedence. Conflicts must be documented as comments on #2205 with a proposed amendment before any deviation.

---

## 3. Relationship to Sibling Contracts (#2207, #2206)

The [provenance/reuse contract](standards-codes-provenance-reuse-contract.md) defines identity (`doc_key`), provenance fields, and reuse-vs-reparse rules for standards/codes. The [conformance checks design](pyramid-conformance-checks.md) defines validation rules that assert compliance with the parent and child contracts. This boundary policy complements both without overlap:

| This policy (#2209) | Provenance contract (#2207) | Conformance checks (#2206) |
|---|---|---|
| Classifies artifact **roles** as durable vs transient | Defines artifact **identity** and provenance fields | Defines **validation rules** that detect violations |
| Governs which artifacts may persist and which must expire | Governs how to identify, trace, and reuse artifacts | Governs how to detect non-conformance automatically |
| Defines promotion criteria (when to move to durable) | Defines promotion path mechanics (how the pipeline moves artifacts) | Defines pass/fail signals for promotion traceability |
| Covers all artifact classes across all layers | Specializes for standards/codes at L1-L2-L3 | Specializes for rule enforcement across all layers |

**Non-overlap rule:** This policy does not define `doc_key` semantics, provenance field requirements, or reparse decision trees. Those belong to #2207. This policy does not define registry schemas or accessibility registries. Those belong to #2136. This policy does not define executable validation rules. Those belong to #2206.

**Frontmatter schema scope (2026-04-19 revision):** Neither #2209 nor #2207 nor #2206 independently declares the required frontmatter shape for L3 wiki pages. Per parent Section 8.1, the **per-wiki `CLAUDE.md` is the binding authority**. This policy specifies which *additional* fields durable pages promoted per the L6→L3 / L5→L3 flows should declare, on top of the parent baseline floor and subject to each wiki's `CLAUDE.md`.

---

## 4. Artifact Classes and Ownership Statements

Every artifact class below is assigned to exactly one of L1–L6 per #2205 Section 2. The parent's Section 2 "Worked examples for the most-durable-owner rule" is binding; this section applies those examples to workspace-hub's concrete artifact classes.

### 4.1 LLM-Wikis

**Layer:** L3 — Durable knowledge
**Location:** `knowledge/wikis/*/wiki/{concepts,entities,standards,workflows,sources}/`

**What wikis are for:**
- Distilled, reusable conceptual and technical knowledge
- Synthesized domain understanding that outlives any single issue or session
- Authoritative reference for agents and humans consulting the intelligence ecosystem

**What wikis are NOT for:**
- Live task tracking or execution state (use GitHub issues)
- Session-specific research notes or working context (use handoffs or `.planning/`)
- Raw provenance inventory or document indexing (use registries at L2)
- Opinions, speculations, or unverified claims without source traceability

**Durability:** Permanent. Wiki pages persist until superseded by a more accurate or complete page. Pages are updated, not deleted, unless the underlying domain concept is retired.

**Frontmatter:** Governed by the per-wiki `CLAUDE.md` (parent Section 8.1 authority), layered over the parent baseline floor of `title`, `last_updated`, `doc_key`. See Section 10.1 for durable-page additional fields this policy recommends.

**Examples from this repo:**
- `knowledge/wikis/engineering/wiki/concepts/mooring-line-failure-physics.md` — durable domain knowledge
- `knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md` — durable tool reference
- `knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md` — promoted L5→L3 findings

### 4.2 Normative Architecture and Policy Documents

**Layer:** L3 — Durable knowledge
**Location:** `docs/document-intelligence/*.md`, governance documents under `docs/`, control-plane contracts

**What these are for:**
- Durable knowledge *about how the system operates*
- Distilled design decisions for reuse across issues and sessions
- Authoritative contracts that downstream work implements

**What these are NOT for:**
- Execution-state tracking (plans, reviews live at L5)
- Transient session residue

**Durability:** Permanent once approved. Revisions happen in place (with version/amendment history) rather than as throwaway artifacts. The parent operating model itself, this boundary policy, #2207's provenance contract, and #2206's conformance design are all L3.

**Rationale (2026-04-19 revision):** Per parent Section 2 worked examples, normative architecture documents are L3 — they are durable knowledge about system operation. This supersedes the earlier classification of this document as "L3-adjacent" (a forbidden invention per parent Section 2).

**Examples from this repo:**
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — parent operating model (L3)
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` — this document (L3)
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` — #2207 contract (L3)
- `docs/document-intelligence/pyramid-conformance-checks.md` — #2206 design (L3)

### 4.3 GitHub Issues, Plans, and Review Artifacts

**Layer:** L5 — Execution state
**Location:** GitHub issues, `docs/plans/`, `scripts/review/results/`

**What execution-state artifacts are for:**
- Tracking scope, ownership, approval state, acceptance criteria, and delivery
- Recording the plan-review-implement-ship lifecycle for specific work items
- Providing evidence of review and compliance for governance gates

**What execution-state artifacts are NOT for:**
- Serving as the durable source of truth for domain knowledge — issues close and become stale
- Replacing wiki pages as the canonical reference for technical concepts
- Accumulating narrative synthesis that should live in L3

**Durability:** Execution-bound with respect to domain knowledge. Issues close. Plans are consumed during execution and become historical records. Review artifacts are evidence of a point-in-time assessment. (Terminology note: this document uses "execution-bound" for the L5 property and "transient" exclusively for the L6 layer name, per Finding F3 terminology fix.)

**Retention:** Retain indefinitely for audit trail and governance compliance, but do NOT treat as canonical knowledge sources after issue closure. Valuable findings must be promoted to L3 via explicit promotion.

**Examples from this repo:**
- `docs/plans/2026-04-11-issue-2205-*.md` — execution plan, L5 execution-bound
- `scripts/review/results/2026-04-11-issue-2207-claude-review.md` — review evidence, L5 execution-bound
- GitHub issue #2209 — L5 execution state (the resulting policy doc is L3 durable, the issue is not)

### 4.4 Plan Approval Markers

**Layer:** L5 — Execution state
**Location:** `.planning/plan-approved/NNN.md`

**What these are for:**
- Local audit evidence that a plan was approved for a given issue number
- Authority source for the planning-skill precedence order (`issue-planning-mode/SKILL.md:103, 115`)
- Witness for the skill's fresh-review rollback rule (`SKILL.md:210-227`) when a previously-approved issue is re-reviewed

**What these are NOT for:**
- Transient session scratch (their absence changes effective approval state)
- Durable domain knowledge

**Durability:** Permanent for closed issues. These markers are governance audit evidence, not session residue. The planning skill explicitly depends on their continued presence.

**Retention:** **Do not delete at issue closure.** Retain for the life of the repository as local approval evidence. They may be relocated into an archive subtree if the active directory grows unmanageable, but the contents must remain recoverable.

**Rationale (2026-04-19 revision, resolves F2):** The 2026-04-11 version of this policy classified these markers as L6 transient with retention "delete after issue closure." That broke the audit trail the planning skill depends on. Per parent Section 2 worked examples, plan documents are L5 (execution-state ownership); approval markers are governance-side metadata about execution state, so they are L5 as well. This fix preserves the planning workflow.

### 4.5 Recurring Operational Run Outputs

**Layer:** L5 — Execution state (each individual run)
**Promotion path:** Synthesized findings across runs flow to L3 via the standard L5→L3 promotion path.
**Location:** Weekly review outputs, nightly batch summaries, daily readiness reports

**What individual run outputs are for:**
- Point-in-time evidence of what happened in this period (an execution-state record of operations)
- Triggering follow-on issues when gaps are found
- Providing input to the synthesis work that produces L3 durable findings

**What individual run outputs are NOT for:**
- Serving as the durable source of truth for domain knowledge — each run is a snapshot
- Replacing wiki pages, registries, or governance docs
- Accumulating into an ever-growing canonical reference

**Durability:** Individual runs are execution-bound (L5). The process definitions themselves (weekly-review template, batch-run playbook) are L3 durable and live under `docs/modules/ai/` or similar. Findings that emerge *across runs* — patterns, trend signals, newly-confirmed domain knowledge — are promoted to L3 via the standard L5→L3 flow defined in Section 7.

**Retention:** Retain individual run outputs for 90 days or the most recent 12 runs (whichever is longer) for trend analysis. Older outputs may be archived or pruned. Significant findings must be promoted to L3 or captured as new issues at L5.

**Rationale (2026-04-19 revision, resolves F1):** The 2026-04-11 version classified weekly review artifacts as "Between L5 and L6 — Recurring operational evidence" with an associated "Recurring-operational artifact" glossary class. Per parent Section 2 "Forbidden inventions" (added 2026-04-19), "between layers" classifications are explicit violations of the ownership invariant. Per the parent's Section 2 worked examples, recurring operational outputs are L5 individually; synthesized findings flow to L3 via the existing promotion path. The "Recurring-operational artifact" class has been removed from this document entirely.

### 4.6 Registries, Ledgers, and Manifests

**Layer:** L2 — Registry/provenance
**Location:** `data/document-index/`, manifests, ledgers

**What registries are for:**
- Inventory of known documents: paths, `doc_key` values, extraction status, lineage
- Provenance tracking: where a document came from, when a provenance record was merged, what was extracted
- Machine-readable lookup for `doc_key`-based identity resolution (using the `<algorithm>:<hex>` form per parent Section 3)

**What registries are NOT for:**
- Narrative synthesis or conceptual knowledge (use wikis at L3)
- Execution tracking or task state (use issues at L5)
- Human-readable documentation or editorial content

**Durability:** Durable. Registry entries persist as long as the underlying source documents exist. Entries may be updated (status changes per parent Section 3 status vocabulary, new path aliases, `merged_at` stamps per parent Section 3) but are not deleted unless the source is retired.

**Examples from this repo:**
- `data/document-index/standards-transfer-ledger.yaml` — durable provenance ledger
- `data/document-index/registry.yaml` — durable aggregate statistics
- `data/document-index/mounted-source-registry.yaml` — durable source-root inventory

### 4.7 Session and Handoff Artifacts

**Layer:** L6 — Transient session
**Location:** `docs/handoffs/`, agent scratchpads

**What session artifacts are for:**
- Capturing working context for session continuity: what was done, what remains, what was discovered
- Providing input for the next session or the next agent in a multi-agent chain
- Recording temporary research, debugging notes, and draft analysis

**What session artifacts are NOT for:**
- Serving as canonical knowledge — session notes decay and are never authoritative
- Replacing wiki entries, registry records, or governance documents
- Persisting beyond their useful continuity window without explicit promotion

**Durability:** Transient by default (L6 per parent Section 2). Session artifacts are consumed by downstream sessions and then become stale. They must be promoted (L6→L3) or allowed to expire.

**Retention:** See Section 8.

### 4.8 `.planning/` Artifact Sub-Classes

**Layer distribution:** The `.planning/` tree contains heterogeneous artifact classes. Each is classified per the parent's Section 2 worked examples. This section replaces the earlier treatment of `.planning/` as a single L6 bucket (Codex finding C2).

| Sub-class | Location | Layer | Rationale | Retention |
|---|---|---|---|---|
| Plan approval markers | `.planning/plan-approved/NNN.md` | **L5** (execution state) | Governance audit evidence for plan-approved state; planning skill depends on their presence | Permanent for closed issues (see Section 4.4 and Section 8.1) |
| Paused-workflow handoffs | `.planning/HANDOFF.json` | **L6** (transient session) | Session-level working context; informal | Superseded by the next handoff; otherwise aligned with associated-issue lifecycle (see Section 8.1) |
| Quick review/prompt lane | `.planning/quick/` | **L6** | Short-lived session tooling output | 14 days after parent issue closure |
| Research synthesis drafts | `.planning/research/` | **L6** pending promotion | Synthesis candidates; promoted to L3 if findings meet Section 7 criteria, otherwise expire | 30 days or until promoted/discarded |
| Archive | `.planning/archive/` | Same layer as the archived content | Archive holds already-expired or completed artifacts; layer follows original classification | Archive-long (no further expiration unless space pressure) |
| Worker discoveries | `.planning/discoveries/*.jsonl` | **L6** pending pipeline processing | Raw discovery events awaiting the nightly learning pipeline | 14 days (consumed by pipeline) |
| Verification markers | `.planning/verified/NNN.md` | **L5** | Governance audit evidence for verified state | Permanent for closed issues (same treatment as plan-approved markers) |

If new `.planning/` sub-classes are introduced, they must be classified here before use, or they fall back to L6 (default transient) per the most-durable-owner rule only if their primary purpose is session context.

### 4.9 `.claude/state/` Artifacts

**Layer:** L6 — Transient session (committed subclasses) or local-only (untracked subclasses)
**Location:** `.claude/state/`

**Important scope note (Codex finding C3):** `.claude/state/` mixes committed artifacts with local-only untracked state. Classification depends on whether a subtree is committed:

| Subtree | Committed? | Layer | Rationale |
|---|---|---|---|
| `.claude/state/corrections/` | Committed | **L6** | Session correction logs checked into the repo |
| `.claude/state/session-governor/` | Committed | **L6** | Governor state files checked into the repo |
| `.claude/state/session-signals/*.jsonl` | **Not committed** (local-only telemetry) | Outside the committed-artifact taxonomy | These are local machine state, not repo artifacts. This policy does not classify untracked files |

**Retention:** See Section 8 for committed L6 subtrees. Local-only state (e.g., uncommitted `session-signals`) is governed by session-local cleanup, not this policy.

**Rationale (2026-04-19 revision):** The 2026-04-11 version cited `.claude/state/session-signals/2026-04-11.jsonl` as an in-repo example. The cited handoff (`docs/handoffs/session-2026-04-11-session-log-portability-exit.md:66-74`) explicitly flagged that file as uncommitted dirty state. The example has been removed from Section 4; the subtree is now marked as local-only.

---

## 5. Durable vs Transient Classification Rules

### 5.1 The classification test

To determine whether an artifact is durable or transient, apply this decision tree. Every outcome is one of L1–L6 per parent Section 2; no between-layer or adjacent-layer answers are permitted.

```
Does the artifact contain reusable domain knowledge that
outlives the issue/session that created it?
├── YES → Is it conceptual/technical synthesis?        → L3 (wiki)
│         Is it normative architecture or policy?      → L3 (docs/document-intelligence/)
│         Is it provenance/inventory data?             → L2 (registry)
│         Is it raw source content?                    → L1 (source document)
└── NO  → Is it tracking execution of a specific work item,
          or audit evidence of execution state?
          ├── YES → L5 (issue/plan/review/approval marker)
          └── NO  → Is it a single recurring operational run output?
                    ├── YES → L5 (individual run); findings may flow to L3 via Section 7
                    └── NO  → Is it capturing session context for continuity?
                              ├── YES → L6 (handoff/scratchpad/.planning L6 subclass)
                              └── NO  → Apply the most-durable-owner rule from #2205 Section 2;
                                         if still unresolvable, escalate per #2205 Section 10
                                         (do NOT invent a new layer)
```

### 5.2 Hard classification rules

These rules are binary. "Transient" below refers exclusively to the L6 layer name. L5 artifacts are described as "execution-bound" or "execution-state" to preserve the distinction flagged by Finding F3.

| Rule | Classification |
|---|---|
| An LLM-wiki page under `knowledge/wikis/` | L3 durable |
| A normative architecture or policy doc under `docs/document-intelligence/` | L3 durable |
| A registry/ledger entry under `data/document-index/` | L2 durable |
| A GitHub issue | L5 execution-state (execution-bound for domain knowledge) |
| A plan file under `docs/plans/` | L5 execution-state |
| A review result under `scripts/review/results/` | L5 execution-state |
| A plan approval marker under `.planning/plan-approved/` | L5 execution-state (governance audit evidence, permanent) |
| A verification marker under `.planning/verified/` | L5 execution-state (governance audit evidence, permanent) |
| A session handoff under `docs/handoffs/` | L6 transient |
| A session handoff under `.planning/HANDOFF.json` | L6 transient |
| A `.planning/quick/`, `.planning/research/`, or `.planning/discoveries/` artifact | L6 transient |
| A committed `.claude/state/` artifact (e.g., `corrections/`, `session-governor/`) | L6 transient |
| An uncommitted local-only `.claude/state/` artifact (e.g., `session-signals/*.jsonl`) | Outside this taxonomy (local-only) |
| A single recurring operational run output (weekly review, nightly batch summary, daily readiness report) | L5 execution-state; synthesized findings across runs promote to L3 |
| A governance/process definition doc (e.g., `SESSION-GOVERNANCE.md`, weekly review *template*) | L3 durable |

### 5.3 Borderline cases and resolution

All borderline resolutions must land on one of L1–L6. No "adjacent" or "between" answers.

| Artifact | Seems like | Actually is | Resolution |
|---|---|---|---|
| `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` | Durable analysis | L5 operational audit | It captured a point-in-time compliance state; findings should be promoted to L3 if they are reusable |
| `knowledge/wikis/.../sources/closed-engineering-issues.md` | Transient issue data | L3 (durable promoted knowledge) | The promotion has already happened; the wiki page is the durable artifact, not the original issues |
| `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | Execution output of #2205 | L3 (durable normative architecture) | Per parent Section 2 worked examples, normative architecture docs are L3 |
| A single weekly review output | Recurring evidence | L5 (execution-state record of that run) | Retain per Section 8; promote synthesized findings across runs to L3 per Section 7 |
| This document (`durable-vs-transient-knowledge-boundary.md`) | Execution output of #2209 | L3 (durable policy contract) | Per parent Section 2 worked examples, normative architecture docs are L3 |
| `.planning/plan-approved/NNN.md` | Transient workflow residue | L5 (governance audit evidence) | Planning skill depends on their presence as tier-2 authority; they are execution-state evidence, not session scratch |

---

## 6. Allowed Bridge and Sync Directions

### 6.1 Primary bridge directions

Bridges connect layers. Each bridge is directional. Only L1–L6 endpoints appear; no "recurring-operational" endpoint.

| From | To | Bridge type | Trigger |
|---|---|---|---|
| L1 Source documents | L2 Registry/provenance | **Indexing** | Document discovered → hashed → registered with `doc_key` (`<algorithm>:<hex>`) |
| L2 Registry/provenance | L3 Durable knowledge | **Structured promotion** | Registry outputs (summaries, extractions) promoted into wiki pages per #2207 pipeline |
| L6 Transient session | L3 Durable knowledge | **Promotion** | Explicit decision after review — worker discoveries, session findings meeting Section 7 criteria |
| L5 Execution state | L3 Durable knowledge | **Post-issue promotion** | Issue closure with validated findings worth preserving as domain knowledge |
| L5 Execution state (individual recurring run) | L3 Durable knowledge | **Cross-run synthesis promotion** | Patterns observed across multiple recurring runs (e.g., 3+ weekly reviews) meeting Section 7 criteria |
| L6 Transient session | L5 Execution state | **Issue creation** | Session discovers a bug, gap, or follow-on work item → `gh issue create` |
| L5 Execution state | L6 Transient session | **Context injection** | Session reads issue context, plan, and review history as working input |
| L3 Durable knowledge | L5 Execution state | **Evidence consumption** | Issue planning and execution reads wiki pages and registries as evidence |
| L5 Execution state (individual recurring run) | L5 Execution state (new issue) | **Finding escalation** | Recurring-run finding triggers a new issue when the gap is a work item, not a knowledge item |

### 6.2 Forbidden bridge directions

| From | To | Why forbidden |
|---|---|---|
| L5 Execution state | L3 Durable knowledge (without promotion) | Issues and plans must not silently become the knowledge source — they close and go stale |
| L6 Transient session | L3 Durable knowledge (without promotion) | Session notes must not become canonical — they decay by definition |
| L3 Durable knowledge | L6 Transient session (write-back) | Wikis must not be updated with session-local findings that haven't been reviewed |
| L3 Durable knowledge | L5 Execution state (ownership transfer) | Wiki pages must not become owned by an issue — the issue consumes the wiki, not the reverse |
| L5 Individual recurring run | L3 Durable knowledge (raw dump, no synthesis) | Single run outputs must not be pasted into wiki pages — only synthesized findings across runs get promoted |

### 6.3 Sync rules

| Rule | Description |
|---|---|
| **No silent promotion** | Every movement from L5/L6 to L3 requires an explicit, auditable decision — either a promotion comment on an issue, a committed wiki page with source traceability (including `doc_key` in the form `<algorithm>:<hex>` when the source is a registered document), or a promoted-artifact record in a registry |
| **No reverse demotion** | L3 durable artifacts do not become L5 or L6. If a wiki page is found to be wrong, it is corrected or archived — not moved to a handoff file |
| **No transient-to-transient canonicalization** | One session's handoff does not become the next session's source of truth for domain knowledge. It becomes working context only. The session must verify against L3/L2 before treating handoff claims as authoritative |
| **Read-through is always allowed** | Any layer may read from any lower or higher layer for context per #2205 Section 6 audit exception. Reading does not change ownership or durability |

---

## 7. Promotion Rules from Transient/Execution-State to Durable

### 7.1 Promotion criteria

A non-durable artifact (L5 or L6) deserves promotion to durable knowledge (L3) when the following signals are met. Four criteria are hard gates; the fifth (stability) is a soft signal.

| Criterion | Test | Gate type |
|---|---|---|
| **Reusability** | The finding is useful beyond the issue/session that produced it — future agents or humans will need this information | Hard |
| **Verification** | The finding has been validated — it is not a speculative hypothesis or untested claim | Hard |
| **Non-redundancy** | No existing wiki page already contains this knowledge (or the existing page needs updating with new evidence) | Hard |
| **Source traceability** | The finding can be traced to a specific source: a `doc_key` (`<algorithm>:<hex>`), a closed issue, a validated experiment, or a cited external reference | Hard |
| **Stability** | The finding is not expected to change imminently — it represents settled understanding | **Soft signal** |

**Stability as a soft signal (2026-04-19 revision, resolves F5):** Stability is not a hard gate. Unstable-but-otherwise-promotable findings should be promoted with an `under-revision` tag (in the wiki frontmatter, subject to the wiki's `CLAUDE.md` schema) rather than blocked. This addresses the slow-wiki failure mode observed for the engineering wiki (121-line index vs. marine-engineering's 21,605; see #2034). Conservative under-promotion is a real failure mode; tagging is cheaper than blocking.

### 7.2 Promotion process

1. **Identify the candidate.** During issue closure, session wrap-up, or post-hoc synthesis of recurring run outputs, flag findings that meet the four hard criteria (stability is a soft signal).
2. **Choose the target.** Determine whether the finding belongs in:
   - An existing wiki page (update) — if the concept/entity already has a page
   - A new wiki page (create) — if no page covers this domain area
   - A registry entry (update) — if the finding is provenance/inventory data (#2207 pipeline)
3. **Write the promoted content.** Create or update the target artifact with proper source traceability. The per-wiki `CLAUDE.md` is the binding schema authority; frontmatter must satisfy both the parent baseline floor (Section 8.1) and any additional fields that wiki requires. See Section 10.1 for the additional fields this policy recommends for durable promoted pages.
4. **Record the promotion.** See Section 7.4 for the auditable record requirement.
5. **Do not modify the source.** The non-durable artifact (handoff, issue comment, discovery JSONL, recurring-run output) remains as-is for audit trail. It is not deleted or edited to match the promoted version.

### 7.3 Promotion anti-patterns

| Anti-pattern | Why it is wrong | Correct approach |
|---|---|---|
| Copy-pasting a handoff section directly into a wiki page | Handoff content is session-local, informal, and often unverified | Extract the verified finding, synthesize it, add source traceability |
| Creating a wiki page from a single unreviewed session | Single-session findings may be wrong or incomplete | Wait for verification through issue closure, cross-review, or repeated recurring-run findings |
| Promoting execution-state language into domain knowledge | "We decided to use approach X for issue #1234" is execution state, not domain knowledge | Promote the *what* and *why* of the approach, not the decision narrative |
| Mass-promoting individual recurring-run findings without synthesis | Individual run outputs are snapshots, not knowledge | Synthesize recurring findings across multiple runs into a single wiki entry with trend evidence |

### 7.4 Auditable promotion trail (revised 2026-04-19, resolves C5)

The 2026-04-11 version asserted that promotions were self-evidencing via wiki frontmatter and the wiki `log.md`. The 2026-04-17 Codex review found that `knowledge/wikis/engineering/wiki/log.md` records bulk ingest events and page counts, not page-level `promoted_from` lineage. The earlier claim is not enforceable today.

**Revised requirement:** An auditor must be able to answer "which non-durable artifact promoted this page?" from committed repo surfaces without reading unrelated issue comments. This requires one of the following to be present on the promoted page:

1. A `promoted_from` field in the wiki frontmatter, linking to the source artifact (issue number, handoff path, recurring-run output, or `doc_key`). The per-wiki `CLAUDE.md` governs whether this field is required; this policy recommends it as an *additional* required field for pages produced by the L6→L3 and L5→L3 flows (see Section 10.1).
2. A page-level entry in the wiki's `log.md` with enough identity to resolve the source artifact (not only bulk ingest batches).
3. A registry entry in #2207's provenance registry that records `promoted_from` at the `doc_key` level.

Until at least one of these mechanisms is operational on every promoted page, the "no silent promotion" guardrail (Section 6.3) is declared *partially enforceable* — the intent stands, but the auditable trail is not complete. Closing this gap is an implementation surface (Section 10.3).

---

## 8. Retention and Expiration Guidance for Transient and Execution-State Artifacts

### 8.1 Retention schedule

**Status (2026-04-19 revision, resolves F4):** The day-counts below are **advisory pending #2237 transient-artifact cleanup workflow** (the cleanup automation does not exist yet). Until that workflow ships, no conformance check should enforce these counts as hard failures. They represent the intended retention policy once automation is in place.

| Artifact class | Default retention | After retention | Notes |
|---|---|---|---|
| Session handoffs (`docs/handoffs/`) | Tied to associated issue lifecycle: retain until the associated issue has been closed for 30 days (fall-back: 90 days if no issue reference) | Archive or delete | Revised per F6: flat 30-day rule was too short when issues outlive 30 days |
| Paused-workflow handoff (`.planning/HANDOFF.json`) | Until superseded by next handoff, or associated issue closed + 14 days | Archive or delete | |
| `.planning/quick/` | Associated issue lifetime + 14 days | Archive or delete | |
| `.planning/research/` | 30 days or until promoted/discarded | Archive or delete | |
| Discovery JSONL (`.planning/discoveries/`) | 14 days (consumed by nightly learning pipeline) | Delete after pipeline processing | |
| Committed `.claude/state/` (corrections, session-governor) | 7 days | Delete | |
| Review results (`scripts/review/results/`) | 90 days | Archive | |
| Plan files (`docs/plans/`) | Issue lifetime + 30 days | Archive | |
| Individual recurring-run outputs (weekly reviews, nightly batches, daily readiness) | 90 days or 12 most recent runs (whichever is longer) | Archive older runs | |
| Plan approval markers (`.planning/plan-approved/`) | **Permanent for closed issues** | Do not delete — archive subtree if directory becomes unmanageable | Revised per F2: earlier "delete after issue closure" rule broke planning-skill audit trail |
| Verification markers (`.planning/verified/`) | **Permanent for closed issues** | Do not delete — archive subtree if directory becomes unmanageable | Governance audit evidence, same treatment as plan-approved markers |

### 8.2 Archive vs delete

- **Archive** means move to a dated archive directory (e.g., `.planning/archive/`) or compress into a bundle. Archived artifacts are not discoverable by default but can be recovered for audit purposes.
- **Delete** means remove from the repository. Deleted artifacts are recoverable via git history but are not present in the working tree.

### 8.3 Expiration signals

An artifact should be considered expired (and eligible for cleanup) when:

| Signal | Applies to |
|---|---|
| Associated issue is closed for > 30 days | Plans, review results, `.planning/quick/`, `.planning/HANDOFF.json`, handoffs with issue references |
| Handoff has been superseded by a newer handoff for the same work stream | Session handoffs |
| Discovery JSONL has been processed by the nightly learning pipeline | Discovery files |
| Recurring-run output has been superseded by 12+ newer runs and no finding has been promoted from it | Weekly review / nightly batch / daily readiness outputs |
| Committed `.claude/state/` file is > 7 days old | Committed `.claude/state/` subtrees |
| Research draft has passed 30 days without promotion | `.planning/research/` |

### 8.4 Metadata dependency (Codex finding C4)

Several expiration signals above reference "associated issue" linkage. Live handoffs at `docs/handoffs/*.md` currently carry only title/date/repo metadata (spot-checked 2026-04-17) and do not encode an associated issue reference. Until handoff templates are migrated to include an issue reference (proposed in Section 10.1), the "associated issue is closed for > 30 days" signal is **not computable** for handoffs that lack the reference. For those handoffs, use a date-based fall-back (e.g., 90 days from handoff date).

---

## 9. Anti-Patterns and Guardrails

### 9.1 Anti-patterns

| # | Anti-pattern | Description | Why it is harmful | Example |
|---|---|---|---|---|
| AP-1 | **Issue as knowledge base** | Using GitHub issues (open or closed) as the canonical reference for domain knowledge | Issues close, context decays, search is unreliable for structured knowledge retrieval. Future agents will not find it. | Citing "see issue #1234 comment #7" instead of creating a wiki page |
| AP-2 | **Handoff as source of truth** | Treating a session handoff as the authoritative reference for a technical decision | Handoffs are informal, session-scoped, and unreviewed. They capture what one agent believed at exit time. | A new session reading `docs/handoffs/session-*.md` and treating its claims as verified domain knowledge without checking L3 |
| AP-3 | **Registry as narrative** | Writing explanatory text, synthesis, or editorial commentary into registry/ledger entries | Registries own inventory and provenance (L2). Narrative synthesis belongs in wikis (L3). | Adding "this standard is important for deepwater pipeline design" to a `standards-transfer-ledger.yaml` entry |
| AP-4 | **Wiki as task tracker** | Using wiki pages to track in-progress work, open questions about implementation, or who-is-doing-what | Wikis own durable knowledge (L3). Execution tracking belongs in issues (L5). | A wiki page containing "TODO: need to add section on fatigue" or "Assigned to terminal 3 for overnight batch" |
| AP-5 | **Silent promotion** | Moving content from L5/L6 to L3 without an explicit, auditable promotion step | Breaks traceability. Makes it impossible to verify when and why knowledge entered the durable layer. | Editing a wiki page during a session without recording the source of the new information in frontmatter or the wiki log |
| AP-6 | **Transient canonicalization** | One session's handoff becoming the next session's accepted truth without verification | Creates a chain of unverified claims. Errors in one session propagate indefinitely. | Session B reading Session A's handoff claim "the API changed in v2.3" and writing code based on it without checking the actual API |
| AP-7 | **Recurring-run output accumulation** | Retaining every individual recurring-run output indefinitely as if each one were durable knowledge | Creates unbounded growth of operational snapshots that nobody reads. Obscures the actual durable findings. | 52 weekly review files in a directory with no synthesis, no pruning, and no promotion of recurring findings |
| AP-8 | **Plan as specification** | Treating an execution plan as the living specification after the issue is closed | Plans directed a specific implementation. Once closed, the *code and tests* are the specification, not the plan. | Referencing `docs/plans/2026-04-11-issue-*.md` as the authoritative behavior spec months after the issue closed |
| AP-9 | **Layer invention** | Classifying an artifact as "between L_n and L_m", "L_n-adjacent", or "hybrid" | Forbidden by parent #2205 Section 2 ("Forbidden inventions"). Breaks the ownership invariant. | Classifying recurring-run outputs as "between L5 and L6" rather than L5 with L5→L3 synthesis |
| AP-10 | **Deleting governance audit evidence** | Treating `.planning/plan-approved/` or `.planning/verified/` markers as session scratch and deleting them at issue closure | Breaks the planning-skill fresh-review rollback rule; loses canonical local witness for post-mortem audits | Running a cleanup script that removes `.planning/plan-approved/NNN.md` when issue NNN closes |

### 9.2 Guardrails

| # | Guardrail | Enforcement level | Description |
|---|---|---|---|
| GR-1 | **Wiki pages must have source traceability** | Policy (enforceable via conformance check, subject to the wiki's `CLAUDE.md`) | Every wiki page must satisfy its wiki's frontmatter authority (`knowledge/wikis/*/CLAUDE.md`), which must layer over the parent baseline floor (`title`, `last_updated`, `doc_key`) per #2205 Section 8.1. Source-traceability fields (`sources`, `source_ref`, or equivalent) are specified by the wiki's CLAUDE.md. |
| GR-2 | **Issues must not be cited as domain knowledge after closure** | Policy (enforceable via linter) | References to closed issues should point to the promoted wiki page, not the issue itself |
| GR-3 | **Handoffs must be consumed, not canonicalized** | Convention (enforceable via session-start skill) | The session-start routine should treat handoff content as unverified context, not accepted truth |
| GR-4 | **Promotion requires explicit auditable record** | Policy (enforceable via wiki ingest pipeline and #2207 provenance registry) | Any wiki page update from a promotion must record at least one of: frontmatter `promoted_from` linking to source, page-level `log.md` entry with source identity, or provenance-registry entry at `doc_key` level (see Section 7.4). |
| GR-5 | **Non-durable artifacts should include expiration-enabling metadata** | Convention (future enforcement via cleanup script) | Handoffs, `.planning/` files, and recurring-run outputs should include a date or issue reference. Until templates are migrated (Section 10.1), date-based fall-backs apply per Section 8.4. |
| GR-6 | **Recurring-run findings must be synthesized-and-promoted or dropped within 30 days** | Convention | Findings that recur across 3+ individual runs must be synthesized and promoted to a wiki page or escalated to an L5 issue; one-time findings expire with the run output. |
| GR-7 | **Governance audit evidence must not be deleted** | Policy (planning-skill authority) | `.planning/plan-approved/NNN.md` and `.planning/verified/NNN.md` are L5 governance audit evidence; they must persist for the life of the repository for closed issues. |
| GR-8 | **No invented layers** | Policy (enforceable via parent conformance check GUARD-1 per #2205 Section 2) | No classification may use "between L_n and L_m", "L_n-adjacent", or "hybrid layer" terminology. All artifacts must resolve to L1–L6. |

---

## 10. Likely Implementation Surfaces

This section identifies where future work is needed to enforce the boundary policy. No code changes are defined here — only targets.

### 10.1 Templates and conventions

**Scope note on frontmatter (2026-04-19 revision, resolves C1 and Addendum A):** This policy does NOT prescribe a free-standing required-set for wiki frontmatter. Per parent Section 8.1, the binding authority is the per-wiki `CLAUDE.md` (e.g., `knowledge/wikis/engineering/CLAUDE.md`). This policy declares **additional fields** that durable pages produced by the L6→L3 and L5→L3 promotion flows should carry, on top of the parent baseline floor.

**Parent baseline floor (binding, from #2205 Section 8.1):** `title`, `last_updated`, `doc_key` (in `<algorithm>:<hex>` form). Every wiki's `CLAUDE.md` must declare these as required.

**Additional fields this policy recommends for durable promoted pages** (layered over the baseline; final binding lives in each wiki's `CLAUDE.md`):

| Field | Type | Purpose | Scope |
|---|---|---|---|
| `promoted_from` | string (issue reference, handoff path, run-output reference, or `doc_key`) | Audit-trail link from L3 back to the L5/L6 source that was promoted (see Section 7.4) | Recommended required for pages produced by L6→L3 or L5→L3 promotion |
| `sources` | list of source identifiers | Editorial source-traceability (non-identity) | As defined by the wiki's `CLAUDE.md` |
| `tags` | list of strings | Classification for discovery | As defined by the wiki's `CLAUDE.md` |
| `added` | ISO date | When the page was first created | As defined by the wiki's `CLAUDE.md` |
| `under-revision` | boolean (optional) | Marks an unstable-but-promoted finding per Section 7.1 soft-signal rule | Optional, per Section 7.1 |

Children may not override or weaken the parent baseline floor. Where a wiki's `CLAUDE.md` requires fields this policy does not list, those wiki-specific fields take precedence.

**Scope of this policy's frontmatter recommendations:** The engineering wiki (`knowledge/wikis/engineering/`) is the primary target for the L6→L3 and L5→L3 promotion flows defined in Section 7 and is the surface for which these recommendations are most concretely grounded. Domain wikis (`maritime-law`, `naval-architecture`, `marine-engineering`) have their own `CLAUDE.md` schemas and may adopt or decline these recommendations on a per-wiki basis. The parent baseline floor binds universally; this policy's additional fields are recommendations.

**Templates:**

| Surface | Current state | Recommended change |
|---|---|---|
| Session handoff template | No formal template; live handoffs (spot-checked at `docs/handoffs/session-2026-04-11-*.md:1-4`) carry only title/date/repo | Add `## Expiration` section with issue reference and expected lifetime — required to make Section 8.3 expiration signals computable for handoffs (Codex finding C4) |
| Plan file template (`docs/plans/_template-issue-plan.md`) | No expiration metadata | Add `## Retention` section noting the plan expires with the issue |
| `.planning/discoveries/` JSONL schema | Structured per worker-discovery-protocol skill | No change needed; existing schema supports promotion routing |
| Wiki `CLAUDE.md` files (per-wiki authority) | Engineering wiki's `CLAUDE.md` declares `title, tags, added, last_updated` required; `sources` recommended | Each wiki `CLAUDE.md` must be updated to add `doc_key` as a required field (parent Section 8.1 baseline floor). This update is coordinated across #2207, #2209, #2206 revisions; the wiki `CLAUDE.md` update itself is out of this policy's write scope |

### 10.2 Skills and workflows

| Surface | Current state | Recommended change |
|---|---|---|
| `session-start-routine` skill | Loads context from handoffs and `.planning/` | Add guidance: "Treat handoff claims as unverified working context; verify domain claims against L3 wikis before acting on them" |
| `issue-planning-mode` skill | Full 5-step planning workflow; treats `.planning/plan-approved/` as tier-2 authority | Add post-closure step: "Identify findings worth promoting to L3 and route via promotion process". Do NOT add deletion of approval markers at closure (Section 4.4, GR-7) |
| `worker-discovery-protocol` skill | Defines discovery capture and orchestrator triage | Already supports promotion routing by category; no change needed |
| `comprehensive-learning-wrapper` skill | Nightly learning pipeline | Add promotion step: discoveries that meet all 4 hard promotion criteria (stability is soft signal) → wiki page creation or update with `promoted_from` field |
| Weekly review process (`#2089`) | Template exists; no automated output cleanup | Add retention enforcement: archive individual-run outputs older than 90 days or 12 runs; classify outputs as L5, with L5→L3 synthesis promotion path for cross-run findings |

### 10.3 Automated enforcement (future)

| Surface | Enforcement type | Effort |
|---|---|---|
| Wiki frontmatter validator (baseline floor) | Conformance check (#2206 FRONT-1) — reject wiki pages missing `title`, `last_updated`, or `doc_key` (parent Section 8.1) | Small |
| Transient artifact cleanup script | Cron job — archive/delete expired handoffs, `.planning/` L6 subclasses, committed `.claude/state/` per Section 8.1 | Medium |
| Closed-issue citation linter | Pre-commit check — warn when code or docs cite closed issues instead of wiki pages | Medium |
| Recurring-run output pruner | Scheduled job — archive run outputs beyond retention window per Section 8.1 | Small |
| Promotion audit trail checker | Conformance check — verify that promoted wiki pages have at least one of: `promoted_from` frontmatter field, page-level `log.md` entry, or registry `promoted_from` (Section 7.4) | Medium |
| Invented-layer detector | Conformance check (#2206 GUARD-1 per parent Section 2) — reject any document using "between L_n and L_m", "L_n-adjacent", or "hybrid layer" terminology | Small |
| Governance-marker protection | Pre-commit/cleanup-script guard — reject deletion of `.planning/plan-approved/` and `.planning/verified/` for closed issues | Small |

---

## 11. Open Questions and Residual Risks

1. **Retention enforcement timing.** This policy defines retention periods but does not implement the cleanup automation. Until a transient-artifact cleanup script exists, retention is **advisory** (Section 8.1). Risk: transient artifacts accumulate indefinitely, blurring the boundary by sheer volume. Mitigation: #2206 should not enforce the day-counts as hard failures until the cleanup workflow exists (follow-on #2237 proposed).

2. **Promotion judgment calls.** The four hard promotion criteria (Section 7.1) require human or orchestrator judgment. There is no fully automated test for "reusability" or "non-redundancy". Risk: under-promotion (valuable findings left to rot in handoffs) or over-promotion (premature findings polluting wikis). Mitigation: stability is now a soft signal (Section 7.1) to reduce conservative under-promotion; `under-revision` tag allows unstable-but-promoted findings.

3. **Recurring-run output format.** The weekly review process (#2089) has not yet standardized its output format (#2139). Nightly batch summaries and daily readiness reports also vary. Until the formats are stable, retention and promotion rules for these outputs are difficult to enforce mechanically.

4. **Handoff template adoption.** Adding expiration metadata to handoffs requires updating the session-exit workflow across all agents (Claude, Codex, Gemini). Risk: inconsistent adoption leading to some handoffs having expiration data and others not. Mitigation: Section 8.4 defines a date-based fall-back for handoffs that lack issue references until templates migrate.

5. **Cross-repo boundary.** This policy covers `workspace-hub` only. Satellite repos (e.g., `digitalmodel`) have their own knowledge artifacts. The boundary policy should eventually extend to cover promoted artifacts that cross repo boundaries, but this is out of scope for #2209.

6. **Promotion audit trail completeness.** The "no silent promotion" guardrail is declared *partially enforceable* until at least one of the three mechanisms in Section 7.4 is operational on every promoted page. This is tracked as an implementation surface (Section 10.3, "Promotion audit trail checker").

7. **Four-authority frontmatter reconciliation.** Parent Section 8.1 establishes the per-wiki `CLAUDE.md` as the binding authority and mandates a three-field baseline floor (`title`, `last_updated`, `doc_key`). Live wikis and earlier child contracts disagreed on required shapes. Each wiki's `CLAUDE.md` must be updated to declare `doc_key` as required; that update lives outside this policy's write scope and is coordinated across the three child-revision passes.

---

## 12. Recommended Follow-On Implementation Sequence

Based on the implementation surfaces identified in Section 10 and the dependency order from the parent operating model:

| Order | Work item | Scope | Depends on |
|---|---|---|---|
| 1 | Update each wiki `CLAUDE.md` to require `doc_key` per parent Section 8.1 baseline floor | Small — edit per-wiki CLAUDE.md files | Parent amendment (already landed 2026-04-19) |
| 2 | Update `session-start-routine` skill with handoff-verification guidance | Small — edit one skill file | Nothing |
| 3 | Add `## Retention` section to plan file template | Small — edit template | Nothing |
| 4 | Add `## Expiration` section to handoff template with issue reference | Small — edit template | Nothing (unblocks Section 8.3 signals for new handoffs) |
| 5 | Add post-closure promotion step to `issue-planning-mode` skill | Small — edit one skill file | #1 (wiki schemas updated); do NOT add approval-marker deletion |
| 6 | Build transient-artifact cleanup script (honors GR-7 governance-marker protection) | Medium — cron job for handoff/`.planning/` L6 expiration | #3, #4 (retention metadata in templates) |
| 7 | Add wiki frontmatter validator (FRONT-1) to conformance checks (#2206) | Medium — linter enforcing parent baseline floor | #1 |
| 8 | Add closed-issue citation linter | Medium — pre-commit warning for stale issue references | Nothing |
| 9 | Add recurring-run output pruner | Small — scheduled cleanup of old run outputs | Recurring-run output format stabilization (#2139 and siblings) |
| 10 | Add promotion audit trail checker to conformance checks (#2206) | Medium — linter enforcing Section 7.4 requirement | #1, #7 |
| 11 | Add invented-layer detector (GUARD-1) to conformance checks (#2206) | Small — linter rejecting forbidden layer terminology | Nothing (parent Section 2 already normative) |

These items should be captured as implementation issues under #2209 or as sub-tasks of #2206 (conformance checks), depending on whether they primarily affect boundary policy or validation tooling.

---

## 13. Revision History

### 2026-04-19 — Amendment-driven revision (this pass)

Triggered by: 2026-04-17 cross-provider adversarial review (13 findings across Claude and Codex) and 2026-04-19 parent operating-model amendments resolving Patterns 1/2/3 (parent Section 2 worked examples, Section 3 identity/status/`merged_at`, new Section 8.1 frontmatter authority).

**Amendments applied:**

| Amendment | Summary |
|---|---|
| A | Removed "Between L5 and L6" classification and the "Recurring-operational artifact" glossary class. Recurring-run outputs are now L5 individually; synthesized findings flow to L3 via the standard L5→L3 promotion path (parent Section 2 worked examples). Also removed "L3-adjacent" classification of this document and sibling normative docs — they are L3 per parent Section 2. |
| B | Reframed Section 10.1 frontmatter prescription as *additional fields on top of the parent baseline floor* (`title`, `last_updated`, `doc_key`). Per-wiki `CLAUDE.md` is the binding authority (parent Section 8.1). |
| C | `doc_key` references now use the `<algorithm>:<hex>` namespaced form (parent Section 3 identity namespace). |
| D | Adopted `merged_at` terminology where provenance timestamps are referenced (parent Section 3). |
| E | Cross-references updated to point to amended parent sections and the parent amendment summary comment. |

**Findings addressed (13 total from 2026-04-17 review):**

| Finding | Severity | Disposition |
|---|---|---|
| Claude F1 | MAJOR | **Fixed** via Amendment A (Section 4.5 reclassified; glossary class removed) |
| Claude F2 | MAJOR | **Fixed** (Section 4.4 reclassifies plan-approval markers as L5 permanent; GR-7 added) |
| Claude F3 | MINOR | **Fixed** (Section 4.3 and 5.2 reserve "transient" for L6; use "execution-bound" for L5 knowledge property) |
| Claude F4 | MINOR | **Fixed** (Section 8.1 marked advisory pending #2237 cleanup workflow) |
| Claude F5 | MINOR | **Fixed** (Section 7.1 demotes stability to soft signal; `under-revision` tag for unstable-but-promoted findings) |
| Claude F6 | MINOR | **Fixed** (Section 8.1 handoff retention tied to associated-issue lifecycle; Section 8.4 date-based fall-back until templates migrate) |
| Claude F7 | MAJOR (process) | **Resolved** — 2026-04-17 Codex cross-provider review landed; gate satisfied |
| Codex C1 | MAJOR | **Fixed** via Amendment B (frontmatter reframed as additional fields on baseline floor; non-overlap with #2207 restored) |
| Codex C2 | MAJOR | **Fixed** (Section 4.8 splits `.planning/` into plan-approved, HANDOFF.json, quick, research, archive, discoveries, verified — each with its own layer and retention) |
| Codex C3 | MAJOR | **Fixed** (Section 4.9 removes uncommitted `session-signals` example; clarifies committed vs local-only subtrees) |
| Codex C4 | MAJOR | **Fixed** (Section 8.4 declares associated-issue signal non-computable for handoffs that lack issue references; date-based fall-back specified) |
| Codex C5 | MINOR | **Fixed** (Section 7.4 defines three concrete auditable-trail mechanisms; "no silent promotion" declared partially enforceable until at least one is operational) |
| Claude Addendum A | MAJOR (cross-cutting) | **Fixed** via Amendment B (parent Section 8.1 establishes wiki `CLAUDE.md` as binding authority; this policy no longer prescribes a stand-alone required-set) |

### 2026-04-11 — Initial approval

Original boundary policy produced for #2209 plan-approved 2026-04-11. Classified weekly-review artifacts as "Between L5 and L6" (subsequently found to be a forbidden invention); classified `.planning/plan-approved/` markers as L6 transient with issue-lifetime retention (subsequently found to break planning-skill audit trail); prescribed a stand-alone wiki frontmatter required-set (subsequently found to conflict with #2207, #2206, and the engineering wiki's own `CLAUDE.md` authority). All three defects were corrected in the 2026-04-19 revision.

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| **Durable artifact** | An artifact that persists as canonical knowledge or infrastructure — its value does not decay with time unless the underlying domain changes. Lives at L1, L2, or L3 per parent Section 2. |
| **Transient artifact** | An artifact at L6 (session/handoff/scratchpad) — it serves a temporary purpose and must be promoted or allowed to expire. Reserved exclusively for the L6 layer name in this document. |
| **Execution-bound artifact** | An L5 artifact (issue, plan, review, approval marker) that tracks execution state and is not canonical for domain knowledge. Distinct from "transient" (L6). |
| **Recurring-run output** | An individual output of a recurring operation (weekly review run, nightly batch run, daily readiness run). Classified as L5 per parent Section 2 worked examples. **This is not a layer class**; it is a description of the artifact's cadence. Synthesized findings across multiple runs promote to L3 via the standard L5→L3 flow. |
| **Promotion** | The explicit, auditable act of extracting verified findings from an L5 or L6 artifact and recording them in an L3 artifact (wiki page, normative doc) or L2 registry entry, with an auditable trail per Section 7.4. |
| **Retention** | The defined period during which a non-durable artifact remains in the working tree before archival or deletion. Advisory until cleanup automation ships (Section 8.1). |
| **Bridge** | A directional connection between layers that allows information to flow (promotion upward; context injection downward). All bridges use L1–L6 endpoints only. |
| **Silent promotion** | Moving content from L5/L6 to L3 without an auditable trail — an anti-pattern (AP-5). "Auditable" means at least one of the three mechanisms in Section 7.4. |
| **Canonicalization** | Treating a transient artifact as if it were authoritative and durable — an anti-pattern (AP-6) unless formal promotion has occurred. |
| **Parent baseline floor** | The three-field minimum required-set for L3 wiki frontmatter (`title`, `last_updated`, `doc_key`) declared by parent #2205 Section 8.1. Every wiki `CLAUDE.md` must declare these as required. |
| **doc_key** | Canonical content-based identity of a source document, in the form `<algorithm>:<hex>` per parent #2205 Section 3 (e.g., `sha256:a1b2c3...`). Bare-hex form is a violation. |
| **`merged_at`** | Provenance-record timestamp recorded when a record is first appended to a document's `provenance[]` array (per parent #2205 Section 3, renamed from `discovered` on 2026-04-19). |
