---
name: gmail-triage
description: Daily multi-account Gmail inbox triage — scan unread, classify by urgency, cross-reference contacts, generate actionable digest. Supports ace/personal/skestates accounts.
version: 1.0.0
author: vamsee
tags: [email, gmail, triage, digest, automation]
related_skills: [gmail-multi-account, himalaya, gmail-unsubscribe, gmail-touchbase]
metadata:
  hermes:
    tags: [email, gmail, triage, digest]
    related_skills: [gmail-multi-account, himalaya]
---

# Gmail Triage

Scan all 3 Gmail accounts, classify emails, cross-reference contacts, and produce an actionable digest.

## Prerequisites

- himalaya configured with 3 accounts (see `gmail-multi-account` skill)
- Contact CSVs available in respective repos

## Triage Workflow

### Step 1: Scan all inboxes

```bash
for acct in ace personal skestates; do
  echo "=== $acct ==="
  himalaya --account $acct envelope list --page-size 50 --output json
done
```

### Step 2: Classify each email

Categories (priority order):
1. **URGENT** — from VIP/client contacts, contains "urgent", "asap", "deadline", invoice/payment
2. **ACTIONABLE** — requires response, question asked, meeting request, RFP
3. **FYI** — informational, no action needed, CC'd
4. **NEWSLETTER** — marketing, subscription content, bulk sender
5. **SPAM** — unknown sender, no contact match, suspicious

### Step 3: Cross-reference contacts

For each sender:
1. Search contact CSV for the account
2. If found: use contact category (client/vendor/recruiter/personal)
3. If NOT found: flag as "unknown sender" — recommend add-to-contacts or unsubscribe

### Step 4: Generate digest

Format:
```
=== GMAIL DAILY DIGEST — {date} ===

[ACE] vamsee.achanta@aceengineer.com
  URGENT (2):
    - From: client@company.com | Subject: RFP Response Deadline
    - From: vendor@co.com | Subject: Invoice #1234 Past Due
  ACTIONABLE (3):
    - ...
  FYI (5): [collapsed]
  NEWSLETTER (12): [collapsed, unsubscribe candidates marked]

[PERSONAL] achantav@gmail.com
  ...

[SKESTATES] skestatesinc@gmail.com
  ...

=== RECOMMENDED ACTIONS ===
1. Reply to client@company.com RE: RFP (ACE)
2. Review invoice from vendor@co.com (ACE)
3. Unsubscribe from 8 newsletters (PERSONAL)
4. Add 2 unknown senders to contacts or block
```

## Account-Specific Classification Rules

### ace
- VIP: anyone in GTM prospect list, active clients
- URGENT: anything from @ril.com, @dorisgroup.com, @mcdermott.com (known clients)
- NEWSLETTER: LinkedIn notifications, industry digests (keep subscribed but low priority)

### personal
- VIP: family (achanta*, @gmail.com family addresses)
- URGENT: banks, government, medical
- NEWSLETTER: aggressive unsubscribe candidates

### skestates
- VIP: TX_Rents@familydollar.com, leaseadministration@familydollar.com
- URGENT: insurance, tax, legal, tenant maintenance requests
- NEWSLETTER: real estate marketing (unsubscribe)

## Automation

This skill is designed to run as a cron job:

```
# Daily at 7 AM CT
0 7 * * * hermes "Load gmail-triage skill. Scan all 3 accounts and deliver digest."
```

Deliver to: Telegram or CLI local file at `~/.hermes/email-digests/`

## Pitfalls

1. himalaya JSON output can be large — use `--page-size` to limit
2. Contact CSV parsing: watch for malformed entries (angle brackets in email fields)
3. Don't auto-act on emails — digest is READ-ONLY, actions need user approval
4. Rate limit Gmail IMAP — space requests 1-2 seconds apart
5. Some emails have no From header — skip gracefully
