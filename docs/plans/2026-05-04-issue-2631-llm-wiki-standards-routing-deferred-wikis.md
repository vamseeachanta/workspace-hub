# Issue #2631: llm-wiki standards routing for deferred wikis

> **Status:** plan-review
> **Date:** 2026-05-04
> **Complexity:** T1 — governance decision / bounded documentation
> **Review artifacts:** `scripts/review/results/2026-05-04-plan-2631-claude.md`, `scripts/review/results/2026-05-04-plan-2631-gemini.md`

## Problem Statement

Issue #2631 will resolve the deferred standards-routing decisions for `maritime-law`, `lng-projects`, and `acma-projects` after the prior llm-wiki standards-routing wave. The work will not let an agent choose sanction/defer/archive independently. It will capture the **user-selected outcome** for each wiki and will leave any wiki unresolved when explicit user choice is absent.

- `/mnt/ace` raw corpora will remain outside git; approved implementation will promote only curated summaries, metadata, cross-links, and provenance fields.
- No plan will self-approve, create approval markers, or move an issue to `status:plan-approved`; this plan will stop at `status:plan-review` for user approval.
- Codex adversarial review remains unavailable due #2479 unless verified fixed; this plan will not block solely on Codex.

## Resource Intelligence Summary

| Source | Evidence | Impact |
|---|---|---|
| Issue #2631 | Deferred standards-routing decision issue | Confirms decision-only scope. |
| Issue #2615 / plan #2613 | Prior standards-routing wave left these wikis deferred | Defines predecessor context. |
| Issues #2592 and #2612 | Maritime-law and LNG-project predecessor work | Prevents duplicate implementation scope. |
| Issue body acceptance | Names `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_wiki_standards_path_decision.md` | Repo decision record will be preparatory; memory acceptance surface will be updated only after approval and explicit user choice. |

## Scope

### In Scope
- Draft a repo-side decision record capturing the user’s chosen outcome for each deferred wiki.
- Support `sanction`, `defer`, `archive`, and `unresolved` states.
- Reconcile repo documentation with the memory-file acceptance target.

### Out of Scope
- Authoring standards pages/templates.
- Filing follow-up implementation issues before user-selected outcomes.
- Creating approval markers or moving beyond `status:plan-review`.
- Copying raw corpus content or `/mnt/ace` paths into git.

## Proposed Deliverable

The approved implementation will create `docs/governance/llm-wiki-standards-routing-deferred-wikis-decision.md`. The record will capture the user-selected outcome for each wiki. If the user does not choose an outcome for a wiki, that row will remain `unresolved`. Acceptance for #2631 will also require updating `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_wiki_standards_path_decision.md` in the approved downstream step.

## Pseudocode / TDD Contract

```python
def test_decision_record_requires_user_choice():
    for wiki in ["maritime-law", "lng-projects", "acma-projects"]:
        assert decision[wiki]["outcome"] in {"sanction", "defer", "archive", "unresolved"}
        if decision[wiki]["outcome"] != "unresolved":
            assert decision[wiki]["user_choice_source"]

def test_no_implementation_scope_leaks():
    assert not creates_standard_pages_or_templates
    assert not creates_plan_approval_markers
```

## Files to Change

| Action | Path | Purpose |
|---|---|---|
| Create | `docs/governance/llm-wiki-standards-routing-deferred-wikis-decision.md` | Decision record capturing explicit user choices and unresolved rows |
| Conditional downstream | `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_wiki_standards_path_decision.md` | Acceptance surface after approval and explicit user choice |

## Acceptance Criteria

- [ ] Each wiki row will capture explicit user choice or remain `unresolved`.
- [ ] The plan will not treat an agent-inferred outcome as user approval.
- [ ] The decision record will reconcile repo documentation with the memory-file acceptance target.
- [ ] No standards pages/templates, raw-data copies, follow-up implementation issues, or approval markers will be created without separate approval.

## Adversarial Review Summary

| Reviewer | Verdict | Notes |
|---|---|---|
| Claude internal | MAJOR → RESOLVED | Findings required explicit user authority, memory-file acceptance reconciliation, #2615 evidence, and conditional follow-up scope. Applied; artifact: `scripts/review/results/2026-05-04-plan-2631-claude.md`. |
| Gemini | UNAVAILABLE_NOT_BLOCKING | Rerun path recorded in `scripts/review/results/2026-05-04-plan-2631-gemini.md`. |
| Codex | UNAVAILABLE | Codex remains unavailable due #2479. |

**Overall result:** APPROVAL-READY FOR USER REVIEW; stop at `status:plan-review`.
