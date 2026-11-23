#!/usr/bin/env python3
# ABOUTME: Driver script for research & literature gathering per engineering domain
# ABOUTME: Queries standards ledger, doc index, capability map; outputs research brief YAML

"""
Usage:
    python scripts/data/research-literature/research-domain.py \
        --category geotechnical --repo digitalmodel [--dry-run] [--generate-download-script]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

HUB_ROOT = Path(__file__).resolve().parents[3]
DOMAIN_MAP_PATH = HUB_ROOT / "config" / "research-literature" / "domain-repo-map.yaml"
LEDGER_PATH = HUB_ROOT / "data" / "document-index" / "standards-transfer-ledger.yaml"
INDEX_PATH = HUB_ROOT / "data" / "document-index" / "index.jsonl"
BRIEF_DIR = HUB_ROOT / "specs" / "capability-map" / "research-briefs"
TEMPLATE_PATH = HUB_ROOT / "scripts" / "data" / "research-literature" / "download-template.sh"


def load_domain_map() -> dict:
    data = yaml.safe_load(DOMAIN_MAP_PATH.read_text())
    return data.get("domains", {})


def query_ledger(domain: str) -> list[dict]:
    """Return standards from ledger matching domain."""
    if not LEDGER_PATH.exists():
        print(f"Warning: ledger not found at {LEDGER_PATH}", file=sys.stderr)
        return []
    data = yaml.safe_load(LEDGER_PATH.read_text())
    standards = data.get("standards", [])
    return [s for s in standards if s.get("domain") == domain]


def query_doc_index(keywords: list[str], limit: int = 50) -> list[dict]:
    """Search doc index for matching documents."""
    if not INDEX_PATH.exists():
        print(f"Warning: doc index not found at {INDEX_PATH}", file=sys.stderr)
        return []
    matches = []
    kw_lower = [k.lower() for k in keywords]
    with open(INDEX_PATH) as f:
        for line in f:
            if len(matches) >= limit:
                break
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            path_lower = rec.get("path", "").lower()
            summary_lower = (rec.get("summary") or "").lower()
            text = path_lower + " " + summary_lower
            if any(kw in text for kw in kw_lower):
                matches.append(rec)
    return matches


def query_capability_map(repo: str, domain: str) -> list[dict]:
    """Find capability map modules matching domain."""
    cap_path = HUB_ROOT / "specs" / "capability-map" / f"{repo}.yaml"
    if not cap_path.exists():
        return []
    data = yaml.safe_load(cap_path.read_text())
    results = []
    for mod in data.get("modules", []):
        mod_name = mod.get("module", "").lower()
        if domain.lower() in mod_name:
            results.append(mod)
    return results


def build_brief(
    category: str,
    repo: str,
    domain_cfg: dict,
    ledger_standards: list[dict],
    doc_matches: list[dict],
    cap_modules: list[dict],
) -> dict:
    """Assemble a research brief dict from gathered data."""
    applicable_standards = []
    for s in ledger_standards:
        applicable_standards.append({
            "id": s.get("id", "UNKNOWN"),
            "title": s.get("title", ""),
            "org": s.get("org", ""),
            "status": _map_ledger_status(s.get("status", "gap")),
            "doc_path": s.get("doc_path"),
            "key_sections": s.get("key_sections", []),
        })

    available_documents = []
    for doc in doc_matches[:20]:
        available_documents.append({
            "path": doc.get("path", ""),
            "source": doc.get("source", "unknown"),
            "summary": doc.get("summary", ""),
            "relevance": "medium",
        })

    download_tasks = []
    for s in applicable_standards:
        if s["status"] in ("needs_download", "paywalled"):
            download_tasks.append({
                "standard": s["id"],
                "url": None,
                "notes": f"{s['status']} — search required",
            })

    brief = {
        "category": category,
        "subcategory": "general",
        "generated": date.today().isoformat(),
        "applicable_standards": applicable_standards,
        "available_documents": available_documents,
        "download_tasks": download_tasks,
        "key_equations": [],
        "worked_examples": [],
        "implementation_target": {
            "repo": repo,
            "module": f"{category}/",
            "existing_code": None,
        },
    }
    return brief


def _map_ledger_status(status: str) -> str:
    """Map ledger status to brief status."""
    mapping = {
        "done": "available",
        "reference": "available",
        "in_progress": "available",
        "gap": "needs_download",
        "wrk_captured": "needs_download",
        "deferred": "needs_download",
    }
    return mapping.get(status, "needs_download")


def generate_download_script(
    category: str,
    domain_cfg: dict,
    brief: dict,
    dry_run: bool = False,
) -> Path | None:
    """Generate a download script from template for this domain."""
    dest_dir = Path(domain_cfg["ace_path"])

    if not TEMPLATE_PATH.exists():
        print(f"Warning: template not found at {TEMPLATE_PATH}", file=sys.stderr)
        return None

    template = TEMPLATE_PATH.read_text()
    script_content = template.replace("{{DOMAIN}}", category)
    script_content = script_content.replace("{{DEST}}", str(dest_dir))

    # Build URL block from download tasks
    url_lines = []
    for task in brief.get("download_tasks", []):
        url = task.get("url") or "# TODO: find URL"
        std = task.get("standard", "unknown")
        url_lines.append(f'# {std}')
        url_lines.append(f'# download "{url}" "${{DEST}}" "{std}.pdf"')
    url_block = "\n".join(url_lines) if url_lines else "# No download tasks identified"
    script_content = script_content.replace("{{URLS}}", url_block)

    output_path = dest_dir / "download-literature.sh"
    if dry_run:
        print(f"Would write download script to: {output_path}")
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(script_content)
    output_path.chmod(0o755)
    print(f"Download script written to: {output_path}")
    return output_path


def save_brief(brief: dict, category: str, dry_run: bool = False) -> Path:
    """Save research brief YAML to specs/capability-map/research-briefs/."""
    BRIEF_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{category}.yaml"
    output_path = BRIEF_DIR / filename

    if dry_run:
        print(f"Would write research brief to: {output_path}")
        return output_path

    header = (
        f"# ABOUTME: Research brief for {category} domain\n"
        f"# ABOUTME: Auto-generated by research-domain.py\n\n"
    )
    output_path.write_text(header + yaml.dump(brief, default_flow_style=False, sort_keys=False))
    print(f"Research brief written to: {output_path}")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research & literature gathering for engineering domains",
    )
    parser.add_argument("--category", required=True, help="Engineering domain")
    parser.add_argument("--repo", required=True, help="Target repo")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument(
        "--generate-download-script", action="store_true",
        help="Also generate download script from template",
    )
    args = parser.parse_args()

    domain_map = load_domain_map()
    if args.category not in domain_map:
        print(f"Error: unknown domain '{args.category}'", file=sys.stderr)
        print(f"Available: {', '.join(sorted(domain_map.keys()))}", file=sys.stderr)
        return 1

    domain_cfg = domain_map[args.category]
    print(f"Researching domain: {args.category} → {args.repo}")

    # Query data sources
    ledger_standards = query_ledger(domain_cfg["ledger_domain"])
    print(f"  Ledger: {len(ledger_standards)} standards")

    doc_matches = query_doc_index(domain_cfg["keywords"])
    print(f"  Doc index: {len(doc_matches)} matches")

    cap_modules = query_capability_map(args.repo, args.category)
    print(f"  Capability map: {len(cap_modules)} modules")

    # Build and save brief
    brief = build_brief(
        args.category, args.repo, domain_cfg,
        ledger_standards, doc_matches, cap_modules,
    )
    brief_path = save_brief(brief, args.category, dry_run=args.dry_run)

    if args.generate_download_script:
        generate_download_script(
            args.category, domain_cfg, brief, dry_run=args.dry_run,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
