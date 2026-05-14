"""Tests for scripts/ai/approve-provider-plan.py (#2665).

Uses monkeypatched subprocess.run runner so tests never touch live GitHub or
the repo's .planning/plan-approved directory.
"""
from __future__ import annotations

import importlib.util
import json
import threading
from pathlib import Path

import pytest

import sys

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "approve-provider-plan.py"
spec = importlib.util.spec_from_file_location("approve_provider_plan", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["approve_provider_plan"] = module  # dataclass needs the module in sys.modules
spec.loader.exec_module(module)


class FakeResult:
    def __init__(self, stdout: str = "", returncode: int = 0):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = ""


def _issue_payload(number: int, *, state: str = "OPEN", labels=None, comments=None) -> dict:
    return {
        "number": number,
        "title": "sample issue",
        "state": state,
        "url": f"https://example.test/issues/{number}",
        "body": "",
        "labels": [{"name": lbl} for lbl in (labels or ["status:plan-review"])],
        "comments": comments or [],
    }


def _setup_plan_and_reviews(root: Path, number: int) -> tuple[Path, list[Path]]:
    (root / "docs" / "plans").mkdir(parents=True, exist_ok=True)
    plan = root / "docs" / "plans" / f"2026-05-12-issue-{number}-sample.md"
    plan.write_text("# Plan body\n", encoding="utf-8")
    (root / "scripts" / "review" / "results").mkdir(parents=True, exist_ok=True)
    reviews: list[Path] = []
    for provider in ("claude", "codex", "gemini"):
        rpath = root / "scripts" / "review" / "results" / f"2026-05-12-plan-{number}-{provider}.md"
        rpath.write_text(f"Verdict: MINOR\nProvider: {provider}\n", encoding="utf-8")
        reviews.append(rpath)
    return plan, reviews


def _patch_workspace(monkeypatch, root: Path) -> tuple[Path, Path]:
    """Repoint module-level paths at a tmp workspace and return tx + approved dirs."""
    tx_dir = root / ".planning" / "approval-transactions"
    approved = root / ".planning" / "plan-approved"
    monkeypatch.setattr(module, "WORKSPACE_HUB", root)
    monkeypatch.setattr(module, "APPROVAL_TX_DIR", tx_dir)
    monkeypatch.setattr(module, "APPROVED_DIR", approved)
    monkeypatch.setattr(module, "PLANS_DIR", root / "docs" / "plans")
    monkeypatch.setattr(module, "REVIEW_RESULTS_DIR", root / "scripts" / "review" / "results")
    return tx_dir, approved


def _runner_factory(state: dict, *, comment_url: str = "https://example.test/comment/1"):
    """Returns a fake subprocess.run that simulates gh CLI for the happy path.

    state is mutated to track which gh calls were issued and what body files
    were sent, so tests can assert ordering invariants.
    """

    state.setdefault("calls", [])
    state.setdefault("comment_body_seen_at_call_time", None)
    state.setdefault("issue", None)
    state.setdefault("comment_posted", False)
    state.setdefault("labels_transitioned", False)

    def fake_run(cmd, **kwargs):
        state["calls"].append(list(cmd))
        if cmd[:3] == ["gh", "issue", "view"]:
            issue = state["issue"]
            assert issue is not None, "test must set state['issue'] before run"
            return FakeResult(stdout=json.dumps(issue))
        if cmd[:3] == ["gh", "issue", "comment"]:
            # Verify body-file argument and its existence at call time
            assert "--body-file" in cmd
            body_path = Path(cmd[cmd.index("--body-file") + 1])
            assert body_path.exists(), f"body-file must exist before gh issue comment: {body_path}"
            state["comment_body_seen_at_call_time"] = body_path.read_text(encoding="utf-8")
            state["comment_posted"] = True
            # Inject the idempotency-keyed comment back into the issue payload
            # so post-mutation verification finds it.
            issue = state["issue"]
            issue["comments"] = list(issue.get("comments", [])) + [
                {"body": state["comment_body_seen_at_call_time"]}
            ]
            return FakeResult(stdout=comment_url)
        if cmd[:3] == ["gh", "issue", "edit"]:
            state["labels_transitioned"] = True
            issue = state["issue"]
            labels = [lbl["name"] for lbl in issue["labels"]]
            if "--remove-label" in cmd:
                labels = [l for l in labels if l != cmd[cmd.index("--remove-label") + 1]]
            if "--add-label" in cmd:
                labels.append(cmd[cmd.index("--add-label") + 1])
            issue["labels"] = [{"name": l} for l in labels]
            return FakeResult()
        # provider-work-queue refresh — no-op
        if cmd[:2] == ["uv", "run"]:
            return FakeResult()
        raise AssertionError(f"unexpected subprocess call: {cmd}")

    return fake_run


# ────────────────────────────────────────────────────────────────────────────
# Plan-named tests
# ────────────────────────────────────────────────────────────────────────────


def test_approve_provider_plan_dry_run_reports_exact_transaction(tmp_path, monkeypatch):
    _patch_workspace(monkeypatch, tmp_path)
    _setup_plan_and_reviews(tmp_path, 9001)
    tracked = {"issue": _issue_payload(9001)}

    result = module.execute_transaction(
        9001,
        mode="dry-run",
        user_identity="vamsee.achanta@aceengineer.com",
        approval_source="cli",
        confirmation_token=None,
        is_tty=True,
        runner=_runner_factory(tracked),
    )

    assert result["phase"] == "dry-run-only"
    assert "planned_mutations" in result
    assert "preview_comment_body" in result
    assert "preview_marker_text" in result
    # Dry-run must NOT have written a journal nor created markers.
    tx_dir = tmp_path / ".planning" / "approval-transactions"
    assert not list(tx_dir.glob("9001-*.json")) if tx_dir.exists() else True
    # No mutating gh commands made.
    for call in tracked["calls"]:
        assert call[:3] != ["gh", "issue", "comment"], "dry-run must not post comments"
        assert call[:3] != ["gh", "issue", "edit"], "dry-run must not edit labels"


def test_approve_provider_plan_real_mode_requires_user_confirmation(tmp_path, monkeypatch):
    _patch_workspace(monkeypatch, tmp_path)
    _setup_plan_and_reviews(tmp_path, 9002)
    tracked = {"issue": _issue_payload(9002)}

    # Real mode without user_identity → ApprovalError
    with pytest.raises(module.ApprovalError, match="--user-identity"):
        module.execute_transaction(
            9002, mode="real",
            user_identity=None, approval_source=None,
            confirmation_token=None, is_tty=False,
            runner=_runner_factory(tracked),
        )

    # Real mode with identity but no TTY and no confirmation token → ApprovalError
    with pytest.raises(module.ApprovalError, match="TTY or a --confirmation-token"):
        module.execute_transaction(
            9002, mode="real",
            user_identity="vamsee", approval_source="cron",
            confirmation_token=None, is_tty=False,
            runner=_runner_factory(tracked),
        )


def test_approve_provider_plan_writes_comment_body_file_before_mutation(tmp_path, monkeypatch):
    _patch_workspace(monkeypatch, tmp_path)
    _setup_plan_and_reviews(tmp_path, 9003)
    tracked = {"issue": _issue_payload(9003)}

    result = module.execute_transaction(
        9003, mode="real",
        user_identity="vamsee", approval_source="cli",
        confirmation_token="test-token", is_tty=False,
        runner=_runner_factory(tracked),
    )

    # The body-file existed at the time gh issue comment was called
    assert tracked["comment_body_seen_at_call_time"], (
        "gh issue comment must be called with an existing body-file"
    )
    assert "Idempotency key:" in tracked["comment_body_seen_at_call_time"]
    assert result["comment_body_path"] is not None


def test_approve_provider_plan_serializes_concurrent_approvals_per_issue(tmp_path, monkeypatch):
    _patch_workspace(monkeypatch, tmp_path)
    _setup_plan_and_reviews(tmp_path, 9004)
    # Acquire the lock manually to simulate an in-flight concurrent transaction
    tx_dir = tmp_path / ".planning" / "approval-transactions"
    fd = module.acquire_issue_lock(9004, tx_dir=tx_dir)
    try:
        tracked = {"issue": _issue_payload(9004)}
        with pytest.raises(module.ApprovalError, match="holds the lock|active for"):
            module.execute_transaction(
                9004, mode="real",
                user_identity="vamsee", approval_source="cli",
                confirmation_token="test-token", is_tty=False,
                runner=_runner_factory(tracked),
            )
    finally:
        import fcntl
        fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
        fd.close()


def test_approve_provider_plan_resume_race_is_serialized(tmp_path, monkeypatch):
    tx_dir, _ = _patch_workspace(monkeypatch, tmp_path)
    _setup_plan_and_reviews(tmp_path, 9005)
    # Pre-create a stuck in-flight journal record
    tx_dir.mkdir(parents=True, exist_ok=True)
    state = module.TxState(
        issue_number=9005, txid="abc123def4567890",
        started_at=module.utc_now(), user_identity="vamsee", approval_source="cli",
        plan_path=f"docs/plans/2026-05-12-issue-9005-sample.md",
        plan_sha256="0" * 64, review_artifacts=[],
        idempotency_key="x" * 32, phase="comment_posted",
    )
    module.write_journal(state, tx_dir=tx_dir)

    tracked = {"issue": _issue_payload(9005)}
    # Without --resume the second invocation must refuse.
    with pytest.raises(module.ApprovalError, match="another transaction is active"):
        module.execute_transaction(
            9005, mode="real",
            user_identity="vamsee", approval_source="cli",
            confirmation_token="t", is_tty=False,
            runner=_runner_factory(tracked),
        )
    # --resume with wrong txid must also refuse.
    with pytest.raises(module.ApprovalError, match="resume txid mismatch"):
        module.execute_transaction(
            9005, mode="real",
            user_identity="vamsee", approval_source="cli",
            confirmation_token="t", is_tty=False,
            resume_txid="WRONGTXIDxxxxxx",
            runner=_runner_factory(tracked),
        )


def test_approve_provider_plan_promotes_marker_only_after_verification(tmp_path, monkeypatch):
    tx_dir, approved = _patch_workspace(monkeypatch, tmp_path)
    _setup_plan_and_reviews(tmp_path, 9006)
    tracked = {"issue": _issue_payload(9006)}

    result = module.execute_transaction(
        9006, mode="real",
        user_identity="vamsee", approval_source="cli",
        confirmation_token="t", is_tty=False,
        runner=_runner_factory(tracked),
    )

    final = approved / "9006.md"
    assert final.exists(), "final marker must exist in .planning/plan-approved/ after verification"
    # Pending marker should NOT exist anymore (atomic promotion)
    pending = tx_dir / f"9006-{result['txid']}.marker.pending.md"
    assert not pending.exists(), "pending quarantine marker must be moved, not copied"
    assert result["phase"] == "complete"
    assert "Idempotency key:" in final.read_text(encoding="utf-8")


def test_approve_provider_plan_rejects_stale_closed_or_unlabeled_issue(tmp_path, monkeypatch):
    _patch_workspace(monkeypatch, tmp_path)
    _setup_plan_and_reviews(tmp_path, 9007)
    # Closed issue
    tracked_closed = {"issue": _issue_payload(9007, state="CLOSED")}
    with pytest.raises(module.ApprovalError, match="not OPEN"):
        module.execute_transaction(
            9007, mode="dry-run",
            user_identity="vamsee", approval_source="cli",
            confirmation_token=None, is_tty=True,
            runner=_runner_factory(tracked_closed),
        )
    # Unlabeled issue
    tracked_unlabeled = {"issue": _issue_payload(9007, labels=["priority:medium"])}
    with pytest.raises(module.ApprovalError, match="status:plan-review"):
        module.execute_transaction(
            9007, mode="dry-run",
            user_identity="vamsee", approval_source="cli",
            confirmation_token=None, is_tty=True,
            runner=_runner_factory(tracked_unlabeled),
        )


def test_approve_provider_plan_partial_failure_keeps_marker_quarantined(tmp_path, monkeypatch):
    tx_dir, approved = _patch_workspace(monkeypatch, tmp_path)
    _setup_plan_and_reviews(tmp_path, 9008)
    tracked = {"issue": _issue_payload(9008), "fail_at_label": True}

    base_runner = _runner_factory(tracked)

    def runner(cmd, **kwargs):
        if cmd[:3] == ["gh", "issue", "edit"] and tracked.get("fail_at_label"):
            raise RuntimeError("simulated gh edit failure")
        return base_runner(cmd, **kwargs)

    with pytest.raises(RuntimeError, match="simulated"):
        module.execute_transaction(
            9008, mode="real",
            user_identity="vamsee", approval_source="cli",
            confirmation_token="t", is_tty=False,
            runner=runner,
        )

    # No final marker
    assert not (approved / "9008.md").exists()
    # Journal records phase up to comment_posted (last write before failure)
    journals = list(tx_dir.glob("9008-*.json"))
    assert journals, "journal record must persist after partial failure"
    final_phase = json.loads(journals[0].read_text(encoding="utf-8")).get("phase")
    assert final_phase in {"comment_posted", "labels_transitioned"}, (
        f"phase after partial failure should record last successful step; got {final_phase}"
    )
    # Quarantine marker survives for recovery
    pending = list(tx_dir.glob("9008-*.marker.pending.md"))
    assert pending, "quarantine marker must remain for --resume recovery"


def test_approve_provider_plan_resume_completes_pending_actions_without_duplicates(tmp_path, monkeypatch):
    tx_dir, approved = _patch_workspace(monkeypatch, tmp_path)
    _setup_plan_and_reviews(tmp_path, 9009)

    # First attempt: fail at label step.
    tracked = {"issue": _issue_payload(9009), "fail_at_label": True}
    base_runner = _runner_factory(tracked)

    def fail_runner(cmd, **kwargs):
        if cmd[:3] == ["gh", "issue", "edit"] and tracked.get("fail_at_label"):
            raise RuntimeError("simulated first-attempt failure")
        return base_runner(cmd, **kwargs)

    with pytest.raises(RuntimeError):
        module.execute_transaction(
            9009, mode="real",
            user_identity="vamsee", approval_source="cli",
            confirmation_token="t", is_tty=False,
            runner=fail_runner,
        )

    # Comment was posted in the failed first attempt.
    assert tracked["comment_posted"] is True
    first_comment_count = sum(
        1 for c in tracked["calls"] if c[:3] == ["gh", "issue", "comment"]
    )
    assert first_comment_count == 1

    # Resume run: same txid, runner stops failing.
    journals = list(tx_dir.glob("9009-*.json"))
    txid = json.loads(journals[0].read_text(encoding="utf-8"))["txid"]
    tracked["fail_at_label"] = False

    result = module.execute_transaction(
        9009, mode="real",
        user_identity="vamsee", approval_source="cli",
        confirmation_token="t", is_tty=False,
        resume_txid=txid,
        runner=fail_runner,
    )

    assert result["phase"] == "complete"
    assert (approved / "9009.md").exists()
    # No duplicate comment was posted on resume.
    total_comment_count = sum(
        1 for c in tracked["calls"] if c[:3] == ["gh", "issue", "comment"]
    )
    assert total_comment_count == 1, (
        f"resume must not duplicate the comment; got {total_comment_count} comment calls"
    )
