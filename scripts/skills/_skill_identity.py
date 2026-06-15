"""_skill_identity.py — single source of truth for the skill universe + the
canonical short_name key (#3139).

Both skill-invocation-scanner.py and skill-usage-report.py import this so they
iterate the IDENTICAL skill set and derive the short_name join key from ONE
implementation (closing the #3112 BUG-2 join's latent divergence).

Pure stdlib (no yaml) so the scanner stays dependency-free; the report keeps its
own yaml parse for OTHER frontmatter fields (related_skills/see_also) but routes
the universe walk + short_name KEY through here.

Underscore-named lib with no PEP-723 header (never executed directly) — mirrors
the established scripts/skills/audit_skill_lib.py / skill_tier_lib.py precedent.
"""
from __future__ import annotations

from pathlib import Path

# The canonical exclusion set. NOTE `_archived` (trailing "d") is included —
# the report previously excluded only `_archive`, leaking 6 archived email
# skills and producing the gmail-data-extraction short_name collision (#3139).
DEFAULT_EXCLUSIONS = frozenset({"_archive", "_archived", "_core", "_internal"})


def discover_skills(skills_root, exclusions=DEFAULT_EXCLUSIONS):
    """Return sorted rel-path skill ids under skills_root, minus excluded dirs.

    A skill is a directory containing SKILL.md; its id is the POSIX rel-path of
    that directory relative to skills_root (e.g. 'email/gmail-triage').
    """
    root = Path(skills_root)
    out = []
    for skill_md in root.rglob("SKILL.md"):
        if any(part in exclusions for part in skill_md.parts):
            continue
        out.append(skill_md.parent.relative_to(root).as_posix())
    return sorted(out)


def _read_frontmatter_name(skill_md_path: Path):
    """Minimal, dependency-free single-line `name:` frontmatter read.

    Matches the value skill-usage-report.py derives via yaml for the common
    single-line case (verified 0 divergences over the 833 report-visible skills,
    #3139). Tolerant of surrounding quotes. Returns None if absent/unreadable.
    """
    try:
        text = skill_md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    block = text[3:end] if end != -1 else ""
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("name:"):
            return s[len("name:"):].strip().strip('"').strip("'")
    return None


def derive_short_name(skill_md_path) -> str:
    """Canonical short_name = frontmatter `name` lowercased, else dir basename.

    Mirrors skill-usage-report.py:150-153 so scanner output keys join report
    tier keys. This is THE single derivation both scripts must use.
    """
    p = Path(skill_md_path)
    basename = p.parent.name
    name = _read_frontmatter_name(p)
    return ((name or basename).strip() or basename).lower()
