# Plan for #2364: Execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains

> **Status:** draft (v4 — surgical fixes for Claude r3 + Gemini r3 MAJOR; PyYAML attestation added; partition/classify ordering pinned; `code_id` heuristic specified; consumer is_stale signal added; CLAUDE.md paths reconciled)
> **Complexity:** T2
> **Date:** 2026-04-25
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2364
> **Anchor HEAD:** `12b4be834954505ca1e7fc8ad8b20bda34e92baf`
> **Supersedes:** v3 draft (2026-04-24, branch `plan/issue-2364-batch-pack-1`)
> **Review artifacts (v3):** scripts/review/results/20260425T092133Z-…-plan-claude.md (MAJOR) | scripts/review/results/20260425T093644Z-…-plan-gemini.md (MAJOR)

---

## Review History

| Version | Date | Reviewer(s) | Verdict | Summary |
|---|---|---|---|---|
| v1 | 2026-04-23 | Claude r1 | **MAJOR** | 2 P1s + 3 P2s + 3 P3s. |
| v2 | 2026-04-24 | Claude r2 + Gemini r2 | **MAJOR / MAJOR** | Claude r2: 3 P2s + 6 P3s. Gemini r2: 1 P1 (regex YAML patching) + 1 P3 (shell pipeline). |
| v3 | 2026-04-24 | Claude r3 + Gemini r3 | **MAJOR / MAJOR** | Claude r3: P2 partition/classify ordering ambiguity, P2 `optional_2471_fields` extraction unspecified, P2 stale-overlay consumer needs explicit `is_stale` signal. Gemini r3: P1 "yaml is NOT in stdlib" critique (technically correct — PyYAML is the runtime, not stdlib — though PyYAML is already a direct dep, so the v3 "no new deps" claim still holds; v4 corrects the wording and attests), P3 quoted-source_id false-negative in duplicate check, P3 missing CLAUDE.md path attestation (v3 used wrong sub-path `<wiki>/wiki/CLAUDE.md`; correct is `<wiki>/CLAUDE.md`), P3 pure-Python scan cost on 19,191-page wiki. |
| v4 | 2026-04-25 | (pending) | — | Surgical deltas only — see Revisions (v3 → v4) below. No structural pivot. |

**Revisions (v3 → v4):**

- **Gemini r3 P1 (yaml is NOT in stdlib) → WORDING FIX + ATTESTED EVIDENCE ROW:** Gemini is correct that Python has no stdlib `yaml` module. v3's prose was sloppy. However, PyYAML IS already a direct, pinned project dependency, so the "no new dependencies" claim is preserved. v4 corrects every "stdlib yaml" mention in the plan to read "`yaml.safe_load` / `yaml.safe_dump` from PyYAML 6.0+ (already in `pyproject.toml`, transitively present in all milestone projects)" and adds an `Attested Evidence` row capturing the actual `grep` and `uv pip list` outputs proving the claim. v4 introduces NO new dependencies.

- **Claude r3 P2 (partition/classify ordering ambiguity) → CLASSIFY-FIRST PIPELINE:** v3 pseudocode called `classify_domain` inside the per-entry loop AFTER `partition_three_bucket`, which made `test_partition_three_bucket_invariant` ambiguous (the maritime-law-catalog-only branch depends on knowing the domain at partition time). v4 rewrites the pipeline so `classify_domain` runs ONCE per entry up front, producing a list of `(entry, domain)` tuples. `partition_three_bucket` then consumes those tuples and routes by `(domain == "maritime-law")` for the catalog-only bucket. Maritime-law detection is inside `classify_domain` (it is the first-pass classification rule); partition is a pure routing step over already-classified entries. Test names + invariants restated to match.

- **Claude r3 P2 (`optional_2471_fields(e)` extraction heuristic unspecified) → CONCRETE REGEX HEURISTIC + FIXTURE PAIR:** v4 specifies the heuristic concretely. See "`optional_2471_fields` heuristic" section below. Two new fixtures land in the test list: one positive (entry with notes `"DNV-OS-E301 Rev 2024-04 — mooring safety factors"` extracts `code_id="DNV-OS-E301"`, `publisher="DNV"`, `revision="2024-04"`), one negative (entry with notes containing no recognizable code-id pattern → all three fields ABSENT from frontmatter, not present-as-empty-strings).

- **Claude r3 P2 (stale-overlay consumer needs `is_stale` signal) → CONSUMER CONTRACT CHANGE:** v3 returned `record | None`, which collapsed the "checksum-mismatch / using stale anyway" case into the same return type as the happy path — the consumer could not distinguish. v4 changes the consumer signature to `Tuple[Optional[ProcessedRecord], bool]` where the boolean is `is_stale`. `is_stale=True` iff `overlay["source_registry_sha256"] != sha256(SOURCE_PATH.read_bytes())` at consumer-call time. Default consumer behavior: WARN log + use the record anyway. Downstream consumers (#2039 / #2067 / #2068) MAY elect halt-on-stale semantics; the contract surfaces the signal but does not dictate the policy. New test `test_consumer_returns_is_stale_flag_on_checksum_mismatch` covers this.

- **Gemini r3 P3 (CLAUDE.md path attestation wrong) → PATH RECONCILIATION:** Gemini r3 attested `<wiki>/wiki/CLAUDE.md` (which does NOT exist for any of the four domains). The actual paths are `knowledge/wikis/{engineering,marine-engineering,maritime-law,naval-architecture}/CLAUDE.md` (no `/wiki/` segment). All four files DO exist on HEAD. v4 fixes this in the Resource Intel section + adds an `Attested Evidence` row with the live `git ls-files | grep CLAUDE.md` output as ground truth. No "EXISTS-CHECK PENDING" stub is needed because the four files are present.

- **Gemini r3 P3 (quoted-source_id false-negative) → TOLERANT REGEX:** v3 used literal-string compare (`source_id: noaa_ndbc`). v4 replaces this with a compiled regex `^source_id:\s*"?{re.escape(source_id)}"?\s*$` (anchors, optional surrounding quotes, tolerant whitespace). The list-form `  - {source_id}` check is similarly relaxed to `^\s*-\s*"?{re.escape(source_id)}"?\s*$`. New test `test_check_duplicate_tolerates_quoted_source_id` covers both `'noaa_ndbc'` and `"noaa_ndbc"` forms.

- **Gemini r3 P3 (pure-Python scan cost) → ACKNOWLEDGED, NO ACTION:** v3 already gates this behind `@pytest.mark.perf` with `RUN_PERF_TESTS=1`. The default CI invocation does not run it; `subprocess(rg)` fallback remains an option for the runner if the perf budget is breached during execution (documented in Risks). No code change in v4.

- **Carried from v3:** overlay-file pivot (v2 Gemini P1 fix), pure-Python duplicate check, allow-list path guard, underscore-only Python module names (no hyphen-paths), UTC ISO-8601 `processed_date`, atomic temp-file overlay write, byte-identity-across-reruns AC, three-bucket partition with maritime-law catalog-only.

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/knowledge/llm_wiki.py` — read-only context; helper module that downstream wiki ingest may consume.
- `scripts/knowledge/wiki-cross-links.py` — cross-link generator; downstream consumer of Batch Pack 1 output.
- `scripts/knowledge/build-knowledge-index.sh`, `wiki_health_cron.py`, `registry-freshness-check.py` — adjacent tooling, read-only.
- Gap: no `batch_pack_1_runner*` exists in any owned path; will be created.

### Standards
Not directly applicable to the runner itself. Per the new #2471 contract, any stub that references a named standard will carry forward-compatible `code_id`/`publisher`/`revision` fields in frontmatter so downstream wiki-standards ingestion (#2227, #2207) inherits them. `optional_2471_fields(e)` extraction heuristic specified below.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` (83 pages) — five-bucket structure; Batch Pack 1 stubs target `sources/`.
- `knowledge/wikis/engineering/CLAUDE.md`, `knowledge/wikis/naval-architecture/CLAUDE.md`, `knowledge/wikis/marine-engineering/CLAUDE.md`, `knowledge/wikis/maritime-law/CLAUDE.md` — frontmatter schemas; required keys `title`, `tags`, `added`, `last_updated`. **(v4 path correction: `<wiki-domain>/CLAUDE.md`, NOT `<wiki-domain>/wiki/CLAUDE.md`. Verified via `git ls-files`.)**
- Marine-engineering wiki has 19,191 pages — duplicate scan must stay frontmatter-only (no body parse).

### Documents consulted
- `docs/reports/llm-wiki-external-source-priority-queue.md` — Queue P1 row 1: 40 entries, metadata-first promotion.
- `docs/reports/llm-wiki-staged-batch-packs.md` — §3.1 path policy; **Owned** = `data/document-index/**`, `docs/reports/**`; **Forbidden** = `config/**`, `.claude/**`, `tests/**`, `scripts/**`.
- `data/document-index/online-resource-registry.yaml` — source registry; 40 entries match `type in {data_api, standard_portal}` (verified). Top-level keys: `generated`, `total_entries`, `summary`, `entries`.
- Epic `#2390`; downstream `#2068`, `#2067`, `#2039`, `#1609`.

### Project memory consulted
- `feedback_llm_wiki_hyphen_module_path_pattern` — hyphen-in-Python-module-path recurs as P1 smell; v4 inherits underscore filenames; final grep audit `grep -RE 'llm-wiki\.' /tmp/plan-drafts/plan-2364-v4.md` enforces zero matches.
- `project_wiki_standards_path_decision` — #2471 sanctions `wiki/standards/` subtree with `code_id`/`publisher`/`revision` frontmatter; v4 stubs forward-adopt these via the specified heuristic.
- `data_format_guidelines` — YAML default for agent-facing structured data; overlay is YAML.

### Gaps identified
- No runner under any owned path — will be created at `docs/reports/batch_pack_1_runner.py`.
- All 40 candidates have `tags: None` (verified on HEAD `12b4be8`) — classifier uses host-regex + notes-keyword only.
- "Insufficient notes" threshold not specified upstream — runner introduces `len(notes) >= 120` AND >=1 capability indicator.
- No existing precedent in repo for `<file>.processed.yaml` overlay — v3 established the convention; v4 inherits unchanged.

### Evidence (embedded verification)

**Anchor:** all references verified against HEAD `12b4be834954505ca1e7fc8ad8b20bda34e92baf` (anchor preserved from v3; v4 adds 2026-04-25 attestations for PyYAML and CLAUDE.md paths).

**Issue statuses** (verified 2026-04-25):
- `#2364` — OPEN; `#2390` — OPEN; `#2068`, `#2067`, `#2039`, `#1609` — OPEN; `#2242`, `#2243`, `#2241` — CLOSED.

**File existence** (`git ls-files` on HEAD `12b4be8`):
- EXISTS: `docs/reports/llm-wiki-external-source-priority-queue.md`, `docs/reports/llm-wiki-staged-batch-packs.md` (17,928 bytes), `data/document-index/online-resource-registry.yaml` (3,423 lines).
- EXISTS: all four target-wiki `CLAUDE.md` files, at the **flat** path `knowledge/wikis/<domain>/CLAUDE.md` (NOT `<domain>/wiki/CLAUDE.md`). Live ground truth via `git ls-files | grep -E 'wikis/.*CLAUDE\.md'`:
  - `knowledge/wikis/engineering/CLAUDE.md`
  - `knowledge/wikis/marine-engineering/CLAUDE.md`
  - `knowledge/wikis/maritime-law/CLAUDE.md`
  - `knowledge/wikis/naval-architecture/CLAUDE.md`
- MISSING (will be created in **owned** paths): `docs/reports/batch_pack_1_runner.py`, `docs/reports/batch_pack_1_runner_tests.py`, `docs/reports/conftest.py`, `docs/reports/batch-pack-1-api-portal-metadata-stubs.md`, `data/document-index/batch-pack-1-follow-on-issues.yaml`, `data/document-index/online-resource-registry.processed.yaml`.

**Forbidden-paths clause (quoted verbatim from `docs/reports/llm-wiki-staged-batch-packs.md`, §3.1, line 80):**
> `| **Forbidden** | \`config/**\`, \`.claude/**\`, \`tests/**\`, \`scripts/**\` |`

Owned (line 78): `data/document-index/**`, `docs/reports/**`. Read-only (line 79): `knowledge/wikis/**`, `docs/document-intelligence/**`.

**v4 path compliance:** every new artifact lands under Owned. The source registry is not modified — overlay sits beside it under the same Owned `data/document-index/**` subtree.

**PyYAML availability** (verified 2026-04-25):
- `grep -nE '^\s*"?(P|p)y(Y|y)aml' pyproject.toml` →
  - line 17: `"pyyaml>=6.0",`
  - line 30: `"PyYAML>=6.0",`
  (Both casings present — historical artifact; PEP-503 normalizes both to `pyyaml`.)
- `uv pip list | grep -i yaml` → `pyyaml 6.0.3`
- Conclusion: PyYAML is a direct, already-pinned project dependency; v4 adds NO new dependencies. The phrase "stdlib yaml" in the v3 plan body was a misnomer — corrected throughout v4 to "`yaml.safe_load` / `yaml.safe_dump` from PyYAML 6.0+ (already in `pyproject.toml`)".

**40-entry survey** (verified 2026-04-24, anchor `12b4be8`):
- `grep -cE "^\\s+type:\\s+(data_api|standard_portal)" data/document-index/online-resource-registry.yaml` → 40 (31 `data_api` + 9 `standard_portal`).
- All 40 have `tags: None`.
- Sufficient/insufficient/catalog-only split: 23 / 15 / 2.

**120-char threshold dry-run count (v3 — three-bucket model, carried unchanged):**

| Bucket | Count | Notes |
|---|---:|---|
| Sufficient (`len(notes) >= 120` AND >=1 indicator AND not maritime-law) | **23 / 40** | promoted as stubs |
| Insufficient | **15 / 40** | routed to follow-on catalog (notes-too-short or no-indicator) |
| Catalog-only (maritime-law: `imo_gisis`, `gisis_imo_org_5db4e8`) | **2 / 40** | enumerated, NOT counted as promoted |
| **Total** | **40 / 40** | invariant |

**`noaa_ndbc` fixture id** (verified): line 125 of `online-resource-registry.yaml`.

**Duplicate-check cost (benchmark plan):** marine-engineering wiki has 19,191 pages. Pure-Python frontmatter scan (`pathlib.Path.rglob('*.md')` + read first 30 lines + match tolerant `source_id:` regex). Wall-clock target <=30 s. Test marked `@pytest.mark.perf`, opt-in via `RUN_PERF_TESTS=1`. Fallback to `subprocess(rg)` documented in Risks if budget breached during real-world execution.

<!-- Source count: 14 (issue body + 13 artifacts/scripts/memory entries) — exceeds >=3 minimum. -->

---

## Attested Evidence (carried + extended)

| Claim | Evidence | Line / command |
|---|---|---|
| §3.1 forbidden paths include `scripts/**` AND `tests/**` | `docs/reports/llm-wiki-staged-batch-packs.md` | line 80 (verbatim above) |
| §3.1 owned paths include `docs/reports/**` and `data/document-index/**` | same file | line 78 |
| 40 candidate entries have `tags: None` | live registry survey | `yaml.safe_load` + `Counter()` — zero tags across 40 |
| **PyYAML availability attested (NEW v4)** | `pyproject.toml` + `uv pip list` | `grep -nE '^\s*"?(P\|p)y(Y\|y)aml' pyproject.toml` → line 17 `"pyyaml>=6.0",` + line 30 `"PyYAML>=6.0",`; `uv pip list \| grep -i yaml` → `pyyaml 6.0.3`. Conclusion: PyYAML is a direct, already-pinned project dep; v4 adds NO new deps. |
| **Target-wiki `CLAUDE.md` files exist at flat path (NEW v4 — supersedes Gemini r3 P3 incorrect path)** | `git ls-files \| grep -E 'wikis/.*CLAUDE\.md'` | Returns the four flat-path entries `knowledge/wikis/{engineering,marine-engineering,maritime-law,naval-architecture}/CLAUDE.md`. The `<wiki>/wiki/CLAUDE.md` paths Gemini r3 attempted to attest do NOT exist (and never have); the correct convention is the domain-root `CLAUDE.md`. |
| `ruamel.yaml` not in pyproject/requirements | `grep ruamel pyproject.toml requirements*.txt` | no match |
| `noaa_ndbc` exists at line 125 | live registry | `grep -n "noaa_ndbc"` -> line 125 |
| Source registry has top-level `entries:` at line 35 | live registry | `grep -n '^entries:'` -> line 35 |
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
| Overlay file (v3 pivot, carried) | `data/document-index/online-resource-registry.processed.yaml` (new) | YES (sibling, additive) |
| Source registry | `data/document-index/online-resource-registry.yaml` | **NOT MODIFIED** (read-only since v3) |
| Plan reviews | `scripts/review/results/…-plan-{claude,codex,gemini}.md` | — (review tree) |

---

## Overlay schema (carried from v3, unchanged)

The overlay file `data/document-index/online-resource-registry.processed.yaml` is a sibling to the source registry. Schema:

```yaml
# data/document-index/online-resource-registry.processed.yaml
schema_version: 1
generated_by: batch_pack_1_runner@v4
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
    classifier_trace: <string>                 # required, e.g. "host:standards.dnv.com -> naval-architecture"
    runner_version: batch-pack-1@v4            # required
    # Optional forward-compat #2471 fields (see optional_2471_fields heuristic below):
    code_id: <string>                          # optional, present iff stub references a named standard
    publisher: <string>                        # optional
    revision: <string>                         # optional
```

| Key | Type | Required | Example |
|---|---|---|---|
| `schema_version` | int | yes | `1` |
| `generated_by` | str | yes | `batch_pack_1_runner@v4` |
| `generated_at` | str (ISO-8601 UTC seconds) | yes | `2026-04-25T19:42:11+00:00` |
| `source_registry` | str (relative path) | yes | `data/document-index/online-resource-registry.yaml` |
| `source_registry_sha256` | str (64-hex) | yes | `a1b2…` |
| `processed[].id` | str | yes | `noaa_ndbc` |
| `processed[].processed` | bool | yes | `true` |
| `processed[].processed_date` | str (ISO-8601 UTC seconds) | yes | `2026-04-25T19:42:11+00:00` |
| `processed[].source_checksum` | str (64-hex) | yes | sha256 of the entry block in the source |
| `processed[].target_wiki_domain` | enum | yes | `engineering` |
| `processed[].out_of_scope_for_promotion` | bool | yes | `false` |
| `processed[].classifier_trace` | str | yes | `host:standards.dnv.com -> naval-architecture` |
| `processed[].runner_version` | str | yes | `batch-pack-1@v4` |
| `processed[].code_id` | str | optional | `DNV-OS-E301` |
| `processed[].publisher` | str | optional | `DNV` |
| `processed[].revision` | str | optional | `2024-04` |

The `processed:` list is sorted by `id` (lexicographic) for deterministic output. Optional `code_id`/`publisher`/`revision` keys are emitted ONLY when extractable; absent (not empty-string) when the heuristic finds nothing.

---

## `optional_2471_fields` heuristic (NEW v4 — addresses Claude r3 P2)

Purpose: forward-adopt the #2471 standards-frontmatter contract by extracting `code_id`, `publisher`, and `revision` from the entry's `notes` field when a recognizable pattern is present. Field **absence** is the signal for "no recognizable pattern" — the keys are NOT emitted as empty strings.

### Regex contract

```python
import re

KNOWN_PUBLISHERS = ("DNV", "API", "IMO", "CSA", "OCIMF", "ABS")
PUBLISHER_RE = re.compile(r"\b(?P<publisher>" + "|".join(KNOWN_PUBLISHERS) + r")\b")
CODE_ID_RE = re.compile(r"\b(?P<code_id>[A-Z]{2,5}[- ]?[A-Z0-9][A-Z0-9-]+)\b")
REVISION_RE = re.compile(
    r"\b[Rr]ev(?:ision)?\.?\s*(?P<revision>\d{4}(?:-\d{2}){0,2})\b"
    r"|\b(?P<revision_year>\d{4}-\d{2})\b"
)

def optional_2471_fields(entry: dict) -> dict:
    """
    Extract #2471-style standards frontmatter fields from entry notes.
    Returns a dict containing ONLY the keys whose values were extractable.
    Returns {} when nothing extractable -- never returns empty-string values.
    """
    notes = (entry.get("notes") or "").strip()
    if not notes:
        return {}

    out: dict = {}
    pub_m = PUBLISHER_RE.search(notes)
    code_m = CODE_ID_RE.search(notes)
    rev_m = REVISION_RE.search(notes)

    # Require code_id presence as the gating signal -- a bare publisher mention
    # without a code is too noisy.
    if code_m and pub_m:
        out["code_id"] = code_m.group("code_id")
        out["publisher"] = pub_m.group("publisher")
        if rev_m:
            out["revision"] = rev_m.group("revision") or rev_m.group("revision_year")
    return out
```

### Fixture pair (NEW tests)

**Positive (`test_optional_2471_fields_extracts_dnv_os_e301`):**
- Input notes: `"DNV-OS-E301 Rev 2024-04 — mooring safety factors for offshore units"`
- Expected output: `{"code_id": "DNV-OS-E301", "publisher": "DNV", "revision": "2024-04"}`

**Negative (`test_optional_2471_fields_returns_empty_for_unrecognizable_notes`):**
- Input notes: `"Public oceanographic data API for tide gauges and buoy stations along the US coast."`
- Expected output: `{}` (NOT `{"code_id": "", "publisher": "", "revision": ""}`)
- Stub frontmatter assertion: keys `code_id`, `publisher`, `revision` are ABSENT from emitted YAML (verified by `assert "code_id" not in stub.frontmatter`).

---

## Generator contract (deterministic + idempotent)

The runner MUST:

1. Read the source registry exactly once. Compute `source_registry_sha256` over the raw bytes of the source file.
2. **Classify domain for every candidate entry up front** (NEW v4 ordering). Produce `classified: List[Tuple[entry, domain]]` before partitioning.
3. **Partition the classified tuples** into `(sufficient, insufficient, catalog_only)` using the three-bucket rule. The catalog-only bucket is exactly `{(e, d) | d == "maritime-law"}`. The sufficient bucket requires `len(e.notes) >= 120` AND >=1 capability indicator AND `d != "maritime-law"`. The insufficient bucket is everything else outside catalog-only.
4. If the overlay already exists and its `source_registry_sha256` matches: load the prior overlay's `processed` list as a dict keyed by `id`. For any `id` already present, **carry `processed_date` forward unchanged** (this is what makes the per-entry payload byte-identical across runs).
5. For each entry in `sufficient + catalog_only`, compute `source_checksum` over the entry block (deterministic — `yaml.safe_dump(entry, sort_keys=True, default_flow_style=False)` then `sha256`).
6. Sort the `processed` list by `id`.
7. Emit the overlay using `yaml.safe_dump(payload, sort_keys=True, default_flow_style=False, allow_unicode=True)` from PyYAML 6.0+ (already a project dep — see Attested Evidence row "PyYAML availability"). Write to `<overlay>.tmp` then `os.replace(tmp, final)` (atomic).
8. Insufficient entries are NOT in the overlay; they appear only in `data/document-index/batch-pack-1-follow-on-issues.yaml`.

**Determinism caveat:** `generated_at` (top-level) is non-deterministic by design. The acceptance test for byte-identity strips this top-level field before comparison. Per-entry data is fully deterministic across re-runs once entries are first processed.

```
# Pseudocode (deterministic + idempotent overlay generator) -- v4 classify-first ordering

OVERLAY_PATH = Path("data/document-index/online-resource-registry.processed.yaml")
SOURCE_PATH = Path("data/document-index/online-resource-registry.yaml")

function emit_overlay(processed_records: List[ProcessedRecord]):
    src_bytes = SOURCE_PATH.read_bytes()
    src_sha = sha256(src_bytes)

    prior = load_prior_overlay(OVERLAY_PATH, expected_src_sha=src_sha)  # {} if missing/stale

    payload_processed = []
    for r in sorted(processed_records, key=lambda x: x.id):
        prior_date = prior.get(r.id, {}).get("processed_date")
        record = {
            "id": r.id,
            "processed": True,
            "processed_date": prior_date or now_utc_iso_seconds(),
            "source_checksum": sha256_of_entry_block(r.id),
            "target_wiki_domain": r.target_wiki_domain,
            "out_of_scope_for_promotion": (r.target_wiki_domain == "maritime-law"),
            "classifier_trace": r.classifier_trace,
            "runner_version": "batch-pack-1@v4",
        }
        # Optional #2471 fields -- ONLY include keys whose values were extractable.
        record.update(optional_2471_fields(r.entry))
        payload_processed.append(record)

    payload = {
        "schema_version": 1,
        "generated_by": "batch_pack_1_runner@v4",
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

## Consumer-side fallback logic (NEW v4 — `is_stale` signal added)

Any downstream consumer that needs to know "has entry X been processed by Batch Pack 1?" will use this contract:

```
function has_been_processed(entry_id: str) -> Tuple[Optional[ProcessedRecord], bool]:
    """
    Returns (record, is_stale).
      - record is None if overlay is missing OR if entry_id is not in the overlay.
      - is_stale is True iff the overlay exists but its source_registry_sha256
        does not match sha256(SOURCE_PATH.read_bytes()) at consumer-call time.
      - is_stale is False when overlay is missing (no overlay -> no staleness signal,
        only a missing-coverage signal via record=None) OR when checksums match.
    Default consumer behavior: if is_stale -> WARN log + use record anyway.
    Strict consumers (e.g. #2039/#2067/#2068 may opt in) -> halt-on-stale.
    """
    if not OVERLAY_PATH.exists():
        log.warning("Overlay missing; falling back to source registry. "
                    "Batch Pack 1 may not have run yet.")
        return (None, False)
    overlay = yaml.safe_load(OVERLAY_PATH.read_bytes())
    src_sha = sha256(SOURCE_PATH.read_bytes())
    is_stale = (overlay["source_registry_sha256"] != src_sha)
    if is_stale:
        log.warning("Overlay stale: source_registry_sha256 mismatch. "
                    "Source has changed since overlay was generated. "
                    "Caller should decide whether to use-anyway or halt.")
    by_id = {r["id"]: r for r in overlay.get("processed", [])}
    return (by_id.get(entry_id), is_stale)
```

**Fallback rules:**
- Overlay missing -> `(None, False)`. Consumer treats all entries as unprocessed; logs warning; does not error.
- Overlay present + checksum match -> `(record_or_None, False)`. Overlay is authoritative.
- Overlay present + checksum mismatch (stale) -> `(record_or_None, True)`. Default = WARN + use anyway. Strict consumers MAY halt — the contract surfaces the signal but does not dictate the policy.

This design preserves the property Gemini r2 flagged: **the source registry is never structurally mutated**, so YAML edge cases (commented `- id:` lines, multi-line strings, unexpected indentation) cannot corrupt it. The overlay is generated from `yaml.safe_load` parsed data + `yaml.safe_dump` emission (PyYAML 6.0+, already a project dep) — no regex on YAML text.

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
| `code_id` | str | optional | forward-adopt #2471 — present iff `optional_2471_fields` extracted it; ABSENT (not empty-string) otherwise |
| `publisher` | str | optional | forward-adopt #2471 — same absence semantics |
| `revision` | str | optional | forward-adopt #2471 — same absence semantics |

Test `test_build_stub_frontmatter_matches_wiki_schema` asserts presence + type for every required key. Tests `test_optional_2471_fields_extracts_dnv_os_e301` and `test_optional_2471_fields_returns_empty_for_unrecognizable_notes` cover the optional triple's emit/absent semantics.

---

## Pseudocode (runner top-level — v4 classify-first ordering)

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
    notes_lower = (entry.notes or "").lower()
    # Precedence: LAW > NAVAL_ARCH > MARINE > engineering default.
    if host in LAW_HOSTS or any(t in notes_lower for t in LAW_TERMS):
        return "maritime-law"
    if host in NAVAL_ARCH_HOSTS or any(t in notes_lower for t in NAVAL_ARCH_TERMS):
        return "naval-architecture"
    if host in MARINE_HOSTS or any(t in notes_lower for t in MARINE_TERMS):
        return "marine-engineering"
    return "engineering"

function partition_three_bucket(classified, min_chars, require_any_of):
    """
    Consumes a list of (entry, domain) tuples produced by classify_domain.
    Returns (sufficient, insufficient, catalog_only) -- partition is total
    and disjoint over the input.
    """
    sufficient, insufficient, catalog_only = [], [], []
    for entry, domain in classified:
        if domain == "maritime-law":
            catalog_only.append((entry, domain))
            continue
        notes_lower = (entry.notes or "").lower()
        long_enough = len(entry.notes or "") >= min_chars
        has_indicator = any(tok in notes_lower for tok in require_any_of)
        if long_enough and has_indicator:
            sufficient.append((entry, domain))
        else:
            insufficient.append((entry, domain))
    return sufficient, insufficient, catalog_only

function run_batch_pack_1(registry_path, wiki_root, output_report_path,
                          overlay_path, follow_on_path):
    src = load_yaml(registry_path)
    candidates = [e for e in src["entries"] if e["type"] in {"data_api", "standard_portal"}]
    assert len(candidates) == 40

    # v4: classify FIRST, partition SECOND.
    classified = [(e, classify_domain(e)) for e in candidates]

    sufficient, insufficient, catalog_only = partition_three_bucket(
        classified,
        min_chars=120,
        require_any_of=["endpoint", "api", "http", "portal", "coverage",
                        "dataset", "standard", "rule"])
    assert len(sufficient) + len(insufficient) + len(catalog_only) == 40

    grouped = {d: [] for d in ["engineering", "marine-engineering",
                               "naval-architecture", "maritime-law"]}
    processed_records = []
    for entry, domain in (sufficient + catalog_only):
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
    # No subprocess, no shell=True. Pure pathlib + tolerant regex.
    # v4: tolerate optional surrounding quotes around the source_id (Gemini r3 P3).
    import re
    target_re = re.compile(rf'^source_id:\s*"?{re.escape(source_id)}"?\s*$')
    list_re = re.compile(rf'^\s*-\s*"?{re.escape(source_id)}"?\s*$')
    for md in wiki_root.rglob("*.md"):
        # Read only first 30 lines (frontmatter region) to bound cost.
        with md.open() as fh:
            for i, line in enumerate(fh):
                if i >= 30:
                    break
                line_stripped = line.rstrip("\n")
                if target_re.match(line_stripped) or list_re.match(line_stripped):
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
| Create | `data/document-index/online-resource-registry.processed.yaml` | overlay (v3 pivot, carried) — sibling, deterministic, atomic write |
| Update | `docs/plans/README.md` | add index row |

**No writes to:** `config/**`, `.claude/**`, `tests/**`, `scripts/**`, `knowledge/wikis/**`, `data/document-index/online-resource-registry.yaml` (source registry is **read-only** since v3). Allow-list-guarded by AC.

---

## TDD Test List

Tests at `docs/reports/batch_pack_1_runner_tests.py`. `docs/reports/conftest.py` adds the directory to `sys.path` so the test module can `import batch_pack_1_runner` directly. Invocation: `uv run pytest docs/reports/batch_pack_1_runner_tests.py -v`.

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| `test_filter_yields_exact_40_entries` | filter(type ∈ {data_api, standard_portal}) count = 40 | committed registry | `len == 40` |
| `test_classify_runs_before_partition` | **NEW v4** runner produces `classified` (list of `(entry, domain)` tuples) before calling `partition_three_bucket` | trace runner call order via monkeypatched fakes | classify_domain called == 40 times BEFORE partition_three_bucket invoked |
| `test_partition_three_bucket_invariant` | sufficient + insufficient + catalog_only == 40; buckets are disjoint | committed registry, post-classification | invariant holds; pairwise intersection empty |
| `test_partition_three_bucket_routes_maritime_law_to_catalog_only` | **NEW v4** every `(entry, "maritime-law")` tuple lands in `catalog_only`, none in `sufficient` or `insufficient` | synth tuples covering all 4 domains | partition routes correctly |
| `test_partition_dry_run_matches_23_15_2` | live partition matches v3 survey | committed registry | sufficient=23, insufficient=15, catalog_only=2 (or runner reports actual + AC requires invariant) |
| `test_partition_notes_quality_threshold_rejects_empty_notes` | notes-length < 120 → insufficient | synth 30-char note | insufficient |
| `test_partition_notes_quality_threshold_accepts_endpoint_mention` | >=120 chars AND "endpoint" → sufficient | synth 250-char note | sufficient |
| `test_classify_law_wins_over_marine` | IMO host beats marine notes | synth `gisis.imo.org` + "ocean" notes | `maritime-law` |
| `test_classify_law_wins_over_naval_arch` | IMO-keyword notes on `standards.dnv.com` | synth entry | `maritime-law` |
| `test_classify_naval_wins_over_marine` | class-rules notes on a marine-adjacent host | synth entry on `data.marine.copernicus.eu` w/ "class rules" notes | `naval-architecture` |
| `test_classify_marine_host_wins` | NDBC → marine-engineering | synth `www.ndbc.noaa.gov` | `marine-engineering` |
| `test_classify_naval_host_wins` | IACS/DNV → naval-architecture | synth `iacs.org.uk` | `naval-architecture` |
| `test_classify_default_engineering` | no marine/naval/law signal | synth plain entry | `engineering` |
| `test_imo_entries_flagged_out_of_scope` | both real IMO entries `out_of_scope_for_promotion=True` | live (`imo_gisis`, `gisis_imo_org_5db4e8`) | both flagged |
| `test_build_stub_frontmatter_matches_wiki_schema` | asserts presence + type for every required key (10 keys) | sample entry | per-key assertion |
| `test_optional_2471_fields_extracts_dnv_os_e301` | **NEW v4** positive fixture: notes `"DNV-OS-E301 Rev 2024-04 — mooring safety factors"` | synth entry | returns `{"code_id":"DNV-OS-E301","publisher":"DNV","revision":"2024-04"}` |
| `test_optional_2471_fields_returns_empty_for_unrecognizable_notes` | **NEW v4** negative fixture: notes about a NOAA tide-gauge API | synth entry | returns `{}`; emitted stub frontmatter has NO `code_id`/`publisher`/`revision` keys (not present-as-empty-strings) |
| `test_check_duplicate_finds_existing_wiki_page` | finds wiki page with `source_id: noaa_ndbc` (or list-form `- noaa_ndbc`) | fixture wiki tree | returns the path |
| `test_check_duplicate_tolerates_quoted_source_id` | **NEW v4 (Gemini r3 P3)** matches `source_id: 'noaa_ndbc'` AND `source_id: "noaa_ndbc"` AND `source_id: noaa_ndbc` AND `  - "noaa_ndbc"` | four fixture variants | all four matched |
| `test_check_duplicate_pure_python_no_subprocess` | implementation does not import `subprocess` (defensive) | inspect runner module | `subprocess` not imported |
| `test_overlay_schema_validates` | overlay matches the schema table | full run | `schema_version`, `generated_at`, `source_registry_sha256`, `processed[]` keys all present + correct types |
| `test_overlay_byte_identical_across_reruns` | running runner twice yields byte-identical overlay (after stripping top-level `generated_at`) | live registry | `sha256(overlay_run1_minus_generated_at) == sha256(overlay_run2_minus_generated_at)` |
| `test_overlay_carries_processed_date_forward` | re-run does NOT bump per-entry `processed_date` | overlay-from-prior-run | per-entry `processed_date` unchanged |
| `test_overlay_atomic_write_no_partial` | crash mid-write leaves prior overlay intact | monkeypatch `os.replace` to raise after partial tmp write | prior overlay unchanged; tmp file removed |
| `test_overlay_processed_date_format_utc_iso_seconds` | `processed_date` matches `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$` | run with mocked `now_utc_iso_seconds` | regex matches |
| `test_source_registry_unchanged` | source registry sha256 before == after run | live registry | sha256 equal |
| `test_consumer_overlay_missing_returns_none_with_warning` | fallback returns `(None, False)` + emits warning when overlay absent | overlay deleted | returns `(None, False)`; warning logged |
| `test_consumer_returns_is_stale_flag_on_checksum_mismatch` | **NEW v4 (Claude r3 P2)** mutated source -> overlay checksum mismatch -> consumer returns `(record_or_None, True)` | mutated source bytes after overlay write | `is_stale == True`; record returned for ids present in overlay |
| `test_consumer_overlay_stale_returns_partial_coverage` | overlay with mismatching `source_registry_sha256` is still consulted, missing ids fall back | mutated source bytes | overlay-present ids returned; missing ids return `(None, True)` |
| `test_output_report_three_bucket_counts` | report header lists sufficient + insufficient + catalog_only summing to 40 | full run | three counts present + sum == 40 |
| `test_run_is_idempotent_at_report_layer` | re-running produces 0 newly-added stubs | already-promoted state | report says "0 new" |
| `test_no_writes_outside_allow_list` | `git diff` after run touches only allow-listed paths | full run in clean clone | diff matches allow-list regex set |
| `test_pyyaml_is_a_direct_dep` | **NEW v4 (Gemini r3 P1)** pyyaml resolvable in test environment AND listed in `pyproject.toml` | `import yaml` + `tomllib.load(open("pyproject.toml","rb"))` | `yaml.__version__ >= "6.0"` and `"pyyaml"` (or `"PyYAML"`) appears in resolved deps |
| `test_duplicate_check_wall_clock_under_budget` | `@pytest.mark.perf` — full marine-eng scan <=30 s | 19,191 pages | wall_clock < 30 s; **skipped unless `RUN_PERF_TESTS=1`** |

---

## Acceptance Criteria

- [ ] All non-perf tests pass: `uv run pytest docs/reports/batch_pack_1_runner_tests.py -v -m "not perf"`
- [ ] Perf test passes when run with `RUN_PERF_TESTS=1 uv run pytest docs/reports/batch_pack_1_runner_tests.py -v -m perf` (run once at plan-approval time, not gating CI)
- [ ] `uv run python docs/reports/batch_pack_1_runner.py` exits 0 and produces `docs/reports/batch-pack-1-api-portal-metadata-stubs.md`, `data/document-index/batch-pack-1-follow-on-issues.yaml`, and `data/document-index/online-resource-registry.processed.yaml`
- [ ] Source registry `data/document-index/online-resource-registry.yaml` is **byte-identical** before and after the run (sha256 verified)
- [ ] Output report header reports three bucket counts summing to exactly 40: `sufficient + insufficient + catalog_only == 40`
- [ ] Each generated stub has `target_wiki_domain ∈ {engineering, marine-engineering, naval-architecture, maritime-law}`
- [ ] Every `maritime-law`-classified stub carries `out_of_scope_for_promotion: true` and is counted in `catalog_only`, NOT `sufficient`
- [ ] **Classify-before-partition pipeline** is exercised: runner produces the `(entry, domain)` tuple list before partitioning, verified by `test_classify_runs_before_partition`
- [ ] `optional_2471_fields` heuristic emits `code_id`/`publisher`/`revision` ONLY when extractable (positive + negative fixture pair pass)
- [ ] Each generated stub records provenance (`sources: [<registry-entry-id>]`) and source URL
- [ ] A **Classifier Trace** section in the report lists the matched rule for every one of the 40 entries; zero `Unclassified`
- [ ] Duplicate check uses pure-Python `pathlib.Path.rglob` (no subprocess, no shell=True); tolerant regex matches quoted and unquoted `source_id` forms; every matched pair listed in a Duplicates section (does NOT block promotion)
- [ ] `data/document-index/batch-pack-1-follow-on-issues.yaml` exists and lists every deferred entry with a reason code (`notes-too-short`, `no-capability-indicator`, `duplicate-suspected`, `classifier-ambiguous`)
- [ ] Overlay file `data/document-index/online-resource-registry.processed.yaml` validates against the schema table; `processed[]` is sorted by `id`; per-entry `processed_date` matches UTC ISO-8601 seconds regex
- [ ] **Byte-identity across reruns**: running the runner twice on the same source registry produces overlay files whose sha256 is equal after stripping the top-level `generated_at` field
- [ ] **Consumer `is_stale` signal**: `has_been_processed(id)` returns `(record_or_None, is_stale)`; `is_stale==True` iff overlay's `source_registry_sha256` mismatches the live source sha256
- [ ] **PyYAML attestation**: `pyyaml>=6.0` (case-insensitive) appears in `pyproject.toml` and is importable as `yaml` in the runner environment (no new dependency added)
- [ ] Allow-list-only file change set: `git diff --name-only origin/main...HEAD` matches only paths in the allow-list (enumerated above in "v3 revisions §forbidden-path guard")
- [ ] Review artifacts for all three providers posted to `scripts/review/results/`
- [ ] No wiki pages promoted — downstream #2039 / #2067 / #2068 consume the report

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (v1) | MAJOR | 2 P1 + 3 P2 + 3 P3 — addressed in v2 |
| Claude (v2) | MAJOR | 3 P2 + 6 P3 — all addressed in v3 |
| Gemini (v2) | MAJOR | 1 P1 (regex YAML) + 1 P3 (shell pipeline) — both resolved by v3 overlay pivot + pure-Python duplicate check |
| Codex (v2) | UNAVAILABLE | upstream regression #2479 — provider unavailable across this batch |
| Claude (v3) | MAJOR | P2 partition/classify ordering, P2 `optional_2471_fields` extraction unspecified, P2 stale-overlay consumer needs `is_stale` signal — **all addressed in v4** |
| Gemini (v3) | MAJOR | P1 "yaml is NOT in stdlib" wording (PyYAML is the runtime; PyYAML IS already a direct dep so the no-new-deps claim holds) + P3 quoted-source_id false-negative + P3 missing CLAUDE.md path attestation (correct path is flat, not under `/wiki/`) — **all addressed in v4** |
| Codex (v3) | UNAVAILABLE | upstream regression #2479 still in effect |
| Claude (v4) | PENDING | (to be filled by v4 fanout) |
| Gemini (v4) | PENDING | (to be filled by v4 fanout) |
| Codex (v4) | PENDING | (subject to #2479 status) |

**Overall result:** PENDING (awaits v4 r1 fanout).

---

## Risks and Open Questions

- **Risk (overlay+source drift):** if the source registry changes between Batch Pack 1 runs and a downstream consumer reads the overlay, the consumer might act on a stale `target_wiki_domain`. Mitigation: per-entry `source_checksum` AND top-level `source_registry_sha256` let the consumer detect drift. **NEW v4:** consumer return contract now exposes `is_stale: bool` so callers can choose use-anyway vs halt; default is WARN + use anyway.
- **Risk (overlay convention is new):** no prior precedent in the repo for `<file>.processed.yaml`. Documented inline in the runner module docstring; if the convention proves useful, it generalizes (the source-registry sha256 + per-entry checksum pattern is reusable).
- **Risk (classifier precision):** deterministic host + notes classifier may misclassify edge entries. Mitigation: Classifier Trace section in the report; downstream wiki-ingest reviewer can override.
- **Risk (insufficient-notes false-positives):** 120-char + indicator threshold may push adequately-documented entries into the follow-on. Dry-run shows 15/40 insufficient; threshold recorded in the report and adjustable via flag.
- **Risk (duplicate-check on marine-engineering):** 19,191 pages — pure-Python frontmatter scan with 30-s wall-clock budget; perf test gated behind `@pytest.mark.perf` so default CI does not flake. **Fallback:** if perf budget is breached during real-world execution, the runner may switch to `subprocess(["rg", "-l", ...])` — added to followups but NOT required for v4 acceptance.
- **Risk (`optional_2471_fields` heuristic over-extracts):** the regex `[A-Z]{2,5}[- ]?[A-Z0-9][A-Z0-9-]+` may match unrelated all-caps tokens. Mitigation: gating on co-occurrence of a known publisher (`KNOWN_PUBLISHERS`) before emitting; absence of either signal yields `{}`. Two new tests (positive + negative fixtures) lock the contract.
- **Open:** Should the follow-on catalog auto-file GitHub child issues under #2390 or leave issue creation to a human? Default: NOT auto-filing; user decides at approval.
- **Open:** Should the overlay file be committed by the runner directly, or staged for a human commit? Plan defaults to: runner writes the file and exits; human inspects, reviews, and commits as part of the issue's PR.

---

## Complexity: T2

**T2** — new runner + self-test module + report + follow-on catalog + overlay file, all in owned paths; **source registry is unchanged**; no schema migrations; **no new dependencies** (uses already-pinned `PyYAML 6.0+`, plus `hashlib`, `pathlib`, `re` from the standard library); no network calls.
