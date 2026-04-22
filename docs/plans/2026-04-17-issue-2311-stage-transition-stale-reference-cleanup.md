# Plan for #2311: Stage-transition stale reference cleanup

> Status: draft
> Complexity: T2
> Date: 2026-04-17
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2311
> Review artifacts: scripts/review/results/2026-04-17-plan-2311-claude.md | scripts/review/results/2026-04-22-plan-2311-codex.md | scripts/review/results/2026-04-22-plan-2311-gemini.md

---

## Resource Intelligence Summary

### Existing repo code and tests
- Found: `tests/helpers/stale_reference_docs.py` already defines the core banned-pattern regex for deleted stage-transition scripts, including `scripts/work-queue/start_stage.py`, `scripts/work-queue/exit_stage.py`, and `scripts/work-queue/verify_checklist.py`.
- Found: `tests/docs/test_banned_stale_references.py` already protects a small curated set of current docs, but its fixed list does not yet include hidden instructional surfaces such as `.claude/docs/*.md`.
- Found: `tests/docs/test_legacy_reference_allowlist.py` currently allows two legacy/reference docs: `docs/ops/legacy-claude-reference-map.md` and `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`.
- Found: `scripts/analysis/provider_session_ecosystem_audit.py` already codifies the canonical redirect targets for the legacy stage-transition cluster via `LEGACY_REMEDIATION_RULES[legacy_work_queue_transition]`, so the plan can validate against repo-attested targets instead of speculative issue-body claims.

### Governing workflow / standards
| Standard | Status | Source |
|---|---|---|
| Mandatory issue-planning workflow (`resource intel -> draft plan -> adversarial review -> user approval`) | applicable | `docs/plans/README.md` |
| Hard stop before implementation without approval | applicable | `docs/standards/HARD-STOP-POLICY.md` |
| Current workflow/governance redirect targets for removed work-queue paths | applicable | `docs/governance/SESSION-GOVERNANCE.md`, `docs/governance/TRUST-ARCHITECTURE.md`, `scripts/workflow/governance-checkpoints.yaml` |

### Documents and artifacts consulted
- `docs/ops/legacy-claude-reference-map.md` explicitly maps the removed stage-transition scripts to the current governance docs/hooks/review surfaces.
- `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md` is explicitly labeled `Status: legacy architecture note with current-path redirects`, which makes it an intentional legacy redirect surface for this issue; deeper decomposition remains separate follow-up work under `#2214`.
- `docs/work-queue-workflow.md` documents the current GitHub issue + `.planning/` operating model and distinguishes legacy compatibility notes from canonical execution.
- `docs/reports/provider-session-ecosystem-audit.md` and `analysis/provider-session-ecosystem-audit.json` preserve the stale-read cluster as historical evidence and reference the same redirect targets as the audit generator.
- `scripts/review/results/2026-04-22-plan-2311-codex.md` and `scripts/review/results/2026-04-22-plan-2311-gemini.md` both require the plan to resolve the taxonomy now, remove conditional scope, and make the tests falsifiable.

### Current scan findings relevant to scope
- Protected current docs already covered by `tests/docs/test_banned_stale_references.py` do not need speculative expansion beyond this issue's exact stale-path cluster.
- Hidden current instructional surface with a known live hit: `.claude/docs/data-format-guide.md` still mentions `exit_stage.py` and must be cleaned in this issue.
- The implementation test for this issue will lock `.planning/templates/**/*.md` and `.gemini/**/*.md` into the protected current-surface scan so future reintroductions there fail deterministically, regardless of the current zero-hit state.
- Historical/planning/report surfaces still contain intentional references, including `.planning/archive/**/*.md`, `.planning/skills/capability-assessment-wrk-624-skills.md`, `docs/reports/**/*.md`, `analysis/**/*.json|md`, and review/log/history artifacts. Those are evidence surfaces, not live workflow instructions.

### Gaps identified
- There is no issue-specific test that locks the exact protected-surface scan universe and the exact allowed legacy/history buckets for this stale-path cluster.
- There is no current regression proving that `.claude/docs/*.md` surfaces stay clean.
- The prior draft left file dispositions and the legacy/history taxonomy unresolved; this redraft fixes those decisions in-plan so implementation is not a discovery-time heuristic.

<!-- Verification: count distinct sources above (issue-independent repo-attested sources).
     Minimum 3 required. Current count: 10+ -->

---

## Resolved Classification Rule for This Issue

This issue uses fixed buckets, not execution-time judgment.

### Forbidden bucket: protected current instructional surfaces
Any mention of `scripts/work-queue/start_stage.py`, `scripts/work-queue/exit_stage.py`, or `scripts/work-queue/verify_checklist.py` is a test failure inside these surfaces:
- Root agent entrypoints: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`
- Current docs: `docs/README.md`, `docs/context-pipeline.md`, `docs/governance/TRUST-ARCHITECTURE.md`, `docs/modules/workflow/SPEC_LOCALITY_POLICY.md`, `docs/work-queue-workflow.md`
- Current plan/governance index: `docs/plans/README.md`
- Current planning templates: `.planning/templates/**/*.md`
- Current Claude instructional docs: `.claude/docs/**/*.md`
- Current Claude command/skill instructions: `.claude/commands/**/*.md`, `.claude/skills/**/*.md`
- Current Gemini workflow instructions: `.gemini/**/*.md`

### Allowed bucket: intentional legacy redirect surfaces
References may remain in these exact legacy redirect files for now:
- `docs/ops/legacy-claude-reference-map.md`
- `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`

Decision note: `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md` remains allowed in this issue because it is already marked as a legacy redirect note; cleanup/splitting of that document is deferred to `#2214`, not reopened here.

### Allowed bucket: tooling/test-source retained-reference surfaces
References may remain in source files whose explicit purpose is to detect, classify, or remediate the stale names rather than teach users to execute them:
- `tests/helpers/stale_reference_docs.py`
- `scripts/analysis/provider_session_ecosystem_audit.py`

Decision note: this issue does not attempt to remove the literal stale names from detector/remediation source code. They are intentional implementation data for the guardrails and audit mappings, and must be excluded from the "only two non-history files may retain the names" rule.

### Allowed bucket: historical / generated evidence surfaces
References may remain when preserved as audit history rather than live guidance:
- `docs/reports/**/*.md`
- `analysis/**/*.md`
- `analysis/**/*.json`
- `scripts/review/results/**/*.md`
- `.planning/archive/**/*.md`
- `.planning/skills/**/*.md`
- `logs/**/*.jsonl`
- `state/reflect-history/**/*.md`
- `state/session-signals/**/*.jsonl`

### Known live rewrite set to handle during implementation
- `.claude/docs/data-format-guide.md` — remove the stale `exit_stage.py` reference and replace it with a generic current parser-description note only; do not link readers back to deleted stage-transition executables.

This resolves the Codex/Gemini objection that the scan universe and allowed legacy/history classes were undefined.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2311-stage-transition-stale-reference-cleanup.md` |
| Targeted confinement test | `tests/docs/test_stage_transition_reference_confinement.py` |
| Shared stale-reference helper updates | `tests/helpers/stale_reference_docs.py` |
| Curated protected-surface test update | `tests/docs/test_banned_stale_references.py` |
| Legacy/reference allowlist alignment | `tests/docs/test_legacy_reference_allowlist.py` |
| Current instructional doc cleanup | `.claude/docs/data-format-guide.md` |
| Canonical legacy redirect surface | `docs/ops/legacy-claude-reference-map.md` |
| Legacy architecture redirect note | `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md` |
| Audit rule source for redirect targets | `scripts/analysis/provider_session_ecosystem_audit.py` |
| Review artifact — Claude | `scripts/review/results/2026-04-17-plan-2311-claude.md` |
| Review artifact — Codex | `scripts/review/results/2026-04-22-plan-2311-codex.md` |
| Review artifact — Gemini | `scripts/review/results/2026-04-22-plan-2311-gemini.md` |

---

## Deliverable

A bounded stale-reference cleanup plus regression suite that proves the deleted stage-transition script names are absent from fixed current instructional surfaces, while remaining allowed only in explicitly enumerated legacy redirect and historical evidence buckets.

---

## Pseudocode

```text
load the three issue-specific stale script paths
lock the protected current-surface path set and the allowed legacy/history bucket rules in test code
scan the protected current-surface set for any of the three stale paths
assert the known live hit in .claude/docs/data-format-guide.md is removed during implementation
scan the explicit legacy redirect files and assert they are the only non-history files allowed to retain those names
validate that each required redirect target exists in repo-attested sources:
    docs/ops/legacy-claude-reference-map.md
    scripts/analysis/provider_session_ecosystem_audit.py legacy_work_queue_transition rule
add a negative/mutation-style test that proves a sample protected-surface reintroduction would match the banned patterns
run the targeted docs test subset
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/docs/test_stage_transition_reference_confinement.py` | define the exact protected-surface universe, the exact allowed buckets, and issue-specific reintroduction checks |
| Modify | `tests/helpers/stale_reference_docs.py` | expose issue-specific constants/helpers for the three stage-transition script names and bucket scanning |
| Modify | `tests/docs/test_banned_stale_references.py` | add `.claude/docs/data-format-guide.md` to the curated protected set after cleanup so the known live hit stays covered |
| Modify | `tests/docs/test_legacy_reference_allowlist.py` | align the generic legacy test with the explicit decision that only the two legacy redirect docs remain allowed outside history buckets |
| Modify | `.claude/docs/data-format-guide.md` | remove the live instructional `exit_stage.py` reference discovered during prerequisite scanning |

Removed from scope in this redraft:
- `docs/plans/README.md` indexing work
- speculative `if needed` edits
- audit-refresh/regeneration work without an explicit generator contract for this issue

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_stage_transition_references_are_forbidden_in_protected_current_surfaces` | fixed protected current-surface universe stays clean | exact path set/globs listed in this plan + the three stale script paths | zero matches |
| `test_stage_transition_references_are_limited_to_two_legacy_redirect_docs_outside_history_and_tooling_buckets` | only the two intentional legacy redirect docs may retain the names outside history/report/tooling buckets | repo scan results bucketed by explicit rules | non-history/non-tooling hits limited to `docs/ops/legacy-claude-reference-map.md` and `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md` |
| `test_stage_transition_known_live_hit_removed_from_data_format_guide` | the known current instructional hit does not regress | `.claude/docs/data-format-guide.md` | zero matches for the three stale names |
| `test_stage_transition_redirect_targets_exist_in_legacy_map_and_audit_rule` | redirect guidance is measurable, not hand-wavy | `docs/ops/legacy-claude-reference-map.md` plus `scripts/analysis/provider_session_ecosystem_audit.py` | all required targets present: `docs/governance/SESSION-GOVERNANCE.md`, `docs/governance/TRUST-ARCHITECTURE.md`, `scripts/workflow/governance-checkpoints.yaml`, `.claude/hooks/plan-approval-gate.sh`, `.claude/hooks/session-governor-check.sh`, `scripts/review/cross-review.sh` |
| `test_stage_transition_tooling_sources_are_explicitly_classified_not_false-flagged` | detector/remediation source files are intentionally retained-reference surfaces, not accidental live guidance | `tests/helpers/stale_reference_docs.py`, `scripts/analysis/provider_session_ecosystem_audit.py` | both files land in the tooling/test-source bucket and do not fail the legacy-doc confinement rule |
| `test_stage_transition_pattern_matches_sample_reintroduction` | negative/mutation-style proof that the guardrail would catch a future reintroduction | sample protected-surface text containing one of the stale paths | helper reports a match |

---

## Acceptance Criteria

- [ ] The plan and implementation use the fixed bucket taxonomy above: protected current instructional surfaces, two allowed legacy redirect docs, explicit tooling/test-source retained-reference surfaces, and explicit historical/generated evidence buckets.
- [ ] `.claude/docs/data-format-guide.md` no longer mentions `start_stage.py`, `exit_stage.py`, or `verify_checklist.py`.
- [ ] `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md` is explicitly treated as an allowed legacy redirect surface for this issue, with broader cleanup deferred to `#2214`.
- [ ] `tests/helpers/stale_reference_docs.py` and `scripts/analysis/provider_session_ecosystem_audit.py` are explicitly treated as tooling/test-source retained-reference surfaces rather than accidental live-guidance hits.
- [ ] No speculative file targets remain in the plan; every listed file has a concrete reason and disposition.
- [ ] The targeted regression suite includes one forbidden-surface scan, one allowed-bucket confinement test, one redirect-target existence test, one tooling-bucket classification test, and one negative/mutation-style test.
- [ ] Targeted docs tests pass via `uv run pytest tests/docs/test_stage_transition_reference_confinement.py tests/docs/test_banned_stale_references.py tests/docs/test_legacy_reference_allowlist.py -q`.
- [ ] Audit/history artifacts may continue to mention the removed scripts only within the explicit historical/generated evidence buckets above; this issue does not require regenerating those artifacts.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings now addressed in this redraft |
|---|---|---|
| Claude (2026-04-17) | MAJOR | Earlier taxonomy gaps and conditional rewrite language are now resolved through a fixed bucket table and an explicit known live rewrite target. |
| Codex (2026-04-22) | MAJOR | The scan universe is now explicit, the architecture-doc disposition is decided, scope-creep items were removed, and the tests are now measurable instead of omission-based. |
| Gemini (2026-04-22) | MAJOR | The redraft removes `if needed` ambiguity, hardens redirect-target validation, and answers how instructional vs legacy/history surfaces are classified before implementation starts. |

Overall result: prior reviews identified real blocking issues; this redraft folds those findings into the actual plan body instead of preserving them only as a failure note.

---

## Risks and Open Questions

### Risks
- Historical surfaces are numerous; the implementation must keep the history bucket explicit so the test does not become noisy or silently permissive.
- If additional hidden instructional surfaces are discovered during implementation, they should be added only when they match the fixed “current instructional surface” rule above, not by broad uncontrolled repo scanning.

### Open questions
- None blocking approval readiness in this draft. The previously open taxonomy and disposition questions are now resolved in-plan.

---

## Complexity: T2

T2 — bounded documentation/test hardening with one known current-doc cleanup and explicit regression coverage. The work spans multiple files and requires deterministic bucket rules, but it does not require architecture redesign or broad audit regeneration.
