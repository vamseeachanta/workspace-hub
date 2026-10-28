"""Recommend suppression clears without changing suppression records.

Policy source: issue #2198 requires caller-configured clean-run windows and
excludes manual-only and high-risk records. No numeric policy default is
introduced. The existing declarations load_previous_audit and
build_cleared_followup_issue_drafts in
scripts/analysis/provider_session_ecosystem_audit.py compare audit snapshots;
they establish neither a multi-run threshold nor suppression mutation authority.

Input contract (an explicit adapter contract, not an operational file format):
* Suppressions have unique, nonempty string suppression_id values and explicit
  boolean manual_only and high_risk flags. Unknown flags block recommendations.
* Runs are supplied oldest first within a comparable observation scope. Each
  has a nonempty string run_ref, complete=True, and an observations mapping.
  For each suppression_id, False means explicitly absent and True present.
  Missing keys, other values and incomplete runs break that target's streak.
* Repeated run references count once. Conflicting evidence for a reference
  invalidates every occurrence of that reference for all supplied targets.
  Replay of an earlier absence cannot repair a later evidence gap; unknown
  or incomplete evidence always breaks the streak, including on replay.

The caller establishes chronology, run identity, scope and record applicability.
References are opaque evidence labels, not authenticated provenance. This module
performs no I/O, assignment, policy inference or suppression removal.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _observation_state(run: Mapping, identifier: str) -> str:
    if run.get("complete") is not True:
        return "incomplete_run"
    observations = run.get("observations")
    if not isinstance(observations, Mapping):
        return "unknown_observation"
    if identifier not in observations:
        return "missing_observation"
    observed = observations[identifier]
    if observed is False:
        return "absent"
    if observed is True:
        return "observed"
    return "unknown_observation"


def _run_evidence(runs: Sequence, identifiers: list[str]) -> list[tuple]:
    """Snapshot evidence and detect conflicting replays before counting runs."""
    rows = []
    signatures = {}
    conflicts = set()
    for run in runs:
        reference = run.get("run_ref") if isinstance(run, Mapping) else None
        if not _nonempty_string(reference):
            rows.append((None, tuple("unknown_run" for _ in identifiers)))
            continue
        states = tuple(_observation_state(run, identifier) for identifier in identifiers)
        if reference in signatures and signatures[reference] != states:
            conflicts.add(reference)
        signatures[reference] = states
        rows.append((reference, states))

    distinct = []
    seen = set()
    for reference, states in rows:
        if reference in conflicts:
            # Every ambiguous occurrence breaks the streak at its own position.
            states = tuple("conflicting_run" for _ in identifiers)
        elif reference is not None:
            if reference in seen:
                # Replayed absence is not new evidence. Unknown or adverse
                # observations still break the streak for affected targets.
                states = tuple(
                    "duplicate_run" if state == "absent" else state for state in states
                )
            seen.add(reference)
        distinct.append((reference, states))
    return distinct


def recommend_suppression_clears(
    suppressions: Sequence[Mapping],
    runs: Sequence[Mapping | None],
    *,
    clean_run_window: int,
) -> list[dict]:
    """Return one independent recommendation/diagnostic per suppression.

    A candidate requires a positive integer window of distinct, complete,
    explicitly absent runs at the end of the supplied evidence. Unknown input
    breaks the streak; later clean evidence can establish a new window. Boolean
    truthiness is never accepted in place of an explicit observation or flag.

    reason_codes contains exclusions and, when short of the window, the most
    recent streak-breaking reason followed by insufficient_clean_runs.
    clean_window_met occurs only on recommendations. supporting_run_refs gives
    the final window of clean evidence, or the shorter available clean suffix.
    Evidence may be reported for excluded records without recommending a clear.

    ValueError rejects invalid windows and ambiguous suppression identifiers.
    Nothing is removed or modified, and output containers share no input state.
    """
    # Zero is the empty-window boundary, not a policy threshold (issue #2198).
    if type(clean_run_window) is not int or clean_run_window <= 0:
        raise ValueError("clean_run_window must be a positive integer")

    identifiers = []
    for record in suppressions:
        identifier = record.get("suppression_id") if isinstance(record, Mapping) else None
        if not _nonempty_string(identifier) or identifier in identifiers:
            raise ValueError("suppression identifiers must be unique nonempty strings")
        identifiers.append(identifier)

    evidence = _run_evidence(runs, identifiers)
    results = []
    for index, (identifier, record) in enumerate(zip(identifiers, suppressions)):
        clean_refs = []
        last_break = None
        for reference, states in evidence:
            state = states[index]
            if state == "duplicate_run":
                continue
            if state == "absent":
                clean_refs.append(reference)
            else:
                clean_refs.clear()
                last_break = state

        reasons = []
        if record.get("manual_only") is True:
            reasons.append("manual_only")
        if record.get("high_risk") is True:
            reasons.append("high_risk")
        if any(type(record.get(flag)) is not bool for flag in ("manual_only", "high_risk")):
            reasons.append("unknown_policy")
        if len(clean_refs) < clean_run_window:
            if last_break:
                reasons.append(last_break)
            reasons.append("insufficient_clean_runs")

        recommend = not reasons
        results.append({
            "suppression_id": identifier,
            "recommend_clear": recommend,
            "reason_codes": ["clean_window_met"] if recommend else reasons,
            "supporting_run_refs": clean_refs[-clean_run_window:],
        })
    return results
