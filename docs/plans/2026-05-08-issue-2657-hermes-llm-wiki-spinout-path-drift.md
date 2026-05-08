# Plan for #2657: Remediate Hermes llm-wiki spinout path drift

> **Status:** plan-approved
> **Complexity:** T2
> **Date:** 2026-05-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2657
> **Review artifacts:** scripts/review/results/2026-05-08-plan-2657-claude-round4.md | scripts/review/results/2026-05-08-plan-2657-codex.md | scripts/review/results/2026-05-08-plan-2657-gemini.md | scripts/review/results/2026-05-08-plan-2657-disagreement.md
> **Review-of-record note:** `claude-round4.md` is the preserved non-empty Claude review artifact from the latest completed fanout. `claude.md` is treated as the runner's mutable working output because the fanout truncates that path during each new Claude run; copy any completed non-empty Claude output to a round-specific filename before citing it. `disagreement.md` records fanout/tooling status and cross-provider synthesis, especially when a provider stub is unavailable.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/analysis/provider_session_ecosystem_audit.py` already defines the `llm_wiki_spinout_path_drift` remediation rule. It matches legacy `knowledge/wikis/` and `knowledge/seeds/` paths and points remediation toward `llm-wiki/wikis/`, `llm-wiki/docs/`, `docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md`, and `docs/sessions/2026-05-07-nest-llm-wiki-kaggle-into-hub.md`.
- Found: `tests/analysis/test_provider_session_ecosystem_audit.py` already covers the rule at a minimal level by asserting that `knowledge/wikis/engineering/wiki/index.md` maps to `llm_wiki_spinout_path_drift` and includes `llm-wiki/wikis/` in canonical targets.
- Found: event-time vs corpus-growth separation already has baseline coverage in `tests/analysis/test_provider_session_ecosystem_audit.py::test_build_corpus_change_summary_separates_snapshot_and_event_time_deltas`; #2657 should preserve or tighten that invariant, not duplicate it blindly.
- Found: `scripts/cron/provider-session-ecosystem-audit.sh` runs the provider-session audit and writes the current-state generated artifacts `analysis/provider-session-ecosystem-audit.json` and `docs/reports/provider-session-ecosystem-audit.md`.
- Gap: tests do not yet encode all three focal Hermes examples from #2657 (`engineering/wiki/index.md`, `engineering/wiki/log.md`, `marine-engineering/wiki/index.md`) as a single regression fixture, and do not assert a structured remediation contract that separates actionable stale spinout reads from preserved historical/retained/compatibility surfaces.
- Gap: the current audit/report output can be interpreted too broadly as “go fix every `knowledge/wikis/` reference,” while repo evidence shows some references are still-valid workspace-hub contracts, compatibility fallbacks, health artifacts, personal wiki paths, or historical evidence. The implementation must clarify the audit rule’s decision boundary and update active stale spinout references that directly cite the three #2657 focal paths.
- Gap: active documentation/registry surfaces still cite moved domain wiki entry points, cross-links, and seeds as current workspace-hub paths. Approved implementation must update live references for the moved set listed in `knowledge/wikis/README.md` or explicitly mark any remaining occurrence historical; it must not defer these active docs/registry references to #2650 because #2657 acceptance requires no active stale `knowledge/wikis/.../wiki/` spinout references to remain unqualified.

### Standards and required retrieval bundle

| Standard / bundle item | Status | Source |
|---|---|---|
| Issue planning workflow | applies | `AGENTS.md`, `docs/plans/README.md`, and `docs/plans/_template-issue-plan.md` require issue → resource intelligence → plan → adversarial review → `status:plan-review` → user approval before implementation. |
| Documentation retrieval bundle | applies | `docs/plans/README.md:49-58` requires target governance docs, `docs/standards/CONTROL_PLANE_CONTRACT.md`, and durable-vs-transient boundary policy for `cat:documentation`. Consulted `docs/document-intelligence/README.md`, `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`, and the control-plane contract. |
| Harness/infra retrieval bundle | applies | `docs/plans/README.md:49-58` requires `CONTROL_PLANE_CONTRACT.md`, `config/agents/`, and `.claude/rules/` for `cat:harness`. Consulted `config/agents/{claude,codex,gemini}/state-snapshots|memory-snapshots` as provider-session state surfaces and `.claude/rules/{README.md,patterns.md,coding-style.md,calc-citation-contract.md}` as Claude adapter rules. No direct edits are planned there unless implementation discovers a focal stale spinout reference. |
| Hard-stop / approval gate | applies | `AGENTS.md` forbids implementation before user approval for GitHub issues and requires TDD before implementation. |
| Control-plane/session governance | applies | `docs/standards/CONTROL_PLANE_CONTRACT.md:18-35,54-63` defines provider adapters as control-plane surfaces and the reading order for AI agents; this issue should preserve workspace-hub as control plane and route moved llm-wiki content reads toward the llm-wiki repo rather than recreating missing focal files under `workspace-hub/knowledge`. |
| Durable vs transient/evidence boundary | applies | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md:45-66,87-99` distinguishes L3 durable knowledge from L5/L6 execution/session artifacts; provider-session audit outputs and logs must preserve historical/evidence references while active docs/tools should not present moved spinout paths as current authority. |

### LLM Wiki pages consulted

- N/A for direct content consultation — #2657 concerns provider-session audit stale-path remediation, not adding/editing wiki content.
- The focal `knowledge/wikis/...` files are missing in the current checkout and should not be recreated as part of #2657.
- Canonical target family for moved engineering/marine-engineering wiki content after spinout: `llm-wiki/wikis/` and `llm-wiki/docs/`.

### Documents consulted

- Issue #2657 — defines the Hermes `llm_wiki_spinout_path_drift` remediation scope and the three required sampled stale paths.
- `docs/reports/provider-session-ecosystem-audit.md` — current human audit report flags Hermes as `red`/`next_up` due to `llm_wiki_spinout_path_drift`, lists the three focal stale paths, and records 225 combined reads for the rule.
- `analysis/provider-session-ecosystem-audit.json` — machine-readable audit output records `rule_id: llm_wiki_spinout_path_drift`, `total_count: 225`, and the same top matched paths and canonical targets.
- `docs/reports/2026-05-08-provider-session-learning-transfer.md` — transfer report explains why #2657 remains separate from #2650: #2657 is scoped to provider-session audit evidence and stale-path-rule remediation.
- `docs/ops/legacy-claude-reference-map.md` — existing guidance classifies `knowledge/wikis/*` as historical paths and points agents toward `llm-wiki/*`.
- `knowledge/wikis/README.md` — documents that most domain wikis moved out, while `health-reports/` and `personal/` remain in workspace-hub; this is a required exception boundary.
- `scripts/content/wiki-to-website.py`, `scripts/data/llm-wiki/resolve_wiki_path.py`, and their tests/docs — evidence that some `knowledge/wikis/` references are executable compatibility contracts and must not be changed under #2657 without separate tests/scope.
- `docs/plans/2026-05-07-issue-2655-codex-nested-repo-context-drift.md` — adjacent provider-session drift plan; useful precedent for bounded remediation, exact evidence, and out-of-scope separation from broader cleanup.

### Decision rule for #2657 vs #2650 / valid exceptions

This issue is **not** a global `knowledge/wikis/` cleanup. During approved implementation, classify references as follows:

| Category | Examples | #2657 action |
|---|---|---|
| Provider-session audit sampled stale reads | the three missing paths listed in #2657 and top-matched by `llm_wiki_spinout_path_drift` | strengthen audit tests/metadata/report guidance so they clearly say redirect to `llm-wiki/*`, do not recreate workspace-hub files |
| Current generated audit artifacts | `analysis/provider-session-ecosystem-audit.json`, `docs/reports/provider-session-ecosystem-audit.md` | regenerate after the structured audit-rule contract patch; treat as current-state snapshots, not immutable logs |
| Historical/evidence/log/prior plan references | `logs/orchestrator/**`, old plans, review artifacts, transfer reports, quoted evidence blocks | preserve; do not rewrite solely to remove old paths |
| Still-valid workspace-hub wiki/storage contracts | `knowledge/wikis/health-reports/**`, `knowledge/wikis/personal/**`, compatibility fallback docs/code, intentionally retained examples | out of scope; preserve unless a separate approved issue/test covers changing that contract |
| Active documentation/registry references to moved wiki content | `docs/document-intelligence/README.md` knowledge-assets table, `data/document-index/intelligence-accessibility-registry.yaml` wiki/cross-link/seed rows, and any current-authority references in `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | in scope after approval: update all moved-domain/cross-link/seed current targets to `llm-wiki/*` or explicitly mark historical, with before/after evidence |
| Broader architecture/doc-intelligence references not directly required by active current-authority cleanup | other `docs/document-intelligence/**`, registries, `scripts/content/wiki-to-website.py` | read-only inventory only; if stale beyond the moved set or requires behavior changes, record as follow-up to #2650 or a separate issue, not as #2657 implementation |

Per-surface inclusion test for any planned edit beyond audit source/tests/generated report: **edit active prompts/docs/tools when they present the moved `knowledge/wikis/<domain>/wiki/`, `knowledge/wikis/cross-links.md`, `knowledge/seeds/`, or `tests/fixtures/llm-wiki/` locations as current authority; preserve historical/evidence/log references and behavior contracts unless a targeted test covers the change.**

Structured current-vs-historical marker for #2657 docs/registry edits: implementation must use explicit machine-checkable metadata rather than free-text "historical" prose. For YAML registry rows whose current authority has moved, add/update fields such as `current_authority_path: llm-wiki/...` and `legacy_workspace_hub_path_disposition: historical-reference`; retained rows such as `wiki-personal` and `knowledge/wikis/health-reports/**` must instead be marked or asserted as `legacy_workspace_hub_path_disposition: retained-workspace-hub-authority` (or equivalent documented enum) so verification can distinguish them from moved rows. For Markdown docs, use a bounded marker phrase/table column such as `Disposition: historical-reference; Current authority: llm-wiki/...`; tests must key on that marker shape, not on the mere substring `historical`.

Registry moved-set rule: #2657 updates existing registry rows for moved assets that are already present (`wiki-engineering`, `wiki-marine-engineering`, `wiki-maritime-law`, `wiki-naval-architecture`, `wiki-cross-links`, `knowledge-seeds`) plus any currently-present `tests/fixtures/llm-wiki/` row if discovered. The moved domains listed in `knowledge/wikis/README.md` but absent from the registry (`acma-projects`, `asset-management`, `engineering-standards`, `lng-projects`) are included in docs/current-authority scans; do **not** fabricate new registry rows for them under #2657 unless a RED test and source evidence prove the absence itself is a #2657 blocker. Otherwise record absent rows as follow-up evidence for #2650/separate registry completeness work.

### Gaps identified

- Add RED tests for the sampled stale path examples plus structured audit-rule metadata that is not currently present: `forbidden_actions` (do-not-recreate/restore), `exception_path_prefixes`, and `current_authority_scan_paths`. These are behavior/contract fields consumed by report/playbook generation, not free-text substring tests.
- Add or tighten assertions so generated remediation/playbook output is derived from those fields and separates actionable stale reads from valid exceptions/history rather than implying every `knowledge/wikis/` reference is actionable.
- Preserve the existing event-time-vs-corpus-growth regression and, if report wording changes, add a narrow assertion that `positive_corpus_growth_beyond_recent_activity` remains user-visible and separate from event-time activity counts.
- Do **not** build a new repo-wide active/historical classifier under #2657. Manual inventory in this plan is enough to define scope; automation belongs in a separate approved issue if needed.
- Update known active docs/registry entries for all moved domains listed in `knowledge/wikis/README.md` (`acma-projects`, `asset-management`, `engineering`, `engineering-standards`, `lng-projects`, `marine-engineering`, `maritime-law`, `naval-architecture`) plus `cross-links.md`, `knowledge/seeds/`, and `tests/fixtures/llm-wiki/` if present, so they no longer present workspace-hub paths as current live locations unless explicitly labeled historical.
- Regenerate audit outputs after the approved structured audit-rule contract patch using `scripts/cron/provider-session-ecosystem-audit.sh`, and inspect generated diffs for semantic confinement to #2657.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-08T12:48:55Z via `gh issue view`):

```text
2657 OPEN chore(provider-session): remediate Hermes llm-wiki spinout path drift labels=enhancement,priority:high,cat:documentation,cat:harness
```

**File existence** (verified 2026-05-08T12:48:55Z):

```text
EXISTS scripts/analysis/provider_session_ecosystem_audit.py
EXISTS tests/analysis/test_provider_session_ecosystem_audit.py
EXISTS analysis/provider-session-ecosystem-audit.json
EXISTS docs/reports/provider-session-ecosystem-audit.md
EXISTS docs/reports/2026-05-08-provider-session-learning-transfer.md
EXISTS docs/ops/legacy-claude-reference-map.md
MISSING knowledge/wikis/engineering/wiki/index.md
MISSING knowledge/wikis/engineering/wiki/log.md
MISSING knowledge/wikis/marine-engineering/wiki/index.md
```

**Latest audit excerpt** (`docs/reports/provider-session-ecosystem-audit.md`, verified 2026-05-08T12:48:55Z):

```text
21:  - `hermes` [next_up] — prioritize legacy-path redirect cleanup and prompt/doc updates (urgency 41.4, issue: llm_wiki_spinout_path_drift; health=red; ... corpus grew faster than event-time activity)
39:  - `hermes` [act_this_week] — issue=llm_wiki_spinout_path_drift | lane=monitoring | owner=audit-operators | owner_surface=docs/reports/provider-session-ecosystem-audit.md | inspect=knowledge/wikis/engineering/wiki/index.md, knowledge/wikis/engineering/wiki/log.md, knowledge/wikis/marine-engineering/wiki/index.md | targets=llm-wiki/wikis/, llm-wiki/docs/, docs/session-handoffs/2026-05-05-llm-wiki-spinout-max-completeness-handoff.md | steps: Inspect the top matched stale paths for llm_wiki_spinout_path_drift and confirm they should redirect rather than be recreated.
545:- Status: positive_corpus_growth_beyond_recent_activity
550:- `knowledge/wikis/engineering/wiki/index.md` — 52
576:- `knowledge/wikis/engineering/wiki/index.md` (52), `knowledge/wikis/engineering/wiki/log.md` (35), `knowledge/wikis/marine-engineering/wiki/index.md` (28), ... — 225 combined reads
```

**Existing implementation/test proof** (`git grep`, verified 2026-05-08T12:48:55Z):

```text
scripts/analysis/provider_session_ecosystem_audit.py:144:        "rule_id": "llm_wiki_spinout_path_drift",
tests/analysis/test_provider_session_ecosystem_audit.py:1517:            {"path": "knowledge/wikis/engineering/wiki/index.md", "count": 6},
tests/analysis/test_provider_session_ecosystem_audit.py:1534:    assert by_rule["llm_wiki_spinout_path_drift"]["matched_paths"] == [
tests/analysis/test_provider_session_ecosystem_audit.py:1535:        {"path": "knowledge/wikis/engineering/wiki/index.md", "count": 6}
tests/analysis/test_provider_session_ecosystem_audit.py:1537:    assert "llm-wiki/wikis/" in by_rule["llm_wiki_spinout_path_drift"]["canonical_targets"]
tests/analysis/test_provider_session_ecosystem_audit.py:459:def test_build_corpus_change_summary_separates_snapshot_and_event_time_deltas(...)
```

**Occurrence inventory for the three focal stale paths** (refreshed 2026-05-08 after round-4 review; counts are planning evidence, not an implementation allowlist):

| Focal path | Total files matched by search | Important current surfaces | #2657 interpretation |
|---|---:|---|---|
| `knowledge/wikis/engineering/wiki/index.md` | 73 | `analysis/provider-session-ecosystem-audit.json`, `docs/reports/provider-session-ecosystem-audit.md`, `tests/analysis/test_provider_session_ecosystem_audit.py`, `docs/document-intelligence/README.md`, `data/document-index/intelligence-accessibility-registry.yaml`, prior plans/logs | Audit source/test/report guidance is in scope. Active current-authority docs/registry rows for existing moved assets are in scope with structured disposition markers. Prior plans/logs are evidence. |
| `knowledge/wikis/engineering/wiki/log.md` | 42 | `analysis/provider-session-ecosystem-audit.json`, `docs/reports/provider-session-ecosystem-audit.md`, `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`, prior plans/logs | Audit source/test/report guidance is in scope. Durable/transient docs and prior plans are mixed-purpose/historical surfaces; preserve under #2657. |
| `knowledge/wikis/marine-engineering/wiki/index.md` | 46 | `analysis/provider-session-ecosystem-audit.json`, `docs/reports/provider-session-ecosystem-audit.md`, `docs/document-intelligence/README.md`, `data/document-index/intelligence-accessibility-registry.yaml`, prior plans/logs | Audit source/test/report guidance is in scope. Active current-authority docs/registry rows for existing moved assets are in scope with structured disposition markers. Prior plans/logs are evidence. |

**Harness/config retrieval proof and intentional exception examples discovered by review**:

```text
config/agents/claude/memory-snapshots/* and config/agents/{codex,gemini}/state-snapshots/* are provider-session state inputs; no focal stale path edit identified in the retrieval pass.
.claude/rules/{README.md,patterns.md,coding-style.md,calc-citation-contract.md} are Claude adapter rules; no focal stale path edit identified in the retrieval pass.
```

**Intentional exception examples discovered by review**:

```text
knowledge/wikis/README.md: health-reports/ and personal/ remain in workspace-hub.
scripts/content/wiki-to-website.py: reads knowledge/wikis/* and needs separate behavior tests if changed.
scripts/data/llm-wiki/resolve_wiki_path.py: retains tested fallback behavior to knowledge/wikis.
docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md: includes normative knowledge/wikis/** architecture references.
```

**No prior canonical #2657 plan proof** (`git grep -n "2657\|llm_wiki_spinout_path_drift" -- docs/plans`, verified before creating this plan):

```text
docs/plans/2026-05-07-issue-2655-codex-nested-repo-context-drift.md:44:- Issue #2650 — open LLM-wiki post-spinout cleanup; separates `llm_wiki_spinout_path_drift` from this Codex nested-repo stream.
docs/plans/2026-05-07-issue-2655-codex-nested-repo-context-drift.md:186:- LLM-wiki spinout cleanup (`llm_wiki_spinout_path_drift`), currently separated into #2650.
```

**Baseline targeted test proof** (verified 2026-05-08T12:48:55Z):

```text
$ uv run --no-project pytest tests/analysis/test_provider_session_ecosystem_audit.py -q
.................................................                        [100%]
49 passed in 0.53s
```

**Reproduction proofs** (verify-against-repo-state, per issue-planning mode):

- N/A as a runtime-failure reproduction: #2657 does not allege a broken import, user-facing exception, or failing test. It alleges provider-session audit drift and stale path remediation. Baseline executable proof is the current passing audit test suite above; implementation must start with RED tests for the newly planned behavior.

**Distinct source count:** 12+ (issue #2657, audit report, audit JSON, transfer report, source script, test file, legacy reference map, `knowledge/wikis/README.md`, `scripts/content/wiki-to-website.py`, `scripts/data/llm-wiki/resolve_wiki_path.py`, planning template/README, adjacent #2655 plan).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-08-issue-2657-hermes-llm-wiki-spinout-path-drift.md` |
| Plan index | `docs/plans/README.md` |
| Existing implementation | `scripts/analysis/provider_session_ecosystem_audit.py` |
| Tests to harden | `tests/analysis/test_provider_session_ecosystem_audit.py` |
| Current-state generated audit JSON | `analysis/provider-session-ecosystem-audit.json` |
| Current-state generated audit markdown | `docs/reports/provider-session-ecosystem-audit.md` |
| Transfer report evidence | `docs/reports/2026-05-08-provider-session-learning-transfer.md` |
| Legacy path guidance | `docs/ops/legacy-claude-reference-map.md` |
| Read-only scope-boundary surfaces | `knowledge/wikis/README.md`, `docs/document-intelligence/**`, `data/document-index/intelligence-accessibility-registry.yaml`, `scripts/content/wiki-to-website.py`, `scripts/data/llm-wiki/**` |
| Plan review — Claude preserved per-provider artifact | `scripts/review/results/2026-05-08-plan-2657-claude-round4.md` |
| Plan review — Codex per-provider artifact / unavailable stub | `scripts/review/results/2026-05-08-plan-2657-codex.md` |
| Plan review — Gemini per-provider artifact / unavailable stub | `scripts/review/results/2026-05-08-plan-2657-gemini.md` |
| Plan review — fanout disagreement / verdict synthesis | `scripts/review/results/2026-05-08-plan-2657-disagreement.md` |

---

## Deliverable

A bounded, test-backed provider-session audit remediation that makes `llm_wiki_spinout_path_drift` unambiguous for the three Hermes focal stale reads: redirect moved engineering/marine-engineering wiki reads to `llm-wiki/*`, do not recreate missing `workspace-hub/knowledge/wikis/...` files, preserve historical/exception surfaces, and keep event-time activity distinct from corpus/snapshot growth.

Expected closure behavior: #2657 may be complete even if Hermes remains `red`/`next_up` in the generated audit because preserved provider-session logs and historical reports can continue to contain old paths. Success is **clearer rule/report guidance, active current-reference remediation for moved wiki paths, and regression tests**, not necessarily zero count or a changed provider health rank.

---

## Scope Boundaries

### In scope after user approval

- Add RED tests in `tests/analysis/test_provider_session_ecosystem_audit.py` for the #2657 sampled stale paths and for new structured rule metadata/report output that is currently absent: `forbidden_actions`, `exception_path_prefixes`, and `current_authority_scan_paths`.
- Add documentation/registry verification that active current-authority references for the moved wiki set listed in `knowledge/wikis/README.md` are redirected to `llm-wiki/*` or explicitly labeled historical.
- Preserve the existing event-time/corpus-growth regression test and add/tighten a report-output assertion only if source/report wording changes.
- Update the active docs/registry references in `docs/document-intelligence/README.md`, `data/document-index/intelligence-accessibility-registry.yaml`, and current-authority `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` lines if present so moved wiki/cross-link/seed entries point at `llm-wiki/*` current targets or are explicitly marked historical.
- Update `scripts/analysis/provider_session_ecosystem_audit.py` to add the structured rule metadata and report/playbook rendering required by the RED tests; do not satisfy the tests by appending prose only.
- Regenerate `analysis/provider-session-ecosystem-audit.json` and `docs/reports/provider-session-ecosystem-audit.md` after the structured audit-rule contract patch; commit regenerated artifacts as current snapshots with semantic diff review.
- If active mixed surfaces are discovered during implementation, record them in the issue closeout or a follow-up issue instead of changing them under #2657 unless they pass the per-surface inclusion test above.

### Out of scope / follow-up only

- Recreating `knowledge/wikis/engineering/wiki/index.md`, `knowledge/wikis/engineering/wiki/log.md`, or `knowledge/wikis/marine-engineering/wiki/index.md` under workspace-hub.
- Moving or editing actual wiki content in the separate `llm-wiki` repository.
- Broad post-spinout cleanup already tracked by #2650.
- Broadly rewriting `docs/document-intelligence/**`, `data/document-index/intelligence-accessibility-registry.yaml`, `scripts/content/wiki-to-website.py`, or `scripts/data/llm-wiki/**` under #2657. Active current-authority docs/registry lines for the moved wiki set are in scope; behavior changes and unrelated architecture rewrites remain follow-up unless a specific line is required to satisfy the #2657 stale-spinout acceptance criterion and has matching verification.
- Changing `scripts/content/wiki-to-website.py` runtime behavior or `scripts/data/llm-wiki/resolve_wiki_path.py` fallback behavior; those require separate issue scope and direct tests.
- Rewriting historical reports, logs, prior plans, review outputs, or memory snapshots solely to remove evidence of old paths.
- Changing provider-session audit ranking/urgency formulas unless RED tests reveal a direct #2657 classification bug.

---

## Pseudocode

```text
function implementation_phase_after_approval():
    moved_set = parse/encode the moved wiki set from knowledge/wikis/README.md:
        domains = [acma-projects, asset-management, engineering, engineering-standards,
                   lng-projects, marine-engineering, maritime-law, naval-architecture]
        moved_aux = [knowledge/wikis/cross-links.md, knowledge/seeds/]
        fixtures_path = tests/fixtures/llm-wiki/ is scan-only/absent-at-planning unless implementation discovers an active current-authority surface

    write RED tests for provider_session_ecosystem_audit:
        sampled stale paths map to llm_wiki_spinout_path_drift
        rule exposes structured forbidden_actions including do_not_recreate_legacy_workspace_hub_wiki_files
        rule exposes structured exception_path_prefixes for historical/evidence, retained health/personal, and compatibility/tooling contracts
        rule exposes current_authority_scan_paths derived from moved_set so docs/registry verification cannot silently cover only two domains
        generated playbook/report text is rendered from those structured fields
        event-time/corpus-growth invariant remains visible if report wording changes

    update active docs/registry current-authority references for moved_set entries
        docs/document-intelligence/README.md: scan all moved domains and moved_aux, plus fixtures_path only if active evidence appears; update current-authority references or add structured historical-reference marker
        data/document-index/intelligence-accessibility-registry.yaml: update only existing moved rows (engineering, marine-engineering, maritime-law, naval-architecture, cross-links, knowledge-seeds, and any fixtures row if present); do not fabricate missing rows for acma/asset-management/engineering-standards/lng under #2657
        docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md: inspect and update current-authority refs; preserve historical context with structured marker
        distinguish moved rows from retained wiki-personal/health-reports rows via machine-checkable disposition metadata

    update provider_session_ecosystem_audit.py only for the named structured contract and rendering fields
        do not use prose-only string append as the implementation
        do not change ranking/urgency formulas unless a failing #2657 test requires it

    run exactly: scripts/cron/provider-session-ecosystem-audit.sh
    because structured rule fields affect JSON/report serialization
    inspect JSON/markdown diff:
        allowed: llm_wiki_spinout_path_drift structured contract/guidance/targets and current snapshot counts
        disallowed: broad unrelated provider ranking/formula churn unless explained

    prove RED-first discipline by recording the failing targeted test output before implementation changes, then the passing targeted test output after implementation changes
    run targeted tests and verify named #2657 tests/assertions are present beyond the baseline 49-test suite
    record any mixed active surfaces as follow-up evidence, not as #2657 edits
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create/update | `docs/plans/2026-05-08-issue-2657-hermes-llm-wiki-spinout-path-drift.md` | canonical plan and review synthesis |
| Update | `docs/plans/README.md` | add/sync plan index row |
| Generated/review evidence | `scripts/review/results/2026-05-08-plan-2657-claude-round4.md` | preserved Claude adversarial review artifact; `claude.md` is mutable runner output and not cited as approval evidence |
| Generated/review evidence | `scripts/review/results/2026-05-08-plan-2657-codex.md` | adversarial review unavailable stub; not an implementation-phase deliverable |
| Generated/review evidence | `scripts/review/results/2026-05-08-plan-2657-gemini.md` | adversarial review unavailable stub; not an implementation-phase deliverable |
| Generated/review evidence | `scripts/review/results/2026-05-08-plan-2657-disagreement.md` | fanout verdict synthesis and review-of-record when per-provider artifacts/stubs diverge |
| Update after approval | `tests/analysis/test_provider_session_ecosystem_audit.py` | RED tests for sampled stale paths, structured rule contract fields, docs/registry moved-set verification, and any report invariant tightened by #2657 |
| Update after approval | `scripts/analysis/provider_session_ecosystem_audit.py` | add structured `llm_wiki_spinout_path_drift` contract fields/rendering needed by RED tests; avoid prose-only patch |
| Regenerate after approval | `analysis/provider-session-ecosystem-audit.json` | structured audit rule fields affect serialized current-state machine audit artifact |
| Regenerate after approval | `docs/reports/provider-session-ecosystem-audit.md` | structured audit rule fields affect rendered current-state human audit artifact |
| Update after approval | `docs/document-intelligence/README.md` | active navigation index points moved wiki/cross-link/seed assets at workspace-hub paths; update the full moved set from `knowledge/wikis/README.md` to current `llm-wiki/*` targets or explicit historical wording |
| Update after approval | `data/document-index/intelligence-accessibility-registry.yaml` | active registry marks moved wiki/cross-link/seed assets as git-tracked workspace-hub paths; update existing moved rows (`wiki-engineering`, `wiki-marine-engineering`, `wiki-maritime-law`, `wiki-naval-architecture`, `wiki-cross-links`, `knowledge-seeds`, and any `tests/fixtures/llm-wiki/` row if present); do not fabricate absent `wiki-acma-projects`, `wiki-asset-management`, `wiki-engineering-standards`, or `wiki-lng-projects` rows under #2657 |
| Update after approval | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | inspect and update active current-authority references to moved paths; preserve historical context |
| Read-only evidence / follow-up candidates | broader `docs/document-intelligence/**`, broader `data/document-index/**`, `scripts/content/wiki-to-website.py`, `scripts/data/llm-wiki/**`, `knowledge/wikis/README.md`, `config/agents/**`, `.claude/rules/**` | boundary evidence; not edited under #2657 unless separately justified by per-surface inclusion test and tests |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_llm_wiki_spinout_path_drift_covers_sampled_hermes_paths` | sampled #2657 stale paths are classified under `llm_wiki_spinout_path_drift` | fixture records for `knowledge/wikis/engineering/wiki/index.md`, `knowledge/wikis/engineering/wiki/log.md`, `knowledge/wikis/marine-engineering/wiki/index.md` | one remediation hint with all three matched paths/counts and total count equal to fixture sum |
| `test_llm_wiki_spinout_rule_exposes_forbidden_actions` | audit rule has a structured no-recreate contract, not only prose | rule metadata for `llm_wiki_spinout_path_drift` | `forbidden_actions` includes `do_not_recreate_legacy_workspace_hub_wiki_files`; current code lacks this field so the test should fail before implementation |
| `test_llm_wiki_spinout_rule_exposes_exception_prefixes` | audit rule separates actionable stale reads from preserved exceptions in structured metadata | rule metadata for `llm_wiki_spinout_path_drift` | `exception_path_prefixes` includes retained `knowledge/wikis/health-reports/`, `knowledge/wikis/personal/`, historical/evidence locations, and compatibility/tooling contracts; current code lacks this field so the test should fail before implementation |
| `test_llm_wiki_spinout_current_authority_scan_uses_full_moved_set` | docs/registry verification cannot silently cover only engineering and marine-engineering, and can distinguish retained `wiki-personal` from moved rows | moved-set fixture derived from `knowledge/wikis/README.md`; active docs/registry files; known existing registry asset keys | docs scan covers all eight domains plus `cross-links.md` and `knowledge/seeds/`; `tests/fixtures/llm-wiki/` is asserted absent or scan-only unless an active surface is found; registry scan updates only existing moved rows and asserts absent moved rows are reported as absent/follow-up, not silently skipped; retained `wiki-personal`/health paths use `retained-workspace-hub-authority` (or equivalent enum) rather than being treated as stale |
| `test_llm_wiki_spinout_historical_marker_is_machine_checkable` | "explicitly historical" cannot be satisfied by loose prose substring | Markdown/YAML examples and real edited files | remaining legacy moved paths must appear with structured marker shape (`legacy_workspace_hub_path_disposition: historical-reference` or `Disposition: historical-reference; Current authority: ...`); bare `(historical)` prose fails |
| `test_llm_wiki_spinout_report_renders_structured_contract` | generated report/playbook text is derived from structured fields and wired into output | synthetic audit output or report builder fixture | report includes redirect target, forbidden action, exception-boundary, and current-authority scan sections generated from metadata, preserving event-time/corpus-growth separation; AC explicitly requires this named test |
| Existing `test_build_corpus_change_summary_separates_snapshot_and_event_time_deltas` plus optional report assertion | event-time post records remain distinct from corpus/snapshot growth | synthetic prior/current snapshot with snapshot delta greater than event-time records | status `positive_corpus_growth_beyond_recent_activity`; event-time count remains separately reported and not treated as fresh work |

---

## Acceptance Criteria

- [ ] No implementation begins until this plan is adversarially reviewed, posted to GitHub, labeled `status:plan-review`, and user approved.
- [ ] RED tests are added before implementation for sampled Hermes stale paths and for currently-missing structured rule contract fields (`forbidden_actions`, `exception_path_prefixes`, `current_authority_scan_paths`) plus generated report rendering.
- [ ] RED-first evidence is captured in closeout: targeted #2657 tests fail before implementation changes and pass after implementation changes; `uv run --no-project pytest tests/analysis/test_provider_session_ecosystem_audit.py -q` passes with the named #2657 tests present beyond the 49-test baseline observed during planning.
- [ ] The audit rule/report guidance clearly distinguishes provider-session stale reads from historical evidence, retained workspace-hub paths (`health-reports/`, `personal/`), and compatibility/tooling contracts, and `test_llm_wiki_spinout_report_renders_structured_contract` verifies those fields are wired into rendered output.
- [ ] Active docs/registry surfaces (`docs/document-intelligence/README.md`, `data/document-index/intelligence-accessibility-registry.yaml`, and `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`) no longer present any moved-set workspace-hub paths as current authority unless they use the structured historical-reference marker; moved set is `acma-projects`, `asset-management`, `engineering`, `engineering-standards`, `lng-projects`, `marine-engineering`, `maritime-law`, `naval-architecture`, `cross-links.md`, and `knowledge/seeds/`. `tests/fixtures/llm-wiki/` is handled as scan-only/absent-at-planning evidence unless implementation discovers an active current-authority surface for it. Existing registry rows are limited to the currently present moved rows; absent moved-domain rows are reported as follow-up, not fabricated.
- [ ] The audit/report continues to expose `positive_corpus_growth_beyond_recent_activity` separately from event-time recent activity; closure must not treat corpus delta as fresh provider work.
- [ ] Missing `knowledge/wikis/...` focal files are not recreated under workspace-hub.
- [ ] No broad doc-intelligence, registry, wiki-to-website, or llm-wiki resolver behavior changes are made under #2657 beyond the known active focal references unless a specific line passes the per-surface inclusion test and has matching verification; closeout must list every line/path accepted through this escape hatch and the matching verification evidence.
- [ ] Audit outputs are regenerated after the structured rule contract patch; diffs are reviewed and confined to #2657 semantics; generated audit files are treated as replaceable current-state snapshots, while logs/prior plans/review artifacts remain historical evidence.
- [ ] Issue closeout comment includes before/after evidence for the sampled stale paths, the targeted test output, and any follow-up surfaces deferred to #2650/separate issue.
- [ ] Review artifacts are saved under `scripts/review/results/`; the plan summary cites preserved non-empty per-provider artifacts where available (`*-roundN.md` for Claude because `claude.md` is mutable runner output), verifies the cited Claude round is the highest-numbered non-empty Claude artifact at posting time, and uses `disagreement.md` only as fanout/synthesis evidence, not as a substitute for a missing provider artifact.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR | Preserved `claude-round4.md` found six residual MINOR textual/process findings after prior MAJOR blockers were addressed; this revision tightened the cited items before posting for approval. |
| Codex | UNAVAILABLE after workaround | Earlier fanout recorded Codex CLI incompatible version (`0.129.0` in known-bad range). Workaround `scripts/install/pin-codex.sh` was applied and verified `codex-cli 0.123.0`, but manual/fanout retry failed because the configured `gpt-5.5` model requires a newer Codex CLI; no usable Codex review signal. Artifact: `scripts/review/results/2026-05-08-plan-2657-codex.md`; manual retry summary: `scripts/review/results/2026-05-08-plan-2657-codex-manual.md`. |
| Gemini | UNAVAILABLE | Gemini CLI returned 429 capacity for `gemini-3.1-pro-preview`; no review signal. |

**Overall result:** preserved `claude-round4.md` returned MINOR after prior MAJOR blockers were addressed; Codex and Gemini contributed no usable review signal after documented retries/workarounds. This revision cites the preserved non-empty Claude artifact instead of the mutable `claude.md` runner path, keeps `disagreement.md` as fanout synthesis, removes absent registry rows from required updates, defines machine-checkable historical/retained disposition markers, requires RED-first evidence, pins the regeneration command to `scripts/cron/provider-session-ecosystem-audit.sh`, forces audit output regeneration, and makes report rendering of structured contract fields a named acceptance gate. Round-4 residual findings are MINOR and have been tightened in this revision; Codex/Gemini unavailability is documented as tooling/capacity evidence rather than approval signal.

Revisions made based on review:
- Rebalanced scope: no broad runtime/tooling behavior changes, but active docs/registry current-authority entries for the full moved-wiki set are explicitly in scope because #2657 acceptance forbids unqualified current stale spinout references.
- Added explicit #2657 vs #2650 decision rule and valid exception classes (`health-reports/`, `personal/`, compatibility fallbacks, historical evidence).
- Added occurrence inventory for the three focal stale paths.
- Removed untested runtime/tooling changes from planned implementation scope while retaining documentation/registry verification for the full moved-set current-authority references.
- Clarified artifact lifecycle: generated audit outputs are replaceable current-state snapshots; logs/prior plans/review artifacts are preserved evidence.
- Clarified closure objective: success is structured audit contract/tests plus active current-reference remediation for moved wiki paths, not necessarily zero stale-path count or a changed Hermes health rank.
- Added documentation + harness retrieval evidence for `docs/document-intelligence/*`, `CONTROL_PLANE_CONTRACT.md`, durable/transient boundary policy, `config/agents/**`, and `.claude/rules/**`.
- Added `scripts/review/results/2026-05-08-plan-2657-disagreement.md` as the fanout verdict-synthesis artifact and distinguished review evidence from implementation deliverables; preserved non-empty Claude evidence as `scripts/review/results/2026-05-08-plan-2657-claude-round4.md` because the runner truncates `claude.md` during reruns.
- Corrected registry scope: update only existing moved rows in `data/document-index/intelligence-accessibility-registry.yaml`; scan/report absent moved-domain rows instead of fabricating asset keys.
- Defined machine-checkable disposition markers for historical moved paths and retained workspace-hub paths so tests do not rely on loose prose.
- Replaced conditional generated-output language with mandatory regeneration after structured audit-rule fields are added, added RED-first closeout evidence as an acceptance gate, documented Codex downgrade retry failure due current Hermes model/CLI compatibility, refreshed focal-path occurrence counts (73/42/46), made `tests/fixtures/llm-wiki/` scan-only unless active evidence appears, and added closeout evidence requirements for per-surface escape-hatch and highest-round review artifact freshness.

---

## Risks and Open Questions

- **Risk:** repo-wide `knowledge/wikis/` references include many historical, generated, compatibility, valid retained, and evidence artifacts. A naive global replacement would destroy audit traceability and break intended contracts; this plan now forbids that under #2657.
- **Risk:** generated audit artifacts may shift counts/ranking due to unrelated concurrent provider-session activity. Any regenerated diff must be reviewed semantically rather than committed blindly.
- **Risk:** if reviewers or implementers expect a red-to-green audit status change, they may overreach. The intended #2657 result is clearer guidance and regression coverage; remaining historical counts can keep the provider red until logs age out or broader cleanup lands.
- **Open:** whether broader behavior/tooling cleanup beyond active current-authority docs/registry references should be filed under #2650 or split into a new governance issue after #2657 closeout evidence is collected.

---

## Complexity: T2

**T2** — bounded harness/docs remediation with existing implementation and tests, plus nontrivial governance boundaries around generated artifacts, historical evidence, retained workspace-hub wiki paths, and broader #2650 cleanup separation.
