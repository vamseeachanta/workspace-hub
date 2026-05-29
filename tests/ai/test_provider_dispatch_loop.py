"""Tests for scripts/ai/provider-dispatch-loop.py (#2665)."""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "provider-dispatch-loop.py"
spec = importlib.util.spec_from_file_location("provider_dispatch_loop", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["provider_dispatch_loop"] = module
spec.loader.exec_module(module)


# ────────────────────────────────────────────────────────────────────────────
# Fixtures / helpers
# ────────────────────────────────────────────────────────────────────────────


def _cfg(tmp_path: Path, *, leader_host: str = "ace-linux-1", promotion_token: str | None = None):
    return module.DispatcherConfig(
        leader_host=leader_host,
        leader_lock_path=tmp_path / "leader.lock",
        lease_ledger_path=tmp_path / "leases.jsonl",
        run_ledger_path=tmp_path / "runs.jsonl",
        coexistence_marker_dir=tmp_path,
        promotion_token=promotion_token,
    )


def _kanban_card(number: int, *, lane: str = "execution_ready",
                 provider: str = "codex", machine: str = "ace-linux-1",
                 machine_ready: bool = True, approval_marker: bool = True,
                 labels: list[str] | None = None) -> dict:
    return {
        "number": number,
        "title": f"sample #{number}",
        "url": f"https://example.test/issues/{number}",
        "lane": lane,
        "provider_route": provider,
        "machine_route": machine,
        "machine_role": "leader" if machine == "ace-linux-1" else "worker",
        "machine_ready": machine_ready,
        "machine_blocker": None if machine_ready else "unreachable",
        "approval_ready": True,
        "approval_blockers": [],
        "review_clean": True,
        "approval_marker": f".planning/plan-approved/{number}.md" if approval_marker else None,
        "plan": f"docs/plans/2026-05-12-issue-{number}-sample.md",
        "warnings": [],
        "hover": {
            "title": f"sample #{number}",
            "labels": labels or ["status:plan-approved"],
            "plan_summary": "summary",
            "risks": "",
            "tests": "",
            "provider_route": provider,
            "machine_route": machine,
            "machine_readiness": "ready" if machine_ready else "blocked",
        },
    }


def _kanban_with(cards: list[dict]) -> dict:
    lanes: dict[str, list] = {
        "plan_review": [], "execution_ready": [], "running_leased": [],
        "qa_closeout": [], "planning_feedstock": [], "blocked": [],
    }
    for c in cards:
        lanes.setdefault(c["lane"], []).append(c)
    return {"generated_at": "2026-05-12T12:00:00Z", "lanes": lanes, "cards": cards}


def _set_machine(monkeypatch, machine: str):
    monkeypatch.setenv("DISPATCHER_MACHINE", machine)


# ────────────────────────────────────────────────────────────────────────────
# Plan-named tests
# ────────────────────────────────────────────────────────────────────────────


def test_dispatch_loop_never_launches_implementation_without_approval_marker(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")
    # Card has plan-approved label BUT no marker
    card = _kanban_card(8001, approval_marker=False)
    kanban = _kanban_with([card])

    summary = module.run_loop(cfg, kanban, {}, dry_run=False)

    assert summary["execution_ready"] == [], "issue without marker must not be leased"
    # And nothing fell through to planning because the card stays in execution_ready lane
    assert summary["planning_fallback"] == []


def test_dispatch_loop_refuses_lease_write_without_leader_lock(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-2")  # NOT the leader
    card = _kanban_card(8002)
    kanban = _kanban_with([card])

    # Direct: acquire_leader_lock must refuse on non-leader
    with pytest.raises(module.DispatchError, match="not the leader"):
        module.acquire_leader_lock(cfg)
    # And run_loop refuses to originate dispatch.
    with pytest.raises(module.DispatchError, match="non-leader|not the leader"):
        module.run_loop(cfg, kanban, {})


def test_dispatch_loop_aborts_when_competing_dispatcher_detected(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")
    # Plant a competing-dispatcher marker pointing at a DIFFERENT lock path
    marker = cfg.coexistence_marker_dir / module.COEXISTENCE_MARKER_NAME
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps({"leader_lock_path": str(tmp_path / "other-leader.lock")}),
        encoding="utf-8",
    )
    kanban = _kanban_with([_kanban_card(8003)])
    with pytest.raises(module.DispatchError, match="independent lease writers forbidden"):
        module.run_loop(cfg, kanban, {})


def test_non_leader_node_cannot_originate_dispatch(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-2")
    kanban = _kanban_with([_kanban_card(8004)])
    with pytest.raises(module.DispatchError):
        module.run_loop(cfg, kanban, {})


def test_dispatch_loop_single_writer_promotion_disables_previous_leader(tmp_path, monkeypatch):
    """Promotion is opt-in (--promotion-token); without it, ace-linux-2 cannot
    write leases. With it, ace-linux-2 can — provided the previous leader has
    released its lock (i.e., not running). The lock acquisition itself enforces
    "one writer at a time": if the leader lock is held, even a promoted machine
    fails. Promotion is therefore the EXPLICIT handoff step.
    """
    # Phase 1: ace-linux-2 without promotion → refused
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-2")
    with pytest.raises(module.DispatchError, match="not the leader"):
        module.acquire_leader_lock(cfg)

    # Phase 2: ace-linux-2 with promotion token → allowed
    cfg_promoted = _cfg(tmp_path, promotion_token="OPS-TOKEN-XYZ")
    lock = module.acquire_leader_lock(cfg_promoted)
    try:
        # Verify lock file recorded the promoted machine
        text = cfg_promoted.leader_lock_path.read_text(encoding="utf-8")
        assert "ace-linux-2" in text
    finally:
        import fcntl
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()

    # Phase 3: while promoted machine holds lock, a fresh leader attempt fails
    # (single-writer property holds across the promotion handoff).
    cfg_third = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")  # back to leader identity
    lock2 = module.acquire_leader_lock(cfg_third)  # lock is released; should succeed
    try:
        pass
    finally:
        import fcntl
        fcntl.flock(lock2.fileno(), fcntl.LOCK_UN)
        lock2.close()


def test_dispatch_loop_blocks_unready_machine_routes(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")
    card = _kanban_card(8005, machine_ready=False)
    kanban = _kanban_with([card])

    summary = module.run_loop(cfg, kanban, {})

    assert summary["execution_ready"] == []
    assert any(s["number"] == 8005 for s in summary["skipped_due_to_machine"])


def test_dispatch_loop_falls_back_to_planning_recon_review_when_no_execution_ready_work(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")
    # Plan-review card (planning fallback)
    pr_card = _kanban_card(8006, lane="plan_review",
                           labels=["status:plan-review"], approval_marker=False)
    pf_card = _kanban_card(8007, lane="planning_feedstock",
                           labels=[], approval_marker=False)
    kanban = _kanban_with([pr_card, pf_card])

    summary = module.run_loop(cfg, kanban, {}, dry_run=True)

    assert summary["execution_ready"] == []
    assert len(summary["planning_fallback"]) >= 1
    leased_numbers = {l["issue_number"] for l in summary["planning_fallback"]}
    assert {8006, 8007} & leased_numbers, "planning fallback should pull from plan_review or planning_feedstock"


def test_dispatch_loop_uses_lease_idempotency_to_prevent_double_dispatch(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")
    card = _kanban_card(8008)
    kanban = _kanban_with([card])

    # First tick: lease created.
    summary1 = module.run_loop(cfg, kanban, {})
    assert len(summary1["execution_ready"]) == 1

    # Second tick on the same Kanban → no new lease, same issue+provider+machine
    # is already active in the ledger.
    summary2 = module.run_loop(cfg, kanban, {})
    assert summary2["execution_ready"] == [], "duplicate lease for same issue/provider/machine must be skipped"


def test_dispatch_loop_applies_wednesday_friday_reset_usage_policy(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")
    utilization = {
        "providers": {
            "codex": {"usage_pct": 0.10},  # very under-used
            "gemini": {"usage_pct": 0.50},  # mid
        }
    }
    # Wednesday at 13:00 UTC (after noon)
    wed_noon = datetime(2026, 5, 13, 13, 0, tzinfo=timezone.utc)
    policy_wed = module.apply_utilization_policy(utilization, now=wed_noon)
    assert policy_wed["codex"] == "feed_planning", "Wed pm + under 25% → feed_planning"
    assert policy_wed["gemini"] == "feed_anything", "Wed pm + 50% → feed_anything (above 25% threshold)"

    # Friday at 13:00 UTC (after noon)
    fri_noon = datetime(2026, 5, 15, 13, 0, tzinfo=timezone.utc)
    policy_fri = module.apply_utilization_policy(utilization, now=fri_noon)
    assert policy_fri["codex"] == "feed_planning"
    assert policy_fri["gemini"] == "feed_planning", "Fri pm + under 60% → feed_planning"

    # Reset window (Sunday)
    sun = datetime(2026, 5, 17, 1, 0, tzinfo=timezone.utc)
    policy_sun = module.apply_utilization_policy(utilization, now=sun)
    assert policy_sun["codex"] == "reset_window"


def test_morning_qa_packet_summarizes_completed_running_blocked_and_user_actions(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")
    # Seed lease ledger with one completed, one running (with TTL not yet expired), one stale
    now = datetime(2026, 5, 13, 10, 0, tzinfo=timezone.utc)
    completed = module.Lease(
        lease_id="L-A", issue_number=1, provider="codex", machine="ace-linux-1",
        mode="implementation", parent_issue="#2519",
        idempotency_key="1:codex:ace-linux-1", state="completed",
        created_at="2026-05-12T08:00:00Z", ttl_seconds=3600,
        expected_artifact="docs/plans/issue-1.md",
        expires_at="2026-05-12T09:00:00Z",
        completed_at="2026-05-13T05:00:00Z",
    )
    running = module.Lease(
        lease_id="L-B", issue_number=2, provider="claude", machine="ace-linux-1",
        mode="implementation", parent_issue="#2519",
        idempotency_key="2:claude:ace-linux-1", state="active",
        created_at="2026-05-13T09:30:00Z", ttl_seconds=7200,
        expires_at="2026-05-13T11:30:00Z",
    )
    stale = module.Lease(
        lease_id="L-C", issue_number=3, provider="gemini", machine="ace-linux-1",
        mode="planning", parent_issue="#2519",
        idempotency_key="3:gemini:ace-linux-1", state="active",
        created_at="2026-05-12T01:00:00Z", ttl_seconds=3600,
        expires_at="2026-05-12T02:00:00Z",
    )
    cfg.lease_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cfg.lease_ledger_path, "w", encoding="utf-8") as fh:
        for l in (completed, running, stale):
            fh.write(json.dumps(module.dataclasses.asdict(l)) + "\n")

    text = module.generate_morning_qa(cfg, now=now)
    assert "## Completed" in text
    assert "L-A" in text
    assert "## Running" in text
    assert "L-B" in text
    assert "## Stale" in text
    assert "L-C" in text
    assert "Recommended user actions" in text


def test_dispatch_loop_creates_lease_with_idempotency_key_and_parent_issue(tmp_path, monkeypatch):
    """Sanity: lease records include all required fields for cross-referencing #2519."""
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")
    card = _kanban_card(8100)
    kanban = _kanban_with([card])

    summary = module.run_loop(cfg, kanban, {})
    lease = summary["execution_ready"][0]
    assert lease["idempotency_key"] == "8100:codex:ace-linux-1"
    assert lease["parent_issue"] == "#2519"
    assert lease["expires_at"]
    assert lease["expected_artifact"]


# ────────────────────────────────────────────────────────────────────────────
# #2847 Phase 1b — self-fence wired into the lease path
# ────────────────────────────────────────────────────────────────────────────

# Load the sibling dispatch_leader module to build a fake store + reuse its types.
_DL_PATH = REPO_ROOT / "scripts" / "ai" / "dispatch_leader.py"
_dl_spec = importlib.util.spec_from_file_location("dispatch_leader", _DL_PATH)
_dl = importlib.util.module_from_spec(_dl_spec)
sys.modules["dispatch_leader"] = _dl
_dl_spec.loader.exec_module(_dl)


class _FenceStore:
    """Minimal injectable LeaderStateStore for the fence tests."""
    def __init__(self, leader, term, claim_result):
        self._leader, self._term, self._claim = leader, term, claim_result
        self.claims = []

    def read(self):
        if self._leader is None:
            raise _dl.StoreUnavailable("uninitialized")
        return _dl.LeaderState(leader=self._leader, term=self._term,
                               heartbeat_utc=datetime(2026, 5, 28, tzinfo=timezone.utc).isoformat(),
                               heartbeat_pid=1)

    def claim(self, state):
        self.claims.append(state)
        return self._claim


def test_loop_default_off_originates_without_a_store(tmp_path, monkeypatch):
    # enforce_leader_fence defaults False -> behavior unchanged, no store needed.
    cfg = _cfg(tmp_path)
    _set_machine(monkeypatch, "ace-linux-1")
    summary = module.run_loop(cfg, _kanban_with([_kanban_card(8200)]), {})
    assert summary.get("self_fenced") is False
    assert len(summary["execution_ready"]) == 1


def test_loop_originates_when_confirmed_git_leader(tmp_path, monkeypatch):
    _set_machine(monkeypatch, "ace-linux-1")
    cfg = _cfg(tmp_path)
    cfg.enforce_leader_fence = True
    cfg.leader_state_store = _FenceStore("ace-linux-1", 7, _dl.ClaimResult.PUSHED)
    summary = module.run_loop(cfg, _kanban_with([_kanban_card(8201)]), {})
    assert summary["self_fenced"] is False
    assert len(summary["execution_ready"]) == 1


def test_loop_self_fences_when_push_not_confirmed(tmp_path, monkeypatch):
    # Leader is correct but the heartbeat push cannot be confirmed -> stand down.
    _set_machine(monkeypatch, "ace-linux-1")
    cfg = _cfg(tmp_path)
    cfg.enforce_leader_fence = True
    cfg.leader_state_store = _FenceStore("ace-linux-1", 7, _dl.ClaimResult.PUSH_FAILED)
    summary = module.run_loop(cfg, _kanban_with([_kanban_card(8202)]), {})
    assert summary["self_fenced"] is True
    assert summary["execution_ready"] == []  # originated NOTHING
    assert not cfg.lease_ledger_path.exists() or cfg.lease_ledger_path.read_text() == ""


def test_loop_self_fences_when_not_the_committed_leader(tmp_path, monkeypatch):
    # This machine is ace-linux-2 but committed leader is ace-linux-1 (and it
    # passes the config leader check via promotion_token) -> git-fence still blocks.
    _set_machine(monkeypatch, "ace-linux-2")
    cfg = _cfg(tmp_path, promotion_token="tok")  # passes is_leader_machine
    cfg.enforce_leader_fence = True
    cfg.leader_state_store = _FenceStore("ace-linux-1", 7, _dl.ClaimResult.PUSHED)
    summary = module.run_loop(cfg, _kanban_with([_kanban_card(8203)]), {})
    assert summary["self_fenced"] is True
    assert summary["execution_ready"] == []


def test_loop_dry_run_is_not_fenced(tmp_path, monkeypatch):
    # dry-run writes no leases -> it must still produce a plan preview even when the
    # fence is on and this machine could not originate (review #1).
    _set_machine(monkeypatch, "ace-linux-1")
    cfg = _cfg(tmp_path)
    cfg.enforce_leader_fence = True
    cfg.leader_state_store = _FenceStore("ace-linux-1", 7, _dl.ClaimResult.PUSH_FAILED)  # would block origination
    summary = module.run_loop(cfg, _kanban_with([_kanban_card(8204)]), {}, dry_run=True)
    assert summary["self_fenced"] is False
    assert len(summary["execution_ready"]) == 1  # planned (dry-run), not originated
    assert summary["execution_ready"][0].get("planned") is True


def test_loop_self_fences_with_reason_when_store_unavailable(tmp_path, monkeypatch):
    # Enabling the fence before the ref is bootstrapped halts origination, but the
    # reason must be surfaced (not silent) (review #2).
    _set_machine(monkeypatch, "ace-linux-1")
    cfg = _cfg(tmp_path)
    cfg.enforce_leader_fence = True
    cfg.leader_state_store = _FenceStore(None, 0, _dl.ClaimResult.PUSHED)  # read() raises StoreUnavailable
    summary = module.run_loop(cfg, _kanban_with([_kanban_card(8205)]), {})
    assert summary["self_fenced"] is True
    assert summary["execution_ready"] == []
    assert any("unavailable" in m.lower() for m in summary.get("self_fenced_detail", []))


def test_leader_fence_enabled_from_env(monkeypatch):
    monkeypatch.delenv("DISPATCH_ENFORCE_LEADER_FENCE", raising=False)
    assert module.leader_fence_enabled_from_env() is False
    for v in ("1", "true", "TRUE", "yes", " Yes "):
        monkeypatch.setenv("DISPATCH_ENFORCE_LEADER_FENCE", v)
        assert module.leader_fence_enabled_from_env() is True
    for v in ("0", "false", "no", "", "off", "enabled-please"):
        monkeypatch.setenv("DISPATCH_ENFORCE_LEADER_FENCE", v)
        assert module.leader_fence_enabled_from_env() is False
