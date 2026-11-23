# Plan for #2364: Execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains

> **Status:** draft (v3 — overlay file pivot resolves Gemini r2 P1; addresses all Claude r2 P2/P3s)
> **Complexity:** T2
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2364
> **Anchor HEAD:** `12b4be834954505ca1e7fc8ad8b20bda34e92baf`
> **Supersedes:** v2 draft (2026-04-24, branch `plan/issue-2364-batch-pack-1` @ `5db2c0cbf`)
> **Review artifacts:** scripts/review/results/20260424T205053Z-plan-2364-v2.md-plan-claude.md | …-gemini.md

---

## Review History

| Version | Date | Reviewer(s) | Verdict | Summary |
|---|---|---|---|---|
| v1 | 2026-04-23 | Claude r1 | **MAJOR** | 2 P1s (forbidden-path scope conflict + un-cited rationalization), 3 P2s, 3 P3s. |
| v2 | 2026-04-24 | Claude r2 + Gemini r2 | **MAJOR / MAJOR** | Claude r2: 3 P2s + 6 P3s (idempotency only at report layer, wall-clock test flakiness, hyphen-path import unspecified, atomicity, `processed_date` tz unspecified, classifier-precedence gaps, stub schema unenumerated, deliverable/AC disagree on maritime-law counting, forbidden-path guard regex). Gemini r2: 1 P1 (regex-based YAML patching is fragile) + 1 P3 (shell pipeline brittleness). |
| v3 | 2026-04-24 | (pending) | — | **Pivots to overlay-file pattern** to resolve Gemini r2 P1 without adding a YAML round-trip dep. Source registry stays untouched; runner emits sibling `online-resource-registry.processed.yaml`. Renames runner + tests to underscore filenames + specifies import mechanism (Claude r2 P2-3). Pins `processed_date` to UTC ISO-8601 (Claude r2 P3). Marks wall-clock perf test `@pytest.mark.perf` (Claude r2 P2-2). Tightens forbidden-path guard to allow-list (Claude r2 P3). Adopts #2471 v3 frontmatter contract for any standards-page citations (project memory). |

**Revisions (v2 → v3):**

- **Gemini r2 P1 (regex YAML patching is fragile) → OVERLAY FILE PIVOT:** The runner will NOT mutate `data/document-index/online-resource-registry.yaml`. Instead it will emit a sibling overlay `data/document-index/online-resource-registry.processed.yaml` containing one entry per processed `id` with `processed: true`, `processed_date: <utc-iso>`, `source_checksum: <sha256-of-source-entry-block>`, and `runner_version: batch-pack-1@v3`. Consumer code reads the overlay if present and source-checksum matches; otherwise falls back to the base registry and logs a staleness warning. Generator is **deterministic and idempotent**: identical inputs produce byte-identical overlay output (sorted-key emission, fixed timestamp source, no `now()` in the file). See "Overlay schema" + "Generator contract" sections.
- **Gemini r2 P3 (shell pipeline brittleness) → PURE-PYTHON DUPLICATE CHECK:** Replace `find | xargs grep` with `pathlib.Path.rglob('*.md')` + line-prefix scan in pure Python. No `subprocess`, no `shell=True`. Behaves identically across Linux/macOS/Windows.
- **Claude r2 P2-1 (idempotency only tested at report layer) → BYTE-LEVEL OVERLAY IDEMPOTENCY:** Acceptance test runs the runner twice on a fixed-input registry and asserts `sha256(overlay_run_1) == sha256(overlay_run_2)`. The pivot makes this trivial because the overlay is the only emitted YAML.
- **Claude r2 P2-2 (wall-clock test flakes on CI) → PERF MARKER:** `test_duplicate_check_wall_clock_under_budget` is decorated `@pytest.mark.perf` and skipped by default; CI runs it only when `RUN_PERF_TESTS=1` is set. Default `pytest` invocation passes regardless of host load.
- **Claude r2 P2-3 (hyphen-path import unspecified) → UNDERSCORE FILENAMES + EXPLICIT MECHANISM:** Runner is renamed `docs/reports/batch_pack_1_runner.py` and tests are renamed `docs/reports/batch_pack_1_runner_tests.py` (underscore — valid Python module names). A `docs/reports/conftest.py` (or local `sys.path.insert(0, str(Path(__file__).parent))` block at the top of the test file) makes the runner importable. **Memory tag:** see `feedback_llm_wiki_hyphen_module_path_pattern` — hyphen-in-module-path is a recurring P1 smell; v3 eliminates it.
- **Claude r2 P3 (registry-patch atomicity) → ATOMIC OVERLAY WRITE:** Overlay write uses temp-file-plus-`os.replace` semantics (`Path(tmp).write_bytes(payload); os.replace(tmp, final)`). A partial-write crash leaves the previous overlay intact (or no overlay → consumers fall back to base). No half-mutated YAML possible since the source is never touched.
- **Claude r2 P3 (`processed_date` tz unspecified) → UTC ISO-8601 SECONDS:** Pinned to `datetime.now(timezone.utc).replace(microsecond=0).isoformat()` → e.g. `2026-04-24T19:42:11+00:00`. Generator-determinism caveat: timestamps are non-deterministic by definition, so the overlay file uses a separate `generated_at` field at the top, NOT per-entry timestamps. Per-entry `processed_date` is set ONCE on first promotion and carried forward unchanged on subsequent runs (read from prior overlay if present). Result: byte-identical overlay across runs once a given entry has been processed.
- **Claude r2 P3 (classifier-precedence gaps) → 3 NEW PRECEDENCE TESTS:** Add `test_classify_law_wins_over_naval_arch` (IMO-keyword notes on `standards.dnv.com`), `test_classify_naval_wins_over_marine` (class-rules notes on a marine-adjacent host), plus the existing `test_classify_law_wins_over_marine`. The precedence chain is `LAW > NAVAL_ARCH > MARINE > engineering` — all three boundaries get a test.
- **Claude r2 P3 (stub frontmatter schema unenumerated) → SCHEMA TABLE + FULL ASSERTION:** Stub schema enumerated below in "Stub frontmatter schema". Test `test_build_stub_frontmatter_matches_wiki_schema` upgraded to assert presence + type for every required key (`title`, `tags`, `added`, `last_updated`, `target_wiki_domain`, `out_of_scope_for_promotion`, `sources`, `classifier_trace`, `duplicate_candidate`).
- **Claude r2 P3 (deliverable vs AC disagree on maritime-law counting) → CATALOG-ONLY THIRD BUCKET:** Maritime-law entries are reported as `catalog-only` — neither in the `sufficient → stub generated` count nor in the `insufficient` count. Total invariant: `sufficient + insufficient + catalog_only == 40`. Both Deliverable and AC restated to match.
- **Claude r2 P3 (forbidden-path guard regex) → ALLOW-LIST GUARD:** Acceptance criterion inverts to allow-list. Concrete check: `git diff --name-only origin/main...HEAD` may contain only paths matching one of: `^data/document-index/online-resource-registry\.processed\.yaml$`, `^data/document-index/batch-pack-1-follow-on-issues\.yaml$`, `^docs/reports/batch_pack_1_runner\.py$`, `^docs/reports/batch_pack_1_runner_tests\.py$`, `^docs/reports/batch-pack-1-api-portal-metadata-stubs\.md$`, `^docs/reports/conftest\.py$`, `^docs/plans/2026-04-23-issue-2364-.+\.md$`, `^docs/plans/README\.md$`. Anything outside this list fails the gate.
- **#2471 v3 frontmatter (project memory `project_wiki_standards_path_decision`):** Stubs that classify as `target_wiki_domain: engineering | naval-architecture | marine-engineering` AND reference a named standards code (DNV, API, IMO, CSA, OCIMF, ABS) record forward-compatible fields `code_id`, `publisher`, `revision` in the stub frontmatter when extractable from notes — even though Batch Pack 1 does not promote pages itself, downstream consumers (#2227, #2207) will inherit them. Field absence is acceptable; presence is structurally validated.

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/knowledge/llm_wiki.py` — read-only context; helper module that downstream wiki ingest may consume.
- `scripts/knowledge/wiki-cross-links.py` — cross-link generator; downstream consumer of Batch Pack 1 output.
- `scripts/knowledge/build-knowledge-index.sh`, `wiki_health_cron.py`, `registry-freshness-check.py` — adjacent tooling, read-only.
- Gap: no `batch_pack_1_runner*` exists in any owned path; will be created.

### Standards
Not directly applicable to the runner itself. Per the new #2471 contract, any stub that references a named standard will carry forward-compatible `code_id`/`publisher`/`revision` fields in frontmatter so downstream wiki-standards ingestion (#2227, #2207) inherits them.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` (83 pages) — five-bucket structure; Batch Pack 1 stubs target `sources/`.
- `knowledge/wikis/engineering/CLAUDE.md`, `naval-architecture/CLAUDE.md`, `marine-engineering/CLAUDE.md`, `maritime-law/CLAUDE.md` — frontmatter schemas; required keys `title`, `tags`, `added`, `last_updated`.
- Marine-engineering wiki has 19,191 pages — duplicate scan must stay frontmatter-only (no body parse).

### Documents consulted
- `docs/reports/llm-wiki-external-source-priority-queue.md` — Queue P1 row 1: 40 entries, metadata-first promotion.
- `docs/reports/llm-wiki-staged-batch-packs.md` — §3.1 path policy; **Owned** = `data/document-index/**`, `docs/reports/**`; **Forbidden** = `config/**`, `.claude/**`, `tests/**`, `scripts/**`.
- `data/document-index/online-resource-registry.yaml` — source registry; 40 entries match `type in {data_api, standard_portal}` (verified). Top-level keys: `generated`, `total_entries`, `summary`, `entries`.
- Epic `#2390`; downstream `#2068`, `#2067`, `#2039`, `#1609`.

### Project memory consulted
- `feedback_llm_wiki_hyphen_module_path_pattern` — hyphen-in-Python-module-path recurs as P1 smell; v3 uses underscore filenames.
- `project_wiki_standards_path_decision` — #2471 sanctions `wiki/standards/` subtree with `code_id`/`publisher`/`revision` frontmatter; v3 stubs forward-adopt these when extractable.
- `data_format_guidelines` — YAML default for agent-facing structured data; overlay is YAML.

### Gaps identified
- No runner under any owned path — will be created at `docs/reports/batch_pack_1_runner.py`.
- All 40 candidates have `tags: None` (verified on HEAD `12b4be8`) — classifier uses host-regex + notes-keyword only.
- "Insufficient notes" threshold not specified upstream — runner introduces `len(notes) ≥ 120` AND ≥1 capability indicator.
- No existing precedent in repo for `<file>.processed.yaml` overlay — v3 establishes the convention; documented inline in the runner module docstring.

### Evidence (embedded verification)

**Anchor:** all references verified against HEAD `12b4be834954505ca1e7fc8ad8b20bda34e92baf` (2026-04-24).

**Issue statuses** (verified 2026-04-24):
- `#2364` — OPEN; `#2390` — OPEN; `#2068`, `#2067`, `#2039`, `#1609` — OPEN; `#2242`, `#2243`, `#2241` — CLOSED.

**File existence** (`git ls-files` on HEAD `12b4be8`):
- EXISTS: `docs/reports/llm-wiki-external-source-priority-queue.md`, `docs/reports/llm-wiki-staged-batch-packs.md` (17,928 bytes), `data/document-index/online-resource-registry.yaml` (3,423 lines).
- EXISTS: all five target-wiki `CLAUDE.md` files.
- MISSING (will be created in **owned** paths): `docs/reports/batch_pack_1_runner.py`, `docs/reports/batch_pack_1_runner_tests.py`, `docs/reports/conftest.py`, `docs/reports/batch-pack-1-api-portal-metadata-stubs.md`, `data/document-index/batch-pack-1-follow-on-issues.yaml`, `data/document-index/online-resource-registry.processed.yaml`.

**Forbidden-paths clause (quoted verbatim from `docs/reports/llm-wiki-staged-batch-packs.md`, §3.1, line 80):**
> `| **Forbidden** | \`config/**\`, \`.claude/**\`, \`tests/**\`, \`scripts/**\` |`

Owned (line 78): `data/document-index/**`, `docs/reports/**`. Read-only (line 79): `knowledge/wikis/**`, `docs/document-intelligence/**`.

**v3 path compliance:** every new artifact lands under Owned. The source registry is not modified — overlay sits beside it under the same Owned `data/document-index/**` subtree.

**`ruamel.yaml` dependency status:** still NOT in `pyproject.toml` / `requirements*.txt` (verified). v3 does not add it. The overlay pivot uses standard `yaml.safe_dump` with `sort_keys=True, default_flow_style=False` — deterministic byte output without round-trip-fidelity needs.

**40-entry survey** (verified 2026-04-24):
- `grep -cE "^\\s+type:\\s+(data_api|standard_portal)" data/document-index/online-resource-registry.yaml` → 40 (31 `data_api` + 9 `standard_portal`).
- All 40 have `tags: None`.
- Sufficient/insufficient split under 120-char + indicator rule: 25 / 13 (recounted v3 — see split table below; minus 2 maritime-law catalog-only).

**120-char threshold dry-run count (v3 — three-bucket model):**

| Bucket | Count | Notes |
|---|---:|---|
| Sufficient (`len(notes) ≥ 120` AND ≥1 indicator AND not maritime-law) | **23 / 40** | promoted as stubs |
| Insufficient | **15 / 40** | routed to follow-on catalog (notes-too-short or no-indicator) |
| Catalog-only (maritime-law: `imo_gisis`, `gisis_imo_org_5db4e8`) | **2 / 40** | enumerated, NOT counted as promoted |
| **Total** | **40 / 40** | invariant |

(v2 reported 25/40 sufficient + 15/40 insufficient with maritime-law double-counted in `sufficient`. v3 separates the 2 maritime-law entries into a third bucket. Counts will be revalidated by the runner during execution; if the live count differs, the runner reports the actual numbers and the AC requires the three-bucket invariant to hold.)

**`noaa_ndbc` fixture id** (verified): line 125 of `online-resource-registry.yaml`.

**Duplicate-check cost (benchmark plan):** marine-engineering wiki has 19,191 pages. Pure-Python frontmatter scan (`pathlib.Path.rglob('*.md')` + read first 30 lines + match `source_id:` prefix). Wall-clock target ≤30 s. Test marked `@pytest.mark.perf`, opt-in via `RUN_PERF_TESTS=1`.

<!-- Source count: 12 (issue body + 11 artifacts/scripts/memory entries) — exceeds ≥3 minimum. -->

---

## Attested Evidence (carried + extended)

| Claim | Evidence | Line / command |
|---|---|---|
| §3.1 forbidden paths include `scripts/**` AND `tests/**` | `docs/reports/llm-wiki-staged-batch-packs.md` | line 80 (verbatim above) |
| §3.1 owned paths include `docs/reports/**` and `data/document-index/**` | same file | line 78 |
| 40 candidate entries have `tags: None` | live registry survey | `yaml.safe_load` + `Counter()` — zero tags across 40 |
| `ruamel.yaml` not in pyproject/requirements | `grep ruamel pyproject.toml requirements*.txt` | no match |
| `noaa_ndbc` exists at line 125 | live registry | `grep -n "noaa_ndbc"` → line 125 |
| Source registry has top-level `entries:` at line 35 | live registry | `grep -n '^entries:'` → line 35 |
| Hyphen-path is a recurring P1 smell | `feedback_llm_wiki_hyphen_module_path_pattern` | memory file, 3 documented recurrences |
| Standards pages get `wiki/standards/` + `code_id`/`publisher`/`revision` frontmatter | `project_wiki_standards_path_decision` (#2471) | memory file |

---

## Artifact Map

| Artifact | Path | Owned? |
|---|---|---|
| This plan | `docs/plans/2026-04-23-issue-2364-batch-pack-1-api-standards-portal-promotion.md` | — (planning tree) |
| Runner | `docs/reports/batch_pack_1_runner.py` (new, **underscore name**) | YES (§3.1 Owned) |
| Runner self-tests | `docs/reports/batch_pack_1_runner_tests.py` (new, **underscore name**) | YES |
| Conftest (sys.path shim) | `docs/reports/conftest.py` (new) | YES |
| Primary output report | `docs/reports/batch-pack-1-api-portal-metadata-stubs.md` (new) | YES |
| Follow-on catalog | `data/document-index/batch-pack-1-follow-on-issues.yaml` (new) | YES |
| **Overlay file (NEW IN v3)** | `data/document-index/online-resource-registry.processed.yaml` (new) | YES (sibling, additive) |
| Source registry | `data/document-index/online-resource-registry.yaml` | **NOT MODIFIED** (read-only in v3) |
| Plan reviews | `scripts/review/results/…-plan-{claude,codex,gemini}.md` | — (review tree) |

---

## Overlay schema

The overlay file `data/document-index/online-resource-registry.processed.yaml` is a sibling to the source registry. Schema:

```yaml
# data/document-index/online-resource-registry.processed.yaml
schema_version: 1
generated_by: batch_pack_1_runner@v3
generated_at: <UTC-ISO-8601-seconds>          # this field IS allowed to vary across runs
source_registry: data/document-index/online-resource-registry.yaml
source_registry_sha256: <sha256 of source file at run time>
processed:
  - id: <registry_entry_id>                    # required, must match an id in source registry
    processed: true                            # required, always true
    processed_date: <UTC-ISO-8601-seconds>     # required, set ONCE on first promotion; carried forward unchanged on re-run
    source_checksum: <sha256 of the source entry block>  # required, used by consumers to detect upstream drift
    target_wiki_domain: <engineering|marine-engineering|naval-architecture|maritime-law>  # required
    out_of_scope_for_promotion: <bool>         # required, true iff target_wiki_domain == "maritime-law"
    classifier_trace: <string>                 # required, e.g. "host:standards.dnv.com → naval-architecture"
    runner_version: batch-pack-1@v3            # required
    # Optional forward-compat #2471 fields:
    code_id: <string>                          # optional, present iff stub references a named standard
    publisher: <string>                        # optional
    revision: <string>                         # optional
```

| Key | Type | Required | Example |
|---|---|---|---|
| `schema_version` | int | yes | `1` |
| `generated_by` | str | yes | `batch_pack_1_runner@v3` |
| `generated_at` | str (ISO-8601 UTC seconds) | yes | `2026-04-24T19:42:11+00:00` |
| `source_registry` | str (relative path) | yes | `data/document-index/online-resource-registry.yaml` |
| `source_registry_sha256` | str (64-hex) | yes | `a1b2…` |
| `processed[].id` | str | yes | `noaa_ndbc` |
| `processed[].processed` | bool | yes | `true` |
| `processed[].processed_date` | str (ISO-8601 UTC seconds) | yes | `2026-04-24T19:42:11+00:00` |
| `processed[].source_checksum` | str (64-hex) | yes | sha256 of the entry block in the source |
| `processed[].target_wiki_domain` | enum | yes | `engineering` |
| `processed[].out_of_scope_for_promotion` | bool | yes | `false` |
| `processed[].classifier_trace` | str | yes | `host:standards.dnv.com → naval-architecture` |
| `processed[].runner_version` | str | yes | `batch-pack-1@v3` |
| `processed[].code_id` | str | optional | `DNV-OS-E301` |
| `processed[].publisher` | str | optional | `DNV` |
| `processed[].revision` | str | optional | `2018-07` |

The `processed:` list is sorted by `id` (lexicographic) for deterministic output.

---

## Generator contract (deterministic + idempotent)

The runner MUST:

1. Read the source registry exactly once. Compute `source_registry_sha256` over the raw bytes of the source file.
2. If the overlay already exists and its `source_registry_sha256` matches: load the prior overlay's `processed` list as a dict keyed by `id`. For any `id` already present, **carry `processed_date` forward unchanged** (this is what makes the per-entry payload byte-identical across runs).
3. For each entry in the 23 sufficient + 2 catalog-only buckets, compute `source_checksum` over the entry block (deterministic — `yaml.safe_dump(entry, sort_keys=True, default_flow_style=False)` then `sha256`).
4. Sort the `processed` list by `id`.
5. Emit the overlay using `yaml.safe_dump(payload, sort_keys=True, default_flow_style=False, allow_unicode=True)`. Write to `<overlay>.tmp` then `os.replace(tmp, final)` (atomic).
6. Insufficient entries are NOT in the overlay; they appear only in `data/document-index/batch-pack-1-follow-on-issues.yaml`.

**Determinism caveat:** `generated_at` (top-level) is non-deterministic by design. The acceptance test for byte-identity strips this top-level field before comparison. Per-entry data is fully deterministic across re-runs once entries are first processed.

```
# Pseudocode (deterministic + idempotent overlay generator)

OVERLAY_PATH = Path("data/document-index/online-resource-registry.processed.yaml")
SOURCE_PATH = Path("data/document-index/online-resource-registry.yaml")

function emit_overlay(processed_entries: List[ProcessedEntry]):
    src_bytes = SOURCE_PATH.read_bytes()
    src_sha = sha256(src_bytes)

    prior = load_prior_overlay(OVERLAY_PATH, expected_src_sha=src_sha)  # {} if missing/stale

    payload_processed = []
    for e in sorted(processed_entries, key=lambda x: x.id):
        prior_date = prior.get(e.id, {}).get("processed_date")
        payload_processed.append({
            "id": e.id,
            "processed": True,
            "processed_date": prior_date or now_utc_iso_seconds(),
            "source_checksum": sha256_of_entry_block(e.id),
            "target_wiki_domain": e.target_wiki_domain,
            "out_of_scope_for_promotion": (e.target_wiki_domain == "maritime-law"),
            "classifier_trace": e.classifier_trace,
            "runner_version": "batch-pack-1@v3",
            **optional_2471_fields(e),  # code_id/publisher/revision when extractable
        })

    payload = {
        "schema_version": 1,
        "generated_by": "batch_pack_1_runner@v3",
        "generated_at": now_utc_iso_seconds(),
        "source_registry": str(SOURCE_PATH),
        "source_registry_sha256": src_sha,
        "processed": payload_processed,
    }

    tmp = OVERLAY_PATH.with_suffix(".yaml.tmp")
    tmp.write_bytes(yaml.safe_dump(payload, sort_keys=True,
                                   default_flow_style=False,
                                   allow_unicode=True).encode("utf-8"))
    os.replace(tmp, OVERLAY_PATH)
```

---

## Consumer-side fallback logic

Any downstream consumer that needs to know "has entry X been processed by Batch Pack 1?" will use this contract:

```
function has_been_processed(entry_id: str) -> Optional[ProcessedRecord]:
    if not OVERLAY_PATH.exists():
        log.warning("Overlay missing; falling back to source registry. "
                    "Batch Pack 1 may not have run yet.")
        return None
    overlay = yaml.safe_load(OVERLAY_PATH.read_bytes())
    src_sha = sha256(SOURCE_PATH.read_bytes())
    if overlay["source_registry_sha256"] != src_sha:
        log.warning("Overlay stale: source_registry_sha256 mismatch. "
                    "Source has changed since overlay was generated. "
                    "Treating overlay as authoritative for present ids; "
                    "missing ids fall back to source registry.")
        # Stale overlay is still consulted — partial-coverage is correct semantics
        # because re-running the runner will refresh checksums and timestamps.
    by_id = {r["id"]: r for r in overlay.get("processed", [])}
    return by_id.get(entry_id)
```

**Fallback rules:**
- Overlay missing → consumer treats all entries as unprocessed; logs warning; does not error.
- Overlay present + checksum match → overlay is authoritative.
- Overlay present + checksum mismatch (stale) → overlay still consulted for present ids (best-effort), missing ids fall back to source. Re-running the runner refreshes the overlay.

This design preserves the property Gemini r2 flagged: **the source registry is never structurally mutated**, so YAML edge cases (commented `- id:` lines, multi-line strings, unexpected indentation) cannot corrupt it. The overlay is generated from `yaml.safe_load` parsed data + `yaml.safe_dump` emission — no regex on YAML text.

---

## Stub frontmatter schema (in the markdown report, per-stub)

Each stub in `docs/reports/batch-pack-1-api-portal-metadata-stubs.md` carries the following YAML frontmatter:

| Key | Type | Required | Notes |
|---|---|---|---|
| `title` | str | yes | derived from entry `name` or URL host |
| `tags` | list[str] | yes | derived from `target_wiki_domain` (e.g. `["sources", "data-api"]`); empty list allowed |
| `added` | str (ISO date) | yes | UTC date of stub generation |
| `last_updated` | str (ISO date) | yes | same as `added` for first emission |
| `target_wiki_domain` | enum | yes | one of `engineering | marine-engineering | naval-architecture | maritime-law` |
| `out_of_scope_for_promotion` | bool | yes | `true` iff `target_wiki_domain == maritime-law` |
| `sources` | list[str] | yes | `[<registry-entry-id>]` |
| `classifier_trace` | str | yes | matched-rule provenance |
| `duplicate_candidate` | str or null | yes | wiki page path if duplicate detected, else `null` |
| `code_id` | str | optional | forward-adopt #2471 if entry references a named standard |
| `publisher` | str | optional | forward-adopt #2471 |
| `revision` | str | optional | forward-adopt #2471 |

Test `test_build_stub_frontmatter_matches_wiki_schema` asserts presence + type for every required key.

---

## Pseudocode (runner top-level)

```
# Classifier sets — derived from live 40-entry survey on HEAD 12b4be8.
# Tag-based rules omitted because every candidate has tags=None.

MARINE_HOSTS = {
    "www.ndbc.noaa.gov", "api.tidesandcurrents.noaa.gov",
    "data.marine.copernicus.eu", "psmsl.org", "nsidc.org",
    "www.gebco.net", "cds.climate.copernicus.eu",
}
NAVAL_ARCH_HOSTS = {"iacs.org.uk", "standards.dnv.com", "www.dnv.com"}
LAW_HOSTS = {"gisis.imo.org"}

MARINE_TERMS = {"marine", "ocean", "wave", "tide", "sea level",
                "bathymetry", "offshore", "subsea", "hydrodynamic",
                "metocean", "wind-farm"}
NAVAL_ARCH_TERMS = {"classification society", "ship rules", "hull",
                    "naval architecture", "ship design", "class rules"}
LAW_TERMS = {"imo", "convention", "solas", "marpol", "unclos",
             "maritime law"}

function classify_domain(entry):
    host = extract_host(entry.url)
    notes_lower = entry.notes.lower()
    # Precedence: LAW > NAVAL_ARCH > MARINE > engineering default.
    if host in LAW_HOSTS or any(t in notes_lower for t in LAW_TERMS):
        return "maritime-law"
    if host in NAVAL_ARCH_HOSTS or any(t in notes_lower for t in NAVAL_ARCH_TERMS):
        return "naval-architecture"
    if host in MARINE_HOSTS or any(t in notes_lower for t in MARINE_TERMS):
        return "marine-engineering"
    return "engineering"

function run_batch_pack_1(registry_path, wiki_root, output_report_path,
                          overlay_path, follow_on_path):
    src = load_yaml(registry_path)
    candidates = [e for e in src["entries"] if e["type"] in {"data_api", "standard_portal"}]
    assert len(candidates) == 40

    # Three-bucket partition:
    sufficient, insufficient, catalog_only = partition_three_bucket(candidates,
        min_chars=120,
        require_any_of=["endpoint", "api", "http", "portal", "coverage",
                        "dataset", "standard", "rule"])
    assert len(sufficient) + len(insufficient) + len(catalog_only) == 40

    grouped = {d: [] for d in ["engineering", "marine-engineering",
                               "naval-architecture", "maritime-law"]}
    processed_records = []
    for entry in sufficient + catalog_only:
        domain = classify_domain(entry)
        stub = build_stub(entry, domain)
        stub.duplicate_candidate = check_duplicate_pure_python(wiki_root, stub.source_id)
        grouped[domain].append(stub)
        processed_records.append(make_processed_record(entry, domain, stub.classifier_trace))

    write_report(output_report_path, grouped, insufficient,
                 counts={"sufficient": len(sufficient),
                         "insufficient": len(insufficient),
                         "catalog_only": len(catalog_only)})
    write_follow_on_catalog(follow_on_path, insufficient)
    emit_overlay(processed_records, overlay_path=overlay_path,
                 source_path=registry_path)
    return summary(...)

function check_duplicate_pure_python(wiki_root: Path, source_id: str) -> Optional[Path]:
    # No subprocess, no shell=True. Pure pathlib + line-prefix check.
    target_line = f"source_id: {source_id}"
    target_listed = f"  - {source_id}"
    for md in wiki_root.rglob("*.md"):
        # Read only first 30 lines (frontmatter region) to bound cost.
        with md.open() as fh:
            for i, line in enumerate(fh):
                if i >= 30:
                    break
                if line.strip() == target_line or line.rstrip() == target_listed:
                    return md
    return None
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/reports/batch_pack_1_runner.py` | runner (underscore name to avoid hyphen-path import smell) |
| Create | `docs/reports/batch_pack_1_runner_tests.py` | self-tests |
| Create | `docs/reports/conftest.py` | adds `docs/reports/` to `sys.path` for pytest collection (single-line shim) |
| Create | `docs/reports/batch-pack-1-api-portal-metadata-stubs.md` | primary output |
| Create | `data/document-index/batch-pack-1-follow-on-issues.yaml` | catalog of insufficient entries |
| Create | `data/document-index/online-resource-registry.processed.yaml` | **overlay (v3 pivot)** — sibling, deterministic, atomic write |
| Update | `docs/plans/README.md` | add index row |

**No writes to:** `config/**`, `.claude/**`, `tests/**`, `scripts/**`, `knowledge/wikis/**`, `data/document-index/online-resource-registry.yaml` (source registry is **read-only** in v3). Allow-list-guarded by AC.

---

## TDD Test List

Tests at `docs/reports/batch_pack_1_runner_tests.py`. `docs/reports/conftest.py` adds the directory to `sys.path` so the test module can `import batch_pack_1_runner` directly. Invocation: `uv run pytest docs/reports/batch_pack_1_runner_tests.py -v`.

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| `test_filter_yields_exact_40_entries` | filter(type ∈ {data_api, standard_portal}) count = 40 | committed registry | `len == 40` |
| `test_partition_three_bucket_invariant` | sufficient + insufficient + catalog_only == 40 | committed registry | invariant holds |
| `test_partition_dry_run_matches_23_15_2` | live partition matches v3 survey | committed registry | sufficient=23, insufficient=15, catalog_only=2 (or runner reports actual + AC requires invariant) |
| `test_partition_notes_quality_threshold_rejects_empty_notes` | notes-length < 120 → insufficient | synth 30-char note | insufficient |
| `test_partition_notes_quality_threshold_accepts_endpoint_mention` | ≥120 chars AND "endpoint" → sufficient | synth 250-char note | sufficient |
| `test_classify_law_wins_over_marine` | IMO host beats marine notes | synth `gisis.imo.org` + "ocean" notes | `maritime-law` |
| `test_classify_law_wins_over_naval_arch` | **NEW (Claude r2 P3)** IMO-keyword notes on `standards.dnv.com` | synth entry | `maritime-law` |
| `test_classify_naval_wins_over_marine` | **NEW (Claude r2 P3)** class-rules notes on a marine-adjacent host | synth entry on `data.marine.copernicus.eu` w/ "class rules" notes | `naval-architecture` |
| `test_classify_marine_host_wins` | NDBC → marine-engineering | synth `www.ndbc.noaa.gov` | `marine-engineering` |
| `test_classify_naval_host_wins` | IACS/DNV → naval-architecture | synth `iacs.org.uk` | `naval-architecture` |
| `test_classify_default_engineering` | no marine/naval/law signal | synth plain entry | `engineering` |
| `test_imo_entries_flagged_out_of_scope` | both real IMO entries `out_of_scope_for_promotion=True` | live (`imo_gisis`, `gisis_imo_org_5db4e8`) | both flagged |
| `test_build_stub_frontmatter_matches_wiki_schema` | **UPGRADED** asserts presence + type for every required key (10 keys) | sample entry | per-key assertion |
| `test_check_duplicate_finds_existing_wiki_page` | finds wiki page with `source_id: noaa_ndbc` (or list-form `- noaa_ndbc`) | fixture wiki tree | returns the path |
| `test_check_duplicate_pure_python_no_subprocess` | implementation does not import `subprocess` (defensive) | inspect runner module | `subprocess` not imported |
| `test_overlay_schema_validates` | overlay matches the schema table | full run | `schema_version`, `generated_at`, `source_registry_sha256`, `processed[]` keys all present + correct types |
| `test_overlay_byte_identical_across_reruns` | **NEW (Claude r2 P2-1 fix at file layer)** running runner twice yields byte-identical overlay (after stripping top-level `generated_at`) | live registry | `sha256(overlay_run1_minus_generated_at) == sha256(overlay_run2_minus_generated_at)` |
| `test_overlay_carries_processed_date_forward` | re-run does NOT bump per-entry `processed_date` | overlay-from-prior-run | per-entry `processed_date` unchanged |
| `test_overlay_atomic_write_no_partial` | crash mid-write leaves prior overlay intact | monkeypatch `os.replace` to raise after partial tmp write | prior overlay unchanged; tmp file removed |
| `test_overlay_processed_date_format_utc_iso_seconds` | `processed_date` matches `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$` | run with mocked `now_utc_iso_seconds` | regex matches |
| `test_source_registry_unchanged` | source registry sha256 before == after run | live registry | sha256 equal |
| `test_consumer_overlay_missing_returns_none_with_warning` | fallback returns `None` + emits warning when overlay absent | overlay deleted | returns `None`, warning logged |
| `test_consumer_overlay_stale_returns_partial_coverage` | overlay with mismatching `source_registry_sha256` is still consulted, missing ids fall back | mutated source bytes | overlay-present ids returned; missing ids return `None` |
| `test_output_report_three_bucket_counts` | report header lists sufficient + insufficient + catalog_only summing to 40 | full run | three counts present + sum == 40 |
| `test_run_is_idempotent_at_report_layer` | re-running produces 0 newly-added stubs | already-promoted state | report says "0 new" |
| `test_no_writes_outside_allow_list` | `git diff` after run touches only allow-listed paths | full run in clean clone | diff matches allow-list regex set |
| `test_duplicate_check_wall_clock_under_budget` | **`@pytest.mark.perf`** — full marine-eng scan ≤30 s | 19,191 pages | wall_clock < 30 s; **skipped unless `RUN_PERF_TESTS=1`** |

---

## Acceptance Criteria

- [ ] All non-perf tests pass: `uv run pytest docs/reports/batch_pack_1_runner_tests.py -v -m "not perf"`
- [ ] Perf test passes when run with `RUN_PERF_TESTS=1 uv run pytest docs/reports/batch_pack_1_runner_tests.py -v -m perf` (run once at plan-approval time, not gating CI)
- [ ] `uv run python docs/reports/batch_pack_1_runner.py` exits 0 and produces `docs/reports/batch-pack-1-api-portal-metadata-stubs.md`, `data/document-index/batch-pack-1-follow-on-issues.yaml`, and `data/document-index/online-resource-registry.processed.yaml`
- [ ] Source registry `data/document-index/online-resource-registry.yaml` is **byte-identical** before and after the run (sha256 verified)
- [ ] Output report header reports three bucket counts summing to exactly 40: `sufficient + insufficient + catalog_only == 40`
- [ ] Each generated stub has `target_wiki_domain ∈ {engineering, marine-engineering, naval-architecture, maritime-law}`
- [ ] Every `maritime-law`-classified stub carries `out_of_scope_for_promotion: true` and is counted in `catalog_only`, NOT `sufficient`
- [ ] Each generated stub records provenance (`sources: [<registry-entry-id>]`) and source URL
- [ ] A **Classifier Trace** section in the report lists the matched rule for every one of the 40 entries; zero `Unclassified`
- [ ] Duplicate check uses pure-Python `pathlib.Path.rglob` (no subprocess, no shell=True); every matched pair listed in a Duplicates section (does NOT block promotion)
- [ ] `data/document-index/batch-pack-1-follow-on-issues.yaml` exists and lists every deferred entry with a reason code (`notes-too-short`, `no-capability-indicator`, `duplicate-suspected`, `classifier-ambiguous`)
- [ ] Overlay file `data/document-index/online-resource-registry.processed.yaml` validates against the schema table; `processed[]` is sorted by `id`; per-entry `processed_date` matches UTC ISO-8601 seconds regex
- [ ] **Byte-identity across reruns**: running the runner twice on the same source registry produces overlay files whose sha256 is equal after stripping the top-level `generated_at` field
- [ ] Allow-list-only file change set: `git diff --name-only origin/main...HEAD` matches only paths in the allow-list (enumerated above in "v3 revisions §forbidden-path guard")
- [ ] Review artifacts for all three providers posted to `scripts/review/results/`
- [ ] No wiki pages promoted — downstream #2039 / #2067 / #2068 consume the report

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (v1) | MAJOR | 2 P1 + 3 P2 + 3 P3 — addressed in v2 |
| Claude (v2) | MAJOR | 3 P2 + 6 P3 — all addressed in v3 (see Review History) |
| Gemini (v2) | MAJOR | 1 P1 (regex YAML) + 1 P3 (shell pipeline) — both resolved by v3 overlay pivot + pure-Python duplicate check |
| Codex (v2) | UNAVAILABLE | upstream regression #2479 — provider unavailable across this batch |
| Claude (v3) | PENDING | (to be filled by v3 fanout) |
| Gemini (v3) | PENDING | (to be filled by v3 fanout) |
| Codex (v3) | PENDING | (subject to #2479 status) |

**Overall result:** PENDING (awaits v3 r1 fanout).

---

## Risks and Open Questions

- **Risk (overlay+source drift):** if the source registry changes between Batch Pack 1 runs and a downstream consumer reads the overlay, the consumer might act on a stale `target_wiki_domain`. Mitigation: per-entry `source_checksum` AND top-level `source_registry_sha256` let the consumer detect drift and warn. Re-running the runner refreshes both.
- **Risk (overlay convention is new):** no prior precedent in the repo for `<file>.processed.yaml`. Documented inline in the runner module docstring; if the convention proves useful, it generalizes (the source-registry sha256 + per-entry checksum pattern is reusable).
- **Risk (classifier precision):** deterministic host + notes classifier may misclassify edge entries. Mitigation: Classifier Trace section in the report; downstream wiki-ingest reviewer can override.
- **Risk (insufficient-notes false-positives):** 120-char + indicator threshold may push adequately-documented entries into the follow-on. Dry-run shows 15/40 insufficient; threshold recorded in the report and adjustable via flag.
- **Risk (duplicate-check on marine-engineering):** 19,191 pages — pure-Python frontmatter scan with 30-s wall-clock budget; perf test gated behind `@pytest.mark.perf` so default CI does not flake.
- **Open:** Should the follow-on catalog auto-file GitHub child issues under #2390 or leave issue creation to a human? Default: NOT auto-filing; user decides at approval.
- **Open:** Should the overlay file be committed by the runner directly, or staged for a human commit? Plan defaults to: runner writes the file and exits; human inspects, reviews, and commits as part of the issue's PR.

---

## Complexity: T2

**T2** — new runner + self-test module + report + follow-on catalog + overlay file, all in owned paths; **source registry is unchanged**; no schema migrations; no new dependencies (uses stdlib `yaml`, `hashlib`, `pathlib`); no network calls.
