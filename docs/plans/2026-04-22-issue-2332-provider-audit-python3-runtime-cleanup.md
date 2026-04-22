# Plan for #2332: Provider-audit python3 runtime cleanup

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2332
> **Review artifacts:** pending adversarial review

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/analysis/provider_session_ecosystem_audit.py` — already computes provider-level `python3_bash_calls`, `uv_python_bash_calls`, recent command-family summaries, and rolling-window activity needed to turn this issue into an evidence-driven cleanup plan.
- Found: `tests/analysis/test_provider_session_ecosystem_audit.py` — existing audit coverage is the natural place to lock in any new runtime-policy reporting fields, exception handling, or provider-specific command-family assertions.
- Found: `docs/reports/provider-session-ecosystem-audit.md` — the refreshed audit now exposes both full-corpus runtime debt and recent-event-time command-family slices, which allows cleanup to target current high-leverage behavior instead of only historical totals.
- Gap: there is no issue-specific hotspot inventory or allowlist contract yet distinguishing acceptable bare `python3` use from repo-policy violations.
- Gap: no plan artifact exists yet for `#2332`, so the issue has evidence but no executable draft for plan review.

### Standards
| Standard | Status | Source |
|---|---|---|
| Workspace policy: `uv run` always — never bare `python3` | applicable | `AGENTS.md` |
| Not an external engineering standard issue | n/a | runtime/governance cleanup |

### LLM Wiki pages consulted
- No relevant wiki pages — issue scope is provider-audit/runtime-governance behavior, not domain knowledge.

### Documents consulted
- Issue #2332 — defines the cross-provider bare-`python3` debt and the need for canonical `uv run ... python` replacements plus explicit exceptions.
- `docs/reports/provider-session-ecosystem-audit.md` — refreshed 2026-04-22 audit shows Hermes overall at `2059` bare `python3` vs `2045` `uv run ... python`, Gemini overall at `291` vs `39`, and recent Hermes command families at `python3` 33 vs `uv run` 5.
- `docs/reports/2026-04-22-provider-session-learning-transfer.md` — clarifies that Hermes is the highest-leverage runtime-policy surface because its recent session mix is orchestration-heavy and cross-provider in nature.
- `AGENTS.md` — states the repo runtime rule directly: `uv run` always, never bare `python3`.
- Issue #48 — broad cross-platform bash sweep already tracks repo-wide shell portability cleanup, so this plan should complement rather than duplicate it.

### Gaps identified
- No current exception taxonomy defines when bare `python3` is acceptable for system tooling or non-repo execution.
- No ranked repo-local hotspot list yet converts the audit metrics into a bounded first cleanup wave.
- No acceptance criteria yet separate event-time improvement from corpus/backfill effects, which matters because provider-audit snapshots can grow without proportional recent activity.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2332-provider-audit-python3-runtime-cleanup.md` |
| Audit engine | `scripts/analysis/provider_session_ecosystem_audit.py` |
| Audit tests | `tests/analysis/test_provider_session_ecosystem_audit.py` |
| Audit wrapper tests | `tests/cron/test_provider_session_ecosystem_audit_wrapper.py` |
| Runtime policy reference | `AGENTS.md` |
| Learning-transfer note | `docs/reports/2026-04-22-provider-session-learning-transfer.md` |
| Refreshed audit report | `docs/reports/provider-session-ecosystem-audit.md` |

---

## Deliverable

A bounded runtime-policy cleanup plan that turns provider-audit `python3` debt into a ranked hotspot inventory, an explicit exception policy, measurable reporting changes, and a first repo-local remediation wave.

---

## Pseudocode

```text
read current provider audit totals and recent command-family slices
separate providers with real recent event-time runtime debt from providers showing mostly historical/backfilled debt
build a hotspot table of repo-local bare-python3 command families
classify each hotspot as:
    allowed exception
    rewrite to uv run python
    rewrite to uv run --no-project python
    defer to sibling issue or external-tool contract
update audit/tests so the exception policy and reporting are explicit
patch the highest-leverage repo-local offenders first
rerun the audit and compare recent/event-time and full-corpus metrics separately
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/analysis/provider_session_ecosystem_audit.py` | expose or refine runtime-policy reporting fields and exception framing |
| Modify | `tests/analysis/test_provider_session_ecosystem_audit.py` | lock in runtime-policy summaries, exception handling, and hotspot reporting behavior |
| Modify | `docs/reports/provider-session-ecosystem-audit.md` | render explicit runtime-policy interpretation for recent vs corpus views |
| Modify | `AGENTS.md` or adjacent runtime-governance doc | clarify any approved bare-`python3` exceptions if they are truly needed |
| Modify | repo-local hotspot scripts discovered during resource intel | convert the first bounded wave from bare `python3` to canonical `uv run` forms |
| Update | `docs/plans/README.md` | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_runtime_policy_summary_includes_recent_and_corpus_views` | runtime debt is reported in a way that distinguishes fresh activity from backfilled totals | synthetic provider snapshot | separate recent and corpus metrics rendered |
| `test_runtime_policy_exception_bucket_does_not_count_allowlisted_system_cases_as_debt` | approved exceptions do not inflate actionable debt | representative allowlisted command sample | excluded from actionable-debt bucket |
| `test_runtime_policy_hotspot_ranking_is_deterministic` | hotspot ordering is stable for issue follow-up and weekly review | fixed sample command-family counts | deterministic sorted output |
| `test_first_wave_repo_local_hotspots_use_uv_run_variants` | patched repo-local scripts no longer use forbidden bare `python3` forms | targeted changed files | zero disallowed matches |

---

## Acceptance Criteria

- [ ] The plan defines an explicit allowlist/exception policy for legitimate bare `python3` cases
- [ ] The first remediation wave is ranked using provider-audit evidence, not ad hoc guessing
- [ ] Reporting distinguishes recent event-time runtime debt from corpus/backfill growth
- [ ] Targeted tests cover runtime-policy summary behavior and any exception logic added
- [ ] The follow-up implementation wave targets Hermes-first orchestration hotspots unless fresher evidence overturns that ordering

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | not yet reviewed |
| Codex | PENDING | not yet reviewed |
| Gemini | PENDING | not yet reviewed |

**Overall result:** PENDING

Revisions made based on review:
- none yet

---

## Risks and Open Questions

- **Risk:** Broad repo-wide runtime cleanup can sprawl unless the first wave is constrained to the highest-leverage repo-local hotspots.
- **Risk:** Audit totals alone can mislead if backfilled corpus growth is mistaken for fresh behavior; the implementation plan must preserve the recent-vs-corpus distinction.
- **Open:** Which bare `python3` families are true repo-policy violations versus acceptable system/integration edge cases?
- **Open:** Should the first implementation wave focus purely on workspace-hub maintenance scripts, or include adjacent orchestrator wrappers invoked by Hermes?

---

## Complexity: T2

**T2** — bounded multi-file reporting/policy/test cleanup with a likely first remediation wave, but no architecture-scale redesign.
