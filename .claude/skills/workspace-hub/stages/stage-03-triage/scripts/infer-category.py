#!/usr/bin/env -S uv run --no-project python
"""Infer category + subcategory for a WRK item from its title and body text.

Returns JSON: {"category": "engineering", "subcategory": "pipeline"}

Subcategories are adaptive free-text (kebab-case). The script prefers existing
values found in the queue over minting new ones.

Usage:
    python scripts/work-queue/infer-category.py "title text" ["body text"]
    python scripts/work-queue/infer-category.py --scan-existing   # list known subcategories
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

QUEUE_ROOT = Path(__file__).resolve().parent.parent.parent / ".claude" / "work-queue"
STATUS_DIRS = ["pending", "working", "blocked"]

# ---------------------------------------------------------------------------
# Category rules — ordered, first match wins
# Title + body text matched case-insensitively
# ---------------------------------------------------------------------------

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    # personal: physical/home items — checked first, very specific
    ("personal", [
        "heriberto", "handyman", "fence", "faucet", "sink", "caulk",
        "photo upload", "photos from", "upload photos", "email cleanup",
        "clean up email", "gmail", "garage", "powder room", "iphone",
    ]),
    # harness: workflow infrastructure — checked before engineering to avoid
    # skill/queue items being caught by engineering domain keywords
    ("harness", [
        "work-queue", "work queue", "gatepass", "gate pass",
        "lifecycle", "hookify", "session-start", "session start", "session end",
        "session replay", "session signal", "session scanner",
        "comprehensive-learning", "comprehensive learning",
        "pre-commit", "stop hook", "signal emitter", "html review", "workflow-html",
        "generate-index", "infer-category", "assign-categories",
        "category grouping", "subcategory",
        "skill eval", "skill-eval", "skill upkeep", "skill curation",
        "skill creator", "skill-creator", "capability assessment", "knowledge map",
        "readme.md violation", "oversized skill",
        "(skills)", "(work-queue)", "(workflow)", "(session)", "(memory)",
        "(hooks)", "(skill-creator)",
    ]),
    # engineering: specific domain keywords only — no repo names (too broad)
    ("engineering", [
        "pipeline", "free span", "viv", "dnv rp f105", "api rp 1111",
        "plate capacity", "fea", "ansys", "apdl", "wbjn",
        "mooring", "hydrodynamic", "diffraction", "qtf", "planing hull",
        "orcaflex", "offshore", "hull form", "seakeeping", "rao",
        "openfoam", "supply boat", "floater", "vessel motion",
        "rop model", "wellhead", "drilling riser", "casing design",
        "cathodic protection", "cp module", "anode", "iso 15589", "api rp 1632",
        "wind resource", "aep", "pywake", "pywasp", "windkit",
        "reservoir simulation", "geospatial", "corrosion", "fatigue analysis",
        "subsea", "riser analysis", "anchor", "tendon",
        "structural analysis", "buckling", "collapse", "burst",
    ]),
    # data: data sources, standards, document intelligence
    ("data", [
        "document index", "document intelligence", "index.jsonl", "summaries",
        "standards transfer", "ledger", "api rp", "dnv rp", "abs standard",
        "semantic scholar", "mcp server", "online resources", "open data",
        "production forecast", "arps", "decline curve", "eia", "shale",
        "bsee", "maib", "ntsb", "polymathic", "misle", "uscg",
        "dataset", "bulk dataset",
    ]),
    # business: finance, GTM, website
    ("business", [
        "net lease", "walgreens", "pharmacy", "retail nn",
        "stocks", "52wk", "52-week", "net_lease", "assethold",
        "gtm", "go-to-market", "oil man", "persona",
        "aceengineer-website", "aceengineer-admin", "portfolio", "brochure",
        "aceengineer-strategy",
    ]),
    # platform: machines, AI tools, CI/cron, dev environment
    ("platform", [
        "plugin", "claude code", "codex install", "gemini install",
        "workstation", "ace-linux", "acma-ansys", "acma-ws", "kvm",
        "vnc", "tailscale", "remote desktop", "cron", "nightly", "ci ",
        "ai-agent-readiness", "ai tools", "node.js", "npm", "upgrade gh",
        "setup-cron", "sync coordinator", "mount path", "fstab", "sshfs",
        "hardware consolidation", "blender", "gmsh", "qgis",
    ]),
    # maintenance: cleanup, refactor, test debt
    ("maintenance", [
        "cleanup", "clean up", "delete stale", "remove stale", "archive stale",
        "refactor", "god object", "src layout", "pyproject",
        "setup.py", "gitignore", "egg-info", "0-byte", "garbage file",
        "failing test", "fixture", "collection error", "test coverage",
        "polar typeerror", "yml fixture",
    ]),
]

# Subcategory rules — matched within each category
SUBCATEGORY_RULES: dict[str, list[tuple[str, list[str]]]] = {
    "harness": [
        ("skills",      ["skill", "skill-creator", "skill eval", "eval framework",
                         "capability assessment", "knowledge map", "readme.md violation",
                         "oversized skill"]),
        ("work-queue",  ["work-queue", "work queue", "index.md", "generate-index",
                         "infer-category", "assign-categories", "category grouping",
                         "next-id", "queue-status", "queue-report", "close-item",
                         "archive-item", "claim-item", "mission", "subcategory"]),
        ("workflow",    ["gatepass", "gate pass", "lifecycle", "html review",
                         "workflow-html", "stage evidence", "verify-gate", "plan gate",
                         "cross-review", "future work synthesis"]),
        ("hooks",       ["hookify", "pre-commit", "stop hook", "signal emitter",
                         "post-commit", "hook rule", "hook script"]),
        ("session",     ["session-start", "session start", "session end",
                         "comprehensive-learning", "comprehensive learning",
                         "active-wrk", "session signal", "readiness"]),
    ],
    "engineering": [
        ("pipeline",        ["pipeline", "free span", "viv", "dnv rp f105",
                             "api rp 1111", "installation", "s-lay", "propagating buckle",
                             "burst", "collapse"]),
        ("structural",      ["structural", "plate capacity", "fea", "ansys", "apdl",
                             "wbjn", "design point", "buckling"]),
        ("marine",          ["mooring", "hydrodynamic", "diffraction", "qtf",
                             "planing hull", "orcaflex", "marine", "offshore",
                             "vessel", "hull", "seakeeping", "wave"]),
        ("drilling",        ["drilling", "rop model", "wellhead", "riser", "casing",
                             "drilling riser", "bit "]),
        ("cathodic-protection", ["cathodic protection", "cp module", "anode",
                                 "iso 15589", "api rp 1632", "dnv rp b401",
                                 "dnv rp f103"]),
        ("wind",            ["wind resource", "aep", "pywake", "pywasp", "windkit",
                             "wind energy", "wind farm", "wake"]),
        ("reservoir",       ["reservoir", "decline curve", "arps", "shale",
                             "production forecast"]),
        ("manufacturing",   ["ogmanufacturing", "manufacturing"]),
    ],
    "data": [
        ("document-intelligence", ["document index", "index.jsonl", "summaries",
                                   "phase-e2", "remap", "document intelligence"]),
        ("standards",       ["standards transfer", "ledger", "api rp", "dnv ",
                             "abs ", "iso ", "asme", "aisc", "nace", "porting"]),
        ("online-resources", ["semantic scholar", "mcp server", "online resources",
                              "open data", "polymathic", "huggingface"]),
        ("production",      ["eia", "bsee", "maib", "ntsb", "production data",
                             "shale decline", "dpr "]),
    ],
    "platform": [
        ("ai-tools",    ["plugin", "claude code", "codex install", "gemini install",
                         "ai-agent-readiness", "ai tools", "upgrade gh", "npm"]),
        ("workstations", ["workstation", "ace-linux", "acma-ansys", "acma-ws",
                          "kvm", "vnc", "tailscale", "remote desktop", "node.js"]),
        ("ci-cron",     ["cron", "nightly", "ci ", "setup-cron", "sync coordinator",
                         "comprehensive-learning cron"]),
    ],
    "business": [
        ("cre-finance", ["net lease", "cre", "walgreens", "pharmacy", "retail nn",
                         "assethold", "stocks", "52wk", "52-week", "net_lease"]),
        ("gtm",         ["gtm", "go-to-market", "oil man", "persona", "brochure"]),
        ("website",     ["aceengineer-website", "aceengineer-admin", "portfolio",
                         "aceengineer-strategy", "website"]),
    ],
    "maintenance": [
        ("cleanup",   ["cleanup", "clean up", "delete", "remove stale", "0-byte",
                       "garbage file", "worktree", "stale", "archive stale"]),
        ("refactor",  ["refactor", "god object", "split ", "src layout", "pyproject",
                       "setup.py", "gitignore", "egg-info"]),
        ("testing",   ["failing test", "fixture", "collection error", "test coverage",
                       "polar typeerror", "yml fixture"]),
    ],
    "personal": [
        ("home",  ["heriberto", "handyman", "fence", "faucet", "sink", "caulk",
                   "garage", "powder room"]),
        ("admin", ["photo upload", "email cleanup", "gmail"]),
    ],
}


def _match(text: str, keywords: list[str]) -> bool:
    """Case-insensitive keyword match. Short keywords (≤4 chars) use word boundaries
    to avoid false positives (e.g. 'fea' matching 'feat', 'abs' matching 'absolute')."""
    import re
    t = text.lower()
    for kw in keywords:
        k = kw.lower()
        if len(k) <= 4 and k.isalpha():
            # word-boundary match for short alphabetic keywords
            if re.search(rf"\b{re.escape(k)}\b", t):
                return True
        else:
            if k in t:
                return True
    return False


def infer(title: str, body: str = "") -> dict[str, str]:
    # Title-first: strong signal. Body: fallback only.
    category = "uncategorised"
    for cat, keywords in CATEGORY_RULES:
        if _match(title, keywords):
            category = cat
            break
    if category == "uncategorised":
        for cat, keywords in CATEGORY_RULES:
            if _match(body, keywords):
                category = cat
                break

    # Subcategory: title first, then body
    subcategory = "uncategorised"
    if category in SUBCATEGORY_RULES:
        for sub, keywords in SUBCATEGORY_RULES[category]:
            if _match(title, keywords):
                subcategory = sub
                break
        if subcategory == "uncategorised":
            for sub, keywords in SUBCATEGORY_RULES[category]:
                if _match(body, keywords):
                    subcategory = sub
                    break

    return {"category": category, "subcategory": subcategory}


def scan_existing() -> dict[str, set[str]]:
    """Return existing category→subcategory values found in the queue."""
    result: dict[str, set[str]] = {}
    for d in STATUS_DIRS:
        for f in (QUEUE_ROOT / d).glob("WRK-*.md"):
            text = f.read_text(errors="replace")
            cat_m = re.search(r"^category:\s*(.+)$", text, re.MULTILINE)
            sub_m = re.search(r"^subcategory:\s*(.+)$", text, re.MULTILINE)
            if cat_m:
                cat = cat_m.group(1).strip()
                sub = sub_m.group(1).strip() if sub_m else "uncategorised"
                result.setdefault(cat, set()).add(sub)
    return result


if __name__ == "__main__":
    if "--scan-existing" in sys.argv:
        existing = scan_existing()
        for cat, subs in sorted(existing.items()):
            print(f"{cat}: {', '.join(sorted(subs))}")
        sys.exit(0)

    args = sys.argv[1:]
    if not args:
        print("Usage: infer-category.py <title> [body]", file=sys.stderr)
        sys.exit(1)

    title = args[0]
    body = args[1] if len(args) > 1 else ""
    result = infer(title, body)
    print(json.dumps(result))
