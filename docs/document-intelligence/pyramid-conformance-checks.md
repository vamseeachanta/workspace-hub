# Pyramid Conformance Checks — Validation Design

> **Issue:** [#2206](https://github.com/vamseeachanta/workspace-hub/issues/2206)
> **Parent:** [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) — LLM-Wiki + Resource/Document Intelligence Operating Model
> **Siblings:** [#2207](https://github.com/vamseeachanta/workspace-hub/issues/2207) (provenance contract), [#2209](https://github.com/vamseeachanta/workspace-hub/issues/2209) (durable/transient boundary), [#2096](https://github.com/vamseeachanta/workspace-hub/issues/2096) (accessibility map)
> **Status:** Normative — approved conformance-check design for the single-source-of-truth pyramid
> **Date:** 2026-04-11 (revised 2026-04-19)
> **Scope:** Validation design only. Implementation of scripts, CI hooks, and registry changes is delegated to follow-on issues.
> **2026-04-19 revision:** Applies parent #2205 amendments (Sections 2 worked examples + forbidden inventions, 3 identity namespace + status vocabulary + `merged_at` rename, 8.1 L3 frontmatter schema authority) and addresses the 14 findings from the 2026-04-17 cross-provider adversarial review. See Section 12 for revision history.

---

## 1. Purpose and Scope

### What this document defines

This is the **conformance-check design** for the workspace-hub intelligence ecosystem's single-source-of-truth pyramid. It establishes:

- Concrete validation rules derived from the approved parent operating model (#2205) and its child contracts (#2207, #2209, #2096)
- A candidate checks matrix with pass/fail signals for each rule, including an explicit target-precondition for every automatable check
- Classification of each check as automatable (from existing repo state) or manual
- Priority ordering for which checks to implement first
- Anti-patterns and failure modes that conformance checks should detect
- Recommended implementation sequence for building the checks, including two integration modes (hook-mode vs pre-commit/CLI-mode) that match existing harness surfaces

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
| **The per-wiki frontmatter schema** (authority delegated to per-wiki `CLAUDE.md` by #2205 Section 8.1) | `knowledge/wikis/<domain>/CLAUDE.md` |

This document is a **validation design** — it defines what to check and how to recognize pass/fail. It does not contain executable scripts, CI pipeline definitions, or linter implementations.

### Design vs implementation distinction

Throughout this document:
- **"Check"** means a defined validation rule with inputs, logic, and a pass/fail signal
- **"Automatable"** means the check can be implemented as a script that reads existing repo files and produces a binary pass/fail result
- **"Manual"** means the check requires human or agent judgment that cannot be reduced to file inspection
- **"Checkable now"** means all inputs for the check already exist in the repo today
- **"Requires future tooling"** means the check depends on artifacts, schemas, or pipelines that sibling issues have not yet implemented
- **"Target precondition"** means the file or directory the check must inspect; when a precondition is not met the check emits a distinct `target-missing` signal rather than a conformance failure

---

## 2. Relationship to Parent Operating Model (#2205)

This document inherits from the [parent operating model](llm-wiki-resource-doc-intelligence-operating-model.md) (amended 2026-04-19) and operates under its constraints:

| Parent rule | How this design applies it |
|---|---|
| **Single-source-of-truth pyramid** (Section 2) | Checks validate that artifacts are assigned to exactly one layer using the layer definitions and worked examples from Section 2 |
| **Ownership invariant + most-durable-owner rule** (Section 2) | Checks detect artifacts that serve two layers or are misassigned |
| **Forbidden inventions** (Section 2) | GUARD-1 detects the explicit patterns the parent forbids: `"between L<n> and L<m>"`, `"L<n>-adjacent"`, `"hybrid layer"` |
| **`doc_key` rule + identity namespace** (Section 3) | Identity-namespace check validates `<algorithm>:<hex>` form and permitted prefixes (`sha256:` canonical, `md5:` legacy reads-only) |
| **Status vocabulary** (Section 3) | Status-vocabulary check validates that `status` values fall within the normative superset `gap \| indexed \| summarized \| extracted \| promoted \| superseded \| unreachable` |
| **`merged_at` rename** (Section 3) | `merged_at` migration check detects post-amendment writes still using legacy `discovered` field |
| **Allowed information flows** (Section 4) | Checks validate that cross-layer references follow permitted directions |
| **Forbidden information flows** (Section 5) | Checks detect anti-pattern flows (L3 reparsing, issues as knowledge base, etc.) |
| **Named exceptions** (Section 6) | Checks permit audit reads across layers without flagging |
| **Cross-machine access model** (Section 7) | Checks validate that cached artifacts do not silently become canonical |
| **Unified artifact registry** (Section 8) | Checks validate `doc_key` convergence across existing identity fields |
| **L3 frontmatter schema authority** (Section 8.1) | FRONT-1 validates that every wiki `CLAUDE.md` declares the parent-mandated baseline floor as required; DT-1 defers the per-page required-set to the relevant wiki `CLAUDE.md` |
| **Child issue guardrails** (Section 10) | Checks detect when child artifacts redefine parent-level contracts |
| **Discoverability** (Section 11) | Checks validate that cross-links exist between parent and child artifacts |

### Conflict resolution

If a conformance check is found to conflict with the parent operating model, the parent takes precedence. The check must be amended or retired — the parent model is never adjusted to accommodate a check.

---

## 3. Relationship to Sibling Child Artifacts (#2207, #2209, #2096)

Each sibling artifact contributes specific rules that this conformance design validates. Per #2205 Section 8.1, when a child required-set conflicts with another child's required-set for L3 page frontmatter, the authoritative source is the per-wiki `CLAUDE.md`, not the child contract text. Children may declare *additional* fields on top of the baseline floor for pages they govern.

### #2207 — Standards/Codes Provenance + Reuse Contract

| Rule from #2207 | Conformance check class |
|---|---|
| `doc_key` is `<algorithm>:<hex>` per #2205 Section 3 (Section 3.1 of #2207) | Identity consistency + identity-namespace checks |
| All registry entries must reference `doc_key` (Section 3.2) | Identity field presence checks |
| Reuse-vs-reparse decision tree requires artifact existence (Section 5.1) | Artifact-existence guard checks |
| Anti-patterns: duplicate parsing, path-only identity, broken lineage, wiki outranking provenance, prefix inconsistency (Section 8) | Anti-pattern detection checks |

### #2209 — Durable-vs-Transient Knowledge Boundary

| Rule from #2209 | Conformance check class |
|---|---|
| Hard classification rules: wikis are L3, registries are L2, issues are L5, handoffs are L6 (Section 5.2) | Layer assignment checks |
| Forbidden bridge directions (Section 6.2) | Flow direction checks |
| Promotion requires explicit frontmatter update (Guardrail GR-4) | Promotion traceability checks |
| Wiki pages must have source traceability — fields delegated to the per-wiki `CLAUDE.md` authority per #2205 Section 8.1 | Wiki frontmatter checks (DT-1 + FRONT-1) |
| Transient artifacts in normative directories (Anti-pattern related) | Misplaced artifact checks |
| Retention schedule compliance (Section 8.1) — **advisory** pending cleanup tooling | Retention-advisory checks (conditional) |

### #2096 — Intelligence Accessibility Map

| Rule from #2096 | Conformance check class |
|---|---|
| `docs/README.md` must link to intelligence ecosystem (Section 6.1) | Entry-point link checks |
| `docs/document-intelligence/` needs an index (Section 6.3) | Directory index checks |
| Wiki domains must be reachable from `docs/` (Section 6.4) | Cross-tree link checks |
| No session handoffs in architecture directories (Section 6.7) | Misplaced artifact checks |
| Weekly accessibility checklist items (Section 7) | Accessibility regression checks — inputs must be git-tracked, not untracked working-tree |

### Non-overlap rule

This document does NOT redefine the rules above. It creates checks that validate them. If a rule needs changing, the change must happen in the owning sibling artifact (#2207, #2209, #2096, or the per-wiki `CLAUDE.md`), not in a conformance check definition.

---

## 4. Conformance Target Classes

The pyramid's rules group into six conformance target classes. Each class corresponds to a family of related checks.

### 4.1 Layer Ownership

**What it validates:** Every artifact in the intelligence ecosystem belongs to exactly one layer, and that assignment matches the layer's ownership definition and worked examples from #2205 Section 2.

**Parent rules consumed:**
- Ownership invariant: "Every artifact belongs to exactly one layer"
- Most-durable-owner rule: "Assign to the lowest-numbered layer whose ownership definition covers the artifact's primary purpose"
- Layer ownership table from #2205 Section 2 (L1–L6 with "Owns" and "Must NOT own" columns)
- Worked examples (Section 2 amendment 2026-04-19): normative architecture docs under `docs/document-intelligence/` are **L3** (not a new "adjacent" layer)
- Forbidden inventions (Section 2): `"between L<n> and L<m>"`, `"L<n>-adjacent"`, `"hybrid layer"` are explicit violations

**What violations look like:**
- A wiki page (`knowledge/wikis/`) that tracks execution state (TODO items, assigned-to fields)
- A registry entry (`data/document-index/`) that contains narrative synthesis
- A session handoff filed in an architecture directory (`docs/document-intelligence/`) — the architecture directory itself is L3 per the worked examples, but session handoffs are L6
- An issue plan (`docs/plans/`) treated as the living specification after issue closure
- Any child doc using a forbidden invention pattern

**Concrete examples from current repo:**
- #2096 Section 6.7 identified session handoff files inside `docs/document-intelligence/` — an L6 artifact in an L3 directory
- Pre-revision drafts of this document and #2209 both invented layer classifications (`"L3-adjacent"`, `"between L5 and L6"`) — resolved by the 2026-04-19 parent amendment

### 4.2 Document Identity Usage

**What it validates:** All references to source documents use content-based identity (`doc_key`) in the `<algorithm>:<hex>` form per #2205 Section 3, not path-only references that create competing identities.

**Parent rules consumed:**
- #2205 Section 3: "File paths are aliases. The same document may appear at multiple paths."
- #2205 Section 3 (amendment 2026-04-19): `<algorithm>:<hex>` namespace is normative; permitted prefixes are `sha256:` (canonical) and `md5:` (legacy `og_standards` reads only). Bare-hex without prefix is a warning-level violation.
- #2205 Section 3 (amendment 2026-04-19): `status` vocabulary superset and `merged_at` rename for provenance timestamps.
- #2207 Section 3.2: "All registry entries, summaries, promoted artifacts, and wiki-ready records must reference documents by `doc_key`"
- #2207 Section 8.2: Path-only identity anti-pattern

**What violations look like:**
- A registry entry whose `content_hash` is a bare hex string with no algorithm prefix
- A `md5:`-prefixed `content_hash` in a record whose `source` is not `og_standards` (warning)
- Two separate registry entries for the same document at different paths, without a shared `doc_key`
- A wiki page citing a source by path alone with no `doc_key` reference

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

**What it validates:** Artifact classification follows #2209's decision tree and hard rules, promotion happens through explicit auditable steps, and retention advisories are surfaced (but not hard-enforced until #2209 promotes retention from advisory to binding).

**Parent rules consumed:**
- #2209 Section 5.2: Hard classification rules (wikis=L3, registries=L2, issues=L5, handoffs=L6, etc.)
- #2209 Section 6.2: Forbidden bridge directions
- #2209 Section 7: Promotion criteria and process
- #2209 Section 8: Retention schedule — **advisory** per #2209 Section 11 item 1
- #2209 Section 9: Anti-patterns (AP-1 through AP-8) and guardrails (GR-1 through GR-6)
- #2205 Section 8.1: L3 frontmatter schema authority — per-wiki `CLAUDE.md` binds the required-set; parent-mandated baseline floor is `{title, last_updated, doc_key}`

**What violations look like:**
- A wiki `CLAUDE.md` omitting any baseline-floor field from its required-set (FRONT-1 violation)
- A wiki page missing a field its wiki `CLAUDE.md` declares required (DT-1 violation)
- A session handoff older than 30 days still in the working tree (retention advisory; not a hard-fail until #2209 promotes)
- A `.planning/` artifact in an issue-addressable subtree surviving more than 14 days after its issue closed (retention advisory)
- Content moved from a handoff directly into a wiki without source traceability (AP-5: silent promotion)

### 4.5 Accessibility/Discoverability Linkage

**What it validates:** Intelligence assets are reachable from standard entry points within the navigation-hop budget defined by #2096, and that the files referenced by accessibility navigation are **git-tracked** (not merely present in a local working tree).

**Parent rules consumed:**
- #2096 Section 5: Accessibility map table (discoverability ratings per asset)
- #2096 Section 6: Broken and weak accessibility patterns
- #2096 Section 7: Weekly accessibility checklist
- #2205 Section 11: Cross-link table (which artifacts should reference the parent model)

**What violations look like:**
- `docs/README.md` having zero links to `knowledge/wikis/`, `data/document-index/`, or `docs/document-intelligence/`
- A child artifact not linking back to the parent operating model
- The parent operating model not listing a child artifact in its cross-links table
- A wiki domain's `CLAUDE.md` not referencing the parent operating model
- A navigation doc advertising a path that is present in a local working tree but not git-tracked (the `knowledge/wikis/personal/wiki/index.md` defect class identified by the 2026-04-17 Codex review)

### 4.6 Issue Classification and Child Guardrails

**What it validates:** Child issues operate within the guardrails defined by #2205 Section 10, and their artifacts do not redefine parent-level contracts or invent layers forbidden by Section 2.

**Parent rules consumed:**
- #2205 Section 2: Forbidden inventions (the patterns GUARD-1 explicitly detects)
- #2205 Section 10: "May implement" and "Must NOT redefine" table for each child issue
- #2205 Section 10: Conflict resolution — child must document conflicts as comments on #2205 and wait for approval

**What violations look like:**
- A child doc using `"L3-adjacent"`, `"between L5 and L6"`, or `"hybrid layer"` terminology
- A #2207 artifact redefining the pyramid layer boundaries
- A #2209 artifact redefining the `doc_key` identity model
- Any child artifact silently changing parent-level terminology, adding layers, or altering flow rules without an amendment comment on #2205

---

## 5. Candidate Checks Matrix

Each check is defined with: name, purpose, whether it is manual or automatable, required inputs, pass/fail signal, and a **target precondition** that specifies what the check emits when its inputs are missing. The target-precondition column resolves the Section 13 item 5 brittleness observation: `target-missing` is emitted as a distinct signal (stderr + exit 2) rather than conflated with `fail`.

### 5.1 Layer Ownership Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal | Target precondition |
|---|---|---|---|---|---|---|---|
| OWN-1 | Wiki-page-is-not-tracker | Detect L3 wiki pages that contain execution-state language (TODO, assigned-to, in-progress) | Automatable (now) | `knowledge/wikis/*/wiki/**/*.md` | No wiki page body contains execution-tracking keywords (`TODO:`, `ASSIGNED:`, `IN-PROGRESS:`, `status:in-flight`) | Any wiki page contains execution-tracking keywords | If `knowledge/wikis/` is empty or missing, emit `target-missing` and exit 2 |
| OWN-2 | Registry-is-not-narrative | Detect L2 registry entries containing narrative synthesis | Automatable (now) | `data/document-index/*.yaml` | No registry entry contains paragraph-length prose in value fields | Registry entries contain explanatory text > 200 characters in a single value | If no `*.yaml` under `data/document-index/`, emit `target-missing` |
| OWN-3 | Transient-not-in-normative-dir | Detect L6 session artifacts in L3 normative directories | Automatable (now) | `docs/document-intelligence/`, `docs/standards/`, `docs/governance/` | No files matching `session-handoff-*`, `handoff-*` patterns in normative directories (the directories themselves are L3 per #2205 Section 2 worked examples) | Session/handoff files found in normative directories | If target directory missing, emit `target-missing` |
| OWN-4 | Plan-not-treated-as-spec | Detect references to closed-issue plan files as authoritative specifications | Automatable (partial) | `docs/**/*.md`, `knowledge/**/*.md`, closed issue list | No doc references a plan file for a closed issue as a specification source | Doc cites `docs/plans/YYYY-MM-DD-issue-NNN-*.md` for a closed issue as authoritative | If `gh` CLI unavailable, emit `target-missing` and skip |
| OWN-5 | Single-layer-assignment | Verify each artifact is assigned to exactly one layer | Manual | Full artifact inventory, layer definitions from #2205 | Each artifact maps to one and only one layer | An artifact serves two layers without being split | N/A — manual |

### 5.2 Document Identity Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal | Target precondition |
|---|---|---|---|---|---|---|---|
| ID-1 | Registry-has-doc-key | Verify registry entries include a content-based identity field | Automatable (now) | `data/document-index/index.jsonl` | Every record has a `content_hash` or `doc_key` field whose value matches `<algorithm>:<hex>` per #2205 Section 3 | Records exist without any content-based identity field | If `index.jsonl` missing, emit `target-missing` and exit 2 |
| ID-2 | No-duplicate-doc-keys | Detect duplicate `doc_key` entries with conflicting metadata | Automatable (now) | `data/document-index/index.jsonl` | No two records share the same `doc_key` with contradictory `source`, `status`, or path values (per-path provenance entries are not conflicts) | Duplicate `doc_key` with genuinely conflicting metadata | If `index.jsonl` missing, emit `target-missing` |
| ID-3 | Identity-namespace-conformance (**new/revised** per parent Section 3 amendment) | Validate that every identity value uses the `<algorithm>:<hex>` namespace with a permitted prefix | Automatable (now) | `data/document-index/index.jsonl`, shard files, summary filenames | Every identity value matches the regex `^(sha256|md5):[0-9a-f]+$`; `md5:` appears only on records where `source == "og_standards"`; bare-hex values emit warnings | An identity value uses an unknown prefix (e.g., `sha1:`), uses `md5:` outside `og_standards` (warning, not fail), or is bare-hex without prefix (warning) | If `index.jsonl` missing, emit `target-missing` |
| ID-4 | Wiki-cites-doc-key | Verify wiki pages that cite source documents include `doc_key` or a resolvable source reference | Automatable (now) | `knowledge/wikis/*/wiki/**/*.md` | Every wiki page with a `sources` (or wiki-CLAUDE-defined equivalent) frontmatter field includes at least one `doc_key` or content-identity reference | Wiki page cites sources by path alone without content-based identity | If wiki directory missing, emit `target-missing` |
| ID-5 | Promoted-artifact-has-backlink | Verify promoted code artifacts in sibling repos contain `doc_key` back-link comments | **Manual (cross-repo)** | External `digitalmodel/` checkout (separate git repo; verified by 2026-04-17 Codex review) | Promoted modules contain `# doc_key:` or equivalent comments | Promoted module has no source-document back-link | **Precondition:** `digitalmodel/` checkout must be present as a sibling directory with a clean tree. If absent, emit `target-missing`. ID-5 is **not** part of the local automatable surface; see Section 7.6 cross-repo invocation contract |
| ID-6 | Path-only-identity-leakage | Detect systems tracking the same document by path alone at different locations | Manual | Registry entries, path alias arrays | Each document tracked by path at multiple locations shares a single `doc_key` | Same document at two paths without a shared `doc_key` | N/A — manual |
| ID-7 | `merged_at` migration check (**new** per parent Section 3 amendment) | Detect post-2026-04-19 provenance writes still using the legacy `discovered` field | Automatable (now) | `data/document-index/index.jsonl` provenance entries + git blame of `scripts/data/document-index/provenance.py` | Provenance entries written after 2026-04-19 use `merged_at`; pre-amendment entries may use `discovered` (informational notice only, not a violation — backward compatibility is required) | A provenance entry whose `discovered` or `merged_at` timestamp is ≥ 2026-04-19T00:00:00Z and uses `discovered` rather than `merged_at` | If `index.jsonl` missing, emit `target-missing` |

### 5.3 Information-Flow Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal | Target precondition |
|---|---|---|---|---|---|---|---|
| FLOW-1 | No-L3-reparsing-with-L2-evidence | Detect wiki ingest reading raw files when summaries exist | Automatable (future) | `llm_wiki.py` ingest logs, `data/document-index/summaries/` | Wiki ingest checks for existing summary before reading raw file | Wiki ingest reads raw file for a `doc_key` that already has a summary | Requires #2034 structured logging; until then emit `precondition-not-met` |
| FLOW-2 | Issue-not-knowledge-base | Detect docs/code citing closed issues as domain knowledge source | Automatable (now) | `docs/**/*.md`, `knowledge/**/*.md` | References to closed issues point to promoted wiki pages, not to issue comments | Doc cites `#NNNN` (closed) as authoritative without a wiki page reference | If `gh` CLI unavailable for closed-issue lookup, emit `target-missing` |
| FLOW-3 | Entry-point-no-provenance-invention | Detect L4 entry-point docs asserting provenance facts not in L2 | Manual | `docs/document-intelligence/intelligence-accessibility-map.md`, `docs/document-intelligence/data-intelligence-map.md`, `docs/README.md` | Entry-point docs reference existing asset locations without inventing new provenance claims | Entry-point doc asserts document properties not backed by registry | N/A — manual |
| FLOW-4 | No-circular-layer-claims | Detect two artifacts each claiming the other as source of truth | Manual | Cross-layer reference analysis | Every source-of-truth claim is unidirectional | Artifact A cites B as source; artifact B cites A as source | N/A — manual |
| FLOW-5 | Transient-not-canonical-without-promotion | Detect transient artifacts treated as canonical without explicit promotion | Manual | Session handoffs, `.planning/` files, wiki pages | Every piece of domain knowledge in L3 has a traceable promotion path | Wiki page content appears to originate from a handoff or session note without promotion record | N/A — manual |
| FLOW-6 | Status-vocabulary-conformance (**new** per parent Section 3 amendment) | Validate that `status` values in registry records fall within the parent superset | Automatable (now) | `data/document-index/index.jsonl` | Every `status` value is one of `{gap, indexed, summarized, extracted, promoted, superseded, unreachable}`; children may use subsets | Record has a `status` value outside the superset | If `index.jsonl` missing, emit `target-missing` |

### 5.4 Durable/Transient Boundary Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal | Target precondition |
|---|---|---|---|---|---|---|---|
| FRONT-1 | Wiki-CLAUDE-declares-baseline-floor (**new** per parent Section 8.1) | Validate that every wiki `CLAUDE.md` declares `title`, `last_updated`, and `doc_key` as **required** for L3 page frontmatter | Automatable (now) | `knowledge/wikis/*/CLAUDE.md` | Each wiki `CLAUDE.md` frontmatter-schema section lists all three baseline-floor fields (`title`, `last_updated`, `doc_key`) with "required" marking (not "optional" / "recommended") | Any wiki `CLAUDE.md` omits a baseline-floor field OR downgrades one to "optional"/"recommended" | If `knowledge/wikis/*/CLAUDE.md` glob returns zero files, emit `target-missing` |
| DT-1 | Wiki-page-frontmatter-conformance (**revised** per parent Section 8.1 — DT-1 no longer hardcodes fields) | Verify each wiki page satisfies the required-set declared by the **relevant wiki `CLAUDE.md`** (the binding authority per parent Section 8.1), which must itself satisfy the baseline floor per FRONT-1 | Automatable (now) | `knowledge/wikis/<domain>/wiki/**/*.md`, `knowledge/wikis/<domain>/CLAUDE.md` | Every wiki page under `<domain>` satisfies the required-set declared by `<domain>/CLAUDE.md`. Auto-generated index files (`wiki/index.md`) may be scoped out if the wiki `CLAUDE.md` explicitly declares an index schema | Wiki page missing a field required by its wiki `CLAUDE.md` | If the wiki `CLAUDE.md` is missing OR doesn't satisfy FRONT-1, emit `target-missing` and skip DT-1 for that wiki |
| DT-2 | Handoff-retention-advisory (**revised** — uses embedded timestamps, marked advisory) | Surface session handoffs past 30-day advisory | Automatable (now), **advisory-only** | `docs/handoffs/*.md` — use **embedded frontmatter timestamp** or filename date, NOT `mtime` (per 2026-04-17 Codex Finding 6) | No handoff file whose embedded/filename date is older than 30 days | Handoff file whose embedded/filename date is > 30 days ago (advisory — per #2209 Section 11 item 1, retention is advisory pending cleanup tooling) | If `docs/handoffs/` missing, emit `target-missing` |
| DT-3 | Planning-artifact-retention-advisory (**revised** — scoped to issue-addressable subtrees) | Surface `.planning/` artifacts in **issue-addressable** subtrees surviving past issue closure + 14 days | Automatable (partial), **advisory-only** | `.planning/plan-approved/<issue-number>.md`, `.planning/issue-<number>/**` — explicitly **excluding** non-issue artifacts like `.planning/.continue-here.md`, `.planning/STATE.md`, `.planning/plan-approved/session.md` (per 2026-04-17 Codex Finding 2 + `.claude/hooks/plan-approval-gate.sh:4-8`) | No issue-addressable `.planning/` artifact exists for an issue closed > 14 days ago | Issue-addressable `.planning/` file references an issue closed > 14 days ago (advisory) | If `gh` CLI unavailable for issue state lookup, emit `target-missing` |
| DT-4 | Session-signal-retention-advisory | Surface `.claude/state/session-signals/` files older than 7 days | Automatable (now), **advisory-only** | `.claude/state/session-signals/` — use filename timestamp | No signal file whose filename timestamp is older than 7 days | Signal file older than 7 days (advisory) | If directory missing, emit `target-missing` |
| DT-5 | Review-result-retention-advisory (**revised** — uses embedded/filename timestamps) | Surface `scripts/review/results/` files older than 90 days | Automatable (now), **advisory-only** | `scripts/review/results/*.md` — use filename date prefix (e.g., `2026-04-17-...`) or embedded date, NOT `mtime` | No review result file whose embedded/filename date is older than 90 days | Review file older than 90 days (advisory) | If directory missing, emit `target-missing` |
| DT-6 | Silent-promotion-detection | Detect wiki page updates without corresponding frontmatter changes | Automatable (partial) | Git diff of `knowledge/wikis/*/wiki/**/*.md`, frontmatter `last_updated` | Every wiki page modification is accompanied by a `last_updated` change | Wiki page content changed but `last_updated` field unchanged | If git history unavailable, emit `target-missing` |
| DT-7 | No-issue-as-knowledge-base | Detect wiki or doc references to issues as durable domain knowledge | Automatable (now) | `knowledge/wikis/*/wiki/**/*.md`, `docs/**/*.md` | References to issues serve as provenance citations, not as the knowledge content itself | A wiki page's primary content is "see issue #NNNN" with no synthesized knowledge | If target directory missing, emit `target-missing` |

**Advisory-vs-enforceable note (resolves 2026-04-17 Claude Finding 3):** DT-2, DT-3, DT-4, and DT-5 are **advisory-only** as long as #2209 Section 11 item 1 classifies retention as advisory. Emitting them as advisories avoids the alert-fatigue failure mode (CF-2) while still surfacing the signal for human review during the weekly review (#2089). They are promoted to hard-fail when (a) the cleanup workflow ships and (b) #2209 promotes retention from advisory to enforceable. Until then, the checks emit `advisory` (not `fail`) in their structured output and do not block any workflow.

### 5.5 Accessibility/Discoverability Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal | Target precondition |
|---|---|---|---|---|---|---|---|
| ACC-1 | Docs-README-links-intelligence | Verify `docs/README.md` links to intelligence ecosystem | Automatable (now) | `docs/README.md` | File contains links to `knowledge/wikis/`, `docs/document-intelligence/`, and `data/document-index/` (or equivalent navigation paths) | No links to intelligence ecosystem from `docs/README.md` | If `docs/README.md` missing, emit `target-missing` |
| ACC-2 | Doc-intelligence-has-index | Verify `docs/document-intelligence/` has a navigable index | Automatable (now) | `docs/document-intelligence/README.md` or `INDEX.md` | Index file exists and is non-empty | No index file in `docs/document-intelligence/` | If directory missing, emit `target-missing` |
| ACC-3 | Child-artifact-backlinks-parent | Verify child artifacts link back to parent operating model | Automatable (now) | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`, `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`, `docs/document-intelligence/intelligence-accessibility-map.md`, this document | Each child doc contains a link to `llm-wiki-resource-doc-intelligence-operating-model.md` | Child artifact has no reference to the parent document | If child doc missing, emit `target-missing` per file |
| ACC-4 | Parent-lists-child-artifacts | Verify parent operating model cross-links table includes all child artifacts | Automatable (now) | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` Section 11 | Cross-links table lists all existing child artifacts with correct paths | Child artifact exists but is not listed in parent cross-links | If parent doc missing, emit `target-missing` |
| ACC-5 | Wiki-CLAUDE-md-references-parent | Verify wiki domain `CLAUDE.md` files reference the parent operating model | Automatable (now) | `knowledge/wikis/*/CLAUDE.md` | Each wiki `CLAUDE.md` contains a reference to the operating model or L3 scope | Wiki `CLAUDE.md` has no reference to governing architecture | If no wiki `CLAUDE.md` files found, emit `target-missing` |
| ACC-6 | Weekly-checklist-file-existence (**revised** — git-tracked precondition) | Verify all files referenced in the weekly accessibility checklist exist **and are git-tracked** | Automatable (now) | File paths from #2096 Section 7 checklist | All referenced files exist in the working tree AND appear in `git ls-files` output (catches the `knowledge/wikis/personal/wiki/index.md` untracked-but-advertised defect class identified by 2026-04-17 Codex Finding 5) | A file referenced in the weekly checklist is missing, empty, OR present locally but not git-tracked | If the source checklist file is missing, emit `target-missing`. If the navigation source contains header-text-vs-content drift (e.g., "25 links" in header but `total_cross_references: 15`), emit a second check via ACC-7 |
| ACC-7 | Navigation-counts-agree (**new** per 2026-04-17 Codex Finding 5) | Detect header-text-vs-content drift in navigation docs | Automatable (now) | `docs/document-intelligence/README.md`, `knowledge/wikis/cross-links.md` | Count claims in prose match the structured counters in the target file (e.g., `total_cross_references` field) | A navigation doc asserts a count that disagrees with the referenced file's own counter field | If target file missing, emit `target-missing` |

### 5.6 Child Guardrail Checks

| # | Check name | Purpose | Type | Inputs | Pass signal | Fail signal | Target precondition |
|---|---|---|---|---|---|---|---|
| GUARD-1 | Child-does-not-redefine-layers OR invent layer classifications (**strengthened** per parent Section 2 forbidden inventions) | Detect child artifacts that invent layer classifications forbidden by #2205 Section 2 | Automatable (now — regex-based) + Manual (semantic) | Child artifacts in `docs/document-intelligence/**`, `docs/governance/**`, `docs/assessments/**` | **Zero** occurrences of the regex patterns `\bL[0-9]+-adjacent\b`, `\bbetween L[0-9]+ and L[0-9]+\b`, `\bhybrid layer\b` in any child doc. AND manual review confirms no child contains a layer table that contradicts #2205 Section 2 | Any match of the forbidden-invention regexes, or a layer table contradicting the parent | If `docs/document-intelligence/` missing, emit `target-missing` |
| GUARD-2 | Child-does-not-redefine-doc-key | Detect child artifacts that define a `doc_key` rule different from #2205/#2207 | Automatable (now) | Child artifacts | Child docs use `doc_key` consistently with #2205 Section 3 definition (namespace `<algorithm>:<hex>`) | Child doc defines `doc_key` differently or introduces a competing identity concept | If target docs missing, emit `target-missing` |
| GUARD-3 | Child-does-not-redefine-flows | Detect child artifacts that add or remove permitted/forbidden flows | Manual | Child artifacts, #2205 Sections 4-5 | Child docs reference parent flow rules without adding new ones | Child doc permits a flow forbidden by #2205 or forbids a flow permitted by #2205 | N/A — manual |
| GUARD-4 | Child-scope-stays-within-guardrails | Verify each child artifact stays within its "May implement" scope | Manual | Child artifacts, #2205 Section 10 guardrail table | Child doc content matches its "May implement" column | Child doc implements something from another child's scope or from the parent's "Must NOT redefine" list | N/A — manual |
| GUARD-5 | Conflict-documented-before-deviation | Verify any parent-model deviation is documented as a comment on #2205 | Manual | GitHub issue #2205 comments, child artifacts | Any deviation from the parent model has a corresponding amendment proposal on #2205 | Child artifact deviates from parent without a documented conflict resolution | N/A — manual |

**GUARD-1 scoping note (prevents meta-match).** A naive regex over this document itself would match the forbidden patterns inside the rows above (the patterns are quoted as the thing GUARD-1 detects). The GUARD-1 implementation MUST skip matches that occur inside (a) backtick-delimited inline code, (b) fenced code blocks, (c) table cells that are themselves the pattern-definition rows of this document's Section 5.6 and Section 12 revision-history table, and (d) links/URLs. The scoping rule can be phrased as "match only free-running prose text, not quoted/formatted tokens." This document passes a correctly-scoped GUARD-1 because every remaining occurrence of `L3-adjacent`, `between L<n> and L<m>`, or `hybrid layer` is wrapped in quotes or backticks as a pattern citation.

### Check-count summary (revised)

| Category | Check count | Automatable now | Automatable partial/future | Manual |
|---|---|---|---|---|
| Layer ownership (OWN-*) | 5 | 3 | 1 (OWN-4) | 1 (OWN-5) |
| Document identity (ID-*) | 7 | 4 (ID-1, ID-2, ID-3, ID-7) | 0 | 3 (ID-4 automatable; ID-5 manual cross-repo; ID-6 manual) |
| Information flow (FLOW-*) | 6 | 2 (FLOW-2, FLOW-6) | 1 (FLOW-1 future) | 3 |
| Front/boundary (FRONT-1 + DT-*) | 8 | 6 (FRONT-1, DT-1, DT-2, DT-4, DT-5, DT-7) | 2 (DT-3 partial, DT-6 partial) | 0 |
| Accessibility (ACC-*) | 7 | 7 | 0 | 0 |
| Child guardrails (GUARD-*) | 5 | 2 (GUARD-1 regex, GUARD-2) | 0 | 3 |
| **Total** | **38** | **24 now** | **4 partial/future** | **10 manual** |

The revised matrix adds 5 new checks (FRONT-1, strengthened GUARD-1, ID-3 identity-namespace, FLOW-6 status-vocabulary, ID-7 `merged_at` migration) and ACC-7 (navigation-counts drift from Codex Finding 5), raising the total from 33 to 38 (one net: ID-3 is strengthened but was already counted).

---

## 6. Priority Checks to Implement First

Priority is determined by (a) severity of the violation they detect, (b) feasibility from current repo state, and (c) return on implementation effort. The revised priorities below reflect the 2026-04-19 amendments — in particular, FRONT-1 is promoted to P1 because it is the precondition for DT-1 working at all.

### Tier 1: Immediate value, automatable now

| Priority | Check | Why first |
|---|---|---|
| P1 | **FRONT-1** Wiki CLAUDE declares baseline floor | Precondition for DT-1. Five `CLAUDE.md` files to check; none currently declare `doc_key` as required (verified 2026-04-19). Surfaces the concrete amendment-driven migration work. |
| P2 | **GUARD-1** strengthened (forbidden-invention regex) | Catches the exact defect pattern resolved by the 2026-04-19 parent amendment in any future child. Cheap regex check, zero false-positive domain. |
| P3 | **DT-1** Wiki page frontmatter conformance (now deferring to wiki CLAUDE.md) | High volume (19K+ wiki pages); delegates the schema to the per-wiki authority so it no longer false-fails pages with legitimate per-wiki shapes. |
| P4 | **ACC-1** docs/README.md links intelligence | Single-file check with highest discoverability impact. |
| P5 | **OWN-3** Transient not in normative dir | Simple glob pattern. Already identified as a real violation. |
| P6 | **ID-1 + ID-3** Registry doc-key + namespace-conformance | Now correctly accepts `sha256:`/`md5:` prefixes, so it will run clean against shipped data (resolves Claude Finding 2). |
| P7 | **ID-7** `merged_at` migration check | Catches regressions on the 2026-04-19 rename. Backward-compatible (informational for pre-amendment records). |
| P8 | **FLOW-6** Status-vocabulary conformance | Regex-checks a single field against a fixed enum. Close to zero-cost. |
| P9 | **ACC-3** Child artifact backlinks parent | 4-file check; validates cross-reference chain. |
| P10 | **ACC-6** Weekly checklist file existence (git-tracked) | Runs #2096 Section 7 checklist; revised precondition catches local-untracked-but-advertised defect. |
| P11 | **ACC-7** Navigation counts agree | New in revision; catches the 15-vs-25 cross-link drift class Codex identified. |

### Tier 2: High value, requires moderate effort

| Priority | Check | Why second tier |
|---|---|---|
| P12 | **DT-2, DT-5** Retention advisories (embedded/filename timestamps) | Advisory-only; report into weekly review. Prevents unbounded accumulation without blocking. |
| P13 | **ID-2** No duplicate doc-keys | Requires `index.jsonl` streaming scan; useful for registry drift. |
| P14 | **OWN-1** Wiki page is not tracker | Keyword scanning; medium false-positive risk — keep reporting-only until tuned. |
| P15 | **DT-7** No issue as knowledge base | Pattern matching for issue references used as primary content. |

### Tier 3: Important but requires judgment or future tooling

| Priority | Check | Why third tier |
|---|---|---|
| P16 | **FLOW-1** No L3 reparsing with L2 evidence | Requires ingest pipeline instrumentation (#2034). |
| P17 | **ID-5** Promoted artifact has backlink | **Cross-repo** — see Section 7.6 invocation contract. Never local Phase 1. |
| P18 | **GUARD-3/4/5** Manual semantic guardrails | Not reducible to pattern matching. |
| P19 | **OWN-5** Single-layer assignment | Requires full artifact inventory. |

---

## 7. Feasible Automation Surfaces

### 7.1 Docs linters

**What:** Scripts that scan markdown files for structural conformance.

**Automatable checks:** FRONT-1, DT-1, OWN-1, OWN-3, ACC-1, ACC-2, ACC-3, ACC-5, DT-7, GUARD-1 (regex portion)

**Implementation approach:**
- A Python or shell script that reads markdown files and checks for:
  - Wiki `CLAUDE.md` baseline-floor declaration (FRONT-1): parse the "Frontmatter Schema" table and verify `title`, `last_updated`, `doc_key` are marked required
  - Per-wiki page frontmatter (DT-1): load the required-set from the wiki's `CLAUDE.md`, then verify each page under that wiki satisfies it
  - Execution-tracking keywords in wiki pages (OWN-1): regex scan
  - Session handoffs in normative directories (OWN-3): glob patterns
  - Intelligence links in `docs/README.md` (ACC-1): grep
  - Index file existence (ACC-2): file-existence check
  - Parent backlinks in child artifacts (ACC-3): grep
  - Wiki `CLAUDE.md` references (ACC-5): grep
  - Issue-as-knowledge-base pattern (DT-7): detect wiki pages where primary content is "see issue #NNNN"
  - Forbidden-invention patterns (GUARD-1 regex): three regexes over `docs/document-intelligence/**` and `docs/governance/**`

**Estimated effort:** Small-medium.

**Run context:** Can run as a standalone script, a pre-commit check, or a CI step. Recommend the two integration modes in Section 7.6.

### 7.2 Cross-link validators

**What:** Scripts that verify bidirectional references between parent and child documents.

**Automatable checks:** ACC-3, ACC-4, ACC-5, ACC-6, ACC-7

**Implementation approach:**
- Read the parent operating model's cross-links table (Section 11)
- For each listed artifact: verify the file exists, is git-tracked, and contains a back-reference to the parent
- For each child artifact: verify it appears in the parent's cross-links table
- For each file path in the weekly checklist (#2096 Section 7): verify the file exists AND is git-tracked (not merely in local working tree)
- For navigation docs that include count claims: verify the claims match the referenced file's own counter fields (ACC-7)

### 7.3 Artifact-ownership checks

**What:** Scripts that verify artifacts are in the correct directory for their layer assignment.

**Automatable checks:** OWN-3, DT-2, DT-3, DT-4, DT-5

**Implementation approach:**

Map directories to expected layer assignments per #2205 Section 2 worked examples (amendment 2026-04-19):
- `knowledge/wikis/*/wiki/` → L3 only
- `data/document-index/` → L2 only
- `docs/plans/` → L5 only
- `docs/handoffs/` → L6 only
- `.planning/` → L6 only
- `.claude/state/` → L6 only
- `docs/document-intelligence/` → **L3** (durable architectural knowledge per Section 2 worked examples — no longer "L3-adjacent"). May contain L3 child contracts and conformance designs; must not contain L6 session handoffs
- `scripts/review/results/` → L5 review evidence only

Verify no files in a directory violate its layer constraint. Retention checks use embedded frontmatter or filename-date timestamps (not `mtime`) and are **advisory-only** pending #2209 retention-tooling landing.

**Non-issue `.planning/` subtrees are explicitly scoped out** of DT-3 (per Codex Finding 2): `.planning/.continue-here.md`, `.planning/STATE.md`, `.planning/plan-approved/session.md`, and other non-issue files are governed by a separate rule (not defined here) rather than issue-closure + 14 days.

### 7.4 Label/doc consistency checks

**What:** Scripts that verify GitHub issue labels and states are consistent with their document artifacts.

**Automatable checks:** OWN-4, DT-3, GUARD-5

**Implementation approach:**
- Use `gh` CLI to query issue state and labels
- For each plan file in `docs/plans/`: check if the associated issue is open or closed
- For each **issue-addressable** `.planning/` artifact: check if the associated issue is still open
- For closed issues with `status:plan-approved`: verify deliverable documents exist at expected paths

**Not suitable for pre-commit hooks** (require network access and issue-state lookups). Suitable for weekly-review runs.

### 7.5 Identity consistency checks

**What:** Scripts that verify `doc_key` / content-identity usage across registry files.

**Automatable checks:** ID-1, ID-2, ID-3, ID-7, FLOW-6

**Implementation approach:**
- Stream `data/document-index/index.jsonl` (1M+ records)
- For each record: verify the identity field matches `^(sha256|md5):[0-9a-f]+$` (ID-3). Bare-hex emits a warning; unknown prefixes emit a failure
- For each record: verify the `status` value is in the normative superset (FLOW-6)
- For each provenance entry with `discovered`/`merged_at` timestamp ≥ 2026-04-19: verify field is named `merged_at` (ID-7). Pre-amendment entries are informational only
- Check for duplicate `doc_key` values with conflicting metadata (ID-2)

**Estimated effort:** Medium — streaming JSONL parse to avoid full-file load.

### 7.6 Runner contract — two integration modes (**new** per 2026-04-17 Codex Finding 3)

The repo already has two incompatible enforcement surfaces. Conformance-check scripts must declare which mode they support — one script may support one mode, the other, or both (dispatched by flag):

| Mode | Contract | Existing reference |
|---|---|---|
| **hook-mode** | Print JSON decision to stdout (`{"decision":"block","reason":"..."}`) AND `exit 0`. Never `exit 1` from a PreToolUse hook — the harness will hard-fail | `.claude/hooks/plan-approval-gate.sh:97-106` |
| **cli/pre-commit-mode** | Emit plain text or JSON lines to stderr; `exit 0` on pass, `exit 1` on fail, `exit 2` on `target-missing` | `scripts/enforcement/require-plan-approval.sh:92-109` |

Each script must document which mode it implements. A single 0/1 JSON contract for both surfaces is **not** specified — the two surfaces have different semantics. Composite runners (that invoke multiple check scripts) adapt the individual mode outputs to a unified weekly-review report.

### 7.7 Cross-repo invocation contract for ID-5 (**new** per 2026-04-17 Codex Finding 4)

ID-5 (promoted-artifact backlink) requires reading files from `digitalmodel/`, which is a **separate git repository** present as a sibling checkout — not a submodule of workspace-hub. The invocation contract:

1. **Sibling directory location.** The script MUST resolve `digitalmodel/` as a sibling of the workspace-hub repo root. If absent, emit `target-missing` and exit 2 (never fail ID-5 because a sibling repo is not checked out).
2. **Branch state.** The script MUST verify `digitalmodel/` is on its default branch (`main`) with a clean tree before running. A dirty or detached-HEAD state emits `target-missing` — checks against unknown branch state are meaningless.
3. **Ownership of failures.** A failure found in `digitalmodel/` is an issue **against `digitalmodel/`**, not against workspace-hub. The conformance check script must emit the finding with a `target-repo: digitalmodel` field so downstream tooling files follow-up issues in the correct repo.
4. **Never block workspace-hub commits on ID-5.** Cross-repo checks are weekly-review-only. They are never promoted to the workspace-hub pre-commit surface.

---

## 8. Checks That Are Intentionally Manual for Now

The following checks require human or agent judgment and are not automatable from static file inspection:

| Check | Why manual | When it might become automatable |
|---|---|---|
| **OWN-5** Single-layer assignment | Requires understanding an artifact's *purpose*, not just its location | When a machine-readable artifact-to-layer registry exists (#2136) |
| **FLOW-1** No L3 reparsing with L2 evidence | Requires runtime pipeline instrumentation | When `llm_wiki.py` ingest emits structured logs with reuse/reparse decisions (#2034) |
| **FLOW-3** Entry-point no provenance invention | Requires semantic analysis of what constitutes a "provenance fact" | Unlikely to be fully automatable; keep as review checklist item |
| **FLOW-4** No circular layer claims | Requires cross-document semantic analysis of source-of-truth claims | Could be partially automated with a reference-graph builder |
| **FLOW-5** Transient not canonical without promotion | Requires tracing knowledge content back to its origin | Could be partially automated with `git blame` + frontmatter analysis |
| **GUARD-1** (semantic portion) | Layer-table comparison beyond regex | Could be partially automated by hashing key sections |
| **GUARD-3** Child does not redefine flows | Requires semantic comparison of flow tables | Same as GUARD-1 |
| **GUARD-4** Child scope stays within guardrails | Requires understanding what a child *implemented* versus what it was *allowed* to implement | Unlikely to be fully automatable |
| **GUARD-5** Conflict documented before deviation | Requires checking GitHub issue comments for amendment proposals | Automatable with `gh` API but requires NLP to classify comments |
| **ID-5** Promoted artifact has backlink | Cross-repo check; requires `digitalmodel/` checkout invocation contract (Section 7.7) | Only partially — would remain manual weekly-review item |
| **ID-6** Path-only identity leakage | Requires comparing documents at different paths | Automatable when a `doc_key` lookup service exists (#2136) |

### How manual checks should be performed

Manual checks should be included in the **weekly ecosystem execution and intelligence review** (#2089) as checklist items. The reviewer should:

1. Sample 3-5 artifacts per check category
2. Apply the check criteria from Section 5
3. Record pass/fail per sample in the review output
4. Create follow-up issues for any failures found

---

## 9. Anti-Patterns and Failure Modes

### 9.1 Anti-patterns in conformance checking itself

| # | Anti-pattern | Description | Why harmful | Mitigation |
|---|---|---|---|---|
| CF-1 | **Check-as-governance** | Treating a passing conformance check as proof the ecosystem is healthy | Checks validate specific signals, not holistic health | Always pair automated checks with manual review sampling |
| CF-2 | **Check proliferation** | Adding checks for every conceivable violation without prioritization | Creates alert fatigue | Maintain priority tiers; promote to automated enforcement only after manual-review value demonstrated |
| CF-3 | **Check-as-blanket-enforcement** (**revised** per 2026-04-17 Claude Finding 7) | Applying a single enforcement-vs-reporting policy to all checks regardless of their false-positive profile | The harness already enforces immediately for binary checks (plan-approval gate). Forcing 30 days reporting for a binary check like GUARD-1 regex (which has near-zero false positive domain) is overly conservative. Conversely, shipping a heuristic check like OWN-1 keyword scan in enforcement mode on day 1 would erode trust | **Two-class policy:** (a) *Binary unambiguous* checks (GUARD-1 regex, GUARD-2 prefix check, ACC-3 backlink grep, FRONT-1 schema-table parse) may ship enforcement-first if they integrate via one of the Section 7.6 modes. (b) *Heuristic* checks (OWN-1 keyword scan, OWN-4 closed-issue citation, DT-6 silent-promotion detection) MUST ship reporting-only for at least 30 days with < 5% false-positive rate before promotion |
| CF-4 | **Checking the checker** | Recursive validation | Meta-checks consume effort | Periodic manual review of check effectiveness replaces meta-checks |
| CF-5 | **Stale check targets** | Check references a file/field that has been renamed/removed | Check passes vacuously or fails spuriously | Every check must declare a target precondition (Section 5 column); `target-missing` emits exit 2 (distinct from pass=0 / fail=1) |
| CF-6 | **Scope creep into implementation** | Drifting into scripts/registry/CI definitions | Violates the #2206 boundary | This document defines checks and signals only |
| CF-7 | **mtime-based retention** (**new** per 2026-04-17 Codex Finding 6) | Using filesystem modification time for retention checks | Rebase/sync churn resets mtime, corrupting retention signal | DT-2 and DT-5 use embedded frontmatter dates or filename date prefixes, never `mtime` |
| CF-8 | **Untracked-as-canonical** (**new** per 2026-04-17 Codex Finding 5) | A navigation doc advertises a file present in the local working tree but not git-tracked | The file resolves for the author but not for anyone else cloning the repo; masquerades as canonical | ACC-6 must check `git ls-files` membership, not merely file existence. ACC-7 (new) catches the related header-count-vs-content drift class |

### 9.2 Anti-patterns the checks are designed to detect

| # | Anti-pattern | Source rule | Detection checks |
|---|---|---|---|
| AP-1 | Issue as knowledge base | #2205 S5, #2209 AP-1 | FLOW-2, DT-7 |
| AP-2 | Transient artifact becoming canonical | #2205 S5, #2209 AP-5 | FLOW-5, DT-6, OWN-3 |
| AP-3 | Path-only identity creating duplicate truth | #2205 S5, #2207 S8.2 | ID-6, ID-1, ID-3 |
| AP-4 | L3 reparsing raw documents when L2 evidence exists | #2205 S5, #2207 S8.1 | FLOW-1 |
| AP-5 | Entry-point docs inventing provenance facts | #2205 S5 | FLOW-3 |
| AP-6 | Circular flows between layers | #2205 S5 | FLOW-4 |
| AP-7 | Wiki pages outranking provenance | #2207 S8.4 | ID-4, DT-1 (+ FRONT-1 as precondition) |
| AP-8 | Silent promotion (no frontmatter update) | #2209 GR-4, AP-5 | DT-6, DT-1 |
| AP-9 | Recurring-output accumulation without pruning | #2209 AP-7 | DT-5 (advisory) |
| AP-10 | Plan treated as living specification after issue closure | #2209 AP-8 | OWN-4 |
| AP-11 | Child issue redefining parent contracts | #2205 S10 | GUARD-1 through GUARD-5 |
| AP-12 | Registry entries with narrative synthesis | #2205 S2 (L2 ownership) | OWN-2 |
| AP-13 | Child invents forbidden layer classification (**new** per parent Section 2 amendment) | #2205 S2 forbidden inventions | GUARD-1 regex |
| AP-14 | Unknown status value in registry record (**new** per parent Section 3 amendment) | #2205 S3 status enum | FLOW-6 |
| AP-15 | Post-amendment provenance write uses legacy `discovered` field (**new** per parent Section 3 amendment) | #2205 S3 `merged_at` rename | ID-7 |
| AP-16 | Bare-hex identity value (**new** per parent Section 3 amendment) | #2205 S3 namespace | ID-3 |

---

## 10. Recommended Implementation Sequence

### Phase 1: Foundation (standalone scripts, reporting-only except where CF-3 binary-class applies)

| Order | Work item | Checks covered | Effort | Depends on | Mode |
|---|---|---|---|---|---|
| 1.1 | Build FRONT-1 wiki-CLAUDE-schema linter | FRONT-1 | Small | Nothing — 5 `CLAUDE.md` files | enforcement-first (binary) |
| 1.2 | Build GUARD-1 forbidden-invention regex scanner | GUARD-1 (regex) | Small | Nothing | enforcement-first (binary) |
| 1.3 | Build DT-1 wiki-page frontmatter linter (per-wiki authority) | DT-1 | Small | Phase 1.1 (FRONT-1 clean) | reporting-only initially |
| 1.4 | Build cross-link validator | ACC-3, ACC-4, ACC-5, ACC-7 | Small | Nothing | enforcement-first (binary) |
| 1.5 | Build misplaced-artifact detector | OWN-3 | Small | Nothing | enforcement-first (binary) |
| 1.6 | Build docs-README link checker | ACC-1, ACC-2 | Small | Nothing | enforcement-first (binary) |
| 1.7 | Build identity-namespace + status + merged_at validator for index.jsonl | ID-1, ID-2, ID-3, FLOW-6, ID-7 | Medium | Nothing | enforcement-first for new writes; informational for legacy |
| 1.8 | Build retention-advisory checker (embedded timestamps) | DT-2, DT-4, DT-5 | Small | Nothing | **advisory-only** pending #2209 |
| 1.9 | Build weekly-checklist file-existence + git-tracked checker | ACC-6 | Small | #2096 checklist finalized | enforcement-first (binary) |

**Phase 1 outcome:** Standalone scripts runnable manually or during weekly review. Binary checks may block via one of the Section 7.6 modes; heuristic/retention/advisory checks report into weekly review only.

### Phase 2: Integration with weekly review

| Order | Work item | Checks covered | Effort | Depends on |
|---|---|---|---|---|
| 2.1 | Integrate Phase 1 scripts into weekly review workflow | All Phase 1 checks | Small | Phase 1 complete, #2089 weekly review process |
| 2.2 | Build execution-state keyword scanner for wikis | OWN-1 | Small | Phase 1.3 |
| 2.3 | Build issue-reference pattern checker | FLOW-2, DT-7 | Medium | Closed-issue list cache |
| 2.4 | Build `.planning/` retention-advisory checker with issue-state lookup (issue-addressable subtrees only) | DT-3 | Medium | `gh` CLI |

### Phase 3: Selective enforcement promotion

| Order | Work item | Checks covered | Effort | Depends on |
|---|---|---|---|---|
| 3.1 | Promote heuristic checks to pre-commit after 30-day clean run | OWN-1, DT-6 | Small | 30-day reporting data |
| 3.2 | Add label/doc consistency check to a plan-gated workflow (decoupled from #1839 per 2026-04-17 Claude Finding 6 — define minimum interface) | OWN-4 | Medium | Minimum plan-gate interface definition |
| 3.3 | Promote retention checks from advisory to enforceable | DT-2, DT-3, DT-4, DT-5 | Medium | #2209 Section 11 item 1 promoted to enforceable + cleanup-tooling issue lands |

Phase 3.2 no longer depends hard on #1839. Instead, the conformance check integrates against whichever plan-gate implementation is available, using a minimum interface: "given a plan file path, return the associated issue number and its current state."

### Phase 4: Future (depends on sibling issue implementation)

| Order | Work item | Checks covered | Effort | Depends on |
|---|---|---|---|---|
| 4.1 | Build reuse-vs-reparse audit from ingest logs | FLOW-1 | Medium | `llm_wiki.py` structured logging (#2034) |
| 4.2 | Build artifact-to-layer registry lookup | OWN-5 | Large | #2136 |
| 4.3 | Build `doc_key`-based cross-machine identity check | ID-6 | Large | #2136 `doc_key` lookup service |
| 4.4 | Build cross-repo ID-5 runner per Section 7.7 invocation contract | ID-5 | Medium | `digitalmodel/` cross-repo contract finalized |
| 4.5 | Build child-guardrail semantic analyzer | GUARD-3, GUARD-4 (semantic portion) | Large | NLP or structured section hashing |

---

## 11. Open Questions / Residual Risks

1. **Wiki-CLAUDE migration cost.** FRONT-1 will fail on all five current wiki `CLAUDE.md` files because none currently declare `doc_key` as required (verified 2026-04-19). Migrating the five files to include `doc_key` in the required set is out of this issue's scope (see forbidden paths) but is a precondition for DT-1 to run cleanly. Mitigation: a follow-on issue or a scheduled amendment pass should update the five wiki `CLAUDE.md` files. Until then, FRONT-1 itself is valuable — it surfaces the gap that the amendment created.

2. **Retention advisory lifecycle.** DT-2/3/4/5 remain advisory-only until #2209 promotes retention from advisory to enforceable and the cleanup-tooling issue lands. If that never happens, retention advisories accumulate indefinitely in weekly-review output. Mitigation: an explicit retirement clause — if retention is not promoted within 6 months of this document, the advisories are retired rather than left in weekly-review noise.

3. **Wiki page volume and linter performance.** ~19K wiki pages. DT-1 must process efficiently. Risk: linter runs too long for pre-commit. Mitigation: pre-commit only checks *changed* files; full-repo scans run during weekly review.

4. **Cross-repo check boundaries.** Per Section 7.7, ID-5 operates cross-repo. Workspace-hub tooling must not block on it. For Phase 1-3, ID-5 is manual weekly-review only.

5. **Check target stability.** Every check in Section 5 now declares a target-precondition. The `target-missing` signal (exit 2, stderr report) is distinct from pass/fail. Composite runners must distinguish the three exit codes.

6. **Manual check sustainability.** 10 manual checks remain. If weekly review is skipped, manual checks go unperformed. Mitigation: the highest-value manual checks are candidates for eventual automation.

7. **Interaction with existing cross-review gate.** The repo has `scripts/review/` and a pre-push hook. Conformance checks complement, not duplicate. The cross-review gate validates plan/review artifacts; conformance checks validate pyramid rules.

8. **Conformance-check freshness.** This document is synchronized with the 2026-04-19 parent amendment. If the parent is amended again, this document's check definitions must be reviewed. Mitigation: any amendment to #2205 triggers a review of this document's Section 5.

9. **Phase 4 dependency risk.** Phase 4 depends on #2034, #2136, or NLP capabilities that may not arrive soon. Mitigation: accept that some checks are permanently manual; focus implementation on Phases 1-3.

10. **`md5:` legacy indefinitely.** #2205 Section 3 says `md5:` reads are permitted indefinitely with opportunistic upgrade. There is no sunset date. Risk: the legacy namespace persists forever. Mitigation: acceptable per parent contract — this is an explicit architectural decision, not a defect.

---

## 12. Revision History

| Date | Driver | Changes |
|---|---|---|
| 2026-04-11 | Initial delivery | 33 checks across 6 categories; initial priority tiers and implementation phases |
| 2026-04-19 | Parent amendment (#2205 Sections 2, 3, 8.1) + 2026-04-17 cross-provider adversarial review (14 findings) | Amendments A–H applied (see below); 5 new checks added (FRONT-1, strengthened GUARD-1, identity-namespace ID-3, status-vocabulary FLOW-6, `merged_at` ID-7) plus ACC-7 from Codex Finding 5. DT-1 reframed to defer to wiki `CLAUDE.md` authority. Retention checks reclassified as advisory. Section 7.3 `docs/document-intelligence/` reclassified as **L3** (not L3-adjacent). Runner contract split into hook-mode and pre-commit-mode (Section 7.6). Cross-repo invocation contract for ID-5 added (Section 7.7). Target-precondition column added to every automatable check. mtime-based retention removed in favor of embedded/filename timestamps. CF-3 split into binary-vs-heuristic policy. CF-7 and CF-8 added |

### Amendment-driver detail (2026-04-19)

| Amendment | Parent Section | Change here |
|---|---|---|
| A — Remove invented "L3-adjacent" | Section 2 worked examples | Section 7.3 directory-to-layer mapping now classifies `docs/document-intelligence/` as **L3**. All mentions of "L3-adjacent" removed. Section 4.1 updated. GUARD-1 would have flagged the prior wording — the self-contradiction is resolved |
| B — Strengthen GUARD-1 (forbidden inventions) | Section 2 | GUARD-1 now explicitly lists three regex patterns (`\bL[0-9]+-adjacent\b`, `\bbetween L[0-9]+ and L[0-9]+\b`, `\bhybrid layer\b`) and asserts zero occurrences in `docs/document-intelligence/**` and `docs/governance/**` |
| C — Add FRONT-1 (baseline floor) | Section 8.1 | New check FRONT-1 validates every wiki `CLAUDE.md` declares `title`, `last_updated`, `doc_key` as required |
| D — Reframe DT-1 (defer to wiki CLAUDE.md) | Section 8.1 | DT-1 no longer hardcodes `{title, tags, sources, last_updated}`. It now delegates the required-set to the relevant wiki `CLAUDE.md`. This resolves Claude Finding 1 and Codex Finding 1 (three live frontmatter shapes) |
| E — Identity-namespace check | Section 3 | ID-3 now validates `<algorithm>:<hex>` form with permitted prefixes (`sha256:` canonical, `md5:` legacy `og_standards` reads-only). Bare-hex emits warning; unknown prefixes fail. This resolves Claude Finding 2 (ID-1/ID-3 false-fail on 100% of shipped storage) |
| F — Status-vocabulary check | Section 3 | New FLOW-6 validates `status` values against the normative superset `gap \| indexed \| summarized \| extracted \| promoted \| superseded \| unreachable` |
| G — `merged_at` migration check | Section 3 | New ID-7 detects post-amendment provenance writes still using `discovered`. Pre-amendment writes are informational only (backward compatibility required) |
| H — Update cross-references | Various | Section 2 references point to the amended parent. Parent amendment comment referenced in the document header |

### Finding disposition (2026-04-17 cross-provider review)

| # | Finding | Severity | Disposition |
|---|---|---|---|
| Claude-1 | DT-1 frontmatter contradicts siblings | MAJOR | Fixed via Amendment D |
| Claude-2 | ID-1/ID-3 false-fail on 100% shipped storage | MAJOR | Fixed via Amendment E (namespace check accepts prefixed values) |
| Claude-3 | DT-2/3/4/5 retention contradicts advisory admission | MAJOR | Fixed: retention checks reclassified as advisory; promotion to enforceable gated on #2209 promoting its own policy |
| Claude-4 | Section 7.3 commits the GUARD-1 violation it detects | MAJOR | Fixed via Amendments A + B |
| Claude-5 | Section 5 hardcoded targets with no missing-input handling | MINOR | Fixed: `target precondition` column added to every automatable check matrix row; `target-missing` is exit 2 |
| Claude-6 | Phase 3.3 depends on OPEN #1839 | MINOR | Fixed: Phase 3.2 decoupled by defining a minimum plan-gate interface |
| Claude-7 | CF-3 collides with existing enforcement-first hooks | MINOR | Fixed: CF-3 split into binary-vs-heuristic two-class policy |
| Claude-8 | Cross-provider review absent | MAJOR (process) | Resolved: Codex review landed 2026-04-17 |
| Codex-1 | DT-1 false positives across 3+ live frontmatter shapes | MAJOR | Fixed via Amendment D (per-wiki authority) |
| Codex-2 | DT-3 assumes `.planning/` is issue-addressable | MAJOR | Fixed: DT-3 scope narrowed to `.planning/plan-approved/<issue>.md` and `.planning/issue-<number>/**`; non-issue artifacts explicitly out of scope |
| Codex-3 | Runner contract incompatible with both hook surfaces | MAJOR | Fixed: Section 7.6 defines two integration modes (hook-mode, cli/pre-commit-mode) |
| Codex-4 | ID-5 cross-repo dependency treated as local | MAJOR | Fixed: ID-5 reclassified as cross-repo manual; Section 7.7 defines invocation contract |
| Codex-5 | ACC-6 targets untracked files | MAJOR | Fixed: ACC-6 now requires git-tracked membership; ACC-7 added for header-vs-content count drift |
| Codex-6 | DT-2/DT-5 mtime-based retention unstable | MINOR | Fixed: DT-2/DT-5 now use embedded frontmatter or filename date prefixes, never `mtime`; codified as CF-7 anti-pattern |

---

## Appendix A: Check-to-Source Traceability

Every check defined in Section 5 traces to a specific rule in the parent or sibling contracts:

| Check ID | Source document | Source section | Rule summary |
|---|---|---|---|
| OWN-1 | #2205, #2209 | #2205 S2, #2209 AP-4 | Wikis must not track execution state |
| OWN-2 | #2205 | S2 (L2 ownership) | Registries must not contain narrative |
| OWN-3 | #2209, #2205 | #2205 S2 worked examples, #2096 S6.7 | Session artifacts do not belong in L3 normative directories |
| OWN-4 | #2209 | AP-8 | Plans are not living specifications |
| OWN-5 | #2205 | S2 ownership invariant | Every artifact belongs to one layer |
| ID-1 | #2207 | S3.2, S4.1 | Registry entries must have `doc_key` |
| ID-2 | #2207 | S3.2 | No duplicate `doc_key` with conflicting metadata |
| ID-3 | #2205, #2207 | #2205 S3 namespace amendment | `<algorithm>:<hex>` form with permitted prefixes |
| ID-4 | #2207 | S6.3, S8.4 | Wiki pages must cite sources by `doc_key` |
| ID-5 | #2207 | S8.3 | Promoted artifacts must have source backlinks (cross-repo) |
| ID-6 | #2205, #2207 | #2205 S3, #2207 S8.2 | No path-only identity creating duplicates |
| ID-7 | #2205 | S3 `merged_at` rename amendment | Post-amendment writes use `merged_at` |
| FLOW-1 | #2205, #2207 | #2205 S5, #2207 S8.1 | L3 must not reparse when L2 evidence exists |
| FLOW-2 | #2205, #2209 | #2205 S5, #2209 AP-1 | Issues are not the durable knowledge base |
| FLOW-3 | #2205 | S5 | Entry-point docs must not invent provenance |
| FLOW-4 | #2205 | S5 | No circular flow between layers |
| FLOW-5 | #2205, #2209 | #2205 S5, #2209 GR-1/AP-5 | Transient must not become canonical without promotion |
| FLOW-6 | #2205 | S3 status vocabulary amendment | `status` values must fall within the normative superset |
| FRONT-1 | #2205 | S8.1 | Each wiki `CLAUDE.md` declares baseline floor `{title, last_updated, doc_key}` as required |
| DT-1 | #2205, #2209 | #2205 S8.1, #2209 GR-1/GR-4 | Wiki pages satisfy the required-set declared by their wiki `CLAUDE.md` |
| DT-2 | #2209 | S8.1 | Handoff retention: 30 days (advisory) |
| DT-3 | #2209 | S8.1 | Planning-artifact retention in issue-addressable subtrees (advisory) |
| DT-4 | #2209 | S8.1 | Session signal retention: 7 days (advisory) |
| DT-5 | #2209 | S8.1 | Review result retention: 90 days (advisory) |
| DT-6 | #2209 | GR-4, AP-5 | No silent promotion |
| DT-7 | #2209 | AP-1 | Issue content is not domain knowledge |
| ACC-1 | #2096 | S6.1 | docs/README.md must link to intelligence |
| ACC-2 | #2096 | S6.3 | docs/document-intelligence/ needs an index |
| ACC-3 | #2205, #2096 | #2205 S11, #2096 S5.3 | Child artifacts must backlink parent |
| ACC-4 | #2205 | S11 | Parent must list child artifacts |
| ACC-5 | #2096 | S6.4 | Wiki `CLAUDE.md` must reference governing architecture |
| ACC-6 | #2096 | S7 | Weekly-checklist file targets must exist AND be git-tracked |
| ACC-7 | #2096 | S7 (drift-detection extension) | Navigation count claims agree with referenced file counters |
| GUARD-1 | #2205 | S2 forbidden inventions + S10 | Child must not invent layers or redefine layer model |
| GUARD-2 | #2205, #2207 | #2205 S3, #2207 S3 | Child must not redefine `doc_key` |
| GUARD-3 | #2205 | S10 | Child must not redefine flows |
| GUARD-4 | #2205 | S10 | Child scope within guardrails |
| GUARD-5 | #2205 | S10 | Deviations documented before acting |

## Appendix B: Glossary

| Term | Definition |
|---|---|
| **Conformance check** | A defined validation rule with inputs, logic, and a pass/fail signal that verifies an artifact or relationship conforms to a pyramid rule |
| **Automatable check** | A check that can be implemented as a script reading existing repo files and producing a binary pass/fail result |
| **Manual check** | A check requiring human or agent judgment |
| **Checkable now** | All inputs for the check exist in the repo today |
| **Requires future tooling** | The check depends on artifacts, schemas, or pipelines that sibling issues have not yet implemented |
| **Reporting mode** | A check runs and emits results but does not block any workflow |
| **Enforcement mode** | A check blocks a workflow (commit, merge, push) when it fails |
| **Advisory** | A check emits its signal into weekly review but never blocks and never causes a follow-up issue to auto-create |
| **Check target** | The file, field, or artifact that a check inspects |
| **Target precondition** | The condition under which a check can meaningfully run. When unmet, the check emits `target-missing` (exit 2) rather than `fail` |
| **Conformance target class** | A family of related checks that validate the same aspect of the pyramid |
| **hook-mode** | Script integration mode for PreToolUse hooks: JSON decision on stdout + exit 0 |
| **cli/pre-commit-mode** | Script integration mode for pre-commit and CLI: exit 0 pass / exit 1 fail / exit 2 target-missing |
| **Baseline floor** | The `{title, last_updated, doc_key}` required-set mandated by parent Section 8.1 on every wiki `CLAUDE.md` |
| **Binary check** | A check with near-zero false-positive domain (e.g., regex match on forbidden patterns). May ship enforcement-first |
| **Heuristic check** | A check with non-trivial false-positive risk (e.g., keyword scans). Must ship reporting-only for at least 30 days before enforcement |
