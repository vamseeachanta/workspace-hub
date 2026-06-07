#!/usr/bin/env python3
"""domain_coverage.py — warn-only guard on the ecosystem `domain:` label invariant.

On 2026-06-07 every open issue across the repo ecosystem was brought to EXACTLY
ONE `domain:` label, and deckhand `routing/taxonomy.yaml` established the 1:1
crosswalk of those labels to llm-wiki nodes (workspace-hub#2962, deckhand#84).
Without a guard the invariant rots with every new issue. This tool reports, per
repo, the four ways it can break:

  1. zero    — open issue with NO `domain:` label (unroutable)
  2. multi   — open issue with >1 `domain:` label (reconcile takes the FIRST;
               order-dependent placement — the #2878 adversarial finding)
  3. unknown — a `domain:` value NOT in routing/taxonomy.yaml (crosswalk drift;
               new domains must go through a taxonomy PR first)
  4. alias   — use of a synonym label pending staged rename (should shrink, not grow)

Checks 1 and 2 need only GitHub labels and always run. Checks 3 and 4 need the
canonical label set + aliases from taxonomy.yaml; pass it with --taxonomy. If it
is absent (e.g. the private SoT is unreachable in CI) those checks are skipped
with a logged notice rather than failing.

Warn-only by default (exit 0); --strict exits 1 when any violation exists so a
gate can block. The planning core (`analyze`) is pure; gh calls are isolated
behind an injectable runner so the whole tool is hermetically testable.

Usage:
  domain_coverage.py                              report all default repos
  domain_coverage.py --taxonomy routing/taxonomy.yaml
  domain_coverage.py --repos repos.txt --strict
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # taxonomy checks degrade gracefully

DOMAIN_PREFIX = "domain:"

# The canonical coverage set: every repo that must keep one-domain-per-issue.
# Explicit (not manifest-derived) because the kanban manifest is board-scoped —
# it carries the wrong owner for assethold and omits the client wikis + deckhand.
DEFAULT_REPOS = [
    "vamseeachanta/aceengineer-admin",
    "vamseeachanta/aceengineer-strategy",
    "vamseeachanta/achantas-data",
    "vamseeachanta/assetutilities",
    "vamseeachanta/deckhand",
    "vamseeachanta/deckhand-sandbox",
    "vamseeachanta/digitalmodel",
    "vamseeachanta/hobbies",
    "vamseeachanta/investments",
    "vamseeachanta/llm-wiki",
    "vamseeachanta/llm-wiki-acma",
    "vamseeachanta/llm-wiki-fdas",
    "vamseeachanta/sabithaandkrishnaestates",
    "vamseeachanta/teamresumes",
    "vamseeachanta/workspace-hub",
    "vamseeachanta/worldenergydata",
    "samdansk2/assethold",
]


def domains_of(issue: dict) -> list[str]:
    """The `domain:`-prefixed label names on an issue, prefix stripped."""
    return [
        lbl["name"][len(DOMAIN_PREFIX):]
        for lbl in issue.get("labels", [])
        if lbl["name"].startswith(DOMAIN_PREFIX)
    ]


def analyze(issues: list[dict], canonical: set[str] | None, aliases: set[str] | None) -> dict:
    """Pure core: classify a repo's open issues against the invariant.

    `canonical`/`aliases` None => taxonomy unavailable; checks 3 & 4 skipped.
    Returns lists of {number, title, domains} (and the offending label for 3/4).
    """
    zero, multi, unknown, alias = [], [], [], []
    for it in issues:
        ds = domains_of(it)
        rec = {"number": it["number"], "title": it["title"], "domains": ds}
        if len(ds) == 0:
            zero.append(rec)
            continue
        if len(ds) > 1:
            multi.append(rec)
        # check the first label (the one reconcile actually routes on)
        first = ds[0]
        if aliases is not None and first in aliases:
            alias.append({**rec, "label": first})
        elif canonical is not None and first not in canonical and (aliases is None or first not in aliases):
            unknown.append({**rec, "label": first})
    return {
        "total": len(issues),
        "zero": zero,
        "multi": multi,
        "unknown": unknown,
        "alias": alias,
        "taxonomy_checked": canonical is not None,
    }


def load_taxonomy(path: Path) -> tuple[set[str], set[str]]:
    """Return (canonical_label_names, alias_label_names) from taxonomy.yaml."""
    if yaml is None:
        raise RuntimeError("PyYAML required to read taxonomy.yaml")
    doc = yaml.safe_load(path.read_text())
    canonical = set(doc["crosswalk"].keys())
    aliases = {a["alias"] for a in doc.get("aliases", [])}
    return canonical, aliases


def _gh(repo: str, runner) -> list[dict]:
    out = runner(
        ["gh", "issue", "list", "-R", repo, "--state", "open",
         "--limit", "1000", "--json", "number,title,labels"]
    )
    return json.loads(out) if out.strip() else []


def _default_runner(args: list[str]) -> str:
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def render(report: dict) -> tuple[str, int]:
    """Markdown report + total violation count."""
    lines = ["# Domain-coverage guard\n"]
    if not report["any_taxonomy"]:
        lines.append("> taxonomy.yaml not provided — crosswalk-drift (unknown) "
                     "and alias checks skipped; zero/multi still enforced.\n")
    lines.append("| Repo | Open | Zero | Multi | Unknown | Alias |")
    lines.append("|---|--:|--:|--:|--:|--:|")
    total_viol = 0
    for repo, r in report["repos"].items():
        n = len(r["zero"]) + len(r["multi"]) + len(r["unknown"]) + len(r["alias"])
        total_viol += n
        lines.append(f"| {repo} | {r['total']} | {len(r['zero'])} | "
                     f"{len(r['multi'])} | {len(r['unknown'])} | {len(r['alias'])} |")
    lines.append("")
    for repo, r in report["repos"].items():
        detail = []
        for kind in ("zero", "multi", "unknown", "alias"):
            for rec in r[kind]:
                tag = f" → `{rec['label']}`" if kind in ("unknown", "alias") else ""
                doms = ",".join(rec["domains"]) or "—"
                detail.append(f"- **{kind}** {repo}#{rec['number']} [{doms}]{tag}: {rec['title']}")
        if detail:
            lines.append(f"### {repo}")
            lines.extend(detail)
            lines.append("")
    if total_viol == 0:
        lines.append("✅ Invariant holds: every open issue has exactly one taxonomy-known domain.")
    return "\n".join(lines), total_viol


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repos", type=Path, help="file with one owner/repo per line (default: built-in list)")
    ap.add_argument("--taxonomy", type=Path, help="path to routing/taxonomy.yaml for drift/alias checks")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any violation")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = ap.parse_args()

    repos = (
        [l.strip() for l in args.repos.read_text().splitlines() if l.strip() and not l.startswith("#")]
        if args.repos else DEFAULT_REPOS
    )

    canonical = aliases = None
    if args.taxonomy and args.taxonomy.exists():
        canonical, aliases = load_taxonomy(args.taxonomy)
    elif args.taxonomy:
        print(f"notice: {args.taxonomy} not found — skipping drift/alias checks", file=sys.stderr)

    report = {"repos": {}, "any_taxonomy": canonical is not None}
    for repo in repos:
        try:
            issues = _gh(repo, _default_runner)
        except subprocess.CalledProcessError as e:
            print(f"warn: {repo}: gh failed ({e.stderr.strip()[:120]}) — skipped", file=sys.stderr)
            continue
        report["repos"][repo] = analyze(issues, canonical, aliases)

    if args.json:
        print(json.dumps(report, indent=2))
        total = sum(len(r["zero"]) + len(r["multi"]) + len(r["unknown"]) + len(r["alias"])
                    for r in report["repos"].values())
    else:
        md, total = render(report)
        print(md)

    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    sys.exit(main())
