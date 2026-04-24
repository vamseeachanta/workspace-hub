# Gmail Ace Account Sweep — Session Summary

**Date:** 2026-04-24
**Operator:** Claude Code via claude-in-chrome extension
**Account:** vamsee.achanta@aceengineer.com
**Issue:** #2423 (Gmail-side mutation, Option B chosen)
**Outcome:** SUCCESS — Inbox 121 → 17 unread (87% reduction)

## Result

| Metric | Before | After |
|---|---|---|
| Inbox unread | 121 | 17 |
| Inbox older-than-30d (unlabeled) | ~180 | 0 (archived) |
| CRE label | 0 | 449 |
| AutoNoise label | 0 | 255 |
| Industry label | 0 | 59 |
| VIP filter (star + important) | 0 active | live |
| Override-filters setting | ON (filter-leaking) | OFF |
| Pre-existing filters | 6 | 6 (intact) + 4 new |

## Filters installed

### Filter A — CRE (consolidated three-layer)

```
from:(@sandsig.com OR @marcusmillichap.com OR @ccsend.com OR @loopnet.com OR @costarmail.com OR partnersrealestate.com OR @cushwake.com OR @cbre.com OR @colliers.com OR @jll.com OR @newmark.com OR avisonyoung.com OR kiddermathews.com OR @naiglobal.com OR lee-associates.com)
OR from:("Cafiero Team" OR "Chez Eider" OR "Eddy Nevarez" OR "John Chua" OR "Randy Blankstein" OR "Sands Investment" OR "Marcus & Millichap")
OR ("absolute NNN" OR "offering memorandum" OR "sale leaseback" OR "ground lease" OR "1031 exchange")
```

**Action:** Skip Inbox + Label CRE + Never to Spam + Apply to existing matching conversations.

**Catch:** 449 historical emails. Three layers (domain / display name / content phrase) ensure recall across direct platforms, named brokers, and any future broker using CRE terminology.

### Filter B — AutoNoise (23 domains)

```
from:(collide.io OR promote.weebly.com OR e.swimoutlet.com OR email.myflighthub.com OR mail.urbanairparks.com OR e.stantonoptical.com OR lists.wikimedia.org OR jongordon.com OR atticbuddies.com OR email.theparkingspot.com OR academia-mail.com OR accounts.google.com OR suzeorman.com OR marketing.goindigo.in OR deeplearning.ai OR gamemail.com OR m.learn.coursera.org OR irctc.co.in OR info.tatacapital.co.in OR info.dpam.com OR blueskysfund.com OR cincsystems.net OR indianstarllc.ccsend.com)
```

**Action:** Skip Inbox + Label AutoNoise + Apply to existing.

**Catch:** 255 historical emails. Promote individual domains to "Delete it" filter after 1-week observation if no false positives surface.

### Filter C — Industry reference

```
from:(substack.com OR info.marineinsight.com OR rigzonemail.com OR news.ogj.com)
```

**Action:** Skip Inbox + Label Industry + Apply to existing.

**Catch:** 59 historical emails.

### Filter D — VIP (clients + colleagues)

```
from:(@mcdermott.com OR @shell.com OR @bp.com OR @ril.com OR @kbr.com OR @technipfmc.com OR @technip.com OR @subsea7.com OR @nov.com OR @aker.com OR @vulcanoffshore.com OR @dorisgroup.com OR @frontierdeepwater.com OR @2hoffshore.com OR @2hoffshoreinc.com OR @eagle.org OR @engineeredcustomsolutions.com OR @km.kongsberg.com OR @boptechnologies.com OR @awilcodrilling.com OR @aceengineer.com)
```

**Action:** Star + Mark as important + Never to Spam + Apply to existing.

**Catch:** Star count not measured at time of session.

## Settings change

**S1.** Inbox → "For messages classified as important: **Don't override filters**"
- Was set to "Override filters" — meaning Skip-Inbox filter rules were ignored for messages Gmail's heuristic deemed important.
- Most Sands IG / CRE marketing carries "Important according to Google magic" — without this flip, the CRE filter would have leaked.

## Observed gaps for next session

1. **Seth Equities** — appeared in inbox as "JUST LISTED - Comfort Inn & Suites SW Houston Sugar Land" but did not match the CRE filter. Domain unknown; add when discoverable.
2. **SPARK Newsletter** — "Happy birthday, SPARK!" — newsletter not currently in AutoNoise list. Add to next sweep.
3. **Indian Eagle** — travel newsletter, also not in AutoNoise list. Add next sweep.
4. **dependabot[bot]** — GitHub dependency PR notifications. Already routed to `achantas-data/docs/email/dev-notifications` per `email-routing.yaml`, but no Gmail filter exists. Should add a "GitHub" label filter.
5. **Existing collide.io filter** — still applies "O&G Industry" label (misconfigured). New AutoNoise filter also applies. Mail ends up double-labeled. Recommend deleting the old filter manually.

## Architecture proven (for #2423)

**Browser-automation path works for the filter-install model.** No OAuth scope change needed; Gmail UI mutations via `claude-in-chrome` succeed end-to-end without dialogs because:
- Filter creation: in-page modals only
- Bulk archive of 180 conversations: no confirm dialog
- Label creation, "Apply to existing": in-page only

**Dialogs that would have broken the session (all avoided):**
- Unsubscribe via List-Unsubscribe → dialog. **Avoided** by going filter-route instead.
- "Delete forever" from Trash → dialog. **Avoided** by using Skip Inbox + Label, not Trash.
- Empty Trash → dialog. **Not invoked.**

## Implications for #2423

- **Option B (browser automation) chosen and proven.** OAuth re-auth (Option A) is no longer needed for the inbox-hygiene scope.
- **Per-thread Gmail mutation is partially obsoleted.** Filters handle 80% at ingestion. The remaining 20% (older-than-30d archive sweep) is a periodic UI run, not a per-thread state-machine call.
- **#2026 scope reduces** — local state machine only needs to track the actionable threads (client, tenant, tax) that escape the CRE/AutoNoise/Industry filter mesh.

## Followups

- [ ] Replay the same sweep on `achantav@gmail.com` (different noise pattern).
- [ ] Replay on `skestatesinc@gmail.com` (low volume, may be lighter-touch).
- [ ] Delete the misconfigured `from:(collide.io) → label O&G Industry` filter.
- [ ] Add `Seth Equities`, `SPARK Newsletter`, `Indian Eagle`, `dependabot[bot]` to appropriate filters.
- [ ] Schedule weekly archive sweep via `/schedule` once #2423 acceptance criteria are ratified.
- [ ] Wire #2024 extraction pipeline to consume `label:CRE` for `assethold/data/cre-listings/` extraction.

## Artifacts

- `config/email-filters/ace-filters-pre-sweep-2026-04-24.md` — baseline before sweep (rollback marker)
- `config/email-filters/ace-noise-domains.yaml` — updated with REVIEW promotions
- `scripts/email/email-routing.yaml` — updated with expanded CRE sender list
- `docs/sessions/2026-04-24-gmail-sweep-ace.gif` — full session recording (12.9 MB)
- This file
