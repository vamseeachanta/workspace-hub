# Plan for #2375: feat(knowledge): normalize WRK completions into structured seeds and wiki-candidate corpus

> **Status:** draft — PLAN DRAFT — NOT APPROVED
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2375
> **Review artifacts:** scripts/review/results/2026-04-29-plan-2375-claude.md | ...-codex.md | ...-gemini.md
> **Prior draft:** docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md (superseded by this plan; path corrections and prompt-aligned artifact routing applied)

---

## Resource Intelligence Summary

<!-- RETRIEVAL CONTRACT (per #2208):
     Issue labels: cat:data-pipeline, cat:harness, domain:knowledge-management
     Required bundles: Data Pipeline + Harness + Knowledge/Intelligence (union)
     Source count: 9 distinct sources (≥3 required) -->

### Existing repo code
- Found: `knowledge-base/wrk-completions.jsonl` — 420 records (332 KB, mtime 2026-03-25), three source cohorts: `synthesize-archive` (389), `memory-migration` (21), `capture-wrk-summary` (10). All records have `type: wrk`.
- Found: `scripts/knowledge/synthesize_archive.py` — upstream backfill that produces structured records (id/type/category/subcategory/title/archived_at/source/mission/patterns/follow_ons) from WRK archive frontmatter. #2375 normalizes downstream of this, not a replacement.
- Found: `scripts/knowledge/capture-wrk-summary.sh` — append-only hook; same structured field set as synthesize-archive. Uses `flock` on `wrk-completions.jsonl.lock`. This is the live append path that must be extended with YAML co-write.
- Found: `scripts/knowledge/categorize_uncategorized.py` — regex `RULES[]` list (49 rules, priority-order, first-match-wins) mapping lowercased title → `(category, subcategory)`. This plan reuses these rules verbatim for the memory-migration cohort.
- Found: `knowledge-base/index.jsonl` — query cache rebuilt from structured sources. Per #894 architecture, JSONL is cache; YAML seed is authoritative.
- Found: `knowledge/seeds/` — existing seed files: `career-learnings.yaml` (entries[] schema), `mooring-failures-lng-terminals.yaml`, `maritime-law-cases.yaml`, `maritime-liabilities.yaml`, `naval-architecture-resources.yaml`, `schema.md`. The `entries[]` schema is the WRK target.
- Found: `docs/archive-synthesis-report.yaml` — report artifact from `synthesize_archive.py --report-only`, categorizes 410+ WRKs. This plan adds a normalization report alongside it, not replacing it.
- Found: `scripts/knowledge/tests/test_synthesize_archive.py` (465 lines) — pytest harness for upstream backfill. Establishes the testing pattern this plan extends.
- Gap: no `knowledge/seeds/wrk-completions.yaml` file exists today. Must build.
- Gap: no script normalizes the 21 `memory-migration` records; they carry only `{id, type, source, raw}`.
- Gap: no wiki-candidate corpus or schema exists. `rg -l 'wiki-candidate'` returns only prose references.
- Gap: no append-flow that keeps YAML seed in sync after JSONL append.
- Gap: `knowledge/seeds/schema.md` documents only the resource-catalog variant, not the `type: wrk` entries variant.
- Gap: no `docs/document-intelligence/wrk-seed-policy.md` append-flow policy.

### Standards
Not applicable. Labels `cat:data-pipeline`, `cat:harness`, `domain:knowledge-management` — no engineering standards exercised, no calc constants emitted. `.claude/rules/calc-citation-contract.md` does not apply. `.claude/rules/coding-style.md` (relative paths via `${REPO_ROOT}` / `git rev-parse --show-toplevel`) and `.claude/rules/patterns.md` (Level-2 script enforcement) do apply.

### LLM Wiki pages consulted
- No wiki pages consumed by this plan. Wiki-candidate routing identifies *target* wiki domains by category rule, not by reading existing wiki content. Cross-linking happens at promotion time, not at normalization time.

### Documents consulted
- Issue [#2375](https://github.com/vamseeachanta/workspace-hub/issues/2375) body — defines deliverables: structured seed artifact(s), raw→normalized mapping/report, wiki-candidate projection, append/update guidance.
- Parent [#2205](https://github.com/vamseeachanta/workspace-hub/issues/2205) (CLOSED) — operating model. WRK completions are L3 durable knowledge; raw `memory-migration` strings are L2 transient residue. Normalization moves them to L3; wiki-candidate projection is the L3→L4 promotion-readiness signal.
- [#2374](https://github.com/vamseeachanta/workspace-hub/issues/2374) (OPEN) — sibling: transient-promotion candidate queue from handoffs/review artifacts. Sources from text-Markdown artifacts. Both emit a candidate ledger with shared status vocabulary (`candidate`/`reviewed`/`promoted`/`rejected`) so a unified review pass is possible.
- [#2370](https://github.com/vamseeachanta/workspace-hub/issues/2370) (OPEN) — sibling: closed-issue promotion ledger for `cat:engineering*`. Shares the same qualitative promotion dimensions (reusable methodology, decision durability, evidence richness) but uses a 4-dimension × 0-5 weighted composite scoring system, whereas this plan uses a simpler 0..3 binary-increment rubric. Both produce `wiki_target_domain` + extend-vs-create recommendation. Score normalization will be required for any future unified ledger merge.
- [#103](https://github.com/vamseeachanta/workspace-hub/issues/103) (OPEN) — archive synthesis + knowledge backfill. `synthesize_archive.py` already implements that backfill; #2375 is the normalize-and-project follow-on, explicitly framed as additive per issue body acceptance criterion 4.
- [#894](https://github.com/vamseeachanta/workspace-hub/issues/894) (CLOSED) — knowledge-persistence architecture. Proposed `knowledge/seeds/wrk-completions.yaml` schema and the `documents_read[]` field. #2375 implements that proposal.
- `docs/plans/2026-04-01-knowledge-persistence-architecture.md` lines 126-175 — defines the proposed `entries[]` schema for `type: wrk` (id, category, subcategory, title, completed_at, commit, artifacts, tests, documents_read, gh_issue, patterns, follow_ons). #2375 adopts this and extends with wiki-candidate scoring fields.
- [#2209](https://github.com/vamseeachanta/workspace-hub/issues/2209) (CLOSED) — durable-vs-transient boundary. WRK completions are durable (post-archive); YAML seed = durable surface, JSONL = rebuildable cache.
- Prior draft: `docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md` — thorough design with `scripts/knowledge/normalize_wrk_completions.py` and `scripts/knowledge/build_wiki_candidates.py` split. This plan consolidates into a single normalizer with integrated wiki-candidate projection, and aligns artifact paths per the prompt-specified architecture.

### Gaps identified
- No `knowledge/seeds/wrk-completions.yaml` seed file — must build.
- No raw→structured mapping for the 21 `memory-migration` records — must build.
- No normalization report (field-fill rates, unrecoverable list) — must build.
- No wiki-candidate schema or corpus — must define and build.
- No wiki-candidate scoring rule — must define (inspired by #2370 promotion dimensions but uses a simpler 0..3 binary-increment rubric; see Pseudocode § `score_candidate`).
- No wiki-candidate projection at `data/document-index/wrk-wiki-candidates.yaml` — must build.
- No append-flow that keeps YAML in sync with JSONL — must extend `capture-wrk-summary.sh`.
- No append-flow policy doc at `docs/document-intelligence/wrk-seed-policy.md` — must write.
- No schema-doc update to `knowledge/seeds/schema.md` for the `type: wrk` variant — must update.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29T05:30:00Z via `gh issue view`):
- `#2375` — OPEN — feat(knowledge): normalize WRK completions into structured seeds and wiki-candidate corpus
- `#2205` — CLOSED — parent operating model
- `#2374` — OPEN — sibling transient-promotion candidate queue
- `#2370` — OPEN — sibling closed-issue promotion ledger
- `#103`  — OPEN — WRK-1332: Archive synthesis + knowledge backfill (synthesize-archive.py)
- `#894`  — CLOSED — WRK-1105: Knowledge persistence architecture

**File existence** (verified 2026-04-29):
- EXISTS: `knowledge-base/wrk-completions.jsonl` (420 records, 332016 bytes, mtime 2026-03-25)
- EXISTS: `knowledge-base/index.jsonl`
- EXISTS: `scripts/knowledge/synthesize_archive.py`
- EXISTS: `scripts/knowledge/capture-wrk-summary.sh`
- EXISTS: `scripts/knowledge/categorize_uncategorized.py` (49 RULES)
- EXISTS: `scripts/knowledge/tests/test_synthesize_archive.py` (465 lines)
- EXISTS: `knowledge/seeds/career-learnings.yaml` (entries[] schema, type: career)
- EXISTS: `knowledge/seeds/schema.md` (resource-catalog variant only)
- EXISTS: `docs/plans/2026-04-01-knowledge-persistence-architecture.md`
- EXISTS: `docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md` (prior draft)
- EXISTS: `docs/document-intelligence/intelligence-accessibility-map.md`
- MISSING (new — this plan creates): `knowledge/seeds/wrk-completions.yaml`
- MISSING (new — this plan creates): `data/document-index/wrk-wiki-candidates.yaml`
- MISSING (new — this plan creates): `scripts/knowledge/normalize_wrk_seeds.py`
- MISSING (new — this plan creates): `scripts/knowledge/tests/test_normalize_wrk_seeds.py`
- MISSING (new — this plan creates): `docs/reports/wrk-completions-normalization-report.md`
- MISSING (new — this plan creates): `docs/document-intelligence/wrk-seed-policy.md`

**Source-cohort breakdown** (verified 2026-04-29 via inline Python):
```
total=420
sources={'synthesize-archive': 389, 'memory-migration': 21, 'capture-wrk-summary': 10}
memory-migration keys=['id', 'raw', 'source', 'type']
synthesize-archive keys=['archived_at', 'category', 'follow_ons', 'id', 'mission', 'patterns', 'source', 'subcategory', 'title', 'type']
capture-wrk-summary keys=['archived_at', 'category', 'follow_ons', 'id', 'mission', 'patterns', 'source', 'subcategory', 'title', 'type']
memory-migration: 21 total, 21 regex-parseable
```

**Memory-migration regex pattern** (verified 2026-04-29):
```
Pattern: ^- \*\*(WRK-\d+) ARCHIVED\*\*(?: \(([0-9a-f]+)\))?:\s*(.+)$
Result: 21/21 records match — zero unparseable raw records.
```

**Gap proofs**:
- `ls knowledge/seeds/wrk-completions.yaml 2>&1` → "No such file or directory"
- `ls data/document-index/wrk-wiki-candidates.yaml 2>&1` → "No such file or directory"
- `ls scripts/knowledge/normalize_wrk_seeds.py 2>&1` → "No such file or directory"
- `ls docs/document-intelligence/wrk-seed-policy.md 2>&1` → "No such file or directory"

<!-- Verification: 9 distinct sources: issue body + #2205 + #2374 + #2370 + #103 + #894 + persistence-arch plan + #2209 + prior draft = 9 (≥3 required). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md |
| Prior draft (superseded) | docs/plans/2026-04-26-issue-2375-wrk-completions-normalize-seeds.md |
| Normalizer + wiki-candidate projection | scripts/knowledge/normalize_wrk_seeds.py |
| Normalized seed (authoritative) | knowledge/seeds/wrk-completions.yaml |
| Wiki-candidate corpus | data/document-index/wrk-wiki-candidates.yaml |
| Normalization report | docs/reports/wrk-completions-normalization-report.md |
| Append-flow policy | docs/document-intelligence/wrk-seed-policy.md |
| Schema doc update | knowledge/seeds/schema.md |
| Tests | scripts/knowledge/tests/test_normalize_wrk_seeds.py |
| Append-hook update | scripts/knowledge/capture-wrk-summary.sh |
| Plan review — Claude | scripts/review/results/2026-04-29-plan-2375-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-29-plan-2375-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-29-plan-2375-gemini.md |
| Plans index update | docs/plans/README.md |

---

## Scope

### In scope
1. **Normalize all 420 JSONL records** into a structured `knowledge/seeds/wrk-completions.yaml` using the `entries[]` schema defined by #894 architecture plan.
2. **Parse memory-migration cohort** (21 records): regex-extract `title`, `commit`, `context` from `raw` field; assign `category`/`subcategory` via `categorize_uncategorized.RULES`.
3. **Field-rename structured cohorts** (399 records): map `archived_at→completed_at`, `mission→context`; preserve all other fields.
4. **Generate wiki-candidate projection** at `data/document-index/wrk-wiki-candidates.yaml`: score each normalized entry on a 0..3 rubric, emit entries scoring ≥2 with `wiki_target_domain` + `extend_or_create` recommendation.
5. **Produce normalization report** at `docs/reports/wrk-completions-normalization-report.md`: per-cohort record counts, field-fill rates per field, and an explicit unrecoverable section.
6. **Write append-flow policy** at `docs/document-intelligence/wrk-seed-policy.md`: how new WRK completions enter the YAML seed structured-by-default.
7. **Extend `capture-wrk-summary.sh`** to co-write YAML seed entry inside the existing `flock` critical section after JSONL append.
8. **Update `knowledge/seeds/schema.md`** to document the `type: wrk` entries variant and the wiki-candidate schema.

### Out of scope
- **#103 backfill re-run** — `synthesize_archive.py` is the upstream; this plan consumes its output, not replaces it.
- **#2374 transient-promotion queue** — separate source surface (handoffs/review artifacts), separate plan.
- **#2370 closed-issue ledger** — separate source surface (closed engineering issues), separate plan.
- **Auto-promotion to wiki** — this plan produces *candidates*; actual promotion is governed by #2236 workflow.
- **`gh_issue` backfill** — cross-referencing WRK IDs to GitHub issues is a follow-on. The field exists (nullable) at v1.
- **JSONL→YAML reconciliation cron** — a follow-on concern; this plan establishes the YAML and the append hook.
- **Index rebuild integration** — updating `build-knowledge-index.sh` to read from YAML seed is a follow-on.

### Dependencies
- `synthesize_archive.py` and `capture-wrk-summary.sh` must remain stable during implementation (read, not modify their core logic).
- `categorize_uncategorized.RULES` must be importable as a module-level constant (already is).
- The `entries[]` schema from #894 architecture plan is the normative reference.

---

## Deliverable

A normalized `knowledge/seeds/wrk-completions.yaml` seed (entries[] schema, all 420 records — including the 21 raw memory-migration records that today carry only `{id, raw}`), a derived `data/document-index/wrk-wiki-candidates.yaml` wiki-candidate corpus with routing and scoring, a normalization report, an append-flow policy document, and a hook extension so new completions enter the YAML seed structured-by-default.

---

## Pseudocode

### `normalize_wrk_seeds.py`
```
function main():
    repo = git_root()
    jsonl_in  = repo / "knowledge-base/wrk-completions.jsonl"
    yaml_out  = repo / "knowledge/seeds/wrk-completions.yaml"
    wiki_out  = repo / "data/document-index/wrk-wiki-candidates.yaml"
    report    = repo / "docs/reports/wrk-completions-normalization-report.md"

    records  = load_jsonl(jsonl_in)        # 420 records, three source cohorts
    # classify() imported from categorize_uncategorized (handles lowercasing internally)

    entries  = []
    stats    = {"total": 0, "by_source": Counter(), "fields_filled": Counter(),
                "unrecoverable": []}

    for rec in records:
        stats["total"] += 1
        stats["by_source"][rec["source"]] += 1

        if rec["source"] == "memory-migration":
            entry = normalize_raw_record(rec)           # regex extract title/sha/body
        else:
            entry = normalize_structured_record(rec)   # field-rename pass

        for k, v in entry.items():
            if v not in (None, "", [], {}):
                stats["fields_filled"][k] += 1

        if not entry.get("title") and not entry.get("context"):
            stats["unrecoverable"].append(rec["id"])

        entries.append(entry)

    # Sort by ID for stable output
    entries.sort(key=lambda e: wrk_sort_key(e["id"]))

    if not args.dry_run:
        write_yaml_atomic(yaml_out, {"entries": entries})
        build_wiki_candidates(entries, wiki_out)
        write_report(report, stats)

function normalize_raw_record(rec):
    raw = rec["raw"]
    m = re.match(r'^- \*\*(WRK-\d+) ARCHIVED\*\*(?: \(([0-9a-f]+)\))?:\s*(.+)$', raw)
    title_part = m.group(3) if m else raw
    title = title_part.split(" — ")[0].strip(" —`")
    body  = title_part[len(title):].lstrip(" —`")[:500]
    cat, sub = classify(title)  # from categorize_uncategorized import classify
    return {
        "id": rec["id"], "type": "wrk",
        "category": cat, "subcategory": sub,
        "title": title, "completed_at": None,
        "commit": m.group(2) if m else None,
        "source": "memory-migration",
        "context": body,
        "patterns": [], "follow_ons": [],
        "artifacts": [], "tests": None, "documents_read": [], "gh_issue": None,
    }

function normalize_structured_record(rec):
    return {
        "id": rec["id"], "type": "wrk",
        "category": rec.get("category") or "uncategorized",
        "subcategory": rec.get("subcategory") or "",
        "title": rec.get("title", ""),
        "completed_at": rec.get("archived_at"),
        "commit": None,
        "source": rec.get("source"),
        "context": rec.get("mission", ""),
        "patterns": rec.get("patterns", []),
        "follow_ons": rec.get("follow_ons", []),
        "artifacts": [], "tests": None, "documents_read": [], "gh_issue": None,
    }

function build_wiki_candidates(entries, wiki_out):
    candidates = []
    for entry in entries:
        score, reasons = score_candidate(entry)
        if score >= 2:
            candidates.append({
                "source_wrk": entry["id"],
                "source_path": "knowledge/seeds/wrk-completions.yaml",
                "title": entry["title"],
                "wiki_target_domain": route_domain(entry),
                "extend_or_create": "extend" if existing_wiki_page_for(entry) else "create",
                "score": score, "reasons": reasons,
                "patterns": entry.get("patterns", []),
                "status": "candidate",
            })
    candidates.sort(key=lambda c: -c["score"])
    write_yaml_atomic(wiki_out, {
        "generated_at": utcnow_iso(),
        "schema_version": "1.0.0",
        "candidates": candidates,
    })

function score_candidate(entry):
    # Inspired by #2370 promotion dimensions (reusable methodology, decision
    # durability, evidence richness) but uses a simpler 0..3 binary-increment
    # rubric — NOT the same numeric scale as #2370's 4-dimension × 0-5
    # weighted composite.  Any future unified ledger merge across #2370,
    # #2374, and #2375 must normalize scores before comparison.
    score, reasons = 0, []
    if entry.get("patterns"):
        score += 1; reasons.append("has-patterns")
    if entry.get("category") in DURABLE_CATEGORIES:
        score += 1; reasons.append("durable-category")
    if entry.get("artifacts") or entry.get("commit"):
        score += 1; reasons.append("has-evidence")
    return score, reasons

function route_domain(entry):
    cat = entry.get("category", "")
    if cat == "engineering":
        return route_engineering_subdomain(entry.get("subcategory", ""))
    if cat in ("ai-orchestration", "ci", "automation"):
        return "process"
    if cat == "personal":
        return "personal"
    return "general"

# ── Plan-local helper contracts ─────────────────────────────────────────

# Categories whose entries carry long-term reuse value and are strong
# wiki-promotion signals.  Derived from the durable-vs-transient boundary
# defined by #2209.  Implementer may refine this list during TDD; the
# contract is that the set is a module-level constant, not computed at
# runtime.
DURABLE_CATEGORIES = {
    "engineering", "data", "harness", "standards",
}

function route_engineering_subdomain(subcategory):
    # Maps engineering subcategories to wiki target domains.
    # Falls back to the generic "engineering" domain for subcategories
    # without a finer-grained wiki home.
    SUBDOMAIN_MAP = {
        "hydrodynamics": "engineering",
        "orcaflex":      "engineering",
        "pipeline":      "engineering",
        "mooring":       "engineering",
        "cathodic-protection": "engineering",
        "fatigue":       "engineering",
        "drilling":      "engineering",
        "lng":           "marine",
        "metocean":      "marine",
        "cad-fea":       "engineering",
        "standards":     "engineering",
    }
    return SUBDOMAIN_MAP.get(subcategory, "engineering")

function existing_wiki_page_for(entry):
    # Read-only heuristic: checks whether an existing wiki page in
    # knowledge/wikis/*/wiki/ has a title that fuzzy-matches entry["title"].
    # Implementation: glob knowledge/wikis/*/wiki/*.md, parse YAML
    # frontmatter title fields, compare via normalized substring match.
    # Returns the wiki-page path (str) if a match is found, else None.
    #
    # CONTRACT:
    # - Read-only — does NOT create, modify, or promote wiki pages.
    # - May return false negatives (no wiki index exists yet); the
    #   default recommendation is therefore "create" when in doubt.
    # - Used only to set the extend_or_create field on candidates;
    #   actual promotion decisions are made by a human reviewer per
    #   #2236 workflow.
    for page in glob("knowledge/wikis/*/wiki/*.md"):
        if normalize(page.frontmatter.title) in normalize(entry["title"]):
            return page.path
    return None
```

### `capture-wrk-summary.sh` extension
```
# After existing JSONL append (inside flock critical section):
if [[ "${APPENDED:-0}" == "1" ]]; then
  uv run --no-project python "${REPO_ROOT}/scripts/knowledge/normalize_wrk_seeds.py" \
    --append-only --wrk-id "${WRK_ID}" || \
    log_warn "YAML append failed for ${WRK_ID} (non-blocking)"
fi
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/knowledge/normalize_wrk_seeds.py | JSONL → entries[] YAML + wiki-candidate projection + report |
| Create | knowledge/seeds/wrk-completions.yaml | Authoritative seed (entries[] schema, type: wrk, 420 records) |
| Create | data/document-index/wrk-wiki-candidates.yaml | Wiki-candidate corpus with routing, scoring, status |
| Create | docs/reports/wrk-completions-normalization-report.md | Per-cohort field-fill rates and unrecoverable list |
| Create | docs/document-intelligence/wrk-seed-policy.md | Append-flow policy: how new WRKs enter YAML structured-by-default |
| Create | scripts/knowledge/tests/test_normalize_wrk_seeds.py | TDD coverage for normalizer + wiki-candidate builder |
| Modify | knowledge/seeds/schema.md | Document entries[] type: wrk variant + wiki-candidate schema |
| Modify | scripts/knowledge/capture-wrk-summary.sh | Add YAML co-write step inside flock critical section |
| Update | docs/plans/README.md | Add this plan to index |

No engineering-package files (`digitalmodel/`, `assethold/`, `assetutilities/`, etc.) are touched. All work is hub-local under `scripts/knowledge/`, `knowledge/`, `data/document-index/`, and `docs/`.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_normalize_raw_extracts_title | regex extracts title before em-dash from raw string | `{"id":"WRK-637","raw":"- **WRK-637 ARCHIVED** (a9057331): memory compaction — ..."}` | `entry.title == "memory compaction"` |
| test_normalize_raw_extracts_commit | regex captures sha in parens | same record | `entry.commit == "a9057331"` |
| test_normalize_raw_no_completed_at | raw cohort has no timestamp | same record | `entry.completed_at is None` |
| test_normalize_raw_assigns_category | reuses categorize_uncategorized.RULES | title contains "memory compaction" | `entry.category` assigned by RULES (not "uncategorized") |
| test_normalize_raw_unparseable_still_produces_entry | raw record that somehow doesn't match regex | bad fixture `{"id":"WRK-X","raw":"garbage"}` | entry exists with `title=""`, logged in unrecoverable list |
| test_normalize_structured_passthrough | field-rename only: archived_at→completed_at, mission→context | synthesize-archive record | `entry.completed_at == rec["archived_at"]`; `entry.context == rec["mission"]` |
| test_normalize_all_three_cohorts | end-to-end on fixture with one of each cohort | 3-record JSONL | 3 entries, sources preserved, all required keys present |
| test_normalize_writes_atomic_yaml | uses tempfile + os.replace | run on tmp jsonl | output file exists, parses, no `.tmp` leftover |
| test_normalize_idempotent | second run produces byte-identical YAML | run twice on same input | byte-equal outputs |
| test_normalize_dry_run_no_writes | --dry-run flag suppresses writes | --dry-run on tmp | no output yaml/report created |
| test_report_field_fill_rates | report tallies which fields are populated per cohort | mixed JSONL fixture | report contains per-cohort fill-rate rows |
| test_report_lists_unrecoverable_ids | record with no parseable title or context | bad fixture | report Unrecoverable section names that ID |
| test_append_only_mode | --append-only --wrk-id appends one entry | call after JSONL append | yaml grows by 1 entry, no reordering |
| test_wiki_score_threshold | entries with score < 2 are excluded from candidates | low-signal entry | not in candidates output |
| test_wiki_score_full | entry with patterns + durable-category + commit scores 3 | rich entry | `score == 3`, three reasons listed |
| test_wiki_route_engineering | engineering-category entry routes to engineering domain | engineering/hydrodynamics entry | `wiki_target_domain == "engineering"` |
| test_wiki_route_personal | personal-category entry routes to personal domain | personal/household entry | `wiki_target_domain == "personal"` |
| test_wiki_route_process | ai-orchestration/ci/automation categories route to process domain | entry with category="ai-orchestration" | `wiki_target_domain == "process"` |
| test_wiki_route_general_catchall | uncategorized or unknown category falls through to general domain | entry with category="uncategorized" | `wiki_target_domain == "general"` |
| test_wiki_status_default | every candidate starts at status="candidate" | any entry | `status == "candidate"` |
| test_wiki_extend_vs_create | when wiki page exists, recommend "extend" | mocked existing-page lookup | `extend_or_create == "extend"` |
| test_wiki_sorted_by_score_desc | output stable-sorted by score descending | mixed scores | first candidate has highest score |
| test_wiki_min_10_candidates | full corpus produces at least 10 wiki candidates at score≥2 | full 420-record fixture | `len(candidates) >= 10` |
| test_capture_hook_appends_yaml | shell-level: hook writes YAML entry after JSONL append | mocked WRK file | YAML entries[] grows by 1 |
| test_capture_hook_skips_on_dup | hook does NOT touch YAML when JSONL append was skipped | duplicate WRK | YAML unchanged |

---

## Acceptance Criteria

- [ ] `knowledge/seeds/wrk-completions.yaml` exists, contains 420 normalized entries. All entries carry `id`, `type=wrk`, `category`, `subcategory`, `title` populated where evidence exists.
- [ ] Each raw JSONL row produces at least one structured YAML entry, OR is logged in the normalization report's unrecoverable section with a reason. No silent drops.
- [ ] All 21 `memory-migration` records have `title` and (where present) `commit` recovered from regex parsing.
- [ ] All 399 `synthesize-archive` + `capture-wrk-summary` records carry `category`, `subcategory`, `title`, `completed_at`, `context`, `patterns`, `follow_ons` via field rename (no data loss).
- [ ] `data/document-index/wrk-wiki-candidates.yaml` exists with at least 10 high-confidence candidates (score ≥ 2) for the first promotion sweep, assuming the corpus has enough qualifying records.
- [ ] Wiki-candidate corpus includes the `status` vocabulary `{candidate, reviewed, promoted, rejected}` documented inline in the schema.
- [ ] `docs/reports/wrk-completions-normalization-report.md` lists per-cohort record count, field-fill rates per field, and an explicit unrecoverable section. Field-fill report explicitly counts `completed_at` nulls (expected: 21 from memory-migration cohort) and documents this as an accepted deviation from #894's required-field designation — these records have no archival timestamp in the raw source.
- [ ] `docs/document-intelligence/wrk-seed-policy.md` documents the append-flow: how new WRK completions enter the YAML seed structured-by-default, and how the JSONL→YAML relationship works.
- [ ] `knowledge/seeds/schema.md` documents the `type: wrk` entries variant and the wiki-candidate schema.
- [ ] `scripts/knowledge/capture-wrk-summary.sh` co-writes the YAML seed entry inside the existing `flock` critical section after JSONL append (no-op on duplicate).
- [ ] Append flow keeps new completions structured-by-default — verified by the `test_capture_hook_appends_yaml` test.
- [ ] All new tests pass: `uv run pytest scripts/knowledge/tests/test_normalize_wrk_seeds.py -v`.
- [ ] No regression: `uv run pytest scripts/knowledge/tests/ -v` and `bash scripts/knowledge/tests/test-knowledge-scripts.sh` pass.
- [ ] Issue-body acceptance criterion 4 satisfied: this plan is explicitly positioned as a follow-on to `synthesize_archive.py` (#103) and `capture-wrk-summary.sh`, not a duplicate. No overlap with #2374 (different source) or #2370 (different source). Shared status vocabulary and rubric enable future merge.
- [ ] Review artifacts posted to `scripts/review/results/`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (feed14) | MINOR | F1: scoring rubric ≠ #2370; F2: #2374 stale path; F3: undefined helpers |
| Codex | PENDING | (filled after review wave) |
| Gemini | PENDING | (filled after review wave) |

**Overall result:** PENDING (Claude MINOR addressed in feed15 patch; Codex/Gemini pending)

Revisions made based on review:
- **feed15 patch (2026-04-29):** addressed all 3 MINOR findings (F1-F3) and all 4 LOW observations (F4-F7) from Claude feed14 adversarial review. See `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2375-feed15.md` for patch details.

---

## Rollback

This issue creates new files and modifies two existing files (`schema.md`, `capture-wrk-summary.sh`). Rollback strategy:

1. **Delete created files:** `knowledge/seeds/wrk-completions.yaml`, `data/document-index/wrk-wiki-candidates.yaml`, `scripts/knowledge/normalize_wrk_seeds.py`, `scripts/knowledge/tests/test_normalize_wrk_seeds.py`, `docs/reports/wrk-completions-normalization-report.md`, `docs/document-intelligence/wrk-seed-policy.md`.
2. **Revert modifications:** `git checkout HEAD~N -- knowledge/seeds/schema.md scripts/knowledge/capture-wrk-summary.sh` (where N = number of implementation commits).
3. **No data loss risk:** the source `knowledge-base/wrk-completions.jsonl` is never modified by this plan; it is read-only input. The YAML seed and wiki-candidate corpus are generated outputs that can be regenerated from the JSONL.

---

## Risks and Open Questions

- **Risk — silent data loss on memory-migration cohort:** regex must tolerate variations in the legacy raw string (em-dash vs hyphen, no-sha records, missing body). Mitigation: verified 21/21 records match the regex pattern; the normalizer still emits entries with `title=""` for any future non-matching record and logs it as unrecoverable.
- **Risk — JSONL/YAML drift after this lands:** if `capture-wrk-summary.sh` ever runs on a machine where the YAML hook fails silently, the JSONL and YAML diverge. Mitigation: hook is non-blocking but logs to stderr; a follow-up reconciliation script (out of scope) compares JSONL IDs vs YAML IDs and reports drift.
- **Risk — wiki-candidate routing wrong:** initial routing is title/category-driven and may misroute engineering subcategory entries. Mitigation: routing emits a single coarse `wiki_target_domain` (engineering / marine / naval / process / personal / general); finer routing is deferred to the human reviewer at promotion time per #2236 workflow.
- **Risk — seed file size:** 420 entries × ~10 fields × YAML overhead may produce a large file. Mitigation: keep as a single file (matches existing `career-learnings.yaml` convention); revisit sharding only if file exceeds 1 MB.
- **Risk — duplication with #2370 / #2374:** if the wiki-candidate schema diverges from those siblings' candidate schemas, downstream consumers must reconcile formats. Mitigation: this plan adopts the shared status vocabulary `{candidate, reviewed, promoted, rejected}` and shares the same qualitative promotion dimensions (methodology, durability, evidence). **Note:** #2375 uses a 0..3 binary-increment rubric while #2370 uses a 4-dimension × 0-5 weighted composite (range [-1.0, +4.0]). Scores are NOT directly comparable across siblings. Any future unified ledger merge must normalize scores before ranking.
- **Risk — append-hook race:** `capture-wrk-summary.sh` already uses `flock` on the JSONL. The YAML co-write must happen inside the same critical section to avoid races from concurrent terminals. Mitigation: YAML append goes inside the existing `flock` block, not as a separate lock.
- **Risk — `data/document-index/` path convention:** the prior draft used `knowledge-base/wiki-candidates.yaml`. This plan uses `data/document-index/wrk-wiki-candidates.yaml` per the prompt architecture. The `data/document-index/` directory is the established home for projection/ledger artifacts (e.g., `standards-transfer-ledger.yaml`, `online-resource-registry.yaml`). Verify this path choice during approval.
- **Coordination hazard — #2374 references stale wiki-candidate path:** The #2374 plan (`docs/plans/2026-04-27-issue-2374-transient-promotion-candidate-queue.md`, lines 35, 51, 359, 396, 406, 438) references the prior-draft wiki-candidate path `knowledge-base/wiki-candidates.yaml`. This plan moved the artifact to `data/document-index/wrk-wiki-candidates.yaml`. When #2374 advances to implementation, its path references and merge-contract documentation must be updated to match. This is a documentation-only coordination debt — it does NOT block #2375 implementation, but the #2374 plan should be patched before its own `status:plan-approved` gate.
- **Open:** Should `gh_issue` cross-references be best-effort backfilled at normalization time (search closed issues for `WRK-NNN` mentions)? Plan defers this to a follow-on; the field exists, it is `None` at v1.
- **Open:** Should the append-flow policy doc live at `docs/document-intelligence/wrk-seed-policy.md` or at `docs/knowledge/wrk-seed-policy.md`? Plan picks `docs/document-intelligence/` because the operating model (#2205) places knowledge-surface governance there. Flag for user during approval.

---

## Adversarial Review Checklist

Before requesting review, verify:
- [ ] All evidence section entries are verifiable (file paths, issue states, regex results)
- [ ] Scope boundary with #103, #2374, #2370 is explicit and non-overlapping
- [ ] JSONL is read-only input; YAML is generated output (no data loss path)
- [ ] Append-hook extends existing `flock` critical section (no new lock file)
- [ ] Wiki-candidate scoring rubric shares #2370 qualitative dimensions but documents the numeric-scale difference (0..3 binary vs 4-dim × 0-5 weighted)
- [ ] Status vocabulary matches #2374 sibling
- [ ] All 420 records accounted for (no silent drops)
- [ ] Schema update to schema.md covers both variants (resource-catalog and entries/wrk)
- [ ] Memory-migration regex verified against all 21 records (21/21 match)

---

## Complexity: T2

**T2** — one new Python script with integrated wiki-candidate projection, one TDD test harness, one shell-script extension, two new authoritative artifacts (seed + candidate corpus), one new report, one new policy doc, one schema-doc update. Bounded scope: single-shot normalization over an existing 420-record corpus + a deterministic scoring projection. No external network, no new infrastructure, no cross-repo edits, no engineering-package changes.
