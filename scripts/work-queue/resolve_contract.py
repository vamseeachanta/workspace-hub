"""Contract path resolver for stage contracts.

Resolves stage contract YAML from folder-skill locations
(.claude/skills/workspace-hub/stages/stage-NN-*/contract.yaml),
with fallback to legacy flat location (scripts/work-queue/stages/).
"""
import glob
import os


def resolve_contract_path(stage: int, repo_root: str) -> str | None:
    """Find the contract YAML for a given stage number.

    Checks folder-skill location first, then legacy flat location.
    Returns absolute path or None.
    """
    # Primary: folder-skill location
    pattern = os.path.join(
        repo_root, ".claude", "skills", "workspace-hub", "stages",
        f"stage-{stage:02d}-*", "contract.yaml",
    )
    matches = glob.glob(pattern)
    if matches:
        return matches[0]

    # Fallback: legacy flat location
    pattern = os.path.join(
        repo_root, "scripts", "work-queue", "stages",
        f"stage-{stage:02d}-*.yaml",
    )
    matches = glob.glob(pattern)
    if matches:
        return matches[0]

    return None


def resolve_stages_dir(repo_root: str) -> str:
    """Return the canonical stages directory (folder-skill location)."""
    return os.path.join(repo_root, ".claude", "skills", "workspace-hub", "stages")
