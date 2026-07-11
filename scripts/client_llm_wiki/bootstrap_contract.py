"""CLI and authorization boundary for client-wiki metadata bootstrap."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import Callable, Sequence

from .bootstrap_renderer import (
    BootstrapRenderError,
    BoundClone,
    RenderManifest,
    RenderTokens,
    bind_empty_clone,
    render_committed_template,
)
from .bootstrap_schema import (
    BootstrapSchemaError,
    RegistryValidationError,
    get_entry,
    load_registry,
    validate_repo_slug,
    validate_root_disjointness,
)


class BootstrapContractError(RuntimeError):
    """Live repository or clone state denies bootstrap."""


@dataclass(frozen=True, slots=True)
class WorkspaceLayout:
    template_worktree: Path
    canonical_checkout: Path
    checkout_parent: Path
    target: Path


CommandRunner = Callable[..., subprocess.CompletedProcess[str]]
_ORIGIN_TEMPLATES = (
    "https://github.com/{repo}",
    "https://github.com/{repo}.git",
    "git@github.com:{repo}.git",
)


def _template_worktree() -> Path:
    return Path(__file__).resolve().parents[2]


def _git_env() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return env


def _run_text(args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, check=False, capture_output=True, text=True, env=_git_env())
    except OSError as exc:
        raise BootstrapContractError(f"Git command unavailable: {exc}") from exc


def _git_text(worktree: Path, *args: str) -> str:
    result = _run_text(["git", "-C", str(worktree), *args])
    if result.returncode != 0:
        raise BootstrapContractError(f"Git layout query failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _same_directory(first: Path, second: Path) -> bool:
    try:
        left, right = first.stat(), second.stat()
    except OSError as exc:
        raise BootstrapContractError(f"workspace directory unavailable: {exc}") from exc
    return (
        stat.S_ISDIR(left.st_mode)
        and stat.S_ISDIR(right.st_mode)
        and (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)
    )


def _require_real_directory(path: Path, label: str) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        raise BootstrapContractError(f"{label} unavailable: {exc}") from exc
    if not stat.S_ISDIR(info.st_mode) or path.is_symlink():
        raise BootstrapContractError(f"{label} must be a real non-symlink directory")


def derive_workspace_layout(template_worktree: Path, repo_slug: str) -> WorkspaceLayout:
    """Derive the target from the canonical Git common-directory owner."""
    worktree = Path(template_worktree).absolute()
    try:
        short_name = validate_repo_slug(repo_slug)
    except RegistryValidationError as exc:
        raise BootstrapContractError("registered repository slug is invalid") from exc
    basename = f"llm-wiki-{short_name}"
    top = Path(_git_text(worktree, "rev-parse", "--show-toplevel"))
    _require_real_directory(worktree, "active template worktree")
    if not _same_directory(worktree, top):
        raise BootstrapContractError("active template worktree is not its Git toplevel")
    common_text = _git_text(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir")
    common = Path(common_text)
    if not common.is_absolute() or common.name != ".git":
        raise BootstrapContractError("Git common directory must be a real .git directory")
    _require_real_directory(common, "Git common directory .git")
    canonical = common.parent
    _require_real_directory(canonical, "canonical checkout")
    parent = canonical.parent
    return WorkspaceLayout(worktree, canonical, parent, parent / basename)


def verify_private_repo(repo_slug: str, *, runner: CommandRunner = subprocess.run) -> None:
    args = [
        "gh",
        "repo",
        "view",
        f"github.com/{repo_slug}",
        "--json",
        "nameWithOwner,visibility,isArchived",
    ]
    try:
        result = runner(args, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise BootstrapContractError(f"GitHub CLI unavailable: {exc}") from exc
    if result.returncode != 0:
        raise BootstrapContractError("GitHub repository lookup failed")
    try:
        payload = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        raise BootstrapContractError("GitHub repository response is malformed") from exc
    if not isinstance(payload, dict):
        raise BootstrapContractError("GitHub repository response is malformed")
    valid = (
        payload.get("nameWithOwner") == repo_slug
        and payload.get("visibility") == "PRIVATE"
        and payload.get("isArchived") is False
    )
    if not valid:
        raise BootstrapContractError("repository identity must match and be PRIVATE/unarchived")


def _run_bound_git(clone: BoundClone, *args: str) -> subprocess.CompletedProcess[str]:
    command = [
        "git",
        f"--git-dir=/proc/self/fd/{clone.git_fd}",
        f"--work-tree=/proc/self/fd/{clone.root_fd}",
        *args,
    ]
    try:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            pass_fds=(clone.root_fd, clone.git_fd),
            env=_git_env(),
        )
    except OSError as exc:
        raise BootstrapContractError(f"clone Git command unavailable: {exc}") from exc


def _require_bound_git(clone: BoundClone, *args: str) -> str:
    result = _run_bound_git(clone, *args)
    if result.returncode != 0:
        raise BootstrapContractError(f"clone Git check failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _verify_named_git(clone: BoundClone) -> None:
    try:
        info = os.stat(".git", dir_fd=clone.root_fd, follow_symlinks=False)
    except OSError as exc:
        raise BootstrapContractError(f".git identity unavailable: {exc}") from exc
    identity = (info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode))
    expected = (clone.git_id.device, clone.git_id.inode, clone.git_id.file_type)
    if identity != expected:
        raise BootstrapContractError(".git identity changed after descriptor binding")


def _verify_bound_clone(clone: BoundClone, repo_slug: str, *, require_empty: bool = True) -> None:
    _verify_named_git(clone)
    expected = {template.format(repo=repo_slug) for template in _ORIGIN_TEMPLATES}
    fetch = _require_bound_git(clone, "remote", "get-url", "--all", "origin").splitlines()
    push = _require_bound_git(clone, "remote", "get-url", "--push", "--all", "origin").splitlines()
    if len(fetch) != 1 or len(push) != 1 or fetch[0] not in expected or push[0] not in expected:
        raise BootstrapContractError("clone origin does not match registered repository")
    top = _require_bound_git(clone, "rev-parse", "--show-toplevel")
    top_info = os.stat(top)
    root_info = os.fstat(clone.root_fd)
    if (top_info.st_dev, top_info.st_ino) != (root_info.st_dev, root_info.st_ino):
        raise BootstrapContractError("clone toplevel does not match bound target")
    symbolic = _run_bound_git(clone, "symbolic-ref", "-q", "HEAD")
    if symbolic.returncode != 0 or not symbolic.stdout.strip().startswith("refs/heads/"):
        raise BootstrapContractError("clone HEAD is not a valid symbolic branch")
    head = _run_bound_git(clone, "rev-parse", "--verify", "HEAD")
    if head.returncode == 0:
        raise BootstrapContractError("clone HEAD must be unborn")
    if head.returncode not in {1, 128}:
        raise BootstrapContractError("clone HEAD query failed unexpectedly")
    if require_empty:
        status_text = _require_bound_git(clone, "status", "--porcelain=v1", "--untracked-files=all")
        if status_text:
            raise BootstrapContractError("clone must be clean and empty")
    _verify_named_git(clone)


def verify_unborn_clone(target: Path, repo_slug: str) -> None:
    try:
        with bind_empty_clone(target) as clone:
            _verify_bound_clone(clone, repo_slug)
    except BootstrapRenderError as exc:
        raise BootstrapContractError(str(exc)) from exc


def _load_planned_entry(registry_path: Path, short_name: str):
    try:
        registry = load_registry(registry_path)
        entry = get_entry(registry, short_name)
    except BootstrapSchemaError as exc:
        raise BootstrapContractError(str(exc)) from exc
    if entry.status != "planned":
        raise BootstrapContractError("render requires a planned registry entry")
    return entry


def execute_render(
    registry_path: Path,
    short_name: str,
    *,
    runner: CommandRunner = subprocess.run,
) -> RenderManifest:
    """Authorize and render with one continuously bound clone descriptor."""
    entry = _load_planned_entry(Path(registry_path), short_name)
    template = _template_worktree().absolute()
    layout = derive_workspace_layout(template, entry.repo)
    validate_root_disjointness(
        entry,
        [
            str(layout.template_worktree),
            str(layout.canonical_checkout),
            str(layout.target),
        ],
    )
    verify_private_repo(entry.repo, runner=runner)
    tokens = RenderTokens(
        entry.short_name,
        entry.short_name.upper(),
        entry.repo,
        entry.raw_source_status,
        entry.ingestion_enabled,
    )
    try:
        with bind_empty_clone(layout.target) as clone:
            _verify_bound_clone(clone, entry.repo)
            return render_committed_template(
                clone,
                template,
                tokens,
                _final_validator=lambda bound: _verify_bound_clone(bound, entry.repo, require_empty=False),
            )
    except BootstrapRenderError as exc:
        raise BootstrapContractError(str(exc)) from exc


def _validate_command(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    for warning in registry.warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    print(json.dumps({"kind": registry.kind.value, "version": registry.registry_version}))
    return 0


def _classify_command(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    entry = get_entry(registry, args.short_name)
    layout = derive_workspace_layout(_template_worktree(), entry.repo)
    validate_root_disjointness(
        entry,
        [
            str(layout.template_worktree),
            str(layout.canonical_checkout),
            str(layout.target),
        ],
    )
    payload = {
        "mode": entry.mode.value,
        "repo": entry.repo,
        "short_name": entry.short_name,
        "status": entry.status,
        "target": str(layout.target),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


def _render_command(args: argparse.Namespace) -> int:
    manifest = execute_render(Path(args.registry), args.short_name)
    print(json.dumps(asdict(manifest), sort_keys=True))
    return 0


def _verify_command(args: argparse.Namespace) -> int:
    verify_private_repo(args.repo)
    print(json.dumps({"repo": args.repo, "private": True, "archived": False}))
    return 0


def _add_registry_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--registry", required=True, type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="client-wiki-bootstrap")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-registry")
    _add_registry_argument(validate)
    validate.set_defaults(handler=_validate_command)
    classify = commands.add_parser("classify")
    _add_registry_argument(classify)
    classify.add_argument("--short-name", required=True)
    classify.set_defaults(handler=_classify_command)
    render = commands.add_parser("render")
    _add_registry_argument(render)
    render.add_argument("--short-name", required=True)
    render.set_defaults(handler=_render_command)
    verify = commands.add_parser("verify-private-repo")
    verify.add_argument("--repo", required=True)
    verify.set_defaults(handler=_verify_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (BootstrapSchemaError, BootstrapRenderError, BootstrapContractError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
