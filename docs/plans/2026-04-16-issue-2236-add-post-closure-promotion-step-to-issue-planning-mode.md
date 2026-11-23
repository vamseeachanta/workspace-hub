# Plan for #2236: Add Post-Closure Promotion Step to Issue-Planning-Mode

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2236
> **Review artifacts:** scripts/review/results/2026-04-16-plan-2236-claude-overnight.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` -- current workflow has Steps 1-7 (Intake, Draft Plan, Adversarial Review, Post and Label, User Approval, Implement, Close); Step 7 (Close) mentions "Post summary comment, close issue" but has no promotion check; the file also contains extensive governance sections on status precedence, rollback, and audit routines
- Found: `docs/plans/README.md` -- Step 8 (Close) already includes "Promotion candidates" line requirement per #2208 contract: close comment should include "Promotion candidates: none or specific findings worth promoting from transient (L5) to durable knowledge (L3) per #2209 Section 7"; this is a close-comment convention but NOT a distinct workflow step in the SKILL.md
- Gap: No post-closure promotion step exists as a formal workflow step in issue-planning-mode; the README mentions it at close-comment level but the SKILL.md does not implement it as a distinct step after close

### Standards
| Standard | Status | Source |
|---|---|---|
| Not applicable | n/a | Non-engineering governance issue |

### LLM Wiki pages consulted
- No relevant wiki pages -- this is a workflow/governance change

### Documents consulted
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` -- Section 7 defines the 5 promotion criteria (reusability, verification, non-redundancy, source traceability, stability); Section 10.2 row 4 explicitly calls for adding a post-closure promotion step to issue-planning-mode skill with dependency on wiki schema supporting `promoted_from`
- `docs/plans/README.md` -- Section "Step 8: Close" has "Retrieval evidence at closeout" with "Promotion candidates" line requirement, showing partial awareness of promotion at closeout but not as a distinct post-closure step
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` -- Step 7 (Close) says "Commit with conventional message referencing the issue; Push, post summary comment, close issue" with no promotion guidance
- Issue #2209 (parent policy) -- boundary policy defining promotion rules
- Issue #2208 (related) -- retrieval contract that introduced the close-comment promotion-candidates line

### Gaps identified
- SKILL.md has no post-closure promotion step -- closeout and promotion are not distinguished
- SKILL.md Step 7 (Close) does not reference #2209 Section 7 promotion criteria or the durable-vs-transient boundary
- No concrete prompt/checklist exists for agents to evaluate promotion candidates at issue closure

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 5 (issue body, SKILL.md, plans README, durable-vs-transient policy, #2208 contract) -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-16-issue-2236-add-post-closure-promotion-step-to-issue-planning-mode.md |
| Implementation | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Plan review -- Claude | scripts/review/results/2026-04-16-plan-2236-claude-overnight.md |

---

## Deliverable

A new "Step 8: Post-Closure Promotion" section in `.claude/skills/coordination/issue-planning-mode/SKILL.md` that provides a concrete checklist for evaluating whether issue-derived findings should be promoted from transient (L5) to durable knowledge (L3), with explicit references to #2209 Section 7 promotion criteria and #2208 close-comment conventions.

---

## Pseudocode

Trivial -- see files to change. The change is adding a new workflow step section to an existing skill markdown file.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Add "Step 8: Post-Closure Promotion" after current Step 7 (Close); renumber existing duplicate Step 6 references; include promotion checklist, pointer to #2209 Section 7 criteria, distinction between closeout and promotion |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_promotion_step_exists | SKILL.md contains a post-closure promotion step heading | `grep -c 'Post-Closure Promotion' SKILL.md` | >= 1 |
| verify_promotion_references_2209 | Promotion step references #2209 Section 7 | `grep -A20 'Post-Closure Promotion' SKILL.md` | contains "#2209" and "Section 7" |
| verify_promotion_references_2208 | Promotion step references #2208 close-comment convention | `grep -A20 'Post-Closure Promotion' SKILL.md` | contains "#2208" |
| verify_closeout_distinction | Step explicitly distinguishes closeout (ship the work) from promotion (elevate findings) | `grep -A30 'Post-Closure Promotion' SKILL.md` | contains "closeout" and "promotion" as distinct concepts |
| verify_promotion_checklist | Step includes a concrete checklist or decision criteria for agents | `grep -A30 'Post-Closure Promotion' SKILL.md` | contains checklist items (lines starting with -) |
| verify_workflow_overview_updated | Workflow overview diagram includes promotion step | `grep -A2 'Close' SKILL.md` in workflow overview | shows promotion after close |

---

## Acceptance Criteria

- [ ] SKILL.md contains a "Step 8: Post-Closure Promotion" section (or equivalent numbered step after Close)
- [ ] Promotion step includes a concrete checklist for evaluating promotion candidates against #2209 Section 7 criteria
- [ ] Step explicitly distinguishes between closeout (commit, push, close) and promotion (evaluate findings for L3 elevation)
- [ ] Step references both #2208 (close-comment promotion-candidates line) and #2209 (promotion criteria and process)
- [ ] Step points to durable targets: wiki pages under `knowledge/wikis/`, registry entries, governance docs
- [ ] No conformance tooling or enforcement scripts are implemented (governance guidance only)
- [ ] Workflow overview diagram at top of SKILL.md updated to include the promotion step
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

- **Risk:** SKILL.md already has duplicated step numbers (two "Step 5" and two "Step 6" sections exist); this edit should clean up numbering in the affected area but a full renumber across the entire file may introduce scope creep -- plan limits renumbering to the Close/Promotion area only
- **Risk:** #2209 Section 10.2 states this step depends on wiki schema supporting `promoted_from` frontmatter field; the promotion step guidance should work regardless of whether `promoted_from` is implemented (it is a best-practice hint, not a hard dependency for the workflow step itself)
- **Open:** Should the promotion step be mandatory for all issue classes or only for engineering/knowledge issues? Plan proposes mandatory for all classes with a "not applicable" shortcut for trivial T1 issues

---

## Complexity: T1

**T1** -- single-file skill edit adding one new workflow step section with no code, no tests beyond grep verification, no multi-file changes.
