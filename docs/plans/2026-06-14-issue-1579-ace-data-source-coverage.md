# Plan for #1579: /mnt/ace data-source coverage, dedup/reorg safety, and llm-wiki mapping

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-06-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/1579
> **Client:** N/A
> **Project:** workspace-hub data inventory
> **Lane:** lane:codex
> **Review artifacts:** latest completed review wave is r5 under `scripts/review/results/2026-06-14-plan-1579-r5/`; r6 is required after this revision before `status:plan-review`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/data/ace_resource_audit.py` already audits four narrow surfaces for [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579): expected engineering repos, `docs/conferences`, `O&G-Standards`, and `docs/engineering-refs`. It writes `docs/reports/ace-undiscovered-resources.md`.
- Found: `tests/data/test_ace_resource_audit.py` already mocks the prior audit surfaces and verifies repo catalog, conference index, standards coverage, engineering-ref scan, and report generation behavior.
- Found: `docs/reports/ace-undiscovered-resources.md` records the prior pass: 8 repos scanned, 7/8 in catalog, 30 conference collections unindexed, 26,884 standards files on disk, and 364 standards in ledger.
- Found local prerequisite: `data/document-index/index.jsonl` exists on `dev-primary` as ignored machine-local document-index state. Sample keys include `path`, `old_path`, `content_hash`, `summary`, `summary_done`, `summary_file_exists`, `target_repos`, `domain`, `source`, and `status`. Some rows can carry `summary: null`, `summary_done: true`, and `summary_file_exists: true`, so implementation must resolve ignored summary sidecars under `data/document-index/summaries/` before treating a row as described. Implementation must fail closed with a clear prerequisite error if the local index or a required summary sidecar is absent.
- Found: `data/document-index/cross-drive-dedup-report.json` already has prior dedup evidence across `/mnt/ace` and remote DDE source pairs, including `exact_duplicates`, `name_size_matches`, `unique_to_ace`, and `unique_to_dde`.
- Found: `data/document-index/mounted-source-registry.yaml` already carries source roots, canonical storage policy, provenance rules, and dedup rules for `/mnt/ace`, `/mnt/ace-data`, remote DDE, standards, literature, and project archives.
- Found: `config/client-wikis.yml` declares `llm-wiki-mkt-a` and `llm-wiki-client-e` as bootstrapped client wiki siblings, with additional planned client wiki siblings for client-b, client-c, lng-a, client-a, and client-d.
- Routing context: this plan reads `llm-wiki*` checkout metadata for coverage mapping but does not write wiki content, so the plan header remains `Client: N/A` per the issue-plan template.
- Boundary: generated tracked inventory/report artifacts must be positive-allowlist sanitized. This plan and review artifacts may quote minimal path/config evidence for governance review; generated JSON/JSONL/CSV/HTML outputs must not repeat exact raw mount paths, private wiki paths, client/project basenames, client-identifying raw filenames, or free-text descriptions. Generated tracked artifacts will use content-free sequential refs (`row_000001`, `wiki_0001`), safe enum values, and aggregate counts. The ref-to-path mapping lives only in a durable ignored local full-fidelity artifact under `artifacts/private/issue-1579/`, with a tracked manifest that records local artifact SHA and retention metadata but no raw paths.
- Gap: no existing artifact records every live `/mnt/ace` root child with description status, decision state, duplicate/reorg state, raw-source preservation state, and `llm-wiki*` mapping status.
- Gap: no deterministic queue currently surfaces unknown descriptions and uncertain duplicate-quality choices one at a time for user decisions.
- Gap: no current percentage mapping from `/mnt/ace` data-source inventory to live `llm-wiki*` repos exists with reproducible denominators.

### Standards and rules

| Standard / rule | Status | Source |
|---|---|---|
| Issue planning workflow | active; this issue is still `status:needs-plan` and must stop before implementation approval | `.claude/skills/coordination/issue-planning-mode/SKILL.md`, `docs/plans/README.md` |
| Repo/data location planning | active; raw/source placement and repo placement must stay separate and moves must be future reviewable transactions | `.claude/skills/coordination/issue-planning-mode/references/repo-location-contract-planning.md` |
| Wiki sibling routing | active for any `llm-wiki` or `llm-wiki-<client>` mapping, even if this issue only reads wiki repos | `.claude/rules/wiki-sibling-routing.md` |
| Codes and standards routing | active for standards-derived material; raw vendor PDFs stay off-repo at `/mnt/ace` and wiki holds derived knowledge only | `.claude/rules/codes-standards-data-routing.md` |
| Legal/security scan | required before code closeout | `scripts/legal/legal-sanity-scan.sh` |
| Completeness before close | active because [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579) has `gate:completeness`; implementation closeout will build and save a deterministic package map, call `classify(changed_files, path_package_map)`, require `evidence`, then compute the stamped record with `score_evidence()` for owner verification | `.claude/rules/completeness-before-close.md`, `scripts/workflow/completeness_score.py`, `scripts/workflow/render_completeness_html.py`, `scripts/workflow/completeness_gate_runner.py` |

### LLM Wiki pages and repos consulted

- Live sibling checkouts observed on this machine: `/mnt/local-analysis/llm-wiki`, `/mnt/local-analysis/llm-wiki-mkt-a`, and `/mnt/local-analysis/llm-wiki-fdas`.
- `llm-wiki` checkout membership and git status can drift between planning and implementation. During r5 review, a transient `llm-wiki-vbatch-165-review` worktree was observed and then disappeared before the next local poll. Implementation must record each observed wiki checkout's branch, clean/dirty state, ahead/behind state, and checkout class at run time. Eligible sibling checkouts feed coverage percentages; transient/non-sibling worktrees are recorded as exclusions and must not create registry-drift decisions.
- `llm-wiki-mkt-a` is clean at planning time and contains client workflow docs, `projects/proj-a`, `projects/B1546-Noble-Drilling`, `sources/`, and `ledgers/`.
- `llm-wiki-fdas` is live on disk but not listed in `config/client-wikis.yml`; `config/client-wikis.yml` does list planned `client-a` with repo `vamseeachanta/llm-wiki-client-a`. Because the live registry has no `fdas` alias or row, implementation must classify the current live state as `observed-unregistered` and queue registry reconciliation. `registered-slug-mismatch` is allowed only when explicit registry or source-manifest alias evidence links the live checkout to a registered client row.
- `llm-wiki-client-e` is listed as bootstrapped in `config/client-wikis.yml`, but no sibling checkout was observed under `/mnt/local-analysis` during planning while its registered raw root exists under `/mnt/ace`. Implementation must report this reverse drift as `registered-but-not-checked-out` and must not collapse it into the same bucket as live-but-unregistered repos.
- `llm-wiki` contains source manifests and data-document-index artifacts such as `data/document-index/og-standards-raw-bucket-disposition.jsonl`, `og-standards-raw-unique-quarantine.jsonl`, `conference-candidate-manifest.jsonl`, and multiple source-manifest validators. These are reuse candidates for mapping and dedup/reorg semantics.

### Documents consulted

- Issue [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579) is open and currently asks for `/mnt/ace` description coverage, dedup/reorg readiness without raw-data loss, duplicate-quality decisions, and `llm-wiki*` percentage mapping.
- Issue [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) and plan `docs/plans/2026-05-19-issue-2731-data-repo-location-contract.md` already establish the repo/data location boundary: active checkouts under `/mnt/local-analysis`, raw/bulk/source data under `/mnt/ace`, and no movement during planning.
- Issue [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) remains open for first/second-level mount and folder taxonomy. This plan will consume that taxonomy direction but will not block on it.
- Issue [#2643](https://github.com/vamseeachanta/workspace-hub/issues/2643) and plan `docs/plans/2026-05-04-issue-2643-llm-wiki-rawlike-source-triage.md` already define metadata-only raw-like routing and prohibit raw content promotion.
- Issue [#2392](https://github.com/vamseeachanta/workspace-hub/issues/2392) and plan `docs/plans/2026-04-23-issue-2392-wiki-coverage-gap-detector.md` define a wiki gap detector using indexed metadata rather than direct mount scanning.
- `docs/reports/ace-undiscovered-resources.md` is prior evidence for the first [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579) pass, but it is not description coverage or reorg/deletion authorization.

### Gaps identified

- No script currently builds a row per `/mnt/ace` root child with `indexed`, `described`, and `decided` states.
- No artifact currently distinguishes exact duplicate, near duplicate, superseded version, lossy export, generated derivative, and raw/source original for `/mnt/ace` root coverage.
- No relocation/deletion ledger exists for [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579). This issue must create a proposal ledger but must not execute moves or deletions.
- No deterministic user-decision queue exists for unknown descriptions or uncertain duplicate-quality ratings.
- No coverage percentages currently map eligible `/mnt/ace` data-source items into live `llm-wiki*` checkouts with explicit denominators.
- No validation currently proves percentage math is reproducible from the machine-readable coverage artifact.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-14T10:31:36Z via `gh issue view`):

- [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579) - OPEN - Audit /mnt/ace descriptions, dedup/reorg safety, and llm-wiki coverage mapping - labels include `status:needs-plan`, `gate:completeness`, `cat:data`, `cat:data-pipeline`, `cat:document-intelligence`, `domain:document-intelligence-indexing`, `domain:knowledge-management-corpus`, `domain:repo-organization-cleanup-migration`, `machine:dev-primary`, `dispatch:ready`, and `lane:codex`. Coverage percentages produced by this plan are machine-specific to the live mounts visible on `dev-primary`.
- [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) - OPEN - data/repo location contract for llm-wiki promotion.
- [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) - OPEN - first/second-level mount and folder taxonomy.
- [#2643](https://github.com/vamseeachanta/workspace-hub/issues/2643) - CLOSED - metadata-only `/mnt/ace-data` raw-like source coverage triage.
- [#2392](https://github.com/vamseeachanta/workspace-hub/issues/2392) - OPEN - wiki coverage-gap detector.

**File existence** (`git ls-files` where tracked, `test -e` for local prerequisites, and live reads, 2026-06-14T10:31:36Z):

- EXISTS: `scripts/data/ace_resource_audit.py`
- EXISTS: `tests/data/test_ace_resource_audit.py`
- EXISTS: `docs/reports/ace-undiscovered-resources.md`
- EXISTS LOCAL IGNORED PREREQUISITE: `data/document-index/index.jsonl`
- EXISTS: `data/document-index/cross-drive-dedup-report.json`
- EXISTS: `data/document-index/mounted-source-registry.yaml`
- EXISTS: `config/client-wikis.yml`
- EXISTS: `.claude/rules/wiki-sibling-routing.md`
- EXISTS: `.claude/rules/codes-standards-data-routing.md`
- EXISTS: `.claude/rules/completeness-before-close.md`
- MISSING (new, this plan will create): `scripts/data/ace_data_source_coverage.py`
- MISSING (new, this plan will create): `scripts/data/ace_data_source_coverage_lib.py`
- MISSING (new, this plan will create): `tests/data/test_ace_data_source_coverage.py`
- MISSING (new, this plan will create): `data/inventory/ace-data-source-description-coverage.json`
- MISSING (new, this plan will create): `data/inventory/ace-data-source-decision-queue.jsonl`
- MISSING (new, this plan will create): `data/inventory/ace-data-source-relocation-ledger.csv`
- MISSING (new, this plan will create): `docs/reports/ace-data-source-description-coverage.html`
- MISSING (new, this plan will create): `docs/reports/issue-1579-implementation-notes.html`
- MISSING (new, tracked private-artifact manifest): `data/inventory/ace-data-source-private-artifact-manifest.json`
- MISSING (new, ignored local artifact): `artifacts/private/issue-1579/ace-data-source-description-coverage.full.json`
- MISSING (new at implementation closeout): `docs/reports/<completion-date>-1579-completeness.html`

**Line excerpts**:

`scripts/data/ace_resource_audit.py:1-12` shows the prior audit scope:

```text
"""Audit /mnt/ace for undiscovered resources and cross-reference against indexes.

Scans:
  1. 8 cloned GitHub repos vs open-source-engineering-catalog.yaml
  2. docs/conferences/ vs document-index/index.jsonl
  3. O&G-Standards/ orgs vs standards-transfer-ledger.yaml
  4. docs/engineering-refs/ subdirectories

Output: docs/reports/ace-undiscovered-resources.md

GH issue: #1579
"""
```

`data/document-index/mounted-source-registry.yaml` records source-root provenance and dedup policy fields. Selected fields from the live file include:

```text
- source_id: ace_project_local
  document_intelligence_bucket: ace_project
  mount_root: /mnt/ace/docs
  canonical_storage_policy: mounted project-document source
  provenance_rule: mounted project path should stay authoritative
  dedup_rule: prefer canonical mounted project path
  availability_check_ref: scripts/readiness/check-network-mounts.sh
- source_id: research_literature_local
  mount_root: /mnt/ace-data/digitalmodel/docs/domains
  symlink_note: /mnt/ace-data is a symlink to /mnt/ace (local drive /dev/sda1)
  canonical_storage_policy: downloaded research literature organized by engineering domain
  dedup_rule: prefer this location over ad-hoc downloads; check before re-downloading
```

`config/client-wikis.yml:6-73` shows the registry has `mkt-a` and `client-e` bootstrapped plus several planned client wikis, but no `fdas` row:

```text
- short_name: mkt-a
  repo: vamseeachanta/llm-wiki-mkt-a
  raw_roots:
    - /mnt/ace/mkt-a/
  status: bootstrapped
...
- short_name: client-e
  repo: vamseeachanta/llm-wiki-client-e
  raw_roots:
    - /mnt/ace/client-e/
  status: bootstrapped
```

`.claude/rules/wiki-sibling-routing.md:9-32` establishes suffix-form client siblings, `LLM_WIKI_TARGET`, visibility fields, and generic/client linking discipline.

`.claude/rules/codes-standards-data-routing.md:9-21` requires keeping raw vendor PDFs off-repo at `/mnt/ace` while derived content may live in private `llm-wiki`.

**Live filesystem proofs** (verified 2026-06-14T10:31:36Z):

```text
$ find /mnt/ace -mindepth 1 -maxdepth 1 | wc -l
61
$ find /mnt/ace -mindepth 1 -maxdepth 1 -type d | wc -l
54
$ find /mnt/ace -mindepth 1 -maxdepth 1 -type f | wc -l
7

$ find /mnt/local-analysis -maxdepth 1 -type d -name 'llm-wiki*' -printf '%f\n' | sort
llm-wiki
llm-wiki-mkt-a
llm-wiki-fdas

$ ls -ld /mnt/ace-data /mnt/ace
drwxrwxrwx 56 nobody nogroup 4096 Jun 12 03:21 /mnt/ace
lrwxrwxrwx  1 root   root       8 Mar 13 14:03 /mnt/ace-data -> /mnt/ace
```

**Reproduction proofs:** N/A - this is an audit/planning/data-governance issue, not a runtime failure. The required empirical proof is live filesystem enumeration plus artifact validation.

**Distinct source count:** 12+ (`#1579`, `#2731`, `#2732`, `#2643`, `#2392`, `scripts/data/ace_resource_audit.py`, `tests/data/test_ace_resource_audit.py`, `docs/reports/ace-undiscovered-resources.md`, `data/document-index/index.jsonl`, `data/document-index/cross-drive-dedup-report.json`, `data/document-index/mounted-source-registry.yaml`, `config/client-wikis.yml`, wiki routing rule, codes/standards routing rule).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-14-issue-1579-ace-data-source-coverage.md` |
| Implementation CLI wrapper | `scripts/data/ace_data_source_coverage.py` |
| Implementation library | `scripts/data/ace_data_source_coverage_lib.py` |
| Tests | `tests/data/test_ace_data_source_coverage.py` |
| Sanitized machine-readable coverage map | `data/inventory/ace-data-source-description-coverage.json` |
| Full-fidelity local coverage map (ignored, not committed) | `artifacts/private/issue-1579/ace-data-source-description-coverage.full.json` |
| Private artifact manifest (tracked, sanitized) | `data/inventory/ace-data-source-private-artifact-manifest.json` |
| Deterministic user-decision queue | `data/inventory/ace-data-source-decision-queue.jsonl` |
| Relocation/deletion proposal ledger | `data/inventory/ace-data-source-relocation-ledger.csv` |
| Human-facing report | `docs/reports/ace-data-source-description-coverage.html` |
| Implementation notes | `docs/reports/issue-1579-implementation-notes.html` |
| Completeness gate report | `docs/reports/<completion-date>-1579-completeness.html` |
| Planning index | `docs/plans/README.md` |
| Plan review - Claude | `scripts/review/results/2026-06-14-plan-1579-claude.md` (output target; valid evidence only after review process completes and file is non-empty) |
| Plan review - Codex | `scripts/review/results/2026-06-14-plan-1579-codex.md` (output target; valid evidence only after review process completes and file is non-empty) |
| Plan review - Gemini | `scripts/review/results/2026-06-14-plan-1579-gemini.md` (output target; valid evidence only after review process completes and file is non-empty) |
| Plan review r3 - Claude | `scripts/review/results/2026-06-14-plan-1579-r3/2026-06-14-plan-1579-claude.md` |
| Plan review r3 - Codex | `scripts/review/results/2026-06-14-plan-1579-r3/2026-06-14-plan-1579-codex.md` |
| Plan review r3 - Gemini | `scripts/review/results/2026-06-14-plan-1579-r3/2026-06-14-plan-1579-gemini.md` |
| Plan review r3 - Disagreement | `scripts/review/results/2026-06-14-plan-1579-r3/2026-06-14-plan-1579-disagreement.md` |
| Plan review r4 - Claude | `scripts/review/results/2026-06-14-plan-1579-r4/2026-06-14-plan-1579-claude.md` |
| Plan review r4 - Codex | `scripts/review/results/2026-06-14-plan-1579-r4/2026-06-14-plan-1579-codex.md` |
| Plan review r4 - Gemini | `scripts/review/results/2026-06-14-plan-1579-r4/2026-06-14-plan-1579-gemini.md` |
| Plan review r4 - Disagreement | `scripts/review/results/2026-06-14-plan-1579-r4/2026-06-14-plan-1579-disagreement.md` |
| Plan review r5 - Claude | `scripts/review/results/2026-06-14-plan-1579-r5/2026-06-14-plan-1579-claude.md` |
| Plan review r5 - Codex | `scripts/review/results/2026-06-14-plan-1579-r5/2026-06-14-plan-1579-codex.md` |
| Plan review r5 - Gemini | `scripts/review/results/2026-06-14-plan-1579-r5/2026-06-14-plan-1579-gemini.md` |
| Plan review r5 - Disagreement | `scripts/review/results/2026-06-14-plan-1579-r5/2026-06-14-plan-1579-disagreement.md` |

---

## Deliverable

A read-only `/mnt/ace` audit will produce a full-fidelity local description coverage map, sanitized tracked coverage artifacts, decision queues for unknowns, a dedup/reorg proposal ledger, raw-data preservation checks, and reproducible `llm-wiki*` percentage coverage without moving or deleting raw data in this issue.

---

## Pseudocode

```text
function collect_live_ace_roots(ace_root):
    enumerate first-level children with type, size if file, mtime, and realpath
    classify hidden/system entries separately from candidate data-source entries
    return stable sorted records

function apply_recursion_policy(root_records, indexes):
    enumerate all first-level /mnt/ace children
    enumerate max-depth-2 descendants for every first-level directory without following symlink directories
    fully recurse only candidate roots that realpath-resolve under /mnt/ace, are filesystem paths, are present, and are not already visited
    skip empty, remote, api://, missing, and non-/mnt/ace registry roots with explicit excluded_reason
    record symlink rows and canonical targets; count physical targets by realpath, with device/inode stored only as advisory evidence
    enforce deterministic defaults per root: timeout=120 seconds and row_cap=50000 unless CLI flags override them
    mark timed-out or capped roots partial, exclude partial rows from headline denominators, and report excluded counts next to each percentage
    record explicit scope_class and denominator_bucket for every emitted row

function load_existing_indexes():
    require data/document-index/index.jsonl to exist locally; fail closed with prerequisite error if absent
    require data/document-index/summaries/ when an index row has summary_file_exists=true and no inline summary
    stream data/document-index/index.jsonl for path, old_path, content_hash, summary, summary_done, summary_file_exists, target_repos, domain, source, status
    resolve summary sidecars deterministically; if the existing sidecar naming convention cannot be derived, fail closed and record the missing prerequisite in implementation notes
    load mounted-source-registry.yaml for source-root provenance and dedup rules
    load cross-drive-dedup-report.json for prior duplicate evidence
    load config/client-wikis.yml and live llm-wiki* checkout metadata

function describe_path(record, indexes):
    match exact path, old_path, source-root prefix, or registry raw_root prefix
    if indexed summary, summary file, prior report description, or wiki source-manifest description exists, record described=known with evidence
    registry policy/provenance fields may classify raw preservation but must not count as user-facing description evidence
    if only filename/path heuristics exist, record described=needs-user-decision
    never infer confidential client meaning from filename alone

function classify_duplicate_candidate(record, index_records):
    use content_hash when available for exact duplicates
    use name+size as near-duplicate signal only, not deletion proof
    score preserved-copy quality from raw/source priority, readability, completeness, size, parseability, source metadata, and domain usefulness
    if best copy is uncertain, queue side-by-side review decision and prohibit deletion

function map_to_llm_wiki(record, wiki_repos):
    classify every observed llm-wiki* checkout as eligible-sibling, registered-missing-checkout, or transient-non-sibling before coverage math
    identify transient-non-sibling worktrees by explicit worktree/review naming markers such as *-vbatch-*, *-review, detached worktree metadata, or matching the generic llm-wiki remote under a noncanonical directory name
    record transient-non-sibling checkouts in run metadata with excluded_reason=transient-non-sibling and exclude them from per-wiki denominators and registry reconciliation queues
    derive eligibility: generic, client, both, not-wiki-eligible, or needs-user-decision
    match registry raw_roots, wiki source manifests, wiki pages, and source folders
    record content-free target_wiki_ref in tracked artifacts; exact repo/path only in ignored full-fidelity artifact
    mark live-but-unregistered repos as observed-unregistered registry drift
    compare live checkout remote names with registry repo names and explicit registry/source-manifest alias fields
    when explicit alias evidence links a live repo to a registered client under a different slug, mark registered-slug-mismatch and queue a registry reconciliation decision
    when no explicit alias evidence exists, keep the conservative observed-unregistered drift status and queue registry reconciliation
    mark registered repos without local checkout as registered-but-not-checked-out registry drift
    when a registered raw root is live but the wiki checkout is absent, record target_wiki_ref, coverage_denominator_status=checkout-unavailable, and queue a follow-up decision
    classify applicability as client, general, both, unknown, or not-applicable

function calculate_coverage(rows):
    compute denominators from rows and explicit denominator_bucket values, not prose
    compute root-level, selected-recursive, client-work, general-work, and per-eligible-wiki-sibling percentages
    define general-work denominator as rows with client_general_applicability in {general, both} and scope_class in the included root or selected-recursive buckets, excluding partial rows and rows whose denominator_bucket is not-wiki-eligible
    fail if any denominator is zero without an explicit not-applicable reason
    keep tracked artifact diffs aggregate-stable only; path-level cross-run diffs require comparing local full-fidelity artifacts from both runs

function emit_artifacts(rows, decisions, relocation_proposals):
    create parent directories for all output artifacts before writing
    write ignored durable-local full-fidelity JSON coverage map with exact absolute paths under artifacts/private/issue-1579/
    write tracked sanitized private-artifact manifest with local artifact path, sha256, run_id, generated_at, and retention note; manifest must contain no raw path mappings
    write tracked sanitized JSON coverage map with content-free sequential refs, safe enum fields only, and no exact raw mount paths, private wiki paths, client/project basename tokens, reversible hashes, or free-text descriptions
    write tracked JSONL decision queue sorted by severity then path_ref
    write tracked CSV relocation/deletion proposal ledger with no executed actions; it is a proposal index keyed by path_ref and full_fidelity_artifact_sha256, not a standalone execution manifest
    render sanitized HTML report with sections for unknown descriptions, duplicate candidates, preservation risks, and wiki coverage
    render implementation-notes HTML with decisions, deviations, tradeoffs, open questions

function compute_completeness_before_close(changed_files, evidence_items):
    import completeness_score.classify, score_evidence, and render_completeness_html.write_html
    build deterministic path_package_map for the issue closeout from repo package roots discovered at implementation time: src/ plus top-level pyproject.toml or package.json roots, excluding node_modules, agent runtime/config folders, tests, docs, data, scripts, and generated artifacts
    save path_package_map and path_package_map_source in docs/reports/issue-1579-completeness-inputs.json
    call classify(changed_files, path_package_map) and require it returns evidence before score_evidence is called; if it returns code, stop and revise the plan before owner verification
    build weighted evidence_items for targeted tests, prior-audit regression tests, generated artifacts, redaction scan, legal scan, T3 code-stage review, no-move/no-delete verification, issue comment, and acceptance checklist
    call score_evidence(evidence_items, issue_number=1579)
    require result.passed is true, result.cls == "evidence", and result.threshold == 80 before requesting owner completeness verification
    write docs/reports/issue-1579-completeness-inputs.json with changed_files, evidence_class_rationale, weighted evidence_items, result.to_dict(), and artifact/test/review/legal evidence refs
    persist the result with hermes kanban complete --metadata '<record-json>' and stamp the issue body; if hermes is unavailable in lane:codex, stop closeout, record the failure in implementation notes and final issue comment, and do not ask for status:completeness-verified or close the issue until Hermes persistence succeeds or the completeness rule is explicitly revised
    render HTML with render_completeness_html.write_html(result.to_dict(), issue=1579, title="Audit /mnt/ace descriptions, dedup/reorg safety, and llm-wiki coverage mapping") and stamp result.to_dict() on the issue body for owner verification
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/ace_data_source_coverage.py` | Thin read-only CLI wrapper that orchestrates coverage map, dedup/reorg proposal ledger, wiki coverage percentages, decision queue, and HTML report |
| Create | `scripts/data/ace_data_source_coverage_lib.py` | Importable pure functions for enumeration, description evidence including summary sidecars, dedup classification, redaction, percentage math, and rendering inputs; split if needed to keep files under coding-style limits |
| Create | `tests/data/test_ace_data_source_coverage.py` | TDD coverage for enumeration, description states, duplicate classification, no-raw-loss guardrails, artifact redaction, relocation ledger integrity, and percentage math |
| Create | `data/inventory/ace-data-source-description-coverage.json` | Sanitized tracked source of truth for description/dedup/wiki coverage states; content-free refs only; no exact raw mount paths, private wiki paths, client/project basename tokens, reversible hashes, or free-text descriptions |
| Create local ignored | `artifacts/private/issue-1579/ace-data-source-description-coverage.full.json` | Durable local full-fidelity join artifact with exact raw paths for same-machine user decisions; must stay untracked |
| Create | `data/inventory/ace-data-source-private-artifact-manifest.json` | Sanitized tracked manifest containing local artifact path, sha256, run_id, generated_at, and retention note so future transactions can verify the local join artifact without exposing raw paths |
| Create | `data/inventory/ace-data-source-decision-queue.jsonl` | Deterministic one-item-at-a-time queue for unknown descriptions and uncertain duplicate-quality decisions using sanitized path references |
| Create | `data/inventory/ace-data-source-relocation-ledger.csv` | Proposed move/delete ledger with zero executed actions in this issue; future transaction plans must regenerate or securely load the full-fidelity artifact and join by content-free `path_ref` before executing any move |
| Create | `docs/reports/ace-data-source-description-coverage.html` | Sanitized human-facing report for data-source coverage, dedup/reorg candidates, raw preservation risks, and `llm-wiki*` coverage |
| Create | `docs/reports/issue-1579-implementation-notes.html` | Running implementation notes required by the issue |
| Create at closeout | `docs/reports/issue-1579-completeness-inputs.json` | Reviewable inputs for completeness scoring: changed files, path package map, map source, evidence-class rationale, weighted evidence items, result dictionary, issue number, and links to tests/artifacts/reviews/legal scan |
| Create at closeout | `docs/reports/<completion-date>-1579-completeness.html` | Required `gate:completeness` score report before closing [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579) |
| Update | `docs/plans/README.md` | Add this plan to the issue-plan index |
| Update if needed | `scripts/data/ace_resource_audit.py` | Only if code reuse requires adding a wrapper or deprecation pointer; the prior Markdown report should remain reproducible |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_root_enumeration_preserves_all_live_children` | first-level `/mnt/ace` child enumeration is stable and complete for fixture roots | fixture tree with dirs, files, hidden dirs | one row per child, stable sorted paths |
| `test_recursion_policy_sets_denominator_buckets` | approved recursion policy has explicit root, max-depth-2, selected-recursive, client, general, and per-wiki buckets | fixture tree plus registry and wiki raw roots | every emitted row has deterministic denominator buckets |
| `test_recursion_filters_registry_roots_to_ace_realpaths` | remote, empty, api, missing, and non-`/mnt/ace` roots do not get traversed | fixture registry with local, remote, empty, and api roots | only realpath-under-ace roots are traversed; others get excluded_reason |
| `test_symlink_realpath_dedup_prevents_double_count` | `/mnt/ace-data` or in-tree symlink aliases cannot inflate denominators | fixture `/mnt/ace-data -> /mnt/ace` plus symlinked subtree | one physical target counted once; symlink row recorded separately |
| `test_traversal_budget_marks_partial_and_excludes_denominator` | slow/huge roots do not produce false complete percentages | fixture walker timeout or row-cap hit | root has `scan_status=partial`, decision item exists, headline denominator excludes partial rows |
| `test_description_known_from_index_summary` | indexed path with summary becomes `described=known` | fixture index row with `summary` | coverage row records description and evidence |
| `test_description_known_from_summary_sidecar` | indexed path with `summary_done=true`, `summary_file_exists=true`, and empty inline summary resolves the ignored sidecar before marking described | fixture index row plus fixture sidecar directory | row is `described=known` with sidecar evidence |
| `test_missing_summary_sidecar_fails_closed` | a row that claims a summary sidecar cannot silently become described or unknown | fixture index row with missing sidecar | prerequisite error names the missing sidecar convention |
| `test_registry_policy_is_not_description_evidence` | provenance/dedup policy cannot mark a row described | fixture registry row with no summary/report text | row can have raw preservation evidence but remains `needs-user-decision` for description |
| `test_description_unknown_queues_user_decision` | path without evidence is not guessed | fixture root with no index/registry match | row has `needs-user-decision`; JSONL queue has one item |
| `test_registry_source_root_marks_raw_preservation` | mounted-source registry drives raw/source preservation classification | fixture mounted-source registry | row has raw/source status and provenance evidence |
| `test_exact_duplicate_uses_content_hash_only` | exact duplicate classification requires matching content hashes | two fixture index rows with same `content_hash` | `dedup_status=exact_duplicate_candidate` |
| `test_name_size_match_is_not_delete_authorization` | name+size match alone cannot authorize deletion | two same-name/same-size rows with no hash | `dedup_status=near_duplicate_candidate`, deletion prohibited |
| `test_uncertain_best_copy_creates_side_by_side_review` | uncertain quality does not delete | duplicate candidates with tied quality | decision queue item recommends side-by-side review |
| `test_relocation_ledger_requires_refs_checksum_and_rollback` | every proposed move has source ref, destination ref, checksum ref, reason, and rollback ref | fixture relocation proposal | ledger row validates or test fails |
| `test_no_executed_move_or_delete_actions` | this issue remains audit/proposal only | generated relocation ledger | all action states are `proposed` or `needs-user-decision` |
| `test_llm_wiki_live_repo_set_is_recorded` | live `llm-wiki*` clone enumeration is represented | fixture repo list | coverage metadata records exact repo set, checkout class, stale/clean status, and excluded counts |
| `test_transient_llm_wiki_worktree_is_excluded_from_denominators` | review/batch worktrees cannot pollute wiki coverage or drift queues | fixture `llm-wiki`, `llm-wiki-mkt-a`, and `llm-wiki-vbatch-165-review` with generic wiki remote under noncanonical name | transient checkout is recorded with `excluded_reason=transient-non-sibling`, excluded from per-wiki denominators, and not queued as `observed-unregistered` |
| `test_live_unregistered_client_wiki_registry_drift_is_flagged` | live wiki clone with no registry or alias evidence becomes drift candidate | fixture live `llm-wiki-fdas` remote, registry `client-a` row, no alias row | row/status flags `observed-unregistered` drift and queues registry reconciliation |
| `test_registered_slug_mismatch_requires_explicit_alias_evidence` | live wiki clone can become slug-mismatch only when the link is represented as data | fixture live wiki remote plus registry row carrying an explicit alias/source-manifest alias | row/status flags `registered-slug-mismatch` and queues registry reconciliation |
| `test_registered_wiki_without_checkout_is_drift_candidate` | registered wiki with raw root but no local checkout does not disappear from mapping | fixture `config/client-wikis.yml` row, live raw root, missing checkout | row/status flags `registered-but-not-checked-out`, denominator status `checkout-unavailable`, and follow-up decision item |
| `test_percentage_math_has_explicit_denominators` | coverage percentages are reproducible from rows | fixture rows with mapped/unmapped/not-eligible statuses | percentages match expected denominator arithmetic |
| `test_general_work_denominator_is_reproducible` | generic coverage denominator does not depend on prose or repo names | fixture rows across `general`, `both`, `client`, `unknown`, partial, and not-eligible buckets | denominator includes only eligible `general`/`both` complete rows in root or selected-recursive scope |
| `test_client_general_applicability_is_explicit` | each eligible row states client/general/both/unknown | fixture rows with raw roots and generic standards | no eligible row has empty applicability |
| `test_tracked_artifacts_redact_raw_mount_paths` | committed JSON/JSONL/CSV/HTML do not leak exact `/mnt/ace` or `/mnt/ace-data` raw paths | generated tracked artifacts | no exact raw mount path literals; content-free path_ref joins exist |
| `test_tracked_artifacts_redact_private_wiki_and_client_tokens` | sanitization removes private wiki paths, client/project basenames, raw path components, index summaries, summary sidecar text, dedup filenames, and observed raw filesystem basenames | generated tracked artifacts plus deterministic fixture leak corpus from client wiki registry, wiki project rosters, observed private paths, fixture `index.jsonl`, fixture summary sidecars, fixture dedup report, and raw fixture filenames | no denied token appears outside approved aggregate labels |
| `test_tracked_artifacts_are_positive_allowlist_only` | tracked per-row artifacts have no free-text description or domain fields | generated tracked artifacts | only schema-approved enum/hash/count fields appear; descriptions and evidence text are local-only |
| `test_tracked_refs_are_not_reversible_hashes` | tracked join keys cannot be brute-forced from known raw roots | generated tracked artifacts plus candidate raw paths | refs match content-free sequential pattern and contain no digest of raw path |
| `test_full_fidelity_artifact_is_local_only` | exact raw paths are available only in ignored full artifact | generated local and tracked artifacts | local artifact has exact paths; tracked artifacts do not |
| `test_private_artifact_manifest_is_sanitized_and_joinable` | tracked manifest lets future work verify the local full artifact without leaking paths | generated full artifact and manifest | manifest has local artifact path, sha256, run_id, generated_at, retention note; no path mappings |
| `test_sanitized_rows_are_aggregate_diffable_not_path_diffable` | tracked artifacts do not promise stable path-level refs across runs | two generated runs with reordered private paths | aggregate counts/status buckets diff cleanly; path-level comparison requires local full artifacts |
| `test_relocation_ledger_is_joinable_but_not_standalone_executable` | sanitized ledger can support future transaction planning without leaking paths | relocation proposal and full-fidelity artifact | ledger has content-free path_ref/full_fidelity_artifact_sha256; exact source/destination paths absent |
| `test_html_report_contains_required_sections` | human report carries all issue-required sections | generated HTML | sections for unknowns, dedup/reorg, raw preservation, wiki coverage |
| `test_decision_queue_order_is_deterministic` | user decisions surface one at a time in stable priority order | multiple unknown fixture rows | JSONL order is severity, then path |
| `test_completeness_path_package_map_derivation_is_saved` | governance audit closeout uses the repo's non-selectable class contract with a deterministic map | fixture repo roots with `src/`, package manifests, scripts, tests, docs, and data changed files | closeout inputs include `path_package_map`, map source, and `classify(changed_files, path_package_map) == "evidence"` |
| `test_completeness_closeout_stops_if_classify_returns_code` | implementation cannot bypass code-class scoring by rationale | fixture changed file under `src/` plus evidence items | closeout raises a plan-revision error before `score_evidence()` |
| `test_completeness_closeout_score_evidence_passes_threshold` | evidence-class closeout meets the opted-in completeness gate | weighted evidence fixture for tests/artifacts/legal/review/no-delete/checklist | `score_evidence(..., issue_number=1579)` returns `passed=true`, `cls=evidence`, and `threshold=80` |
| `test_completeness_inputs_json_is_written` | closeout record is reviewable and issue-bound | fixture closeout run | `docs/reports/issue-1579-completeness-inputs.json` contains changed files, path package map, evidence-class rationale, weighted evidence items, `result.to_dict()`, issue number, and evidence refs |

Run targeted tests with:

```bash
uv run pytest tests/data/test_ace_data_source_coverage.py -v
```

---

## Acceptance Criteria

- [ ] The implementation re-enumerates live `/mnt/ace` root children and writes exact counts into both the ignored full-fidelity artifact and the sanitized tracked coverage artifact.
- [ ] Exact absolute raw paths and free-text descriptions are written only to `artifacts/private/issue-1579/ace-data-source-description-coverage.full.json`, which remains ignored and untracked; generated tracked JSON/JSONL/CSV/HTML artifacts use content-free sequential `path_ref` / `target_wiki_ref`, safe enum values, counts, and aggregate labels only.
- [ ] `data/inventory/ace-data-source-private-artifact-manifest.json` is tracked and sanitized. It records the local full-fidelity artifact path, sha256, run_id, generated_at, and retention note, but no raw path mappings, client-identifying basenames, or free-text evidence. Future move/delete transaction issues must verify this manifest and local artifact or regenerate the full-fidelity artifact before acting.
- [ ] Generated tracked inventory/report artifacts contain no exact raw mount paths, private wiki paths, private repo paths, raw path components, client/project basename tokens, free-text descriptions, or free-text evidence snippets derived from `config/client-wikis.yml`, raw roots, wiki project rosters, observed private source paths, `index.jsonl`, or filenames. Exact values stay only in the ignored full-fidelity artifact.
- [ ] Tracked refs are not unsalted hashes or reversible encodings of paths; they are content-free sequential IDs scoped to the run. Path-level cross-run diffability is intentionally waived for generated tracked artifacts because non-reversible refs are required. Tracked artifact diffs are aggregate/status-bucket stable; exact path-level diffs require local full-fidelity artifacts from both runs.
- [ ] Every root child in the ignored full-fidelity artifact has exact `path`, `type`, `realpath`, `scope_class`, `denominator_bucket`, `likely_source_or_domain_text`, `description_text`, `description_evidence_text`, `index_membership`, `confidence`, `disposition`, `dedup_status`, `reorg_recommendation`, `raw_source_preservation_status`, `llm_wiki_mapping_status`, exact `target_wiki_repo_path`, and `client_general_applicability`.
- [ ] Every root child in the tracked sanitized artifact has `path_ref`, `type`, `canonical_target_ref`, `scan_status`, `scope_class`, `denominator_bucket`, `description_state`, `description_evidence_type`, `index_membership`, `confidence_bucket`, `disposition`, `dedup_status`, `reorg_recommendation`, `raw_source_preservation_status`, `llm_wiki_mapping_status`, `target_wiki_ref`, and `client_general_applicability`.
- [ ] The approved recursion policy is fixed for this implementation: all first-level `/mnt/ace` children; max-depth-2 descendants for every first-level directory without following symlink directories; full recursion only for existing mounted-source-registry roots, existing `config/client-wikis.yml` raw roots, and roots already represented in index/dedup evidence when their realpath resolves under `/mnt/ace`.
- [ ] Empty registry roots, `api://` sources, missing roots, `/mnt/remote` roots, and any root whose canonical realpath is outside `/mnt/ace` are recorded with `excluded_reason` and are excluded from `/mnt/ace` coverage denominators.
- [ ] Symlink aliases such as `/mnt/ace-data -> /mnt/ace` and in-tree symlinked folders are canonicalized by realpath before denominator calculation. Device/inode may be recorded as advisory evidence only; `st_ino==0` or duplicate inode values must never collapse distinct realpaths. The symlink row remains visible, but the physical target counts once.
- [ ] Traversal defaults are deterministic: `per_root_timeout_sec=120` and `per_root_row_cap=50000`, overridable only by explicit CLI flags recorded in the artifacts. If a selected root cannot complete within budget, its `scan_status=partial`, its rows are excluded from headline complete-coverage denominators, and an expansion/retry decision item is queued.
- [ ] Unknown descriptions are not guessed. They are added to `data/inventory/ace-data-source-decision-queue.jsonl` in deterministic order for one-by-one user decisions.
- [ ] Decision queue rows include `decision_severity` (`critical`, `high`, `medium`, `low`), `decision_type`, `path_ref`, `reason_code`, and `local_full_fidelity_required`; ordering is `decision_severity` then `path_ref`.
- [ ] A row is `described=known` only when supported by indexed summary, resolved summary sidecar, prior report description, or wiki/source-manifest description evidence. Registry provenance, canonical storage policy, and dedup policy alone do not count as description evidence.
- [ ] Duplicate candidates are classified as exact duplicate, near duplicate, superseded version, lossy export, generated derivative, raw/source original, or not duplicate.
- [ ] No delete is proposed without evidence of the preserved best-quality copy. If quality is uncertain, the candidate is queued for side-by-side review and deletion is prohibited.
- [ ] No move/delete is executed in this issue. `data/inventory/ace-data-source-relocation-ledger.csv` is a proposal ledger only.
- [ ] The relocation/deletion ledger schema is explicit: `proposal_id`, `source_path_ref`, `destination_ref`, `action`, `reason_code`, `quality_score_bucket`, `checksum_ref`, `rollback_ref`, `full_fidelity_artifact_sha256`, and `decision_status`. It is not a standalone move/delete execution manifest. Future transaction issues must regenerate or securely load the full-fidelity artifact before executing any path-specific action.
- [ ] Raw/source originals remain recoverable and carry provenance evidence in the coverage artifact.
- [ ] The live `llm-wiki*` repo set is enumerated, each observed checkout is classified as `eligible-sibling`, `registered-missing-checkout`, or `transient-non-sibling`, and eligible siblings are compared with `config/client-wikis.yml`; registry drift is reported only for eligible siblings and registered missing checkouts.
- [ ] Transient/non-sibling wiki worktrees such as `*-vbatch-*`, `*-review`, detached worktree clones, and noncanonical directories pointing at the generic wiki remote are recorded with `excluded_reason=transient-non-sibling`, excluded from per-wiki coverage denominators, and not emitted as `observed-unregistered` registry reconciliation decisions.
- [ ] Wiki coverage percentages include explicit denominators for root-level `/mnt/ace`, selected recursive scope, client-work coverage, general-work coverage, and each eligible live wiki sibling repo. `general-work` denominator is reproducible from rows as `client_general_applicability in {general, both}` plus included root/selected-recursive scope, excluding partial rows and rows whose denominator bucket is `not-wiki-eligible`.
- [ ] A live `llm-wiki*` repo without registry `raw_roots` and without explicit alias evidence receives `coverage_denominator_status=not-applicable-registry-drift` and drift status `observed-unregistered` rather than causing a zero-denominator failure. The current live `llm-wiki-fdas` / registered `client-a` state must use this conservative path unless an explicit alias is added to registry/source-manifest data before implementation. A live repo receives drift status `registered-slug-mismatch` only when explicit alias evidence links it to a registered client under a different slug. A registered wiki whose raw root is live but whose checkout is absent receives drift status `registered-but-not-checked-out`, `coverage_denominator_status=checkout-unavailable`, and a queued follow-up decision. Exact private repo names appear only in the full-fidelity artifact and the plan's bounded evidence section; generated tracked artifacts and final issue comments use `target_wiki_ref` plus aggregate counts.
- [ ] Percentage math is reproducible from `data/inventory/ace-data-source-description-coverage.json`.
- [ ] `docs/reports/ace-data-source-description-coverage.html` renders the human-facing report and includes unknowns, dedup/reorg candidates, preservation risks, coverage percentages, and next decision item.
- [ ] The HTML report renders `partial_excluded_count` and `partial_excluded_ref_count` adjacent to every headline percentage whose denominator excludes partial rows.
- [ ] `docs/reports/issue-1579-implementation-notes.html` records design decisions, deviations, tradeoffs, and open questions.
- [ ] All targeted tests pass: `uv run pytest tests/data/test_ace_data_source_coverage.py -v`.
- [ ] Regression tests for the prior audit pass continue to pass: `uv run pytest tests/data/test_ace_resource_audit.py -v`.
- [ ] Legal/security scan passes: `scripts/legal/legal-sanity-scan.sh`.
- [ ] T3 code-stage cross-review runs after implementation and before completeness/closeout. Required artifacts: `scripts/review/results/<completion-date>-impl-1579-claude.md`, `...-codex.md`, and `...-gemini.md`, or documented provider `UNAVAILABLE` degradation per cross-review routing.
- [ ] Because [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579) has `gate:completeness`, implementation closeout first builds a deterministic `path_package_map` from implementation-time repo package roots (`src/` plus top-level `pyproject.toml`/`package.json` package roots, excluding `node_modules`, agent runtime/config folders, tests, docs, data, scripts, and generated artifacts), records the map and source in `docs/reports/issue-1579-completeness-inputs.json`, and calls `completeness_score.classify(changed_files, path_package_map)`. Expected class is `evidence` because this is a governance/audit script and artifact issue that intentionally adds no package-mapped application code under `src/`. If `classify()` returns `code`, closeout stops and the plan must be revised before owner verification. Only after `classify()` returns `evidence` does implementation call `score_evidence(evidence_items, issue_number=1579)`. Implementation creates `docs/reports/issue-1579-completeness-inputs.json` with changed files, path package map, evidence-class rationale, weighted evidence items, issue number, `result.to_dict()`, and links to tests/artifacts/reviews/legal scan. Closeout requires `result.passed == true`, `result.cls == "evidence"`, and `result.threshold == 80` before any owner verification request. The issue-bound record is persisted with `hermes kanban complete --metadata '<record-json>'` and stamped into the issue-body ```completeness {json}``` block. If `hermes` is unavailable in the Codex lane, closeout fails closed: implementation notes and the final issue comment name the persistence failure, no `status:completeness-verified` request is made, and the issue is not closed until Hermes persistence succeeds or the completeness rule is explicitly revised. The record is rendered with `scripts/workflow/render_completeness_html.write_html(result.to_dict(), issue=1579, title="Audit /mnt/ace descriptions, dedup/reorg safety, and llm-wiki coverage mapping")` to `docs/reports/<completion-date>-1579-completeness.html`, and held for owner-applied `status:completeness-verified` before any close attempt.
- [ ] Pre-completion cleanup audit runs before any final "done" handoff, using `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`, and reports CLEAN/EXPECTED/UNEXPECTED residue.
- [ ] Final issue comment summarizes live `/mnt/ace` count, mapped/described/unknown counts, duplicate candidate count, proposed move count, executed move count fixed at zero, proposed deletion count with evidence refs, executed deletion count fixed at zero, live wiki aggregate counts by `target_wiki_ref`, coverage percentages, decision queue locations, artifacts, tests, legal scan, code-stage review artifacts, cleanup audit result, and pending user decisions.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MAJOR | missing `gate:completeness` close flow; stale lane evidence; undefined recursion denominators |
| Codex r1 | MAJOR | tracked artifact private-path boundary missing; `Client: N/A` inconsistent with wiki routing; registry policy treated as description evidence; review artifacts needed rerun |
| Gemini r1 | MAJOR / evidence-disputed | provider reviewed an isolated `/tmp/wf0/repo` snapshot that contradicted live local `git ls-files` and `test -e` evidence for existing tracked files; kept as disagreement evidence, not accepted as local fact |
| Claude r2 | UNAVAILABLE | CLI returned rc=143 before producing a usable current review |
| Codex r2 | UNAVAILABLE | rerun did not produce a usable current review; stale prior artifact cited text no longer present |
| Gemini r2 | UNAVAILABLE | rerun did not produce a usable current review; stale prior artifact cited text no longer present |
| Claude r3 | MAJOR | forced `code` completeness class is structurally near-unpassable for a new audit package; module-status scope and `write_html(result)` call are broken; `llm-wiki-fdas` should be reconciled against registered `client-a` as a slug mismatch |
| Codex r3 | MAJOR | `score_code()` snapshot shape, package import name, threshold requirement, and closeout integration tests were underspecified |
| Gemini r3 | MAJOR / evidence-disputed | provider reviewed from `/tmp` and falsely reported repo files missing; kept as disagreement evidence, with only generally applicable closeout-schema concerns considered |
| Claude r4 | MAJOR | package-map class derivation was not wired in the current close gate; `fdas` to `client-a` slug mismatch requires explicit alias data; r4 had insufficient usable provider signal |
| Codex r4 | UNAVAILABLE | Codex CLI returned `Reading additional input from stdin...` before producing a usable review |
| Gemini r4 | UNAVAILABLE | Gemini CLI failed before producing a usable review |
| Claude r5 | MAJOR | transient `llm-wiki-vbatch-165-review` worktree can pollute wiki denominators and drift queues without an exclusion policy |
| Codex r5 | MAJOR | same transient wiki-worktree blocker; completeness closeout must use the non-selectable `classify()` contract or a reviewed rule change |
| Gemini r5 | UNAVAILABLE | Gemini CLI failed before producing a usable review |

**Overall result:** blocked draft after r5. This revision addresses accepted r5 blockers by adding transient/non-sibling wiki checkout exclusion and restoring deterministic `classify(changed_files, path_package_map)` before evidence scoring. A fresh no-MAJOR r6 adversarial review is required before `status:plan-review`.

Revisions made based on review:
- Added explicit `gate:completeness` closeout criteria, issue-body stamp, HTML report, and owner verification requirement.
- Replaced tracked exact raw-path outputs with a sanitized tracked artifact plus ignored local full-fidelity join artifact.
- Clarified `Client: N/A` because the plan reads wiki metadata for coverage mapping but does not write wiki content.
- Fixed stale [#1579](https://github.com/vamseeachanta/workspace-hub/issues/1579) label evidence to match live `lane:codex` state and included `gate:completeness`.
- Replaced open recursion question with a fixed recursion policy and explicit denominator buckets.
- Removed registry policy/provenance as description evidence; it now supports raw preservation only.
- Added realpath-under-`/mnt/ace` filtering, symlink realpath canonicalization with inode advisory-only handling, traversal budget handling, stronger client/wiki token redaction, join-only relocation ledger semantics, and evidence-class completeness record requirements.
- Reclassified `data/document-index/index.jsonl` and its ignored summary sidecars as machine-local prerequisites, made tracked artifacts positive-allowlist only, kept free-text descriptions local-only, added parent-directory creation, defined live-but-unregistered and registered-but-not-checked-out wiki drift handling, and added required Kanban completeness persistence.
- Replaced reversible path hashes with content-free sequential refs, made generated tracked artifact redaction distinct from this plan's bounded evidence citations, specified deterministic traversal budgets, added code-stage T3 review, and added the pre-completion cleanup audit gate.
- Rejected the forced-code completeness path after r3 review showed it creates an impractical closeout gate for a governance audit; restored evidence-class scoring with explicit anti-dodge boundaries and no `src/` package-mapped application code.
- Moved the full-fidelity ref-to-path join artifact from ephemeral `tmp/` to ignored durable-local `artifacts/private/issue-1579/` and added a tracked sanitized manifest so future transaction work can verify the local artifact without exposing raw paths.
- Clarified that sanitized tracked artifacts are aggregate/status-bucket diffable only; path-level cross-run diffs require local full-fidelity artifacts from both runs because refs cannot be reversible path hashes.
- Pinned the `general-work` coverage denominator to row fields and changed Hermes completeness persistence from fallback-equivalent to fail-closed if unavailable.
- Addressed r3 completeness blockers by removing module-status/`score_code()` dependencies, requiring `score_evidence()` threshold pass evidence, using `result.to_dict()` for HTML/body stamps, and creating `issue-1579-completeness-inputs.json`.
- Addressed r4/r5 completeness blockers by specifying a deterministic implementation-time `path_package_map`, saving it in the closeout inputs, calling `classify(changed_files, path_package_map)`, and stopping if it returns `code` before evidence scoring.
- Addressed r4 wiki-drift blocker by requiring explicit registry/source-manifest alias evidence before `registered-slug-mismatch`; absent that evidence, live `llm-wiki-fdas` remains `observed-unregistered` plus queued registry reconciliation.
- Addressed r5 wiki-denominator blocker by adding `transient-non-sibling` checkout classification for review/batch worktrees and excluding those rows from per-wiki denominators and registry reconciliation queues.

---

## Risks and Open Questions

- **Risk:** `/mnt/ace` is large enough that full recursive per-file description coverage may be expensive. The implementation will default to exact root-child coverage plus approved selected-recursive surfaces and will make any deeper deferral explicit.
- **Risk:** filename/path heuristics can leak or misclassify confidential client context. Tracked artifacts will be sanitized beyond mount-prefix removal; exact raw paths, private wiki paths, and client/project basenames remain only in the ignored local full-fidelity artifact, and path-only inference is queued for user decision.
- **Risk:** symlink aliases and remote/API registry entries can corrupt denominators. The implementation will canonicalize to realpaths, traverse only present filesystem roots under `/mnt/ace`, and count each physical target once.
- **Risk:** live wiki checkout status and set membership can drift after planning, including short-lived review/batch worktrees. The implementation will record wiki repo status and checkout class, exclude transient/non-sibling clones from coverage denominators, and either refresh eligible checkouts under a separate safe step or mark mapping evidence as stale.
- **Risk:** wiki registry state has multiple drift classes: live `llm-wiki-fdas` is currently unregistered because no explicit alias links it to registered planned `client-a`, and registered `llm-wiki-client-e` was not observed as a local checkout during planning. The implementation will report observed-unregistered, explicit-alias slug-mismatch, and registered-without-checkout classes separately rather than silently excluding or conflating them.
- **Risk:** document-index rows can point to ignored summary sidecars not visible in tracked files. The implementation will require and resolve sidecars explicitly, then fail closed if the sidecar convention or file is unavailable.
- **Risk:** exact duplicate detection depends on available hashes. When hashes are missing, the implementation will classify candidates as near duplicates and prohibit deletion.
- **Decision:** The first approved implementation will use the fixed recursion policy in Acceptance Criteria: all root children, max-depth-2 for every first-level directory, and full recursion only for registry/wiki/index/dedup-backed roots whose canonical realpath is present under `/mnt/ace`.
- **Open:** Should future move/delete transactions become child issues per source family after this audit, or should one follow-up transaction issue consume the whole relocation ledger? Default recommendation: child issues per high-risk source family.

---

## Complexity: T3

**T3** - broad data governance and audit work across `/mnt/ace`, document-index artifacts, dedup evidence, live wiki siblings, client/general routing, and legal/raw-data preservation boundaries. Implementation is read-only/proposal-only but has high blast radius if the plan is wrong, so it requires T3 adversarial review.
