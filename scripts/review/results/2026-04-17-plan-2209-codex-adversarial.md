# Adversarial Review: #2209 Durable vs Transient Knowledge Boundary

> **Reviewer:** Codex (cross-provider second opinion per planning-skill Step 3)
> **Date:** 2026-04-17
> **Transcribed by:** Claude — Codex's sandbox blocked the local artifact write. Findings below are Codex's verbatim; Claude has spot-verified each load-bearing claim against live repo state and added one cross-finding (Addendum A) discovered during verification.
> **Deliverable under review:** `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
> **Sibling Claude review:** `scripts/review/results/2026-04-17-plan-2209-claude-adversarial.md`

## Stance declaration (Codex)

> "I reviewed this deliverable adversarially and assumed it was wrong until the repo proved otherwise. I did not treat cited sibling docs, examples, or prior reviews as trustworthy without checking the live repo surfaces they referenced."

## Verdict: **MAJOR** — 5 findings (4 MAJOR, 1 MINOR), none overlapping the Claude pass

---

## Codex Finding 1 — MAJOR: Boundary doc weakens wiki provenance below the sibling contract

**Claim under review:** Section 10.1 row 2 ("Wiki page frontmatter | `title`, `tags`, `sources`, `added`, `last_updated`") and Section 7.2 step 4 ("Wiki pages include frontmatter with `last_updated` and source references"). `promoted_from` is listed as optional.

**Evidence:** `docs/document-intelligence/standards-codes-provenance-reuse-contract.md:244-259` requires every wiki page created from a standards/codes document to carry `doc_key`, `source_ref`, `domain`, `promoted_from`, and `last_updated`. Live wiki pages such as `knowledge/wikis/engineering/wiki/entities/aqwa-solver.md:1` and `knowledge/wikis/engineering/wiki/concepts/fatigue-analysis-offshore.md:1` only contain `title`, `tags`, `sources`, `added`, `last_updated`.

**Why this is a defect:** #2209 says it complements rather than redefines #2207 (Section 3 non-overlap rule), but its implementation guidance normalizes a weaker schema and makes `promoted_from` optional where the sibling contract makes a fuller provenance block mandatory. That creates conflicting follow-on guidance for the same wiki layer.

**Required fix:** Align Section 7.2 and Section 10.1 to the #2207 provenance contract, or explicitly scope the lighter schema to non-standards pages and restate that #2207 fields remain mandatory wherever standards/codes promotion is involved.

**Claude verification (2026-04-17):** Confirmed at cited line numbers. See also Addendum A below — the live wiki has a *third* schema authority that differs from both contracts.

---

## Codex Finding 2 — MAJOR: The document does not actually classify the live `.planning` artifact classes it claims to cover

**Claim under review:** Section 1 ("It establishes ... A clear classification of every major artifact class"), Section 4.5 examples list, Section 5.2 hard rule ("A `.planning/` artifact | Always transient (L6)"), Section 8.1 retention table.

**Evidence:** The live repo has materially different `.planning` artifact types: `.planning/HANDOFF.json`, `.planning/quick/session-handoff-2026-04-15-plan-review-wave.md`, `.planning/research/2026-04-17-synthesis.md`, `.planning/archive/modules/dapper-stargazing-willow.md`, `.planning/plan-approved/1839.md`.

**Why this is a defect:** These committed subtrees do not share one role or one lifecycle. A paused workflow handoff JSON, a quick review prompt/output lane, research synthesis notes, archival modules, and approval markers are distinct artifact classes, but #2209 collapses them into one generic `.planning` bucket and only names discoveries/verified/plan-approved. The policy therefore misses active repo surfaces while claiming complete classification.

**Required fix:** Split `.planning` into explicit sub-classes (`HANDOFF.json`, `quick/`, `research/`, `archive/`, `plan-approved/`, and any other committed subtree), and assign owner/lifecycle/bridge rules for each rather than using one blanket `.planning` classification.

**Claude verification (2026-04-17):** All five paths spot-checked previously during planning-skill audit; the `.planning` tree is heterogeneous.

---

## Codex Finding 3 — MAJOR: The `.claude/state/session-signals` example is not a committed repo example

**Claim under review:** Section 4.5 examples ("`.claude/state/session-signals/2026-04-11.jsonl` — transient session telemetry") and Section 8.1 retention row ("Session signals (`.claude/state/session-signals/`) | 7 days | Delete").

**Evidence:** `docs/handoffs/session-2026-04-11-session-log-portability-exit.md:66-74` explicitly lists `.claude/state/session-signals/2026-04-11.jsonl` under "Unrelated dirty/untracked items remain and were intentionally left untouched". The same handoff shows committed `.claude/state` examples such as `.claude/state/corrections/*` (lines 68-71).

**Why this is a defect:** Section 4.5 presents `session-signals` as an in-repo example, but the repo's own handoff says that file was not committed. That makes the taxonomy look grounded in committed repo state when it is actually citing local transient residue.

**Required fix:** Replace the example with committed `.claude/state` artifacts that actually exist in the repo, or explicitly mark `session-signals` as local/untracked operational state outside the committed-artifact taxonomy.

---

## Codex Finding 4 — MAJOR: Handoff expiration rules depend on issue metadata the cited handoff structure does not carry

**Claim under review:** Section 4.5 retention ("Retain `.planning/` artifacts for the duration of the associated issue plus 14 days after closure"), Section 8.3 expiration signal ("Associated issue is closed for > 30 days"), GR-5 ("transient artifacts should include date or issue reference enabling automated cleanup").

**Evidence:** Live committed handoffs do not include issue references or expiration metadata: `docs/handoffs/session-2026-04-11-provider-audit-exit.md:1-4` and `docs/handoffs/session-2026-04-11-session-log-portability-exit.md:1-4` contain title/date/repo only.

**Why this is a defect:** The cleanup policy depends on "associated issue" linkage, but the live handoff structure it points to does not provide that linkage. That makes the stated expiration rule non-computable from the current repo surfaces.

**Required fix:** Either make the retention rule explicitly date-based until handoff templates are migrated, or elevate issue/expiration metadata from a future convention to a prerequisite and update the examples/retention language accordingly.

---

## Codex Finding 5 — MINOR: The claimed promotion audit trail is not actually represented in current wiki surfaces

**Claim under review:** Section 7.2 step 4 ("The promotion is its own evidence: ... The wiki log (`wiki/log.md`) records the ingest event ... The originating issue or session handoff can note `promoted to <wiki-page-path>`").

**Evidence:** `knowledge/wikis/engineering/wiki/log.md:1-28` and `:29-59` record bulk ingest events, source classes, and page counts, not page-level `promoted_from` lineage. `knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md:1-8` likewise has no field tying it back to a specific transient source artifact or promotion event.

**Why this is a defect:** #2209 treats current wiki/log surfaces as sufficient to enforce "no silent promotion", but those surfaces do not let an auditor answer "which transient artifact promoted this page?" without reading unrelated issue comments or handoffs manually.

**Required fix:** Define a concrete auditable promotion field or registry entry for wiki pages, instead of relying on generic log lines plus optional external notes.

---

## Addendum A — Claude cross-finding (MAJOR): the live wiki schema is a fourth, distinct authority

This finding emerged while Claude verified Codex Finding 1. Both #2207 and #2209 (and #2206 by extension) prescribe wiki frontmatter without acknowledging that the **wiki's own schema authority is a third shape that none of them match**.

**Live wiki schema (verified at `knowledge/wikis/engineering/CLAUDE.md`, the authoritative schema for the engineering wiki):**

| Field | Required? |
|---|---|
| `title` | **required** |
| `tags` | **required** |
| `added` | **required** |
| `last_updated` | **required** |
| `sources` | **recommended** (not required) |
| `domain` | optional |
| `cross_links` | optional |

Compared to:
- **#2207 Section 6.3 example:** `title, doc_key, source_ref, domain, promoted_from, last_updated` (no `sources`, no `tags`, no `added`)
- **#2209 Section 10.1 row 2:** `title, tags, sources, added, last_updated`, optional `promoted_from`
- **#2206 DT-1 pass signal:** `title, tags, sources, last_updated` (`sources` REQUIRED)
- **Live wiki CLAUDE.md:** `title, tags, added, last_updated` required; `sources` only RECOMMENDED

**Why this matters:** The wiki's own schema authority is the operational ground truth. Every conformance check, promotion contract, or boundary policy that prescribes a different frontmatter shape will produce false positives against actual wiki pages. The three contract documents are arguing about frontmatter shape while the wiki's own CLAUDE.md schema is yet a fourth shape that the live pages actually follow.

**Required fix (cross-cutting):** Either (a) reconcile all four schemas into one (likely requires amending the wiki's CLAUDE.md, #2207 Section 6.3, #2209 Section 10.1, and #2206 DT-1 in a single coordinated revision), or (b) declare the wiki CLAUDE.md as the single source of truth and demote the contract examples to "must include the CLAUDE.md required set; may add provenance fields per #2207."

---

## Verified claims (from Codex's check list, with Claude additions)

- Live wiki pages use `title / tags / sources / added / last_updated` — verified at `knowledge/wikis/engineering/wiki/entities/aqwa-solver.md:1-8` and `knowledge/wikis/engineering/wiki/concepts/fatigue-analysis-offshore.md:1-8`.
- #2207 Section 6.3 prescribes `doc_key, source_ref, domain, promoted_from, last_updated` for standards-promoted pages.
- `.planning/plan-approved/1839.md` is a real committed artifact (not hypothetical).
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` exists but is still draft, not normative — relevant to #2209 Section 4.4 weekly-review classification.
- `knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md` exists as durable promoted page.
- **(Claude addition):** `knowledge/wikis/engineering/CLAUDE.md` defines the authoritative wiki schema with `sources` as RECOMMENDED, not required — contradicting both #2207, #2209, and #2206.

## Disagreements with Claude review

> "I agree with the prior Claude adversarial review's findings. No rebuttals."

(All five Codex findings are non-overlapping with the seven in the Claude pass. Codex Finding 1 partially overlaps Claude Finding 1 of #2206 review, but from a different angle — Codex compared #2209 to #2207 and live pages; Claude compared #2206 DT-1 to #2207 and #2209.)

## Process note

Codex's sandbox blocked the direct artifact write (same as the #2207 dispatch). Findings transcribed by Claude with the wrapper above. Full Codex stdout transcript is available locally at the dispatcher's task output file.
