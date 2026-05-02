# Archived Skill: `gmail-triage`

Original path: `/home/vamsee/.hermes/skills/email/gmail-triage`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/email/gmail-triage`
Consolidation date: 2026-04-29

---

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

## Core Principle: Email is a QUEUE, Not an ARCHIVE

Do NOT save all emails to repos. The workflow is:

```
INBOUND → TRIAGE → EXTRACT DATA → ACT → DELETE
                                      ↓
                          Topic completed? → DELETE email
                          Awaiting reply?  → KEEP (live)
                          New reply arrives → RE-ACTIVATE
```

Key rules:
1. Extract only structured DATA/information needed (not raw email bodies)
2. Delete the email when the topic is completed
3. Keep email alive when awaiting response from other party
4. When client/other party responds, the topic is live again
5. Learn from patterns — extraction and routing improve over time

See GitHub issue #2017 for the full workflow design.

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

## Gmail API Direct Usage Pattern (no dependencies)

For headless server automation, use the Gmail REST API directly with urllib (no pip deps).

Operational note from live triage:
- Prefer Gmail API for all three accounts when you need a fast, uniform inbox scan.
- In this environment, Himalaya is configured for `ace` and `personal`, but `skestates` is not present in `~/.config/himalaya/config.toml`.
- Shared OAuth client config lives at `~/.gmail-mcp/oauth-env.json`.
- Per-account refresh-token files live at:
  - `~/.gmail-ace/credentials.json`
  - `~/.gmail-personal/credentials.json`
  - `~/.gmail-skestates/credentials.json`
- Himalaya/IMAP can also emit repeated warning lines before JSON output, which makes machine parsing less reliable for quick triage. Gmail API metadata queries are cleaner for unread/latest-message summaries.

For live triage, fetch two slices per account:
1. `in:inbox is:unread newer_than:14d` for actionable unread work
2. `in:inbox newer_than:7d` for latest active threads even if already read

Then request message metadata with headers `From`, `To`, `Subject`, and `Date`, plus `snippet` and `labelIds`, to produce a compact digest without downloading full bodies.

```python
import json, os, urllib.request, urllib.parse, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# OAuth config (shared file, never hardcoded)
cfg_path = os.path.expanduser("~/.gmail-mcp/oauth-env.json")
with open(cfg_path) as f:
    cfg = json.load(f)

def refresh_token(acct):
    """Refresh access token using stored refresh token"""
    cred_path = os.path.expanduser(f"~/.gmail-{acct}/credentials.json")
    with open(cred_path) as f:
        saved = json.load(f)
    data = urllib.parse.urlencode({
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "refresh_token": saved["refresh_token"],
        "grant_type": "refresh_token",
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        tokens = json.loads(resp.read().decode())
    saved.update(tokens)
    with open(cred_path, "w") as f:
        json.dump(saved, f, indent=2)
    return tokens["access_token"]

def gmail_get(endpoint, token):
    req = urllib.request.Request(
        f"https://gmail.googleapis.com/gmail/v1/{endpoint}",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def gmail_post(endpoint, token, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"https://gmail.googleapis.com/gmail/v1/{endpoint}",
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

# Usage:
token = refresh_token("ace")
profile = gmail_get("users/me/profile", token)
messages = gmail_get(f"users/me/messages?maxResults=25&q=is:unread", token)
```

### Creating a Draft in an Existing Thread

To reply within an existing email chain (not create a new thread):

```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. Get the original thread's last message Message-ID
detail = gmail_get(f"users/me/threads/{thread_id}", token)
last_msg = detail["messages"][-1]
last_hdrs = {h["name"]: h["value"] for h in last_msg["payload"]["headers"]}
last_message_id = last_hdrs.get("Message-ID", "")

# 2. Build email with threading headers
msg = MIMEMultipart("alternative")
msg["To"] = "recipient@example.com"
msg["Subject"] = last_hdrs["Subject"]  # EXACT same subject
msg["In-Reply-To"] = last_message_id
msg["References"] = " ".join(all_message_ids_in_thread)  # all Message-IDs from thread
msg.attach(MIMEText(text_body, "plain"))
msg.attach(MIMEText(html_body, "html"))

# 3. Create draft WITH threadId
raw_b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
gmail_post("users/me/drafts", token, {"message": {"threadId": thread_id, "raw": raw_b64}})
```

### Extracting Structured Data from Email Subjects

Common CRE/business email patterns:

```python
import re

# Cap rate: "9.75% CAP", "7.00% CAP"
cap_match = re.search(r'(\d+\.?\d*)\s*%?\s*CAP', subject, re.IGNORECASE)

# Price: "$800K", "$3.2M", "$500,000"
price_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)', subject)

# Building SF: "62,225 SF", "18,265 SF"
sf_match = re.search(r'([\d,]+)\s*SF', subject, re.IGNORECASE)

# Lease years: "15 Years Remaining", "10 Yr NNN"
years_match = re.search(r'(\d+)\s*(?:Years?|Yr)(?:\s+Remaining)?', subject, re.IGNORECASE)

# Vehicles per day: "72,000+ VPD"
vpd_match = re.search(r'([\d,]+)\s*VPD', subject, re.IGNORECASE)

# State: "| FL |", "- TX"
state_match = re.search(r'\|\s*([A-Z]{2})\s*\|', subject)
```

### Legal Scan Before Committing Email Data

Always scan extracted email content before committing to git repos:

```python
import yaml

# Load deny list
with open("/path/to/workspace-hub/.legal-deny-list.yaml") as f:
    deny = yaml.safe_load(f)

# Scan all extracted text
all_text = " ".join(extracted_data).lower()
for item in deny.get("client_references", []):
    pattern = item["pattern"]
    case_sensitive = item.get("case_sensitive", False)
    searchable = all_text if not case_sensitive else " ".join(extracted_data)
    if (pattern.lower() if not case_sensitive else pattern) in searchable:
        # BLOCK — do not commit, flag for review
        raise ValueError(f"Protected client reference found: {pattern}")

# If no matches, safe to commit
```

## Practical retrieval notes (2026-04-09)

1. Himalaya v1.2 account selection is subcommand-local: use `himalaya envelope list -a ace ...`, not `himalaya --account ace ...`.
2. Himalaya JSON output may be polluted by IMAP warning lines (for example `Rectified missing text`) before the JSON payload, which breaks direct `json.loads(...)` parsing.
3. If clean machine-readable output is required, prefer the Gmail REST API with stored OAuth credentials instead of Himalaya IMAP.
4. In this environment, Gmail API OAuth is configured for all three accounts via:
   - `~/.gmail-ace/credentials.json`
   - `~/.gmail-personal/credentials.json`
   - `~/.gmail-skestates/credentials.json`
   - shared client config: `~/.gmail-mcp/oauth-env.json`
5. Himalaya config currently covers ace and personal only; skestates is better accessed via Gmail API unless Himalaya account config is added.
6. A robust triage pattern is:
   - use Gmail API for unread/latest metadata across all accounts
   - use Claude/delegate_task only for reasoning/summarization on the harvested metadata
   - keep final action output as a compact digest plus send-ready drafts

## Pitfalls

1. himalaya JSON output can be large — use `--page-size` to limit
2. Contact CSV parsing: watch for malformed entries (angle brackets in email fields)
3. Don't auto-act on emails — digest is READ-ONLY, actions need user approval
4. Rate limit Gmail IMAP — space requests 1-2 seconds apart
5. Some emails have no From header — skip gracefully
6. Do NOT archive entire email bodies to repos — extract structured data only (#2017)
7. Old skills (gmail-extract-and-clean, gmail-extract-archive) use the deprecated archive-everything model — use the queue model instead
8. Himalaya account selection is on the subcommand (`himalaya envelope list -a ace ...`), not top-level `himalaya --account ace ...`
9. Himalaya JSON output may be polluted by IMAP warning logs (for example `imap_codec::response` warnings) before the JSON payload, which breaks naive `json.loads(stdout)` parsing. If you need reliable machine-readable output, either strip leading log lines first or prefer Gmail API OAuth.
10. In this environment, Himalaya currently covers `ace` and `personal`, while `skestates` is available via Gmail API OAuth credentials only. For cross-account triage, prefer Gmail API OAuth for all three accounts to keep one consistent extraction path.

## Live triage + send-ready drafting pattern (2026-04-09)

When the user wants "latest work to be done" across all Gmail accounts and/or wants drafts prepared for reply:

1. Use Gmail API OAuth for all available accounts (`~/.gmail-ace/credentials.json`, `~/.gmail-personal/credentials.json`, `~/.gmail-skestates/credentials.json` plus `~/.gmail-mcp/oauth-env.json`) to fetch:
   - unread inbox items for triage
   - latest inbox items if unread is empty
   - metadata headers: From / To / Cc / Subject / Date / Reply-To
   - snippet text for quick classification
2. Use Claude/delegate workers to classify each account into:
   - true work items
   - newsletters/promotions/noise
   - recommended next actions
3. For business-critical threads, fetch the live Gmail thread metadata and at least one prior sent message body before drafting. This lets you recover:
   - exact recipients and CC list
   - canonical subject line to preserve thread continuity
   - signature block actually used before
   - factual details already stated in-thread (vendor IDs, dates, amounts, commitments)
4. Generate three deliverables, not just a summary:
   - action digest (priority-ranked work items)
   - send-ready drafts for each external thread
   - thread reply map with thread ID, subject, reply-vs-new guidance, recipients, and cautions
5. If the user is manually sending mail, also generate a copy-paste outbound packet with plain text `Subject`, `To`, `Cc`, and `Body` blocks.
6. Prefer replying in-thread for ongoing operational/tax/property issues unless there is a reason to deliberately break the thread.

This pattern worked well for mixed accounts where some inboxes were mostly marketing noise while one account (`skestates`) contained the real operational work.8. When using Himalaya in scripts, strip or suppress log lines before JSON parsing, or switch to Gmail API if reliability matters more than IMAP parity
