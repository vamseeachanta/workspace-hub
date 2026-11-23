#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""classify_skill_scope.py — Gemini-specific vs shared skill-scope classifier (#3256, epic #3248).

Closes gap #8 ("no distinction between Gemini-specific skill needs and shared cross-provider
patterns"). Given candidate skill *family* names, it tags each as:
  * ``shared``          — belongs in the canonical cross-provider surface ``.claude/skills/``
                          (already a canonical family, OR a brand-new cross-provider need).
  * ``gemini-specific`` — a legitimately Gemini-only family (matches the ``expected_skill_divergence``
                          allowlist), belongs under the Gemini surface ``.agents/skills/``.
  * ``gemini-drift``    — present on the Gemini surface, NOT allowlisted, NOT canonical (would be
                          flagged by the #3250 drift detector; surfaced here, not auto-routed).

The classifier REUSES ``audit_skill_currency``'s ``_families`` / ``_load_allow`` / (module-level)
``_allowed`` rather than reimplementing the family-diff/allowlist machinery — a single source of
truth for "is this family a legitimate Gemini-specific family".

NOTE on the Gemini surface (correcting the issue text): the issue says Gemini lives under
``.gemini/``, but the live Gemini *skill* surface graded by the audit is ``.agents/skills`` —
``.gemini/`` holds GSD/agent config, not the skill family tree. The classifier binds to the same
``.agents/skills`` surface the audit already trusts.

Round-2 major #2 — SINGLE WRITER: the classifier's ONLY durable output is
``.claude/state/skill-scope-classification.json``. It does NOT edit
``.claude/state/candidates/skill-candidates.md`` — that file is cron-regenerated, append-structured,
"do not edit manually", and already has two append-owners (session-analysis.sh,
comprehensive_learning_pipeline.py); a second in-place writer would race them and be clobbered on
the morning regeneration. If a future enhancement wants the scope tag rendered into the candidate
md, it must invert ownership — have those generators READ this JSON at generation time.

The CLI ALWAYS exits 0 (Hard Rule 4 — signal via JSON, never the exit code). It performs no
state-ref push (Hard Rule 5) and writes no `status:*` label (Hard Rule 1).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"
DEFAULT_STATE = STATE / "skill-scope-classification.json"
CANDIDATES_MD = STATE / "candidates" / "skill-candidates.md"

# Import the audit module (single source of truth for family enumeration + allowlist matching).
# Same-dir module; ensure the curation dir is importable (mirrors detect_skill_drift.py).
_CURATION_DIR = str(Path(__file__).resolve().parent)
if _CURATION_DIR not in sys.path:
    sys.path.insert(0, _CURATION_DIR)
import audit_skill_currency  # noqa: E402  (path set up above)

# Re-export the reused helpers at module level so tests/CLI bind to a single, monkeypatchable name.
_families = audit_skill_currency._families
_load_allow = audit_skill_currency._load_allow
_allowed = audit_skill_currency._allowed
CANON = audit_skill_currency.CANONICAL_PREFIX     # ".claude/skills"
GEM = audit_skill_currency.GEMINI_PREFIX          # ".agents/skills"
SCHEMA_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# PURE CORE — no IO, no clock, no subprocess
# --------------------------------------------------------------------------- #
def classify_scope(family: str, *, canonical: set, gemini: set, allow: list) -> str:
    """Tag a candidate skill family. PURE.

    Precedence: canonical membership wins (already a cross-provider family ⇒ ``shared``); then the
    Gemini allowlist (``gemini-specific``); then Gemini-surface-but-unlisted (``gemini-drift``);
    otherwise a new cross-provider need defaults to ``shared`` (lands in canonical ``.claude/skills``).
    """
    if family in canonical:
        return "shared"
    if _allowed(family, allow):
        return "gemini-specific"
    if family in gemini:
        return "gemini-drift"
    return "shared"


# --------------------------------------------------------------------------- #
# THIN CLI — IO lives here; ALWAYS exits 0; JSON-only output
# --------------------------------------------------------------------------- #
def run_cli(args: argparse.Namespace) -> int:
    """Enumerate canonical/gemini families + allowlist, classify each candidate, write the JSON.

    ALWAYS returns 0. Writes ONLY the classification JSON — never touches skill-candidates.md.
    """
    canonical = _families(CANON) or set()      # None on git failure ⇒ degrade to empty set
    gemini = _families(GEM) or set()
    allow = _load_allow()

    families = list(getattr(args, "families", []) or [])
    classifications = [
        {"family": fam, "scope": classify_scope(fam, canonical=canonical, gemini=gemini, allow=allow)}
        for fam in families
    ]
    doc = {
        "schema_version": SCHEMA_VERSION,
        "audited_at": _now(),
        "canonical_prefix": CANON,
        "gemini_prefix": GEM,
        "canonical_count": len(canonical),
        "gemini_count": len(gemini),
        "classifications": classifications,
    }

    if getattr(args, "stdout", False):
        print(json.dumps(doc, indent=2))
        return 0

    state_path = Path(args.state)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(doc, indent=2) + "\n")
    counts: dict[str, int] = {}
    for c in classifications:
        counts[c["scope"]] = counts.get(c["scope"], 0) + 1
    print(f"classify_skill_scope: {len(classifications)} families classified {counts} "
          f"→ {state_path.name}", file=sys.stderr)
    return 0


def _read_candidate_families(path: Path) -> list[str]:
    """Best-effort READ-ONLY parse of skill-candidates.md family names (markdown bullets).

    Round-2 major #2: this opens the file for READING ONLY — the classifier never writes it.
    Returns [] on any failure. Heuristic: pull the first backticked or bolded token from each
    bullet line. Callers may pass families explicitly instead.
    """
    import re
    try:
        text = path.read_text()
    except OSError:
        return []
    fams: list[str] = []
    for line in text.splitlines():
        m = re.match(r"\s*[-*]\s+", line)
        if not m:
            continue
        tok = re.search(r"`([^`]+)`|\*\*([^*]+)\*\*", line)
        if tok:
            name = (tok.group(1) or tok.group(2)).strip().split("/")[0].split()[0]
            if name:
                fams.append(name)
    return fams


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Classify candidate skill families as gemini-specific / shared / gemini-drift "
                    "(#3256). JSON-only output; never edits skill-candidates.md.")
    p.add_argument("families", nargs="*", help="candidate family names to classify")
    p.add_argument("--from-candidates", action="store_true",
                   help="READ-ONLY parse family names from skill-candidates.md (never written)")
    p.add_argument("--state", default=str(DEFAULT_STATE),
                   help="classification JSON output path")
    p.add_argument("--stdout", action="store_true",
                   help="print the classification JSON to stdout and do NOT write the state file")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    families = list(args.families)
    if args.from_candidates:
        families += _read_candidate_families(CANDIDATES_MD)
    args.families = families
    return run_cli(args)


if __name__ == "__main__":
    sys.exit(main())
