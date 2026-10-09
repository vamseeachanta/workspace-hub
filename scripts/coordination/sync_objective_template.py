"""Sync the Objective issue template to canonical sibling repositories."""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO_ROOT / "config" / "objective-intake-sync.yml"


def load_manifest(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def planned_targets(manifest: dict, workspace_root: Path) -> list[Path]:
    destination = Path(manifest["destination"])
    targets = []
    for repo in manifest["canonical_repos"]:
        repo_root = REPO_ROOT if repo == "workspace-hub" else workspace_root / repo
        targets.append(repo_root / destination)
    return targets


def sync_templates(
    manifest_path: Path, workspace_root: Path, apply: bool = False
) -> list[str]:
    manifest = load_manifest(manifest_path)
    source = REPO_ROOT / manifest["source"]
    actions: list[str] = []
    for target in planned_targets(manifest, workspace_root):
        repo_root = _repo_root_for_target(target, Path(manifest["destination"]))
        if not _is_git_repo(repo_root):
            actions.append(f"missing-repo {repo_root}")
            continue
        if target.resolve() == source.resolve():
            actions.append(f"already-current {target}")
            continue
        if not apply:
            actions.append(f"would-copy {source} -> {target}")
            continue
        blocker = _apply_blocker(repo_root)
        if blocker:
            actions.append(blocker)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        actions.append(f"copied {source} -> {target}")
    return actions


def _repo_root_for_target(target: Path, destination: Path) -> Path:
    return target.parents[len(destination.parts) - 1]


def _is_git_repo(path: Path) -> bool:
    return (path / ".git").exists() or (path / ".git").is_file()


def _apply_blocker(repo_root: Path) -> str | None:
    if _git(repo_root, "status", "--porcelain").stdout.strip():
        return f"skip-dirty {repo_root}"
    current_branch = _git(repo_root, "branch", "--show-current").stdout.strip()
    default_branch = _default_branch(repo_root)
    if current_branch != default_branch:
        return (
            f"skip-non-default-branch {repo_root} "
            f"{current_branch} default={default_branch}"
        )
    return None


def _default_branch(repo_root: Path) -> str:
    result = _git(
        repo_root,
        "symbolic-ref",
        "--quiet",
        "--short",
        "refs/remotes/origin/HEAD",
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().removeprefix("origin/")
    result = _git(repo_root, "config", "--get", "init.defaultBranch", check=False)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return "main"


def _git(
    repo_root: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=check,
        capture_output=True,
        text=True,
        timeout=30,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--workspace-root", type=Path, default=REPO_ROOT.parent)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview mode (default).")
    mode.add_argument("--apply", action="store_true", help="Write eligible target repos.")
    args = parser.parse_args(argv)

    for action in sync_templates(args.manifest, args.workspace_root, apply=args.apply):
        print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
