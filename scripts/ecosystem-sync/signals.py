"""Signal detectors. Pure for signals 1-3; detect_showcase uses gh CLI."""
from __future__ import annotations
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from scripts.ecosystem_sync.models import Signal
from scripts.ecosystem_sync.state import RepoState


SEMVER_RE = re.compile(r"^v?\d+\.\d+(\.\d+)?$")
NOISE_PREFIXES = ("nightly-", "snapshot-", "pre-")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True, timeout=30,
    )
    return result.stdout


def detect_release_tag(
    repo_name: str, repo_path: Path, state: RepoState,
) -> list[Signal]:
    """Signal 1: new semver tags not seen before, filtered to non-noise, <90 days old."""
    tags_out = _git(repo_path, "tag", "-l")
    all_tags = [t.strip() for t in tags_out.splitlines() if t.strip()]
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    signals: list[Signal] = []
    known = set(state.last_seen_tags)

    for tag in all_tags:
        if tag in known:
            continue
        if tag.startswith(NOISE_PREFIXES):
            continue
        if not SEMVER_RE.match(tag):
            continue
        # Check tag age
        try:
            ts_out = _git(repo_path, "log", "-1", "--format=%cI", tag)
            tag_date = datetime.fromisoformat(ts_out.strip())
            if tag_date < cutoff:
                continue
        except (subprocess.CalledProcessError, ValueError):
            continue
        # Build body from commit log since previous semver tag
        prev = _previous_semver(all_tags, tag)
        log_range = f"{prev}..{tag}" if prev else tag
        try:
            log_out = _git(repo_path, "log", log_range, "--oneline")
            body_commits = "\n".join(log_out.splitlines()[:20])
        except subprocess.CalledProcessError:
            body_commits = "(unable to compute commit log)"
        signals.append(Signal(
            repo=repo_name,
            kind="release",
            title=f"[sync] {repo_name} released {tag}",
            body=(
                f"New release detected in `{repo_name}`: **{tag}**\n\n"
                f"## Commits since previous release\n\n```\n{body_commits}\n```\n\n"
                f"## Proposed website update\n\n"
                f"Add to changelog/releases page; consider blog post if user-facing."
            ),
            dedupe_key=f"release:{repo_name}:{tag}",
            payload={"tag": tag},
        ))
    return signals


def _previous_semver(all_tags: Iterable[str], current: str) -> str | None:
    semvers = sorted(
        [t for t in all_tags if SEMVER_RE.match(t) and not t.startswith(NOISE_PREFIXES)],
        key=_semver_key,
    )
    if current not in semvers:
        return None
    idx = semvers.index(current)
    return semvers[idx - 1] if idx > 0 else None


def _semver_key(tag: str) -> tuple[int, ...]:
    parts = tag.lstrip("v").split(".")
    return tuple(int(p) for p in parts)
