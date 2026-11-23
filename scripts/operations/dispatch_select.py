# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Pure machine-selection core for dispatched tasks (issue #2970, F3).

Decides WHICH machine(s) are eligible to run a dispatched task by combining
(a) the role model (F1 `harness_profile.roles` / F2 task `roles`) and (b) a live
capability probe.

These functions are PURE: no ssh / git / subprocess. The live probe is injected
as ``probe_fn`` so the core is unit-testable. The real caller wires ``probe_fn``
to an ssh + ``command -v`` / license check.

Key invariant: DECLARED capability != PROVEN capability. A machine may declare a
capability in the registry yet fail to prove it at dispatch time (binary missing,
license expired). Such a machine is *eligible* but not *ready*. The probe gate
FAILS CLOSED.
"""

from __future__ import annotations

# Registry capability sub-keys that hold a flat list of capability tokens.
# Mirrors scripts/operations/workstation-dispatch.sh flattening.
_LIST_CAP_KEYS = ("agent_clis", "tools", "languages")


def _machine_caps(machine: dict) -> set[str]:
    """Flatten a machine's declared capabilities into a token set.

    Includes every entry of capabilities.{agent_clis,tools,languages}; if
    capabilities.gpu is truthy, adds the token ``"gpu"`` (and, when gpu is a
    non-bool string such as a model name, that string too).
    """
    caps: set[str] = set()
    c = (machine or {}).get("capabilities", {}) or {}
    for key in _LIST_CAP_KEYS:
        for tok in c.get(key, []) or []:
            caps.add(tok)
    gpu = c.get("gpu")
    if gpu:
        caps.add("gpu")
        if gpu is not True and isinstance(gpu, str):
            caps.add(gpu)
    return caps


def _machine_roles(machine: dict) -> set[str]:
    """Roles declared under harness_profile.roles (F1); empty if absent."""
    hp = (machine or {}).get("harness_profile", {}) or {}
    return set(hp.get("roles", []) or [])


def eligible_machines(
    task: dict, machines: dict
) -> tuple[list[str], list[dict]]:
    """Decide which machines are eligible for ``task``.

    A machine is eligible if EITHER:
      * its harness_profile.roles intersects task['roles'], OR
      * it satisfies every capability in task['requires'] (each present in its
        flattened capabilities, where a truthy gpu yields the "gpu" token).

    A machine that is role-excluded AND capability-short is excluded.

    Returns ``(eligible_ids_sorted, reasons)`` where ``reasons`` is one dict per
    machine explaining the include/exclude decision.
    """
    task = task or {}
    task_roles = set(task.get("roles", []) or [])
    required = list(task.get("requires", []) or [])

    eligible: list[str] = []
    reasons: list[dict] = []

    for mid in sorted((machines or {}).keys()):
        machine = machines[mid] or {}
        mroles = _machine_roles(machine)
        mcaps = _machine_caps(machine)

        role_hit = sorted(task_roles & mroles)
        missing_caps = [cap for cap in required if cap not in mcaps]
        caps_ok = len(missing_caps) == 0

        # Role-only match is meaningful only when the task declares roles;
        # capability match requires that the task declares requirements.
        role_match = bool(task_roles) and bool(role_hit)
        cap_match = bool(required) and caps_ok

        included = role_match or cap_match

        if included:
            eligible.append(mid)
            if role_match and cap_match:
                why = (
                    f"role match {role_hit} and all requires satisfied"
                )
            elif role_match:
                why = f"role match {role_hit}"
            else:
                why = "all requires satisfied"
        else:
            if not task_roles and not required:
                why = "task declares no roles and no requires"
            elif missing_caps and not role_hit:
                why = (
                    f"role-excluded (machine roles {sorted(mroles)} "
                    f"vs task roles {sorted(task_roles)}) and "
                    f"capability-short (missing {missing_caps})"
                )
            elif missing_caps:
                why = f"capability-short (missing {missing_caps})"
            else:
                why = (
                    f"role-excluded (machine roles {sorted(mroles)} "
                    f"vs task roles {sorted(task_roles)})"
                )

        reasons.append(
            {
                "machine": mid,
                "included": included,
                "role_match": role_match,
                "cap_match": cap_match,
                "role_hit": role_hit,
                "missing_caps": missing_caps,
                "reason": why,
            }
        )

    return eligible, reasons


def probe_gate(
    machine_id: str, required_caps: list[str], probe_fn
) -> dict:
    """Live-probe each required capability on a machine. FAILS CLOSED.

    Calls ``probe_fn(machine_id, cap) -> bool`` for each required capability. A
    capability counts as proven only if the probe returns truthy. If the probe
    returns falsy OR RAISES, the capability is treated as failed (the exception
    is caught, not propagated).

    Returns ``{"ready": bool, "failed": [caps that did not prove]}``.
    ``ready`` is True only when every required cap proved.
    """
    failed: list[str] = []
    for cap in required_caps or []:
        try:
            ok = bool(probe_fn(machine_id, cap))
        except Exception:
            ok = False  # fail closed: cannot prove -> not ready
        if not ok:
            failed.append(cap)
    return {"ready": len(failed) == 0, "failed": failed}


def select(task: dict, machines: dict, probe_fn=None) -> dict:
    """Compose eligibility + live probe into a dispatch decision.

    1. Compute eligible machines via :func:`eligible_machines`.
    2. If ``probe_fn`` is given, run :func:`probe_gate` against each eligible
       machine's required capabilities; only machines whose probe passes land in
       ``ready``. If ``probe_fn`` is None, the probe is deferred to the
       caller/JIT and ``ready == eligible``.

    Returns ``{"eligible": [...], "ready": [...], "excluded": {id: reason}}``.
    """
    task = task or {}
    required = list(task.get("requires", []) or [])

    eligible, reasons = eligible_machines(task, machines)

    excluded = {
        r["machine"]: r["reason"] for r in reasons if not r["included"]
    }

    if probe_fn is None:
        return {
            "eligible": list(eligible),
            "ready": list(eligible),
            "excluded": excluded,
        }

    ready: list[str] = []
    for mid in eligible:
        gate = probe_gate(mid, required, probe_fn)
        if gate["ready"]:
            ready.append(mid)
        else:
            failed = gate["failed"]
            excluded[mid] = (
                f"eligible but probe failed (unproven caps {failed})"
            )

    return {
        "eligible": list(eligible),
        "ready": ready,
        "excluded": excluded,
    }
