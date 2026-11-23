# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "requests"]
# ///
"""Manage a YAML-based URL fetch queue with domain-aware throttling and resume."""

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import yaml

from scripts.data.doc_intelligence.queue import (
    get_pending,
    load_queue,
    mark_completed,
    mark_failed,
    save_queue,
)


def create_queue(urls: list[str], path: Path) -> None:
    """Create a YAML queue file from a list of URLs.

    Deduplicates URLs. Writes atomically via tmp + os.replace.
    """
    path = Path(path)
    seen: set[str] = set()
    documents: list[dict] = []
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        parsed = urlparse(url)
        domain = parsed.hostname or ""
        documents.append({"url": url, "domain": domain, "status": "pending"})

    queue: dict = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "documents": documents,
    }
    save_queue(queue, path)


def get_domain_stats(queue: dict) -> dict[str, dict[str, int]]:
    """Return per-domain counts of {pending, completed, failed}."""
    stats: dict[str, dict[str, int]] = {}
    for doc in queue.get("documents", []):
        domain = doc.get("domain", "")
        status = doc.get("status", "pending")
        if domain not in stats:
            stats[domain] = {"pending": 0, "completed": 0, "failed": 0}
        if status in stats[domain]:
            stats[domain][status] += 1
    return stats


def _output_path_for(url: str, output_dir: Path) -> Path:
    """Derive a stable output file path from the URL."""
    parsed = urlparse(url)
    domain = parsed.hostname or "unknown"
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    path_part = parsed.path.rstrip("/")
    ext = Path(path_part).suffix if Path(path_part).suffix else ".html"
    return output_dir / domain / f"{url_hash}{ext}"


def process_queue(
    queue_path: Path,
    output_dir: Path,
    batch_size: int = 10,
    rate_limit: float = 1.0,
    fetcher=None,
) -> None:
    """Process pending items in the queue.

    For each pending URL: fetch, save content, mark completed/failed.
    Saves queue state after each batch. Resume-safe (skips completed items).

    Args:
        queue_path: Path to the YAML queue file.
        output_dir: Directory to save fetched content.
        batch_size: Number of items processed per batch before saving queue.
        rate_limit: Seconds between requests to the same domain (passed to
            UrlFetcher when no fetcher is provided).
        fetcher: Optional UrlFetcher instance. If None, a default is created.
    """
    queue_path = Path(queue_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if fetcher is None:
        from scripts.data.doc_intelligence.fetcher import UrlFetcher
        fetcher = UrlFetcher(rate_limit=rate_limit)

    queue = load_queue(queue_path)
    pending = get_pending(queue)

    batch_count = 0
    for doc in pending:
        url = doc["url"]
        try:
            result = fetcher.fetch(url)
            if result is None:
                mark_failed(doc, "Blocked by robots.txt")
            else:
                dest = _output_path_for(url, output_dir)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(result.content_bytes)
                doc["status"] = "completed"
                doc["output_path"] = str(dest)
                doc["fetched_at"] = datetime.now(timezone.utc).isoformat()
        except Exception as exc:
            mark_failed(doc, str(exc))

        batch_count += 1
        if batch_count % batch_size == 0:
            save_queue(queue, queue_path)

    # Final save to persist any remaining partial batch
    save_queue(queue, queue_path)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manage a YAML URL fetch queue."
    )
    parser.add_argument("--create-from", metavar="URL_LIST_FILE",
                        help="Read URLs from file (one per line) and create queue")
    parser.add_argument("--process", metavar="QUEUE_YAML",
                        help="Process pending items in the queue")
    parser.add_argument("--output-dir", metavar="DIR", default=".",
                        help="Directory to save fetched content (default: .)")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Items per batch before queue is saved (default: 10)")
    parser.add_argument("--stats", metavar="QUEUE_YAML",
                        help="Print per-domain stats for a queue file")
    parser.add_argument("--rate-limit", type=float, default=1.0,
                        help="Seconds between requests per domain (default: 1.0)")

    args = parser.parse_args()

    if args.create_from:
        url_file = Path(args.create_from)
        urls = [
            line.strip()
            for line in url_file.read_text().splitlines()
            if line.strip()
        ]
        queue_path = Path(args.create_from).with_suffix(".queue.yaml")
        create_queue(urls, queue_path)
        print(f"Queue created: {queue_path} ({len(urls)} URLs)")

    elif args.process:
        process_queue(
            queue_path=Path(args.process),
            output_dir=Path(args.output_dir),
            batch_size=args.batch_size,
            rate_limit=args.rate_limit,
        )
        queue = load_queue(Path(args.process))
        from scripts.data.doc_intelligence.queue import get_stats
        stats = get_stats(queue)
        print(f"Done: {stats}")

    elif args.stats:
        queue = load_queue(Path(args.stats))
        stats = get_domain_stats(queue)
        print(yaml.dump(stats, default_flow_style=False))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
