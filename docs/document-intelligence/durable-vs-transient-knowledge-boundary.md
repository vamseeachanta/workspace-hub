# Durable vs Transient Knowledge Boundary

> **Issue:** [#2209](https://github.com/vamseeachanta/workspace-hub/issues/2209)
> **Parent:** [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) — LLM-Wiki + Resource/Document Intelligence Operating Model
> **Sibling:** [#2207](https://github.com/vamseeachanta/workspace-hub/issues/2207) — Standards/Codes Provenance + Reuse Contract
> **Status:** Normative — approved boundary policy for durable vs transient knowledge
> **Date:** 2026-04-11
> **Scope:** Policy only. Implementation delegated to follow-on issues.

---

## 1. Purpose and Scope

### What this document defines

This is the **durable-vs-transient knowledge boundary policy** for the workspace-hub intelligence ecosystem. It establishes:

- A clear classification of every major artifact class as durable, transient, or recurring-operational
- Ownership statements for each artifact class: what it is for, what it is not for
- Allowed bridge and sync directions between durable and transient layers
- Promotion rules: when and how a transient artifact graduates to durable knowledge
- Retention and expiration guidance for transient artifacts
- Anti-patterns that blur the boundary
- Guardrails to prevent boundary drift
- Recommended follow-on implementation surfaces

### What this document does NOT define

| Out of scope | Owner |
|---|---|
| The parent pyramid model, layer ownership, or information flow rules | #2205 (parent operating model) |
| Provenance schema, `doc_key` definition, or reuse-vs-reparse rules | #2207 (provenance contract) |
| Conformance validation scripts or linters | #2206 |
| Retrieval contract for issue workflows | #2208 |
| Unified registry file format or query interface | #2136 |

This policy specializes the parent model for the durable/transient boundary. It does not redefine it.

---

## 2. Relationship to Parent Operating Model (#2205)

This document inherits from the [parent operating model](llm-wiki-resource-doc-intelligence-operating-model.md) and operates under its constraints:

| Parent rule | How this policy applies it |
|---|---|
| **Layer 3 — Durable knowledge** owns distilled reusable knowledge and conceptual synthesis | This policy defines what qualifies as "durable" and the criteria for admission to L3 |
| **Layer 5 — Execution state** owns scope, ownership, approval state, delivery tracking | This policy makes explicit that L5 artifacts are transient with respect to domain knowledge — they track execution, not truth |
| **Layer 6 — Transient session** owns handoffs, research notes, working context | This policy defines retention, expiration, and promotion rules for L6 artifacts |
| **L6→L3 promotion flow** requires "explicit promotion decision" | This policy specifies the concrete criteria and process for that promotion |
| **L5→L3 promotion flow** for post-issue validated findings | This policy defines when issue-derived findings deserve promotion and when they should remain in execution state |
| **Ownership invariant**: every artifact belongs to exactly one layer | This policy resolves ambiguous cases where artifacts appear to serve both durable and transient purposes |
| **Most-durable-owner rule**: assign to the lowest-numbered layer whose ownership covers the artifact's primary purpose | This policy applies this rule to classify borderline artifacts |

### Conflict resolution

If this policy is found to conflict with the parent operating model, the parent takes precedence. Conflicts must be documented as comments on #2205 with a proposed amendment before any deviation.

---

## 3. Relationship to Sibling Provenance/Reuse Contract (#2207)

The [provenance/reuse contract](standards-codes-provenance-reuse-contract.md) defines identity (`doc_key`), provenance fields, and reuse-vs-reparse rules for standards/codes. This boundary policy complements it without overlap:

| This policy (#2209) | Provenance contract (#2207) |
|---|---|
| Classifies artifact **roles** as durable vs transient | Defines artifact **identity** and provenance fields |
| Governs which artifacts may persist and which must expire | Governs how to identify, trace, and reuse artifacts |
| Defines promotion criteria (when to move to durable) | Defines promotion path mechanics (how the pipeline moves artifacts) |
| Covers all artifact classes across all layers | Specializes for standards/codes at L1-L2-L3 |

**Non-overlap rule:** This policy does not define `doc_key` semantics, provenance field requirements, or reparse decision trees. Those belong to #2207. This policy does not define registry schemas or accessibility registries. Those belong to #2136.

---

## 4. Artifact Classes and Ownership Statements

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

**Examples from this repo:**
- `knowledge/wikis/engineering/wiki/concepts/mooring-line-failure-physics.md` — durable domain knowledge
- `knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md` — durable tool reference
- `knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md` — promoted L5→L3 findings

### 4.2 GitHub Issues, Plans, and Review Artifacts

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

**Durability:** Transient with respect to domain knowledge. Issues close. Plans are consumed during execution and become historical records. Review artifacts are evidence of a point-in-time assessment.

**Retention:** Retain indefinitely for audit trail and governance compliance, but do NOT treat as canonical knowledge sources after issue closure. Valuable findings must be promoted to L3 via explicit promotion.

**Examples from this repo:**
- `docs/plans/2026-04-11-issue-2205-*.md` — execution plan, transient
- `scripts/review/results/2026-04-11-issue-2207-claude-review.md` — review evidence, transient
- GitHub issue #2209 — execution state, transient (the resulting policy doc is durable, the issue is not)

### 4.3 Registries, Ledgers, and Manifests

**Layer:** L2 — Registry/provenance
**Location:** `data/document-index/`, manifests, ledgers

**What registries are for:**
- Inventory of known documents: paths, hashes, extraction status, lineage
- Provenance tracking: where a document came from, when it was indexed, what was extracted
- Machine-readable lookup for `doc_key`-based identity resolution

**What registries are NOT for:**
- Narrative synthesis or conceptual knowledge (use wikis at L3)
- Execution tracking or task state (use issues at L5)
- Human-readable documentation or editorial content

**Durability:** Durable. Registry entries persist as long as the underlying source documents exist. Entries may be updated (status changes, new path aliases) but are not deleted unless the source is retired.

**Examples from this repo:**
- `data/document-index/standards-transfer-ledger.yaml` — durable provenance ledger
- `data/document-index/registry.yaml` — durable aggregate statistics
- `data/document-index/mounted-source-registry.yaml` — durable source-root inventory

### 4.4 Weekly Review Artifacts

**Layer:** Between L5 and L6 — Recurring operational evidence
**Location:** Weekly review outputs (format per #2089/#2139)

**What weekly reviews are for:**
- Recurring operational health assessment of the intelligence ecosystem
- Point-in-time evidence of machine readiness, knowledge freshness, and accessibility
- Triggering follow-on issues when gaps are found

**What weekly reviews are NOT for:**
- Serving as the durable source of truth for domain knowledge — each review is a snapshot
- Replacing wiki pages, registries, or governance docs
- Accumulating into an ever-growing canonical reference

**Durability:** Recurring-operational. Each review instance is transient (it captures a moment in time). The review *template* and *process definition* are durable (they live in `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`). The *output artifacts* from individual runs are retained for trend analysis but are not canonical knowledge.

**Retention:** Retain weekly outputs for 90 days or the most recent 12 runs (whichever is longer) for trend analysis. Older outputs may be archived or pruned. Significant findings must be promoted to L3 or captured as new issues at L5.

### 4.5 Session, Handoff, and Scratchpad Artifacts

**Layer:** L6 — Transient session
**Location:** `docs/handoffs/`, `.planning/`, `.claude/state/`, agent scratchpads

**What session artifacts are for:**
- Capturing working context for session continuity: what was done, what remains, what was discovered
- Providing input for the next session or the next agent in a multi-agent chain
- Recording temporary research, debugging notes, and draft analysis

**What session artifacts are NOT for:**
- Serving as canonical knowledge — session notes decay and are never authoritative
- Replacing wiki entries, registry records, or governance documents
- Persisting beyond their useful continuity window without explicit promotion

**Durability:** Transient by default. Session artifacts are consumed by downstream sessions and then become stale. They must be promoted or allowed to expire.

**Retention:** Retain handoff files for 30 days. Retain `.planning/` artifacts for the duration of the associated issue plus 14 days after closure. Retain `.claude/state/session-signals/` for 7 days. After retention, artifacts may be archived or deleted.

**Examples from this repo:**
- `docs/handoffs/session-2026-04-11-provider-audit-exit.md` — transient session handoff
- `.planning/plan-approved/*.md` — transient governance markers
- `.planning/discoveries/*.jsonl` — transient worker discoveries (pending promotion)
- `.claude/state/session-signals/2026-04-11.jsonl` — transient session telemetry

---

## 5. Durable vs Transient Classification Rules

### 5.1 The classification test

To determine whether an artifact is durable or transient, apply this decision tree:

```
Does the artifact contain reusable domain knowledge that
outlives the issue/session that created it?
├── YES → Is it conceptual/technical synthesis? → L3 Durable (wiki)
│         Is it provenance/inventory data?     → L2 Durable (registry)
│         Is it process/governance definition?  → Durable (governance doc)
└── NO  → Is it tracking execution of a specific work item?
          ├── YES → L5 Transient (issue/plan/review)
          └── NO  → Is it capturing session context for continuity?
                    ├── YES → L6 Transient (handoff/scratchpad)
                    └── NO  → Is it recurring operational evidence?
                              ├── YES → Recurring-operational (weekly review output)
                              └── NO  → Apply the most-durable-owner rule from #2205
```

### 5.2 Hard classification rules

These rules are not "it depends" — they are binary:

| Rule | Classification |
|---|---|
| An LLM-wiki page under `knowledge/wikis/` | Always durable (L3) |
| A registry/ledger entry under `data/document-index/` | Always durable (L2) |
| A GitHub issue | Always transient for domain knowledge (L5 execution state) |
| A session handoff under `docs/handoffs/` | Always transient (L6) |
| A `.planning/` artifact | Always transient (L6) |
| A `.claude/state/` artifact | Always transient (L6) |
| An agent scratchpad or discovery JSONL | Always transient (L6) until promoted |
| A governance/process definition doc (e.g., `SESSION-GOVERNANCE.md`) | Durable — it defines how the system operates |
| A plan file under `docs/plans/` | Transient (L5) — it directed a specific work item |
| A review result under `scripts/review/results/` | Transient (L5) — it is evidence of a point-in-time review |

### 5.3 Borderline cases and resolution

| Artifact | Seems like | Actually is | Resolution |
|---|---|---|---|
| `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` | Durable analysis | Transient operational audit | L5 — it captured a point-in-time compliance state; findings should be promoted to L3 if they are reusable |
| `knowledge/wikis/.../sources/closed-engineering-issues.md` | Transient issue data | Durable promoted knowledge | L3 — the promotion has already happened; the wiki page is the durable artifact, not the original issues |
| `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | Execution output of #2205 | Durable architecture document | L3-adjacent — it is a normative contract, not execution state; it lives at L3 durability even though it was produced by L5 execution |
| Weekly review output | Recurring evidence | Recurring-operational | Neither fully durable nor fully transient — retain for trend analysis, promote significant findings |
| This document (`durable-vs-transient-knowledge-boundary.md`) | Execution output of #2209 | Durable policy contract | Durable — once approved, it governs future behavior regardless of issue #2209's lifecycle |

---

## 6. Allowed Bridge and Sync Directions

### 6.1 Primary bridge directions

Bridges connect transient and durable layers. Each bridge is directional.

| From | To | Bridge type | Trigger |
|---|---|---|---|
| L6 Transient session | L3 Durable knowledge | **Promotion** | Explicit decision after review — worker discoveries, session findings |
| L5 Execution state | L3 Durable knowledge | **Post-issue promotion** | Issue closure with validated findings worth preserving as domain knowledge |
| L6 Transient session | L5 Execution state | **Issue creation** | Session discovers a bug, gap, or follow-on work item → `gh issue create` |
| L5 Execution state | L6 Transient session | **Context injection** | Session reads issue context, plan, and review history as working input |
| L3 Durable knowledge | L5 Execution state | **Evidence consumption** | Issue planning and execution reads wiki pages and registries as evidence |
| L2 Registry/provenance | L3 Durable knowledge | **Structured promotion** | Registry outputs (summaries, extractions) promoted into wiki pages per #2207 pipeline |
| Recurring-operational | L5 Execution state | **Finding escalation** | Weekly review finds a gap → creates or updates an issue |
| Recurring-operational | L3 Durable knowledge | **Trend promotion** | Repeated weekly findings indicate a pattern worth documenting in a wiki page |

### 6.2 Forbidden bridge directions

| From | To | Why forbidden |
|---|---|---|
| L5 Execution state | L3 Durable knowledge (without promotion) | Issues must not silently become the knowledge source — they close and go stale |
| L6 Transient session | L3 Durable knowledge (without promotion) | Session notes must not become canonical — they decay by definition |
| L3 Durable knowledge | L6 Transient session (write-back) | Wikis must not be updated with session-local findings that haven't been reviewed |
| L3 Durable knowledge | L5 Execution state (ownership transfer) | Wiki pages must not become owned by an issue — the issue consumes the wiki, not the reverse |
| Recurring-operational | L3 Durable knowledge (raw dump) | Individual weekly review outputs must not be pasted into wiki pages — only synthesized findings get promoted |

### 6.3 Sync rules

| Rule | Description |
|---|---|
| **No silent promotion** | Every movement from transient to durable requires an explicit, auditable decision — either a promotion comment on an issue, a committed wiki page with source traceability, or a promoted-artifact record in a registry |
| **No reverse demotion** | Durable artifacts do not become transient. If a wiki page is found to be wrong, it is corrected or archived — not moved to a handoff file |
| **No transient-to-transient canonicalization** | One session's handoff does not become the next session's source of truth for domain knowledge. It becomes working context only. The session must verify against L3/L2 before treating handoff claims as authoritative |
| **Read-through is always allowed** | Any layer may read from any lower layer for context. Reading does not change ownership or durability |

---

## 7. Promotion Rules from Transient to Durable

### 7.1 Promotion criteria

A transient artifact deserves promotion to durable knowledge (L3) when ALL of the following are true:

| Criterion | Test |
|---|---|
| **Reusability** | The finding is useful beyond the issue/session that produced it — future agents or humans will need this information |
| **Verification** | The finding has been validated — it is not a speculative hypothesis or untested claim |
| **Non-redundancy** | No existing wiki page already contains this knowledge (or the existing page needs updating with new evidence) |
| **Source traceability** | The finding can be traced to a specific source: a `doc_key`, a closed issue, a validated experiment, or a cited external reference |
| **Stability** | The finding is not expected to change within the next 30 days — it represents settled understanding, not in-flight work |

### 7.2 Promotion process

1. **Identify the candidate.** During issue closure, session wrap-up, or weekly review, flag findings that meet all five criteria above.
2. **Choose the target.** Determine whether the finding belongs in:
   - An existing wiki page (update) — if the concept/entity already has a page
   - A new wiki page (create) — if no page covers this domain area
   - A registry entry (update) — if the finding is provenance/inventory data
3. **Write the promoted content.** Create or update the target artifact with proper source traceability (cite the issue, `doc_key`, or session that produced the finding).
4. **Record the promotion.** The promotion is its own evidence:
   - Wiki pages include frontmatter with `last_updated` and source references
   - The wiki log (`wiki/log.md`) records the ingest event
   - The originating issue or session handoff can note "promoted to `<wiki-page-path>`"
5. **Do not modify the source.** The transient artifact (handoff, issue comment, discovery JSONL) remains as-is for audit trail. It is not deleted or edited to match the promoted version.

### 7.3 Promotion anti-patterns

| Anti-pattern | Why it is wrong | Correct approach |
|---|---|---|
| Copy-pasting a handoff section directly into a wiki page | Handoff content is session-local, informal, and often unverified | Extract the verified finding, synthesize it, add source traceability |
| Creating a wiki page from a single unreviewed session | Single-session findings may be wrong or incomplete | Wait for verification through issue closure, cross-review, or repeated weekly findings |
| Promoting execution-state language into domain knowledge | "We decided to use approach X for issue #1234" is execution state, not domain knowledge | Promote the *what* and *why* of the approach, not the decision narrative |
| Mass-promoting weekly review findings without synthesis | Individual weekly outputs are snapshots, not knowledge | Synthesize recurring findings into a single wiki entry with trend evidence |

---

## 8. Retention and Expiration Guidance for Transient Artifacts

### 8.1 Retention schedule

| Artifact class | Default retention | After retention |
|---|---|---|
| Session handoffs (`docs/handoffs/`) | 30 days | Archive or delete |
| Planning workspace (`.planning/`) | Issue lifetime + 14 days | Archive or delete |
| Discovery JSONL (`.planning/discoveries/`) | 14 days (consumed by nightly learning pipeline) | Delete after pipeline processing |
| Session signals (`.claude/state/session-signals/`) | 7 days | Delete |
| Session governor state (`.claude/state/session-governor/`) | Per-session (tied to process lifetime) | Auto-cleaned after 7 days |
| Review results (`scripts/review/results/`) | 90 days | Archive |
| Plan files (`docs/plans/`) | Issue lifetime + 30 days | Archive |
| Weekly review outputs | 90 days or 12 most recent runs | Archive older runs |
| Plan approval markers (`.planning/plan-approved/`) | Issue lifetime | Delete after issue closure |
| Verification markers (`.planning/verified/`) | Issue lifetime + 14 days | Delete |

### 8.2 Archive vs delete

- **Archive** means move to a dated archive directory or compress into a bundle. Archived artifacts are not discoverable by default but can be recovered for audit purposes.
- **Delete** means remove from the repository. Deleted artifacts are recoverable via git history but are not present in the working tree.

### 8.3 Expiration signals

An artifact should be considered expired (and eligible for cleanup) when:

| Signal | Applies to |
|---|---|
| Associated issue is closed for > 30 days | Plans, review results, `.planning/` markers |
| Handoff has been superseded by a newer handoff for the same work stream | Session handoffs |
| Discovery JSONL has been processed by the nightly learning pipeline | Discovery files |
| Weekly review output has been superseded by 12+ newer runs | Weekly review outputs |
| Session signal file is > 7 days old | `.claude/state/` signals |

---

## 9. Anti-Patterns and Guardrails

### 9.1 Anti-patterns

| # | Anti-pattern | Description | Why it is harmful | Example |
|---|---|---|---|---|
| AP-1 | **Issue as knowledge base** | Using GitHub issues (open or closed) as the canonical reference for domain knowledge | Issues close, context decays, search is unreliable for structured knowledge retrieval. Future agents will not find it. | Citing "see issue #1234 comment #7" instead of creating a wiki page |
| AP-2 | **Handoff as source of truth** | Treating a session handoff as the authoritative reference for a technical decision | Handoffs are informal, session-scoped, and unreviewed. They capture what one agent believed at exit time. | A new session reading `docs/handoffs/session-*.md` and treating its claims as verified domain knowledge without checking L3 |
| AP-3 | **Registry as narrative** | Writing explanatory text, synthesis, or editorial commentary into registry/ledger entries | Registries own inventory and provenance (L2). Narrative synthesis belongs in wikis (L3). | Adding "this standard is important for deepwater pipeline design" to a `standards-transfer-ledger.yaml` entry |
| AP-4 | **Wiki as task tracker** | Using wiki pages to track in-progress work, open questions about implementation, or who-is-doing-what | Wikis own durable knowledge (L3). Execution tracking belongs in issues (L5). | A wiki page containing "TODO: need to add section on fatigue" or "Assigned to terminal 3 for overnight batch" |
| AP-5 | **Silent promotion** | Moving content from transient to durable layers without an explicit, auditable promotion step | Breaks traceability. Makes it impossible to verify when and why knowledge entered the durable layer. | Editing a wiki page during a session without recording the source of the new information in frontmatter or the wiki log |
| AP-6 | **Transient canonicalization** | One session's handoff becoming the next session's accepted truth without verification | Creates a chain of unverified claims. Errors in one session propagate indefinitely. | Session B reading Session A's handoff claim "the API changed in v2.3" and writing code based on it without checking the actual API |
| AP-7 | **Recurring-output accumulation** | Retaining every weekly review output indefinitely as if each one were durable knowledge | Creates unbounded growth of operational snapshots that nobody reads. Obscures the actual durable findings. | 52 weekly review files in a directory with no synthesis, no pruning, and no promotion of recurring findings |
| AP-8 | **Plan as specification** | Treating an execution plan as the living specification after the issue is closed | Plans directed a specific implementation. Once closed, the *code and tests* are the specification, not the plan. | Referencing `docs/plans/2026-04-11-issue-*.md` as the authoritative behavior spec months after the issue closed |

### 9.2 Guardrails

| # | Guardrail | Enforcement level | Description |
|---|---|---|---|
| GR-1 | **Wiki pages must have source traceability** | Policy (enforceable via conformance check) | Every wiki page must include frontmatter linking to its sources (`doc_key`, issue number, or external citation) |
| GR-2 | **Issues must not be cited as domain knowledge after closure** | Policy (enforceable via linter) | References to closed issues should point to the promoted wiki page, not the issue itself |
| GR-3 | **Handoffs must be consumed, not canonicalized** | Convention (enforceable via session-start skill) | The session-start routine should treat handoff content as unverified context, not accepted truth |
| GR-4 | **Promotion requires explicit frontmatter update** | Policy (enforceable via wiki ingest pipeline) | Any wiki page update must update `last_updated` and `sources` frontmatter fields |
| GR-5 | **Transient artifacts must have expiration metadata** | Convention (future enforcement via cleanup script) | Handoffs and `.planning/` files should include a date or issue reference enabling automated cleanup |
| GR-6 | **Weekly review findings must be promoted or dropped within 30 days** | Convention | Findings that recur across 3+ weekly reviews must be promoted to a wiki page or issue; one-time findings expire with the review output |

---

## 10. Likely Implementation Surfaces

This section identifies where future work is needed to enforce the boundary policy. No code changes are defined here — only targets.

### 10.1 Templates and conventions

| Surface | Current state | Recommended change |
|---|---|---|
| Session handoff template | No formal template; handoffs vary in structure | Add `## Expiration` section with issue reference and expected lifetime |
| Wiki page frontmatter | `title`, `tags`, `sources`, `added`, `last_updated` | Add `promoted_from` field (optional) indicating the transient source that was promoted |
| Plan file template (`docs/plans/_template-issue-plan.md`) | No expiration metadata | Add `## Retention` section noting the plan expires with the issue |
| `.planning/discoveries/` JSONL schema | Structured per worker-discovery-protocol skill | No change needed; existing schema supports promotion routing |

### 10.2 Skills and workflows

| Surface | Current state | Recommended change |
|---|---|---|
| `session-start-routine` skill | Loads context from handoffs and `.planning/` | Add guidance: "Treat handoff claims as unverified working context; verify domain claims against L3 wikis before acting on them" |
| `issue-planning-mode` skill | Full 5-step planning workflow | Add post-closure step: "Identify findings worth promoting to L3 and route via promotion process" |
| `worker-discovery-protocol` skill | Defines discovery capture and orchestrator triage | Already supports promotion routing by category; no change needed |
| `comprehensive-learning-wrapper` skill | Nightly learning pipeline | Add promotion step: discoveries that meet all 5 promotion criteria → wiki page creation or update |
| Weekly review process (`#2089`) | Template exists; no automated output cleanup | Add retention enforcement: archive outputs older than 90 days or 12 runs |

### 10.3 Automated enforcement (future)

| Surface | Enforcement type | Effort |
|---|---|---|
| Wiki frontmatter validator | Conformance check (#2206) — reject wiki pages missing `sources` or `last_updated` | Small |
| Transient artifact cleanup script | Cron job — archive/delete expired handoffs, `.planning/` files, session signals | Medium |
| Closed-issue citation linter | Pre-commit check — warn when code or docs cite closed issues instead of wiki pages | Medium |
| Weekly review pruner | Scheduled job — archive weekly outputs beyond retention window | Small |
| Promotion audit trail checker | Conformance check — verify that promoted wiki pages have matching source references | Medium |

---

## 11. Open Questions and Residual Risks

1. **Retention enforcement timing.** This policy defines retention periods but does not implement the cleanup automation. Until a transient-artifact cleanup script exists, retention is advisory only. Risk: transient artifacts accumulate indefinitely, blurring the boundary by sheer volume.

2. **Promotion judgment calls.** The five promotion criteria (Section 7.1) require human or orchestrator judgment. There is no fully automated test for "reusability" or "stability." Risk: under-promotion (valuable findings left to rot in handoffs) or over-promotion (premature findings polluting wikis).

3. **Weekly review output format.** The weekly review process (#2089) has not yet standardized its output format (#2139). Until the format is stable, retention and promotion rules for weekly outputs are difficult to enforce mechanically.

4. **Handoff template adoption.** Adding expiration metadata to handoffs requires updating the session-exit workflow across all agents (Claude, Codex, Gemini). Risk: inconsistent adoption leading to some handoffs having expiration data and others not.

5. **Cross-repo boundary.** This policy covers `workspace-hub` only. Satellite repos (e.g., `digitalmodel`) have their own knowledge artifacts. The boundary policy should eventually extend to cover promoted artifacts that cross repo boundaries, but this is out of scope for #2209.

6. **Recurring-operational classification.** Weekly review outputs are classified as "recurring-operational" — a category that sits between L5 and L6. This is a pragmatic classification, not a formal new layer. If recurring-operational artifacts proliferate beyond weekly reviews (e.g., nightly batch reports, daily dashboards), a more formal classification may be needed.

---

## 12. Recommended Follow-On Implementation Sequence

Based on the implementation surfaces identified in Section 10 and the dependency order from the parent operating model:

| Order | Work item | Scope | Depends on |
|---|---|---|---|
| 1 | Add `promoted_from` frontmatter field to wiki page schema | Small — update `SCHEMA.md`, update ingest validation | Nothing |
| 2 | Update `session-start-routine` skill with handoff-verification guidance | Small — edit one skill file | Nothing |
| 3 | Add `## Retention` section to plan file template | Small — edit template | Nothing |
| 4 | Add post-closure promotion step to `issue-planning-mode` skill | Small — edit one skill file | #1 (wiki schema must support `promoted_from`) |
| 5 | Build transient-artifact cleanup script | Medium — cron job for handoff/`.planning/` expiration | #3 (retention metadata in templates) |
| 6 | Add wiki frontmatter validator to conformance checks (#2206) | Medium — linter rejecting missing `sources`/`last_updated` | #1 |
| 7 | Add closed-issue citation linter | Medium — pre-commit warning for stale issue references | Nothing |
| 8 | Add weekly review output pruner | Small — scheduled cleanup of old review outputs | Weekly review output format stabilization (#2139) |

These items should be captured as implementation issues under #2209 or as sub-tasks of #2206 (conformance checks), depending on whether they primarily affect boundary policy or validation tooling.

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| **Durable artifact** | An artifact that persists as canonical knowledge or infrastructure — its value does not decay with time unless the underlying domain changes |
| **Transient artifact** | An artifact tied to a specific issue, session, or point in time — it serves a temporary purpose and must be promoted or allowed to expire |
| **Recurring-operational artifact** | An artifact produced on a regular cadence (weekly, nightly) that captures a snapshot of system state — individually transient, collectively useful for trend analysis |
| **Promotion** | The explicit, auditable act of extracting verified findings from a transient artifact and recording them in a durable artifact (wiki page, registry entry) |
| **Retention** | The defined period during which a transient artifact remains in the working tree before archival or deletion |
| **Bridge** | A directional connection between layers that allows information to flow from transient to durable (promotion) or durable to transient (context injection) |
| **Silent promotion** | Moving content from transient to durable without explicit traceability — an anti-pattern |
| **Canonicalization** | Treating a transient artifact as if it were authoritative and durable — an anti-pattern unless formal promotion has occurred |
