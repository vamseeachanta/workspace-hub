#!/usr/bin/env python3
"""Generate the ecosystem domain->pointer map consumed by the UserPromptSubmit
auto-suggestion hook and the ecosystem-data-sources skill (#801).

Source of truth = llm-wiki/data/domain-database-index.yml (domain names,
repo_home, and whether any table routes private_sidecar => latent ACE_SHARE
precedent). Deliberately does NOT emit GitHub issue numbers — those live in the
trackers and drift; the hook points at the YAML + skill and lets those resolve.

Keywords are the one curated input (stable: 'riser'->SCR/TTR/VIV), kept here.

Usage:
  LLM_WIKI_PATH=/path/to/llm-wiki python3 scripts/data-sources/gen_domain_pointers.py [--out PATH] [--check]

Writes .claude/hooks/ecosystem-domain-map.json (relative to workspace-hub root)
unless --out given. --check exits 1 if the on-disk map is stale vs regenerated.
"""
import argparse
import json
import os
import sys

# Curated, stable keyword triggers per domain (word-boundary matched by the hook).
DOMAIN_KEYWORDS = {
    "riser": ["riser", "scr", "slwr", "ttr", "viv", "touchdown", "catenary riser"],
    "mooring": ["mooring", "station-keeping", "station keeping", "catenary", "anchor", "mooring line"],
    "pipeline-subsea": ["pipeline", "flowline", "on-bottom stability", "lateral buckling", "upheaval", "free span", "on bottom stability"],
    "structural-ffs": ["fitness-for-service", "fitness for service", "ffs", "api 579", "plate buckling", "tubular", "s-n curve", "sn curve"],
    "naval-arch-hydro": ["rao", "seakeeping", "vessel motion", "hydrodynamic", "aqwa", "orcawave", "wamit", "hull form"],
    "metocean": ["metocean", "wave scatter", "hindcast", "hs/tp", "extreme value", "design storm", "ndbc", "current profile"],
    "materials-standards": ["material grade", "steel grade", "line pipe", "api 5l", "aisc", "grade matrix"],
    "production-reservoir": ["production data", "ogor", "decline curve", "field production", "reservoir", "bsee", "eia"],
    "geotech": ["geotechnical", "soil profile", "p-y curve", "t-z curve", "pile capacity", "cpt", "anchor holding"],
    "asset-financial": ["portfolio", "equities", "ohlcv", "yfinance", "sec edgar", "valuation", "watchlist"],
    "drilling-well": ["well trajectory", "directional survey", "casing", "tubing", "drilling rig", "wellbore"],
    "cad-simulation": ["step file", "iges", "brep", "mesh", "solver deck", "orcaflex model", "cad geometry"],
}


def load_index(llm_wiki_path):
    import yaml
    path = os.path.join(llm_wiki_path, "data", "domain-database-index.yml")
    if not os.path.exists(path):
        raise SystemExit(f"domain-database-index.yml not found at {path}; set LLM_WIKI_PATH")
    with open(path) as f:
        return yaml.safe_load(f)


def build_map(index):
    domains = index.get("domains", {})
    out = {}
    for name, d in domains.items():
        if name not in DOMAIN_KEYWORDS:
            # index has a domain we have no keywords for -> surface it so it's not silently dropped
            keywords = [name]
        else:
            keywords = DOMAIN_KEYWORDS[name]
        has_precedent = any(t.get("route") == "private_sidecar" for t in d.get("tables", []))
        out[name] = {
            "repo_home": d.get("repo_home", ""),
            "keywords": keywords,
            "has_ace_share_precedent": has_precedent,
        }
    return {
        "_generated_from": "llm-wiki/data/domain-database-index.yml",
        "_note": "issue numbers deliberately omitted (drift); resolve via the index + ecosystem-data-sources skill",
        "domains": out,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--llm-wiki", default=os.environ.get("LLM_WIKI_PATH"))
    args = ap.parse_args(argv)

    llm_wiki = args.llm_wiki
    if not llm_wiki:
        # default: sibling of workspace-hub root
        here = os.path.dirname(os.path.abspath(__file__))
        ws_root = os.path.dirname(os.path.dirname(here))  # scripts/data-sources -> ws root
        llm_wiki = os.path.join(os.path.dirname(ws_root), "llm-wiki")

    result = build_map(load_index(llm_wiki))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"

    out = args.out
    if not out:
        here = os.path.dirname(os.path.abspath(__file__))
        ws_root = os.path.dirname(os.path.dirname(here))
        out = os.path.join(ws_root, ".claude", "hooks", "ecosystem-domain-map.json")

    if args.check:
        existing = open(out).read() if os.path.exists(out) else ""
        if existing != text:
            print(f"STALE: {out} differs from regenerated map", file=sys.stderr)
            return 1
        print("OK: map up to date")
        return 0

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(text)
    print(f"wrote {out} ({len(result['domains'])} domains)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
