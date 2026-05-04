---
name: gmail-data-extraction
description: Extract structured data from Gmail emails using REST API (no pip dependencies). Covers inbox scanning, subject line regex extraction, email text parsing, thread-aware drafting, and legal-scan-before-commit workflow.
version: 1.0.0
author: vamsee
tags: [email, gmail, data-extraction, structured-data, legal-scan, gmail-api]
related_skills: [gmail-multi-account, gmail-triage, legal-sanity-scan, contact-manager]
metadata:
  hermes:
    tags: [email, gmail, data-extraction, structured-data, legal-scan]
    related_skills: [gmail-multi-account, gmail-triage]
---

# Gmail Data Extraction

Extract structured data from Gmail emails using the REST API directly.
No pip dependencies — stdlib only (urllib, json, base64, csv, re).

## OAuth Setup Prerequisites

- OAuth tokens stored in `~/.gmail-{account}/credentials.json`
- Client credentials in `~/.gmail-mcp/oauth-env.json`
- See `gmail-multi-account` skill for setup instructions

## Core Functions

### Token Refresh

```python
import json, urllib.request, urllib.parse, os

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
```

### Gmail API Requests

```python
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
```

### Search and Fetch

```python
token = refresh_token("ace")

# Search (use Gmail query syntax)
search = gmail_get(
    f"users/me/messages?q={urllib.parse.quote('from:sandsig.com is:unread')}&maxResults=500",
    token
)

# Fetch message details (metadata-only for fast listing)
for msg_stab in search.get("messages", []):
    detail = gmail_get(
        f"users/me/messages/{msg_stab['id']}?format=metadata"
        f"&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date",
        token
    )
    hdrs = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
```

### Extract Text Body from Full Email

```python
import base64

def extract_text_body(payload):
    """Recursively extract text/plain from MIME payload"""
    def walk(part):
        if part.get("body", {}).get("data"):
            decoded = base64.urlsafe_b64decode(
                part["body"]["data"]
            ).decode("utf-8", errors="replace")
            if part.get("mimeType") == "text/plain":
                return decoded
        for sub in part.get("parts", []):
            text = walk(sub)
            if text:
                return text
        return ""
    return walk(payload)
```

### Extract All Attachments from Email

```python
def find_attachments(payload):
    """Recursively find all attachments in MIME payload"""
    attachments = []
    def walk(part):
        filename = part.get("filename", "")
        body = part.get("body", {})
        if filename and body.get("attachmentId"):
            attachments.append({
                "filename": filename,
                "mimeType": part.get("mimeType", ""),
                "attachmentId": body.get("attachmentId"),
                "size": body.get("size", 0),
            })
        for sub in part.get("parts", []):
            walk(sub)
    walk(payload)
    return attachments
```

### Download Attachment by ID

```python
def download_attachment(msg_id, attachment_id, token):
    """Download attachment as raw bytes"""
    data = gmail_get(f"users/me/messages/{msg_id}/attachments/{attachment_id}", token)
    if data and "data" in data:
        return base64.urlsafe_b64decode(data["data"])
    return None
```

## Structured Data Extraction from Subject Lines

Use regex to extract common patterns from email subjects:

```python
import re

def extract_subject_data(subject):
    data = {}
    
    # Cap rate: "9.75% CAP", "7.00% CAP"
    cap = re.search(r'(\d+\.?\d*)\s*%?\s*CAP', subject, re.IGNORECASE)
    if cap: data["cap_rate"] = float(cap.group(1))
    
    # Price: "$800K", "$3.2M", "$500,000"
    price = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)', subject)
    if price:
        s = price.group(1).upper()
        if 'K' in s: data["price"] = float(s.replace('K','')) * 1000
        elif 'M' in s: data["price"] = float(s.replace('M','')) * 1000000
        else: data["price"] = float(s.replace(',', ''))
    
    # Building SF: "62,225 SF", "18,265 SF"
    sf = re.search(r'([\d,]+)\s*SF', subject, re.IGNORECASE)
    if sf: data["building_sf"] = int(sf.group(1).replace(',', ''))
    
    # Lease years: "15 Years Remaining", "10 Yr NNN"
    yrs = re.search(r'(\d+)\s*(?:Years?|Yr)(?:\s+Remaining)?', subject, re.IGNORECASE)
    if yrs: data["lease_years"] = int(yrs.group(1))
    
    # Vehicles per day: "72,000+ VPD"
    vpd = re.search(r'([\d,]+)\s*VPD', subject, re.IGNORECASE)
    if vpd: data["vehicles_per_day"] = int(vpd.group(1).replace(',', ''))
    
    # State abbreviation: "| FL |", "- TX"
    st = re.search(r'\|\s*([A-Z]{2})\s*\|', subject)
    if not st: st = re.search(r'-\s*([A-Z]{2})\b', subject)
    if st: data["state"] = st.group(1)
    
    # Split by pipe for sections (common in newsletter subjects)
    parts = [p.strip() for p in subject.split("|") if p.strip()]
    if parts: data["primary_subject"] = parts[0]
    if len(parts) > 1: data["secondary_info"] = " | ".join(parts[1:])
    
    return data
```

## Thread-Aware Draft Creation

To create a draft that threads with an existing conversation:

```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def create_threaded_draft(token, text_body, html_body, thread_id,
                            recipients, cc="", subject=""):
    # Get thread data for Message-ID history
    thread_data = gmail_get(f"users/me/threads/{thread_id}", token)
    all_msg_ids = []
    for m in thread_data.get("messages", []):
        m_hdrs = {h["name"]: h["value"] for h in m.get("payload",{}).get("headers",[])}
        mid = m_hdrs.get("Message-ID", "")
        if mid: all_msg_ids.append(mid)
    
    last_msg = thread_data["messages"][-1]
    last_hdrs = {h["name"]: h["value"] for h in last_msg.get("payload",{}).get("headers",[])}
    
    msg = MIMEMultipart("alternative")
    msg["To"] = recipients
    msg["Cc"] = cc
    msg["Subject"] = last_hdrs["Subject"]  # EXACT same subject
    msg["In-Reply-To"] = last_hdrs.get("Message-ID", "")
    msg["References"] = " ".join(all_msg_ids)
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    
    raw_b64 = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return gmail_post("users/me/drafts", token, {
        "message": {"threadId": thread_id, "raw": raw_b64}
    })
```

## Legal Scan Before Committing

ALWAYS scan extracted email content before committing data to git repos:

```python
import yaml

def legal_scan(text):
    """Return list of forbidden patterns found in text"""
    with open("/path/to/workspace-hub/.legal-deny-list.yaml") as f:
        deny = yaml.safe_load(f)
    
    hits = []
    text_lower = text.lower()
    for item in deny.get("client_references", []):
        pattern = item["pattern"]
        case_sensitive = item.get("case_sensitive", False)
        searchable = text_lower if not case_sensitive else text
        if (pattern.lower() if not case_sensitive else pattern) in searchable:
            hits.append(f"BLOCK: {pattern} - {item.get('description', '')}")
    return hits

# Usage
all_text = " ".join(extracted_emails)
hits = legal_scan(all_text)
if hits:
    for h in hits:
        print(h)
    # DO NOT COMMIT
else:
    print("Legal scan PASSED — safe to commit")
```

## Workflow: Extract Data → Scan → Save to Repo

```python
from pathlib import Path

def extract_and_save(account, query, output_dir, repo_path):
    """Full workflow: extract, scan, save"""
    token = refresh_token(account)
    
    # 1. Search
    search = gmail_get(
        f"users/me/messages?q={urllib.parse.quote(query)}&maxResults=500",
        token
    )
    
    # 2. Extract structured data
    listings = []
    for msg_stab in search.get("messages", []):
        detail = gmail_get(f"users/me/messages/{msg_stab['id']}?format=metadata", token)
        hdrs = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        data = extract_subject_data(hdrs.get("Subject", ""))
        data["date"] = hdrs.get("Date", "")
        data["subject"] = hdrs.get("Subject", "")
        listings.append(data)
    
    # 3. Legal scan
    all_text = " ".join(l.get("subject", "") for l in listings)
    hits = legal_scan(all_text)
    if hits:
        print(f"Legal scan FAILED: {hits}")
        return False
    
    # 4. Save
    os.makedirs(output_dir, exist_ok=True)
    import json
    with open(f"{output_dir}/listings.json", "w") as f:
        json.dump(listings, f, indent=2)
    
    # 5. Commit to repo
    # Commit to repo using subprocess (preferred over os.system)
    
    return True
```

## Pitfalls

1. Gmail API has rate limits (~250 req/sec/user) — batch requests, don't spam
2. `format=full` fetch is slow — use `format=metadata` for listing, `full` only for body/attachments
3. Base64 encoding is URL-safe variant — use `base64.urlsafe_b64decode`, not `base64.b64decode`
4. Token refresh must update the saved credentials.json — tokens expire in 1 hour
5. OAuth secrets must never be hardcoded — use env vars or `~/.gmail-mcp/oauth-env.json`
6. Subject line parsing is heuristic-only — many emails don't follow patterns
7. Thread ID from Gmail API is NOT the same as Message-ID — need both for threading
8. Attachment IDs are per-message — can't reuse across messages
9. Legal scan must run BEFORE git add — once committed, history contains the data
10. For large extraction (>500 messages), use pagination: add `pageToken` from previous response
