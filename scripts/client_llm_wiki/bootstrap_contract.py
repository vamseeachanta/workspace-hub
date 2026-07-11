"""CLI and authorization boundary for client-wiki metadata bootstrap."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from typing import Callable, Sequence

from .bootstrap_attestation import BootstrapManifestError
from .bootstrap_finalizer import finalize_scaffold as finalize_scaffold
from .bootstrap_git import (
    BootstrapGitError, accepted_origins, isolated_env, validate_clone_git,
)
from .bootstrap_layout import BoundCloneLayout
from .bootstrap_manifest import PersistedRenderManifest, persist_render_manifest

from .bootstrap_renderer import (
    BootstrapRenderError,
    BoundClone,
    RenderManifest,
    RenderResidue,
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

    def __init__(self, message: str, *, residue=None):
        super().__init__(message)
        self.residue = residue


def sanitize_backing_name(final_name: str, candidate: object) -> str | None:
    """Accept only the manifest publisher's exact final-name-bound grammar."""
    if not isinstance(candidate, str):
        return None
    pattern = rf"\.{re.escape(final_name)}\.backing-[1-9][0-9]*-[0-9a-f]{{16}}"
    return candidate if re.fullmatch(pattern, candidate) else None


class ManifestPersistenceError(BootstrapContractError):
    """Manifest publication failed without exposing raw exception text."""

    def __init__(self, final_name: str, backing_name: str | None):
        safe = sanitize_backing_name(final_name, backing_name)
        super().__init__("manifest persistence failed")
        self.backing_name = safe


@dataclass(frozen=True, slots=True)
class WorkspaceLayout:
    template_worktree: Path
    canonical_checkout: Path
    checkout_parent: Path
    target: Path


CommandRunner = Callable[..., subprocess.CompletedProcess[str]]
def _template_worktree() -> Path:
    return Path(__file__).resolve().parents[2]


def _git_env() -> dict[str, str]:
    return isolated_env()


def _run_text(args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args, check=False, capture_output=True, text=True, env=_git_env()
        )
    except OSError as exc:
        raise BootstrapContractError(f"Git command unavailable: {exc}") from exc


def _git_text(worktree: Path, *args: str) -> str:
    result = _run_text(["git", "-C", str(worktree), *args])
    if result.returncode != 0:
        raise BootstrapContractError(
            f"Git layout query failed: {result.stderr.strip()}"
        )
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
    common_text = _git_text(
        worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"
    )
    common = Path(common_text)
    if not common.is_absolute() or common.name != ".git":
        raise BootstrapContractError(
            "Git common directory must be a real .git directory"
        )
    _require_real_directory(common, "Git common directory .git")
    canonical = common.parent
    _require_real_directory(canonical, "canonical checkout")
    parent = canonical.parent
    return WorkspaceLayout(worktree, canonical, parent, parent / basename)


def verify_private_repo(
    repo_slug: str, *, runner: CommandRunner = subprocess.run
) -> None:
    args = [
        "gh",
        "repo",
        "view",
        f"github.com/{repo_slug}",
        "--json",
        "nameWithOwner,visibility,isArchived",
        "--hostname",
        "github.com",
    ]
    try:
        result = runner(
            args, check=False, capture_output=True, text=True, env=isolated_env()
        )
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
        raise BootstrapContractError(
            "repository identity must match and be PRIVATE/unarchived"
        )


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


def _verify_bound_clone(
    clone: BoundClone, repo_slug: str, *, require_empty: bool = True
) -> None:
    _verify_named_git(clone)
    try:
        config_fd = os.open(
            "config", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=clone.git_fd,
        )
        try:
            bound = BoundCloneLayout(
                clone.parent_fd, clone.root_fd, clone.git_fd, config_fd,
            )
            validate_clone_git(bound, repo_slug)
        finally:
            os.close(config_fd)
    except (OSError, BootstrapGitError) as exc:
        raise BootstrapContractError("clone origin/config authorization failed") from exc
    top = _require_bound_git(clone, "rev-parse", "--show-toplevel")
    top_info = os.stat(top)
    root_info = os.fstat(clone.root_fd)
    if (top_info.st_dev, top_info.st_ino) != (root_info.st_dev, root_info.st_ino):
        raise BootstrapContractError("clone toplevel does not match bound target")
    if require_empty:
        status_text = _require_bound_git(
            clone, "status", "--porcelain=v1", "--untracked-files=all"
        )
        if status_text:
            raise BootstrapContractError("clone must be clean and empty")
    _verify_named_git(clone)


def verify_unborn_clone(target: Path, repo_slug: str) -> None:
    try:
        with bind_empty_clone(target) as clone:
            _verify_bound_clone(clone, repo_slug)
    except BootstrapRenderError as exc:
        raise BootstrapContractError(str(exc), residue=exc.residue) from exc


def _load_planned_entry(registry_path: Path, short_name: str):
    try:
        registry = load_registry(registry_path)
        entry = get_entry(registry, short_name)
    except BootstrapSchemaError as exc:
        raise BootstrapContractError(str(exc)) from exc
    if entry.status != "planned":
        raise BootstrapContractError("render requires a planned registry entry")
    return entry


def _persist_render(
    clone: BoundClone,
    destination: Path,
    entry,
    manifest: RenderManifest,
) -> PersistedRenderManifest:
    return persist_render_manifest(
        clone,
        destination,
        registered_repo=entry.repo,
        allowed_origins=tuple(sorted(accepted_origins(entry.repo))),
        template_commit=manifest.template_commit,
        template_tree=manifest.template_tree,
    )


def _validate_rendered_clone(
    clone: BoundClone, manifest: RenderManifest, repo: str
) -> None:
    try:
        _verify_bound_clone(clone, repo, require_empty=False)
    except BaseException as exc:
        residue = RenderResidue(
            manifest.template_commit,
            manifest.clone_device,
            manifest.clone_inode,
            manifest.created_paths,
            None,
            "final_validation",
        )
        raise BootstrapContractError(
            "render final validation failed",
            residue=residue,
        ) from exc


def execute_render(
    registry_path: Path,
    short_name: str,
    *,
    runner: CommandRunner = subprocess.run,
    _manifest_path: Path | None = None,
) -> RenderManifest | tuple[RenderManifest, PersistedRenderManifest]:
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
            manifest = render_committed_template(clone, template, tokens)
            _validate_rendered_clone(clone, manifest, entry.repo)
            if _manifest_path is not None:
                return manifest, _persist_render(clone, _manifest_path, entry, manifest)
            return manifest
    except BootstrapManifestError as exc:
        final_name = _manifest_path.name if _manifest_path is not None else ""
        raise ManifestPersistenceError(final_name, exc.backing_name) from exc
    except BootstrapRenderError as exc:
        raise BootstrapContractError(str(exc), residue=exc.residue) from exc


def build_parser():
    from .bootstrap_contract_cli import build_parser as cli_parser

    return cli_parser()


def main(argv: Sequence[str] | None = None) -> int:
    from .bootstrap_contract_cli import main as cli_main

    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
