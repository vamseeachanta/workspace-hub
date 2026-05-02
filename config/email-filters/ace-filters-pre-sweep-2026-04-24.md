# Ace Account — Gmail Filters Baseline

**Captured:** 2026-04-24 via claude-in-chrome session
**Account:** vamsee.achanta@aceengineer.com
**Purpose:** Rollback marker before the 2026-04-24 filter-install sweep
**Source:** Gmail UI → Settings → Filters and Blocked Addresses (read live, not exported XML)

## Inbox unread baseline

| View | Unread |
|---|---|
| Inbox | 121 |
| Investments | 193 |
| Neighborhood | 446 |
| O&G Industry | 129 |
| Drafts | 5 |

## Critical setting

> **Inbox setting for important messages is set to "Override filters."**
> This means "Skip Inbox" filter rules will be ignored for messages Gmail's heuristic deems important.

This is the load-bearing reason why `collide.io` is already filtered yet still appears in `ace-noise-domains.yaml` as ongoing noise. **Recommend flipping to "No override" before adding new Skip-Inbox filters.**

## Existing filters (6)

| # | Match | Action | Notes |
|---|---|---|---|
| 1 | `subject:Late` | Skip Inbox + Never to Spam | Likely keeps overdue-payment alerts visible |
| 2 | `is:spam` | Delete it | Standard spam autopurge |
| 3 | `from:(collide.io)` | Apply label "O&G Industry" | **MISCONFIGURED** — collide.io is marketing per `ace-noise-domains.yaml` line 16; no Skip Inbox; mislabeled as O&G |
| 4 | `from:privateinvestorclub` | Skip Inbox + Apply label "Investments" | Drives the 193-unread Investments label |
| 5 | `from:(@frontierdeepwater.com)` | Star it + Mark as important | Client VIP — already good |
| 6 | `from:(nextdoor.com)` | Skip Inbox + Apply label "Neighborhood" | Drives the 446-unread Neighborhood label |

## Blocked senders (1)

- `Manikanta Sai <mani@imcsgroup.net>`

## Pre-existing labels (visible in sidebar)

- Investments (193 unread)
- Misc
- Neighborhood (446 unread)
- Notes
- O&G Industry (129 unread)
- Priority

## Rollback procedure

If the 2026-04-24 sweep needs to be undone:

1. Settings → Filters and Blocked Addresses
2. Delete any filter created on 2026-04-24 (anything not in the table above)
3. Manually un-label affected mail: `label:CRE OR label:AutoNoise OR label:Industry OR label:VIP` → Select all → Remove labels
4. Restore "Override filters" setting if it was changed

## Session log

This baseline is part of the manual-sweep + automated-filter session described in:
- `docs/plans/2026-04-24-gmail-manual-sweep-checklist.md`
- GitHub issue #2423 (Gmail-side mutation)
