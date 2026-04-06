#!/usr/bin/env python3
"""Gmail multi-account daily digest.

Scans 3 Gmail accounts via OAuth2, classifies emails against contact databases,
generates an actionable digest with priority-ordered recommendations.

Run with: uv run scripts/email/gmail-digest.py
Cron:     0 12 * * * cd /mnt/local-analysis/workspace-hub && uv run scripts/email/gmail-digest.py

No pip dependencies — stdlib only (urllib, json, csv, pathlib).
"""

import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================
CLIENT_ID = os.environ.get("GMAIL_OAUTH_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GMAIL_OAUTH_CLIENT_SECRET", "")
TOKEN_URL = "https://oauth2.googleapis.com/token"

if not CLIENT_ID or not CLIENT_SECRET:
    # Try loading from shared config file
    _cfg_path = os.path.expanduser("~/.gmail-mcp/oauth-env.json")
    if os.path.exists(_cfg_path):
        with open(_cfg_path) as _f:
            _cfg = json.load(_f)
            CLIENT_ID = CLIENT_ID or _cfg.get("client_id", "")
            CLIENT_SECRET = CLIENT_SECRET or _cfg.get("client_secret", "")
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: Set GMAIL_OAUTH_CLIENT_ID and GMAIL_OAUTH_CLIENT_SECRET env vars", file=sys.stderr)
        print("  Or create ~/.gmail-mcp/oauth-env.json with {\"client_id\": ..., \"client_secret\": ...}", file=sys.stderr)
        sys.exit(1)
GMAIL_BASE = "https://gmail.googleapis.com/gmail/v1"

ACCOUNTS = {
    "ace": {
        "display": "ACE Engineer",
        "email": "vamsee.achanta@aceengineer.com",
        "cred": "~/.gmail-ace/credentials.json",
    },
    "personal": {
        "display": "Personal",
        "email": "achantav@gmail.com",
        "cred": "~/.gmail-personal/credentials.json",
    },
    "skestates": {
        "display": "SKEstates Inc",
        "email": "skestatesinc@gmail.com",
        "cred": "~/.gmail-skestates/credentials.json",
    },
}

BASE = Path("/mnt/local-analysis/workspace-hub")
CONTACT_FILES = {
    "ace": BASE / "aceengineer-admin/admin/contacts/aceengineer_normalized.csv",
    "personal": BASE / "aceengineer-admin/admin/contacts/achantav_normalized.csv",
    "skestates": BASE / "sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv",
}

# VIP domains per account
ACE_VIP_DOMAINS = {
    "ril.com", "dorisgroup.com", "mcdermott.com", "shell.com",
    "kbr.com", "bp.com", "subsea7.com", "technipfmc.com",
}
SKESTATES_VIP_DOMAINS = {
    "familydollar.com", "dollartree.com", "marsh.com",
}

# ============================================================
# CONTACT LOADING
# ============================================================
def load_contacts():
    contacts_db = {}
    for acct, cpath in CONTACT_FILES.items():
        contacts_db[acct] = {}
        if cpath.exists():
            with open(cpath) as f:
                for row in csv.DictReader(f):
                    contacts_db[acct][row["email"].lower()] = row
    return contacts_db


# ============================================================
# TOKEN MANAGEMENT
# ============================================================
def refresh_token(cred_path):
    path = os.path.expanduser(cred_path)
    if not os.path.exists(path):
        return None

    with open(path) as f:
        saved = json.load(f)

    rt = saved.get("refresh_token")
    if not rt:
        return None

    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": rt,
        "grant_type": "refresh_token",
    }).encode("utf-8")

    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tokens = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Token refresh failed: {e}", file=sys.stderr)
        return None

    saved.update(tokens)
    with open(path, "w") as f:
        json.dump(saved, f, indent=2)

    return tokens["access_token"]


# ============================================================
# GMAIL API
# ============================================================
def gmail_get(endpoint, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{GMAIL_BASE}/{endpoint}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} on {endpoint}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Error on {endpoint}: {e}", file=sys.stderr)
        return None


def get_messages(access_token, query="is:unread", max_results=25):
    q = urllib.parse.quote(query)
    listing = gmail_get(f"users/me/messages?maxResults={max_results}&q={q}", access_token)
    if not listing:
        return []

    messages = []
    for msg_stub in listing.get("messages", []):
        detail = gmail_get(f"users/me/messages/{msg_stub['id']}?format=full", access_token)
        if not detail:
            continue

        hdrs = {}
        for h in detail.get("payload", {}).get("headers", []):
            hdrs[h["name"]] = h["value"]

        messages.append({
            "id": msg_stub["id"],
            "threadId": detail.get("threadId", ""),
            "from": hdrs.get("From", ""),
            "to": hdrs.get("To", ""),
            "subject": hdrs.get("Subject", ""),
            "date": hdrs.get("Date", ""),
            "snippet": detail.get("snippet", "")[:200],
            "unread": "UNREAD" in detail.get("labelIds", []),
            "labels": detail.get("labelIds", []),
        })

    return messages


# ============================================================
# CLASSIFICATION
# ============================================================
def extract_email(from_header):
    match = re.search(r"<([^>]+)>", from_header)
    if match:
        return match.group(1).lower()
    if "@" in from_header:
        return from_header.strip().lower()
    return ""


def classify(msg, contacts, account_name):
    sender_email = extract_email(msg["from"])
    domain = sender_email.split("@")[-1] if "@" in sender_email else ""
    contact = contacts.get(sender_email, {})
    category = contact.get("category", "unknown")
    text = (msg["subject"] + " " + msg["snippet"]).lower()

    # VIP detection
    is_vip = False
    if account_name == "ace" and domain in ACE_VIP_DOMAINS:
        is_vip = True
    elif account_name == "skestates" and domain in SKESTATES_VIP_DOMAINS:
        is_vip = True
    elif category in ("client", "tenant"):
        is_vip = True

    # Priority assignment
    urgent_words = ["urgent", "asap", "deadline", "overdue", "past due", "immediate"]
    high_words = ["invoice", "payment", "1099", "tax", "rent", "lease"]
    action_words = ["rfp", "proposal", "scope of work", "meeting request", "interview", "question"]

    if any(w in text for w in urgent_words) or (is_vip and msg["unread"]):
        priority = "URGENT"
    elif is_vip or category in ("client", "tenant") or any(w in text for w in high_words):
        priority = "HIGH"
    elif any(w in text for w in action_words) or "?" in msg["subject"]:
        priority = "ACTIONABLE"
    elif category in ("newsletter", "spam"):
        priority = "IGNORE"
    elif "unsubscribe" in text and not contact:
        priority = "UNSUBSCRIBE"
    else:
        priority = "FYI"

    return {
        **msg,
        "sender_email": sender_email,
        "domain": domain,
        "priority": priority,
        "category": category,
        "contact_match": bool(contact),
        "contact_name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip() if contact else "",
        "contact_company": contact.get("company", ""),
    }


# ============================================================
# SCAN
# ============================================================
def scan_account(account_name, contacts_db):
    acct = ACCOUNTS[account_name]
    contacts = contacts_db.get(account_name, {})

    token = refresh_token(acct["cred"])
    if not token:
        return {"status": "AUTH_FAILED", "messages": []}

    profile = gmail_get("users/me/profile", token)
    if not profile:
        return {"status": "API_FAILED", "messages": []}

    # Fetch unread + recent
    unread = get_messages(token, query="is:unread", max_results=25)
    recent = get_messages(token, query="newer_than:1d", max_results=15)

    # Deduplicate by message ID
    seen_ids = set()
    all_msgs = []
    for msg in unread + recent:
        if msg["id"] not in seen_ids:
            seen_ids.add(msg["id"])
            classified = classify(msg, contacts, account_name)
            all_msgs.append(classified)

    return {
        "status": "OK",
        "email": profile["emailAddress"],
        "total": profile.get("messagesTotal", 0),
        "threads": profile.get("threadsTotal", 0),
        "unread_scanned": len(unread),
        "recent_scanned": len(recent),
        "messages": all_msgs,
    }


# ============================================================
# DIGEST FORMATTER
# ============================================================
PRIORITY_ORDER = ["URGENT", "HIGH", "ACTIONABLE", "UNSUBSCRIBE", "FYI", "IGNORE"]
PRIORITY_ICONS = {
    "URGENT": "!!!", "HIGH": " ! ", "ACTIONABLE": " > ",
    "UNSUBSCRIBE": "unsub", "FYI": " . ", "IGNORE": " x ",
}


def format_digest(results):
    now = datetime.now()
    lines = []
    lines.append(f"GMAIL DAILY DIGEST — {now.strftime('%A %B %d, %Y %I:%M %p CT')}")
    lines.append("=" * 65)

    action_items = []
    global_counts = Counter()

    for acct_key in ["ace", "personal", "skestates"]:
        acct = ACCOUNTS[acct_key]
        r = results.get(acct_key, {})
        status = r.get("status", "UNKNOWN")

        lines.append("")
        lines.append(f"--- {acct['display']} ({acct['email']}) ---")

        if status != "OK":
            lines.append(f"  Status: FAILED ({status})")
            continue

        lines.append(f"  Total: {r['total']} msgs | Unread scanned: {r['unread_scanned']} | Recent: {r['recent_scanned']}")

        msgs = r.get("messages", [])
        by_priority = {}
        for msg in msgs:
            p = msg["priority"]
            by_priority.setdefault(p, []).append(msg)
            global_counts[p] += 1

        for priority in PRIORITY_ORDER:
            items = by_priority.get(priority, [])
            if not items:
                continue

            icon = PRIORITY_ICONS.get(priority, "   ")
            lines.append(f"  [{icon}] {priority} ({len(items)}):")

            for msg in items[:8]:
                contact_info = ""
                if msg["contact_match"]:
                    contact_info = f" [{msg['contact_name']} @ {msg['contact_company']}]"

                lines.append(f"    {msg['sender_email']}{contact_info}")
                lines.append(f"      {msg['subject'][:100]}")

                if priority in ("URGENT", "HIGH", "ACTIONABLE"):
                    action_items.append(
                        f"[{acct_key.upper()}] {msg['sender_email']}: {msg['subject'][:80]}"
                    )

            if len(items) > 8:
                lines.append(f"    ... and {len(items) - 8} more")

    lines.append("")
    lines.append("=" * 65)
    lines.append("RECOMMENDED ACTIONS")
    lines.append("-" * 65)
    if action_items:
        for i, item in enumerate(action_items, 1):
            lines.append(f"  {i}. {item}")
    else:
        lines.append("  No urgent actions.")

    lines.append("")
    lines.append(f"Totals: {dict(global_counts)}")
    lines.append(f"Generated: {now.isoformat()}")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================
def main():
    contacts_db = load_contacts()

    results = {}
    for acct_key in ACCOUNTS:
        try:
            results[acct_key] = scan_account(acct_key, contacts_db)
        except Exception as e:
            results[acct_key] = {"status": f"EXCEPTION: {e}", "messages": []}

    digest = format_digest(results)

    # Save to file
    out_dir = Path(os.path.expanduser("~/.gmail-digests"))
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"digest_{ts}.txt"
    with open(out_path, "w") as f:
        f.write(digest)

    # Print to stdout (for cron delivery)
    print(digest)
    print(f"\nSaved: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
