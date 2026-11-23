"""Config loader for the ecosystem-sync cron."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class RepoConfig:
    name: str
    path: str
    readme_sections: list[str]


@dataclass(frozen=True)
class SyncConfig:
    repos: list[RepoConfig]
    issue_repo: str
    digest_dir: str
    state_file: str
    max_issues_per_run: int


def load_config(path: Path) -> SyncConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    raw = yaml.safe_load(path.read_text())
    repos = [RepoConfig(**r) for r in raw["repos"]]
    return SyncConfig(
        repos=repos,
        issue_repo=raw["issue_repo"],
        digest_dir=raw["digest_dir"],
        state_file=raw["state_file"],
        max_issues_per_run=int(raw["max_issues_per_run"]),
    )
