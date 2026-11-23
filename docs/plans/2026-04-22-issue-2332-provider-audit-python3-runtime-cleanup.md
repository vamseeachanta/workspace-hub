# Plan for #2332: Provider-audit python3 runtime cleanup

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2332

---

## Resource Intelligence Summary

### Existing repo code and artifacts
- `scripts/analysis/provider_session_ecosystem_audit.py` and `tests/analysis/test_provider_session_ecosystem_audit.py` are the existing audit/reporting implementation surface for python-runtime telemetry.
- `analysis/provider-session-ecosystem-audit.json` is the numeric source artifact for current provider baselines: Claude `744`, Codex `337`, Hermes `2059`, Gemini `291` bare `python3` calls.
- `docs/reports/provider-session-ecosystem-audit.md` is generated from the audit script and must be regenerated, not edited manually.
- `scripts/ai/provider-routing-scorecard.py`, `config/ai-tools/provider-routing-scorecard.json`, and `docs/reports/provider-routing-scorecard.md` are the weekly publication surfaces that this issue extends.
- First-wave launcher targets are exactly:
  - `scripts/ai/generate-agent-radar.py`
  - `scripts/coordination/git/git_sync_all_enhanced.py`
  - `scripts/automation/sync_and_propagate_commands.py`
- `scripts/ai/generate-agent-radar.py` already documents `uv run --no-project python ...` in its usage header and is a standalone `# /// script`.
- `scripts/coordination/git/git_sync_all_enhanced.py` and `scripts/automation/sync_and_propagate_commands.py` use stdlib-only imports and launch external setup/utility scripts rather than project-package entry points.
- `src/ace/router.py` contains the interpreter-discovery/path-probing exception class this plan explicitly excludes from actionable debt.

### Standards
| Standard | Status | Source |
|---|---|---|
| Workspace runtime policy: `uv run` always — never bare `python3` | applicable | `AGENTS.md` line 14 |
| Weekly ecosystem review is the canonical publication surface for provider telemetry | applicable | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` |
| Generated reports should be refreshed by the owning script, not hand-edited | applicable | current `provider_session_ecosystem_audit.py` + existing generated artifacts |
| Broad cross-platform shell portability sweep exists already | applicable sibling scope | Issue `#48` |

### LLM Wiki pages consulted
- No relevant wiki pages. This is repo-policy and telemetry work, not domain-knowledge work.

### Documents consulted
- Issue `#2332` — requires audit-driven hotspot inventory, explicit allowlist policy, provider-level budgets, repo patches for worst offenders, and weekly-review integration or a standalone scorecard with trend deltas.
- `analysis/provider-session-ecosystem-audit.json` — freshest attested numeric baseline and recent-window evidence for provider runtime debt.
- `docs/reports/provider-session-ecosystem-audit.md` — confirms the existing public report shape and highlights the current JSON/markdown divergence that this plan must close by regeneration.
- `docs/reports/2026-04-22-provider-session-learning-transfer.md` — supports Hermes as an active orchestration surface with recent `python3` pressure, but does not supersede JSON/report provider rankings; the plan should use it only as prioritization context, not as sole numeric evidence.
- `config/ai-tools/provider-routing-scorecard.json` and `docs/reports/provider-routing-scorecard.md` — demonstrate an existing weekly scorecard publication surface that can absorb explicit per-provider python-runtime budgets and trend deltas.
- Issue `#48` (`WRK-1118`) — owns the broad repo-wide bash portability sweep across `scripts/` and hooks; this issue must stay narrower and audit-driven.

### Explicit allowlist / exception policy for this plan
Actionable bare-`python3` debt for `#2332` means repo-local shell/runtime invocations that choose `python3` where `uv run ... python` or another approved wrapper should be used.

Allowed exceptions in-scope for reporting but excluded from remediation debt:
1. Interpreter-discovery or path-probing code that inspects external repo environments without executing workspace-hub code through bare `python3`.
   - Example evidence: `src/ace/router.py` checking `.venv/bin/python3`.
2. Pre-`uv` bootstrap or system-tooling contexts where `uv` is unavailable by definition and the code is preparing the environment rather than running repo logic.
   - Any such case must be called out explicitly in code comments or fixture names when retained.
3. Text-only mentions that are not executable runtime choices: shebangs, docs/examples, historical artifacts, and raw log fixtures.

Everything else is a violation for this issue, including:
- `subprocess.run(["python3", ...])` inside workspace-hub tooling
- bash snippets in generated reports, docs, or workflow instructions that direct agents to run `python3` for workspace-hub tasks
- provider-audit/accountability surfaces that count debt without publishing the allowlist rationale

### Gaps identified
- The numeric source-of-truth contract must remain explicit so generated markdown cannot drift from the underlying audit JSON.
- The runtime exception policy and provider budget schema must be machine-checkable in the canonical scorecard JSON artifact.
- The first remediation wave must stay bounded to named repo-local launcher/orchestration files plus audit/scorecard publication surfaces.
- Weekly scorecard publication must include Hermes and explicit python-runtime budget/trend fields.
- Scope must remain non-overlapping with Issue `#48`.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2332-provider-audit-python3-runtime-cleanup.md` |
| Audit JSON source of truth | `analysis/provider-session-ecosystem-audit.json` |
| Audit engine | `scripts/analysis/provider_session_ecosystem_audit.py` |
| Audit tests | `tests/analysis/test_provider_session_ecosystem_audit.py` |
| Weekly/runtime scorecard generator | `scripts/ai/provider-routing-scorecard.py` |
| Weekly/runtime scorecard JSON | `config/ai-tools/provider-routing-scorecard.json` |
| Weekly/runtime scorecard markdown | `docs/reports/provider-routing-scorecard.md` |
| Weekly review publication doc | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` |
| Runtime policy reference | `AGENTS.md` |
| First-wave launcher hotspots | `scripts/ai/generate-agent-radar.py`, `scripts/coordination/git/git_sync_all_enhanced.py`, `scripts/automation/sync_and_propagate_commands.py` |

---

## Deliverable

A bounded implementation plan for `#2332` that (1) defines the runtime exception policy, (2) publishes explicit per-provider python-runtime budgets/trend outputs through the existing audit/scorecard path, and (3) constrains the first remediation wave to named workspace-hub orchestration/launcher files rather than a repo-wide python3 sweep.

---

## Scope boundary versus Issue #48

`#2332` owns:
- provider-audit reporting changes
- explicit allowlist/exception policy for bare-`python3` telemetry
- per-provider budgets and trend-delta publication in audit/scorecard artifacts
- first-wave remediation only for the named provider-audit / AI-orchestration launcher files listed in this plan
- workflow/docs updates that point agents to the canonical runtime choices for those surfaces

`#48` owns:
- the broad repo-wide cross-platform shell sweep across `scripts/` and `.claude/hooks/`
- generic shell portability replacement of `python3`, `bc`, and `nproc` outside the named `#2332` surfaces
- setup/maintenance/bash-script cleanup not driven by provider-session audit evidence

Non-overlap rule:
- If a bare-`python3` site is outside the named `#2332` first-wave files and outside the audit/scorecard/publication surfaces, it is tracked as context for `#48`, not remediated under this issue.

---

### Prior-audit delta contract

Authoritative prior-audit source for this issue:
- before writing any regenerated output, `scripts/analysis/provider_session_ecosystem_audit.py` must load the current checked-in `analysis/provider-session-ecosystem-audit.json` snapshot into memory as the `previous_audit_snapshot`
- delta computation uses that in-memory snapshot; only after deltas are computed and the new payload is complete may the script overwrite `analysis/provider-session-ecosystem-audit.json`
- if regeneration fails before the new payload is written successfully, the checked-in prior snapshot remains untouched and no partial overwrite is accepted
- the scorecard consumes deltas from the regenerated audit output rather than inventing a second historical store

No-history / first-run behavior:
- if a prior audit file is absent, publish `delta_status = no_prior_audit`
- if a prior audit file exists but cannot be parsed, publish `delta_status = prior_snapshot_unreadable`
- if a prior audit file exists but the provider row is missing, publish `delta_status = provider_missing_from_prior_snapshot`
- for every non-baseline branch (`no_prior_audit`, `prior_snapshot_unreadable`, `provider_missing_from_prior_snapshot`):
  - set `python3_delta_count = null`
  - set `python3_baseline_count = null`
  - keep `python3_cap_count` fixed to the published phase-1 provider cap from the table below
  - emit `python3_compliance_status = no_prior_audit`
- required `python3_compliance_reason` text by branch:
  - `no_prior_audit` => `prior audit snapshot absent; fixed phase-1 cap published without delta`
  - `prior_snapshot_unreadable` => `prior audit snapshot unreadable; fixed phase-1 cap published without delta`
  - `provider_missing_from_prior_snapshot` => `provider missing from prior audit snapshot; fixed phase-1 cap published without delta`
- markdown/publication output must render the exact `delta_status` and `python3_compliance_reason` for non-baseline branches; do not collapse them into generic `baseline only` wording
- tests for this issue must assert the normal delta path plus all three non-baseline branches.

Canonical weekly publication surface for phase 1:
- `config/ai-tools/provider-routing-scorecard.json` is the single canonical machine-checkable schema artifact for the runtime-budget contract in this issue.
- The top-level JSON shape is a provider-keyed object under `recommendations_by_provider`, with keys exactly `claude`, `codex`, `hermes`, and `gemini`.
- `docs/reports/provider-routing-scorecard.md` is the human-readable rendering derived from that JSON.
- `analysis/provider-session-ecosystem-audit.json` remains the numeric telemetry source of truth that feeds the scorecard, but it is not the schema contract artifact for budget publication.
- no separate runtime scorecard file is introduced in `#2332`.

## Provider budget contract for phase 1

Numeric source of truth: `analysis/provider-session-ecosystem-audit.json`.
Canonical machine-checkable publication contract: `config/ai-tools/provider-routing-scorecard.json`.
Human-readable publication surface: `docs/reports/provider-routing-scorecard.md`.

Required per-provider compliance fields to emit in `config/ai-tools/provider-routing-scorecard.json` under `recommendations_by_provider.<provider>`:
- `python3_baseline_count` (`integer | null`)
- `python3_current_count` (`integer`)
- `python3_delta_count` (`integer | null`)
- `delta_status` (`baseline_available | no_prior_audit | prior_snapshot_unreadable | provider_missing_from_prior_snapshot`)
- `python3_cap_count` (`integer | null`)
- `python3_compliance_status` (`within_cap | over_cap | no_prior_audit`)
- `python3_compliance_reason` (`string`)
- Hermes-only additional fields for phase 1:
  - `recent_since_previous_audit_python3_count` (`integer` on `hermes`, `null` on non-Hermes providers)
  - `recent_since_previous_audit_uv_run_count` (`integer` on `hermes`, `null` on non-Hermes providers)
  - `last_7d_python3_count` (`integer` on `hermes`, `null` on non-Hermes providers)
  - `last_7d_uv_run_count` (`integer` on `hermes`, `null` on non-Hermes providers)

| Provider | Current baseline | Phase-1 hard cap to publish | Extra phase-1 trend field |
|---|---|---|---|
| Claude | `744` bare `python3`; `8.88` per 1k | `python3_cap_count = 744` until a named Claude-owned hotspot is explicitly added to scope | delta vs previous checked-in audit snapshot |
| Codex | `337` bare `python3`; `18.89` per 1k | `python3_cap_count = 337` until a named Codex-owned hotspot is explicitly added to scope | delta vs previous checked-in audit snapshot |
| Hermes | `2059` bare `python3`; `17.93` per 1k | `python3_cap_count = 2059`; publish both overall and recent-window compliance because Hermes is an active orchestration surface | `since_previous_audit` `python3` vs `uv run` and `last_7d` `python3` vs `uv run` |
| Gemini | `291` bare `python3`; `47.34` per 1k | `python3_cap_count = 291`; `python3_compliance_status` must remain `over_cap`/flagged red if current count rises above baseline | delta vs previous checked-in audit snapshot |

Policy rule for phase 1:
- if a prior snapshot exists and the provider row exists, emit `delta_status = baseline_available`
- if a prior audit file is absent, emit `delta_status = no_prior_audit`
- if a prior audit file exists but cannot be parsed, emit `delta_status = prior_snapshot_unreadable`
- if a prior audit file exists but the provider row is missing, emit `delta_status = provider_missing_from_prior_snapshot`
- if `delta_status = baseline_available` and `python3_current_count <= python3_cap_count`, emit `python3_compliance_status = within_cap`
- if `delta_status = baseline_available` and `python3_current_count > python3_cap_count`, emit `python3_compliance_status = over_cap`
- if `delta_status` is `no_prior_audit`, `prior_snapshot_unreadable`, or `provider_missing_from_prior_snapshot`, emit `python3_compliance_status = no_prior_audit`

Phase-1 meaning:
- This issue’s first merge must make the budgets machine-checkable and visible.
- Only the named first-wave files are expected to reduce debt immediately.
- Future tighter burn-down targets can be lowered in follow-on work once the scorecard is publishing stable deltas.

---

## Pseudocode

```text
load the current checked-in provider-session audit JSON into memory as previous_audit_snapshot before any overwrite
extract per-provider overall python3 counts, uv-python counts, and recent-window slices from the regenerated payload
apply explicit exception taxonomy:
    ignore text-only mentions and fixture/shebang cases
    ignore interpreter-path discovery for external environments
    flag repo-local shell/subprocess python3 invocations as actionable debt
publish a runtime compliance section in the audit/scorecard output that includes:
    python3_baseline_count
    python3_current_count
    python3_delta_count
    python3_cap_count
    python3_compliance_status
    python3_compliance_reason
    Hermes recent-window runtime counts
patch only the named first-wave launcher/orchestration files to canonical uv forms
regenerate markdown/json scorecard and audit artifacts through their owning scripts
assert tests for exception handling, machine-checkable budget status, deterministic hotspot scope, and file-level no-regression on the named remediation set
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/analysis/provider_session_ecosystem_audit.py` | add explicit runtime-policy section/fields for allowlisted vs actionable debt, provider budgets, and recent-window runtime deltas |
| Modify | `tests/analysis/test_provider_session_ecosystem_audit.py` | make budget rendering, exception policy, recent-vs-corpus split, and hotspot scoping falsifiable |
| Modify | `scripts/ai/provider-routing-scorecard.py` | publish explicit python-runtime budgets/deltas, include Hermes in the scorecard, and make the weekly output a real tracking surface for `#2332` |
| Regenerate | `config/ai-tools/provider-routing-scorecard.json` | checked-in budget/trend artifact produced by the scorecard script |
| Regenerate | `docs/reports/provider-routing-scorecard.md` | human-readable budget/trend publication surface produced by the scorecard script |
| Modify | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | wire the runtime-budget publication/check into the weekly review procedure |
| Modify | `AGENTS.md` | add one concise pointer sentence from the general `uv run` rule to the explicit exception-policy/reporting contract defined by the audit/scorecard outputs |
| Modify | `scripts/ai/generate-agent-radar.py` | replace the direct bare-`python3` launcher with canonical `uv run --no-project python ...` |
| Modify | `scripts/coordination/git/git_sync_all_enhanced.py` | replace the direct bare-`python3` launcher with canonical `uv run --no-project python ...` |
| Modify | `scripts/automation/sync_and_propagate_commands.py` | replace the direct bare-`python3` launcher with canonical `uv run --no-project python ...` |
| Regenerate | `analysis/provider-session-ecosystem-audit.json` and `docs/reports/provider-session-ecosystem-audit.md` | rerun the audit after implementation so JSON and markdown agree on published runtime metrics |

---

## First remediation wave

This plan does not approve a repo-wide python3 rewrite. Phase 1 is bounded to the following named surfaces only:

1. Audit/reporting/accountability surfaces
   - `scripts/analysis/provider_session_ecosystem_audit.py`
   - `tests/analysis/test_provider_session_ecosystem_audit.py`
   - `scripts/ai/provider-routing-scorecard.py`
   - `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
   - regenerated scorecard/audit artifacts
2. Repo-local launcher/orchestration hotspots with direct bare-`python3` subprocess calls
   - `scripts/ai/generate-agent-radar.py`
   - `scripts/coordination/git/git_sync_all_enhanced.py`
   - `scripts/automation/sync_and_propagate_commands.py`

Any broader sweep through setup, maintenance, hooks, or unrelated bash scripts is deferred to `#48` unless a later re-plan explicitly expands scope.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_runtime_policy_budget_section_uses_audit_json_baselines` | the runtime budget section renders from attested provider metrics, not hard-coded prose guesses | synthetic audit payload with Claude/Codex/Hermes/Gemini `python3_bash_calls`, `python3_per_1k_records`, and previous-audit deltas | rendered output contains each provider baseline and delta exactly as supplied |
| `test_runtime_policy_exception_policy_excludes_interpreter_path_discovery` | allowlisted interpreter-path probes are not counted as actionable runtime debt | fixture including a `src/ace/router.py`-style `.venv/bin/python3` path probe plus one repo-local `subprocess.run(["python3", ...])` call | probe classified as allowlisted/non-actionable; subprocess launcher classified as actionable |
| `test_runtime_policy_recent_and_corpus_views_are_both_published_for_hermes` | Hermes output shows both overall debt and recent-window counts because recent orchestration activity matters | synthetic Hermes payload with overall counts plus `since_previous_audit` and `last_7d` bash families | runtime section contains overall baseline plus both recent-window fields |
| `test_provider_routing_scorecard_includes_hermes_runtime_budget_row` | weekly scorecard covers all four providers and publishes python-runtime budgets/deltas | sample utilization JSON plus audit JSON including Hermes | generated JSON/markdown scorecard contains a Hermes entry with budget cap and delta fields |
| `test_first_wave_launcher_files_have_no_direct_python3_subprocess_calls` | named phase-1 launcher files are clean after remediation | run the audit runtime-debt matcher against only `scripts/ai/generate-agent-radar.py`, `scripts/coordination/git/git_sync_all_enhanced.py`, and `scripts/automation/sync_and_propagate_commands.py` | the audit matcher reports zero actionable bare-`python3` findings for the three named files |
| `test_first_wave_launcher_files_still_execute_with_uv_no_project_contract` | the chosen runtime replacement preserves launcher behavior for the bounded first wave | exact non-destructive command-path checks:
  1. `uv run --no-project python scripts/ai/generate-agent-radar.py --output /tmp/agent-radar-test.html`
  2. monkeypatch `subprocess.run` inside `EnhancedGitSyncAll.sync_slash_commands()`, execute that method with a temporary `sync_script` path, and assert the captured argv equals `['uv', 'run', '--no-project', 'python', str(sync_script)]` with the original `cwd=self.base_path`, `capture_output=True`, and `text=True` kwargs preserved exactly
  3. monkeypatch `subprocess.run` inside `sync_and_propagate_repo()`, execute that function with a temporary repo path + `source_setup`, and assert the captured argv equals `['uv', 'run', '--no-project', 'python', str(source_setup)]` with the original `cwd=repo_path` and `capture_output=True` kwargs preserved exactly
| expected outputs:
  1. exits 0 and writes the requested HTML file
  2. the real `sync_slash_commands()` path reaches the launcher call site and preserves the full subprocess contract except for the interpreter wrapper swap
  3. the real `sync_and_propagate_repo()` path reaches the launcher call site and preserves the full subprocess contract except for the interpreter wrapper swap |
| `test_runtime_budget_non_baseline_markdown_renders_exact_branch_reason` | non-baseline publication output stays branch-specific rather than collapsing to generic wording | synthetic markdown/render payloads for `no_prior_audit`, `prior_snapshot_unreadable`, and `provider_missing_from_prior_snapshot` | markdown contains the exact `delta_status` and matching `python3_compliance_reason` text for each branch |
| `test_regenerated_audit_markdown_matches_json_runtime_totals_and_recent_fields` | published markdown is regenerated from the same runtime totals and recent-window fields as the JSON source | regenerated audit JSON and markdown from the same test fixture/run | markdown provider totals plus Hermes runtime section agree with JSON counts and recent-window fields for all providers |
| `test_runtime_budget_delta_fields_handle_non_baseline_states` | non-baseline branches are explicit rather than silently fabricated | synthetic provider payloads covering missing prior file, unreadable prior file, and provider missing from prior snapshot | scorecard/audit publish the declared `delta_status` value, `python3_delta_count = null`, seeded `python3_baseline_count` and `python3_cap_count`, `python3_compliance_status = no_prior_audit`, and the exact branch-specific `python3_compliance_reason` text |
| `test_runtime_budget_flags_provider_over_cap_when_count_regresses_above_baseline` | published hard-cap policy is actually enforced, not just printed | prior snapshot baseline plus current snapshot above baseline for one provider | generated audit/scorecard marks that provider as over budget / non-compliant according to the phase-1 cap rules |
| `test_runtime_budget_schema_fields_exist_for_every_provider` | machine-checkable compliance schema is complete for every provider row | regenerated audit/scorecard payload with Claude/Codex/Hermes/Gemini rows | every provider row under `recommendations_by_provider.<provider>` emits `python3_baseline_count`, `python3_current_count`, `python3_delta_count`, `delta_status`, `python3_cap_count`, `python3_compliance_status`, and `python3_compliance_reason`; Hermes-only keys exist on every row and are `integer` on `hermes` and `null` on non-Hermes providers |

---

## Acceptance Criteria

- [ ] The plan itself defines the allowlist/exception policy and distinguishes allowlisted cases from actionable runtime debt.
- [ ] The plan names the first-wave remediation files explicitly and limits implementation to those surfaces plus audit/scorecard publication code.
- [ ] The plan states a clear non-overlap boundary with Issue `#48`.
- [ ] Provider runtime budgets are explicit for Claude, Codex, Hermes, and Gemini, with `analysis/provider-session-ecosystem-audit.json` identified as the numeric source of truth.
- [ ] Weekly-review integration is concrete: the implementation updates `scripts/ai/provider-routing-scorecard.py`, regenerates its JSON/markdown outputs, and documents the check in `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`.
- [ ] Tests are concrete and falsifiable, including named exception fixtures, Hermes recent-window publication, named first-wave file scans, runtime smoke preservation for the `uv run --no-project python` contract, JSON/markdown regeneration consistency, and no-prior-audit delta behavior.

---

## Risks and Open Questions

- **Risk:** `docs/reports/provider-session-ecosystem-audit.md` currently diverges from `analysis/provider-session-ecosystem-audit.json`; implementation must regenerate both from code in one pass or the review problem will recur.
- **Risk:** Some historical bare-`python3` counts come from past sessions and external repos, so phase-1 budgets should be treated as publication/accountability gates first, not as proof that all ecosystem debt can be removed in one PR.
- **Risk:** Touching launcher/orchestration files outside the named first wave would blur into Issue `#48` and should be avoided without explicit scope expansion.
- **Open:** None blocking approval readiness. The canonical publication artifact, first-run schema behavior, and bounded launcher contract are fully specified in the plan above.

---

## Complexity: T2

**T2** — bounded multi-file policy/reporting/test cleanup plus three named launcher-file remediations; no repo-wide shell sweep or architecture redesign is included.