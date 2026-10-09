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
import os
import re
import subprocess
import sys
import tempfile
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
    out_path, manifest_path = Path(args.out).resolve(), Path(args.manifest).resolve()
    inputs = {(root / p).resolve() for p in args.paths}
    if out_path == manifest_path:
        return _fail(1, "--out and --manifest must be different files")
    if out_path in inputs or manifest_path in inputs:
        return _fail(1, "an output path is also a reviewed input; refusing to overwrite it")
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
        # Split on \n only: str.splitlines() also splits at form feed and Unicode line separators,
        # which would make packet line numbers disagree with editors and `path:line`.
        lines = [ln[:-1] if ln.endswith("\r") else ln for ln in text.split("\n")]
        if lines and lines[-1] == "":
            lines.pop()
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

    packet_bytes = packet.encode("utf-8")
    manifest = {"schema": SCHEMA, "created": created, "git_head": head, "digest_domain": "raw-bytes",
                "packet_path": str(out_path), "packet_bytes": size,
                "packet_sha256": hashlib.sha256(packet_bytes).hexdigest(), "files": entries}
    # Stage both outputs in exclusively created, uniquely named temp files, then publish.
    # The manifest goes last and pins the packet digest, so a half-published pair fails `verify`.
    staged = []
    try:
        for dest, data in ((out_path, packet_bytes),
                           (manifest_path, (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))):
            fd, tmp_name = tempfile.mkstemp(dir=dest.parent, prefix=f".{dest.name}.", suffix=".staging")
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
            staged.append((Path(tmp_name), dest))
        for tmp, dest in staged:
            os.replace(tmp, dest)
    finally:
        for tmp, _ in staged:
            if tmp.exists():
                tmp.unlink()
    print(json.dumps({"packet": args.out, "bytes": size, "files": len(entries)}))
    return 0


def verify(args: argparse.Namespace) -> int:
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return _fail(1, f"cannot read manifest: {exc}")
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA or not isinstance(files, list) or not files:
        return _fail(1, f"manifest is not a non-empty {SCHEMA} manifest")
    paths = [f.get("path") for f in files if isinstance(f, dict)]
    if (len(paths) != len(files) or not all(isinstance(p, str) and p for p in paths)
            or len(set(paths)) != len(paths) or not all(
                isinstance(f.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", f["sha256"]) for f in files)):
        return _fail(1, "manifest entries need unique string paths and 64-hex sha256 digests")
    packet_state = "not-recorded"
    if manifest.get("packet_sha256"):
        pp = Path(str(manifest.get("packet_path") or ""))
        if not pp.is_file():
            packet_state = "missing"
        else:
            packet_state = ("match" if hashlib.sha256(pp.read_bytes()).hexdigest() == manifest["packet_sha256"]
                            else "mismatch")
    root = Path.cwd().resolve()
    changed, missing = [], []
    for f in files:
        p = (root / f["path"]).resolve()
        try:
            p.relative_to(root)
        except ValueError:
            return _fail(1, f"manifest path {f['path']!r} is outside the packet root {root}")
        if not p.is_file():
            missing.append(f["path"])
        elif hashlib.sha256(p.read_bytes()).hexdigest() != f["sha256"]:
            changed.append(f["path"])
    status = "changed" if changed or missing or packet_state in ("missing", "mismatch") else "unchanged"
    print(json.dumps({"status": status, "changed": changed, "missing": missing, "packet": packet_state,
                      "files": len(files)}))
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
