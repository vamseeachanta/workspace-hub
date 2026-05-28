"""TDD tests for #2801 build-equality-matrix.py — the machine-equality verdict engine.

Targets a functional API (verdict_for / load_roster / coerce_to_mib / cold_verdict /
uniform_verdict) so the verdict state machine is unit-testable independent of HTML
rendering. Covers the full precedence and both grading families per the approved plan.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "readiness" / "build-equality-matrix.py"

spec = importlib.util.spec_from_file_location("build_equality_matrix", MODULE_PATH)
assert spec is not None and spec.loader is not None
bem = importlib.util.module_from_spec(spec)
sys.modules["build_equality_matrix"] = bem  # register BEFORE exec (kebab-case import safety)
spec.loader.exec_module(bem)


# ── fixtures ────────────────────────────────────────────────────────────────
TIER1 = ["assetutilities", "digitalmodel", "worldenergydata", "assethold"]


def _config(machines: dict) -> dict:
    return {"workstations": machines}


def _report(machine: str, **dims) -> dict:
    base = {
        "machine": machine,
        "os": "linux",
        "status": "active",
        "dimensions": {
            "compute": {"static": {"cores": 32, "ram_total_mib": 31744, "gpu_model": "GTX 750 Ti"},
                        "headroom": {"ram_avail_mib": 23000, "disk_avail_gb": 881}},
            "data_access": [{"repo": r, "mode": "sibling"} for r in TIER1],
            "harness": {"providers": {"claude": "present", "codex": "present"},
                        "readiness_overall": "fail", "python_cmd": "uv-run"},
            "skills": {"repo_skill_count": 407},
            "kanban": {"dispatch_queues": "dev-primary,multi"},
            "memory": {"hermes_home": "present", "context_md_mtime": "2026-05-26T02:05:23"},
            "behavior": {"enums": {"b1": "deny", "b2": "ok", "b3": "html", "b4": "pass"},
                         "hashes": {"b5": "abc123"}},
            "scheduler": {"has_repo_sync": True, "has_parity_review": True, "job_count": 38},
        },
    }
    for k, v in dims.items():
        base["dimensions"][k] = v
    return base


# ── roster from config (M1) ─────────────────────────────────────────────────
def test_matrix_roster_from_config():
    cfg = _config({"dev-primary": {}, "dev-secondary": {}, "licensed-win-1": {}})
    roster = bem.load_roster(cfg)
    assert set(roster) == {"dev-primary", "dev-secondary", "licensed-win-1"}


# ── unit coercion (DG2/DC3/D2-2) ────────────────────────────────────────────
@pytest.mark.parametrize("raw,expected_mib", [("31Gi", 31744), ("512Mi", 512), (16384, 16384)])
def test_coerce_to_mib_units(raw, expected_mib):
    assert bem.coerce_to_mib(raw) == expected_mib


def test_coerce_to_mib_parse_failure_raises():
    with pytest.raises(ValueError):
        bem.coerce_to_mib("garbage")


def test_coerce_to_mib_negative_raises():
    with pytest.raises(ValueError):
        bem.coerce_to_mib(-1)


def test_matrix_malformed_report_is_missing_evidence():
    # CC4: a parse-error / non-dict report must not flow into verdict logic
    roster = {"dev-primary": {"status": "active"}}
    for bad in ({"_error": "boom"}, "not-a-dict", {"no": "dimensions"}):
        assert bem.verdict_for("compute", "dev-primary", {"dev-primary": bad}, {}, roster, TIER1) == "MISSING-EVIDENCE"


# ── cold-dim conformance (D2) ───────────────────────────────────────────────
def _baseline(cores_min=16, ram_gib_min=16, required=None, gpu_required=False):
    return {"compute_floor": {"cores_min": cores_min, "ram_gib_min": ram_gib_min,
                              "gpu_required": gpu_required},
            "required_data_access": required if required is not None else TIER1}


def test_matrix_compute_conforms_above_floor():
    v = bem.cold_verdict("compute", _report("dev-primary"), _baseline(), TIER1)
    assert v == "CONFORMS"  # 32c/31GiB >= 16/16


def test_matrix_compute_below_floor_cores():
    rep = _report("dev-primary", compute={"static": {"cores": 8, "ram_total_mib": 31744, "gpu_model": "x"},
                                           "headroom": {}})
    assert bem.cold_verdict("compute", rep, _baseline(), TIER1) == "BELOW-BASELINE"


def test_matrix_compute_floor_per_field_ram():
    # cores OK but RAM below floor — ALL fields graded, not just cores (DG2/DC3)
    rep = _report("dev-primary", compute={"static": {"cores": 32, "ram_total_mib": 8192, "gpu_model": "x"},
                                           "headroom": {}})
    assert bem.cold_verdict("compute", rep, _baseline(ram_gib_min=16), TIER1) == "BELOW-BASELINE"


def test_matrix_compute_unit_normalized_mi_never_passes_gi():
    # 512 MiB must NOT pass a 16 GiB floor (unit-aware)
    rep = _report("dev-primary", compute={"static": {"cores": 32, "ram_total_mib": 512, "gpu_model": "x"},
                                           "headroom": {}})
    assert bem.cold_verdict("compute", rep, _baseline(ram_gib_min=16), TIER1) == "BELOW-BASELINE"


def test_matrix_compute_gpu_required_present_conforms():
    assert bem.cold_verdict("compute", _report("dev-primary"), _baseline(gpu_required=True), TIER1) == "CONFORMS"


def test_matrix_compute_gpu_required_absent_below():
    rep = _report("dev-primary", compute={"static": {"cores": 32, "ram_total_mib": 31744, "gpu_model": "none"},
                                           "headroom": {}})
    assert bem.cold_verdict("compute", rep, _baseline(gpu_required=True), TIER1) == "BELOW-BASELINE"


def test_matrix_compute_unknown_is_missing_evidence():
    rep = _report("dev-primary", compute={"static": {"cores": "unknown", "ram_total_mib": 31744,
                                                      "gpu_model": "x"}, "headroom": {}})
    assert bem.cold_verdict("compute", rep, _baseline(), TIER1) == "MISSING-EVIDENCE"


def test_matrix_data_access_required_subset_bare_names():
    # actual emits {repo, mode}; baseline names bare repos — subset on bare names (DG3/MC2)
    assert bem.cold_verdict("data_access", _report("dev-primary"),
                            _baseline(required=["digitalmodel"]), TIER1) == "CONFORMS"


def test_matrix_data_access_missing_required():
    rep = _report("dev-primary",
                  data_access=[{"repo": r, "mode": ("absent" if r == "digitalmodel" else "sibling")}
                               for r in TIER1])
    assert bem.cold_verdict("data_access", rep, _baseline(required=["digitalmodel"]), TIER1) == "BELOW-BASELINE"


def test_matrix_missing_baseline_fail_closed():
    assert bem.cold_verdict("compute", _report("dev-primary"), None, TIER1) == "MISSING-BASELINE"


def test_matrix_baseline_unprobed_repo_is_config_error():
    # baseline requires a repo the collector never probes → config error, not BELOW-BASELINE (D2-1)
    assert bem.cold_verdict("data_access", _report("dev-primary"),
                            _baseline(required=["foo-repo"]), TIER1) == "MISSING-BASELINE"


# ── solvers cold-dim conformance (#2849, STRICT) ────────────────────────────
def _solvers(orcaflex="absent", orcawave="absent", aqwa="absent", ansys="absent"):
    return [{"name": "orcaflex", "status": orcaflex, "evidence": "absent"},
            {"name": "orcawave", "status": orcawave, "evidence": "absent"},
            {"name": "aqwa", "status": aqwa, "evidence": "absent"},
            {"name": "ansys", "status": ansys, "evidence": "absent"}]


def _solver_baseline(**want):
    base = {"orcaflex": "absent", "orcawave": "absent", "aqwa": "absent", "ansys": "absent"}
    base.update(want)
    return {"solvers_baseline": base}


def test_solvers_is_cold_dim():
    assert "solvers" in bem.COLD_DIMS


def test_solvers_conforms_dev_primary_all_absent():
    # dev-primary: declared all-absent + detected all-absent → CONFORMS (expected divergence)
    rep = _report("dev-primary", solvers=_solvers())
    assert bem.cold_verdict("solvers", rep, _solver_baseline(), TIER1) == "CONFORMS"


def test_solvers_conforms_licensed_baseline_met():
    rep = _report("licensed-win-1", solvers=_solvers(
        orcaflex="licensed", orcawave="licensed", aqwa="licensed", ansys="licensed"))
    bl = _solver_baseline(orcaflex="licensed", orcawave="licensed", aqwa="licensed", ansys="licensed")
    assert bem.cold_verdict("solvers", rep, bl, TIER1) == "CONFORMS"


def test_solvers_below_baseline_when_licensed_missing():
    # licensed baseline but detected absent → BELOW-BASELINE
    rep = _report("licensed-win-1", solvers=_solvers(orcaflex="absent"))
    bl = _solver_baseline(orcaflex="licensed")
    assert bem.cold_verdict("solvers", rep, bl, TIER1) == "BELOW-BASELINE"


def test_solvers_strict_present_does_not_satisfy_licensed():
    # STRICT (decision 1): an install-only `present` must FAIL a `licensed` baseline.
    rep = _report("licensed-win-1", solvers=_solvers(orcaflex="present"))
    bl = _solver_baseline(orcaflex="licensed")
    assert bem.cold_verdict("solvers", rep, bl, TIER1) == "BELOW-BASELINE"


def test_solvers_below_baseline_when_unexpected_extra():
    # declared absent but detected licensed (probe found one we didn't declare) → BELOW-BASELINE
    rep = _report("dev-primary", solvers=_solvers(orcaflex="licensed"))
    assert bem.cold_verdict("solvers", rep, _solver_baseline(), TIER1) == "BELOW-BASELINE"


def test_solvers_missing_baseline_when_unset():
    # a machine with compute_floor but no solvers_baseline → MISSING-BASELINE (fail-closed)
    rep = _report("dev-primary", solvers=_solvers())
    assert bem.cold_verdict("solvers", rep, {"compute_floor": {"cores_min": 8}}, TIER1) == "MISSING-BASELINE"


def test_solvers_missing_evidence_when_unknown_against_licensed():
    # licensed baseline but detected `unknown` (probe couldn't run) → MISSING-EVIDENCE, not fail
    rep = _report("licensed-win-1", solvers=_solvers(orcaflex="unknown"))
    bl = _solver_baseline(orcaflex="licensed")
    assert bem.cold_verdict("solvers", rep, bl, TIER1) == "MISSING-EVIDENCE"


def test_solvers_absent_baseline_unknown_is_missing_evidence():
    # declared absent + detected unknown → MISSING-EVIDENCE (unknown is never evidence,
    # for ANY baseline — a missing probe must not masquerade as CONFORMS). #2849 Codex r1 #1.
    rep = _report("dev-primary", solvers=_solvers(orcaflex="unknown"))
    assert bem.cold_verdict("solvers", rep, _solver_baseline(), TIER1) == "MISSING-EVIDENCE"


def test_solvers_legacy_v2_absent_baseline_missing_evidence():
    # a v2 report (no solvers block) against a dev absent-baseline → MISSING-EVIDENCE,
    # NOT CONFORMS (the whole solvers cell is unknown). #2849 Codex r1 #1.
    rep = _report("dev-primary")  # base fixture has no solvers key
    assert bem.cold_verdict("solvers", rep, _solver_baseline(), TIER1) == "MISSING-EVIDENCE"


def test_solvers_concrete_miss_dominates_unknown():
    # one concrete BELOW miss + one unknown → BELOW-BASELINE wins (hard fail dominates)
    rep = _report("licensed-win-1", solvers=_solvers(orcaflex="absent", orcawave="unknown"))
    bl = _solver_baseline(orcaflex="licensed", orcawave="licensed")
    assert bem.cold_verdict("solvers", rep, bl, TIER1) == "BELOW-BASELINE"


def test_solvers_legacy_v2_report_missing_evidence():
    # a v2 report (no solvers block) against a licensed baseline → MISSING-EVIDENCE, not a crash
    rep = _report("licensed-win-1")  # base fixture has no solvers key
    bl = _solver_baseline(orcaflex="licensed", orcawave="licensed", aqwa="licensed", ansys="licensed")
    assert bem.cold_verdict("solvers", rep, bl, TIER1) == "MISSING-EVIDENCE"


def test_solvers_in_display_dims_after_data_access():
    assert "solvers" in bem.DISPLAY_DIMS
    assert bem.DISPLAY_DIMS.index("solvers") == bem.DISPLAY_DIMS.index("data_access") + 1


def test_solvers_renders_row_in_html(tmp_path, monkeypatch):
    # End-to-end: matrix HTML includes a solvers row. Drive main() against a tmp state dir.
    state = tmp_path / "state"
    state.mkdir()
    reports_dir = tmp_path / "reports"
    cfg = tmp_path / "harness-config.yaml"
    cfg.write_text(yaml.safe_dump({"workstations": {
        "dev-primary": {"compute_floor": {"cores_min": 8}, "required_data_access": ["digitalmodel"],
                        "solvers_baseline": {"orcaflex": "absent", "orcawave": "absent",
                                             "aqwa": "absent", "ansys": "absent"}}},
        "tier1_repos": TIER1}))
    rep = _report("dev-primary", data_access=[{"repo": "digitalmodel", "mode": "sibling"}],
                  solvers=_solvers())
    (state / "equality-dev-primary.yaml").write_text(yaml.safe_dump(rep))
    monkeypatch.setattr(bem, "STATE", state)
    monkeypatch.setattr(bem, "REPORTS", reports_dir)
    monkeypatch.setattr(bem, "CONFIG", cfg)
    bem.main()
    html = next(reports_dir.glob("*-machine-equality-matrix.html")).read_text()
    assert "<th>solvers</th>" in html
    assert "conforms" in html  # the dev-primary all-absent cell


# ── uniform-dim equality + ties (C1) ────────────────────────────────────────
def test_matrix_pending_under_two():
    assert bem.uniform_verdict("skills", ["407"]) == "PENDING"


def test_matrix_two_equal():
    assert bem.uniform_verdict("skills", ["407", "407"]) == "EQUAL"


def test_matrix_two_disagree_no_majority():
    assert bem.uniform_verdict("skills", ["407", "401"]) == "NO-MAJORITY"


def test_matrix_four_split_tie():
    assert bem.uniform_verdict("skills", ["a", "a", "b", "b"]) == "NO-MAJORITY"


def test_matrix_diverges_on_minority():
    assert bem.uniform_verdict("skills", ["407", "407", "401"]) == "DIVERGES"  # for the 401 cell


def test_matrix_expected_diff_python_only():
    assert bem.uniform_verdict("python_cmd", ["uv-run", "python"]) == "EXPECTED-DIFF"


# ── precedence orchestrator (C3) ────────────────────────────────────────────
def test_verdict_unreachable_over_missing():
    roster = {"home-win": {"status": "unreachable"}}
    assert bem.verdict_for("compute", "home-win", {}, {}, roster, TIER1) == "UNREACHABLE"


def test_verdict_active_no_report_missing_evidence():
    roster = {"dev-secondary": {"status": "active"}}
    assert bem.verdict_for("compute", "dev-secondary", {}, {}, roster, TIER1) == "MISSING-EVIDENCE"


def test_harness_config_real_roster_and_baselines():
    # Loads the REAL harness-config.yaml: home-win/macbook unreachable; active machines have baselines.
    cfg = yaml.safe_load((REPO_ROOT / "scripts" / "readiness" / "harness-config.yaml").read_text())
    roster = bem.load_roster(cfg)
    assert roster["home-win"]["status"] == "unreachable"
    assert roster["macbook-portable"]["status"] == "unreachable"
    assert roster["dev-primary"]["status"] == "active"
    baselines = bem.load_baselines(cfg)
    for m in ("dev-primary", "dev-secondary", "licensed-win-1", "licensed-win-2"):
        assert "compute_floor" in baselines[m] and "required_data_access" in baselines[m]
        # baseline must only name repos the collector actually probes (D2-1)
        assert set(baselines[m]["required_data_access"]) <= set(TIER1)
        # #2849: every active machine declares a solvers baseline over the 4 named solvers
        sb = baselines[m]["solvers_baseline"]
        assert set(sb) == {"orcaflex", "orcawave", "aqwa", "ansys"}
        assert all(v in ("licensed", "present", "absent") for v in sb.values())


def test_wiring_single_source_schedule():
    # DC5: the schedule lives in the ONE canonical source (schedule-tasks.yaml), weekly,
    # all 4 active machines, invoking both collector and matrix builder.
    tasks = yaml.safe_load(
        (REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml").read_text())["tasks"]
    eq = next(t for t in tasks if t["id"] == "equality-report")
    assert eq["schedule"].split()[-1] == "1"            # weekly, Monday
    assert "collect-equality.sh" in eq["command"]
    assert "build-equality-matrix.py" in eq["command"]
    for m in ("dev-primary", "dev-secondary", "licensed-win-1", "licensed-win-2"):
        assert m in eq["machines"]


def test_verdict_behavior_is_uniform_not_expected_diff():
    # behavior probes compared across machines; identical → EQUAL (M2: never EXPECTED-DIFF)
    roster = {"dev-primary": {"status": "active"}, "dev-secondary": {"status": "active"}}
    reports = {"dev-primary": _report("dev-primary"), "dev-secondary": _report("dev-secondary")}
    assert bem.verdict_for("behavior", "dev-primary", reports, {}, roster, TIER1) == "EQUAL"
