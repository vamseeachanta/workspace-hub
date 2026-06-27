#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""extract_hermes_patterns.py — Hermes pattern → skill/memory CANDIDATE emitter (#3253, epic #3248).

Reads the **Hermes-authored** memory (``~/.hermes/memories/MEMORY.md`` + ``USER.md``; NEVER the
bridge-written ``cross-provider.md`` — that would feed canonical content back as a candidate
forever) and emits recurring learnings as **review-gated candidates** into
``.claude/state/candidates/hermes-pattern-candidates.md``. It NEVER writes a canonical surface and
NEVER marks anything promoted — promotion to a skill/memory stays the **human owner-review gate**
(same gate as #3252). Mirrors the ``detect_skill_drift.py`` shape: a PURE decide-core
(``extract_patterns`` / ``strip_bridge_block`` / ``evaluate`` — no IO, no clock, no subprocess) plus
a thin CLI that gathers inputs, calls the core, and routes each alert through an injectable
``notify_fn``.

Round-2 BLOCKER fix (the de-dup ordering problem):
  The bridge (``bridge-hermes-claude.sh`` §2-3) re-injects the SAME Hermes-authored ``MEMORY.md`` /
  ``USER.md`` lines into the ``<!-- BRIDGE:START -->`` … ``<!-- BRIDGE:END -->`` block of
  ``agents.md`` on every run, *before* this extractor's §7c step runs in the same process. Because
  ``_slug('- foo') == _slug('foo')``, a naive ``MEMORY.rglob`` content index would read back the
  just-injected lines and mark EVERY candidate already-canonical → emit zero candidates forever.
  ``canonical_text_index()`` therefore STRIPS the bridge block before slugifying, so de-dup runs
  only against genuinely human-promoted memory. This is **independent of whether §7c runs before or
  after the §3 injection** — robust by construction (vs. the weaker "snapshot the index before
  injection", which would still break if §7c were re-ordered).

Hard-rule compliance:
  * Rule 1 — writes ONLY under ``.claude/state/candidates/``; ``status: candidate`` only; never
    ``promoted`` / ``approved`` / owner-gate labels.
  * Rule 4 — returns 0 on the candidates-found path; the "new candidates" signal travels via the
    last-seen state + ``notify.sh``, not the exit code.
  * Rule 5 — optional ``--publish`` to the ``hermes-pattern-candidate-state`` ref is OFF by default
    and bounded by a 90s subprocess timeout, fail-soft.
  * No pyyaml dependency — the bridge launches bare ``python3`` / ``uv run --no-project python``;
    the deny-list is parsed by a dependency-free regex.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[2]

# Cross-dir reuse: the dependency lives in scripts/curation/, this module in scripts/memory/.
# Mirror detect_skill_drift.py:49-54 — insert the curation dir on sys.path BEFORE importing.
_CURATION_DIR = str(REPO / "scripts" / "curation")
if _CURATION_DIR not in sys.path:
    sys.path.insert(0, _CURATION_DIR)
from curate_session_memory import machine_label, MEMORY  # noqa: E402  (path set up above)

PUBLISH_TIMEOUT_S = 90
CAND_REF = "hermes-pattern-candidate-state"

STATE = REPO / ".claude" / "state"
STATE_CAND = STATE / "candidates"
CANDIDATES = STATE_CAND / "hermes-pattern-candidates.md"
SKILLS_DIR = REPO / ".claude" / "skills"
DENY_LIST = REPO / ".legal-deny-list.yaml"
NOTIFY_SH = REPO / "scripts" / "notify.sh"
EQUIVALENCE_CLI = REPO / "scripts" / "monitoring" / "equivalence_state.py"

HERMES_DIR = Path.home() / ".hermes" / "memories"
SOURCES = ["MEMORY.md", "USER.md"]            # Hermes-AUTHORED only — NOT cross-provider.md (loop guard)

BRIDGE_START = "BRIDGE:START"                  # markers written by the bridge §3 (:102/:108)
BRIDGE_END = "BRIDGE:END"

# Heuristic: a learning that reads like a reusable rule/pattern is a "skill" candidate; otherwise
# it is a "memory" candidate. Not load-bearing for any hard rule — just a reviewer hint.
_SKILL_HINTS = ("always", "never", "prefer", "use ", "pattern", "workflow", "gotcha", "rule", "avoid")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# PURE CORE — no IO, no clock, no subprocess
# --------------------------------------------------------------------------- #


def _slug(text: str) -> str:
    """Normalize a line to a stable key. PURE. Strips any leading '- ' (the bridge injects each
    Hermes line as ``- ${line}``) via the ``[^a-z0-9]+`` collapse + strip."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def slug_tokens(text: str) -> set[str]:
    """Per-line slug set of a blob (empty slugs dropped). PURE."""
    return {s for ln in text.splitlines() if (s := _slug(ln))}


def strip_bridge_block(text: str) -> str:
    """Remove the inclusive ``BRIDGE:START`` … ``BRIDGE:END`` span (round-2 BLOCKER fix). PURE.

    The bridge re-injects the same Hermes-authored lines into this block on every run, so excluding
    it makes the de-dup index compare candidates only against genuinely human-promoted memory —
    independent of §7c's placement relative to the injection step.
    """
    out: list[str] = []
    skipping = False
    for ln in text.splitlines():
        if BRIDGE_START in ln:
            skipping = True
            continue                              # drop the START marker line
        if BRIDGE_END in ln:
            skipping = False
            continue                              # drop the END marker line
        if not skipping:
            out.append(ln)
    return "\n".join(out)


def _kind_for(text: str) -> str:
    low = text.lower()
    return "skill" if any(h in low for h in _SKILL_HINTS) else "memory"


def extract_patterns(hermes_text: str, *, source_file: str = "MEMORY.md") -> list[dict]:
    """Split the '§'/newline-delimited Hermes items (same split the bridge uses), normalize, and
    keep each as a keyed candidate. De-dups within the source (first occurrence wins). PURE — no IO.

    Each candidate: ``{key, summary, source_file, kind}``; ``key = _slug(text)`` (strips any leading
    '- ', matching the bridge's ``- ${line}`` injection form).
    """
    cands: list[dict] = []
    seen: set[str] = set()
    for seg in re.split(r"[§\n]", hermes_text):
        seg = seg.strip()
        if not seg or seg == "§":
            continue
        key = _slug(seg)
        if not key or key in seen:
            continue
        # Drop the leading list-marker / heading punctuation from the human-facing summary.
        summary = re.sub(r"^[-*#>\s]+", "", seg).strip()
        if not summary:
            continue
        seen.add(key)
        cands.append({"key": key, "summary": summary, "source_file": source_file,
                      "kind": _kind_for(summary)})
    return cands


def canonical_text_index() -> set[str]:
    """Slug index of the FULL canonical CONTENT surface (``MEMORY.rglob('*.md')`` text — no 200-cap,
    no mtime cutoff) MINUS the bridge-injected block (round-2 fix). Reads files (no clock)."""
    idx: set[str] = set()
    if MEMORY.exists():
        for p in MEMORY.rglob("*.md"):
            try:
                idx |= slug_tokens(strip_bridge_block(p.read_text(encoding="utf-8", errors="replace")))
            except OSError:
                continue
    return idx


def skill_text_index() -> set[str]:
    """Slug index of the skills tree: each SKILL.md's directory name + its heading / ``name:`` lines
    (header region only, bounded). Reads files (no clock)."""
    idx: set[str] = set()
    if not SKILLS_DIR.exists():
        return idx
    for p in SKILLS_DIR.rglob("SKILL.md"):
        try:
            idx.add(_slug(p.parent.name))
            head = p.read_text(encoding="utf-8", errors="replace")[:4096]
            for ln in head.splitlines():
                stripped = ln.strip()
                if stripped.startswith("#") or stripped.lower().startswith("name:"):
                    if s := _slug(stripped):
                        idx.add(s)
        except OSError:
            continue
    return idx


def is_already_canonical(cand: dict, canonical_slugs: set[str], skill_slugs: set[str]) -> bool:
    """PURE de-dup gate: present in human-promoted canonical memory OR the skills tree."""
    return cand["key"] in canonical_slugs or cand["key"] in skill_slugs


def is_sensitive(text: str, deny_patterns: list[str]) -> bool:
    """PURE fail-closed scrub: True if any deny-list pattern matches (case-insensitive, broader)."""
    return any(re.search(p, text, re.I) for p in deny_patterns)


def candidate_signature(cands: list[dict]) -> str:
    """Sorted-keys fingerprint (order-independent). PURE. ``CLEAN`` when empty."""
    return "CLEAN" if not cands else "|".join(sorted(c["key"] for c in cands))


def evaluate(patterns, canonical_slugs, skill_slugs, deny_patterns, last_seen, *, now_iso) -> dict:
    """Decide which patterns are fresh candidates + whether to alert. PURE — no IO/clock.

    De-dups against canonical/skills, drops PII matches (fail-closed), and fires a single ``pass``
    alert only on a transition into / change-of the candidate set (last-seen spam suppression).
    """
    fresh: list[dict] = []
    dropped = 0
    for c in patterns:
        if is_already_canonical(c, canonical_slugs, skill_slugs):
            continue
        if is_sensitive(f"{c.get('summary', '')} {c['key']}", deny_patterns):
            dropped += 1                          # fail-closed: drop, do not redact-and-emit
            continue
        fresh.append(c)
    sig = candidate_signature(fresh)
    last_sig = (last_seen or {}).get("signature") if isinstance(last_seen, dict) else None
    new = sig != "CLEAN" and sig != last_sig
    alerts = (
        [{"job": "hermes-pattern-candidates", "status": "pass",
          "detail": f"{len(fresh)} new Hermes pattern candidate(s) for review"}]
        if new else []
    )
    return {
        "candidates": fresh,
        "dropped_sensitive": dropped,
        "signature": sig,
        "new": new,
        "alerts": alerts,
        "new_state": {"signature": sig, "updated_at": now_iso},
    }


def existing_candidate_keys(path: Path) -> set[str]:
    """The candidate keys already recorded in the file. PURE-ish (one read)."""
    if not path.exists():
        return set()
    return {m.group(1) for m in re.finditer(r"^- key: (\S+)", path.read_text(encoding="utf-8"), re.M)}


# --------------------------------------------------------------------------- #
# THIN CLI — IO, clock, subprocess live here
# --------------------------------------------------------------------------- #


def _read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def load_deny_patterns(path: Path) -> list[str]:
    """Extract client/PII deny patterns from .legal-deny-list.yaml WITHOUT a yaml dependency (the
    bridge launches bare python3). Each ``pattern: "..."`` value → an escaped regex literal."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    pats: list[str] = []
    for m in re.finditer(r"""^\s*-?\s*pattern:\s*["']([^"']+)["']""", text, re.M):
        pats.append(re.escape(m.group(1)))
    return pats


def append_candidates_md(path: Path, cands: list[dict], dropped: int) -> None:
    """Idempotently append a dated ``## Candidates`` block listing only NOT-yet-recorded keys. Never
    double-appends — safe under re-runs and the bridge's §8 stash-then-restore (minor #2). Writes
    ONLY this path (Rule 1: candidates surface, never canonical)."""
    have = existing_candidate_keys(path)
    new = [c for c in cands if c["key"] not in have]
    if not new:
        return                                    # no new keys → file untouched (idempotent: a
        # dropped-only run must NOT re-append a notice block every cron cycle — the dropped count is
        # surfaced in the run-log stderr instead, so the candidate file stays stash-/re-run-safe).
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "",
        f"## Candidates (from {today} — Hermes patterns)",
        "> Auto-emitted by extract_hermes_patterns.py — status: candidate. Promotion to a skill/memory",
        "> is a HUMAN owner-review action (gate per #3252). Do not edit manually.",
    ]
    for c in new:
        summary = c.get("summary", "").replace("\n", " ").replace('"', "'")
        lines.append(
            f'- key: {c["key"]}  status: candidate  kind: {c.get("kind", "memory")}  '
            f'source: {c.get("source_file", "?")}  summary: "{summary}"'
        )
    if dropped:
        lines.append(f"(dropped {dropped} sensitive candidate(s) — see run log)")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Hermes Pattern Candidates\n"
    path.write_text(existing.rstrip("\n") + "\n" + "\n".join(lines), encoding="utf-8")


def _default_notify(alert: dict) -> None:
    """Append one JSONL event via scripts/notify.sh (source=cron, job=hermes-pattern-candidates)."""
    status = alert.get("status", "pass")
    detail = alert.get("detail", "")
    try:
        subprocess.run(
            ["bash", str(NOTIFY_SH), "cron", "hermes-pattern-candidates", status, detail],
            check=False, timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass                                       # a wedged notify.sh must never stall the cron


def _last_seen_path(machine: str) -> Path:
    return STATE_CAND / f"hermes-patterns-last-seen-{machine}.json"


def publish_candidates(machine: str) -> str:
    """Publish the candidate file to the dedicated git ref via the equivalence-state CLI, in a
    BOUNDED subprocess. The git push can hang (a sibling publish was observed stuck >1h), so we cap
    it and fail soft — a hung/failed publish must never stall the bridge. Mirrors
    curate_session_memory.publish_fingerprint."""
    if not CANDIDATES.exists() or not EQUIVALENCE_CLI.exists():
        return "publish-skipped (no candidates/cli)"
    try:
        r = subprocess.run(
            [sys.executable, str(EQUIVALENCE_CLI), "publish", "--repo", str(REPO),
             "--role", machine, "--file", str(CANDIDATES), "--ref", CAND_REF],
            capture_output=True, text=True, timeout=PUBLISH_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return f"publish-timeout ({PUBLISH_TIMEOUT_S}s)"
    except Exception as e:  # noqa: BLE001 — best-effort fleet slice; never fail local extraction
        return f"publish-error: {str(e)[:80]}"
    return "published" if r.returncode == 0 else f"publish-rc{r.returncode}"


def run_cli(args: argparse.Namespace, notify_fn: Callable[[dict], None] = _default_notify) -> int:
    """Read Hermes memory, decide, persist candidates, fire one notify_fn per alert. Returns 0 on
    any successful run (no Hermes OR candidates-found) — the alert is the signal, not the exit code
    (Rule 4). notify_fn is injectable so tests assert call counts without shelling out."""
    machine = machine_label()
    patterns: list[dict] = []
    for s in SOURCES:
        p = HERMES_DIR / s
        if p.exists():
            try:
                patterns.extend(extract_patterns(p.read_text(encoding="utf-8", errors="replace"),
                                                 source_file=s))
            except OSError:
                continue
    if not patterns:
        return 0                                   # no Hermes on this box (Windows/dev-secondary) → no-op

    canonical = canonical_text_index()             # bridge-block-stripped canonical CONTENT
    skills = skill_text_index()
    deny = load_deny_patterns(DENY_LIST)
    last = _read_json(_last_seen_path(machine))
    r = evaluate(patterns, canonical, skills, deny, last, now_iso=_now())

    append_candidates_md(CANDIDATES, r["candidates"], dropped=r["dropped_sensitive"])  # idempotent
    for a in r["alerts"]:
        notify_fn(a)
    _write_json(_last_seen_path(machine), r["new_state"])  # gitignored runtime state

    if getattr(args, "publish", False):
        print(publish_candidates(machine), file=sys.stderr)

    print(f"hermes-pattern-candidates: {len(r['candidates'])} candidate(s), "
          f"{r['dropped_sensitive']} dropped, new={r['new']} (machine={machine})", file=sys.stderr)
    return 0                                        # ALWAYS 0 on the candidates path (Rule 4)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Emit Hermes-authored learnings as review-gated skill/memory candidates."
    )
    p.add_argument("--publish", action="store_true",
                   help="Publish the candidate file to the hermes-pattern-candidate-state git ref "
                        "(bounded 90s, fail-soft; OFF by default).")
    return p


def main(argv: list[str] | None = None) -> int:
    return run_cli(_build_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
