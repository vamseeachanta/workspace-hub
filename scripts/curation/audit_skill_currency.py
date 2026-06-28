#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""audit_skill_currency.py — cross-provider skill-currency audit (#3249, epic #3248).

Emits the FACTS for the machine-equality `skill_currency` line item: are all providers' skill
surfaces up to date vs canonical, and is the skills index intact? The matrix
(build-equality-matrix.py::skill_currency_verdict) maps these facts → verdict.

Design decisions (locked by the #3249 adversarial review):
  * Compare the COMMITTED tree via `git ls-tree -r HEAD`, not the working tree — symlink-transparent
    (`.codex/skills` is a symlink; Windows materializes it as a text file), deterministic, and
    immune to skill-development WIP blinding the very alert you want during skill development.
  * Compare at FAMILY granularity (top-level dir under each skills root) — skills nest up to 8 deep,
    so leaf-path comparison is hopeless; families are the meaningful unit.
  * Grade DRIFT only on UNEXPECTED family differences. Legitimate provider-specific families
    (Gemini's `source-command-*`, `workspace_hub_learned`, …) are allowlisted in harness-config
    `expected_skill_divergence` — the same posture as the provider_harness expected_divergence model.
  * Hermes external dir == canonical `.claude/skills` (tautological) and Codex is an intentional
    curated subset → graded present/absent only, NEVER count-compared.
  * Index integrity = dangling entries (index paths no longer in the tree), NOT an mtime check
    (mtime is non-deterministic on fresh checkouts).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"
HARNESS_CONFIG = REPO / "scripts" / "readiness" / "harness-config.yaml"
SKILLS_INDEX = REPO / ".claude" / "skills-index.yaml"

CANONICAL_PREFIX = ".claude/skills"          # Claude canonical (Hermes external dir aliases this)
GEMINI_PREFIX = ".agents/skills"             # Gemini skill surface
# Fallback allowlist if harness-config has none — the families that legitimately differ today.
DEFAULT_GEMINI_ALLOW = ["source-command-", "workspace_hub_learned", "digitalmodel", "memory"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def machine_label() -> str:
    if os.environ.get("EQ_MACHINE"):
        return os.environ["EQ_MACHINE"]
    host = (os.uname().nodename if hasattr(os, "uname") else os.environ.get("COMPUTERNAME", "")).lower()
    table = {"ace-linux-1": "dev-primary", "ace-linux-2": "dev-secondary",
             "ace-win-1": "ace-win-1", "licensed-win-1": "ace-win-1", "acma-ansys05": "ace-win-1",
             "ace-win-2": "ace-win-2", "licensed-win-2": "ace-win-2", "acma-ws014": "ace-win-2"}
    for key, label in table.items():
        if host.startswith(key):
            return label
    return ("macbook-portable" if "macbook" in host else (host or "unknown"))


def _git_tree_skillmd(prefix: str) -> list[str] | None:
    """Tracked SKILL.md paths under `prefix` in the committed tree (HEAD). None on git failure."""
    try:
        r = subprocess.run(["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", "HEAD", prefix],
                           capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, OSError):
        return None                                      # hung/locked git ⇒ no evidence (fail-closed)
    if r.returncode != 0:
        return None
    return [ln for ln in r.stdout.splitlines() if ln.endswith("/SKILL.md")]


def _families(prefix: str) -> set[str] | None:
    """Top-level family dir names (the component right after `prefix`) that contain a SKILL.md."""
    paths = _git_tree_skillmd(prefix)
    if paths is None:
        return None
    plen = len(prefix.rstrip("/").split("/"))
    fams = set()
    for p in paths:
        parts = p.split("/")
        if len(parts) > plen and parts[plen] != "SKILL.md":   # skip a SKILL.md directly under root
            fams.add(parts[plen])
    return fams


def _allowed(f: str, allow: list[str]) -> bool:
    """True if family ``f`` matches the gemini allowlist.

    An allowlist entry ending in ``-`` is an explicit PREFIX (e.g. ``source-command-``); any
    other entry must match EXACTLY (e.g. ``memory``), so a bare ``memory`` can never silently
    allowlist an unrelated ``memory-bank`` family and hide real drift (review axis #4).

    Module-level (was nested in ``audit()``) so it is the SINGLE source of truth reused by
    ``classify_skill_scope.py`` (#3256) — behavior-identical to the prior nested def.
    """
    return any(f.startswith(p) if p.endswith("-") else f == p for p in allow)


def _load_allow() -> list[str]:
    try:
        cfg = yaml.safe_load(HARNESS_CONFIG.read_text()) if HARNESS_CONFIG.exists() else {}
        allow = ((cfg or {}).get("expected_skill_divergence") or {}).get("gemini")
        if isinstance(allow, list) and allow:
            return [str(a) for a in allow]
    except (OSError, yaml.YAMLError):
        pass
    return list(DEFAULT_GEMINI_ALLOW)


def _index_dangling() -> int | None:
    """Count of skills-index.yaml `path:` entries that no longer exist in the committed tree.
    None if the index can't be read or the tree can't be listed (→ MISSING-EVIDENCE upstream)."""
    if not SKILLS_INDEX.exists():
        return None
    try:
        data = yaml.safe_load(SKILLS_INDEX.read_text()) or {}
    except yaml.YAMLError:
        return None
    index_paths = {sk.get("path") for cat in data.get("categories", []) or []
                   for sk in (cat.get("skills") or []) if sk.get("path")}
    tree = _git_tree_skillmd(CANONICAL_PREFIX)
    if tree is None:
        return None
    return len(index_paths - set(tree))


def audit(machine: str) -> dict:
    canonical = _families(CANONICAL_PREFIX)
    gemini = _families(GEMINI_PREFIX)
    allow = _load_allow()

    # Presence from the COMMITTED tree (non-empty family set), NOT a working-tree stat — staying on
    # the same basis as the comparison so a working-tree delete during skill-dev can't silently
    # disable drift detection (the module's stated WIP-immunity).
    gemini_present = gemini is not None and len(gemini) > 0
    # init BEFORE the guard so the gemini-absent path can't NameError on these (#3250 review)
    gemini_unexpected = gemini_expected = 0
    unexpected_families: list[str] = []
    if canonical is not None and gemini is not None and gemini_present:
        diff = canonical ^ gemini
        # Allowlist match via the module-level _allowed (single source of truth, #3256): an entry
        # ending in '-' is an explicit PREFIX (e.g. 'source-command-'); any other entry must match
        # EXACTLY (e.g. 'memory'), so a bare 'memory' can never silently allowlist an unrelated
        # 'memory-bank' family and hide real drift (review axis #4).
        expected = {f for f in diff if _allowed(f, allow)}
        unexpected = diff - expected
        gemini_expected = len(expected)
        gemini_unexpected = len(unexpected)
        unexpected_families = sorted(unexpected)            # named for the #3250 drift alert

    dangling = _index_dangling()
    return {
        "machine": machine,
        "audited_at": _now(),
        "canonical_count": (len(canonical) if canonical is not None else None),
        "gemini_present": gemini_present,
        "gemini_unexpected": gemini_unexpected,
        "gemini_unexpected_families": unexpected_families,   # names for the #3250 drift detector
        "gemini_expected": gemini_expected,
        "codex_present": (Path.home() / ".codex" / "skills").exists(),
        "hermes_present": (REPO / CANONICAL_PREFIX).exists(),
        "index_dangling": (dangling if dangling is not None else None),
        "index_stale": (dangling is not None and dangling > 0),
        "schema_version": 2,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cross-provider skill-currency audit")
    ap.add_argument("--machine", default=None)
    ap.add_argument("--stdout", action="store_true", help="print state JSON, do not write")
    a = ap.parse_args(argv)
    machine = a.machine or machine_label()
    state = audit(machine)
    if a.stdout:
        print(json.dumps(state, indent=2))
        return 0
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / f"skill-currency-{machine}.json").write_text(json.dumps(state, indent=2) + "\n")
    print(f"audited {machine}: canonical={state['canonical_count']} families, "
          f"gemini unexpected={state['gemini_unexpected']} expected={state['gemini_expected']}, "
          f"index_dangling={state['index_dangling']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
