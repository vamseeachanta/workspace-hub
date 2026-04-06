---
name: gmail-multi-account
description: Multi-account Gmail management via himalaya CLI. Three accounts (aceengineer, achantav, skestates) with distinct triage rules, contact DBs, and tone profiles. Foundation skill for email automation.
version: 1.0.0
author: vamsee
tags: [email, gmail, himalaya, multi-account, triage]
related_skills: [himalaya, google-workspace, gmail-triage, gmail-unsubscribe, gmail-touchbase]
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

**Primary: gmail-mcp-multiauth (npm)** — purpose-built multi-account Gmail MCP
- Each account gets named MCP server (gmail-ace, gmail-personal, gmail-skestates)
- OAuth2 per-account, one GCP project
- 381K downloads/mo base (GongRzhe fork), token refresh fix
- Install: `npm install -g gmail-mcp-multiauth`

**Fallback: himalaya CLI** — for cron jobs and shell scripts
- App Password auth (simpler, no OAuth dance)
- Multi-account via --account flag
- Install: `curl -sSL .../install.sh | PREFIX=~/.local sh`

**NOT chosen:**
- himalaya-mcp wrapper: too many layers (Rust CLI + npm MCP + TOML config)
- workspace-mcp (taylorwilsdon): overkill (full Workspace suite, 2K stars but heavy)
- @gongrzhe/server-gmail-autoauth-mcp: single-account only
- DIY google-workspace OAuth script: high maintenance

**Unsubscribe note:** No MCP server has native List-Unsubscribe support. Must parse raw headers via Gmail API or custom tool.

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
[accounts.ace]
email = "vamsee.achanta@aceengineer.com"
display-name = "Vamsee Achanta"
default = true

backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "vamsee.achanta@aceengineer.com"
backend.auth.type = "password"
backend.auth.cmd = "cat ~/.config/himalaya/.secret_ace"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "vamsee.achanta@aceengineer.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "cat ~/.config/himalaya/.secret_ace"

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

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "achantav@gmail.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "cat ~/.config/himalaya/.secret_personal"

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

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "skestatesinc@gmail.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "cat ~/.config/himalaya/.secret_skestates"
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

## Contact Database Locations

| Account | CSV Path | Count |
|---|---|---|
| ace | aceengineer-admin/admin/contacts/aceengineer_contacts.csv | ~1,306 |
| personal | aceengineer-admin/admin/contacts/achantav_contacts.csv | ~1,157 |
| skestates | sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv | TBD (create from key_contacts.md) |

## Pitfalls

1. Gmail IMAP must be enabled: Settings > Forwarding and POP/IMAP > Enable IMAP
2. App Passwords only work with 2FA enabled
3. Google may block "less secure" access — App Passwords bypass this
4. himalaya message IDs are folder-relative — re-list after folder changes
5. Never send email without user confirmation — show draft first
6. Rate limit: don't rapid-fire API calls; batch reads
7. The skestatesinc email in memory says "skestatesinc.gmail.com" but correct is "skestatesinc@gmail.com"
