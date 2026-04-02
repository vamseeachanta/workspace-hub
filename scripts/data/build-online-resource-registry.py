#!/usr/bin/env python3
"""
ABOUTME: Builds a unified online resource registry by merging 7 catalog files.
Deduplicates by URL, normalizes to a unified schema, writes YAML output.
Usage: uv run --no-project python scripts/data/build-online-resource-registry.py
"""

import hashlib
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import yaml

HUB_ROOT = Path(__file__).resolve().parents[2]

# --- Source catalog paths ---
CATALOG_PATHS = {
    "online_resources": HUB_ROOT / ".planning/archive/online-resources/catalog.yaml",
    "engineering_catalog": HUB_ROOT / ".planning/archive/catalog/open-source-engineering-catalog.yaml",
    "public_og": HUB_ROOT / "data/document-index/public-og-data-sources.yaml",
    "orcaflex_web": HUB_ROOT / "digitalmodel/.claude/agents/orcaflex/context/external/web/web_resources.yaml",
    "aqwa_web": HUB_ROOT / "digitalmodel/.claude/agents/aqwa/context/external/web/web_resources.yaml",
    "web_test_module": HUB_ROOT / "digitalmodel/.claude/agents/web-test-module/context/external/web/web_resources.yaml",
    "naval_architecture": HUB_ROOT / "knowledge/seeds/naval-architecture-resources.yaml",
}

OUTPUT_PATH = HUB_ROOT / "data/document-index/online-resource-registry.yaml"

# --- Valid enum values ---
VALID_TYPES = {
    "github_repo", "paper", "standard_portal", "data_api", "tutorial",
    "tool", "library", "reference_page", "dataset", "professional_body",
    "course_material",
}
VALID_DOMAINS = {
    "orcawave", "orcaflex", "structural", "hydrodynamics", "pipeline",
    "naval_architecture", "fatigue", "subsea", "geotechnical", "electrical",
    "general", "marine", "cfd", "cad", "materials", "data_science",
    "oil_and_gas", "visualization", "sustainability", "cathodic_protection",
    "installation", "regulatory", "energy_economics",
}
VALID_STATUSES = {
    "not_started", "downloaded", "indexed", "extracted", "reference_only",
}

# --- Domain keyword mapping ---
DOMAIN_KEYWORDS = {
    "orcaflex": ["orcaflex", "orcina"],
    "orcawave": ["orcawave"],
    "hydrodynamics": [
        "hydrodynamic", "bem", "wave", "diffraction", "radiation",
        "capytaine", "hams", "wec-sim", "bemio", "oceanwave",
        "bemrosetta", "wavespectra", "marine-weather", "tide",
        "ndbc", "copernicus", "open-meteo",
    ],
    "structural": [
        "structural", "fea", "fem", "fenics", "calculix", "code.aster",
        "opensees", "kratos", "moose", "sfepy", "getfem",
    ],
    "pipeline": [
        "pipeline", "flow.assurance", "thermopack", "thermo", "fluids",
        "dwsim",
    ],
    "naval_architecture": [
        "naval.architecture", "ship", "sname", "vessel", "hull",
        "stability", "classnk", "bureau.veritas", "lloyd", "rina",
        "solas", "imo",
    ],
    "marine": [
        "marine", "offshore", "mooring", "moordyn", "moorpy", "openfast",
        "raft", "qblade", "map++", "floating",
    ],
    "cfd": ["cfd", "openfoam", "su2", "palabos", "pyfr", "nektar", "basilisk"],
    "oil_and_gas": [
        "oil", "gas", "petroleum", "bsee", "boem", "opec", "baker.hughes",
        "rig.count", "opm", "resinsight", "mrst",
    ],
    "cad": ["cad", "geometry", "opencascade", "freecad", "cadquery", "gmsh", "salome", "ngsolve"],
    "materials": ["material", "corrosion", "twi", "ampp", "fatigue", "weld"],
    "fatigue": ["fatigue"],
    "subsea": ["subsea"],
    "data_science": ["numpy", "scipy", "pandas", "polars", "xarray", "dask", "pyarrow", "vaex"],
    "visualization": ["pyvista", "paraview", "visualization"],
    "sustainability": ["carbon", "climate", "esg", "emission", "ipcc", "nsidc"],
    "regulatory": ["regulatory", "imo", "gisis"],
    "general": [],
}


def normalize_url(url: str) -> str:
    """Normalize URL for dedup comparison."""
    url = url.strip().rstrip("/")
    # Remove trailing fragments
    url = url.split("#")[0]
    return url


def generate_id(url: str, name: str = "") -> str:
    """Generate a deterministic ID from the URL."""
    parsed = urlparse(url)
    # Use domain + path for readable slug
    slug = parsed.netloc.replace("www.", "").replace(".", "_")
    path_parts = [p for p in parsed.path.strip("/").split("/") if p]
    if path_parts:
        slug += "_" + "_".join(path_parts[:3])
    # Clean up slug
    slug = re.sub(r"[^a-z0-9_]", "_", slug.lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    # Truncate and add hash suffix for uniqueness
    if len(slug) > 60:
        slug = slug[:60]
    short_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{slug}_{short_hash}"


def infer_type(url: str, entry: dict) -> str:
    """Infer resource type from URL and metadata."""
    url_lower = url.lower()

    if "github.com" in url_lower or "gitlab.com" in url_lower:
        # Check if it's a project page vs repo
        parsed = urlparse(url_lower)
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(parts) >= 2 and not any(
            x in parts for x in ["blob", "tree", "issues", "wiki"]
        ):
            return "github_repo"
        return "github_repo"
    if "arxiv.org" in url_lower:
        return "paper"
    if any(x in url_lower for x in ["onepetro.org", "asme", "isope", "doi.org"]):
        return "paper"
    if any(x in url_lower for x in [".pdf", "archive.org/details"]):
        return "paper"
    if any(
        x in url_lower
        for x in ["dnv.com/rules", "api.org/products", "iacs.org", "standards"]
    ):
        return "standard_portal"
    if any(x in url_lower for x in ["api/", "data.", "opendata", "/data/"]):
        return "data_api"
    if any(x in url_lower for x in ["readthedocs", "docs.", "webhelp", "/docs/"]):
        return "tutorial"
    if any(x in url_lower for x in ["pypi.org", "pip"]):
        return "library"
    if any(x in url_lower for x in ["ocw.mit.edu", "course", "training"]):
        return "course_material"
    if any(x in url_lower for x in ["sname.org", "rina.org", "iogp.org", "imarest"]):
        return "professional_body"

    # Fallback based on entry metadata
    category = entry.get("category", "")
    if "standard" in category:
        return "standard_portal"
    if "data" in category or "api" in category:
        return "data_api"
    if "tool" in category:
        return "tool"

    return "tool"


def infer_domain(url: str, entry: dict) -> str:
    """Infer domain from URL, name, and metadata."""
    text = " ".join([
        url.lower(),
        entry.get("name", "").lower(),
        entry.get("notes", "").lower(),
        entry.get("category", "").lower(),
        entry.get("subcategory", "").lower(),
        entry.get("related_module", "").lower(),
        str(entry.get("capabilities", [])).lower(),
        entry.get("relevance_to_ace", "").lower(),
        entry.get("domain_hint", "").lower(),
    ])

    # Score each domain by keyword matches
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if not keywords:
            continue
        score = sum(1 for kw in keywords if re.search(kw, text))
        if score > 0:
            scores[domain] = score

    if scores:
        return max(scores, key=scores.get)
    return "general"


def normalize_entry(entry: dict) -> dict:
    """Normalize a raw entry to the unified schema."""
    url = entry.get("url", "")
    name = entry.get("name", entry.get("title", ""))

    return {
        "id": entry.get("id") or generate_id(url, name),
        "url": url,
        "name": name,
        "type": entry.get("type_override") or infer_type(url, entry),
        "domain": entry.get("domain_override") or entry.get("domain") or infer_domain(url, entry),
        "local_backup_path": entry.get("local_backup_path", ""),
        "download_status": entry.get("download_status", "not_started"),
        "last_checked": entry.get("last_checked", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "relevance_score": entry.get("relevance_score", 3),
        "source_catalog": entry.get("source_catalog", ""),
        "notes": entry.get("notes", ""),
    }


def deduplicate_by_url(entries: list) -> list:
    """Deduplicate entries by normalized URL, keeping highest relevance_score."""
    seen = {}
    for entry in entries:
        key = normalize_url(entry.get("url", ""))
        if not key:
            continue
        existing = seen.get(key)
        if existing is None:
            seen[key] = entry
        else:
            # Keep the one with higher relevance_score, merge notes
            if entry.get("relevance_score", 0) > existing.get("relevance_score", 0):
                old_notes = existing.get("notes", "")
                old_source = existing.get("source_catalog", "")
                seen[key] = entry
                if old_notes and old_notes not in entry.get("notes", ""):
                    seen[key]["notes"] = f"{entry.get('notes', '')} | {old_notes}".strip(" | ")
                if old_source and old_source not in entry.get("source_catalog", ""):
                    seen[key]["source_catalog"] = f"{entry.get('source_catalog', '')}; {old_source}".strip("; ")
            else:
                # Merge source_catalog info into existing
                new_source = entry.get("source_catalog", "")
                if new_source and new_source not in existing.get("source_catalog", ""):
                    existing["source_catalog"] = f"{existing.get('source_catalog', '')}; {new_source}".strip("; ")
    return list(seen.values())


# --- Parsers for each catalog format ---


def safe_yaml_load(path: Path) -> dict:
    """Load YAML, fixing common unquoted-colon errors if needed."""
    import re as _re
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except yaml.scanner.ScannerError as e:
        # Try fixing unquoted colons in values
        print(f"  WARNING: YAML error in {path.name}, attempting auto-fix...")
        with open(path) as f:
            text = f.read()
        # Quote any line where value contains an unquoted colon
        # Pattern: key: value_with_unquoted_colon
        lines = text.split("\n")
        fixed = []
        for line in lines:
            stripped = line.lstrip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("-"):
                # Check if this is a key: value line with extra colons in value
                m = _re.match(r"^(\s+\w[\w_]*:\s+)(.*:.*)$", line)
                if m and not m.group(2).startswith(("'", '"', "|", ">", "[", "{")):
                    val = m.group(2)
                    # Count colons in value portion
                    if ":" in val and not val.startswith("http"):
                        line = f'{m.group(1)}"{val}"'
            fixed.append(line)
        return yaml.safe_load("\n".join(fixed))


def parse_online_resources_catalog(path: Path) -> list:
    """Parse .planning/archive/online-resources/catalog.yaml."""
    data = safe_yaml_load(path)
    entries = []
    for item in data.get("resources", []):
        entry = {
            "url": item.get("url", ""),
            "name": item.get("name", ""),
            "id": item.get("id", ""),
            "notes": item.get("notes", ""),
            "relevance_score": item.get("relevance_score", 3),
            "category": item.get("category", ""),
            "subcategory": item.get("subcategory", ""),
            "related_module": item.get("related_module", ""),
            "source_catalog": str(path),
        }
        if entry["url"]:
            entries.append(entry)
        # Also add secondary URLs (github, paper, etc.)
        for extra_key in ["github", "paper", "huggingface"]:
            extra_url = item.get(extra_key, "")
            if extra_url and extra_url != entry["url"]:
                extra_entry = dict(entry)
                extra_entry["url"] = extra_url
                extra_entry["id"] = ""
                extra_entry["name"] = f"{entry['name']} ({extra_key})"
                entries.append(extra_entry)
    return entries


def parse_engineering_catalog(path: Path) -> list:
    """Parse .planning/archive/catalog/open-source-engineering-catalog.yaml."""
    with open(path) as f:
        data = yaml.safe_load(f)
    entries = []
    for domain_key, domain_data in data.get("domains", {}).items():
        for lib in domain_data.get("libraries", []):
            # Primary URL (usually GitHub)
            entry = {
                "url": lib.get("url", ""),
                "name": lib.get("name", ""),
                "notes": lib.get("integration_notes", ""),
                "relevance_score": 4,
                "domain_hint": domain_key,
                "capabilities": lib.get("capabilities", []),
                "relevance_to_ace": lib.get("relevance_to_ace", ""),
                "source_catalog": str(path),
            }
            if entry["url"]:
                entries.append(entry)
            # Project URL (docs site)
            project_url = lib.get("project_url", "")
            if project_url and project_url != entry["url"]:
                doc_entry = dict(entry)
                doc_entry["url"] = project_url
                doc_entry["name"] = f"{lib['name']} (docs)"
                entries.append(doc_entry)
    return entries


def parse_public_og_sources(path: Path) -> list:
    """Parse data/document-index/public-og-data-sources.yaml."""
    with open(path) as f:
        data = yaml.safe_load(f)
    entries = []
    categories = data.get("categories", {})

    # already_ingested don't have URLs, skip
    for cat_key in ["known_not_ingested", "newly_discovered"]:
        for item in categories.get(cat_key, []):
            url = item.get("url", "")
            if not url:
                continue
            priority_map = {"high": 5, "medium": 3, "low": 1}
            entries.append({
                "url": url,
                "name": item.get("name", ""),
                "notes": item.get("rationale", ""),
                "relevance_score": priority_map.get(item.get("priority", "medium"), 3),
                "category": "open_data_api",
                "source_catalog": str(path),
            })
    return entries


def parse_web_resources(path: Path) -> list:
    """Parse agent web_resources.yaml files (orcaflex/aqwa/web-test-module)."""
    with open(path) as f:
        data = yaml.safe_load(f)
    entries = []
    for link in data.get("user_added_links", []):
        entries.append({
            "url": link.get("url", ""),
            "name": link.get("title", ""),
            "notes": link.get("notes", ""),
            "relevance_score": 4,
            "source_catalog": str(path),
        })
    return entries


def parse_naval_architecture(path: Path) -> list:
    """Parse knowledge/seeds/naval-architecture-resources.yaml."""
    with open(path) as f:
        data = yaml.safe_load(f)
    entries = []

    # Sections with source_url
    for section_key in ["textbooks", "hydrostatics_stability", "additional_resources", "regulatory"]:
        for item in data.get(section_key, []):
            url = item.get("source_url", "")
            if not url:
                continue
            entries.append({
                "url": url,
                "name": item.get("title", ""),
                "notes": item.get("notes", ""),
                "relevance_score": 4,
                "domain_override": "naval_architecture",
                "local_backup_path": item.get("local_path", ""),
                "download_status": "downloaded" if item.get("local_path") else "not_started",
                "source_catalog": str(path),
            })

    # Sections with url field
    for section_key in ["online_portals", "classification_portals", "pending_manual"]:
        for item in data.get(section_key, []):
            url = item.get("url", "")
            if not url:
                continue
            entries.append({
                "url": url,
                "name": item.get("title", ""),
                "notes": item.get("notes", ""),
                "relevance_score": 4,
                "domain_override": "naval_architecture",
                "source_catalog": str(path),
            })

    return entries


def write_registry(entries: list, output_path: Path) -> None:
    """Write the unified registry YAML."""
    # Build summary
    type_counts = Counter(e["type"] for e in entries)
    domain_counts = Counter(e["domain"] for e in entries)
    status_counts = Counter(e["download_status"] for e in entries)

    registry = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "total_entries": len(entries),
        "summary": {
            "by_type": dict(sorted(type_counts.items(), key=lambda x: -x[1])),
            "by_domain": dict(sorted(domain_counts.items(), key=lambda x: -x[1])),
            "by_download_status": dict(sorted(status_counts.items(), key=lambda x: -x[1])),
        },
        "entries": sorted(entries, key=lambda e: (-e.get("relevance_score", 0), e["domain"], e["name"])),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)


def generate_report(entries: list) -> str:
    """Generate a human-readable summary report."""
    type_counts = Counter(e["type"] for e in entries)
    domain_counts = Counter(e["domain"] for e in entries)
    status_counts = Counter(e["download_status"] for e in entries)

    lines = [
        f"=== Unified Online Resource Registry ===",
        f"Total entries: {len(entries)}",
        f"",
        f"--- By Type ---",
    ]
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {t}: {c}")
    lines.append("")
    lines.append("--- By Domain ---")
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {d}: {c}")
    lines.append("")
    lines.append("--- By Download Status ---")
    for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {s}: {c}")

    # Top 10 undownloaded
    undownloaded = [e for e in entries if e["download_status"] == "not_started"]
    undownloaded.sort(key=lambda e: -e.get("relevance_score", 0))
    if undownloaded:
        lines.append("")
        lines.append("--- Top 10 Undownloaded (by relevance) ---")
        for e in undownloaded[:10]:
            lines.append(f"  [{e['relevance_score']}] {e['name']}: {e['url']}")

    return "\n".join(lines)


def main():
    """Main entry point — read all catalogs, merge, dedup, write."""
    all_entries = []

    parsers = {
        "online_resources": parse_online_resources_catalog,
        "engineering_catalog": parse_engineering_catalog,
        "public_og": parse_public_og_sources,
        "orcaflex_web": parse_web_resources,
        "aqwa_web": parse_web_resources,
        "web_test_module": parse_web_resources,
        "naval_architecture": parse_naval_architecture,
    }

    for catalog_key, parser in parsers.items():
        path = CATALOG_PATHS[catalog_key]
        if not path.exists():
            print(f"WARNING: {catalog_key} not found at {path}", file=sys.stderr)
            continue
        entries = parser(path)
        print(f"  Parsed {catalog_key}: {len(entries)} entries from {path.name}")
        all_entries.extend(entries)

    print(f"\nTotal raw entries: {len(all_entries)}")

    # Normalize all entries
    normalized = [normalize_entry(e) for e in all_entries]

    # Deduplicate
    deduped = deduplicate_by_url(normalized)
    print(f"After deduplication: {len(deduped)} entries")

    # Write registry
    write_registry(deduped, OUTPUT_PATH)
    print(f"\nRegistry written to: {OUTPUT_PATH}")

    # Generate report
    report = generate_report(deduped)
    print(f"\n{report}")

    return deduped, report


if __name__ == "__main__":
    main()
