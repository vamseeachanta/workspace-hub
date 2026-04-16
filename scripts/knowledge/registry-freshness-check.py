#!/usr/bin/env python3
"""registry-freshness-check.py — URL validation for the online resource registry.

Validates URLs in online-resource-registry.yaml via HTTP HEAD requests, flags dead
links, and produces a freshness report. Designed for periodic (weekly) execution.

Usage:
    uv run scripts/knowledge/registry-freshness-check.py [--timeout SEC] [--json] [--limit N]

Issue: #1614 — Registry freshness checker — periodic URL validation and dead link detection
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Use PyYAML if available, fall back to basic parsing
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "data" / "document-index" / "online-resource-registry.yaml"


def load_registry() -> List[Dict[str, Any]]:
    """Load entries from online-resource-registry.yaml."""
    if not REGISTRY_PATH.exists():
        print(f"Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)

    text = REGISTRY_PATH.read_text(encoding="utf-8")

    if HAS_YAML:
        data = yaml.safe_load(text)
        return data.get("entries", [])

    # Minimal fallback parser for YAML list-of-dicts
    entries = []
    current = {}
    for line in text.split("\n"):
        if line.startswith("- "):
            if current:
                entries.append(current)
            current = {}
            key, _, val = line[2:].partition(":")
            current[key.strip()] = val.strip()
        elif line.startswith("  ") and ":" in line and current is not None:
            key, _, val = line.strip().partition(":")
            current[key.strip()] = val.strip()
    if current:
        entries.append(current)
    return entries


def check_url(entry: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
    """Check a single URL via HEAD request. Returns result dict."""
    url = entry.get("url", "")
    entry_id = entry.get("id", "unknown")
    name = entry.get("name", entry_id)

    if not url:
        return {
            "id": entry_id, "name": name, "url": url,
            "status": "error", "code": None, "reason": "no URL",
        }

    # Create an SSL context that doesn't verify (some engineering sites have bad certs)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(url, method="HEAD", headers={
            "User-Agent": "workspace-hub-freshness-check/1.0",
        })
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return {
                "id": entry_id, "name": name, "url": url,
                "status": "alive", "code": resp.status, "reason": None,
            }
    except urllib.error.HTTPError as e:
        # Some servers reject HEAD — try GET with range header
        if e.code in (405, 403):
            try:
                req2 = urllib.request.Request(url, method="GET", headers={
                    "User-Agent": "workspace-hub-freshness-check/1.0",
                    "Range": "bytes=0-0",
                })
                with urllib.request.urlopen(req2, timeout=timeout, context=ctx) as resp:
                    return {
                        "id": entry_id, "name": name, "url": url,
                        "status": "alive", "code": resp.status, "reason": None,
                    }
            except Exception:
                pass
        return {
            "id": entry_id, "name": name, "url": url,
            "status": "dead" if e.code in (404, 410, 451) else "error",
            "code": e.code, "reason": str(e.reason),
        }
    except urllib.error.URLError as e:
        return {
            "id": entry_id, "name": name, "url": url,
            "status": "unreachable", "code": None, "reason": str(e.reason)[:100],
        }
    except Exception as e:
        return {
            "id": entry_id, "name": name, "url": url,
            "status": "error", "code": None, "reason": str(e)[:100],
        }


def run_freshness_check(timeout: int = 10, limit: int = 0,
                        json_output: bool = False, workers: int = 8) -> int:
    """Run freshness checks on all registry URLs."""
    entries = load_registry()

    if limit > 0:
        entries = entries[:limit]

    results: List[Dict[str, Any]] = []

    if not json_output:
        print(f"Checking {len(entries)} URLs (timeout={timeout}s, workers={workers})...")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(check_url, e, timeout): e for e in entries}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            if not json_output and result["status"] != "alive":
                symbol = {"dead": "✗", "unreachable": "⚠", "error": "?"}.get(result["status"], "?")
                print(f"  {symbol} [{result['code'] or '---'}] {result['id']}: {result['reason']}")

    # Categorize results
    alive = [r for r in results if r["status"] == "alive"]
    dead = [r for r in results if r["status"] == "dead"]
    unreachable = [r for r in results if r["status"] == "unreachable"]
    errors = [r for r in results if r["status"] in ("error",)]

    if json_output:
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_checked": len(results),
            "summary": {
                "alive": len(alive),
                "dead": len(dead),
                "unreachable": len(unreachable),
                "errors": len(errors),
            },
            "dead_links": dead,
            "unreachable": unreachable,
            "errors": errors,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'=' * 60}")
        print(f" Registry Freshness Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'=' * 60}")
        print(f"  Total checked: {len(results)}")
        print(f"  ✓ Alive:       {len(alive)}")
        print(f"  ✗ Dead (404):  {len(dead)}")
        print(f"  ⚠ Unreachable: {len(unreachable)}")
        print(f"  ? Errors:      {len(errors)}")
        print(f"{'=' * 60}")

        if dead:
            print(f"\nDead links ({len(dead)}):")
            for r in dead:
                print(f"  ✗ {r['id']}: {r['url']}")

        if unreachable:
            print(f"\nUnreachable ({len(unreachable)}):")
            for r in unreachable[:10]:
                print(f"  ⚠ {r['id']}: {r['reason']}")
            if len(unreachable) > 10:
                print(f"  ... and {len(unreachable) - 10} more")

    return 1 if dead else 0


def main():
    parser = argparse.ArgumentParser(
        description="URL freshness checker for online-resource-registry.yaml (#1614)",
    )
    parser.add_argument("--timeout", "-t", type=int, default=10,
                        help="Request timeout in seconds (default: 10)")
    parser.add_argument("--limit", "-l", type=int, default=0,
                        help="Limit to first N entries (default: 0=all)")
    parser.add_argument("--workers", "-w", type=int, default=8,
                        help="Concurrent workers (default: 8)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output results as JSON")
    args = parser.parse_args()

    sys.exit(run_freshness_check(
        timeout=args.timeout,
        limit=args.limit,
        json_output=args.json,
        workers=args.workers,
    ))


if __name__ == "__main__":
    main()
