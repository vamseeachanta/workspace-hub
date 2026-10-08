#!/usr/bin/env python3
"""Build and verify an inline, hash-pinned review packet (#3973 R4).

A reviewer that cannot read the filesystem (Codex read-only sandbox on Windows,
a remote provider, an argv-length-limited CLI) still reviews the exact bytes
when they arrive inline. The manifest pins each file's raw-byte SHA-256, and
`verify` reports whether any reviewed file changed after the packet was built,
so a verdict on stale bytes is not carried forward.

    build-review-packet.py build --out PACKET.md --manifest M.json [--max-bytes N] [--label TEXT] PATH...
    build-review-packet.py verify --manifest M.json

Send the packet on stdin, never as an argument:
    codex exec -s read-only - < PACKET.md

Exit codes: 0 ok; 1 invalid input (missing, outside root, not UTF-8);
2 packet exceeds --max-bytes (nothing written); 3 verify found changes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_MAX_BYTES = 400_000
SCHEMA = "review-packet/1"


def _fail(code: int, msg: str) -> int:
    print(f"build-review-packet: {msg}", file=sys.stderr)
    return code


def _git_head(root: Path) -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=15)
        return (r.stdout.strip() or None) if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _fence(text: str) -> str:
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def build(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    entries, sections = [], []
    for raw_path in args.paths:
        p = (root / raw_path).resolve()
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            return _fail(1, f"{raw_path}: path is outside the packet root {root}")
        if not p.is_file():
            return _fail(1, f"{raw_path}: file not found")
        data = p.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return _fail(1, f"{raw_path}: not UTF-8 text; binary files are not inlined")
        digest = hashlib.sha256(data).hexdigest()
        entries.append({"path": rel, "sha256": digest, "bytes": len(data)})
        lines = text.splitlines()
        width = max(4, len(str(len(lines))))
        body = "\n".join(f"{i:>{width}} | {line}" for i, line in enumerate(lines, 1))
        fence = _fence(text)
        sections.append(f"## {rel}\n\nsha256 `{digest}` · {len(data)} bytes · {len(lines)} lines\n\n{fence}\n{body}\n{fence}\n")

    head = _git_head(root)
    created = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    header = [f"# Review packet{': ' + args.label if args.label else ''}", "",
              f"Generated {created}" + (f" · git HEAD `{head}`" if head else ""),
              "Digest domain: raw bytes as stored on disk (line endings included).",
              "Line numbers are prefixed; cite findings as `path:line`. The packet is the complete review target.", ""]
    packet = "\n".join(header) + "\n" + "\n".join(sections)
    size = len(packet.encode("utf-8"))
    if size > args.max_bytes:
        return _fail(2, f"packet is {size} bytes, over the {args.max_bytes}-byte budget; split the review instead of truncating")

    manifest = {"schema": SCHEMA, "created": created, "git_head": head, "digest_domain": "raw-bytes",
                "packet_bytes": size, "files": entries}
    Path(args.out).write_text(packet, encoding="utf-8", newline="\n")
    Path(args.manifest).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"packet": args.out, "bytes": size, "files": len(entries)}))
    return 0


def verify(args: argparse.Namespace) -> int:
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return _fail(1, f"cannot read manifest: {exc}")
    root = Path.cwd().resolve()
    changed, missing = [], []
    for f in manifest.get("files", []):
        p = root / f["path"]
        if not p.is_file():
            missing.append(f["path"])
        elif hashlib.sha256(p.read_bytes()).hexdigest() != f["sha256"]:
            changed.append(f["path"])
    status = "changed" if changed or missing else "unchanged"
    print(json.dumps({"status": status, "changed": changed, "missing": missing, "files": len(manifest.get("files", []))}))
    return 3 if status == "changed" else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build packet + manifest")
    b.add_argument("--out", required=True)
    b.add_argument("--manifest", required=True)
    b.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    b.add_argument("--label", default="")
    b.add_argument("paths", nargs="+")
    v = sub.add_parser("verify", help="recheck reviewed files against the manifest")
    v.add_argument("--manifest", required=True)
    args = ap.parse_args(argv)
    return build(args) if args.cmd == "build" else verify(args)


if __name__ == "__main__":
    sys.exit(main())
