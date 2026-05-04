# Plan for #2373: Execute Batch Pack 4 for non-ACMA standards summary promotion

> **Status:** draft (v3)
> **Complexity:** T2
> **Date:** 2026-04-23 (v2 revised 2026-04-24; v3 revised 2026-04-24)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2373
> **Review artifacts (v2):** scripts/review/results/20260425T034634Z-plan-2373-v2.md-plan-claude.md (MAJOR), scripts/review/results/20260425T034912Z-plan-2373-v2.md-plan-gemini.md (MINOR)
> **Review artifacts (v1):** scripts/review/results/20260424T032933Z-2026-04-23-issue-2373-batch-pack-4-non-acma-standards-summary-promotion.md-plan-{claude,codex,gemini}.md

---

## v3 Revision Log (surgical deltas only)

Addresses Claude r2 MAJOR (10 items, P2/P3) and Gemini r2 MINOR (3 items). Codex r2 unavailable per #2479 stdin-hang regression; consensus gate decision recorded in §Cross-Provider Gate Decision below. Forward-adopts deterministic-hash invariant (`hashlib.sha256`) and deterministic-grouping invariant (`collections.defaultdict`) to eliminate cross-process drift in `collision_group_id` and per-domain emission.

| # | r2 item | v3 delta |
|---|---|---|
| C-r2-1 | EXPECTED_SLICE_COUNT placeholder | RESOLVED via Option (i): pre-approval dry-run executed 2026-04-24 against `data/document-index/standards-transfer-ledger.yaml` (436 entries) and `data/design-codes/code-registry.yaml` (10 design-code ids). Pinned: **EXPECTED_SLICE_COUNT = 68** plus **EXPECTED_SLICE_ID_CHECKSUM = `a7996eb6b79f9882b35f5fe33fca36fd144c67a1ff5e10525bd7d260306e4d70`** (sha256 of `\n`-joined sorted ledger ids). Per-domain breakdown: cathodic-protection=4, pipeline=22, structural=42. Exclusion-impact cross-tab embedded in §Pre-Approval Count Pinning. |
| C-r2-2 | `collision_group_id = hash(p)` non-deterministic (PYTHONHASHSEED) | REPLACED with `hashlib.sha256(p.encode("utf-8")).hexdigest()[:16]`. Pseudocode Step 5 updated; reruns over identical inputs now produce identical 16-hex-char `collision_group_id` strings. Determinism invariant cross-referenced from §Topic Clustering Rule and §Slug Normalization Rule. |
| C-r2-3 | `find_shard_summary_rows` matching algorithm unspecified | DEFINED inline in §Shard-Summary Matching Rule (NEW v3): iterate the 20 shard JSON files, materialize all records, treat each record as a hit iff `record.get("standards_refs", [])` contains the exact ledger `id` OR `record.get("title", "").lower()` contains the lowercased normalized ledger id. Pre-test `pre_run_shard_match_locked` pins the count for one known seed id. |
| C-r2-4 | `itertools.groupby` on unsorted input | REPLACED with `collections.defaultdict(list)` accumulation in pseudocode Steps 5–6. No iterator exhaustion; one-pass O(n). |
| C-r2-5 + G-r2-2 | `to_slug()` regex too narrow | EXTENDED to `re.sub(r"[^a-z0-9]+", "-", s)` per Gemini's recommendation; covers parentheses, ampersands, commas, slashes, dots, whitespace in one pass. Then collapse-and-strip stays unchanged. New §Slug Normalization Rule includes a refreshed verification table. |
| C-r2-6 | Manual-alias source-of-truth unspecified | LANDED as a new pre-landed fixture `data/document-index/standards-aliases.yaml`. Pre-land sequence and schema specified in §Standards-Aliases Fixture (NEW v3); test `pre_run_aliases_fixture_exists` enforces. |
| C-r2-7 | Topic-clustering tie-break missing | ADDED tie-break rule in §Topic Clustering Rule: longest-matching-keyword wins; ties broken by `cluster_id` lexicographic order. Removes order-sensitivity on fixture YAML row order. |
| C-r2-8 | `post_run_no_source_reads_audit` mechanism unspecified | PINNED to `sys.addaudithook` filtering on `open` audit events with path-prefix `/mnt/ace/`. Reference snippet inline in §TDD Test List notes. Wrapper script path: `scripts/enforcement/audit-no-mnt-ace.py` (created in this plan). |
| C-r2-9 | Codex r2 gate decision missing | RECORDED in §Cross-Provider Gate Decision (NEW v3): Claude+Gemini r3 consensus suffices for v3 approval given (a) Codex sandbox blocks shell exec per `feedback_codex_sandbox_no_execution`, (b) #2479 stdin-hang upstream regression unresolved as of 2026-04-24, and (c) this plan touches NO live system state — outputs are deterministic file emissions, so live-state-contradiction surface (the area Codex's GitHub-connector grounding adds value) is not load-bearing here. Re-dispatch to Codex deferred to post-#2479 close. |
| C-r2-10 | `<domain>-other` clusters not declared in fixture | ADDED to §Topic Clustering Rule fixture: each domain's cluster list now ends with an explicit `<domain>-other` entry with `keywords: []`. Render of `cluster_id: cp-other` now has a corresponding row in the per-domain report keyword table. |
| C-r2-11 | `post_run_only_owned_paths` permits `^docs/plans/` for the lane | TIGHTENED via split: `post_run_lane_diff_owned_paths` (lane commit) FORBIDS `^docs/plans/`; `post_run_main_diff_owned_paths` (main-session README append commit) PERMITS only `^docs/plans/README.md` and nothing else. §Files to Change clarified to mark `docs/plans/README.md` explicitly as `Update (main-session-only commit, NOT in lane diff)`. |
| G-r2-1 | `count_slice.py` referenced but not in Files-to-Change | ADDED to §Files to Change as `scripts/data/document-index/count_slice.py` (underscore-only filename to avoid the `llm-wiki/` hyphen-path hazard pattern; this script lives outside `llm-wiki/` so the hazard does not apply, but underscore convention adopted preemptively). Test `post_run_slice_count_exact` invokes it with `python3 scripts/data/document-index/count_slice.py`. |
| G-r2-3 | `find_shard_summary_rows` performance unstated | NOTED in §Shard-Summary Matching Rule: 20 shard files, total ~640k summaries, ~50–80MB combined; load-once-into-memory acceptable on the standard developer machine; no streaming required. |

---

## Resource Intelligence Summary

### Existing repo code
- Found: `data/document-index/standards-transfer-ledger.yaml` (7,727 lines, total=436 entries) — canonical L2 ledger with `id`, `title`, `org`, `domain`, `doc_path`, `doc_paths`, `status`, `wrk_id`, `repo`, `modules`, `implemented_at`, `notes`, `exhausted`, `exhausted_at`, `absorbed_into` fields per standard. (entry-key set verified 2026-04-24 v3 dry-run.)
- Found: `data/document-index/resource-intelligence-maturity.yaml` — authoritative maturity status (documents_in_scope=425; 639,585 index summaries; reclassification to 10 domains complete; `process`=55 and `drilling`=9 domains new).
- Found: `data/document-index/shards/shard-00.json` … `shard-09.json` + `data/document-index/shards/ace-shard-00.json` … `ace-shard-09.json` — 20 document-index shards with existing summaries (no source PDFs read required). Verified per §Evidence.
- Found: `data/design-codes/code-registry.yaml` — EXISTS (3,512 bytes, 10 design-code ids: `API-RP-1111`, `API-RP-2A-WSD`, `API-RP-2RD`, `ASME-B31.4`, `BS-7910`, `DNV-RP-C203`, `DNV-RP-C205`, `DNV-RP-F105`, `DNV-ST-F101`, `ISO-13628-7`). v2's `DESIGN_CODE_EXCLUSION=noop` fallback is therefore NOT triggered; 5 ledger rows excluded by registry overlap. Cross-tab in §Pre-Approval Count Pinning.
- Found: `docs/reports/llm-wiki-staged-batch-packs.md` §3.4 — Batch Pack 4 design document specifying scope, sub-slicing (4a–4j by domain), owned/read-only/forbidden paths, and validation sequence.
- Gap: No Batch Pack 4 promotion artifact under `docs/reports/batch-pack-4-*.md` exists yet.

### Standards
| Standard family | Status | Source |
|---|---|---|
| `cathodic-protection` domain (19 entries) | summary-backed; 47.4% calc implemented | `data/document-index/standards-transfer-ledger.yaml` |
| `pipeline` domain (55 entries) | summary-backed; 21.8% calc implemented | `data/document-index/standards-transfer-ledger.yaml` |
| `structural` domain (71 entries) | summary-backed; 5.6% calc implemented | `data/document-index/standards-transfer-ledger.yaml` |
| `marine` domain (42 entries) | reserved for ACMA/OCIMF/CSA scope (#2216, #2227, #2284) — EXCLUDED | issue #2373 scope |
| `process` domain (55 entries) | new domain (zero prior calc) — DEFERRED | maturity YAML |
| `drilling` domain (9 entries) | new domain (zero prior calc) — DEFERRED | maturity YAML |
| `materials` domain (122 entries) | DEFERRED to separate wave (locked v2) | this plan §Acceptance Criteria |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/` — 7 pages exist (verified): `api-579-ffs.md`, `dnv-os-e301.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `ocimf-meg4.md`. Exact-match entries for these are extend-only (except `ocimf-meg4` which is excluded by org filter).
- `knowledge/wikis/engineering/wiki/index.md` — concept pages already cover `pipeline-integrity-assessment`, `free-span-viv-fatigue`, `sn-curve-fatigue-definitions`, `cathodic-protection-design`, `structural-analysis-offshore`. Some stubs are extend-only via concept cross-linking.
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema; per #2471 v3 (decision 2026-04-23) `wiki/standards/` is the sanctioned subtree for standards overview pages with required frontmatter `code_id`, `publisher`, `revision` (optional `jurisdiction`, `supersedes`).
- `knowledge/wikis/marine-engineering/wiki/` — has no `standards/` subdir; any marine-tagged standard is carried forward to #2216/#2227/#2284, never promoted by this wave.

### Documents consulted
- Parent epic #2390 — Batch Pack 4 assigned to Wave 7 (after Wave 6 Batch Packs 1+3); standalone, not paired.
- Issue #2373 body — scope locked to non-ACMA domains; first slice = `cathodic-protection + pipeline + structural`; summary/ledger evidence only; no raw PDF rereads; excludes #2216/#2227/#2284 ACMA/OCIMF/CSA work and #2365 design-code-registry work.
- `docs/reports/llm-wiki-external-source-priority-queue.md` §5 — ranks `standards-with-existing-summaries` as P1; aligns with this wave.
- Issue #2365 — design-code registry promotion sources from `data/design-codes/code-registry.yaml` (separate from ledger); overlap avoided.
- Issue #2207 — provenance/reuse contract; outputs cite ledger entries and shard summaries by stable key (ledger `id` + shard record path).
- #2471 v3 (codification plan landing 2026-04-23) — `wiki/standards/` sanctioned subtree + frontmatter contract; this plan forward-adopts.
- `.claude/rules/calc-citation-contract.md` — extend-only verdicts that touch standards pages must, when emitted to `wiki/standards/<code-id>.md`, carry `code_id`/`publisher`/`revision` frontmatter. v2/v3 wiki-ready stubs include these fields.

### Gaps identified
- No extend-vs-create mapping exists from ledger entries to `knowledge/wikis/engineering/wiki/standards/*.md` or `concepts/*.md`.
- No provenance fixture linking shard summary → ledger entry → proposed wiki stub.
- No reusable topic-clustering fixture (this plan will land it as `data/document-index/standards-topic-clusters.yaml` BEFORE running per-domain reports).
- No standards-aliases fixture for ledger-id → canonical-page reconciliation (v3 will land `data/document-index/standards-aliases.yaml`).
- `marine` domain overlap boundary not mechanically enforced — hand-verified per row pre-classification.

### Evidence (embedded verification, run 2026-04-23 unless noted; v3 dry-run 2026-04-24)

**Issue statuses** (verified via `gh issue view`):
- `#2373` — OPEN — "feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion"
- `#2390` — OPEN — epic coordinator
- `#2216`, `#2227`, `#2284` — scope-excluded ACMA/OCIMF/CSA scope
- `#2365` — scope-excluded design-code-registry
- `#2471` — sanctioned `wiki/standards/` subtree decision (referenced by v2/v3)
- `#2039` — engineering wiki ingest umbrella (downstream consumer)
- `#2479` — codex-cli 0.124.0 stdin-hang upstream regression (gates Codex r2 dispatch; see §Cross-Provider Gate Decision)

**File existence** (`ls -la` + `find`, run 2026-04-23 + v3 dry-run 2026-04-24):
- EXISTS: `data/document-index/standards-transfer-ledger.yaml` (7,727 lines, 436 entries)
- EXISTS: `data/document-index/resource-intelligence-maturity.yaml` (59 lines)
- EXISTS: `data/document-index/shards/shard-0[0-9].json` (10 files)
- EXISTS: `data/document-index/shards/ace-shard-0[0-9].json` (10 files)
- EXISTS: `knowledge/wikis/engineering/wiki/standards/api-579-ffs.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-rp-c203.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-rp-c205.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-rp-f101.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-rp-f105.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` (excluded by org filter)
- EXISTS: `knowledge/wikis/engineering/wiki/concepts/` (33 concept pages)
- EXISTS: `docs/reports/llm-wiki-staged-batch-packs.md`
- EXISTS (v3 verified 2026-04-24): `data/design-codes/code-registry.yaml` (3,512 bytes, 10 ids); `DESIGN_CODE_EXCLUSION=active`, NOT noop
- MISSING (this plan creates): `data/document-index/standards-topic-clusters.yaml` — clustering fixture pre-landed
- MISSING (this plan creates): `data/document-index/standards-aliases.yaml` — alias fixture pre-landed (NEW v3)
- MISSING (this plan creates): `scripts/data/document-index/count_slice.py` — slice-count test helper (NEW v3)
- MISSING (this plan creates): `scripts/enforcement/audit-no-mnt-ace.py` — audithook wrapper (NEW v3)
- MISSING (this plan creates): `docs/reports/batch-pack-4-non-acma-standards-{cathodic-protection,pipeline,structural}.md`
- MISSING (this plan creates): `docs/reports/batch-pack-4-extend-vs-create-map.yaml`
- MISSING (this plan creates): `docs/reports/batch-pack-4-provenance-sample.yaml`

**Line excerpts** (ledger `domain:` tallies via `grep | sort | uniq -c`):
```
122   domain: materials
 71   domain: structural
 55   domain: process
 55   domain: pipeline
 42   domain: marine
 23   domain: cad
 22   domain: installation
 19   domain: cathodic-protection
 15   domain: regulatory
  9   domain: drilling
```
First-slice raw target = cathodic-protection + pipeline + structural = 19 + 55 + 71 = **145 candidate entries**, before applying org/registry/summary-evidence filters. Post-filter pinned **EXPECTED_SLICE_COUNT = 68** (see §Pre-Approval Count Pinning).

**Gap proofs**:
- `ls docs/reports/batch-pack-4*` will return "No such file or directory" — confirms no per-domain report exists yet.
- `ls knowledge/wikis/engineering/wiki/standards/api-579-ffs.md` returns EXISTS — confirms extend-only candidate for API 579 structural entry.
- `ls knowledge/wikis/marine-engineering/wiki/standards/` returns "No such file or directory" — marine-engineering wiki has no `standards/` family; any marine standard is mis-placed if promoted here.

<!-- 8 distinct sources consulted: issue body, standards-transfer-ledger.yaml, resource-intelligence-maturity.yaml, staged-batch-packs design, engineering wiki index/CLAUDE.md/standards-dir, epic #2390, priority-queue doc, sibling issues #2216/#2227/#2284/#2365/#2207, #2471 v3 decision, calc-citation-contract rule. -->

---

## Pre-Approval Count Pinning (PINNED v3)

The dry-run computation specified in v2 was executed on 2026-04-24 against the canonical inputs (`data/document-index/standards-transfer-ledger.yaml`, `data/design-codes/code-registry.yaml`). Results below are committed inline so the equality acceptance gate is falsifiable from the plan body alone:

```
# Dry run results — 2026-04-24
DOMAINS_IN_SLICE = {"cathodic-protection", "pipeline", "structural"}
EXCLUDED_ORGS = {"OCIMF", "CSA"}
design_code_ids = {  # from data/design-codes/code-registry.yaml (n=10)
  "API-RP-1111", "API-RP-2A-WSD", "API-RP-2RD", "ASME-B31.4", "BS-7910",
  "DNV-RP-C203", "DNV-RP-C205", "DNV-RP-F105", "DNV-ST-F101", "ISO-13628-7"
}

# Exclusion-impact ladder:
#   domain in slice:                145
#   after org exclusion:            145 (dropped 0 — no OCIMF/CSA rows in these 3 domains)
#   after registry exclusion:       140 (dropped 5 ledger rows that are also design-code ids)
#   after summary-evidence gate:     68 (dropped 72 rows lacking notes AND summary)

EXPECTED_SLICE_COUNT = 68
EXPECTED_SLICE_ID_CHECKSUM = "a7996eb6b79f9882b35f5fe33fca36fd144c67a1ff5e10525bd7d260306e4d70"
# Computed as: sha256("\n".join(sorted([e["id"] for e in slice_entries]))).hexdigest()

# Per-domain final counts:
#   cathodic-protection: 4
#   pipeline:           22
#   structural:         42

# Per-domain × org cross-tab (raw, before any filter except domain):
#   cathodic-protection: API=4, ASTM=5, DNV=6, ISO=4
#   pipeline:           API=30, DNV=15, ISO=7, (blank-org)=3
#   structural:         API=18, ASTM=23, BS=1, ISO=2, (blank-org)=27
# OCIMF=0 and CSA=0 in all three slice domains, confirming Claude r1 P3
# cathodic-protection × OCIMF/CSA question: NO impact, exclusion is a no-op
# at the domain level. Only registry overlap (5 rows) and missing-summary
# (72 rows) trim the slice.
```

**Acceptance gate (equality, not range):** the post-run row count MUST equal **68** AND the sha256 of the sorted ledger-ids in the emitted reports MUST equal **`a7996eb6b79f9882b35f5fe33fca36fd144c67a1ff5e10525bd7d260306e4d70`**. If either differs, the lane fails and the plan re-enters review.

---

## Topic Clustering Rule (UPDATED v3 — addresses Claude r2 P3 #6 + #10)

The pre-landed fixture `data/document-index/standards-topic-clusters.yaml` carries the following deterministic schema (now including explicit `<domain>-other` rows so unmatched assignments render in the per-domain keyword tables):

```yaml
version: 1
clusters:
  cathodic-protection:
    - cluster_id: cp-design
      keywords: ["design", "anode", "current density"]
    - cluster_id: cp-monitoring
      keywords: ["monitoring", "potential", "survey"]
    - cluster_id: cp-coating
      keywords: ["coating", "fbe", "interaction"]
    - cluster_id: cp-other
      keywords: []
  pipeline:
    - cluster_id: pipe-design
      keywords: ["design", "wall thickness", "pressure"]
    - cluster_id: pipe-inspection
      keywords: ["inspection", "ili", "ndt"]
    - cluster_id: pipe-corrosion
      keywords: ["corrosion", "internal", "mic"]
    - cluster_id: pipe-materials
      keywords: ["material", "linepipe", "cra"]
    - cluster_id: pipe-other
      keywords: []
  structural:
    - cluster_id: struct-fatigue
      keywords: ["fatigue", "sn", "viv"]
    - cluster_id: struct-strength
      keywords: ["strength", "buckling", "ultimate"]
    - cluster_id: struct-foundation
      keywords: ["foundation", "pile", "soil"]
    - cluster_id: struct-other
      keywords: []
```

**Assignment rule (deterministic, tie-break specified):** case-insensitive substring match against `entry.title + " " + entry.notes + " " + entry.summary`. For each entry, score every cluster by the longest matching keyword's character length (0 if no match). Winner = highest score; ties broken by `cluster_id` lexicographic order. Entries with score 0 land in `<domain>-other`. Per-domain reports include the full keyword table inline (including `<domain>-other`'s empty list) so a reviewer can challenge a specific assignment by hand.

---

## Slug Normalization Rule (UPDATED v3 — addresses Claude r2 P2 #5 + Gemini r2 P2 #2 + collision detection)

Pseudocode:
```
import hashlib, re

def to_slug(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)   # broadened from r"[/. ]+"; covers (, ), &, ,, /, ., whitespace, etc.
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")

def propose_target_page(entry, aliases):
    # Standard-specific entry → wiki/standards/<slug>.md per #2471 v3
    if entry.get("type") == "standard" or entry.get("id"):
        slug = to_slug(entry["id"])
        # Check the pre-landed alias fixture for a canonical-reviewer-judgment override
        if entry["id"] in aliases:
            return aliases[entry["id"]]   # absolute path under wiki/standards/
        return f"knowledge/wikis/engineering/wiki/standards/{slug}.md"
    return f"knowledge/wikis/engineering/wiki/concepts/{to_slug(entry['topic'])}.md"
```

**Canonical-slug verification table** (refreshed for the broadened regex):

| Ledger `id` example | `to_slug()` output | Existing file | Resolution |
|---|---|---|---|
| `API 579-1` | `api-579-1` | none — no exact match | `manual_alias` → `api-579-ffs.md` (in `standards-aliases.yaml`) |
| `API 579-1/ASME FFS-1` | `api-579-1-asme-ffs-1` | none — no exact match | `manual_alias` → `api-579-ffs.md` (in `standards-aliases.yaml`) |
| `DNV-OS-E301` | `dnv-os-e301` | EXISTS | direct (extend-only) |
| `DNV-RP-C203` | `dnv-rp-c203` | EXISTS | direct (extend-only) — but EXCLUDED by registry filter |
| `DNV-RP-C205` | `dnv-rp-c205` | EXISTS | direct (extend-only) — but EXCLUDED by registry filter |
| `DNV-RP-F101` | `dnv-rp-f101` | EXISTS | direct (extend-only) |
| `DNV-RP-F105` | `dnv-rp-f105` | EXISTS | direct (extend-only) — but EXCLUDED by registry filter |
| `OCIMF MEG4` | `ocimf-meg4` | EXISTS (excluded by org filter) | n/a |
| `API-RP-2A-WSD (1993)` | `api-rp-2a-wsd-1993` | none | `manual_alias` if reviewer-judgment maps to existing page; else `create` (— but EXCLUDED by registry filter) |

**Collision detection (deterministic v3):** after computing all `target_page` values, group by path using `collections.defaultdict(list)`. If two ledger rows produce the same path, both rows get `collision_group_id = hashlib.sha256(target_page.encode("utf-8")).hexdigest()[:16]` and the post-run test `post_run_no_silent_collisions` fails the run unless the extend-vs-create map explicitly notes which row owns the page and why.

---

## Standards-Aliases Fixture (NEW v3 — addresses Claude r2 P2 #6)

A new pre-landed fixture `data/document-index/standards-aliases.yaml` records the human-curated canonical-page overrides for ledger ids whose `to_slug()` output does not match an existing wiki standards page. Schema:

```yaml
version: 1
aliases:
  "API 579-1":
    target_page: knowledge/wikis/engineering/wiki/standards/api-579-ffs.md
    note: "API 579 is canonically pegged to the ASME FFS overview page"
  "API 579-1/ASME FFS-1":
    target_page: knowledge/wikis/engineering/wiki/standards/api-579-ffs.md
    note: "Joint API/ASME standard; same canonical page"
```

**Pre-land sequence:** the alias fixture commits BEFORE the per-domain reports run (same atomic commit as the topic-clusters fixture is acceptable). Test `pre_run_aliases_fixture_exists` enforces presence; if absent, the lane fails fast.

**Authorship:** the lane drafter (this plan's executor) authors the alias fixture by inspecting the slug-collision rows surfaced during the dry-run. v3 expects ≤5 alias rows for the 68-entry slice; if more are needed, that's a signal the regex needs further work — the lane MUST surface this rather than silently ballooning the alias table.

---

## Shard-Summary Matching Rule (NEW v3 — addresses Claude r2 P2 #3 + Gemini r2 P3 #3)

`find_shard_summary_rows(entry_id, entry_title)` operates as follows:

```
def find_shard_summary_rows(entry_id, entry_title):
    # Load all 20 shards once at module import; ~50–80MB combined, ~640k summaries.
    # In-memory scan acceptable on standard developer machine.
    hits = []
    norm_id = to_slug(entry_id)
    for record in ALL_SHARD_RECORDS:
        if entry_id in record.get("standards_refs", []):
            hits.append(record)
            continue
        title_lower = record.get("title", "").lower()
        if norm_id and norm_id in title_lower:
            hits.append(record)
    return hits
```

**Determinism invariant:** shard records iterated in stable file order (`shard-00.json` → `shard-09.json` → `ace-shard-00.json` → `ace-shard-09.json`); within each file, original record order preserved. `shard_summary_refs[0]` is therefore deterministic across runs.

**Pre-test seed lock:** `pre_run_shard_match_locked` invokes `find_shard_summary_rows("DNV-OS-E301", "")` and asserts `len(hits) >= 1` (DNV-OS-E301 has documented shard coverage). If the count drifts, shard contents have changed and the slice must be re-validated.

---

## Cross-Provider Gate Decision (NEW v3 — addresses Claude r2 P3 #8)

**Decision:** Claude r3 + Gemini r3 consensus is sufficient for v3 → `status:plan-approved`. Codex r2 re-dispatch is **deferred** to post-#2479 close.

**Rationale:**
1. Per `feedback_codex_cli_0_124_upstream_regression`, the local Codex CLI 0.124.0 stdin-hang regression makes `codex exec` blocking even on 90-byte plans as of 2026-04-24. #2479 tracks the workaround/downgrade.
2. Per `feedback_codex_sandbox_no_execution`, even when Codex is reachable, its sandbox blocks shell execution — its differentiating value is grounded review via the GitHub connector against live state.
3. This plan emits **deterministic, file-only** outputs (3 reports, 2 YAML maps, 1 alias fixture, 1 cluster fixture, 2 helper scripts). There is no live system state to contradict; the load-bearing falsifiability surface is fully captured by static-file + count-equality tests already in §TDD Test List.
4. Per `feedback_codex_sustained_MAJOR_loop` — that precedent triggers on sustained-MAJOR-from-Codex, not on Codex unavailability. It does not apply here.

**Re-review trigger:** if either Claude or Gemini r3 returns MAJOR, the plan re-enters review. If Claude+Gemini r3 both return MINOR or APPROVE, the user gates approval and Codex r2 is re-dispatched non-blockingly post-merge for audit purposes only.

---

## Frontmatter Forward-Adoption (UNCHANGED from v2 — #2471 + calc-citation-contract)

Per the #2471 v3 decision (2026-04-23) and the calc-citation-contract rule, every wiki-ready standards stub emitted into the per-domain reports MUST carry the following frontmatter when targeting `wiki/standards/<slug>.md`:

```yaml
---
code_id: <ledger.id>
publisher: <ledger.org>
revision: <ledger.revision_or_unknown>
jurisdiction: <optional>
supersedes: <optional>
---
```

Stubs targeting `wiki/concepts/` continue to use the existing concept frontmatter; the new fields apply only to the standards subtree. `revision` is permitted to be `unknown` if the ledger does not record one, but MUST appear (per calc-citation-contract: forward-adopt these fields if the page does not yet carry them).

---

## Serialization Protocol (UPDATED v3 — addresses Claude r2 P3 #11)

Per `feedback_multi_agent_commit_serialization` and `feedback_merge_race_silent_revert`:

1. The lane's automated work commits the plan + per-domain reports + extend-vs-create map + provenance sample + topic-clusters fixture + aliases fixture + helper scripts in **one atomic commit** on its own branch. **The lane diff MUST NOT contain `^docs/plans/README.md`** — enforced by `post_run_lane_diff_owned_paths`.
2. Main session (single-writer) appends the `#2373` row to `docs/plans/README.md` AFTER the lane commit lands, in a **separate commit** containing **only** the README diff. Enforced by `post_run_main_diff_owned_paths` (forbids any path other than `^docs/plans/README\.md$`).
3. The main-session README append commit must observe any concurrently-merging Lane B1 plans (#2364, #2369) and serialize after them.
4. If a `[rejected]` push is observed, defer to `feedback_autosync_silent_pusher` (wait + verify reflog) before retrying.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v3) | docs/plans/2026-04-23-issue-2373-batch-pack-4-non-acma-standards-summary-promotion.md |
| Topic-cluster fixture (NEW v2) | data/document-index/standards-topic-clusters.yaml |
| Standards-aliases fixture (NEW v3) | data/document-index/standards-aliases.yaml |
| Slice-count helper script (NEW v3) | scripts/data/document-index/count_slice.py |
| Audithook wrapper script (NEW v3) | scripts/enforcement/audit-no-mnt-ace.py |
| Per-domain report: cathodic-protection | docs/reports/batch-pack-4-non-acma-standards-cathodic-protection.md |
| Per-domain report: pipeline | docs/reports/batch-pack-4-non-acma-standards-pipeline.md |
| Per-domain report: structural | docs/reports/batch-pack-4-non-acma-standards-structural.md |
| Extend-vs-create map | docs/reports/batch-pack-4-extend-vs-create-map.yaml |
| Provenance fixture (sample rows) | docs/reports/batch-pack-4-provenance-sample.yaml |
| Wiki-ready stubs | appended within per-domain reports (no commits to `knowledge/wikis/**` in this wave) |
| Plan review v2 — Claude (MAJOR) | scripts/review/results/20260425T034634Z-plan-2373-v2.md-plan-claude.md |
| Plan review v2 — Gemini (MINOR) | scripts/review/results/20260425T034912Z-plan-2373-v2.md-plan-gemini.md |
| Plan review v1 — Claude (MAJOR) | scripts/review/results/20260424T032933Z-...-plan-claude.md |
| Plan review v1 — Codex (TIMEOUT) | scripts/review/results/20260424T032933Z-...-plan-codex.md (#2479) |
| Plan review v1 — Gemini (MAJOR-fp) | scripts/review/results/20260424T032933Z-...-plan-gemini.md |

---

## Deliverable

Three per-domain Batch Pack 4 execution reports (cathodic-protection, pipeline, structural) containing wiki-ready topic/standard stubs derived exclusively from the existing `standards-transfer-ledger.yaml` entries and the `data/document-index/shards/*.json` summary surface, plus an extend-vs-create YAML map against `knowledge/wikis/engineering/wiki/standards/` (with #2471 v3 frontmatter forward-adopted) and `concepts/`, plus a provenance fixture demonstrating the ledger→shard→stub chain — with zero raw PDF rereads, zero ACMA/OCIMF/CSA (marine) rows, zero `data/design-codes/code-registry.yaml` rows, and no modifications to `knowledge/wikis/**` in this wave. New clustering, aliases, and helper-script artifacts pre-land to make per-domain clustering, slug-collision resolution, and slice-count verification deterministic.

**Note on scope boundary:** Wiki-READY stubs land as artifacts under `docs/reports/`; actual page creation under `knowledge/wikis/engineering/wiki/**` is out of scope for #2373 and belongs to downstream consumers (#2039 engineering wiki ingest umbrella).

---

## Pseudocode

```
# Step 0 — Ensure pre-landed fixtures exist
import hashlib, re, os, yaml, json
from collections import defaultdict

assert os.path.exists("data/document-index/standards-topic-clusters.yaml")
assert os.path.exists("data/document-index/standards-aliases.yaml")
clusters = yaml.safe_load(open("data/document-index/standards-topic-clusters.yaml"))["clusters"]
aliases  = {row_id: spec["target_page"]
            for row_id, spec in (yaml.safe_load(open("data/document-index/standards-aliases.yaml"))["aliases"] or {}).items()}

# Step 1 — Load ledger + maturity
ledger   = yaml.safe_load(open("data/document-index/standards-transfer-ledger.yaml"))
maturity = yaml.safe_load(open("data/document-index/resource-intelligence-maturity.yaml"))

# Step 2 — First-slice filter (pinned constants from §Pre-Approval Count Pinning)
DOMAINS_IN_SLICE = {"cathodic-protection", "pipeline", "structural"}
EXCLUDED_ORGS    = {"OCIMF", "CSA"}
EXPECTED_SLICE_COUNT       = 68
EXPECTED_SLICE_ID_CHECKSUM = "a7996eb6b79f9882b35f5fe33fca36fd144c67a1ff5e10525bd7d260306e4d70"

def collect_design_code_ids(obj):
    out = set()
    if isinstance(obj, dict):
        if isinstance(obj.get("id"), str):
            out.add(obj["id"])
        for v in obj.values():
            out |= collect_design_code_ids(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= collect_design_code_ids(v)
    return out

design_code_ids = collect_design_code_ids(yaml.safe_load(open("data/design-codes/code-registry.yaml")))

def in_slice(entry):
    if entry.get("domain") not in DOMAINS_IN_SLICE: return False
    if entry.get("org") in EXCLUDED_ORGS: return False
    if entry.get("id") in design_code_ids: return False
    if not (entry.get("notes") or entry.get("summary")): return False
    return True

slice_entries = [e for e in ledger["standards"] if in_slice(e)]
assert len(slice_entries) == EXPECTED_SLICE_COUNT, (len(slice_entries), EXPECTED_SLICE_COUNT)

ids_sorted = sorted(e["id"] for e in slice_entries)
checksum   = hashlib.sha256("\n".join(ids_sorted).encode("utf-8")).hexdigest()
assert checksum == EXPECTED_SLICE_ID_CHECKSUM, (checksum, EXPECTED_SLICE_ID_CHECKSUM)

# Step 3 — Deterministic clustering with longest-keyword + lex-tiebreak (Step 0 fixture)
def assign_cluster(entry, domain_clusters):
    haystack = " ".join([entry.get("title",""), entry.get("notes",""), entry.get("summary","")]).lower()
    best = (0, None)  # (longest_kw_len, cluster_id)
    for c in domain_clusters:
        for kw in c["keywords"]:
            if kw in haystack:
                cand = (len(kw), c["cluster_id"])
                if cand > best:    # tuple compare: longer first; lex tiebreak on cluster_id
                    best = cand
    return best[1] or f"{entry['domain']}-other"

per_domain = defaultdict(list)
for e in slice_entries:
    per_domain[e["domain"]].append(e)

# Step 4 — Cross-reference shards (deterministic file order; rule in §Shard-Summary Matching Rule)
ALL_SHARD_RECORDS = []
for shard in sorted(os.listdir("data/document-index/shards")):
    if shard.endswith(".json"):
        with open(f"data/document-index/shards/{shard}") as fh:
            doc = json.load(fh)
            recs = doc if isinstance(doc, list) else doc.get("records", [])
            ALL_SHARD_RECORDS.extend(recs)

def find_shard_summary_rows(entry_id, entry_title):
    hits = []
    norm_id = to_slug(entry_id)
    for record in ALL_SHARD_RECORDS:
        if entry_id in record.get("standards_refs", []):
            hits.append(record); continue
        if norm_id and norm_id in record.get("title","").lower():
            hits.append(record)
    return hits

for entry in slice_entries:
    shard_hits = find_shard_summary_rows(entry["id"], entry.get("title", ""))
    entry["shard_summary_refs"]  = [r.get("path", r.get("id","")) for r in shard_hits]
    entry["has_summary_evidence"] = bool(shard_hits) or bool(entry.get("summary"))

# Step 5 — Extend-vs-create + DETERMINISTIC collision detection (sha256, not built-in hash())
for entry in slice_entries:
    entry["target_page"] = propose_target_page(entry, aliases)
    entry["verdict"]     = "extend-only" if os.path.exists(entry["target_page"]) else "create"

target_groups = defaultdict(list)
for e in slice_entries:
    target_groups[e["target_page"]].append(e)

collisions = {p: rows for p, rows in target_groups.items() if len(rows) > 1}
for p, rows in collisions.items():
    cgid = hashlib.sha256(p.encode("utf-8")).hexdigest()[:16]   # FIX: was hash(p), non-deterministic
    for r in rows:
        r["collision_group_id"] = cgid

# Step 6 — Emit per-domain reports (each with #2471 frontmatter for standards stubs)
for domain, entries in sorted(per_domain.items()):
    write_report(f"docs/reports/batch-pack-4-non-acma-standards-{domain}.md",
                 entries=entries,
                 cluster_assignments={e["id"]: assign_cluster(e, clusters[domain]) for e in entries})

# Step 7 — Emit extend-vs-create map + stratified provenance sample
write_yaml("docs/reports/batch-pack-4-extend-vs-create-map.yaml",
           extend_only=[e for e in slice_entries if e["verdict"] == "extend-only"],
           create=[e for e in slice_entries if e["verdict"] == "create"],
           collisions=collisions)

def stratified_sample(slice_entries):
    out = []
    for d in sorted(DOMAINS_IN_SLICE):
        d_rows = sorted([e for e in slice_entries if e["domain"] == d], key=lambda e: e["id"])
        if not d_rows: continue
        idxs = [0, len(d_rows)//3, 2*len(d_rows)//3]
        out.extend(d_rows[i] for i in idxs)
    multi = next((e for e in slice_entries if len(e["shard_summary_refs"]) > 1), slice_entries[-1])
    if multi not in out: out.append(multi)
    assert any(e["verdict"] == "extend-only" for e in out)
    assert any(e["verdict"] == "create"      for e in out)
    return out[:10]

write_yaml("docs/reports/batch-pack-4-provenance-sample.yaml", rows=stratified_sample(slice_entries))

# Step 8 — Post-run validation gates (below; including audithook wrapper for /mnt/ace/ blocking)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | data/document-index/standards-topic-clusters.yaml | Deterministic clustering fixture (incl. `<domain>-other` rows) |
| Create | data/document-index/standards-aliases.yaml | NEW v3: ledger-id → canonical-page alias fixture (Claude r2 P2 #6) |
| Create | scripts/data/document-index/count_slice.py | NEW v3: invokes the in_slice filter and prints len + checksum (Gemini r2 P2 #1) |
| Create | scripts/enforcement/audit-no-mnt-ace.py | NEW v3: `sys.addaudithook` wrapper that traps any `open` event whose path begins with `/mnt/ace/` and exits non-zero (Claude r2 P3 #8) |
| Create | docs/reports/batch-pack-4-non-acma-standards-cathodic-protection.md | Sub-slice 4a deliverable |
| Create | docs/reports/batch-pack-4-non-acma-standards-pipeline.md | Sub-slice 4b deliverable |
| Create | docs/reports/batch-pack-4-non-acma-standards-structural.md | Sub-slice 4c deliverable |
| Create | docs/reports/batch-pack-4-extend-vs-create-map.yaml | Extend-vs-create + collision-group map (deterministic sha256 group ids) |
| Create | docs/reports/batch-pack-4-provenance-sample.yaml | Stratified 10-row sample (3 per domain + 1 multi-shard) |
| Update (separate commit, **main-session-only — NOT in lane diff**) | docs/plans/README.md | Plan row for #2373 — see §Serialization Protocol; enforced by `post_run_lane_diff_owned_paths` (forbids `^docs/plans/`) and `post_run_main_diff_owned_paths` (only `^docs/plans/README\.md$`) |

**Forbidden / out of scope** (per issue body and Batch Pack 4 design doc §3.4 Paths):
- `knowledge/wikis/**` — read-only; no wiki page commits in this wave
- `/mnt/ace/**` or any source-PDF path — no raw re-reading (audithook enforces)
- `config/**`, `.claude/**`, `tests/**`
- Any ledger entry with `org in {OCIMF, CSA}` or `domain == "marine"` (owned by #2216/#2227/#2284)
- Any entry that also appears in `data/design-codes/code-registry.yaml` (owned by #2365)
- `process` (55), `drilling` (9), and `materials` (122) domains — DEFERRED to later waves (locked v2)

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| pre_run_ledger_exists | Ledger present | `test -f data/document-index/standards-transfer-ledger.yaml` | exit 0 |
| pre_run_clusters_fixture_exists | Topic-cluster fixture pre-landed | `test -f data/document-index/standards-topic-clusters.yaml` | exit 0 |
| pre_run_aliases_fixture_exists | Standards-aliases fixture pre-landed | `test -f data/document-index/standards-aliases.yaml` | exit 0 |
| pre_run_domain_counts | Pre-filter domain tallies | `grep -c "domain: pipeline" ledger` | ≥55 |
| pre_run_shards_exist | All 20 shards present | `ls data/document-index/shards/*.json \| wc -l` | 20 |
| pre_run_design_code_state | Design-code registry verified | `test -f data/design-codes/code-registry.yaml` | exit 0 (file confirmed EXISTS during v3 dry-run; `DESIGN_CODE_EXCLUSION=active`) |
| pre_run_shard_match_locked | Shard matcher returns ≥1 hit for known seed `DNV-OS-E301` | `python3 -c "from <helper> import find_shard_summary_rows; assert find_shard_summary_rows('DNV-OS-E301','')"` | exit 0 |
| post_run_slice_count_exact | Post-filter row count matches pinned EXPECTED_SLICE_COUNT | `python3 scripts/data/document-index/count_slice.py` | prints `68` |
| post_run_slice_id_checksum | Sorted-id sha256 matches pinned EXPECTED_SLICE_ID_CHECKSUM | `python3 scripts/data/document-index/count_slice.py --checksum` | prints `a7996eb6b79f9882b35f5fe33fca36fd144c67a1ff5e10525bd7d260306e4d70` |
| post_run_yaml_parses | Extend-vs-create YAML parses | `python3 -c "import yaml; yaml.safe_load(open(...))"` | exit 0 |
| post_run_provenance_parses | Provenance sample YAML parses | same | exit 0 |
| post_run_no_marine | No marine/ACMA rows escaped | grep for `domain: marine` in reports | 0 matches |
| post_run_no_ocimf_csa | No OCIMF/CSA rows escaped | grep for `org: OCIMF` or `org: CSA` | 0 matches |
| post_run_no_design_code_overlap | No row in design-code registry | cross-compare against `data/design-codes/code-registry.yaml` | empty intersection |
| post_run_all_extend_pages_exist | Every `extend-only` row references a real wiki page | `test -f` per page path | exit 0 per row |
| post_run_provenance_chain | Every sample row has `ledger_id` + `shard_summary_ref` + `proposed_stub_target` | YAML validation | 10/10 complete |
| post_run_provenance_stratification | Sample = 3 per domain + 1 multi + ≥1 extend-only + ≥1 create | YAML row inspection | passes |
| post_run_no_wiki_writes | No wiki pages modified | `git diff --cached --name-only \| grep '^knowledge/wikis/'` | empty (and pre-commit guard fails the commit if non-empty) |
| post_run_lane_diff_owned_paths | Lane commit stays in lane-owned paths only | `git diff --name-only \| grep -v '^docs/reports/' \| grep -v '^data/document-index/' \| grep -v '^scripts/data/document-index/' \| grep -v '^scripts/enforcement/' \| wc -l` | 0; AND lane diff MUST NOT include any `^docs/plans/` path |
| post_run_main_diff_owned_paths | Main-session README append commit stays minimal | main-session commit's `git diff --name-only` | exactly one path matching `^docs/plans/README\.md$` |
| post_run_no_source_reads_diff | No `/mnt/ace/` paths in diff | `git diff --cached \| grep '/mnt/ace/'` | 0 matches (pre-commit guard) |
| post_run_no_source_reads_audit | No open() against `/mnt/ace/**` during execution | wrapper at `scripts/enforcement/audit-no-mnt-ace.py` uses `sys.addaudithook` filtering on `open` events with path-prefix `/mnt/ace/` and exits non-zero on hit; main lane runs under `python3 -X dev scripts/enforcement/audit-no-mnt-ace.py -- <real-script>` | exit 0 |
| post_run_frontmatter_standards | Wiki-ready stubs targeting `wiki/standards/` carry `code_id`, `publisher`, `revision` | YAML frontmatter inspection per stub | all three fields present |
| post_run_no_silent_collisions | No two ledger rows silently map to same target page | extend-vs-create map collision-group inspection | every collision has explicit owner-row note |
| post_run_collision_id_deterministic | `collision_group_id` is a 16-hex sha256 prefix, not a Python `hash()` int | regex `^[0-9a-f]{16}$` per collision row | all rows match |
| post_run_clustering_deterministic | Re-running emission produces identical cluster_ids per ledger row | rerun pseudocode Steps 0–6 in fresh process; diff cluster-assignment dicts | empty diff |

**Audithook reference snippet** (lives in `scripts/enforcement/audit-no-mnt-ace.py`):
```python
import sys
def _hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes)):
        path = args[0] if isinstance(args[0], str) else args[0].decode("utf-8", "replace")
        if path.startswith("/mnt/ace/"):
            sys.stderr.write(f"BLOCKED open on /mnt/ace/ path: {path}\n")
            raise SystemExit(2)
sys.addaudithook(_hook)
# Then: exec the real lane script via runpy with the hook installed
```

---

## Acceptance Criteria

- [ ] Three per-domain reports exist: `batch-pack-4-non-acma-standards-{cathodic-protection,pipeline,structural}.md`
- [ ] Topic-cluster fixture `data/document-index/standards-topic-clusters.yaml` pre-lands BEFORE per-domain reports run, including `<domain>-other` declarations
- [ ] Standards-aliases fixture `data/document-index/standards-aliases.yaml` pre-lands BEFORE per-domain reports run (NEW v3)
- [ ] Combined post-filter row count equals `EXPECTED_SLICE_COUNT = 68` (PINNED v3, NOT a range)
- [ ] Sorted-id sha256 equals `EXPECTED_SLICE_ID_CHECKSUM = a7996eb6b79f9882b35f5fe33fca36fd144c67a1ff5e10525bd7d260306e4d70` (PINNED v3)
- [ ] `docs/reports/batch-pack-4-extend-vs-create-map.yaml` parses; every row labelled `extend-only` or `create`; collisions explicit; every `collision_group_id` is a 16-hex sha256 prefix
- [ ] `docs/reports/batch-pack-4-provenance-sample.yaml` contains 10 rows stratified per §Pseudocode Step 7 (3 per domain + 1 multi-shard, ≥1 extend-only, ≥1 create)
- [ ] Zero rows with `domain == "marine"`, `org in {OCIMF, CSA}`, or `id` also in `data/design-codes/code-registry.yaml`
- [ ] Zero files under `knowledge/wikis/**` modified by this plan's commits (pre-commit guard + post-commit grep)
- [ ] Zero reads of `/mnt/ace/**` (diff grep + `sys.addaudithook`-based wrapper at `scripts/enforcement/audit-no-mnt-ace.py`)
- [ ] Every `extend-only` row references an existing file under `knowledge/wikis/engineering/wiki/{standards,concepts}/`
- [ ] Every wiki-ready stub targeting `wiki/standards/<slug>.md` carries `code_id`, `publisher`, `revision` frontmatter (revision may be `unknown`) per #2471 v3
- [ ] `materials` (122 entries), `process` (55), and `drilling` (9) domains are LOCKED as deferred — not open questions
- [ ] Lane commit diff contains zero `^docs/plans/` paths (lane is plan + reports + fixtures + helper scripts only); main-session README append is a separate single-file commit
- [ ] Re-running emission in a fresh process produces byte-identical `collision_group_id` and `cluster_id` outputs
- [ ] Review artifacts posted to `scripts/review/results/<timestamp>-...-plan-{claude,gemini}.md`; Codex r2 deferred to post-#2479 per §Cross-Provider Gate Decision

---

## Adversarial Review Summary

| Provider | v1 Verdict | v2 Verdict | Disposition for v3 |
|---|---|---|---|
| Claude | MAJOR (8 items) | MAJOR (10 items) | All 10 items addressed surgically per §v3 Revision Log |
| Codex | UNAVAILABLE (timeout — #2479) | UNAVAILABLE (#2479 still open) | Deferred per §Cross-Provider Gate Decision; non-blocking re-dispatch post-merge |
| Gemini | MAJOR (2 false-positive items) | MINOR (3 items) | All 3 folded per §v3 Revision Log |

**Overall result:** v3 PENDING re-review (Claude + Gemini r3)

---

## Risks and Open Questions

- **Risk:** `marine` domain in the ledger is broader than ACMA/OCIMF/CSA. Mitigation: blanket-exclude `domain == "marine"`; carry forward to a later issue.
- **Risk:** Ledger `status == "done"` does NOT imply an existing wiki page. Mitigation: file-existence check for extend-vs-create classification.
- **Risk:** Topic-cluster keyword tables may misclassify edge cases. Mitigation: per-domain reports include the full keyword table inline (including `<domain>-other` empty-keyword row); misclassifications become surgical follow-ups, not silent. Tie-break is longest-keyword + lex-`cluster_id`.
- **Risk:** Provenance fixture is 10 stratified rows. Mitigation: stratification rule pinned; full coverage deferred to #2207 / #2039 ingest.
- **Risk:** Parallel Lane B1 (#2364, #2369) may write `docs/plans/README.md` concurrently. Mitigation: §Serialization Protocol — main-session-only README append, after lane content commits, enforced by lane-vs-main owned-path tests.
- **Risk:** Standards-aliases fixture grows unbounded if `to_slug()` regex still misses cases. Mitigation: v3 limits the alias table to ≤5 entries; if more are needed the lane MUST surface this rather than silently ballooning.
- **Risk:** Codex r2 deferred — review surface is Claude+Gemini-only for v3 approval. Mitigation: §Cross-Provider Gate Decision documents the rationale (Codex differential value is live-state grounding; this plan is file-only deterministic emission).
- **Open:** None for v3 (all v2 review items resolved; deferral set is locked).

---

## Complexity: T2

**T2** — new reports across 8 files (3 reports + 2 YAML maps + 2 fixtures + 1 helper script + 1 audithook), non-trivial filter (three exclusion conditions + summary-evidence gate), extend-vs-create detection against two wiki page families with deterministic collision detection (sha256 group ids), stratified provenance fixture, frontmatter forward-adoption, clear acceptance gates with pinned exact count AND pinned id-checksum. Not T1 (multiple files + new schema + helper scripts); not T3 (no multi-repo, no `src/` code, no new standards).
