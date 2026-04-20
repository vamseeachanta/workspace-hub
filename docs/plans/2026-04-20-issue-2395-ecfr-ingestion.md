# Plan for #2395: eCFR ingestion — Title 30/33/40/46/49 regulatory corpus

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-04-20
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2395
> **Review artifacts:** scripts/review/results/2026-04-20-plan-2395-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/data/document-index/phase-a-index.py` — L2 indexing pipeline this extends (new source type: CFR).
- Found (closed): #596 WRK-5041 `extract-url.py` — prior art for internet document extraction; not used for scheduled CFR pulls.
- Found: `data/document-index/standards-transfer-ledger.yaml` — tracks industry codes, does NOT track federal regs (confirmed via grep for "CFR").
- Found: `data/design-codes/code-registry.yaml` — industry codes only.
- Gap: no federal-regulation registry, no eCFR API client, no regulatory wiki domain.

### Standards
- `30 CFR` — BOEM/BSEE offshore operations (primary target for mooring, riser, pipeline, safety domains).
- `33 CFR` — USCG (navigation, anchoring, pollution).
- `40 CFR` — EPA (NPDES, spill prevention).
- `46 CFR` — USCG (shipping, vessel inspection).
- `49 CFR` — PHMSA (pipeline safety).

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — references some federal standards by citation but has no CFR page.
- `knowledge/wikis/` — no `regulatory` domain exists yet; must be created.

### Documents consulted
- Operating model §3 (`sha256:` `doc_key`), §4 (L1→L2→L3 flow), §8.1 (frontmatter authority — new `regulatory/CLAUDE.md` required).
- [eCFR API v1 docs](https://www.ecfr.gov/developers/documentation/api/v1) — JSON + XML endpoints; rate limit 60 req/min.
- Related issue #2373 (non-ACMA standards) — this fills the regulatory gap excluded by #2373 scope.
- Related issue #2365 (design-code registry promotion) — parallel pattern for industry codes.
- Memory `project_cross_review_policy.md` — long-running scripts need checkpoint/resume.

### Gaps identified
- No CFR-aware `doc_key` scheme (XML-normalization rules required).
- No regulatory wiki domain exists (new `CLAUDE.md` + schema).
- No federal-reg refresh cadence.

**Distinct sources consulted: 9** — exceeds ≥3 minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2395-ecfr-ingestion.md` |
| Implementation | `scripts/data/doc_intelligence/ingest_cfr.py` |
| eCFR client | `scripts/data/doc_intelligence/ecfr_client.py` |
| Registry | `data/document-index/cfr-registry.yaml` (git-tracked) |
| L1 storage | `/mnt/ace/CFR/Title-XX/part-NN/section-NN.NN.txt` (gitignored; authoritative copy on shared mount) |
| Wiki domain | `knowledge/wikis/regulatory/CLAUDE.md` + `knowledge/wikis/regulatory/wiki/` |
| Tests | `tests/data/doc_intelligence/test_ingest_cfr.py` + recorded-response fixtures in `tests/fixtures/ecfr/` |
| Cron wiring | `config/scheduled-tasks/schedule-tasks.yaml` |
| Plan review — Claude | `scripts/review/results/2026-04-20-plan-2395-claude.md` |

---

## Deliverable

A CFR ingestion pipeline that pulls 5 Titles via eCFR JSON API, hashes sections into a git-tracked `cfr-registry.yaml`, stores raw text at `/mnt/ace/CFR/`, and promotes Title overviews into a new `regulatory` wiki domain.

---

## Pseudocode

```
function ingest_title(title_num, edition_date):
    sections = ecfr_api.list_sections(title_num, edition_date)  # paginated
    for section in sections with rate_limit(60/min):
        text = ecfr_api.get_section_text(title_num, part, section, format="plain")
        normalized = normalize_whitespace_and_cross_refs(text)
        doc_key = "sha256:" + sha256(normalized)
        prior = cfr_registry.get_by_title_part_section(title_num, part, section)
        if prior and prior.doc_key != doc_key:
            mark prior as status=superseded
            emit new entry with status=indexed
        elif prior:
            skip  # unchanged
        else:
            emit new entry
        write L1 text to /mnt/ace/CFR/Title-{title_num}/part-{part}/section-{section}.txt
    write cfr-registry.yaml atomically

function promote_title_overview(title_num):
    regs = cfr_registry.filter(title=title_num)
    render knowledge/wikis/regulatory/wiki/cfr-title-{title_num}.md
        with frontmatter: title, last_updated, doc_key (of rendered page), source_ref, promoted_from

# quarterly cron
for title in [30, 33, 40, 46, 49]:
    edition = ecfr_api.latest_edition()
    ingest_title(title, edition)
    promote_title_overview(title)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/doc_intelligence/ingest_cfr.py` | Main pipeline |
| Create | `scripts/data/doc_intelligence/ecfr_client.py` | API client w/ rate-limit + retry |
| Create | `scripts/data/doc_intelligence/cfr_normalize.py` | Whitespace, cross-ref, amendment-note normalization |
| Create | `tests/data/doc_intelligence/test_ingest_cfr.py` | TDD suite |
| Create | `tests/data/doc_intelligence/test_ecfr_client.py` | API-client tests (recorded responses) |
| Create | `tests/fixtures/ecfr/*.json` | Recorded API responses |
| Create | `data/document-index/cfr-registry.yaml` | Initial empty shell |
| Create | `knowledge/wikis/regulatory/CLAUDE.md` | Frontmatter schema authority per §8.1 |
| Create | `knowledge/wikis/regulatory/wiki/index.md` | Wiki entry point |
| Modify | `.gitignore` | Ignore `/mnt/ace/CFR/**` cache mirror if any |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Quarterly schedule |
| Update | `docs/plans/README.md` | Add this plan |

---

## TDD Test List

| Test | Verifies | Input | Expected |
|---|---|---|---|
| test_normalize_whitespace_stable | Normalization idempotent | raw→norm→norm = raw→norm | byte-identical |
| test_doc_key_stable_across_reingests | Same edition → same `doc_key` | fixture API response run twice | identical keys |
| test_doc_key_changes_on_amendment | Edition bump amending one word changes doc_key | 2 fixture responses | different keys |
| test_supersession_marked | Old entry gets status=superseded when content changes | registry fixture | old entry status updated |
| test_rate_limit_60_per_min | Client sleeps to honor 60 req/min | 120 rapid calls | total time ≥ 60s |
| test_retry_on_503 | 503 → retry with backoff | mocked transient 503 | eventual success |
| test_retry_gives_up | Persistent 500 → exits with error | mocked hard failure | exit ≠ 0, clear log |
| test_resume_from_checkpoint | Crash midway → resume picks up from last completed section | checkpoint fixture | no duplicate work, no skipped sections |
| test_wiki_overview_has_required_frontmatter | Generated page has title/last_updated/doc_key | full pipeline run | frontmatter validates |
| test_regulatory_claude_md_declares_baseline_floor | New CLAUDE.md conforms to §8.1 | static check | grep passes |

---

## Acceptance Criteria

- [ ] All tests pass
- [ ] First real run of Title-30 completes end-to-end; ≥1000 sections indexed
- [ ] First real run of Title-33 likewise
- [ ] `cfr-registry.yaml` git-tracked; `/mnt/ace/CFR/` populated
- [ ] `knowledge/wikis/regulatory/` domain created with CLAUDE.md + Title-30 + Title-33 overview pages
- [ ] Quarterly cron wired (first Sunday of Jan/Apr/Jul/Oct)
- [ ] Resumable: `--resume` flag restores from checkpoint if first run crashes
- [ ] Review artifacts posted

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self) | MINOR | See findings below |
| Codex | PENDING | **Recommended** given pipeline complexity + API-contract dependency |
| Gemini | PENDING | Optional |

Revisions made inline:
- **A:** Added explicit normalization module (`cfr_normalize.py`) — without normalization, whitespace/encoding differences cause `doc_key` churn.
- **B:** Added `test_resume_from_checkpoint` — long runs will crash; recovery tested up front.
- **C:** Promoted regulatory CLAUDE.md to explicit Files-to-Change row and conformance test — enforces §8.1.
- **D:** Added rate-limit test at 60/min honoring eCFR public guidance.
- **E:** Added `test_supersession_marked` — operating-model §3 status vocab requires explicit state transitions.

---

## Risks and Open Questions

- **Risk:** eCFR API schema changes break client. Mitigation: recorded-response fixtures for regression; API-version pin; error-clear failure.
- **Risk:** Title-30 full pull ≈30+ min; cron may hit machine suspend. Mitigation: resume flag + checkpoint state.
- **Risk:** Normalization choices affect `doc_key` — if changed later, all existing keys churn. Mitigation: `normalize_version` field in registry; migrations documented.
- **Open:** Should XML source be retained in addition to plain text? Plan: text-only initially; XML as follow-on if cross-referencing structured sections matters.
- **Open:** Cross-walk to DNV/API/ISO standards (which CFR cites which standard)? Explicitly **out of scope** — follow-on issue.

---

## Complexity: T3

Multi-stage (client + ingest + normalize + promote), new wiki domain, multi-machine storage, scheduled refresh.
