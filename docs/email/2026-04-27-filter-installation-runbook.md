# Gmail Filter Installation Runbook — 2026-04-27

> **Purpose:** One-time inbox sweep that does not depend on automation. Repeatable across all 3 accounts (ace, personal, skestates).
> **Provenance:** Sample analysis of 50 inbox threads on `vamsee.achanta@aceengineer.com`, 2026-04-27. Filter rules below cover ~76% of sampled volume.
> **Companion:** `docs/email/WORKFLOW.md` (queue model, GitHub [#2017](https://github.com/vamseeachanta/workspace-hub/issues/2017)).
> **Bulk import (recommended):** `docs/email/gmail-filters-2026-04-27.xml` — one-shot Gmail Settings → Filters → "Import filters" instead of entering 7 rules manually. Read the preflight comments in the XML before importing.

## Why filters before #2017 v1 ships

The Email-as-Queue workflow ([#2017](https://github.com/vamseeachanta/workspace-hub/issues/2017)) is `status:plan-approved` but its v1 scope ([Path-3 hybrid](https://github.com/vamseeachanta/workspace-hub/blob/main/docs/plans/2026-04-20-issue-2017-plan.md)) delivers **local-queue contract only** — Gmail-side mutation is deferred to [#2423](https://github.com/vamseeachanta/workspace-hub/issues/2423). Until #2423 lands, **manual UI filters are the supported path** for inbox hygiene.

Filters give an immediate ~76% noise reduction with zero infra and survive the eventual #2423 automation (filters are additive, not conflicting).

## Preflight (do this once per account)

1. Open Gmail → Settings → "See all settings" → **Inbox** tab.
2. Find "Filtered mail" → **Override filters → uncheck "Override filters for important"**.
   - Without this step, "Skip Inbox" filters silently no-op for messages Gmail's importance classifier flags. See feedback memory `feedback_gmail_override_filters_silent_defeat.md`.
3. **Filters and Blocked Addresses** tab → "Create a new filter" for each rule below.
4. For each filter: tick **Skip the Inbox**, **Apply the label** (create new if absent), **Mark as read** (optional, recommended for noise), and **Apply filter to N matching conversations**.

## The 7 filter rules

### Group 1 — Pure marketing/promo
**Label:** `AutoNoise` (existing)
**Has the words (Gmail "From" field):**
```
from:(lowes@e.lowes.com OR email@e.godaddy.com OR zmail@zmail.zillow.com OR marketing@supermicro.com OR estore-support@supermicro.com OR eagle@indianeagle.com OR newsletter@mailing.milesandmore.com OR costcoauto@mail.costcoauto.com OR homedepotcustomercare@mg.homedepot.com OR info@c.davidweekleyhomes.com OR service@info.remitly.com)
```
Actions: Skip Inbox, Apply `AutoNoise`, Mark as read.

### Group 2 — Newsletters / weekly reads
**Label:** `AutoNoise`
```
from:(sahil@sahilbloom.com OR turiya@mail.beehiiv.com OR info@realpython.com OR jason@pyquantnews.com OR welcome@openrouter.ai OR noreply@email.openai.com OR no-reply@kaggle.com OR nasem@nationalacademies.org OR newsletter@sparkforautism.org)
```
Actions: Skip Inbox, Apply `AutoNoise`, Mark as read.

### Group 3 — Industry feeds (real signal, just not inbox-worthy)
**Label:** `O&G Industry` (existing)
```
from:(update@maritimereporter.com OR registrar@api.org)
```
Actions: Skip Inbox, Apply `O&G Industry`. (Leave unread so weekly skim is easy.)

### Group 4 — CRE listings (extraction target per [#2017](https://github.com/vamseeachanta/workspace-hub/issues/2017))
**Label:** `CRE` (existing)
```
from:(rorik@sethequities.com OR IanIppolito@therealestatecrowdfundingreview.com)
```
Actions: Skip Inbox, Apply `CRE`. Once [#2024](https://github.com/vamseeachanta/workspace-hub/issues/2024) ships, the extraction pipeline will read from this label and write structured data to `assethold/data/`.

### Group 5 — Trello bot from deleted account
**Label:** `AutoNoise`
```
from:do-not-reply@trello.com subject:"deleted account"
```
Actions: Skip Inbox, Apply `AutoNoise`, Mark as read, **Delete it** (Trello cannot stop sending these — the account is gone). One-time bulk-delete the existing matches; filter handles future ones.

### Group 6 — Dependabot review-requests for worldenergydata
**New label:** `gh-dependabot` (create first)
```
from:notifications@github.com to:worldenergydata@noreply.github.com
```
Actions: Skip Inbox, Apply `gh-dependabot`. Batch-review under [#2433](https://github.com/vamseeachanta/workspace-hub/issues/2433) (worldenergydata main CI) instead of inbox-by-inbox.

### Group 7 — Closed/stale GitHub threads (one-time cleanup, no filter)
- Bulk archive threads where `from:notifications@github.com` AND last activity older than 30 days AND no @mention of you.
- This is a one-shot sweep, not a recurring filter — the inbox-noise generator was the lack of filter routing on Group 6, not stale state.

## Verification checklist

After installing filters and running "Apply to existing conversations":

- [ ] Inbox count dropped (record before/after — sample showed ~38 of 50 archived).
- [ ] `AutoNoise` label has expected senders only (spot-check 5).
- [ ] No filter accidentally caught a thread you replied to (search `label:AutoNoise from:vamsee` should return 0).
- [ ] `gh-dependabot` label populated and Dependabot PRs are still open in GitHub (filters do not affect repo state).
- [ ] Override-filters preflight is `unchecked` — recheck Settings → Inbox.

## What stays in the inbox (expected residue)

After the sweep, the inbox should contain only:
- Live conversations (e.g., Sabitha tax + property thread, Frontier Deepwater group).
- Job-application status updates (e.g., Anthropic STEM Fellow, GC Squared Naval Architect).
- Calendar invitations and reminders.
- Soccer-style local social coordination (Selim Ozkul / Memorial Outdoor).
- Genuinely actionable mail from people, not bots.

This residue is the queue [#2017](https://github.com/vamseeachanta/workspace-hub/issues/2017) operates on. Filters do not handle the queue itself — that work continues through [#2024](https://github.com/vamseeachanta/workspace-hub/issues/2024) ([extract-and-act pipeline](https://github.com/vamseeachanta/workspace-hub/issues/2024)) and [#2026](https://github.com/vamseeachanta/workspace-hub/issues/2026) (state tracking).

## Replicating on accounts 2 and 3

The 7 rules above were derived from the `aceengineer.com` inbox sample. Personal and skestates inboxes will need their own sender-domain audit, but the **structure** (group by intent, label by domain meaning, apply preflight first) transfers verbatim. Run a 50-thread sample on each account before authoring its filter set.

## Forward dependencies

- **[#2423](https://github.com/vamseeachanta/workspace-hub/issues/2423)** (Gmail-side automated delete/archive) — once OAuth scope-bump lands (see new issue filed 2026-04-27), the script can apply the same rules programmatically and tear down the manual filters if desired.
- **[#2024](https://github.com/vamseeachanta/workspace-hub/issues/2024)** — will read from `CRE`, `O&G Industry`, and other domain-meaning labels as extraction sources.
- **[#2026](https://github.com/vamseeachanta/workspace-hub/issues/2026)** — `wh-email/*` queue-state labels are independent of the filters above; both layers coexist.
