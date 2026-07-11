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
    get_entry,
    load_registry,
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


def _run_text(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=False, capture_output=True, text=True)


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


def derive_workspace_layout(template_worktree: Path, repo_slug: str) -> WorkspaceLayout:
    """Derive the target from the canonical Git common-directory owner."""
    worktree = Path(template_worktree).absolute()
    basename = repo_slug.rsplit("/", 1)[-1]
    if "/" not in repo_slug or basename != f"llm-wiki-{basename.removeprefix('llm-wiki-')}":
        raise BootstrapContractError("registered repository slug is invalid")
    common_text = _git_text(
        worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"
    )
    common = Path(common_text)
    if common.name != ".git" or not common.is_dir():
        raise BootstrapContractError("Git common directory must be a real .git directory")
    canonical = common.parent
    if not _same_directory(common, canonical / ".git"):
        raise BootstrapContractError("Git common directory owner is ambiguous")
    parent = canonical.parent
    return WorkspaceLayout(worktree, canonical, parent, parent / basename)


def verify_private_repo(
    repo_slug: str, *, runner: CommandRunner = subprocess.run
) -> None:
    args = [
        "gh",
        "repo",
        "view",
        repo_slug,
        "--json",
        "visibility,isArchived",
    ]
    result = runner(args, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise BootstrapContractError("GitHub repository lookup failed")
    try:
        payload = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        raise BootstrapContractError("GitHub repository response is malformed") from exc
    if not isinstance(payload, dict):
        raise BootstrapContractError("GitHub repository response is malformed")
    if payload.get("visibility") != "PRIVATE" or payload.get("isArchived") is not False:
        raise BootstrapContractError("repository must be PRIVATE and unarchived")


def _run_bound_git(clone: BoundClone, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", f"/proc/self/fd/{clone.root_fd}", *args],
        check=False,
        capture_output=True,
        text=True,
        pass_fds=(clone.root_fd,),
    )


def _require_bound_git(clone: BoundClone, *args: str) -> str:
    result = _run_bound_git(clone, *args)
    if result.returncode != 0:
        raise BootstrapContractError(f"clone Git check failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _verify_bound_clone(
    clone: BoundClone, repo_slug: str, *, require_empty: bool = True
) -> None:
    expected = {template.format(repo=repo_slug) for template in _ORIGIN_TEMPLATES}
    origin = _require_bound_git(clone, "config", "--get", "remote.origin.url")
    if origin not in expected:
        raise BootstrapContractError("clone origin does not match registered repository")
    top = _require_bound_git(clone, "rev-parse", "--show-toplevel")
    top_info = os.stat(top)
    root_info = os.fstat(clone.root_fd)
    if (top_info.st_dev, top_info.st_ino) != (root_info.st_dev, root_info.st_ino):
        raise BootstrapContractError("clone toplevel does not match bound target")
    if _run_bound_git(clone, "rev-parse", "--verify", "HEAD").returncode == 0:
        raise BootstrapContractError("clone HEAD must be unborn")
    if require_empty:
        status_text = _require_bound_git(
            clone, "status", "--porcelain=v1", "--untracked-files=all"
        )
        if status_text:
            raise BootstrapContractError("clone must be clean and empty")


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
    template_worktree: Path | None = None,
    runner: CommandRunner = subprocess.run,
) -> RenderManifest:
    """Authorize and render with one continuously bound clone descriptor."""
    entry = _load_planned_entry(Path(registry_path), short_name)
    template = Path(template_worktree or _template_worktree()).absolute()
    layout = derive_workspace_layout(template, entry.repo)
    validate_root_disjointness(
        entry,
        [str(layout.template_worktree), str(layout.canonical_checkout), str(layout.target)],
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
            manifest = render_committed_template(clone, template, tokens)
            _verify_bound_clone(clone, entry.repo, require_empty=False)
            return manifest
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
        [str(layout.template_worktree), str(layout.canonical_checkout), str(layout.target)],
    )
    payload = {
        "mode": entry.mode.value,
        "repo": entry.repo,
        "short_name": entry.short_name,
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
