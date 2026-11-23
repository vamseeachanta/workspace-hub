# Blocker Revalidation After Child Closeout

Use this when a blocked parent GitHub issue has one or more child governance/input-restore/prep issues that just closed, and the next question is whether the parent can move from `status:blocked` to executable work.

## Core rule

A closed child prep issue does **not** automatically unblock the parent. Treat it as clearing only the specific prerequisite it delivered (for example, "checklist artifact exists") unless the child closeout and the linked artifact explicitly complete every required evidence/approval field and authorize a separately approved implementation lane.

## Revalidation checklist

1. Inspect live parent issues and child issues with `gh issue view`.
   - Confirm parent state, labels, last blocker comments, and child closeout comments.
   - Confirm whether child comments say "artifact landed" versus "clearance/input fields completed".
2. Inspect the linked governance/input-readiness artifacts in the repo.
   - Look for frontmatter/status and required fields.
   - If the artifact says required fields are still needed, the parent remains blocked.
3. Run deterministic local validation for the artifact class when available.
   - Example: `uv run scripts/validate_governance_artifacts.py`.
4. Use an independent read-only review when risk is high.
   - Ask Codex or another provider to classify only the blocker state.
   - Prompt must prohibit file edits, issue comments, and raw/private-source extraction.
5. Post one concise parent comment per affected parent issue.
   - State: remains blocked vs unblocked.
   - Name exactly which child prerequisite was cleared.
   - List remaining fields/gates before execution.
   - Give next execution order/recommendation.
6. Verify final state.
   - Parents should still be open + `status:blocked` if prerequisites remain incomplete.
   - Check repo state is clean/synced if no local file changes were intended.

## Pitfalls

- Do not remove `status:blocked` just because a child issue closed.
- Do not execute parent scope from an input-readiness checklist alone.
- Do not treat a governance/checklist artifact as approval to read/copy/promote raw `/mnt/ace` or private/vendor/client material.
- Do not bury the recommendation in a general summary only; post it directly on each parent issue so future agents see the live blocker state.

## Comment shape

```markdown
## Blocker revalidation after #<child> closeout

Decision: **#<parent> remains blocked**.

#<child> completed `<artifact>`. That clears the "<specific prerequisite>" prerequisite, but it does **not** complete <clearance/input surface> or authorize implementation.

Still required before any implementation lane can run:
- <field/gate 1>
- <field/gate 2>
- separate future implementation issue routed through plan review and user approval

Revalidation evidence:
- <validation command/result>
- <independent review result if used>
- No raw/private extraction or promotion performed.

Next recommendation: <specific next issue/order>.
```
