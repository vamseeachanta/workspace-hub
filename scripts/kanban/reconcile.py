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


GH_PAGE_SIZE = 100

# GraphQL query: paginate issues exhaustively (states OPEN+CLOSED) with a nested
# labels page. We never truncate -- if a page fetch fails mid-loop we raise rather
# than return a partial set, so a partial fetch is structurally impossible.
ISSUES_QUERY = (
    "query($owner:String!, $name:String!, $first:Int!, $cursor:String) {"
    " repository(owner:$owner, name:$name) {"
    " issues(first:$first, after:$cursor, states:[OPEN,CLOSED]) {"
    " pageInfo { hasNextPage endCursor }"
    " nodes {"
    " number title state"
    " labels(first:100) { pageInfo { hasNextPage } nodes { name } }"
    " } } } }"
)


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
    # ruamel round-trip mode preserves formatting and does not execute Python tags.
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 1000
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(dump_yaml(data), encoding="utf-8")


def fetch_repo_issues(repo: str, *, page_size: int = GH_PAGE_SIZE, runner=None) -> list[dict]:
    """Fetch ALL issues for a repo via `gh api graphql` cursor pagination.

    Paginates to pageInfo.hasNextPage == false, accumulating every page. A
    mid-pagination failure (nonzero exit, bad JSON, or a node whose labels are
    themselves truncated) RAISES rather than returning a truncated set, so a
    partial fetch cannot silently shrink the board. Each node is mapped to the
    card shape downstream consumes: {number, title, state, labels:[{name}]}.
    """
    runner = runner or subprocess.run
    owner, name = repo.split("/", 1)
    issues: list[dict] = []
    cursor: str | None = None
    seen_cursors: set[str] = set()
    while True:
        cmd = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={ISSUES_QUERY}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"first={page_size}",
        ]
        if cursor is not None:
            cmd += ["-F", f"cursor={cursor}"]
        out = runner(cmd, capture_output=True, text=True, check=False)
        if out.returncode != 0:
            raise RuntimeError(
                f"gh api graphql failed for {repo} (cursor={cursor}): {out.stderr.strip()}"
            )
        try:
            payload = json.loads(out.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"gh api graphql returned invalid JSON for {repo} (cursor={cursor})"
            ) from exc
        if payload.get("errors"):
            raise RuntimeError(
                f"gh api graphql returned errors for {repo} (cursor={cursor}): {payload['errors']}"
            )
        try:
            connection = payload["data"]["repository"]["issues"]
        except (KeyError, TypeError) as exc:
            raise RuntimeError(
                f"gh api graphql response missing issues for {repo} (cursor={cursor})"
            ) from exc
        for node in connection.get("nodes") or []:
            # Fail closed on a malformed labels connection: board routing depends on
            # labels, so a missing/garbled labels.pageInfo is NOT treated as "no more".
            labels = node.get("labels")
            label_page = labels.get("pageInfo") if isinstance(labels, dict) else None
            if not isinstance(label_page, dict) or "hasNextPage" not in label_page:
                raise RuntimeError(
                    f"issue #{node.get('number')} in {repo}: malformed/missing labels.pageInfo"
                )
            if label_page.get("hasNextPage"):
                raise RuntimeError(
                    f"issue #{node.get('number')} in {repo} has more than {100} labels; "
                    "label pagination is not implemented and board routing depends on labels"
                )
            issues.append(
                {
                    "number": node["number"],
                    "title": node.get("title"),
                    "state": node.get("state"),
                    "labels": [{"name": lbl.get("name")} for lbl in (labels.get("nodes") or [])],
                }
            )
        # Fail closed on a malformed issue pageInfo: a missing/garbled pageInfo is
        # indistinguishable from "last page", so it must RAISE, not silently stop
        # (that would return a partial set — the exact thing this rewrite prevents).
        page_info = connection.get("pageInfo")
        if not isinstance(page_info, dict) or "hasNextPage" not in page_info:
            raise RuntimeError(
                f"gh api graphql: malformed/missing issues.pageInfo for {repo} (cursor={cursor})"
            )
        if page_info.get("hasNextPage"):
            next_cursor = page_info.get("endCursor")
            # hasNextPage with no endCursor would re-fetch page 1 forever; a repeated
            # endCursor that doesn't advance would also loop. This runs on a 20-min
            # cron — both must raise, not hang.
            if not next_cursor:
                raise RuntimeError(
                    f"gh api graphql: hasNextPage=true but endCursor missing for {repo}"
                )
            if next_cursor in seen_cursors:
                raise RuntimeError(
                    f"gh api graphql: endCursor did not advance ({next_cursor}) for {repo} — possible loop"
                )
            seen_cursors.add(next_cursor)
            cursor = next_cursor
            continue
        break
    return issues


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
    return sorted({entry.file for entry in entries})


def validate_unmanifested_boards(kanban_root: Path, entries: list[BoardEntry]) -> None:
    manifest_files = {entry.file for entry in entries}
    for path in sorted((kanban_root / "boards").glob("*.yaml")):
        if path in manifest_files:
            continue
        rel_path = path.relative_to(kanban_root)
        cards = load_yaml(path).get("cards") or []
        if cards:
            raise RuntimeError(
                f"unmanifested board {rel_path} has {len(cards)} card(s); "
                "add it to manifest.yaml before reconciling"
            )
        print(f"WARNING: unmanifested empty board ignored: {rel_path}", file=sys.stderr)


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
    allow_shrink_repos: set[str],
) -> dict[str, tuple[Path, dict]]:
    live = {}
    for repo in repos:
        issues = issue_fetcher(repo)
        existing_count = existing_counts.get(repo, 0)
        if len(issues) < existing_count:
            if not issues and repo in allow_empty_repos:
                pass
            elif repo in allow_shrink_repos:
                pass
            elif not issues:
                raise RuntimeError(
                    f"empty issue list for {repo} would remove "
                    f"{existing_count} existing github_issue card(s); "
                    "use --allow-empty only after verifying the repo legitimately has zero issues"
                )
            else:
                raise RuntimeError(
                    f"partial issue list for {repo} returned {len(issues)} live issue(s) "
                    f"but {existing_count} existing github_issue card(s) are present; "
                    "use --allow-shrink only after verifying the reduction is legitimate"
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
    allow_shrink_repos: set[str] | None = None,
) -> ReconcileResult:
    entries = load_manifest_entries(kanban_root)
    validate_unmanifested_boards(kanban_root, entries)
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
        allow_shrink_repos or set(),
    )
    rebuilt = rebuild_boards(board_data, files, set(repos), live)
    after = {}
    for path in files:
        after[path] = before[path] if rebuilt[path] == board_data[path] else dump_yaml(rebuilt[path])
    changed_files = [path for path in files if before[path] != after[path]]
    write = write_files and not dry_run
    if write:
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
    parser.add_argument(
        "--page-size",
        "--limit",
        dest="page_size",
        type=int,
        default=GH_PAGE_SIZE,
        help="GraphQL issues page size (default 100); paginates exhaustively regardless",
    )
    parser.add_argument("--kanban-root", type=Path)
    parser.add_argument(
        "--allow-empty",
        action="append",
        default=[],
        metavar="OWNER/REPO",
        help="allow an active repo with existing cards to reconcile to zero live issues",
    )
    parser.add_argument(
        "--allow-shrink",
        action="append",
        default=[],
        metavar="OWNER/REPO",
        help="allow an active repo to reconcile fewer live issues than existing cards",
    )
    args = parser.parse_args(argv)

    root = args.kanban_root or repo_root() / ".claude/memory/kanban"

    def fetch(repo: str) -> list[dict]:
        return fetch_repo_issues(repo, page_size=args.page_size)

    result = reconcile_kanban(
        root,
        issue_fetcher=fetch,
        dry_run=args.dry_run,
        write_files=not args.dry_run,
        repo_filter=args.repo,
        allow_empty_repos=set(args.allow_empty),
        allow_shrink_repos=set(args.allow_shrink),
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
