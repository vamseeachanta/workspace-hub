"""Fail-closed Git authority for client-wiki bootstrap."""

from __future__ import annotations

import os
from pathlib import Path
import pwd
import re
import subprocess
from typing import Mapping

from .bootstrap_layout import BoundCloneLayout


class BootstrapGitError(RuntimeError):
    """Clone Git state falls outside the closed bootstrap contract."""


_INHERITED_ENV = (
    "HOME", "GH_TOKEN",
    "GITHUB_TOKEN", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", "TEMP", "TMP",
)
_TRUSTED_PATH = "/usr/local/bin:/usr/bin:/bin"


def isolated_env(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Build the complete, literal environment for a Git/GitHub child."""
    inherited = os.environ if source is None else source
    env = {key: inherited[key] for key in _INHERITED_ENV if key in inherited}
    env.update(
        PATH=_TRUSTED_PATH,
        GIT_CONFIG=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_NO_REPLACE_OBJECTS="1",
    )
    return env


def trusted_executable(name: str) -> str:
    """Resolve a fixed operational tool without consulting ambient PATH/HOME."""
    if name not in {"gh", "git"}:
        raise BootstrapGitError("operational executable is not allowlisted")
    home = Path(pwd.getpwuid(os.getuid()).pw_dir)
    candidates = (Path("/usr/local/bin"), Path("/usr/bin"), Path("/bin"), home / ".local/bin")
    for directory in candidates:
        candidate = directory / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise BootstrapGitError(f"required operational executable is unavailable: {name}")


def author_env(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return isolated command environment with required ephemeral identity."""
    values = os.environ if source is None else source
    name = values.get("CLIENT_WIKI_GIT_AUTHOR_NAME")
    email = values.get("CLIENT_WIKI_GIT_AUTHOR_EMAIL")
    if not name or not email:
        raise BootstrapGitError("client-wiki author name and email are required")
    env = isolated_env(values)
    env.update(
        GIT_AUTHOR_NAME=name,
        GIT_AUTHOR_EMAIL=email,
        GIT_COMMITTER_NAME=name,
        GIT_COMMITTER_EMAIL=email,
        GIT_AUTHOR_DATE="@0 +0000",
        GIT_COMMITTER_DATE="@0 +0000",
    )
    return env


def accepted_origins(repo_slug: str) -> frozenset[str]:
    if re.fullmatch(r"[A-Za-z0-9-]+/llm-wiki-[a-z0-9-]+", repo_slug) is None:
        raise BootstrapGitError("registered repository is invalid")
    return frozenset(
        {
            f"https://github.com/{repo_slug}.git",
            f"git@github.com:{repo_slug}.git",
        }
    )


def mutation_command(git_fd: int, *args: str) -> list[str]:
    """Build a descriptor-bound plumbing command with hooks disabled."""
    return [
        trusted_executable("git"), f"--git-dir=/proc/self/fd/{git_fd}",
        "-c", f"core.hooksPath={os.devnull}", *args,
    ]


def push_command(git_fd: int, repo_slug: str, object_id: str) -> list[str]:
    """Build the only authorized push transport command."""
    if re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", object_id) is None:
        raise BootstrapGitError("push object ID is invalid")
    canonical = f"https://github.com/{repo_slug}.git"
    if canonical not in accepted_origins(repo_slug):
        raise BootstrapGitError("registered push repository is invalid")
    return mutation_command(
        git_fd,
        "-c", "credential.helper=",
        "-c", "credential.helper=!gh auth git-credential",
        "push", canonical, f"{object_id}:refs/heads/main",
    )


def _read_config(bound: BoundCloneLayout) -> list[tuple[str, str]]:
    command = [
        trusted_executable("git"), "config", "--file", f"/proc/self/fd/{bound.config_fd}",
        "--null", "--list", "--no-includes",
    ]
    try:
        result = subprocess.run(
            command, check=False, capture_output=True, pass_fds=(bound.config_fd,),
            env=isolated_env(), timeout=5,
        )
    except subprocess.TimeoutExpired as exc:
        raise BootstrapGitError("held clone config parse timed out") from exc
    if result.returncode != 0:
        raise BootstrapGitError("held clone config cannot be parsed")
    records: list[tuple[str, str]] = []
    for raw_record in result.stdout.split(b"\0"):
        if not raw_record:
            continue
        try:
            raw_key, raw_value = raw_record.split(b"\n", 1)
            records.append((raw_key.decode("utf-8"), raw_value.decode("utf-8")))
        except (ValueError, UnicodeError) as exc:
            raise BootstrapGitError("held clone config contains a malformed record") from exc
    return records


def _value_contract(origins: frozenset[str]) -> dict[str, frozenset[str]]:
    return {
        "core.repositoryformatversion": frozenset({"0"}),
        "core.bare": frozenset({"false"}),
        "core.filemode": frozenset({"true", "false"}),
        "core.logallrefupdates": frozenset({"true"}),
        "remote.origin.url": origins,
        "remote.origin.pushurl": origins,
        "remote.origin.fetch": frozenset({"+refs/heads/*:refs/remotes/origin/*"}),
        "branch.main.remote": frozenset({"origin"}),
        "branch.main.merge": frozenset({"refs/heads/main"}),
    }


def _validate_records(records: list[tuple[str, str]], repo_slug: str) -> dict[str, str]:
    contract = _value_contract(accepted_origins(repo_slug))
    parsed: dict[str, str] = {}
    for key, value in records:
        if key not in contract:
            raise BootstrapGitError(f"clone config key is forbidden: {key}")
        if key in parsed:
            raise BootstrapGitError(f"duplicate clone config key: {key}")
        if value not in contract[key]:
            raise BootstrapGitError(f"clone config value is forbidden for {key}")
        parsed[key] = value
    required = {
        "core.repositoryformatversion", "core.bare", "remote.origin.url",
        "remote.origin.fetch",
    }
    if not required <= parsed.keys():
        raise BootstrapGitError("clone config is missing a required key")
    return parsed


def _validate_head(bound: BoundCloneLayout) -> None:
    result = _run_head_git(bound, "symbolic-ref", "-q", "HEAD", text=True)
    if result.returncode != 0 or result.stdout != "refs/heads/main\n":
        raise BootstrapGitError("clone HEAD must be the symbolic main branch")
    branch = _run_head_git(
        bound, "show-ref", "--verify", "--quiet", "refs/heads/main",
    )
    if branch.returncode != 1:
        raise BootstrapGitError("clone HEAD main branch must be truly unborn")


def _run_head_git(
    bound: BoundCloneLayout, *args: str, text: bool = False,
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            [trusted_executable("git"), f"--git-dir=/proc/self/fd/{bound.git_fd}", *args],
            check=False, capture_output=True, text=text, pass_fds=(bound.git_fd,),
            env=isolated_env(), timeout=5,
        )
    except subprocess.TimeoutExpired as exc:
        raise BootstrapGitError("clone HEAD validation timed out") from exc


def validate_clone_git(bound: BoundCloneLayout, repo_slug: str) -> dict[str, str]:
    """Validate held config and HEAD without consulting ambient Git authority."""
    parsed = _validate_records(_read_config(bound), repo_slug)
    _validate_head(bound)
    return parsed


def validate_clone_config(bound: BoundCloneLayout, repo_slug: str) -> dict[str, str]:
    """Validate only the held config; callers classify HEAD separately."""
    return _validate_records(_read_config(bound), repo_slug)
