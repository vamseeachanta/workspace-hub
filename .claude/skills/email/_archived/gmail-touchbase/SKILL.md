---
name: gmail-touchbase
description: Periodic relationship maintenance via email — identify contacts due for outreach, draft personalized check-ins, queue for user approval. Supports per-account tone and cadence.
version: 1.0.0
author: vamsee
tags: [email, gmail, touchbase, networking, CRM, automation]
related_skills: [gmail-multi-account, gmail-triage, himalaya]
metadata:
  hermes:
    tags: [email, gmail, touchbase, networking, CRM]
    related_skills: [gmail-multi-account, gmail-triage]
---

# Gmail Touchbase

Maintain professional and personal relationships through periodic, thoughtful email outreach.

## Prerequisites

- himalaya configured (see `gmail-multi-account`)
- Contact CSVs with touchbase tags
- `~/.hermes/email-logs/touchbase-tracker.csv` (auto-created)

## Contact Tagging

Contacts must be tagged in their CSV with a `touchbase_cadence` field:

| Cadence | Meaning | Example |
|---|---|---|
| `monthly` | High-value relationship, regular check-in | Active clients, close colleagues |
| `quarterly` | Professional network maintenance | Former colleagues, industry peers |
| `biannual` | Loose ties, keep warm | Conference contacts, alumni |
| `none` | No proactive outreach | Vendors, newsletters, transactional |

## Workflow

### Step 1: Check touchbase tracker

```bash
# See who is overdue for outreach
cat ~/.hermes/email-logs/touchbase-tracker.csv
```

Format: `email,name,account,cadence,last_contact,next_due`

### Step 2: Scan sent folders for last interaction

```bash
# Check when we last emailed someone
himalaya --account ace envelope list --folder "Sent" --output json | \
  python3 -c "
import json, sys
msgs = json.load(sys.stdin)
for m in msgs:
    if 'target@email.com' in m.get('to',''):
        print(f\"{m['date']} — {m['subject']}\")
        break
"
```

### Step 3: Draft touchbase emails

Per-account tone templates:

#### ace (Professional/Engineering)
```
Subject: Checking in — {topic/project reference}

Hi {FirstName},

Hope things are going well. I was {thinking about our conversation / reading about X in the industry / working on a project similar to Y} and thought of you.

{Personalized detail — reference shared project, industry event, mutual connection}

Would love to catch up sometime. Let me know if you have 15 minutes for a quick call.

Best regards,
Vamsee Achanta, P.E.
ACE Engineer Consulting
```

#### personal (Casual/Warm)
```
Subject: Hey {FirstName} — long time!

Hey {FirstName},

Been a while! Just wanted to check in and see how things are going.

{Personal detail — reference family, shared hobby, last conversation topic}

Let's catch up soon — coffee/call/lunch sometime?

Best,
Vamsee
```

#### skestates (Business/Formal)
```
Subject: {Topic} — SKEstates Inc

Dear {FirstName},

I wanted to follow up regarding {specific business matter}.

{Business-relevant detail}

Please let me know if you need anything from our side.

Best regards,
SKEstates Inc
skestatesinc@gmail.com
```

### Step 4: Queue for approval

NEVER send touchbase emails automatically. Always:
1. Present draft to user
2. Wait for approval/edits
3. Send only after explicit "send it" confirmation

### Step 5: Update tracker

After sending:
```bash
# Log the touchbase
echo "target@email.com,FirstName LastName,ace,quarterly,$(date +%Y-%m-%d),$(date -d '+3 months' +%Y-%m-%d)" >> ~/.hermes/email-logs/touchbase-tracker.csv
```

## Touchbase Candidates by Account

### ace — Engineering Network
Priority contacts:
- Former colleagues at DORIS, McDermott, Trendsetter, etc.
- GTM prospect pipeline (link to aceengineer-strategy/)
- SPE/OTC conference connections
- Cadence: monthly for active prospects, quarterly for network

### personal — Personal Network
Priority contacts:
- Close friends and family (check, don't email — text/call better)
- Alumni network (TAMU)
- Career mentors/mentees
- Cadence: quarterly for professional, biannual for loose ties

### skestates — Business Contacts
Priority contacts:
- Property management contacts
- Tax advisor, CPA, attorney
- Insurance agent
- Cadence: quarterly for advisors, biannual for others

## Automation

Weekly reminder cron:
```
# Every Monday at 8 AM CT
0 8 * * 1 hermes "Load gmail-touchbase. Check touchbase tracker for overdue contacts this week. Report who needs outreach — do not draft or send."
```

## Pitfalls

1. NEVER send without user approval — touchbase is relationship-critical
2. Don't touchbase people who recently emailed us — check inbox first
3. Personalization is key — generic "just checking in" emails are worse than none
4. Respect unsubscribe: if someone doesn't reply to 2 consecutive touchbases, reduce cadence
5. Don't touchbase clients with active billing disputes
6. Track all outreach in CSV to avoid double-contacting
