#!/usr/bin/env python3
"""The capability map must not claim a capability a host cannot exercise.

deckhand#579. This is the defect `route.py`'s write gate warns about by name:
`routing-rules.yaml` routes solver and hydro work to `licensed-win-1`, a host
that **cannot obtain an OrcaFlex licence**.

## The evidence

Verified 2026-07-30 on that host via `OrcFxAPI.Model()`:

    DLLError, Error code: 25
      FlexNet: OrcaFlex could not access the FlexNet service. Error 21
      HASP:    No licence files could be found

Root cause: no Sentinel LDK runtime. Port 1947 is not listening, `hasplms.exe`
is absent, no `hasplm.ini`, no Sentinel/HASP/FlexNet service registered. A
network soft dongle cannot be consumed without the client-side runtime.

## Why the claim exists at all

`licensed-win-1` used to denote a *different, now-retired* machine that did hold
licences. When the label was repointed to the current host, the capability list
came along unchanged. **The name moved; the capabilities did not.** Nothing
checked, because nothing could — no test asserted that a routing target can do
the work routed to it.

## Blast radius, measured 2026-07-30

    domain:solver  →  80 open digitalmodel issues
    domain:hydro   →  97 open digitalmodel issues
                      ───
                      177 routed to a host that provably cannot execute them

## Scope of these tests

This asserts the *internal consistency* of the routing config: no rule may
target a machine whose licence status is unproven. It deliberately does not
probe a live host — a unit test that needs a Windows box and a dongle is a test
that gets skipped and then deleted.

The registry field is therefore an explicit, dated, human-attested claim
(`licence_verified`), not an inference. An attestation that goes stale is
visible; an inference that goes stale is not.

Run: uv run --with pyyaml pytest tests/dispatch/test_routing_rules_capability_truth.py
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = REPO_ROOT / ".claude" / "memory" / "kanban" / "routing-rules.yaml"

#: Capabilities that require a licence a host must be *proven* to obtain.
#: Routing work to a host that cannot get one is not a degraded run, it is a
#: guaranteed failure — the run cannot start.
LICENSED_CAPABILITIES = {"orcaflex", "orcawave", "aqwa"}


@pytest.fixture(scope="module")
def rules() -> dict:
    return yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def machines(rules) -> dict:
    return rules["machines"]


# --------------------------------------------------------------------------
# the attestation field itself
# --------------------------------------------------------------------------


def test_every_licensed_capability_claim_carries_an_attestation(machines):
    """A licensed capability without `licence_verified` is an unbacked claim.

    This is the assertion that would have caught #579 the day the label was
    repointed: the capability list survived a machine swap because nothing
    required it to be re-attested.
    """
    unbacked = []
    for name, spec in machines.items():
        claimed = set(spec.get("capabilities") or []) & LICENSED_CAPABILITIES
        if claimed and "licence_verified" not in spec:
            unbacked.append(f"{name} claims {sorted(claimed)} with no licence_verified")
    assert not unbacked, "unbacked licensed-capability claims: " + "; ".join(unbacked)


def test_licence_verified_is_per_solver_and_dated(machines):
    """Licence is PER SOLVER, not per host (fleet handover 2026-07-31).

    A bare `true` discards the evidence; a host-level flag discards WHICH solver.
    AQWA is licensed and idle on the heavy node while OrcaFlex is unavailable
    there — one boolean cannot say that. Shape:
    `licence_verified: {<capability>: {at, by, how}}`.
    """
    for name, spec in machines.items():
        v = spec.get("licence_verified")
        if v is False or v is None:
            continue
        assert isinstance(v, dict), f"{name}: licence_verified must be false or a per-solver map"
        for cap, att in v.items():
            assert isinstance(att, dict), f"{name}.licence_verified.{cap} must be a dated attestation"
            for field in ("at", "by", "how"):
                assert att.get(field), f"{name}.licence_verified.{cap}.{field} is required"


# --------------------------------------------------------------------------
# the rules must not target an unproven host
# --------------------------------------------------------------------------


def _licence_proven(spec: dict) -> bool:
    """At least one licensed capability on this host carries a dated attestation.

    Per-solver since 2026-07-31: `licence_verified` maps capability -> {at,by,how}.
    A host with AQWA attested and OrcaFlex blocked counts as proven HERE — the
    per-capability question ("can this host run THIS solver?") is answered by
    `licence_verified[cap]` at dispatch time, not by this coarse check.
    """
    verified = spec.get("licence_verified")
    return isinstance(verified, dict) and bool(
        set(verified) & LICENSED_CAPABILITIES
    )


def test_no_rule_routes_licensed_work_to_an_unproven_host(rules, machines):
    """The operative check.

    `capabilities:` is *documentation* — `route.py` never reads it (confirmed by
    `git grep capabilit -- scripts/dispatch/route.py`: every hit is a comment or
    a docstring). The `rules:` list is what actually assigns. So correcting only
    the capability list would leave the defect fully intact while looking fixed —
    the same declared-but-unwired shape as an uncalled safety gate.

    UPDATED 2026-07-31 after the owner's correction "that host is not powerful
    enough". The original form of this test demanded a *proven licence* and
    nothing else, so it accepted repointing batch work to a workstation — I
    satisfied it by trading a licence failure for a capacity failure.

    An unproven licence is now acceptable **only when `blocked_on` names the
    prerequisite**, because silently rerouting to a lesser host hides the
    blockage. Capacity is asserted separately in test_route_capacity.py.
    """
    offenders = []
    for rule in rules.get("rules") or []:
        target = (rule.get("assign") or {}).get("machine")
        if not target:
            continue
        spec = machines.get(target)
        if spec is None:
            offenders.append(f"rule -> unknown machine {target!r}")
            continue
        needs_licence = set(spec.get("capabilities") or []) & LICENSED_CAPABILITIES
        if needs_licence and not _licence_proven(spec) and not spec.get("blocked_on"):
            offenders.append(
                f"rule {rule.get('match')} -> {target} "
                f"(claims {sorted(needs_licence)}, licence unproven AND no blocked_on)"
            )
    assert not offenders, (
        "rules route licensed work to a host whose licence is neither proven nor "
        "openly blocked: " + "; ".join(offenders)
    )


def test_every_rule_targets_a_machine_in_the_roster(rules, machines):
    """A typo'd target silently produces a label nothing recognises."""
    for rule in rules.get("rules") or []:
        target = (rule.get("assign") or {}).get("machine")
        if target:
            assert target in machines, f"rule targets {target!r}, absent from the roster"


# --------------------------------------------------------------------------
# guard the guard — these must not be satisfiable by documentation
# --------------------------------------------------------------------------


def test_the_check_reads_rules_not_prose(rules):
    """Sanity: the config actually parses into the shape these tests assume.

    A YAML edit that renamed `rules:` would make every assertion above vacuous —
    they would iterate an empty list and pass. Absence of findings must not be
    reachable by absence of input.
    """
    assert isinstance(rules.get("rules"), list) and rules["rules"], "no rules parsed"
    assert isinstance(rules.get("machines"), dict) and rules["machines"], "no machines parsed"
    targets = [(r.get("assign") or {}).get("machine") for r in rules["rules"]]
    assert any(targets), "no rule assigns a machine — the checks above would be vacuous"


def test_wip_caps_do_not_reference_a_machine_outside_the_roster(rules, machines):
    """`wip_caps.per_machine` keys must resolve, or a cap silently applies to nothing."""
    caps = (rules.get("wip_caps") or {}).get("per_machine") or {}
    unknown = [k for k in caps if k != "default" and k not in machines]
    assert not unknown, f"wip_caps reference machines absent from the roster: {unknown}"
