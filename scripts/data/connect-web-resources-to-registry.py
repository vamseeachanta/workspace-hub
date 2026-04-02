#!/usr/bin/env python3
"""
ABOUTME: Connects OrcaWave/OrcaFlex/AQWA web resources to the unified registry.
Classifies each URL as downloadable or reference-only, updates download_status
and local_backup_path, generates a prioritized download list.
Usage: uv run --no-project python scripts/data/connect-web-resources-to-registry.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import yaml

HUB_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = HUB_ROOT / "data/document-index/online-resource-registry.yaml"

# Web resource files
WEB_RESOURCE_FILES = {
    "orcaflex": HUB_ROOT / "digitalmodel/.claude/agents/orcaflex/context/external/web/web_resources.yaml",
    "aqwa": HUB_ROOT / "digitalmodel/.claude/agents/aqwa/context/external/web/web_resources.yaml",
    "web_test_module": HUB_ROOT / "digitalmodel/.claude/agents/web-test-module/context/external/web/web_resources.yaml",
}

# --- URL classification rules ---
# URLs that point to downloadable content (PDFs, repos, datasets)
DOWNLOADABLE_PATTERNS = [
    ".pdf", "/download/", "github.com", "gitlab.com",
    "arxiv.org/abs", "arxiv.org/pdf", "/dataset",
    "huggingface.co", "zenodo.org",
]

# URLs that are reference pages only
REFERENCE_PATTERNS = [
    "webhelp", "help/htm", "/products/", "training-center",
    "product-page", "ansys.com/products", "ansys.com/training",
    "ansyshelp.ansys.com", "docs.python.org",
]


def classify_url(url: str, notes: str = "") -> dict:
    """Classify a URL as downloadable or reference-only.

    Returns dict with:
      - is_downloadable: bool
      - classification: str (downloadable_pdf, downloadable_repo, reference_page, standard_portal)
      - local_backup_path: str (suggested path for downloads)
      - download_priority: int (1-5, higher = more important)
    """
    url_lower = url.lower()
    notes_lower = notes.lower()

    # Check for downloadable patterns
    is_downloadable = any(p in url_lower for p in DOWNLOADABLE_PATTERNS)
    is_reference = any(p in url_lower for p in REFERENCE_PATTERNS)

    # Standards portals are reference but have downloadable sub-content
    is_standard = any(x in url_lower for x in [
        "dnv.com/rules", "dnv.com/oilgas/download", "api.org/products",
        "api.org/standards", "iacs.org",
    ])

    if is_standard:
        return {
            "is_downloadable": True,
            "classification": "standard_portal",
            "download_priority": 5,
        }
    elif is_downloadable and not is_reference:
        if "github.com" in url_lower or "gitlab.com" in url_lower:
            return {
                "is_downloadable": True,
                "classification": "downloadable_repo",
                "download_priority": 4,
            }
        elif ".pdf" in url_lower or "/download/" in url_lower:
            return {
                "is_downloadable": True,
                "classification": "downloadable_pdf",
                "download_priority": 5,
            }
        else:
            return {
                "is_downloadable": True,
                "classification": "downloadable_data",
                "download_priority": 3,
            }
    else:
        return {
            "is_downloadable": False,
            "classification": "reference_page",
            "download_priority": 1,
        }


def infer_domain_for_url(url: str, notes: str, source_agent: str) -> str:
    """Infer domain based on URL content and source agent."""
    url_lower = url.lower()
    notes_lower = notes.lower()

    if "orcaflex" in url_lower or "orcina" in url_lower:
        return "orcaflex"
    if "orcawave" in url_lower:
        return "orcawave"
    if "aqwa" in url_lower or "ansys" in url_lower:
        return "hydrodynamics"  # AQWA is a hydrodynamics tool
    if "dnv" in url_lower:
        if "c205" in url_lower or "environmental" in notes_lower:
            return "hydrodynamics"
        return "structural"
    if "api.org" in url_lower:
        if "2sk" in url_lower or "mooring" in notes_lower or "station keeping" in notes_lower:
            return "marine"
        return "structural"
    if "python" in url_lower:
        return "general"

    # Fallback to source agent
    agent_domain_map = {
        "orcaflex": "orcaflex",
        "aqwa": "hydrodynamics",
        "web_test_module": "general",
    }
    return agent_domain_map.get(source_agent, "general")


def suggest_backup_path(url: str, domain: str, classification: str) -> str:
    """Suggest a local backup path for downloadable resources."""
    if classification == "reference_page":
        return ""

    parsed = urlparse(url)
    # Build path based on domain
    base = f"/mnt/ace/digitalmodel/{domain}"

    if classification == "downloadable_repo":
        # Extract repo name from GitHub URL
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(parts) >= 2:
            return f"{base}/repos/{parts[-1]}"
        return f"{base}/repos/"

    if classification == "downloadable_pdf":
        filename = parsed.path.split("/")[-1] or "document.pdf"
        return f"{base}/pdfs/{filename}"

    if classification == "standard_portal":
        return f"{base}/standards/"

    return f"{base}/downloads/"


def update_registry_with_web_resources():
    """Main function to update the registry with web resource classifications."""
    # Load current registry
    with open(REGISTRY_PATH) as f:
        registry = yaml.safe_load(f)

    entries = registry.get("entries", [])
    url_index = {e["url"].rstrip("/"): i for i, e in enumerate(entries)}

    # Track new entries and updates
    new_entries = []
    updated_count = 0
    web_resource_report = []

    for agent_key, path in WEB_RESOURCE_FILES.items():
        if not path.exists():
            print(f"WARNING: {agent_key} not found at {path}", file=sys.stderr)
            continue

        with open(path) as f:
            data = yaml.safe_load(f)

        for link in data.get("user_added_links", []):
            url = link.get("url", "")
            if not url:
                continue

            notes = link.get("notes", "")
            title = link.get("title", url)

            # Classify the URL
            classification = classify_url(url, notes)
            domain = infer_domain_for_url(url, notes, agent_key)
            backup_path = suggest_backup_path(
                url, domain, classification["classification"]
            )

            # Determine download_status
            if classification["is_downloadable"]:
                download_status = "not_started"
            else:
                download_status = "reference_only"

            report_entry = {
                "url": url,
                "title": title,
                "agent": agent_key,
                "classification": classification["classification"],
                "is_downloadable": classification["is_downloadable"],
                "domain": domain,
                "download_priority": classification["download_priority"],
                "local_backup_path": backup_path,
                "download_status": download_status,
                "notes": notes,
            }
            web_resource_report.append(report_entry)

            # Check if URL already in registry
            norm_url = url.rstrip("/")
            if norm_url in url_index:
                idx = url_index[norm_url]
                # Update existing entry with agent-specific metadata
                entry = entries[idx]
                if download_status == "reference_only" and entry.get("download_status") == "not_started":
                    entry["download_status"] = "reference_only"
                if backup_path and not entry.get("local_backup_path"):
                    entry["local_backup_path"] = backup_path
                if domain != "general" and entry.get("domain") == "general":
                    entry["domain"] = domain
                # Add agent source note
                agent_note = f"[{agent_key} agent]"
                if agent_note not in entry.get("notes", ""):
                    entry["notes"] = f"{entry.get('notes', '')} {agent_note}".strip()
                updated_count += 1
            else:
                # Add new entry
                from build_online_resource_registry import generate_id, normalize_entry
                # Inline the normalize to avoid import issues
                import hashlib
                import re

                slug = urlparse(url).netloc.replace("www.", "").replace(".", "_")
                path_parts = [p for p in urlparse(url).path.strip("/").split("/") if p]
                if path_parts:
                    slug += "_" + "_".join(path_parts[:3])
                slug = re.sub(r"[^a-z0-9_]", "_", slug.lower())
                slug = re.sub(r"_+", "_", slug).strip("_")
                if len(slug) > 60:
                    slug = slug[:60]
                short_hash = hashlib.md5(url.encode()).hexdigest()[:6]
                entry_id = f"{slug}_{short_hash}"

                new_entry = {
                    "id": entry_id,
                    "url": url,
                    "name": title,
                    "type": "standard_portal" if classification["classification"] == "standard_portal"
                            else "tutorial" if "doc" in notes.lower() or "help" in url.lower()
                            else "tool",
                    "domain": domain,
                    "local_backup_path": backup_path,
                    "download_status": download_status,
                    "last_checked": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "relevance_score": classification["download_priority"],
                    "source_catalog": str(path),
                    "notes": f"{notes} [{agent_key} agent]",
                }
                new_entries.append(new_entry)
                url_index[norm_url] = len(entries) + len(new_entries) - 1

    # Add new entries to registry
    entries.extend(new_entries)

    # Rebuild summary
    from collections import Counter
    type_counts = Counter(e["type"] for e in entries)
    domain_counts = Counter(e["domain"] for e in entries)
    status_counts = Counter(e["download_status"] for e in entries)

    registry["entries"] = sorted(
        entries, key=lambda e: (-e.get("relevance_score", 0), e["domain"], e["name"])
    )
    registry["total_entries"] = len(entries)
    registry["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    registry["summary"] = {
        "by_type": dict(sorted(type_counts.items(), key=lambda x: -x[1])),
        "by_domain": dict(sorted(domain_counts.items(), key=lambda x: -x[1])),
        "by_download_status": dict(sorted(status_counts.items(), key=lambda x: -x[1])),
    }

    # Write updated registry
    with open(REGISTRY_PATH, "w") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)

    # Generate prioritized download list
    downloadable = [r for r in web_resource_report if r["is_downloadable"]]
    downloadable.sort(key=lambda x: -x["download_priority"])

    print(f"=== OrcaWave/OrcaFlex Web Resources → Registry ===")
    print(f"Total web resource URLs processed: {len(web_resource_report)}")
    print(f"Already in registry (updated): {updated_count}")
    print(f"New entries added: {len(new_entries)}")
    print(f"Registry total entries: {len(entries)}")
    print()

    print("--- URL Classifications ---")
    for r in web_resource_report:
        dl_marker = "📥" if r["is_downloadable"] else "📄"
        print(f"  {dl_marker} [{r['agent']}] {r['classification']}: {r['url']}")
        if r["local_backup_path"]:
            print(f"     → {r['local_backup_path']}")

    print()
    print("--- Prioritized Download List ---")
    for i, r in enumerate(downloadable, 1):
        print(f"  {i}. [P{r['download_priority']}] [{r['domain']}] {r['title']}")
        print(f"     URL: {r['url']}")
        print(f"     Target: {r['local_backup_path']}")

    # Return for testing
    return web_resource_report, new_entries, updated_count


if __name__ == "__main__":
    update_registry_with_web_resources()
