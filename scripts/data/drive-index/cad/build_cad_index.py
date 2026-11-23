#!/usr/bin/env python3
"""Parameterized CAD readability TSV builder vendored from the drive-local original."""

from __future__ import annotations

import argparse
import collections
import csv
import json
import os
from pathlib import Path
import re


READ = {
    "step": ("STEP (neutral)", "oss-3d", "pythonocc/OCC"),
    "stp": ("STEP (neutral)", "oss-3d", "pythonocc/OCC"),
    "iges": ("IGES (neutral)", "oss-3d", "pythonocc/OCC (surfaces)"),
    "igs": ("IGES (neutral)", "oss-3d", "pythonocc/OCC (surfaces)"),
    "x_t": ("Parasolid", "seat-only", "commercial OCC/Datakit"),
    "x_b": ("Parasolid", "seat-only", "commercial OCC/Datakit"),
    "dwg": ("AutoCAD", "convert-2d", "ODA->DXF->ezdxf/Blender"),
    "dxf": ("AutoCAD", "oss-2d", "ezdxf/Blender"),
    "sldprt": ("SolidWorks", "seat-only", "SolidWorks seat / STEP export"),
    "sldasm": ("SolidWorks", "seat-only", "SolidWorks seat / STEP export"),
    "ipt": ("Inventor", "seat-only", "Inventor seat / STEP export"),
    "iam": ("Inventor", "seat-only", "Inventor seat / STEP export"),
    "prt": ("NX/generic", "seat-likely", "varies (NX/ProE)"),
    "catpart": ("CATIA", "seat-only", "CATIA seat / STEP export"),
    "f3d": ("Fusion 360", "seat-only", "Fusion / export"),
    "f3z": ("Fusion 360", "seat-only", "Fusion / export"),
    "stl": ("Mesh", "oss-mesh", "trimesh/Blender"),
    "3mf": ("Mesh", "oss-mesh", "trimesh/Blender"),
    "nc": ("CAM/NetCDF", "ambiguous", "inspect"),
    "cnc": ("CAM", "cam", "postproc"),
    "tap": ("CAM", "cam", "postproc"),
    "gcode": ("CAM", "cam", "postproc"),
    "mcam": ("Mastercam", "seat-only", "Mastercam seat"),
}
CAD = set(READ)
HEADER = "path\tformat\tecosystem\treadability\tread_tool\tglb\tname_description\tproject\tsize\tmtime\n"


def clean_name(path: str) -> str:
    name = os.path.basename(path)
    name = re.sub(r"\.[^.]+$", "", name)
    name = re.sub(r"^~\$", "", name)
    return re.sub(r"[_]+", " ", name).strip()


def project(path: str) -> str:
    if "/docs/disciplines/knowledge_skills/projects/ri/" in path:
        return "ri-hoard (personal backup)"
    match = re.search(r"/docs/disciplines/([^/]+)/projects/([^/]+)/", path)
    if match:
        return f"docs/{match.group(1)}/{match.group(2)}"
    if "/digitalmodel/docs/domain/subsea-risers/" in path:
        return "digitalmodel/subsea-risers"
    parts = path.split("/")
    return parts[3] if len(parts) > 3 else "?"


def load_dedup(dedup: Path) -> tuple[set[str], dict[str, str]]:
    deleted = set()
    deletion_log = dedup / "deletion-log.tsv"
    if deletion_log.exists():
        for row in csv.reader(deletion_log.open(), delimiter="\t"):
            if row:
                deleted.add(row[0])
    glb = {}
    manifest = dedup / "glb-library-manifest.tsv"
    if manifest.exists():
        for row in csv.DictReader(manifest.open(), delimiter="\t"):
            glb[row["source"]] = row["glb"]
    return deleted, glb


def build(raw: Path, dedup: Path, out: Path) -> dict:
    deleted, glb = load_dedup(dedup)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    count = 0
    by_read = collections.Counter()
    by_fmt = collections.Counter()
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(HEADER)
        with raw.open(encoding="utf-8", errors="replace") as source:
            for line in source:
                fields = line.rstrip("\n").split("\t", 2)
                if len(fields) != 3:
                    continue
                size, mtime, path = fields
                if path in deleted:
                    continue
                ext = path.rsplit(".", 1)[-1].lower() if "." in os.path.basename(path) else ""
                if ext not in CAD:
                    continue
                ecosystem, readability, tool = READ[ext]
                handle.write(
                    f"{path}\t{ext}\t{ecosystem}\t{readability}\t{tool}\t{glb.get(path, '')}\t"
                    f"{clean_name(path)}\t{project(path)}\t{size}\t{mtime}\n"
                )
                count += 1
                by_read[readability] += 1
                by_fmt[ext] += 1
    tmp.replace(out)
    summary = {
        "indexed_cad_files": count,
        "readable_breakdown": dict(by_read.most_common()),
        "by_format": dict(by_fmt.most_common()),
        "glb_linked": len(glb),
        "output": str(out),
    }
    (out.parent / "index-summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CAD readability TSV from raw scan TSV.")
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--dedup", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(build(args.raw, args.dedup, args.out), indent=1))
    print("DONE_CADINDEX")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
