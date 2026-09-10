"""Pacing and morning evidence for the pull loop (rail R6 of #3773).

## The two defects

**No cap, no backoff.** Nothing bounded how many cards one run attempted. Each
drain writes two commits to `main` plus a push, so the worst case over the
`dev-primary` queue was roughly 1344 cards x 2 commits, unattended, into a repo
with CI and a PII gate. The run needs a ceiling and a gap between cards, and
both need to be settable without editing the file.

**Failure and silence look identical.** A night that refused all 1344 cards and
a night that completed them produced the same artifact: the stdout of a process
nobody was attached to. The morning question — "did anything happen?" — had no
answer that survived the terminal.

## What is asserted

Properties, not messages: how many times the executor was reached, how many
sleeps separated those calls, which statuses the log carries, and which strings
it must never contain. The cap tests are paired with an uncapped control so a
cap that "passes" by running nothing cannot hide.

The prose guard is the one worth reading twice. Titles were removed from the
dispatch surface because they leaked client identifiers into a public repo
(#3768); a log that dumped the card would put them straight back. The log is
built from a fixed key set, and the test feeds it a card carrying a title to
prove the key set — not a filter, not a regex — is what keeps prose out.

Hermetic: FakeGit, injected clock/token/sleep, tmp_path logs. No subprocess.

Run: uv run --with pyyaml --with pytest pytest tests/operations/test_dispatch_pull_pacing.py
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]


def _load(mod, rel):
    spec = importlib.util.spec_from_file_location(mod, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


dp = _load("dispatch_pull", "scripts/operations/dispatch_pull.py")

TTL = 900
REPO = "vamseeachanta/deckhand"


class FakeGit:
    """Dict-backed git model — same shape as test_dispatch_pull_executor.FakeGit."""

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

    def cas_update_ref(self, name, expected_sha, blob):
        cur = self.store.get(name)
        if cur is None or cur[0] != expected_sha:
            return None
        sha = self._next_sha()
        self.store[name] = (sha, dict(blob))
        return sha


def _tokens():
    n = {"i": 0}

    def fn():
        n["i"] += 1
        return f"tok{n['i']}"
    return fn


def _items(count: int) -> list[dict]:
    return [{"id": f"{REPO}#{n}", "card": {"gh": f"{REPO}#{n}", "wip_eligible": True}}
            for n in range(1, count + 1)]


class Spy:
    """Counts executor calls; optionally raises for chosen ids."""

    def __init__(self, fail_ids=()):
        self.calls: list[str] = []
        self.fail_ids = set(fail_ids)

    def __call__(self, item):
        self.calls.append(item["id"])
        if item["id"] in self.fail_ids:
            raise dp.DrainFailed(item["id"], 2)
        return 0


class Clock:
    """A sleep that records instead of sleeping, and a clock it advances."""

    def __init__(self):
        self.slept: list[float] = []
        self.t = 1000.0

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.t += seconds

    def now(self):
        return self.t


def _run(items, *, executor, git=None, clock=None, **kw):
    return dp.claim_run(items, holder="host-a", git=git or FakeGit(),
                        executor=executor, ttl_s=TTL,
                        now_fn=(clock or Clock()).now, token_fn=_tokens(), **kw)


# ── (a) the cap ─────────────────────────────────────────────────────────────


def test_the_run_stops_after_the_cap(tmp_path):
    """Five cards, a cap of two: the executor is reached twice."""
    spy = Spy()
    _run(_items(5), executor=spy, max_cards=2)

    assert len(spy.calls) == 2


def test_without_a_cap_the_same_queue_runs_to_the_end(tmp_path):
    """Control: the cap test above is not passing because nothing ran."""
    spy = Spy()
    _run(_items(5), executor=spy, max_cards=None)

    assert len(spy.calls) == 5


def test_cards_past_the_cap_are_reported_not_dropped(tmp_path):
    """A queue that shrinks silently is the failure this rail exists to close."""
    out = _run(_items(5), executor=Spy(), max_cards=2)

    assert len(out) == 5
    assert [o["status"] for o in out] == ["ran", "ran"] + [dp.RUN_CAPPED] * 3
    assert dp.RUN_CAPPED not in {"ran", "failed", "skipped_held", "lost_fence",
                                 dp.NO_COMMAND, dp.WIP_CAPPED}


def test_a_capped_card_never_takes_a_lease(tmp_path):
    """Past the ceiling, the loop must stop touching refs, not just stop running."""
    git = FakeGit()
    _run(_items(5), executor=Spy(), git=git, max_cards=2)

    assert len(git.store) == 2


def test_a_failed_card_still_consumes_the_cap(tmp_path):
    """The ceiling bounds ATTEMPTS. A failing drain has already written to main."""
    spy = Spy(fail_ids={f"{REPO}#1", f"{REPO}#2"})
    out = _run(_items(5), executor=spy, max_cards=2)

    assert len(spy.calls) == 2
    assert [o["status"] for o in out[:2]] == ["failed", "failed"]


def test_a_card_held_elsewhere_does_not_consume_the_cap(tmp_path):
    """A skipped claim writes nothing to `main`, so it must not eat the budget."""
    git = FakeGit()
    items = _items(3)
    # host-b already holds the first card's lease, fresh.
    held = dp.default_lease_name(items[0])
    git.create_ref(dp.lease_ref(held), {"holder": "host-b", "generation": 1,
                                        "token": "t", "ttl_s": TTL,
                                        "renewed_at": 1000.0})
    spy = Spy()
    out = _run(items, executor=spy, git=git, max_cards=2)

    assert [o["status"] for o in out] == ["skipped_held", "ran", "ran"]
    assert len(spy.calls) == 2


# ── (a) the delay ───────────────────────────────────────────────────────────


def test_a_delay_separates_consecutive_cards(tmp_path):
    """Three runs, two gaps — the pause is between cards, not around them."""
    clock = Clock()
    _run(_items(3), executor=Spy(), clock=clock, delay_s=30.0, sleep_fn=clock.sleep)

    assert clock.slept == [30.0, 30.0]


def test_nothing_sleeps_before_the_first_card(tmp_path):
    clock = Clock()
    _run(_items(1), executor=Spy(), clock=clock, delay_s=30.0, sleep_fn=clock.sleep)

    assert clock.slept == []


def test_a_zero_delay_does_not_sleep(tmp_path):
    clock = Clock()
    _run(_items(3), executor=Spy(), clock=clock, delay_s=0.0, sleep_fn=clock.sleep)

    assert clock.slept == []


def test_capped_cards_are_not_paced(tmp_path):
    """Waiting out a delay for cards the run has already declined is dead time."""
    clock = Clock()
    _run(_items(6), executor=Spy(), clock=clock, max_cards=2,
         delay_s=30.0, sleep_fn=clock.sleep)

    assert clock.slept == [30.0]


# ── (a) both, at the CLI ────────────────────────────────────────────────────


def test_the_cli_default_cap_is_finite_and_conservative():
    """A default of `None`/0/unbounded would leave the overnight risk in place."""
    default = _arg_default("--max-cards")

    assert isinstance(default, int)
    assert 0 < default <= 50


def test_the_cli_default_delay_is_a_real_pause():
    default = _arg_default("--delay")

    assert isinstance(default, (int, float)) and default > 0


def test_no_cli_value_can_disable_the_cap(tmp_path):
    """`--max-cards` is a ceiling, not a switch. Unbounded must be unreachable.

    Parsed, not run — and `--repo` is pinned at `tmp_path` regardless, because a
    regression in the guard would otherwise let this test fall through into a
    real pull against the real queue. (It did, once, while mutation-testing the
    guard: 1344 live cards read and a 316 KB log written into the repo.)
    """
    for bad in ("-1", "-100"):
        with pytest.raises(SystemExit):
            dp.build_parser().parse_args(
                ["--max-cards", bad, "--repo", str(tmp_path)])


def _arg_default(flag: str):
    parser = dp.build_parser()
    for action in parser._actions:
        if flag in action.option_strings:
            return action.default
    raise AssertionError(f"{flag} is not a CLI option")


# ── (b) the run log ─────────────────────────────────────────────────────────


def _read(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]


def _log(tmp_path, **kw) -> "dp.RunLog":
    return dp.RunLog(tmp_path / "2026-08-01.jsonl", run_id="r1",
                     machine="dev-primary", now_fn=lambda: 1000.0, **kw)


def test_every_card_gets_its_own_line(tmp_path):
    log = _log(tmp_path)
    out = _run(_items(3), executor=Spy(), on_outcome=log.card)

    records = _read(log.path)
    assert len(records) == 3
    assert [r["issue"] for r in records] == [o["id"] for o in out]
    assert {r["status"] for r in records} == {"ran"}


def test_a_line_names_the_run_the_machine_and_the_attempt(tmp_path):
    log = _log(tmp_path)
    _run(_items(1), executor=Spy(), on_outcome=log.card)

    record = _read(log.path)[0]
    for field in ("ts", "run_id", "machine", "issue", "status", "attempt"):
        assert field in record
    assert record["run_id"] == "r1" and record["machine"] == "dev-primary"


def test_deferred_cards_are_logged_too(tmp_path):
    """`no_command` and `wip_capped` never reach `claim_run` — and still count."""
    log = _log(tmp_path)
    items = [{"id": f"{REPO}#1", "card": {"gh": f"{REPO}#1", "wip_eligible": False}},
             {"id": f"{REPO}#2", "card": {"gh": f"{REPO}#2", "wip_eligible": True}}]
    _runnable, deferred = dp.partition_runnable(items, {})
    for outcome in deferred:
        log.card(outcome)

    assert {r["status"] for r in _read(log.path)} == {dp.WIP_CAPPED, dp.NO_COMMAND}


def test_a_failure_carries_its_cause(tmp_path):
    log = _log(tmp_path)
    _run(_items(1), executor=Spy(fail_ids={f"{REPO}#1"}), on_outcome=log.card)

    record = _read(log.path)[0]
    assert record["status"] == "failed" and "2" in record["error"]


def test_the_summary_counts_every_outcome_by_cause(tmp_path):
    """The one line that answers "what happened last night" without a terminal."""
    log = _log(tmp_path)
    items = _items(6)
    out = _run(items, executor=Spy(fail_ids={f"{REPO}#2"}), max_cards=3,
               on_outcome=log.card)
    deferred = [{"id": f"{REPO}#9", "status": dp.NO_COMMAND, "reason": "unbound"}]
    summary = log.summary(deferred + out)

    assert summary["counts"] == {"ran": 2, "failed": 1, dp.RUN_CAPPED: 3,
                                 dp.NO_COMMAND: 1}
    assert summary["total"] == 7
    assert _read(log.path)[-1]["event"] == "run_summary"


def test_a_run_that_refused_everything_reads_differently_from_one_that_worked(tmp_path):
    """The defect: both nights produced identical evidence. They must not."""
    all_refused = _log(tmp_path / "a").summary(
        [{"id": f"{REPO}#{n}", "status": dp.NO_COMMAND} for n in range(1, 5)])
    all_ran = _log(tmp_path / "b").summary(
        [{"id": f"{REPO}#{n}", "status": "ran"} for n in range(1, 5)])

    assert all_refused["counts"] != all_ran["counts"]


def test_the_log_never_writes_issue_prose(tmp_path):
    """#3768: titles left this surface because they leaked client identifiers.

    The card is fed a title here precisely because a real one has none — the
    assertion is about what the writer is ALLOWED to copy, not about what today's
    cards happen to hold.
    """
    secret = "Confidential Client Alpha riser fatigue rework"
    log = _log(tmp_path)
    log.card({"id": f"{REPO}#1", "status": "ran", "title": secret,
              "card": {"gh": f"{REPO}#1", "title": secret, "body": secret}})

    text = log.path.read_text()
    assert secret not in text
    assert "title" not in text and "body" not in text
    assert f"{REPO}#1" in text          # the issue ref itself is fine


def test_the_summary_never_writes_issue_prose(tmp_path):
    secret = "Confidential Client Alpha riser fatigue rework"
    log = _log(tmp_path)
    log.summary([{"id": f"{REPO}#1", "status": "ran", "title": secret}])

    assert secret not in log.path.read_text()


def test_the_log_appends_rather_than_truncating(tmp_path):
    """Two runs in one night must both survive."""
    path = tmp_path / "2026-08-01.jsonl"
    for run_id in ("r1", "r2"):
        log = dp.RunLog(path, run_id=run_id, machine="dev-primary",
                        now_fn=lambda: 1000.0)
        log.card({"id": f"{REPO}#1", "status": "ran"})

    assert [r["run_id"] for r in _read(path)] == ["r1", "r2"]


def test_the_log_is_dated_and_lands_under_the_repo(tmp_path):
    path = dp.run_log_path(tmp_path, today="2026-08-01")

    assert path.parent == tmp_path / dp.RUN_LOG_DIR_REL
    assert path.name == "2026-08-01.jsonl"


def test_the_log_directory_is_gitignored():
    """A public repo with a PII gate must not be handed a nightly card log."""
    probe = str(dp.RUN_LOG_DIR_REL / "2026-08-01.jsonl")
    done = subprocess.run(["git", "-C", str(_ROOT), "check-ignore", "-q", probe],
                          capture_output=True, text=True, timeout=60)

    assert done.returncode == 0, f"{probe} is not gitignored"
