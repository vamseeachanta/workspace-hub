---
name: gmail-headless-oauth
description: Manual OAuth2 token exchange for Gmail on headless servers. Bypass gmail-mcp-multiauth browser requirement. Generate auth URLs, exchange codes, manage multi-account credentials with auto-refresh.
version: 1.0.0
author: vamsee
tags: [email, gmail, oauth, headless, authentication]
related_skills: [gmail-multi-account, google-workspace]
metadata:
  hermes:
    tags: [email, gmail, oauth, headless]
    related_skills: [gmail-multi-account]
---

# Gmail Headless OAuth2

Set up Gmail API OAuth2 on servers without a browser. The standard gmail-mcp-multiauth `setup` command calls `open()` to launch a browser and listens on localhost:3000 — this fails on headless CLI servers. This skill provides the manual workaround.

## When to Use

- Setting up Gmail API access on a headless server (no GUI browser)
- gmail-mcp-multiauth `setup` fails or hangs waiting for browser callback
- Need to re-authorize after token expiry
- Adding new Gmail accounts to an existing setup

## Prerequisites

- GCP project with Gmail API enabled
- OAuth 2.0 Desktop App credentials (client_secret JSON downloaded)
- Each Gmail account added as "test user" in GCP OAuth consent screen (unless app is verified/published)

## Pitfall: GCP Test Users (CRITICAL)

If your GCP app is in "Testing" status (not published), only emails listed as **test users** can authorize. Other accounts get: `Error 403: access_denied — Hermes Gmail Automation has not completed the Google verification process`.

**Fix:** Go to https://console.cloud.google.com/apis/credentials/consent → Click **"Audience"** in the left sidebar (NOT "Clients") → scroll to "Test users" → Add each email.

## Step 1: Store OAuth Client Credentials Locally

```python
# NEVER hardcode in scripts — GitHub push protection WILL block it
# Store in ~/.gmail-mcp/oauth-env.json (chmod 600)
import json, os
path = os.path.expanduser("~/.gmail-mcp/oauth-env.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    json.dump({"client_id": "YOUR_CLIENT_ID", "client_secret": "YOUR_SECRET"}, f)
os.chmod(path, 0o600)
```

Scripts load via: `os.environ.get("GMAIL_OAUTH_CLIENT_ID")` or fallback to this file.

## Step 2: Generate Auth URLs

Use the OOB (out-of-band) redirect — user gets the code on-screen instead of via localhost callback:

```python
client_id = "YOUR_CLIENT_ID"
scopes = "https://www.googleapis.com/auth/gmail.modify+https://www.googleapis.com/auth/gmail.settings.basic"
redirect = "urn:ietf:wg:oauth:2.0:oob"

auth_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth?"
    f"scope={scopes}&response_type=code&access_type=offline"
    f"&client_id={client_id}&redirect_uri={redirect}"
)
print(auth_url)
```

The same URL works for all accounts — the difference is which Google account the user signs in as.

## Step 3: Exchange Auth Code for Tokens

**CRITICAL: Auth codes are SINGLE-USE.** If the exchange fails (network, typo, sandbox restart), the user must generate a new code. Plan accordingly — do NOT attempt exchange in a sandbox that may lose state.

```python
import json, os, urllib.request, urllib.parse

def exchange_code(code, client_id, client_secret):
    data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "grant_type": "authorization_code",
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

# Returns: {"access_token": "ya29...", "refresh_token": "1//...", "expires_in": 3599, ...}
```

## Step 4: Save Credentials Per-Account

```python
account = "ace"  # or "personal", "skestates"
account_dir = os.path.expanduser(f"~/.gmail-{account}")
os.makedirs(account_dir, exist_ok=True)

# Save tokens
cred_path = os.path.join(account_dir, "credentials.json")
with open(cred_path, "w") as f:
    json.dump(tokens, f, indent=2)
os.chmod(cred_path, 0o600)

# Copy OAuth keys for MCP compatibility
oauth_src = os.path.expanduser("~/.gmail-mcp/gcp-oauth.keys.json")
oauth_dst = os.path.join(account_dir, "gcp-oauth.keys.json")
shutil.copy2(oauth_src, oauth_dst)
os.chmod(oauth_dst, 0o600)
```

## Step 5: Verify via Gmail API

```python
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
req = urllib.request.Request(
    "https://gmail.googleapis.com/gmail/v1/users/me/profile",
    headers=headers
)
with urllib.request.urlopen(req, timeout=30) as resp:
    profile = json.loads(resp.read().decode())
    print(f"Connected: {profile['emailAddress']} — {profile['messagesTotal']} messages")
```

## Step 6: Create MCP Start Script

```bash
#!/bin/bash
export GMAIL_OAUTH_PATH=~/.gmail-{account}/gcp-oauth.keys.json
export GMAIL_CREDENTIALS_PATH=~/.gmail-{account}/credentials.json
export GMAIL_ACCOUNT_NAME={account}
exec node ~/.npm-global/lib/node_modules/gmail-mcp-multiauth/dist/index.js
```

Save to `~/.gmail-{account}/start-mcp.sh`, chmod +x.

## Token Refresh (automated)

Tokens expire in 3600s. Refresh using the stored refresh_token:

```python
def refresh_access_token(account):
    cred_path = os.path.expanduser(f"~/.gmail-{account}/credentials.json")
    with open(cred_path) as f:
        saved = json.load(f)

    with open(os.path.expanduser("~/.gmail-mcp/oauth-env.json")) as f:
        cfg = json.load(f)

    data = urllib.parse.urlencode({
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "refresh_token": saved["refresh_token"],
        "grant_type": "refresh_token",
    }).encode("utf-8")

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        new_tokens = json.loads(resp.read().decode())

    saved.update(new_tokens)  # Preserves refresh_token
    with open(cred_path, "w") as f:
        json.dump(saved, f, indent=2)

    return new_tokens["access_token"]
```

## Multi-Account Batch Auth

When authorizing multiple accounts in one session:
1. Generate ONE auth URL (it's the same for all accounts)
2. Ask user to open it, sign in as each account separately, paste codes labeled
3. Exchange ALL codes in a SINGLE execute_code block (codes are single-use, sandbox state may not persist between turns)

## Pitfalls

1. **Auth codes are single-use** — if exchange fails, user must re-authorize
2. **execute_code sandbox resets between turns** — exchange code in the same block you receive it
3. **GitHub push protection blocks OAuth credentials** — never hardcode client_id/client_secret in committed files
4. **GCP test user list** — must add each email BEFORE they can authorize. The setting is under "Audience" not "Clients" in the GCP console
5. **Some Google accounts can't generate App Passwords** — Workspace accounts without 2FA admin control, or accounts with Advanced Protection. OAuth still works for these.
6. **himalaya config v1.2.0 breaks on duplicate keys** — `backend.auth.type = "password"` and `backend.auth.type = "cmd"` on separate lines causes TOML parse error. Use only the password type with `.cmd` for the command.
7. **Scopes are per-authorization** — if you need Drive access later, you must re-authorize with additional scopes. Gmail-only scopes won't give Drive access.
8. **himalaya v1.2.0 `-a` flag position** — the account flag goes on the SUBCOMMAND, not global: `himalaya envelope list -a ace` NOT `himalaya -a ace envelope list` or `himalaya --account ace envelope list`.
9. **Token refresh returns NO new refresh_token** — the response only has access_token. Always `saved.update(new_tokens)` to preserve the original refresh_token.
10. **OOB redirect deprecated but still works** — Google deprecated `urn:ietf:wg:oauth:2.0:oob` for new apps in 2022, but it still functions for Desktop App type credentials. If it stops working, switch to localhost redirect with a background HTTP server.
11. **GitGuardian will detect secrets in local git history** even if GitHub push protection blocks the push. Always amend the commit to remove secrets before they enter any git history.

## Verified Working Setup (2026-04-06)

Three accounts fully authorized on ace-linux-1:
- ace: OAuth2 + himalaya App Password
- personal: OAuth2 + himalaya App Password
- skestates: OAuth2 only (App Passwords unavailable — Workspace account limitation)

GCP Project: hermes-gmail-automation
Credential paths: ~/.gmail-{ace,personal,skestates}/credentials.json
Shared config: ~/.gmail-mcp/oauth-env.json (client_id + client_secret)
Digest script: scripts/email/gmail-digest.py (stdlib only, zero pip deps)
