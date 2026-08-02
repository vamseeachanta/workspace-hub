"""Target-selection contract for scripts/legal/check-client-pii.py (#3775, Task 2).

A scanner that scanned NOTHING must never be indistinguishable from a scanner
that scanned everything and found nothing. Before #3775, passing a directory
expanded to zero files and exited 0 — a silent false PASS.

Synthetic sentinels only. No real client identifier appears in this file; every
test builds its own throwaway map in a tmp_path.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "legal" / "check-client-pii.py"

# Sentinels chosen so they cannot collide with anything real in this repo.
SENTINEL = "zzsynthclientalpha"
CODENAME = "client-synth-a"

SYNTH_MAP = f"""
version: 1
rules:
  - {{pattern: '{SENTINEL}', replacement: '{CODENAME}', word_bound: false}}
"""


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A throwaway git repo — the guard's domain is git-tracked files."""
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    _git(r, "config", "user.email", "t@example.invalid")
    _git(r, "config", "user.name", "t")
    (r / ".gitignore").write_text("ignored-*\n", encoding="utf-8")
    _git(r, "add", ".gitignore")
    _git(r, "commit", "-qm", "init")
    return r


@pytest.fixture()
def synth_map(tmp_path: Path) -> Path:
    p = tmp_path / "synth-map.yaml"
    p.write_text(SYNTH_MAP, encoding="utf-8")
    return p


def run_guard(repo: Path, synth_map: Path, *args: str, stdin: str | None = None):
    env = dict(os.environ)
    env.pop("LEGAL_PII_ALLOW", None)
    env.pop("LEGAL_CLIENT_MAP", None)
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--map", str(synth_map), *args],
        cwd=repo,
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
    )


def track(repo: Path, rel: str, body: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-qm", f"add {rel}")


# ── directories must not read as a silent PASS ────────────────────────────────


def test_directory_argument_detects_identifier_inside_it(repo, synth_map):
    """THE #3775 BUG: `check-client-pii.py somedir/` scanned nothing and exited 0."""
    track(repo, "d/doc.md", f"a line mentioning {SENTINEL} here\n")
    r = run_guard(repo, synth_map, "d")
    assert r.returncode == 1, f"directory scan missed the identifier: {r.stdout}{r.stderr}"


def test_directory_argument_never_claims_clean_when_dirty(repo, synth_map):
    """Property, not exit code: the word 'clean' must not appear for a dirty tree."""
    track(repo, "d/doc.md", f"{SENTINEL}\n")
    r = run_guard(repo, synth_map, "d")
    assert "clean" not in (r.stdout + r.stderr).lower()


def test_directory_argument_recurses(repo, synth_map):
    track(repo, "d/a/b/c/deep.md", f"deep {SENTINEL}\n")
    r = run_guard(repo, synth_map, "d")
    assert r.returncode == 1


def test_directory_argument_reports_the_files_it_actually_scanned(repo, synth_map):
    """A clean directory result must be backed by a non-zero scanned count."""
    track(repo, "d/one.md", "nothing here\n")
    track(repo, "d/two.md", "nor here\n")
    report = repo / "report.json"
    r = run_guard(repo, synth_map, "d", "--report-json", str(report))
    assert r.returncode == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["scanned"] == 2, data
    assert data["status"] == "clean"


def test_directory_expansion_skips_gitignored_files(repo, synth_map):
    """The private client map itself is gitignored and lives in a scanned dir.

    Expanding a directory over the working tree instead of the git index would
    scan the map and flag it forever. Expansion is tracked-files-only.
    """
    track(repo, "d/tracked.md", "clean content\n")
    (repo / "d" / "ignored-map.yaml").write_text(f"{SENTINEL}\n", encoding="utf-8")
    r = run_guard(repo, synth_map, "d")
    assert r.returncode == 0, f"scanned a gitignored file: {r.stdout}{r.stderr}"


def test_directory_with_no_tracked_files_is_not_a_pass(repo, synth_map):
    """Zero scannable files => inconclusive (2), never success (0)."""
    (repo / "empty").mkdir()
    (repo / "empty" / "ignored-x").write_text("hi\n", encoding="utf-8")
    r = run_guard(repo, synth_map, "empty")
    assert r.returncode == 2, f"{r.returncode}: {r.stdout}{r.stderr}"
    assert "clean" not in (r.stdout + r.stderr).lower()


# ── nonexistent paths ─────────────────────────────────────────────────────────


def test_nonexistent_path_is_an_error_not_a_pass(repo, synth_map):
    r = run_guard(repo, synth_map, "does/not/exist.md")
    assert r.returncode == 2
    assert "clean" not in (r.stdout + r.stderr).lower()


def test_one_missing_path_poisons_an_otherwise_clean_run(repo, synth_map):
    """A typo'd path in a list must not be silently dropped behind a green result."""
    track(repo, "ok.md", "fine\n")
    r = run_guard(repo, synth_map, "ok.md", "typo.md")
    assert r.returncode == 2


# ── the legitimate empty sets must still pass ─────────────────────────────────


def test_empty_staged_set_still_passes(repo, synth_map):
    """Nothing staged is a legitimate pre-commit pass — do not over-correct."""
    r = run_guard(repo, synth_map, "--staged")
    assert r.returncode == 0


def test_empty_diff_range_still_passes(repo, synth_map):
    """A PR that changed no scannable file is a legitimate CI pass."""
    r = run_guard(repo, synth_map, "--base-ref", "HEAD")
    assert r.returncode == 0


def test_explicit_clean_file_still_passes(repo, synth_map):
    track(repo, "ok.md", "nothing to see\n")
    r = run_guard(repo, synth_map, "ok.md")
    assert r.returncode == 0


def test_explicit_dirty_file_still_fails(repo, synth_map):
    track(repo, "bad.md", f"{SENTINEL}\n")
    r = run_guard(repo, synth_map, "bad.md")
    assert r.returncode == 1


# ── value withholding survives every new code path ────────────────────────────


def test_directory_hit_withholds_the_matched_value(repo, synth_map):
    track(repo, "d/doc.md", f"line with {SENTINEL} in it\n")
    r = run_guard(repo, synth_map, "d")
    blob = r.stdout + r.stderr
    assert SENTINEL not in blob
    assert CODENAME not in blob


def test_quiet_withholds_paths_as_well_as_values(repo, synth_map):
    """Public main-branch logs: a PATH can itself contain a client identifier."""
    track(repo, "d/doc.md", f"{SENTINEL}\n")
    r = run_guard(repo, synth_map, "d", "--quiet")
    blob = r.stdout + r.stderr
    assert r.returncode == 1
    assert SENTINEL not in blob
    assert CODENAME not in blob
    assert "d/doc.md" not in blob, "quiet mode leaked a file path"
    assert "doc.md" not in blob, "quiet mode leaked a file name"


def test_quiet_still_reports_that_something_was_found(repo, synth_map):
    track(repo, "d/a.md", f"{SENTINEL}\n")
    track(repo, "d/b.md", f"{SENTINEL}\n")
    report = repo / "r.json"
    r = run_guard(repo, synth_map, "d", "--quiet", "--report-json", str(report))
    assert r.returncode == 1
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["files_flagged"] == 2
    assert data["status"] == "violations"


# ── the machine-readable report the main-branch job consumes ──────────────────


def test_report_json_is_path_free(repo, synth_map):
    """The report is posted to a PUBLIC issue — it must carry no paths at all."""
    track(repo, "d/secretname.md", f"{SENTINEL}\n")
    report = repo / "r.json"
    run_guard(repo, synth_map, "d", "--quiet", "--report-json", str(report))
    raw = report.read_text(encoding="utf-8")
    assert "secretname" not in raw
    assert SENTINEL not in raw
    assert CODENAME not in raw
    data = json.loads(raw)
    assert set(data) == {"status", "scanned", "files_flagged", "fingerprint"}


def test_report_fingerprint_changes_when_the_flagged_set_changes(repo, synth_map):
    """Dedup key for issue escalation: same finding => same fingerprint."""
    track(repo, "d/a.md", f"{SENTINEL}\n")
    r1 = repo / "r1.json"
    run_guard(repo, synth_map, "d", "--quiet", "--report-json", str(r1))
    r2 = repo / "r2.json"
    run_guard(repo, synth_map, "d", "--quiet", "--report-json", str(r2))
    fp1 = json.loads(r1.read_text())["fingerprint"]
    fp2 = json.loads(r2.read_text())["fingerprint"]
    assert fp1 and fp1 == fp2

    track(repo, "d/b.md", f"{SENTINEL}\n")
    r3 = repo / "r3.json"
    run_guard(repo, synth_map, "d", "--quiet", "--report-json", str(r3))
    assert json.loads(r3.read_text())["fingerprint"] != fp1


def test_report_written_even_when_the_run_is_inconclusive(repo, synth_map):
    """The workflow reads this file unconditionally — it must always exist."""
    missing_map = repo / "no-such-map.yaml"
    report = repo / "r.json"
    env = dict(os.environ)
    env.pop("LEGAL_PII_ALLOW", None)
    r = subprocess.run(
        [
            sys.executable, str(SCRIPT), "--map", str(missing_map), "--strict",
            "--all", "--report-json", str(report),
        ],
        cwd=repo, capture_output=True, text=True, env=env,
    )
    assert r.returncode == 2
    assert json.loads(report.read_text(encoding="utf-8"))["status"] == "inconclusive"


def test_report_status_inconclusive_when_nothing_was_scanned(repo, synth_map):
    (repo / "empty").mkdir()
    report = repo / "r.json"
    r = run_guard(repo, synth_map, "empty", "--report-json", str(report))
    assert r.returncode == 2
    assert json.loads(report.read_text(encoding="utf-8"))["status"] == "inconclusive"


# ── --all keeps its meaning ───────────────────────────────────────────────────


def test_all_mode_scans_the_tracked_tree(repo, synth_map):
    track(repo, "nested/deep/file.md", f"{SENTINEL}\n")
    r = run_guard(repo, synth_map, "--all")
    assert r.returncode == 1


def test_all_mode_clean_repo_passes_with_nonzero_scanned(repo, synth_map):
    track(repo, "a.md", "fine\n")
    report = repo / "r.json"
    r = run_guard(repo, synth_map, "--all", "--report-json", str(report))
    assert r.returncode == 0
    assert json.loads(report.read_text(encoding="utf-8"))["scanned"] >= 2
