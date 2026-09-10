#!/usr/bin/env python3
"""The PAUSE sentinel must stop the loop, not fail every card (#3773 R2+R6).

This defect was created by fixing two things in parallel. `drain.py` gained a
`.claude/dispatch/PAUSE` sentinel and exit code 3 to mean "the fleet is paused,
I refused to claim anything". `dispatch_pull.py`'s executor, written at the same
time, raises `DrainFailed` on ANY nonzero exit.

Composed, a paused fleet does not stop. It walks the whole queue recording a
failure per card — so the kill switch produces the loudest possible false alarm
and stops nothing. On `dev-primary` that is 1344 fabricated failures.

The distinction the tests below pin is a general one: an exit code that means
"the system said no" is not an exit code that means "this unit of work broke".
Collapsing them loses the only signal that says stop.

Run: uv run --with pyyaml --with pytest pytest tests/operations/test_dispatch_pull_pause.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PULL_PY = REPO_ROOT / "scripts" / "operations" / "dispatch_pull.py"

# drain.py's PAUSED exit. Imported rather than restated where possible; the
# literal here is the point of `test_the_paused_code_matches_drains_own`.
DRAIN_PAUSED_EXIT = 3


def _load():
    spec = importlib.util.spec_from_file_location("dispatch_pull", PULL_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_pull"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def dp():
    return _load()


class _FakeGit:
    """Dict-backed ref store — the shape `dispatch_lease` actually drives.

    `claim_run` calls the lease module's functions with this object, not methods
    on it, so the surface that matters is `read_ref` / `create_ref`, matching
    the FakeGit in `test_dispatch_pull_executor.py`. Every lease is granted;
    leases are not what these tests are about.
    """

    def __init__(self):
        self.store: dict[str, tuple[str, dict]] = {}
        self._counter = 0

    def _next_sha(self) -> str:
        self._counter += 1
        return f"sha{self._counter:04d}"

    def read_ref(self, name):
        if name not in self.store:
            return None
        sha, blob = self.store[name]
        return sha, dict(blob)

    def create_ref(self, name, blob):
        if name in self.store:
            return None
        sha = self._next_sha()
        self.store[name] = (sha, dict(blob))
        return sha

    def update_ref(self, name, blob, expect_sha):
        cur = self.store.get(name)
        if cur is None or cur[0] != expect_sha:
            return None
        sha = self._next_sha()
        self.store[name] = (sha, dict(blob))
        return sha


def _cards(n):
    return [{"id": f"owner/repo#{i}", "card": {"gh": f"owner/repo#{i}"}} for i in range(1, n + 1)]


def _run(dp, executor, items, mark_done=None):
    """Drive claim_run with leases and fencing stubbed out.

    `verify_token` is a module-level alias (`dispatch_pull.verify_token`), not a
    parameter, so it is patched on the freshly-loaded module rather than passed
    in. Each test loads its own copy, so this cannot leak between tests.

    `max_cards` is left at its default of None (unbounded) on purpose: the CLI
    default is 5, and a capped run would truncate the ten-card case and make the
    stop-the-loop assertion pass for the wrong reason.
    """
    dp.verify_token = lambda *a, **k: True
    return dp.claim_run(
        items,
        holder="ace-linux-1",
        git=_FakeGit(),
        executor=executor,
        ttl_s=900,
        now_fn=lambda: 1000.0,
        token_fn=lambda: "tok",
        mark_done=mark_done,
        sleep_fn=lambda s: None,
    )


def test_the_paused_code_matches_drains_own(dp):
    """A pause the loop does not recognise is not a pause.

    Asserts the constant, not a message: if drain renumbers its exit codes this
    fails here rather than silently degrading to `failed` in production.
    """
    assert dp.FLEET_PAUSED_EXIT == DRAIN_PAUSED_EXIT


def test_a_paused_drain_stops_the_loop_instead_of_walking_the_queue(dp):
    """THE test. Ten cards, drain reports paused on the first.

    Fails on the pre-fix code with ten `failed` outcomes — the shape that would
    have put 1344 fabricated failures in a run log.
    """
    calls = []

    def executor(item):
        calls.append(item["id"])
        raise dp.FleetPaused(item["id"])

    outcomes = _run(dp, executor, _cards(10))

    assert len(calls) == 1, (
        f"the loop ran {len(calls)} cards after a pause; it must stop at the first"
    )
    statuses = [o["status"] for o in outcomes]
    assert "failed" not in statuses, (
        f"a paused fleet was recorded as card failures: {statuses}"
    )


def test_a_paused_card_is_not_recorded_as_a_failure(dp):
    """`paused` and `failed` must be separable by a reader, not just by wording."""
    outcomes = _run(dp, lambda item: (_ for _ in ()).throw(dp.FleetPaused(item["id"])), _cards(3))
    first = outcomes[0]
    assert first["status"] == "paused"
    assert first["status"] != "failed"


def test_a_paused_card_is_never_marked_done(dp):
    """A refusal to start is not a completion. The card must stay claimable."""
    marked = []
    _run(
        dp,
        lambda item: (_ for _ in ()).throw(dp.FleetPaused(item["id"])),
        _cards(3),
        mark_done=lambda item: marked.append(item["id"]),
    )
    assert marked == []


def test_a_real_card_failure_still_fails_and_still_continues(dp):
    """The discriminator.

    Without this, "treat every exception as a pause" would pass every test
    above while destroying the retry path. A genuine failure must NOT stop the
    loop, and must NOT be reported as paused.
    """
    calls = []

    def executor(item):
        calls.append(item["id"])
        raise dp.DrainFailed(item["id"], 1)

    outcomes = _run(dp, executor, _cards(4))

    assert len(calls) == 4, "a single card failure must not halt the run"
    assert [o["status"] for o in outcomes] == ["failed"] * 4


def test_the_executor_raises_paused_on_drains_paused_exit(dp):
    """End of the wire: exit 3 from the child becomes FleetPaused, not DrainFailed.

    Asserts on the exception TYPE reaching the caller, not on a returncode
    comparison inside the executor, so moving the check cannot silently break it.
    """
    class _Done:
        returncode = DRAIN_PAUSED_EXIT

    ex = dp.make_drain_executor(
        repo=REPO_ROOT,
        records_dir=REPO_ROOT / ".claude" / "dispatch" / "records",
        machine="dev-primary",
        bindings={"owner/repo#1": "true"},
        apply=False,
        run=lambda argv, **kw: _Done(),
    )

    with pytest.raises(dp.FleetPaused):
        ex({"id": "owner/repo#1", "card": {"gh": "owner/repo#1"}})


def test_other_nonzero_exits_are_still_drain_failures(dp):
    """Only 3 is a pause. 1 and 2 remain per-card failures."""
    class _Done:
        def __init__(self, rc):
            self.returncode = rc

    for rc in (1, 2, 66):
        ex = dp.make_drain_executor(
            repo=REPO_ROOT,
            records_dir=REPO_ROOT / ".claude" / "dispatch" / "records",
            machine="dev-primary",
            bindings={"owner/repo#1": "true"},
            apply=False,
            run=lambda argv, _rc=rc, **kw: _Done(_rc),
        )
        with pytest.raises(dp.DrainFailed):
            ex({"id": "owner/repo#1", "card": {"gh": "owner/repo#1"}})
