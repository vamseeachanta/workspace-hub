# Plan-Review Readiness Brief: Issue #2281

> Issue: Implement v1 weekly audit for existing skills-curation workflow
> Plan: `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md`
> Date: 2026-04-15
> Status: draft (not yet plan-approved)

---

## Current-State Summary

Issue #2281 defines the deterministic v1 weekly skills-audit implementation that replaces the current Claude-only `skills-curation` cron wrapper. The plan went through adversarial cross-review (Claude: MAJOR, Codex: MAJOR, Gemini: UNAVAILABLE due to provider 429s). The plan was revised to address all substantive Claude and Codex findings: deterministic entrypoint location fixed at `scripts/skills/weekly_skills_audit.py`, canonical waiver path at `config/skills/weekly-audit-waivers.yaml`, concrete JSON/Markdown artifact paths with output-root redirection for TDD, richer output schema (12 required JSON fields), scheduler metadata alignment in acceptance criteria, and six additional tests covering malformed frontmatter, stable finding keys, first-run baseline, incompatible baseline handling, and waiver application. The plan correctly defers richer classification/ranking policy to sibling issue #2282.

---

## Resolved Review Blockers

These items were flagged as MAJOR by Claude and/or Codex and have been addressed in the latest plan revision:

1. **Deterministic entrypoint location** (Claude, Codex) -- Fixed at `scripts/skills/weekly_skills_audit.py` with thin cron wrapper in `scripts/cron/skills-curation.sh`.
2. **Scheduler metadata migration** (Claude, Codex) -- Explicit acceptance criteria added: `requires`, `is_claude_task`, description, and log contract must match deterministic reality.
3. **Malformed/missing frontmatter handling** (Claude, Codex) -- Test `test_weekly_skills_audit_handles_missing_or_malformed_frontmatter` added to TDD list.
4. **First-run baseline behavior** (Claude, Codex) -- Test `test_weekly_skills_audit_handles_first_run_without_baseline` added; `baseline_artifact=null` behavior defined.
5. **Incompatible prior baseline handling** (Codex) -- Test `test_weekly_skills_audit_ignores_incompatible_baseline_versions` added.
6. **Redirectable output roots for TDD/manual runs** (Claude, Codex) -- Required in output contract; CLI flag or environment variable specified.
7. **Stable finding keys across unchanged runs** (Codex) -- Test `test_weekly_skills_audit_computes_stable_finding_keys_across_unchanged_runs` added.
8. **Canonical waiver registry** (Claude, Codex) -- Path fixed at `config/skills/weekly-audit-waivers.yaml`; application and surfacing test added.
9. **Concrete artifact paths and output schema** (Claude, Codex) -- JSON artifact requires 12 fields; Markdown summary bounded to 5 sections.
10. **Classification scope bounded** (Claude, Codex) -- v1 uses only 5 deterministic buckets; richer policy explicitly deferred to #2282.

---

## Remaining Blockers

1. **Gemini review unavailable** -- Provider returned repeated `429 RESOURCE_EXHAUSTED`. This is an operational gap, not a plan-quality gap. The #2282 sibling plan received a Gemini review (MINOR verdict), suggesting Gemini's concerns for this family of issues are lighter than Claude/Codex. A reduced-provider exception should be documented or a retry scheduled.

No other blockers identified. The following are acknowledged risks (not blockers):

- **Classification noise without #2282 policy** (both reviewers): v1 buckets are named but their decision rules live in #2282's policy YAML. Mitigated by the `needs-human-review` fallback and read-only v1 posture.
- **Missing waiver file behavior** (minor): TDD list tests waiver application but not absent/malformed waiver file. The pseudocode says "load ... when present", implying graceful absence. Recommend adding one test during implementation.
- **Fixture vs. real-world gap** (Codex): Synthetic fixtures may not cover messy cases. Mitigated by `needs-human-review` bucket and noted in plan risks.

---

## Recommendation

**READY_FOR_PLAN_REVIEW**

All substantive MAJOR findings from both available reviewers (Claude, Codex) have been incorporated into the plan revision. The plan has 15 TDD tests, 14 acceptance criteria, concrete artifact paths, and clear v1 scope boundaries. The Gemini gap is operational (provider capacity), not a plan-quality concern. The plan is ready for human review and `status:plan-review`.

---

## Approval-Ready GitHub Comment

```markdown
## Plan review: #2281 -- Ready for approval

The plan for **implement v1 weekly audit for existing skills-curation workflow** has completed adversarial cross-review (Claude: MAJOR, Codex: MAJOR, Gemini: UNAVAILABLE/provider capacity). All substantive findings from Claude and Codex have been addressed in the latest revision.

**Key revisions made:**
- Deterministic entrypoint fixed at `scripts/skills/weekly_skills_audit.py`
- Scheduler metadata migration (`requires`, `is_claude_task`) elevated to acceptance criteria
- Concrete JSON (12 required fields) + Markdown (5 sections) artifact contract
- Redirectable output roots for TDD/manual runs
- 6 additional tests: malformed frontmatter, stable finding keys, first-run baseline, incompatible baseline, waiver application
- v1 classification bounded to 5 deterministic buckets; richer policy deferred to #2282

**Gemini review gap:** Provider 429s prevented completion. Sibling #2282 received Gemini MINOR, suggesting low risk. Recommend reduced-provider exception or retry.

**Readiness brief:** `docs/reports/2026-04-15-issue-2281-planreview-readiness.md`
**Plan:** `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md`

Requesting `status:plan-review` to proceed toward approval.
```

---

## Dependency Relationship with #2282

Issue #2282 (lock classification and ranking policy) defines the machine-readable policy contract (`config/skills/weekly-audit-policy.yaml`) that #2281's implementation will consume for deterministic bucket assignment, severity/confidence scoring, and carry-forward behavior.

**Dependency type:** Soft, not hard.
- #2281 can proceed to approval and begin implementation with its own minimal 5-bucket rubric.
- #2282's policy YAML would refine and formalize the classification rules that #2281 consumes.
- Both reviewers flagged classification ambiguity as the primary noise risk -- implementing #2282 first (or concurrently) would reduce that risk.
- **Recommended sequencing:** Approve #2282 first or in parallel with #2281. If #2281 is implemented before #2282's policy lands, the v1 classification logic should be written to be policy-file-aware so it can adopt #2282's YAML without a rewrite.
- #2282's own readiness brief (`docs/reports/2026-04-15-issue-2282-planreview-readiness.md`) recommends READY_FOR_PLAN_REVIEW.
