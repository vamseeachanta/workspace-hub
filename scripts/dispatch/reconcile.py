#!/usr/bin/env python3
"""reconcile.py — the label is a projection; this pass recomputes it. #3740 slice 3.

867 issues sit at `dispatch:ready` and cannot advance. `SCHEMA.yaml:125` documents
`ready | active | done`, but only `ready` was ever created and nothing writes a
later state. Slice 1 made the record authoritative; slice 2 made claiming it safe.
This slice closes the loop: it derives what each `dispatch:` label *should* say
from the record, and writes only the difference.

## One direction, always

Records -> labels. **Never** labels -> records. A label carries no evidence — not
when, not which host, not what exit code — so inferring a record from one would
manufacture history that no run produced. An issue carrying `dispatch:active`
with no record behind it is therefore REPORTED and left alone; it is not adopted.
That asymmetry is the whole design, and every no-op class below exists to make a
violation of it visible rather than convenient.

## Drift is a finding, not a silent fix

Humans read the GitHub UI and believe it. If the label says `ready` while the
record says `done`, someone has already been told something false — possibly
acted on it. Quietly correcting the label repairs the data and destroys the
evidence that the projection had failed. So drift is reported FIRST, and reported
**even when writes are disabled**: a dry run that hides drift is worse than no
reconciler, because it reads as confirmation.

## Dry run by default

`DISPATCH_APPLY_ENABLED` gates every mutation, mirroring `route.assert_write_allowed`
(deckhand#584 slice 2, where `--apply` reached a live `gh issue edit` while the help
text claimed the path was disabled). The gate covers **record** writes too, not
just label writes: this pass can transition a stale claim to `ready` or `blocked`,
and a dry run that advances the state machine is not a dry run.

## What it corrects, and what it refuses to

- expired heartbeat  -> back to `ready`, reason "heartbeat expired"
- expired AND out of attempts -> `blocked`, keeping the attempt history. An
  unbounded retry loop is this epic's defect wearing a helpful face: it looks
  like resilience and hides a job that can never succeed.
- heartbeat in the FUTURE -> clock skew. Reported, never acted on. Hosts do not
  share a clock; treating a fast clock as expiry requeues live work and presents
  as random job loss.

Run: uv run --with pyyaml python scripts/dispatch/reconcile.py --records <dir> \
       --labels-json <file>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Sibling scripts, not a package. Same shape as slice 2's loader: put this
# directory on the path so `records`/`route` resolve whether reconcile.py is run
# directly, imported by a test, or exec'd from another cwd.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import records  # noqa: E402
import route  # noqa: E402

DISPATCH_PREFIX = "dispatch:"

#: The projection itself. Built FROM `records.STATES` rather than typed out, so a
#: new state cannot be added to the lifecycle without a label to project it into.
LABEL_FOR_STATE = {state: f"{DISPATCH_PREFIX}{state}" for state in records.STATES}
STATE_LABELS = frozenset(LABEL_FOR_STATE.values())

#: Declared at the write boundary, exactly as `route.cmd_apply` declares `ai:`.
#: `dispatch:` is not in routing-rules.yaml's `single` list because nothing used
#: to write it; this process is the only place it is created, so this is the
#: place that has to say it is scalar. Two `dispatch:` labels on one issue would
#: make the state depend on the order GitHub returned them.
WRITE_SINGLE_AXES = frozenset({DISPATCH_PREFIX})

#: Reused, not reimplemented. A second copy of the cardinality rule would drift
#: from route.py's and the two would disagree about what a legal write is.
assert_write_preserves_cardinality = route.assert_write_preserves_cardinality

APPLY_FLAG = route.APPLY_FLAG
#: Only these open the gate. Anything else — including "0", "false", "off" and the
#: empty string — fails closed. Bound to route.py's set by an equality test rather
#: than by import of a private name: two gates that disagree about what "armed"
#: means is worse than one gate, because each looks correct in isolation.
AFFIRMATIVE = frozenset({"1", "true", "yes", "on"})

# ---------------------------------------------------------------------------
# Finding classes.
#
# Declared as an ordered table, and the report walks THE TABLE — not the findings
# it happened to collect. A reconciler that prints nothing when it changed nothing
# is indistinguishable from one that failed to run, so every class reports its
# count even when that count is zero.
# ---------------------------------------------------------------------------

IN_SYNC = "in-sync"
DRIFT = "label-record-drift"
LABEL_MISSING = "label-missing"
LABEL_AMBIGUOUS = "label-ambiguous"
ORPHAN_LABEL = "label-without-record"
STALE_ACTIVE = "stale-active"
QUARANTINED = "quarantined"
CLOCK_SKEW = "clock-skew"
UNREADABLE = "record-unreadable"

FINDING_KINDS = (
    (IN_SYNC, "label already equals the record — nothing to do"),
    (DRIFT, "GitHub shows a state the record does not support"),
    (LABEL_MISSING, "record exists, issue carries no dispatch: label at all"),
    (LABEL_AMBIGUOUS, "two dispatch: labels — state would depend on API order"),
    (ORPHAN_LABEL, "label with no record — REPORTED, never adopted as state"),
    (STALE_ACTIVE, "heartbeat past its own ttl — returned to ready"),
    (QUARANTINED, "attempts exhausted — stopped at blocked instead of looping"),
    (CLOCK_SKEW, "heartbeat ahead of this host's clock — held, not expired"),
    (UNREADABLE, "record could not be parsed — skipped, pass continues"),
)


DECLARED_KINDS = frozenset(kind for kind, _ in FINDING_KINDS)


@dataclass(frozen=True)
class Finding:
    kind: str
    issue: str
    detail: str

    def __post_init__(self):
        """Refuse an undeclared kind AT EMISSION, not at reporting time.

        The table above exists so a class with a count of zero still prints.
        This is that guarantee's other direction, and it was missing: `counts()`
        tallies any kind via `.get(kind, 0)`, but `format_report` walks the
        DECLARED table — so a kind emitted here and never added to the table is
        counted and never shown. The report stays complete-looking while an
        entire class of finding is invisible, which is the exact defect the
        table was built to prevent.

        Raising here fails at the line that made the mistake. Validating in
        `format_report` instead would surface it only on a run that happened to
        produce one, which for a rare class could be months later.
        """
        if self.kind not in DECLARED_KINDS:
            raise ValueError(
                f"finding kind {self.kind!r} is not in FINDING_KINDS — it would be "
                f"counted and never printed. Add it to the table, with the line the "
                f"report should show, before emitting it."
            )


@dataclass
class Outcome:
    """One issue's reconciliation. Computed identically armed or not."""

    issue: str
    current: tuple[str, ...]
    intended: str
    add: tuple[str, ...] = ()
    remove: tuple[str, ...] = ()
    record: dict | None = None
    record_changed: bool = False
    findings: tuple[Finding, ...] = ()

    @property
    def writes_labels(self) -> bool:
        return bool(self.add or self.remove)


@dataclass
class Report:
    outcomes: list[Outcome]
    findings: list[Finding]
    records_root: Path | None = None

    def counts(self) -> dict[str, int]:
        """Every declared kind, including the zeros. See FINDING_KINDS."""
        out = {kind: 0 for kind, _ in FINDING_KINDS}
        for f in self.findings:
            out[f.kind] = out.get(f.kind, 0) + 1
        return out

    def of_kind(self, kind: str) -> list[Finding]:
        return [f for f in self.findings if f.kind == kind]

    @property
    def label_writes(self) -> list[Outcome]:
        return [o for o in self.outcomes if o.writes_labels]

    @property
    def record_writes(self) -> list[Outcome]:
        return [o for o in self.outcomes if o.record_changed]


# ---------------------------------------------------------------------------
# liveness: what the record says about itself before anything is projected
# ---------------------------------------------------------------------------


def attempt_history(record: dict) -> str:
    """Who tried what, in order.

    Quarantine without the history is a dead end nobody can debug: the question
    that follows `blocked` is always "failing the same way on the same host, or
    differently on three?" and only the attempt list answers it.
    """
    parts = []
    for a in record.get("attempts") or []:
        line = f"#{a.get('attempt')} {a.get('host')}/{a.get('job_id')}"
        if a.get("outcome"):
            line += f" -> {a['outcome']}"
        parts.append(line)
    return "; ".join(parts) or "no attempt history recorded"


def settle(record: dict, now=None) -> tuple[dict, list[Finding]]:
    """Resolve a claim's liveness. Returns the record the label should project.

    `now` is a zero-argument CALLABLE, matching records.py — an injected clock,
    so expiry is testable without sleeping and without a real host clock.
    """
    issue = record.get("issue", "?")
    if record.get("state") != "active":
        return record, []          # only a live claim can go stale

    # Skew is checked BEFORE expiry, though `is_expired` already returns False
    # for a future beat. The point is not the arithmetic — it is that a fast
    # clock produces a REPORT rather than silence. Without this branch the
    # outcome is correct and invisible, and nobody learns the fleet's clocks
    # have drifted until something else breaks.
    if records.clock_skew_detected(record, now=now):
        return record, [Finding(
            CLOCK_SKEW, issue,
            f"heartbeat {record.get('heartbeat_at')} is more than "
            f"{records.SKEW_GRACE_SECONDS}s ahead of this host — held as active, "
            f"not expired, and no attempt consumed")]

    if not records.is_expired(record, now=now):
        return record, []

    ttl = record.get("ttl_minutes") or records.DEFAULT_TTL_MINUTES
    attempt = record.get("attempt") or 1
    limit = record.get("max_attempts") or records.DEFAULT_MAX_ATTEMPTS

    if records.should_quarantine(record):
        out = records.transition(record, "blocked", reason="attempts exhausted",
                                 failure_category="quarantine", now=now)
        return out, [Finding(
            QUARANTINED, issue,
            f"expired at attempt {attempt}/{limit} — stopped rather than "
            f"requeued; history: {attempt_history(record)}")]

    out = records.transition(record, "ready", reason="heartbeat expired", now=now)
    return out, [Finding(
        STALE_ACTIVE, issue,
        f"heartbeat {record.get('heartbeat_at')} older than its own ttl of {ttl}m "
        f"— returned to ready (attempt {attempt}/{limit})")]


# ---------------------------------------------------------------------------
# projection
# ---------------------------------------------------------------------------


def intended_label(record: dict) -> str:
    """The one label this record implies. The only direction that exists."""
    records.validate(record)
    return LABEL_FOR_STATE[record["state"]]


def reconcile_issue(record: dict, labels=(), now=None) -> Outcome:
    """Compute one issue's difference. Pure: reads nothing, writes nothing."""
    records.validate(record)
    before = record.get("state")
    record, findings = settle(record, now=now)
    # A record correction is a state change, not "settle returned a new dict":
    # `transition()` copies, so identity would report a change on every pass and
    # every dry run would claim work it did not do.
    changed = record.get("state") != before
    issue = record["issue"]
    intended = LABEL_FOR_STATE[record["state"]]

    # Sorted, because GitHub's label order is not stable and a message that
    # varies with it is as unhelpful as the ambiguity it describes.
    present = tuple(sorted(
        lab for lab in (labels or ()) if lab.startswith(DISPATCH_PREFIX)))

    add = () if intended in present else (intended,)
    remove = tuple(lab for lab in present if lab != intended)

    if len(present) > 1:
        findings.append(Finding(
            LABEL_AMBIGUOUS, issue,
            f"carries {', '.join(present)}; the record says {record['state']!r} "
            f"— collapsing to {intended}"))
    elif not present:
        findings.append(Finding(
            LABEL_MISSING, issue,
            f"record says {record['state']!r} but the issue carries no "
            f"dispatch: label — invisible in every board view"))
    elif present[0] != intended:
        findings.append(Finding(
            DRIFT, issue,
            f"label says {present[0]!r}, record says {intended!r} "
            f"(state {record['state']!r} since {record.get('last_transition_at')}) "
            f"— the GitHub UI has been showing the wrong state"))
    else:
        findings.append(Finding(IN_SYNC, issue, f"{intended} matches the record"))

    return Outcome(issue=issue, current=present, intended=intended, add=add,
                   remove=remove, record=record, record_changed=changed,
                   findings=tuple(findings))


def reconcile(records_root, labels_by_issue=None, now=None) -> Report:
    """Reconcile every record under `records_root`. READ-ONLY.

    `labels_by_issue` maps `owner/repo#123` -> the issue's current label names.
    Injected rather than fetched so this function has no network surface at all;
    `fetch_labels()` is the production adapter.
    """
    labels_by_issue = dict(labels_by_issue or {})
    root = Path(records_root)
    outcomes: list[Outcome] = []
    findings: list[Finding] = []
    seen: set[str] = set()

    for path in sorted(root.glob("*.json")):
        try:
            record = records.read_record(path)
        except (ValueError, OSError) as exc:
            # Fail closed on THIS record, never on the pass. One corrupt file
            # must not strand the other 866 — that pressure is how a check gets
            # disabled outright (route.classify_card_axes takes the same line).
            findings.append(Finding(
                UNREADABLE, path.name,
                f"{type(exc).__name__}: {exc} — left exactly as it is"))
            continue
        seen.add(record["issue"])
        outcome = reconcile_issue(record, labels_by_issue.get(record["issue"], ()),
                                  now=now)
        outcomes.append(outcome)
        findings.extend(outcome.findings)

    # Labels with no record behind them. The temptation is to read them as state
    # — 867 issues already carry `dispatch:ready`, so adopting them would look
    # like instant progress. It would also invent 867 runs that never happened.
    for issue in sorted(set(labels_by_issue) - seen):
        present = sorted(lab for lab in labels_by_issue[issue]
                         if lab.startswith(DISPATCH_PREFIX))
        if present:
            findings.append(Finding(
                ORPHAN_LABEL, issue,
                f"carries {', '.join(present)} with no record — NOT inferred "
                f"backwards; a claim has to come from a run"))

    return Report(outcomes=outcomes, findings=findings, records_root=root)


# ---------------------------------------------------------------------------
# write gate
# ---------------------------------------------------------------------------


def assert_write_allowed() -> None:
    """Exit unless the operator explicitly armed writes for this invocation.

    Same flag and same affirmative set as `route.assert_write_allowed` — one
    armed invocation, one env var, set by the person running the command at the
    moment they run it. A config value would be committed and diffable, so a PR
    could arm a mass-write path without anyone registering that it had.
    """
    value = (os.environ.get(APPLY_FLAG) or "").strip().lower()
    if value not in AFFIRMATIVE:
        sys.exit(
            f"REFUSED: reconcile writes are gated. Set {APPLY_FLAG}=1 to arm "
            f"this invocation.\n"
            f"  This pass can edit `dispatch:` labels AND transition records "
            f"(stale claims to ready, exhausted ones to blocked).\n"
            f"  The dry-run report above is complete — drift is reported "
            f"whether or not writes are armed. Read it first."
        )


def split_issue(issue: str) -> tuple[str, str]:
    """`owner/repo#123` -> ("owner/repo", "123").

    The record carries a fully-qualified issue precisely so a write needs no
    ambient repo: a reconciler run from the wrong checkout must not be able to
    edit the wrong repository's issue of the same number.
    """
    repo, sep, number = issue.rpartition("#")
    if not sep or not repo or not number.isdigit():
        raise ValueError(f"issue {issue!r} is not owner/repo#N — refusing to guess a repo")
    return repo, number


def apply(report: Report, records_root, gh_fn=None) -> dict:
    """Write the difference. Gated; raises SystemExit when not armed."""
    assert_write_allowed()
    gh_fn = gh_fn or route.gh
    stats = {"labels_written": 0, "records_written": 0, "noop": 0, "errors": 0}

    for outcome in report.outcomes:
        # Record BEFORE label, deliberately. If the label write fails afterwards
        # the state is still correct and the next pass re-projects it. Reversed,
        # a failed record write would leave a label advertising a state nothing
        # supports — manufacturing exactly the drift this module exists to remove.
        if outcome.record_changed and outcome.record is not None:
            records.write_record(records_root, outcome.record)
            stats["records_written"] += 1

        if not outcome.writes_labels:
            stats["noop"] += 1
            continue

        merged = (set(outcome.current) - set(outcome.remove)) | set(outcome.add)
        # At the mutation boundary, not in a report afterwards: a wrongly-written
        # label costs a mass migration to undo (#582's 676-issue pass is the
        # local proof of how far one travels).
        assert_write_preserves_cardinality(merged, WRITE_SINGLE_AXES)

        repo, number = split_issue(outcome.issue)
        args = ["issue", "edit", number, "--repo", repo]
        if outcome.add:
            args += ["--add-label", ",".join(outcome.add)]
        if outcome.remove:
            args += ["--remove-label", ",".join(outcome.remove)]
        result = gh_fn(args)
        if getattr(result, "returncode", 1) == 0:
            stats["labels_written"] += 1
        else:
            stats["errors"] += 1
            print(f"    {outcome.issue}  ERR {str(getattr(result, 'stderr', ''))[:70]}")
    return stats


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

#: Classes whose individual lines are always printed. `in-sync` is a count only —
#: it is the one class where the detail carries no information.
DETAILED = (DRIFT, LABEL_AMBIGUOUS, ORPHAN_LABEL, STALE_ACTIVE, QUARANTINED,
            CLOCK_SKEW, LABEL_MISSING, UNREADABLE)


def format_report(report: Report, armed: bool = False) -> str:
    counts = report.counts()
    lines = [
        f"dispatch reconcile — {len(report.outcomes)} record(s) under "
        f"{report.records_root}",
        "  labels are a projection of records; no record is ever inferred from a label",
        "",
    ]
    for kind, description in FINDING_KINDS:
        lines.append(f"  {kind:<22} {counts[kind]:>5}   {description}")
    lines.append("")

    for kind in DETAILED:
        for finding in report.of_kind(kind):
            lines.append(f"  {kind.upper()}  {finding.issue}: {finding.detail}")
    if any(counts[k] for k in DETAILED):
        lines.append("")

    lines.append(
        f"  planned: {len(report.label_writes)} label write(s), "
        f"{len(report.record_writes)} record correction(s)")
    if armed:
        lines.append(f"  WRITES ARMED ({APPLY_FLAG} is set).")
    else:
        lines.append(f"  dry run — no writes. Set {APPLY_FLAG}=1 to arm.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# adapters and CLI
# ---------------------------------------------------------------------------


def fetch_labels(repo: str, fetch=None) -> dict[str, set[str]]:
    """Live labels keyed the way records are: `owner/repo#123`.

    Returns {} and says so rather than {} silently when the API fails — an empty
    snapshot read as "no labels anywhere" would propose adding a label to every
    issue in the repo.
    """
    fetch = fetch or route.fetch_open_issues
    snapshot = fetch(repo)
    if snapshot is None:
        raise RuntimeError(
            f"could not fetch open issues for {repo} (rate limit?) — refusing to "
            f"reconcile against an empty snapshot, which would look like every "
            f"issue had lost its label")
    return {f"{repo}#{number}": set(labels) for number, labels in snapshot.items()}


def load_labels_json(path) -> dict[str, set[str]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {issue: set(labels or ()) for issue, labels in data.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--records", required=True, help="directory of record JSON files")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--labels-json", help="offline {issue: [labels]} snapshot")
    src.add_argument("--repo", help="fetch live labels for owner/name")
    ap.add_argument("--apply", action="store_true",
                    help=f"write the difference (still requires {APPLY_FLAG})")
    args = ap.parse_args(argv)

    labels = (load_labels_json(args.labels_json) if args.labels_json
              else fetch_labels(args.repo))
    report = reconcile(args.records, labels)

    # The report is printed BEFORE the gate is consulted. Drift is a finding, and
    # a finding that only appears once someone has armed writes is a finding
    # nobody sees until it is already being corrected.
    print(format_report(report, armed=args.apply))
    if args.apply:
        stats = apply(report, args.records)
        print(f"  {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
