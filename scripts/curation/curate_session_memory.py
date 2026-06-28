#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""curate_session_memory.py — daily session-analysis + memory-curation engine.

The "session analysis and memory curation" line item of the machine-equality matrix.
Runs on EVERY machine (Linux/macOS/Windows-Git-Bash). Two responsibilities:

  1. ANALYZE all AI-provider session logs on THIS box (Claude / Codex / Gemini / Hermes)
     — bounded, mtime-first, never reads gigabytes — into per-provider activity counts.
  2. CURATE the workspace memory delta (what changed in .claude/memory/ since the last
     run) into a machine-portable digest, and PUBLISH a fingerprint to the dedicated
     `session-curation-state` git ref so sibling machines can pull it (transfer).

Outputs (all under .claude/state/, committed via the equality-* allowlist):
  * session-curation-<machine>.json   — state for the matrix freshness cell (last_curated_at)
  * session-curation-digest-<machine>.md — human-readable transferable digest
  * (published)  session-curation-state ref  — cross-machine fingerprint blob

Modes:
  (default)    curate this box + publish fingerprint
  --collect    pull every box's fingerprint from the ref → session-curation-fleet.md
  --stdout     print state JSON instead of writing (dry run; no publish)

Design notes:
  * Efficiency: each provider scan is capped (MAX_FILES_PER_PROVIDER) and prefers known
    session subdirs, so Hermes' 27 GB tree is never fully walked.
  * No leak: digest + state carry counts / bare basenames / timestamps only — never abs
    paths, prompt text, tokens, or client identifiers (matches collect-equality's allowlist).
  * Fail-soft: a missing provider dir, an unavailable git ref, or a parse error degrades
    that slice to zero/absent — the run still completes and stamps last_curated_at.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"
MEMORY = REPO / ".claude" / "memory"
CURATION_REF = "session-curation-state"

# Bound every provider scan so a multi-GB tree (Hermes ~27 GB) is never fully walked. Two
# independent guards: a MATCHED-file cap, AND — because a tree can hold millions of NON-matching
# entries that os.walk still traverses — a hard ENTRIES-WALKED cap plus a per-provider wall-clock
# deadline. Whichever trips first ends the scan (returns partial counts; freshness is unaffected).
MAX_FILES_PER_PROVIDER = 20000
MAX_ENTRIES_WALKED = 300000
SCAN_DEADLINE_S = 8.0
RECENT_WINDOW_H = 24
PUBLISH_TIMEOUT_S = 90          # hard cap on the git-ref publish — a hung push must not stall cron

# Provider → (home-relative roots to scan, in preference order; file suffixes of interest).
# First existing root wins for the "newest" probe; counts aggregate across all that exist.
PROVIDERS = {
    "claude": (["{home}/.claude/projects"], (".jsonl",)),
    "codex":  (["{home}/.codex/sessions", "{home}/.codex/logs", "{home}/.codex"], (".jsonl", ".json")),
    "gemini": (["{home}/.gemini/tmp", "{home}/.gemini/logs", "{home}/.gemini"], (".json", ".jsonl", ".log")),
    "hermes": (["{home}/.hermes/sessions", "{home}/.hermes/logs", "{home}/.hermes/history"], (".jsonl", ".json", ".log")),
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def machine_label() -> str:
    """Resolve this box's matrix label the same way collect-equality.sh does."""
    if os.environ.get("EQ_MACHINE"):
        return os.environ["EQ_MACHINE"]
    host = (os.uname().nodename if hasattr(os, "uname") else os.environ.get("COMPUTERNAME", "")).lower()
    table = {
        "ace-linux-1": "dev-primary", "ace-linux-2": "dev-secondary",
        "ace-win-1": "ace-win-1", "licensed-win-1": "ace-win-1", "acma-ansys05": "ace-win-1",
        "ace-win-2": "ace-win-2", "licensed-win-2": "ace-win-2", "acma-ws014": "ace-win-2",
    }
    for key, label in table.items():
        if host.startswith(key):
            return label
    if "macbook" in host:
        return "macbook-portable"
    return host or "unknown"


def _scan_dir(root: Path, suffixes: tuple[str, ...], cap: int) -> tuple[int, int, float]:
    """Bounded walk of `root`. Returns (file_count, recent_24h_count, newest_mtime_epoch).

    Three guards, whichever trips first ends the scan: (a) `cap` MATCHED files, (b)
    MAX_ENTRIES_WALKED total filesystem entries visited — the true bound on a tree whose
    bulk is non-matching (Hermes 27 GB), (c) SCAN_DEADLINE_S wall-clock. mtime-only: never
    opens a file. Skips obvious non-session bulk dirs to keep the walk cheap."""
    count = recent = walked = 0
    newest = 0.0
    cutoff = _now().timestamp() - RECENT_WINDOW_H * 3600
    deadline = time.monotonic() + SCAN_DEADLINE_S
    skip = {"node_modules", ".git", "__pycache__", ".cache", "venv", ".venv", "models", "blobs"}
    try:
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in skip]
            if time.monotonic() > deadline:         # wall-clock budget exhausted ⇒ stop (partial)
                break
            for fn in filenames:
                walked += 1
                if walked >= MAX_ENTRIES_WALKED:    # hard traversal bound, matched or not
                    return count, recent, newest
                if not fn.endswith(suffixes):
                    continue
                try:
                    mt = os.stat(os.path.join(dirpath, fn)).st_mtime
                except OSError:
                    continue
                count += 1
                if mt > newest:
                    newest = mt
                if mt >= cutoff:
                    recent += 1
                if count >= cap:
                    return count, recent, newest
    except OSError:
        pass
    return count, recent, newest


def analyze_providers(home: Path) -> dict:
    """Per-provider activity on THIS box. Counts only — no content, no paths."""
    out: dict[str, dict] = {}
    for prov, (roots, suffixes) in PROVIDERS.items():
        total = recent = 0
        newest = 0.0
        present = False
        for tmpl in roots:
            root = Path(tmpl.format(home=str(home)))
            if not root.exists():
                continue
            present = True
            c, r, n = _scan_dir(root, suffixes, MAX_FILES_PER_PROVIDER)
            total += c
            recent += r
            newest = max(newest, n)
            break  # first existing root is the canonical session store for this provider
        out[prov] = {
            "present": present,
            "sessions": total,
            "sessions_24h": recent,
            "newest": (datetime.fromtimestamp(newest).isoformat(timespec="seconds") if newest else None),
        }
    return out


def memory_delta(since: datetime | None) -> list[str]:
    """Basenames of memory files changed since the last curation (the transferable delta)."""
    if not MEMORY.exists():
        return []
    cutoff = since.timestamp() if since else 0.0
    changed: list[str] = []
    for p in sorted(MEMORY.rglob("*.md")):
        try:
            if p.stat().st_mtime >= cutoff:
                changed.append(p.relative_to(MEMORY).as_posix())
        except OSError:
            continue
    return changed[:200]  # bound the list; full set is reconstructable from the repo


def _parse_iso(s) -> datetime | None:
    if not isinstance(s, str):
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_prev_state(machine: str) -> dict:
    f = STATE / f"session-curation-{machine}.json"
    if f.exists():
        try:
            return json.loads(f.read_text())
        except (OSError, ValueError):
            pass
    return {}


def build_state(machine: str, home: Path) -> tuple[dict, list[str], dict]:
    prev = load_prev_state(machine)
    since = _parse_iso(prev.get("last_curated_at"))
    providers = analyze_providers(home)
    changed = memory_delta(since)
    now = _now().isoformat(timespec="seconds")
    state = {
        "machine": machine,
        "last_curated_at": now,
        "providers": {p: d["sessions"] for p, d in providers.items()},
        "sessions_24h": sum(d["sessions_24h"] for d in providers.values()),
        "providers_active": sorted(p for p, d in providers.items() if d["present"]),
        "memory_files_changed": len(changed),
        "digest_ref": CURATION_REF,
        "schema_version": 1,
    }
    return state, changed, providers


def render_digest(state: dict, providers: dict, changed: list[str]) -> str:
    lines = [
        f"# Session-curation digest — {state['machine']}",
        f"_Curated {state['last_curated_at']} · transferable to sibling machines via `{CURATION_REF}` ref_",
        "",
        "## Provider session activity (this box)",
        "| Provider | Present | Sessions | Last 24h | Newest |",
        "|---|---|---|---|---|",
    ]
    for prov, d in providers.items():
        lines.append(f"| {prov} | {'yes' if d['present'] else 'no'} | {d['sessions']} | "
                     f"{d['sessions_24h']} | {d['newest'] or '—'} |")
    lines += [
        "",
        f"## Memory delta — {len(changed)} file(s) changed since last curation",
    ]
    lines += [f"- `{c}`" for c in changed[:50]] or ["- (none)"]
    if len(changed) > 50:
        lines.append(f"- … and {len(changed) - 50} more")
    lines += [
        "",
        "## Fleet transfer",
        f"- Fingerprint published to git ref `{CURATION_REF}` (per-machine blob).",
        "- Pull all boxes' digests: `uv run --script scripts/curation/curate_session_memory.py --collect`.",
        "",
    ]
    return "\n".join(lines)


def publish_fingerprint(machine: str) -> str:
    """Publish this box's fingerprint to the dedicated ref via the equivalence-state CLI, in a
    BOUNDED subprocess. The git push has no internal timeout and CAN hang (network/auth/lock —
    observed: a sibling publish stuck >1h), so we cap it and fail soft: a hung or failed publish
    must never stall the daily curation cron, whose state JSON is already written before this runs.
    Subprocess (not import) so the timeout actually kills the blocked git child; portable to Windows."""
    state_file = STATE / f"session-curation-{machine}.json"
    cli = REPO / "scripts" / "monitoring" / "equivalence_state.py"
    if not state_file.exists() or not cli.exists():
        return "publish-skipped (no state/cli)"
    try:
        r = subprocess.run(
            [sys.executable, str(cli), "publish", "--repo", str(REPO),
             "--role", machine, "--file", str(state_file), "--ref", CURATION_REF],
            capture_output=True, text=True, timeout=PUBLISH_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return f"publish-timeout ({PUBLISH_TIMEOUT_S}s)"
    except Exception as e:  # noqa: BLE001 — best-effort fleet slice; never fail local curation
        return f"publish-error: {str(e)[:80]}"
    return "published" if r.returncode == 0 else f"publish-rc{r.returncode}"


def collect_fleet() -> str:
    """Pull every box's fingerprint from the ref and render a merged fleet view."""
    sys.path.insert(0, str(REPO / "scripts" / "monitoring"))
    import equivalence_state as store  # type: ignore
    try:
        fps = store.collect(str(REPO), ref=CURATION_REF)
    except store.StoreUnavailable as e:  # type: ignore[attr-defined]
        return f"# Session-curation fleet view\n\n_store unavailable: {e}_\n"
    lines = ["# Session-curation fleet view", f"_collected {_now().isoformat(timespec='seconds')}_", "",
             "| Machine | Last curated | Sessions 24h | Active providers | Mem Δ |",
             "|---|---|---|---|---|"]
    for fp in sorted(fps, key=lambda x: x.get("machine", "")):
        lines.append(f"| {fp.get('machine','?')} | {fp.get('last_curated_at','?')} | "
                     f"{fp.get('sessions_24h','?')} | {','.join(fp.get('providers_active', []))} | "
                     f"{fp.get('memory_files_changed','?')} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Daily session analysis + memory curation")
    ap.add_argument("--machine", default=None, help="override machine label")
    ap.add_argument("--home", default=os.environ.get("HOME") or os.path.expanduser("~"))
    ap.add_argument("--collect", action="store_true", help="merge all boxes' fingerprints → fleet view")
    ap.add_argument("--stdout", action="store_true", help="print state JSON, do not write or publish")
    ap.add_argument("--no-publish", action="store_true", help="curate locally but skip the git-ref publish")
    a = ap.parse_args(argv)

    if a.collect:
        out = STATE / "session-curation-fleet.md"
        text = collect_fleet()
        if a.stdout:
            print(text)
        else:
            STATE.mkdir(parents=True, exist_ok=True)
            out.write_text(text)
            print(f"wrote {out}")
        return 0

    machine = a.machine or machine_label()
    home = Path(a.home)
    state, changed, providers = build_state(machine, home)

    if a.stdout:
        print(json.dumps(state, indent=2))
        return 0

    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / f"session-curation-{machine}.json").write_text(json.dumps(state, indent=2) + "\n")
    (STATE / f"session-curation-digest-{machine}.md").write_text(render_digest(state, providers, changed))
    pub = "skipped" if a.no_publish else publish_fingerprint(machine)
    print(f"curated {machine}: {state['sessions_24h']} sessions/24h across "
          f"{len(state['providers_active'])} providers, {state['memory_files_changed']} memory Δ "
          f"(publish: {pub})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
