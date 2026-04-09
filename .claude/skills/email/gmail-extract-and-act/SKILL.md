---
name: gmail-extract-and-act
description: The email-as-queue workflow — extract structured data from emails, act on it, track thread state, and delete emails when topics complete. Email is transient; extracted data is persistent.
version: 1.0.0
author: vamsee
tags: [email, gmail, extract, queue, delete, structured-data, lifecycle]
related_skills: [gmail-triage, gmail-multi-account, contact-manager, legal-sanity-scan]
metadata:
  hermes:
    tags: [email, gmail, extract, queue]
    related_skills: [gmail-triage, gmail-multi-account]
---

# Gmail Extract and Act — Email-as-Queue Workflow

> **Core principle: Email is a QUEUE, not an ARCHIVE.**
> See GitHub #2017 for the full workflow design.

Extract structured data from emails, commit the data to repos, then delete the raw email from the inbox when the topic is complete. Do NOT save entire email bodies to git repos.

## Workflow

```
INBOUND EMAIL
    ↓
TRIAGE (gmail-triage skill scans + classifies)
    ↓
EXTRACT — pull structured data from subject/body/attachments
    ↓
COMMIT — save extracted data to repo (legal-scan first)
    ↓
TRACK STATE — label the thread: awaiting-reply | completed
    ↓
DELETE — remove email from inbox when topic is resolved
    ↓ (if new reply arrives)
RE-ACTIVATE — back to INBOUND
```

## Thread State Model

States tracked via Gmail labels + optional local state log:

| State | Gmail Label | Meaning |
|---|---|---|
| `inbox` | (no label) | New, untriaged |
| `extracted` | `wh-email/extracted` | Data pulled, awaiting reply or action |
| `awaiting-reply` | `wh-email/awaiting-reply` | You replied, waiting for other party |
| `completed` | `wh-email/completed` | Topic resolved, email marked for deletion |
| `noise` | `wh-email/noise` | Spam/newsletter, safe to delete |

### State Transitions

```
inbox → extracted    (after data extraction)
extracted → awaiting-reply  (after you send a response)
awaiting-reply → inbox      (when new reply arrives — re-activated)
awaiting-reply → completed  (topic resolved without further reply)
extracted → completed       (topic resolved, no reply needed)
completed → [DELETE]         (grace period passed, email deleted)
inbox → noise → [DELETE]     (spam/newsletter, no extraction needed)
```

### Grace Period Policy

- `completed` threads: 7-day grace period before deletion
- `noise` threads: delete immediately
- `awaiting-reply` threads: NEVER auto-delete
- If a new reply arrives during grace period: state reverts to `inbox`, grace timer resets

## Prerequisites

- OAuth tokens in `~/.gmail-{account}/credentials.json`
- Client credentials in `~/.gmail-mcp/oauth-env.json`
- `gmail-multi-account` skill configured
- `scripts/email/email-routing.yaml` with sender routes (see below)

## Email Routing Configuration

`scripts/email/email-routing.yaml` maps sender domains to extraction targets:

```yaml
rules:
  # ---- DELETE (noise, no extraction) ----
  "collide.io":                     DELETE
  "skylineseven.ccsend.com":        DELETE
  # ... full file has 100+ rules

  # ---- REVIEW (decide before acting) ----
  "substack.com":                   REVIEW
  # ...

  # ---- Extract to repos ----
  "familydollar.com":               "sabithaandkrishnaestates/data/tenant"
  "frontierdeepwater.com":          "frontierdeepwater/data/client"
  "engineeredcustomsolutions.com":  "aceengineer-admin/data/client-ecs"
  "sandsig.com":                    "assethold/data/cre-listings"
  # ... default → "achantas-data/data/other"
```

**Actions:**
- `<repo-path>` — Extract structured data to that repo subdirectory
- `DELETE` — Delete immediately, no extraction needed
- `REVIEW` — Flag for manual review, do not auto-delete

## Structured Data Extraction Templates

### CRE Listings (Sands IG, Marcus Millichap)
Extract from subject + body:
- property_name, tenant_name, address, state, price, cap_rate
- building_sf, lease_years, vehicles_per_day, sale_date, broker

### Client/Project Emails
- sender_name, sender_company, project_name, subject_category
- deliverable_type, deadline, action_required, reply_status

### Tenant Communications (SKEstates)
- store_number, issue_type, date_reported, resolution, vendor
- cost_estimate, insurance_claim_number

### Tax/Financial
- document_type (1099, K-1, etc.), entity, tax_year, amount
- due_date, filing_status

### Invoice/Payments
- invoice_number, vendor, amount, due_date, status
- payment_method, confirmed_date

## Implementation: Extraction Script Pattern

```python
import json, os, re, base64, urllib.request, urllib.parse, subprocess, yaml
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = "/mnt/local-analysis/workspace-hub"
SCRIPTS = os.path.join(WORKSPACE, "scripts")

def load_routing():
    with open(os.path.join(SCRIPTS, "email", "email-routing.yaml")) as f:
        return yaml.safe_load(f)

def refresh_token(acct):
    cfg_path = os.path.expanduser("~/.gmail-mcp/oauth-env.json")
    with open(cfg_path) as f:
        cfg = json.load(f)
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

def extract_headers(msg_id, token):
    detail = gmail_get(
        f"users/me/messages/{msg_id}?format=metadata",
        token
    )
    headers = {}
    for h in detail.get("payload", {}).get("headers", []):
        headers[h["name"]] = h["value"]
    return headers

def extract_body(payload):
    """Recursively extract text/plain body"""
    def walk(part):
        if part.get("body", {}).get("data"):
            decoded = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            if part.get("mimeType") == "text/plain":
                return decoded
        for sub in part.get("parts", []):
            text = walk(sub)
            if text:
                return text
        return ""
    return walk(payload)

def get_sender_domain(headers):
    frm = headers.get("From", "")
    match = re.search(r"@([^\s>]+)", frm)
    if match:
        return match.group(1).lower().rstrip(">").strip()
    return None

def ensure_git_repo(repo_name):
    """Ensure we're working in the correct repo path for git operations"""
    repo_path = os.path.join(WORKSPACE, repo_name)
    if not os.path.isdir(repo_path):
        # Clone external_dir if needed
        subprocess.run(
            ["git", "clone", f"https://github.com/vamseeachanta/{repo_name}.git", repo_path],
            capture_output=True
        )
    return repo_path

def commit_extracted_data(repo_path, data_path, records, message_suffix):
    """YAML dump records, legal scan, git add + commit + push"""
    os.makedirs(data_path, exist_ok=True)
    outfile = os.path.join(data_path, f"extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml")
    with open(outfile, "w") as f:
        import yaml
        yaml.dump(records, f, default_flow_style=False, allow_unicode=True)

    # Legal scan
    try:
        result = subprocess.run(
            ["bash", f"{WORKSPACE}/scripts/legal/legal-sanity-scan.sh", outfile],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"LEGAL SCAN FAILED for {outfile}: {result.stdout}")
            os.remove(outfile)
            return False
    except Exception as e:
        print(f"Legal scan error: {e}")
        return False

    # Git commit
    subprocess.run(["git", "add", outfile], cwd=repo_path)
    subprocess.run(
        ["git", "commit", "-m", f"extract: email data — {message_suffix}"],
        cwd=repo_path
    )
    subprocess.run(["git", "push"], cwd=repo_path)
    return True

def label_thread(thread_id, label_name, token):
    """Add a Gmail label to a thread for state tracking"""
    # Get or create the label
    label_name = f"wh-email/{label_name}"
    labels = gmail_get("users/me/labels", token)
    label_id = None
    for lbl in labels.get("labels", []):
        if lbl.get("name") == label_name:
            label_id = lbl["id"]
            break

    if label_id is None:
        new_label = gmail_post("users/me/labels", token, {
            "labelListVisibility": "labelHide",
            "messageListVisibility": "hide",
            "name": label_name
        })
        label_id = new_label["id"]

    # Apply to thread messages
    gmail_post(f"users/me/threads/{thread_id}/modify", token, {
        "addLabelIds": [label_id]
    })

def mark_for_deletion(msg_id, token):
    """Move message to trash"""
    gmail_post(f"users/me/messages/{msg_id}/trash", token, {})

def process_inbox_batch(account, query="is:unread", max_results=100, dry_run=False):
    """Main extraction loop for an inbox batch"""
    token = refresh_token(account)
    routing = load_routing()

    search = gmail_get(
        f"users/me/messages?q={urllib.parse.quote(query)}&maxResults={max_results}",
        token
    )

    stats = {"extracted": 0, "deleted": 0, "skipped": 0, "review": 0}

    for msg_stab in search.get("messages", []):
        headers = extract_headers(msg_stab["id"], token)
        domain = get_sender_domain(headers)

        if not domain:
            stats["skipped"] += 1
            continue

        # Find routing rule
        rule = routing.get("rules", {}).get(domain, routing["rules"].get("default"))

        if rule == "DELETE":
            if not dry_run:
                mark_for_deletion(msg_stab["id"], token)
            stats["deleted"] += 1
            continue

        if rule == "REVIEW":
            stats["review"] += 1
            continue

        # rule is a repo path
        repo_path = ensure_git_repo(rule.split("/")[0])
        data_path = os.path.join(repo_path, *rule.split("/")[1:])

        # Extract structured data from this message
        # (Implement per-domain extraction logic here)
        detail = gmail_get(f"users/me/messages/{msg_stab['id']}?format=full", token)
        body = extract_body(detail.get("payload", {}))
        thread_id = detail.get("threadId", "")

        record = {
            "date": headers.get("Date", ""),
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "thread_id": thread_id,
            "domain": domain,
            "snippet": body[:500] if body else "",
        }

        if not dry_run:
            ok = commit_extracted_data(repo_path, data_path, [record], f"{domain} data")
            if ok:
                label_thread(thread_id, "extracted", token)
                stats["extracted"] += 1
        else:
            stats["extracted"] += 1

    return stats
```

## Usage

### Dry run — see what would happen
```bash
cd /mnt/local-analysis/workspace-hub
# Modify gmail-archive-extract.py or use the pattern above
# with dry_run=True
```

### Extract CRE listings from Sands IG
```bash
process_inbox_batch("ace", "from:sandsig.com is:unread", max_results=200)
# → Extracts structured CRE data → assethold/data/cre-listings/
# → Labels threads as extracted
```

### Delete noise senders
```bash
process_inbox_batch("personal", "from:promote.weebly.com", max_results=500)
# → Marks noise for immediate deletion
```

### Check for completed threads ready for deletion
```bash
# Find messages with wh-email/completed label
# and delete if > 7 days old
process_inbox_batch("ace", "label:wh-email/completed older_than:7d", max_results=200)
```

### Re-activate on new reply
```bash
# Check for messages in wh-email/awaiting-reply that have new messages
process_inbox_batch("ace", "label:wh-email/awaiting-reply is:unread", max_results=50)
# → Re-labels as inbox, notifies user
```

## State Log (Local Tracking)

For robust state tracking beyond Gmail labels, maintain a local state file:

```yaml
# ~/.hermes/email-state.yaml
threads:
  - thread_id: "18f3a2b..."
    account: "ace"
    subject: "RFP Response for Pipeline Analysis"
    sender: "engineeredcustomsolutions.com"
    state: "awaiting-reply"
    extracted_to: "aceengineer-admin/data/client-ecs/"
    extracted_date: "2026-04-07"
    last_activity: "2026-04-07"
    reply_count: 3

  - thread_id: "18f3a2c..."
    account: "skestates"
    subject: "Family Dollar Store #30150 Maintenance"
    sender: "familydollar.com"
    state: "completed"
    extracted_to: "sabithaandkrishnaestates/data/tenant/"
    extracted_date: "2026-04-05"
    last_activity: "2026-04-05"
    reply_count: 2
    completed_date: "2026-04-06"
    eligible_for_deletion: "2026-04-13"
```

## Related Scripts

- `scripts/email/gmail-digest.py` — Daily inbox scan (cron at 12 PM CT)
- `scripts/email/email-routing.yaml` — Sender domain → extraction target mapping
- `scripts/email/contact-normalizer.py` — Contact database maintenance

## Superseded Skills (archived per #2019)

The following skills used the deprecated archive-everything model and have been moved to `_archived/`:
- `gmail-extract-and-clean` — archived (superseded by this skill)
- `gmail-extract-archive` — archived (superseded by this skill)
- `gmail-email-to-repo-extraction` — archived (merged into this skill)
- `gmail-data-extraction` — archived (code patterns incorporated here)

## Pitfalls

1. NEVER archive entire email bodies to repos — extract structured data only
2. Do NOT auto-delete threads that might receive replies — use completed state + grace period
3. Legal scan MUST run BEFORE git add/commit — once committed, data is in history
4. Gmail labels are case sensitive — use consistent `wh-email/` prefix
5. OAuth tokens expire every ~1 hour — the script refreshes automatically
6. /mnt/ace/ paths have no .git — always commit via /mnt/local-analysis/workspace-hub/
7. Thread re-activation: when a "completed" thread gets a new reply, check for unread and re-label
8. Grace period allows recovery — 7 days gives time to catch mistakes
9. The state log (~/.hermes/email-state.yaml) is the authoritative state tracker — Gmail labels are the visual indicator
10. When in doubt about deleting a thread, set it to REVIEW — never auto-delete without user approval for the first implementation run
