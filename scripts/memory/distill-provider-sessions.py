#!/usr/bin/env python3
"""
distill-provider-sessions.py — Bridge other-provider sessions into the Claude dream.

WHAT / WHY
  Claude Code's "dreaming" (auto-memory consolidation) only ingests its own
  auto-memory store + its own ~/.claude/projects/*/*.jsonl transcripts. It has
  NO native awareness of Codex, Gemini, or Hermes sessions. Per the user's
  decision (see reference_claude_dreaming_managed_agents.md), the Claude dream
  is THE cross-provider consolidator — so this script feeds it.

  It reads other-provider session files, pre-filters them to conversational
  signal (dropping tool-output/blob noise — ~5.3 GB raw across providers),
  batches them, and asks Claude itself (headless `claude -p` on the
  subscription — "get Claude to do the dreaming", ONE consistent engine for all
  providers) to extract only durable, novel learnings. Each learning is written
  as a provenance-tagged memory file into the Claude auto-memory dir, which the
  native dream then consolidates / dedupes / prunes.

  Filenames are content-hashed so re-runs are idempotent (same learning ->
  same file -> overwrite, never flood). The dream prunes whatever it doesn't
  keep.

DESIGN NOTES
  - Resumable: a per-provider watermark (last-processed session mtime) means a
    mid-backfill kill just resumes. Essential given codex CLI flakiness over
    10k sessions (feedback_codex_cli_0_124_upstream_regression).
  - Batched: several pre-filtered sessions per codex call -> fewer flaky calls.
  - stdlib-only: shells out to `codex` for the LLM, so no pip deps; runs under
    plain python3 or `uv run`.

USAGE
  python3 distill-provider-sessions.py --dry-run --provider codex --limit 3
      # distill 3 codex sessions, print what WOULD be written, no files, no watermark
  python3 distill-provider-sessions.py --backfill          # all history, all providers
  python3 distill-provider-sessions.py                      # incremental (since watermark)

  Flags: --provider {codex,gemini,hermes,all}  --backfill  --dry-run
         --limit N (cap sessions this run)  --batch-size N  --since-days N
         --max-learnings-per-provider N

Called by: scripts/memory/bridge-providers-to-dream.sh (cron, 04:00 daily)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from shutil import which

HOME = Path.home()

# --- Provider session locations ------------------------------------------------
CODEX_SESSIONS = HOME / ".codex" / "sessions"          # YYYY/MM/DD/rollout-*.jsonl
GEMINI_ROOT = HOME / ".gemini"                          # **/chats/session-*.json
HERMES_SESSIONS = HOME / ".hermes" / "sessions"        # session_*.json

# --- Claude auto-memory dir (the dream's input) --------------------------------
# Matches autoMemoryDirectory in ~/.claude/settings.json; override with env.
DEFAULT_MEM_DIR = HOME / ".claude" / "projects" / "-mnt-local-analysis-workspace-hub" / "memory"
MEM_DIR = Path(os.environ.get("CLAUDE_AUTO_MEMORY_DIR", str(DEFAULT_MEM_DIR)))

WATERMARK_FILE = MEM_DIR / ".provider-bridge-watermark.json"

# --- Distiller backend: Claude itself, headless, on the subscription ----------
# "Get Claude to do the dreaming" — dreaming is a Claude-native capability, so
# the cross-provider distiller is Claude too, for ONE consistent engine across
# all providers/sessions. Uses `claude -p` (subscription auth, no API key; the
# .env ANTHROPIC_API_KEY is empty). Calls run from a neutral cwd so they don't
# reload this repo's ~67K-token CLAUDE.md/MEMORY.md context on every batch.
CLAUDE_BIN = os.environ.get("CLAUDE_BIN") or (
    "claude" if which("claude") else str(HOME / ".npm-global" / "bin" / "claude")
)
CLAUDE_MODEL = os.environ.get("DISTILL_MODEL", "haiku")
CLAUDE_TIMEOUT = int(os.environ.get("DISTILL_TIMEOUT_SECONDS", "180"))
# Neutral working dir for headless calls — no project CLAUDE.md to load.
_NEUTRAL_CWD = tempfile.mkdtemp(prefix="distill-cwd-")

# --- Pre-filter / batching knobs ------------------------------------------------
PER_SESSION_CHAR_CAP = int(os.environ.get("PER_SESSION_CHAR_CAP", "6000"))
MIN_SESSION_CHARS = int(os.environ.get("MIN_SESSION_CHARS", "200"))
DEFAULT_BATCH_SIZE = int(os.environ.get("DISTILL_BATCH_SIZE", "8"))

# Keys whose string values look like conversational text; everything else
# (tool results, diffs, base64, file dumps) is noise we drop before the LLM.
_TEXT_KEYS = {"text", "message", "content", "value", "input_text", "output_text"}
_NOISE_RE = re.compile(r"(data:[^;]+;base64,|\b[A-Za-z0-9+/]{200,}={0,2})")

# Roles whose content is conversation we want. System/developer/tool turns and
# their boilerplate (sandbox/permissions/instructions blocks) are dropped.
_HUMAN_ROLES = {"user", "assistant", "agent", "model", "human", "ai"}
_SKIP_ROLES = {"system", "developer", "tool", "function", "tool_result"}
# System-prompt boilerplate fingerprints — drop any segment starting with these.
_BOILERPLATE_RE = re.compile(
    r"^\s*(<permissions|<user_instructions|<environment|<system|"
    r"sandbox_mode|you are codex|you are a|# instructions\b|## instructions\b)",
    re.IGNORECASE,
)


# ==============================================================================
# Pre-filter: extract conversational text from each provider's session format
# ==============================================================================

def _harvest_text(obj, out: list[str], depth: int = 0, role: str | None = None) -> None:
    """Recursively pull human/assistant text from arbitrary nested JSON,
    skipping system/tool turns and obvious blob noise. Role-aware: when a dict
    carries a `role`, that role governs its subtree. Defensive — provider
    formats drift across versions, so we don't hard-code one schema."""
    if depth > 12:
        return
    if isinstance(obj, dict):
        # A role on this node governs its subtree (messages are role-tagged).
        node_role = obj.get("role")
        if isinstance(node_role, str):
            role = node_role.lower()
        if role in _SKIP_ROLES:
            return  # drop system/developer/tool turns wholesale
        for k, v in obj.items():
            if k == "role":
                continue
            if isinstance(v, str):
                seg = v.strip()
                # Only collect text under known human/assistant roles, or when
                # role is still unknown (many formats put the first user turn
                # before any role tag). Never collect once role is a skip-role.
                collectable = role in _HUMAN_ROLES or role is None
                if (k in _TEXT_KEYS and seg and collectable
                        and not _NOISE_RE.search(seg)
                        and not _BOILERPLATE_RE.match(seg)):
                    out.append(seg)
            else:
                _harvest_text(v, out, depth + 1, role)
    elif isinstance(obj, list):
        for item in obj:
            _harvest_text(item, out, depth + 1, role)


def _filter_codex(path: Path) -> str:
    """Codex JSONL. The clean conversation lives in `event_msg` records of
    subtype user_message / agent_message (the `message` field). We target those
    exclusively — `response_item/message` duplicates the assistant text AND
    carries the AGENTS.md / <permissions> injections, `reasoning` is encrypted,
    and function_call(_output) is tool noise. All dropped."""
    parts: list[str] = []
    found_event_msg = False
    try:
        with path.open("r", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("type") != "event_msg":
                    continue
                p = rec.get("payload", {})
                if not isinstance(p, dict) or p.get("type") not in ("user_message", "agent_message"):
                    continue
                found_event_msg = True
                msg = p.get("message")
                if isinstance(msg, str) and msg.strip() and not _NOISE_RE.search(msg) \
                        and not _BOILERPLATE_RE.match(msg.strip()):
                    parts.append(msg.strip())
    except OSError:
        return ""
    # Fallback for older codex formats with no event_msg stream.
    if not found_event_msg:
        return _filter_json_messages(path) if path.suffix == ".json" else ""
    return _join(parts)


def _filter_json_messages(path: Path) -> str:
    """Gemini & Hermes: single JSON object with a `messages[]` array."""
    try:
        data = json.loads(path.read_text(errors="replace"))
    except (OSError, json.JSONDecodeError):
        return ""
    parts: list[str] = []
    msgs = data.get("messages") if isinstance(data, dict) else None
    _harvest_text(msgs if msgs is not None else data, parts)
    return _join(parts)


def _join(parts: list[str]) -> str:
    seen, uniq = set(), []
    for p in parts:
        key = p[:120]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    text = "\n".join(uniq).strip()
    return text[:PER_SESSION_CHAR_CAP]


PROVIDERS = {
    "codex":  (lambda: sorted(CODEX_SESSIONS.rglob("rollout-*.jsonl")), _filter_codex),
    "gemini": (lambda: sorted(GEMINI_ROOT.rglob("session-*.json")),     _filter_json_messages),
    "hermes": (lambda: sorted(HERMES_SESSIONS.glob("session_*.json")),  _filter_json_messages),
}


# ==============================================================================
# Watermark
# ==============================================================================

def load_watermark() -> dict:
    if WATERMARK_FILE.exists():
        try:
            return json.loads(WATERMARK_FILE.read_text())
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def save_watermark(wm: dict) -> None:
    WATERMARK_FILE.write_text(json.dumps(wm, indent=2))


# ==============================================================================
# Distillation via codex exec (gpt-5.5)
# ==============================================================================

_PROMPT = """You are performing a DREAM — distilling AI-agent session logs into \
durable memory for a cross-provider memory store. The sessions below come from \
the {provider} agent.

Extract ONLY learnings that are durable, non-obvious, and worth remembering across \
future sessions: converged workflows, recurring mistakes and their fixes, tooling \
quirks, user preferences, environment facts, and architectural decisions.

STRICT rules:
- Skip anything transient (one-off task state, ephemeral file paths, "now doing X").
- Skip anything a competent engineer would already know.
- Each learning must stand alone without the session context.
- Prefer FEWER, higher-signal learnings. An empty list is correct when the batch \
holds nothing durable.
- Keep each body to 1-3 sentences. Tags are short kebab-case topic labels.

OUTPUT: Return ONLY a single JSON object, no prose and no markdown fences, shaped \
exactly as: {{"learnings": [{{"title": "...", "body": "...", "tags": ["..."]}}]}}

--- SESSIONS ---
{body}
"""


def _extract_json_obj(text: str) -> dict | None:
    """Parse a JSON object out of model output that may be fence-wrapped or
    prefixed with prose."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None


def claude_distill(provider: str, batch_text: str) -> list[dict] | None:
    """Distill via headless `claude -p` (the subscription). Returns a list of
    learning dicts on success (possibly empty == nothing durable in the batch),
    or None on FAILURE (non-zero exit, no output, unparseable). Callers must
    NOT advance the watermark past a None batch — those sessions get retried.
    One consistent Claude engine for all providers."""
    prompt = _PROMPT.format(provider=provider, body=batch_text)
    # Prompt goes via STDIN, not argv — a full batch (~120 KB) exceeds the OS
    # per-argument limit (MAX_ARG_STRLEN ~128 KB). `claude -p` with no positional
    # reads instructions from stdin.
    cmd = [
        "timeout", str(CLAUDE_TIMEOUT), CLAUDE_BIN, "-p",
        "--output-format", "json", "--model", CLAUDE_MODEL,
    ]
    try:
        proc = subprocess.run(
            cmd, input=prompt, cwd=_NEUTRAL_CWD,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
    except OSError as e:
        sys.stderr.write(f"[distill] claude -p spawn error for {provider} batch: {e}\n")
        return None  # transient/infra — abort provider, retry next run
    if proc.returncode != 0 or not proc.stdout.strip():
        sys.stderr.write(
            f"[distill] claude -p FAILED (rc={proc.returncode}) for {provider} batch: "
            f"{(proc.stderr or proc.stdout or '')[:300]}\n"
        )
        return None
    envelope = _extract_json_obj(proc.stdout)
    if not envelope:
        sys.stderr.write(f"[distill] claude -p unparseable envelope for {provider} batch\n")
        return None
    # A subscription error surfaces inside the envelope, not via exit code.
    if isinstance(envelope, dict) and envelope.get("is_error"):
        sys.stderr.write(
            f"[distill] claude -p envelope error for {provider} batch: "
            f"{str(envelope.get('result') or envelope.get('api_error_status'))[:200]}\n"
        )
        return None
    # `claude -p --output-format json` wraps the answer in `.result`.
    inner = envelope.get("result", envelope) if isinstance(envelope, dict) else None
    parsed = _extract_json_obj(inner) if isinstance(inner, str) else inner
    if not isinstance(parsed, dict):
        # Claude REPLIED but the result wasn't JSON (prose, refusal, garbled).
        # This is a content problem with THIS batch, not an infra failure —
        # return [] (skip this batch, advance watermark, continue) rather than
        # None (which would abort the whole provider and wedge it forever on a
        # persistently-bad batch). The infra-failure paths above still return None.
        sys.stderr.write(f"[distill] claude -p result not JSON for {provider} batch "
                         f"— skipping this batch, continuing\n")
        return []
    out = parsed.get("learnings", [])
    return [l for l in out if isinstance(l, dict) and l.get("title") and l.get("body")]


# ==============================================================================
# Memory-file emission (idempotent, content-hashed)
# ==============================================================================

def write_learning(provider: str, learning: dict, dry_run: bool) -> Path | None:
    title = learning["title"].strip()
    body = learning["body"].strip()
    tags = [str(t).strip() for t in learning.get("tags", []) if str(t).strip()]
    digest = hashlib.sha1(f"{provider}:{title}:{body}".encode()).hexdigest()[:8]
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48] or "untitled"
    fname = f"crossprovider_{provider}_{slug}_{digest}.md"
    path = MEM_DIR / fname
    content = (
        "---\n"
        f"name: crossprovider {provider} {slug}\n"
        f"description: {title}\n"
        "metadata:\n"
        "  type: reference\n"
        f"  source: {provider}\n"
        f"  bridged: {datetime.now(timezone.utc).date().isoformat()}\n"
        f"  tags: [{', '.join(tags)}]\n"
        "---\n\n"
        f"{body}\n\n"
        f"*(Distilled from {provider} sessions by bridge-providers-to-dream; "
        "the Claude dream consolidates and prunes these.)*\n"
    )
    if dry_run:
        return path
    path.write_text(content)
    return path


# ==============================================================================
# Main per-provider run
# ==============================================================================

def run_provider(provider: str, args, watermark: dict) -> dict:
    lister, filt = PROVIDERS[provider]
    files = lister()
    last_ts = 0.0 if args.backfill else float(watermark.get(provider, 0))
    since_cut = (time.time() - args.since_days * 86400) if args.since_days else None

    # Select sessions newer than watermark (and within --since-days if set).
    pending = []
    for f in files:
        try:
            mt = f.stat().st_mtime
        except OSError:
            continue
        if mt <= last_ts:
            continue
        if since_cut and mt < since_cut:
            continue
        pending.append((mt, f))
    pending.sort()
    if args.limit:
        pending = pending[: args.limit]

    stats = {"provider": provider, "available": len(files), "pending": len(pending),
             "distilled_sessions": 0, "learnings": 0, "batches": 0, "files": []}
    if not pending:
        return stats

    max_learn = args.max_learnings_per_provider
    high_water = last_ts
    pending_skip_hw = last_ts  # advances over skipped (too-small) sessions only
    batch: list[str] = []
    batch_mts: list[float] = []

    def flush() -> bool:
        """Process the current batch. Returns True on success (watermark may
        advance), False on distill FAILURE (watermark must hold so the batch
        is retried next run)."""
        nonlocal high_water
        if not batch:
            return True
        stats["batches"] += 1
        learnings = claude_distill(provider, "\n\n===== NEXT SESSION =====\n\n".join(batch))
        if learnings is None:
            batch.clear(); batch_mts.clear()
            return False
        for ln in learnings:
            if max_learn and stats["learnings"] >= max_learn:
                break
            p = write_learning(provider, ln, args.dry_run)
            if p:
                stats["files"].append(p.name)
            stats["learnings"] += 1
        # Success: it is safe to advance past every session in this batch
        # (and any skipped-small sessions we passed on the way to it).
        high_water = max(high_water, pending_skip_hw, max(batch_mts))
        batch.clear(); batch_mts.clear()
        return True

    aborted = False
    for mt, f in pending:
        text = filt(f)
        if len(text) < MIN_SESSION_CHARS:
            pending_skip_hw = max(pending_skip_hw, mt)
            continue
        header = f"[{provider}] {f.name} ({datetime.fromtimestamp(mt).date()})"
        batch.append(f"{header}\n{text}")
        batch_mts.append(mt)
        stats["distilled_sessions"] += 1
        if len(batch) >= args.batch_size:
            ok = flush()
            if not args.dry_run:
                watermark[provider] = high_water
                save_watermark(watermark)
            if not ok:
                # Distill failed (quota/timeout/transport) — stop this provider
                # at the last good watermark; next run resumes here.
                sys.stderr.write(f"[distill] {provider}: aborting run at watermark "
                                 f"{high_water} after batch failure (will retry next run)\n")
                aborted = True
                break
        if max_learn and stats["learnings"] >= max_learn:
            break
    if not aborted:
        if flush():
            # Final batch good — safe to advance over any trailing pure-skip tail.
            high_water = max(high_water, pending_skip_hw)
        else:
            aborted = True

    if not args.dry_run:
        watermark[provider] = high_water
        save_watermark(watermark)
    stats["aborted"] = aborted
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--provider", choices=list(PROVIDERS) + ["all"], default="all")
    ap.add_argument("--backfill", action="store_true",
                    help="ignore watermark; process ALL history (token-heavy)")
    ap.add_argument("--dry-run", action="store_true",
                    help="distill but write no files and do not advance watermark")
    ap.add_argument("--limit", type=int, default=0, help="cap sessions processed this run")
    ap.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    ap.add_argument("--since-days", type=int, default=0,
                    help="only sessions modified within N days")
    ap.add_argument("--max-learnings-per-provider", type=int, default=0,
                    help="cap learnings written per provider this run (0 = no cap)")
    args = ap.parse_args()

    if not MEM_DIR.exists():
        sys.stderr.write(f"[distill] auto-memory dir not found: {MEM_DIR}\n")
        return 1

    providers = list(PROVIDERS) if args.provider == "all" else [args.provider]
    watermark = load_watermark()

    print(f"[distill] mode={'BACKFILL' if args.backfill else 'incremental'}"
          f"{' DRY-RUN' if args.dry_run else ''} | engine=claude:{CLAUDE_MODEL} | mem={MEM_DIR}")
    grand = {"learnings": 0, "sessions": 0}
    for prov in providers:
        st = run_provider(prov, args, watermark)
        grand["learnings"] += st["learnings"]
        grand["sessions"] += st["distilled_sessions"]
        print(f"[distill] {prov}: available={st['available']} pending={st['pending']} "
              f"distilled={st['distilled_sessions']} batches={st['batches']} "
              f"learnings={st['learnings']}")
        if args.dry_run and st["files"]:
            print(f"           would write: {', '.join(st['files'][:10])}"
                  + (" ..." if len(st["files"]) > 10 else ""))
    print(f"[distill] TOTAL: {grand['sessions']} sessions -> {grand['learnings']} learnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
