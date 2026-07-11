"""Closed Git authority tests for client-wiki bootstrap."""

from __future__ import annotations

import os
import errno
from pathlib import Path
import subprocess
import time

import pytest

from client_llm_wiki.bootstrap_git import (
    BootstrapGitError,
    author_env,
    isolated_env,
    mutation_command,
    push_command,
    trusted_executable,
    validate_clone_git,
)
from client_llm_wiki.bootstrap_layout import bind_clone


REPO = "owner/llm-wiki-slug"


def test_isolated_env_inherits_only_literal_allowlist(monkeypatch):
    monkeypatch.setenv("PATH", "/trusted/bin")
    monkeypatch.setenv("GH_TOKEN", "token")
    for key in (
        "GH_HOST", "LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH", "PYTHONHOME",
        "GIT_EXEC_PATH", "GIT_ASKPASS", "SSH_ASKPASS", "AWS_SECRET_ACCESS_KEY",
    ):
        monkeypatch.setenv(key, "hostile")

    env = isolated_env()

    assert env["PATH"] == "/usr/local/bin:/usr/bin:/bin"
    assert env["GH_TOKEN"] == "token"
    assert set(env) <= {
        "PATH", "HOME", "GH_TOKEN",
        "GITHUB_TOKEN", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", "TEMP", "TMP",
        "GIT_CONFIG", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL",
        "GIT_NO_REPLACE_OBJECTS",
    }
    assert not set(env) & {"GH_HOST", "LD_PRELOAD", "PYTHONPATH", "GIT_ASKPASS"}
    assert "GH_CONFIG_DIR" not in env


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _clone(tmp_path: Path, fetch: str | None = None, push: str | None = None) -> Path:
    repo = tmp_path / "clone"
    _git(tmp_path, "init", str(repo))
    _git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
    if fetch:
        _git(repo, "remote", "add", "origin", fetch)
    if push:
        _git(repo, "config", "remote.origin.pushurl", push)
    return repo


@pytest.mark.parametrize(
    ("fetch", "push"),
    [
        ("https://github.com/owner/llm-wiki-slug.git", "git@github.com:owner/llm-wiki-slug.git"),
        ("git@github.com:owner/llm-wiki-slug.git", "https://github.com/owner/llm-wiki-slug.git"),
        ("https://github.com/owner/llm-wiki-slug.git", None),
        ("git@github.com:owner/llm-wiki-slug.git", None),
    ],
)
def test_bound_config_accepts_independent_exact_origin_spellings(tmp_path, fetch, push):
    clone = _clone(tmp_path, fetch, push)

    with bind_clone(clone) as bound:
        config = validate_clone_git(bound, REPO)

    assert config["remote.origin.url"] == fetch
    assert config.get("remote.origin.pushurl") == push


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("include.path", "/definitely/not/opened"),
        ("includeif.gitdir:/tmp/.path", "/not/opened"),
        ("core.hookspath", "/tmp/hooks"),
        ("core.fsmonitor", "true"),
        ("core.sshcommand", "evil"),
        ("commit.gpgsign", "true"),
        ("filter.evil.clean", "evil"),
        ("credential.helper", "evil"),
        ("extensions.objectformat", "sha256"),
        ("alias.status", "!evil"),
        ("url.https://evil/.insteadof", "https://github.com/"),
    ],
)
def test_config_rejects_every_forbidden_control_without_applying_include(tmp_path, key, value):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    _git(clone, "config", key, value)

    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="key"):
        validate_clone_git(bound, REPO)


def test_no_includes_never_opens_existing_fifo_target(tmp_path):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    fifo = tmp_path / "hostile-config"
    os.mkfifo(fifo)
    _git(clone, "config", "include.path", str(fifo))

    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="key"):
        validate_clone_git(bound, REPO)

    with pytest.raises(OSError) as caught:
        os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
    assert caught.value.errno == errno.ENXIO


def test_config_parse_timeout_fails_closed(tmp_path, monkeypatch):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")

    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == 5
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr("client_llm_wiki.bootstrap_git.subprocess.run", timeout)
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="timed out"):
        validate_clone_git(bound, REPO)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("core.repositoryformatversion", "1"),
        ("core.bare", "no"),
        ("core.filemode", "yes"),
        ("core.logallrefupdates", "false"),
        ("remote.origin.url", "https://github.com/owner/llm-wiki-slug"),
        ("remote.origin.pushurl", "git@github.com:owner/other.git"),
        ("remote.origin.fetch", "+refs/heads/main:refs/remotes/origin/main"),
        ("branch.main.remote", "upstream"),
        ("branch.main.merge", " refs/heads/main"),
    ],
)
def test_config_rejects_wrong_literal_values(tmp_path, key, value):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    _git(clone, "config", "--replace-all", key, value)
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="value"):
        validate_clone_git(bound, REPO)


def test_repository_format_one_is_rejected_even_with_sha256_extension(tmp_path):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    _git(clone, "config", "core.repositoryformatversion", "1")
    _git(clone, "config", "extensions.objectformat", "sha256")
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError):
        validate_clone_git(bound, REPO)


@pytest.mark.parametrize(
    "key",
    [
        "core.repositoryformatversion", "core.bare", "core.filemode",
        "core.logallrefupdates", "remote.origin.url", "remote.origin.pushurl",
        "remote.origin.fetch", "branch.main.remote", "branch.main.merge",
    ],
)
def test_config_rejects_duplicate_every_scalar_family(tmp_path, key):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    optional_values = {
        "core.filemode": "true",
        "core.logallrefupdates": "true",
        "remote.origin.pushurl": "git@github.com:owner/llm-wiki-slug.git",
        "branch.main.remote": "origin",
        "branch.main.merge": "refs/heads/main",
    }
    if key in optional_values:
        _git(clone, "config", key, optional_values[key])
    value = subprocess.run(
        ["git", "-C", str(clone), "config", "--get", key],
        check=True, capture_output=True, text=True,
    ).stdout.rstrip("\n")
    _git(clone, "config", "--add", key, value)
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="duplicate"):
        validate_clone_git(bound, REPO)


def test_config_preserves_origin_whitespace_instead_of_normalizing(tmp_path):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    _git(clone, "config", "--replace-all", "remote.origin.url", " https://github.com/owner/llm-wiki-slug.git")
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="value"):
        validate_clone_git(bound, REPO)


@pytest.mark.parametrize("head", ["refs/heads/missing", "not-a-ref"])
def test_clone_rejects_dangling_or_corrupt_symbolic_head(tmp_path, head):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    (clone / ".git" / "HEAD").write_text(f"ref: {head}\n", encoding="utf-8")
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="HEAD"):
        validate_clone_git(bound, REPO)


def test_clone_accepts_authorized_unborn_main(tmp_path):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    with bind_clone(clone) as bound:
        validate_clone_git(bound, REPO)


@pytest.mark.parametrize("ref_text", ["a" * 40 + "\n", "not-an-object-id\n"])
def test_clone_rejects_present_dangling_or_corrupt_main_ref(tmp_path, ref_text):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    (clone / ".git" / "refs" / "heads" / "main").write_text(ref_text, encoding="ascii")
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="HEAD"):
        validate_clone_git(bound, REPO)


def test_clone_rejects_valid_born_main(tmp_path):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    _git(clone, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-m", "born")
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="unborn"):
        validate_clone_git(bound, REPO)


@pytest.mark.parametrize("fifo_location", ["HEAD", "main-ref"])
def test_clone_fifo_git_ref_state_fails_within_fixed_bound(tmp_path, fifo_location):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    fifo = clone / ".git" / "HEAD"
    if fifo_location == "main-ref":
        fifo = clone / ".git" / "refs" / "heads" / "main"
    fifo.unlink(missing_ok=True)
    os.mkfifo(fifo)

    started = time.monotonic()
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="timed out"):
        validate_clone_git(bound, REPO)
    assert time.monotonic() - started < 7


def test_author_env_requires_both_values_and_does_not_persist_config():
    with pytest.raises(BootstrapGitError, match="author"):
        author_env({"CLIENT_WIKI_GIT_AUTHOR_NAME": "Operator"})
    env = author_env({
        "CLIENT_WIKI_GIT_AUTHOR_NAME": "Operator",
        "CLIENT_WIKI_GIT_AUTHOR_EMAIL": "operator@example.invalid",
        "GIT_AUTHOR_NAME": "Hostile",
    })
    assert env["GIT_AUTHOR_NAME"] == env["GIT_COMMITTER_NAME"] == "Operator"
    assert env["GIT_AUTHOR_EMAIL"] == env["GIT_COMMITTER_EMAIL"] == "operator@example.invalid"


def test_mutation_and_push_commands_fix_hooks_credentials_and_https_target():
    assert mutation_command(9, "hash-object", "-w", "--stdin") == [
        trusted_executable("git"), "--git-dir=/proc/self/fd/9", "-c", "core.hooksPath=/dev/null",
        "hash-object", "-w", "--stdin",
    ]
    assert push_command(9, REPO, "a" * 40) == [
        trusted_executable("git"), "--git-dir=/proc/self/fd/9", "-c", "core.hooksPath=/dev/null",
        "-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential",
        "push", "https://github.com/owner/llm-wiki-slug.git",
        f"{'a' * 40}:refs/heads/main",
    ]


@pytest.mark.parametrize(
    "object_id",
    ["a" * 39, "a" * 41, "a" * 63, "a" * 65, "A" * 40, "g" * 40],
)
def test_push_rejects_non_exact_or_non_lowercase_object_ids(object_id):
    with pytest.raises(BootstrapGitError, match="object ID"):
        push_command(9, REPO, object_id)


@pytest.mark.parametrize("width", [40, 64])
def test_push_accepts_exact_lowercase_object_id_widths(width):
    assert push_command(9, REPO, "a" * width)[-1] == f"{'a' * width}:refs/heads/main"
