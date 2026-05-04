---
name: gmail-extract-and-clean
description: "DEPRECATED — superseded by gmail-extract-and-act. Extract emails from Gmail to /mnt/ace/<repo>/, archive to repos, commit, then delete. Uses archive-everything model."
version: 2.0.0
status: deprecated
superseded_by: gmail-extract-and-act
deprecation_reason: "Archives raw email bodies to repos. Per #2017, the new model extracts only structured data and deletes emails when topics complete (queue model, not archive model). See #2019 for consolidation plan."
author: vamsee
tags: [email, gmail, extraction, cleanup, archive, routing, DEPRECATED]
related_skills: [gmail-multi-account, contact-manager, gmail-extract-and-act]
metadata:
  hermes:
    tags: [email, gmail, extraction, cleanup]
---

# Gmail Extract and Clean

Extract emails from Gmail into the correct `/mnt/ace/<repo>/doc/email/` location, commit to the workspace-hub external repo, then optionally delete from Gmail inbox.

## Architecture

```
Gmail Inbox (3 accounts: ace, personal, skestates)
    ↓ extract + classify + route
/mnt/ace/<repo>/docs/email/     ← data lands here
    ↓ (samba share — no git here)
/mnt/local-analysis/workspace-hub/<repo>/  ← git lives here
    ↓ commit + push
Gmail message deleted from inbox
```

## Key Finding: /mnt/ace/ Has No Git

The `/mnt/ace/` directory contains samba share copies of external_dir repos. These have NO `.git` directories. The actual git repos live at `/mnt/local-analysis/workspace-hub/<repo>/` (which includes `<repo>` as a subdirectory).

**Critical: Always commit via the workspace-hub path, not /mnt/ace/ path.**

## Routing Rules

Email routing is defined in `scripts/email/email-routing.yaml` (workspace-hub repo):

```yaml
rules:
  "familydollar.com"     → "sabithaandkrishnaestates/docs/email/tenant"
  "sandsig.com"          → "assethold/data/sandsig-cre-listings/email"
  "github.com"           → "achantas-data/docs/email/dev-notifications"
  "collide.io"           → DELETE          # spam — just delete, don't archive
  "indianstarllc.ccsend.com" → REVIEW      # needs manual review
  "default"              → "achantas-data/docs/email/other"
```

Actions: `<repo/path>` = archive to that repo, `DELETE` = remove without archiving, `REVIEW` = flag for manual review.

## Usage

### Batch extraction with delete
```bash
cd /mnt/local-analysis/workspace-hub
uv run scripts/email/gmail-archive-extract.py --account ace --query "from:sandsig.com" --max 500 --delete --no-sheets
```

### Dry run (see what would happen)
```bash
uv run scripts/email/gmail-archive-extract.py --account personal --query "from:promote.weebly.com" --max 100 --dry-run
```

### Extract without deleting (safe first pass)
```bash
uv run scripts/email/gmail-archive-extract.py --account ace --query "from:dorisgroup.com" --max 100
```

### After extraction: sync to workspace-hub repos and commit
```bash
# The script writes to /mnt/ace/<repo>/ — sync to git repos:
cd /mnt/local-analysis/workspace-hub/assethold
rsync -a /mnt/ace/assethold/data/ data/
count=$(ls data/sandsig-cre-listings/email/*.md 2>/dev/null | wc -l)
git add -f data/
git commit -m "extract: ace email — $count messages archived, deleted from inbox"
git push origin main
```

## OAuth Token Expiration

OAuth access tokens expire every ~1 hour. The extraction script refreshes tokens on every run using the refresh_token stored at `~/.gmail-{account}/credentials.json`. Client ID/secret loaded from `~/.gmail-mcp/oauth-env.json`.

## Rate Limiting

The script sleeps 0.15s per message. Batch processing 500 messages takes ~80-170 seconds. For large cleanup, run in batches of 100-200.

## Contact Data

Before extracting, ensure contact CSVs are normalized:
- `aceengineer-admin/admin/contacts/aceengineer_normalized.csv` (1,281 contacts)
- `aceengineer-admin/admin/contacts/achantav_normalized.csv` (994 contacts)
- `sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv` (25 contacts)

Use `contact-manager` skill for normalization.

## Email Account Handling

Each account has different cleanup priorities:
- **ace**: Extract client emails (doris, mcdermott, shell, etc.) → their repos. Extract CRE market data → assethold. Delete spam/newsletters.
- **personal**: Delete spam aggressively (promote.weebly.com, swimoutlet, wikimedia, etc.). Archive personal docs → achantas-data. School/parent emails → keep.
- **skestates**: Almost everything is valuable (tenant, insurance, tax). Archive all → sabithaandkrishnaestates docs.

## Deletion Without Archiving

Some domains are pure spam — safe to delete without extracting:
- collide.io, skylineseven.ccsend.com, promote.weebly.com, e.swimoutlet.com
- email.myflighthub.com, mail.urbanairparks.com, e.stantonoptical.com
- lists.wikimedia.org, jongordon.com, academia-mail.com, suzeorman.com
- atticbuddies.com, email.theparkingspot.com, marketing.goindigo.in

## Spreadsheet Parsing

If emails have .xlsx attachments, the script parses them to CSV automatically:
- Requires `openpyxl` installed (`uv pip install --system openpyxl`)
- CSVs saved to `<repo>/spreadsheets/`
- Use `--no-sheets` flag to skip for speed

## Pitfalls

1. `/mnt/ace/<repo>/` has no `.git` — always commit via `/mnt/local-analysis/workspace-hub/<repo>/`
2. OAuth tokens expire hourly — script auto-refreshes, but very long runs may fail
3. Gmail API search estimates cap at ~201 for free tier — use actual message ID pagination for true counts
4. Legal scan (.legal-deny-list.yaml) blocks emails containing protected client names — these are skipped, not deleted
5. The script extracts to `/mnt/ace/` but you must rsync to workspace-hub for git tracking
6. Delete only works on messages in the inbox — archived/starred messages need separate queries
