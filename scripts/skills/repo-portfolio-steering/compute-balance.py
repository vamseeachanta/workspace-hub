#!/usr/bin/env python3
"""
compute-balance.py — L1+L2 balance reader for repo-portfolio-steering skill.

L1: Parses INDEX.md ## By Category section for category counts.
L2: Reads .claude/state/portfolio-signals.yaml for per-provider activity.

Does NOT write or update portfolio-signals.yaml (that is WRK-1020 scope).

Usage (CLI):
    uv run --no-project python compute-balance.py [--signals <path>] [--threshold 0.30]

Returns JSON to stdout.
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

REPO_ROOT = Path(__file__).parents[3]

DOMAIN_PERSONA_MAP = {
    "subsea": ("Offshore operator / pipeline integrity engineer", "VIV/freespan assessment"),
    "pipeline": ("Offshore operator / pipeline integrity engineer", "Pipeline integrity report"),
    "cathodic": ("Corrosion engineer / asset manager", "CP system design report"),
    "marine": ("Naval architect / offshore designer", "Motions & loads study"),
    "hydrodynamic": ("Naval architect / offshore designer", "Motions & loads study"),
    "drilling": ("Drilling engineer / well planner", "Drilling performance analysis"),
    "rop": ("Drilling engineer / well planner", "Drilling performance analysis"),
    "production": ("Reservoir engineer / E&P consultant", "Decline curve + reserves"),
    "forecast": ("Reservoir engineer / E&P consultant", "Decline curve + reserves"),
    "arps": ("Reservoir engineer / E&P consultant", "Decline curve + reserves"),
    "net_lease": ("Real estate investor / asset manager", "NNN lease underwriting"),
    "net lease": ("Real estate investor / asset manager", "NNN lease underwriting"),
    "structural": ("Structural engineer / EPC contractor", "Plate/beam design check"),
    "fea": ("Structural engineer / EPC contractor", "Plate/beam design check"),
}


def _parse_category_counts(index_path: Path) -> dict[str, int]:
    """Parse ## By Category summary table from INDEX.md."""
    text = index_path.read_text(encoding="utf-8")
    # Find the summary table (first By Category block)
    # Format: | harness | 45 |
    counts: dict[str, int] = {}
    in_table = False
    for line in text.splitlines():
        if "### By Category" in line or "## By Category" in line:
            in_table = True
            continue
        if in_table:
            m = re.match(r"\|\s*(\w+)\s*\|\s*(\d+)\s*\|", line)
            if m:
                counts[m.group(1).strip()] = int(m.group(2))
            elif line.startswith("##") and "By Category" not in line:
                break
    return counts


def _load_signals(signals_path: Path | None) -> dict | None:
    """Load portfolio-signals.yaml; return None if missing or unparseable."""
    if signals_path is None or not signals_path.exists():
        return None
    if not _YAML_AVAILABLE:
        return None
    try:
        return yaml.safe_load(signals_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None


def _harness_budget(harness_pct: float) -> str:
    if harness_pct <= 0.15:
        return "1 harness per 3 engineering (ramp up harness)"
    elif harness_pct <= 0.30:
        return "1 harness per 5 engineering (maintain)"
    else:
        return "0 harness — pure engineering until below threshold"


def _gtm_ranking(index_path: Path) -> list[dict]:
    """
    Simple GTM ranking from active WRK items.
    Reads pending/ + working/ dirs for brochure_status + percent_complete.
    Returns top entries ranked: brochure_status=ready > draft > n/a, then pct desc.
    """
    queue_dir = index_path.parent
    entries = []
    for folder in ("pending", "working"):
        d = queue_dir / folder
        if not d.exists():
            continue
        for f in d.glob("WRK-*.md"):
            text = f.read_text(encoding="utf-8")
            cat = _fm_value(text, "category") or ""
            if cat != "engineering":
                continue
            wrk_id = _fm_value(text, "id") or f.stem
            brochure = _fm_value(text, "brochure_status") or "n/a"
            pct = int(_fm_value(text, "percent_complete") or "0")
            title = _fm_value(text, "title") or ""
            domain = _infer_domain(title)
            entries.append({
                "wrk_id": wrk_id,
                "domain": domain,
                "brochure_status": brochure,
                "percent_complete": pct,
            })
    # Sort: ready > draft > n/a, then pct desc, then id asc
    brochure_rank = {"ready": 0, "updated": 1, "draft": 2, "synced": 1, "n/a": 3, "pending": 2}
    entries.sort(key=lambda e: (
        brochure_rank.get(e["brochure_status"], 9),
        -e["percent_complete"],
        e["wrk_id"],
    ))
    return entries


def _next3_fund(gtm_ranking: list[dict]) -> list[dict]:
    """Top 3 engineering items with domain→persona mapping."""
    result = []
    for e in gtm_ranking:
        persona, project_type = _persona_for(e.get("domain", ""))
        result.append({
            "wrk_id": e["wrk_id"],
            "domain": e["domain"],
            "client_persona": persona,
            "project_type": project_type,
            "percent_complete": e["percent_complete"],
        })
        if len(result) == 3:
            break
    return result


def _fm_value(text: str, key: str) -> str | None:
    """Extract a frontmatter scalar value."""
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if in_fm:
            m = re.match(rf"^{re.escape(key)}\s*:\s*(.*)", line)
            if m:
                val = m.group(1).strip().strip('"').strip("'")
                return val if val else None
    return None


def _infer_domain(title: str) -> str:
    t = title.lower()
    for kw in DOMAIN_PERSONA_MAP:
        if kw in t:
            return kw
    return "engineering"


def _persona_for(domain: str) -> tuple[str, str]:
    for kw, (persona, proj) in DOMAIN_PERSONA_MAP.items():
        if kw in domain.lower():
            return persona, proj
    return ("Engineering practitioner", "Technical analysis")


def compute_balance(
    index_path: Path,
    signals_path: Path | None = None,
    harness_threshold: float = 0.30,
) -> dict:
    """
    Compute harness/engineering balance from INDEX.md + optional signals file.
    Returns a dict with L1 (queue balance) and L2 (provider activity) data.
    """
    cats = _parse_category_counts(index_path)
    total = sum(cats.values()) if cats else 1
    harness_count = cats.get("harness", 0)
    engineering_count = cats.get("engineering", 0)
    harness_pct = harness_count / total if total else 0.0
    engineering_pct = engineering_count / total if total else 0.0

    harness_status = "HEALTHY" if harness_pct <= harness_threshold else "OVER-INVESTED"

    signals = _load_signals(signals_path)
    provider_activity = signals.get("provider_activity") if signals else None

    gtm = _gtm_ranking(index_path)
    next3 = _next3_fund(gtm)

    return {
        "categories": cats,
        "total": total,
        "harness_pct": round(harness_pct, 4),
        "engineering_pct": round(engineering_pct, 4),
        "harness_threshold": harness_threshold,
        "harness_status": harness_status,
        "harness_budget": _harness_budget(harness_pct),
        "gtm_ranking": gtm,
        "next3": next3,
        "provider_activity": provider_activity,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Compute portfolio balance")
    parser.add_argument("--signals", type=Path, default=None)
    parser.add_argument("--threshold", type=float, default=0.30)
    parser.add_argument("--index", type=Path,
                        default=REPO_ROOT / ".claude/work-queue/INDEX.md")
    args = parser.parse_args()

    result = compute_balance(
        index_path=args.index,
        signals_path=args.signals,
        harness_threshold=args.threshold,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
