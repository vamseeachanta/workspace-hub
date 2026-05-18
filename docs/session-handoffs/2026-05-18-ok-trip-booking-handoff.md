# OK Trip Booking Handoff — Broken Bow / Hochatown

Timestamp: 2026-05-18T05:03:35-05:00

## Scope

Review vacation-trip evidence in `achantas-data` and prepare booking decision support for the OK / Broken Bow family trip.

Primary user constraint after revision: **visible mountain/ridge/panorama view is the top criterion**. Kitchen remains required.

GitHub issue: https://github.com/vamseeachanta/achantas-data/issues/91

## Current decision state

Do **not** book Crooked Pine blindly if panorama is the priority.

Priority order for Jun 6–9, 2026 after booking-engine re-check:

1. **Lookout at Eagle Ridge** — strongest small-cabin panorama evidence; current booking engine showed **RESERVED**.
2. **Hilltop at Eagle Ridge** — strong panorama benchmark; current booking engine showed **RESERVED** and cabin is oversized.
3. **Trail House at Eagle Ridge** — best currently available panorama-adjacent lead; host must confirm whether lake/nature view is visible from cabin/deck.
4. **Ridgeview Retreat** — available wooded hillside backup.
5. **Crooked Pine** — available and strongest kitchen/amenity fit, but weaker panorama/private wooded view.
6. **Sierra / Cimarron** — fallback only if secluded acreage/water beats ridge panorama.

Vehicle noted during decision support: **2013 Nissan Pathfinder XLE / Pathfinder SUV**. Provisionally passes general SUV/access requirement, but host should still confirm acceptability for specific driveway and weather conditions.

## Durable issue comments updated

The following issue comments were edited/verified as the durable booking board:

- Visual booking board — panorama-first priority order: https://github.com/vamseeachanta/achantas-data/issues/91#issuecomment-4476217524
- Decision path update — panorama is the primary gate: https://github.com/vamseeachanta/achantas-data/issues/91#issuecomment-4476258381
- Panorama / view evidence board — priority order: https://github.com/vamseeachanta/achantas-data/issues/91#issuecomment-4476349542

Verification from `gh api` after update showed those comments contain the updated `PANORAMA`/`RESERVED` decision framing and point back to issue #91.

## Booking call script

Use this exact call script before booking:

> We are booking Jun 6–9 for 2 adults and one child. Panorama / visible mountain-ridge view is the most important criterion, and we also need a kitchen. We have a 2013 Nissan Pathfinder SUV. Lookout at Eagle Ridge and Hilltop at Eagle Ridge look like the strongest view cabins but show reserved online. Is either actually available by cancellation/manual booking, or do you have another available cabin with comparable view from the cabin/deck/hot tub? If not, does Trail House have the lake/nature view visible from the cabin/deck, or only from the property/trail?

## Restart checklist

1. Open issue #91 and review the three durable comments above.
2. Call Cabins in Broken Bow / host before booking.
3. Ask first about cancellation/manual availability for **Lookout** and **Hilltop**.
4. If unavailable, ask whether **Trail House** has the view visible from cabin/deck.
5. If Trail House view is not from cabin/deck, decide explicitly between:
   - **Ridgeview Retreat** = better wooded hillside signal, weaker amenities.
   - **Crooked Pine** = better kitchen/amenities, weaker panorama.
6. Confirm total all-in price, cancellation terms, exact kitchen facilities, driveway/access suitability for Pathfinder, and whether view is visible from the booked place itself.
7. No booking/payment action should be performed by an agent without explicit user approval.

## External-action status

No booking, payment, phone call, external message, or reservation hold was performed. Work completed was documentation/review/update of GitHub issue comments only.

## Repo-state evidence

### workspace-hub control repo

Live proof before handoff file creation:

- path: `/mnt/local-analysis/workspace-hub`
- branch: `main`
- HEAD: `46ff5a2cb625dcb0b865efcdec9b5c675aa5dd43`
- origin/main: `46ff5a2cb625dcb0b865efcdec9b5c675aa5dd43`
- ahead/behind: `0/0`
- dirty/untracked count before this handoff: `50`

Dirty state was pre-existing/concurrent session state and was not staged by this booking handoff. Notable classes included provider-report churn, plan/review artifacts, skill/reference updates, and session-signal/correction state. This handoff should stage only this file unless explicitly directed otherwise.

### achantas-data

No local clone was present at `/mnt/local-analysis/achantas-data`; issue work was performed through GitHub API/CLI against `vamseeachanta/achantas-data` issue #91.

Live issue evidence:

- issue: https://github.com/vamseeachanta/achantas-data/issues/91
- state checked by `gh issue view`: `OPEN`
- title checked by `gh issue view`: `trip: plan Broken Bow OK family road trip (Jun 6-9 2026 vs September variant)`

## Branch/worktree disposition

No separate branch or worktree was created for this task. Work occurred on `workspace-hub` `main` for this closeout artifact plus GitHub issue comments in `achantas-data`.

## Final push/sync proof

Final proof after committing this handoff:

- handoff commit: `7d35f47fa85927a0d3aa259ddb5818964cd14d9e` (`docs: add ok trip booking handoff`)
- branch: `main`
- HEAD after fetch: `7d35f47fa85927a0d3aa259ddb5818964cd14d9e`
- origin/main after fetch: `7d35f47fa85927a0d3aa259ddb5818964cd14d9e`
- ahead/behind: `0/0`
- remaining dirty/untracked count: `43`

Remaining dirty paths were not staged by this handoff and are preserved as unrelated/concurrent workspace-hub session state.
