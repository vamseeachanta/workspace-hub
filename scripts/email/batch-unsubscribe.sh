#!/usr/bin/env bash
# batch-unsubscribe.sh — Unsubscribe from noise domains and delete historical messages
#
# Reads confirmed noise domains from config/email-filters/ace-noise-domains.yaml
# and executes List-Unsubscribe for each, then trashes historical messages.
#
# Usage:
#   ./scripts/email/batch-unsubscribe.sh [--dry-run] [--account ace]
#
# Prerequisites:
#   - OAuth tokens in ~/.gmail-{account}/credentials.json
#   - Client credentials in ~/.gmail-mcp/oauth-env.json
#   - uv available for Python execution
#
# Issue: #1991
# Related: config/email-filters/ace-noise-domains.yaml

set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"

DRY_RUN=false
ACCOUNT="ace"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --account) ACCOUNT="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

NOISE_FILE="${REPO_ROOT}/config/email-filters/ace-noise-domains.yaml"
if [[ ! -f "$NOISE_FILE" ]]; then
    echo "ERROR: Noise domain list not found: $NOISE_FILE"
    exit 1
fi

echo "=== Batch Unsubscribe ==="
echo "Account: $ACCOUNT"
echo "Dry run: $DRY_RUN"
echo "Noise file: $NOISE_FILE"
echo ""

# Extract domains with UNSUBSCRIBE action from the YAML file
DOMAINS=$(uv run --with pyyaml python -c "
import yaml, sys
with open('${NOISE_FILE}') as f:
    data = yaml.safe_load(f)
for entry in data.get('domains', []):
    if entry.get('action') == 'UNSUBSCRIBE':
        print(entry['domain'])
")

if [[ -z "$DOMAINS" ]]; then
    echo "No domains to unsubscribe from."
    exit 0
fi

DOMAIN_COUNT=$(echo "$DOMAINS" | wc -l)
echo "Found $DOMAIN_COUNT domains to process:"
echo "$DOMAINS" | sed 's/^/  - /'
echo ""

if $DRY_RUN; then
    echo "[DRY RUN] Would unsubscribe and delete messages from the above domains."
    echo "[DRY RUN] Run without --dry-run to execute."
    echo ""
    echo "Checking message counts per domain..."
    echo ""
fi

# Process each domain using the Gmail API via Python
uv run --with pyyaml python - "$ACCOUNT" "$DRY_RUN" <<'PYTHON_SCRIPT'
import json, os, sys, urllib.request, urllib.parse, re
from pathlib import Path

account = sys.argv[1]
dry_run = sys.argv[2].lower() == "true"

# Read domains from stdin
import yaml
repo_root = os.environ.get("REPO_ROOT", os.popen("git rev-parse --show-toplevel").read().strip())
noise_file = os.path.join(repo_root, "config", "email-filters", "ace-noise-domains.yaml")
with open(noise_file) as f:
    data = yaml.safe_load(f)

domains = [e["domain"] for e in data.get("domains", []) if e.get("action") == "UNSUBSCRIBE"]

def refresh_token(acct):
    cfg_path = os.path.expanduser("~/.gmail-mcp/oauth-env.json")
    cred_path = os.path.expanduser(f"~/.gmail-{acct}/credentials.json")
    if not os.path.exists(cfg_path) or not os.path.exists(cred_path):
        print(f"ERROR: OAuth credentials not found for account '{acct}'")
        print(f"  Expected: {cfg_path} and {cred_path}")
        sys.exit(1)
    with open(cfg_path) as f:
        cfg = json.load(f)
    with open(cred_path) as f:
        saved = json.load(f)
    payload = urllib.parse.urlencode({
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "refresh_token": saved["refresh_token"],
        "grant_type": "refresh_token",
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=payload, method="POST")
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

def execute_unsubscribe(url):
    """Execute HTTP-based List-Unsubscribe"""
    if not url:
        return False
    # Extract URL from angle brackets if present
    url_match = re.search(r'<(https?://[^>]+)>', url)
    if url_match:
        url = url_match.group(1)
    elif not url.startswith("http"):
        return False
    try:
        req = urllib.request.Request(url, method="POST",
            headers={"List-Unsubscribe": "One-Click"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status < 400
    except Exception as e:
        print(f"    Unsubscribe request failed: {e}")
        return False

try:
    token = refresh_token(account)
except Exception as e:
    print(f"ERROR: Could not authenticate: {e}")
    sys.exit(1)

total_unsubscribed = 0
total_trashed = 0
total_errors = 0

for domain in domains:
    print(f"\n--- {domain} ---")
    query = urllib.parse.quote(f"from:{domain}")
    try:
        search = gmail_get(f"users/me/messages?q={query}&maxResults=500", token)
    except Exception as e:
        print(f"  Search error: {e}")
        total_errors += 1
        continue

    messages = search.get("messages", [])
    count = len(messages)
    est_total = search.get("resultSizeEstimate", count)
    print(f"  Messages found: {count} (estimated total: {est_total})")

    if count == 0:
        continue

    # Try to unsubscribe using the first message with a List-Unsubscribe header
    unsub_done = False
    for msg_stub in messages[:5]:  # Check first 5 for unsubscribe header
        try:
            detail = gmail_get(
                f"users/me/messages/{msg_stub['id']}?format=metadata"
                "&metadataHeaders=List-Unsubscribe&metadataHeaders=List-Unsubscribe-Post",
                token
            )
            hdrs = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
            unsub_url = hdrs.get("List-Unsubscribe", "")
            if unsub_url and not unsub_done:
                if dry_run:
                    print(f"  [DRY RUN] Would unsubscribe via: {unsub_url[:80]}...")
                else:
                    ok = execute_unsubscribe(unsub_url)
                    if ok:
                        print(f"  Unsubscribed successfully")
                        total_unsubscribed += 1
                    else:
                        print(f"  Unsubscribe attempt made (may need manual verification)")
                        total_unsubscribed += 1
                unsub_done = True
                break
        except Exception as e:
            print(f"  Header check error: {e}")

    if not unsub_done:
        print(f"  No List-Unsubscribe header found — manual unsubscribe may be needed")

    # Trash all messages from this domain
    trashed = 0
    for msg_stub in messages:
        if dry_run:
            trashed += 1
        else:
            try:
                gmail_post(f"users/me/messages/{msg_stub['id']}/trash", token, {})
                trashed += 1
            except Exception as e:
                print(f"  Trash error for {msg_stub['id']}: {e}")
                total_errors += 1

    if dry_run:
        print(f"  [DRY RUN] Would trash {trashed} messages")
    else:
        print(f"  Trashed {trashed} messages")
    total_trashed += trashed

print(f"\n=== Summary ===")
print(f"Domains processed: {len(domains)}")
print(f"Unsubscribe attempts: {total_unsubscribed}")
print(f"Messages {'would be trashed' if dry_run else 'trashed'}: {total_trashed}")
print(f"Errors: {total_errors}")
if dry_run:
    print(f"\n[DRY RUN] No changes were made. Run without --dry-run to execute.")
PYTHON_SCRIPT

echo ""
echo "Done."
