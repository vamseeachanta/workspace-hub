"""Closed Git authority tests for client-wiki bootstrap."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest

from client_llm_wiki.bootstrap_git import (
    BootstrapGitError,
    author_env,
    isolated_env,
    mutation_command,
    push_command,
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

    assert env["PATH"] == "/trusted/bin"
    assert env["GH_TOKEN"] == "token"
    assert set(env) <= {
        "PATH", "HOME", "XDG_CONFIG_HOME", "GH_CONFIG_DIR", "GH_TOKEN",
        "GITHUB_TOKEN", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", "TEMP", "TMP",
        "GIT_CONFIG", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL",
        "GIT_NO_REPLACE_OBJECTS",
    }
    assert not set(env) & {"GH_HOST", "LD_PRELOAD", "PYTHONPATH", "GIT_ASKPASS"}


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


def test_bound_config_accepts_independent_exact_origin_spellings(tmp_path):
    clone = _clone(
        tmp_path,
        "https://github.com/owner/llm-wiki-slug.git",
        "git@github.com:owner/llm-wiki-slug.git",
    )

    with bind_clone(clone) as bound:
        config = validate_clone_git(bound, REPO)

    assert config["remote.origin.url"] == "https://github.com/owner/llm-wiki-slug.git"
    assert config["remote.origin.pushurl"] == "git@github.com:owner/llm-wiki-slug.git"


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


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("core.repositoryformatversion", "1"),
        ("core.bare", "no"),
        ("core.filemode", "yes"),
        ("core.logallrefupdates", "false"),
        ("remote.origin.url", "https://github.com/owner/llm-wiki-slug"),
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


def test_config_rejects_duplicate_scalar_and_preserves_whitespace(tmp_path):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    _git(clone, "config", "--add", "remote.origin.url", " https://github.com/owner/llm-wiki-slug.git")
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="duplicate"):
        validate_clone_git(bound, REPO)


@pytest.mark.parametrize("head", ["refs/heads/missing", "not-a-ref"])
def test_clone_rejects_dangling_or_corrupt_symbolic_head(tmp_path, head):
    clone = _clone(tmp_path, "https://github.com/owner/llm-wiki-slug.git")
    (clone / ".git" / "HEAD").write_text(f"ref: {head}\n", encoding="utf-8")
    with bind_clone(clone) as bound, pytest.raises(BootstrapGitError, match="HEAD"):
        validate_clone_git(bound, REPO)


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
        "git", "--git-dir=/proc/self/fd/9", "-c", "core.hooksPath=/dev/null",
        "hash-object", "-w", "--stdin",
    ]
    assert push_command(9, REPO, "a" * 40) == [
        "git", "--git-dir=/proc/self/fd/9", "-c", "core.hooksPath=/dev/null",
        "-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential",
        "push", "https://github.com/owner/llm-wiki-slug.git",
        f"{'a' * 40}:refs/heads/main",
    ]
