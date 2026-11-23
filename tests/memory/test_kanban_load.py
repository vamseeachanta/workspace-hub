#!/usr/bin/env python3
"""TDD tests for .claude/memory/kanban/scripts/load.py — issue #2827 safe-park fix.

The loader must park imported cards as *sticky-blocked-WITH-a-reason* so the
Hermes gateway does not auto-unblock them to `ready` (and so `triage` — the
pipeline *entry* — is never used). Verified against hermes v0.14.0 source:
`block_task` only transitions `running`/`ready` -> `blocked` and only THEN emits
the sticky `"blocked"` event the gateway keys auto-unblock-suppression on. A card
CREATED already-`blocked` matches 0 rows, emits no sticky event, and gets
auto-unblocked. So the loader must create in a block-ELIGIBLE status (`running`)
THEN block. These tests assert:

  * create uses --initial-status running (NOT blocked, NOT --triage, NOT ready)
  * after create, a `block <id> "<reason>"` follow-up runs with a real reason
  * the idempotency key is preserved on create
  * a create failure short-circuits (no orphan block call)
  * idempotent re-run: when create's JSON reports status already `blocked`, the
    loader SKIPS the block call (no comment-bloat, no false failure)
  * when create's JSON reports status `running`/`ready`, the block call fires

Strategy: import load.py via importlib, stub its `run()` so no real hermes
process is spawned, capture the command list, and assert on it. These tests are
HERMETIC — they never touch the live ~/.hermes/kanban.db.

Run: uv run --with "pyyaml" pytest tests/memory/test_kanban_load.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LOAD_PY = REPO_ROOT / ".claude" / "memory" / "kanban" / "scripts" / "load.py"


def _import_loader():
    spec = importlib.util.spec_from_file_location("kanban_load", LOAD_PY)
    assert spec and spec.loader, f"cannot load spec for {LOAD_PY}"
    mod = importlib.util.module_from_spec(spec)
    # Register before exec for any dataclass/forward-ref resolution.
    sys.modules["kanban_load"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def loader():
    return _import_loader()


def _patch_run(loader, returns):
    """Replace loader.run with a recorder.

    `returns` is a list of (rc, stdout, stderr) tuples, consumed in order.
    Returns the list that accumulates each invoked cmd.
    """
    calls: list[list[str]] = []
    seq = iter(returns)

    def fake_run(cmd, dry):
        calls.append(list(cmd))
        try:
            return next(seq)
        except StopIteration:
            return 0, "", ""

    loader.run = fake_run
    return calls


SAMPLE_CARD = {
    "idempotency_key": "gh:vamseeachanta/digitalmodel#2289",
    "title": "Sample imported card",
    "priority": 3,
}


def test_create_uses_running_status_not_blocked_not_triage(loader):
    # create returns a `running` card -> loader must then block it.
    calls = _patch_run(loader, [(0, '{"id": "t42", "status": "running"}', ""),
                                (0, "", "")])
    ok = loader.create_card("repo-digitalmodel", dict(SAMPLE_CARD), None, dry=False)
    assert ok is True
    create_cmd = calls[0]
    joined = " ".join(create_cmd)
    assert "--initial-status" in create_cmd
    # MUST create block-ELIGIBLE so the follow-up block emits the sticky event.
    assert create_cmd[create_cmd.index("--initial-status") + 1] == "running", (
        "create must use --initial-status running (a card created already "
        "'blocked' gets auto-unblocked — block_task matches 0 rows, no sticky "
        "event fires)"
    )
    assert "blocked" not in create_cmd, (
        "must NOT create with --initial-status blocked (the original bug)"
    )
    assert "--triage" not in create_cmd, "triage is the pipeline ENTRY — unsafe park"
    assert "--idempotency-key" in create_cmd
    assert (
        create_cmd[create_cmd.index("--idempotency-key") + 1]
        == SAMPLE_CARD["idempotency_key"]
    )
    assert joined.endswith(SAMPLE_CARD["title"])


def test_block_followup_sets_a_reason(loader):
    # create returns a running card; loader must then call `block <id> <reason>`.
    calls = _patch_run(loader, [(0, '{"id": "t42", "status": "running"}', ""),
                                (0, "", "")])
    ok = loader.create_card("repo-digitalmodel", dict(SAMPLE_CARD), None, dry=False)
    assert ok is True
    assert len(calls) >= 2, f"expected a block follow-up call, got: {calls}"
    block_cmd = calls[1]
    assert "block" in block_cmd, f"second call must be a block: {block_cmd}"
    assert "t42" in block_cmd, f"block must target created id t42: {block_cmd}"
    # A non-empty reason argument must follow the id (positional reason).
    idx = block_cmd.index("t42")
    reason_tokens = block_cmd[idx + 1 :]
    assert reason_tokens, f"block call carried no reason: {block_cmd}"
    assert any(t.strip() for t in reason_tokens), f"reason is blank: {block_cmd}"
    # It must be scoped to the right board.
    assert "--board" in block_cmd
    assert block_cmd[block_cmd.index("--board") + 1] == "repo-digitalmodel"


def test_block_fires_when_status_ready(loader):
    # `ready` is also block-eligible (block_task: WHERE status IN running/ready).
    calls = _patch_run(loader, [(0, '{"id": "t99", "status": "ready"}', ""),
                                (0, "", "")])
    ok = loader.create_card("repo-x", dict(SAMPLE_CARD), None, dry=False)
    assert ok is True
    assert len(calls) == 2, f"ready card must be blocked: {calls}"
    assert "block" in calls[1]


def test_rerun_idempotent_skips_block_when_already_blocked(loader):
    # Re-run: idempotency-key returns the EXISTING card, already sticky-blocked.
    # The loader must NOT call block again (would re-comment + report a false
    # failure since block_task returns False on a blocked card).
    calls = _patch_run(loader, [(0, '{"id": "t42", "status": "blocked"}', "")])
    ok = loader.create_card("repo-digitalmodel", dict(SAMPLE_CARD), None, dry=False)
    assert ok is True, "already-blocked card is a clean idempotent no-op"
    assert len(calls) == 1, (
        f"must NOT re-block an already-blocked (sticky) card: {calls}"
    )
    assert not any("block" in c for c in calls[1:]), (
        f"no block call expected on re-run of a blocked card: {calls}"
    )


def test_create_failure_short_circuits_no_block(loader):
    calls = _patch_run(loader, [(1, "", "boom")])
    ok = loader.create_card("repo-digitalmodel", dict(SAMPLE_CARD), None, dry=False)
    assert ok is False
    assert len(calls) == 1, f"must not issue block after a failed create: {calls}"


def test_no_task_id_from_create_fails_loud(loader):
    # create succeeds but emits no parseable id -> cannot guarantee the park;
    # fail loud rather than leave a card the gateway will auto-unblock.
    calls = _patch_run(loader, [(0, "not json", "")])
    ok = loader.create_card("repo-digitalmodel", dict(SAMPLE_CARD), None, dry=False)
    assert ok is False
    assert len(calls) == 1, f"must not block when id is unknown: {calls}"


def test_detected_gap_card_skipped(loader):
    calls = _patch_run(loader, [(0, '{"id": "x"}', "")])
    card = {"idempotency_key": "gap:repo-x:1", "title": "gap", "source": "detected_gap"}
    ok = loader.create_card("repo-x", card, None, dry=False)
    assert ok is True
    assert calls == [], "detected_gap cards are YAML-only; no hermes calls"


def test_dry_run_emits_no_real_calls(loader):
    # In dry mode the real run() prints and returns 0 without spawning hermes;
    # we don't stub it so we exercise the actual dry path.
    ok = loader.create_card("repo-x", dict(SAMPLE_CARD), None, dry=True)
    assert ok is True
