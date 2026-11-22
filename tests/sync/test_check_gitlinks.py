"""Read-only gitlink checks using disposable indexes, with no commits or remotes.

Fixture modes and object IDs follow Git's index-format and git-update-index
manuals: 160000 denotes a gitlink, 100644 a regular file, stage 0 a resolved
entry, and a SHA-1 object name has 40 hexadecimal digits. Exit expectations
follow the diagnostic contract documented in README-sync-ecosystem.md.
"""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/sync/check_gitlinks.py"
GITLINK_MODE = "160000"
FILE_MODE = "100644"
# A gitlink can reference an unavailable commit; no commit object is needed.
COMMIT_OID = "1" * 40


def _git(repo, env, *args, data=None):
    result = subprocess.run(
        ["git", *args], cwd=repo, env=env, input=data, capture_output=True,
        check=True,
    )
    return result.stdout


@pytest.fixture
def repository(tmp_path):
    # Inherited repository bindings must never redirect fixture writes.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0")
    repo = tmp_path / "repository"
    repo.mkdir()
    _git(repo, env, "init", "--quiet", "--object-format=sha1")
    env["GIT_INDEX_FILE"] = str(repo / ".git" / "fixture-index")
    _git(repo, env, "read-tree", "--empty")
    return repo, env


def _index(repository, paths=(), metadata=None):
    repo, env = repository
    entries = [(GITLINK_MODE, COMMIT_OID, path) for path in paths]
    if metadata is not None:
        oid = _git(repo, env, "hash-object", "-w", "--stdin", data=metadata).strip().decode()
        entries.append((FILE_MODE, oid, ".gitmodules"))
    records = b"".join(
        f"{mode} {oid} 0\t".encode() + os.fsencode(path) + b"\0"
        for mode, oid, path in entries
    )
    _git(repo, env, "update-index", "-z", "--index-info", data=records)


def _metadata(*paths):
    # Git's quoted config values use the same escapes here as JSON strings.
    return "".join(
        f'[submodule "module-{number}"]\n\tpath = {json.dumps(path, ensure_ascii=False)}\n'
        for number, path in enumerate(paths)
    ).encode()


def _run(repository, cwd=None):
    repo, env = repository
    return subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=cwd or repo, env=env,
        capture_output=True, text=True, encoding="utf-8",
    )


def _unmapped(result):
    prefix = "unmapped gitlink: "
    return {
        json.loads(line.removeprefix(prefix))
        for line in result.stdout.splitlines() if line.startswith(prefix)
    }


def _snapshot(repo):
    return {
        path.relative_to(repo): path.read_bytes()
        for path in repo.rglob("*") if path.is_file()
    }


def test_mapped_gitlink_is_clean(repository):
    _index(repository, {"modules/mapped"}, _metadata("modules/mapped"))
    result = _run(repository)
    assert result.returncode == 0, result.stderr
    assert _unmapped(result) == set()


def test_unmapped_gitlink_is_reported(repository):
    gitlinks = {"modules/mapped", "modules/stale", "modules/other"}
    declared = {"modules/mapped", "modules/unused"}
    _index(repository, gitlinks, _metadata(*sorted(declared)))
    result = _run(repository)
    assert result.returncode == 1, result.stderr
    # Independent oracle: literal input sets, not diagnostic internals.
    assert _unmapped(result) == gitlinks - declared


def test_missing_metadata_with_no_gitlinks_is_clean(repository):
    result = _run(repository)
    assert result.returncode == 0, result.stderr


def test_missing_metadata_with_gitlinks_is_reported(repository):
    gitlinks = {"modules/stale"}
    _index(repository, gitlinks)
    result = _run(repository)
    assert result.returncode == 1, result.stderr
    assert _unmapped(result) == gitlinks - set()


@pytest.mark.parametrize("metadata", [b'[submodule "broken"\npath = broken\n',
                                      b'[submodule "broken"]\npath = "unterminated\n'])
def test_malformed_metadata_is_error(repository, metadata):
    _index(repository, metadata=metadata)
    result = _run(repository)
    assert result.returncode == 2
    assert "error:" in result.stderr
    assert ".gitmodules" in result.stderr


@pytest.mark.parametrize("metadata", [
    _metadata("modules/repeated", "modules/repeated"),
    b'[submodule "same"]\npath = modules/first\npath = modules/second\n',
])
def test_duplicate_declarations_are_reported(repository, metadata):
    _index(repository, metadata=metadata)
    result = _run(repository)
    assert result.returncode == 2
    assert "duplicate" in result.stderr.lower()


def test_path_boundaries(repository):
    gitlinks = {"modules/a", "modules/a longer", "modules/caf\u00e9", "modules/line\nbreak",
                "modules/tab\ttext", 'modules/quote"text', "modules/back\\slash"}
    declared = {"modules/a longer", "modules/caf\u00e9", "modules/line\nbreak",
                "modules/tab\ttext", 'modules/quote"text', "modules/back\\slash"}
    _index(repository, gitlinks, _metadata(*sorted(declared)))
    result = _run(repository)
    assert result.returncode == 1, result.stderr
    assert _unmapped(result) == gitlinks - declared


def test_indexed_metadata_overrides_worktree(repository):
    repo, _ = repository
    _index(repository, {"modules/mapped"}, _metadata("modules/mapped"))
    (repo / ".gitmodules").write_bytes(b"malformed working-tree metadata\n")
    result = _run(repository)
    assert result.returncode == 0, result.stderr


def test_unindexed_metadata_does_not_map_gitlink(repository):
    repo, _ = repository
    gitlinks = {"modules/stale"}
    _index(repository, gitlinks)
    (repo / ".gitmodules").write_bytes(_metadata(*gitlinks))
    result = _run(repository)
    assert result.returncode == 1, result.stderr
    assert _unmapped(result) == gitlinks - set()


def test_invocation_from_subdirectory_checks_whole_index(repository):
    repo, _ = repository
    _index(repository, {"modules/stale"})
    subdir = repo / "nested"
    subdir.mkdir()
    result = _run(repository, cwd=subdir)
    assert result.returncode == 1, result.stderr
    assert _unmapped(result) == {"modules/stale"}


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("mapped", [False, True])
def test_inherited_literal_pathspecs_checks_selected_index(repository, nested, mapped):
    repo, env = repository
    gitlinks = {"modules/stale"}
    _index(repository, gitlinks, _metadata(*gitlinks) if mapped else None)
    cwd = repo / "nested" if nested else repo
    cwd.mkdir(exist_ok=True)
    env["GIT_LITERAL_PATHSPECS"] = "1"
    before = _snapshot(repo)
    result = _run(repository, cwd=cwd)
    assert result.returncode == (0 if mapped else 1), result.stderr
    assert _unmapped(result) == (set() if mapped else gitlinks)
    assert _snapshot(repo) == before


@pytest.mark.parametrize("metadata, expected_status", [
    (None, 1), (_metadata("modules/stale"), 0), (b"[broken\n", 2),
])
def test_diagnostic_preserves_index_and_worktree(repository, metadata, expected_status):
    repo, _ = repository
    _index(repository, {"modules/stale"}, metadata)
    (repo / ".gitmodules").write_bytes(b"unstaged metadata\n")
    (repo / "untracked.txt").write_bytes(b"unstaged bytes\x00\xff")
    before = _snapshot(repo)
    result = _run(repository)
    assert result.returncode == expected_status
    assert "gitlink" in result.stdout or "error:" in result.stderr
    assert _snapshot(repo) == before


def test_metadata_includes_are_not_followed(repository):
    repo, _ = repository
    included = repo / "external.config"
    included.write_bytes(_metadata("modules/stale"))
    metadata = f'[include]\npath = {json.dumps(str(included))}\n'.encode()
    _index(repository, {"modules/stale"}, metadata)
    result = _run(repository)
    assert result.returncode == 1, result.stderr
    assert _unmapped(result) == {"modules/stale"}


def test_git_failure_is_nonzero(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=tmp_path,
        env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode == 2
    assert "error:" in result.stderr


@pytest.mark.parametrize("failure", ["ls-files", "config", "missing executable"])
def test_git_read_failure_is_explicit(repository, monkeypatch, capsys, failure):
    spec = importlib.util.spec_from_file_location("check_gitlinks", SCRIPT)
    diagnostic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(diagnostic)
    repo, _ = repository
    monkeypatch.chdir(repo)

    def fake_run(command, **kwargs):
        if failure == "missing executable":
            raise FileNotFoundError("git unavailable")
        if failure in command:
            return subprocess.CompletedProcess(command, 128, b"", b"read failure")
        # git-ls-files --stage: a regular indexed metadata blob, stage zero.
        return subprocess.CompletedProcess(
            command, 0, f"{FILE_MODE} {COMMIT_OID} 0\t.gitmodules\0".encode(), b""
        )

    monkeypatch.setattr(diagnostic.subprocess, "run", fake_run)
    assert diagnostic.main() == 2
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("metadata", [b"", b"# no declarations\n",
                                      b'[submodule "unused"]\nurl = unused\n'])
def test_valid_metadata_without_paths_is_clean(repository, metadata):
    _index(repository, metadata=metadata)
    result = _run(repository)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("metadata", [b'[submodule "empty"]\npath\n',
                                      b'[submodule "empty"]\npath = \n'])
def test_empty_path_declaration_is_error(repository, metadata):
    _index(repository, metadata=metadata)
    result = _run(repository)
    assert result.returncode == 2
    assert "empty path" in result.stderr


def test_git_reads_disable_fetch_replacements_and_optional_locks(monkeypatch):
    spec = importlib.util.spec_from_file_location("check_gitlinks", SCRIPT)
    diagnostic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(diagnostic)

    def fake_run(command, **kwargs):
        # Git environment-variable contract: 1 disables lazy fetching and object
        # replacements; 0 disables optional locks (git and git-config manuals).
        assert kwargs["env"]["GIT_NO_LAZY_FETCH"] == "1"
        assert kwargs["env"]["GIT_NO_REPLACE_OBJECTS"] == "1"
        assert kwargs["env"]["GIT_OPTIONAL_LOCKS"] == "0"
        assert command[1] in {"ls-files", "config"}
        return subprocess.CompletedProcess(command, 0, b"", b"")

    monkeypatch.setattr(diagnostic.subprocess, "run", fake_run)
    assert diagnostic.main() == 0


@pytest.mark.parametrize("path", ["modules/stale", ".gitmodules"])
def test_unmerged_relevant_entry_is_error(repository, path):
    repo, env = repository
    # Index-format: stage 1 is the merge-base entry of an unresolved path.
    record = f"{GITLINK_MODE} {COMMIT_OID} 1\t{path}\0".encode()
    _git(repo, env, "update-index", "-z", "--index-info", data=record)
    before = _snapshot(repo)
    result = _run(repository)
    assert result.returncode == 2
    assert "Unmerged" in result.stderr
    assert _snapshot(repo) == before


def test_symlink_metadata_is_error(monkeypatch, capsys):
    # Git refuses to construct this .gitmodules state via update-index, so use
    # a subprocess stub to exercise the diagnostic's defensive mode check.
    spec = importlib.util.spec_from_file_location("check_gitlinks", SCRIPT)
    diagnostic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(diagnostic)

    def fake_run(command, **kwargs):
        # Git index-format: 120000 denotes a symlink, not config content.
        record = f"120000 {COMMIT_OID} 0\t.gitmodules\0".encode()
        return subprocess.CompletedProcess(command, 0, record, b"")

    monkeypatch.setattr(diagnostic.subprocess, "run", fake_run)
    assert diagnostic.main() == 2
    assert "regular file" in capsys.readouterr().err
