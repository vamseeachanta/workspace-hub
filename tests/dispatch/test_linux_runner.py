#!/usr/bin/env python3
"""Linux dispatch runner — the completion record as a side effect. #3740 slice 4.

867 issues sit at `dispatch:ready` because the queue is drained by per-machine
sessions and nothing reports back. `scripts/dispatch/run.sh` is the Linux half of
the fix: a wrapper you cannot run work through without the exit code, the
timings, and the owning issue being written down. Windows already has this as
`scripts/windows/dispatch-run.ps1` (wh#3729), and the two MUST stay
interchangeable to a caller — same verbs, one JSON object per invocation.

## What these tests cover

Argument handling, the JSON shape of every verb, exit-code round-tripping,
state-dir layout, and that an unknown verb fails loudly instead of defaulting to
something that looks like it worked. Everything that runs a payload runs it via
`submit --foreground` with a command that finishes immediately — that path writes
the *identical* record as the detached path, so the round-trip is exercised for
real without racing a background process.

## What these tests deliberately do NOT cover, and why

- **Durability across session close.** The claim is that `setsid` detaches the
  runner into a new session so an SSH/tmux teardown's SIGHUP has nothing to
  reach. Proving it needs a real login session to tear down. A test that spawned
  a sleeper and killed a process group would be testing the harness's own
  process tree, not the thing that fails on a fleet host. Verified manually on
  the host instead.
- **Heartbeat cadence over minutes.** That the beat keeps arriving for hours
  requires wall-clock sleeps and is inherently flaky.

  This entry previously claimed the structural property was covered by "the beat
  is written by the wrapper for a payload that never writes anything itself". It
  was not. The runner beats unconditionally *before* starting the child and again
  *after* `wait`, so that assertion held with the entire sibling beater deleted —
  mutation confirmed all 67 tests green with `( while … beat … ) &` replaced by
  `: &`. A named check that does not discriminate is worse than an admitted gap,
  because the gap at least gets revisited.
  `test_the_heartbeat_is_refreshed_WHILE_the_payload_runs` now covers it: one
  advance observed during a live run, which is the property the reaper depends
  on. Only the multi-hour cadence stays untested.
- **Concurrent submits racing on one job id.** The create-only check is tested
  sequentially; a genuine race needs two processes and would be timing-flaky.
  Cross-machine mutual exclusion is slice 2's protocol, not this script's.
- **The FlexNet/SSH constraint itself.** Unverifiable without an Orcina licence
  server. Only the presence of its warning in the header is asserted — that note
  is load-bearing documentation and deleting it is how the constraint gets
  rediscovered the expensive way.

Hermetic: tmp_path state dirs, immediate commands, no network, no gh, no git.

Run: uv run --with pytest pytest tests/dispatch/test_linux_runner.py
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_SH = REPO_ROOT / "scripts" / "dispatch" / "run.sh"
WINDOWS_PS1 = REPO_ROOT / "scripts" / "windows" / "dispatch-run.ps1"

VERBS = ("submit", "status", "logs", "list", "cancel", "cleanup")

EX_USAGE = 64
EX_NOJOB = 2


def run(state_dir: Path, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Invoke run.sh with an isolated state root.

    `timeout` is not decoration: an argument parser that fails to consume a flag
    can spin forever, and a hang is a worse bug report than an error message.
    """
    return subprocess.run(
        ["bash", str(RUN_SH), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env={
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": str(state_dir),
            "WH_DISPATCH_STATE_DIR": str(state_dir),
            "WH_DISPATCH_HEARTBEAT_SECONDS": "1",
        },
    )


def one_object(proc: subprocess.CompletedProcess) -> dict:
    """Parse stdout as exactly ONE JSON object.

    The contract is one object per invocation, not one per line and not a JSON
    document with a banner in front of it. A caller over SSH pipes stdout
    straight into a parser; a second object or a stray print breaks it.
    """
    out = proc.stdout.strip()
    assert out, f"no stdout (stderr={proc.stderr!r})"
    assert "\n" not in out, f"expected a single JSON object, got:\n{out}"
    obj = json.loads(out)
    assert isinstance(obj, dict)
    return obj


def submit(state_dir: Path, command: str, *extra: str, job_id: str = "j1",
           issue: str = "vamseeachanta/digitalmodel#1885") -> dict:
    """Submit and run to completion in the foreground.

    Foreground is the same runner writing the same record — it just removes the
    race, so an assertion about the recorded exit code is deterministic.
    """
    proc = run(state_dir, "submit", "--command", command, "--issue-ref", issue,
               "--job-id", job_id, "--foreground", *extra)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return one_object(proc)


# ---------------------------------------------------------------------------
# an unknown verb must fail loudly
# ---------------------------------------------------------------------------


def test_an_unknown_verb_fails_rather_than_defaulting(tmp_path):
    """A typo that silently ran `list` would report a clean-looking result.

    That is the exact shape of quiet false success this slice exists to remove:
    an absent signal reading as a green one.
    """
    proc = run(tmp_path, "frobnicate")
    obj = one_object(proc)
    assert proc.returncode == EX_USAGE
    assert obj["ok"] is False
    assert "unknown verb" in obj["error"]


def test_an_unknown_verb_does_not_touch_the_state_dir(tmp_path):
    """Failing loudly also means failing inertly — no half-made job dirs."""
    state = tmp_path / "state"
    run(state, "frobnicate")
    assert not state.exists()


def test_no_verb_at_all_fails(tmp_path):
    proc = run(tmp_path)
    assert proc.returncode == EX_USAGE
    assert one_object(proc)["ok"] is False


@pytest.mark.parametrize("verb", VERBS)
def test_each_verb_rejects_an_unknown_option(tmp_path, verb):
    proc = run(tmp_path, verb, "--wat")
    assert proc.returncode == EX_USAGE
    obj = one_object(proc)
    assert obj["ok"] is False and obj["action"] == verb


@pytest.mark.parametrize("args", [
    ("submit", "--command"),
    ("submit", "--command", "true", "--issue-ref"),
    ("status", "--job-id"),
    ("logs", "--job-id", "j1", "--tail"),
])
def test_a_flag_missing_its_value_fails_instead_of_hanging(tmp_path, args):
    """`shift 2` on a one-element list fails silently and leaves the list intact.

    The parse loop then runs forever. The 10s timeout here is the actual
    assertion; the JSON check is the pleasant part.
    """
    proc = run(tmp_path, *args, timeout=10)
    assert proc.returncode == EX_USAGE
    assert "requires a value" in one_object(proc)["error"]


# ---------------------------------------------------------------------------
# submit argument validation
# ---------------------------------------------------------------------------


def test_submit_requires_a_command(tmp_path):
    proc = run(tmp_path, "submit", "--issue-ref", "o/r#1")
    assert proc.returncode == EX_USAGE
    assert "--command" in one_object(proc)["error"]


def test_submit_requires_an_issue_ref(tmp_path):
    """A run with no issue ref is precisely the 867-issue failure.

    Work happens, nothing joins it back to the queue item, and the record has
    nowhere to land. Refusing at submit is cheaper than reconciling an orphan.
    """
    proc = run(tmp_path, "submit", "--command", "true")
    assert proc.returncode == EX_USAGE
    # "required", not just "--issue-ref". Both the presence check and the format
    # validator name the flag, so the looser assertion passed with the presence
    # check removed — an empty ref merely failed the format check instead, and
    # the test claimed to cover a guard it never exercised.
    assert "required" in one_object(proc)["error"]


@pytest.mark.parametrize("ref", [
    "digitalmodel#1885",          # no owner
    "owner/repo",                 # no issue number
    "owner/repo#abc",             # not a number
    "owner repo#1",               # space
    "owner/repo#1; rm -rf /",     # shell metacharacters
])
def test_a_malformed_issue_ref_is_refused(tmp_path, ref):
    """An unvalidated ref ties the run to a typo, which is not tying it at all."""
    proc = run(tmp_path, "submit", "--command", "true", "--issue-ref", ref)
    assert proc.returncode == EX_USAGE
    assert "issue-ref" in one_object(proc)["error"]


@pytest.mark.parametrize("bad", ["../../etc", "a/b", "with space", "x" * 65, "$(id)"])
def test_a_job_id_that_could_escape_the_state_dir_is_refused(tmp_path, bad):
    """Job ids become directory names.

    `../..` would place a job's logs outside the state root, and the tmp files
    used for atomic replace would land somewhere nobody cleans up.
    """
    proc = run(tmp_path, "submit", "--command", "true", "--issue-ref", "o/r#1",
               "--job-id", bad)
    assert proc.returncode == EX_USAGE
    assert "job-id" in one_object(proc)["error"]


def test_an_unknown_shell_is_refused(tmp_path):
    proc = run(tmp_path, "submit", "--command", "true", "--issue-ref", "o/r#1",
               "--shell", "fish")
    assert proc.returncode == EX_USAGE
    assert "--shell" in one_object(proc)["error"]


def test_a_non_numeric_tail_is_refused(tmp_path):
    submit(tmp_path, "true")
    proc = run(tmp_path, "logs", "--job-id", "j1", "--tail", "lots")
    assert proc.returncode == EX_USAGE
    assert "--tail" in one_object(proc)["error"]


def test_a_duplicate_job_id_is_refused_not_reused(tmp_path):
    """Reuse would overwrite a live job's logs and exit code while it runs."""
    submit(tmp_path, "true")
    proc = run(tmp_path, "submit", "--command", "true", "--issue-ref", "o/r#1",
               "--job-id", "j1", "--foreground")
    assert proc.returncode == EX_USAGE
    assert "already exists" in one_object(proc)["error"]


# ---------------------------------------------------------------------------
# exit codes round-trip through the record, not the submitting shell
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", [0, 1, 7, 42])
def test_the_child_exit_code_round_trips_through_status(tmp_path, code):
    """Requirement 5: the caller reads the real code from a LATER invocation.

    The submitting shell is usually gone by the time the job ends, so the code
    has to survive in the record or it is lost.
    """
    submit(tmp_path, f"exit {code}")
    obj = one_object(run(tmp_path, "status", "--job-id", "j1"))
    assert obj["exit_code"] == code
    assert obj["state"] == "finished"


def test_exit_code_is_a_number_not_a_string(tmp_path):
    """A code arriving as "7" turns every numeric comparison into a silent false."""
    submit(tmp_path, "exit 7")
    assert one_object(run(tmp_path, "status", "--job-id", "j1"))["exit_code"] == 7


def test_submit_exits_zero_even_when_the_child_will_fail(tmp_path):
    """Submit reports on the SUBMISSION.

    Conflating the two would make every failed job look like a dispatch bug and
    every dispatch bug look like a failed job.
    """
    proc = run(tmp_path, "submit", "--command", "exit 3", "--issue-ref", "o/r#1",
               "--job-id", "j1", "--foreground")
    assert proc.returncode == 0
    assert one_object(proc)["ok"] is True
    assert one_object(run(tmp_path, "status", "--job-id", "j1"))["exit_code"] == 3


def test_a_finished_job_is_not_reported_as_successful_by_state_alone(tmp_path):
    """`finished` means ran to completion, NOT that it worked.

    Same distinction records.py draws with `done` + returncode. Collapsing them
    would let a failed run be counted as delivered work.
    """
    submit(tmp_path, "exit 9")
    obj = one_object(run(tmp_path, "status", "--job-id", "j1"))
    assert obj["state"] == "finished" and obj["exit_code"] != 0


def test_a_missing_work_dir_is_a_dispatch_error_not_a_payload_error(tmp_path):
    """The wrapper's own failures must not masquerade as the job's result.

    A payload that never ran and a payload that ran and failed call for opposite
    follow-ups — retry the dispatch, or investigate the work. 66 (EX_NOINPUT)
    keeps them apart.
    """
    obj = submit(tmp_path, "exit 0", "--work-dir", str(tmp_path / "nope"))
    assert obj["ok"] is True, "submission itself succeeded; the runner found the problem"
    status = one_object(run(tmp_path, "status", "--job-id", "j1"))
    assert status["exit_code"] == 66
    assert "work dir" in one_object(run(tmp_path, "logs", "--job-id", "j1"))["stderr"]


def test_a_missing_job_exits_2_not_0(tmp_path):
    """A caller polling a job that was cleaned up must not read that as success."""
    proc = run(tmp_path, "status", "--job-id", "ghost")
    assert proc.returncode == EX_NOJOB
    obj = one_object(proc)
    assert obj["ok"] is False and obj["error"] == "no such job"
    assert obj["job_id"] == "ghost", "a caller polling several jobs needs to know which one"


@pytest.mark.parametrize("verb", ["status", "logs", "cancel", "cleanup"])
def test_every_job_addressed_verb_reports_a_missing_job_the_same_way(tmp_path, verb):
    proc = run(tmp_path, verb, "--job-id", "ghost")
    assert proc.returncode == EX_NOJOB
    assert one_object(proc)["ok"] is False


# ---------------------------------------------------------------------------
# JSON shape per verb
# ---------------------------------------------------------------------------


def test_submit_emits_the_windows_key_set(tmp_path):
    obj = submit(tmp_path, "true")
    for key in ("ok", "action", "job_id", "dir", "stdout", "stderr", "shell", "task"):
        assert key in obj, f"submit lost the '{key}' key the Windows verb emits"
    assert obj["action"] == "submit"
    assert obj["issue_ref"] == "vamseeachanta/digitalmodel#1885"


def test_status_emits_the_windows_key_set(tmp_path):
    submit(tmp_path, "true")
    obj = one_object(run(tmp_path, "status", "--job-id", "j1"))
    for key in ("ok", "action", "job_id", "state", "exit_code", "task_state",
                "task_last_result", "stdout_bytes", "stderr_bytes"):
        assert key in obj, f"status lost the '{key}' key the Windows verb emits"


def test_status_reports_the_issue_ref_the_run_is_tied_to(tmp_path):
    """The tie is the point of the wrapper; it has to be readable back out."""
    submit(tmp_path, "true", issue="vamseeachanta/workspace-hub#3740")
    obj = one_object(run(tmp_path, "status", "--job-id", "j1"))
    assert obj["issue_ref"] == "vamseeachanta/workspace-hub#3740"


def test_status_byte_counts_are_numbers(tmp_path):
    submit(tmp_path, "echo hello")
    obj = one_object(run(tmp_path, "status", "--job-id", "j1"))
    assert obj["stdout_bytes"] == len("hello\n")
    assert obj["stderr_bytes"] == 0


def test_task_state_is_absent_once_the_payload_has_gone(tmp_path):
    submit(tmp_path, "true")
    assert one_object(run(tmp_path, "status", "--job-id", "j1"))["task_state"] == "absent"


def test_logs_emits_stdout_and_stderr_separately(tmp_path):
    submit(tmp_path, "echo out; echo err >&2")
    obj = one_object(run(tmp_path, "logs", "--job-id", "j1"))
    assert obj["stdout"] == "out"
    assert obj["stderr"] == "err"


def test_logs_of_a_job_that_wrote_nothing_returns_empty_strings(tmp_path):
    """Empty is a valid answer; an error here would look like a broken job."""
    submit(tmp_path, "true")
    obj = one_object(run(tmp_path, "logs", "--job-id", "j1"))
    assert obj["stdout"] == "" and obj["stderr"] == ""


def test_logs_json_survives_quotes_backslashes_and_newlines(tmp_path):
    """Output is arbitrary text and will contain JSON's own metacharacters.

    Hand-rolled escaping is where a shell JSON emitter usually breaks, and it
    breaks by emitting something that *parses* as truncated rather than failing.
    """
    submit(tmp_path, "echo 'a \"quoted\" and a \\ backslash'\necho 'second line'")
    obj = one_object(run(tmp_path, "logs", "--job-id", "j1"))
    assert obj["stdout"] == 'a "quoted" and a \\ backslash\nsecond line'


def test_logs_strips_raw_control_characters(tmp_path):
    """A 0x07 from a progress bar inside a JSON string is invalid JSON.

    Losing the whole payload over a terminal decoration is a bad trade.
    """
    submit(tmp_path, r"printf 'a\007b\n'", "--shell", "sh")
    obj = one_object(run(tmp_path, "logs", "--job-id", "j1"))
    assert obj["stdout"] == "ab"


def test_logs_tail_limits_the_lines_returned(tmp_path):
    submit(tmp_path, "for i in 1 2 3 4 5; do echo line$i; done")
    obj = one_object(run(tmp_path, "logs", "--job-id", "j1", "--tail", "2"))
    assert obj["stdout"] == "line4\nline5"


def test_list_reports_state_and_exit_code_per_job(tmp_path):
    submit(tmp_path, "exit 5", job_id="alpha")
    submit(tmp_path, "true", job_id="beta")
    obj = one_object(run(tmp_path, "list"))
    assert obj["count"] == 2
    by_id = {j["job_id"]: j for j in obj["jobs"]}
    assert by_id["alpha"]["exit_code"] == 5
    assert by_id["beta"]["exit_code"] == 0
    assert by_id["alpha"]["state"] == "finished"


def test_list_on_an_untouched_state_dir_is_an_empty_list_not_an_error(tmp_path):
    """A host with no jobs is a normal state, not a failure to report."""
    obj = one_object(run(tmp_path / "never-used", "list"))
    assert obj["ok"] is True and obj["count"] == 0 and obj["jobs"] == []


def test_cancel_of_a_finished_job_succeeds_without_rewriting_history(tmp_path):
    """Cancelling a job that just completed is a normal reaper race, not an error.

    Cancel must never overwrite the recorded outcome — the record is the only
    evidence of what actually happened.
    """
    submit(tmp_path, "exit 5")
    obj = one_object(run(tmp_path, "cancel", "--job-id", "j1"))
    assert obj["ok"] is True and obj["signalled"] is False
    assert one_object(run(tmp_path, "status", "--job-id", "j1"))["exit_code"] == 5


def test_cleanup_removes_the_job_and_a_later_status_says_so(tmp_path):
    submit(tmp_path, "true")
    obj = one_object(run(tmp_path, "cleanup", "--job-id", "j1"))
    assert obj["ok"] is True
    assert not Path(obj["removed_dir"]).exists()
    assert run(tmp_path, "status", "--job-id", "j1").returncode == EX_NOJOB


def test_help_names_every_verb(tmp_path):
    obj = one_object(run(tmp_path, "help"))
    assert set(obj["verbs"]) == set(VERBS)


# ---------------------------------------------------------------------------
# state dir layout
# ---------------------------------------------------------------------------


def test_the_job_dir_holds_the_full_record(tmp_path):
    """Each file answers a question a stuck-queue investigation actually asks.

    What was run, under which shell, what it printed, what it returned, and
    whether it was alive — all reconstructible from disk without the script.
    """
    submit(tmp_path, "echo hi")
    d = tmp_path / "j1"
    for name in ("job.kv", "command.txt", "runner.sh", "status.kv", "heartbeat",
                 "runner.pid", "child.pid", "stdout.log", "stderr.log"):
        assert (d / name).exists(), f"missing {name} in the job dir"


def test_the_job_dir_sits_directly_under_the_state_root(tmp_path):
    """No nesting scheme. A record that is hard to find is a record nobody reads."""
    obj = submit(tmp_path, "true", job_id="flat")
    assert Path(obj["dir"]).parent == tmp_path
    assert Path(obj["dir"]).name == "flat"


def test_the_command_is_stored_as_a_file_and_not_re_quoted(tmp_path):
    """The payload is executed as a file, so its quoting is parsed exactly once.

    Interpolating it into a generated wrapper would give it a second trip through
    a shell parser, where `$(...)` and quotes mean something new.
    """
    cmd = "echo '$(id) is not expanded'"
    submit(tmp_path, cmd)
    assert (tmp_path / "j1" / "command.txt").read_text().rstrip("\n") == cmd
    obj = one_object(run(tmp_path, "logs", "--job-id", "j1"))
    assert obj["stdout"] == "$(id) is not expanded"


def test_the_generated_runner_is_valid_bash(tmp_path):
    """A wrapper that will not parse turns every dispatched job into a no-op.

    It would fail after submit reported success, so nothing upstream would show
    a problem — precisely the silent-loss shape this slice removes.
    """
    submit(tmp_path, "true")
    proc = subprocess.run(["bash", "-n", str(tmp_path / "j1" / "runner.sh")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_the_runner_is_written_per_job_not_shared(tmp_path):
    """Two jobs must not share a mutable wrapper.

    A shared tool path edited while jobs are in flight is a documented hazard in
    this repo (`feedback_parallel_agents_shared_mutable_tool_path`).
    """
    submit(tmp_path, "true", job_id="a")
    submit(tmp_path, "true", job_id="b")
    assert (tmp_path / "a" / "runner.sh").read_text() == (tmp_path / "b" / "runner.sh").read_text()
    assert not (tmp_path / "runner.sh").exists()


def test_the_work_dir_defaults_to_the_job_dir(tmp_path):
    submit(tmp_path, "pwd")
    obj = one_object(run(tmp_path, "logs", "--job-id", "j1"))
    assert obj["stdout"] == str(tmp_path / "j1")


def test_an_explicit_work_dir_is_honoured(tmp_path):
    work = tmp_path / "elsewhere"
    work.mkdir()
    submit(tmp_path, "pwd", "--work-dir", str(work))
    assert one_object(run(tmp_path, "logs", "--job-id", "j1"))["stdout"] == str(work)


# ---------------------------------------------------------------------------
# heartbeat
# ---------------------------------------------------------------------------


def test_the_heartbeat_is_written_by_the_wrapper_not_the_payload(tmp_path):
    """Requirement 4, in its testable form.

    The payload here writes nothing and returns nonzero — yet the beat exists.
    A job blocked in a solver cannot beat for itself, and requiring it to would
    make every long run look dead to the reaper, which would then requeue work
    that was fine.
    """
    submit(tmp_path, "exit 3")
    beat = (tmp_path / "j1" / "heartbeat").read_text().strip()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", beat), beat


def test_status_surfaces_the_heartbeat(tmp_path):
    """A beat nobody can read is not liveness — the reaper polls through `status`."""
    submit(tmp_path, "true")
    obj = one_object(run(tmp_path, "status", "--job-id", "j1"))
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", obj["heartbeat_at"])


# ---------------------------------------------------------------------------
# cross-platform contract
# ---------------------------------------------------------------------------


def test_the_verb_set_matches_the_windows_script():
    """Both platforms must be interchangeable to a caller.

    A verb added on one side only is how a control-surface host starts branching
    on which machine it is talking to — the thing this pair exists to avoid.
    """
    ps1 = WINDOWS_PS1.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"ValidateSet\(\s*((?:'[a-z]+'\s*,\s*)+'[a-z]+')\s*\)", ps1)
    assert match, "could not find the Windows ValidateSet of verbs"
    windows_verbs = set(re.findall(r"'([a-z]+)'", match.group(1)))
    assert windows_verbs == set(VERBS)


def test_the_header_documents_the_flexnet_ssh_constraint():
    """Requirement 6: the note that stops the next well-meaning simplification.

    Orcina products cannot complete a FlexNet checkout under an SSH public-key
    logon token, and the failure lands at solve time — long after dispatch looked
    fine — which is why it keeps getting rediscovered. Losing this comment costs
    someone a day, so its absence is a test failure.
    """
    header = RUN_SH.read_text(encoding="utf-8")[:6000]
    assert "FlexNet" in header
    assert "ssh" in header.lower()
    assert "licensed-solver-dispatch.md" in header, "the rule must be cited by path"
    assert "Scheduled Task" in header, "the Windows-only escape hatch must be named"


# ---------------------------------------------------------------------------
# the two properties the suite named but did not discriminate
#
# Both found by mutation after the module was otherwise complete: deleting the
# sibling beater, and collapsing `cancelled` into `finished`, each left all 67
# tests green.
# ---------------------------------------------------------------------------


def _await_state(state_dir: Path, want, job_id="j1", limit=15.0):
    """Poll `status` until the job reaches one of `want`. Returns the object."""
    deadline = time.monotonic() + limit
    obj = {}
    while time.monotonic() < deadline:
        obj = one_object(run(state_dir, "status", "--job-id", job_id))
        if obj.get("state") in want:
            return obj
        time.sleep(0.1)
    raise AssertionError(f"job never reached {want}; last={obj}")


def test_the_heartbeat_is_refreshed_WHILE_the_payload_runs(tmp_path):
    """The beater, not merely the existence of a beat.

    `test_the_heartbeat_is_written_by_the_wrapper_not_the_payload` asserts a
    valid timestamp exists once the job has finished — but the runner beats
    unconditionally before starting the child AND again after `wait`, so that
    assertion holds with the entire sibling loop deleted. Mutation confirmed it:
    replacing the beater with `: &` left all 67 tests green.

    The distinction is the whole point of the design. A five-hour OrcaFlex batch
    beats only through the sibling; without it the record goes stale against its
    own TTL and the reaper requeues work that was running fine — the failure the
    heartbeat exists to prevent.
    """
    proc = run(tmp_path, "submit", "--command", "sleep 4", "--issue-ref",
               "o/r#1", "--job-id", "j1")
    assert proc.returncode == 0, proc.stdout + proc.stderr

    first = _await_state(tmp_path, {"running"})["heartbeat_at"]
    assert first, "no beat while running"

    # The beat interval is 1s in this suite's env; two seconds is comfortably
    # more than one interval and comfortably less than the payload's 4.
    deadline = time.monotonic() + 3.0
    later = first
    while time.monotonic() < deadline and later == first:
        time.sleep(0.2)
        obj = one_object(run(tmp_path, "status", "--job-id", "j1"))
        if obj["state"] != "running":
            break
        later = obj["heartbeat_at"]

    assert later != first, (
        f"heartbeat never advanced during the run ({first!r}) — the sibling "
        f"beater is not beating, so a long job will be reaped mid-flight")


def test_a_killed_job_is_cancelled_not_finished(tmp_path):
    """"Ran to completion with a nonzero code" and "was killed" need different follow-up.

    Only cancelling an ALREADY-FINISHED job was covered, so collapsing the
    branch to `state=finished` survived mutation. A killed run reported as
    `finished` reads downstream as a genuine failure to investigate rather than
    an interruption to re-dispatch.
    """
    proc = run(tmp_path, "submit", "--command", "sleep 30", "--issue-ref",
               "o/r#1", "--job-id", "j1")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    _await_state(tmp_path, {"running"})

    assert one_object(run(tmp_path, "cancel", "--job-id", "j1"))["ok"] is True
    obj = _await_state(tmp_path, {"cancelled", "finished"})

    assert obj["state"] == "cancelled", (
        f"a signalled job reported {obj['state']!r}; the state must name the "
        f"shape of the ending, not just that it ended")
    assert obj["exit_code"] > 128, (
        f"exit_code {obj['exit_code']} lost the signal — the state names the "
        f"shape, the code carries the detail")
