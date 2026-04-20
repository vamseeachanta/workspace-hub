# Plan for #2395: eCFR ingestion — v3 (post-iter-2 fixes + embedded evidence)

> **Status:** plan-review (iteration 3 of 3 — final)
> **Complexity:** T3
> **Date:** 2026-04-20 (v3)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2395
> **Prior reviews:** v1 at `5b4c347cd` (Claude MINOR + Codex/Gemini MAJOR); v2 at `27821dafa` (Codex/Gemini MAJOR).

---

## Revision History

- **v1:** initial; convergent P1s: sha256, resume undefined, L1 desync, .gitignore no-op, §4 flow.
- **v2:** added §Identity / §Checkpoint / §Flow Map / §Threat Model. Still MAJOR on (a) desync-repair bug, (b) int() crash on alphanumeric parts, (c) NFS atomicity, (d) namespace ambiguity, (e) §8.1 fields undefined, (f) rate-limit fact incorrect, (g) unverified claims.
- **v3 (this revision):**
  - **M1 fix:** desync-repair bug — introduces `needs_write` flag; correct control flow guarantees `atomic_write_l1` runs whenever L1 file is missing, regardless of registry state.
  - **M1 fix:** alphanumeric part compare — checkpoint comparison uses `(natural_key(part.number), natural_key(section.number))` tuples, not `int()`.
  - **M1 fix:** NFS atomicity — uses `os.replace()` + `os.fsync(dirfd)` + documented fallback when mount is NFS/SMB; checkpoint durability explicitly tested.
  - **M1 fix:** namespace pinned — implementation in **existing** `scripts/data/doc_intelligence/` directory (not `scripts/data/document-index/`).
  - **M1 fix:** §8.1 baseline-floor fields for `regulatory/CLAUDE.md` enumerated explicitly.
  - **Correction:** eCFR actual rate limit is **1,000 req/hour ≈ 16/min**, not 60/min (source: `https://www.ecfr.gov/developers/documentation/api/v1`). All rate-limit tests updated.
  - **M2 fix:** Evidence block embeds actual `gh`/`ls`/`grep` output.

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/data/doc_intelligence/` — **exists** with 30+ scripts; new CFR ingest lives here (iter-2 namespace correction).
- `scripts/data/document-index/phase-a-index.py` — L2 indexing pattern.
- `scripts/data/document-index/provenance.py` — provenance record shape.
- `data/document-index/standards-transfer-ledger.yaml` — confirmed 0 CFR entries.

### Standards
- 30 CFR (BOEM/BSEE), 33 CFR (USCG) — v3 first-delivery scope. 40/46/49 deferred to follow-on.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/CLAUDE.md` — §8.1 example (see #2392 evidence excerpt).

### Documents consulted
- Operating model §3/§4/§7/§8.1.
- eCFR API v1 public documentation: rate limit published as "1,000 requests per hour (about 16 per minute average)".

### Dependency Matrix

| Issue | State | Relationship | Behavior if unshipped |
|---|---|---|---|
| #2205 | CLOSED | authority | — |
| #2373 | OPEN | parallel (non-ACMA standards) | scope-separated |
| #2365 | OPEN | parallel (design-code registry) | no blocking |
| #596 | CLOSED | prior art (extract-url.py) | reference only |

### Gaps identified
- No CFR registry, no `regulatory/` wiki domain, no quarterly CFR refresh.

### Evidence (embedded verification)

**Issue statuses** (2026-04-20T15:50Z):
- `#2205` — **CLOSED**
- `#2373` — **OPEN** — feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion
- `#2365` — **OPEN** — feat(knowledge): promote design-code registry into standards overviews
- `#596` — **CLOSED** — WRK-5041: feat(doc-intel): extract-url.py — internet document extraction pipeline

**File/directory existence:**
```
EXISTS: scripts/data/doc_intelligence/                  (30+ files; v3 lives here)
EXISTS: scripts/data/document-index/phase-a-index.py
EXISTS: scripts/data/document-index/provenance.py
EXISTS: data/document-index/standards-transfer-ledger.yaml
EXISTS: knowledge/wikis/engineering/CLAUDE.md
MISSING (new — this plan creates): knowledge/wikis/regulatory/
```

**Grep proof — no CFR in ledger:**
```
$ grep -c -i "CFR\|30 CFR\|33 CFR" data/document-index/standards-transfer-ledger.yaml
0
```

**eCFR rate limit** — published at https://www.ecfr.gov/developers/documentation/api/v1:
> "Please do not make more than 1,000 requests per hour (about 16 per minute average)"

This is the **correct** rate limit. v1/v2 cited 60/min, which exceeds the published guideline by 4×; v3 caps at 16/min.

---

## Identity Contract (§3)

- Section-level: `sha256:<64-hex>` of normalized text. Canonical.
- Rendered wiki overview page: `sha256:<64-hex>` of page body (frontmatter excluded from hash input to avoid self-reference circularity).
- No md5 in CFR corpus (new content).
- Bare-hex rejected; path-only forbidden.

Tests: `test_section_doc_key_stable`, `test_section_doc_key_changes_on_amendment`, `test_wiki_page_doc_key_excludes_frontmatter`, `test_bare_hex_rejected`.

---

## Cross-Machine Tier Assignment

| Artifact | Path | Tier | Authority |
|---|---|---|---|
| CFR registry | `data/document-index/cfr-registry.yaml` | 1 | authoritative |
| Wiki domain config | `knowledge/wikis/regulatory/CLAUDE.md` | 1 | authoritative |
| Wiki overview pages | `knowledge/wikis/regulatory/wiki/*.md` | 1 | authoritative |
| L1 raw text | `/mnt/ace/CFR/Title-XX/part-NN/section-NN.NN.txt` | 2 | preferred when reachable |
| Checkpoint state | `/mnt/ace/CFR/.checkpoints/title-XX.yaml` | 2 | authoritative for resume |
| Run logs | `logs/ecfr-ingest/run-YYYY-MM-DD.jsonl` | 3 | local-only |

---

## §8.1 Baseline-Floor for `regulatory/CLAUDE.md` (explicit — v3 fix)

New `knowledge/wikis/regulatory/CLAUDE.md` declares these REQUIRED fields for every L3 page:

| Field | Type | Purpose |
|---|---|---|
| `title` | string | Page title |
| `last_updated` | ISO date | Freshness signal |
| `doc_key` | `sha256:<hex>` | §3 identity |
| `source_ref` | string | e.g. `cfr:30:250:250.901` |
| `promoted_from` | `doc_key` | Source registry entry |

Test: `test_regulatory_claude_md_schema_valid_json_schema_check` (uses `pyyaml` + schema validation, not `grep`).

---

## Checkpoint Contract (§7 tier 2, atomicity specified)

**State file:** `/mnt/ace/CFR/.checkpoints/title-{title}.yaml`.

**Schema:** as in v2 (title, edition_date, last_completed_part, last_completed_section, etc.).

**Atomicity on POSIX local filesystems:**
```python
def atomic_checkpoint_write(path, content):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(content); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)  # atomic on POSIX
    dirfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try: os.fsync(dirfd)
    finally: os.close(dirfd)
```

**Atomicity on NFS/SMB:** `os.replace()` is not guaranteed atomic under network failure. Mitigation:
1. Checkpoint is idempotent — re-running from same last-completed-section produces identical output.
2. After resume, run **checkpoint-consistency check**: verify `last_completed_section` actually exists in registry; if mismatch, treat as "checkpoint suspect" and restart from last known-good part.
3. Fast-fail flag `--require-posix-mount` available for reliability-critical runs.

Tests: `test_checkpoint_atomic_write_posix`, `test_checkpoint_recovery_on_mismatch`, `test_posix_mount_flag_fails_closed_on_nfs`.

---

## Flow Map (§4 compliance)

| Flow | Direction | Allowed | Rationale |
|---|---|---|---|
| eCFR API → L1 raw text | external → L1 | ✓ | standard L1 ingest |
| L1 → L2 (cfr-registry.yaml) | ✓ | indexing |
| L2 → L3 (wiki overview) | ✓ | promotion |
| L3 → L5 (via retrieval) | ✓ | consumption |

No forbidden flows: no L5-as-durable-store, no L3↔L5 circular.

---

## Threat Model

**Input surfaces:** eCFR JSON API, writes to `/mnt/ace/CFR/`, new repo files.
**Mitigations:**
- Path sanitization: `title`/`part`/`section` stringified to `^[0-9A-Za-z.\-]+$`; non-conforming → reject.
- Rate limit: **16 req/min** (1,000/hr), honoring published guideline.
- Exponential backoff on 5xx; circuit-break after 10 consecutive failures.
- Atomic writes + NFS fallback (above).
- API schema version-pinned; schema-mismatch fails closed.

**Tests:** `test_path_traversal_rejected`, `test_null_byte_rejected`, `test_rate_limit_16_per_min` (was `_60` in v2 — corrected), `test_backoff_on_503`, `test_circuit_break_after_10_failures`, `test_mount_unreachable_fails_closed`, `test_atomic_l1_write_on_crash`, `test_api_schema_mismatch_aborts`.

---

## AC ↔ Test Map

Every AC mapped:

| AC | Test(s) |
|---|---|
| Tests pass | all listed |
| Title-30 e2e ≥1000 sections | `test_title30_e2e_minimum_sections` |
| Title-33 e2e ≥1000 sections | `test_title33_e2e_minimum_sections` |
| `cfr-registry.yaml` git-tracked + valid | `test_registry_schema_validates` |
| `/mnt/ace/CFR/` populated | integration-test (mount-conditional) |
| `regulatory` wiki created with baseline-floor | `test_regulatory_claude_md_schema_valid_json_schema_check` + `test_overview_page_has_all_required_frontmatter` |
| Quarterly first-Sun cron | `test_cron_schedule_is_first_sunday_quarterly` (parses to concrete dates) |
| `--resume` | `test_resume_skips_completed_sections`, `test_resume_noop_on_completed`, `test_resume_reprocesses_on_edition_bump`, `test_resume_restores_missing_l1_file` (NEW — desync-repair) |
| Rate limit 16/min | `test_rate_limit_16_per_min` |
| §3 identity | identity tests above |
| §4 flow | flow-map tests |
| Path-safety | threat-model tests |
| Alphanumeric parts | `test_natural_key_sort_on_alphanumeric_parts` (NEW — fixes v2 int() bug) |

---

## Pseudocode (v3 — desync-repair + alphanumeric fixes)

```python
def natural_key(s):
    # Split "250a" → ("250", "a"); "1.5001-3" → ("1", ".", "5001", "-", "3")
    # Used for checkpoint-resume comparison; avoids int() crash on alphanumeric parts.
    return tuple(int(x) if x.isdigit() else x for x in re.findall(r'\d+|\D+', s))

def ingest_title(title_num, edition_date):
    checkpoint = load_or_init_checkpoint(title_num)
    if checkpoint.status == "completed" and checkpoint.edition_date == edition_date:
        return "noop-already-complete"

    structure = ecfr_api.get_title_structure(title_num, edition_date)
    for part in structure.parts:
        part_num = sanitize_path(part.number)

        # Natural-key compare (v3 fix: works on alphanumeric parts)
        if checkpoint.last_completed_part and \
           natural_key(part.number) < natural_key(checkpoint.last_completed_part):
            continue

        for section in part.sections:
            section_num = sanitize_path(section.number)

            # v3 desync-repair fix:
            needs_write = False
            already_in_registry = cfr_registry.find(title_num, part.number, section.number)
            l1_exists = l1_file_exists(title_num, part_num, section_num)

            if already_completed_in_checkpoint(checkpoint, part.number, section.number):
                if already_in_registry and l1_exists:
                    continue  # truly complete
                else:
                    needs_write = True  # desync — re-fetch+write even though checkpoint says done
                    log_warning(f"checkpoint desync at {title_num}/{part.number}/{section.number}; repairing")
            else:
                needs_write = True

            if needs_write:
                text = rate_limited(ecfr_api.get_section_text, title_num, part.number, section.number)
                normalized = cfr_normalize.run(text)
                doc_key = "sha256:" + sha256(normalized)
                if already_in_registry and already_in_registry.doc_key != doc_key:
                    mark_superseded(already_in_registry); emit_new(doc_key)
                elif not already_in_registry:
                    emit_new(doc_key)
                atomic_write_l1(title_num, part_num, section_num, text)
                update_checkpoint(title_num, part.number, section.number)

    write_checkpoint(status="completed")
    promote_title_overview(title_num)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/doc_intelligence/ingest_cfr.py` | main (in existing dir) |
| Create | `scripts/data/doc_intelligence/ecfr_client.py` | API client |
| Create | `scripts/data/doc_intelligence/cfr_normalize.py` | normalization |
| Create | `scripts/data/doc_intelligence/cfr_checkpoint.py` | checkpoint (atomic + NFS fallback) |
| Create | `scripts/data/doc_intelligence/cfr_path_safe.py` | path sanitization |
| Create | `scripts/data/doc_intelligence/cfr_natural_key.py` | alphanumeric sort helper |
| Create | `tests/data/doc_intelligence/test_*.py` | TDD |
| Create | `tests/fixtures/ecfr/*.json` | recorded responses |
| Create | `data/document-index/cfr-registry.yaml` | registry |
| Create | `knowledge/wikis/regulatory/{CLAUDE.md, wiki/index.md, wiki/cfr-title-30.md, wiki/cfr-title-33.md}` | new domain |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | quarterly |

---

## Acceptance Criteria

All v2 ACs + v3 corrections:
- [ ] Rate limit enforced at **16 req/min** (corrected from v2's 60/min)
- [ ] Desync-repair path restores missing L1 file (test: `test_resume_restores_missing_l1_file`)
- [ ] Natural-key sort handles alphanumeric parts (test: `test_natural_key_sort_on_alphanumeric_parts`)
- [ ] NFS mount fallback documented and tested
- [ ] `regulatory/CLAUDE.md` declares full baseline-floor schema (validated, not grepped)
- [ ] Implementation in existing `scripts/data/doc_intelligence/` (not `document-index/`)

---

## Adversarial Review Summary

| Provider | Verdict | Artifact |
|---|---|---|
| Claude v1 | MINOR | `2026-04-20-plan-2395-claude.md` |
| Codex v1 / Gemini v1 | MAJOR / MAJOR | `...-codex.md`, `...-gemini.md` |
| Codex v2 / Gemini v2 | MAJOR / MAJOR | `2026-04-20-v2-plan-2395-{codex,gemini}.md` |
| Codex v3 / Gemini v3 | PENDING | — |

---

## Risks and Open Questions

- **Risk:** NFS atomicity edge case. Mitigation: idempotent checkpoint + consistency check on resume + `--require-posix-mount` flag.
- **Open:** Titles 40/46/49 — follow-on issue after #2395 closes.

---

## Complexity: T3
