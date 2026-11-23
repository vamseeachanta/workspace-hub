# Lane feed8 Result — Plan Draft for #2370

**Lane:** ace1-plan-draft-2370-feed8
**Completed:** 2026-04-29T04:45Z
**Machine:** ace-linux-1

## Discoveries

### Seed Fact Verification (counts are stale)
- Issue body cited **74** closed `cat:engineering` — actual count is **92** (+24% growth since issue filed)
- Issue body cited **13** closed `cat:engineering-calculations` — actual count is **15**
- 1 dual-labeled issue → **106 deduped unique issues** in scope
- SOURCE_INVENTORY.md Class 11 shows only 3 wiki pages created from 5 issues — vast majority untriaged

### Key Structural Findings
- `scripts/knowledge/llm_wiki.py` has **no promotion or issue-ingestion logic** — it handles wiki lifecycle (init/status/lint/ingest/query) on YAML/JSONL metadata. The ledger script is a new standalone tool.
- `data/document-index/promotions/2026-04-16-standards-promotion.yaml` provides a **precedent YAML schema** for promotion records — fields include title, slug, id, org, domain, tags, summary, issue, status, source_registry.
- Engineering wiki has **82 pages** (34 concepts, 22 entities, 12 sources, 7 standards, 3 workflows, 4 other) — this is the overlap target surface.
- Related issues #2236, #2238, #2039, #2042, #2366 are all OPEN. None blocks #2370 — they govern different lifecycle phases (future workflow, citation guardrails, ingest umbrella, strengthening scorecard).

### Already-Ingested Issues
- SOURCE_INVENTORY.md states "3 pages created from 5 issues" for Class 11 but does **not list the specific issue numbers**. Implementation will need to cross-reference `wiki/log.md` or page frontmatter provenance to identify the 5.

## Files Written
- `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md` — full plan draft, status=draft, 15 TDD tests, 13 acceptance criteria, 8 open questions/risks, out-of-scope boundary, rollback plan

## Unresolved Questions (for user approval review)
1. **Composite score weights** — proposed 0.30/0.25/0.25/0.20 split across methodology/durability/evidence/overlap_penalty. User should confirm or adjust.
2. **Already-ingested identification** — the 5 previously-ingested issue numbers are not recorded in structured data. Script may need to parse wiki log.md or page frontmatter to identify them.
3. **Single vs. split ledger** — should `cat:engineering-calculations` issues be in the same ledger as `cat:engineering`, or separate? Plan recommends single ledger with tag-filtered views.

## Next Safe Action
- Route to adversarial review (Step 4 of planning workflow): dispatch plan to 2+ AI providers for defect-hunting review
- Then post to GitHub with `status:plan-review` label
- Wait for user approval before any implementation
