---
name: gmail-extract-archive
description: "DEPRECATED — superseded by gmail-extract-and-act. Extract Gmail data into archive repo, parse attachments, legal scan, then delete. Uses archive-everything model."
version: 2.0.0
status: deprecated
superseded_by: gmail-extract-and-act
deprecation_reason: "Archives raw email bodies to repos. Per #2017, the new model extracts only structured data and deletes emails when topics complete (queue model, not archive model). See #2019 for consolidation plan."
author: vamsee
tags: [email, gmail, extraction, archive, cleanup, gmail-archive, DEPRECATED]
related_skills: [gmail-multi-account, gmail-triage, contact-manager, legal-sanity-scan]
metadata:
  hermes:
    tags: [email, gmail, extraction, archive, cleanup]
    related_skills: [gmail-multi-account, gmail-triage, contact-manager, legal-sanity-scan]
---

# Gmail Extract & Archive Pipeline

Extract Gmail messages into `~/gmail-archive/` — a dedicated private repo as the single source of truth for all email data. Every message → markdown. Every attachment → saved. Every spreadsheet → parsed to CSV. Legal scan mandatory. Delete from inbox after successful archive.

## Prerequisites
- gmail-multi-account skill configured (3 accounts with OAuth tokens)
- `~/gmail-archive/` repo exists (created via `gh repo create vamseeachanta/gmail-archive --private`)
- openpyxl installed in repo: `uv pip install openpyxl pyyaml`
- Deny-list copied: `config/deny-list.yaml` from workspace-hub

## Repo Structure
```
gmail-archive/
├── README.md                 # Archive conventions
├── config/
│   ├── accounts.yaml         # Account definitions (tokens external)
│   └── deny-list.yaml        # Legal scan patterns
├── data/
│   ├── {account}/
│   │   ├── messages/         # Individual .md extracts per message
│   │   ├── threads/          # Full thread .md extracts
│   │   ├── attachments/      # Downloaded files organized by thread
│   │   └── spreadsheets/     # Parsed JSON + CSV for each Excel
├── reports/
│   ├── digest/               # Daily digest outputs
│   └── cleanup/              # Cleanup tracking logs
└── scripts/
    └── extract.py            # Main extraction pipeline
```

## Extraction Commands

### Basic extraction (scan + preview)
```bash
cd ~/gmail-archive
uv run scripts/extract.py --account ace --query "from:sandsig.com in:inbox" --max 500 --dry-run
```

### Extract + save (no delete)
```bash
uv run scripts/extract.py --account ace --query "from:sandsig.com in:inbox" --max 500
```

### Extract + delete from Gmail
```bash
uv run scripts/extract.py --account ace --query "from:sandsig.com in:inbox" --max 500 --delete
```

### Extract full threads
```bash
uv run scripts/extract.py --account skestates --query "subject:1099 has:attachment" --threads --delete
```

### Force through legal violations
```bash
uv run scripts/extract.py --account personal --query "category:promotions" --max 1000 --delete --force
```

## Common Queries
| Purpose | Query |
|---------|-------|
| All inbox | `in:inbox -in:trash` |
| From specific domain | `from:sandsig.com` |
| With attachments | `has:attachment` |
| Specific thread | `subject:"2025 Form 1099-MISC"` |
| Old unread | `is:unread older_than:30d` |
| Spam-like | `subject:(unsubscribe OR no-reply)` |

## Key Learnings / Pitfalls

### 1. Headless OAuth limitation
The `gmail-mcp-multiauth` npm package requires a GUI browser for OAuth flow. On headless servers:
- Generate auth URL manually: `accounts.google.com/o/oauth2/v2/auth?access_type=offline&scope=https://www.googleapis.com/auth/gmail.modify+https://www.googleapis.com/auth/gmail.settings.basic&response_type=code&client_id={client_id}&redirect_uri=urn:ietf:wg:oauth:2.0:oob`
- Sign in via browser on another machine
- Extract authorization code from the page
- Exchange code for tokens via `https://oauth2.googleapis.com/token`
- Save tokens as `~/.gmail-{account}/credentials.json`

### 2. Token refresh
OAuth access tokens expire in 1 hour. Always refresh at runtime using the refresh_token in credentials.json:
```python
data = urllib.parse.urlencode({
    "client_id": ..., "client_secret": ...,
    "refresh_token": saved["refresh_token"], "grant_type": "refresh_token",
})
```

### 3. Legal scan is mandatory
Run against `config/deny-list.yaml` before every commit. Skip (don't archive) messages that match "block" patterns. Use `--force` only for known safe data.

### 4. Spreadsheet parsing
Gmail API returns attachments as base64. For spreadsheets:
1. Save the raw .xlsx to `spreadsheets/`
2. Parse with openpyxl: `wb = openpyxl.load_workbook(xlsx_path, data_only=True)`
3. Export each sheet to CSV: `ws.iter_rows(values_only=True)`
4. Also save full data as JSON for analysis

### 5. Category queries return 0
Gmail API `category:promotions` and similar queries may return 0 results via REST API even though the Gmail UI shows results. Use domain-based or sender-based queries instead: `from:collide.io OR from:promote.weebly.com OR from:e.swimoutlet.com`

### 6. Self-forwards are smaller than expected
The "personal→ace shuttle" pattern was estimated at 2,000-3,000 emails from sent-folder analysis. Actual count was only ~183. Most "shuttle" entries were brief notes ("FYI", "Print") without attachments, or were external emails received in the personal inbox, not actual file transfers.

## Account-Specific Patterns

### ace (vamsee.achanta@aceengineer.com)
- Sands IG CRE listings: `from:sandsig.com` → extract, parse property data, then delete
- Keep: github.com, openrouter.ai, substack.com (review), deeplearning.ai
- Delete: collide.io, promowebly.com, email.theparkingspot.com, etc.

### personal (achantav@gmail.com)
- Keep: parentsquare.com (school), github.com, em1.turbotax.intuit.com (tax)
- Delete: promote.weebly.com, e.swimoutlet.com, mail.urbanairparks.com, lists.wikimedia.org, etc.
- Review: rigzonemail.com, info.marineinsight.com, m.learn.coursera.org

### skestates (skestatesinc@gmail.com)
- Almost all emails are actionable business correspondence
- Sands IG CRE listings forwarded: extract, then delete
- Thread archive critical for tax/legal reference

## Data Flow After Extraction
Extracted data feeds into:
- `sabithaandkrishnaestates/docs/tax/` — tax documents, payment analyses
- `aceengineer-admin/admin/contacts/` — contact databases
- `assethold/data/` — CRE market intelligence
- `achantas-data/` — personal/family docs
