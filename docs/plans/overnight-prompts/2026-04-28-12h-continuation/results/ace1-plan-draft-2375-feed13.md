# Lane feed13 Result — Plan Draft for #2375

> **Lane:** feed13 — pure planning draft for workspace-hub issue #2375
> **Machine:** ace-linux-1 (control surface)
> **Executed:** 2026-04-29 ~05:30 CDT
> **Status:** COMPLETE — draft plan written, no commits, no GitHub mutation

---

## Discoveries

1. **Prior draft exists:** `docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md` (April 26) — a comprehensive draft already covering the same scope. This feed13 plan supersedes it with prompt-aligned artifact paths and consolidates two scripts into one.

2. **Corpus verified:** `knowledge-base/wrk-completions.jsonl` — 420 records, 332 KB, three source cohorts:
   - `synthesize-archive`: 389 records (fully structured: id/type/category/subcategory/title/archived_at/mission/patterns/follow_ons)
   - `memory-migration`: 21 records (raw-string only: id/type/source/raw)
   - `capture-wrk-summary`: 10 records (same structure as synthesize-archive)

3. **Memory-migration regex 21/21:** All 21 raw records match the extraction pattern `^- \*\*(WRK-\d+) ARCHIVED\*\*(?: \(([0-9a-f]+)\))?:\s*(.+)$`. Zero unparseable records. Title, commit SHA, and body are all recoverable.

4. **Target YAML does not exist:** `knowledge/seeds/wrk-completions.yaml` confirmed missing. This was proposed by #894 architecture plan but never landed.

5. **Wiki-candidate path decision:** Prior draft used `knowledge-base/wiki-candidates.yaml`; this plan uses `data/document-index/wrk-wiki-candidates.yaml` per the prompt architecture, aligning with existing projection files in that directory (`standards-transfer-ledger.yaml`, `online-resource-registry.yaml`).

6. **Categorization rules available:** `scripts/knowledge/categorize_uncategorized.py` has 28+ regex rules importable as `RULES`. Reusable for assigning category/subcategory to the memory-migration cohort.

7. **Sibling plans exist and are compatible:**
   - #2374 plan (`docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`) — uses same status vocabulary and scoring rubric
   - #2370 plan (separate) — same scoring philosophy
   - Both explicitly reference the #2375 plan as a sibling, confirming non-overlap

8. **Issue states verified:**
   - #2375 — OPEN
   - #103 — OPEN (upstream backfill, not duplicate)
   - #894 — CLOSED (architecture proposal that #2375 implements)
   - #2374 — OPEN (sibling, different source surface)
   - #2370 — OPEN (sibling, different source surface)

## Files Written

| File | Type |
|---|---|
| `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md` | Draft plan (NEW) |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-draft-2375-feed13.md` | This result summary (NEW) |

## Key Differences from Prior Draft (April 26)

| Aspect | Prior draft (Apr 26) | This draft (Apr 29) |
|---|---|---|
| Script name | `normalize_wrk_completions.py` + `build_wiki_candidates.py` (two scripts) | `normalize_wrk_seeds.py` (one script, integrated) |
| Wiki-candidate path | `knowledge-base/wiki-candidates.yaml` | `data/document-index/wrk-wiki-candidates.yaml` |
| Policy doc | Not included | `docs/document-intelligence/wrk-seed-policy.md` |
| Acceptance: min candidates | Not specified | ≥10 high-confidence candidates at score≥2 |
| Acceptance: no-drop guarantee | Implicit | Explicit: each raw row → structured row OR logged in unrecoverable report |

## Unresolved Questions (for User at Approval)

1. **Wiki-candidate corpus path:** `data/document-index/wrk-wiki-candidates.yaml` vs `knowledge-base/wiki-candidates.yaml` — plan picks the former for consistency with existing document-index projections. Confirm.
2. **Append-flow policy location:** `docs/document-intelligence/wrk-seed-policy.md` — is this the right directory per the #2205 operating model? Alternative: `docs/knowledge/`.
3. **`gh_issue` backfill:** deferred to follow-on. The field exists as nullable. Confirm this deferral is acceptable or if v1 should attempt best-effort cross-referencing.
4. **Prior draft disposition:** `docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md` is marked superseded in this plan's header. Should it be deleted or retained for provenance?

## Next Safe Action

1. **Route to adversarial review:** `scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`
2. **Post to GitHub:** after review passes, comment plan on issue #2375 and label `status:plan-review`
3. **Wait for user approval** before any implementation
