"""Tests for the pure machine-selection core (issue #2970, F3).

Loads scripts/operations/dispatch_select.py by path via importlib so the test
does not depend on package layout.
"""

import importlib.util
from pathlib import Path

_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "operations"
    / "dispatch_select.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "dispatch_select", _MODULE_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ds = _load_module()


# ── fixtures ────────────────────────────────────────────────────────────────

def _machines():
    return {
        "dev-primary": {
            "harness_profile": {"roles": ["dev", "research"]},
            "capabilities": {
                "agent_clis": ["claude", "gemini"],
                "languages": ["python3", "bash"],
                "tools": ["uv", "git", "gh"],
                "gpu": False,
            },
        },
        "gpu-box": {
            "harness_profile": {"roles": ["render"]},
            "capabilities": {
                "agent_clis": ["claude"],
                "languages": ["python3"],
                "tools": ["uv", "git"],
                "gpu": "rtx-4090",
            },
        },
        "bare-box": {
            "harness_profile": {"roles": ["idle"]},
            "capabilities": {
                "agent_clis": [],
                "languages": ["bash"],
                "tools": ["git"],
                "gpu": False,
            },
        },
    }


# ── eligible_machines ───────────────────────────────────────────────────────

def test_role_intersection_selects():
    machines = _machines()
    # Task roles intersect dev-primary (dev) but its requires would NOT match.
    task = {"roles": ["dev"], "requires": ["nonexistent-cap"]}
    eligible, reasons = ds.eligible_machines(task, machines)
    assert "dev-primary" in eligible
    r = next(x for x in reasons if x["machine"] == "dev-primary")
    assert r["role_match"] is True
    assert "dev" in r["role_hit"]


def test_capability_match_selects_when_roles_dont():
    machines = _machines()
    # No role overlap (task role 'analysis' matches nothing), but gpu-box has
    # all required caps including the gpu token.
    task = {"roles": ["analysis"], "requires": ["claude", "uv", "gpu"]}
    eligible, reasons = ds.eligible_machines(task, machines)
    assert "gpu-box" in eligible
    r = next(x for x in reasons if x["machine"] == "gpu-box")
    assert r["cap_match"] is True
    assert r["role_match"] is False
    # dev-primary has no gpu -> capability-short, no role overlap -> excluded.
    assert "dev-primary" not in eligible


def test_gpu_model_string_satisfies_named_cap():
    machines = _machines()
    task = {"roles": [], "requires": ["rtx-4090"]}
    eligible, _ = ds.eligible_machines(task, machines)
    assert eligible == ["gpu-box"]


def test_neither_role_nor_caps_excluded_with_reason():
    machines = _machines()
    # bare-box: role 'idle' not in task roles, and missing claude+uv.
    task = {"roles": ["dev"], "requires": ["claude", "uv"]}
    eligible, reasons = ds.eligible_machines(task, machines)
    assert "bare-box" not in eligible
    r = next(x for x in reasons if x["machine"] == "bare-box")
    assert r["included"] is False
    assert "role-excluded" in r["reason"]
    assert "capability-short" in r["reason"]
    assert "claude" in r["missing_caps"]
    assert "uv" in r["missing_caps"]


# ── probe_gate (fail-closed) ────────────────────────────────────────────────

def test_probe_gate_false_is_not_ready():
    def probe(_mid, cap):
        return cap != "uv"  # uv probes False

    gate = ds.probe_gate("m1", ["claude", "uv"], probe)
    assert gate["ready"] is False
    assert gate["failed"] == ["uv"]


def test_probe_gate_raise_is_caught_not_ready():
    def probe(_mid, cap):
        if cap == "license-solver":
            raise RuntimeError("ssh blew up / license server unreachable")
        return True

    gate = ds.probe_gate("m1", ["claude", "license-solver"], probe)
    assert gate["ready"] is False  # exception did NOT propagate
    assert gate["failed"] == ["license-solver"]


def test_probe_gate_all_pass_is_ready():
    gate = ds.probe_gate("m1", ["claude", "uv"], lambda _m, _c: True)
    assert gate == {"ready": True, "failed": []}


# ── select (integration) ────────────────────────────────────────────────────

def test_select_no_probe_ready_equals_eligible():
    machines = _machines()
    task = {"roles": ["dev"], "requires": ["claude", "uv"]}
    out = ds.select(task, machines, probe_fn=None)
    assert out["ready"] == out["eligible"]
    assert "dev-primary" in out["ready"]


def test_select_declared_but_probe_fails_is_eligible_not_ready():
    """KEY invariant: declared capability != proven capability."""
    machines = _machines()
    # dev-primary declares claude+uv (eligible), but its probe will fail uv.
    task = {"roles": ["dev"], "requires": ["claude", "uv"]}

    def probe(mid, cap):
        if mid == "dev-primary" and cap == "uv":
            return False  # declared in registry, cannot prove live
        return True

    out = ds.select(task, machines, probe_fn=probe)
    assert "dev-primary" in out["eligible"]
    assert "dev-primary" not in out["ready"]
    assert "dev-primary" in out["excluded"]
    assert "probe failed" in out["excluded"]["dev-primary"]
    assert "uv" in out["excluded"]["dev-primary"]


def test_select_excluded_carries_eligibility_reasons():
    machines = _machines()
    task = {"roles": ["dev"], "requires": ["claude", "uv"]}
    out = ds.select(task, machines, probe_fn=lambda _m, _c: True)
    # bare-box never eligible -> appears in excluded with eligibility reason.
    assert "bare-box" in out["excluded"]
    assert "bare-box" not in out["ready"]
