---
name: gmail-multi-account
description: Multi-account Gmail management via himalaya CLI. Three accounts (aceengineer, achantav, skestates) with distinct triage rules, contact DBs, and tone profiles. Foundation skill for email automation.
version: 1.0.0
author: vamsee
tags: [email, gmail, himalaya, multi-account, triage]
related_skills: [himalaya, google-workspace, gmail-triage, gmail-outreach, gmail-extract-and-act]
metadata:
  hermes:
    tags: [email, gmail, himalaya, multi-account]
    related_skills: [himalaya, google-workspace]
---

# Gmail Multi-Account Management

Three Gmail accounts managed from CLI via himalaya. Each account has distinct purpose, contacts, and handling rules.

## Accounts

| Alias | Email | Purpose | Contacts Repo |
|---|---|---|---|
| `ace` | vamsee.achanta@aceengineer.com | Engineering consulting, GTM, clients | aceengineer-admin |
| `personal` | achantav@gmail.com | Personal, networking, subscriptions | aceengineer-admin |
| `skestates` | skestatesinc@gmail.com | Real estate LLC, tenant/vendor | sabithaandkrishnaestates |

## Architecture Decision (April 2026)

### Tool Assessment Results (7 approaches evaluated)

| Tool | Downloads | Multi-Acct | Unsubscribe | Verdict |
|---|---|---|---|---|
| gmail-mcp-multiauth (npm) | 931/mo | YES (3 named servers) | NO (custom headers) | **WINNER — npm install** |
| @gongrzhe/gmail-mcp-autoauth | 381K/mo | NO (single) | NO | Rejected — single account |
| @shinzolabs/gmail-mcp | 5.6K/mo | Limited | NO | Rejected — complex auth |
| workspace-mcp (taylorwilsdon) | 2K stars | YES (OAuth 2.1) | NO | Rejected — overkill |
| himalaya CLI | N/A | YES native | NO (IMAP flags) | **FALLBACK — cron/scripts** |
| himalaya-mcp (Data-Wise) | 0 stars | YES | NO | Rejected — too many layers |
| google-workspace DIY | N/A | YES | YES (custom) | Rejected — high maintenance |

### Setup Architecture

**Primary:** gmail-mcp-multiauth (npm) for MCP tool access
- `npm install -g gmail-mcp-multiauth` (installed, 15s setup)
- Requires: GCP project + Gmail API enabled + OAuth Desktop App credentials
- Each account gets named MCP server: `gmail-ace`, `gmail-personal`, `gmail-skestates`
- Auth: OAuth2 browser flow per account (one-time, tokens persist with refresh)
- GCP project name: "Hermes Gmail Automation" (or user-provided)

**Fallback:** himalaya CLI (installed v1.2.0, Linux musl x86_64)
- `curl -sSL .../install.sh | PREFIX=~/.local sh` (installed, 30s setup)
- Auth: Gmail App Passwords (2FA required, Settings → App Passwords)
- Config: `~/.config/himalaya/config.toml` (TOML format)
- Uses `backend.auth.cmd` to read passwords from files (NOT keyring)
- Config syntax changed significantly in v1.x — don't use old v0 config docs

### Critical Config Gotcha (v1.2.0)
The himalaya v1.2.0 config schema is NOT compatible with v0 docs. Key differences:
- No `backend.auth.keyring` or `backend.auth.type = "cmd"` syntax
- Use `backend.auth.cmd = "cat /path/to/secret"` directly under account
- No `message.send.backend.*` — use `message.send.type`, `message.send.host`, etc.
- The account block is flat: `[accounts.name]` with keys directly inside
- Test connection: `himalaya envelope list --account ace --page-size 1`

### Credential Files
- Config: `~/.config/himalaya/config.toml` (created)
- Secret files: `~/.config/himalaya/.secret_{ace,personal,skestates}` (created, chmod 600)
- OAuth state: stored by gmail-mcp-multiauth per-account in `~/.gmail-mcp/` or similar

### Unsubscribe Gap
No MCP server or himalaya command has native List-Unsubscribe support.
Must parse headers manually: `himalaya message export ID --full | grep -i list-unsubscribe`
For gmail-mcp-multiauth: use the raw message body parsing tools to extract List-Unsubscribe headers.

## Gmail MCP on Headless Servers (IMPORTANT)

**gmail-mcp-multiauth will NOT work on headless servers.** The `setup`
command calls `open()` to launch a browser and listens on port 3000 for
the OAuth callback. This requires a running GUI browser.

### Manual OAuth Flow for Headless

If you need MCP OAuth without a browser:
1. Generate OAuth URLs using the OOB (out-of-band) redirect:
   ```
   https://accounts.google.com/o/oauth2/v2/auth?
     scope=https://www.googleapis.com/auth/gmail.modify+https://www.googleapis.com/auth/gmail.settings.basic
     &response_type=code
     &access_type=offline
     &client_id=YOUR_CLIENT_ID
     &redirect_uri=urn:ietf:wg:oauth:2.0:oob
   ```
2. Open URL → sign in → grant permission → copy the authorization code
3. Exchange code for tokens manually
4. Save tokens to `~/.gmail-<account>/credentials.json`

### himalaya Config Gotcha (v1.2.0)

The himalaya v1.2.0 config schema differs from the skill example below.
The actual working config is already at `~/.config/himalaya/config.toml`.
Key differences from v0:
- `message.send.type = "smtp"` not `message.send.backend.type`
- `message.send.auth.cmd = "cat ~/.config/himalaya/.secret_<acct>"` 
- No `backend.auth.keyring` or `\"cmd\"` workaround

## Setup

### Step 1: Install himalaya

```bash
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh
```

### Step 2: Generate Gmail App Passwords

For each account:
1. Go to https://myaccount.google.com/apppasswords (2FA must be enabled)
2. Create app password for "Mail" on "Other (Custom name)"
3. Store securely: `echo "APP_PASSWORD" > ~/.config/himalaya/.secret_<alias>`
4. `chmod 600 ~/.config/himalaya/.secret_*`

### Step 3: Configure himalaya

Create `~/.config/himalaya/config.toml`:

```toml
# Global defaults
display-name = "Vamsee Achanta"
downloads-dir = "~/.config/himalaya/downloads"

[accounts.ace]
default = true
email = "vamsee.achanta@aceengineer.com"
display-name = "Vamsee Achanta"
backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "vamsee.achanta@aceengineer.com"
backend.auth.type = "password"
backend.auth.cmd = "cat ~/.config/himalaya/.secret_ace"
message.send.type = "smtp"
message.send.host = "smtp.gmail.com"
message.send.port = 587
message.send.encryption.type = "starttls"
message.send.login = "vamsee.achanta@aceengineer.com"
message.send.auth.type = "password"
message.send.auth.cmd = "cat ~/.config/himalaya/.secret_ace"

[accounts.personal]
email = "achantav@gmail.com"
display-name = "Vamsee Achanta"
backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "achantav@gmail.com"
backend.auth.type = "password"
backend.auth.cmd = "cat ~/.config/himalaya/.secret_personal"
message.send.type = "smtp"
message.send.host = "smtp.gmail.com"
message.send.port = 587
message.send.encryption.type = "starttls"
message.send.login = "achantav@gmail.com"
message.send.auth.type = "password"
message.send.auth.cmd = "cat ~/.config/himalaya/.secret_personal"

[accounts.skestates]
email = "skestatesinc@gmail.com"
display-name = "SKEstates Inc"
backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "skestatesinc@gmail.com"
backend.auth.type = "password"
backend.auth.cmd = "cat ~/.config/himalaya/.secret_skestates"
message.send.type = "smtp"
message.send.host = "smtp.gmail.com"
message.send.port = 587
message.send.encryption.type = "starttls"
message.send.login = "skestatesinc@gmail.com"
message.send.auth.type = "password"
message.send.auth.cmd = "cat ~/.config/himalaya/.secret_skestates"
```

### Step 4: Verify

```bash
himalaya --account ace envelope list --page-size 5
himalaya --account personal envelope list --page-size 5
himalaya --account skestates envelope list --page-size 5
```

## Usage Patterns

### Quick scan all accounts
```bash
for acct in ace personal skestates; do
  echo "=== $acct ==="
  himalaya --account $acct envelope list --page-size 10 --output json 2>/dev/null
done
```

### Read specific message
```bash
himalaya --account ace message read 42
```

### Send (always confirm with user first)
```bash
cat << 'EOF' | himalaya --account ace template send
From: vamsee.achanta@aceengineer.com
To: recipient@example.com
Subject: Subject Line

Body text here.
EOF
```

## Account-Specific Rules

### ace (vamsee.achanta@aceengineer.com)
- PRIORITY: client emails, RFPs, invoice responses, GTM prospects
- TONE: Professional engineering — P.E. credentials, technical precision
- CONTACTS: aceengineer-admin/admin/contacts/aceengineer_contacts.csv (1,306 entries)
- LINK TO: aceengineer-strategy/ prospect pipeline
- TOUCHBASE: engineering contacts, potential clients

### personal (achantav@gmail.com)
- PRIORITY: personal finance, family, career networking
- TONE: Casual/personal, warm
- CONTACTS: aceengineer-admin/admin/contacts/achantav_contacts.csv (1,157 entries)
- AGGRESSIVE UNSUBSCRIBE: marketing, social media notifications
- TOUCHBASE: close professional network, alumni, friends

### skestates (skestatesinc@gmail.com)
- PRIORITY: tenant communications (Family Dollar Store #30150), tax/legal, insurance
- TONE: Business formal, landlord correspondence
- CONTACTS: sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv
- KEY CONTACT: TX_Rents@familydollar.com (tenant)
- LINK TO: sabithaandkrishnaestates/ deal files, tax docs

## Contact Database Locations (normalized + deduped)

| Account | CSV Path | Count |
|---|---|---|
| ace | aceengineer-admin/admin/contacts/aceengineer_normalized.csv | 1,281 |
| personal | aceengineer-admin/admin/contacts/achantav_normalized.csv | 994 |
| skestates | sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv | 25 |

Cross-file dedup: 132 overlaps resolved (see reports/email/contact-dedup-report.md)

## Live Status (as of 2026-04-06)

All 3 accounts fully connected:
- ace: OAuth2 ✅ + himalaya (App Password) ✅
- personal: OAuth2 ✅ + himalaya (App Password) ✅
- skestates: OAuth2 ✅ + himalaya ❌ (App Passwords unavailable for this account)

Credential paths:
- OAuth tokens: ~/.gmail-{ace,personal,skestates}/credentials.json
- OAuth config: ~/.gmail-mcp/oauth-env.json (client_id + client_secret)
- Himalaya secrets: ~/.config/himalaya/.secret_{ace,personal}
- Himalaya config: ~/.config/himalaya/config.toml
- MCP start scripts: ~/.gmail-{ace,personal,skestates}/start-mcp.sh

Digest script: scripts/email/gmail-digest.py (run with uv)
Cron: daily at 12 PM CT (job id: 908c4afa32cf)

GCP Project: hermes-gmail-automation
OAuth consent: External, test users added (all 3 emails)

## Pitfalls

1. Gmail IMAP must be enabled: Settings > Forwarding and POP/IMAP > Enable IMAP
2. App Passwords only work with 2FA enabled
3. Google may block "less secure" access — App Passwords bypass this
4. himalaya message IDs are folder-relative — re-list after folder changes
5. Never send email without user confirmation — show draft first
6. Rate limit: don't rapid-fire API calls; batch reads
7. The skestatesinc email was "skestatesinc.gmail.com" — correct is "skestatesinc@gmail.com"
8. **himalaya v1.2.0 config schema changed** — `backend.auth.type = "cmd"` is INVALID (duplicate key error with `backend.auth.type = "password"`). Use only `backend.auth.cmd` under the password type.
9. gmail-mcp-multiauth setup requires browser — use manual OOB flow on headless servers
10. External repo contacts must be committed from within their respective repo dirs (not workspace-hub root)
