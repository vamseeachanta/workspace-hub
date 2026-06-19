#!/usr/bin/env python3
"""check-skill-index-coherence.py — skill-index drift gate (#3208).

Binds the curated skill graph (.planning/skills/skills-knowledge-graph.yaml +
config/agents/skill-graph-index.yaml) and the generated full index
(config/agents/skill-index-full.yaml, by scripts/ai/build_skill_index.py).

Checks:
  (a) BLOCKING — coherence: every curated node's skill basename exists somewhere
      under .claude/skills (incl. archived `_*` families). A basename with no
      match anywhere = real removed/renamed drift. Known-stale curated ids
      (curated graph references skills not in the tree) are allowlisted pending
      the graph cleanup tracked in the follow-up issue.
  (b) ADVISORY — authored-but-backfilled: full-index entries marked
      `when_to_use_source: backfill` whose SKILL.md still has a loose
      when-to-use/trigger heading the generator does not recognize (h1, hyphen/
      underscore variants, etc.). Reported, not failed — surfaces authoring the
      generator can't parse for a human to fix (heading or generator widening).
  (c) BLOCKING — determinism: `build_skill_index.py --check` == the committed
      full index (re-run = no diff). Catches a stale index.

Exit 1 on any BLOCKING failure. Bypass: SKILL_INDEX_COHERENCE_ALLOW=1 (logged).

Curated↔full use different id namespaces (curated `<repo>/<skill>`, full
`<family-path>/<skill>`); (a) joins by skill basename by design (#3208 reshape).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO / ".claude" / "skills"
FULL_INDEX = REPO / "config" / "agents" / "skill-index-full.yaml"
KNOWLEDGE_GRAPH = REPO / ".planning" / "skills" / "skills-knowledge-graph.yaml"
GRAPH_INDEX = REPO / "config" / "agents" / "skill-graph-index.yaml"
BUILDER = REPO / "scripts" / "ai" / "build_skill_index.py"

# Curated graph references skills not present in .claude/skills. Emptied by #3214
# (the 8 stale nodes were removed from the graph). New unlisted drift fails (a).
KNOWN_STALE_CURATED: set[str] = set()

# Pre-existing dangling EDGE endpoints (edges referencing node ids that were never
# defined as nodes) — a SEPARATE drift class from the #3214 stale-node removal,
# needing per-edge judgment (some are real skills missing a node def, some are
# absent). Allowlisted pending the follow-up; NEW dangling edges fail check (d).
KNOWN_DANGLING_EDGE_REFS: set[str] = set()  # emptied by #3220 (4 nodes added, 1 dead edge removed)

# Loose when-to-use/trigger heading the GENERATOR may not recognize (it matches
# only `#{2,4} When to Use…` / `Trigger…`). Used by the advisory check (b).
_LOOSE_WTU_HEADING = re.compile(
    r"(?im)^\s*#{1,6}\s*(when[\s_-]*(to|you)[\s_-]*use|trigger)\b")


def _load_yaml(path: Path):
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def _curated_ids() -> set[str]:
    ids: set[str] = set()
    kg = _load_yaml(KNOWLEDGE_GRAPH)
    ids.update(n["id"] for n in kg.get("nodes", []) if isinstance(n, dict) and n.get("id"))
    gi = _load_yaml(GRAPH_INDEX)
    for lst in (gi.get("by_domain", {}) or {}).values():
        ids.update(lst or [])
    return ids


def _tree_basenames() -> set[str]:
    # every skill dir name under .claude/skills, INCLUDING archived `_*` families
    return {p.parent.name for p in SKILLS_DIR.rglob("SKILL.md")}


def check_a_coherence(failures: list[str]) -> None:
    tree = _tree_basenames()
    for cid in sorted(_curated_ids()):
        if cid in KNOWN_STALE_CURATED:
            continue
        if cid.split("/")[-1] not in tree:
            failures.append(
                f"(a) curated skill '{cid}' has no matching skill in .claude/skills "
                f"(removed/renamed). Reconcile the curated graph or add to "
                f"KNOWN_STALE_CURATED with a tracking issue.")


def check_b_advisory() -> list[str]:
    advisories: list[str] = []
    entries = _load_yaml(FULL_INDEX).get("skills", [])
    for e in entries:
        if e.get("when_to_use_source") != "backfill":
            continue
        sk = SKILLS_DIR / e["id"] / "SKILL.md"
        if not sk.is_file():
            continue
        if _LOOSE_WTU_HEADING.search(sk.read_text(encoding="utf-8", errors="replace")):
            advisories.append(e["id"])
    return advisories


def check_d_graph_integrity(failures: list[str]) -> None:
    """(d) BLOCKING — no dangling EDGE endpoints (#3214). Every edge from/to must
    be a defined node id. Pre-existing dangling refs are allowlisted
    (KNOWN_DANGLING_EDGE_REFS) pending the follow-up; a NEW dangling edge fails.

    Coverage `coverage.*.skills` is intentionally NOT node-constrained (it lists a
    domain's skills broadly, incl. non-curated ones) — so it is not checked here.
    """
    kg = _load_yaml(KNOWLEDGE_GRAPH)
    node_ids = {n["id"] for n in kg.get("nodes", []) if isinstance(n, dict) and n.get("id")}
    for e in kg.get("edges", []) or []:
        if not isinstance(e, dict):
            continue
        for ep in (e.get("from"), e.get("to")):
            if ep and ep not in node_ids and ep not in KNOWN_DANGLING_EDGE_REFS:
                failures.append(
                    f"(d) edge endpoint '{ep}' is not a defined node (dangling edge "
                    f"{e.get('from')}->{e.get('to')}). Add the node, remove the edge, "
                    f"or allowlist in KNOWN_DANGLING_EDGE_REFS with a tracking issue.")


def check_c_determinism(failures: list[str]) -> None:
    cmd = (["uv", "run", "--quiet", str(BUILDER)] if _has_uv() else [sys.executable, str(BUILDER)])
    out = subprocess.run(cmd + ["--check"], capture_output=True, text=True, cwd=REPO)
    if out.returncode != 0:
        failures.append(f"(c) build_skill_index.py --check failed: {out.stderr.strip()[:200]}")
        return
    # Compare line-wise so a CRLF checkout (Windows autocrlf) doesn't false-fail
    # against the subprocess's \n-normalized stdout (review r3-F4).
    if out.stdout.splitlines() != FULL_INDEX.read_text(encoding="utf-8").splitlines():
        failures.append(
            "(c) config/agents/skill-index-full.yaml is STALE — regenerate via "
            "`uv run python scripts/ai/build_skill_index.py`.")


def _has_uv() -> bool:
    from shutil import which
    return which("uv") is not None


def main() -> int:
    failures: list[str] = []
    check_a_coherence(failures)
    check_d_graph_integrity(failures)
    check_c_determinism(failures)
    advisories = check_b_advisory()

    if advisories:
        print(f"[advisory] (b) {len(advisories)} backfilled skill(s) have an "
              f"unrecognized when-to-use heading (fix the heading or widen the "
              f"generator): {', '.join(advisories[:10])}"
              + (" …" if len(advisories) > 10 else ""), file=sys.stderr)

    if failures:
        if os.environ.get("SKILL_INDEX_COHERENCE_ALLOW") == "1":
            print("SKILL_INDEX_COHERENCE_ALLOW=1 — bypassing skill-index drift:",
                  file=sys.stderr)
            for f in failures:
                print("  (bypassed) " + f, file=sys.stderr)
            return 0
        print("skill-index coherence FAILED:", file=sys.stderr)
        for f in failures:
            print("  " + f, file=sys.stderr)
        return 1

    print("skill-index coherence OK"
          + (f" ({len(advisories)} advisory)" if advisories else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
