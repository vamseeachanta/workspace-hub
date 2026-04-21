# Plan for #2392: Wiki coverage-gap detector — v9 (post-#2405 re-file draft)

> Status: draft
> Complexity: T2
> Date: 2026-04-21
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2392
> Purpose: replace the preserved closed-issue plan with a re-file-ready draft that reflects current repo state and the #2405 attestation contract.

---

## Revision History

- v1-v3 (2026-04-20): preserved historical iterations that ended in MAJOR review and were closed pending #2405 review-infrastructure fixes.
- v4: addressed the six defects from `scripts/review/results/2026-04-20-validation-2405-via-plan-2392-codex.md` by:
  - removing closed-issue `plan-review` posture from the header
  - replacing missing/stale review-history claims with current repository reality
  - defining exact source inputs and optional-input behavior
  - defining the md5/sha256 join contract without false-gap behavior
  - replacing the data-dependent "one YAML per domain" acceptance criterion
  - replacing the undefined `L3-eligibility heuristic` with a concrete allowlist
- v5-v9 (2026-04-21): iterative adversarial tightening of the re-file draft. Latest draft adds explicit source dedupe contract, cross-domain coverage policy, canonical status enum, publication/exit-code contract, wiki-domain derivation precedence, supplemental-source field mappings, and shell-level scheduler locking/clean-worktree rules.

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

### Authoritative source inputs for this detector
The detector reads only git-tracked metadata and wiki pages. It does not dereference `/mnt/ace/**` directly.

Required inputs:
- `data/document-index/index.jsonl` — per-record indexed source inventory for `/mnt/ace/**` coverage questions
- `data/design-codes/code-registry.yaml` — structured standards/code inventory
- `knowledge/wikis/*/wiki/**/*.md` — candidate coverage-bearing wiki pages

Optional inputs:

Reporting-only optional:
- `data/document-index/registry.yaml` — aggregate counts only; summary/reporting aid, not join corpus
- `data/document-index/intelligence-accessibility-registry.yaml`
- `data/document-index/mounted-source-registry.yaml` — source-root metadata only; not normalized into gap records in v5
- `data/document-index/online-resource-registry.yaml` — reporting/reference aid only until a per-record join schema is defined

Supplemental coverage inputs (optional-by-presence, but coverage-affecting if configured/present):
- `data/document-index/dde-standards-inventory.yaml`
- `data/document-index/standards-transfer-ledger.yaml`
- `data/document-index/promotions/*.yaml`

Input roles:
- required join corpus: `index.jsonl`, `code-registry.yaml`
- supplemental join corpus: joinable per-record ledgers/manifests when present
- reporting-only: `registry.yaml`, accessibility hints, and skipped-input diagnostics

Optional semantics:
- reporting-only optional missing input != crash
- supplemental coverage input missing on a repo that does not use that surface != crash, but must be recorded in `_summary.md`
- if config explicitly expects a supplemental coverage input/pattern and it is missing, run status becomes `degraded`
- zero matches for an unconfigured glob pattern count as normal empty expansion; zero matches for a config-required pattern count as missing/degraded
- `degraded` runs may emit reports and may be published operationally, but they do NOT satisfy plan approval / acceptance gates for full detector readiness
- tests explicitly cover absent optional inputs and degraded-run semantics

### Scope boundary
This issue is analysis-only. It emits candidate gap reports and identity/status diagnostics. It does not generate wiki pages and does not mutate registry truth.

---

## Problem Statement

We need a repeatable way to answer:
- which indexed or registry-backed sources have no corresponding L3 wiki coverage yet
- which records cannot be matched safely because identity is legacy/ambiguous
- which disciplines have the highest uncovered source volume

The detector compares source-side inventory with wiki-side coverage by canonical `doc_key`, deduplicates multi-surface source records down to one canonical candidate per `doc_key`, then emits per-domain gap YAML plus a durable summary markdown.

---

## Identity Join Contract

### Canonical rule
- `sha256:<64hex>` is the only positive match key.
- `md5:<hex>` is accepted for reads but is never treated as a positive match against a `sha256:` wiki key.
- bare hex is a conformance violation everywhere and must always emit a warning.

### Source-side compatibility reads
For each source-side record:
1. if a canonical `sha256:` key is present, use it as the join key
2. else if a bare 64-hex value is present, emit a source-identity warning and classify the record as `identity-unresolved`
3. else if only `md5:` is present, emit entry/status `identity-unresolved`
4. else if no conforming key is present, emit entry/status `identity-unresolved`
5. do not classify unresolved identity as a true wiki-coverage gap

### Wiki-side coverage rule
For wiki pages:
1. schema validation applies to every non-structural wiki markdown file in scope
2. only explicit canonical `sha256:<64hex>` `doc_key` values enter the coverage index
3. bare-hex wiki `doc_key` values remain diagnostic-only (`wiki-schema-warning`) until the page is corrected
4. nonconforming wiki keys never count as coverage in this detector

This avoids false positives during migration while still surfacing actionable backlog.

### Canonical source-record status enum
Every normalized source candidate must end in exactly one authoritative status from this enum:
- `gap` — canonical source key present, no same-domain wiki page with the same canonical `doc_key`
- `covered` — canonical source key present and same-domain wiki page exists
- `identity-unresolved` — source exists but lacks canonical joinable identity
- `domain-unresolved` — source identity exists but the record cannot be assigned to a valid output domain/domain_slug
- `domain-mismatch` — canonical `doc_key` exists in wiki coverage, but only in a different normalized wiki domain
- `coverage-conflict` — canonical `doc_key` cannot be trusted for coverage because duplicate wiki pages claim the same key

This enum is authoritative for all later sections, pseudocode, tests, acceptance criteria, and report outputs.

### Wiki diagnostics
Wiki-frontmatter problems are tracked separately from source-record status:
- `wiki-schema-warning` — a non-structural wiki markdown file fails the §8.1/baseline validation needed for clean coverage accounting (for example missing `title`, `last_updated`, or canonical `doc_key`)

`wiki-schema-warning` entries appear only in `_summary.md` diagnostics and test assertions; they are not gap records.

---

## L3 Coverage Boundary (replaces undefined heuristic)

The previous plan's `docs/reports/*.md` heuristic was too loose. v4 replaces it with a concrete allowlist.

The detector uses three distinct surfaces:

### A. Source-side gap candidates
1. required join corpus from `data/document-index/index.jsonl`
2. required structured design-code inventory from `data/design-codes/code-registry.yaml`
3. supplemental join corpus with per-record document identity when present/configured:
   - `data/document-index/standards-transfer-ledger.yaml`
   - `data/document-index/dde-standards-inventory.yaml`
   - expanded matches from `data/document-index/promotions/*.yaml`

### B. Coverage-providing wiki artifacts
4. non-structural wiki markdown under `knowledge/wikis/*/wiki/**/*.md` is schema-validated for §8.1 compliance
5. only wiki pages with canonical `sha256:` `doc_key` participate in coverage indexing
6. wiki-domain derivation is authoritative in this order:
   - first: explicit domain hint in frontmatter field `domain` when present and normalized by config
   - second: repo path anchor `knowledge/wikis/<wiki-domain>/wiki/**` where `<wiki-domain>` becomes the normalized wiki domain slug
   - third: config mapping for exceptional wiki roots if path and frontmatter disagree
   - if derivation disagrees irreconcilably, treat the wiki page as diagnostic-only and emit `wiki-schema-warning`

### C. Reporting/context aids
6. optional reporting aids that do not become source records in v5:
   - `data/document-index/intelligence-accessibility-registry.yaml`
   - `data/document-index/registry.yaml`
   - `data/document-index/mounted-source-registry.yaml`
   - `data/document-index/online-resource-registry.yaml`

The detector must NOT scan arbitrary `docs/reports/*.md` as source inventory.
That content is L5 run output unless a separate promotion manifest has already elevated it into a durable source candidate.

Implication: `_summary.md` can never self-ingest, and report markdown cannot create feedback loops.

---

## Deliverable

A CLI at `scripts/knowledge/detect_wiki_gaps.py` that:
- loads required and optional inputs
- normalizes source candidates into a common record shape
- deduplicates records by canonical `doc_key` before coverage accounting
- parses wiki frontmatter and builds a canonical-coverage index by `sha256:` `doc_key`
- applies explicit cross-domain coverage policy before classifying a record as covered
- emits per-domain YAML only for domains with true canonical gaps
- emits `_summary.md` with counts for gaps, covered records, unresolved identity, unresolved domain, source-identity warnings, skipped optional inputs, duplicate wiki keys, domain-slug collisions, and wiki-schema warnings
- supports `--dry-run` to print the same summary without writing files

---

## Candidate Record Shape

Normalized source record fields:
- `source_type` (`index-record`, `ledger`, `promotion-manifest`, `design-code`)
- `domain`
- `domain_slug` — canonical file-safe domain identifier used for `<domain>.yaml`
- `title`
- `source_path`
- `doc_key`
- `availability_tier` (per operating-model §7)
- `discipline`
- `suggested_page`
- `status`
- `notes`
- `source_identity_warning` (optional)

Allowed source statuses (same authoritative enum as in Identity Join Contract):
- `gap`
- `covered`
- `identity-unresolved`
- `domain-unresolved`
- `domain-mismatch`
- `coverage-conflict`

Deduplication contract:
- one canonical `doc_key` yields at most one normalized source candidate in coverage accounting
- merge precedence for duplicate source surfaces is:
  1. `index-record`
  2. `promotion-manifest`
  3. `ledger`
  4. `design-code`
- higher-precedence records win for `source_path`, `title`, and `availability_tier`
- `domain`/`discipline` merge conservatively: if conflicting non-empty values disagree after normalization, emit `domain-unresolved` and exclude the record from per-domain YAML
- every collapsed duplicate set must be counted in `_summary.md` as a deduplication event

Cross-domain coverage policy:
- coverage is `doc_key + domain`, not `doc_key` alone
- if a wiki page with matching canonical `doc_key` exists in the same normalized domain, classify `covered`
- if a wiki page with matching canonical `doc_key` exists only in a different wiki domain, classify `domain-mismatch`; report it in `_summary.md`; and do not emit either `gap` or `covered` for that source record in per-domain YAML

Duplicate wiki-key policy:
- if multiple wiki pages claim the same canonical `doc_key`, classify affected source records as `coverage-conflict`
- `coverage-conflict` is summary-only diagnostic output and never serialized as per-domain gap YAML
- duplicate-conflict records count toward degraded run status and must be listed in `_summary.md`

Mapping expectations:
- `index-record`: read canonical identity/path from `index.jsonl`; derive `domain`/`discipline` from indexed metadata when present, otherwise from config mapping by source root/path prefix.
- `design-code`: derive `domain`/`discipline` from registry fields and configured default wiki-domain mapping.
- `ledger` / `promotion-manifest`: preserve source-provided domain when available; otherwise fall back to config mapping.
- `domain_slug` is derived from the resolved domain using lowercase kebab-case `[a-z0-9-]+`; collisions must be returned from normalization, reported in `_summary.md`, and mark the run `degraded`.
- if no mapping resolves a valid domain/domain_slug pair, emit `domain-unresolved`, count it in `_summary.md`, and do not write it into any per-domain YAML file.

Supplemental source field contracts:
- `standards-transfer-ledger.yaml`:
  - `doc_key`: row field `doc_key`
  - `title`: `title`, else `name`
  - `source_path`: `doc_path`, else `path`, else `source_path`
  - `domain`: `domain`, else `family`, else config domain map by standards org/category
  - `discipline`: `discipline`, else normalized `domain`
  - `availability_tier`: default `1` (git-tracked metadata per operating-model §7)
  - `suggested_page`: `knowledge/wikis/<normalized-domain>/wiki/<slugified-title>.md`
- `dde-standards-inventory.yaml`:
  - `doc_key`: `doc_key`, else namespaced hash field if already canonicalized, else unresolved
  - `title`: `title`, else `document_title`, else `name`
  - `source_path`: `doc_path`, else `path`, else `source_path`
  - `domain`: `domain`, else `category`, else config domain map by DDE section/type
  - `discipline`: `discipline`, else normalized `domain`
  - `availability_tier`: default `1`
  - `suggested_page`: `knowledge/wikis/<normalized-domain>/wiki/<slugified-title>.md`
- `promotions/*.yaml`:
  - `doc_key`: `doc_key`
  - `title`: `title`
  - `source_path`: `doc_path`, else `source_path`
  - `domain`: `domain`
  - `discipline`: `discipline`, else normalized `domain`
  - `availability_tier`: default `1`
  - `suggested_page`: `knowledge/wikis/<normalized-domain>/wiki/<slugified-title>.md`
- `index.jsonl` required corpus:
  - `doc_key`: `doc_key`
  - `title`: `title`, else basename from path
  - `source_path`: `path`
  - `domain`: explicit `domain`, else config `source_root_domain_map`
  - `discipline`: `discipline`, else normalized `domain`
  - `availability_tier`: default `1`
  - `suggested_page`: `knowledge/wikis/<normalized-domain>/wiki/<slugified-title>.md`
- `code-registry.yaml` required corpus:
  - `doc_key`: canonical code/standard key field if present; otherwise unresolved until linked to a source document
  - `title`: registry title/name field
  - `source_path`: linked source reference if present; otherwise unresolved
  - `domain`: config `design_code_domain_defaults`
  - `discipline`: normalized `domain`
  - `availability_tier`: default `1`
  - `suggested_page`: `knowledge/wikis/<normalized-domain>/wiki/<slugified-title>.md`
- if a source row lacks the authoritative identity/path fields above, it must be classified as `identity-unresolved` rather than silently normalized.

Gap YAML entry fields:
- `doc_key`
- `source_path`
- `domain`
- `discipline`
- `availability_tier`
- `suggested_page`
- `status`
- `notes`

Exit-code contract:
- `0` — clean success or degraded-but-reportable success in interactive/manual dry-run mode
- `2` — degraded scheduled/publication run; reports written but not approval-ready
- `1` — fail-closed error, including missing required inputs or normalization exceptions

---

## Pseudocode

```text
function run(config_path, dry_run=False, publication_mode=False):
    config = load_detector_config(config_path)  # domain mapping, structural excludes, output dir
    publication_mode = publication_mode or config.publication_mode
    required_inputs = [
        "data/document-index/index.jsonl",
        "data/design-codes/code-registry.yaml",
    ]
    reporting_optional_inputs = [
        "data/document-index/registry.yaml",
        "data/document-index/intelligence-accessibility-registry.yaml",
        "data/document-index/mounted-source-registry.yaml",
        "data/document-index/online-resource-registry.yaml",
    ]
    supplemental_input_patterns = [
        "data/document-index/dde-standards-inventory.yaml",
        "data/document-index/standards-transfer-ledger.yaml",
        "data/document-index/promotions/*.yaml",
    ]

    required_data = load_required_inputs(required_inputs)
    inspect_reporting_inputs(reporting_optional_inputs)  # existence/metadata only; payload is not normalized into source records
    missing_reporting = find_missing_reporting_inputs(reporting_optional_inputs)
    supplemental_matches, missing_supplemental = expand_and_load_optional_patterns(supplemental_input_patterns)

    run_status = "clean"
    if configured_supplemental_inputs_missing(config, missing_supplemental):
        run_status = "degraded"

    source_records, source_identity_warnings, domain_slug_collisions, dedupe_events = normalize_and_dedupe_source_records(required_data, supplemental_matches, config)
    if domain_slug_collisions:
        run_status = "degraded"

    wiki_index = {}
    wiki_domains_by_key = {}
    invalid_wiki_doc_keys = set()
    wiki_schema_warnings = []
    duplicate_wiki_doc_keys = {}
    for page in glob("knowledge/wikis/*/wiki/**/*.md"):
        if is_structural_wiki_page(page, config):
            continue
        fm = parse_frontmatter_safe(page)
        warning = validate_l3_frontmatter_baseline(fm)  # title, last_updated, doc_key
        if warning:
            wiki_schema_warnings.append({"page": page, "warning": warning})
        key = normalize_wiki_doc_key_for_coverage(fm.get("doc_key"))  # canonical sha256 only
        if not key:
            continue
        page_domain = infer_wiki_domain(page, fm, config)
        if key in invalid_wiki_doc_keys:
            duplicate_wiki_doc_keys[key].append(page)
            run_status = "degraded"
            continue
        if key in wiki_index:
            duplicate_wiki_doc_keys[key] = [wiki_index[key], page]
            del wiki_index[key]
            del wiki_domains_by_key[key]
            invalid_wiki_doc_keys.add(key)
            run_status = "degraded"
            continue
        wiki_index[key] = page
        wiki_domains_by_key[key] = page_domain

    gaps_by_domain = {}
    summary = counts(
        missing_reporting,
        missing_supplemental,
        wiki_schema_warnings,
        duplicate_wiki_doc_keys,
        source_identity_warnings,
        domain_slug_collisions,
        dedupe_events,
        run_status,
    )
    for record in source_records:
        if record.status == "domain-unresolved":
            add_domain_unresolved(summary, record)
            continue
        canonical_key = extract_canonical_join_key(record)
        if canonical_key is None:
            add_unresolved(summary, record)
            continue
        if canonical_key in invalid_wiki_doc_keys:
            add_duplicate_conflict(summary, record, canonical_key)
            set_status(record, "coverage-conflict")
            run_status = "degraded"
            continue
        if canonical_key in wiki_index:
            if wiki_domains_by_key[canonical_key] == record.domain_slug:
                add_covered(summary, record, wiki_index[canonical_key])
                set_status(record, "covered")
                continue
            add_domain_mismatch(summary, record, wiki_index[canonical_key], wiki_domains_by_key[canonical_key])
            set_status(record, "domain-mismatch")
            run_status = "degraded"
            continue
        set_status(record, "gap")
        add_gap(gaps_by_domain, summary, record, canonical_key)

    if dry_run:
        print(render_summary(summary, gaps_by_domain))
        return 0 if run_status in ("clean", "degraded") else 1

    if publication_mode:
        require_clean_worktree()

    reconcile_output_directory(
        config.output_dir,
        keep_domains=[record.domain_slug for record in gap_records(gaps_by_domain)],
        preserve_files=["README.md", "_summary.md"],
        domain_file_suffix=".yaml",
    )
    write_gap_yaml_only_for_domains_with_entries(gaps_by_domain)
    write_summary_md(summary, gaps_by_domain, missing_reporting, missing_supplemental, wiki_schema_warnings, duplicate_wiki_doc_keys, source_identity_warnings, domain_slug_collisions, dedupe_events)

    if not publication_mode:
        return 0 if run_status in ("clean", "degraded") else 1
    return 0 if run_status == "clean" else 2
```

---

## Scheduled Task Contract

Planned detector config at `config/ai-tools/wiki-gap-detection.yaml`:
- `output_dir`: `docs/reports/wiki-coverage-gaps`
- `structural_excludes`: basename/path patterns for `index.md`, `log.md`, and navigation-only wiki files
- `source_root_domain_map`: path-prefix/domain mapping for `index.jsonl` records that lack explicit domain metadata
- `design_code_domain_defaults`: default wiki-domain mapping for code-registry entries
- `wiki_domain_rules`: frontmatter/path/config precedence rules for deriving normalized wiki domain slugs
- `expected_supplemental_inputs`: optional join-bearing sources that must mark the run `degraded` when configured but missing
- `required_input_prechecks`: shell/file checks for `data/document-index/index.jsonl` and `data/design-codes/code-registry.yaml` before scheduled execution
- `publication_mode`: config field consumed by the CLI to enable publication branch explicitly (`publication_mode: true|false`)

Planned weekly scheduler entry in `config/scheduled-tasks/schedule-tasks.yaml`:
- `id`: `wiki-coverage-gap-detection`
- `label`: `Wiki coverage-gap detector`
- `schedule`: `15 4 * * 1`
- `machines`: `[dev-primary, ace-linux-1]`
- `requires`: `[python3, uv, git, flock]`
- `prefer`: `dev-primary`
- `single-run lock`: shell-level only via `flock -n $WORKSPACE_HUB/.locks/wiki-coverage-gap-detection.lock`
- `clean-worktree precondition`: abort publication if `git status --porcelain` is non-empty before the detector stages report outputs
- `command`:
  `mkdir -p $WORKSPACE_HUB/logs/knowledge $WORKSPACE_HUB/.locks && cd $WORKSPACE_HUB && test -f data/document-index/index.jsonl && test -f data/design-codes/code-registry.yaml && test -z "$(git status --porcelain)" && flock -n $WORKSPACE_HUB/.locks/wiki-coverage-gap-detection.lock sh -lc 'uv run python scripts/knowledge/detect_wiki_gaps.py --config config/ai-tools/wiki-gap-detection.yaml --publication-mode >> "$WORKSPACE_HUB"/logs/knowledge/wiki-coverage-gap-$(date +\%Y-\%m-\%d).log 2>&1; rc=$?; if [ $rc -eq 0 ] || [ $rc -eq 2 ]; then git add docs/reports/wiki-coverage-gaps; if ! git diff --cached --quiet; then git commit -m "docs(reports): refresh wiki coverage gaps" && git push origin main; fi; fi; exit $rc'`
- `log`: `logs/knowledge/wiki-coverage-gap-*.log`
- `is_claude_task`: `false`
- `description`: weekly source-vs-wiki gap detection; writes reports and publishes clean/degraded report updates from a clean target checkout only when output changes

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
- `test_bare_hex_source_key_emits_source_identity_warning_and_does_not_become_true_gap_without_canonical_match`
- `test_missing_doc_key_becomes_identity_unresolved`

### Input-boundary behavior
- `test_missing_reporting_optional_inputs_are_reported_not_fatal`
- `test_missing_configured_supplemental_input_marks_run_degraded`
- `test_missing_required_input_fails_closed`
- `test_optional_glob_patterns_expand_to_matching_files`
- `test_only_allowlisted_inputs_are_loaded`
- `test_docs_reports_markdown_is_not_scanned_as_source_inventory`
- `test_source_surfaces_deduplicate_by_canonical_doc_key`

### Wiki/frontmatter behavior
- `test_wiki_page_missing_doc_key_emits_schema_warning`
- `test_wiki_page_missing_title_or_last_updated_emits_schema_warning`
- `test_nonconforming_wiki_doc_key_not_added_to_coverage_index`
- `test_duplicate_wiki_doc_key_marks_run_degraded_and_sets_coverage_conflict`
- `test_domain_slug_collision_marks_run_degraded_and_reports_diagnostic`
- `test_matching_doc_key_in_wrong_wiki_domain_emits_domain_mismatch_without_gap_yaml`

### Output behavior
- `test_dry_run_prints_summary_without_writing_files`
- `test_gap_yaml_written_only_for_domains_with_true_gaps`
- `test_stale_domain_yaml_removed_when_domain_is_now_covered`
- `test_summary_lists_missing_reporting_and_supplemental_inputs`
- `test_summary_lists_source_identity_warnings`
- `test_summary_lists_domain_slug_collisions`
- `test_summary_lists_deduplication_events`
- `test_gap_entry_contains_required_fields`
- `test_summary_counts_gap_covered_identity_unresolved_domain_unresolved_and_domain_mismatch`
- `test_domain_unresolved_records_do_not_create_invalid_output_files`

### Runtime and scheduling
- `test_cron_config_parses_and_schedules_weekly`
- `test_runtime_smoke_command_is_documented`
- `test_publication_mode_requires_clean_worktree`
- `test_publication_mode_uses_shell_lock_only`
- `test_exit_code_contract_clean_degraded_and_fail_closed`

### Manual verification before approval
- On the chosen approval target checkout, run:
  - `test -f data/document-index/index.jsonl`
  - `test -f data/design-codes/code-registry.yaml`
- Then run:
  - `timeout 300 uv run python scripts/knowledge/detect_wiki_gaps.py --config config/ai-tools/wiki-gap-detection.yaml --dry-run`
- Approval gate interpretation:
  - required-input prechecks must pass on that target checkout
  - dry-run must exit `0`
  - only `clean` manual verification satisfies plan approval readiness for this issue
  - `degraded` runs may still be operationally publishable in scheduled mode, but they are NOT sufficient for plan approval
  - summary must print counts for gaps / covered / identity-unresolved / domain-unresolved / domain-mismatch / skipped-inputs / duplicate-conflicts / dedupe-events

---

## Acceptance Criteria

- [ ] `scripts/knowledge/detect_wiki_gaps.py` exists with unit tests
- [ ] `uv run pytest tests/knowledge/test_detect_wiki_gaps.py -q` passes
- [ ] detector emits `docs/reports/wiki-coverage-gaps/<domain>.yaml` only for domains with true canonical gaps
- [ ] one canonical `doc_key` contributes at most one normalized source candidate after source-surface deduplication
- [ ] each gap entry includes `doc_key`, `source_path`, `availability_tier`, `discipline`, `status`, and `suggested_page`
- [ ] records with only legacy/ambiguous identity are surfaced as `identity-unresolved`, not false gaps
- [ ] records whose domain cannot be resolved are surfaced as `domain-unresolved` and excluded from per-domain YAML output
- [ ] same-`doc_key` wiki pages in the wrong domain emit `domain-mismatch` and are summary-only diagnostics, not gap YAML rows
- [ ] duplicate wiki-key coverage conflicts emit `coverage-conflict` and are summary-only diagnostics, not gap YAML rows
- [ ] `--dry-run` prints summary counts and writes nothing
- [ ] `_summary.md` reports missing reporting inputs, missing supplemental inputs, wiki-schema warnings, source-identity warnings, duplicate wiki `doc_key` diagnostics, deduplication events, and overall `run_status`
- [ ] stale `<domain>.yaml` files are removed when a previously-gapped domain becomes covered
- [ ] weekly schedule is wired in `config/scheduled-tasks/schedule-tasks.yaml` using task id `wiki-coverage-gap-detection`
- [ ] publication mode is activated consistently via CLI/config contract and uses shell-level locking only
- [ ] publication mode requires a clean worktree before staging/commit/push
- [ ] on the chosen approval target checkout, required-input prechecks for `data/document-index/index.jsonl` and `data/design-codes/code-registry.yaml` pass before the smoke run
- [ ] manual runtime smoke check `timeout 300 uv run python scripts/knowledge/detect_wiki_gaps.py --config config/ai-tools/wiki-gap-detection.yaml --dry-run` exits `0`, reports `run_status: clean`, and reports no new detector-internal regressions on the approval target checkout

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
- Codex v5: MAJOR — `scripts/review/results/2026-04-21-v5-plan-2392-codex.md`
- Gemini v5: MAJOR — `scripts/review/results/2026-04-21-v5-plan-2392-gemini.md`
- Codex v6: MAJOR — `scripts/review/results/2026-04-21-v6-plan-2392-codex.md`
- Gemini v6: MAJOR — `scripts/review/results/2026-04-21-v6-plan-2392-gemini.md`
- Codex v7: MAJOR — `scripts/review/results/2026-04-21-v7-plan-2392-codex.md`
- Gemini v7: MAJOR — `scripts/review/results/2026-04-21-v7-plan-2392-gemini.md`
- Codex v8: MAJOR — `scripts/review/results/2026-04-21-v8-plan-2392-codex.md`
- Gemini v8: MAJOR — `scripts/review/results/2026-04-21-v8-plan-2392-gemini.md`
- Codex v9: MAJOR — `scripts/review/results/2026-04-21-v9-plan-2392-codex.md`
- Gemini v9: MAJOR — `scripts/review/results/2026-04-21-v9-plan-2392-gemini.md`
- Codex v10: MAJOR — `scripts/review/results/2026-04-21-v10-plan-2392-codex.md`
- Codex v11: MAJOR — `scripts/review/results/2026-04-21-v11-plan-2392-codex.md`

Live blocker themes after the latest 2026-04-21 wave:
- scheduler still is not truly single-publisher across the declared machine set
- domain-mapping config schema/precedence still needs fully normative shape
- dedupe contract still needs an explicit policy for sources that may legitimately map to multiple wiki domains
- publication path still needs a repo-clean guarantee for logs/side effects beyond staged report files
- approval gate still needs attested verification for `data/document-index/index.jsonl`

---

## Risks and Open Questions

- Registry schemas are heterogeneous; normalization must stay explicit and test-backed.
- Optional inputs may disappear or move over time; summary accounting must make that visible.
- Some durable knowledge may still lack `doc_key` until #2360/#2389 fully land; this is expected and must not be misreported as canonical coverage gaps.

---

## Complexity

T2 — single-script detector with explicit normalization and medium test surface, but no production mutation path.
