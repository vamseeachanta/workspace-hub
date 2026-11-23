"""Tests for the #3298 session-publish step in scripts/build_pages.py.

Verifies the Pages builder copies the session index + each manifest-enumerated
page (no glob) into public/sessions/, preserving the relative tree.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_build_pages(public_dir: Path, sessions_src: Path):
    spec = importlib.util.spec_from_file_location(
        "build_pages_under_test", ROOT / "scripts" / "build_pages.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # redirect module globals at the paths it copies from/to
    mod.PUBLIC = public_dir
    mod.SESSIONS_SRC = sessions_src
    return mod


def test_build_sessions_copies_index_and_enumerated_pages(tmp_path):
    src = tmp_path / "sessions"
    src.mkdir()
    (src / "index.html").write_text("<html>idx</html>", encoding="utf-8")
    (src / "2026-06-28-demo.html").write_text("<html>page</html>", encoding="utf-8")
    (src / "manifest.json").write_text(
        json.dumps([{"slug": "demo", "date": "2026-06-28", "file": "2026-06-28-demo.html"}]),
        encoding="utf-8")

    public = tmp_path / "public"
    public.mkdir()
    mod = _load_build_pages(public, src)
    built = mod.build_sessions()

    assert "sessions/index.html" in built
    assert "sessions/2026-06-28-demo.html" in built
    assert (public / "sessions" / "index.html").exists()
    assert (public / "sessions" / "2026-06-28-demo.html").read_text() == "<html>page</html>"


def test_build_sessions_noop_without_manifest(tmp_path):
    src = tmp_path / "sessions"
    src.mkdir()
    public = tmp_path / "public"
    public.mkdir()
    mod = _load_build_pages(public, src)
    assert mod.build_sessions() == []


def test_build_sessions_skips_missing_file_listed_in_manifest(tmp_path):
    src = tmp_path / "sessions"
    src.mkdir()
    (src / "index.html").write_text("idx", encoding="utf-8")
    (src / "manifest.json").write_text(
        json.dumps([{"slug": "gone", "date": "2026-06-28", "file": "missing.html"}]),
        encoding="utf-8")
    public = tmp_path / "public"
    public.mkdir()
    mod = _load_build_pages(public, src)
    built = mod.build_sessions()
    assert built == ["sessions/index.html"]  # missing page skipped, no crash
