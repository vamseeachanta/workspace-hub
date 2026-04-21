# Plan for #2392: Wiki coverage-gap detector — v4 (post-#2405 re-file draft)

> Status: draft
> Complexity: T2
> Date: 2026-04-21
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2392
> Purpose: replace the preserved closed-issue plan with a re-file-ready draft that reflects current repo state and the #2405 attestation contract.

---

## Revision History

- v1-v3 (2026-04-20): preserved historical iterations that ended in MAJOR review and were closed pending #2405 review-infrastructure fixes.
- v4 (this draft): addresses the six defects from `scripts/review/results/2026-04-20-validation-2405-via-plan-2392-codex.md` by:
  - removing closed-issue `plan-review` posture from the header
  - replacing missing/stale review-history claims with current repository reality
  - defining exact source inputs and optional-input behavior
  - defining the md5/sha256 join contract without false-gap behavior
  - replacing the data-dependent "one YAML per domain" acceptance criterion
  - replacing the undefined `L3-eligibility heuristic` with a concrete allowlist

---

## Resource Intelligence Summary

### Existing code and adjacent contracts
- `scripts/knowledge/llm_wiki.py` — existing L3 wiki tooling surface.
- `scripts/data/document-index/provenance.py` — provenance merge/write semantics.
- `scripts/data/document-index/phase-a-index.py` — legacy `md5:` handling for older inventory records.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
  - §3 canonical identity / legacy `md5:` read-only rule
  - §7 cross-machine tier model
  - §8.1 parent-mandated L3 frontmatter baseline (`title`, `last_updated`, `doc_key`)

### Current-state evidence (2026-04-21 live verification)
- `data/design-codes/code-registry.yaml` exists.
- `.planning/quick/review-2408-*` artifacts still exist and are unrelated to this issue.

### Authoritative source inputs for this detector
The detector reads only git-tracked metadata and wiki pages. It does not dereference `/mnt/ace/**` directly.

Required inputs:
- `data/document-index/index.jsonl` — per-record indexed source inventory for `/mnt/ace/**` coverage questions
- `data/design-codes/code-registry.yaml` — structured standards/code inventory
- `knowledge/wikis/*/wiki/**/*.md` — candidate coverage-bearing wiki pages

Optional inputs (must degrade gracefully if absent):
- `data/document-index/registry.yaml` — aggregate counts only; summary/reporting aid, not join corpus
- `data/document-index/mounted-source-registry.yaml`
- `data/document-index/online-resource-registry.yaml`
- `data/document-index/dde-standards-inventory.yaml`
- `data/document-index/standards-transfer-ledger.yaml`
- `data/document-index/promotions/*.yaml`
- `data/document-index/intelligence-accessibility-registry.yaml`

Input roles:
- join corpus: `index.jsonl`, joinable per-record ledgers/manifests, design-code entries with canonical doc identity
- reporting-only: `registry.yaml`, accessibility hints, and skipped-input diagnostics

Optional means:
- missing file != crash
- detector records the skipped input in `_summary.md`
- tests explicitly cover absent optional inputs

### Scope boundary
This issue is analysis-only. It emits candidate gap reports and identity/status diagnostics. It does not generate wiki pages and does not mutate registry truth.

---

## Problem Statement

We need a repeatable way to answer:
- which indexed or registry-backed sources have no corresponding L3 wiki coverage yet
- which records cannot be matched safely because identity is legacy/ambiguous
- which disciplines have the highest uncovered source volume

The detector compares source-side inventory with wiki-side coverage by canonical `doc_key`, then emits per-domain gap YAML plus a durable summary markdown.

---

## Identity Join Contract

### Canonical rule
- `sha256:<64hex>` is the only positive match key.
- `md5:<hex>` is accepted for reads but is never treated as a positive match against a `sha256:` wiki key.
- bare hex is a conformance violation; readers normalize it to `sha256:<hex>` for compatibility and emit a warning.

### Mixed-state behavior
For each source-side record:
1. if a canonical `sha256:` key is present, use it as the join key
2. else if a bare 64-hex value is present, normalize to `sha256:<hex>` and emit a warning
3. else if only `md5:` is present, emit entry/status `identity-unresolved`
4. else if no conforming key is present, emit entry/status `identity-unresolved`
5. do not classify unresolved identity as a true wiki-coverage gap

This avoids false positives during migration while still surfacing actionable backlog.

### Source record statuses
Each normalized source record must be exactly one of:
- `gap` — canonical source key present, no wiki page with the same canonical `doc_key`
- `covered` — canonical source key present and wiki page exists (summary counts only; not emitted into gap YAML)
- `identity-unresolved` — source exists but lacks canonical joinable identity

### Wiki diagnostics
Wiki-frontmatter problems are tracked separately from source-record status:
- `wiki-schema-warning` — a coverage-bearing wiki page is missing `title`, `last_updated`, or a conforming `doc_key`

`wiki-schema-warning` entries appear only in `_summary.md` diagnostics and test assertions; they are not gap records.

---

## L3 Coverage Boundary (replaces undefined heuristic)

The previous plan's `docs/reports/*.md` heuristic was too loose. v4 replaces it with a concrete allowlist.

The detector may treat only these artifacts as source-side candidates for wiki coverage:
1. per-record index inventory from `data/document-index/index.jsonl`
2. joinable L2 ledgers/manifests with per-record document identity:
   - `data/document-index/standards-transfer-ledger.yaml`
   - `data/document-index/dde-standards-inventory.yaml`
   - `data/document-index/promotions/*.yaml`
3. structured design-code entries from `data/design-codes/code-registry.yaml` when they carry or can map to canonical source identity
4. wiki pages under `knowledge/wikis/*/wiki/**/*.md` for coverage comparison, but only for coverage-bearing page classes:
   - include pages with a conforming `doc_key` in frontmatter
   - exclude structural/navigation files by path or basename: `**/wiki/index.md`, `**/wiki/log.md`, and any markdown file whose frontmatter declares `page_count`/`source_count` navigation metadata instead of a `doc_key`
5. optional wiki-domain hints from `data/document-index/intelligence-accessibility-registry.yaml`
6. aggregate `data/document-index/registry.yaml` for reporting-only context; never normalize it into candidate source records

The detector must NOT scan arbitrary `docs/reports/*.md` as source inventory.
That content is L5 run output unless a separate promotion manifest has already elevated it into a durable source candidate.

Implication: `_summary.md` can never self-ingest, and report markdown cannot create feedback loops.

---

## Deliverable

A CLI at `scripts/knowledge/detect_wiki_gaps.py` that:
- loads required and optional inputs
- normalizes source candidates into a common record shape
- parses wiki frontmatter and builds a canonical-coverage index by `sha256:` `doc_key`
- emits per-domain YAML only for domains with true canonical gaps
- emits `_summary.md` with counts for gaps, covered records, unresolved identity, skipped optional inputs, and wiki-schema warnings
- supports `--dry-run` to print the same summary without writing files

---

## Candidate Record Shape

Normalized source record fields:
- `source_type` (`index-record`, `ledger`, `promotion-manifest`, `design-code`)
- `domain`
- `title`
- `source_path`
- `doc_key`
- `availability_tier` (per operating-model §7)
- `discipline`
- `suggested_slug`
- `status`
- `notes`

Mapping expectations:
- `index-record`: read canonical identity/path from `index.jsonl`; derive `domain`/`discipline` from indexed metadata when present, otherwise from config mapping by source root/path prefix.
- `design-code`: derive `domain`/`discipline` from registry fields and configured default wiki-domain mapping.
- `ledger` / `promotion-manifest`: preserve source-provided domain when available; otherwise fall back to config mapping.

Gap YAML entry fields:
- `doc_key`
- `source_path`
- `domain`
- `discipline`
- `availability_tier`
- `suggested_page`
- `status`
- `notes`

---

## Pseudocode

```text
function run(config_path, dry_run=False):
    config = load_detector_config(config_path)  # domain mapping, structural excludes, output dir
    required_inputs = [
        "data/document-index/index.jsonl",
        "data/design-codes/code-registry.yaml",
    ]
    optional_inputs = [
        "data/document-index/registry.yaml",
        "data/document-index/mounted-source-registry.yaml",
        "data/document-index/online-resource-registry.yaml",
        "data/document-index/dde-standards-inventory.yaml",
        "data/document-index/standards-transfer-ledger.yaml",
        "data/document-index/intelligence-accessibility-registry.yaml",
        "data/document-index/promotions/*.yaml",
    ]

    required_data = load_required_inputs(required_inputs)
    optional_data, skipped_inputs = load_optional_inputs(optional_inputs)

    source_records = normalize_source_records(required_data, optional_data, config)

    wiki_index = {}
    wiki_schema_warnings = []
    for page in glob("knowledge/wikis/*/wiki/**/*.md"):
        if is_structural_wiki_page(page, config):
            continue
        fm = parse_frontmatter_safe(page)
        warning = validate_l3_frontmatter_baseline(fm)  # title, last_updated, doc_key
        if warning:
            wiki_schema_warnings.append({"page": page, "warning": warning})
        key = normalize_wiki_doc_key_for_coverage(fm.get("doc_key"))  # sha256 only; bare hex stays warning-only
        if key:
            wiki_index[key] = page

    gaps_by_domain = {}
    summary = counts(skipped_inputs, wiki_schema_warnings)
    for record in source_records:
        canonical_key = extract_canonical_join_key(record)
        if canonical_key is None:
            add_unresolved(summary, record)
            continue
        if canonical_key in wiki_index:
            add_covered(summary, record, wiki_index[canonical_key])
            continue
        add_gap(gaps_by_domain, summary, record, canonical_key)

    if dry_run:
        print(render_summary(summary, gaps_by_domain))
        return

    reconcile_output_directory(
        config.output_dir,
        keep_domains=gaps_by_domain.keys(),
        preserve_files=["README.md", "_summary.md"],
    )
    write_gap_yaml_only_for_domains_with_entries(gaps_by_domain)
    write_summary_md(summary, gaps_by_domain, skipped_inputs, wiki_schema_warnings)
```

---

## Scheduled Task Contract

Planned detector config at `config/ai-tools/wiki-gap-detection.yaml`:
- `output_dir`: `docs/reports/wiki-coverage-gaps`
- `structural_excludes`: basename/path patterns for `index.md`, `log.md`, and navigation-only wiki files
- `source_root_domain_map`: path-prefix/domain mapping for `index.jsonl` records that lack explicit domain metadata
- `design_code_domain_defaults`: default wiki-domain mapping for code-registry entries

Planned weekly scheduler entry in `config/scheduled-tasks/schedule-tasks.yaml`:
- `id`: `wiki-coverage-gap-detection`
- `label`: `Wiki coverage-gap detector`
- `schedule`: `15 4 * * 1`
- `machines`: `[dev-primary, ace-linux-1]`
- `requires`: `[python3, uv, git]`
- `prefer`: `dev-primary`
- `command`:
  `mkdir -p $WORKSPACE_HUB/logs/knowledge && cd $WORKSPACE_HUB && uv run python scripts/knowledge/detect_wiki_gaps.py --config config/ai-tools/wiki-gap-detection.yaml >> $WORKSPACE_HUB/logs/knowledge/wiki-coverage-gap-$(date +\%Y-\%m-\%d).log 2>&1`
- `log`: `logs/knowledge/wiki-coverage-gap-*.log`
- `is_claude_task`: `false`
- `description`: weekly source-vs-wiki gap detection; writes reports only, no issue creation

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/detect_wiki_gaps.py` | CLI implementation |
| Create | `tests/knowledge/test_detect_wiki_gaps.py` | TDD coverage |
| Create | `config/ai-tools/wiki-gap-detection.yaml` | detector config |
| Create | `docs/reports/wiki-coverage-gaps/README.md` | output contract |
| Create/runtime output | `docs/reports/wiki-coverage-gaps/_summary.md` | summary + skipped-input accounting |
| Runtime output | `docs/reports/wiki-coverage-gaps/<domain>.yaml` | per-domain gaps for domains with true gap entries |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | weekly schedule |

---

## TDD Test List

### Identity and matching
- `test_sha256_source_key_matches_wiki_page`
- `test_md5_only_source_becomes_identity_unresolved_not_gap`
- `test_bare_hex_source_key_warns_and_normalizes_to_sha256`
- `test_missing_doc_key_becomes_identity_unresolved`

### Input-boundary behavior
- `test_missing_optional_inputs_are_reported_not_fatal`
- `test_missing_required_input_fails_closed`
- `test_only_allowlisted_inputs_are_loaded`
- `test_docs_reports_markdown_is_not_scanned_as_source_inventory`

### Wiki/frontmatter behavior
- `test_wiki_page_missing_doc_key_emits_schema_warning`
- `test_wiki_page_missing_title_or_last_updated_emits_schema_warning`
- `test_nonconforming_wiki_doc_key_not_added_to_coverage_index`

### Output behavior
- `test_dry_run_prints_summary_without_writing_files`
- `test_gap_yaml_written_only_for_domains_with_true_gaps`
- `test_stale_domain_yaml_removed_when_domain_is_now_covered`
- `test_summary_lists_skipped_optional_inputs`
- `test_gap_entry_contains_required_fields`
- `test_summary_counts_gap_covered_and_identity_unresolved`

### Runtime and scheduling
- `test_cron_config_parses_and_schedules_weekly`
- `test_runtime_smoke_command_is_documented`

### Manual verification before approval
- `test -f data/document-index/index.jsonl`
- `timeout 300 uv run python scripts/knowledge/detect_wiki_gaps.py --config config/ai-tools/wiki-gap-detection.yaml --dry-run`
  - run only after the required-input precheck passes
  - must exit 0 on the current corpus
  - must print summary counts including gaps / covered / identity-unresolved / skipped-inputs

---

## Acceptance Criteria

- [ ] `scripts/knowledge/detect_wiki_gaps.py` exists with unit tests
- [ ] `uv run pytest tests/knowledge/test_detect_wiki_gaps.py -q` passes
- [ ] detector emits `docs/reports/wiki-coverage-gaps/<domain>.yaml` only for domains with true canonical gaps
- [ ] each gap entry includes `doc_key`, `source_path`, `availability_tier`, `discipline`, `status`, and `suggested_page`
- [ ] records with only legacy/ambiguous identity are surfaced as `identity-unresolved`, not false gaps
- [ ] `--dry-run` prints summary counts and writes nothing
- [ ] `_summary.md` reports skipped optional inputs and wiki-schema warnings
- [ ] stale `<domain>.yaml` files are removed when a previously-gapped domain becomes covered
- [ ] weekly schedule is wired in `config/scheduled-tasks/schedule-tasks.yaml` using task id `wiki-coverage-gap-detection`
- [ ] required-input precheck `test -f data/document-index/index.jsonl` passes on the target checkout before the smoke run
- [ ] manual runtime smoke check `timeout 300 uv run python scripts/knowledge/detect_wiki_gaps.py --config config/ai-tools/wiki-gap-detection.yaml --dry-run` exits 0 on the current corpus and prints summary counts

---

## Adversarial Review Summary

Historical preserved artifacts:
- `scripts/review/results/2026-04-20-plan-2392-claude.md`
- `scripts/review/results/2026-04-20-plan-2392-codex.md`
- `scripts/review/results/2026-04-20-plan-2392-gemini.md`
- `scripts/review/results/2026-04-20-v2-plan-2392-codex.md`
- `scripts/review/results/2026-04-20-v2-plan-2392-gemini.md`
- `scripts/review/results/2026-04-20-v3-plan-2392-codex.md`
- `scripts/review/results/2026-04-20-v3-plan-2392-gemini.md`
- `scripts/review/results/2026-04-20-validation-2405-via-plan-2392-codex.md`

Current re-file wave (this session):
- Codex v4: MAJOR — `scripts/review/results/2026-04-21-v4-plan-2392-codex.md`
- Gemini v4: MAJOR — `scripts/review/results/2026-04-21-v4-plan-2392-gemini.md`

Live blocker themes after the 2026-04-21 wave:
- source-vs-wiki normalization still needs a fully consistent migration contract
- join-bearing optional inputs need explicit degraded/fail-closed semantics
- page-class selection for schema validation vs coverage indexing needs one coherent rule
- scheduled-task/report distribution semantics need to be explicit
- duplicate wiki `doc_key` and unresolved-domain handling need first-class behavior

---

## Risks and Open Questions

- Registry schemas are heterogeneous; normalization must stay explicit and test-backed.
- Optional inputs may disappear or move over time; summary accounting must make that visible.
- Some durable knowledge may still lack `doc_key` until #2360/#2389 fully land; this is expected and must not be misreported as canonical coverage gaps.

---

## Complexity

T2 — single-script detector with explicit normalization and medium test surface, but no production mutation path.
