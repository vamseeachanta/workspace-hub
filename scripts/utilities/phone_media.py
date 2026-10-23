"""Copy phone USB archives into calendar folders; never move or delete originals."""

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

# Format scope: issue 3585. Tag priority is an explicit organizer policy, not
# an assertion that filesystem or container dates always represent capture time.
MEDIA = {".heic", ".mov", ".png", ".jpg", ".jpeg"}
TAGS = ("DateTimeOriginal", "CreationDate", "CreateDate", "MediaCreateDate")


def digest(path):
    """Hash complete bytes with SHA-256 (Python hashlib documentation)."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_metadata(path):
    """ExifTool application documentation: -j, -s and -- options.

    https://exiftool.org/exiftool_pod.html (accessed 2026-10-22).
    No shell is used and no metadata-writing option is passed.
    """
    result = subprocess.run(
        [
            "exiftool",
            "-j",
            "-s",
            *(f"-Keys:{tag}" if tag == "CreationDate" else f"-{tag}" for tag in TAGS),
            "--",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    records = json.loads(result.stdout)
    if (
        not isinstance(records, list)
        or len(records) != 1
        or not isinstance(records[0], dict)
    ):
        raise ValueError("unexpected ExifTool JSON structure")
    return records[0]


def capture_month(path, reader, warnings, relative):
    try:
        metadata = reader(path)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        # Do not leak absolute filenames from tool diagnostics into reports.
        warnings.append(
            f"{relative}: metadata unavailable ({type(exc).__name__}); using mtime"
        )
        metadata = {}
    for tag in TAGS:
        value = metadata.get(tag)
        if value is None:
            continue
        try:
            # ExifTool's default date representation is YYYY:mm:dd HH:MM:SS.
            # String dates retain their local month. Integer MOV dates use UTC
            # per QuickTime, without conversion to the computer's timezone.
            stamp = str(value)
            date = datetime.strptime(stamp[:19], "%Y:%m:%d %H:%M:%S")
            basis = tag
            if path.suffix.lower() == ".mov" and tag in (
                "CreateDate",
                "MediaCreateDate",
            ):
                basis = f"{tag}_utc"
            return date.strftime("%Y/%m"), basis
        except ValueError:
            warnings.append(f"{relative}: invalid {tag}")
    # UTC makes fallback independent of the computer's local timezone.
    return datetime.fromtimestamp(path.stat().st_mtime, UTC).strftime(
        "%Y/%m"
    ), "mtime_utc"


def reject_link(path, context):
    """Reject aliases, including Windows junctions, before descending or copying."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode):
        raise ValueError(f"{context} symlink is not supported")
    if getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        raise ValueError(f"{context} reparse point is not supported")


def inventory(root):
    files = []

    def visit(phone, usb, directory):
        for path in sorted(directory.iterdir()):
            reject_link(path, f"{path.relative_to(root).as_posix()}: source")
            if path.is_dir():
                visit(phone, usb, path)
            elif path.is_file() and path.suffix.lower() in MEDIA | {".aae"}:
                files.append((phone.name, usb, path))

    for phone in sorted(root.iterdir()):
        reject_link(phone, f"{phone.name}: source")
        if not phone.is_dir():
            continue
        usb = phone / "usb"
        reject_link(usb, f"{phone.name}/usb: source")
        if not usb.is_dir():
            continue
        visit(phone, usb, usb)
    return files


def check_destination(output, target):
    for path in (target, *target.parents):
        reject_link(path, f"{target.relative_to(output).as_posix()}: destination")
        if path == output:
            break


def copy_verified(source, target, expected):
    if target.exists():
        if not target.is_file() or digest(target) != expected:
            raise FileExistsError("destination differs; no overwrite permitted")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also refuses files created after the existence check.
    with source.open("rb") as incoming, target.open("xb") as outgoing:
        shutil.copyfileobj(incoming, outgoing)
    if digest(target) != expected:
        raise OSError("copy digest mismatch; destination retained for inspection")
    shutil.copystat(source, target)


def error_reason(exc):
    """Keep native exception filenames out of command-line diagnostics."""
    if isinstance(exc, OSError) and exc.filename is not None:
        return exc.strerror or type(exc).__name__
    return str(exc)


def organize(root, output, *, apply=False, metadata_reader=read_metadata):
    root, output = Path(root).resolve(), Path(output).absolute()
    resolved_output = output.resolve()
    if (
        root == resolved_output
        or root in resolved_output.parents
        or resolved_output in root.parents
    ):
        raise ValueError("input and output roots overlap")
    if not root.is_dir():
        raise ValueError("input root must be a directory")
    # Reject output aliases before resolution could hide a symlink.
    for path in (output, *output.parents):
        reject_link(path, "destination")
    entries = inventory(root)
    warnings, dates, companions = [], {}, defaultdict(list)
    for phone, usb, path in entries:
        if path.suffix.lower() in MEDIA:
            dates[path] = capture_month(
                path, metadata_reader, warnings, path.relative_to(root).as_posix()
            )
            companions[(path.parent, path.stem.casefold())].append(path)
    records, groups = [], defaultdict(list)
    for phone, usb, path in entries:
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() == ".aae":
            matches = companions[(path.parent, path.stem.casefold())]
            if matches:
                # Prefer a still over its Live Photo MOV; ties use lexical order.
                paired = min(
                    matches, key=lambda p: (p.suffix.lower() == ".mov", p.name)
                )
                month, basis = dates[paired]
                basis = f"paired:{basis}"
                if len({dates[p][0] for p in matches}) > 1:
                    warnings.append(
                        f"{relative}: companions span months; paired with {paired.name}"
                    )
            else:
                warnings.append(f"{relative}: orphan sidecar; using mtime")
                month, basis = capture_month(path, lambda p: {}, warnings, relative)
        else:
            month, basis = dates[path]
        destination = Path(month) / phone / path.relative_to(usb)
        target = output / destination
        check_destination(output, target)
        record = {
            "source": relative,
            "destination": destination.as_posix(),
            "phone": phone,
            "sha256": digest(path),
            "date_source": basis,
        }
        records.append(record)
        if path.suffix.lower() in MEDIA:
            groups[record["sha256"]].append(record)
    # Preflight every existing destination before any copies occur.
    conflicts = []
    for record in records:
        target = output / record["destination"]
        if target.exists() and (
            not target.is_file() or digest(target) != record["sha256"]
        ):
            conflicts.append(
                {
                    "destination": record["destination"],
                    "reason": "destination differs; no overwrite permitted",
                }
            )
    if apply and conflicts:
        first = conflicts[0]
        raise FileExistsError(f"{first['destination']}: {first['reason']}")
    if apply:
        for record in records:
            target = output / record["destination"]
            check_destination(output, target)
            try:
                copy_verified(root / record["source"], target, record["sha256"])
            except OSError as exc:
                raise OSError(f"{record['destination']}: {error_reason(exc)}") from exc
    duplicates = [
        {"sha256": key, "files": [r["source"] for r in group]}
        for key, group in sorted(groups.items())
        if len({r["phone"] for r in group}) > 1
    ]
    return {
        "schema_version": "1",
        "mode": "copy" if apply else "dry_run",
        "files": records,
        "duplicates": duplicates,
        "warnings": warnings,
        "conflicts": conflicts,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="root containing PHONE/usb/ trees")
    parser.add_argument("output", type=Path, help="separate organized-copy root")
    parser.add_argument(
        "--apply", action="store_true", help="copy files (default: dry run)"
    )
    args = parser.parse_args(argv)
    try:
        report = organize(args.input, args.output, apply=args.apply)
    except (OSError, ValueError) as exc:
        parser.exit(
            1,
            f"phone-media: {type(exc).__name__}: {error_reason(exc)}; "
            "no files are deleted\n",
        )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
