#!/usr/bin/env python3
"""curate_readback_slice.py — the ONE shared cross-provider memory read-back selector (#2841 Phase A).

WHAT: emits a budget-capped, machine-invariant slice of consolidated memory for
  the OTHER orchestrators (Codex, Hermes) to read back — closing the dream's
  contribute-only asymmetry.

F1 (machine-invariance): sources ONLY git-tracked `.claude/memory/` (KNOWLEDGE.md +
  claude-auto-memory.md, the bridge-maintained snapshot of the auto-memory index).
  NEVER reads `$HOME/.claude/projects/.../memory/` (per-machine, untracked) — that
  would make the committed slice differ per machine and cause cross-machine churn.

F4 (filter polarity): Claude-only entries are dropped by FILENAME SLUG (structured,
  precise) against an explicit set — NOT by title substring. Default is INCLUDE, so an
  unknown/new entry (or a shared entry whose text merely mentions "browser") is kept,
  never silently dropped. (Leaking a Claude-only note to Codex is mild; dropping a
  shared learning is the damaging direction — so we err toward keeping.)

F5 (capping): truncates at ENTRY boundaries. An entry that alone exceeds the cap is
  DROPPED with an omitted-marker — never a mid-entry cut.

Deterministic: source order preserved, NO generation timestamp in the body, so the
  same tracked input yields byte-identical output (no churn commits).

USAGE:
  python3 curate_readback_slice.py --target codex  [--source-dir .claude/memory] [--cap 7000]
  python3 curate_readback_slice.py --target hermes [--cap 2000]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Claude-runtime-specific entry slugs (substring match on the linked filename slug —
# structured, not title text). Default for everything else is INCLUDE (F4).
CLAUDE_ONLY_SLUGS = (
    "claude_in_chrome", "gmail", "claude_desktop", "gif_creator",
    "chatgpt_share", "output_style", "mcp_scope",
)

DEFAULT_CAPS = {"codex": 7000, "hermes": 2000}
_HEADER = "<!-- MANAGED by curate_readback_slice.py — do not hand-edit; regenerate via bridge-hermes-claude.sh -->\n\n"
_MARKER_RESERVE = 64  # bytes reserved so the omitted-marker always fits under the cap

_INDEX_RE = re.compile(r"^- \[(?P<title>.+?)\]\((?P<slug>[^)]+?)\.md\)\s*—\s*(?P<desc>.*)$")


def _is_claude_only(slug: str) -> bool:
    return any(tok in slug for tok in CLAUDE_ONLY_SLUGS)


def _collect_entries(source_dir: Path) -> list[str]:
    """Return ordered candidate lines from the git-tracked snapshot only."""
    entries: list[str] = []

    # 1) auto-memory index lines: "- [Title](slug.md) — desc" (titles + descriptions, NOT bodies)
    auto = source_dir / "claude-auto-memory.md"
    if auto.exists():
        for line in auto.read_text(encoding="utf-8", errors="replace").splitlines():
            m = _INDEX_RE.match(line.strip())
            if not m:
                continue
            if _is_claude_only(m.group("slug")):
                continue  # F4: precise slug match, default-include
            entries.append(line.strip())

    # 2) KNOWLEDGE.md bullets (institutional, shared); skip quote/`>`/header lines
    know = source_dir / "KNOWLEDGE.md"
    if know.exists():
        for line in know.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if s.startswith("- "):
                entries.append(s)
    return entries


def curate(source_dir, target: str, cap: int) -> str:
    """Build the capped, deterministic slice. Reads ONLY source_dir (F1)."""
    source_dir = Path(source_dir)
    entries = _collect_entries(source_dir)

    budget = cap - len(_HEADER) - _MARKER_RESERVE
    out: list[str] = []
    used = 0
    omitted = 0
    for e in entries:
        line = e.rstrip("\n") + "\n"
        if len(line) > budget:          # F5: oversize — can never fit, drop with marker
            omitted += 1
            continue
        if used + len(line) <= budget:
            out.append(line)
            used += len(line)
        else:
            omitted += 1                # cap reached
    body = _HEADER + "".join(out)
    if omitted:
        body += f"_[{omitted} entr{'y' if omitted == 1 else 'ies'} omitted: oversize/over-cap]_\n"
    # F3: hard cap guarantee — for a degenerate tiny cap (< header+reserve) the fixed
    # overhead alone can exceed cap; clamp so len(body) <= cap always holds.
    return body if len(body) <= cap else body[:cap]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", choices=list(DEFAULT_CAPS), required=True)
    ap.add_argument("--source-dir", default=".claude/memory")
    ap.add_argument("--cap", type=int, default=0, help="char cap (0 = per-target default)")
    args = ap.parse_args()
    cap = args.cap or DEFAULT_CAPS[args.target]
    sys.stdout.write(curate(args.source_dir, args.target, cap))
    return 0


if __name__ == "__main__":
    sys.exit(main())
