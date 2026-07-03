#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path


CAD_EXTENSIONS = {
    ".step", ".stp", ".iges", ".igs", ".x_t", ".x_b", ".dwg", ".dxf",
    ".sldprt", ".sldasm", ".ipt", ".iam", ".prt", ".catpart", ".f3d",
    ".f3z", ".stl", ".3mf", ".nc", ".cnc", ".tap", ".gcode", ".mcam",
}


def iter_cad(root: Path):
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in {".ace-knowledge", "_cad-index", "$RECYCLE.BIN", "System Volume Information"}]
        for name in sorted(files):
            path = Path(current) / name
            if path.suffix.lower() in CAD_EXTENSIONS:
                yield path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a tree and emit CAD raw TSV rows.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for path in iter_cad(args.root):
            try:
                stat = path.stat()
            except OSError:
                continue
            handle.write(f"{stat.st_size}\t{int(stat.st_mtime)}\t{path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
