# Plan for #2235: Add Retention Metadata Section to Issue Plan Template

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2235
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2235-claude-overnight.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/plans/_template-issue-plan.md` -- current plan template with no retention metadata section; contains Resource Intelligence Summary, Artifact Map, Deliverable, Pseudocode, Files to Change, TDD Test List, Acceptance Criteria, Adversarial Review Summary, Risks and Open Questions, and Complexity sections
- Found: `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` -- normative #2209 boundary policy; Section 8 defines retention schedule for plan files as "Issue lifetime + 30 days" and for review results as "90 days"; Section 10.1 explicitly recommends adding a `## Retention` section to the plan file template noting the plan expires with the issue
- Gap: No retention section exists in the plan template today; the template gives no guidance to plan authors about artifact lifecycle

### Standards
<!-- Not applicable for governance/documentation issues -->
| Standard | Status | Source |
|---|---|---|
| Not applicable | n/a | Non-engineering issue |

### LLM Wiki pages consulted
- No relevant wiki pages — this is a governance template change, not a domain knowledge issue

### Documents consulted
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` -- Section 8.1 defines the retention schedule for plan files ("Issue lifetime + 30 days") and review results ("90 days"); Section 10.1 row 3 explicitly calls for this template change
- `docs/plans/README.md` -- Section "Required Sections in Each Plan" lists 10 required sections; retention is not among them (will need update if retention becomes required, but that is outside this issue's scope)
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` -- Step 2 lists required sections; no mention of retention metadata
- Issue #2209 (parent policy) -- durable-vs-transient boundary policy; this issue is a direct follow-on from Section 10.1

### Gaps identified
- No retention section in the current plan template
- No guidance for plan authors on how to fill retention metadata
- Template comment blocks do not reference #2209 retention schedule

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 4 (issue body, plan template, durable-vs-transient policy, plans README) -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-16-issue-2235-add-retention-metadata-section-to-plan-template.md |
| Implementation | `docs/plans/_template-issue-plan.md` |
| Plan review -- Claude | scripts/review/results/2026-04-16-plan-2235-claude-overnight.md |

---

## Deliverable

A `## Retention` section in `docs/plans/_template-issue-plan.md` that provides structured retention metadata (artifact class, default retention period, expiration trigger) aligned with the #2209 retention schedule, with author guidance in HTML comments.

---

## Pseudocode

Trivial -- see files to change. The change is a new markdown section added to an existing template file.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `docs/plans/_template-issue-plan.md` | Add `## Retention` section between Adversarial Review Summary and Risks/Open Questions, with HTML comment guidance referencing #2209 Section 8 retention schedule |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_retention_section_exists | Template contains `## Retention` heading | `grep -c '## Retention' docs/plans/_template-issue-plan.md` | 1 |
| verify_retention_references_2209 | Template retention section references #2209 | `grep -c '#2209' docs/plans/_template-issue-plan.md` retention section | >= 1 |
| verify_retention_has_table | Retention section includes a table with artifact class, retention period, and expiration trigger columns | `grep -A5 '## Retention' docs/plans/_template-issue-plan.md` | contains pipe-delimited table |
| verify_template_structure | Template still has all 10 existing required sections intact after edit | `grep -c '## ' docs/plans/_template-issue-plan.md` | >= 11 (10 existing + 1 new) |

---

## Acceptance Criteria

- [ ] `docs/plans/_template-issue-plan.md` contains a `## Retention` section
- [ ] Retention section includes a pre-filled table with artifact classes: plan file, review artifacts, approval markers
- [ ] Retention periods align with #2209 Section 8.1 schedule (plan: issue lifetime + 30d, reviews: 90d, markers: issue lifetime)
- [ ] HTML comment guidance tells authors how to customize retention for their specific issue
- [ ] All 10 existing required sections remain intact and unmodified
- [ ] Change is template/governance scoped -- no conformance tooling or enforcement scripts modified
- [ ] Review artifacts posted to scripts/review/results/

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | overnight draft review |
| Codex | PENDING | awaiting routing |
| Gemini | PENDING | awaiting routing |

**Overall result:** PENDING

Revisions made based on review:
- (none yet)

---

## Risks and Open Questions

- **Risk:** If #2209 retention schedule changes, this template section becomes stale -- mitigated by referencing #2209 as the authoritative source rather than hardcoding values
- **Open:** Should the retention section be a "required" section in `docs/plans/README.md`? This plan does NOT update README required-sections list per the scope constraint -- that decision is deferred to the user or a follow-on issue

---

## Complexity: T1

**T1** -- single-file template edit adding one new section with no code, no tests beyond grep verification, no multi-file changes.
