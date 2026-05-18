# Issue tree scope removal pattern

Use when a parent issue has child issues for machines, phases, workstreams, or deliverables and the user removes one from scope because it is unavailable, obsolete, or no longer intended.

## Goal

Keep the GitHub issue tree truthful without pretending implementation happened.

## Pattern

1. Inspect the parent and candidate child issue bodies/comments before editing.
2. Update the parent body first:
   - remove the child from the active checklist/subissue list;
   - add an explicit `Out of scope / removed` section with the reason;
   - keep the removed issue number in the out-of-scope note for traceability.
3. Post a closeout comment on the child before closing it:
   - state the user direction or evidence that removed it from scope;
   - state that no implementation was performed if it was still planning-only;
   - state what remains in residual scope;
   - state how to reintroduce the work later, usually by opening a fresh issue with new evidence rather than reopening stale scope.
4. Close the child as `not planned`.
5. Adjust labels so the state is not ambiguous, e.g. remove `status:needs-plan`, add `status:closed` and `wontfix` if those labels exist in the repo.
6. Comment on the parent with the scope update summary.
7. Verify both sides:
   - child is closed with `stateReason: NOT_PLANNED`;
   - child closeout comment is present;
   - parent active checklist no longer includes the child;
   - parent body still preserves the out-of-scope rationale.

## Why

If you only close the child, future planning waves may re-add it from the parent checklist. If you only edit the parent, future agents may reopen or duplicate the child because no durable issue-level rationale exists. Do both.

## Suggested child closeout shape

```markdown
## Closeout — removed from scope

Result: **not planned / removed**.

User direction/evidence: `<why this workstream is unavailable or obsolete>`.

Actions taken:
- Removed `<workstream>` from active parent scope in #<parent>.
- Left the reason durable here so future planning waves do not re-add it by inference.
- No implementation was performed; this issue was still at `<prior status>`.

Residual scope:
- Continue with `<remaining active scope>`.
- If this workstream becomes available later, open a fresh issue with new readiness/evidence rather than reopening this stale ticket.
```

## Suggested parent note shape

```markdown
## Scope update — unavailable/obsolete workstream removed

`<workstream>` is not available / no longer in scope and has been removed from this feature's active checklist.

Updated parent issue body:
- Removed #<child> from the active subissue checklist.
- Added an explicit out-of-scope note for `<workstream>`.
- Kept active scope focused on `<remaining scope>`.

Related closeout:
- #<child> closed as **not planned** with durable rationale.
```
