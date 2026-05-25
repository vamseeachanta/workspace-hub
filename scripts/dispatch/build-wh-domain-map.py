#!/usr/bin/env python3
"""build-wh-domain-map.py — draft a fine->coarse domain mapping for workspace-hub.

workspace-hub has 162 fine-grained `domain:*` labels actively used on issues.
The kanban has 6 coarse board-domains. This maps each fine label to ONE coarse
board-domain (many-to-one) so both layers agree WITHOUT relabeling any issue:
an issue keeps its precise `domain:agent-patterns` label; its board grouping is
derived as map[agent-patterns] -> ai-orchestration.

Ordered keyword rules; first match wins. Anything unmatched lands in
`uncategorised` for explicit human review (never silently bucketed).

Output: .claude/memory/kanban/domain-map-workspace-hub.yaml  (--write)
Default: print the grouped draft for review.
"""
from __future__ import annotations
import json, subprocess, sys
from collections import defaultdict
from pathlib import Path

COARSE = ["ai-orchestration", "business", "data", "engineering", "harness", "ops"]

# Ordered (coarse, [substrings]). First rule whose substring is IN the fine name wins.
# Order matters: more specific / higher-priority buckets first.
RULES = [
    ("engineering", ["naval", "hydro", "mooring", "drill", "structural", "subsea",
                     "riser", "fatigue", "cathodic", "asset-integrity", "marine",
                     "maritime", "offshore", "reservoir", "artificial-lift",
                     "electrical", "semiconductor", "chip", "cad-fea", "orcaflex",
                     "parametric", "ship-plan", "units", "calculation"]),
    ("data",        ["extraction", "pipeline", "ingest", "data-", "data-pipeline",
                     "document", "knowledge", "index", "search", "query", "bsee",
                     "gis", "dataset", "dedup", "doc-generation", "reporting",
                     "daily-report", "internet-extraction", "extraction-skill"]),
    ("ai-orchestration", ["agent", "ai-", "mcp", "memory", "session", "cross-review",
                          "skill", "prompt", "context", "orchestration", "llm",
                          "notification"]),
    ("harness",     ["workflow", "gate", "enforce", "spec-template", "scaffold",
                     "code-quality", "code-promotion", "test", "static-analysis",
                     "type-stub", "lint", "refactor", "review", "hooks",
                     "work-queue", "standards-tooling", "standards", "patterns",
                     "compliance", "audit", "dependency", "quality"]),
    ("business",    ["strategy", "finance", "gtm", "cv-", "cv-strategy", "labor",
                     "branding", "portfolio", "tax", "household", "cre-", "market",
                     "website", "content", "onboarding", "training",
                     "project-management", "home", "admin"]),
    ("ops",         ["ci-cd", "release", "infra", "machine", "workstation", "cleanup",
                     "repo-", "secrets", "environment", "platform", "backup", "git",
                     "maintenance", "performance", "security", "session-health",
                     "automation", "config", "scripts", "terminal", "cross-platform",
                     "tooling", "integrations"]),
]


def fine_labels(repo="vamseeachanta/workspace-hub") -> list[str]:
    out = subprocess.run(["gh", "label", "list", "--repo", repo, "--limit", "400",
                          "--json", "name"], capture_output=True, text=True)
    out.check_returncode()
    return sorted(l["name"][7:] for l in json.loads(out.stdout)
                  if l["name"].startswith("domain:"))


# Exact-name overrides — win over keyword rules. Resolve false substring matches
# (e.g. "git" inside "digital") and place the 13 ambiguous labels deliberately.
OVERRIDES = {
    "digitalmodel": "engineering", "ops": "ops", "safety": "engineering",
    "skills enhancement": "ai-orchestration", "aceengineer": "business",
    "api-contracts": "harness", "assetutilities": "engineering", "cli-ux": "harness",
    "docs": "harness", "financial-analysis": "business", "frontend-design": "business",
    "visualization": "data", "notification": "ops", "general": "ops",
    "uncategorised": "ops",
}


def classify(name: str) -> str:
    if name.lower() in OVERRIDES:
        return OVERRIDES[name.lower()]
    for coarse, subs in RULES:
        if any(s in name for s in subs):
            return coarse
    return "uncategorised"


def main():
    write = "--write" in sys.argv
    labels = fine_labels()
    mapping = {name: classify(name) for name in labels}
    groups = defaultdict(list)
    for name, coarse in mapping.items():
        groups[coarse].append(name)

    print(f"workspace-hub domain reconciliation — {len(labels)} fine labels\n")
    for coarse in COARSE + ["uncategorised"]:
        items = sorted(groups.get(coarse, []))
        if not items:
            continue
        marker = "  ⚠ REVIEW" if coarse == "uncategorised" else ""
        print(f"\033[1m{coarse}\033[0m ({len(items)}){marker}")
        print("  " + ", ".join(items) + "\n")

    if write:
        out = Path(".claude/memory/kanban/domain-map-workspace-hub.yaml")
        payload = {
            "repo": "vamseeachanta/workspace-hub",
            "note": "fine domain: label -> coarse board-domain. No issue relabeling; "
                    "board grouping is derived via this map. Draft — review uncategorised.",
            "coarse_domains": COARSE,
            "map": dict(sorted(mapping.items())),
        }
        import yaml
        with open(out, "w") as f:
            yaml.safe_dump(payload, f, sort_keys=False, width=100)
        print(f"wrote {out}")
    else:
        print("\033[2m(draft — re-run with --write to save the mapping yaml)\033[0m")


if __name__ == "__main__":
    main()
