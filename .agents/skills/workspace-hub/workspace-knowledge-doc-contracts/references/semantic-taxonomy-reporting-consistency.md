# Archived Skill: `semantic-taxonomy-reporting-consistency`

Original path: `/home/vamsee/.hermes/skills/development/semantic-taxonomy-reporting-consistency`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/development/semantic-taxonomy-reporting-consistency`
Consolidation date: 2026-04-29

---

---
name: semantic-taxonomy-reporting-consistency
description: Keep semantic-diff taxonomy summaries consistent with evidence tables when adding richer categories to legacy comparison/reporting pipelines.
version: 1.0.0
author: Hermes Agent
category: development
license: MIT
---

# Semantic Taxonomy Reporting Consistency

Use when upgrading a legacy diff/comparison/reporting path from coarse levels (for example `significant` / `convention` / `cosmetic`) to a richer taxonomy.

## Trigger conditions
- A producer emits per-diff records plus aggregate category counts
- HTML/JSON reports show both summary counts and detailed evidence rows
- Legacy buckets are being split into richer categories
- There is risk that counts and visible evidence can drift apart

## Core rule
When explicit diff rows exist, derive rendered category counts from those diff rows.
Only fall back to producer-supplied aggregate counts when there is no diff list.

Why:
- prevents summary tables from overclaiming categories not supported by the evidence rows
- avoids contradictory reports where counts say one thing and visible diffs say another
- keeps review/debugging grounded in inspectable evidence

## Recommended implementation pattern
1. Add a normalizer function such as `summarize_semantic_equivalence(payload)`.
2. In that function:
   - read `diffs`
   - map legacy levels to richer taxonomy when category is missing
   - build `taxonomy_counts` from `diffs`
   - if `diffs` is empty, optionally use payload-level `taxonomy_counts` as fallback
3. Return one normalized structure for all consumers:
   - `match_count`
   - `cosmetic_count`
   - `convention_count`
   - `significant_count`
   - `taxonomy_counts`
   - grouped diff lists by legacy level and/or taxonomy
4. Make every renderer consume the normalized structure rather than re-deriving its own counts.

## Important UI/reporting rule
Do not place significant taxonomy categories inside sections labeled as non-semantic or "no solver effect".

Bad pattern:
- footnote/details block says `cosmetic + convention diffs (no solver effect)`
- same block also includes `physics_significant` or `solver_mode_significant` counts

Safer pattern:
- show an overall taxonomy summary separately
- keep non-significant footnotes restricted to non-significant categories only

## Test strategy
Add tests for all of these:
1. Producer emits richer taxonomy category per diff
2. Producer emits aggregate `taxonomy_counts`
3. Renderer shows counts that match diff evidence when diffs are present
4. Renderer falls back safely when no diffs are present
5. Significant categories are not shown in non-significant footnotes/sections
6. Legacy payloads without `category` still map through a compatibility table
7. Test fixtures stay internally consistent: if a test includes both `diffs` and aggregate `taxonomy_counts`, the counts should be supported by the diff rows unless the test is explicitly exercising the no-diffs fallback path

Common testing pitfall:
- A renderer test that passes one diff row but asserts additional taxonomy counts from payload metadata can accidentally lock in contradictory reporting behavior.
- Prefer fixtures where visible evidence and asserted summary counts agree, then add a separate no-diffs fixture to cover aggregate-count fallback.

## Review checklist
- Are rendered counts reproducible from the visible diff rows?
- Can summary counts mention categories with zero evidence rows?
- Are any significant categories presented under "cosmetic" or "no solver effect" wording?
- Does the fallback behavior only apply when detailed evidence is absent?
- Do tests cover partial/truncated diff payloads?

## Example lesson
In issue #521 (digitalmodel OrcaWave semantic-equivalence taxonomy follow-through), an initial implementation allowed payload `taxonomy_counts` to override diff-derived counts even when only a partial diff list was present. Adversarial review caught that this could overclaim unsupported categories. The fix was:
- derive counts from diff rows when diffs exist
- use payload aggregate counts only when diffs are absent
- move overall taxonomy summary out of the "no solver effect" footnote
- keep non-significant footnotes restricted to non-significant categories
