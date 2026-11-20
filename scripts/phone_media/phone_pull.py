#!/usr/bin/env python3
"""Helper for phone_pull.sh: scan, reconcile, verify, safe-to-delete list,
optional HEIC-to-JPEG copies and a YouTube upload plan.

Safety rules enforced here (issue #3584, #3586):
* The phone tree is only read. Nothing on the phone is written or deleted.
* Nothing in the archive is overwritten. A phone file whose name is taken by a
  different local file is saved beside it as <stem>__phone-<sha8><ext>.
* A file is listed as safe to delete only when it passed the local check
  (same size, SHA-256 recorded) AND the Drive size check AND the Drive hash
  check (or rclone reported that the remote has no common hash). A file that
  is missing, different or unreadable on Drive is never listed.
* Output files name private media and stay on the archive host. Terminal
  output carries counts and report paths only, never media file names.

Standard library only, except the optional `jpeg` step (pillow-heif).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

PHOTO = {".heic", ".heif", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif",
         ".dng", ".tif", ".tiff"}
VIDEO = {".mov", ".mp4", ".m4v", ".3gp", ".avi"}
SIDECAR = {".aae"}
MTIME_SLACK = 2.0  # seconds; AFC and FAT round timestamps
ALT_TAG = "__phone-"
GB = 1_000_000_000  # decimal GB, as the iPhone Storage screen shows
MANIFEST_FIELDS = ["phone_path", "local_path", "kind", "size", "sha256",
                   "captured", "date_source", "status"]
DRYRUN_MARKER = ".phone-pull-dryrun"
MARK_WORDS = {"+": "missing_on_drive", "*": "different_on_drive",
              "!": "drive_read_error", "-": "only_on_drive"}


# ----------------------------------------------------------------- basics
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def scan(root: Path) -> list[dict]:
    """List regular files under root (relative POSIX paths), skipping dot
    files and dot folders (rsync temp files, iOS internals) and symlinks."""
    root = Path(root)
    out = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for name in sorted(filenames):
            if name.startswith("."):
                continue
            path = Path(dirpath) / name
            if path.is_symlink() or not path.is_file():
                continue
            st = path.stat()
            out.append({"rel": path.relative_to(root).as_posix(),
                        "size": st.st_size, "mtime": st.st_mtime})
    return out


def classify(rels: list[str]) -> dict[str, str]:
    """photo / video / live_clip / sidecar / other. A live clip is a video
    with the same stem as a photo in the same folder (Live Photo motion)."""
    photo_stems = set()
    for rel in rels:
        p = Path(rel)
        if p.suffix.lower() in PHOTO:
            photo_stems.add((p.parent.as_posix(), p.stem.lower()))
    kinds = {}
    for rel in rels:
        p = Path(rel)
        ext = p.suffix.lower()
        if ext in PHOTO:
            kinds[rel] = "photo"
        elif ext in VIDEO:
            live = (p.parent.as_posix(), p.stem.lower()) in photo_stems
            kinds[rel] = "live_clip" if live else "video"
        elif ext in SIDECAR:
            kinds[rel] = "sidecar"
        else:
            kinds[rel] = "other"
    return kinds


def alt_name(rel: str, phone_sha: str) -> str:
    p = Path(rel)
    return (p.parent / f"{p.stem}{ALT_TAG}{phone_sha[:8]}{p.suffix}").as_posix()


def copy_no_overwrite(src: Path, dst: Path) -> str:
    """Copy src to dst via a temp file; refuse if dst exists. Returns the
    SHA-256 of what was written."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.parent / f".{dst.name}.part-{os.getpid()}"
    h = hashlib.sha256()
    with open(src, "rb") as fin, open(tmp, "xb") as fout:
        for block in iter(lambda: fin.read(1 << 20), b""):
            h.update(block)
            fout.write(block)
    shutil.copystat(src, tmp)
    try:
        os.link(tmp, dst)  # fails if dst exists: never overwrites
        os.unlink(tmp)
    except FileExistsError:
        os.unlink(tmp)
        raise
    except OSError:  # file system without hard links
        if dst.exists():
            os.unlink(tmp)
            raise FileExistsError(str(dst))
        os.rename(tmp, dst)
    return h.hexdigest()


def fmt_gb(n: int) -> str:
    if 0 < n < GB // 100:
        return f"{n / 1e6:.2f} MB"
    return f"{n / GB:.2f} GB"


def write_json(path: Path, data) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


# -------------------------------------------------------------- preflight
def preflight(scan_rows: list[dict], local_free: int, remote_free: int | None,
              remote_used_by_phone: int) -> dict:
    """Local space must be >= 2x the phone's DCIM bytes (hard stop).
    Drive must hold the bytes not yet there (backup stop, pull may go on)."""
    phone_bytes = sum(r["size"] for r in scan_rows)
    need_local = 2 * phone_bytes
    drive_need = max(0, phone_bytes - remote_used_by_phone)
    result = {
        "phone_files": len(scan_rows), "phone_bytes": phone_bytes,
        "local_free": local_free, "local_need": need_local,
        "local_ok": local_free >= need_local,
        "remote_free": remote_free, "drive_need": drive_need,
        "drive_ok": remote_free is None or remote_free >= drive_need,
        "remote_free_known": remote_free is not None,
    }
    return result


# -------------------------------------------------------------- reconcile
def reconcile(phone_dir: Path, local_dir: Path) -> list[dict]:
    """Run after `rsync --ignore-existing`. Decide, for every phone file,
    which local file holds its bytes. Different files under the same name are
    kept both: the phone version is copied to an alternate name."""
    rows = []
    for e in scan(phone_dir):
        rel = e["rel"]
        src, dst = phone_dir / rel, local_dir / rel
        row = {"phone_path": rel, "size": e["size"], "mtime": e["mtime"],
               "local_path": None, "how": "missing", "phone_sha256": None}
        if dst.is_file():
            st = dst.stat()
            if st.st_size == e["size"] and abs(st.st_mtime - e["mtime"]) <= MTIME_SLACK:
                row.update(local_path=rel, how="same")
            else:
                phone_sha = sha256(src)
                row["phone_sha256"] = phone_sha
                if st.st_size == e["size"] and sha256(dst) == phone_sha:
                    row.update(local_path=rel, how="same")
                else:
                    alt = alt_name(rel, phone_sha)
                    altp = local_dir / alt
                    if altp.exists():
                        ok = altp.stat().st_size == e["size"] and sha256(altp) == phone_sha
                        row.update(local_path=alt if ok else None,
                                   how="kept_both" if ok else "conflict_unresolved")
                    else:
                        written = copy_no_overwrite(src, altp)
                        ok = written == phone_sha
                        row.update(local_path=alt if ok else None,
                                   how="kept_both" if ok else "copy_changed")
        rows.append(row)
    return rows


# ----------------------------------------------------------------- verify
def exif_dates(paths: list[Path]) -> dict[str, str]:
    """Capture dates from exiftool when installed; {} otherwise."""
    exe = shutil.which("exiftool")
    if not exe or not paths:
        return {}
    found = {}
    for i in range(0, len(paths), 200):
        chunk = [str(p) for p in paths[i:i + 200]]
        res = subprocess.run(
            [exe, "-j", "-q", "-d", "%Y-%m-%dT%H:%M:%S", "-DateTimeOriginal",
             "-Keys:CreationDate", "-CreateDate", "--", *chunk],
            capture_output=True, text=True, encoding="utf-8", check=False)
        try:
            records = json.loads(res.stdout or "[]")
        except ValueError:
            continue
        for rec in records:
            for tag in ("DateTimeOriginal", "CreationDate", "CreateDate"):
                val = str(rec.get(tag, ""))
                if re.match(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d", val):
                    found[rec.get("SourceFile")] = val[:19]
                    break
    return found


def verify(pull_map: list[dict], phone_dir: Path, local_dir: Path,
           hash_phone: bool = False, use_exif: bool = True) -> list[dict]:
    kinds = classify([r["phone_path"] for r in pull_map])
    locals_ = [local_dir / r["local_path"] for r in pull_map if r.get("local_path")]
    dates = exif_dates(locals_) if use_exif else {}
    out = []
    for r in pull_map:
        rel = r["phone_path"]
        row = {"phone_path": rel, "local_path": r.get("local_path") or "",
               "kind": kinds[rel], "size": r["size"], "sha256": "",
               "captured": "", "date_source": "", "status": "ok"}
        src = phone_dir / rel
        lp = local_dir / r["local_path"] if r.get("local_path") else None
        if lp is None or not lp.is_file():
            row["status"] = f"not_copied:{r.get('how', 'missing')}"
        else:
            phone_size = src.stat().st_size if src.is_file() else None
            local_size = lp.stat().st_size
            if phone_size is None:
                row["status"] = "gone_from_phone"
            elif local_size != phone_size or local_size != r["size"]:
                row["status"] = "size_mismatch"
            else:
                row["sha256"] = sha256(lp)
                ref = r.get("phone_sha256") or (sha256(src) if hash_phone else None)
                if ref and ref != row["sha256"]:
                    row["status"] = "hash_mismatch"
            when = dates.get(str(lp))
            if when:
                row.update(captured=when, date_source="exif")
            else:
                stamp = datetime.fromtimestamp(lp.stat().st_mtime)
                row.update(captured=stamp.strftime("%Y-%m-%dT%H:%M:%S"),
                           date_source="mtime")
        out.append(row)
    return out


def write_manifest(rows: list[dict], path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, delimiter="\t")
        w.writeheader()
        w.writerows(rows)


def read_manifest(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    for r in rows:
        r["size"] = int(r["size"])
    return rows


# -------------------------------------------------------- safe to delete
def parse_combined(path: Path | None) -> dict[str, str] | None:
    """rclone check --combined (rclone docs): '= p' identical, '+ p' only in
    the source (missing on Drive), '- p' only on Drive, '* p' different, '! p' error."""
    if path is None or not Path(path).is_file():
        return None
    marks = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if len(line) >= 3 and line[1] == " " and line[0] in "=-+*!":
            marks[line[2:]] = line[0]
    return marks


def hash_state(hash_marks: dict | None, hash_log: Path | None) -> str:
    """checked | unsupported | missing."""
    if hash_marks is None:
        return "missing"
    if hash_log and Path(hash_log).is_file():
        if "No common hash found" in Path(hash_log).read_text(encoding="utf-8", errors="replace"):
            return "unsupported"
    return "checked"


def safe_to_delete(manifest: list[dict], size_marks: dict | None,
                   hash_marks: dict | None, hstate: str) -> tuple[list, list]:
    safe, unsafe = [], []
    for r in manifest:
        lp = r["local_path"]
        if r["status"] != "ok":
            reason = f"local:{r['status']}"
        elif size_marks is None:
            reason = "drive:size_check_not_run"
        elif size_marks.get(lp) != "=":
            reason = "drive_size:" + MARK_WORDS.get(size_marks.get(lp), "not_checked")
        elif hstate == "missing":
            reason = "drive:hash_check_not_run"
        elif hstate == "checked" and hash_marks.get(lp) != "=":
            reason = "drive_hash:" + MARK_WORDS.get(hash_marks.get(lp), "not_checked")
        else:
            safe.append(r)
            continue
        unsafe.append({**r, "reason": reason})
    return safe, unsafe


def totals(rows: list[dict]) -> dict:
    t = {k: {"count": 0, "bytes": 0} for k in
         ("photo", "live_clip", "video", "sidecar", "other", "all")}
    for r in rows:
        for k in (r["kind"], "all"):
            t[k]["count"] += 1
            t[k]["bytes"] += r["size"]
    return t


def cutoff(manifest: list[dict], unsafe: list[dict]) -> date | None:
    """Last calendar day such that every item captured on or before it is
    safe. None when the earliest item is unsafe or dates are missing."""
    days = [r["captured"][:10] for r in manifest if r.get("captured")]
    if not days:
        return None
    bad = [r["captured"][:10] for r in unsafe if r.get("captured")]
    if len(bad) < len(unsafe):  # an unsafe item with no date: no safe range
        return None
    if not bad:
        return date.fromisoformat(max(days))
    first_bad = date.fromisoformat(min(bad))
    day = first_bad - timedelta(days=1)
    return day if day >= date.fromisoformat(min(days)) else None


def safe_report(phone: str, manifest: list[dict], safe: list[dict],
                unsafe: list[dict], hstate: str, stamp: str) -> str:
    t = totals(safe)
    cut = cutoff(manifest, unsafe)
    lines = [
        f"Safe-to-delete list for {phone} ({stamp})",
        "",
        f"Checked on the phone: {len(manifest)} files, {fmt_gb(sum(r['size'] for r in manifest))}",
        f"Safe to delete: {t['all']['count']} files, {fmt_gb(t['all']['bytes'])}",
        f"  photos:            {t['photo']['count']:>6}  {fmt_gb(t['photo']['bytes'])}",
        f"  videos:            {t['video']['count']:>6}  {fmt_gb(t['video']['bytes'])}",
        f"  Live Photo clips:  {t['live_clip']['count']:>6}  {fmt_gb(t['live_clip']['bytes'])}"
        "  (part of a photo in the Photos app)",
        f"  edit sidecars:     {t['sidecar']['count']:>6}  {fmt_gb(t['sidecar']['bytes'])}",
        f"  other:             {t['other']['count']:>6}  {fmt_gb(t['other']['bytes'])}",
        f"NOT safe (kept off the list): {len(unsafe)} files; reasons in the not-safe file",
        f"Drive checks: size = yes; hash = {hstate}",
        "",
    ]
    if cut:
        upto = [r for r in safe if r.get("captured", "")[:10] <= cut.isoformat()]
        lines.append(
            f"Everything taken on or before {cut.isoformat()} is backed up: "
            f"{len(upto)} files, {fmt_gb(sum(r['size'] for r in upto))}.")
    else:
        lines.append("No date range is fully backed up; delete only items on the list.")
    lines += [
        "",
        "How to free the space (the script never deletes anything on the phone):",
        "  1. On the phone open Photos, Library, All Photos; tap Select and pick",
        "     items up to the date above (drag to select many at once).",
        "  2. Tap the bin, Delete. Then Albums, Recently Deleted, Select,",
        "     Delete All. Space only comes back after this second step.",
        f"  3. That frees about {fmt_gb(t['all']['bytes'])}.",
        "  If iCloud Photos is ON, deleting on the phone also deletes from",
        "  iCloud and every other signed-in device. Turn it off first or",
        "  accept that the Drive copy becomes the only copy.",
        "  Photos taken after this pull are not on the list.",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- YouTube
def video_minutes(path: Path) -> float | None:
    exe = shutil.which("ffprobe")
    if not exe:
        return None
    res = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)],
                         capture_output=True, text=True, check=False)
    try:
        return float(res.stdout.strip()) / 60.0
    except ValueError:
        return None


def youtube_plan(manifest: list[dict], local_dir: Path, min_mb: float,
                 min_minutes: float, minutes=video_minutes) -> list[dict]:
    plan = []
    for r in manifest:
        if r["kind"] != "video" or r["status"] != "ok":
            continue
        mins = minutes(local_dir / r["local_path"])
        if r["size"] >= min_mb * 1e6 or (mins is not None and mins >= min_minutes):
            when = r.get("captured", "")
            title = when[:16].replace("T", " ") if when else Path(r["local_path"]).stem
            plan.append({"local_path": r["local_path"], "size_mb": round(r["size"] / 1e6, 1),
                         "minutes": None if mins is None else round(mins, 1),
                         "title": title, "privacy": "private"})
    return plan


YOUTUBE_NOTES = """YouTube upload plan (PREPARED, NOT RUN)

Videos stay at full quality on the archive host and on Drive. YouTube is a
viewing copy only: it re-encodes, so it is never the backup.

Each row: title = capture date and time, privacy = private (change by hand
later if you want to share). Paths are relative to: {base}

Before the first upload the owner must:
  1. In Google Cloud Console (his account) create a project, enable
     "YouTube Data API v3", create an OAuth client of type Desktop app and
     download its JSON to ~/.config/phone-media/youtube/client_secret.json on
     the archive host (never into a repository).
  2. Run the uploader once in a terminal he controls and sign in with the
     YouTube account (OAuth). The token is cached next to the client JSON.
Notes: uploads from an unverified API project are locked to private, which
matches this plan. The default API quota allows only a handful of uploads a
day (check Google's current quota table). Nothing here uploads by itself.
"""


# ------------------------------------------------------------------ JPEG
def make_jpegs(manifest: list[dict], local_dir: Path, out_dir: Path,
               quality: int = 92) -> dict:
    """JPEG copies of HEIC photos, stored in a parallel tree; originals untouched."""
    from PIL import Image  # noqa: PLC0415 - optional dependency
    import pillow_heif  # noqa: PLC0415

    pillow_heif.register_heif_opener()
    stats = {"made": 0, "skipped": 0, "failed": 0}
    for r in manifest:
        lp = r["local_path"]
        if r["status"] != "ok" or Path(lp).suffix.lower() not in (".heic", ".heif"):
            continue
        dst = out_dir / Path(lp).with_suffix(".jpg")
        if dst.exists():
            stats["skipped"] += 1
            continue
        src = local_dir / lp
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.parent / f".{dst.name}.part-{os.getpid()}"
        try:
            with Image.open(src) as im:
                extra = {k: im.info[k] for k in ("exif", "icc_profile") if im.info.get(k)}
                im.convert("RGB").save(tmp, "JPEG", quality=quality, **extra)
            st = src.stat()
            os.utime(tmp, (st.st_atime, st.st_mtime))
            os.link(tmp, dst)
            stats["made"] += 1
        except Exception:  # noqa: BLE001 - count, keep going, no names printed
            stats["failed"] += 1
        finally:
            if tmp.exists():
                os.unlink(tmp)
    return stats


# --------------------------------------------------------------- dry run
FAKE_FILES = [  # (relative path, bytes, capture date)
    ("100APPLE/IMG_0001.HEIC", 40_000, "2026-06-02T09:15:00"),
    ("100APPLE/IMG_0001.MOV", 60_000, "2026-06-02T09:15:00"),
    ("100APPLE/IMG_0002.JPG", 30_000, "2026-07-14T18:40:00"),
    ("100APPLE/IMG_0003.PNG", 20_000, "2026-08-01T12:00:00"),
    ("100APPLE/IMG_0003.AAE", 1_000, "2026-08-01T12:00:00"),
    ("100APPLE/IMG_0004.MOV", 300_000, "2026-09-10T16:05:00"),
    ("101APPLE/IMG_0100.MP4", 500_000, "2026-10-20T20:30:00"),
    ("101APPLE/IMG_0101.HEIC", 50_000, "2026-11-05T08:00:00"),
]


def make_fake_dcim(dcim: Path, seed_conflict: Path | None = None) -> int:
    """Synthetic DCIM with random bytes (real tiny HEIC when pillow-heif is
    importable). Optionally pre-seeds a different same-name local file to
    exercise keep-both."""
    rng = random.Random(3584)
    try:
        from PIL import Image  # noqa: PLC0415
        import pillow_heif  # noqa: PLC0415
    except ImportError:
        pillow_heif = None
    for rel, size, when in FAKE_FILES:
        p = dcim / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix.lower() == ".heic" and pillow_heif is not None:
            img = Image.new("RGB", (64, 48), (rng.randrange(256), 120, 200))
            pillow_heif.from_pillow(img).save(str(p), quality=60)
        else:
            p.write_bytes(rng.randbytes(size))
        ts = datetime.fromisoformat(when).timestamp()
        os.utime(p, (ts, ts))
    if seed_conflict is not None:
        q = seed_conflict / "100APPLE/IMG_0002.JPG"
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_bytes(rng.randbytes(12_345))
        ts = datetime.fromisoformat("2025-01-01T00:00:00").timestamp()
        os.utime(q, (ts, ts))
    return len(FAKE_FILES)


def simulate_missing(dest: Path, count: int) -> int:
    """Dry run only: drop files from the FAKE Drive folder to prove that a
    file missing on Drive never reaches the safe list."""
    dest = Path(dest).resolve()
    if not any((parent / DRYRUN_MARKER).is_file() for parent in dest.parents):
        raise SystemExit("refusing: destination is not inside a dry-run folder")
    victims = [dest / r["rel"] for r in scan(dest)][:count]
    for v in victims:
        v.unlink()
    return len(victims)


# -------------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan")
    s.add_argument("--source", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)

    s = sub.add_parser("preflight")
    s.add_argument("--scan", type=Path, required=True)
    s.add_argument("--local-free", type=int, required=True)
    s.add_argument("--about", type=Path, help="rclone about --json output")
    s.add_argument("--remote-size", type=Path, help="rclone size --json output")
    s.add_argument("--out", type=Path, required=True)

    s = sub.add_parser("reconcile")
    s.add_argument("--phone-dir", type=Path, required=True)
    s.add_argument("--local-dir", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)

    s = sub.add_parser("verify")
    s.add_argument("--map", type=Path, required=True)
    s.add_argument("--phone-dir", type=Path, required=True)
    s.add_argument("--local-dir", type=Path, required=True)
    s.add_argument("--manifest", type=Path, required=True)
    s.add_argument("--hash-phone", action="store_true")
    s.add_argument("--no-exif", action="store_true")

    s = sub.add_parser("safe-list")
    s.add_argument("--phone", required=True)
    s.add_argument("--manifest", type=Path, required=True)
    s.add_argument("--size-check", type=Path)
    s.add_argument("--hash-check", type=Path)
    s.add_argument("--hash-log", type=Path)
    s.add_argument("--out-dir", type=Path, required=True)
    s.add_argument("--stamp", required=True)

    s = sub.add_parser("youtube-plan")
    s.add_argument("--manifest", type=Path, required=True)
    s.add_argument("--local-dir", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True, help="path without extension")
    s.add_argument("--min-mb", type=float, default=500)
    s.add_argument("--min-minutes", type=float, default=10)

    s = sub.add_parser("jpeg")
    s.add_argument("--manifest", type=Path, required=True)
    s.add_argument("--local-dir", type=Path, required=True)
    s.add_argument("--out-dir", type=Path, required=True)

    s = sub.add_parser("make-fake-dcim")
    s.add_argument("--dcim", type=Path, required=True)
    s.add_argument("--seed-conflict", type=Path)

    s = sub.add_parser("simulate-missing")
    s.add_argument("--dest", type=Path, required=True)
    s.add_argument("--count", type=int, default=1)

    a = ap.parse_args(argv)

    if a.cmd == "scan":
        rows = scan(a.source)
        write_json(a.out, rows)
        total = sum(r["size"] for r in rows)
        print(f"phone DCIM: {len(rows)} files, {fmt_gb(total)}")
        return 0 if rows else 3

    if a.cmd == "preflight":
        rows = json.loads(a.scan.read_text(encoding="utf-8"))
        free = used = None
        if a.about and a.about.is_file() and a.about.stat().st_size:
            free = json.loads(a.about.read_text(encoding="utf-8")).get("free")
        if a.remote_size and a.remote_size.is_file() and a.remote_size.stat().st_size:
            used = json.loads(a.remote_size.read_text(encoding="utf-8")).get("bytes")
        res = preflight(rows, a.local_free, free, used or 0)
        write_json(a.out, res)
        print(f"local free {fmt_gb(res['local_free'])}; need 2 x DCIM = "
              f"{fmt_gb(res['local_need'])}: {'OK' if res['local_ok'] else 'TOO LITTLE SPACE'}")
        drive_free = "unknown" if free is None else fmt_gb(free)
        print(f"Drive free {drive_free}; still to upload about {fmt_gb(res['drive_need'])}: "
              f"{'OK' if res['drive_ok'] else 'TOO LITTLE SPACE (backup step will stop)'}")
        return 0 if res["local_ok"] else 4

    if a.cmd == "reconcile":
        rows = reconcile(a.phone_dir, a.local_dir)
        write_json(a.out, rows)
        hows = {}
        for r in rows:
            hows[r["how"]] = hows.get(r["how"], 0) + 1
        print("reconcile: " + ", ".join(f"{k} {v}" for k, v in sorted(hows.items())))
        return 0 if hows.get("same", 0) + hows.get("kept_both", 0) == len(rows) else 9

    if a.cmd == "verify":
        pull_map = json.loads(a.map.read_text(encoding="utf-8"))
        rows = verify(pull_map, a.phone_dir, a.local_dir, a.hash_phone, not a.no_exif)
        write_manifest(rows, a.manifest)
        bad = [r for r in rows if r["status"] != "ok"]
        print(f"verify: {len(rows) - len(bad)} of {len(rows)} files match the phone "
              f"(count and size{', phone hash' if a.hash_phone else ''}); {len(bad)} problems")
        return 0 if not bad else 6

    if a.cmd == "safe-list":
        manifest = read_manifest(a.manifest)
        size_marks = parse_combined(a.size_check)
        hash_marks = parse_combined(a.hash_check)
        hstate = hash_state(hash_marks, a.hash_log)
        safe, unsafe = safe_to_delete(manifest, size_marks, hash_marks, hstate)
        a.out_dir.mkdir(parents=True, exist_ok=True)
        base = a.out_dir / f"safe-to-delete-{a.stamp}"
        with open(f"{base}.tsv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(["phone_path", "kind", "size", "captured"])
            for r in sorted(safe, key=lambda r: r["captured"]):
                w.writerow([r["phone_path"], r["kind"], r["size"], r["captured"]])
        with open(a.out_dir / f"not-safe-{a.stamp}.tsv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(["phone_path", "kind", "size", "captured", "reason"])
            for r in unsafe:
                w.writerow([r["phone_path"], r["kind"], r["size"], r["captured"], r["reason"]])
        report = safe_report(a.phone, manifest, safe, unsafe, hstate, a.stamp)
        Path(f"{base}.txt").write_text(report, encoding="utf-8")
        print(report, end="")
        print(f"lists: {base}.tsv, {base}.txt, {a.out_dir / f'not-safe-{a.stamp}.tsv'}")
        return 0

    if a.cmd == "youtube-plan":
        manifest = read_manifest(a.manifest)
        plan = youtube_plan(manifest, a.local_dir, a.min_mb, a.min_minutes)
        with open(f"{a.out}.tsv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["local_path", "size_mb", "minutes",
                                               "title", "privacy"], delimiter="\t")
            w.writeheader()
            w.writerows(plan)
        Path(f"{a.out}.txt").write_text(YOUTUBE_NOTES.format(base=a.local_dir), encoding="utf-8")
        print(f"YouTube plan (not run): {len(plan)} videos, "
              f"{sum(p['size_mb'] for p in plan) / 1000:.2f} GB -> {a.out}.tsv, {a.out}.txt")
        return 0

    if a.cmd == "jpeg":
        stats = make_jpegs(read_manifest(a.manifest), a.local_dir, a.out_dir)
        print(f"JPEG copies: made {stats['made']}, already there {stats['skipped']}, "
              f"failed {stats['failed']} -> {a.out_dir}")
        return 0 if not stats["failed"] else 7

    if a.cmd == "make-fake-dcim":
        n = make_fake_dcim(a.dcim, a.seed_conflict)
        print(f"fake DCIM: {n} files")
        return 0

    if a.cmd == "simulate-missing":
        n = simulate_missing(a.dest, a.count)
        print(f"dry run: removed {n} file(s) from the FAKE Drive folder")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
