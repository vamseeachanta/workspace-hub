# Gmail Manual-Sweep Checklist

**Date:** 2026-04-24
**Goal:** Clean all three Gmail inboxes to a manageable day-to-day volume in one sitting (~30-60 min per account), independent of the #2017 → #2024 → #2423 automation build.
**Trigger:** 2026-04-24 decision sweep — bridge between the archive-era infrastructure and the queue-era pipeline that has not landed yet.

## Scope

Three accounts:

| Account | Role | Inbox pain point |
|---|---|---|
| `vamsee.achanta@aceengineer.com` | Business / engineering consulting | 33% CRE listings (sandsig.com et al); 16 confirmed noise domains |
| `achantav@gmail.com` | Personal / networking | Marketing newsletters; self-forwards to ace |
| `skestatesinc@gmail.com` | Real estate LLC | Tenant comms (low volume; leave as-is unless noise surfaces) |

## Why manual, not scripted

- Gmail MCP is `read + compose + label` only — **no archive/delete from Claude**. See `reference_gmail_mcp_scope.md`.
- `scripts/email/batch-unsubscribe.sh` exists but needs OAuth with mutation scope (the exact thing #2423 is deciding).
- Manual UI sweep takes one hour once; the scripted path is weeks out.

## Pre-flight (5 min)

- [ ] Open Gmail in three tabs: ace, achantav, skestates.
- [ ] Open `config/email-filters/ace-noise-domains.yaml` for reference.
- [ ] Settings → Filters and Blocked Addresses → have this tab ready in each account.

## Part A — Ace account (`vamsee.achanta@aceengineer.com`)

### A1. CRE listings filter (the big win — 33% reduction) (5 min)

Do **not** unsubscribe. The data is being extracted to `assethold/data/cre-listings`. Just get it out of the inbox view.

1. Gmail → Settings → Filters → Create new filter.
2. `From:` paste exactly:
   ```
   sandsig.com OR marcusmillichap.com OR email.loopnet.com OR partnersrealestate.com OR ten-x.ccsend.com OR c.costarmail.com
   ```
3. Create filter → check:
   - [x] Skip the Inbox (Archive it)
   - [x] Apply label: **CRE** (create if new)
   - [x] Never send to Spam
   - [x] **Also apply filter to matching conversations** (cleans history)
4. Create.

Expected effect: ~1/3 of unread disappears from Inbox view; still searchable under `label:CRE`.

### A2. Noise-domain bulk unsubscribe + delete (15 min)

For each of the 16 noise domains in `config/email-filters/ace-noise-domains.yaml`:

| # | Domain | Action |
|---|---|---|
| 1 | collide.io | UNSUB |
| 2 | skylineseven.ccsend.com | UNSUB |
| 3 | promote.weebly.com | UNSUB |
| 4 | e.swimoutlet.com | UNSUB |
| 5 | email.myflighthub.com | UNSUB |
| 6 | mail.urbanairparks.com | UNSUB |
| 7 | e.stantonoptical.com | UNSUB |
| 8 | lists.wikimedia.org | UNSUB |
| 9 | jongordon.com | UNSUB |
| 10 | atticbuddies.com | UNSUB |
| 11 | email.theparkingspot.com | UNSUB |
| 12 | academia-mail.com | UNSUB |
| 13 | suzeorman.com | UNSUB |
| 14 | marketing.goindigo.in | UNSUB |
| 15 | deeplearning.ai | UNSUB |
| 16 | gamemail.com | UNSUB |
| 17 | accounts.google.com | DELETE only (no unsub) |

Workflow per domain:

1. Search bar: `from:<domain>`
2. Click any one email → scroll to the unsubscribe link at the top (Gmail auto-extracts it) → Unsubscribe → Confirm.
3. Back to search → "Select all" → "Select all conversations matching this search" → Delete (trash icon).
4. Move to next domain.

> **Skip unsubscribe for #17** — Google account notifications have no unsubscribe; just delete historical ones and ignore going forward.

### A3. 30-day archive sweep (10 min)

1. Search: `in:inbox older_than:30d -label:awaiting-reply -is:starred -label:CRE`
2. Select all → Select all conversations → Archive.

This leaves only: recent (< 30 days), things you starred, things you explicitly marked awaiting-reply, and the CRE label (already skipped inbox but just being explicit).

### A4. VIP pin (5 min — optional)

For the 5-10 clients/contacts you actually want to never miss:

1. Create filter → `From: <vip@domain>` → Star it + Apply label: **VIP** + Never mark as spam.

## Part B — achantav account (10-15 min)

### B1. Marketing sweep

Run the same noise-domain workflow from A2 adapted to whatever newsletters flood this account (the ace config is account-specific). Common candidates — search each, unsub + bulk delete if noise:

- `from:(newsletter OR marketing OR promo OR deals OR noreply)` — eyeball what's there; unsub the obvious marketing.

### B2. Self-forward cleanup

Per #1990 history: you often forward from personal → ace. Search:

```
from:achantav@gmail.com to:vamsee.achanta@aceengineer.com
```

…in the **ace** account (Part A accidentally missed). If these are all "shuttle" forwards, bulk-delete; the content is elsewhere.

### B3. 30-day archive

Same as A3: `in:inbox older_than:30d -is:starred` → archive.

## Part C — skestates account (5 min)

Low volume. Just:

1. Search: `in:inbox older_than:60d -label:awaiting-reply -is:starred` → archive.
2. If any tenant/vendor pattern shows repeated noise (unlikely), add to a `skestates-noise-domains.yaml` equivalent.

## Post-sweep

- [ ] Take a screenshot of unread counts (3 accounts) — baseline for "normal use."
- [ ] Set calendar reminder: re-run this checklist weekly until #2423 lands.
- [ ] If any new noise domain appears more than twice in a week, append to `config/email-filters/ace-noise-domains.yaml` and commit.

## What this does NOT do

- Does **not** replace #2017's queue state machine (local tracking of actionable threads).
- Does **not** extract data from CRE / tax / invoice emails — that's #2024's job.
- Does **not** set up auto-reply drafts — #2423 territory.
- Does **not** touch the contact databases (`aceengineer-admin/admin/contacts/`) — already normalized via #1965/#1966/#1967.

## Exit criteria

Inbox is "clean, caught up for normal use" when:

- All three accounts show < 20 unread at any given moment.
- Inbox view contains only last-30-days + awaiting-reply + starred.
- CRE, marketing, and system notifications are labeled out of the inbox view.
- Any new noise domain gets surfaced and added to the YAML within a week, not a month.

## Handoff to automation

When #2423 lands with Gmail-side mutation:

1. The `batch-unsubscribe.sh` script can run over `ace-noise-domains.yaml` end-to-end without the UI steps in A2.
2. The filter in A1 becomes a YAML routing rule in `email-routing.yaml` instead of a Gmail-side filter.
3. The archive-sweeps in A3/B3/C1 become a cron job keyed off thread state (#2026 grace period).

Until then, this checklist is the manual bridge.
