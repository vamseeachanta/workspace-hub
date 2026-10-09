# Activity shortlist note workflow

Use this when the user asks to “make note of activities,” “add these options,” or otherwise preserve a selected activity shortlist for an existing trip in `vamseeachanta/achantas-data`.

## Pattern

1. Treat this as a lightweight trip-maintenance task, not a full new trip-plan issue.
2. Identify or use the existing destination/trip issue when one is already implied by context; avoid opening a duplicate parent trip issue just to store a shortlist.
3. Preserve the source URL, selected item numbers/titles, and a compact marker string that can be searched later.
4. Add a concise GitHub issue comment or issue-body note with:
   - source URL,
   - selected activities exactly as provided,
   - one-line scheduling note if relevant,
   - evidence/marker for future retrieval.
5. If creating local repo traceability, keep it as a short handoff/ledger entry; do not expand into the full mandatory trip-plan template unless the user explicitly asks for an itinerary or plan.
6. Close out with the issue URL/comment URL and state that no bookings/reservations/payments were performed.

## Good marker shape

`<trip-slug>-selected-activities-<source-slug>-YYYY-MM-DD`

Example:

`ok-trip-selected-activities-rustic-luxury-2026-05-18`

## Pitfalls

- Do not run the full visual-board/lodging/cost workflow for a simple note-taking request.
- Do not fabricate descriptions beyond the supplied source; if activity details matter, cite the source URL and keep the note compact.
- Do not imply reservations or commitments were made. This is planning metadata only.
