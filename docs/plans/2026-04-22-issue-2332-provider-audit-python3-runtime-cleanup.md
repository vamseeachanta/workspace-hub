# Plan for #2332: Provider-audit python3 runtime cleanup

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2332
> **Review artifacts:** `scripts/review/results/2026-04-22-plan-2332-codex.md`, `scripts/review/results/2026-04-22-plan-2332-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code and artifacts
- Found: `scripts/analysis/provider_session_ecosystem_audit.py` plus `tests/analysis/test_provider_session_ecosystem_audit.py` already compute and test provider-level `python3_bash_calls`, `uv_python_bash_calls`, recent-activity slices, rolling-window summaries, and python-hygiene status fields. This issue should extend that existing audit/reporting path instead of inventing a second telemetry source.
- Found: `analysis/provider-session-ecosystem-audit.json` is the freshest numeric source in-repo (`generated_at: 2026-04-22T00:19:59Z`). Current provider baselines in that artifact are: Claude `744` bare `python3` vs `5989` `uv ... python`; Codex `337` vs `421`; Hermes `2059` vs `2045`; Gemini `291` vs `39`.
- Found: the same JSON already separates recent-event-time views from corpus totals. For Hermes, the recent slices still show live runtime pressure: `recent_activity_since_previous_audit` top Bash families include `python3` `33` vs `uv run` `5`, and the `last_7d` window shows `python3` `512` vs `uv run` `679`.
- Found: `docs/reports/provider-session-ecosystem-audit.md` is a generated markdown companion but currently diverges from the JSON on Hermes totals and recent-family detail. Approval-stage planning should therefore treat the JSON plus generator code as the numeric source of truth and require regeneration of markdown/report artifacts through the script, not manual edits.
- Found: `scripts/ai/provider-routing-scorecard.py`, `config/ai-tools/provider-routing-scorecard.json`, and `docs/reports/provider-routing-scorecard.md` already publish weekly provider telemetry, but the script currently targets only `claude`, `codex`, and `gemini` and does not publish explicit python-runtime budgets or deltas for Hermes.
- Found repo-local actionable launcher hot spots with direct bare-`python3` subprocess usage in tracked code:
  - `scripts/ai/generate-agent-radar.py` line 42
  - `scripts/coordination/git/git_sync_all_enhanced.py` line 38
  - `scripts/automation/sync_and_propagate_commands.py` line 148
- Found an existing legitimate interpreter-discovery edge case in `src/ace/router.py` lines 86-99: it probes `.venv/bin/python` and `.venv/bin/python3` as file paths while resolving external repo interpreters. That is evidence for an explicit exception category distinct from repo-local shell/runtime invocation debt.

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
- The plan previously mixed unsupported markdown-report numbers with fresher JSON numbers; the numeric source-of-truth contract must be explicit.
- No explicit runtime exception policy was written in-plan even though the issue and reviews require one.
- No approval-ready first-wave file list previously bounded repo-local remediation.
- Existing weekly scorecard publication excludes Hermes and does not publish python-runtime budgets/trend deltas.
- Scope boundary versus Issue `#48` was not previously explicit enough to prevent duplicate repo-wide shell-sweep work.

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

Non-overlap rule for approval:
- If a bare-`python3` site is outside the named `#2332` first-wave files and outside the audit/scorecard/publication surfaces, it is tracked as context for `#48`, not remediated under this issue.

---

### Prior-audit delta contract

Authoritative prior-audit source for this issue:
- the previous checked-in `analysis/provider-session-ecosystem-audit.json` snapshot loaded by `scripts/analysis/provider_session_ecosystem_audit.py`
- the scorecard consumes deltas from that regenerated audit output rather than inventing a second historical store

No-history / first-run behavior:
- if no previous audit snapshot exists for a provider, publish `delta_status: no_prior_audit`, set numeric delta fields to `null`, and render `baseline only` rather than fabricating a zero change.
- tests for this issue must assert both the normal delta path and the no-prior-audit path.

Canonical weekly publication surface for phase 1:
- `scripts/ai/provider-routing-scorecard.py` plus its generated JSON/markdown outputs remain the canonical weekly runtime-budget artifact for this issue.
- no separate runtime scorecard file is introduced in `#2332`.

## Provider budget contract for phase 1

Source of truth: `analysis/provider-session-ecosystem-audit.json` for counts/rates, published via regenerated scorecard/report artifacts.

| Provider | Current baseline | Phase-1 hard cap to publish | Extra phase-1 trend field |
|---|---|---|---|
| Claude | `744` bare `python3`; `8.88` per 1k | no regression above baseline until a named Claude-owned hotspot is in scope | week-over-week delta vs prior audit |
| Codex | `337` bare `python3`; `18.89` per 1k | no regression above baseline until a named Codex-owned hotspot is in scope | week-over-week delta vs prior audit |
| Hermes | `2059` bare `python3`; `17.93` per 1k | no regression above baseline; publish both overall and recent-window counts because Hermes is an active orchestration surface | `since_previous_audit` `python3` vs `uv run` and `last_7d` `python3` vs `uv run` |
| Gemini | `291` bare `python3`; `47.34` per 1k | no regression above baseline; remains the worst density and should be flagged red until improved | week-over-week delta vs prior audit |

Phase-1 meaning:
- This issue’s first merge must make the budgets visible and testable.
- Only the named first-wave files are expected to reduce debt immediately.
- Future tighter burn-down targets can be lowered in follow-on work once the scorecard is publishing stable deltas.

---

## Pseudocode

```text
load provider-session audit JSON as numeric source of truth
extract per-provider overall python3 counts, uv-python counts, and recent-window slices
apply explicit exception taxonomy:
    ignore text-only mentions and fixture/shebang cases
    ignore interpreter-path discovery for external environments
    flag repo-local shell/subprocess python3 invocations as actionable debt
publish a runtime compliance section in the audit/scorecard output that includes:
    baseline budget per provider
    current count/rate per provider
    delta versus previous audit
    Hermes recent-window runtime counts
patch only the named first-wave launcher/orchestration files to canonical uv forms
regenerate markdown/json scorecard and audit artifacts through their owning scripts
assert tests for exception handling, budget rendering, deterministic hotspot scope, and file-level no-regression on the named remediation set
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
| `test_regenerated_audit_markdown_matches_json_runtime_totals_and_recent_fields` | published markdown is regenerated from the same runtime totals and recent-window fields as the JSON source | regenerated audit JSON and markdown from the same test fixture/run | markdown provider totals plus Hermes runtime section agree with JSON counts and recent-window fields for all providers |
| `test_runtime_budget_delta_fields_handle_no_prior_audit` | first-run/no-history behavior is explicit rather than silently fabricated | synthetic provider payload without previous audit snapshot | scorecard/audit publish `delta_status: no_prior_audit`, `null` delta fields, and `baseline only` wording |

---

## Acceptance Criteria

- [ ] The plan itself defines the allowlist/exception policy and distinguishes allowlisted cases from actionable runtime debt.
- [ ] The plan names the first-wave remediation files explicitly and limits implementation to those surfaces plus audit/scorecard publication code.
- [ ] The plan states a clear non-overlap boundary with Issue `#48`.
- [ ] Provider runtime budgets are explicit for Claude, Codex, Hermes, and Gemini, with `analysis/provider-session-ecosystem-audit.json` identified as the numeric source of truth.
- [ ] Weekly-review integration is concrete: the implementation updates `scripts/ai/provider-routing-scorecard.py`, regenerates its JSON/markdown outputs, and documents the check in `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`.
- [ ] Tests are concrete and falsifiable, including named exception fixtures, Hermes recent-window publication, named first-wave file scans, JSON/markdown regeneration consistency, and no-prior-audit delta behavior.
- [ ] After fresh external re-review, the plan can advance toward `status:plan-review`; remaining in `draft` is not itself a success criterion.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | not yet re-run on the revised draft |
| Codex | MAJOR | unsupported audit claims, unnamed remediation files, missing scope boundary with `#48`, missing budget/weekly-review contract, vague tests |
| Gemini | MAJOR | first-wave files unnamed, allowlist policy missing from the plan itself, generated-report workflow unclear, tests not falsifiable |

**Overall result:** REVISED DRAFT — major findings addressed in-plan; fresh review still required before approval.

Revisions made based on review:
- replaced unsupported runtime claims with current repo-evidenced JSON/report findings
- wrote the allowlist/exception policy directly into the plan
- named the first-wave launcher hotspots and bounded the remediation surface
- added an explicit boundary versus Issue `#48`
- added explicit provider budget publication requirements and tied them to existing scorecard artifacts
- rewrote the TDD table so each test has a concrete fixture/scope/pass condition
- removed speculative file targets like "AGENTS.md or adjacent doc" and "hotspots discovered later"

---

## Risks and Open Questions

- **Risk:** `docs/reports/provider-session-ecosystem-audit.md` currently diverges from `analysis/provider-session-ecosystem-audit.json`; implementation must regenerate both from code in one pass or the review problem will recur.
- **Risk:** Some historical bare-`python3` counts come from past sessions and external repos, so phase-1 budgets should be treated as publication/accountability gates first, not as proof that all ecosystem debt can be removed in one PR.
- **Risk:** Touching launcher/orchestration files outside the named first wave would blur into Issue `#48` and should be avoided without explicit scope expansion.
- **Open:** None blocking approval readiness. This redraft fixes the prior conditional file-target and weekly-artifact ambiguity by selecting the existing routing scorecard as the canonical phase-1 publication surface and by requiring a concise `AGENTS.md` pointer update.

---

## Complexity: T2

**T2** — bounded multi-file policy/reporting/test cleanup plus three named launcher-file remediations; no repo-wide shell sweep or architecture redesign is included.