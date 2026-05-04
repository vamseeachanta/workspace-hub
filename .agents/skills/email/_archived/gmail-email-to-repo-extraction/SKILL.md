---
name: gmail-email-to-repo-extraction
description: Extract structured data from Gmail inbox emails, enrich with domain-specific
  classification, legal-scan against deny list, commit to appropriate repo, then optionally
  delete originals.
version: 1.0.0
author: vamsee
tags:
- email
- gmail
- data-extraction
- repo-commit
- legal-scan
- cleanup
related_skills:
- gmail-multi-account
- legal-sanity-scan
metadata:
  hermes:
    tags:
    - email
    - gmail
    - data-extraction
    - legal-scan
    related_skills:
    - gmail-multi-account
---

# Gmail Email → Repo Extraction

Pattern for extracting structured data from inbox emails, saving to repos, then cleaning up.

## Workflow

### Phase 1: Scan & Categorize

```bash
# 1. Refresh OAuth token
# 2. Search inbox for target sender(s)
# 3. Fetch message metadata for all matches
# 4. Categorize by sender domain:
#    - extract_then_delete: valuable data, extract first
#    - unsubscribe_then_delete: spam/marketing, just delete
#    - keep: dev notifications, critical services
#    - review: needs user decision before action
```

### Phase 2: Extract Structured Data

For data extraction emails (e.g., CRE listings, financial reports):

```python
def extract_enums(subject, body, sender):
    """Extract from subject line patterns first (reliable)"""
    # Cap rates from subject: r'(\d+\.?\d*)\s*%?\s*CAP'
    # Prices from subject: r'\$(\d+(?:\.\d+)?[KMB]?)'
    # SF from subject: r'([\d,]+)\s*SF'
    # Lease years: r'(\d+)\s*(?:Years?|Yr)'
    pass

def extract_from_body(body):
    """Body text is noisy — footers, multi-state refs, signatures"""
    # Only use body for state/province extraction when subject lacks location
    # Use regex patterns for known field types
    pass

def enrich_listing(listing):
    """Add inferred fields: lease_type, investment_grade, property_types, state"""
    pass
```

**Key finding:** Subject line regex extraction is reliable. Body text is noisy due to corporate footers, multi-state operator portfolios, and email signatures.

### Phase 3: Legal Scan

```bash
cd /mnt/local-analysis/workspace-hub
bash scripts/legal/legal-sanity-scan.sh
# OR programmatically:
# Load .legal-deny-list.yaml → scan all extracted text → zero matches required
```

**Must pass before any commit.** Check extracted text + metadata against all deny patterns.

### Phase 4: Commit to Repo

```bash
# Target repo based on data domain:
# - O&G/CRE data → assethold/ or worldenergydata/
# - Business docs → aceengineer-admin/
# - Personal/family → achantas-data/
# - Real estate → sabithaandkrishnaestates/

cd <target-repo>/
git add data/
git commit -m "feat: {source} dataset — {N} records, legal scan passed (#{issue})"
git push origin main
```

Files to include:
- `listings.json` — raw extracted data
- `listings_enriched.json` — with inferred fields
- `listings.csv` — tabular format
- `market_analysis.json` — aggregated statistics
- `README.md` — documentation with dataset description, stats, legal scan status

### Phase 5: Delete from Gmail (after confirmation)

```python
def batch_delete(msg_ids, token, batch_size=25):
    """Delete messages in batches"""
    for mid in msg_ids:
        gmail_delete(mid, token)
```

**Safety rules:**
1. Only delete after data is committed and pushed to repo
2. User must approve delete list before execution
3. Keep messages from VIP/known contacts
4. Process unsubscribe candidates first (less risky)

## Known Sender Actions

Maintained dictionary mapping domains to actions:

```python
ACTIONS = {
    # CRE marketplaces — extract data first
    "sandsig.com": "extract_then_delete",
    "marcusmillichap.com": "extract_then_delete",
    "email.loopnet.com": "extract_then_delete",
    "ten-x.ccsend.com": "extract_then_delete",
    
    # Marketing/promo — unsubscribe then delete
    "collide.io": "unsubscribe_then_delete",
    "promote.weebly.com": "unsubscribe_then_delete",
    "lists.wikimedia.org": "unsubscribe_then_delete",
    "e.swimoutlet.com": "unsubscribe_then_delete",
    "email.myflighthub.com": "unsubscribe_then_delete",
    
    # Keep (valuable notifications)
    "github.com": "keep",
    "openrouter.ai": "keep",
    
    # Review before action
    "substack.com": "review",
    "rigzonemail.com": "review",
    "info.marineinsight.com": "review",
}
```

Expand this dictionary with experience. Use sender domain + List-Unsubscribe header to auto-classify unknown senders.

## Gmail API Notes

### OAuth Token Refresh
```python
def refresh(acct):
    cred = os.path.expanduser(f"~/.gmail-{acct}/credentials.json")
    with open(cred) as f:
        saved = json.load(f)
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "refresh_token": saved["refresh_token"], "grant_type": "refresh_token",
    }).encode()
    # POST to https://oauth2.googleapis.com/token
    # Update saved['access_token'] and save back
```

### List vs Get
- `list` returns `messages[]` with `id`, `threadId`, `resultSizeEstimate`
- `get` with `format=metadata` returns headers without body (fast)
- `get` with `format=full` returns full message (slow, use only for body extraction)

### Delete
```python
req = urllib.request.Request(
    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}",
    headers={"Authorization": f"Bearer {token}"}, method="DELETE")
urllib.request.urlopen(req, timeout=30)
```

### Draft Threading
To create a draft reply in an existing thread:
1. Get the thread's last message ID
2. Set `In-Reply-To` and `References` headers
3. Use `threadId` in the draft API body
4. Keep exact same subject line

### Attachment Download
```python
# Find attachment ID from full message payload
req = urllib.request.Request(
    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}/attachments/{attachment_id}",
    headers={"Authorization": f"Bearer {token}"})
data = json.loads(urllib.request.urlopen(req).read())
file_data = base64.urlsafe_b64decode(data["data"])
```

## Pitfalls

1. **State extraction from body is noisy** — corporate footers, multi-state operators, contact addresses all trigger false matches. Prefer subject line patterns for location data.
2. **Gmail category queries (`category:promotions`) may return 0** — the API sometimes doesn't return estimates for category filters. Use sender-domain-based scanning instead.
3. **OAuth tokens expire every hour** — always refresh before batch operations. For large operations, refresh periodically during processing.
4. **Sandbox state loss** — each code execution is a fresh sandbox. Don't rely on state between calls. Always re-auth tokens at the start of each script.
5. **List-Unsubscribe header is more reliable than email pattern matching** — some marketing emails don't use "unsubscribe" in the sender address but do have the header.
6. **Legal deny list is domain-specific** — the `.legal-deny-list.yaml` checks for offshore engineering client references. CRE listing data from Sands IG is public market info and won't match. Always run the scan regardless.
7. **Don't batch-delete without first confirming extract-then-delete is complete** — order matters: extract → commit → push → delete.
