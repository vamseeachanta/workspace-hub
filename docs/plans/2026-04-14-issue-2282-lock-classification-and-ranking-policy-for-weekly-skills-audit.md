# Plan for #2282: lock classification and ranking policy for weekly skills audit

> Status: plan-review
> Complexity: T2
> Date: 2026-04-14
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2282
> Review artifacts: scripts/review/results/2026-04-14-plan-2282-claude.md | scripts/review/results/2026-04-14-plan-2282-codex.md | scripts/review/results/2026-04-14-plan-2282-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/skills/detect_duplicate_skills.py` — current duplicate detector already distinguishes duplicate frontmatter names from leaf collisions, but does not provide the richer classification/ranking policy needed for weekly governance.
- Found: `scripts/skills/skill-usage-report.py` — current usage/staleness scoring introduces a second signal source with a different audit universe, which is exactly why #2282 is needed to lock deterministic interpretation rules before broader weekly ranking is attempted.
- Found: `tests/skills/test_skill_name_canonicalization.py` — frontmatter `name` already has test support as the canonical identifier, so #2282 should build policy around that existing rule rather than invent a competing identity model.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` and `scripts/cron/skills-curation.sh` — the weekly execution path already exists, so this issue should define only the policy layer that the deterministic implementation in #2281 will consume.

### Standards
| Standard | Status | Source |
|---|---|---|
| Cron governance via YAML installer/validator | done / relevant context | `docs/ops/scheduled-tasks.md`, `scripts/cron/setup-cron.sh`, `scripts/cron/validate-schedule.py` |
| Parent governance contract | draft but authoritative umbrella context | `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` |
| Child implementation contract | draft bounded consumer of this policy | `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md` |

### LLM Wiki pages consulted
- No relevant wiki pages found; this is a repo-governance/policy-design issue rather than domain wiki work.

### Documents consulted
- Issue #2280 — parent umbrella where the broader weekly skills-maintenance governance is being defined.
- Issue #2281 — child implementation issue that explicitly defers richer classification/ranking policy to #2282.
- Review artifacts for #2280 and #2281 under `scripts/review/results/2026-04-14-plan-2280-*.md` and `...2281-*.md` — both review waves consistently flagged classification/ranking ambiguity as a reason plans were still MAJOR.
- Related issue #2083 — concrete example of a canonical-wrapper or duplicate-path decision boundary.
- Related issue #2019 — concrete example of family-level consolidation pressure rather than simple duplicate detection.

### Gaps identified
- No checked-in deterministic policy exists for boundary cases between wrapper pairs, adjacent specializations, generic leaf collisions, and higher-priority duplicate findings.
- No stable severity/confidence rubric currently exists for weekly skill-governance output.
- No carry-forward / unchanged-finding presentation policy currently exists to keep weekly output low-noise.
- No explicit escalation thresholds exist yet for deciding which findings should later become follow-up GitHub issues.

<!-- Verification: distinct sources >= 3. Current count: 9 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md` |
| Parent plan | `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` |
| Child implementation plan | `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md` |
| Duplicate detector | `scripts/skills/detect_duplicate_skills.py` |
| Usage/staleness scorer | `scripts/skills/skill-usage-report.py` |
| Canonical-name tests | `tests/skills/test_skill_name_canonicalization.py` |
| Policy examples/tests | `tests/skills/test_weekly_skills_audit_policy.py` (proposed) |
| Canonical policy schema | `config/skills/weekly-audit-policy.yaml` |
| Optional explanatory doc | `docs/standards/weekly-skills-audit-policy.md` |
| Plan review — Claude | `scripts/review/results/2026-04-14-plan-2282-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-14-plan-2282-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-14-plan-2282-gemini.md` |

---

## Deliverable

A checked-in policy contract for weekly skills-audit classification and ranking that gives #2281 deterministic rules for bucket assignment, severity/confidence scoring, carry-forward behavior, and escalation thresholds without expanding the implementation into ad hoc taxonomy decision-making.

### Canonical policy source of truth
- Canonical machine-consumable source: `config/skills/weekly-audit-policy.yaml`
- Optional explanatory companion: `docs/standards/weekly-skills-audit-policy.md`
- If both exist, the YAML file is authoritative for implementation and tests; the Markdown file is explanatory only and must not introduce conflicting rules.

### Required policy contents
The policy must define:
- deterministic classification guidance for each bucket
- explicit precedence when multiple buckets could apply
- severity and confidence rubric
- low-noise weekly summary / carry-forward rules
- future escalation thresholds for follow-up issue creation
- fixture examples for each class
- a minimal machine-readable finding schema consumed by #2281

### Minimum deterministic posture
- If a case cannot be classified by the explicit policy rules with confidence, it must fall into `needs-human-review` rather than ad hoc heuristic guessing.
- The policy must optimize for low-noise repeatable weekly output, not maximum automatic classification coverage.
- Every finding must resolve to exactly one classification bucket after precedence is applied.

### Required finding schema for policy consumers
Each finding definition consumed by the weekly audit must minimally support:
- `finding_key`
- `classification`
- `severity`
- `confidence`
- `canonical_names`
- `paths`
- `summary`
- `recommended_action`
- `escalation_state`
- `is_new`
- `is_changed`

### Weekly summary semantics
The policy must define the minimum weekly summary sections:
1. new findings
2. changed findings
3. unresolved high-confidence findings
4. suppressed/carry-forward findings
5. operational errors or skipped inputs

Changed-but-unresolved rule:
- If a finding persists across weeks but its severity, confidence, scope footprint, or escalation_state changes materially, it must be surfaced in `changed findings`, not hidden in compact carry-forward.

Escalation model for v1:
- Use a binary escalation state only: `no-escalation` or `candidate`.
- Multi-tier escalation models are deferred until weekly signal quality is proven.

This issue does not implement the weekly audit script itself.

---

## Pseudocode

```text
define_policy_contract():
    choose canonical machine-readable source: config/skills/weekly-audit-policy.yaml
    define bucket criteria with positive criteria and exclusion criteria
    define precedence when multiple buckets could match
    enforce exactly one winning bucket after precedence
    define severity and confidence scoring rubric
    define minimal finding schema for weekly audit consumers
    define weekly carry-forward behavior for unchanged, changed, suppressed, and resolved findings
    define escalation thresholds and idempotence expectations for future issue creation
    encode examples and fixtures for each class
    keep policy small enough that #2281 can consume it deterministically
    route ambiguous or conflicting cases to needs-human-review
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md` | canonical plan artifact |
| Create | `config/skills/weekly-audit-policy.yaml` | canonical machine-readable policy contract |
| Optional create | `docs/standards/weekly-skills-audit-policy.md` | explanatory human-readable companion, subordinate to YAML |
| Create | `tests/skills/test_weekly_skills_audit_policy.py` | fixture-backed policy examples and boundary-case tests |
| Update | `docs/plans/README.md` | add plan index row |
| Update | GitHub issue `#2282` | planning/review progress |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_policy_classifies_exact_duplicate` | exact duplicate rule is deterministic | fixture duplicate pair | bucket = `exact-duplicate` |
| `test_policy_classifies_canonical_wrapper_pair` | wrapper/reference rule is deterministic | fixture canonical+stub pair | bucket = `canonical-wrapper-pair` |
| `test_policy_classifies_adjacent_specialization` | specialization rule preserves separate skills | fixture specialized pair | bucket = `adjacent-specialization` |
| `test_policy_classifies_generic_leaf_collision` | low-risk leaf collision stays low-priority | fixture same-leaf different canonical names | bucket = `generic-leaf-collision` |
| `test_policy_routes_ambiguous_case_to_needs_human_review` | unresolved cases do not get over-classified | conflicting fixture | bucket = `needs-human-review` |
| `test_policy_precedence_picks_highest_priority_bucket` | multi-match findings resolve deterministically | fixture qualifying for multiple buckets | expected precedence winner |
| `test_policy_bucket_resolution_is_mutually_exclusive` | every finding resolves to exactly one bucket after precedence | representative fixture set | single final bucket per finding |
| `test_policy_assigns_severity_and_confidence_levels` | scoring rubric is explicit | representative fixture cases | expected `severity` and `confidence` |
| `test_policy_defines_carry_forward_behavior` | unchanged findings remain compact in weekly output | prior/current identical finding sets | unchanged item not surfaced as new |
| `test_policy_handles_changed_but_unresolved_finding` | worsening or materially changed findings are not hidden as simple carry-forward | prior/current changed fixture | finding marked changed and surfaced appropriately |
| `test_policy_defines_issue_escalation_threshold` | only sufficiently important findings become follow-up candidates | representative high/medium/low cases | expected escalation decision |
| `test_policy_escalation_is_idempotent` | repeated weekly runs do not keep re-qualifying the same finding inconsistently | repeated escalated fixture | same escalation state across runs |
| `test_policy_weekly_summary_sections_are_minimum_contract` | weekly summary semantics are fixed for downstream consumers | policy fixture | exact required summary sections present |
| `test_policy_rejects_invalid_policy_schema` | malformed policy config fails fast | invalid YAML policy | validation error |

---

## Acceptance Criteria

- [ ] Canonical machine-readable policy source is fixed at `config/skills/weekly-audit-policy.yaml`
- [ ] Each weekly classification bucket has deterministic decision guidance
- [ ] Precedence is defined for cases where multiple buckets could apply
- [ ] Every finding resolves to exactly one final classification bucket after precedence is applied
- [ ] Boundary cases between wrapper pairs, adjacent specializations, generic leaf collisions, and human-review cases are documented
- [ ] Severity and confidence each have explicit criteria
- [ ] Carry-forward / unchanged-finding behavior is defined, including changed-but-unresolved cases
- [ ] Minimum weekly summary sections are defined for downstream consumers
- [ ] Escalation thresholds and idempotence expectations for future follow-up issues are defined
- [ ] Policy is concrete enough for test fixtures to encode
- [ ] Policy remains bounded enough that #2281 can consume it without reopening broad taxonomy redesign
- [ ] Plan review artifacts are posted before implementation begins

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | policy split is correct, but canonical source of truth, precedence, carry-forward behavior, and ambiguity routing needed tighter deterministic definition |
| Codex | MAJOR | policy still needed stronger machine-consumable rules for precedence, escalation idempotence, and low-noise weekly report semantics |
| Gemini | MINOR | separation of concerns is strong; main asks were clearer finding-object semantics and changed-severity carry-forward handling |

**Overall result:** FAIL — re-draft required before plan-review

Revisions made based on review:
- Fixed the canonical machine-readable source of truth at `config/skills/weekly-audit-policy.yaml`.
- Made any Markdown companion explicitly subordinate/explanatory only.
- Added minimum deterministic posture: ambiguous cases route to `needs-human-review`.
- Added precedence, changed-but-unresolved carry-forward, escalation idempotence, and invalid-schema tests.
- Expanded acceptance criteria to require precedence and idempotence rules explicitly.

---

## Risks and Open Questions

- Risk: policy may become too abstract to be testable if it is written as prose without fixture examples.
- Risk: policy may become too broad and drift into full taxonomy redesign if not kept tightly scoped to weekly-audit needs.
- Risk: the implementation in #2281 may still need a minimal temporary rubric if #2282 lags too long.
- Decision: canonical policy lives primarily in machine-readable config at `config/skills/weekly-audit-policy.yaml`; Markdown companion is optional and explanatory only.
- Decision: escalation thresholds are binary in v1 (`no-escalation` or `candidate`); richer models are deferred.

---

## Complexity: T2

**T2** — bounded policy-design work with explicit artifacts and tests, but it does not require cross-repo implementation or broad architecture changes.
