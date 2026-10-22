#!/usr/bin/env python3
"""Read-only issue-closure checker.

Rule mapping to docs/governance/issue-closing-procedure.md, section E:
1 -> E row 1, closer source; 2 -> E row 2 plus B.6 reviewer record,
reviewed head; 3 -> E row 3 plus B.1 and B.2, resolving evidence reference,
default-branch ancestry, and each cited path; 4 -> E row 4 plus B.3, test
command/count; 5 -> E row 5 plus B.2, open body checkboxes; 6 -> E row 6 plus
A.3 and A.4, successor or decision for not-planned, duplicate, or superseded
closures; 7 -> E row 7, hedge words with successor; 8 -> E row 8 plus C.1,
bulk closures; 9 -> E row 9 plus C.3, import-style closure; 10 -> E row 10
plus C.4, body edit after closure. Live review and body-edit data that cannot
be read is reported as NOT_EVALUATED instead of inferred.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from bisect import bisect_right
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, urlsplit

API_BUDGET = 500  # Issue 4073, plan item 3: maximum API calls per run.
EVIDENCE_REF = re.compile(r"(?:\b(?=[0-9a-f]{7,40}\b)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b|(?<!\w)#(?P<issue>\d+)(?!\w)|(?<!\w)PR\s*#?(?P<pr>\d+)(?!\w))", re.I)
PATH_REF = re.compile(r"(?<![\w/.:\\-])(?:scripts|tests|docs|reports|src|config)/[A-Za-z0-9._/\-]+")
TEST_COUNT = re.compile(r"\b\d+\s+(?:passed|pass|failed|fail|skipped|skip|tests?)\b", re.I)
# Procedure B.3 and E.4 require a command as well as a count. An explicit
# command label supports builders that are not in this common-tool vocabulary.
TEST_COMMAND = re.compile(
    r"\b(?:pytest|unittest|ctest|tox|nox)\b|\b(?:npm|pnpm|yarn|cargo|go)\s+test\b"
    r"|\b(?:command|builder)\s*:\s*\S+", re.IGNORECASE,
)
CHECKBOX = re.compile(r"^\s*-\s+\[(?P<mark>[ xX])\]\s*(?P<text>.*)$", re.M)
ISSUE_REF = re.compile(r"(?<!\w)(?:(?P<repository>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?#(?P<number>\d+)(?!\w)")
URL_REF = re.compile(r"https://(?:api\.)?github\.com/(?:repos/)?(?P<repository>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/(?P<kind>issues|pulls?)/(?P<number>\d+)\b")
HEDGE = re.compile(r"\b(deferred|follow-up|partial|stub|placeholder|tracked elsewhere)\b", re.I)
NOT_EVALUATED = "NOT_EVALUATED"


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


def normalize_state_reason(value: object) -> str:
    return str(value or "").upper()


def normalize_issue(issue: dict) -> dict:
    copied = dict(issue)
    copied["state_reason"] = normalize_state_reason(copied.get("state_reason"))
    return copied


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
    state = (issue.get("successor_states") or {}).get(str(number))
    if isinstance(state, dict):
        value = state.get("state") or ""
        reason = normalize_state_reason(state.get("state_reason"))
        return f"{value}:{reason}" if reason else str(value)
    return str(state) if state is not None else None


def successor_ok(issue: dict, number: str | int) -> bool:
    state = (successor_state(issue, number) or "").lower()
    return state in {"open", "pass", "closed:completed", "completed"}


def issue_references(text: str) -> list[str]:
    refs = []
    for match in ISSUE_REF.finditer(text):
        repository = match.group("repository")
        number = match.group("number")
        refs.append(f"{repository}#{number}" if repository else number)
    refs.extend(f"{match.group('repository')}#{match.group('number')}" for match in URL_REF.finditer(text))
    return refs


def reference_target(reference: str, repo: str) -> tuple[str, int]:
    if "#" in reference:
        repository, number = reference.rsplit("#", 1)
        return repository, int(number)
    return repo, int(reference)


def has_decision_text(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in (
        "maintainer decision",
        "owner decision",  # wording-allow: historical decision evidence
        "retired", "passed date",
    ))


def evidence_status(issue: dict, *, allow_issue_reference: bool = True) -> tuple[bool, bool, list[str]]:
    evidence = closure_evidence_text(issue)
    reasons: list[str] = []
    has_reference = False
    refs = issue_references(evidence)
    for match in EVIDENCE_REF.finditer(evidence):
        token = match.group(0)
        if token.lower().startswith("pr"):
            refs.append(re.sub(r"\D", "", token))
        elif not token.startswith("#"):
            has_reference = has_reference or token in issue.get("default_branch_shas", [])
    for ref in refs:
        repo = issue.get("repository_slug", "")
        ref_repo, ref_number = reference_target(ref, repo)
        if ref_repo.lower() != repo.lower():
            continue
        has_reference = has_reference or any(
            pr.get("number") == ref_number
            and pr.get("merged")
            and pr.get("merge_commit_sha") in issue.get("default_branch_shas", [])
            for pr in issue.get("pull_requests", [])
        )
        linked = (issue.get("successor_states") or {}).get(ref)
        if allow_issue_reference and isinstance(linked, dict):
            own_evidence = linked.get("evidence")
            if (str(linked.get("state", "")).lower() == "closed"
                    and normalize_state_reason(linked.get("state_reason")) == "COMPLETED"
                    and not linked.get("is_pull_request") and isinstance(own_evidence, dict)):
                own_ok, own_tests, _ = evidence_status(own_evidence, allow_issue_reference=False)
                has_reference = has_reference or (own_ok and own_tests)
    if not has_reference:
        reasons.append("no resolving default-branch SHA or pull request")
    paths = [path.rstrip(".,);:") for path in PATH_REF.findall(evidence)]
    existing = issue.get("paths_at_refs") or {}
    missing_paths = [path for path in paths if not existing.get(path)]
    if not paths:
        reasons.append("no cited path exists at the evidence revision")
    elif missing_paths:
        reasons.append("one or more cited paths do not exist at the evidence revision")
    has_test = bool(TEST_COUNT.search(evidence) and TEST_COMMAND.search(evidence))
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
        return RuleResult(2, NOT_EVALUATED, "review record not evaluated: no merged pull request")
    for pr in prs:
        reviewed = pr.get("review_head_sha")
        reviewer = pr.get("reviewer") or pr.get("reviewed_by")
        merged = pr.get("head_sha")
        if not reviewed:
            return RuleResult(2, NOT_EVALUATED, "review record not evaluated: reviewed head not found")
        if not reviewer:
            return RuleResult(2, NOT_EVALUATED, "review record not evaluated: reviewer not found")
        if len(str(reviewed)) < 7 or not str(merged or "").lower().startswith(str(reviewed).lower()):
            return RuleResult(2, "FAIL", "reviewed head differs from merged head")
    return RuleResult(2, "PASS", "reviewed head equals merged head and reviewer is recorded")


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
        refs = issue_references(match.group("text"))
        if not any(successor_ok(issue, ref) for ref in refs):
            failures.append(match.group("text").strip() or "unticked checkbox")
    if failures:
        return RuleResult(5, "FAIL", "unticked acceptance item lacks resolving successor")
    return RuleResult(5, "PASS", "checkboxes are ticked or routed")


def check_successor_or_decision(issue: dict) -> RuleResult:
    text = text_blob(issue)
    state_reason = issue.get("state_reason")
    applies = state_reason in {"NOT_PLANNED", "DUPLICATE"} or re.search(r"\b(duplicate|superseded)\b", text, re.I)
    if not applies:
        return RuleResult(6, "PASS", "successor rule not triggered")
    refs = issue_references(text)
    if any(successor_ok(issue, ref) for ref in refs) or has_decision_text(text):
        return RuleResult(6, "PASS", "successor or decision resolves")
    return RuleResult(6, "FAIL", "not-planned, duplicate, or superseded closure lacks resolving successor or decision")


def check_hedges(issue: dict) -> RuleResult:
    bad = []
    for line in text_blob(issue).splitlines():
        if HEDGE.search(line):
            refs = issue_references(line)
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
    window = timedelta(minutes=10)
    stamps = sorted(
        stamp for item in closures
        if item.get("closed_by") == actor
        and (stamp := parse_instant(item.get("closed_at"))) is not None
    )
    exceeds_threshold = any(
        bisect_right(stamps, start + window) - index > 5
        for index, start in enumerate(stamps)
        if start <= closed_at <= start + window
    )
    rule3_ok, _has_test, _reasons = evidence_status(issue)
    if exceeds_threshold and not rule3_ok:
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
    value = issue.get("body_edited_after_close")
    if value is None:
        return RuleResult(10, NOT_EVALUATED, "body edit history not evaluated")
    if value:
        return RuleResult(10, "WARN", "body edited after closure")
    return RuleResult(10, "PASS", "no post-closure body edit recorded")


def evaluate_issue(issue: dict, closures: Iterable[dict] = ()) -> dict:
    issue = normalize_issue(issue)
    closure_list = [normalize_issue(item) for item in closures]
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
    elif any(item.verdict in {"WARN", NOT_EVALUATED} for item in results):
        verdict = "WARN"
    return {
        "repository": issue.get("repository", ""),
        "number": issue_number(issue.get("number")),
        "verdict": verdict,
        "rules": [item.__dict__ for item in results],
    }


class ApiBudgetExceeded(RuntimeError):
    """Collection is incomplete; this condition must not become absent evidence."""


class GitHubReader:
    def __init__(self, cache_dir: Path | None = None, budget: int = API_BUDGET):
        if not 0 <= budget <= API_BUDGET:
            raise ValueError(f"API budget must be between 0 and {API_BUDGET}")
        if cache_dir is None:
            cache_dir = Path(tempfile.mkdtemp(prefix="closure-check-cache-"))
        self.cache_dir = cache_dir
        self.budget = budget
        self.calls = 0
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, route: str) -> Path:
        # Exact request identity avoids punctuation collisions and oversized
        # GraphQL filenames. Legacy cache entries are deliberately not reused.
        key = hashlib.sha256(route.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key}.json"

    def _run_gh(self, args: list[str]) -> str:
        if self.calls >= self.budget:
            raise ApiBudgetExceeded("GitHub API budget exceeded; collection incomplete")
        self.calls += 1
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gh api failed")
        return result.stdout

    def api(self, route: str) -> object:
        cached = self._cache_path(route)
        if cached.exists():
            return json.loads(cached.read_text(encoding="utf-8"))
        stdout = self._run_gh(["gh", "api", "--method", "GET", route])
        cached.write_text(stdout, encoding="utf-8", newline="\n")
        return json.loads(stdout)

    def paginated_api(self, route: str) -> tuple[list[object], int | None]:
        cached = self._cache_path(f"paginate/{route}")
        if cached.exists():
            data = json.loads(cached.read_text(encoding="utf-8"))
            return list(data["items"]), data.get("total_count")
        items: list[object] = []
        total_count: int | None = None
        seen = set()
        while route:
            if route in seen:
                raise RuntimeError("pagination repeated a page; collection incomplete")
            seen.add(route)
            # One subprocess per response page: --paginate hides API calls and
            # therefore cannot enforce the issue's per-run request ceiling.
            stdout = self._run_gh(["gh", "api", "--method", "GET", "--include", route])
            headers, separator, body = stdout.replace("\r\n", "\n").partition("\n\n")
            if not separator:
                raise RuntimeError("API response headers missing; collection incomplete")
            page = json.loads(body)
            if isinstance(page, dict) and "items" in page:
                if page.get("incomplete_results"):
                    raise RuntimeError("GitHub search is incomplete")
                total_count = page.get("total_count", total_count)
                items.extend(page.get("items") or [])
            elif isinstance(page, list):
                items.extend(page)
            else:
                items.append(page)
            route = self._next_page(headers)
        cached.write_text(json.dumps({"total_count": total_count, "items": items}, indent=2) + "\n", encoding="utf-8", newline="\n")
        return items, total_count

    @staticmethod
    def _next_page(headers: str) -> str:
        for line in headers.splitlines():
            if not line.lower().startswith("link:"):
                continue
            match = re.search(r'<([^>]+)>;\s*rel="next"', line)
            if not match:
                continue
            url = urlsplit(match.group(1))
            if url.scheme != "https" or url.netloc != "api.github.com":
                raise RuntimeError("untrusted pagination link")
            return url.path.lstrip("/") + (f"?{url.query}" if url.query else "")
        return ""

    def graphql(self, query: str) -> object:
        cached = self._cache_path(f"graphql/{query}")
        if cached.exists():
            return json.loads(cached.read_text(encoding="utf-8"))
        stdout = self._run_gh(["gh", "api", "graphql", "--raw-field", f"query={query}"])
        cached.write_text(stdout, encoding="utf-8", newline="\n")
        return json.loads(stdout)

    def try_api(self, route: str) -> object | None:
        try:
            return self.api(route)
        except ApiBudgetExceeded:
            raise
        except RuntimeError:
            return None


def _login(value: object) -> str:
    if isinstance(value, dict):
        return str(value.get("login") or "")
    return ""


def _closed_by_timeline(timeline: list[object]) -> tuple[str, str]:
    closer_type = "nothing"
    closed_by = ""
    for item in timeline:
        if not isinstance(item, dict):
            continue
        event = item.get("event")
        if event == "closed":
            closed_by = _login(item.get("actor"))
            if item.get("commit_id"):
                closer_type = "commit"
            else:
                closer_type = "comment"
    return closer_type, closed_by


def _body_edit_status(raw: dict, reader: GitHubReader, repo: str, number: int, closed_at: str | None) -> bool | None:
    repo_org, name = repo.split("/", 1)
    query = f"""
    query {{
      repository(owner:{json.dumps(repo_org)}, name:{json.dumps(name)}) {{ # wording-allow: GitHub API field
        issue(number:{int(number)}) {{
          lastEditedAt
          userContentEdits(first: 100) {{ nodes {{ editedAt }} }}
        }}
      }}
    }}
    """
    try:
        data = reader.graphql(query)
    except ApiBudgetExceeded:
        raise
    except RuntimeError:
        return None
    issue = (((data.get("data") or {}).get("repository") or {}).get("issue") or {}) if isinstance(data, dict) else {}
    if not issue:
        return None
    closed = parse_instant(closed_at)
    if not closed:
        return None
    edits = [issue.get("lastEditedAt")]
    edits.extend((node or {}).get("editedAt") for node in (((issue.get("userContentEdits") or {}).get("nodes")) or []))
    known = [parse_instant(value) for value in edits if value]
    if not known:
        return False
    return any(value and value > closed for value in known)


def _review_record(pr: dict, reader: GitHubReader, repo: str, pr_number: int) -> tuple[str | None, str | None]:
    reviewed_head = None
    reviewer = None
    reviews = reader.try_api(f"repos/{repo}/pulls/{pr_number}/reviews?per_page=100")
    if isinstance(reviews, list):
        for review in reversed(reviews):
            if review.get("state") != "APPROVED":
                continue
            commit_id = review.get("commit_id")
            if commit_id:
                reviewed_head = commit_id
                reviewer = _login(review.get("user")) or "reviewer"
                break
    if reviewed_head:
        return reviewed_head, reviewer
    comments, _total = reader.paginated_api(f"repos/{repo}/issues/{pr_number}/comments?per_page=100")
    for comment in reversed(comments):
        if not isinstance(comment, dict):
            continue
        match = re.search(r"review(?:ed)? head:?\s*([0-9a-f]{7,40})", comment.get("body") or "", re.I)
        if match:
            return match.group(1), _login(comment.get("user")) or "reviewer"
    return None, None


def _commit_closes_via_default_merged_pr(reader: GitHubReader, repo: str, sha: str, default_branch: str) -> bool:
    pulls = reader.try_api(f"repos/{repo}/commits/{sha}/pulls")
    if not isinstance(pulls, list):
        return False
    for pull in pulls:
        if not isinstance(pull, dict):
            continue
        base = pull.get("base") or {}
        if pull.get("merged_at") and isinstance(base, dict) and base.get("ref") == default_branch:
            return True
    return False


def _on_default_branch(reader: GitHubReader, repo: str, default_branch: str, sha: str) -> bool:
    compare = reader.try_api(f"repos/{repo}/compare/{quote(default_branch, safe='')}...{sha}")
    return isinstance(compare, dict) and compare.get("status") in {"behind", "identical"}


def _neutral_issue(raw: dict, reader: GitHubReader, repo: str, *, collect_successor_evidence: bool = True) -> dict:
    number = raw["number"]
    comments, _comment_total = reader.paginated_api(f"repos/{repo}/issues/{number}/comments?per_page=100")
    timeline, _timeline_total = reader.paginated_api(f"repos/{repo}/issues/{number}/timeline?per_page=100")
    repo_info = reader.try_api(f"repos/{repo}")
    default_branch = "main"
    if isinstance(repo_info, dict):
        default_branch = repo_info.get("default_branch") or default_branch
    closed_at = raw.get("closed_at")
    closed_events = [event for event in timeline if isinstance(event, dict) and event.get("event") == "closed"]
    commit_id = closed_events[-1].get("commit_id") if closed_events else None
    closer_type, closed_by = _closed_by_timeline(timeline)
    if closer_type == "commit" and commit_id and _commit_closes_via_default_merged_pr(reader, repo, commit_id, default_branch):
        closer_type = "merged_pr"
    neutral_comments = [
        {
            "created_at": item.get("created_at"),
            "closing_evidence": True,
            "body": item.get("body") or "",
        }
        for item in comments if isinstance(item, dict)
    ]
    evidence = "\n".join([raw.get("body") or ""] + [item["body"] for item in neutral_comments])
    # E.3 only consumes closing evidence. Body references still need state for
    # E.5-E.7, but recursively collecting their delivery evidence cannot qualify
    # a closing comment that never cites them.
    evidence_refs = set(issue_references("\n".join(item["body"] for item in neutral_comments)))
    shas = {
        match.group(0) for match in EVIDENCE_REF.finditer(evidence)
        if not match.group(0).startswith("#") and not match.group(0).lower().startswith("pr")
    }
    default_branch_shas = []
    for sha in shas:
        if _on_default_branch(reader, repo, default_branch, sha):
            default_branch_shas.append(sha)
    successor_states = {}
    linked_issues = {}
    for ref in issue_references(evidence):
        ref_repo, ref_number = reference_target(ref, repo)
        linked = reader.try_api(f"repos/{ref_repo}/issues/{ref_number}")
        linked_issues[ref] = linked
        if isinstance(linked, dict):
            state = {"state": linked.get("state"), "state_reason": normalize_state_reason(linked.get("state_reason")), "is_pull_request": bool(linked.get("pull_request"))}
            successor_states[ref] = state
            if (collect_successor_evidence and ref in evidence_refs and ref_repo.lower() == repo.lower()
                    and str(state["state"]).lower() == "closed" and state["state_reason"] == "COMPLETED"
                    and not state["is_pull_request"]):
                own_evidence = _neutral_issue(linked, reader, ref_repo, collect_successor_evidence=False)
                state["evidence"] = own_evidence
                own_ok, own_tests, _ = evidence_status(own_evidence, allow_issue_reference=False)
                if own_ok and own_tests:
                    default_branch_shas.extend(own_evidence["default_branch_shas"])
    pull_requests = []
    foreign_pull_requests = []
    pr_numbers = {int(re.sub(r"\D", "", match.group(0))) for match in EVIDENCE_REF.finditer(evidence) if match.group(0).lower().startswith("pr")}
    pr_targets = {(repo, pr_number) for pr_number in pr_numbers}
    for ref in issue_references(evidence):
        ref_repo, ref_number = reference_target(ref, repo)
        if "#" in ref:
            pr_targets.add((ref_repo, ref_number))
        else:
            linked = linked_issues.get(ref)
            if isinstance(linked, dict) and linked.get("pull_request"):
                pr_targets.add((ref_repo, ref_number))
    for item in timeline:
        if isinstance(item, dict):
            source = item.get("source") or {}
            issue = source.get("issue") or {}
            pr_url = ((issue.get("pull_request") or {}).get("url")) if isinstance(issue, dict) else None
            if pr_url:
                target = re.fullmatch(r"/(?:repos/)?([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pulls?/(\d+)/?", urlsplit(pr_url).path)
                if target:
                    pr_targets.add((target.group(1), int(target.group(2))))
    for pr_repo, pr_number in sorted(pr_targets):
        pr = reader.try_api(f"repos/{pr_repo}/pulls/{pr_number}")
        if isinstance(pr, dict):
            if pr_repo.lower() != repo.lower():
                foreign_pull_requests.append({"repository": pr_repo, "number": pr_number, "merged": bool(pr.get("merged_at"))})
                continue
            reviewed_head, reviewer = _review_record(pr, reader, pr_repo, pr_number)
            merge_commit_sha = pr.get("merge_commit_sha")
            pull_requests.append({
                "number": pr_number,
                "merged": bool(pr.get("merged_at")),
                "head_sha": ((pr.get("head") or {}).get("sha")),
                "review_head_sha": reviewed_head,
                "reviewer": reviewer,
                "merge_commit_sha": merge_commit_sha,
                "body": pr.get("body") or "",
            })
            if pr.get("merged_at") and merge_commit_sha and _on_default_branch(reader, repo, default_branch, merge_commit_sha):
                default_branch_shas.append(merge_commit_sha)
    paths_at_refs = {}
    for path in {item.rstrip(".,);:") for item in PATH_REF.findall(evidence)}:
        paths_at_refs[path] = False
        for sha in default_branch_shas:
            if reader.try_api(f"repos/{repo}/contents/{quote(path, safe='/')}?ref={sha}") is not None:
                paths_at_refs[path] = True
                break
    return {
        "repository": repo.split("/")[-1],
        "repository_slug": repo,
        "number": number,
        "state_reason": normalize_state_reason(raw.get("state_reason")),
        "created_at": raw.get("created_at"),
        "closed_at": closed_at,
        "closed_by": closed_by,
        "closer_type": closer_type,
        "body": raw.get("body") or "",
        "comments": neutral_comments,
        "pull_requests": pull_requests,
        "foreign_pull_requests": foreign_pull_requests,
        "default_branch_shas": sorted(set(default_branch_shas)),
        "paths_at_refs": paths_at_refs,
        "successor_states": successor_states,
        "body_edited_after_close": _body_edit_status(raw, reader, repo, number, closed_at),
    }


def collect_live(repo: str, cache_dir: Path | None = None, *, issue: int | None = None,
                 closed_from: str | None = None, closed_to: str | None = None) -> list[dict]:
    reader = GitHubReader(cache_dir)
    if issue is not None:
        raw = reader.api(f"repos/{repo}/issues/{issue}")
        return [_neutral_issue(raw, reader, repo)]
    if not closed_from or not closed_to:
        raise ValueError("date range requires --closed-from and --closed-to")
    query = f"repo:{repo} is:issue is:closed closed:{closed_from}..{closed_to}"
    route = f"search/issues?q={quote(query, safe='')}&per_page=100"
    items, total_count = reader.paginated_api(route)
    if total_count is not None and total_count > len(items):
        raise RuntimeError(f"search returned {len(items)} of {total_count} issues")
    return [_neutral_issue(item, reader, repo) for item in items if isinstance(item, dict)]


def load_fixture(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return [normalize_issue(item) for item in data.get("issues", [])]
    if isinstance(data, list):
        return [normalize_issue(item) for item in data]
    raise ValueError("fixture must contain an issues list")


def load_auditor(path: Path | None) -> dict[int, str]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8", newline="") as stream:
        return {int(row["number"]): row["auditor_class"] for row in csv.DictReader(stream)}


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
        total = sum(item["number"] in auditor for item in evaluations)
        rate = 0 if total == 0 else matches / total
        lines.extend(["", f"- Auditor agreement: {matches}/{total} ({rate:.1%})"])
    lines.extend(["", "| Repository | Issue | Verdict | Auditor class |", "|---|---:|---|---|"])
    for item in evaluations:
        lines.append(f"| {item['repository']} | {item['number']} | {item['verdict']} | {(auditor or {}).get(item['number'], '')} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def checker_class(verdict: str) -> str:
    return {"PASS": "DONE", "WARN": "PARTLY DONE", "FAIL": "CLOSED WITHOUT DELIVERY"}[verdict]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, help="Evaluate trimmed fixture JSON.")
    parser.add_argument("--repo", help="Repository slug NAME/REPO for live read-only collection.")
    parser.add_argument("--issue", type=int, help="Single issue number for live read-only collection.")
    parser.add_argument("--closed-from", help="Closed date lower bound, YYYY-MM-DD.")
    parser.add_argument("--closed-to", help="Closed date upper bound, YYYY-MM-DD.")
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument("--auditor", type=Path, help="CSV with number and auditor_class columns.")
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
    auditor = load_auditor(args.auditor)
    write_csv(args.csv, evaluations, auditor)
    write_markdown(args.markdown, evaluations, auditor)
    return 1 if any(item["verdict"] == "FAIL" for item in evaluations) else 0


if __name__ == "__main__":
    raise SystemExit(main())
