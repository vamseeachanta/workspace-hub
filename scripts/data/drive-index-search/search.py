#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import queue
import sys
import threading
import time

from adapters import ADAPTER_TYPES
from adapters.base import AdapterError, tokenize
from merge import ranked_merge
from registry import RegistryError, load_registry
from staleness import compute_index_status, stale_warnings

import metrics


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search registered drive indexes.")
    parser.add_argument("query")
    parser.add_argument("--domain")
    parser.add_argument("--drive")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--registry", default="config/drive-index-registry.yml")
    parser.add_argument("--index", action="append", default=[])
    parser.add_argument("--timeout-per-index", type=float, default=60.0)
    parser.add_argument("--session", default=None)  # #3340 metrics join key
    parser.add_argument("--caller", default="manual")  # #3340 integration-point attribution
    args = parser.parse_args(argv)
    t_start = time.monotonic()

    try:
        registry = load_registry(args.registry)
    except RegistryError as exc:
        print(f"registry error: {exc}", file=sys.stderr)
        _emit(args.query, [], [], [], args.as_json)
        return 2

    tokens = tokenize(args.query)
    selected = _select_indexes(registry.indexes, args.drive, args.domain, set(args.index))
    index_status = compute_index_status(selected, registry.defaults)
    for warning in stale_warnings(index_status):
        print(warning, file=sys.stderr)
    if not selected:
        _emit(args.query, [], [], [], args.as_json, index_status)
        return 0

    all_results = []
    gaps = []
    reachable_count = 0
    for index in selected:
        adapter = ADAPTER_TYPES[index.adapter](index)
        status, payload = _run_with_timeout(index, adapter, tokens, args.limit, args.timeout_per_index)
        if status == "ok":
            reachable_count += 1
            all_results.extend(payload)
        else:
            gap = {"id": index.id, "path": str(index.path), "reason": payload}
            gaps.append(gap)
            print(f"warning: index {index.id} {payload} at {index.path} -- skipping", file=sys.stderr)

    for result in all_results:
        result.meta.setdefault("query_tokens", tokens)
    merged = ranked_merge(all_results, registry.alias_map, args.limit)
    envelope = _emit(args.query, [index.id for index in selected], gaps, merged, args.as_json, index_status)
    exit_code = 2 if (selected and reachable_count == 0) else 0
    metrics.emit_invocation(args, envelope, exit_code, t_start)  # fail-open (#3340)
    return exit_code


def _select_indexes(indexes, drive: str | None, domain: str | None, index_ids: set[str]):
    selected = []
    for index in indexes:
        if index_ids and index.id not in index_ids:
            continue
        if drive and drive not in index.coverage.get("drives", []):
            continue
        if domain and index.domains is not None and domain not in index.domains:
            continue
        selected.append(index)
    return selected


def _run_with_timeout(index, adapter, tokens, limit, timeout):
    output = queue.Queue(maxsize=1)

    def worker():
        try:
            if not os.path.exists(index.path):
                output.put(("gap", "unreachable"))
                return
            output.put(("ok", adapter.search(tokens, limit)))
        except AdapterError as exc:
            output.put(("gap", str(exc)))
        except Exception as exc:
            output.put(("gap", f"unexpected error: {exc}"))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        adapter.interrupt()
        thread.join(0.2)
        return "gap", "timeout"
    return output.get_nowait()


def _emit(query: str, indexes_queried: list[str], gaps: list[dict], results, as_json: bool, index_status: list[dict] | None = None) -> dict:
    payload = {
        "query": query,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "indexes_queried": indexes_queried,
        "index_status": index_status or [],
        "coverage_gaps": gaps,
        "results": [result.as_dict() for result in results],
    }
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return payload
    for result in payload["results"]:
        print(f"{result['score']:.3f}\t{result['source_index']}\t{result['canonical_path']}")
    for gap in gaps:
        print(f"gap\t{gap['id']}\t{gap['reason']}", file=sys.stderr)
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
