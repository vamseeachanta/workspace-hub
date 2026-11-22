"""Synthetic examples; calendar destinations are independently read from input dates."""

import importlib.util
import json
import os
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "phone_media", Path(__file__).parents[2] / "scripts/utilities/phone_media.py"
)
media = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(media)


def put(root, phone, name, content=b"image"):
    path = root / phone / "usb" / "100APPLE" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    # Independent hand calculation: Unix epoch zero is 1970-01-01 UTC.
    os.utime(path, (0, 0))
    return path


def test_dates_sidecars_and_preservation(tmp_path):
    """2024:02:29 is in calendar directory 2024/02; all paired files follow it."""
    root, output = tmp_path / "input", tmp_path / "output"
    photo = put(root, "phone-a", "IMG.JPG")
    sidecar = put(root, "phone-a", "img.AAE", b"edits")
    put(root, "phone-a", "IMG.MOV", b"video")
    reader = lambda path: {"DateTimeOriginal": "2024:02:29 10:20:30"}
    report = media.organize(root, output, metadata_reader=reader)
    assert not output.exists()
    assert {r["date_source"] for r in report["files"]} == {
        "DateTimeOriginal",
        "paired:DateTimeOriginal",
    }
    applied = media.organize(root, output, apply=True, metadata_reader=reader)
    assert len(applied["files"]) == 3
    for source in (photo, sidecar):
        target = output / "2024/02/phone-a/100APPLE" / source.name
        assert target.read_bytes() == source.read_bytes()
        assert target.stat().st_mtime_ns == source.stat().st_mtime_ns
    assert (
        media.organize(root, output, apply=True, metadata_reader=reader)["files"]
        == applied["files"]
    )


def test_fallback_formats_and_cross_phone_duplicates(tmp_path):
    """Equal literal bytes on two phones form one group; same-phone copies alone do not."""
    root = tmp_path / "input"
    for extension in ("HEIC", "MOV", "PNG", "JPG", "jpeg", "AAE"):
        put(root, "phone-a", f"asset.{extension}", extension.encode())
    put(root, "phone-b", "copy.HEIC", b"HEIC")
    put(root, "phone-a", "other.JPG", b"JPG")
    report = media.organize(root, tmp_path / "out", metadata_reader=lambda p: {})
    assert len(report["files"]) == 8
    assert all(r["destination"].startswith("1970/01/") for r in report["files"])
    assert len(report["duplicates"]) == 1
    assert len(report["duplicates"][0]["files"]) == 2
    assert any("orphan" in w for w in report["warnings"]) is False


def test_bad_metadata_and_orphan(tmp_path):
    root = tmp_path / "input"
    put(root, "phone-a", "orphan.AAE")
    put(root, "phone-a", "pic.PNG")
    report = media.organize(
        root,
        tmp_path / "out",
        metadata_reader=lambda p: {
            "DateTimeOriginal": "2023:02:29 10:00:00",
            "CreateDate": "2022:12:31 23:59:59",
        },
    )
    photo = next(r for r in report["files"] if r["source"].endswith("PNG"))
    assert photo["destination"].startswith("2022/12/")
    assert any("orphan" in w for w in report["warnings"])
    assert any("invalid DateTimeOriginal" in w for w in report["warnings"])


def test_no_overwrite(tmp_path):
    root, out = tmp_path / "input", tmp_path / "out"
    source = put(root, "phone-a", "pic.JPG")
    report = media.organize(root, out, metadata_reader=lambda p: {})
    dest = out / report["files"][0]["destination"]
    dest.parent.mkdir(parents=True)
    dest.write_bytes(b"different")
    with pytest.raises(FileExistsError):
        media.organize(root, out, apply=True, metadata_reader=lambda p: {})
    assert dest.read_bytes() == b"different"
    assert source.read_bytes() == b"image"


@pytest.mark.parametrize("inside", [True, False])
def test_overlapping_roots(tmp_path, inside):
    root = tmp_path / "input"
    put(root, "phone-a", "pic.JPG")
    with pytest.raises(ValueError, match="overlap"):
        media.organize(root, root / "out" if inside else tmp_path)


def test_source_symlink_rejected(tmp_path):
    root = tmp_path / "input"
    source = put(root, "phone-a", "pic.JPG")
    source.with_name("link.JPG").symlink_to(source)
    with pytest.raises(ValueError, match="symlink"):
        media.organize(root, tmp_path / "out", metadata_reader=lambda p: {})


def test_destination_symlink_rejected(tmp_path):
    root, out = tmp_path / "input", tmp_path / "out"
    put(root, "phone-a", "pic.JPG")
    out.mkdir()
    (out / "1970").symlink_to(root, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        media.organize(root, out, apply=True, metadata_reader=lambda p: {})


def test_exiftool_reader(tmp_path, monkeypatch):
    """ExifTool JSON mode returns tag strings; filenames are passed after --."""

    def run(args, **kwargs):
        assert args[-2:] == ["--", str(tmp_path / "pic.HEIC")]

        class Result:
            stdout = json.dumps([{"DateTimeOriginal": "2024:01:02 03:04:05"}])

        return Result()

    monkeypatch.setattr(media.subprocess, "run", run)
    assert media.read_metadata(tmp_path / "pic.HEIC")["DateTimeOriginal"].startswith(
        "2024:"
    )


def test_missing_metadata_tool_falls_back(tmp_path):
    root = tmp_path / "input"
    put(root, "phone-a", "pic.HEIC")

    def missing(path):
        raise FileNotFoundError("tool absent")

    report = media.organize(root, tmp_path / "out", metadata_reader=missing)
    assert report["files"][0]["date_source"] == "mtime_utc"
    assert report["warnings"] == [
        "phone-a/usb/100APPLE/pic.HEIC: metadata unavailable (FileNotFoundError); using mtime"
    ]


def test_same_names_in_different_camera_folders(tmp_path):
    """Folder identity disambiguates identical filenames without suffix guessing."""
    root, out = tmp_path / "input", tmp_path / "out"
    original = put(root, "phone-a", "pic.JPG", b"one")
    other = original.parent.parent / "101APPLE" / original.name
    other.parent.mkdir()
    other.write_bytes(b"two")
    os.utime(other, (0, 0))
    report = media.organize(root, out, apply=True, metadata_reader=lambda p: {})
    assert len({r["destination"] for r in report["files"]}) == 2
    assert {(out / r["destination"]).read_bytes() for r in report["files"]} == {
        b"one",
        b"two",
    }


def test_changed_source_during_copy_is_detected(tmp_path, monkeypatch):
    root, out = tmp_path / "input", tmp_path / "out"
    source = put(root, "phone-a", "pic.JPG")
    original = media.copy_verified

    def change(incoming, target, expected):
        source.write_bytes(b"changed")
        original(incoming, target, expected)

    monkeypatch.setattr(media, "copy_verified", change)
    with pytest.raises(OSError, match="digest mismatch"):
        media.organize(root, out, apply=True, metadata_reader=lambda p: {})
    # A failed copy is retained for inspection, never silently accepted or deleted.
    assert (out / "1970/01/phone-a/100APPLE/pic.JPG").read_bytes() == b"changed"


def test_whole_plan_preflight_before_copy(tmp_path):
    root, out = tmp_path / "input", tmp_path / "out"
    put(root, "phone-a", "a.JPG")
    put(root, "phone-a", "z.JPG")
    target = out / "1970/01/phone-a/100APPLE/z.JPG"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"conflict")
    with pytest.raises(FileExistsError):
        media.organize(root, out, apply=True, metadata_reader=lambda p: {})
    assert not target.with_name("a.JPG").exists()


def test_capture_local_month_and_mov_fallback(tmp_path):
    """Local March remains March despite a UTC offset; container CreateDate is next priority."""
    root = tmp_path / "input"
    put(root, "phone-a", "pic.JPG")
    put(root, "phone-a", "video.MOV")

    def reader(path):
        if path.suffix == ".JPG":
            return {"DateTimeOriginal": "2024:03:01 00:01:00+12:00"}
        return {"MediaCreateDate": "2021:07:04 01:02:03"}

    report = media.organize(root, tmp_path / "out", metadata_reader=reader)
    assert [r["destination"].split("/")[:2] for r in report["files"]] == [
        ["2024", "03"],
        ["2021", "07"],
    ]


def test_cli_dry_run(tmp_path, monkeypatch, capsys):
    root, out = tmp_path / "input", tmp_path / "out"
    put(root, "phone-a", "pic.JPG")
    monkeypatch.setenv("PATH", "")
    assert media.main([str(root), str(out)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["mode"] == "dry_run"
    assert report["files"][0]["date_source"] == "mtime_utc"
    assert not out.exists()


@pytest.mark.parametrize("keys_date", [True, False])
def test_live_photo_month_boundary(tmp_path, keys_date):
    """The still is February locally; the container timestamp is March in UTC."""
    root = tmp_path / "input"
    for name in ("IMG.HEIC", "IMG.MOV", "IMG.AAE"):
        put(root, "phone-a", name)

    def reader(path):
        if path.suffix == ".HEIC":
            return {"DateTimeOriginal": "2024:02:29 20:00:00-06:00"}
        tags = {"CreateDate": "2024:03:01 02:00:00"}
        if keys_date:
            tags["CreationDate"] = "2024:02:29 20:00:00-06:00"
        return tags

    report = media.organize(root, tmp_path / "out", metadata_reader=reader)
    records = {Path(r["source"]).suffix: r for r in report["files"]}
    assert records[".HEIC"]["destination"].startswith("2024/02/")
    assert records[".AAE"]["destination"].startswith("2024/02/")
    mov = records[".MOV"]
    assert mov["date_source"] == ("CreationDate" if keys_date else "CreateDate_utc")
    assert mov["destination"].startswith("2024/02/" if keys_date else "2024/03/")
    assert bool(report["warnings"]) == (not keys_date)
    if not keys_date:
        assert "companions span months; paired with IMG.HEIC" in report["warnings"][0]


def test_dry_run_lists_all_conflicts(tmp_path):
    root, out = tmp_path / "input", tmp_path / "out"
    for name in ("a.JPG", "z.JPG"):
        put(root, "phone-a", name)
        target = out / "1970/01/phone-a/100APPLE" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"truncated")
    report = media.organize(root, out, metadata_reader=lambda p: {})
    assert report["conflicts"] == [
        {
            "destination": f"1970/01/phone-a/100APPLE/{name}",
            "reason": "destination differs; no overwrite permitted",
        }
        for name in ("a.JPG", "z.JPG")
    ]
    assert all(
        (out / r["destination"]).read_bytes() == b"truncated"
        for r in report["conflicts"]
    )


def test_cli_conflict_failure(tmp_path, monkeypatch, capsys):
    root, out = tmp_path / "input", tmp_path / "out"
    put(root, "phone-a", "pic.JPG")
    relative = "1970/01/phone-a/100APPLE/pic.JPG"
    target = out / relative
    target.parent.mkdir(parents=True)
    target.write_bytes(b"partial")
    monkeypatch.setenv("PATH", "")
    assert media.main([str(root), str(out)]) == 0
    assert (
        json.loads(capsys.readouterr().out)["conflicts"][0]["destination"] == relative
    )
    with pytest.raises(SystemExit) as exc:
        media.main([str(root), str(out), "--apply"])
    assert exc.value.code == 1
    error = capsys.readouterr().err
    assert relative in error
    assert "no overwrite permitted" in error
    assert str(tmp_path) not in error
    assert target.read_bytes() == b"partial"


def test_cli_invalid_input_reason(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        media.main([str(tmp_path / "missing"), str(tmp_path / "out")])
    assert exc.value.code == 1
    error = capsys.readouterr().err
    assert "input root must be a directory" in error
    assert str(tmp_path) not in error


def test_cli_copy_failure_identifies_inspection_file(tmp_path, monkeypatch, capsys):
    root, out = tmp_path / "input", tmp_path / "out"
    put(root, "phone-a", "pic.JPG")
    original = media.shutil.copyfileobj

    def corrupt(incoming, outgoing):
        original(incoming, outgoing)
        outgoing.write(b"incomplete")

    monkeypatch.setattr(media.shutil, "copyfileobj", corrupt)
    monkeypatch.setenv("PATH", "")
    with pytest.raises(SystemExit):
        media.main([str(root), str(out), "--apply"])
    error = capsys.readouterr().err
    assert "1970/01/phone-a/100APPLE/pic.JPG" in error
    assert "digest mismatch; destination retained for inspection" in error
    assert str(tmp_path) not in error


@pytest.mark.parametrize("level", ["phone", "usb"])
def test_source_ancestor_symlink_rejected(tmp_path, level):
    root = tmp_path / "input"
    put(root, "phone-a", "pic.JPG")
    if level == "phone":
        link = root / "phone-b"
        target = root / "phone-a"
    else:
        link = root / "phone-b" / "usb"
        link.parent.mkdir()
        target = root / "phone-a" / "usb"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="source symlink"):
        media.organize(root, tmp_path / "out")


def test_output_ancestor_symlink_rejected(tmp_path):
    root = tmp_path / "input"
    put(root, "phone-a", "pic.JPG")
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "alias"
    link.symlink_to(real, target_is_directory=True)
    with pytest.raises(ValueError, match="destination symlink"):
        media.organize(root, link / "out")


@pytest.mark.parametrize("value", [{}, [], [1], [{}, {}]])
def test_exiftool_json_shape_rejected(tmp_path, monkeypatch, value):
    from types import SimpleNamespace

    monkeypatch.setattr(
        media.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(stdout=json.dumps(value)),
    )
    with pytest.raises(ValueError, match="unexpected ExifTool JSON structure"):
        media.read_metadata(tmp_path / "pic.JPG")


def test_exiftool_uses_utf8_and_keys_creation_date(tmp_path, monkeypatch):
    from types import SimpleNamespace

    def run(args, **kwargs):
        assert kwargs.get("encoding") == "utf-8"
        assert "-Keys:CreationDate" in args
        return SimpleNamespace(stdout='[{"SourceFile": "café.MOV"}]')

    monkeypatch.setattr(media.subprocess, "run", run)
    assert media.read_metadata(tmp_path / "café.MOV")["SourceFile"] == "café.MOV"


@pytest.mark.parametrize("location", ["phone", "usb", "nested", "output", "target"])
def test_reparse_point_rejected(tmp_path, monkeypatch, location):
    from types import SimpleNamespace

    root, out = tmp_path / "input", tmp_path / "out"
    source = put(root, "phone-a", "pic.JPG")
    target = out / "1970/01/phone-a/100APPLE/pic.JPG"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"image")
    selected = {
        "phone": root / "phone-a",
        "usb": root / "phone-a/usb",
        "nested": source.parent,
        "output": out,
        "target": target,
    }[location]
    original = Path.lstat

    def lstat(path, *args, **kwargs):
        result = original(path, *args, **kwargs)
        if path == selected:
            return SimpleNamespace(st_mode=result.st_mode, st_file_attributes=0x400)
        return result

    monkeypatch.setattr(Path, "lstat", lstat)
    with pytest.raises(ValueError, match="reparse point"):
        media.organize(root, out, apply=True, metadata_reader=lambda p: {})
    assert target.read_bytes() == b"image"
    assert source.read_bytes() == b"image"


def test_non_phone_entries_ignored(tmp_path):
    root = tmp_path / "input"
    put(root, "phone-a", "pic.JPG")
    (root / "notes.txt").write_text("archive notes")
    report = media.organize(root, tmp_path / "out", metadata_reader=lambda p: {})
    assert len(report["files"]) == 1


def test_cli_native_copy_error_uses_relative_destination(tmp_path, monkeypatch, capsys):
    root, out = tmp_path / "input", tmp_path / "out"
    source = put(root, "phone-a", "pic.JPG")

    def denied(incoming, outgoing):
        raise PermissionError(13, "Permission denied", str(source))

    monkeypatch.setattr(media.shutil, "copyfileobj", denied)
    monkeypatch.setenv("PATH", "")
    with pytest.raises(SystemExit) as exc:
        media.main([str(root), str(out), "--apply"])
    assert exc.value.code == 1
    error = capsys.readouterr().err
    assert "1970/01/phone-a/100APPLE/pic.JPG" in error
    assert "Permission denied" in error
    assert str(tmp_path) not in error
