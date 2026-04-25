# Plan for #2373: Execute Batch Pack 4 for non-ACMA standards summary promotion

> **Status:** draft (v2)
> **Complexity:** T2
> **Date:** 2026-04-23 (v2 revised 2026-04-24)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2373
> **Review artifacts (v1):** scripts/review/results/20260424T032933Z-2026-04-23-issue-2373-batch-pack-4-non-acma-standards-summary-promotion.md-plan-{claude,codex,gemini}.md

---

## v2 Revision Log (surgical deltas only)

Addresses Claude r1 MAJOR (8 items). Gemini r1 MAJOR was based on two file-existence claims (ace-shards, engineering wiki standards pages) that local `ls` showed false; v2 pre-empts re-occurrence by pinning the falsifiability evidence inline. Codex r1 timed out (#2406 / #2479 stdin-hang regression) — no findings to fold. Forward-adopts the `wiki/standards/` sanction landed in #2471 v3 (decision dated 2026-04-23) for any standards-page extend-vs-create classification.

| # | Claude r1 item | v2 delta |
|---|---|---|
| 1 | P1 — topic-clustering rule undefined / "editorial" | Will pre-land `data/document-index/standards-topic-clusters.yaml` BEFORE per-domain reports run; clustering becomes deterministic keyword-table lookup. Schema documented in §Topic Clustering Rule below. |
| 2 | P1 — pre-run count gate has unbounded `≤145` | Will run the `in_slice` filter during plan-approval (no commits) and pin EXACT expected post-filter count as `EXPECTED_SLICE_COUNT` constant; acceptance criterion will be equality, not range. Computation procedure captured in §Pre-Approval Count Pinning. |
| 3 | P2 — design-code-registry exclusion depends on file whose existence is unverified | §Evidence will add `ls -la data/design-codes/code-registry.yaml` outcome AND a guard: if file is absent or empty, plan logs `DESIGN_CODE_EXCLUSION=noop` and proceeds (does not silently treat exclusion as effective). |
| 4 | P2 — `propose_target_page()` slug normalization unspecified | §Slug Normalization Rule below: lowercase → strip whitespace → `/` and `.` → `-` → collapse repeats → `.md` suffix. Includes table of the 7 existing engineering-wiki standards pages and their canonical slugs so reviewers can check determinism by hand. |
| 5 | P2 — `post_run_no_source_reads` unfalsifiable | Replaced with two concrete checks: (a) pre-commit grep that fails if any new file path in the diff contains `/mnt/ace/`; (b) execution wrapper `python -X importtime -c "..."` runs under audit that traps any open() against `/mnt/ace/**` and exits non-zero. Pseudocode in §TDD Test List. |
| 6 | P2 — provenance sample of 10/145 has no stratification rule | Stratified rule: sample = 3 rows per domain (9) + 1 multi-shard-summary row = 10; must include at least 1 `extend-only` and 1 `create` verdict; selection deterministic by sorting on `ledger_id` and taking `[0, len/3, 2*len/3]` per domain. |
| 7 | P3 — Lane B1 `docs/plans/README.md` serialization mechanism unnamed | §Serialization Protocol below: this lane writes plan + reports only; a final separate commit (main-session-only) appends the row to `docs/plans/README.md` AFTER both lanes' content commits land. Per `feedback_multi_agent_commit_serialization`. |
| 8 | P3 — `grep -v -E` regex `^(docs/reports/\|docs/plans/)` likely broken | Replaced with two chained `grep -v` invocations: `grep -v '^docs/reports/' \| grep -v '^docs/plans/'`. No alternation in ERE. |

Additional Claude r1 P3 items folded:
- cathodic-protection × OCIMF/CSA pre-count: §Pre-Approval Count Pinning will compute and log the per-domain × org cross-tab so the org-exclusion's effect on the cathodic-protection sub-slice is visible.
- materials-deferral hard decision: §Acceptance Criteria explicitly locks `materials` (122 entries) as deferred to a separate wave; not an open question in v2.
- ledger-id slug collision: §Slug Normalization Rule adds a collision-detection step — if two ledger rows normalize to the same target page, both rows are flagged in the extend-vs-create map with `collision_group_id` and the test `post_run_no_silent_collisions` fails the run.
- Acceptance phrasing on `knowledge/wikis/**` modifications: kept as post-commit grep AND a pre-commit guard — `git diff --cached --name-only | grep '^knowledge/wikis/' && exit 1`.

Gemini r1 false-positive pre-emption:
- `data/document-index/shards/ace-shard-0[0-9].json` — §Evidence below verifies all 10 ace-shard files exist via `ls` output.
- `knowledge/wikis/engineering/wiki/standards/*.md` (7 files) — §Evidence below verifies all 7 pages exist.
- For any future review claiming a referenced wiki page is missing, §Slug Normalization Rule documents the exact filename so reviewer disagreement is grounded in the same canonical mapping.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `data/document-index/standards-transfer-ledger.yaml` (7,727 lines, total=436 entries) — canonical L2 ledger with `domain`, `org`, `status`, `notes`, `summary`, `repo`, `modules`, `implemented_at` fields per standard.
- Found: `data/document-index/resource-intelligence-maturity.yaml` — authoritative maturity status (documents_in_scope=425; 639,585 index summaries; reclassification to 10 domains complete; `process`=55 and `drilling`=9 domains new).
- Found: `data/document-index/shards/shard-00.json` … `shard-09.json` + `data/document-index/shards/ace-shard-00.json` … `ace-shard-09.json` — 20 document-index shards with existing summaries (no source PDFs read required). Verified per §Evidence.
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
- `.claude/rules/calc-citation-contract.md` — extend-only verdicts that touch standards pages must, when emitted to `wiki/standards/<code-id>.md`, carry `code_id`/`publisher`/`revision` frontmatter. v2 wiki-ready stubs include these fields.

### Gaps identified
- No extend-vs-create mapping exists from ledger entries to `knowledge/wikis/engineering/wiki/standards/*.md` or `concepts/*.md`.
- No provenance fixture linking shard summary → ledger entry → proposed wiki stub.
- No reusable topic-clustering fixture (v2 will land it as `data/document-index/standards-topic-clusters.yaml` BEFORE running per-domain reports).
- `marine` domain overlap boundary not mechanically enforced — hand-verified per row pre-classification.

### Evidence (embedded verification, run 2026-04-23 unless noted)

**Issue statuses** (verified via `gh issue view`):
- `#2373` — OPEN — "feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion"
- `#2390` — OPEN — epic coordinator
- `#2216`, `#2227`, `#2284` — scope-excluded ACMA/OCIMF/CSA scope
- `#2365` — scope-excluded design-code-registry
- `#2471` — sanctioned `wiki/standards/` subtree decision (referenced by v2)
- `#2039` — engineering wiki ingest umbrella (downstream consumer)

**File existence** (`ls -la` + `find`, run 2026-04-23):
- EXISTS: `data/document-index/standards-transfer-ledger.yaml` (7,727 lines)
- EXISTS: `data/document-index/resource-intelligence-maturity.yaml` (59 lines)
- EXISTS: `data/document-index/shards/shard-0[0-9].json` (10 files)
- EXISTS: `data/document-index/shards/ace-shard-0[0-9].json` (10 files) — pre-empts Gemini r1 P1 false-positive
- EXISTS: `knowledge/wikis/engineering/wiki/standards/api-579-ffs.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-rp-c203.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-rp-c205.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-rp-f101.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-rp-f105.md`
- EXISTS: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` (excluded by org filter)
- EXISTS: `knowledge/wikis/engineering/wiki/concepts/` (33 concept pages)
- EXISTS: `docs/reports/llm-wiki-staged-batch-packs.md`
- EXISTS-CHECK PENDING (v2 plan-approval gate): `data/design-codes/code-registry.yaml` — if absent or zero entries, plan logs `DESIGN_CODE_EXCLUSION=noop` and proceeds; this MUST be re-verified during plan-approval before counts are pinned.
- MISSING (v2 will create): `data/document-index/standards-topic-clusters.yaml` — clustering fixture pre-landed in this plan
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
First-slice raw target = cathodic-protection + pipeline + structural = 19 + 55 + 71 = **145 candidate entries**, before applying org/registry/summary-evidence filters. Pinned post-filter count to be set during plan-approval (see §Pre-Approval Count Pinning).

**Gap proofs**:
- `ls docs/reports/batch-pack-4*` → "No such file or directory" → confirms no per-domain report exists yet.
- `ls knowledge/wikis/engineering/wiki/standards/api-579-ffs.md` → EXISTS → confirms extend-only candidate for API 579 structural entry.
- `ls knowledge/wikis/marine-engineering/wiki/standards/` → "No such file or directory" → marine-engineering wiki has no `standards/` family; any marine standard is mis-placed if promoted here.

<!-- 8 distinct sources consulted: issue body, standards-transfer-ledger.yaml, resource-intelligence-maturity.yaml, staged-batch-packs design, engineering wiki index/CLAUDE.md/standards-dir, epic #2390, priority-queue doc, sibling issues #2216/#2227/#2284/#2365/#2207, #2471 v3 decision, calc-citation-contract rule. -->

---

## Pre-Approval Count Pinning (NEW v2)

Before the user moves this plan to `status:plan-approved`, the main session will run the following dry-run computation and write the result into this plan as `EXPECTED_SLICE_COUNT`:

```
# Dry run — no commits
ledger = yaml.safe_load("data/document-index/standards-transfer-ledger.yaml")
DOMAINS_IN_SLICE = {"cathodic-protection", "pipeline", "structural"}
EXCLUDED_ORGS = {"OCIMF", "CSA"}
design_code_ids = load_design_code_registry_ids()  # logs DESIGN_CODE_EXCLUSION=noop if file absent/empty

slice_entries = [
    e for e in ledger["standards"]
    if e.get("domain") in DOMAINS_IN_SLICE
    and e.get("org") not in EXCLUDED_ORGS
    and e.get("id") not in design_code_ids
    and (e.get("notes") or e.get("summary"))
]
print("EXPECTED_SLICE_COUNT =", len(slice_entries))

# Per-domain × org cross-tab (resolves Claude r1 P3 cathodic-protection × OCIMF/CSA question)
from collections import Counter
print(Counter((e["domain"], e.get("org", "unknown")) for e in ledger["standards"] if e.get("domain") in DOMAINS_IN_SLICE))
```

Acceptance criterion below uses this pinned integer. If approval-time recount differs, plan re-enters review.

---

## Topic Clustering Rule (NEW v2 — addresses Claude r1 P1 #1)

A new fixture `data/document-index/standards-topic-clusters.yaml` will be pre-landed (separate commit, before per-domain reports run) with the following deterministic schema:

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
  pipeline:
    - cluster_id: pipe-design
      keywords: ["design", "wall thickness", "pressure"]
    - cluster_id: pipe-inspection
      keywords: ["inspection", "ili", "ndt"]
    - cluster_id: pipe-corrosion
      keywords: ["corrosion", "internal", "mic"]
    - cluster_id: pipe-materials
      keywords: ["material", "linepipe", "cra"]
  structural:
    - cluster_id: struct-fatigue
      keywords: ["fatigue", "sn", "viv"]
    - cluster_id: struct-strength
      keywords: ["strength", "buckling", "ultimate"]
    - cluster_id: struct-foundation
      keywords: ["foundation", "pile", "soil"]
```

Assignment rule: case-insensitive substring match against `entry.title + " " + entry.notes + " " + entry.summary`. First matching cluster wins (priority order = list order). Unmatched entries land in `cluster_id: <domain>-other`. Per-domain reports include the full keyword table inline so a reviewer can challenge a specific assignment.

---

## Slug Normalization Rule (NEW v2 — addresses Claude r1 P2 #4 + collision detection)

Pseudocode:
```
def to_slug(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[/. ]+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")

def propose_target_page(entry):
    # Standard-specific entry → wiki/standards/<slug>.md per #2471 v3
    if entry.get("type") == "standard" or entry.get("id"):
        slug = to_slug(entry["id"])
        return f"knowledge/wikis/engineering/wiki/standards/{slug}.md"
    # Topic/concept entry → wiki/concepts/<topic>.md
    return f"knowledge/wikis/engineering/wiki/concepts/{to_slug(entry['topic'])}.md"
```

Canonical-slug verification table for the 7 existing engineering-wiki standards pages:
| Ledger `id` example | Slug | Existing file |
|---|---|---|
| `API 579-1` | `api-579-1` | (no exact match — concept page maps via `propose_target_page` rule) |
| `API 579-1/ASME FFS-1` | `api-579-1-asme-ffs-1` | (no exact match — caller must reconcile to `api-579-ffs.md`) |
| `DNV-OS-E301` | `dnv-os-e301` | `api-579-ffs.md` siblings: `dnv-os-e301.md` EXISTS |
| `DNV-RP-C203` | `dnv-rp-c203` | EXISTS |
| `DNV-RP-C205` | `dnv-rp-c205` | EXISTS |
| `DNV-RP-F101` | `dnv-rp-f101` | EXISTS |
| `DNV-RP-F105` | `dnv-rp-f105` | EXISTS |
| `OCIMF MEG4` | `ocimf-meg4` | EXISTS (but excluded by org filter) |

Special case: where a ledger `id` does not normalize to an existing standards-page slug, the plan must record the proposed canonical slug and a `note: "create"` verdict. Where the canonical reviewer-judgment slug differs (e.g., `api-579-ffs.md` for an `API 579-1` ledger row), the extend-vs-create map records BOTH the normalized slug AND a `manual_alias` field linking to the existing canonical page; the normalization rule does not silently rewrite, the alias is explicit.

Collision detection: after computing all `target_page` values, group by path. If two ledger rows produce the same path, both rows get `collision_group_id` and the post-run test `post_run_no_silent_collisions` fails unless the map explicitly notes which row owns the page and why.

---

## Frontmatter Forward-Adoption (NEW v2 — #2471 + calc-citation-contract)

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

## Serialization Protocol (NEW v2 — addresses Claude r1 P3 #7)

Per `feedback_multi_agent_commit_serialization` and `feedback_merge_race_silent_revert`:

1. This lane's automated work commits the plan + per-domain reports + extend-vs-create map + provenance sample + topic-clusters fixture in one atomic commit on its own branch.
2. The lane DOES NOT touch `docs/plans/README.md`.
3. Main session (single-writer) appends the `#2373` row to `docs/plans/README.md` AFTER the lane commit lands, in a separate commit, after verifying any concurrently-merging Lane B1 plans (#2364, #2369) have completed.
4. If a `[rejected]` push is observed, defer to `feedback_autosync_silent_pusher` (wait + verify reflog) before retrying.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan (v2) | docs/plans/2026-04-23-issue-2373-batch-pack-4-non-acma-standards-summary-promotion.md |
| Topic-cluster fixture (NEW v2) | data/document-index/standards-topic-clusters.yaml |
| Per-domain report: cathodic-protection | docs/reports/batch-pack-4-non-acma-standards-cathodic-protection.md |
| Per-domain report: pipeline | docs/reports/batch-pack-4-non-acma-standards-pipeline.md |
| Per-domain report: structural | docs/reports/batch-pack-4-non-acma-standards-structural.md |
| Extend-vs-create map | docs/reports/batch-pack-4-extend-vs-create-map.yaml |
| Provenance fixture (sample rows) | docs/reports/batch-pack-4-provenance-sample.yaml |
| Wiki-ready stubs | appended within per-domain reports (no commits to `knowledge/wikis/**` in this wave) |
| Plan review v1 — Claude | scripts/review/results/20260424T032933Z-...-claude.md |
| Plan review v1 — Codex | scripts/review/results/20260424T032933Z-...-codex.md (timed out — #2479) |
| Plan review v1 — Gemini | scripts/review/results/20260424T032933Z-...-gemini.md (false-positives, see v2 §Evidence) |

---

## Deliverable

Three per-domain Batch Pack 4 execution reports (cathodic-protection, pipeline, structural) containing wiki-ready topic/standard stubs derived exclusively from the existing `standards-transfer-ledger.yaml` entries and the `data/document-index/shards/*.json` summary surface, plus an extend-vs-create YAML map against `knowledge/wikis/engineering/wiki/standards/` (with #2471 v3 frontmatter forward-adopted) and `concepts/`, plus a provenance fixture demonstrating the ledger→shard→stub chain — with zero raw PDF rereads, zero ACMA/OCIMF/CSA (marine) rows, zero `data/design-codes/code-registry.yaml` rows, and no modifications to `knowledge/wikis/**` in this wave. A new clustering fixture `data/document-index/standards-topic-clusters.yaml` will pre-land to make per-domain clustering deterministic.

**Note on scope boundary:** Wiki-READY stubs land as artifacts under `docs/reports/`; actual page creation under `knowledge/wikis/engineering/wiki/**` is out of scope for #2373 and belongs to downstream consumers (#2039 engineering wiki ingest umbrella).

---

## Pseudocode

```
# Step 0 (NEW v2) — Ensure topic-cluster fixture exists
assert os.path.exists("data/document-index/standards-topic-clusters.yaml")
clusters = yaml.safe_load(open("data/document-index/standards-topic-clusters.yaml"))

# Step 1 — Load ledger + maturity
ledger = yaml.safe_load(open("data/document-index/standards-transfer-ledger.yaml"))
maturity = yaml.safe_load(open("data/document-index/resource-intelligence-maturity.yaml"))

# Step 2 — First-slice filter
DOMAINS_IN_SLICE = {"cathodic-protection", "pipeline", "structural"}
EXCLUDED_ORGS = {"OCIMF", "CSA"}
design_code_ids = load_design_code_registry_ids()  # logs DESIGN_CODE_EXCLUSION=noop if absent/empty

def in_slice(entry):
    if entry.get("domain") not in DOMAINS_IN_SLICE: return False
    if entry.get("org") in EXCLUDED_ORGS: return False
    if entry.get("id") in design_code_ids: return False
    if not (entry.get("notes") or entry.get("summary")):
        return False
    return True

slice_entries = [e for e in ledger["standards"] if in_slice(e)]
assert len(slice_entries) == EXPECTED_SLICE_COUNT  # pinned in §Pre-Approval Count Pinning

# Step 3 — Deterministic clustering (Step 0 fixture lookup)
def assign_cluster(entry, domain_clusters):
    haystack = " ".join([entry.get("title",""), entry.get("notes",""), entry.get("summary","")]).lower()
    for c in domain_clusters:
        if any(kw in haystack for kw in c["keywords"]):
            return c["cluster_id"]
    return f"{entry['domain']}-other"

per_domain = groupby(slice_entries, key=lambda e: e["domain"])

# Step 4 — Cross-reference shards for existing summaries
for entry in slice_entries:
    shard_hits = find_shard_summary_rows(entry["id"], entry.get("title", ""))
    entry["shard_summary_refs"] = [r["path"] for r in shard_hits]
    entry["has_summary_evidence"] = bool(shard_hits) or bool(entry.get("summary"))

# Step 5 — Extend-vs-create + collision detection (slug normalization rule)
for entry in slice_entries:
    entry["target_page"] = propose_target_page(entry)
    entry["verdict"] = "extend-only" if os.path.exists(entry["target_page"]) else "create"

collisions = {p: rows for p, rows in groupby(slice_entries, key=lambda e: e["target_page"]) if len(list(rows)) > 1}
for p, rows in collisions.items():
    for r in rows:
        r["collision_group_id"] = hash(p)

# Step 6 — Emit per-domain reports (each with #2471 frontmatter for standards stubs)
for domain, entries in per_domain:
    write_report(f"docs/reports/batch-pack-4-non-acma-standards-{domain}.md",
                 entries=entries,
                 cluster_assignments={e["id"]: assign_cluster(e, clusters[domain]) for e in entries})

# Step 7 — Emit extend-vs-create map + stratified provenance sample
write_yaml("docs/reports/batch-pack-4-extend-vs-create-map.yaml",
           extend_only=[e for e in slice_entries if e["verdict"] == "extend-only"],
           create=[e for e in slice_entries if e["verdict"] == "create"],
           collisions=collisions)

# Stratified sample: 3 rows per domain (ordered by ledger_id), + 1 multi-shard-summary row
def stratified_sample(slice_entries):
    out = []
    for d in DOMAINS_IN_SLICE:
        d_rows = sorted([e for e in slice_entries if e["domain"] == d], key=lambda e: e["id"])
        idxs = [0, len(d_rows)//3, 2*len(d_rows)//3]
        out.extend(d_rows[i] for i in idxs)
    multi = next((e for e in slice_entries if len(e["shard_summary_refs"]) > 1), slice_entries[-1])
    if multi not in out: out.append(multi)
    assert any(e["verdict"] == "extend-only" for e in out)
    assert any(e["verdict"] == "create" for e in out)
    return out[:10]

write_yaml("docs/reports/batch-pack-4-provenance-sample.yaml", rows=stratified_sample(slice_entries))

# Step 8 — Post-run validation gates (below)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | data/document-index/standards-topic-clusters.yaml | NEW v2: deterministic clustering fixture (Claude r1 P1 #1) |
| Create | docs/reports/batch-pack-4-non-acma-standards-cathodic-protection.md | Sub-slice 4a deliverable |
| Create | docs/reports/batch-pack-4-non-acma-standards-pipeline.md | Sub-slice 4b deliverable |
| Create | docs/reports/batch-pack-4-non-acma-standards-structural.md | Sub-slice 4c deliverable |
| Create | docs/reports/batch-pack-4-extend-vs-create-map.yaml | Extend-vs-create + collision-group map |
| Create | docs/reports/batch-pack-4-provenance-sample.yaml | Stratified 10-row sample (3 per domain + 1 multi-shard) |
| Update (separate commit, main-session-only) | docs/plans/README.md | Plan row for #2373 — see §Serialization Protocol |

**Forbidden / out of scope** (per issue body and Batch Pack 4 design doc §3.4 Paths):
- `knowledge/wikis/**` — read-only; no wiki page commits in this wave
- `/mnt/ace/**` or any source-PDF path — no raw re-reading
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
| pre_run_domain_counts | Pre-filter domain tallies | `grep -c "domain: pipeline" ledger` | ≥55 |
| pre_run_shards_exist | All 20 shards present | `ls data/document-index/shards/*.json \| wc -l` | 20 |
| pre_run_design_code_state | Design-code registry checked | `test -f data/design-codes/code-registry.yaml` OR log `DESIGN_CODE_EXCLUSION=noop` | exit 0 |
| post_run_slice_count_exact | Post-filter row count matches pinned EXPECTED_SLICE_COUNT | `python3 count_slice.py` | equals `EXPECTED_SLICE_COUNT` (pinned during plan-approval) |
| post_run_yaml_parses | Extend-vs-create YAML parses | `python3 -c "import yaml; yaml.safe_load(open(...))"` | exit 0 |
| post_run_provenance_parses | Provenance sample YAML parses | same | exit 0 |
| post_run_no_marine | No marine/ACMA rows escaped | grep for `domain: marine` in reports | 0 matches |
| post_run_no_ocimf_csa | No OCIMF/CSA rows escaped | grep for `org: OCIMF` or `org: CSA` | 0 matches |
| post_run_no_design_code_overlap | No row in design-code registry | cross-compare against `data/design-codes/code-registry.yaml` (or noop) | empty intersection |
| post_run_all_extend_pages_exist | Every `extend-only` row references a real wiki page | `test -f` per page path | exit 0 per row |
| post_run_provenance_chain | Every sample row has `ledger_id` + `shard_summary_ref` + `proposed_stub_target` | YAML validation | 10/10 complete |
| post_run_provenance_stratification | Sample = 3 per domain + 1 multi + ≥1 extend-only + ≥1 create | YAML row inspection | passes |
| post_run_no_wiki_writes | No wiki pages modified | `git diff --cached --name-only \| grep '^knowledge/wikis/'` | empty (and pre-commit guard fails the commit if non-empty) |
| post_run_only_owned_paths | Changes stay in owned paths | `git diff --name-only \| grep -v '^docs/reports/' \| grep -v '^docs/plans/' \| grep -v '^data/document-index/' \| wc -l` | 0 |
| post_run_no_source_reads_diff | No `/mnt/ace/` paths in diff | `git diff --cached \| grep '/mnt/ace/'` | 0 matches (pre-commit guard) |
| post_run_no_source_reads_audit | No open() against `/mnt/ace/**` during execution | wrapper traps `open()` calls and exits non-zero on hit | exit 0 |
| post_run_frontmatter_standards | Wiki-ready stubs targeting `wiki/standards/` carry `code_id`, `publisher`, `revision` | YAML frontmatter inspection per stub | all three fields present |
| post_run_no_silent_collisions | No two ledger rows silently map to the same target page | extend-vs-create map collision-group inspection | every collision has explicit owner-row note |

---

## Acceptance Criteria

- [ ] Three per-domain reports exist: `batch-pack-4-non-acma-standards-{cathodic-protection,pipeline,structural}.md`
- [ ] Topic-cluster fixture `data/document-index/standards-topic-clusters.yaml` pre-lands BEFORE per-domain reports run
- [ ] Combined post-filter row count equals `EXPECTED_SLICE_COUNT` (pinned during plan-approval, NOT a range)
- [ ] `docs/reports/batch-pack-4-extend-vs-create-map.yaml` parses; every row labelled `extend-only` or `create`; collisions explicit
- [ ] `docs/reports/batch-pack-4-provenance-sample.yaml` contains 10 rows stratified per §Pseudocode Step 7 (3 per domain + 1 multi-shard, ≥1 extend-only, ≥1 create)
- [ ] Zero rows with `domain == "marine"`, `org in {OCIMF, CSA}`, or `id` also in `data/design-codes/code-registry.yaml`
- [ ] Zero files under `knowledge/wikis/**` modified by this plan's commits (pre-commit guard + post-commit grep)
- [ ] Zero reads of `/mnt/ace/**` (diff grep + audit wrapper)
- [ ] Every `extend-only` row references an existing file under `knowledge/wikis/engineering/wiki/{standards,concepts}/`
- [ ] Every wiki-ready stub targeting `wiki/standards/<slug>.md` carries `code_id`, `publisher`, `revision` frontmatter (revision may be `unknown`) per #2471 v3
- [ ] `materials` (122 entries), `process` (55), and `drilling` (9) domains are LOCKED as deferred — not open questions
- [ ] Review artifacts posted to `scripts/review/results/<timestamp>-...-plan-{claude,codex,gemini}.md`

---

## Adversarial Review Summary

| Provider | v1 Verdict | Disposition for v2 |
|---|---|---|
| Claude | MAJOR (8 real items) | All 8 items addressed surgically per §v2 Revision Log |
| Codex | UNAVAILABLE (timeout — #2479 stdin-hang) | Re-dispatch v2 once #2479 workaround in place |
| Gemini | MAJOR (2 false-positive items) | Pre-empted via §Evidence file-existence verification |

**Overall result:** v2 PENDING re-review

---

## Risks and Open Questions

- **Risk:** `marine` domain in the ledger is broader than ACMA/OCIMF/CSA. Mitigation: blanket-exclude `domain == "marine"`; carry forward to a later issue.
- **Risk:** Ledger `status == "done"` does NOT imply an existing wiki page. Mitigation: file-existence check for extend-vs-create classification.
- **Risk:** Topic-cluster keyword tables may misclassify edge cases. Mitigation: per-domain reports include the full keyword table inline; misclassifications become surgical follow-ups, not silent.
- **Risk:** Provenance fixture is 10 stratified rows. Mitigation: stratification rule pinned; full coverage deferred to #2207 / #2039 ingest.
- **Risk:** Parallel Lane B1 (#2364, #2369) may write `docs/plans/README.md` concurrently. Mitigation: §Serialization Protocol — main-session-only README append, after lane content commits.
- **Risk:** `data/design-codes/code-registry.yaml` may not exist. Mitigation: §Evidence + pre-run check — explicit `DESIGN_CODE_EXCLUSION=noop` log if absent, not silent no-op.
- **Open:** None for v2 (materials, process, drilling deferral locked; topic-clustering rule pre-landed; serialization explicit).

---

## Complexity: T2

**T2** — new reports across 6 files (5 docs + 1 data fixture), non-trivial filter (three exclusion conditions + summary-evidence gate), extend-vs-create detection against two wiki page families with collision detection, stratified provenance fixture, frontmatter forward-adoption, clear acceptance gates with pinned exact count. Not T1 (multiple files + new schema); not T3 (no multi-repo, no `src/` code, no new standards).
