#!/usr/bin/env python3
"""Reconcile GitHub issues into the kanban board tree.

Correctness path: fetch each active manifest repo once, then make the board
YAMLs match GitHub's issue set. Dry-run mode prints the exact diff and does not
write board files.
"""
from __future__ import annotations

import argparse
import copy
import difflib
import io
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ruamel.yaml import YAML


GH_LIMIT = 100000
ISSUE_JSON_FIELDS = "number,title,state,labels"


@dataclass
class ReconcileResult:
    changed: bool
    diff: str
    changed_files: list[Path]


@dataclass(frozen=True)
class BoardEntry:
    slug: str
    tier: str
    repo: str | None
    domain: str | None
    file: Path


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode == 0:
        return Path(out.stdout.strip())
    return Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict:
    data = yaml_rt().load(path.read_text(encoding="utf-8"))
    return data or {}


def dump_yaml(data: dict) -> str:
    out = io.StringIO()
    yaml_rt().dump(data, out)
    return out.getvalue()


def yaml_rt() -> YAML:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 1000
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(dump_yaml(data), encoding="utf-8")


def fetch_repo_issues(repo: str, *, limit: int = 100000, runner=None) -> list[dict]:
    runner = runner or subprocess.run
    cmd = [
        "gh",
        "issue",
        "list",
        "--repo",
        repo,
        "--state",
        "all",
        "--limit",
        str(limit),
        "--json",
        ISSUE_JSON_FIELDS,
    ]
    out = runner(cmd, capture_output=True, text=True, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"gh issue list failed for {repo}: {out.stderr.strip()}")
    try:
        items = json.loads(out.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"gh issue list returned invalid JSON for {repo}") from exc
    if len(items) >= limit:
        raise RuntimeError(f"gh issue list truncated at --limit {limit} for {repo}")
    return items


def load_manifest_entries(kanban_root: Path) -> list[BoardEntry]:
    manifest = load_yaml(kanban_root / "manifest.yaml").get("manifest", {})
    entries = []
    for raw in manifest.get("boards") or []:
        file_name = raw.get("file")
        if not file_name:
            continue
        entries.append(
            BoardEntry(
                slug=str(raw.get("slug") or ""),
                tier=str(raw.get("tier") or ""),
                repo=raw.get("repo"),
                domain=raw.get("domain"),
                file=kanban_root / file_name,
            )
        )
    return entries


def active_repos(entries: list[BoardEntry]) -> list[str]:
    repos = {entry.repo for entry in entries if entry.tier == "repo" and entry.repo}
    return sorted(repos)


def board_files(kanban_root: Path, entries: list[BoardEntry]) -> list[Path]:
    files = {entry.file for entry in entries}
    files.update((kanban_root / "boards").glob("*.yaml"))
    return sorted(files)


def repo_board_map(entries: list[BoardEntry]) -> dict[str, Path]:
    return {
        entry.repo: entry.file
        for entry in entries
        if entry.tier == "repo" and entry.repo
    }


def domain_board_map(entries: list[BoardEntry]) -> dict[tuple[str, str], Path]:
    return {
        (entry.repo, entry.domain): entry.file
        for entry in entries
        if entry.tier == "domain" and entry.repo and entry.domain
    }


def label_names(issue: dict) -> list[str]:
    names = []
    for label in issue.get("labels") or []:
        name = label.get("name") if isinstance(label, dict) else str(label)
        if name and name not in names:
            names.append(clean_scalar(name))
    return names


def clean_scalar(value) -> str:
    text = str(value or "")
    return "".join(ch for ch in text if ch == "\n" or ch == "\t" or ord(ch) >= 32).strip()


def issue_key(repo: str, number) -> str:
    return f"gh:{repo}#{number}"


def key_repo(key: str | None) -> str | None:
    if not key or not key.startswith("gh:") or "#" not in key:
        return None
    return key[3:].rsplit("#", 1)[0]


def key_number(key: str) -> int:
    try:
        return int(key.rsplit("#", 1)[1])
    except (IndexError, ValueError):
        return sys.maxsize


def target_board(repo: str, labels: list[str], repo_boards: dict, domain_boards: dict) -> Path:
    for label in labels:
        if not label.startswith("domain:"):
            continue
        domain = label.split(":", 1)[1]
        board = domain_boards.get((repo, domain))
        if board:
            return board
    return repo_boards[repo]


def priority(labels: list[str]) -> int:
    if "priority:urgent" in labels or "p1" in labels:
        return 2
    if "priority:high" in labels or "p2" in labels:
        return 1
    return 0


def card_for_issue(repo: str, issue: dict, existing: dict | None = None) -> dict:
    labels = label_names(issue)
    number = issue["number"]
    card = dict(existing or {})
    card.update(
        {
            "idempotency_key": issue_key(repo, number),
            "title": clean_scalar(issue.get("title")),
            "source": "github_issue",
            "source_url": f"https://github.com/{repo}/issues/{number}",
            "gh_state": clean_scalar(issue.get("state")).lower(),
            "gh_labels": labels,
            "initial_status": card.get("initial_status", "triage"),
            "priority": priority(labels),
        }
    )
    card.setdefault("gh_assignees", [])
    card.setdefault("body_excerpt", "")
    return card


def existing_cards(board_data: dict, files: list[Path]) -> dict[str, dict]:
    found = {}
    for path in files:
        for card in (board_data[path].get("cards") or []):
            key = card.get("idempotency_key")
            if key and key not in found:
                found[key] = card
    return found


def existing_issue_counts_by_repo(existing: dict[str, dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for key, card in existing.items():
        repo = key_repo(key)
        if repo and card.get("source") == "github_issue":
            counts[repo] = counts.get(repo, 0) + 1
    return counts


def unified_diff(before: dict[Path, str], after: dict[Path, str], root: Path) -> str:
    chunks = []
    diff_root = root.parents[2] if len(root.parents) >= 3 else root
    for path in sorted(after):
        if before[path] == after[path]:
            continue
        rel = path.relative_to(diff_root)
        chunks.extend(
            difflib.unified_diff(
                before[path].splitlines(keepends=True),
                after[path].splitlines(keepends=True),
                fromfile=f"a/{rel}",
                tofile=f"b/{rel}",
            )
        )
    return "".join(chunks)


def build_live_cards(
    repos: list[str],
    issue_fetcher: Callable[[str], list[dict]],
    repo_boards: dict[str, Path],
    domain_boards: dict[tuple[str, str], Path],
    existing: dict[str, dict],
    existing_counts: dict[str, int],
    allow_empty_repos: set[str],
) -> dict[str, tuple[Path, dict]]:
    live = {}
    for repo in repos:
        issues = issue_fetcher(repo)
        if not issues and existing_counts.get(repo, 0) > 0 and repo not in allow_empty_repos:
            raise RuntimeError(
                f"empty issue list for {repo} would remove "
                f"{existing_counts[repo]} existing github_issue card(s); "
                "use --allow-empty only after verifying the repo legitimately has zero issues"
            )
        for issue in issues:
            key = issue_key(repo, issue["number"])
            card = card_for_issue(repo, issue, existing.get(key))
            board = target_board(repo, card["gh_labels"], repo_boards, domain_boards)
            live[key] = (board, card)
    return live


def rebuild_boards(
    board_data: dict[Path, dict],
    files: list[Path],
    active: set[str],
    live: dict[str, tuple[Path, dict]],
) -> dict[Path, dict]:
    rebuilt = {}
    added = set()
    for path in files:
        data = copy.deepcopy(board_data[path])
        cards = []
        for card in data.get("cards") or []:
            key = card.get("idempotency_key")
            if key in live:
                target, new_card = live[key]
                if target == path and key not in added:
                    cards.append(new_card)
                    added.add(key)
                continue
            if card.get("source") == "github_issue" and key_repo(key) in active:
                continue
            cards.append(card)
        data["cards"] = cards
        rebuilt[path] = data
    for key, (target, card) in sorted(live.items(), key=lambda item: key_number(item[0])):
        if key not in added:
            rebuilt[target].setdefault("cards", []).append(card)
    return rebuilt


def reconcile_kanban(
    kanban_root: Path,
    *,
    issue_fetcher: Callable[[str], list[dict]],
    dry_run: bool = True,
    write_files: bool = True,
    repo_filter: str | None = None,
    allow_empty_repos: set[str] | None = None,
) -> ReconcileResult:
    entries = load_manifest_entries(kanban_root)
    repos = active_repos(entries)
    if repo_filter:
        repos = [repo for repo in repos if repo == repo_filter]
    repo_boards = repo_board_map(entries)
    domain_boards = domain_board_map(entries)
    files = board_files(kanban_root, entries)
    board_data = {path: load_yaml(path) for path in files}
    before = {path: path.read_text(encoding="utf-8") for path in files}
    existing = existing_cards(board_data, files)
    live = build_live_cards(
        repos,
        issue_fetcher,
        repo_boards,
        domain_boards,
        existing,
        existing_issue_counts_by_repo(existing),
        allow_empty_repos or set(),
    )
    rebuilt = rebuild_boards(board_data, files, set(repos), live)
    after = {}
    for path in files:
        after[path] = before[path] if rebuilt[path] == board_data[path] else dump_yaml(rebuilt[path])
    changed_files = [path for path in files if before[path] != after[path]]
    if write_files:
        for path in changed_files:
            path.write_text(after[path], encoding="utf-8")
    return ReconcileResult(
        changed=bool(changed_files),
        diff=unified_diff(before, after, kanban_root),
        changed_files=changed_files,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo", help="limit reconciliation to one active owner/repo")
    parser.add_argument("--limit", type=int, default=GH_LIMIT)
    parser.add_argument("--kanban-root", type=Path)
    parser.add_argument(
        "--allow-empty",
        action="append",
        default=[],
        metavar="OWNER/REPO",
        help="allow an active repo with existing cards to reconcile to zero live issues",
    )
    args = parser.parse_args(argv)

    root = args.kanban_root or repo_root() / ".claude/memory/kanban"

    def fetch(repo: str) -> list[dict]:
        return fetch_repo_issues(repo, limit=args.limit)

    result = reconcile_kanban(
        root,
        issue_fetcher=fetch,
        dry_run=args.dry_run,
        write_files=not args.dry_run,
        repo_filter=args.repo,
        allow_empty_repos=set(args.allow_empty),
    )
    if result.diff:
        print(result.diff, end="")
    else:
        print("kanban reconcile: no changes")
    if args.dry_run:
        print("DRY-RUN: no files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
