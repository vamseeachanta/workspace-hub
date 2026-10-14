#!/usr/bin/env python3
"""Read-only issue-closure checker.

Rule mapping to procedure section E:
1 -> closer source; 2 -> reviewed head; 3 -> resolving evidence reference and
path; 4 -> test command/count; 5 -> open body checkboxes; 6 -> successor or
decision for not-planned/superseded; 7 -> hedge words with successor; 8 -> bulk
closures; 9 -> import-style closure; 10 -> body edit after closure.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable
from urllib.parse import quote


API_BUDGET = 500
EVIDENCE_REF = re.compile(r"(?:\b[0-9a-f]{7,40}\b|#(?P<issue>\d+)|PR\s*#?(?P<pr>\d+))", re.I)
PATH_REF = re.compile(r"\b(?:scripts|tests|docs|reports|src|config)/[A-Za-z0-9._/\-]+")
TEST_COUNT = re.compile(r"\b\d+\s+(?:passed|pass|failed|fail|skipped|skip|tests?)\b", re.I)
CHECKBOX = re.compile(r"^\s*-\s+\[(?P<mark>[ xX])\]\s*(?P<text>.*)$", re.M)
ISSUE_REF = re.compile(r"#(?P<number>\d+)")
HEDGE = re.compile(r"\b(deferred|follow-up|partial|stub|placeholder|tracked elsewhere)\b", re.I)


@dataclass(frozen=True)
class RuleResult:
    rule: int
    verdict: str
    reason: str


def parse_instant(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def issue_number(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def text_blob(issue: dict) -> str:
    parts = [issue.get("body") or ""]
    parts.extend(comment.get("body") or "" for comment in issue.get("comments", []))
    for pr in issue.get("pull_requests", []):
        parts.append(pr.get("body") or "")
    return "\n".join(parts)


def closure_evidence_text(issue: dict) -> str:
    comments = [c for c in issue.get("comments", []) if c.get("closing_evidence")]
    if comments:
        return "\n".join(c.get("body") or "" for c in comments)
    return "\n".join(pr.get("body") or "" for pr in issue.get("pull_requests", []) if pr.get("merged"))


def successor_state(issue: dict, number: str | int) -> str | None:
    return (issue.get("successor_states") or {}).get(str(number))


def successor_ok(issue: dict, number: str | int) -> bool:
    state = successor_state(issue, number)
    return state in {"open", "pass"}


def has_decision_text(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in ("owner decision", "retired", "passed date"))


def evidence_status(issue: dict) -> tuple[bool, bool, list[str]]:
    evidence = closure_evidence_text(issue)
    reasons: list[str] = []
    has_reference = False
    for match in EVIDENCE_REF.finditer(evidence):
        token = match.group(0)
        if token.startswith("#"):
            state = successor_state(issue, token[1:])
            has_reference = has_reference or state in {"open", "closed", "pass"}
        elif token.lower().startswith("pr"):
            pr_number = int(re.sub(r"\D", "", token))
            has_reference = has_reference or any(pr.get("number") == pr_number for pr in issue.get("pull_requests", []))
        else:
            has_reference = has_reference or token in issue.get("default_branch_shas", [])
    if not has_reference:
        reasons.append("no resolving default-branch SHA or pull request")
    paths = [path.rstrip(".,);:") for path in PATH_REF.findall(evidence)]
    existing = issue.get("paths_at_refs") or {}
    if not paths or not any(existing.get(path) for path in paths):
        reasons.append("no cited path exists at the evidence revision")
    has_test = bool(TEST_COUNT.search(evidence))
    return not reasons, has_test, reasons


def check_closer(issue: dict) -> RuleResult:
    closer = issue.get("closer_type")
    if closer in {"commit", "nothing", None, ""}:
        return RuleResult(1, "FAIL", "closer is commit-only or absent")
    if closer in {"merged_pr", "comment"}:
        return RuleResult(1, "PASS", f"closer is {closer.replace('_', ' ')}")
    return RuleResult(1, "WARN", "closer type is not recognized")


def check_review_head(issue: dict) -> RuleResult:
    prs = [pr for pr in issue.get("pull_requests", []) if pr.get("merged")]
    if not prs:
        return RuleResult(2, "WARN", "review artifact not found")
    for pr in prs:
        reviewed = pr.get("review_head_sha")
        merged = pr.get("head_sha")
        if not reviewed:
            return RuleResult(2, "WARN", "review artifact not found")
        if reviewed != merged:
            return RuleResult(2, "FAIL", "reviewed head differs from merged head")
    return RuleResult(2, "PASS", "reviewed head equals merged head")


def check_evidence_reference(issue: dict) -> RuleResult:
    ok, _has_test, reasons = evidence_status(issue)
    if ok:
        return RuleResult(3, "PASS", "closing evidence resolves to default-branch content")
    return RuleResult(3, "FAIL", "; ".join(reasons))


def check_test_count(issue: dict) -> RuleResult:
    _ok, has_test, _reasons = evidence_status(issue)
    if has_test:
        return RuleResult(4, "PASS", "test command and count found")
    if issue.get("state_reason") == "NOT_PLANNED":
        return RuleResult(4, "WARN", "test command/count missing on not-planned closure")
    return RuleResult(4, "FAIL", "test command/count missing")


def check_body_checkboxes(issue: dict) -> RuleResult:
    failures = []
    for match in CHECKBOX.finditer(issue.get("body") or ""):
        if match.group("mark").lower() == "x":
            continue
        refs = ISSUE_REF.findall(match.group("text"))
        if not any(successor_ok(issue, ref) for ref in refs):
            failures.append(match.group("text").strip() or "unticked checkbox")
    if failures:
        return RuleResult(5, "FAIL", "unticked acceptance item lacks open successor")
    return RuleResult(5, "PASS", "checkboxes are ticked or routed")


def check_successor_or_decision(issue: dict) -> RuleResult:
    text = text_blob(issue)
    applies = issue.get("state_reason") == "NOT_PLANNED" or re.search(r"\b(duplicate|superseded)\b", text, re.I)
    if not applies:
        return RuleResult(6, "PASS", "successor rule not triggered")
    refs = ISSUE_REF.findall(text)
    if any(successor_ok(issue, ref) for ref in refs) or has_decision_text(text):
        return RuleResult(6, "PASS", "successor or decision resolves")
    return RuleResult(6, "FAIL", "not-planned or superseded closure lacks resolving successor or decision")


def check_hedges(issue: dict) -> RuleResult:
    bad = []
    for line in text_blob(issue).splitlines():
        if HEDGE.search(line):
            refs = ISSUE_REF.findall(line)
            if not any(successor_ok(issue, ref) for ref in refs):
                bad.append(line.strip())
    if bad:
        return RuleResult(7, "FAIL", "hedge wording lacks open successor")
    return RuleResult(7, "PASS", "hedge wording is routed or absent")


def check_bulk(issue: dict, closures: list[dict]) -> RuleResult:
    actor = issue.get("closed_by")
    closed_at = parse_instant(issue.get("closed_at"))
    if not actor or not closed_at:
        return RuleResult(8, "PASS", "bulk rule not triggered")
    window_start = closed_at - timedelta(minutes=10)
    peers = [
        item for item in closures
        if item.get("closed_by") == actor
        and (stamp := parse_instant(item.get("closed_at"))) is not None
        and window_start <= stamp <= closed_at + timedelta(minutes=10)
    ]
    rule3_ok, _has_test, _reasons = evidence_status(issue)
    if len(peers) > 5 and not rule3_ok:
        return RuleResult(8, "FAIL", "bulk closure lacks rule-3 evidence")
    return RuleResult(8, "PASS", "bulk threshold not exceeded or evidence present")


def check_import_closure(issue: dict) -> RuleResult:
    created = parse_instant(issue.get("created_at"))
    closed = parse_instant(issue.get("closed_at"))
    has_comment = bool(issue.get("comments"))
    if created and closed and closed - created <= timedelta(seconds=60) and not has_comment:
        return RuleResult(9, "FAIL", "closed within 60 seconds of creation with no comment")
    return RuleResult(9, "PASS", "not an import-style closure")


def check_body_edit(issue: dict) -> RuleResult:
    if issue.get("body_edited_after_close"):
        return RuleResult(10, "WARN", "body edited after closure")
    return RuleResult(10, "PASS", "no post-closure body edit recorded")


def evaluate_issue(issue: dict, closures: Iterable[dict] = ()) -> dict:
    closure_list = list(closures)
    if not closure_list:
        closure_list = [issue]
    results = [
        check_closer(issue),
        check_review_head(issue),
        check_evidence_reference(issue),
        check_test_count(issue),
        check_body_checkboxes(issue),
        check_successor_or_decision(issue),
        check_hedges(issue),
        check_bulk(issue, closure_list),
        check_import_closure(issue),
        check_body_edit(issue),
    ]
    verdict = "PASS"
    if any(item.verdict == "FAIL" for item in results):
        verdict = "FAIL"
    elif any(item.verdict == "WARN" for item in results):
        verdict = "WARN"
    return {
        "repository": issue.get("repository", ""),
        "number": issue_number(issue.get("number")),
        "verdict": verdict,
        "rules": [item.__dict__ for item in results],
    }


class GitHubReader:
    def __init__(self, cache_dir: Path, budget: int = API_BUDGET):
        self.cache_dir = cache_dir
        self.budget = budget
        self.calls = 0
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def api(self, route: str) -> object:
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", route.strip("/"))
        cached = self.cache_dir / f"{safe}.json"
        if cached.exists():
            return json.loads(cached.read_text(encoding="utf-8"))
        if self.calls >= self.budget:
            raise RuntimeError("GitHub API budget exceeded")
        self.calls += 1
        result = subprocess.run(
            ["gh", "api", route],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gh api failed")
        cached.write_text(result.stdout, encoding="utf-8", newline="\n")
        return json.loads(result.stdout)

    def try_api(self, route: str) -> object | None:
        try:
            return self.api(route)
        except RuntimeError:
            return None


def _login(value: object) -> str:
    if isinstance(value, dict):
        return str(value.get("login") or "")
    return ""


def _neutral_issue(raw: dict, reader: GitHubReader, repo: str) -> dict:
    number = raw["number"]
    comments = reader.api(f"repos/{repo}/issues/{number}/comments")
    events = reader.api(f"repos/{repo}/issues/{number}/events")
    closer_type = "nothing"
    closed_by = ""
    body_edited_after_close = False
    closed_at = raw.get("closed_at")
    for event in events:
        if event.get("event") == "closed":
            closed_by = _login(event.get("actor"))
            commit_id = event.get("commit_id")
            closer_type = "commit" if commit_id else "comment"
        if event.get("event") == "edited" and closed_at and event.get("created_at", "") > closed_at:
            body_edited_after_close = True
    neutral_comments = [
        {
            "created_at": item.get("created_at"),
            "closing_evidence": True,
            "body": item.get("body") or "",
        }
        for item in comments
    ]
    evidence = "\n".join([raw.get("body") or ""] + [item["body"] for item in neutral_comments])
    shas = {
        match.group(0) for match in EVIDENCE_REF.finditer(evidence)
        if not match.group(0).startswith("#") and not match.group(0).lower().startswith("pr")
    }
    default_branch_shas = []
    for sha in shas:
        if reader.try_api(f"repos/{repo}/commits/{sha}") is not None:
            default_branch_shas.append(sha)
    pull_requests = []
    for match in EVIDENCE_REF.finditer(evidence):
        token = match.group(0)
        if token.lower().startswith("pr"):
            pr_number = int(re.sub(r"\D", "", token))
            pr = reader.try_api(f"repos/{repo}/pulls/{pr_number}")
            if isinstance(pr, dict):
                pull_requests.append({
                    "number": pr_number,
                    "merged": bool(pr.get("merged_at")),
                    "head_sha": ((pr.get("head") or {}).get("sha")),
                    "review_head_sha": None,
                    "merge_commit_sha": pr.get("merge_commit_sha"),
                    "body": pr.get("body") or "",
                })
                if pr.get("merge_commit_sha"):
                    default_branch_shas.append(pr["merge_commit_sha"])
    successor_states = {}
    for ref in ISSUE_REF.findall(evidence):
        linked = reader.try_api(f"repos/{repo}/issues/{ref}")
        if isinstance(linked, dict):
            successor_states[ref] = linked.get("state")
    paths_at_refs = {}
    for path in {item.rstrip(".,);:") for item in PATH_REF.findall(evidence)}:
        paths_at_refs[path] = False
        for sha in default_branch_shas:
            if reader.try_api(f"repos/{repo}/contents/{quote(path, safe='/')}?ref={sha}") is not None:
                paths_at_refs[path] = True
                break
    return {
        "repository": repo.split("/")[-1],
        "number": number,
        "state_reason": raw.get("state_reason"),
        "created_at": raw.get("created_at"),
        "closed_at": closed_at,
        "closed_by": closed_by,
        "closer_type": closer_type,
        "body": raw.get("body") or "",
        "comments": neutral_comments,
        "pull_requests": pull_requests,
        "default_branch_shas": sorted(set(default_branch_shas)),
        "paths_at_refs": paths_at_refs,
        "successor_states": successor_states,
        "body_edited_after_close": body_edited_after_close,
    }


def collect_live(repo: str, cache_dir: Path, *, issue: int | None = None,
                 closed_from: str | None = None, closed_to: str | None = None) -> list[dict]:
    reader = GitHubReader(cache_dir)
    if issue is not None:
        raw = reader.api(f"repos/{repo}/issues/{issue}")
        return [_neutral_issue(raw, reader, repo)]
    if not closed_from or not closed_to:
        raise ValueError("date range requires --closed-from and --closed-to")
    query = f"repo:{repo} is:issue is:closed closed:{closed_from}..{closed_to}"
    result = reader.api(f"search/issues?q={quote(query, safe='')}&per_page=100")
    return [_neutral_issue(item, reader, repo) for item in result.get("items", [])]


def load_fixture(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return list(data.get("issues", []))
    if isinstance(data, list):
        return data
    raise ValueError("fixture must contain an issues list")


def write_csv(path: Path, evaluations: list[dict], auditor: dict[int, str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["repository", "issue", "verdict", "rule", "rule_verdict", "reason", "auditor_class"])
        for item in evaluations:
            for rule in item["rules"]:
                writer.writerow([
                    item["repository"], item["number"], item["verdict"], rule["rule"],
                    rule["verdict"], rule["reason"], (auditor or {}).get(item["number"], ""),
                ])


def write_markdown(path: Path, evaluations: list[dict], auditor: dict[int, str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = {key: sum(1 for item in evaluations if item["verdict"] == key) for key in ("PASS", "WARN", "FAIL")}
    lines = ["# Issue Closure Check Summary", "", f"- PASS: {counts['PASS']}", f"- WARN: {counts['WARN']}", f"- FAIL: {counts['FAIL']}"]
    if auditor:
        matches = sum(1 for item in evaluations if checker_class(item["verdict"]) == auditor.get(item["number"]))
        total = len(evaluations)
        rate = 0 if total == 0 else matches / total
        lines.extend(["", f"- Auditor agreement: {matches}/{total} ({rate:.1%})"])
    lines.extend(["", "| Repository | Issue | Verdict | Auditor class |", "|---|---:|---|---|"])
    for item in evaluations:
        lines.append(f"| {item['repository']} | {item['number']} | {item['verdict']} | {(auditor or {}).get(item['number'], '')} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def checker_class(verdict: str) -> str:
    return {"PASS": "DONE", "WARN": "PARTLY DONE", "FAIL": "CLOSED WITHOUT DELIVERY"}[verdict]


def auditor_mapping() -> dict[str, str]:
    return {
        "DONE": "PASS",
        "PARTLY DONE": "WARN",
        "SUPERSEDED": "WARN",
        "NOT PLANNED OR OBSOLETE": "WARN",
        "CLOSED WITHOUT DELIVERY": "FAIL",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, help="Evaluate trimmed fixture JSON.")
    parser.add_argument("--repo", help="Repository as owner/name for live read-only collection.")
    parser.add_argument("--issue", type=int, help="Single issue number for live read-only collection.")
    parser.add_argument("--closed-from", help="Closed date lower bound, YYYY-MM-DD.")
    parser.add_argument("--closed-to", help="Closed date upper bound, YYYY-MM-DD.")
    parser.add_argument("--cache-dir", type=Path, default=Path(".closure-check-cache"))
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.fixture:
        issues = load_fixture(args.fixture)
    elif args.repo:
        issues = collect_live(
            args.repo, args.cache_dir, issue=args.issue,
            closed_from=args.closed_from, closed_to=args.closed_to,
        )
    else:
        parser.error("provide --fixture or --repo")
    evaluations = [evaluate_issue(issue, issues) for issue in issues]
    write_csv(args.csv, evaluations)
    write_markdown(args.markdown, evaluations)
    return 1 if any(item["verdict"] == "FAIL" for item in evaluations) else 0


if __name__ == "__main__":
    raise SystemExit(main())
