#!/usr/bin/env python3
"""Server-side plan-approval label-authority gate for #2817."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from label_authority import (  # noqa: E402
    gh_json,
    is_authorized_human,
    label_is_fresh,
    parse_iso,
    verified_label_event,
)
from plan_approval_gate_io import (  # noqa: E402
    _normalize_path,
    fetch_actor_type,
    fetch_plan_revision_anchor,
    load_current_issue_labels,
    load_issue_binding_sources,
    plan_blob_matches_revision,
    revision_reaches_head,
)

PLAN_APPROVED_LABEL = "status:plan-approved"
_BRANCH_ISSUE_RE = re.compile(
    r"^(?:feat|feature|fix|bugfix|chore|docs|refactor|test)/(?P<issue>\d+)(?:[-_/].*)?$"
)
_IMPLEMENTATION_EXT_RE = re.compile(r"\.(py|js|ts|sh|rs|go)$")
_LOW_RISK_PREFIXES = (
    "scripts/", ".github/", "docs/", "config/", ".claude/skills/",
    ".claude/hooks/", "tests/", "specs/",
)
_PLAN_PATH_RE = re.compile(r"`?(docs/plans/[A-Za-z0-9._/-]+\.md)`?")
_REVISION_RE = re.compile(
    r"(?im)^\s*(?:plan\s+revision|revision|sha|commit)\s*[:=]\s*`?([0-9a-f]{40})`?\s*$"
)


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    reason: str


@dataclass(frozen=True)
class PlanBinding:
    plan_path: str
    revision_sha: str
    recorded_by: str
    recorded_by_type: str | None = None
    recorded_at: object | None = None


@dataclass(frozen=True)
class IssueApproval:
    issue_number: int
    label_actor: str | None
    label_actor_type: str | None
    label_applied_at: object | None
    plan_binding: PlanBinding | None
    plan_revision_time: object | None
    label_current: bool = True
    plan_revision_verified: bool = True
    plan_revision_in_head: bool = True
    plan_revision_in_base: bool = False
    plan_head_matches_revision: bool = True


@dataclass(frozen=True)
class PrContext:
    branch_name: str
    pr_author: str
    touched_paths: set[str]
    head_sha: str | None = None
    base_sha: str | None = None


def _truthy(value: str | None) -> bool:
    return (value or "").lower() in {"1", "true", "yes", "on"}


def _actor_is_bot(actor: str | None, actor_type: str | None) -> bool:
    return bool(actor and actor.lower().endswith("[bot]")) or (actor_type or "").lower() in {"bot", "app"}


def parse_owners(raw: str | None) -> set[str]:
    return {item.strip().lower() for item in (raw or "").split(",") if item.strip()}


def issue_from_branch(branch_name: str) -> int | None:
    match = _BRANCH_ISSUE_RE.match(branch_name or "")
    return int(match.group("issue")) if match else None


def resolve_linked_issues(branch_name: str) -> list[int]:
    branch_issue = issue_from_branch(branch_name)
    if branch_issue is not None:
        return [branch_issue]
    return []


def validate_owner_types(owner_types: dict[str, str | None]) -> GateDecision:
    if not owner_types:
        return GateDecision(False, "PLAN_APPROVAL_OWNERS is empty or unresolved")
    for owner, actor_type in sorted(owner_types.items()):
        if _actor_is_bot(owner, actor_type):
            return GateDecision(False, f"owner {owner!r} resolves to bot/app type {actor_type!r}")
        if not actor_type:
            return GateDecision(False, f"owner {owner!r} type could not be verified")
    return GateDecision(True, "owner allowlist is human-only")


def _comment_author(comment: dict) -> str | None:
    author = comment.get("author") or comment.get("user") or {}
    if isinstance(author, str):
        return author
    return author.get("login")


def _binding_fields(body: str) -> tuple[str, str] | None:
    paths = [_normalize_path(path) for path in _PLAN_PATH_RE.findall(body or "")]
    revisions = _REVISION_RE.findall(body or "")
    if len(paths) != 1 or len(revisions) != 1:
        return None
    return paths[0], revisions[0]


def extract_plan_binding(
    comments: list[dict],
    owners: set[str],
    actor_types: dict[str, str | None],
) -> PlanBinding | None:
    binding = None
    for comment in comments:
        fields = _binding_fields(comment.get("body") or "")
        if fields is None:
            continue
        actor = _comment_author(comment)
        actor_type = actor_types.get((actor or "").lower())
        if not is_authorized_human(actor, owners, reject_bots=True, actor_type=actor_type):
            continue
        candidate = PlanBinding(
            plan_path=fields[0],
            revision_sha=fields[1],
            recorded_by=actor or "",
            recorded_by_type=actor_type,
            recorded_at=parse_iso(
                comment.get("updatedAt")
                or comment.get("updated_at")
                or comment.get("createdAt")
                or comment.get("created_at")
            ),
        )
        if binding is None or candidate.recorded_at is None:
            binding = candidate
        elif binding.recorded_at is not None and candidate.recorded_at >= binding.recorded_at:
            binding = candidate
    return binding


def evaluate_plan_approval(
    context: PrContext,
    approvals: dict[int, IssueApproval],
    owners: set[str],
    *,
    require_separate_approver: bool = False,
) -> GateDecision:
    if not owners:
        return GateDecision(False, "PLAN_APPROVAL_OWNERS is unset; fail-closed")
    issues = resolve_linked_issues(context.branch_name)
    if not issues:
        return GateDecision(False, "no linked issue from branch name; fail-closed")
    touched = {_normalize_path(path) for path in context.touched_paths}
    for issue in issues:
        decision = _evaluate_issue(issue, context, approvals.get(issue), owners, touched,
                                   require_separate_approver)
        if not decision.allowed:
            return decision
    return GateDecision(True, f"plan approval verified for issue(s): {issues}")


def _evaluate_issue(
    issue: int,
    context: PrContext,
    approval: IssueApproval | None,
    owners: set[str],
    touched: set[str],
    require_separate: bool,
) -> GateDecision:
    if approval is None:
        return GateDecision(False, f"issue #{issue}: approval context unavailable; fail-closed")
    if not approval.label_actor or not approval.label_applied_at:
        return GateDecision(False, f"issue #{issue}: {PLAN_APPROVED_LABEL!r} label event not found")
    if not approval.label_current:
        return GateDecision(False, f"issue #{issue}: {PLAN_APPROVED_LABEL!r} label is not currently applied")
    if _actor_is_bot(approval.label_actor, approval.label_actor_type):
        return GateDecision(False, f"issue #{issue}: label actor {approval.label_actor!r} is a bot/app")
    if not is_authorized_human(approval.label_actor, owners, reject_bots=True,
                               actor_type=approval.label_actor_type):
        return GateDecision(False, f"issue #{issue}: label actor {approval.label_actor!r} not authorized")
    if require_separate and approval.label_actor.lower() == context.pr_author.lower():
        return GateDecision(False, f"issue #{issue}: separate approver required")
    return _evaluate_binding(issue, approval, owners, touched)


def _evaluate_binding(
    issue: int,
    approval: IssueApproval,
    owners: set[str],
    touched: set[str],
) -> GateDecision:
    binding = approval.plan_binding
    if binding is None:
        return GateDecision(False, f"issue #{issue}: authorized plan binding not found on issue")
    if _actor_is_bot(binding.recorded_by, binding.recorded_by_type):
        return GateDecision(False, f"issue #{issue}: plan binding recorded by bot/app")
    if not is_authorized_human(binding.recorded_by, owners, reject_bots=True,
                               actor_type=binding.recorded_by_type):
        return GateDecision(False, f"issue #{issue}: plan binding author {binding.recorded_by!r} not authorized")
    if not plan_path_matches_issue(binding.plan_path, issue):
        return GateDecision(False, f"issue #{issue}: recorded plan path does not match issue #{issue}")
    if binding.plan_path not in touched:
        return GateDecision(False, f"issue #{issue}: PR does not touch recorded plan path {binding.plan_path}")
    if not approval.plan_revision_verified:
        return GateDecision(False, f"issue #{issue}: recorded revision does not contain the plan path")
    if not approval.plan_revision_in_head:
        return GateDecision(False, f"issue #{issue}: recorded revision is not in PR head history")
    if approval.plan_revision_in_base:
        return GateDecision(False, f"issue #{issue}: recorded revision is already in PR base history")
    if not approval.plan_head_matches_revision:
        return GateDecision(False, f"issue #{issue}: PR head plan file differs from approved revision")
    if binding.recorded_at is None:
        return GateDecision(False, f"issue #{issue}: plan binding timestamp unavailable; fail-closed")
    if approval.plan_revision_time is None:
        return GateDecision(False, f"issue #{issue}: plan revision time unavailable; fail-closed")
    if not label_is_fresh(approval.label_applied_at, approval.plan_revision_time, binding.recorded_at):
        return GateDecision(False, f"issue #{issue}: approval label predates plan revision; re-approval required")
    return GateDecision(True, f"issue #{issue}: label-authority approval verified")


def plan_path_matches_issue(plan_path: str, issue: int) -> bool:
    return re.search(rf"(?:^|[-_/])issue-{issue}(?:[-_. /]|$)", _normalize_path(plan_path)) is not None


def needs_plan_approval_paths(paths: set[str]) -> bool:
    normalized = {_normalize_path(path) for path in paths}
    return any(
        _IMPLEMENTATION_EXT_RE.search(path) and not path.startswith(_LOW_RISK_PREFIXES)
        for path in normalized
    )


def load_pr_context(repo: str, pr_number: int) -> PrContext:
    data = gh_json(
        "pr", "view", str(pr_number), "--repo", repo,
        "--json", "headRefName,headRefOid,baseRefOid,author",
    ) or {}
    files = load_pr_changed_paths(repo, pr_number)
    return PrContext(
        branch_name=data.get("headRefName") or "",
        pr_author=((data.get("author") or {}).get("login")) or "",
        touched_paths={path for path in files if path},
        head_sha=data.get("headRefOid"),
        base_sha=data.get("baseRefOid"),
    )


def load_pr_changed_paths(repo: str, pr_number: int) -> set[str]:
    out = subprocess.run(
        ["gh", "pr", "diff", str(pr_number), "--repo", repo, "--name-only"],
        capture_output=True, text=True, check=True,
    ).stdout
    return {_normalize_path(line.strip()) for line in out.splitlines() if line.strip()}


def load_issue_approval(
    repo: str,
    issue: int,
    owners: set[str],
    owner_types: dict[str, str | None],
    head_sha: str | None,
    base_sha: str | None,
) -> IssueApproval:
    label_actor, label_at = verified_label_event(repo, issue, PLAN_APPROVED_LABEL)
    actor_types = dict(owner_types)
    if label_actor and label_actor.lower() not in actor_types:
        actor_types[label_actor.lower()] = fetch_actor_type(label_actor)
    label_current = PLAN_APPROVED_LABEL in load_current_issue_labels(repo, issue)
    binding = extract_plan_binding(load_issue_binding_sources(repo, issue), owners, actor_types)
    if binding:
        revision_time, revision_verified = fetch_plan_revision_anchor(
            repo, binding.revision_sha, binding.plan_path, binding.recorded_at)
        revision_in_head = revision_reaches_head(repo, binding.revision_sha, head_sha)
        revision_in_base = True if not base_sha else revision_reaches_head(repo, binding.revision_sha, base_sha)
        head_matches = plan_blob_matches_revision(repo, binding.revision_sha, head_sha, binding.plan_path)
    else:
        revision_time, revision_verified = None, False
        revision_in_head, revision_in_base, head_matches = False, True, False
    return IssueApproval(
        issue_number=issue,
        label_actor=label_actor,
        label_actor_type=actor_types.get((label_actor or "").lower()),
        label_applied_at=label_at,
        plan_binding=binding,
        plan_revision_time=revision_time,
        label_current=label_current,
        plan_revision_verified=revision_verified,
        plan_revision_in_head=revision_in_head,
        plan_revision_in_base=revision_in_base,
        plan_head_matches_revision=head_matches,
    )


def _event_pr_number() -> int | None:
    if os.environ.get("PR_NUMBER"):
        try:
            return int(os.environ["PR_NUMBER"])
        except ValueError:
            return None
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return None
    with open(event_path, encoding="utf-8") as handle:
        payload = json.load(handle)
    pr = payload.get("pull_request") or {}
    try:
        return int(pr.get("number"))
    except (TypeError, ValueError):
        return None


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GH_REPO") or os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--pr", type=int, default=_event_pr_number())
    parser.add_argument("--owners", default=os.environ.get("PLAN_APPROVAL_OWNERS", ""))
    parser.add_argument("--enabled", action="store_true", default=_truthy(os.environ.get("PLAN_APPROVAL_GATE_ENABLED")))
    parser.add_argument("--admin-prereqs-confirmed", action="store_true",
                        default=_truthy(os.environ.get("PLAN_APPROVAL_ADMIN_PREREQS_CONFIRMED")))
    parser.add_argument("--require-separate-approver", action="store_true",
                        default=_truthy(os.environ.get("PLAN_APPROVAL_REQUIRE_SEPARATE")))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    if not args.enabled:
        print("[plan-approval-gate] SKIP: PLAN_APPROVAL_GATE_ENABLED is not set.")
        print("[plan-approval-gate] Admin prereq: make Plan Approval Check required and protect "
              "status:plan-approved label before retiring the old marker gate.")
        return 0
    if not args.repo or not args.pr:
        print("[plan-approval-gate] DENY: repo or PR number unavailable; fail-closed.", file=sys.stderr)
        return 1
    if not args.admin_prereqs_confirmed:
        print("[plan-approval-gate] DENY: admin prereqs are not confirmed; make Plan Approval Check "
              "required and protect status:plan-approved before enabling.", file=sys.stderr)
        return 1
    try:
        return _run_enabled(args)
    except Exception as exc:  # pragma: no cover - exercised in live CI failures
        print(f"[plan-approval-gate] DENY: unverifiable gate context ({exc}); fail-closed.", file=sys.stderr)
        return 1


def _run_enabled(args: argparse.Namespace) -> int:
    owners = parse_owners(args.owners)
    owner_types = {owner: fetch_actor_type(owner) for owner in owners}
    owner_decision = validate_owner_types(owner_types)
    if not owner_decision.allowed:
        print(f"[plan-approval-gate] DENY: {owner_decision.reason}", file=sys.stderr)
        return 1
    context = load_pr_context(args.repo, args.pr)
    if not needs_plan_approval_paths(context.touched_paths):
        print("[plan-approval-gate] SKIP: no implementation changes requiring plan approval.")
        return 0
    issues = resolve_linked_issues(context.branch_name)
    approvals = {
        issue: load_issue_approval(args.repo, issue, owners, owner_types, context.head_sha, context.base_sha)
        for issue in issues
    }
    decision = evaluate_plan_approval(context, approvals, owners,
                                      require_separate_approver=args.require_separate_approver)
    print(f"[plan-approval-gate] {'ALLOW' if decision.allowed else 'DENY'}: {decision.reason}")
    return 0 if decision.allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
