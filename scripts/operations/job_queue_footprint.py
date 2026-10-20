"""Compare retained local Git layouts without modifying the source repository.

Method: Git clone --no-hardlinks, clone --depth, worktree add --detach and
sparse-checkout cone mode, documented in the Git manuals linked in the report.
Sizes are logical file bytes, not allocated disk blocks or peak storage.
"""

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess


def git(*args, cwd):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    return subprocess.run(
        ["git", *args], cwd=cwd, env=env, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def file_bytes(root):
    """Sum each file entry once; directory symlinks are never traversed."""
    if root.is_file() or root.is_symlink():
        return root.lstat().st_size
    if not root.exists():
        return 0
    total = 0
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(parent) / name
            if path.is_symlink() or path.is_file():
                total += path.lstat().st_size
    return total


def layout_row(destination, name, revision):
    checkout = destination / name
    if git("rev-parse", "HEAD", cwd=checkout) != revision:
        raise ValueError("source revision changed during measurement")
    admin = Path(git("rev-parse", "--absolute-git-dir", cwd=checkout))
    metadata = file_bytes(admin)
    if name == "full":
        # Account for linked administrative files in the linked row only.
        metadata -= file_bytes(admin / "worktrees")
    # Linked .git is a pointer file; its administrative directory is shared.
    if name == "linked":
        metadata += file_bytes(checkout / ".git")
    payload = sum(file_bytes(path) for path in checkout.iterdir() if path.name != ".git")
    return {
        "layout": name, "payload_bytes": payload, "metadata_bytes": metadata,
        "incremental_object_bytes": file_bytes(admin / "objects"),
        "commits": int(git("rev-list", "--count", "HEAD", cwd=checkout)),
    }


def measure(source, destination, sparse_path):
    source = Path(source).resolve(strict=True)
    destination = Path(destination).resolve()
    selection = PurePosixPath(sparse_path)
    if (not sparse_path or selection.is_absolute() or ".." in selection.parts
            or ".git" in selection.parts or ":" in sparse_path or "\\" in sparse_path):
        raise ValueError("sparse selection must be a tracked relative directory")
    if destination == source or source in destination.parents:
        raise ValueError("experiment must be outside the source repository")
    revision = git("rev-parse", "HEAD", cwd=source)
    paths = git("ls-tree", "-r", "--name-only", "HEAD", cwd=source).splitlines()
    prefix = selection.as_posix().rstrip("/") + "/"
    if not any(path.startswith(prefix) for path in paths):
        raise ValueError("sparse selection must be a tracked relative directory")
    destination.mkdir(parents=True, exist_ok=False)
    full = destination / "full"
    git("clone", "--no-hardlinks", str(source), str(full), cwd=destination)
    git("worktree", "add", "--detach", str(destination / "linked"), "HEAD", cwd=full)
    # Depth one is the explicit experimental variable, not an admission limit.
    git("clone", "--depth=1", source.as_uri(), str(destination / "shallow"), cwd=destination)
    sparse = destination / "sparse"
    git("clone", "--no-hardlinks", "--no-checkout", str(source), str(sparse), cwd=destination)
    git("sparse-checkout", "set", "--cone", "--", sparse_path, cwd=sparse)
    git("checkout", "--detach", "HEAD", cwd=sparse)
    rows = [layout_row(destination, name, revision)
            for name in ("full", "linked", "shallow", "sparse")]
    if git("rev-parse", "HEAD", cwd=source) != revision:
        raise ValueError("source revision changed during measurement")
    return {"source_commit": revision, "size_basis": "logical file bytes",
            "measurements": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--sparse-path", required=True)
    args = parser.parse_args()
    print(json.dumps(measure(args.source, args.destination, args.sparse_path), indent=2))


if __name__ == "__main__":
    main()
