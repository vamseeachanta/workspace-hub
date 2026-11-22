"""Read-only recovery plans for interrupted publication promotions.

Basis: issue 2183 acceptance (crash before swap, crash after swap before
finalization, and no-op recovery). This proposed format is local to the
planner; no publisher currently emits it. The v1 suffix denotes its initial
schema version, not a measured quantity.

Versioned synthetic journal example::

    {
      "schema": "publication-rollback-journal-v1",
      "promotion_id": "synthetic-promotion",
      "state": "prepared",
      "staged_id": "N",
      "prior_id": "P",
      "recovery_target_id": "P",
      "evidence": {"ref": "synthetic-observation", "notes": ["retain"]}
    }

``plan_recovery(raw_json, observations)`` requires an explicit journal and an
observation object with current_id, staged_id and prior_id. Identifiers are
opaque, nonempty strings supplied by the caller, never filesystem paths to
open. N is the intended new bundle, P the distinct last-known-good bundle.
staged_id and prior_id observe retained bundles, not consumable staging paths;
both remain required even after finalization. No implicit first publication
or missing-bundle inference is supported. recovery_target_id must equal P.

Literal recovery truth table, with observed staged=N and prior=P:

    journal state   current   action       target
    prepared        P         recover      P
    prepared        N         finalize     N
    swapped         P         unresolved   none
    swapped         N         finalize     N
    finalized       P         unresolved   none
    finalized       N         no-op        N
    recovered       P         no-op        P
    recovered       N         unresolved   none

prepared records durable intent before a swap. swapped records a completed
swap awaiting finalization; finalized and recovered are terminal records.
An observed N with a prepared journal covers a crash after swapping but before
the journal advances. recover means confirm the still-current P and propose
marking the interrupted promotion recovered; finalize means propose marking
the observed N finalized. Neither action grants authority or executes a step.
Contradictions, unknown states/schema, missing identities, indistinguishable
bundles, malformed JSON and duplicate keys at any depth yield unresolved with
no target. Additional descriptive fields are retained without interpretation.

All plans retain raw and parsed journal evidence and independent copies of
observations, including unresolved plans (parsed journal is None if parsing
fails). Retain every journal, staged bundle, prior bundle and observation for
independent review; no cleanup or evidence deletion is proposed. Re-evaluating
identical evidence returns an identical plan. No filesystem access, network,
locking, swaps, journal writes or command execution occurs. Identity/digest
verification, race protection, a live executor and publisher integration remain
separate work; this plan cannot establish that observations are still current.
"""

import copy
import json

from .report_provenance import ProvenanceError, load_manifest


SCHEMA = "publication-rollback-journal-v1"
STATES = ("prepared", "swapped", "finalized", "recovered")


def _identifier(value):
    return isinstance(value, str) and bool(value.strip())


def plan_recovery(journal_json, observations):
    """Return recover/finalize/no-op/unresolved without changing caller state.

    journal_json is raw JSON text or bytes, so duplicate fields cannot already
    have been discarded by a caller's parser. Reasons are fixed diagnostic
    codes; original supplied evidence is retained separately and unmodified.
    """
    result = {
        "action": "unresolved",
        "target_id": None,
        "reason": "invalid-journal-json",
        "evidence": {
            "journal_json": copy.deepcopy(journal_json),
            "journal": None,
            "observations": copy.deepcopy(observations),
        },
    }
    if not isinstance(journal_json, (str, bytes)):
        return result
    try:
        journal = load_manifest(journal_json)
        result["evidence"]["journal"] = journal
        # JSON exponents can overflow even when no NaN token was present.
        json.dumps(journal, allow_nan=False)
    except (ProvenanceError, ValueError, RecursionError):
        return result
    if not isinstance(journal, dict) or journal.get("schema") != SCHEMA:
        result["reason"] = "unsupported-journal-schema"
        return result
    if journal.get("state") not in STATES:
        result["reason"] = "unknown-journal-state"
        return result
    if any(not _identifier(journal.get(key)) for key in (
        "promotion_id", "staged_id", "prior_id", "recovery_target_id",
    )):
        result["reason"] = "invalid-journal-identifier"
        return result
    staged, prior = journal["staged_id"], journal["prior_id"]
    if staged == prior:
        result["reason"] = "indistinguishable-bundles"
        return result
    if journal["recovery_target_id"] != prior:
        result["reason"] = "recovery-target-conflict"
        return result
    if not isinstance(observations, dict) or any(
        not _identifier(observations.get(key))
        for key in ("current_id", "staged_id", "prior_id")
    ):
        result["reason"] = "invalid-observed-identifier"
        return result
    if observations["staged_id"] != staged or observations["prior_id"] != prior:
        result["reason"] = "retained-bundle-mismatch"
        return result
    current = observations["current_id"]
    state = journal["state"]
    if current not in (prior, staged):
        result["reason"] = "unrecognized-current"
    elif state == "prepared" and current == prior:
        result.update(action="recover", target_id=prior, reason="prior-still-current")
    elif state in ("prepared", "swapped") and current == staged:
        result.update(action="finalize", target_id=staged, reason="staged-now-current")
    elif state == "finalized" and current == staged:
        result.update(action="no-op", target_id=staged, reason="already-finalized")
    elif state == "recovered" and current == prior:
        result.update(action="no-op", target_id=prior, reason="already-recovered")
    else:
        result["reason"] = "state-observation-conflict"
    return result
