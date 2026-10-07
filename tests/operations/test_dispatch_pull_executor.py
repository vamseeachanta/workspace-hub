"""The pull loop's REAL executor: a queue card -> a `drain.py` invocation.

## The gap this closes

`dispatch_pull.claim_run` has always been able to run something. What it ran was
`_dry_run_executor`, which prints. So every drain the fleet has ever performed
needed an operator to hand-write `--command`, and "continuous unattended
dispatch" stopped one step short of continuous.

## The part that must not be papered over

A card is an ISSUE. Most issues' work is not a shell one-liner, and nothing on
the card says what to run — `.claude/dispatch/<machine>.yaml` carries `gh`,
`repo`, `url`, `domain`, `provider`, `dispatch_status`, `wip_eligible`,
`routed_by` and deliberately no title. There is no field a payload could be read
from, and inventing one per domain would fire the same command at 1344 issues
that have nothing in common but a label.

So the binding is EXPLICIT and per-issue, and an unbound card is REFUSED.

The headline assertion is the negative one: a card with no bound payload must
not reach `mark_done`, must not spawn a drain, and must carry a status that a
reader can tell apart from a completed run. A no-op that reports success is the
exact false completion the record protocol (#3740) exists to prevent — it would
be manufactured here, one layer above, and look identical on the way out.

Every assertion below is on a PROPERTY — which statuses were produced, whether
the drain subprocess was reached, whether `mark_done` fired, which flags are in
the argv — never on the wording of a message.

Hermetic: FakeGit (no git), a fake `run` (no subprocess, no drain, no gh), an
injected clock and token. Nothing here touches the network or the real queue.

Run: uv run --with pyyaml --with pytest pytest tests/operations/test_dispatch_pull_executor.py
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[2]


def _load(mod, rel):
    spec = importlib.util.spec_from_file_location(mod, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


dp = _load("dispatch_pull", "scripts/operations/dispatch_pull.py")

TTL = 30
ISSUE = "vamseeachanta/deckhand#33"
OTHER = "vamseeachanta/deckhand#37"


class FakeGit:
    """Dict-backed git model — same shape as test_dispatch_pull.FakeGit."""

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


class FakeRun:
    """Stands in for `subprocess.run`. Records every argv; returns a chosen code.

    Recording the argv is what lets the tests assert the drain was NOT reached,
    which is the whole point of the unbound-card case — an executor that
    swallowed the card quietly and one that refused it would produce the same
    empty side effects if we only watched `mark_done`.
    """

    def __init__(self, returncode: int = 0):
        self.returncode = returncode
        self.calls: list[list[str]] = []
        self.kwargs: list[dict] = []

    def __call__(self, argv, **kw):
        self.calls.append(list(argv))
        self.kwargs.append(kw)
        return subprocess.CompletedProcess(argv, self.returncode)


def _tokens():
    n = {"i": 0}

    def fn():
        n["i"] += 1
        return f"tok{n['i']}"
    return fn


def _card(gh=ISSUE, *, wip=True, status="ready", domain="capability",
          provider="claude"):
    return {
        "gh": gh,
        "repo": gh.rpartition("#")[0],
        "domain": domain,
        "provider": provider,
        "url": f"https://github.com/{gh.replace('#', '/issues/')}",
        "dispatch_status": status,
        "wip_eligible": wip,
        "routed_by": "manual",
    }


def _item(card):
    return {"id": card["gh"], "card": card}


def _write_bindings(tmp_path: Path, mapping: dict) -> Path:
    path = tmp_path / "commands.yaml"
    path.write_text(yaml.safe_dump({"version": 1, "commands": mapping},
                                   sort_keys=False))
    return path


# ── the headline: an unbound card is never a successful run ──────────────────


def test_unbound_card_is_not_recorded_as_a_successful_run(tmp_path):
    """A card with no declared payload: no drain, no mark_done, not `ran`."""
    run = FakeRun(0)
    done: list[str] = []
    executor = dp.make_drain_executor(
        repo=tmp_path, records_dir=tmp_path / "records", machine="dev-primary",
        bindings={}, apply=False, run=run)

    out = dp.claim_run([_item(_card())], holder="m1", git=FakeGit(),
                       executor=executor, ttl_s=TTL, now_fn=lambda: 100.0,
                       token_fn=_tokens(), mark_done=lambda it: done.append(it["id"]))

    assert done == []                       # never completed
    assert run.calls == []                  # drain.py was never reached
    assert out[0]["status"] != "ran"        # and never reported as a run


def test_unbound_card_status_is_distinguishable_from_a_completed_one(tmp_path):
    """`no_command` is its own status — not a silent skip, not a success."""
    bindings = dp.load_command_bindings(_write_bindings(tmp_path, {ISSUE: "echo bound"}))
    runnable, deferred = dp.partition_runnable(
        [_item(_card(ISSUE)), _item(_card(OTHER))], bindings)

    assert [i["id"] for i in runnable] == [ISSUE]
    assert [(d["id"], d["status"]) for d in deferred] == [(OTHER, dp.NO_COMMAND)]
    assert dp.NO_COMMAND not in {"ran", "failed", "skipped_held", "lost_fence"}


def test_deferred_card_never_takes_a_lease(tmp_path):
    """Refused BEFORE the claim: an unrunnable card must not churn lease refs."""
    git = FakeGit()
    bindings = dp.load_command_bindings(_write_bindings(tmp_path, {}))
    runnable, deferred = dp.partition_runnable([_item(_card())], bindings)
    dp.claim_run(runnable, holder="m1", git=git, executor=lambda it: None,
                 ttl_s=TTL, now_fn=lambda: 100.0, token_fn=_tokens())

    assert deferred and git.store == {}


def test_blank_command_is_undefined_not_an_empty_payload(tmp_path):
    """`command: ""` would exit 0 having run nothing — a manufactured success."""
    for blank in ("", "   ", "\n"):
        bindings = dp.load_command_bindings(_write_bindings(tmp_path, {ISSUE: blank}))
        runnable, deferred = dp.partition_runnable([_item(_card())], bindings)
        assert runnable == []
        assert [d["status"] for d in deferred] == [dp.NO_COMMAND]


def test_executor_refuses_an_unbound_card_even_without_the_pre_filter(tmp_path):
    """Defence in depth: the guard does not live only in `partition_runnable`.

    A caller that wires the executor straight into `claim_run` (the shape the
    module already supports) must not be able to reach a drain for a card whose
    payload nobody declared.
    """
    run = FakeRun(0)
    executor = dp.make_drain_executor(
        repo=tmp_path, records_dir=tmp_path / "records", machine="dev-primary",
        bindings={}, apply=False, run=run)

    with pytest.raises(dp.UndefinedPayload):
        executor(_item(_card()))
    assert run.calls == []


# ── the WIP cap ─────────────────────────────────────────────────────────────


def test_wip_ineligible_card_is_not_claimed(tmp_path):
    """The router capped it. The puller must not run it anyway."""
    git = FakeGit()
    bindings = dp.load_command_bindings(_write_bindings(tmp_path, {OTHER: "echo x"}))
    runnable, deferred = dp.partition_runnable([_item(_card(OTHER, wip=False))], bindings)
    dp.claim_run(runnable, holder="m1", git=git, executor=lambda it: None,
                 ttl_s=TTL, now_fn=lambda: 100.0, token_fn=_tokens())

    assert runnable == []
    assert [d["status"] for d in deferred] == [dp.WIP_CAPPED]
    assert git.store == {}


def test_missing_wip_flag_is_treated_as_capped(tmp_path):
    """An absent flag is not permission. Fail closed, like queue staleness does."""
    card = _card()
    card.pop("wip_eligible")
    bindings = dp.load_command_bindings(_write_bindings(tmp_path, {ISSUE: "echo x"}))
    runnable, deferred = dp.partition_runnable([_item(card)], bindings)

    assert runnable == []
    assert [d["status"] for d in deferred] == [dp.WIP_CAPPED]


# ── the drain invocation ────────────────────────────────────────────────────


def test_bound_card_invokes_drain_with_the_issue_and_its_command(tmp_path):
    run = FakeRun(0)
    records = tmp_path / "records"
    executor = dp.make_drain_executor(
        repo=tmp_path, records_dir=records, machine="dev-primary",
        bindings={ISSUE: "bash scripts/x.sh"}, apply=False, run=run)

    out = dp.claim_run([_item(_card())], holder="m1", git=FakeGit(),
                       executor=executor, ttl_s=TTL, now_fn=lambda: 100.0,
                       token_fn=_tokens())

    assert [o["status"] for o in out] == ["ran"]
    assert len(run.calls) == 1
    argv = run.calls[0]
    assert argv[1].endswith("drain.py")
    for flag, value in (("--issue", ISSUE), ("--command", "bash scripts/x.sh"),
                        ("--records", str(records)), ("--repo-root", str(tmp_path)),
                        ("--machine", "dev-primary")):
        assert argv[argv.index(flag) + 1] == value


def test_dry_run_is_the_default_and_omits_the_apply_flag(tmp_path):
    run = FakeRun(0)
    executor = dp.make_drain_executor(
        repo=tmp_path, records_dir=tmp_path, machine="dev-primary",
        bindings={ISSUE: "echo x"}, run=run)          # `apply` not passed at all
    executor(_item(_card()))

    assert "--apply" not in run.calls[0]


def test_apply_passes_the_flag_through_to_drain(tmp_path):
    run = FakeRun(0)
    executor = dp.make_drain_executor(
        repo=tmp_path, records_dir=tmp_path, machine="dev-primary",
        bindings={ISSUE: "echo x"}, apply=True, run=run)
    executor(_item(_card()))

    assert "--apply" in run.calls[0]


def test_executor_does_not_arm_the_env_gate_itself(tmp_path):
    """Two gates, not one. `--apply` must not smuggle in `DISPATCH_APPLY_ENABLED`.

    If the executor set the env var for the child, the operator's second gate
    would be satisfied by the first one — drain would be armed by a flag alone.
    """
    run = FakeRun(0)
    executor = dp.make_drain_executor(
        repo=tmp_path, records_dir=tmp_path, machine="dev-primary",
        bindings={ISSUE: "echo x"}, apply=True, run=run)
    executor(_item(_card()))

    env = run.kwargs[0].get("env")
    assert env is None or dp.APPLY_FLAG not in env


@pytest.mark.parametrize("code", [1, 2, 66])
def test_nonzero_drain_exit_is_not_recorded_as_done(tmp_path, code):
    """`blocked`/`unknown`/a refused claim all leave drain nonzero.

    drain's own exit code is three-valued: 0 dry-run-or-success, 1 the loop
    closed but the work did not succeed (this is where `blocked` lands), 2 the
    loop did not close. Only 0 may become `ran`.
    """
    run = FakeRun(code)
    done: list[str] = []
    executor = dp.make_drain_executor(
        repo=tmp_path, records_dir=tmp_path, machine="dev-primary",
        bindings={ISSUE: "echo x"}, apply=True, run=run)

    out = dp.claim_run([_item(_card())], holder="m1", git=FakeGit(),
                       executor=executor, ttl_s=TTL, now_fn=lambda: 100.0,
                       token_fn=_tokens(), mark_done=lambda it: done.append(it["id"]))

    assert out[0]["status"] == "failed"
    assert done == []
    assert str(code) in out[0]["error"]     # the child's status is surfaced, not swallowed


# ── the bindings file ───────────────────────────────────────────────────────


def test_absent_bindings_file_binds_nothing(tmp_path):
    """Missing map is not an error — but it grants nothing either."""
    bindings = dp.load_command_bindings(tmp_path / "nope.yaml")
    runnable, deferred = dp.partition_runnable([_item(_card())], bindings)

    assert bindings == {}
    assert runnable == [] and [d["status"] for d in deferred] == [dp.NO_COMMAND]


def test_malformed_binding_key_is_rejected_loudly(tmp_path):
    """A typo'd key would otherwise bind nothing, silently, forever."""
    with pytest.raises(ValueError):
        dp.load_command_bindings(_write_bindings(tmp_path, {"deckhand#33": "echo x"}))


def test_non_string_command_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        dp.load_command_bindings(_write_bindings(tmp_path, {ISSUE: ["echo", "x"]}))


def test_bindings_survive_a_queue_regeneration(tmp_path):
    """The binding lives OUTSIDE the generated queue file, on purpose.

    `dispatch.py` rewrites `.claude/dispatch/<machine>.yaml` wholesale from
    `route.py` proposals; a `command:` field added to a card would be discarded
    by the next `dispatch.py --write`. This pins the property that made the side
    map the choice: resolution reads the map, not the card.
    """
    bindings = dp.load_command_bindings(_write_bindings(tmp_path, {ISSUE: "echo bound"}))
    regenerated = _card()                    # exactly what dispatch.py emits
    assert dp.resolve_command(_item(regenerated), bindings) == "echo bound"


# ── the two gates, at the CLI ───────────────────────────────────────────────


def test_main_refuses_apply_without_the_env_gate(tmp_path, monkeypatch, capsys):
    """`--apply` alone claims nothing: refused before any git or lease call."""
    monkeypatch.delenv(dp.APPLY_FLAG, raising=False)
    calls: list = []
    monkeypatch.setattr(dp, "_fetch_lease_refs", lambda *a, **k: calls.append("fetch"))
    monkeypatch.setattr(dp, "_read_ready_cards", lambda *a, **k: calls.append("read") or [])

    rc = dp.main(["--apply", "--repo", str(tmp_path), "--machine", "dev-primary"])

    assert rc != 0
    assert calls == []
