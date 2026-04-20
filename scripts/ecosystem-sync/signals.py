"""Signal detectors. Pure for signals 1-3; detect_showcase uses gh CLI."""
from __future__ import annotations
import hashlib
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from scripts.ecosystem_sync.models import Signal
from scripts.ecosystem_sync.state import RepoState


SEMVER_RE = re.compile(r"^v?\d+\.\d+(\.\d+)?$")
NOISE_PREFIXES = ("nightly-", "snapshot-", "pre-")

CASE_STUDY_DIRS = ("case-studies", "examples", "demos", "docs/case-studies")
CASE_STUDY_SKIP_NAMES = {"README.md", "CASE_STUDY_TEMPLATE.md"}
CASE_STUDY_SKIP_PATH_SUBSTRINGS = ("/_draft/", "/wip/", "/archive/")


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


def detect_new_case_study(
    repo_name: str, repo_path: Path, state: RepoState,
) -> list[Signal]:
    """Signal 2: files added under case-studies/ / examples/ / demos/ / docs/case-studies/."""
    if not state.last_commit_sha:
        return []
    try:
        diff_out = _git(
            repo_path, "diff", "--name-status",
            f"{state.last_commit_sha}..HEAD", "--",
            *CASE_STUDY_DIRS,
        )
    except subprocess.CalledProcessError:
        return []

    signals: list[Signal] = []
    for line in diff_out.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or parts[0] != "A":
            continue
        rel_path = parts[1]
        name = Path(rel_path).name
        if name.endswith(".template.md") or name in CASE_STUDY_SKIP_NAMES:
            continue
        if any(sub in f"/{rel_path}" for sub in CASE_STUDY_SKIP_PATH_SUBSTRINGS):
            continue
        abs_path = repo_path / rel_path
        preview = ""
        if abs_path.exists():
            try:
                preview = "\n".join(abs_path.read_text().splitlines()[:40])
            except (UnicodeDecodeError, OSError):
                preview = "(binary or unreadable)"
        signals.append(Signal(
            repo=repo_name,
            kind="case-study",
            title=f"[sync] {repo_name} added {name}",
            body=(
                f"New case study / example detected in `{repo_name}`: `{rel_path}`\n\n"
                f"## First 40 lines\n\n```\n{preview}\n```\n\n"
                f"## Proposed website update\n\n"
                f"Lift into `aceengineer-website/case-studies/`, link from index.html."
            ),
            dedupe_key=f"case-study:{repo_name}:{rel_path}",
            payload={"path": rel_path},
        ))
    return signals


def _extract_section(markdown: str, heading: str) -> str:
    """Return body of `## <heading>` section, up to next `## ` or EOF."""
    lines = markdown.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end]).strip()


def _hash_section(body: str) -> str:
    normalized = "\n".join(line.rstrip() for line in body.splitlines() if line.strip())
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def detect_readme_capability_diff(
    repo_name: str, repo_path: Path, state: RepoState, sections: list[str],
) -> list[Signal]:
    """Signal 3: README section hash drift."""
    readme_path = repo_path / "README.md"
    if not readme_path.exists():
        return []
    try:
        md = readme_path.read_text()
    except (UnicodeDecodeError, OSError):
        return []
    signals: list[Signal] = []
    for heading in sections:
        body = _extract_section(md, heading)
        if not body:
            continue  # silent skip per spec
        current_hash = _hash_section(body)
        prev_hash = state.last_readme_hash.get(heading)
        if prev_hash == current_hash:
            continue
        hash_prefix = current_hash.split(":")[1][:8]
        signals.append(Signal(
            repo=repo_name,
            kind="readme-diff",
            title=f"[sync] {repo_name} README \"{heading}\" section changed",
            body=(
                f"README section `## {heading}` changed in `{repo_name}`.\n\n"
                f"## Current section content\n\n```\n{body}\n```\n\n"
                f"## Proposed website update\n\n"
                f"Reflect capability change in engineering.html / about.html."
            ),
            dedupe_key=f"readme-diff:{repo_name}:{heading}:{hash_prefix}",
            payload={"heading": heading, "hash": current_hash},
        ))
    return signals
