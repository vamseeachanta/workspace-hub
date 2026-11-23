#!/usr/bin/env python3
"""Turn extractor JSONL into reviewable text digests, split at session boundaries (#3973).

    python -I build_digests.py --out DIGEST_DIR [--limit 330000] win1.jsonl ws014.jsonl

Writes <machine>-<provider>[-exec]-NN.txt, each under --limit characters, for main
sessions only (subagent logs are counted by the extractor but carry no operator prompts).
Each digest is meant to be inlined into one read-only reviewer prompt; see README.md.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
from pathlib import Path


def _group(r: dict) -> str:
    g = f"{r['machine']}-{r['provider']}"
    return g + ("-exec" if "exec" in (r.get("originator") or "") else "")


def _section(r: dict) -> str:
    head = (f"\n=== SESSION {os.path.basename(r['file'])[:60]} | {r['machine']} {r['provider']} | "
            f"{r.get('start')} -> {r.get('end')} | cwd={r.get('cwd')} | {r.get('size_mb')}MB | "
            f"tools={sum(r.get('tools', {}).values())} errs={r.get('tool_errors', 0)} "
            f"interrupts={r.get('interrupts', 0)} denials={r.get('denials', 0)} compactions={r.get('compactions', 0)}\n")
    body = [f"[U {(ts or '')[:16]}] {p}\n" for ts, p in r.get("prompts", [])]
    body += [f"[A-final {(ts or '')[:16]}] {p}\n" for ts, p in r.get("outcomes", [])]
    body += [f"[ERR] {e.strip()[:200]}\n" for e in r.get("error_samples", [])[:5]]
    return head + "".join(body)


def build(rows, out_dir, limit: int = 330_000) -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    groups = collections.defaultdict(list)
    for r in rows:
        if r.get("subagent") or "fatal" in r or not (r.get("prompts") or r.get("outcomes")):
            continue
        groups[_group(r)].append(r)
    written = []
    for g, rs in sorted(groups.items()):
        rs.sort(key=lambda r: r.get("start") or "")
        buf, n = "", 0
        for r in rs:
            sec = _section(r)
            if len(sec) > limit:
                sec = sec[:limit] + "\n[...session truncated...]\n"
            if buf and len(buf) + len(sec) > limit:
                n += 1
                written.append(out_dir / f"{g}-{n:02d}.txt")
                written[-1].write_text(buf, encoding="utf-8")
                buf = ""
            buf += sec
        if buf:
            n += 1
            written.append(out_dir / f"{g}-{n:02d}.txt")
            written[-1].write_text(buf, encoding="utf-8")
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=330_000)
    ap.add_argument("inputs", nargs="+")
    a = ap.parse_args(argv)
    rows = [json.loads(line) for f in a.inputs for line in open(f, encoding="utf-8") if line.strip()]
    chunks = build(rows, a.out, a.limit)
    print(json.dumps({"digests": [str(c) for c in chunks]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
