#!/usr/bin/env python3
"""Create cross-reference symlinks from domain directories to riser-eng-job literature.

Reads domain-index.yaml and creates a by-domain/ directory tree where each
engineering domain has relative symlinks back to the source project files.

GitHub Issue: #1413 (parent: WRK-1363)
"""

import os
import sys
import yaml
from pathlib import Path
from collections import defaultdict

RISER_ENG_JOB = Path(
    "/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job"
)
DOMAIN_INDEX = RISER_ENG_JOB / "domain-index.yaml"
BY_DOMAIN_DIR = RISER_ENG_JOB / "by-domain"

# Domains whose count equals total_files are catch-all mirrors — skip them
SKIP_CATCHALL = True


def load_index(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def create_symlinks(data: dict, dry_run: bool = False) -> dict:
    """Create relative symlinks for each domain.

    Returns stats: {domain: {created: int, skipped: int, broken_target: int}}
    """
    total_files = data.get("total_files", 0)
    domains = data.get("domains", {})
    stats = {}

    for domain_name, domain_info in sorted(domains.items()):
        count = domain_info.get("count", 0)
        files = domain_info.get("files", [])

        # Skip catch-all domains
        if SKIP_CATCHALL and count == total_files:
            print(f"SKIP  {domain_name} ({count} files = catch-all)")
            stats[domain_name] = {"created": 0, "skipped": count, "broken_target": 0, "catchall": True}
            continue

        domain_dir = BY_DOMAIN_DIR / domain_name
        created = 0
        skipped = 0
        broken_target = 0

        for abs_file_str in files:
            abs_file = Path(abs_file_str)

            # Verify source file exists
            if not abs_file.exists():
                broken_target += 1
                continue

            # Compute path relative to riser-eng-job root
            try:
                rel_from_root = abs_file.relative_to(RISER_ENG_JOB)
            except ValueError:
                # File not under riser-eng-job — skip
                skipped += 1
                continue

            # Symlink location: by-domain/<domain>/<rel_from_root>
            link_path = domain_dir / rel_from_root

            if link_path.exists() or link_path.is_symlink():
                skipped += 1
                continue

            # Compute relative target from link's parent dir to the actual file
            # os.path.relpath handles the ../ traversal
            rel_target = os.path.relpath(abs_file, link_path.parent)

            if dry_run:
                print(f"  LINK {link_path} -> {rel_target}")
            else:
                link_path.parent.mkdir(parents=True, exist_ok=True)
                os.symlink(rel_target, link_path)

            created += 1

        stats[domain_name] = {
            "created": created,
            "skipped": skipped,
            "broken_target": broken_target,
            "catchall": False,
        }
        status = "DRY-RUN" if dry_run else "OK"
        print(f"{status}  {domain_name}: {created} symlinks created, {skipped} skipped, {broken_target} broken targets")

    return stats


def write_manifest(stats: dict, output_path: Path):
    """Write a YAML manifest of created symlinks."""
    manifest = {
        "description": "Cross-reference symlinks from domain dirs to riser-eng-job literature",
        "issue": "#1413",
        "parent": "WRK-1363",
        "by_domain_root": str(BY_DOMAIN_DIR),
        "domains": {},
    }

    total_created = 0
    total_skipped = 0
    total_broken = 0

    for domain, info in sorted(stats.items()):
        manifest["domains"][domain] = info
        if not info.get("catchall", False):
            total_created += info["created"]
            total_skipped += info["skipped"]
            total_broken += info["broken_target"]

    manifest["totals"] = {
        "domains_linked": sum(1 for s in stats.values() if s["created"] > 0),
        "domains_skipped_catchall": sum(1 for s in stats.values() if s.get("catchall")),
        "symlinks_created": total_created,
        "files_skipped": total_skipped,
        "broken_targets": total_broken,
    }

    with open(output_path, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, width=120)

    print(f"\nManifest written to {output_path}")
    print(f"  Domains linked: {manifest['totals']['domains_linked']}")
    print(f"  Total symlinks: {manifest['totals']['symlinks_created']}")
    print(f"  Broken targets: {manifest['totals']['broken_targets']}")


def main():
    dry_run = "--dry-run" in sys.argv

    if not DOMAIN_INDEX.exists():
        print(f"ERROR: Domain index not found: {DOMAIN_INDEX}", file=sys.stderr)
        sys.exit(1)

    if not RISER_ENG_JOB.exists():
        print(f"ERROR: riser-eng-job dir not found: {RISER_ENG_JOB}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading domain index: {DOMAIN_INDEX}")
    data = load_index(DOMAIN_INDEX)
    print(f"Total files in index: {data.get('total_files', '?')}")
    print(f"Domains: {len(data.get('domains', {}))}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}\n")

    stats = create_symlinks(data, dry_run=dry_run)

    manifest_path = RISER_ENG_JOB / "by-domain" / "MANIFEST.yaml"
    if not dry_run:
        write_manifest(stats, manifest_path)
    else:
        print("\nDry-run complete. No files created.")


if __name__ == "__main__":
    main()
