# Closed issue revision thread pattern

Use when the user wants to revise or re-review a completed/closed GitHub issue, especially engineering calculation/report work that needs interactive comments before implementation.

## Trigger

- User points at a closed issue and says the work needs updates/revisions.
- User asks whether to create an open subissue/follow-up for discussion.
- The revision requires interactive review before code/report changes.

## Pattern

1. Inspect the parent issue first: title, state, URL, labels, body, and recent comments.
2. Create a new open revision issue rather than reopening the closed parent when:
   - the parent is completed and should remain traceable as the baseline deliverable,
   - the revision scope needs comment-by-comment discussion,
   - the revision may become gated implementation work later.
3. Copy the relevant parent labels when still applicable (category/domain/priority), but do not invent missing workflow labels.
4. Body shape for the new issue:
   - Purpose: revision/review of the completed work.
   - Parent/source issue link.
   - Existing deliverable links copied from parent comments/body.
   - Interactive review workflow with explicit discussion order.
   - Known scenario/baseline values.
   - Scope boundary separating revision from new physics/new deliverables.
   - Acceptance criteria that include discussion decisions, plan-before-implementation, TDD if implementation follows, regenerated deliverables, and parent link-back.
   - Gate note: open for discussion/planning; implementation blocked until plan review and user approval.
5. Comment on the closed parent with the new revision issue link so future readers do not continue the old closed thread.
6. Verify the new issue is open, labels are correct, and the parent link-back comment exists.

## Engineering calculation/report nuance

For calculation-report revisions, structure the discussion around domain components rather than generic tasks. Example review order:

- coordinate/sign convention and reference point,
- each force component,
- each moment component,
- result presentation/tables/charts,
- assumptions/limitations/report wording.

When the user's revision comment expands scope beyond the completed parent (for example, from rudder-only loads to hull-current loads plus rudder loads), call that out before planning and ask only questions that affect the calculation contract: default case values, heading/sign convention, coefficient source, reference geometry/CoG, force application point, moment method, sweep increments, units/rounding, chart set, and output locations.