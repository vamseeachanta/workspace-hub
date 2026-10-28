"""Merge inventories; verified full hashes and provisional candidates stay separate."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from dedupe._common import (
        FORMAT_VERSION,
        atomic_write_output,
        distinct_outputs,
        identity,
        json_text,
        validate_record,
    )
else:
    from ._common import (
        FORMAT_VERSION,
        atomic_write_output,
        distinct_outputs,
        identity,
        json_text,
        validate_record,
    )


def read_manifest(path, headers):
    with open(path, encoding="utf-8") as stream:
        try:
            header = json.loads(next(stream))
        except (StopIteration, json.JSONDecodeError) as exc:
            raise ValueError("missing manifest header") from exc
        if (
            not isinstance(header, dict)
            or header.get("type") != "manifest"
            or header.get("version") != FORMAT_VERSION
            or type(header.get("complete")) is not bool
            or not isinstance(header.get("label"), str)
            or not isinstance(header.get("errors"), list)
        ):
            raise ValueError("invalid manifest header")
        if header["complete"] and header["errors"]:
            raise ValueError("complete manifest contains scan errors")
        headers.append(header)
        for line in stream:
            row = json.loads(line)
            validate_record(row)
            if row["label"] != header["label"]:
                raise ValueError("manifest label mismatch")
            if header["complete"] and "error" in row:
                raise ValueError("complete manifest contains file errors")
            row["manifest_complete"] = header["complete"]
            yield row


def verified(row):
    return (
        row["manifest_complete"] is True
        and row["stage"] == "full"
        and row["sha256"] is not None
        and "error" not in row
    )


def group(files, status, basis):
    files = sorted(files, key=identity)
    labels = sorted({r["label"] for r in files})
    return {
        "status": status,
        "basis": basis,
        "size": files[0]["size"],
        "sha256": files[0]["sha256"] if status == "verified" else None,
        "sample_sha256": files[0]["sample_sha256"] if basis != "size" else None,
        "labels": labels,
        "files": files,
    }


def totals(groups):
    # README.md, Totals: one retained copy => (number of copies - 1) * size.
    return {
        "groups": len(groups),
        "files": sum(len(g["files"]) for g in groups),
        "bytes_reclaimable": sum((len(g["files"]) - 1) * g["size"] for g in groups),
    }


def merge(paths):
    rows = []
    headers = []
    seen = set()
    for path in paths:
        for row in read_manifest(path, headers):
            key = identity(row)
            if key in seen:
                raise ValueError("duplicate file identity across manifests")
            seen.add(key)
            rows.append(row)
    rows.sort(key=identity)
    full = defaultdict(list)
    by_size = defaultdict(list)
    for row in rows:
        if "error" in row:
            continue
        by_size[row["size"]].append(row)
        if verified(row):
            full[(row["size"], row["sha256"])].append(row)
    groups = [
        group(members, "verified", "full_sha256")
        for _, members in sorted(full.items())
        if len(members) > 1
    ]
    across = [g for g in groups if len(g["labels"]) > 1]
    within = [g for g in groups if len(g["labels"]) == 1]
    candidates = []
    for _, members in sorted(by_size.items()):
        if len(members) < 2 or all(verified(r) for r in members):
            continue
        if any(r["sample_sha256"] is None for r in members):
            candidates.append(group(members, "candidate", "size"))
        else:
            sampled = defaultdict(list)
            for row in members:
                sampled[row["sample_sha256"]].append(row)
            for _, same_sample in sorted(sampled.items()):
                if len(same_sample) > 1 and any(not verified(r) for r in same_sample):
                    candidates.append(
                        group(same_sample, "candidate", "size_and_sample")
                    )
    per_label = {}
    for label in sorted({r["label"] for r in rows}):
        local = []
        for g in groups:
            members = [r for r in g["files"] if r["label"] == label]
            if len(members) > 1:
                local.append(group(members, "verified", "full_sha256"))
        per_label[label] = totals(local)
    return {
        "version": FORMAT_VERSION,
        "across_labels": across,
        "within_label": within,
        "candidate_groups": candidates,
        "errors": [r for r in rows if "error" in r],
        "incomplete_labels": sorted({h["label"] for h in headers if not h["complete"]}),
        "scan_errors": sorted(
            [{"label": h["label"], **error} for h in headers for error in h["errors"]],
            key=lambda e: (e["label"], e["root"], e["path"]),
        ),
        "totals": {
            "verified": totals(groups),
            "across_labels": totals(across),
            "within_label": totals(within),
            "per_label": per_label,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="+")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        distinct_outputs([args.out], inputs=args.manifests)
        atomic_write_output(args.out, json_text(merge(args.manifests)) + "\n")
    except (ValueError, TypeError, OSError) as exc:
        parser.exit(2, f"merge failed: {type(exc).__name__}\n")


if __name__ == "__main__":
    main()
