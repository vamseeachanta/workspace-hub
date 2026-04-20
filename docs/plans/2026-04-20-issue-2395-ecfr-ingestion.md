# Plan for #2395: eCFR ingestion — v2 (post-iteration-1 cross-review)

> **Status:** plan-review (iteration 2 of 3)
> **Complexity:** T3
> **Date:** 2026-04-20 (v2)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2395
> **v1 reference:** commit `5b4c347cd` + findings at `scripts/review/results/2026-04-20-plan-2395-{claude,codex,gemini}.md`
> **Review artifacts:** populated after iteration-2 review dispatch

---

## Revision History

**v1 (2026-04-20, commit 5b4c347cd):** Claude self-review MINOR. Cross-review: Codex MAJOR + Gemini MAJOR.
**Convergent v1 P1 findings fixed in v2:**
- **Gemini P1 pseudocode bug:** `for section in sections` referenced undefined `part` variable → **rewritten with structured iteration** (below)
- D1 `sha256:` namespace not enforced → **§Identity Contract** with rendered-page `doc_key` derivation explicit
- `--resume` checkpoint had no file/schema → **§Checkpoint Contract** with explicit state file + tier
- L1 existence not verified before skip → pseudocode adds existence check + re-fetch on desync
- `.gitignore` for absolute `/mnt/ace/` path was a no-op → removed (replaced with documented mount-side cleanup)
- §4 flow compliance unproven → **§Operating-Model Flow Map** documents L1→L2→L3 transitions
- D5 dependency statuses unverified → **§Dependency Matrix**
- D4 threat model (path traversal, mount availability) → **§Threat Model**
- **Scope reduction:** v2 ships only Titles **30 + 33** in first delivery; Titles 40/46/49 moved to follow-on (#2395-B candidate after this closes)

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/data/document-index/phase-a-index.py` — L2 indexing pattern (confirmed via Read 2026-04-20).
- `scripts/data/document-index/provenance.py` — provenance record shape (confirmed).
- `data/document-index/standards-transfer-ledger.yaml` — no "CFR" entries (confirmed via grep).
- `knowledge/wikis/` — no `regulatory` domain exists (confirmed; must create).

### Standards
- 30 CFR (BOEM/BSEE), 33 CFR (USCG) — v2 first-delivery scope.
- 40 CFR / 46 CFR / 49 CFR — deferred to follow-on issue.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/CLAUDE.md` — §8.1 schema-authority example; new `regulatory/CLAUDE.md` mirrors pattern.

### Documents consulted
- Operating model §3/§4/§7/§8.1.
- [eCFR API v1](https://www.ecfr.gov/developers/documentation/api/v1) — rate limit 60 req/min, JSON endpoints confirmed.

### Dependency Matrix (live-verified 2026-04-20)

| Issue | State | Relationship | Behavior if unshipped |
|---|---|---|---|
| #2205 | CLOSED | authority | — |
| #2373 | OPEN | parallel (non-ACMA standards) | scope-separated; no blocking |
| #2365 | OPEN | parallel (design-code registry) | no blocking |
| #596 | CLOSED (extract-url.py) | prior art | code reviewed; not reused |

### Gaps identified
- No CFR-aware `doc_key` scheme — defined below.
- No `regulatory` wiki domain — this plan creates.
- No quarterly refresh cadence — this plan wires.

Distinct sources: **9**.

---

## Identity Contract (§3 compliance)

**Section-level `doc_key`:** `sha256:<hex>` of normalized section text. Canonical.

**Rendered wiki-overview-page `doc_key`:** `sha256:<hex>` of normalized page content **excluding frontmatter**. Frontmatter is metadata; its `doc_key` field refers to the content-body hash, avoiding the circular "hash includes its own value" problem.

**Legacy:** none (CFR corpus is new; no md5 compatibility needed).

**Path-only identity forbidden.** Section stored at `/mnt/ace/CFR/Title-30/part-250/section-250.901.txt` is identified by content hash; path is metadata alias.

Tests:
- `test_section_doc_key_stable_across_reingests`
- `test_section_doc_key_changes_on_amendment`
- `test_wiki_page_doc_key_excludes_frontmatter`
- `test_bare_hex_rejected`
- `test_path_alias_recorded_not_used_as_identity`

---

## Cross-Machine Tier Assignment (§7 compliance)

| Artifact | Path | Tier | Authority | Sync |
|---|---|---|---|---|
| CFR registry | `data/document-index/cfr-registry.yaml` | 1 git-tracked | authoritative | — |
| Wiki domain config | `knowledge/wikis/regulatory/CLAUDE.md` | 1 git-tracked | authoritative | — |
| Wiki overview pages | `knowledge/wikis/regulatory/wiki/*.md` | 1 git-tracked | authoritative | — |
| L1 raw section text | `/mnt/ace/CFR/Title-XX/part-NN/section-NN.NN.txt` | 2 shared-mount | preferred when reachable | written by ingest; never rewritten outside ingest |
| Checkpoint state | `/mnt/ace/CFR/.checkpoints/title-XX.yaml` | 2 shared-mount | authoritative for resume | co-located with L1 |
| Run logs | `logs/ecfr-ingest/run-YYYY-MM-DD.jsonl` | 3 local-cache | not authoritative | — |

Checkpoint on shared mount is intentional: a run started on machine A must resume on machine B if needed (mount reachability permitting).

---

## Checkpoint Contract

**State file:** `/mnt/ace/CFR/.checkpoints/title-{title}.yaml`

**Schema:**
```yaml
title: 30
edition_date: "2026-01-01"
started_at: "2026-04-20T12:00:00Z"
last_completed_part: 250
last_completed_section: "250.901"
sections_processed: 482
sections_total_estimated: 3500
status: running | completed | failed
last_error: null | "<message>"
```

**Atomicity:** checkpoint written after each successfully completed section via atomic rename (write temp file, fsync, rename).

**Resume semantics:** `--resume` reads checkpoint, skips sections ≤ `last_completed_section`, continues from next. If checkpoint says `status: completed` and `edition_date` matches current, exits success (no-op).

**Tests:** `test_checkpoint_atomic_write`, `test_resume_skips_completed_sections`, `test_resume_noop_on_completed_matching_edition`, `test_resume_reprocesses_on_edition_bump`.

---

## Operating-Model Flow Map (§4 compliance)

| Flow | Direction | Rationale |
|---|---|---|
| eCFR API → L1 raw text (`/mnt/ace/CFR/`) | L1 ingest | allowed: external source → L1 |
| L1 text → L2 registry (`cfr-registry.yaml`) | L1 → L2 | allowed: indexing (per §4 "Indexing, hashing, extraction status tracking") |
| L2 registry → L3 wiki overview page | L2 → L3 | allowed: promotion of structured outputs (per §4 L2→L3) |
| L3 overview → L5 issues (via retrieval contract) | L3 → L5 | allowed: consumption |

**No forbidden flows:** no L5→L1 (wiki page never regenerates source), no L3 circular (overview page is regenerated from registry on edition bump, but with new `doc_key` and `superseded` status on prior version per §3 status vocab).

---

## Threat Model

**Input surfaces:** eCFR JSON API, writes to `/mnt/ace/CFR/`, new repo files.
**Trust boundaries:**
- eCFR content is trusted (public-domain US federal law, served over HTTPS from `.gov` domain).
- Part/section identifiers from API are **untrusted** for use as filesystem paths — must be sanitized.

**Mitigations:**
- Path sanitization: `{title}`, `{part}`, `{section}` stringified to regex `[0-9A-Za-z.\-]+`; any other char → reject with clear error.
- Rate limit: 60 req/min enforced client-side.
- Network failure: exponential backoff on 5xx; circuit-break after 10 consecutive failures.
- Mount unavailability: fail-closed with explicit "mount unreachable" message; checkpoint last-known state.
- Partial-write: atomic rename for L1 text + checkpoint.
- API schema drift: version-pinned client; failed-schema-validation → abort + diagnostic.

**Threat tests:**
- `test_path_traversal_in_section_id_rejected` (inputs like `../evil`)
- `test_null_byte_in_section_id_rejected`
- `test_rate_limit_60_per_min`
- `test_exponential_backoff_on_503`
- `test_circuit_breaker_after_10_failures`
- `test_mount_unreachable_fails_closed`
- `test_atomic_l1_write_on_crash`
- `test_api_schema_mismatch_aborts`

---

## AC ↔ Test Map

Every acceptance criterion is covered by at least one test; AC listed in order:

| AC | Covering test(s) |
|---|---|
| All tests pass | all listed |
| Title-30 end-to-end ≥1000 sections | `test_title30_e2e_minimum_sections` (against recorded fixture) |
| Title-33 end-to-end ≥1000 sections | `test_title33_e2e_minimum_sections` |
| `cfr-registry.yaml` git-tracked | `test_registry_schema_validates` |
| `/mnt/ace/CFR/` populated | integration test (skipped if mount unreachable with clear message) |
| Regulatory wiki CLAUDE.md + overview pages | `test_regulatory_claude_md_schema` (proper schema validation, not grep) + `test_overview_page_frontmatter_has_baseline_floor` |
| Quarterly cron first-Sun of Jan/Apr/Jul/Oct | `test_cron_schedule_is_first_sunday_quarterly` (parses crontab into concrete dates) |
| `--resume` | `test_resume_skips_completed_sections` + others |
| Rate limit respects 60/min | `test_rate_limit_60_per_min` |
| sha256 identity | `test_section_doc_key_*` + `test_wiki_page_doc_key_*` |
| Path safety | `test_path_traversal_*` + `test_null_byte_*` |

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2395-ecfr-ingestion.md` |
| Ingest script | `scripts/data/doc_intelligence/ingest_cfr.py` |
| eCFR client | `scripts/data/doc_intelligence/ecfr_client.py` |
| Normalization | `scripts/data/doc_intelligence/cfr_normalize.py` |
| Checkpoint module | `scripts/data/doc_intelligence/cfr_checkpoint.py` |
| Path sanitization | `scripts/data/doc_intelligence/cfr_path_safe.py` |
| Tests + fixtures | `tests/data/doc_intelligence/test_*` + `tests/fixtures/ecfr/*.json` |
| Registry | `data/document-index/cfr-registry.yaml` |
| Wiki domain | `knowledge/wikis/regulatory/CLAUDE.md`, `knowledge/wikis/regulatory/wiki/index.md`, `wiki/cfr-title-30.md`, `wiki/cfr-title-33.md` |
| Cron wiring | `config/scheduled-tasks/schedule-tasks.yaml` |

No `.gitignore` modification (absolute `/mnt/ace/` paths are already outside repo; the no-op fix is removing the item from v1).

---

## Deliverable

A resumable, path-safe CFR ingestion pipeline with `sha256:` identity, §4-compliant flow, and first delivery of Titles 30 + 33 into a new `regulatory` wiki domain.

---

## Pseudocode (v2 — fixes undefined-`part` bug)

```
function ingest_title(title_num, edition_date):
    checkpoint = load_or_init_checkpoint(title_num)
    if checkpoint.status == "completed" and checkpoint.edition_date == edition_date:
        log "title {title_num} already complete for edition {edition_date}"; return

    structure = ecfr_api.get_title_structure(title_num, edition_date)
    # Structure shape: { parts: [ { number, sections: [ { number, ... } ] } ] }

    for part in structure.parts:
        part_num = sanitize_path(part.number)
        if checkpoint.last_completed_part and int(part.number) < int(checkpoint.last_completed_part):
            continue  # fully skipped, resume
        for section in part.sections:
            section_num = sanitize_path(section.number)
            if already_completed(checkpoint, part.number, section.number):
                if not l1_file_exists(title_num, part_num, section_num):
                    # storage desync — re-fetch
                    pass  # fall through to ingest
                else:
                    continue
            text = rate_limited(ecfr_api.get_section_text, title_num, part.number, section.number)
            normalized = cfr_normalize.run(text)
            doc_key = "sha256:" + sha256(normalized)
            prior = cfr_registry.find(title_num, part.number, section.number)
            if prior:
                if prior.doc_key != doc_key:
                    mark prior as status=superseded; emit new entry status=indexed
                else:
                    continue
            else:
                emit new entry status=indexed
            atomic_write_l1(title_num, part_num, section_num, text)
            update_checkpoint(title_num, part.number, section.number)

    write_checkpoint(status=completed)
    promote_title_overview(title_num)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/doc_intelligence/ingest_cfr.py` | Main pipeline |
| Create | `scripts/data/doc_intelligence/ecfr_client.py` | API client |
| Create | `scripts/data/doc_intelligence/cfr_normalize.py` | Normalization |
| Create | `scripts/data/doc_intelligence/cfr_checkpoint.py` | Checkpoint module |
| Create | `scripts/data/doc_intelligence/cfr_path_safe.py` | Path sanitization |
| Create | `tests/data/doc_intelligence/test_*.py` | TDD suite |
| Create | `tests/fixtures/ecfr/*.json` | Recorded API responses |
| Create | `data/document-index/cfr-registry.yaml` | Initial empty registry |
| Create | `knowledge/wikis/regulatory/CLAUDE.md` + `wiki/index.md` + `cfr-title-{30,33}.md` | New wiki domain |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Quarterly first-Sunday schedule |

---

## Acceptance Criteria

- [ ] All tests pass
- [ ] Titles 30 + 33 ingested end-to-end with ≥1000 sections each
- [ ] `cfr-registry.yaml` valid + git-tracked
- [ ] `regulatory/` wiki domain with CLAUDE.md + 2 Title overview pages
- [ ] Quarterly first-Sunday cron entry parses and schedules correctly (test)
- [ ] `--resume` recovers from crash mid-title
- [ ] Rate limit honored
- [ ] Path safety tests pass
- [ ] §3 identity contract enforced
- [ ] §4 flow map documented in plan + verified by test
- [ ] Review artifacts posted

---

## Adversarial Review Summary

| Provider | Verdict | Key findings | Artifact |
|---|---|---|---|
| Claude v1 | MINOR | 5 self-review fixes | `2026-04-20-plan-2395-claude.md` |
| Codex v1 | MAJOR | unverified deps, resumability, flow, identity, schema, scope, threats, .gitignore no-op | `2026-04-20-plan-2395-codex.md` |
| Gemini v1 | MAJOR | **pseudocode bug (undefined `part`)**, checkpoint undefined, L1 desync | `2026-04-20-plan-2395-gemini.md` |
| Claude v2 | PENDING | — | — |
| Codex v2 | PENDING | — | — |
| Gemini v2 | PENDING | — | — |

---

## Risks and Open Questions

- **Risk:** Full Title-30 pull ≥30 min; cron on a laptop may suspend. Mitigation: checkpoint on shared mount; dev-primary runs cron.
- **Risk:** eCFR API schema drift. Mitigation: pinned client + recorded fixtures + fail-closed.
- **Open:** Title-40/46/49 delivery — file follow-on issue after #2395 closes, reusing the same pipeline.
- **Open:** XML retention (structured hierarchy) — follow-on.

---

## Complexity: T3
