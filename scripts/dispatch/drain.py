#!/usr/bin/env python3
"""drain.py — ONE issue, ready -> active -> done, with a record behind it. #3740 slice 6.

Slices 1-4 built the parts and nothing has yet run end to end:

    records.py    the state is a durable record            (slice 1)
    claim.py      claiming it is exclusive, or refused      (slice 2)
    reconcile.py  the label is a projection of the record   (slice 3)
    run.sh        a run cannot happen without an exit code  (slice 4)

867 issues sit at `dispatch:ready` because nothing reported back. Every one of
those parts is untested in production until a single issue has genuinely reached
`done` **with a record behind it**, and slice 5's new labels are vocabulary with
nothing writing them. This module is the pilot drain: the smallest thing that
closes the loop for real, in the order the protocol requires.

    1. CLAIM     claim.acquire — create-only write, commit, push, verify FROM THE
                 REMOTE. Refused? STOP. The runner is not reached.
    2. EXECUTE   the real runner (run.sh here, dispatch-run.ps1 on Windows), so
                 the exit code, the timings and the issue ref round-trip.
    3. RELEASE   claim.release with the outcome, so the record reaches a terminal
                 state carrying `returncode` and, on failure, `failure_category`.
    4. PROJECT   reconcile derives the label from the record. Records -> labels,
                 one direction, never back.

Nothing here re-implements any of that. A second copy of the claim protocol or
of the projection rule would drift from the original and each would look correct
in isolation — the failure this epic keeps meeting.

## Fail closed at every step

A refused claim, a failed push, a remote we cannot read: none of them proceed to
execution. There is exactly **one floating solver seat fleet-wide** (wh#3721), so
a wrong ALLOW means two hosts racing one licence and two confusing failures. A
wrong DENY makes one card wait for the next drain. The asymmetry is not close.

That is why a claim held by ANOTHER host is refused here rather than adjudicated:
liveness (expiry, quarantine, clock skew) belongs to `reconcile.settle`, which
sees every record and an injected clock. A drain that decided "their heartbeat
looks old to me" would be a second, racier liveness rule.

## `done` is not `success`

`done` means **ran to completion**, not that it worked. `records.is_success`
requires `done` AND `returncode == 0`, and it is the only success test in this
module — `DrainResult.ok` answers a different question ("did the loop close?")
and is documented as such where it is defined. A payload that exits 3 produces a
`done` record with `returncode: 3` and `failure_category: "payload-error"`. A
payload whose exit code we could not learn produces `blocked` with
`failure_category: "unknown-outcome"` and `returncode: null` — never a 0 nobody
observed.

## Dry run by DEFAULT

`--apply` AND `DISPATCH_APPLY_ENABLED` — the same gate as `route.py` and
`reconcile.py`, consulted through `reconcile.writes_armed()` so three modules
cannot disagree about what "armed" means. Without both, this prints exactly what
it would do and reaches no write primitive: no record write, no git call, no
runner invocation.

Real drain (the operator's command, both gates required):

    DISPATCH_APPLY_ENABLED=1 uv run --with pyyaml python scripts/dispatch/drain.py \\
        --issue owner/repo#123 --records <records-dir> --repo-root <checkout> \\
        --command 'echo pilot' --apply

Drop `--apply` (or the env var) for the plan.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Sibling scripts, not a package — same loader shape as reconcile.py, so these
# resolve whether drain.py is run directly, imported by a test, or exec'd from
# another cwd.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import claim  # noqa: E402
import reconcile  # noqa: E402
import records  # noqa: E402

RUN_SH = _HERE / "run.sh"
#: `_HERE` is scripts/dispatch, so the sibling directory is `_HERE.parent /
#: "windows"`. This read `parents[1]`, i.e. the REPO ROOT, and pointed at a
#: `windows/` directory that does not exist. Found by the first real Windows
#: run, not by the suite: the runner test asserts the ps1's ARGV FLAGS, and the
#: flags were right — only the path to the script was wrong. A test that looks
#: like it covers the runner seam and covers only its vocabulary.
WINDOWS_RUNNER = _HERE.parent / "windows" / "dispatch-run.ps1"

#: One flag for the whole dispatch surface. Imported, not re-declared: a second
#: constant with the same value is a second thing to forget to change.
APPLY_FLAG = reconcile.APPLY_FLAG

#: Same character class run.sh and dispatch-run.ps1 validate. Checked HERE, before
#: the claim, because a job id the runner will reject must not be discovered after
#: we already hold the item — that leaves a claim on an issue that cannot run.
JOB_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

#: run.sh's `valid_issue_ref`. `reconcile.split_issue` is stricter about the
#: NUMBER and looser about the owner — it accepts `repo#1`, which the runner would
#: reject at submit time, i.e. after the claim is already held. Both checks run.
ISSUE_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+#[0-9]+$")

#: The runner's own vocabulary for "this job has ended", from run.sh's
#: `write_status` and the Windows script's status.json. `running`/`submitted` are
#: not terminal and must keep the poll loop going.
TERMINAL_JOB_STATES = frozenset({"finished", "cancelled"})

DEFAULT_TIMEOUT_SECONDS = 3600
DEFAULT_POLL_SECONDS = 5

#: Mirrors records.py's stamp format. A test round-trips a stamp minted here
#: through `records._parse` rather than comparing the literals, so the two agree
#: about the format instead of merely looking alike.
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# What prepare() decided to do with the issue.
CLAIM = "claim"          # no record yet
RESUME = "resume"        # our own live claim — re-entered, not re-attempted
RECLAIM = "reclaim"      # a released/finished record, fresh attempt
REFUSE = "refuse"

# How far the drain got. `stage` is diagnostic; `ok` is the decision.
PLANNED = "planned"
REFUSED = "refused"
CLAIM_REFUSED = "claim-refused"
RELEASED = "released"
RELEASE_FAILED = "release-failed"

# failure_category values this module writes.
PAYLOAD_ERROR = "payload-error"
DISPATCH_ERROR = "dispatch-error"
CANCELLED = "cancelled"
UNKNOWN_OUTCOME = "unknown-outcome"

#: run.sh's EX_NOINPUT: the wrapper started but could not enter the work dir, so
#: the payload never ran. Distinguishable from a payload that ran and failed,
#: because the follow-up is different (fix the dispatch, not the work).
EX_NOINPUT = 66


def _stamp(now=None) -> str:
    return (now or (lambda: datetime.now(timezone.utc)))().strftime(TS_FORMAT)


def default_host() -> str:
    """This host's canonical ROLE id — not necessarily its OS hostname.

    The original returned `socket.gethostname()` and guarded, correctly, against
    a hostname LITERAL in shared source. It did not guard against writing the
    runtime value into a record — and records are committed and pushed to a
    PUBLIC repo. On a box whose OS name must not appear there, a real drain would
    have published it in `.claude/dispatch/records/*.json`.

    Found by the first live Windows run, which printed `claim as <real-os-name>`.
    Nothing in the hermetic suite could see it: on the Linux box the OS hostname
    and the role id happen to be the same string, so the defect is invisible
    exactly where the tests run.

    So the private-tier identity is consulted first, via the SAME mechanism as
    scripts/readiness/lib/machine-identity.sh (#3571) and sync-agent-configs.sh —
    an off-repo, gitignored file naming the box's fleet identity. Falling back to
    the OS hostname is correct only where the two already agree.
    """
    label = identity_machine()
    if label:
        return label
    return socket.gethostname().strip().lower()


def identity_machine() -> str | None:
    """The role id this box declares for itself, or None.

    Same contract as machine-identity.sh's resolve_identity_file: absent file
    falls through; a file naming a DIFFERENT box is refused rather than used,
    because an identity file copied to the wrong host would mint claims under
    someone else's name — worse than having no file at all.

    Diagnostics never echo the hostname VALUE: this output can reach tracked logs.
    """
    path = os.environ.get("WORKSPACE_HUB_MACHINE_IDENTITY") or os.path.join(
        os.path.expanduser("~"), ".config", "workspace-hub", "machine-identity.yaml")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as exc:                                    # noqa: BLE001
        raise SystemExit(f"machine-identity: {path} is unreadable: {type(exc).__name__}")
    label = str(data.get("machine") or "").strip()
    if not label:
        raise SystemExit(f"machine-identity: {path} lacks the required 'machine:' key")
    expected = str(data.get("expected_hostname") or "").strip().lower()
    if expected and expected != socket.gethostname().strip().lower():
        raise SystemExit(
            f"machine-identity: expected_hostname in {path} does not match this "
            f"box — refusing a copied identity file")
    return label


# ---------------------------------------------------------------------------
# execution surface
# ---------------------------------------------------------------------------


@dataclass
class ExecOutcome:
    """What the runner observed. `returncode is None` means IT COULD NOT TELL.

    None is not a failure code and must never be coerced into one. A drain that
    turned "the status verb was unreadable" into `returncode: 1` would be
    inventing an observation, and one that turned it into 0 would be inventing a
    completion — the defect this epic exists to close, wearing a helpful face.
    """

    returncode: int | None
    job_state: str | None = None
    detail: str = ""
    log_ref: str | None = None
    started_at: str | None = None
    finished_at: str | None = None


class SubprocessRunner:
    """Drives a dispatch runner through its verbs: submit, then poll status.

    Submit and status are separate on purpose — that split is the runner's whole
    durability story (`run.sh` header, `dispatch-run.ps1` §IssueRef): the runner
    is the only thing that still knows the real exit code if the caller dies, so
    the caller must ask it rather than remember.

    Every failure path returns `ExecOutcome(returncode=None)` with a detail
    string. Raising instead would strand the claim: the drain must still get to
    release, or the item stays `active` until its TTL expires and gets re-run.
    """

    def __init__(self, *, script: Path | str, env: dict | None = None,
                 timeout: int = DEFAULT_TIMEOUT_SECONDS,
                 poll_seconds: float = DEFAULT_POLL_SECONDS,
                 sleep=time.sleep, clock=time.monotonic):
        self.script = Path(script)
        self.env = env
        self.timeout = timeout
        self.poll_seconds = poll_seconds
        self._sleep = sleep
        self._clock = clock

    # -- to be provided by the platform subclass --------------------------

    def submit_argv(self, *, issue: str, job_id: str, command: str,
                    work_dir: str | None) -> list[str]:
        raise NotImplementedError

    def status_argv(self, job_id: str) -> list[str]:
        raise NotImplementedError

    def describe(self, *, issue: str, job_id: str, command: str,
                 work_dir: str | None) -> str:
        return " ".join(self.submit_argv(issue=issue, job_id=job_id,
                                         command=command, work_dir=work_dir))

    # -- plumbing ---------------------------------------------------------

    def _invoke(self, argv: list[str]) -> dict | None:
        """One JSON object, or None. Both runners guarantee exactly one."""
        try:
            done = subprocess.run(argv, capture_output=True, text=True,
                                  timeout=self.timeout, check=False, env=self.env)
        except (OSError, subprocess.SubprocessError):
            return None
        try:
            obj = json.loads((done.stdout or "").strip())
        except (ValueError, TypeError):
            return None
        return obj if isinstance(obj, dict) else None

    def execute(self, *, issue: str, job_id: str, command: str,
                work_dir: str | None = None) -> ExecOutcome:
        submitted = self._invoke(self.submit_argv(
            issue=issue, job_id=job_id, command=command, work_dir=work_dir))
        if not submitted or submitted.get("ok") is not True:
            detail = (submitted or {}).get("error", "no parseable submit output")
            return ExecOutcome(None, detail=f"submit refused: {detail}")

        deadline = self._clock() + self.timeout
        while True:
            status = self._invoke(self.status_argv(job_id))
            if status is None:
                return ExecOutcome(None, detail="status verb produced nothing readable")
            state = status.get("state")
            if state in TERMINAL_JOB_STATES:
                code = status.get("exit_code")
                return ExecOutcome(
                    code if isinstance(code, int) else None,
                    job_state=state,
                    detail=("" if isinstance(code, int)
                            else f"job reported {state!r} with no exit code"),
                    log_ref=status.get("dir"),
                )
            if self._clock() >= deadline:
                return ExecOutcome(
                    None, job_state=state,
                    detail=f"still {state!r} after {self.timeout}s — outcome unknown")
            self._sleep(self.poll_seconds)


class ShellRunner(SubprocessRunner):
    """`scripts/dispatch/run.sh` — the Linux half.

    `--foreground` because a drain is synchronous: it must know the exit code
    before it may release, and a detached submit returns before the payload ends.
    Releasing on a submit's return would record a completion nobody observed. The
    foreground path writes the IDENTICAL record (run.sh `cmd_submit`), so this is
    the same runner, minus the race.
    """

    def __init__(self, *, script: Path | str = RUN_SH, bash: str = "bash", **kw):
        super().__init__(script=script, **kw)
        self.bash = bash

    def submit_argv(self, *, issue, job_id, command, work_dir):
        argv = [self.bash, str(self.script), "submit", "--command", command,
                "--issue-ref", issue, "--job-id", job_id, "--foreground"]
        if work_dir:
            argv += ["--work-dir", str(work_dir)]
        return argv

    def status_argv(self, job_id):
        return [self.bash, str(self.script), "status", "--job-id", job_id]


class PowerShellRunner(SubprocessRunner):
    """`scripts/windows/dispatch-run.ps1` — the licensed-host half.

    No foreground verb exists there and must not be added: the durability comes
    from a Scheduled Task precisely because Windows OpenSSH kills the descendant
    tree at session close. So this one submits and polls, which is why the poll
    loop above is shared rather than special-cased for Linux.
    """

    def __init__(self, *, script: Path | str = WINDOWS_RUNNER,
                 powershell: str = "powershell", shell: str = "bash", **kw):
        super().__init__(script=script, **kw)
        self.powershell = powershell
        self.shell = shell

    def submit_argv(self, *, issue, job_id, command, work_dir):
        argv = [self.powershell, "-NoProfile", "-File", str(self.script),
                "-Action", "submit", "-Command", command, "-IssueRef", issue,
                "-JobId", job_id, "-Shell", self.shell]
        if work_dir:
            argv += ["-WorkDir", str(work_dir)]
        return argv

    def status_argv(self, job_id):
        return [self.powershell, "-NoProfile", "-File", str(self.script),
                "-Action", "status", "-JobId", job_id]


#: The two real execution surfaces. Named here so the dry-run plan can print the
#: exact argv of the runner that would be used, without constructing the one that
#: will be.
RUNNERS = {"shell": ShellRunner, "powershell": PowerShellRunner}


def classify(outcome: ExecOutcome) -> tuple[str, str, str | None]:
    """(state, reason, failure_category) for an observed run. Never optimistic.

    Only an observed 0 is a clean `done`. Everything else is recorded as what it
    was: a payload that failed, a payload that was killed, a dispatch that never
    reached the payload, or an outcome nobody saw.
    """
    rc = outcome.returncode
    if rc is None:
        return "blocked", (outcome.detail or "outcome could not be determined"), UNKNOWN_OUTCOME
    if rc == 0:
        return "done", "ran to completion, exit 0", None
    if rc > 128:
        return "done", f"payload killed by signal {rc - 128}", CANCELLED
    if rc == EX_NOINPUT:
        return "done", f"dispatch could not start the payload (exit {rc})", DISPATCH_ERROR
    return "done", f"payload exited {rc}", PAYLOAD_ERROR


# ---------------------------------------------------------------------------
# what to claim, and whether we may
# ---------------------------------------------------------------------------


@dataclass
class Preparation:
    ok: bool
    action: str
    reason: str
    record: dict | None = None


def prepare(records_root, issue: str, *, host: str, job_id: str,
            machine: str | None = None, queue_generation_id: str | None = None,
            ttl_minutes: int = records.DEFAULT_TTL_MINUTES,
            max_attempts: int = records.DEFAULT_MAX_ATTEMPTS,
            now=None) -> Preparation:
    """Decide the record to claim with — or refuse. READ-ONLY.

    Resumability lives here. Re-running against our OWN live claim re-enters it
    (same host, same job_id, same attempt, fresh heartbeat) instead of minting a
    second attempt: an operator re-running a drain after a dropped SSH session
    must not make the record say the work was tried twice.

    Re-running against SOMEONE ELSE's claim refuses, whatever its heartbeat says.
    See the module docstring: liveness is reconcile's job, and a second opinion
    about it is a race.
    """
    root = Path(records_root)
    path = records.record_path(root, issue)

    if not path.exists():
        return Preparation(True, CLAIM, "no record yet — first attempt",
                           records.new_claim(issue, machine=machine or host,
                                             host=host, job_id=job_id,
                                             queue_generation_id=queue_generation_id,
                                             ttl_minutes=ttl_minutes,
                                             max_attempts=max_attempts, now=now))

    try:
        existing = records.read_record(path)
    except (ValueError, OSError) as exc:
        # Overwriting a record we cannot read destroys the only evidence of
        # whatever wrote it. Refusing costs one drain; guessing costs the history.
        return Preparation(False, REFUSE,
                           f"existing record at {path} is unreadable ({exc}) — "
                           f"refusing to overwrite what we cannot read")

    state = existing.get("state")

    if state == "active":
        if existing.get("host") != host:
            return Preparation(
                False, REFUSE,
                f"{issue} is held by {existing.get('host')}/{existing.get('job_id')} "
                f"(state {state!r}, heartbeat {existing.get('heartbeat_at')}) — "
                f"another host's claim is not ours to adjudicate; run reconcile if "
                f"it is genuinely stale")
        return Preparation(True, RESUME,
                           f"re-entering our own claim (attempt "
                           f"{existing.get('attempt')}, job {existing.get('job_id')})",
                           records.heartbeat(existing, now=now))

    if state == "blocked":
        return Preparation(False, REFUSE,
                           f"{issue} is quarantined: {existing.get('reason')!r} after "
                           f"{existing.get('attempt')} attempt(s) — a human decides "
                           f"whether it runs again, not a drain")

    # `ready` (reconcile returned an expired claim) or `done` (a finished run).
    # Both are fresh attempts, and both consume one.
    if records.should_quarantine(existing):
        return Preparation(False, REFUSE,
                           f"{issue} has used {existing.get('attempt')} of "
                           f"{existing.get('max_attempts')} attempts — refusing to "
                           f"start an unbounded retry loop")
    return Preparation(True, RECLAIM,
                       f"fresh attempt on a record in state {state!r} "
                       f"(attempt {int(existing.get('attempt') or 1) + 1})",
                       records.reclaim(existing, host=host, job_id=job_id, now=now))


# ---------------------------------------------------------------------------
# the drain
# ---------------------------------------------------------------------------


@dataclass
class DrainResult:
    """`ok` answers "DID THE LOOP CLOSE?" — not "did the work succeed".

    Closed means: the claim was confirmed on the remote, the runner was asked,
    and a terminal record carrying the outcome was pushed. A payload that exits 3
    closes the loop perfectly. `work_succeeded` is the only success test and it
    delegates to `records.is_success`, so the two questions cannot be conflated
    by reading the wrong field.
    """

    ok: bool
    stage: str
    reason: str
    record: dict | None = None
    planned: dict | None = None
    returncode: int | None = None
    dry_run: bool = False
    action: str | None = None
    intended_label: str | None = None
    label_stats: dict | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def work_succeeded(self) -> bool:
        return records.is_success(self.record or {})


def new_job_id(now=None) -> str:
    """Sortable stamp plus enough randomness for two submits in one second."""
    stamp = (now or (lambda: datetime.now(timezone.utc)))().strftime("%Y%m%dT%H%M%SZ")
    return f"drain-{stamp}-{os.urandom(3).hex()}"


def plan_text(issue: str, prep: Preparation, *, command: str, records_root,
              work_dir: str | None, runner_desc: str, armed: bool) -> str:
    lines = [
        f"dispatch drain — {issue}",
        f"  records      {records_root}",
        f"  action       {prep.action}: {prep.reason}",
    ]
    if prep.record is not None:
        lines += [
            f"  claim as     {prep.record.get('host')}/{prep.record.get('job_id')} "
            f"attempt {prep.record.get('attempt')}/{prep.record.get('max_attempts')}",
            f"  would run    {runner_desc}",
            f"  work dir     {work_dir or '(runner default: the job dir)'}",
            "  then         claim.acquire -> execute -> claim.release -> reconcile projects the label",
            "  outcome      exit 0 -> done/returncode 0; nonzero -> done with that code "
            "and a failure_category; unknown -> blocked (never a 0 nobody observed)",
        ]
    lines.append(
        f"  WRITES ARMED ({APPLY_FLAG} is set)." if armed
        else f"  dry run — nothing written, nothing executed. Needs --apply AND {APPLY_FLAG}=1.")
    return "\n".join(lines)


def drain(records_root, issue: str, *, command: str, host: str | None = None,
          machine: str | None = None, job_id: str | None = None,
          work_dir: str | None = None, repo_root=None, runner=None,
          runner_kind: str = "shell", git=None,
          apply: bool = False, current_generation: str | None = None,
          queue_generation_id: str | None = None,
          ttl_minutes: int = records.DEFAULT_TTL_MINUTES,
          max_attempts: int = records.DEFAULT_MAX_ATTEMPTS,
          labels=None, gh_fn=None, now=None, log=None) -> DrainResult:
    """Take one issue through claim -> execute -> release -> project.

    Dry run unless `apply` AND the environment gate are BOTH set; a dry run
    reaches no write primitive at all — not the record file, not git, not the
    runner. The plan it prints is computed from the same `prepare()` the armed
    path uses, so it describes the run that would actually happen.
    """
    log = log or (lambda _line: None)
    warnings: list[str] = []
    host = host or default_host()
    job_id = job_id or new_job_id(now=now)

    try:
        reconcile.split_issue(issue)
    except ValueError as exc:
        return DrainResult(False, REFUSED, str(exc), dry_run=not apply)
    if not ISSUE_RE.match(issue):
        return DrainResult(False, REFUSED,
                           f"issue {issue!r} is not owner/repo#N — the runner would "
                           f"reject it at submit time, after the claim was held",
                           dry_run=not apply)
    if not JOB_ID_RE.match(job_id):
        # The runner would reject it AFTER we hold the claim, stranding the item.
        return DrainResult(False, REFUSED,
                           f"job id {job_id!r} is not acceptable to the runner "
                           f"(letters, digits, dot, underscore, hyphen; max 64)",
                           dry_run=not apply)

    armed = apply and reconcile.writes_armed()
    if apply and not armed:
        # Asking for writes is not being permitted them. Same sentence as
        # reconcile's gate, and refused before anything is touched.
        return DrainResult(
            False, REFUSED,
            f"REFUSED: drain writes are gated. Set {APPLY_FLAG}=1 to arm this "
            f"invocation — it claims an issue, runs a command, and pushes a record.",
            dry_run=True)

    prep = prepare(records_root, issue, host=host, job_id=job_id, machine=machine,
                   queue_generation_id=queue_generation_id, ttl_minutes=ttl_minutes,
                   max_attempts=max_attempts, now=now)

    def plan() -> str:
        # The description is built from a FRESH runner of the requested kind, never
        # from the injected one: `describe` is pure, but a dry run that calls a
        # method on the execution surface at all is one refactor away from calling
        # a different one. Nothing on that object is touched until the claim holds.
        desc = RUNNERS[runner_kind](timeout=0).describe(
            issue=issue, job_id=job_id, command=command, work_dir=work_dir)
        return plan_text(issue, prep, command=command, records_root=records_root,
                         work_dir=work_dir, runner_desc=desc, armed=armed)

    if not prep.ok:
        log(plan())
        return DrainResult(False, REFUSED, prep.reason, action=prep.action,
                           dry_run=not armed)

    if not armed:
        log(plan())
        # `planned`, not `record`: a plan must not be reachable through the field
        # a caller reads after a real drain. Same discipline as ClaimResult's
        # `record=None` on refusal.
        return DrainResult(True, PLANNED,
                           "dry run — nothing claimed, nothing executed, nothing written",
                           planned=prep.record, action=prep.action, dry_run=True)

    runner = runner or RUNNERS[runner_kind]()
    git = git or claim.GitBackend(Path(repo_root or records_root),
                                  records_dir=Path(records_root))

    # ---- 1. claim ------------------------------------------------------
    held = claim.acquire(records_root, prep.record, git=git,
                         current_generation=current_generation)
    warnings.extend(held.warnings)
    if not held.ok:
        # THE ONE BRANCH THAT MUST NOT FALL THROUGH. `ok is True` is the only
        # licence to execute; there is no second way to ask.
        return DrainResult(False, CLAIM_REFUSED, held.reason, action=prep.action,
                           warnings=warnings)

    # ---- 2. execute ----------------------------------------------------
    rec = dict(held.record)
    rec["started_at"] = _stamp(now)
    rec["command_ref"] = command
    try:
        outcome = runner.execute(issue=issue, job_id=rec.get("job_id"),
                                 command=command, work_dir=work_dir)
    except Exception as exc:                      # noqa: BLE001 — see below
        # A runner that raises must still produce a truthful record. Letting the
        # exception out would leave the item `active` until its TTL expired and
        # something re-ran it — work that finished with nothing recording it,
        # which is the original defect one layer up.
        outcome = ExecOutcome(None, detail=f"runner raised {type(exc).__name__}: {exc}")

    state, reason, category = classify(outcome)
    if outcome.log_ref:
        rec["log_ref"] = outcome.log_ref
    if category is not None:
        # `claim.release` takes no failure_category, and `records.transition`
        # only overwrites the field when its argument is not None — so setting it
        # on the record we hand over carries it into the terminal state without a
        # second transition and without editing slice 2.
        rec["failure_category"] = category

    # ---- 3. release ----------------------------------------------------
    released = claim.release(records_root, rec, state=state, reason=reason,
                             returncode=outcome.returncode, git=git)
    if not released.ok:
        return DrainResult(False, RELEASE_FAILED,
                           f"{released.reason} (intended {state!r}, returncode "
                           f"{outcome.returncode!r}: {reason})",
                           returncode=outcome.returncode, action=prep.action,
                           warnings=warnings)

    # ---- 4. project ----------------------------------------------------
    final = released.record
    intended = reconcile.intended_label(final)
    stats = None
    if labels is not None:
        outcome_ = reconcile.reconcile_issue(final, tuple(labels), now=now)
        report = reconcile.Report(outcomes=[outcome_],
                                  findings=list(outcome_.findings),
                                  records_root=Path(records_root))
        log(reconcile.format_report(report, armed=True))
        stats = reconcile.apply(report, records_root, gh_fn=gh_fn)
    else:
        log(f"  label projection: {issue} -> {intended}. Project it with:\n"
            f"    {APPLY_FLAG}=1 python {_HERE / 'reconcile.py'} "
            f"--records {records_root} --repo {issue.rpartition('#')[0]} --apply")

    return DrainResult(True, RELEASED, f"{state}: {reason}", record=final,
                       returncode=outcome.returncode, action=prep.action,
                       intended_label=intended, label_stats=stats,
                       warnings=warnings)


def exit_code(result: DrainResult) -> int:
    """0 only for a dry run or work that actually succeeded.

    Three values, because two would force a caller to conflate "the work failed"
    with "the loop did not close" — and those need different humans.
    """
    if result.dry_run and result.ok:
        return 0
    if not result.ok:
        return 2                      # the loop did not close: claim/release/refusal
    return 0 if result.work_succeeded else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--issue", required=True, help="owner/repo#123")
    ap.add_argument("--records", required=True, help="directory of record JSON files")
    ap.add_argument("--command", required=True, help="the payload to run")
    ap.add_argument("--repo-root", help="checkout the records live in (default: --records)")
    ap.add_argument("--work-dir", help="working directory for the payload")
    ap.add_argument("--host", help="claim identity (default: this host's name)")
    ap.add_argument("--machine", help="logical machine label recorded with the claim")
    ap.add_argument("--job-id", help="runner job id (default: minted)")
    ap.add_argument("--queue-generation", help="generation id to record on the claim")
    ap.add_argument("--current-generation",
                    help="refuse the claim unless it declares this generation")
    ap.add_argument("--ttl-minutes", type=int, default=records.DEFAULT_TTL_MINUTES)
    ap.add_argument("--max-attempts", type=int, default=records.DEFAULT_MAX_ATTEMPTS)
    ap.add_argument("--runner", choices=("shell", "powershell"), default="shell")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS,
                    help="seconds to wait for the payload before the outcome is "
                         "recorded as unknown (never as success)")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--branch", help="branch to push and verify against")
    ap.add_argument("--labels-json",
                    help="offline {issue: [labels]} snapshot; supplying it lets the "
                         "drain project the label through reconcile")
    ap.add_argument("--apply", action="store_true",
                    help=f"actually claim, run and record (still requires {APPLY_FLAG}=1)")
    args = ap.parse_args(argv)

    records_root = Path(args.records)
    repo_root = Path(args.repo_root) if args.repo_root else records_root

    runner = git = None
    if args.apply and reconcile.writes_armed():
        runner = RUNNERS[args.runner](timeout=args.timeout)
        git = claim.GitBackend(repo_root, records_dir=records_root,
                               remote=args.remote, branch=args.branch)

    labels = None
    if args.labels_json:
        labels = reconcile.load_labels_json(args.labels_json).get(args.issue, set())

    result = drain(records_root, args.issue, command=args.command, host=args.host,
                   machine=args.machine, job_id=args.job_id, work_dir=args.work_dir,
                   repo_root=repo_root, runner=runner, runner_kind=args.runner,
                   git=git, apply=args.apply,
                   current_generation=args.current_generation,
                   queue_generation_id=args.queue_generation,
                   ttl_minutes=args.ttl_minutes, max_attempts=args.max_attempts,
                   labels=labels, log=print)

    for warning in result.warnings:
        print(f"  WARN {warning}")
    print(f"  {result.stage}: {result.reason}")
    if result.record is not None:
        print(f"  record: state={result.record.get('state')} "
              f"returncode={result.record.get('returncode')!r} "
              f"failure_category={result.record.get('failure_category')!r} "
              f"success={result.work_succeeded}")
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
