"""Load/save the last-sync state YAML. Change-detection excludes timestamps."""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from pathlib import Path
import yaml


@dataclass
class RepoState:
    last_sync_utc: str
    last_commit_sha: str
    last_seen_tags: list[str] = field(default_factory=list)
    last_readme_hash: dict[str, str] = field(default_factory=dict)
    last_case_studies: list[str] = field(default_factory=list)
    last_closed_showcase_issues: list[int] = field(default_factory=list)


def load_state(path: Path) -> dict[str, RepoState]:
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text()) or {}
    return {name: RepoState(**data) for name, data in raw.items()}


def save_state(path: Path, state: dict[str, RepoState]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {name: asdict(rs) for name, rs in state.items()}
    path.write_text(yaml.safe_dump(serializable, sort_keys=True, default_flow_style=False))


def has_substantive_change(
    before: dict[str, RepoState], after: dict[str, RepoState]
) -> bool:
    """True if any repo state changed excluding last_sync_utc."""
    def strip_timestamp(rs: RepoState) -> dict:
        d = asdict(rs)
        d.pop("last_sync_utc", None)
        return d

    before_stripped = {k: strip_timestamp(v) for k, v in before.items()}
    after_stripped = {k: strip_timestamp(v) for k, v in after.items()}
    return before_stripped != after_stripped
