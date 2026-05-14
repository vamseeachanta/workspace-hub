#!/usr/bin/env python3
"""Approval transaction CLI for provider-credit Kanban (#2665).

Validates live GitHub issue state, canonical plan, and latest review artifacts,
then performs an idempotent, audited approval transaction:
  1. acquire per-issue lock (.planning/approval-transactions/<N>.lock)
  2. re-fetch live issue state under the lock
  3. write pending transaction journal
  4. write quarantine marker (NOT under plan-approved/)
  5. gh issue comment --body-file <prepared>
  6. gh issue edit --remove-label status:plan-review --add-label status:plan-approved
  7. refresh provider work queue
  8. verify live labels, comment idempotency, regenerated queue
  9. atomically promote quarantine marker to .planning/plan-approved/<N>.md
 10. final marker verification

Agents/cron may only --mode dry-run. Real mode requires explicit user identity,
approval source, and either a confirmation token from the local approval server
or a TTY (user invocation).
"""
from __future__ import annotations

import argparse
import fcntl
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
APPROVAL_TX_DIR = WORKSPACE_HUB / ".planning" / "approval-transactions"
APPROVED_DIR = WORKSPACE_HUB / ".planning" / "plan-approved"
PLANS_DIR = WORKSPACE_HUB / "docs" / "plans"
REVIEW_RESULTS_DIR = WORKSPACE_HUB / "scripts" / "review" / "results"
DEFAULT_PROVIDERS = ("claude", "codex", "gemini")
APPROVE_LABEL = "status:plan-approved"
REVIEW_LABEL = "status:plan-review"


class ApprovalError(RuntimeError):
    """Raised when an approval transaction precondition fails."""


@dataclass
class TxState:
    """Recovery journal record for an approval transaction.

    `phase` advances through:
      preflight -> journal_written -> quarantine_written -> comment_posted
      -> labels_transitioned -> queue_refreshed -> verified -> promoted -> complete
    """

    issue_number: int
    txid: str
    started_at: str
    user_identity: str
    approval_source: str
    plan_path: str
    plan_sha256: str
    review_artifacts: list[str]
    idempotency_key: str
    phase: str = "preflight"
    comment_body_path: str | None = None
    comment_url: str | None = None
    marker_pending_path: str | None = None
    marker_final_path: str | None = None
    error: str | None = None
    completed_at: str | None = None
    artifacts: dict[str, str] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_string(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def make_txid(issue_number: int) -> str:
    seed = f"{issue_number}-{utc_now()}-{os.getpid()}-{os.urandom(8).hex()}"
    return sha256_string(seed)[:16]


def gh_view_issue(issue_number: int, *, runner: Callable[..., Any] | None = None) -> dict[str, Any]:
    cmd = [
        "gh", "issue", "view", str(issue_number),
        "--json", "number,title,state,labels,url,body,comments",
    ]
    run = runner or subprocess.run
    result = run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def find_canonical_plan(issue_number: int, root: Path | None = None) -> Path:
    """Return the newest plan file matching the issue-NNN convention.

    Plans live at docs/plans/YYYY-MM-DD-issue-NNN-*.md. If multiple plans exist,
    the lexicographically-newest filename wins (matches continuous-planning
    discover_plan_files behavior).
    """
    root = root or WORKSPACE_HUB
    pattern = root / "docs" / "plans"
    matches: list[Path] = []
    for path in sorted(pattern.glob("*-issue-*-*.md")):
        m = re.search(r"issue-(\d+)-", path.name)
        if not m:
            continue
        if int(m.group(1)) == issue_number:
            matches.append(path)
    if not matches:
        raise ApprovalError(f"no canonical plan for #{issue_number} in {pattern}")
    matches.sort(key=lambda p: p.name)
    return matches[-1]


def parse_verdict(text: str) -> str:
    m = re.search(r"\b(APPROVE|MINOR|MAJOR|UNAVAILABLE)\b", text, re.IGNORECASE)
    return m.group(1).upper() if m else "UNKNOWN"


def latest_review_artifacts(
    issue_number: int,
    *,
    providers: tuple[str, ...] = DEFAULT_PROVIDERS,
    root: Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Return {provider: {path, verdict, empty}} using newest-filename-per-provider.

    Synthesis/disagreement/focused-review artifacts are ignored — only the named
    providers count for clean-review evidence.
    """
    root = root or WORKSPACE_HUB
    pattern = str(root / "scripts" / "review" / "results" / f"*-plan-{issue_number}-*.md")
    by_provider: dict[str, Path] = {}
    for name in sorted(glob.glob(pattern)):
        path = Path(name)
        m = re.search(rf"-plan-{issue_number}-([A-Za-z0-9_-]+)\.md$", path.name)
        if not m:
            continue
        provider = m.group(1).lower()
        if provider not in providers:
            continue
        prior = by_provider.get(provider)
        if prior is None or path.name > prior.name:
            by_provider[provider] = path
    out: dict[str, dict[str, Any]] = {}
    for provider in providers:
        path = by_provider.get(provider)
        if path is None:
            out[provider] = {"path": None, "verdict": "MISSING", "empty": True}
            continue
        text = path.read_text(encoding="utf-8")
        out[provider] = {
            "path": str(path.relative_to(root)),
            "verdict": "EMPTY" if not text.strip() else parse_verdict(text),
            "empty": not text.strip(),
        }
    return out


def review_clean(review_artifacts: dict[str, dict[str, Any]]) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    for provider, data in review_artifacts.items():
        verdict = data["verdict"]
        if data["empty"] or verdict in {"MISSING", "EMPTY", "UNAVAILABLE", "UNKNOWN", "MAJOR", "FAIL"}:
            blockers.append(f"{provider}:{verdict.lower()}")
    return not blockers, blockers


def label_names(issue: dict[str, Any]) -> list[str]:
    return [
        str(label.get("name", "")) if isinstance(label, dict) else str(label)
        for label in issue.get("labels", [])
    ]


def validate_issue_state(issue: dict[str, Any]) -> None:
    if str(issue.get("state", "")).upper() != "OPEN":
        raise ApprovalError(f"issue #{issue.get('number')} is not OPEN (state={issue.get('state')})")
    labels = label_names(issue)
    if REVIEW_LABEL not in labels:
        raise ApprovalError(
            f"issue #{issue.get('number')} does not carry {REVIEW_LABEL} (labels={labels})"
        )
    if APPROVE_LABEL in labels:
        raise ApprovalError(
            f"issue #{issue.get('number')} already has {APPROVE_LABEL}; transaction would be a no-op"
        )


def require_explicit_user_intent(
    mode: str,
    user_identity: str | None,
    approval_source: str | None,
    confirmation_token: str | None,
    *,
    is_tty: bool | None = None,
) -> None:
    if mode == "dry-run":
        return
    if not user_identity or not approval_source:
        raise ApprovalError(
            "real mode requires --user-identity and --approval-source; "
            "agents/cron may only --mode dry-run"
        )
    if is_tty is None:
        is_tty = sys.stdin.isatty() and sys.stdout.isatty()
    if not (is_tty or confirmation_token):
        raise ApprovalError(
            "real mode requires either an interactive TTY or a --confirmation-token "
            "from the local approval server (scripts/ai/provider-kanban-server.py); "
            "non-interactive automated callers must use --mode dry-run"
        )


def acquire_issue_lock(issue_number: int, *, tx_dir: Path | None = None) -> Any:
    tx_dir = tx_dir or APPROVAL_TX_DIR
    """Acquire an exclusive flock on a per-issue lockfile.

    Returns an open file descriptor whose close() releases the lock. Raises
    ApprovalError if another transaction holds the lock.
    """
    assert tx_dir is not None
    tx_dir.mkdir(parents=True, exist_ok=True)
    lock_path = tx_dir / f"{issue_number}.lock"
    fd = open(lock_path, "a+")
    try:
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        fd.close()
        raise ApprovalError(
            f"another approval transaction holds the lock for #{issue_number} "
            f"({lock_path}); to recover an interrupted transaction use --resume <txid>"
        ) from e
    return fd


def find_active_transaction(issue_number: int, *, tx_dir: Path | None = None) -> dict[str, Any] | None:
    """Return the most recent in-flight transaction journal entry, or None."""
    tx_dir = tx_dir or APPROVAL_TX_DIR
    tx_dir.mkdir(parents=True, exist_ok=True)
    candidates = sorted(tx_dir.glob(f"{issue_number}-*.json"))
    for path in reversed(candidates):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if data.get("phase") not in {"complete", "aborted"}:
            return data
    return None


def write_journal(state: TxState, *, tx_dir: Path | None = None) -> Path:
    tx_dir = tx_dir or APPROVAL_TX_DIR
    tx_dir.mkdir(parents=True, exist_ok=True)
    path = tx_dir / f"{state.issue_number}-{state.txid}.json"
    payload = json.dumps(asdict(state), indent=2, sort_keys=True) + "\n"
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, path)
    return path


def build_comment_body(state: TxState, plan_path: Path, review_artifacts: dict[str, dict[str, Any]]) -> str:
    lines = [
        f"## Plan approved — #{state.issue_number}",
        "",
        f"Approved by: {state.user_identity}",
        f"Approval source: {state.approval_source}",
        f"Approved at: {state.started_at}",
        f"Transaction id: {state.txid}",
        f"Idempotency key: {state.idempotency_key}",
        "",
        f"Plan path: {plan_path.relative_to(WORKSPACE_HUB)}",
        f"Plan-SHA256: {state.plan_sha256}",
        "",
        "Review artifacts:",
    ]
    for provider, data in sorted(review_artifacts.items()):
        lines.append(f"- {provider}: {data['path']} ({data['verdict']})")
    lines.extend(
        [
            "",
            "Verdicts: " + ", ".join(
                f"{p} {d['verdict']}" for p, d in sorted(review_artifacts.items())
            ),
            "",
            "Choices: Approve / Revise / Hold — this comment records Approve.",
            "Execution remains unauthorized until approval marker creation in "
            ".planning/plan-approved/.",
            "",
            f"Approval marker (atomic promotion target): .planning/plan-approved/{state.issue_number}.md",
        ]
    )
    return "\n".join(lines) + "\n"


def build_marker_text(state: TxState) -> str:
    return (
        f"# Plan Approval Marker: Issue #{state.issue_number}\n\n"
        f"Approved by: {state.user_identity}\n"
        f"Approval source: {state.approval_source}\n"
        f"Approved at: {state.started_at}\n"
        f"Transaction id: {state.txid}\n"
        f"Idempotency key: {state.idempotency_key}\n"
        f"Plan: {state.plan_path}\n"
        f"Plan-SHA256: {state.plan_sha256}\n"
        f"Review artifacts:\n"
        + "\n".join(f"- {p}" for p in state.review_artifacts)
        + "\n"
        f"\nVerification: comment posted at {state.comment_url}; labels transitioned "
        f"({REVIEW_LABEL} → {APPROVE_LABEL}); provider queue refreshed.\n"
    )


def write_quarantine_marker(state: TxState, *, tx_dir: Path | None = None) -> Path:
    tx_dir = tx_dir or APPROVAL_TX_DIR
    tx_dir.mkdir(parents=True, exist_ok=True)
    path = tx_dir / f"{state.issue_number}-{state.txid}.marker.pending.md"
    path.write_text(build_marker_text(state), encoding="utf-8")
    return path


def gh_comment_with_body_file(
    issue_number: int,
    body_path: Path,
    *,
    runner: Callable[..., Any] | None = None,
) -> str:
    if not body_path.exists():
        raise ApprovalError(f"prepared comment body file does not exist: {body_path}")
    run = runner or subprocess.run
    cmd = ["gh", "issue", "comment", str(issue_number), "--body-file", str(body_path)]
    result = run(cmd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def gh_transition_labels(
    issue_number: int,
    *,
    remove: str = REVIEW_LABEL,
    add: str = APPROVE_LABEL,
    runner: Callable[..., Any] | None = None,
) -> None:
    run = runner or subprocess.run
    cmd = [
        "gh", "issue", "edit", str(issue_number),
        "--remove-label", remove, "--add-label", add,
    ]
    run(cmd, check=True, capture_output=True, text=True)


def refresh_provider_work_queue(*, runner: Callable[..., Any] | None = None) -> None:
    run = runner or subprocess.run
    cmd = [
        "uv", "run", "--no-project", "python",
        str(WORKSPACE_HUB / "scripts" / "ai" / "provider-work-queue.py"),
    ]
    run(cmd, check=True, capture_output=True, text=True)


def verify_post_mutation(
    issue_number: int,
    idempotency_key: str,
    *,
    runner: Callable[..., Any] | None = None,
) -> tuple[bool, list[str]]:
    """Re-fetch the live issue and confirm label transition + idempotent comment."""
    issue = gh_view_issue(issue_number, runner=runner)
    labels = label_names(issue)
    problems: list[str] = []
    if APPROVE_LABEL not in labels:
        problems.append(f"missing {APPROVE_LABEL} after edit")
    if REVIEW_LABEL in labels:
        problems.append(f"{REVIEW_LABEL} still present after edit")
    comments = issue.get("comments") or []
    if not any(idempotency_key in str(c.get("body", "")) for c in comments):
        problems.append("approval comment idempotency_key not found in live comments")
    return not problems, problems


def promote_marker(state: TxState, *, approved_dir: Path | None = None) -> Path:
    approved_dir = approved_dir or APPROVED_DIR
    """Atomically promote a quarantine marker to .planning/plan-approved/<N>.md.

    The plan requires this to happen only AFTER verification succeeds. Promotion
    is os.replace-atomic; no intermediate state where both copies exist.
    """
    assert approved_dir is not None
    approved_dir.mkdir(parents=True, exist_ok=True)
    pending_rel = state.marker_pending_path
    if pending_rel is None:
        pending = None
    elif Path(pending_rel).is_absolute():
        pending = Path(pending_rel)
    else:
        pending = WORKSPACE_HUB / pending_rel
    if pending is None or not pending.exists():
        raise ApprovalError(
            f"quarantine marker missing for tx {state.txid}; cannot promote"
        )
    final = approved_dir / f"{state.issue_number}.md"
    os.replace(pending, final)
    try:
        state.marker_final_path = str(final.relative_to(WORKSPACE_HUB))
    except ValueError:
        state.marker_final_path = str(final)
    state.marker_pending_path = None
    return final


def execute_transaction(
    issue_number: int,
    *,
    mode: str,
    user_identity: str | None,
    approval_source: str | None,
    confirmation_token: str | None,
    resume_txid: str | None = None,
    runner: Callable[..., Any] | None = None,
    is_tty: bool | None = None,
    tx_dir: Path | None = None,
    approved_dir: Path | None = None,
) -> dict[str, Any]:
    tx_dir = tx_dir or APPROVAL_TX_DIR
    approved_dir = approved_dir or APPROVED_DIR
    """Run the full approval pipeline. Returns the final journal JSON.

    On any failure after the first mutation, the journal records the phase reached
    and the quarantine marker is preserved. Re-invoke with --resume <txid>.
    """
    require_explicit_user_intent(mode, user_identity, approval_source, confirmation_token, is_tty=is_tty)

    # Preflight ─ before lock
    issue = gh_view_issue(issue_number, runner=runner)
    validate_issue_state(issue)
    plan_path = find_canonical_plan(issue_number)
    review_artifacts = latest_review_artifacts(issue_number)
    clean, blockers = review_clean(review_artifacts)
    if not clean:
        raise ApprovalError(
            f"review artifacts are not clean: {blockers}; address before approval"
        )

    # Concurrency gate ─ check for active transaction
    active = find_active_transaction(issue_number, tx_dir=tx_dir)
    if active and not resume_txid:
        raise ApprovalError(
            f"another transaction is active for #{issue_number} (txid={active['txid']}, "
            f"phase={active['phase']}); re-invoke with --resume {active['txid']} or wait for it to complete"
        )
    if resume_txid and active is None:
        raise ApprovalError(f"no active transaction matches --resume {resume_txid}")
    if resume_txid and active and active["txid"] != resume_txid:
        raise ApprovalError(
            f"resume txid mismatch: requested {resume_txid}, active is {active['txid']}"
        )

    lock_fd = acquire_issue_lock(issue_number, tx_dir=tx_dir)
    try:
        # Re-fetch under lock to defeat race against label-flip elsewhere.
        issue = gh_view_issue(issue_number, runner=runner)
        validate_issue_state(issue)

        if resume_txid:
            state = TxState(**{k: v for k, v in active.items() if k in TxState.__annotations__})
        else:
            plan_sha = sha256_file(plan_path)
            idempotency_key = sha256_string(f"{issue_number}|{plan_path.name}|{plan_sha}")[:32]
            state = TxState(
                issue_number=issue_number,
                txid=make_txid(issue_number),
                started_at=utc_now(),
                user_identity=user_identity or "",
                approval_source=approval_source or "",
                plan_path=str(plan_path.relative_to(WORKSPACE_HUB)),
                plan_sha256=plan_sha,
                review_artifacts=[d["path"] for d in review_artifacts.values() if d.get("path")],
                idempotency_key=idempotency_key,
            )

        if mode == "dry-run":
            state.phase = "dry-run-only"
            state.completed_at = utc_now()
            # Dry-run never mutates the journal directory either — it only emits
            # a planned-transaction JSON to stdout. This keeps agents from leaving
            # phantom transactions in .planning/approval-transactions/.
            preview_body = build_comment_body(state, plan_path, review_artifacts)
            return {
                **asdict(state),
                "preview_comment_body": preview_body,
                "preview_marker_text": build_marker_text(state),
                "planned_mutations": [
                    f"gh issue comment {issue_number} --body-file <prepared>",
                    f"gh issue edit {issue_number} --remove-label {REVIEW_LABEL} --add-label {APPROVE_LABEL}",
                    f"refresh provider-work-queue",
                    f"promote quarantine marker to .planning/plan-approved/{issue_number}.md",
                ],
            }

        # Real mode begins here. Each phase is gated by the journal-recorded
        # state, so --resume picks up at the next pending step without
        # re-running anything that already succeeded.

        # Phase ordering (each later phase implies all earlier are done):
        phase_order = [
            "preflight", "journal_written", "comment_prepared",
            "quarantine_written", "comment_posted", "labels_transitioned",
            "queue_refreshed", "verified", "promoted", "complete",
        ]

        def at_least(phase: str) -> bool:
            return phase_order.index(state.phase) >= phase_order.index(phase)

        if not at_least("journal_written"):
            write_journal(state, tx_dir=tx_dir)
            state.phase = "journal_written"
            write_journal(state, tx_dir=tx_dir)

        body_path = tx_dir / f"{state.issue_number}-{state.txid}.comment.md"
        if not at_least("comment_prepared"):
            body_path.write_text(
                build_comment_body(state, plan_path, review_artifacts),
                encoding="utf-8",
            )
            try:
                state.comment_body_path = str(body_path.relative_to(WORKSPACE_HUB))
            except ValueError:
                state.comment_body_path = str(body_path)
            state.phase = "comment_prepared"
            write_journal(state, tx_dir=tx_dir)

        if not at_least("quarantine_written"):
            marker_pending = write_quarantine_marker(state, tx_dir=tx_dir)
            try:
                state.marker_pending_path = str(marker_pending.relative_to(WORKSPACE_HUB))
            except ValueError:
                state.marker_pending_path = str(marker_pending)
            state.phase = "quarantine_written"
            write_journal(state, tx_dir=tx_dir)

        if not at_least("comment_posted"):
            try:
                comment_url = gh_comment_with_body_file(
                    state.issue_number, body_path, runner=runner
                )
                state.comment_url = comment_url
                state.phase = "comment_posted"
                write_journal(state, tx_dir=tx_dir)
            except Exception as exc:  # noqa: BLE001 — record and re-raise for caller
                state.error = f"comment_post_failed: {exc}"
                write_journal(state, tx_dir=tx_dir)
                raise

        if not at_least("labels_transitioned"):
            try:
                gh_transition_labels(state.issue_number, runner=runner)
                state.phase = "labels_transitioned"
                write_journal(state, tx_dir=tx_dir)
            except Exception as exc:  # noqa: BLE001
                state.error = f"label_transition_failed: {exc}"
                write_journal(state, tx_dir=tx_dir)
                raise

        if not at_least("queue_refreshed"):
            try:
                refresh_provider_work_queue(runner=runner)
                state.phase = "queue_refreshed"
                write_journal(state, tx_dir=tx_dir)
            except Exception as exc:  # noqa: BLE001
                state.error = f"queue_refresh_failed: {exc}"
                write_journal(state, tx_dir=tx_dir)
                raise

        if not at_least("verified"):
            ok, problems = verify_post_mutation(
                state.issue_number, state.idempotency_key, runner=runner
            )
            if not ok:
                state.error = f"verification_failed: {problems}"
                write_journal(state, tx_dir=tx_dir)
                raise ApprovalError(
                    f"post-mutation verification failed: {problems}; "
                    f"quarantine marker preserved at {state.marker_pending_path}"
                )
            state.phase = "verified"
            write_journal(state, tx_dir=tx_dir)

        if not at_least("promoted"):
            promote_marker(state, approved_dir=approved_dir)
            state.phase = "promoted"
            write_journal(state, tx_dir=tx_dir)

        state.phase = "complete"
        state.completed_at = utc_now()
        write_journal(state, tx_dir=tx_dir)
        return asdict(state)
    finally:
        try:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        lock_fd.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Approval transaction CLI for provider-credit Kanban (#2665)",
    )
    parser.add_argument("--issue", type=int, required=True, help="GitHub issue number")
    parser.add_argument(
        "--mode",
        choices=["dry-run", "real"],
        default="dry-run",
        help="dry-run validates and emits the planned transaction; real performs all mutations",
    )
    parser.add_argument("--user-identity", help="Identity of the approving user (required for real mode)")
    parser.add_argument(
        "--approval-source",
        help="Source of approval intent (e.g., 'localhost approval server', 'cli')",
    )
    parser.add_argument(
        "--confirmation-token",
        help="Ephemeral token from provider-kanban-server.py; required for real mode in non-TTY contexts",
    )
    parser.add_argument("--resume", dest="resume_txid", help="Resume a previously interrupted txid")
    parser.add_argument(
        "--output-json",
        help="Optional path to write the final transaction JSON; defaults to stdout",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = execute_transaction(
            args.issue,
            mode=args.mode,
            user_identity=args.user_identity,
            approval_source=args.approval_source,
            confirmation_token=args.confirmation_token,
            resume_txid=args.resume_txid,
        )
    except ApprovalError as exc:
        print(f"approve-provider-plan: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output_json:
        Path(args.output_json).write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
