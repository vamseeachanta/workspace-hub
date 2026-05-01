# Adversarial Plan Review — #2370 Closed-Issue Promotion Ledger

> **Reviewer:** Claude Opus 4.6 (Feed9 — bounded adversarial lane)
> **Date:** 2026-04-29T07:35Z
> **Plan under review:** `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md`
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2370
> **Stance:** hostile — defect-hunting, not charitable reading

---

## Verdict: **MINOR**

The plan is structurally sound, well-scoped, and correctly identifies its boundaries against sibling issues (#2236, #2238, #2366). Issue counts are live-verified and accurate. The plan may advance to second-provider (Codex/Gemini) review after the MINOR findings below are addressed or acknowledged.

---

## Findings

### Finding 1 — MINOR: Retrieval contract bundle compliance gap

**Severity:** MINOR
**Dimension:** 1 — missing resource-intelligence sources

**Evidence:** The plan's own RETRIEVAL CONTRACT comment (line 14-19) identifies issue class as "Data Pipeline + Knowledge/Intelligence (union)" and lists required bundles including: `registry.yaml`, `resource-intelligence-maturity.yaml`, `operating model (#2205)`, `sibling contracts`, `accessibility map (#2096)`.

The "Documents consulted" section (lines 37-46) does **not** list:
- `data/document-index/registry.yaml` — EXISTS (verified: 1M+ doc inventory with domain breakdown)
- `data/document-index/resource-intelligence-maturity.yaml` — EXISTS (verified: 425 docs in scope, 6.8% read)
- `docs/document-intelligence/` entry points — EXISTS (verified: directory with batch-definitions, dark-intelligence, etc.)
- Issue #2205 (operating model) — not consulted
- Issue #2096 (accessibility map) — not consulted

The `registry.yaml` is particularly relevant because it tracks doc counts by domain — the promotion ledger's scoring heuristics would benefit from knowing the 283k marine docs and 50k structural docs in the intelligence surface.

**Remediation:** Add a subsection acknowledging these sources were inspected. If they are genuinely irrelevant to a GitHub-issue-scanning script, state that explicitly with rationale ("registry.yaml tracks document metadata, not issue metadata — no overlap with promotion ledger inputs").

---

### Finding 2 — MINOR: Already-ingested issue identification is solvable, not "open"

**Severity:** MINOR
**Dimension:** 4 — schema/data-contract ambiguity

**Evidence:** The plan's "Risks and Open Questions" section (line 257) says:
> "The 5 previously-ingested issues from Class 11 are mentioned in prose in SOURCE_INVENTORY.md but their exact issue numbers are not listed."

This is **incorrect**. The exact 5 issue numbers are explicitly listed in `knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md` (lines 18-22):
- #1773 — DNV-RP-F105 pipeline free-span VIV fatigue module
- #1791 — Probability-weighted multi-current damage summation
- #1768 — OrcaWave-to-OrcaFlex handoff pipeline
- #1984 — Seakeeping module — 6-DOF motion analysis
- #1858 — Field-dev FDAS + economics integration

This is not an "open question" — it is a solved data point. The implementation should hardcode or load these 5 numbers from the source page frontmatter/body, not treat them as uncertain.

**Remediation:** Move from "Open Questions" to "Dependencies" or the resource-intelligence section. Reference the exact file path (`knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md`) and the 5 issue numbers.

---

### Finding 3 — MINOR: SOURCE_INVENTORY.md Class 11 count is stale and plan acknowledges it, but update scope is underspecified

**Severity:** MINOR
**Dimension:** 5 — failure to protect existing wiki/index artifacts

**Evidence:** `SOURCE_INVENTORY.md` line 99 says: `**Files**: 20 closed issues with 'cat:engineering' label`. The actual count is 92 (verified via `gh issue list --limit 500`). The plan correctly identifies this in line 34 ("only 3 pages created from 5 issues (out of 20 originally scanned)") but the "Files to Change" table (line 187) only says "Update Class 11 counts and add reference to ledger."

The concern: updating counts alone may break the narrative flow of SOURCE_INVENTORY.md. The "Future source classes" section (line 114) says "15 remaining" — this will need to change to ~101. If the update is mechanical (just numbers) it's fine, but if it requires rewriting the Class 11 prose (e.g., changing "20 closed issues" to "92 closed issues" and adjusting the "15 remaining" note to "87 remaining"), the plan should specify the exact edits.

**Remediation:** In "Files to Change," specify which lines/sections of SOURCE_INVENTORY.md will be updated and whether the Class 11 description, the "Future" section, or both are in scope.

---

### Finding 4 — MINOR: Composite score formula has sign-direction ambiguity for overlap_risk

**Severity:** MINOR
**Dimension:** 4 — schema/data-contract ambiguity

**Evidence:** The plan states (line 256):
> "overlap_risk is inverse (high overlap = lower promotion value). Default: methodology=0.30, durability=0.25, evidence=0.25, overlap_risk_penalty=0.20"

And in the pseudocode (line 147): `overlap_risk: score_overlap(issue, wiki_pages),  # 0-5: 0=no overlap, 5=fully covered already`

The composite score formula is stated as `weighted_sum(scores)` (line 135) but the pseudocode doesn't show how overlap_risk is subtracted vs. added. If overlap_risk=5 means "fully covered" and the composite is a simple weighted sum, then high overlap would **increase** the composite score (bad). The plan names it `overlap_risk_penalty=0.20` suggesting subtraction, but the pseudocode function `weighted_sum` doesn't distinguish additive vs. subtractive dimensions.

**Remediation:** Make the formula explicit in pseudocode:
```
composite = (methodology * 0.30) + (durability * 0.25) + (evidence * 0.25) - (overlap_risk * 0.20)
```
Or normalize overlap_risk as `(5 - overlap_risk)` before summing. Either way, the sign direction must be unambiguous in the plan, not left to implementer interpretation.

---

### Finding 5 — MINOR: TDD test list lacks edge cases for wiki index parsing failures

**Severity:** MINOR
**Dimension:** 2 — TDD gaps

**Evidence:** The plan's `load_wiki_index(wiki_root)` function (line 117) parses `index.md` to extract `{slug, title, category, summary}`. The wiki index is a markdown file with pipe-delimited tables (verified: `knowledge/wikis/engineering/wiki/index.md`). The current test list (lines 196-210) has no test for:
- Malformed index.md (missing columns, extra pipes, empty rows)
- Index.md with markdown formatting inside cells (links like `[Title](path)`)
- Index.md page_count frontmatter mismatch with actual table rows (currently 82 in frontmatter, 86 rows in tables including the 4 "other" entries at the bottom outside standard sections)

The `index.md` file has an irregular structure — the bottom section (lines 123-128) contains entries outside standard category headers (Comparisons section + loose pipe-rows). If `load_wiki_index` naively parses all `|` rows, it may include malformed entries.

**Remediation:** Add test cases:
- `test_wiki_index_parse_with_links` — handles `[Title](path.md)` in page column
- `test_wiki_index_parse_irregular_sections` — gracefully handles entries outside standard category headers

---

### Finding 6 — INFO: Scoring heuristics are appropriately scoped as triage aids

**Severity:** INFO (not actionable — positive observation)
**Dimension:** 3 — scope creep check

The plan explicitly limits scoring to keyword heuristics and defers LLM-based semantic scoring to a follow-up (line 265). The shortlist is positioned as human-reviewed input, not an automated promotion pipeline. This correctly avoids scope creep into the #2039/#2236 implementation territory. No action needed.

---

### Finding 7 — INFO: wiki/index.md page_count discrepancy (cosmetic)

**Severity:** INFO
**Dimension:** 5 — wiki artifact protection

The `index.md` frontmatter says `page_count: 82` but the actual table has more rows (32 concepts + 22 entities + 14 sources + 7 standards + 5 workflows = 80 standard + the 2 loose entries at bottom = 82). Count is consistent. However, the sources section in the live index now shows **14** entries (not 13 as listed in `source_count: 16` — that field tracks classes, not pages). This is cosmetic and outside #2370 scope, but the plan's "Files to Change" lists SOURCE_INVENTORY.md but not index.md itself. If the ledger implementation touches index.md, the plan should say so.

**Remediation:** Confirm index.md is NOT in the "Files to Change" table (it shouldn't be — the ledger doesn't create wiki pages). Currently correct.

---

### Finding 8 — MINOR: `--already-ingested` CLI flag source is unspecified

**Severity:** MINOR
**Dimension:** 4 — schema/data-contract ambiguity

**Evidence:** The pseudocode (line 113) shows `--already-ingested` as a CLI argument, and the function signature (line 118) passes it as `already_ingested_path`. But the plan never specifies what file format this argument expects. Is it:
- A newline-separated list of issue numbers?
- A YAML file matching the `closed-engineering-issues.md` source page?
- A JSON array?
- The path to `closed-engineering-issues.md` itself (parsing issue numbers from markdown tables)?

Given Finding 2 establishes that the 5 issue numbers are in `sources/closed-engineering-issues.md`, the implementation needs to either: (a) parse that markdown file, or (b) accept a simpler format. The plan should specify which.

**Remediation:** Define the `--already-ingested` input format. Recommended: accept a simple text file with one issue number per line, and document that the canonical source is extractable from `knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md`.

---

## Summary Table

| # | Severity | Dimension | Finding |
|---|----------|-----------|---------|
| 1 | MINOR | Resource intelligence | Retrieval contract bundle compliance gap — 5 required sources not consulted/acknowledged |
| 2 | MINOR | Data contract | Already-ingested issues are known (5 numbers in `sources/closed-engineering-issues.md`), not "open" |
| 3 | MINOR | Wiki protection | SOURCE_INVENTORY.md update scope underspecified |
| 4 | MINOR | Data contract | Composite score sign-direction ambiguity for overlap_risk |
| 5 | MINOR | TDD gaps | Missing test cases for wiki index parsing edge cases |
| 6 | INFO | Scope creep | Correctly bounded — no scope creep detected |
| 7 | INFO | Wiki protection | index.md not in files-to-change — correct |
| 8 | MINOR | Data contract | `--already-ingested` CLI input format unspecified |

---

## Advance-to-Second-Provider Decision

**YES — the plan may advance to Codex/Gemini cross-review.**

All 5 MINOR findings are addressable with plan text edits (no architectural redesign needed). None are blockers. The plan's core design — keyword-heuristic scoring, YAML ledger, human-reviewed shortlist — is sound and well-scoped. The scope boundaries against #2236/#2238/#2366 are correctly drawn. Issue counts are live-verified accurate.

Recommended sequence:
1. Address Findings 2, 4, and 8 (concrete fixes — 10 min of plan editing)
2. Acknowledge Finding 1 with a brief rationale note
3. Optionally address Finding 5 (adds test coverage depth)
4. Then dispatch to Codex + Gemini for independent review

---

## Files Inspected (read-only)

| File | Purpose |
|------|---------|
| `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md` | Plan under review |
| `docs/plans/_template-issue-plan.md` | Template compliance check |
| GitHub issue #2370 (via `gh issue view`) | Goal alignment |
| `data/document-index/promotions/2026-04-16-standards-promotion.yaml` | Precedent schema |
| `knowledge/wikis/engineering/SOURCE_INVENTORY.md` | Source class definitions |
| `knowledge/wikis/engineering/wiki/index.md` | Wiki page inventory |
| `knowledge/wikis/engineering/wiki/log.md` | Ingest history |
| `knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md` | Already-ingested issues |
| `docs/reports/engineering-wiki-skill-ingest-readiness-2039-2042.md` | Readiness report |
| `scripts/knowledge/llm_wiki.py` (lines 1240-1268) | Batch ingest function |
| `data/document-index/registry.yaml` (lines 1-30) | Doc inventory registry |
| `data/document-index/resource-intelligence-maturity.yaml` (lines 1-30) | Intelligence maturity tracker |
| GitHub API: closed issue counts for `cat:engineering` (92), `cat:engineering-calculations` (15), dual-labeled (1) | Count verification |
