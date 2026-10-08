"""Tests for scripts/review/build-review-packet.py (#3973 R4).

A review packet inlines the exact bytes under review, with per-file SHA-256,
so a reviewer that cannot spawn processes still reviews a pinned target, and
`verify` invalidates the verdict if any reviewed file changed afterwards.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "review" / "build-review-packet.py"


def run(*args, cwd):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8")


def make(tmp_path, name, data: bytes):
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p


def test_build_inlines_numbered_lines_and_raw_byte_digests(tmp_path):
    raw = b"alpha\r\nbeta\r\n"
    make(tmp_path, "src/a.py", raw)
    r = run("build", "--out", "packet.md", "--manifest", "m.json", "src/a.py", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    packet = (tmp_path / "packet.md").read_text(encoding="utf-8")
    assert "src/a.py" in packet
    assert "   1 | alpha" in packet and "   2 | beta" in packet
    digest = hashlib.sha256(raw).hexdigest()
    assert digest in packet
    manifest = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    assert manifest["files"][0] == {"path": "src/a.py", "sha256": digest, "bytes": len(raw)}
    assert manifest["digest_domain"] == "raw-bytes"


def test_verify_passes_when_unchanged(tmp_path):
    make(tmp_path, "a.txt", b"x\n")
    assert run("build", "--out", "p.md", "--manifest", "m.json", "a.txt", cwd=tmp_path).returncode == 0
    r = run("verify", "--manifest", "m.json", cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(r.stdout)["status"] == "unchanged"


def test_verify_fails_and_names_changed_and_missing_files(tmp_path):
    make(tmp_path, "a.txt", b"x\n")
    make(tmp_path, "b.txt", b"y\n")
    assert run("build", "--out", "p.md", "--manifest", "m.json", "a.txt", "b.txt", cwd=tmp_path).returncode == 0
    (tmp_path / "a.txt").write_bytes(b"x changed\n")
    (tmp_path / "b.txt").unlink()
    r = run("verify", "--manifest", "m.json", cwd=tmp_path)
    assert r.returncode == 3
    out = json.loads(r.stdout)
    assert out["status"] == "changed"
    assert out["changed"] == ["a.txt"] and out["missing"] == ["b.txt"]


def test_line_ending_change_alone_invalidates(tmp_path):
    make(tmp_path, "a.txt", b"x\n")
    assert run("build", "--out", "p.md", "--manifest", "m.json", "a.txt", cwd=tmp_path).returncode == 0
    (tmp_path / "a.txt").write_bytes(b"x\r\n")
    assert run("verify", "--manifest", "m.json", cwd=tmp_path).returncode == 3


def test_size_budget_refuses_instead_of_truncating(tmp_path):
    make(tmp_path, "big.txt", b"z" * 5000 + b"\n")
    r = run("build", "--out", "p.md", "--manifest", "m.json", "--max-bytes", "1000", "big.txt", cwd=tmp_path)
    assert r.returncode == 2
    assert "budget" in r.stderr.lower()
    assert not (tmp_path / "p.md").exists() and not (tmp_path / "m.json").exists()


def test_missing_and_binary_inputs_are_refused(tmp_path):
    assert run("build", "--out", "p.md", "--manifest", "m.json", "nope.txt", cwd=tmp_path).returncode == 1
    make(tmp_path, "bin.dat", b"\xff\xfe\x00\x81")
    r = run("build", "--out", "p.md", "--manifest", "m.json", "bin.dat", cwd=tmp_path)
    assert r.returncode == 1 and "utf-8" in r.stderr.lower()
    assert not (tmp_path / "p.md").exists()


def test_fence_is_longer_than_any_backtick_run_in_content(tmp_path):
    make(tmp_path, "doc.md", b"text\n````\ncode\n````\n")
    assert run("build", "--out", "p.md", "--manifest", "m.json", "doc.md", cwd=tmp_path).returncode == 0
    packet = (tmp_path / "p.md").read_text(encoding="utf-8")
    assert "\n`````" in packet  # 5-backtick fence wraps content containing a 4-backtick run


def test_line_numbers_match_editor_lines_with_form_feed(tmp_path):
    make(tmp_path, "a.txt", b"one\x0ctwo\nthree\n")  # str.splitlines() would split at \x0c
    assert run("build", "--out", "p.md", "--manifest", "m.json", "a.txt", cwd=tmp_path).returncode == 0
    packet = (tmp_path / "p.md").read_text(encoding="utf-8")
    assert "   2 | three" in packet and "2 lines" in packet


def test_verify_refuses_tampered_manifest_path_outside_root(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    make(tmp_path, "outside.txt", b"x\n")
    digest = hashlib.sha256(b"x\n").hexdigest()
    (root / "m.json").write_text(json.dumps({"schema": "review-packet/1", "files": [{"path": "../outside.txt", "sha256": digest, "bytes": 2}]}),
                                 encoding="utf-8")
    r = run("verify", "--manifest", "m.json", cwd=root)
    assert r.returncode == 1 and "outside" in r.stderr.lower()


def test_verify_rejects_empty_or_malformed_manifest(tmp_path):
    for body in ({}, {"schema": "review-packet/1", "files": []},
                 {"schema": "review-packet/1", "files": [{"path": "a.txt", "sha256": "nothex"}]}):
        (tmp_path / "m.json").write_text(json.dumps(body), encoding="utf-8")
        r = run("verify", "--manifest", "m.json", cwd=tmp_path)
        assert r.returncode == 1, body


def test_outputs_may_not_overwrite_inputs_or_each_other(tmp_path):
    make(tmp_path, "a.py", b"keep\n")
    r = run("build", "--out", "a.py", "--manifest", "m.json", "a.py", cwd=tmp_path)
    assert r.returncode == 1 and (tmp_path / "a.py").read_bytes() == b"keep\n"
    r = run("build", "--out", "same.md", "--manifest", "same.md", "a.py", cwd=tmp_path)
    assert r.returncode == 1 and not (tmp_path / "same.md").exists()


def test_manifest_binds_packet_digest(tmp_path):
    make(tmp_path, "a.txt", b"x\n")
    assert run("build", "--out", "p.md", "--manifest", "m.json", "a.txt", cwd=tmp_path).returncode == 0
    m = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    assert m["packet_sha256"] == hashlib.sha256((tmp_path / "p.md").read_bytes()).hexdigest()


def test_path_outside_root_is_refused(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    make(tmp_path, "outside.txt", b"x\n")
    r = run("build", "--out", "p.md", "--manifest", "m.json", "../outside.txt", cwd=root)
    assert r.returncode == 1 and "outside" in r.stderr.lower()
