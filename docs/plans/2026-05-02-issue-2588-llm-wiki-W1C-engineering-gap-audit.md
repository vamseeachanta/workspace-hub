# Plan for #2588: audit(llm-wiki) — engineering wiki gap audit + prioritized backfill sequence (W1-C)

> **Status:** plan-review (rev-2 — addresses Gemini r1 MAJOR)
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2588
> **Review artifacts:** scripts/review/results/2026-05-02-plan-2588-claude-internal.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/engineering/wiki/` — 102 files across 5 subdirs (concepts=42, entities=23, sources=23, standards=9, workflows=5) plus 4 root files (total 106).
- Found: `knowledge/wikis/engineering/raw/papers/` — single flat directory holding 520 files (no nested subdirs at depth 2+); a heterogeneous mix of feedback notes, project notes, agent/process docs, and a small slice of engineering content.
- Gap: no coverage-gap detector script will exist until #2392 ships (`scripts/knowledge/detect_wiki_gaps.py`); this audit is a one-time manual precursor that the future detector will subsume.
- Partial-wiring state: ONE engineering wiki path (`knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`) IS already wired into the citation contract via `digitalmodel/src/digitalmodel/citations/registry.py` (referenced from `digitalmodel/tests/citations/test_schema.py`); all other 105 wiki files are unreferenced from `digitalmodel/` Python code. The existing wired path serves as the prioritization anchor — entries falling within the same calc-adjacent surface (mooring/riser/fatigue standards consumed by `orcaflex/mooring_design.py` and siblings) are higher priority than orphan domains. (See citation contract `.claude/rules/calc-citation-contract.md`.)

### Standards
| Standard | Status | Source |
|---|---|---|
| n/a — audit-only plan; emits no calc constants | n/a | n/a |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/concepts/` (42 files) — 7 mooring/riser/fatigue concepts (`mooring-line-failure-physics`, `free-span-viv-fatigue`, `viv-riser-fatigue`, `fatigue-analysis-offshore`, `sn-curve-fatigue-definitions`, `pile-capacity-alpha-method`, `pipeline-integrity-assessment`); 5 hydrodynamics concepts; 6 process/agent concepts (`agent-delegation`, `compound-engineering`, `enforcement-over-instruction`, `multi-agent-parity`, `orchestrator-worker-separation`, `three-agent-cross-review`).
- `knowledge/wikis/engineering/wiki/standards/` (9 files including `TEMPLATE.md`) — DNV: `dnv-os-e301`, `dnv-rp-c203`, `dnv-rp-c205`, `dnv-rp-f101`, `dnv-rp-f105`; API: `api-579-ffs`; OCIMF: `ocimf-meg4`, `ocimf-tandem-mooring`. NO ABS, BV, ISO 19900-series, NORSOK, IACS, BSEE, or full DNV-OS catalog yet.
- `knowledge/wikis/engineering/wiki/entities/` (23 files) — solver/tool entities (`aqwa-solver`, `orcaflex-solver`, `orcawave-solver`, `bemrosetta-tool`, `openfoam-cfd`), failure-incident entities (`elba-island-mooring-incident`, `prelude-flng-mooring`, `nws-lng-mooring-investigation`, `hmpe-mooring-failures`), and process entities (`gsd-framework`, `hermes`, `claude-code`, `codex-cli`, `gemini-cli`).
- `knowledge/wikis/engineering/wiki/workflows/` (5 files) — `orcawave-orcaflex-fixture-expansion-cookbook`, `orcawave-to-orcaflex-pipeline`, `parametric-engineering-reports`, `qgis-flowline-dem-preprocessing`, `solver-debugging-protocol`.
- `knowledge/wikis/engineering/wiki/sources/` (23 files) — predominantly seed/extraction provenance (Doris University modules, Elements ingest dossiers, mooring-failures-seed). Per `.claude/rules/calc-citation-contract.md`, vendor-derivative sources pages are deny-list for citation; calcs must point at `standards/` or `concepts/`.

### Documents consulted
- `docs/plans/2026-04-26-issue-2378-marine-wiki-chunked-index.md` — sibling chunked-index plan for marine-engineering wiki (different domain; informs paginated-index pattern but not engineering-wiki content gaps).
- `docs/plans/2026-04-26-issue-2363-wiki-refs-reverse-lookup.md` — sibling reverse-lookup plan (informs ref tracing).
- `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md` — directly related; #2392 is the future automated coverage-gap detector this manual audit prefigures.
- Issue #2540 — Elements overnight wave epic; out of scope for engineering-wiki content (focused on `/mnt/ace/doris/*` and `/mnt/ace/acma-projects/31522-woodfibre-lng/*` corpora destined for `marine-engineering`/`maritime-law` wikis, not `engineering`). No write-path overlap with this audit.
- Issue #2368 — `feat(knowledge): generate faceted portal pages for large LLM-wiki domains`, OPEN; this audit's prioritized backfill list will feed #2368 portal-page selection downstream.
- Issue #2373 — `feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion`, OPEN; some priority entries from this audit (DNV-OS-F101, API RP 17-series, ISO 19900) may align with Batch Pack 4 scope.
- Issue #2392 — `feat(knowledge): wiki coverage-gap detector`, OPEN; produces `scripts/knowledge/detect_wiki_gaps.py` and per-domain `docs/reports/wiki-coverage-gaps/<domain>.yaml`. This audit is the manual precursor that proves the detector's eventual output shape.
- `.claude/rules/calc-citation-contract.md` — defines fail-closed citation contract; informs prioritization (subdirs that calcs would cite first = higher priority).
- ISO 19900-series offshore-structures standards taxonomy (ISO 19900 general / 19901 specific provisions / 19902 fixed steel / 19903 fixed concrete / 19904 floating / 19905-1 site-specific assessment of jack-ups) — used as the verifiable external taxonomy anchor for priority rationale. Each ISO part defines a discipline scope (structural integrity, environmental loading, materials, fatigue, etc.); priority entries cite a specific part number rather than a generic English noun.

### Gaps identified
- The directory structure of `knowledge/wikis/engineering/raw/` does NOT mirror `wiki/` (concepts/entities/sources/standards/workflows). Raw is a flat `papers/` dump of 520 files. A naive subdir-vs-subdir diff is impossible; the audit must classify each raw file by *destination wiki section* (or `out-of-scope` if the file is process/agent content that does not belong in the engineering wiki at all).
- Of 520 raw files, only 12 (~2.3%) are domain-engineering by filename heuristic; ~56 are `feedback_*` files that are user-memory shards (NOT engineering-wiki source material per `.claude/rules/calc-citation-contract.md` deny-list rationale); ~88 are ALL_CAPS dev/process docs; ~9 are JSON workflow specs (e.g., `sd15_txt2img.json` — image-generation, out of engineering scope); ~16 are YAMLs of mixed nature.
- The 4–5x raw-vs-wiki mismatch is therefore largely a **misclassification artifact** (raw includes content that belongs in `agents/.claude/memory`, `data/document-index/`, or other wikis), not a backfill deficit in the engineering domain.
- True engineering-content gaps DO exist within the actual wiki output — e.g., `standards/` has only 9 codes; the ISO 19900-series taxonomy and citation contract imply the standards count for a complete engineering practice surface is closer to 40–60.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2540` — CLOSED — `epic(llm-wiki): overnight Elements corpus planning wave after #2536` (closed after this plan was authored; gap-audit work proceeds independently of the parent epic's lifecycle)
- `#2368` — OPEN — `feat(knowledge): generate faceted portal pages for large LLM-wiki domains`
- `#2373` — OPEN — `feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion`
- `#2392` — OPEN — `feat(knowledge): wiki coverage-gap detector — inventory × wiki diff per discipline`
- `#2378` — OPEN — `feat(knowledge): chunk and paginate the canonical marine-engineering wiki index`

**File counts** (verified 2026-05-02 via `find ... | wc -l`):
- `knowledge/wikis/engineering/raw/`: 521 files (520 in `papers/` + 1 root)
- `knowledge/wikis/engineering/wiki/`: 106 files total
  - `wiki/concepts/`: 42 files
  - `wiki/entities/`: 23 files
  - `wiki/sources/`: 23 files
  - `wiki/standards/`: 9 files (incl. `TEMPLATE.md`)
  - `wiki/workflows/`: 5 files
  - `wiki/` root: 4 files

**Raw subdir tree** (verified 2026-05-02 via `find -maxdepth 4 -type d`):
```
knowledge/wikis/engineering/raw
knowledge/wikis/engineering/raw/papers
```
(only one subdir — no further nesting)

**Raw filename-prefix bucketing** (verified 2026-05-02; explicit commands shown for re-verification):
- `feedback_*.md`: 56 files (process/memory — out of engineering wiki scope) — `ls papers/ | grep -c '^feedback_'`
- ALL_CAPS_FILES: 88 (dev/process docs — mostly out of scope) — `ls papers/ | grep -cE '^[A-Z_]+\.(md|yml|yaml|json)$'`
- `claude/codex/gemini/agent/ai-/llm-/skill-/hermes/gsd-` prefix: 34 (agent/process — out of scope) — `ls papers/ | grep -ciE '^(claude|codex|gemini|agent|ai-|llm-|skill-|hermes|gsd-)'` (case-insensitive `-i` required)
- `plan-/review-/audit-/sweep-/stage-/prompt-/approval-/adversarial-/artifact-` prefix: 25 (process — out of scope) — `ls papers/ | grep -cE '^(plan-|review-|audit-|sweep-|stage-|prompt-|approval-|adversarial-|artifact-)'`
- `2026-*` dated rollups: 9 (overnight synthesis — out of scope) — `ls papers/ | grep -c '^2026-'`
- `*.json` (e.g., ComfyUI/SDXL workflow files): 9 (out of engineering scope) — `ls papers/ | grep -c '\.json$'`
- `*.yaml/*.yml`: 16 (mixed — must classify case-by-case) — `ls papers/ | grep -cE '\.(yaml|yml)$'`
- **Out-of-scope union (deduplicated, mutually exclusive):** computed via single union regex `ls papers/ | grep -ciE '^(feedback_|[A-Z_]+\.(md|yml|yaml|json)$|claude|codex|gemini|agent|ai-|llm-|skill-|hermes|gsd-|plan-|review-|audit-|sweep-|stage-|prompt-|approval-|adversarial-|artifact-|2026-)|\.json$' | sort -u` — execution time recompute the deduplicated total to replace the naive sum (raw additive sum 237/520 ≈ 46% double-counts files matching multiple buckets, e.g., `CLAUDE.md` matches both ALLCAPS and the agent-prefix bucket). The audit deliverable MUST report the deduplicated union count, not the additive sum. **Note (rev-2):** the trailing `\.json$` is uniformly out-of-scope (ComfyUI/SDXL workflow JSON), but `\.(yaml|yml)$` was REMOVED from this union per Gemini r1 MAJOR-2 — yaml/yml files are mixed (16 total, see bucket above) and must be classified case-by-case in a separate "needs-manual-classification" bucket; blanket-filtering them contradicts the Evidence intent.
- Domain-engineering candidates by name match against `mooring|riser|pipeline|structural|fatigue|subsea|umbilical|cathodic|cfd|hydrodynamic|wave-theory|free-span|viv|seakeeping|fea|orcaflex|orcawave|aqwa|api-|dnv-|ocimf|csa-|naval|offshore`: 12 files.

**Internal cross-reference scan** (verified 2026-05-02 via `grep -rl "knowledge/wikis/engineering" /mnt/local-analysis/workspace-hub/digitalmodel/`):
```
digitalmodel/src/digitalmodel/citations/registry.py
digitalmodel/tests/citations/test_schema.py
```
ONE wiki path is wired: `registry.py` declares `"wiki_path": "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md"` for the DNV-OS-E301 citation template; the schema test asserts on it. All other 105 wiki files are unreferenced from `digitalmodel/` Python code. Implication: prioritization is anchored on the existing wired path — entries falling within the same calc-adjacent surface (mooring/riser/fatigue standards consumed by `orcaflex/mooring_design.py` and siblings) are higher priority than orphan domains. Where citations don't yet exist, fall back to citation-contract intent (which standards calcs *would* cite).

**Existing wiki/standards inventory** (verified 2026-05-02 via `ls`):
```
api-579-ffs.md  dnv-os-e301.md  dnv-rp-c203.md  dnv-rp-c205.md
dnv-rp-f101.md  dnv-rp-f105.md  ocimf-meg4.md   ocimf-tandem-mooring.md  TEMPLATE.md
```

**File existence** (verified 2026-05-02 via `ls -la`):
- EXISTS: `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md`
- EXISTS: `docs/plans/_template-issue-plan.md`
- EXISTS: `docs/plans/README.md`
- MISSING (this plan creates the directory): `docs/audits/` — `ls docs/audits` returned `No such file or directory`; this plan establishes the directory with the audit file as its seed entry.
- MISSING (this plan creates): `docs/audits/2026-05-02-engineering-wiki-gap-audit.md`
- MISSING (this plan creates): `tests/knowledge/test_engineering_wiki_gap_audit_artifact.py`

**Gap proofs** (verified 2026-05-02):
- `find knowledge/wikis/engineering/raw -maxdepth 4 -type d` returned only `raw` and `raw/papers` → confirms no nested subdir taxonomy on raw side.
- `grep -rl "knowledge/wikis/engineering" /mnt/local-analysis/workspace-hub/digitalmodel/ 2>/dev/null` returned `digitalmodel/src/digitalmodel/citations/registry.py` and `digitalmodel/tests/citations/test_schema.py` → confirms ONE wiki path (`dnv-os-e301.md`) is wired into the citation contract; remaining 105 wiki files are unreferenced.

<!-- Source count: (1) issue body / wave prompt, (2) prior plan #2392 wiki-gap-detector, (3) prior plan #2378 marine-wiki-chunked-index, (4) prior plan #2363 wiki-refs-reverse-lookup, (5) `.claude/rules/calc-citation-contract.md`, (6) ISO 19900-series offshore-structures TOC. Total = 6 distinct sources (≥3 required). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2588-llm-wiki-W1C-engineering-gap-audit.md` |
| Audit report (deliverable) | `docs/audits/2026-05-02-engineering-wiki-gap-audit.md` |
| Tests | `tests/knowledge/test_engineering_wiki_gap_audit_artifact.py` |
| Plan review — Claude (internal) | `scripts/review/results/2026-05-02-plan-2588-claude-internal.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-2588-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-2588-gemini.md` |
| Index update | `docs/plans/README.md` |

---

## Deliverable

A single audit report at `docs/audits/2026-05-02-engineering-wiki-gap-audit.md` containing (a) a complete gap-table with one row per top-level subdir on each side and per filename-prefix bucket on the raw side, (b) a prioritized 8–10-entry backfill sequence with one-line rationale per entry, and (c) a deprecation pass naming raw-side filename prefixes that are categorically out-of-scope for the engineering wiki — plus a passing test that asserts the audit file exists with required schema. NO wiki content will be created or edited in this plan.

---

## Pseudocode

```
audit_report_structure:
    1. Header (date, scope, methodology one-paragraph)
    2. Inventory tables:
       table_A_raw_inventory:
         columns = [prefix_bucket, file_count, classification, destination]
         rows = one per filename-prefix bucket above + "domain-engineering candidates"
       table_B_wiki_inventory:
         columns = [subdir, file_count, first_5_files_alphabetical_at_audit_time, taxonomy_completeness_estimate]
         rows = concepts | entities | sources | standards | workflows | root
    3. Gap audit table:
       columns = [logical_subdir, raw_count, wiki_count, ratio, priority, rationale_one_line]
       rows >= 8, covering every wiki/* subdir + key missing-domain rows
    4. Prioritized backfill sequence:
       8-10 entries, each formatted as:
         - title (suggested child issue title)
         - target_path (one wiki page, e.g., wiki/standards/dnv-os-f101.md)
         - priority (P1|P2|P3)
         - rationale (1 line; MUST reference one of: ISO 19900-series part number, the literal string `citation-contract` / `citation contract` / `would cite`, or a ratio expression like `raw/wiki` or `\d+:\d+`)
         - candidate_source(s) on raw side (or "external — DNV/API/ISO doc")
    5. Deprecation pass:
       list of raw filename-prefix patterns recommended for archival to
       agents/memory/ or out-of-engineering-wiki destinations (with target paths).
    6. Open questions section reflecting the Risks & Open Questions in this plan.

test_audit_artifact:
    assert path exists
    parse markdown
    assert table_A row count >= 7 (one per identified prefix bucket)
    assert table_B row count == 6 (5 subdirs + root)
    assert gap-audit table row count >= 8
    assert prioritized backfill list length in [8,10]
    assert each priority entry has fields {title, target_path, priority, rationale, candidate_sources}
    assert each priority entry's rationale matches one of the required anchors:
        - ISO 19900-series part number (regex: `19900|19901|19902|19903|19904|19905-1`)
        - literal `citation-contract` / `citation contract` / `would cite`
        - ratio expression matching `raw/wiki` or `\d+\s*:\s*\d+`
    assert internal self-consistency only (rev-2; replaces live-find compare per Gemini r1 MAJOR-1):
        - sum of per-subdir counts in table_B equals reported total wiki file count
        - sum of per-prefix-bucket counts in table_A is consistent with reported raw total
          (allowing for documented bucket overlap noted in Evidence)
        - NO live `find` invocation; the audit is a point-in-time snapshot and cannot
          assert against future repo state without breaking CI when child issues add files
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create (dir) | `docs/audits/` | new top-level audit-artifact directory (does not currently exist; established by this plan as seed for future audits like #2392 detector outputs) |
| Create | `docs/audits/2026-05-02-engineering-wiki-gap-audit.md` | the audit report deliverable |
| Create | `tests/knowledge/test_engineering_wiki_gap_audit_artifact.py` | TDD test asserting audit file exists, has required columns, ≥8 priority entries, verifiable file-count evidence |
| Update | `docs/plans/README.md` | add this plan to the index |

NO modifications to `knowledge/wikis/engineering/**` of any kind. This plan is audit-only.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_audit_file_exists` | the deliverable file is present | path = `docs/audits/2026-05-02-engineering-wiki-gap-audit.md` | `Path(...).exists() is True` |
| `test_audit_has_inventory_table_A` | raw-inventory table has the canonical columns | parsed markdown | columns include {`prefix_bucket`, `file_count`, `classification`, `destination`} |
| `test_audit_has_inventory_table_B` | wiki-inventory table is complete | parsed markdown | exactly 6 rows (concepts, entities, sources, standards, workflows, root) |
| `test_audit_gap_table_min_rows` | gap-audit table has actionable depth | parsed markdown | row count ≥ 8 |
| `test_audit_priority_list_size` | prioritized backfill has 8–10 entries | parsed markdown | `8 <= len(priority_entries) <= 10` |
| `test_audit_priority_entry_schema` | each entry has required fields | parsed markdown | each entry has `title`, `target_path`, `priority` ∈ {P1,P2,P3}, `rationale`, `candidate_sources` |
| `test_audit_rationales_cite_required_anchors` | each priority rationale references a verifiable anchor | parsed markdown rationale strings | each rationale matches at least one of: ISO 19900-series regex (`19900|19901|19902|19903|19904|19905-1`), literal `citation-contract` / `citation contract` / `would cite`, or ratio regex (`raw/wiki` or `\d+\s*:\s*\d+`) |
| `test_audit_counts_internally_consistent` | cited counts in audit tables sum correctly across rows (no live `find`) | parsed markdown tables | sum of per-subdir counts in table_B equals reported total wiki file count; analogous self-consistency for table_A bucket counts vs. reported raw total. **Rev-2 change:** the prior `test_audit_file_counts_verifiable` (which compared static counts to live `find` with ±2 tolerance) was REPLACED per Gemini r1 MAJOR-1 — point-in-time audits cannot assert against future repo state, since adding 3+ wiki files in any child issue would permanently fail CI |
| `test_audit_no_wiki_writes` | this plan does not modify wiki/ | `git diff --name-only $(git merge-base HEAD origin/main) -- knowledge/wikis/engineering/wiki/` | empty |

---

## Acceptance Criteria

- [ ] All audit-artifact tests pass: `uv run pytest tests/knowledge/test_engineering_wiki_gap_audit_artifact.py -v`
- [ ] No regression: `uv run pytest tests/knowledge/` passes
- [ ] Audit table covers every top-level subdir of `wiki/` (concepts, entities, sources, standards, workflows, root) AND every prefix bucket of `raw/papers/` identified in this plan's evidence section.
- [ ] Prioritized backfill list contains 8–10 entries, each mapping to a single follow-up issue path (e.g., `docs/plans/<future-date>-issue-<NNNN>-<slug>.md` placeholder).
- [ ] Each priority entry's rationale references one of: (a) ISO 19900-series part number (19900 / 19901 / 19902 / 19903 / 19904 / 19905-1), (b) citation-contract intent (literal `citation-contract` / `citation contract` / `would cite`), (c) raw-vs-wiki ratio expression (`raw/wiki` or `\d+:\d+`). Enforced by `test_audit_rationales_cite_required_anchors`.
- [ ] Deprecation pass section names ≥3 raw filename-prefix patterns recommended for relocation out of engineering wiki scope.
- [ ] No file under `knowledge/wikis/engineering/wiki/` is created or modified by this plan's execution commit.
- [ ] Review artifacts posted to `scripts/review/results/`.
- [ ] Plan-level outcome (audit report) will be the single input for a future child-issue wave; no child issues will be opened by this plan.

---

## Adversarial Review Summary

| Provider | Round | Verdict | Key findings |
|---|---|---|---|
| Claude (internal) | r0 (pre-r1) | MAJOR → revised | 3 MAJOR (false zero-citations claim; rationale-anchor test missing; SUT taxonomy unattributed) + 7 MINOR — all addressed inline |
| Codex | r0 (pre-r1) | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479); fanout dispatch hung; killed at 2026-05-02T12:21Z |
| Gemini | r0 (pre-r1) | UNAVAILABLE | gemini CLI cwd=/tmp sandbox cannot resolve repo paths; err logged to scripts/review/results/.failed-fanout-2026-05-02/ |
| Gemini | r1 | MAJOR → revised | 4 findings: (1) TDD test_audit_file_counts_verifiable will permanently fail CI once child issues add 3+ files; (2) out-of-scope union regex blanket-filters yaml/yml contradicting "case-by-case" intent; (3) Evidence section claims #2540 OPEN but it is CLOSED; (4) review-artifact path naming mismatch (`...-claude.md` vs actual `...-claude-internal.md`) — finding 4 is a naming false-positive (the file exists under the internal-suffix name); findings 1–3 are real and addressed in rev-2 |

**Overall result (rev-2):** PASS-after-revision — r0 fixes carried forward; rev-2 addresses Gemini r1 (3 real MAJOR + 1 naming-FP). Pending user re-review for promotion to `status:plan-approved`.

**Revisions made based on r0 review (Claude internal):**
- MAJOR-1: corrected the false "zero digitalmodel cross-refs" claim; embedded actual grep results showing `registry.py` + `test_schema.py` wire `dnv-os-e301.md`; reframed as prioritization anchor.
- MAJOR-2: added `test_audit_rationales_cite_required_anchors` test asserting each rationale matches ISO 19900 / citation-contract literal / ratio regex.
- MAJOR-3: replaced unverifiable SUT taxonomy with ISO 19900-series (19900/19901/19902/19903/19904/19905-1) as the verifiable external anchor.
- MINOR-1 through MINOR-7: see Revision History below for the full r0 fix list.

**Revisions made based on r1 review (Gemini MAJOR):** see `## Revision History` section below.

**Provenance:** r0 = single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. r1 = Gemini cross-review at `scripts/review/results/2026-05-02-plan-2588-gemini.md`. r2 = pending user re-review.

---

## Revision History

| Revision | Date | Trigger | Changes |
|---|---|---|---|
| rev-0 | 2026-05-02 | initial draft | original plan emitted |
| rev-1 | 2026-05-02 | Claude internal r0 review (3 MAJOR + 7 MINOR) | corrected false zero-citations claim; added rationale-anchor test; replaced SUT taxonomy with ISO 19900-series; 7 MINOR fixes (literal `grep -ciE`, "12 files" correction, 105/106 reconciliation, ±2 absolute tolerance, `merge-base` substitution, "first_5_alphabetical" rename, deduplicated union documentation) |
| rev-2 | 2026-05-02 | Gemini r1 review (MAJOR — 3 real findings + 1 naming-FP) | (a) replaced `test_audit_file_counts_verifiable` (live `find` ±2 compare) with `test_audit_counts_internally_consistent` — the prior test would permanently fail CI once child issues add 3+ files [Gemini r1 MAJOR-1]; (b) removed `\.(yaml|yml)$` from out-of-scope union regex — yaml/yml is mixed and must be classified case-by-case per Evidence intent; kept `\.json$` which IS uniformly out-of-scope [Gemini r1 MAJOR-2]; (c) updated #2540 status from OPEN to CLOSED in Evidence with one-line acknowledgment that this plan was authored before parent epic closed and the audit work proceeds independently [Gemini r1 MAJOR-3]; (d) corrected review-artifact header + Artifact Map cell from `2026-05-02-plan-2588-claude.md` to actual filename `2026-05-02-plan-2588-claude-internal.md` [Gemini r1 finding 4 — naming false-positive; the file exists under the internal-suffix name]; (e) updated Risks section drift mitigation to reflect the test-design change |

---

## Risks and Open Questions

- **Risk:** Subdir naming conventions differ between raw (single flat `papers/` directory) and wiki (5 typed subdirs). A naive subdir-name diff will produce false-mismatch noise; this plan addresses by classifying raw files by *destination* (concepts/entities/standards/workflows/sources/out-of-scope) using filename-prefix buckets, not by mirror-subdir matching.
- **Risk:** Priority bias toward visible work. The auditor may over-weight standards (visible, easy to enumerate) and under-weight concepts (harder to scope but core to citation contract). Mitigation: priority rationale must cite ISO 19900-series part number, citation-contract literal, or a verifiable raw-vs-wiki ratio — not just raw count. Enforced by `test_audit_rationales_cite_required_anchors`.
- **Risk:** Count-based heuristic ignores depth-of-content. A single 4-page mooring-failure-physics page can outweigh ten thin standards stubs. Mitigation: priority list is *recommendation*; final scope-per-child-issue happens in each child plan, not here.
- **Risk:** Filename-prefix bucketing is heuristic and will misclassify some files. The audit must explicitly disclose its bucketing rules and acknowledge that final classification happens at child-issue time.
- **Risk:** Drift — `raw/papers/` and `wiki/*/` file counts will change between this plan's draft and execution date. **Rev-2 mitigation (per Gemini r1 MAJOR-1):** the TDD test no longer compares static counts to live `find` (that approach would permanently break CI as soon as child issues add 3+ wiki files); instead it asserts internal self-consistency of the audit's own tables. If repo drift exceeds the audit's stated assumptions before child-issue dispatch, the operator re-runs the audit manually and re-commits the report — drift detection is procedural, not test-enforced.
- **Open:** Should the audit include an explicit deprecation pass (which raw subdirs/prefixes should be archived to `agents/memory/` or moved to `data/document-index/` rather than promoted to wiki)? **Proposed default: YES** — the 46% out-of-scope ratio is too high to ignore; deprecation recommendations are a section of the deliverable.
- **Open:** Should priority list include cross-domain concepts (e.g., `marine-engineering` overlap pages like wave theory) or stay strictly engineering-discipline-only? Flag for user during approval.
- **Open:** Should this audit's output be re-run automatically once #2392's `detect_wiki_gaps.py` ships, to validate the script's output against this manual baseline? **Proposed: YES** — adds a regression check for the future detector. Out of scope for this plan, captured as a follow-up.

---

## Complexity: T2

**T2** — single new audit deliverable file plus a single TDD test file plus a docs-index update; no production-code modifications, no wiki edits. Classification heuristic + manual prioritization is the substantive work.
