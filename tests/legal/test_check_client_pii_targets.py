"""Explicit-target contract for scripts/legal/check-client-pii.py.

A scanner that scanned nothing must never be indistinguishable from a scanner
that scanned everything and found nothing. Before this fix a directory argument
was skipped by the regular-file filter and the run still printed
"1 changed file(s) clean" with exit 0: a silent false PASS.

Contract:
- a directory argument expands to the git-tracked files beneath it (recursive,
  tracked only, so a gitignored private map inside it is never read);
- a directory with no tracked files, or a path that does not exist, exits 2
  (inconclusive) and never prints "clean";
- the legitimate empty sets (nothing staged, empty diff range) still pass.

Synthetic sentinels only; every test builds its own throwaway map and repo.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "legal" / "check-client-pii.py"

SENTINEL = "zzsynthclientalpha"
CODENAME = "client-synth-a"
SYNTH_MAP = f"""
version: 1
rules:
  - {{pattern: '{SENTINEL}', replacement: '{CODENAME}', word_bound: false}}
"""

_GIT_BINDINGS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE")


def _env() -> dict[str, str]:
    env = dict(os.environ)
    for key in ("LEGAL_PII_ALLOW", "LEGAL_CLIENT_MAP", *_GIT_BINDINGS):
        env.pop(key, None)
    return env


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                   text=True, env=_env())


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
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


def run_guard(repo: Path, synth_map: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--map", str(synth_map), *args],
        cwd=repo, capture_output=True, text=True, env=_env(),
    )


def track(repo: Path, rel: str, body: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-qm", f"add {rel}")


def test_directory_argument_detects_identifier_inside_it(repo, synth_map):
    track(repo, "d/doc.md", f"a line mentioning {SENTINEL} here\n")
    r = run_guard(repo, synth_map, "d")
    assert r.returncode == 1, f"directory scan missed the identifier: {r.stdout}{r.stderr}"
    assert "clean" not in (r.stdout + r.stderr).lower()


def test_directory_argument_recurses(repo, synth_map):
    track(repo, "d/a/b/c/deep.md", f"deep {SENTINEL}\n")
    assert run_guard(repo, synth_map, "d").returncode == 1


def test_directory_argument_reports_files_actually_scanned(repo, synth_map):
    track(repo, "d/one.md", "nothing here\n")
    track(repo, "d/two.md", "nor here\n")
    r = run_guard(repo, synth_map, "d")
    assert r.returncode == 0, r.stderr
    assert "2 file(s)" in r.stdout, r.stdout


def test_directory_expansion_skips_gitignored_files(repo, synth_map):
    track(repo, "d/tracked.md", "clean content\n")
    (repo / "d" / "ignored-map.yaml").write_text(f"{SENTINEL}\n", encoding="utf-8")
    r = run_guard(repo, synth_map, "d")
    assert r.returncode == 0, f"scanned a gitignored file: {r.stdout}{r.stderr}"


def test_directory_with_no_tracked_files_is_not_a_pass(repo, synth_map):
    (repo / "empty").mkdir()
    (repo / "empty" / "ignored-x").write_text("hi\n", encoding="utf-8")
    r = run_guard(repo, synth_map, "empty")
    assert r.returncode == 2, f"{r.returncode}: {r.stdout}{r.stderr}"
    assert "clean" not in (r.stdout + r.stderr).lower()


def test_repo_root_dot_expands_to_tracked_tree(repo, synth_map):
    track(repo, "x/doc.md", f"{SENTINEL}\n")
    assert run_guard(repo, synth_map, ".").returncode == 1


def test_nonexistent_path_is_an_error_not_a_pass(repo, synth_map):
    r = run_guard(repo, synth_map, "does/not/exist.md")
    assert r.returncode == 2
    assert "clean" not in (r.stdout + r.stderr).lower()


def test_one_missing_path_poisons_an_otherwise_clean_run(repo, synth_map):
    track(repo, "ok.md", "fine\n")
    assert run_guard(repo, synth_map, "ok.md", "typo.md").returncode == 2


def test_empty_staged_set_still_passes(repo, synth_map):
    assert run_guard(repo, synth_map, "--staged").returncode == 0


def test_empty_diff_range_still_passes(repo, synth_map):
    assert run_guard(repo, synth_map, "--base-ref", "HEAD").returncode == 0


def test_explicit_clean_file_still_passes(repo, synth_map):
    track(repo, "ok.md", "nothing to see\n")
    assert run_guard(repo, synth_map, "ok.md").returncode == 0


def test_explicit_dirty_file_still_fails(repo, synth_map):
    track(repo, "bad.md", f"{SENTINEL}\n")
    assert run_guard(repo, synth_map, "bad.md").returncode == 1


def test_directory_hit_withholds_the_matched_value(repo, synth_map):
    track(repo, "d/doc.md", f"line with {SENTINEL} in it\n")
    r = run_guard(repo, synth_map, "d")
    blob = r.stdout + r.stderr
    assert SENTINEL not in blob
    assert CODENAME not in blob
