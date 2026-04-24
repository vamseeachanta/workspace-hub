# Plan for #2373: Execute Batch Pack 4 for non-ACMA standards summary promotion

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2373
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2373-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `data/document-index/standards-transfer-ledger.yaml` (7,727 lines, total=436 entries) — canonical L2 ledger with `domain`, `org`, `status`, `notes`, `summary`, `repo`, `modules`, `implemented_at` fields per standard.
- Found: `data/document-index/resource-intelligence-maturity.yaml` — authoritative maturity status (documents_in_scope=425; 639,585 index summaries; reclassification to 10 domains complete; `process`=55 and `drilling`=9 domains new).
- Found: `data/document-index/shards/shard-00.json` … `shard-09.json` + `ace-shard-00.json` … `ace-shard-09.json` — document-index shards with existing summaries (no source PDFs read required).
- Found: `docs/reports/llm-wiki-staged-batch-packs.md` §3.4 — Batch Pack 4 design document specifying scope, sub-slicing (4a–4j by domain), owned/read-only/forbidden paths, and validation sequence.
- Gap: No Batch Pack 4 promotion artifact under `docs/reports/batch-pack-4-*.md` exists yet.

### Standards
| Standard family | Status | Source |
|---|---|---|
| `cathodic-protection` domain (19 entries) | summary-backed; 47.4% calc implemented | `data/document-index/standards-transfer-ledger.yaml` |
| `pipeline` domain (55 entries) | summary-backed; 21.8% calc implemented | `data/document-index/standards-transfer-ledger.yaml` |
| `structural` domain (71 entries) | summary-backed; 5.6% calc implemented | `data/document-index/standards-transfer-ledger.yaml` |
| `marine` domain (42 entries) | reserved for ACMA/OCIMF/CSA scope (#2216, #2227, #2284) — EXCLUDED from this wave | issue #2373 scope |
| `process` domain (55 entries) | new domain (zero prior calc coverage) — DEFERRED (out of this wave's first slice) | maturity YAML |
| `drilling` domain (9 entries) | new domain (zero prior calc coverage) — DEFERRED (out of this wave's first slice) | maturity YAML |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/` — 7 pages exist: `api-579-ffs.md`, `dnv-os-e301.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `ocimf-meg4.md`. Exact-match entries in the ledger for these are extend-only (except `ocimf-meg4` which is explicitly ACMA/OCIMF and excluded).
- `knowledge/wikis/engineering/wiki/index.md` — existing concept pages already cover `pipeline-integrity-assessment`, `free-span-viv-fatigue`, `sn-curve-fatigue-definitions`, `cathodic-protection-design`, `structural-analysis-offshore`. Some stubs would be extend-only via concept cross-linking.
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema; `standards/` is the correct page family for standard-specific topics; `concepts/` for topic/domain-level summaries.
- `knowledge/wikis/marine-engineering/wiki/` — has no `standards/` subdir; if a marine standard surfaces accidentally it must be carried forward to #2216/#2227/#2284 scope, not promoted here.

### Documents consulted
- Parent epic #2390 — Batch Pack 4 assigned to Wave 7 (after Wave 6 Batch Packs 1+3); explicitly standalone, not paired.
- Issue #2373 body — scope locked to non-ACMA domains, first slice `cathodic-protection + pipeline + structural`, summary/ledger evidence only, no raw PDF rereads; excludes #2216/#2227/#2284 ACMA/OCIMF/CSA work and #2365 design-code-registry work.
- `docs/reports/llm-wiki-external-source-priority-queue.md` §5 — ranks `standards-with-existing-summaries` as P1 family; aligns with this wave's scope.
- Issue #2365 — design-code registry promotion is a sibling effort that sources from `data/design-codes/code-registry.yaml` (not the ledger); overlap avoided by restricting this wave to the `standards-transfer-ledger.yaml` + shards.
- Issue #2207 — provenance/reuse contract; outputs of this wave must cite ledger entries and shard summaries by stable key (ledger `id` + shard record path).

### Gaps identified
- No extend-vs-create mapping exists from ledger entries to `knowledge/wikis/engineering/wiki/standards/*.md` or `concepts/*.md`.
- No provenance fixture linking a shard summary to a ledger entry to a proposed wiki stub.
- `marine` domain overlap boundary is not mechanically enforced — must be hand-verified per row before classifying any marine-tagged standard into or out of this wave's scope (issue body requires exclusion of ACMA/OCIMF/CSA, which are the marine ledger subset).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2373` — OPEN — "feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion"
- `#2390` — OPEN — epic coordinator
- `#2216` — scope-excluded ACMA work
- `#2227` — scope-excluded OCIMF work
- `#2284` — scope-excluded CSA work
- `#2365` — scope-excluded design-code-registry work
- `#2039` — engineering wiki ingest umbrella (downstream consumer)

**File existence** (`ls -la` 2026-04-23):
- EXISTS: `data/document-index/standards-transfer-ledger.yaml` (7,727 lines)
- EXISTS: `data/document-index/resource-intelligence-maturity.yaml` (59 lines)
- EXISTS: `data/document-index/shards/` (20 shard files — shard-00..09 + ace-shard-00..09)
- EXISTS: `knowledge/wikis/engineering/wiki/standards/` (7 standards pages)
- EXISTS: `knowledge/wikis/engineering/wiki/concepts/` (33 concept pages)
- EXISTS: `docs/reports/llm-wiki-staged-batch-packs.md`
- MISSING (new — this plan creates): `docs/reports/batch-pack-4-non-acma-standards-cathodic-protection.md`
- MISSING (new — this plan creates): `docs/reports/batch-pack-4-non-acma-standards-pipeline.md`
- MISSING (new — this plan creates): `docs/reports/batch-pack-4-non-acma-standards-structural.md`
- MISSING (new — this plan creates): `docs/reports/batch-pack-4-extend-vs-create-map.yaml`
- MISSING (new — this plan creates): `docs/reports/batch-pack-4-provenance-sample.yaml`

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
First-slice target = cathodic-protection + pipeline + structural = 19 + 55 + 71 = **145 entries**.

**Gap proofs**:
- `ls docs/reports/batch-pack-4*` → "No such file or directory" → confirms no per-domain report exists yet.
- `ls knowledge/wikis/engineering/wiki/standards/api-579-ffs.md` → EXISTS → confirms extend-only for API 579 structural entry.
- `ls knowledge/wikis/marine-engineering/wiki/standards/` → "No such file or directory" → marine-engineering wiki has no `standards/` family, so any marine standard would mis-place.

<!-- 7 distinct sources consulted: issue body, standards-transfer-ledger.yaml, resource-intelligence-maturity.yaml, staged-batch-packs design, engineering wiki index/CLAUDE.md/standards-dir, epic #2390, priority-queue doc, and sibling issues #2216/#2227/#2284/#2365/#2207. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-23-issue-2373-batch-pack-4-non-acma-standards-summary-promotion.md |
| Per-domain report: cathodic-protection | docs/reports/batch-pack-4-non-acma-standards-cathodic-protection.md |
| Per-domain report: pipeline | docs/reports/batch-pack-4-non-acma-standards-pipeline.md |
| Per-domain report: structural | docs/reports/batch-pack-4-non-acma-standards-structural.md |
| Extend-vs-create map | docs/reports/batch-pack-4-extend-vs-create-map.yaml |
| Provenance fixture (sample rows) | docs/reports/batch-pack-4-provenance-sample.yaml |
| Wiki-ready stubs | appended within per-domain reports (no commits into `knowledge/wikis/**` in this wave — see Deliverable note) |
| Plan review — Claude | scripts/review/results/2026-04-23-plan-2373-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-23-plan-2373-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-23-plan-2373-gemini.md |

---

## Deliverable

Three per-domain Batch Pack 4 execution reports (cathodic-protection, pipeline, structural) containing wiki-ready topic/standard stubs derived exclusively from the existing `standards-transfer-ledger.yaml` entries and the `data/document-index/shards/*.json` summary surface, plus an extend-vs-create YAML map against `knowledge/wikis/engineering/wiki/standards/` and `concepts/`, plus a provenance fixture demonstrating the ledger→shard→stub chain — with zero raw PDF rereads, zero ACMA/OCIMF/CSA (marine) rows, zero `data/design-codes/code-registry.yaml` rows, and no modifications to `knowledge/wikis/**` in this wave.

**Note on scope boundary:** As with Batch Pack 3, this issue commits wiki-READY stubs as artifacts under `docs/reports/`; the actual page creation under `knowledge/wikis/engineering/wiki/**` is out of scope for #2373 and belongs to downstream consumers (#2039 engineering wiki ingest umbrella).

---

## Pseudocode

```
# Step 1 — Load ledger + maturity
ledger = yaml.safe_load("data/document-index/standards-transfer-ledger.yaml")
maturity = yaml.safe_load("data/document-index/resource-intelligence-maturity.yaml")

# Step 2 — First-slice filter: non-ACMA / non-design-code
DOMAINS_IN_SLICE = {"cathodic-protection", "pipeline", "structural"}
# Excluded orgs (ACMA/OCIMF/CSA scope already owned by #2216/#2227/#2284)
EXCLUDED_ORGS = {"OCIMF", "CSA"}
# Excluded ids (design-code registry scope already owned by #2365)
design_code_ids = load_design_code_registry_ids()  # read-only glance

def in_slice(entry):
    if entry.domain not in DOMAINS_IN_SLICE: return False
    if entry.org in EXCLUDED_ORGS: return False
    if entry.id in design_code_ids: return False
    if not entry.get("notes") and not entry.get("summary"):
        return False  # no summary evidence — carry forward to #2305/#2325 re-index
    return True

slice_entries = [e for e in ledger["standards"] if in_slice(e)]
# Pre-run count gate: len(slice_entries) must equal 145 minus the excluded/CSA/OCIMF rows

# Step 3 — Group and cluster
per_domain = groupby(slice_entries, key=lambda e: e.domain)
for domain, entries in per_domain:
    topic_clusters = cluster_by_topic(entries)  # e.g., pipeline → design/inspection/corrosion/materials

# Step 4 — Cross-reference shards for existing summaries
for entry in slice_entries:
    shard_hits = find_shard_summary_rows(entry.id, entry.title)
    entry.shard_summary_refs = [r.path for r in shard_hits]
    entry.has_summary_evidence = bool(shard_hits) or bool(entry.summary)

# Step 5 — Extend-vs-create classification
existing_pages = list("knowledge/wikis/engineering/wiki/standards/*.md") \
               + list("knowledge/wikis/engineering/wiki/concepts/*.md")
for entry in slice_entries:
    entry.target_page = propose_target_page(entry)  # concept page for topic-level, standard page for standard-specific
    entry.verdict = "extend-only" if entry.target_page in existing_pages else "create"

# Step 6 — Emit per-domain reports
for domain, entries in per_domain:
    write_report(f"docs/reports/batch-pack-4-non-acma-standards-{domain}.md",
                 entries=entries, topic_clusters=topic_clusters_for(domain))

# Step 7 — Emit extend-vs-create map + provenance sample
write_yaml("docs/reports/batch-pack-4-extend-vs-create-map.yaml",
           extend_only=[e for e in slice_entries if e.verdict == "extend-only"],
           create=[e for e in slice_entries if e.verdict == "create"])
# Provenance sample: ~10 rows showing ledger→shard→stub chain end-to-end
write_yaml("docs/reports/batch-pack-4-provenance-sample.yaml",
           rows=sample(slice_entries, 10))

# Step 8 — Post-run validation gates (below)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/reports/batch-pack-4-non-acma-standards-cathodic-protection.md | Sub-slice 4a deliverable (~19 entries grouped by topic) |
| Create | docs/reports/batch-pack-4-non-acma-standards-pipeline.md | Sub-slice 4b deliverable (~55 entries grouped by design/inspection/corrosion/materials) |
| Create | docs/reports/batch-pack-4-non-acma-standards-structural.md | Sub-slice 4c deliverable (~71 entries grouped by structural topic clusters) |
| Create | docs/reports/batch-pack-4-extend-vs-create-map.yaml | Extend-vs-create decision map against engineering wiki standards/ and concepts/ |
| Create | docs/reports/batch-pack-4-provenance-sample.yaml | 10-row sample demonstrating ledger→shard→stub provenance chain per #2207 |
| Update | docs/plans/README.md | Add plan row for #2373 |

**Forbidden / out of scope for this wave** (per issue body and Batch Pack 4 design doc §3.4 Paths):
- `knowledge/wikis/**` — read-only; no wiki page commits
- `/mnt/ace/**` or any source-PDF path — no raw re-reading
- `config/**`, `.claude/**`, `tests/**`
- Any ledger entry with `org in {OCIMF, CSA}` or `domain == "marine"` (owned by #2216/#2227/#2284)
- Any entry that also appears in `data/design-codes/code-registry.yaml` (owned by #2365)
- `process` domain (55 entries) and `drilling` domain (9 entries) — zero prior calc coverage; deferred to a later wave per issue body "first slice" boundary

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| pre_run_ledger_exists | Ledger present | `test -f data/document-index/standards-transfer-ledger.yaml` | exit 0 |
| pre_run_domain_counts | Pre-filter domain tallies | `grep -c "domain: pipeline" ledger` | ≥55 (inclusive of excluded rows before filter) |
| pre_run_shards_exist | Shards present | `ls data/document-index/shards/*.json \| wc -l` | 20 |
| post_run_yaml_parses | Extend-vs-create YAML parses | `python3 -c "import yaml; yaml.safe_load(...)"` | exit 0 |
| post_run_provenance_parses | Provenance sample YAML parses | same | exit 0 |
| post_run_no_marine | No marine/ACMA rows escaped the filter | grep for `domain: marine` in per-domain reports | 0 matches |
| post_run_no_ocimf_csa | No OCIMF/CSA rows escaped the filter | grep for `org: OCIMF` or `org: CSA` in reports | 0 matches |
| post_run_no_design_code_overlap | No row also in design-code registry | cross-compare against `data/design-codes/code-registry.yaml` | empty intersection |
| post_run_all_extend_pages_exist | Every `extend-only` row references a real wiki page | `test -f` per page path | exit 0 per row |
| post_run_provenance_chain | Every sample row has ledger_id + shard_ref + proposed_stub | YAML validation | 10/10 complete |
| post_run_no_wiki_writes | No wiki pages modified | `git diff --name-only \| grep -c '^knowledge/wikis/'` | 0 |
| post_run_only_owned_paths | Changes stay in owned paths | `git diff --name-only \| grep -v -E '^(docs/reports/\|docs/plans/)' \| wc -l` | 0 |
| post_run_no_source_reads | No mount reads | no filesystem access to `/mnt/ace/**` during execution | 0 |

---

## Acceptance Criteria

- [ ] Three per-domain reports exist: `batch-pack-4-non-acma-standards-{cathodic-protection,pipeline,structural}.md`
- [ ] Combined rows across the three reports = first-slice candidate count after exclusions (expected ≤145, with ACMA/OCIMF/CSA/design-code overlap removed); the report documents the exact post-filter count
- [ ] `docs/reports/batch-pack-4-extend-vs-create-map.yaml` parses and every row is labelled `extend-only` or `create`
- [ ] `docs/reports/batch-pack-4-provenance-sample.yaml` contains 10 rows, each with `ledger_id`, `shard_summary_ref`, and `proposed_stub_target`
- [ ] Zero rows with `domain == "marine"`, `org in {OCIMF, CSA}`, or `id` also present in `data/design-codes/code-registry.yaml` appear in any of the three per-domain reports
- [ ] Zero files under `knowledge/wikis/**` modified by this plan's commits
- [ ] Zero reads of `/mnt/ace/**` or any raw source PDF
- [ ] Every `extend-only` row references a file that actually exists under `knowledge/wikis/engineering/wiki/standards/` or `knowledge/wikis/engineering/wiki/concepts/`
- [ ] Review artifacts posted to `scripts/review/results/2026-04-23-plan-2373-*.md`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | dispatched |
| Codex | PENDING | dispatched |
| Gemini | PENDING | dispatched |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk:** The `marine` domain in the ledger is broader than ACMA/OCIMF/CSA — some entries may be non-ACMA marine standards that still match the issue's spirit. Mitigation: blanket-exclude `domain == "marine"` in this wave; carry forward to a later issue so #2216/#2227/#2284 can decide.
- **Risk:** Ledger entry `status == "done"` does NOT imply an existing wiki page — `done` means "summary recorded". This plan uses a file-existence check (`test -f knowledge/wikis/engineering/wiki/{standards,concepts}/<slug>.md`) to classify extend-vs-create, not the ledger status field.
- **Risk:** Topic-cluster definitions (pipeline → design/inspection/corrosion/materials) are editorial. Mitigation: per-domain report must explicitly list the clustering rule used so a reviewer can challenge it; alternative clusterings become carry-forward follow-ups.
- **Risk:** Provenance fixture is only 10 rows — cannot prove end-to-end chain for all 145 entries. Mitigation: #2207 contract already covers the general policy; this plan's fixture is a sampled smoke-check, with full coverage deferred to downstream ingest.
- **Risk:** Process/drilling domains have zero existing calc coverage — if a reviewer argues they should be in the first slice, scope grows from 145 to 209. Defer to user during plan-approval.
- **Risk:** Parallel Lane B1 (#2364, #2369) may be writing `docs/plans/README.md` concurrently. Mitigation: serialized commit through main session; this lane writes plan + reports only.
- **Open:** Should `materials` (122 entries) be added to a second slice in this wave, or kept as a separate wave? Issue body says "first slice = cathodic-protection + pipeline + structural", so materials is deferred. Confirm with user.
- **Open:** Should topic-cluster rules be authored into a reusable `data/document-index/standards-topic-clusters.yaml` now, or emitted inline per report? Default: inline this wave; factor out when a second issue reuses them.

---

## Complexity: T2

**T2** — new reports across 5 files, non-trivial filter (three exclusion conditions), extend-vs-create detection against two wiki page families, provenance fixture, clear acceptance gates. Not T1; not T3 (no multi-repo, no `src/` code, no new standards).
