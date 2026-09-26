#!/usr/bin/env python3
"""Probe the AI-provider accounts logged in on THIS machine and print their usage.

Self-contained (standard library only) so a fleet collector can pipe it over
ssh stdin (``ssh host 'python3 - --json --host <label>' < this-file``) without
needing the remote checkout to be up to date. Runs on Linux, macOS and Windows
(Git Bash / PowerShell).

Providers
  claude  Claude Code OAuth login. Token from ``$CLAUDE_CONFIG_DIR/.credentials.json``
          (default ``~/.claude/.credentials.json``); usage from
          ``GET https://api.anthropic.com/api/oauth/usage``. Utilization buckets
          are reported as the API returns them (five_hour, seven_day,
          seven_day_sonnet, seven_day_opus, ...), each as ``pct`` used and
          ``resets_at``.
  codex   Codex CLI ChatGPT login. Live figures from ``codex app-server``
          (``account/rateLimits/read``); fallback to the newest session log
          under ``$CODEX_HOME/sessions`` (default ``~/.codex``). ``primary`` is
          the five-hour window, ``secondary`` the weekly window.

Identity is reported as a *fingerprint* (first 12 hex of SHA-256 of the
lowercased login email, or of the account id when no email is present) so the
aggregate can tell accounts apart without publishing an address. No token,
email or name is ever printed.

Exit status is 0 whenever a JSON document was produced, even when both
providers are unavailable: the ``source``/``error`` fields carry the reason.

Usage:
  collect-account-usage.py [--json] [--host LABEL] [--no-live]
                           [--claude-config-dir DIR] [--codex-home DIR]
                           [--timeout SECONDS]
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

CLAUDE_USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
CLAUDE_BETA = "oauth-2025-04-20"
SCHEMA_VERSION = 1


# ── helpers ──────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def epoch_to_iso(value) -> str | None:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    if v > 1e12:  # milliseconds
        v /= 1000.0
    return dt.datetime.fromtimestamp(v, dt.timezone.utc).replace(microsecond=0).isoformat()


def fingerprint(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()[:12]


def read_json(path: Path):
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        return {"__error__": f"{type(exc).__name__}: {exc}"}


def jwt_payload(token: str | None) -> dict:
    if not token or token.count(".") < 2:
        return {}
    part = token.split(".")[1]
    part += "=" * (-len(part) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(part).decode())
    except Exception:  # noqa: BLE001 - any malformed token is "no identity"
        return {}


def windows_extra_path() -> None:
    """Git Bash login shells over ssh lack winget shims (jq, codex); add them."""
    if os.name != "nt" and not sys.platform.startswith("win"):
        return
    home = Path.home()
    for extra in (home / "AppData/Local/Microsoft/WinGet/Links",
                  home / "AppData/Roaming/npm",
                  Path("C:/Program Files/nodejs")):
        if extra.is_dir():
            os.environ["PATH"] = str(extra) + os.pathsep + os.environ.get("PATH", "")


# ── claude ───────────────────────────────────────────────────────────────────

def claude_identity(config_dir: Path) -> tuple[str | None, dict]:
    """Return (fingerprint, meta) from the Claude Code config."""
    # With CLAUDE_CONFIG_DIR set, .claude.json lives inside it; otherwise ~/.claude.json.
    candidates = [config_dir / ".claude.json", Path.home() / ".claude.json"]
    for cand in candidates:
        data = read_json(cand)
        if not isinstance(data, dict) or "__error__" in data:
            continue
        acct = data.get("oauthAccount") or {}
        email = acct.get("emailAddress")
        uuid = acct.get("accountUuid")
        fp = fingerprint(email) or fingerprint(uuid)
        meta = {"org": bool(acct.get("organizationName")), "has_email": bool(email)}
        if fp:
            return fp, meta
    return None, {}


def probe_claude(config_dir: Path, timeout: float, live: bool) -> dict:
    out: dict = {"provider": "claude", "config_dir": str(config_dir), "source": "unavailable"}
    fp, meta = claude_identity(config_dir)
    out["fingerprint"] = fp
    out.update(meta)

    creds = read_json(config_dir / ".credentials.json")
    if creds is None:
        out["error"] = "no .credentials.json (not logged in on this host, or keychain-backed)"
        return out
    if "__error__" in creds:
        out["error"] = creds["__error__"]
        return out
    oauth = creds.get("claudeAiOauth") or {}
    out["tier"] = oauth.get("rateLimitTier") or oauth.get("subscriptionType") or "unknown"
    token = oauth.get("accessToken")
    if not token:
        out["error"] = "credentials file has no accessToken"
        return out
    expires = oauth.get("expiresAt")
    if expires and float(expires) / 1000.0 < time.time():
        out["error"] = "access token expired; a Claude Code session on this host will refresh it"
        out["token_expired"] = True
        return out
    if not live:
        out["error"] = "live query disabled (--no-live)"
        return out

    req = urllib.request.Request(
        CLAUDE_USAGE_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "anthropic-beta": CLAUDE_BETA,
            "Accept": "application/json",
            "User-Agent": "workspace-hub collect-account-usage/1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        out["error"] = f"http {exc.code}"
        return out
    except (urllib.error.URLError, socket.timeout, ValueError, OSError) as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    buckets = {}
    for key, val in body.items():
        if isinstance(val, dict) and "utilization" in val:
            pct = val.get("utilization")
            try:
                pct = round(float(pct), 1)
            except (TypeError, ValueError):
                pct = None
            buckets[key] = {"pct": pct, "resets_at": val.get("resets_at")}
    if not buckets:
        out["error"] = "usage response carried no utilization buckets"
        out["raw_keys"] = sorted(body.keys())[:20]
        return out
    out["buckets"] = buckets
    out["five_hour_pct"] = (buckets.get("five_hour") or {}).get("pct")
    out["week_pct"] = (buckets.get("seven_day") or {}).get("pct")
    out["week_resets_at"] = (buckets.get("seven_day") or {}).get("resets_at")
    out["source"] = "oauth-api"
    out.pop("error", None)
    return out


# ── codex ────────────────────────────────────────────────────────────────────

def codex_identity(codex_home: Path) -> tuple[str | None, dict]:
    auth = read_json(codex_home / "auth.json")
    if not isinstance(auth, dict) or "__error__" in auth:
        return None, {"error": None if auth is None else auth.get("__error__")}
    tokens = auth.get("tokens") or {}
    claims = jwt_payload(tokens.get("id_token"))
    oa = claims.get("https://api.openai.com/auth") or {}
    email = claims.get("email")
    acct = oa.get("chatgpt_account_id") or oa.get("chatgpt_user_id")
    fp = fingerprint(email) or fingerprint(acct)
    meta = {"plan": oa.get("chatgpt_plan_type"), "has_email": bool(email),
            "auth_mode": auth.get("auth_mode") or ("api-key" if auth.get("OPENAI_API_KEY") else "chatgpt")}
    return fp, meta


def _reader(stream, sink: list, stop: threading.Event) -> None:
    try:
        for line in iter(stream.readline, b""):
            sink.append(line)
            if b'"id":1' in line or b'"id": 1' in line:
                stop.set()
                break
    except Exception:  # noqa: BLE001
        pass
    stop.set()


def codex_live(timeout: float) -> dict | None:
    exe = shutil.which("codex")
    if not exe:
        return None
    msgs = [
        {"method": "initialize", "id": 0,
         "params": {"clientInfo": {"name": "collect-account-usage", "title": "Quota Probe", "version": "1.0.0"}}},
        {"method": "initialized", "params": {}},
        {"method": "account/rateLimits/read", "id": 1},
    ]
    try:
        proc = subprocess.Popen([exe, "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
    except OSError:
        return None
    lines: list[bytes] = []
    stop = threading.Event()
    t = threading.Thread(target=_reader, args=(proc.stdout, lines, stop), daemon=True)
    t.start()
    try:
        for m in msgs:
            proc.stdin.write((json.dumps(m) + "\n").encode())
        proc.stdin.flush()
        stop.wait(timeout)
    except (OSError, ValueError):
        pass
    finally:
        try:
            proc.kill()
        except OSError:
            pass
    for raw in lines:
        try:
            obj = json.loads(raw.decode())
        except ValueError:
            continue
        if obj.get("id") == 1:
            rl = (obj.get("result") or {}).get("rateLimits") or {}
            data = classify_windows(rl.get("primary"), rl.get("secondary"),
                                    "usedPercent", "resetsAt", "windowDurationMins")
            if data is None:
                return None
            data["source"] = "app-server-live"
            data["plan"] = rl.get("planType") or data.get("plan")
            return data
    return None


def classify_windows(primary, secondary, pct_key, reset_key, window_key) -> dict | None:
    """Map Codex rate-limit windows onto week / five-hour by their duration.

    Codex <= 0.13x reported primary = 5h and secondary = weekly. Codex 0.157
    reports the weekly window as ``primary`` (windowDurationMins 10080) with
    ``secondary`` null, so the slot name is not reliable: classify by the
    window length, defaulting to the legacy slot meaning when it is absent.
    """
    week = five = None
    for slot, default_mins in (("primary", 300), ("secondary", 10080)):
        win = primary if slot == "primary" else secondary
        if not isinstance(win, dict) or win.get(pct_key) is None:
            continue
        mins = win.get(window_key) or default_mins
        try:
            mins = float(mins)
        except (TypeError, ValueError):
            mins = default_mins
        if mins >= 1440:
            week = week or win
        else:
            five = five or win
    if week is None:
        return None
    return {
        "week_pct": week.get(pct_key),
        "week_resets_at": epoch_to_iso(week.get(reset_key)),
        "week_window_mins": week.get(window_key),
        "five_hour_pct": five.get(pct_key) if five else None,
        "five_hour_resets_at": epoch_to_iso(five.get(reset_key)) if five else None,
    }


def codex_from_sessions(codex_home: Path, max_files: int = 20) -> dict | None:
    sessions = codex_home / "sessions"
    if not sessions.is_dir():
        return None
    files = sorted(sessions.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:max_files]
    for f in files:
        try:
            tail = f.read_bytes()[-400_000:].decode(errors="ignore").splitlines()
        except OSError:
            continue
        for line in reversed(tail):
            if '"token_count"' not in line or '"rate_limits"' not in line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            payload = obj.get("payload") or {}
            rl = payload.get("rate_limits") or {}
            data = classify_windows(rl.get("primary"), rl.get("secondary"),
                                    "used_percent", "resets_at", "window_minutes")
            if data is None:
                continue
            data["source"] = "local-session-rate-limits"
            data["sampled_at"] = obj.get("timestamp")
            return data
    return None


def probe_codex(codex_home: Path, timeout: float, live: bool) -> dict:
    out: dict = {"provider": "codex", "codex_home": str(codex_home), "source": "unavailable"}
    fp, meta = codex_identity(codex_home)
    out["fingerprint"] = fp
    out.update({k: v for k, v in meta.items() if v is not None})
    if not (codex_home / "auth.json").exists():
        out["error"] = "no auth.json (codex not logged in on this host)"
        return out
    data = codex_live(timeout) if live else None
    if data is None:
        data = codex_from_sessions(codex_home)
    if data is None:
        out["error"] = "no live app-server answer and no session log with rate_limits"
        return out
    out.update(data)
    out.pop("error", None)
    return out


# ── main ─────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", action="store_true", help="JSON output (default and only mode)")
    p.add_argument("--host", default=None, help="public host label to stamp on the record")
    p.add_argument("--no-live", action="store_true", help="skip network / app-server queries")
    p.add_argument("--claude-config-dir", default=None)
    p.add_argument("--codex-home", default=None)
    p.add_argument("--timeout", type=float, default=8.0)
    args = p.parse_args(argv)

    windows_extra_path()
    claude_dir = Path(args.claude_config_dir or os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    codex_home = Path(args.codex_home or os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    live = not args.no_live

    record = {
        "schema_version": SCHEMA_VERSION,
        "host": args.host or socket.gethostname(),
        "captured_at": now_iso(),
        "platform": sys.platform,
        "providers": {
            "claude": probe_claude(claude_dir, args.timeout, live),
            "codex": probe_codex(codex_home, args.timeout, live),
        },
    }
    # Never echo secrets or paths that name the user profile in the public aggregate.
    for prov in record["providers"].values():
        for key in ("config_dir", "codex_home"):
            prov.pop(key, None)
    json.dump(record, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
