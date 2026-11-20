"""Tests for the phone pull helper (#3584, #3586). Synthetic files only.

Comparators: hand-written rclone --combined outputs and hand-counted byte
totals; no real phone, archive or Drive is touched.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts/phone_media/phone_pull.py"
SCRIPT = ROOT / "scripts/phone_media/phone_pull.sh"


@pytest.fixture(scope="module")
def pp():
    spec = importlib.util.spec_from_file_location("phone_pull", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def put(path: Path, data: bytes, mtime: float = 1_780_000_000.0) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    os.utime(path, (mtime, mtime))
    return path


def row(rel, kind="photo", size=10, status="ok", captured="2026-06-01T10:00:00", local=None):
    return {"phone_path": rel, "local_path": local or rel, "kind": kind, "size": size,
            "sha256": "x", "captured": captured, "date_source": "mtime", "status": status}


# ------------------------------------------------------------ classify/scan
def test_classify_live_clip_video_sidecar(pp):
    kinds = pp.classify(["A/IMG_1.HEIC", "A/IMG_1.MOV", "A/IMG_2.MOV", "A/IMG_1.AAE",
                         "B/IMG_1.MOV", "A/x.bin"])
    assert kinds == {"A/IMG_1.HEIC": "photo", "A/IMG_1.MOV": "live_clip",
                     "A/IMG_2.MOV": "video", "A/IMG_1.AAE": "sidecar",
                     "B/IMG_1.MOV": "video", "A/x.bin": "other"}


def test_scan_skips_dot_files_and_symlinks(pp, tmp_path):
    put(tmp_path / "100APPLE/IMG_1.JPG", b"abc")
    put(tmp_path / "100APPLE/.IMG_1.JPG.tmp", b"partial")
    put(tmp_path / ".hidden/IMG_9.JPG", b"x")
    rows = pp.scan(tmp_path)
    assert [r["rel"] for r in rows] == ["100APPLE/IMG_1.JPG"]
    assert rows[0]["size"] == 3


# --------------------------------------------------------------- reconcile
def test_reconcile_keeps_both_on_name_clash(pp, tmp_path):
    phone, local = tmp_path / "DCIM", tmp_path / "usb"
    put(phone / "100APPLE/IMG_1.JPG", b"phone-bytes", 1_780_000_000)
    put(local / "100APPLE/IMG_1.JPG", b"older-different-file", 1_700_000_000)
    put(phone / "100APPLE/IMG_2.JPG", b"same", 1_780_000_000)
    put(local / "100APPLE/IMG_2.JPG", b"same", 1_780_000_000)
    put(phone / "100APPLE/IMG_3.JPG", b"not copied by rsync")

    rows = {r["phone_path"]: r for r in pp.reconcile(phone, local)}
    clash = rows["100APPLE/IMG_1.JPG"]
    assert clash["how"] == "kept_both"
    assert clash["local_path"].startswith("100APPLE/IMG_1__phone-")
    assert (local / clash["local_path"]).read_bytes() == b"phone-bytes"
    assert (local / "100APPLE/IMG_1.JPG").read_bytes() == b"older-different-file"
    assert rows["100APPLE/IMG_2.JPG"]["how"] == "same"
    assert rows["100APPLE/IMG_3.JPG"]["how"] == "missing"

    before = sorted(p.name for p in (local / "100APPLE").iterdir())
    again = {r["phone_path"]: r for r in pp.reconcile(phone, local)}
    assert again["100APPLE/IMG_1.JPG"]["how"] == "kept_both"
    assert sorted(p.name for p in (local / "100APPLE").iterdir()) == before


def test_reconcile_same_bytes_different_mtime_is_same(pp, tmp_path):
    phone, local = tmp_path / "DCIM", tmp_path / "usb"
    put(phone / "A/IMG_1.HEIC", b"identical", 1_780_000_000)
    put(local / "A/IMG_1.HEIC", b"identical", 1_700_000_000)
    [r] = pp.reconcile(phone, local)
    assert (r["how"], r["local_path"]) == ("same", "A/IMG_1.HEIC")


def test_copy_no_overwrite_refuses_existing(pp, tmp_path):
    src = put(tmp_path / "a", b"new")
    dst = put(tmp_path / "b", b"old")
    with pytest.raises(FileExistsError):
        pp.copy_no_overwrite(src, dst)
    assert dst.read_bytes() == b"old"
    assert not any(p.name.startswith(".b.part") for p in tmp_path.iterdir())


# ------------------------------------------------------------------ verify
def test_verify_flags_size_mismatch_and_missing(pp, tmp_path):
    phone, local = tmp_path / "DCIM", tmp_path / "usb"
    put(phone / "A/ok.JPG", b"12345")
    put(local / "A/ok.JPG", b"12345")
    put(phone / "A/short.JPG", b"12345")
    put(local / "A/short.JPG", b"123")
    put(phone / "A/gone.JPG", b"12345")
    pull_map = [
        {"phone_path": "A/ok.JPG", "size": 5, "local_path": "A/ok.JPG", "how": "same"},
        {"phone_path": "A/short.JPG", "size": 5, "local_path": "A/short.JPG", "how": "same"},
        {"phone_path": "A/gone.JPG", "size": 5, "local_path": None, "how": "missing"},
    ]
    rows = {r["phone_path"]: r for r in pp.verify(pull_map, phone, local, use_exif=False)}
    assert rows["A/ok.JPG"]["status"] == "ok"
    assert len(rows["A/ok.JPG"]["sha256"]) == 64
    assert rows["A/ok.JPG"]["captured"]
    assert rows["A/short.JPG"]["status"] == "size_mismatch"
    assert rows["A/gone.JPG"]["status"] == "not_copied:missing"


def test_verify_hash_phone_catches_same_size_corruption(pp, tmp_path):
    phone, local = tmp_path / "DCIM", tmp_path / "usb"
    put(phone / "A/x.JPG", b"abcde")
    put(local / "A/x.JPG", b"abcdX")
    pull_map = [{"phone_path": "A/x.JPG", "size": 5, "local_path": "A/x.JPG", "how": "same"}]
    assert pp.verify(pull_map, phone, local, use_exif=False)[0]["status"] == "ok"
    assert pp.verify(pull_map, phone, local, hash_phone=True,
                     use_exif=False)[0]["status"] == "hash_mismatch"


def test_manifest_round_trip(pp, tmp_path):
    rows = [row("A/1.JPG", size=7)]
    pp.write_manifest(rows, tmp_path / "m.tsv")
    back = pp.read_manifest(tmp_path / "m.tsv")
    assert back[0]["size"] == 7 and back[0]["phone_path"] == "A/1.JPG"


# --------------------------------------------------------- safe to delete
def combined(tmp_path, name, lines):
    p = tmp_path / name
    p.write_text("".join(f"{mark} {path}\n" for mark, path in lines), encoding="utf-8")
    return p


def test_file_missing_on_drive_is_never_listed(pp, tmp_path):
    manifest = [row("A/1.JPG"), row("A/2.JPG"), row("A/3 with space.MOV", "video")]
    size = pp.parse_combined(combined(tmp_path, "s", [("=", "A/1.JPG"), ("+", "A/2.JPG"),
                                                      ("=", "A/3 with space.MOV")]))
    hashes = pp.parse_combined(combined(tmp_path, "h", [("=", "A/1.JPG"), ("+", "A/2.JPG"),
                                                        ("=", "A/3 with space.MOV")]))
    safe, unsafe = pp.safe_to_delete(manifest, size, hashes, "checked")
    assert [r["phone_path"] for r in safe] == ["A/1.JPG", "A/3 with space.MOV"]
    assert [(r["phone_path"], r["reason"]) for r in unsafe] == [
        ("A/2.JPG", "drive_size:missing_on_drive")]


@pytest.mark.parametrize("size_mark,hash_mark,reason", [
    ("*", "=", "drive_size:different_on_drive"),
    ("!", "=", "drive_size:drive_read_error"),
    (None, "=", "drive_size:not_checked"),
    ("=", "*", "drive_hash:different_on_drive"),
    ("=", "!", "drive_hash:drive_read_error"),
    ("=", None, "drive_hash:not_checked"),
])
def test_any_drive_doubt_keeps_file_off_list(pp, size_mark, hash_mark, reason):
    manifest = [row("A/1.JPG")]
    size = {"A/1.JPG": size_mark} if size_mark else {}
    hashes = {"A/1.JPG": hash_mark} if hash_mark else {}
    safe, unsafe = pp.safe_to_delete(manifest, size, hashes, "checked")
    assert safe == [] and unsafe[0]["reason"] == reason


def test_local_failure_beats_drive_pass(pp):
    manifest = [row("A/1.JPG", status="size_mismatch")]
    safe, unsafe = pp.safe_to_delete(manifest, {"A/1.JPG": "="}, {"A/1.JPG": "="}, "checked")
    assert safe == [] and unsafe[0]["reason"] == "local:size_mismatch"


def test_checks_not_run_mean_nothing_safe(pp, tmp_path):
    manifest = [row("A/1.JPG")]
    assert pp.safe_to_delete(manifest, None, None, "missing")[0] == []
    assert pp.safe_to_delete(manifest, {"A/1.JPG": "="}, None, "missing")[0] == []
    assert pp.hash_state(None, None) == "missing"


def test_no_common_hash_falls_back_to_size_only(pp, tmp_path):
    log = tmp_path / "check-hash.log"
    log.write_text("NOTICE: No common hash found - not using a hash for checks\n")
    hashes = pp.parse_combined(combined(tmp_path, "h", [("=", "A/1.JPG")]))
    assert pp.hash_state(hashes, log) == "unsupported"
    safe, _ = pp.safe_to_delete([row("A/1.JPG")], {"A/1.JPG": "="}, {}, "unsupported")
    assert len(safe) == 1


def test_safe_list_uses_kept_both_local_name(pp):
    r = row("A/IMG_1.JPG", local="A/IMG_1__phone-abcd1234.JPG")
    safe, _ = pp.safe_to_delete([r], {"A/IMG_1__phone-abcd1234.JPG": "="},
                                {"A/IMG_1__phone-abcd1234.JPG": "="}, "checked")
    assert len(safe) == 1
    safe, _ = pp.safe_to_delete([r], {"A/IMG_1.JPG": "="}, {"A/IMG_1.JPG": "="}, "checked")
    assert safe == []


def test_totals_and_cutoff(pp):
    manifest = [row("a", "photo", 100, captured="2026-06-01T09:00:00"),
                row("b", "video", 2_000, captured="2026-06-03T09:00:00"),
                row("c", "live_clip", 50, captured="2026-06-05T09:00:00"),
                row("d", "photo", 70, captured="2026-06-09T09:00:00")]
    safe, unsafe = manifest[:3], [{**manifest[3], "reason": "drive_size:missing_on_drive"}]
    t = pp.totals(safe)
    assert (t["all"]["count"], t["all"]["bytes"]) == (3, 2_150)
    assert (t["photo"]["bytes"], t["video"]["bytes"], t["live_clip"]["bytes"]) == (100, 2_000, 50)
    assert str(pp.cutoff(manifest, unsafe)) == "2026-06-08"
    assert str(pp.cutoff(manifest, [])) == "2026-06-09"
    assert pp.cutoff(manifest, [{**manifest[0], "reason": "x"}]) is None
    text = pp.safe_report("iphone-x", manifest, safe, unsafe, "checked", "2026-11-19")
    assert "Safe to delete: 3 files" in text and "2026-06-08" in text
    assert "Recently Deleted" in text


# ----------------------------------------------------------------- YouTube
def test_youtube_plan_thresholds_private_title(pp, tmp_path):
    manifest = [row("A/big.MOV", "video", 600_000_000, captured="2026-07-04T19:30:00"),
                row("A/long.MOV", "video", 10, captured="2026-07-05T08:00:00"),
                row("A/short.MOV", "video", 10),
                row("A/live.MOV", "live_clip", 900_000_000),
                row("A/bad.MOV", "video", 900_000_000, status="size_mismatch")]
    mins = {"big.MOV": 1.0, "long.MOV": 12.0, "short.MOV": 0.5}
    plan = pp.youtube_plan(manifest, tmp_path, 500, 10, minutes=lambda p: mins.get(p.name))
    assert [p["local_path"] for p in plan] == ["A/big.MOV", "A/long.MOV"]
    assert {p["privacy"] for p in plan} == {"private"}
    assert plan[0]["title"] == "2026-07-04 19:30"


# ---------------------------------------------------------- dry-run guard
def test_simulate_missing_refuses_outside_dry_run(pp, tmp_path):
    put(tmp_path / "drive/A/1.JPG", b"x")
    with pytest.raises(SystemExit):
        pp.simulate_missing(tmp_path / "drive", 1)
    (tmp_path / pp.DRYRUN_MARKER).touch()
    assert pp.simulate_missing(tmp_path / "drive", 1) == 1


# ------------------------------------------------------ end-to-end dry run
def _rclone():
    found = shutil.which("rclone")
    home = Path.home() / ".local/bin/rclone"
    return found or (str(home) if home.exists() else None)


@pytest.mark.skipif(sys.platform == "win32" or not shutil.which("rsync") or not _rclone(),
                    reason="needs Linux with rsync and rclone")
def test_dry_run_end_to_end(tmp_path):
    env = {**os.environ, "PATH": f"{Path(_rclone()).parent}:{os.environ['PATH']}"}
    res = subprocess.run(["bash", str(SCRIPT), "--dry-run", "--root", str(tmp_path / "arch"),
                          "--simulate-drive-missing", "1", "--youtube-plan",
                          "--youtube-min-mb", "0.2"],
                         capture_output=True, text=True, env=env, timeout=300, check=False)
    out = res.stdout + res.stderr
    # 8 fake phone files; the first (sorted) is dropped from the fake Drive.
    assert "Safe to delete: 7 files" in out, out
    assert "NOT safe (kept off the list): 1 files" in out, out
    assert "YouTube plan (not run): 2 videos" in out, out
    reports = tmp_path / "arch/iphone-dryrun/reports"
    [not_safe] = list(reports.glob("not-safe-*.tsv"))
    assert "drive_size:missing_on_drive" in not_safe.read_text()
    usb = tmp_path / "arch/iphone-dryrun/usb/100APPLE"
    assert any(p.name.startswith("IMG_0002__phone-") for p in usb.iterdir())
    assert (usb / "IMG_0002.JPG").stat().st_size == 12_345  # pre-existing file kept
    assert res.returncode == 10, out  # Drive check difference is reported


@pytest.mark.skipif(sys.platform == "win32" or not shutil.which("rsync") or not _rclone(),
                    reason="needs Linux with rsync and rclone")
def test_dry_run_clean_lists_everything(tmp_path):
    env = {**os.environ, "PATH": f"{Path(_rclone()).parent}:{os.environ['PATH']}"}
    res = subprocess.run(["bash", str(SCRIPT), "--dry-run", "--root", str(tmp_path / "arch")],
                         capture_output=True, text=True, env=env, timeout=300, check=False)
    out = res.stdout + res.stderr
    assert res.returncode == 0, out
    assert "Safe to delete: 8 files" in out, out
    assert "Everything taken on or before 2026-11-05 is backed up: 8 files" in out, out


def test_dry_run_refuses_live_root():
    if sys.platform == "win32":
        pytest.skip("bash script targets Linux")
    res = subprocess.run(["bash", str(SCRIPT), "--dry-run", "--root",
                          "/mnt/ace/ws/phone-media/x"],
                         capture_output=True, text=True, timeout=60, check=False)
    assert res.returncode != 0
    assert "refuses the live archive root" in res.stderr
