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


# --------------------------------------------------------------------------- #
# #3137: resolve a Skill-tool id to the canonical short_name + a source flag.
# --------------------------------------------------------------------------- #

# Namespaces that exist as external plugins under ~/.claude/plugins/cache/ and
# are NOT mirrored in the workspace-hub .claude/skills tree (verified #3137:
# codex 815, superpowers 97, gsd 32, data 1 invocations). A namespaced id that
# fails to resolve is flagged `plugin` (still a real skill, just off-repo) vs a
# bare/workspace-hub-namespaced miss which is flagged `unresolved` (likely a
# slash-command, not a SKILL.md). Both preserve the raw id — never dropped.
KNOWN_PLUGIN_NAMESPACES = frozenset({"codex", "superpowers", "gsd", "data"})
# The namespace under which the repo exposes its OWN skills/commands.
WORKSPACE_NAMESPACE = "workspace-hub"


def _build_shortname_index(skills_root, exclusions=DEFAULT_EXCLUSIONS):
    """Map every resolvable lookup key -> canonical short_name.

    Two keys point at each skill so a Skill-tool id resolves whether it carries
    the dir basename or the frontmatter name: the lowercased dir basename AND
    the canonical short_name itself (frontmatter `name` lowercased). Uses the
    SAME discover_skills + derive_short_name the scanner keys rows by, so a
    resolved short_name JOINS the scanner/report tier rows.
    """
    root = Path(skills_root)
    index = {}
    for skill_rel in discover_skills(root, exclusions=exclusions):
        skill_md = root / skill_rel / "SKILL.md"
        short = derive_short_name(skill_md)
        basename = Path(skill_rel).name.lower()
        # short_name wins as the canonical join key; basename is a secondary
        # alias. Insert basename first so short_name (set last) is authoritative
        # if they ever collide on the same string.
        index.setdefault(basename, short)
        index[short] = short
    return index


def normalize_skill_id(raw_id, skills_root, exclusions=DEFAULT_EXCLUSIONS):
    """Resolve a Skill-tool id to {skill_name, skill_source, skill_id}.

    `raw_id` is the value of `.tool_input.skill` (e.g. 'superpowers:test-driven-
    development', 'codex:rescue', 'corporate-tax-form-fill', 'workspace-hub:repo-sync').

    Resolution (pure, no side effects):
      1. split `<namespace>:<name>` on the first ':' (bare id -> empty namespace)
      2. look the lowercased `<name>` up against the workspace-hub skill universe
         (dir basename OR frontmatter-name, _archive/_core/_internal excluded)
      3. classify:
         - resolved                  -> skill_source='workspace-hub', skill_name=<short_name>
         - unresolved + plugin ns    -> skill_source='plugin',        skill_name=''
         - unresolved + bare/wshub ns -> skill_source='unresolved',    skill_name=''
      `skill_id` always preserves the raw id verbatim (never dropped, the
      canonical short_name is NEVER fabricated for an id absent from the tree).
    """
    raw = raw_id or ""
    if ":" in raw:
        namespace, name = raw.split(":", 1)
    else:
        namespace, name = "", raw
    namespace = namespace.strip().lower()
    name_l = name.strip().lower()

    index = _build_shortname_index(skills_root, exclusions=exclusions)
    short = index.get(name_l, "")

    if short:
        return {"skill_name": short, "skill_source": "workspace-hub", "skill_id": raw}
    if namespace and namespace != WORKSPACE_NAMESPACE:
        # A namespaced id that didn't resolve: an external plugin skill (logged + flagged).
        return {"skill_name": "", "skill_source": "plugin", "skill_id": raw}
    # Bare or workspace-hub-namespaced miss (likely a slash-command, not a SKILL.md).
    return {"skill_name": "", "skill_source": "unresolved", "skill_id": raw}
