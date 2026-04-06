---
name: gmail-unsubscribe
description: Identify and batch-unsubscribe from newsletters and marketing emails across Gmail accounts. Scans List-Unsubscribe headers, generates candidates, executes with user approval.
version: 1.0.0
author: vamsee
tags: [email, gmail, unsubscribe, cleanup, automation]
related_skills: [gmail-multi-account, gmail-triage, himalaya]
metadata:
  hermes:
    tags: [email, gmail, unsubscribe, cleanup]
    related_skills: [gmail-multi-account, gmail-triage]
---

# Gmail Unsubscribe

Systematically identify and remove newsletter/marketing email subscriptions.

## Prerequisites

- himalaya configured (see `gmail-multi-account`)
- Contact CSVs with category tags

## Workflow

### Step 1: Identify newsletter senders

```bash
# Get recent emails, look for bulk senders
himalaya --account personal envelope list --page-size 200 --output json | \
  python3 -c "
import json, sys, collections
msgs = json.load(sys.stdin)
senders = collections.Counter(m.get('from','unknown') for m in msgs)
for sender, count in senders.most_common(50):
    if count >= 3:
        print(f'{count:4d}  {sender}')
"
```

### Step 2: Check List-Unsubscribe headers

```bash
# Export raw MIME to check headers
himalaya --account personal message export MESSAGE_ID --full | \
  grep -i "list-unsubscribe"
```

### Step 3: Classify unsubscribe candidates

Criteria for unsubscribe:
- Sender appears 3+ times in last 200 emails
- Sender NOT in VIP/client/personal contacts
- Has List-Unsubscribe header
- Content is marketing/promotional/newsletter

DO NOT unsubscribe from:
- Transactional emails (receipts, shipping, account security)
- Industry newsletters user values (check with user)
- Government/financial institution communications

### Step 4: Execute unsubscribe

For mailto: unsubscribe links:
```bash
cat << 'EOF' | himalaya --account personal template send
From: achantav@gmail.com
To: unsubscribe-address@sender.com
Subject: Unsubscribe

Unsubscribe
EOF
```

For URL unsubscribe links:
- Present URL to user to click manually (security — don't auto-click links)

### Step 5: Clean up

After unsubscribe confirmation:
```bash
# Move old newsletters to trash
himalaya --account personal message delete MESSAGE_ID
```

## Account-Specific Aggressiveness

### ace — Conservative
- Keep: industry digests (SPE, OTC, offshore), technical newsletters
- Unsubscribe: vendor marketing, recruiter spam
- Ask user about: LinkedIn notifications, conference promos

### personal — Aggressive
- Unsubscribe: social media notifications, shopping promos, app notifications
- Keep: banking alerts, subscription receipts, family-related
- Ask user about: news digests, hobby newsletters

### skestates — Moderate
- Unsubscribe: real estate marketing, property listing emails
- Keep: insurance, tax, legal, property management
- Ask user about: CRE investment newsletters

## Safety Rules

1. NEVER auto-unsubscribe without user approval — show candidate list first
2. NEVER click unsubscribe URLs programmatically — present to user
3. Log all unsubscribe actions to `~/.hermes/email-logs/unsubscribe-log.csv`
4. Batch limit: max 20 unsubscribes per session
5. Wait 24h after unsubscribe before deleting old messages (in case user reconsiders)

## Automation

Monthly sweep cron:
```
# First Monday of each month at 8 AM CT
0 8 1-7 * 1 hermes "Load gmail-unsubscribe. Scan personal account for new unsubscribe candidates. Report only — do not act."
```
