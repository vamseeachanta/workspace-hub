#!/usr/bin/env python3
"""A routing target must satisfy EVERY dimension the work needs, not just one.

## The mistake this corrects — mine, made earlier today

deckhand#579 found that solver/hydro work was routed to `licensed-win-1`, a host
that could not obtain an OrcaFlex licence. I fixed it by repointing those rules
to `licensed-win-2`, the only host carrying a dated licence attestation, and
shipped that in workspace-hub#3718.

The owner's correction, 2026-07-31: **"that host is not powerful enough."**

`licensed-win-2` is a workstation. `licensed-win-1` is the heavy node — 64
logical cores / 255.7 GB, the declared batch target for OrcaFlex runs of ~57
parallel sims (dm#1553). So the fix sent batch analysis to a box that cannot
carry it. I traded a licence failure for a capacity failure and called it fixed,
because I was only checking the dimension I had just been burned by.

## The general shape

Capability is not one property. A host must satisfy **all** of:

    licence   — can it obtain the licence the workload needs?
    capacity  — is it sized for the workload?

Checking one dimension and declaring victory is how the original defect happened
(the capability list was inherited from a retired machine and nobody re-checked)
and how my fix repeated it one axis over.

## And the second lesson: rerouting is not always the fix

When the *designated* host is blocked on a prerequisite, silently rerouting to a
lesser host hides the blockage — the work runs badly instead of visibly waiting.
The honest state is "blocked on a named, dated prerequisite", declared in the
config where a human reads it.

Hence `blocked_on`: a host may be a routing target with an unmet licence **only
if** the block is explicitly named. Absent that, an unverified licence is silent
and the guard fires.

Hermetic: parses the shipped YAML. No gh, no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_route_capacity.py
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = REPO_ROOT / ".claude" / "memory" / "kanban" / "routing-rules.yaml"

#: Workloads whose runs are batch-scale and need a heavy node, not a workstation.
HEAVY_DOMAINS = {"solver", "hydro"}
LICENSED_CAPABILITIES = {"orcaflex", "orcawave", "aqwa"}


@pytest.fixture(scope="module")
def cfg() -> dict:
    return yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def machines(cfg) -> dict:
    return cfg["machines"]


# --------------------------------------------------------------------------
# capacity is declared at all
# --------------------------------------------------------------------------


def test_every_licensed_host_declares_a_capacity(machines):
    """A licensed host with no declared capacity cannot be reasoned about.

    This is the field whose absence let me pick a workstation for batch work:
    there was nothing in the config that said it was one.
    """
    missing = [
        name for name, spec in machines.items()
        if set(spec.get("capabilities") or []) & LICENSED_CAPABILITIES
        and not spec.get("capacity")
    ]
    assert not missing, f"licensed hosts with no declared capacity: {missing}"


def test_capacity_values_are_from_a_closed_set(machines):
    allowed = {"heavy", "workstation", "dev", "compute", "aux"}
    bad = {n: s["capacity"] for n, s in machines.items()
           if s.get("capacity") and s["capacity"] not in allowed}
    assert not bad, f"unknown capacity values: {bad} (allowed: {sorted(allowed)})"


def test_exactly_one_heavy_licensed_host_is_declared(machines):
    """Sanity: the fleet has one batch-scale licensed node.

    If a second appears this test should be updated deliberately, not silently —
    two heavy hosts is a capacity-planning decision, not a config detail.
    """
    heavy = [n for n, s in machines.items()
             if s.get("capacity") == "heavy"
             and set(s.get("capabilities") or []) & LICENSED_CAPABILITIES]
    assert len(heavy) == 1, f"expected exactly one heavy licensed host, got {heavy}"


# --------------------------------------------------------------------------
# heavy work goes to a heavy host
# --------------------------------------------------------------------------


def test_heavy_workload_rules_target_a_heavy_host(cfg, machines):
    """The regression this file exists for.

    A rule for a batch-scale domain must not resolve to a workstation, however
    good that workstation's licence attestation is.
    """
    offenders = []
    for rule in cfg.get("rules") or []:
        match = rule.get("match") or {}
        fam = match.get("domain_family")
        if fam not in HEAVY_DOMAINS:
            continue
        target = (rule.get("assign") or {}).get("machine")
        cap = (machines.get(target) or {}).get("capacity")
        if cap != "heavy":
            offenders.append(f"domain_family:{fam} -> {target} (capacity={cap!r})")
    assert not offenders, (
        "batch-scale work routed to a non-heavy host: " + "; ".join(offenders)
    )


# --------------------------------------------------------------------------
# an unmet licence must be VISIBLE, not routed around
# --------------------------------------------------------------------------


def _is_attested(spec: dict) -> bool:
    return isinstance(spec.get("licence_verified"), dict)


def test_a_target_with_unverified_licence_must_declare_blocked_on(cfg, machines):
    """Routing to a host whose licence is pending is allowed — but only openly.

    The alternative, silently rerouting to a lesser host, hides the blockage:
    work runs badly instead of visibly waiting on a named prerequisite. That is
    exactly what workspace-hub#3718 did, and why this rule exists.
    """
    offenders = []
    for rule in cfg.get("rules") or []:
        target = (rule.get("assign") or {}).get("machine")
        spec = machines.get(target) or {}
        if not (set(spec.get("capabilities") or []) & LICENSED_CAPABILITIES):
            continue
        if _is_attested(spec):
            continue
        if not spec.get("blocked_on"):
            offenders.append(target)
    assert not offenders, (
        "routing target has an unverified licence and no `blocked_on` naming the "
        f"prerequisite — the block would be invisible: {offenders}"
    )


def test_blocked_on_names_an_issue(machines):
    """A prerequisite with no tracking reference cannot be chased."""
    for name, spec in machines.items():
        b = spec.get("blocked_on")
        if b:
            assert "#" in str(b), f"{name}.blocked_on must reference an issue: {b!r}"


def test_licence_verified_is_still_false_or_a_dated_attestation(machines):
    """Carried over from deckhand#579 — a bare `true` discards the evidence."""
    for name, spec in machines.items():
        if "licence_verified" not in spec:
            continue
        v = spec["licence_verified"]
        if v is False:
            continue
        assert isinstance(v, dict), f"{name}: licence_verified must be false or a dated dict"
        for field in ("at", "by", "how"):
            assert v.get(field), f"{name}: licence_verified.{field} required"


def test_the_checks_are_not_vacuous(cfg, machines):
    """If `rules` or `machines` were renamed, everything above would pass empty."""
    assert cfg.get("rules"), "no rules parsed"
    assert machines, "no machines parsed"
    assert any(
        (r.get("match") or {}).get("domain_family") in HEAVY_DOMAINS
        for r in cfg["rules"]
    ), "no heavy-domain rule present — the capacity check would inspect nothing"
