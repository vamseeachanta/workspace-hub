# Plan for #2392: feat(knowledge): wiki coverage-gap detector — inventory × wiki diff per discipline

> **Status:** draft (v2 — addresses r1 findings)
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2392
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2392-claude.md | ...-codex.md | ...-gemini.md
> **Note:** supersedes `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` (v1-v9 preserved for review history). This draft intentionally narrows the first wave to a working MVP that can earn approval without another five review rounds.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` — frontmatter parser + `WIKIS_DIR` path anchor; detector will reuse these helpers for wiki-side parsing.
- Found: `scripts/data/document-index/phase-a-index.py` — canonical source for `sha256:`/`md5:` namespacing in `index.jsonl` writers (`content_hash` field shape).
- Found: `scripts/knowledge/doc-key-lookup.py` — existing lookup CLI confirming `doc_key` tooling convention.
- Found: `data/document-index/index.jsonl` — primary indexed-source corpus.
- Found: `data/document-index/standards-transfer-ledger.yaml`, `dde-standards-inventory.yaml`, `online-resource-registry.yaml`, `mounted-source-registry.yaml`, `registry.yaml` — inputs named in issue body.
- Gap: no `scripts/knowledge/detect_wiki_gaps.py` (verified — `ls scripts/knowledge/*gap*` returns empty).
- Gap: no `docs/reports/wiki-coverage-gaps/` directory (verified — `ls docs/reports/wiki-coverage-gaps` → not found).

### Standards
Not applicable directly. The detector reads standards-identity fields but does not exercise any engineering standard.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/entities/anode.md` — sample page using slug-style `sources:` (`- dnv-rp-b401`), NOT `doc_key: sha256:...`. Confirms migration gap: most legacy wiki pages cite sources by slug, not canonical `doc_key`. Detector must tolerate this without false-positive gap reporting.
- `knowledge/wikis/marine-engineering/wiki/sources/001.md` — sample source page; frontmatter has `slug`, `title`, `domain`, `ingested`, but no `doc_key` field at present.
- `knowledge/wikis/engineering/wiki/` (77 pages), `naval-architecture` (45), `marine-engineering` (19,186), `maritime-law` (22), `personal` (5) — five domains; gap reports are per-domain per issue body.

### Documents consulted
- Issue body — deliverable: join three inventories against wiki coverage by `doc_key`; per-domain YAML gap reports; unit tests; dry-run; scheduled weekly; <5 min runtime.
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` Section 3.1 — canonical `doc_key = <algorithm>:<hex>`; `sha256:` canonical, `md5:` legacy read-only; Section 4.2 defines `wiki_refs` as an L2-materialized back-link field originating at L3.
- `docs/document-intelligence/intelligence-accessibility-map.md` — source lines 180, 292, 296 describing wiki discoverability + reverse-lookup gap that this detector begins to close by surfacing uncovered sources.
- `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` (v9) — preserved prior draft; three recurring MAJOR findings carried forward as risk controls in this revision:
  1. Join corpus must not over-claim: detector reads only git-tracked metadata; does not scan `/mnt/ace/**` directly.
  2. Wiki-side coverage requires canonical `sha256:` `doc_key`; slug-style `sources:` entries become a distinct diagnostic class, not a coverage match.
  3. Cross-domain doc_key matches are `domain-mismatch`, not `covered`.
- `config/scheduled-tasks/schedule-tasks.yaml` — single source of truth for scheduled tasks; weekly cadence entry will be added there per issue body.

### Gaps identified
- No detector script, no per-domain output directory, no scheduled-task entry.
- No canonical "wiki page uses canonical `doc_key`" count — must be measured during first run and recorded as baseline in `_summary.md`.
- No normalization contract between slug-style `sources:` and canonical `doc_key` — this detector treats them as separate problems (detector emits slug-style coverage as `identity-legacy-slug` diagnostic; does not infer `doc_key` from slug).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2392` — OPEN — "feat(knowledge): wiki coverage-gap detector — inventory × wiki diff per discipline"
- `#2360` — OPEN — doc_key in L3 required-set (soft dep)
- `#2389` — OPEN — `source_doc_key` threading (soft dep)
- `#2366` — referenced in issue body; downstream consumer
- `#2205` — **CLOSED** — parent operating model (re-verified 2026-04-23 via `gh issue view 2205 --json state` → `CLOSED`). Supersedes earlier v1 assertion of OPEN.
- `#2405` — CLOSED — sandbox repo access (unblocks cross-review verification for this detector's plan)

**File existence** (2026-04-23):
- EXISTS: `scripts/knowledge/llm_wiki.py`, `data/document-index/index.jsonl`, `data/document-index/standards-transfer-ledger.yaml`, `data/document-index/dde-standards-inventory.yaml`, `data/document-index/online-resource-registry.yaml`, `data/document-index/mounted-source-registry.yaml`, `data/document-index/registry.yaml`, `config/scheduled-tasks/schedule-tasks.yaml`
- MISSING (this plan creates): `scripts/knowledge/detect_wiki_gaps.py`, `scripts/knowledge/tests/test_detect_wiki_gaps.py`, `docs/reports/wiki-coverage-gaps/` (directory), `docs/reports/wiki-coverage-gaps/_summary.md`
- **EXISTS (corrected in v2)**: `data/design-codes/code-registry.yaml` — verified 2026-04-23 via `ls -la data/design-codes/code-registry.yaml` (3,512 bytes). Schema: top-level `codes:` list with entries carrying `id` (e.g., `DNV-ST-F101`), `title`, `organization`, `our_edition`, `latest_known_edition`, `disciplines`, `repos`, `status`. v1 incorrectly asserted the file did not exist. Promoted to supplemental MVP input (see Inputs section below).

**Gap proofs**:
- `ls scripts/knowledge/*gap*` → no match → confirms detector does not exist.
- `ls docs/reports/wiki-coverage-gaps/ 2>&1` → "No such file or directory".
- `grep -rn "wiki_refs" data/` → empty → confirms materialized `wiki_refs` does not yet exist (separate from this issue — addressed by #2363).

**Source count verification:** 4 distinct sources (issue body + standards-codes contract + accessibility map + prior v9 plan) — minimum met.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2392-wiki-coverage-gap-detector.md` |
| Implementation | `scripts/knowledge/detect_wiki_gaps.py` |
| Tests | `scripts/knowledge/tests/test_detect_wiki_gaps.py` |
| Per-domain gap reports | `docs/reports/wiki-coverage-gaps/<domain-slug>.yaml` |
| Run summary | `docs/reports/wiki-coverage-gaps/_summary.md` |
| Scheduled-task entry | `config/scheduled-tasks/schedule-tasks.yaml` (add task `wiki-coverage-gaps-weekly`) |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2392-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2392-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2392-gemini.md` |

---

## Deliverable

A `scripts/knowledge/detect_wiki_gaps.py` CLI that loads a defined set of source-side inventories, indexes wiki-side coverage by canonical `sha256:` `doc_key`, and emits per-domain YAML gap reports plus a `_summary.md`, scheduled weekly via `schedule-tasks.yaml`.

---

## Identity Join Contract (narrowed — MVP)

- `sha256:<64hex>` is the only positive coverage match key.
- `md5:<hex>` is read-only: source-side records with only `md5:` identity are classified `identity-unresolved` and are NOT reported as true wiki gaps.
- Bare-hex keys (no namespace) are a conformance violation — detector emits a warning and classifies the record `identity-unresolved`.
- Wiki pages without a canonical `sha256:` `doc_key` frontmatter field are NOT coverage providers. They are counted separately in `_summary.md` as `wiki-schema-warning` so the backlog size is visible without inflating coverage.
- Slug-style `sources:` frontmatter (legacy, e.g. `- dnv-rp-b401`) is tallied as `legacy-slug-coverage` diagnostic only — never treated as positive coverage until a separate promotion step lifts it to `doc_key`.

## Source-Record Status Enum (authoritative)

Every normalized source candidate terminates in exactly one of:
- `gap` — canonical `sha256:` key present, no same-domain wiki page covers it
- `covered` — canonical `sha256:` key present AND same-domain wiki page carries the same `doc_key`
- `identity-unresolved` — source lacks a canonical `sha256:` key
- `domain-unresolved` — valid identity but no resolvable wiki domain
- `domain-mismatch` — canonical `doc_key` appears only in a DIFFERENT wiki domain (not `covered`, not `gap`)
- `coverage-conflict` — duplicate wiki pages claim the same `doc_key` (diagnostic-only, not emitted to per-domain YAML)

## Inputs (strict)

Required (detector exits non-zero if missing unless `--allow-missing-required` for development):
- `data/document-index/index.jsonl`

Supplemental (missing → skipped-input diagnostic; not an error):
- `data/document-index/standards-transfer-ledger.yaml`
- `data/document-index/dde-standards-inventory.yaml`
- `data/document-index/online-resource-registry.yaml` (reporting aid — contributes source candidates only for entries carrying canonical `doc_key`)
- `data/design-codes/code-registry.yaml` (promoted in v2) — supplies standards-identity records keyed by publisher-code (`id` like `DNV-ST-F101`). These are NOT canonical `sha256:` `doc_key`s and therefore cannot produce positive coverage matches directly. Instead, they produce `identity-unresolved` source records scoped to the `standards` discipline so the gap size is visible. They will be labeled with a distinct `input_source: code-registry` tag in the per-domain YAML so that downstream consumers can treat them separately from document-index-sourced records. `online-resource-without-canonical-doc_key` is a specific diagnostic class (see TDD test list below).

Reporting-only (never produces source records):
- `data/document-index/registry.yaml`
- `data/document-index/mounted-source-registry.yaml`

Excluded from MVP (explicitly):
- `/mnt/ace/**` — detector does NOT scan the mount directly.
- `docs/reports/**` — never treated as source inventory; this prevents `_summary.md` self-ingestion feedback loops.

---

## Pseudocode

```
def detect_wiki_gaps(args):
    config = load_config(args.config)          # domain map, slug rules, suggested-page template

    # --- Source side ---
    source_records = []
    source_records += read_index_jsonl(REQUIRED_PATHS["index"])
    for path in SUPPLEMENTAL_PATHS:
        if exists(path):
            source_records += read_supplemental(path)
        else:
            summary["skipped_inputs"].append(path)

    normalized = [normalize(rec, config) for rec in source_records]   # applies identity + domain rules
    dedup = dedupe_by_doc_key(normalized)                             # precedence: index > ledger > dde > online

    # --- Wiki side ---
    wiki_index = {}  # (domain_slug, doc_key) -> list[page_path]
    for page_path in iter_wiki_pages(REPO_ROOT / "knowledge/wikis"):
        fm = parse_frontmatter(page_path)
        domain_slug = derive_domain_slug(page_path, fm, config)
        doc_key = fm.get("doc_key")
        if doc_key and is_canonical_sha256(doc_key):
            wiki_index.setdefault((domain_slug, doc_key), []).append(page_path)
        else:
            summary["wiki_schema_warnings"].append((page_path, reason))

    # --- Classify ---
    per_domain = defaultdict(list)
    for rec in dedup:
        status = classify(rec, wiki_index)      # gap / covered / domain-mismatch / coverage-conflict / identity-unresolved / domain-unresolved
        rec.status = status
        if status == "gap":
            per_domain[rec.domain_slug].append(rec)
        summary["counts"][status] += 1

    # --- Emit ---
    if args.dry_run:
        print_summary(summary); return
    ensure_dir(OUT_DIR)
    for domain_slug, recs in per_domain.items():
        write_yaml(OUT_DIR / f"{domain_slug}.yaml", recs)
    write_markdown(OUT_DIR / "_summary.md", summary)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/detect_wiki_gaps.py` | main implementation |
| Create | `scripts/knowledge/tests/test_detect_wiki_gaps.py` | TDD test suite (uses fixtures) |
| Create | `scripts/knowledge/tests/fixtures/wiki-gaps/` | minimal synthetic inventory + wiki tree for unit tests |
| Create | `config/knowledge/detect-wiki-gaps.yaml` | detector config (domain map, slug rules, suggested-page template, truncation defaults). Concrete file — not a stub. Loaded via `--config`; default points here. |
| Create | `docs/reports/wiki-coverage-gaps/` (directory placeholder via `.gitkeep`) | output sink |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | add weekly task entry |
| Modify | `.gitignore` | conditionally ignore large per-domain YAMLs; `_summary.md` remains tracked |
| Update | `docs/plans/README.md` | add plan row |

**`_summary.md` tracking decision (resolved v2)**: `_summary.md` IS git-tracked (it's a baseline-evidence artifact — committed on first scheduled run and updated by each subsequent run). Per-domain `<domain>.yaml` files default to gitignored (via `docs/reports/wiki-coverage-gaps/*.yaml` pattern), with an explicit allowlist for small domains (`engineering`, `naval-architecture`, `maritime-law`) whose gap reports are small enough to review in PRs. The overwrite tension in v1 is resolved by making `_summary.md` a single file the scheduler rewrites atomically on each run — no merge conflict risk because the scheduler is single-writer. The `.gitignore` modification row above captures this.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_sha256_source_without_wiki_is_gap` | canonical source with no wiki match emits `gap` | fixture index.jsonl with one `sha256:abc...` | per-domain YAML entry with `status: gap` |
| `test_sha256_source_with_same_domain_wiki_is_covered` | matching wiki in same domain → `covered` | fixture with matching wiki page | no YAML row; `_summary.md` counts covered |
| `test_md5_only_source_is_identity_unresolved` | legacy `md5:` never produces `gap` | fixture with `md5:deadbeef` only | `status: identity-unresolved` |
| `test_cross_domain_match_is_domain_mismatch` | same `doc_key` in different wiki domain | fixture: source in `marine-engineering`, wiki in `engineering` | `status: domain-mismatch`, not `gap` |
| `test_duplicate_wiki_doc_keys_emit_coverage_conflict` | two wiki pages with same `doc_key` | fixture | `status: coverage-conflict`; summary only; not in YAML |
| `test_bare_hex_source_emits_warning` | bare hex without namespace | fixture | warning logged, `status: identity-unresolved` |
| `test_legacy_slug_sources_not_coverage` | wiki with only slug-style `sources:` | fixture | does not count as coverage; counted as `legacy-slug-coverage` diagnostic |
| `test_dry_run_writes_no_files` | `--dry-run` mode | any fixture | out dir empty; stdout has summary |
| `test_missing_supplemental_yaml_is_skipped_not_fatal` | ledger file absent | fixture | run succeeds; `skipped_inputs` populated |
| `test_domain_slug_kebab_case` | domain normalization | fixture with `Marine Engineering` | output file is `marine-engineering.yaml` |
| `test_summary_md_counts_sum_to_input_size` | classification is total | fixture with N source records | sum of status counts == N |
| `test_docs_reports_never_read_as_input` | guard against feedback loop | fixture places a `_summary.md` from a prior run | not ingested; not counted |
| `test_domain_unresolved_emits_explicitly` | source with valid sha256 but no resolvable domain | fixture with canonical doc_key, wiki domain absent | `status: domain-unresolved`, summary count incremented |
| `test_md5_legacy_read_only_pathway` | md5-only source never upgraded to coverage | fixture with `md5:abc...` | `status: identity-unresolved`, never `covered`, never `gap` |
| `test_dedup_precedence_index_beats_ledger` | dedup precedence order | fixture: same doc_key in both index.jsonl and ledger with different metadata | winner comes from index.jsonl |
| `test_online_resource_without_canonical_doc_key` | online-resource-registry entry lacking `doc_key` | fixture with URL-only entry | `status: identity-unresolved`, `input_source: online-resource-registry`; not emitted as `gap` |
| `test_code_registry_identity_unresolved` | `code-registry.yaml` entries produce identity-unresolved records | fixture `code-registry.yaml` with DNV-ST-F101 | `status: identity-unresolved`, `input_source: code-registry`, `discipline: standards` |
| `test_validate_schedule_passes_after_task_add` | scheduled task integrates cleanly | run `scripts/cron/validate-schedule.py` after modifying schedule-tasks.yaml | exit 0 |

All tests run via `uv run pytest scripts/knowledge/tests/test_detect_wiki_gaps.py -v`.

---

## Acceptance Criteria

- [ ] `scripts/knowledge/detect_wiki_gaps.py` exists, invoked as `uv run scripts/knowledge/detect_wiki_gaps.py`
- [ ] All unit tests pass via `uv run pytest scripts/knowledge/tests/test_detect_wiki_gaps.py -v`
- [ ] Full knowledge-scripts suite `uv run pytest scripts/knowledge/tests/ -v` does not regress
- [ ] `--dry-run` prints summary counts without writing any file
- [ ] First non-dry-run against current corpus completes in under 5 minutes (measured and recorded in `_summary.md`)
- [ ] Per-domain gap YAML has one file per domain with `status: gap` records; every record has `doc_key`, `source_path`, `availability_tier`, `discipline`, `suggested_page`
- [ ] `_summary.md` counts: `gap`, `covered`, `identity-unresolved`, `domain-unresolved`, `domain-mismatch`, `coverage-conflict`, `wiki-schema-warning`, `legacy-slug-coverage`, `skipped_inputs`
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` contains a weekly task `wiki-coverage-gaps-weekly` that invokes the detector
- [ ] `uv run python scripts/cron/validate-schedule.py` exits 0 after the schedule-tasks.yaml edit (attested by test `test_validate_schedule_passes_after_task_add`; verified interactively before commit)
- [ ] `docs/reports/wiki-coverage-gaps/_summary.md` is committed from the first run as baseline evidence
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (r1 cross-review dispatch follows plan push)

Revisions made based on review: none yet.

---

## Risks and Open Questions

- **Risk:** If most wiki pages lack canonical `doc_key` (confirmed by spot-check: `anode.md` uses slug-style `sources:`), the first run will show artificially high gap counts. Mitigation: `_summary.md` separately tallies `legacy-slug-coverage` so the backlog is visible and not conflated with a real coverage gap; the `gap` number is interpreted against that denominator.
- **Risk:** Committing every `<domain>.yaml` could balloon the repo if marine-engineering has 19K uncovered sources. Mitigation: emit top-N per domain by default (configurable; default 500), record the truncation explicitly in `_summary.md`, and defer full-volume publishing to a separate follow-up.
- **Risk:** `/mnt/ace/**` direct scanning is explicitly excluded — if the index.jsonl is stale, gap counts lag. Mitigation: `_summary.md` records `index.jsonl` mtime so freshness is visible.
- **Resolved (v2):** `data/design-codes/code-registry.yaml` DOES exist (3,512 bytes, 2026-02-24). Promoted to supplemental MVP input; records produce `identity-unresolved` status tagged `input_source: code-registry`.
- **Resolved (v2):** `_summary.md` is git-tracked (single-writer scheduler, atomic rewrite); per-domain `<domain>.yaml` default-ignored via `.gitignore` modification; small domains allowlisted for PR review.
- **Open:** Should truncation default to top-500 per domain? Flag for user during approval.
- **Open:** Should the detector emit `wiki_refs` back-links as a side-effect (merging with #2363)? MVP: NO — detector is read-only. Flag for user.

---

## Complexity: T2

New module, multi-input join logic, deterministic classification enum, TDD required, scheduled-task integration, two docs surfaces updated. Not T3 because no architecture/schema change — detector reads existing fields read-only.
