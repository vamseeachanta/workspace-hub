# Pyramid Conformance Checks — Validation Design

> **Issue:** [#2206](https://github.com/vamseeachanta/workspace-hub/issues/2206)
> **Parent:** [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) — LLM-Wiki + Resource/Document Intelligence Operating Model
> **Siblings:** [#2207](https://github.com/vamseeachanta/workspace-hub/issues/2207) (provenance contract), [#2209](https://github.com/vamseeachanta/workspace-hub/issues/2209) (durable/transient boundary), [#2096](https://github.com/vamseeachanta/workspace-hub/issues/2096) (accessibility map)
> **Status:** Normative — approved conformance-check design for the single-source-of-truth pyramid
> **Date:** 2026-04-11
> **Scope:** Validation design only. Implementation of scripts, CI hooks, and registry changes is delegated to follow-on issues.

---

## 1. Purpose and Scope

### What this document defines

This is the **conformance-check design** for the workspace-hub intelligence ecosystem's single-source-of-truth pyramid. It establishes:

- Concrete validation rules derived from the approved parent operating model (#2205) and its child contracts (#2207, #2209, #2096)
- A candidate checks matrix with pass/fail signals for each rule
- Classification of each check as automatable (from existing repo state) or manual
- Priority ordering for which checks to implement first
- Anti-patterns and failure modes that conformance checks should detect
- Recommended implementation sequence for building the checks

### What this document does NOT define

| Out of scope | Owner |
|---|---|
| The parent pyramid model, layer ownership, or information flow rules | #2205 (parent operating model) |
| Provenance schema, `doc_key` definition, or reuse-vs-reparse rules | #2207 (provenance contract) |
| Durable-vs-transient boundary policy or promotion rules | #2209 (boundary policy) |
| Accessibility inventory or weekly checklist content | #2096 (accessibility map) |
| Registry file format or query interface | #2136 |
| Retrieval contract for issue workflows | #2208 |
| Actual script implementations, CI hook code, or linter executables | Follow-on implementation issues |

This document is a **validation design** — it defines what to check and how to recognize pass/fail. It does not contain executable scripts, CI pipeline definitions, or linter implementations.

### Design vs implementation distinction

Throughout this document:
- **"Check"** means a defined validation rule with inputs, logic, and a pass/fail signal
- **"Automatable"** means the check can be implemented as a script that reads existing repo files and produces a binary pass/fail result
- **"Manual"** means the check requires human or agent judgment that cannot be reduced to file inspection
- **"Checkable now"** means all inputs for the check already exist in the repo today
- **"Requires future tooling"** means the check depends on artifacts, schemas, or pipelines that sibling issues have not yet implemented

---

## 2. Relationship to Parent Operating Model (#2205)

This document inherits from the [parent operating model](llm-wiki-resource-doc-intelligence-operating-model.md) and operates under its constraints:

| Parent rule | How this design applies it |
|---|---|
| **Single-source-of-truth pyramid** (Section 2) | Checks validate that artifacts are assigned to exactly one layer |
| **Ownership invariant** (Section 2) | Checks detect artifacts that serve two layers without being split |
| **`doc_key` rule** (Section 3) | Checks detect path-only identity leakage and `doc_key` absence |
| **Allowed information flows** (Section 4) | Checks validate that cross-layer references follow permitted directions |
| **Forbidden information flows** (Section 5) | Checks detect anti-pattern flows (L3 reparsing, issues as knowledge base, etc.) |
| **Named exceptions** (Section 6) | Checks permit audit reads across layers without flagging |
| **Cross-machine access model** (Section 7) | Checks validate that cached artifacts do not silently become canonical |
| **Unified artifact registry** (Section 8) | Checks validate `doc_key` convergence across existing identity fields |
| **Child issue guardrails** (Section 10) | Checks detect when child artifacts redefine parent-level contracts |
| **Discoverability** (Section 11) | Checks validate that cross-links exist between parent and child artifacts |

### Conflict resolution

If a conformance check is found to conflict with the parent operating model, the parent takes precedence. The check must be amended or retired — the parent model is never adjusted to accommodate a check.

---

## 3. Relationship to Sibling Child Artifacts (#2207, #2209, #2096)

Each sibling artifact contributes specific rules that this conformance design validates:

### #2207 — Standards/Codes Provenance + Reuse Contract

| Rule from #2207 | Conformance check class |
|---|---|
| `doc_key` is SHA-256 of source file content (Section 3.1) | Identity consistency checks |
| All registry entries must reference `doc_key` (Section 3.2) | Identity field presence checks |
| `sha256:` prefix must be stripped for comparison (Section 3.2) | Identity normalization checks |
| Reuse-vs-reparse decision tree requires artifact existence (Section 5.1) | Artifact-existence guard checks |
| Anti-patterns: duplicate parsing, path-only identity, broken lineage, wiki outranking provenance, prefix inconsistency (Section 8) | Anti-pattern detection checks |

### #2209 — Durable-vs-Transient Knowledge Boundary

| Rule from #2209 | Conformance check class |
|---|---|
| Hard classification rules: wikis are L3, registries are L2, issues are L5, handoffs are L6 (Section 5.2) | Layer assignment checks |
| Forbidden bridge directions (Section 6.2) | Flow direction checks |
| Promotion requires explicit frontmatter update (Guardrail GR-4) | Promotion traceability checks |
| Wiki pages must have source traceability (Guardrail GR-1) | Wiki frontmatter checks |
| Transient artifacts in normative directories (Anti-pattern related) | Misplaced artifact checks |
| Retention schedule compliance (Section 8.1) | Retention compliance checks |

### #2096 — Intelligence Accessibility Map

| Rule from #2096 | Conformance check class |
|---|---|
| `docs/README.md` must link to intelligence ecosystem (Section 6.1) | Entry-point link checks |
| `docs/document-intelligence/` needs an index (Section 6.3) | Directory index checks |
| Wiki domains must be reachable from `docs/` (Section 6.4) | Cross-tree link checks |
| No session handoffs in architecture directories (Section 6.7) | Misplaced artifact checks |
| Weekly accessibility checklist items (Section 7) | Accessibility regression checks |

### Non-overlap rule

This document does NOT redefine the rules above. It creates checks that validate them. If a rule needs changing, the change must happen in the owning sibling artifact (#2207, #2209, or #2096), not in a conformance check definition.

---

## 4. Conformance Target Classes

The pyramid's rules group into six conformance target classes. Each class corresponds to a family of related checks.

### 4.1 Layer Ownership

**What it validates:** Every artifact in the intelligence ecosystem belongs to exactly one layer, and that assignment matches the layer's ownership definition from #2205 Section 2.

**Parent rules consumed:**
- Ownership invariant: "Every artifact belongs to exactly one layer"
- Most-durable-owner rule: "Assign to the lowest-numbered layer whose ownership definition covers the artifact's primary purpose"
- Layer ownership table from #2205 Section 2 (L1–L6 with "Owns" and "Must NOT own" columns)

**What violations look like:**
- A wiki page (`knowledge/wikis/`) that tracks execution state (TODO items, assigned-to fields)
- A registry entry (`data/document-index/`) that contains narrative synthesis
- A session handoff (`docs/handoffs/`) filed in an architecture directory (`docs/document-intelligence/`)
- An issue plan (`docs/plans/`) treated as the living specification after issue closure

**Concrete examples from current repo:**
- #2096 Section 6.7 identified session handoff files (`session-handoff-terminal5-2026-04-02*.md`) inside `docs/document-intelligence/` — a transient (L6) artifact in a normative (L3-adjacent) directory

### 4.2 Document Identity Usage

**What it validates:** All references to source documents use content-based identity (`doc_key` / `content_hash` / SHA-256), not path-only references that create competing identities.

**Parent rules consumed:**
- #2205 Section 3: "File paths are aliases. The same document may appear at multiple paths."
- #2207 Section 3.2: "All registry entries, summaries, promoted artifacts, and wiki-ready records must reference documents by `doc_key`"
- #2207 Section 8.2: Path-only identity anti-pattern

**What violations look like:**
- Two separate registry entries for the same document at different paths, without a shared `doc_key`
- A wiki page citing a source by path alone with no `doc_key` or content hash
- A promoted artifact (in digitalmodel) without a `doc_key` back-link comment

### 4.3 Information-Flow Rules

**What it validates:** Cross-layer references follow the permitted flow directions from #2205 Section 4 and do not create the forbidden patterns from #2205 Section 5.

**Parent rules consumed:**
- Permitted flows: L1→L2 (indexing), L2→L3 (promotion), L2→L4 (feeding maps), L3+L2→L5 (evidence consumption), L6→L3 (explicit promotion), L5→L3 (post-issue promotion)
- Forbidden flows: L3 reparsing raw docs when L2 evidence exists, issues as knowledge base, transient artifacts becoming canonical without promotion, entry-point docs inventing provenance, path-only identity creating duplicate truth, circular flows

**What violations look like:**
- A wiki ingest pipeline reading raw PDFs when a summary already exists for that `doc_key`
- A doc or code comment citing a closed issue as authoritative domain knowledge instead of the promoted wiki page
- An entry-point document (`docs/README.md`, accessibility map) asserting provenance facts not backed by L2

### 4.4 Durable/Transient Boundary

**What it validates:** Artifact classification follows #2209's decision tree and hard rules, promotion happens through explicit auditable steps, and retention policies are respected.

**Parent rules consumed:**
- #2209 Section 5.2: Hard classification rules (wikis=L3, registries=L2, issues=L5, handoffs=L6, etc.)
- #2209 Section 6.2: Forbidden bridge directions
- #2209 Section 7: Promotion criteria and process
- #2209 Section 8: Retention schedule
- #2209 Section 9: Anti-patterns (AP-1 through AP-8) and guardrails (GR-1 through GR-6)

**What violations look like:**
- A wiki page missing `sources` or `last_updated` frontmatter (GR-1 violation)
- A session handoff older than 30 days still in the working tree (retention violation)
- A `.planning/` artifact surviving more than 14 days after its issue closed (retention violation)
- Content moved from a handoff directly into a wiki without source traceability (AP-5: silent promotion)

### 4.5 Accessibility/Discoverability Linkage

**What it validates:** Intelligence assets are reachable from standard entry points within the navigation-hop budget defined by #2096.

**Parent rules consumed:**
- #2096 Section 5: Accessibility map table (discoverability ratings per asset)
- #2096 Section 6: Broken and weak accessibility patterns
- #2096 Section 7: Weekly accessibility checklist
- #2205 Section 11: Cross-link table (which artifacts should reference the parent model)

**What violations look like:**
- `docs/README.md` having zero links to `knowledge/wikis/`, `data/document-index/`, or `docs/document-intelligence/`
- A child artifact (#2207, #2209, #2096 docs) not linking back to the parent operating model
- The parent operating model not listing a child artifact in its cross-links table
- A wiki domain's `CLAUDE.md` not referencing the parent operating model

### 4.6 Issue Classification and Child Guardrails

**What it validates:** Child issues operate within the guardrails defined by #2205 Section 10, and their artifacts do not redefine parent-level contracts.

**Parent rules consumed:**
- #2205 Section 10: "May implement" and "Must NOT redefine" table for each child issue
- #2205 Section 10: Conflict resolution — child must document conflicts as comments on #2205 and wait for approval

**What violations look like:**
- A #2207 artifact redefining the pyramid layer boundaries
- A #2209 artifact redefining the `doc_key` identity model
- A #2208 artifact redefining provenance schema
- Any child artifact silently changing parent-level terminology, adding layers, or altering flow rules without an amendment comment on #2205

---

## 5. Candidate Checks Matrix

Each check is defined with: name, purpose, whether it is manual or automatable, required inputs, and the pass/fail signal.

### 5.1 Layer Ownership Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal |
|---|---|---|---|---|---|---|
| OWN-1 | Wiki-page-is-not-tracker | Detect L3 wiki pages that contain execution-state language (TODO, assigned-to, in-progress) | Automatable (now) | `knowledge/wikis/*/wiki/**/*.md` | No wiki page body contains execution-tracking keywords (`TODO:`, `ASSIGNED:`, `IN-PROGRESS:`, `status:in-flight`) | Any wiki page contains execution-tracking keywords |
| OWN-2 | Registry-is-not-narrative | Detect L2 registry entries containing narrative synthesis | Automatable (now) | `data/document-index/*.yaml` | No registry entry contains paragraph-length prose in value fields | Registry entries contain explanatory text > 200 characters in a single value |
| OWN-3 | Transient-not-in-normative-dir | Detect L6 session artifacts in L3-adjacent directories | Automatable (now) | `docs/document-intelligence/`, `docs/standards/`, `docs/governance/` | No files matching `session-handoff-*`, `handoff-*`, or `.planning/` patterns in normative directories | Session/handoff files found in normative directories |
| OWN-4 | Plan-not-treated-as-spec | Detect references to closed-issue plan files as authoritative specifications | Automatable (partial) | `docs/**/*.md`, `knowledge/**/*.md`, closed issue list | No doc references a plan file for a closed issue as a specification source | Doc cites `docs/plans/YYYY-MM-DD-issue-NNN-*.md` for a closed issue as authoritative |
| OWN-5 | Single-layer-assignment | Verify each artifact is assigned to exactly one layer | Manual | Full artifact inventory, layer definitions from #2205 | Each artifact maps to one and only one layer | An artifact serves two layers without being split |

### 5.2 Document Identity Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal |
|---|---|---|---|---|---|---|
| ID-1 | Registry-has-doc-key | Verify registry entries include a content-based identity field | Automatable (now) | `data/document-index/index.jsonl` | Every record has a `content_hash` or `doc_key` field with a 64-character hex value | Records exist without content-based identity |
| ID-2 | No-duplicate-doc-keys | Detect duplicate `doc_key` entries with conflicting metadata | Automatable (now) | `data/document-index/index.jsonl` | No two records share the same `doc_key` with contradictory `source`, `status`, or `path` values | Duplicate `doc_key` with conflicting metadata |
| ID-3 | Prefix-normalization | Detect inconsistent `sha256:` prefix usage | Automatable (now) | `data/document-index/index.jsonl`, shard files | All identity comparisons use bare 64-char hex (no `sha256:` prefix in lookup keys) | Mixed prefixed and bare hex values used as keys in the same context |
| ID-4 | Wiki-cites-doc-key | Verify wiki pages that cite source documents include `doc_key` in frontmatter | Automatable (now) | `knowledge/wikis/*/wiki/**/*.md` | Every wiki page with a `sources` frontmatter field includes at least one `doc_key` or content hash | Wiki page cites sources by path alone without content-based identity |
| ID-5 | Promoted-artifact-has-backlink | Verify promoted code artifacts contain `doc_key` back-link comments | Automatable (partial) | `digitalmodel/` promoted modules | Promoted modules contain `# doc_key:` or `# content_hash:` or `# content-hash:` comments | Promoted module has no source-document back-link |
| ID-6 | Path-only-identity-leakage | Detect systems tracking the same document by path alone at different locations | Manual | Registry entries, path alias arrays | Each document tracked by path at multiple locations shares a single `doc_key` | Same document at two paths without a shared `doc_key` |

### 5.3 Information-Flow Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal |
|---|---|---|---|---|---|---|
| FLOW-1 | No-L3-reparsing-with-L2-evidence | Detect wiki ingest reading raw files when summaries exist | Automatable (future) | `llm_wiki.py` ingest logs, `data/document-index/summaries/` | Wiki ingest checks for existing summary before reading raw file | Wiki ingest reads raw file for a `doc_key` that already has a summary |
| FLOW-2 | Issue-not-knowledge-base | Detect docs/code citing closed issues as domain knowledge source | Automatable (now) | `docs/**/*.md`, `knowledge/**/*.md` | References to closed issues point to promoted wiki pages, not to issue comments | Doc cites `#NNNN` (closed) as authoritative without a wiki page reference |
| FLOW-3 | Entry-point-no-provenance-invention | Detect L4 entry-point docs asserting provenance facts not in L2 | Manual | `docs/document-intelligence/intelligence-accessibility-map.md`, `docs/document-intelligence/data-intelligence-map.md`, `docs/README.md` | Entry-point docs reference existing asset locations without inventing new provenance claims | Entry-point doc asserts document properties (e.g., extraction status, domain classification) not backed by registry |
| FLOW-4 | No-circular-layer-claims | Detect two artifacts each claiming the other as source of truth | Manual | Cross-layer reference analysis | Every source-of-truth claim is unidirectional | Artifact A cites B as source; artifact B cites A as source |
| FLOW-5 | Transient-not-canonical-without-promotion | Detect transient artifacts treated as canonical without explicit promotion | Manual | Session handoffs, `.planning/` files, wiki pages | Every piece of domain knowledge in L3 has a traceable promotion path | Wiki page content appears to originate from a handoff or session note without promotion record |

### 5.4 Durable/Transient Boundary Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal |
|---|---|---|---|---|---|---|
| DT-1 | Wiki-frontmatter-completeness | Verify wiki pages have required frontmatter fields | Automatable (now) | `knowledge/wikis/*/wiki/**/*.md` | Every wiki page has `title`, `tags`, `sources`, `last_updated` in frontmatter | Wiki page missing any required frontmatter field |
| DT-2 | Handoff-retention-compliance | Detect session handoffs past their 30-day retention | Automatable (now) | `docs/handoffs/*.md`, current date | No handoff file older than 30 days | Handoff file with modification date > 30 days ago |
| DT-3 | Planning-artifact-retention | Detect `.planning/` artifacts surviving past issue closure + 14 days | Automatable (partial) | `.planning/` files, GitHub issue state | No `.planning/` artifact exists for an issue closed > 14 days ago | `.planning/` file references an issue closed > 14 days ago |
| DT-4 | Session-signal-retention | Detect `.claude/state/session-signals/` files older than 7 days | Automatable (now) | `.claude/state/session-signals/` | No signal file older than 7 days | Signal file with date > 7 days ago |
| DT-5 | Review-result-retention | Detect `scripts/review/results/` files older than 90 days | Automatable (now) | `scripts/review/results/*.md` | No review result file older than 90 days | Review file with date > 90 days ago |
| DT-6 | Silent-promotion-detection | Detect wiki page updates without corresponding frontmatter changes | Automatable (partial) | Git diff of `knowledge/wikis/*/wiki/**/*.md`, frontmatter `last_updated` | Every wiki page modification is accompanied by a `last_updated` change | Wiki page content changed but `last_updated` field unchanged |
| DT-7 | No-issue-as-knowledge-base | Detect wiki or doc references to issues as durable domain knowledge | Automatable (now) | `knowledge/wikis/*/wiki/**/*.md`, `docs/**/*.md` | References to issues serve as provenance citations, not as the knowledge content itself | A wiki page's primary content is "see issue #NNNN" with no synthesized knowledge |

### 5.5 Accessibility/Discoverability Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal |
|---|---|---|---|---|---|---|
| ACC-1 | Docs-README-links-intelligence | Verify `docs/README.md` links to intelligence ecosystem | Automatable (now) | `docs/README.md` | File contains links to `knowledge/wikis/`, `docs/document-intelligence/`, and `data/document-index/` (or equivalent navigation paths) | No links to intelligence ecosystem from `docs/README.md` |
| ACC-2 | Doc-intelligence-has-index | Verify `docs/document-intelligence/` has a navigable index | Automatable (now) | `docs/document-intelligence/README.md` or `docs/document-intelligence/INDEX.md` | Index file exists and is non-empty | No index file in `docs/document-intelligence/` |
| ACC-3 | Child-artifact-backlinks-parent | Verify child artifacts link back to parent operating model | Automatable (now) | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`, `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`, `docs/document-intelligence/intelligence-accessibility-map.md`, this document | Each child doc contains a link to `llm-wiki-resource-doc-intelligence-operating-model.md` | Child artifact has no reference to the parent document |
| ACC-4 | Parent-lists-child-artifacts | Verify parent operating model cross-links table includes all child artifacts | Automatable (now) | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` Section 11 | Cross-links table lists all existing child artifacts with correct paths | Child artifact exists but is not listed in parent cross-links |
| ACC-5 | Wiki-CLAUDE-md-references-parent | Verify wiki domain CLAUDE.md files reference the parent operating model | Automatable (now) | `knowledge/wikis/*/CLAUDE.md` | Each wiki CLAUDE.md contains a reference to the operating model or L3 scope | Wiki CLAUDE.md has no reference to governing architecture |
| ACC-6 | Weekly-checklist-file-existence | Verify all files referenced in the weekly accessibility checklist exist | Automatable (now) | File paths from #2096 Section 7 checklist | All referenced files exist and are non-empty | A file referenced in the weekly checklist is missing or empty |

### 5.6 Child Guardrail Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal |
|---|---|---|---|---|---|---|
| GUARD-1 | Child-does-not-redefine-layers | Detect child artifacts that define their own layer model | Manual | Child artifacts (#2207, #2208, #2209, #2096 docs) | Child docs reference parent layer definitions without redefining them | Child doc contains a layer table that contradicts #2205 Section 2 |
| GUARD-2 | Child-does-not-redefine-doc-key | Detect child artifacts that define a `doc_key` rule different from #2205/#2207 | Automatable (now) | Child artifacts | Child docs use `doc_key` consistently with #2207 Section 3 definition | Child doc defines `doc_key` differently or introduces a competing identity concept |
| GUARD-3 | Child-does-not-redefine-flows | Detect child artifacts that add or remove permitted/forbidden flows | Manual | Child artifacts, #2205 Sections 4-5 | Child docs reference parent flow rules without adding new ones | Child doc permits a flow forbidden by #2205 or forbids a flow permitted by #2205 |
| GUARD-4 | Child-scope-stays-within-guardrails | Verify each child artifact stays within its "May implement" scope | Manual | Child artifacts, #2205 Section 10 guardrail table | Child doc content matches its "May implement" column | Child doc implements something from another child's scope or from the parent's "Must NOT redefine" list |
| GUARD-5 | Conflict-documented-before-deviation | Verify any parent-model deviation is documented as a comment on #2205 | Manual | GitHub issue #2205 comments, child artifacts | Any deviation from the parent model has a corresponding amendment proposal on #2205 | Child artifact deviates from parent without a documented conflict resolution |

---

## 6. Priority Checks to Implement First

Based on three criteria — (a) severity of the violation they detect, (b) feasibility from current repo state, and (c) return on implementation effort — the following checks should be implemented first:

### Tier 1: Immediate value, automatable now

These checks can be built today using only existing repo files. They detect the most common and harmful violations.

| Priority | Check | Why first |
|---|---|---|
| P1 | **DT-1** Wiki frontmatter completeness | High volume (19K+ wiki pages), fully automatable, catches GR-1 violations. A single script scanning frontmatter YAML catches the most common boundary drift. |
| P2 | **ACC-1** docs/README.md links intelligence | Single-file check with highest discoverability impact. The #2096 review confirmed this is the biggest accessibility gap. |
| P3 | **OWN-3** Transient not in normative dir | Simple glob pattern check. Already identified as a real violation (#2096 Section 6.7 found session handoffs in `docs/document-intelligence/`). |
| P4 | **ID-1** Registry has doc-key | Single-file scan of `index.jsonl`. Validates the foundational identity rule from #2205/#2207. |
| P5 | **ACC-3** Child artifact backlinks parent | 4-file check (one per child artifact). Validates the cross-reference chain that holds the ecosystem together. |
| P6 | **ACC-6** Weekly checklist file existence | Runs the #2096 Section 7 checklist as a file-existence test. Catches broken references before the weekly review discovers them. |

### Tier 2: High value, requires moderate effort

| Priority | Check | Why second tier |
|---|---|---|
| P7 | **DT-2** Handoff retention compliance | Requires date comparison logic but inputs are simple (file modification dates). Prevents unbounded transient artifact accumulation. |
| P8 | **ID-3** Prefix normalization | Requires scanning `index.jsonl` for mixed `sha256:` prefix usage. Prevents join failures noted in #2207 Section 8.5. |
| P9 | **OWN-1** Wiki page is not tracker | Keyword scanning across wiki pages. Medium effort due to volume but catches a critical ownership violation. |
| P10 | **DT-7** No issue as knowledge base | Pattern matching for issue references used as primary knowledge content. Catches AP-1 from #2209. |

### Tier 3: Important but requires judgment or future tooling

| Priority | Check | Why third tier |
|---|---|---|
| P11 | **FLOW-1** No L3 reparsing with L2 evidence | Requires ingest pipeline instrumentation; cannot be checked from static files alone. |
| P12 | **ID-5** Promoted artifact has backlink | Requires access to `digitalmodel/` repo; cross-repo check. |
| P13 | **GUARD-1–5** Child guardrail checks | Require semantic analysis of document content; not reducible to pattern matching. |
| P14 | **OWN-5** Single-layer assignment | Requires full artifact inventory; comprehensive but labor-intensive. |

---

## 7. Feasible Automation Surfaces

### 7.1 Docs linters

**What:** Scripts that scan markdown files for structural conformance.

**Automatable checks:** DT-1, OWN-1, OWN-3, ACC-1, ACC-2, ACC-3, ACC-5, DT-7

**Implementation approach:**
- A single Python or shell script that reads markdown files and checks for:
  - Frontmatter field presence (DT-1): parse YAML frontmatter, verify required fields
  - Execution-tracking keywords in wiki pages (OWN-1): regex scan for TODO/ASSIGNED/IN-PROGRESS patterns
  - Session handoffs in normative directories (OWN-3): glob for `session-handoff-*` or `handoff-*` patterns in `docs/document-intelligence/`, `docs/standards/`, `docs/governance/`
  - Intelligence links in `docs/README.md` (ACC-1): grep for `knowledge/wikis`, `document-intelligence`, `document-index`
  - Index file existence (ACC-2): file-existence check
  - Parent backlinks in child artifacts (ACC-3): grep for `llm-wiki-resource-doc-intelligence-operating-model.md` or `#2205`
  - Wiki CLAUDE.md references (ACC-5): grep in each wiki's CLAUDE.md
  - Issue-as-knowledge-base pattern (DT-7): detect wiki pages where primary content is "see issue #NNNN"

**Estimated effort:** Small-medium. Most checks are file-existence or regex-pattern checks. The wiki frontmatter check (DT-1) is the most complex due to volume (19K+ pages) but is still a straightforward YAML parse.

**Run context:** Can run as a standalone script, a pre-commit check, or a CI step. Recommend starting as a standalone script invoked during weekly review; promote to pre-commit only for the highest-value checks.

### 7.2 Cross-link validators

**What:** Scripts that verify bidirectional references between parent and child documents.

**Automatable checks:** ACC-3, ACC-4, ACC-5, ACC-6

**Implementation approach:**
- Read the parent operating model's cross-links table (Section 11)
- For each listed artifact: verify the file exists and contains a back-reference to the parent
- For each child artifact: verify it appears in the parent's cross-links table
- For each file path in the weekly checklist (#2096 Section 7): verify the file exists

**Estimated effort:** Small. The parent cross-links table has ~12 entries. The weekly checklist has ~25 file-existence checks. Both are enumerable and static.

### 7.3 Artifact-ownership checks

**What:** Scripts that verify artifacts are in the correct directory for their layer assignment.

**Automatable checks:** OWN-3, DT-2, DT-3, DT-4, DT-5

**Implementation approach:**
- Map directories to expected layer assignments:
  - `knowledge/wikis/*/wiki/` → L3 only
  - `data/document-index/` → L2 only
  - `docs/plans/` → L5 only
  - `docs/handoffs/` → L6 only
  - `.planning/` → L6 only
  - `.claude/state/` → L6 only
  - `docs/document-intelligence/` → L3-adjacent normative docs only (no L6 session artifacts)
  - `scripts/review/results/` → L5 review evidence only
- Verify no files in a directory violate its layer constraint
- Check retention dates: handoffs > 30 days, `.planning/` > issue closure + 14 days, signals > 7 days, reviews > 90 days

**Estimated effort:** Small-medium. Directory-to-layer mapping is static. Retention checks require date parsing from filenames or git metadata.

### 7.4 Label/doc consistency checks

**What:** Scripts that verify GitHub issue labels and states are consistent with their document artifacts.

**Automatable checks:** OWN-4, DT-3, GUARD-5

**Implementation approach:**
- Use `gh` CLI to query issue state and labels
- For each plan file in `docs/plans/`: check if the associated issue is open or closed
- For each `.planning/` artifact: check if the associated issue is still open
- For closed issues with `status:plan-approved`: verify deliverable documents exist at expected paths

**Estimated effort:** Medium. Requires GitHub API calls and cross-referencing with local file state. The `gh` CLI is available in this repo's workflow.

**Note:** These checks are useful for the weekly review but are NOT suitable for pre-commit hooks (they require network access and issue-state lookups).

### 7.5 Identity consistency checks

**What:** Scripts that verify `doc_key`/`content_hash` usage across registry files.

**Automatable checks:** ID-1, ID-2, ID-3

**Implementation approach:**
- Parse `data/document-index/index.jsonl` (1M+ records)
- For each record: verify `content_hash` or `doc_key` field exists and is a 64-character hex string
- Check for duplicate `doc_key` values with conflicting metadata fields
- Check for mixed `sha256:` prefix and bare hex in identity fields

**Estimated effort:** Medium. The `index.jsonl` file is large (1M records), so the script must be efficient (streaming JSONL parse, not full-file load). But the checks themselves are simple field-value validations.

---

## 8. Checks That Are Intentionally Manual for Now

The following checks require human or agent judgment and are not automatable from static file inspection:

| Check | Why manual | When it might become automatable |
|---|---|---|
| **OWN-5** Single-layer assignment | Requires understanding an artifact's *purpose*, not just its location | When a machine-readable artifact-to-layer registry exists (#2136) |
| **FLOW-1** No L3 reparsing with L2 evidence | Requires runtime pipeline instrumentation | When `llm_wiki.py` ingest emits structured logs with reuse/reparse decisions |
| **FLOW-3** Entry-point no provenance invention | Requires semantic analysis of what constitutes a "provenance fact" | Unlikely to be fully automatable; keep as review checklist item |
| **FLOW-4** No circular layer claims | Requires cross-document semantic analysis of source-of-truth claims | Could be partially automated with a reference-graph builder, but judgment calls remain |
| **FLOW-5** Transient not canonical without promotion | Requires tracing knowledge content back to its origin | Could be partially automated with `git blame` + frontmatter analysis |
| **GUARD-1** Child does not redefine layers | Requires semantic comparison of layer definitions across documents | Could be partially automated by hashing key sections, but false positives likely |
| **GUARD-3** Child does not redefine flows | Requires semantic comparison of flow tables | Same as GUARD-1 |
| **GUARD-4** Child scope stays within guardrails | Requires understanding what a child *implemented* versus what it was *allowed* to implement | Unlikely to be fully automatable; keep as review checklist item |
| **GUARD-5** Conflict documented before deviation | Requires checking GitHub issue comments for amendment proposals | Automatable with `gh` API but requires NLP to classify comments |
| **ID-6** Path-only identity leakage | Requires comparing documents at different paths to determine if they are the same content | Automatable when a `doc_key` lookup service exists (#2136) |

### How manual checks should be performed

Manual checks should be included in the **weekly ecosystem execution and intelligence review** (#2089) as checklist items. The reviewer (human or orchestrator agent) should:

1. Sample 3-5 artifacts per check category
2. Apply the check criteria from Section 5
3. Record pass/fail per sample in the review output
4. Create follow-up issues for any failures found

This sampling approach is sustainable — exhaustive manual review of 19K+ wiki pages is not.

---

## 9. Anti-Patterns and Failure Modes

### 9.1 Anti-patterns in conformance checking itself

These are failure modes for the conformance-check *system*, not for the pyramid it validates:

| # | Anti-pattern | Description | Why harmful | Mitigation |
|---|---|---|---|---|
| CF-1 | **Check-as-governance** | Treating a passing conformance check as proof that the ecosystem is healthy | Checks validate specific signals, not holistic health. A system can pass all automated checks while having deep structural problems that only manual review catches. | Always pair automated checks with manual review sampling. Never claim "all checks pass = fully conformant." |
| CF-2 | **Check proliferation** | Adding checks for every conceivable violation without prioritization | Creates alert fatigue. Developers and agents ignore a wall of warnings. Failed checks lose their signal value. | Maintain the priority tiers from Section 6. Only promote a check to automated enforcement when it has demonstrated value through manual detection first. |
| CF-3 | **Check-as-enforcement** | Blocking commits or merges on conformance checks before the checks are proven reliable | False positives in new checks will block legitimate work and erode trust. | Start all checks as reporting-only. Promote to blocking (pre-commit or CI gate) only after at least 30 days of reporting with < 5% false positive rate. |
| CF-4 | **Checking the checker** | Defining conformance checks for the conformance-check system itself, creating recursive validation | Meta-checks consume effort without improving the system they validate. | This document is the design specification. The checks validate the *pyramid*, not the check system. Periodic manual review of check effectiveness replaces meta-checks. |
| CF-5 | **Stale check targets** | A check references a file path or field name that has been renamed or removed | The check passes vacuously (there's nothing to fail on) or fails spuriously (can't find the target). | Each check should verify its inputs exist before running. Missing inputs are a distinct error class ("check target missing"), not a pass. |
| CF-6 | **Scope creep into implementation** | The conformance-check design drifts into implementing the checks, defining registry schemas, or building CI pipelines | Violates the boundary between #2206 (validation design) and implementation issues. | This document defines checks and signals. Actual scripts, schemas, and CI hooks are follow-on work. |

### 9.2 Anti-patterns the checks are designed to detect

These are the pyramid violations that the check matrix targets, organized by the parent/sibling rule they violate:

| # | Anti-pattern | Source rule | Detection checks |
|---|---|---|---|
| AP-1 | Issue as knowledge base | #2205 Section 5, #2209 AP-1 | FLOW-2, DT-7 |
| AP-2 | Transient artifact becoming canonical | #2205 Section 5, #2209 AP-5 | FLOW-5, DT-6, OWN-3 |
| AP-3 | Path-only identity creating duplicate truth | #2205 Section 5, #2207 Section 8.2 | ID-6, ID-1, ID-3 |
| AP-4 | L3 reparsing raw documents when L2 evidence exists | #2205 Section 5, #2207 Section 8.1 | FLOW-1 |
| AP-5 | Entry-point docs inventing provenance facts | #2205 Section 5 | FLOW-3 |
| AP-6 | Circular flows between layers | #2205 Section 5 | FLOW-4 |
| AP-7 | Wiki pages outranking provenance | #2207 Section 8.4 | ID-4, DT-1 |
| AP-8 | Silent promotion (no frontmatter update) | #2209 GR-4, AP-5 | DT-6, DT-1 |
| AP-9 | Recurring-output accumulation without pruning | #2209 AP-7 | DT-5 |
| AP-10 | Plan treated as living specification after issue closure | #2209 AP-8 | OWN-4 |
| AP-11 | Child issue redefining parent contracts | #2205 Section 10 | GUARD-1 through GUARD-5 |
| AP-12 | Registry entries with narrative synthesis | #2205 Section 2 (L2 ownership) | OWN-2 |

---

## 10. Recommended Implementation Sequence

### Phase 1: Foundation (standalone scripts, reporting only)

| Order | Work item | Checks covered | Effort | Depends on |
|---|---|---|---|---|
| 1.1 | Build wiki-frontmatter linter | DT-1 | Small | Nothing — wiki pages exist today |
| 1.2 | Build cross-link validator | ACC-3, ACC-4, ACC-5 | Small | Nothing — parent and child docs exist today |
| 1.3 | Build misplaced-artifact detector | OWN-3 | Small | Nothing — directory scan |
| 1.4 | Build docs-README link checker | ACC-1, ACC-2 | Small | Nothing — single-file check |
| 1.5 | Build identity-field validator for index.jsonl | ID-1, ID-2, ID-3 | Medium | Nothing — `index.jsonl` exists |
| 1.6 | Build retention-compliance checker | DT-2, DT-4, DT-5 | Small | Nothing — file dates |

**Phase 1 outcome:** A set of standalone scripts that can be run manually or during weekly review. Each script reads existing repo files and emits a pass/fail report. No CI integration, no commit blocking.

### Phase 2: Integration with weekly review

| Order | Work item | Checks covered | Effort | Depends on |
|---|---|---|---|---|
| 2.1 | Integrate Phase 1 scripts into weekly review workflow | All Phase 1 checks | Small | Phase 1 complete, #2089 weekly review process |
| 2.2 | Build weekly-checklist file-existence runner | ACC-6 | Small | #2096 checklist finalized |
| 2.3 | Build execution-state keyword scanner for wikis | OWN-1 | Small | Phase 1.1 (wiki linter infrastructure) |
| 2.4 | Build issue-reference pattern checker | FLOW-2, DT-7 | Medium | Nothing, but benefits from closed-issue list cache |
| 2.5 | Build `.planning/` retention checker with issue-state lookup | DT-3 | Medium | GitHub API access (`gh` CLI) |

**Phase 2 outcome:** Conformance checks are part of the weekly review process. The weekly review output includes a conformance-check section with pass/fail results. Failures create follow-up issues.

### Phase 3: Selective enforcement

| Order | Work item | Checks covered | Effort | Depends on |
|---|---|---|---|---|
| 3.1 | Promote wiki-frontmatter check to pre-commit (new wiki pages only) | DT-1 (subset) | Small | Phase 1.1 proven reliable (< 5% false positive rate) |
| 3.2 | Promote misplaced-artifact check to pre-commit | OWN-3 | Small | Phase 1.3 proven reliable |
| 3.3 | Add label/doc consistency check to plan-gated workflow | OWN-4, DT-3 | Medium | Phase 2.5, plan-gate workflow (#1839) |
| 3.4 | Add promoted-artifact backlink check | ID-5 | Medium | `digitalmodel/` repo access, #2207 implementation |

**Phase 3 outcome:** Highest-value checks block violations at commit time. Other checks remain as weekly-review reporting.

### Phase 4: Future (depends on sibling issue implementation)

| Order | Work item | Checks covered | Effort | Depends on |
|---|---|---|---|---|
| 4.1 | Build reuse-vs-reparse audit from ingest logs | FLOW-1 | Medium | `llm_wiki.py` structured logging (#2034) |
| 4.2 | Build artifact-to-layer registry lookup | OWN-5 | Large | Machine-readable artifact registry (#2136) |
| 4.3 | Build `doc_key`-based cross-machine identity check | ID-6 | Large | `doc_key` lookup service (#2136) |
| 4.4 | Build child-guardrail semantic analyzer | GUARD-1 through GUARD-4 | Large | NLP or structured section hashing |

**Phase 4 outcome:** Full conformance automation. Most checks run automatically; only GUARD-4 and FLOW-3 remain permanently manual.

---

## 11. Open Questions / Residual Risks

1. **False positive rate for keyword-based checks.** Checks like OWN-1 (wiki page is not tracker) rely on keyword detection (`TODO:`, `IN-PROGRESS:`). Legitimate wiki pages may use these keywords in educational contexts (e.g., "the TODO pattern in software engineering"). Mitigation: start as reporting-only and tune keyword lists based on actual false positive rates before promoting to enforcement.

2. **Wiki page volume and linter performance.** The marine-engineering wiki has ~19K pages. A frontmatter linter (DT-1) must process all of them efficiently. Risk: linter runs take too long for pre-commit hooks. Mitigation: pre-commit hooks should only check *changed* files; full-repo scans run during weekly review.

3. **Cross-repo check boundaries.** Check ID-5 (promoted artifact has backlink) requires reading `digitalmodel/` files, which is a separate git repo. The conformance-check system must either operate across repos or accept that cross-repo checks are always manual. Mitigation: for Phase 1-2, treat cross-repo checks as manual weekly-review items. Phase 3+ may add `digitalmodel/` as a submodule or use a cross-repo script.

4. **Retention enforcement vs retention advisory.** #2209 defines retention periods, but this document only *detects* violations — it does not *enforce* retention by deleting expired files. Deletion is a separate concern and should not be coupled with conformance checking. Risk: retention checks report violations indefinitely without anyone acting on them. Mitigation: retention check failures should auto-create cleanup issues.

5. **Check target stability.** Several checks reference specific file paths (e.g., `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`). If these files are renamed, checks will fail spuriously. Mitigation: checks should emit a distinct "target missing" error (not a conformance failure) when their input files are absent.

6. **Manual check sustainability.** The 10 manual checks in Section 8 are designed for the weekly review. If the weekly review is skipped or abbreviated, manual checks go unperformed. Risk: drift accumulates undetected during review gaps. Mitigation: the highest-value manual checks should be candidates for eventual automation (noted in the "When it might become automatable" column).

7. **Interaction with existing cross-review gate.** The repo already has a cross-review gate (`scripts/review/`) and pre-push hook. Conformance checks should complement, not duplicate, existing review infrastructure. The cross-review gate validates plan/review artifacts; conformance checks validate pyramid rules. They have different scope but may share reporting infrastructure.

8. **Conformance check freshness.** This design document reflects the pyramid model as of 2026-04-11. If the parent operating model (#2205) is amended, the conformance checks must be updated to match. Risk: the check design drifts from the parent model. Mitigation: any amendment to #2205 should trigger a review of this document's check definitions.

9. **Dependency on sibling issue completion for Phase 4.** Checks FLOW-1, OWN-5, ID-6, and GUARD-1-4 depend on tooling from #2034, #2136, or NLP capabilities that may not arrive soon. Risk: Phase 4 remains perpetually "future." Mitigation: accept that some checks are permanently manual and focus implementation effort on Phases 1-3.

10. **Unified check runner vs separate scripts.** Phase 1 proposes separate scripts per check category. As checks accumulate, a unified runner with structured output (JSON/YAML report) would be more maintainable. Mitigation: define a common output format from Phase 1 so scripts can be composed later. Recommend: each script exits 0 (pass) or 1 (fail) and emits a single-line JSON result.

---

## Appendix A: Check-to-Source Traceability

Every check defined in Section 5 traces to a specific rule in the parent or sibling contracts:

| Check ID | Source document | Source section | Rule summary |
|---|---|---|---|
| OWN-1 | #2205, #2209 | #2205 S2, #2209 AP-4 | Wikis must not track execution state |
| OWN-2 | #2205 | S2 (L2 ownership) | Registries must not contain narrative |
| OWN-3 | #2209 | S5.2, S6.7 of #2096 | Session artifacts do not belong in normative directories |
| OWN-4 | #2209 | AP-8 | Plans are not living specifications |
| OWN-5 | #2205 | S2 (ownership invariant) | Every artifact belongs to one layer |
| ID-1 | #2207 | S3.2, S4.1 | Registry entries must have `doc_key` |
| ID-2 | #2207 | S3.2 | No duplicate `doc_key` with conflicting metadata |
| ID-3 | #2207 | S3.2, S8.5 | Consistent prefix handling |
| ID-4 | #2207 | S6.3, S8.4 | Wiki pages must cite sources by `doc_key` |
| ID-5 | #2207 | S8.3 | Promoted artifacts must have source backlinks |
| ID-6 | #2205, #2207 | #2205 S3, #2207 S8.2 | No path-only identity creating duplicates |
| FLOW-1 | #2205, #2207 | #2205 S5, #2207 S8.1 | L3 must not reparse when L2 evidence exists |
| FLOW-2 | #2205, #2209 | #2205 S5, #2209 AP-1 | Issues are not the durable knowledge base |
| FLOW-3 | #2205 | S5 | Entry-point docs must not invent provenance |
| FLOW-4 | #2205 | S5 | No circular flow between layers |
| FLOW-5 | #2205, #2209 | #2205 S5, #2209 GR-1/AP-5 | Transient must not become canonical without promotion |
| DT-1 | #2209 | GR-1, GR-4 | Wiki frontmatter must have source traceability |
| DT-2 | #2209 | S8.1 | Handoff retention: 30 days |
| DT-3 | #2209 | S8.1 | Planning artifact retention: issue + 14 days |
| DT-4 | #2209 | S8.1 | Session signal retention: 7 days |
| DT-5 | #2209 | S8.1 | Review result retention: 90 days |
| DT-6 | #2209 | GR-4, AP-5 | No silent promotion (frontmatter must update) |
| DT-7 | #2209 | AP-1 | Issue content is not domain knowledge |
| ACC-1 | #2096 | S6.1 | docs/README.md must link to intelligence |
| ACC-2 | #2096 | S6.3 | docs/document-intelligence/ needs an index |
| ACC-3 | #2205, #2096 | #2205 S11, #2096 S5.3 | Child artifacts must backlink parent |
| ACC-4 | #2205 | S11 | Parent must list child artifacts |
| ACC-5 | #2096 | S6.4 | Wiki CLAUDE.md must reference governing architecture |
| ACC-6 | #2096 | S7 | Weekly checklist file targets must exist |
| GUARD-1 | #2205 | S10 | Child must not redefine layers |
| GUARD-2 | #2205, #2207 | #2205 S10, #2207 S3 | Child must not redefine `doc_key` |
| GUARD-3 | #2205 | S10 | Child must not redefine flows |
| GUARD-4 | #2205 | S10 | Child scope within guardrails |
| GUARD-5 | #2205 | S10 | Deviations documented before acting |

## Appendix B: Glossary

| Term | Definition |
|---|---|
| **Conformance check** | A defined validation rule with inputs, logic, and a pass/fail signal that verifies an artifact or relationship conforms to a pyramid rule |
| **Automatable check** | A check that can be implemented as a script reading existing repo files and producing a binary pass/fail result |
| **Manual check** | A check requiring human or agent judgment that cannot be reduced to file inspection |
| **Checkable now** | All inputs for the check exist in the repo today |
| **Requires future tooling** | The check depends on artifacts, schemas, or pipelines that sibling issues have not yet implemented |
| **Reporting mode** | A check runs and emits results but does not block any workflow |
| **Enforcement mode** | A check blocks a workflow (commit, merge, push) when it fails |
| **Check target** | The file, field, or artifact that a check inspects |
| **Conformance target class** | A family of related checks that validate the same aspect of the pyramid (e.g., layer ownership, document identity) |
