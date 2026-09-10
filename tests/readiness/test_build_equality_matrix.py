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

# A "fresh" provenance block (#2851): clean tree, current with main, recent origin ref.
# is_stale() is fail-closed, so the default fixture MUST be fresh — otherwise every
# verdict_for() test would short-circuit to STALE-CHECKOUT. Staleness is opt-in per test.
FRESH_PROV = {"checkout_sha": "abc1234", "dirty": False, "behind_main": 0, "ahead_main": 0,
              "origin_ref_age_h": 1}


def _config(machines: dict) -> dict:
    return {"workstations": machines}


def _report(machine: str, provenance: dict | None = None, **dims) -> dict:
    base = {
        "machine": machine,
        "os": "linux",
        "status": "active",
        "provenance": dict(FRESH_PROV) if provenance is None else provenance,
        "dimensions": {
            "compute": {"static": {"cores": 32, "ram_total_mib": 31744, "gpu_model": "GTX 750 Ti"},
                        "headroom": {"ram_avail_mib": 23000, "disk_avail_gb": 881}},
            "data_access": [{"repo": r, "mode": "sibling"} for r in TIER1],
            "harness": {"providers": {"claude": "present", "codex": "present"},
                        "readiness_overall": "fail", "python_cmd": "uv-run"},
            "skills": {"repo_skill_count": 407},
            "kanban": {"dispatch_queues": "dev-primary,multi"},
            "memory": {"hermes_home": "present", "context_md_mtime": "2026-05-26T02:05:23"},
            "provider_harness": {
                "schema_version": 1,
                "providers": {
                    "claude": {
                        "present": True, "installed": True,
                        "memory:read": {"status": "present", "reason": "claude_memory_context_found"},
                        "skills:invoke": {"status": "present", "reason": "repo_skill_tree_found"},
                        "workflow:gates": {"status": "present", "reason": "hard_gates_runtime_found"},
                    },
                    "codex": {
                        "present": True, "installed": True,
                        "memory:read": {"status": "present", "reason": "codex_memory_runtime_found"},
                        "skills:invoke": {"status": "present", "reason": "codex_skill_adapter_found"},
                        "workflow:gates": {"status": "present", "reason": "codex_agents_runtime_active"},
                    },
                    "hermes": {
                        "present": True, "installed": True,
                        "memory:read": {"status": "present", "reason": "hermes_memory_store_found"},
                        "skills:invoke": {"status": "expected_divergence",
                                          "reason": "external_skill_dirs_configured"},
                        "workflow:gates": {"status": "present", "reason": "hermes_soul_runtime_active"},
                    },
                    "gemini": {
                        "present": True, "installed": True,
                        "memory:read": {"status": "present", "reason": "gemini_memory_runtime_found"},
                        "skills:invoke": {"status": "expected_divergence",
                                          "reason": "gemini_skill_dispatch_unsupported"},
                        "workflow:gates": {"status": "present", "reason": "gemini_soul_runtime_gates_found"},
                    },
                },
            },
            "behavior": {"enums": {"b1": "deny", "b2": "ok", "b3": "html", "b4": "pass"},
                         "hashes": {"b5": "abc123"}},
            "scheduler": {"has_repo_sync": True, "has_parity_review": True, "job_count": 38},
        },
    }
    for k, v in dims.items():
        base["dimensions"][k] = v
    return base


def _provider_report(machine: str, provider_overrides: dict | None = None, **kwargs) -> dict:
    rep = _report(machine, **kwargs)
    rep["schema_version"] = 4
    if provider_overrides:
        for provider, fields in provider_overrides.items():
            rep["dimensions"]["provider_harness"]["providers"][provider].update(fields)
    return rep


# ── roster from config (M1) ─────────────────────────────────────────────────
def test_matrix_roster_from_config():
    cfg = _config({"dev-primary": {}, "dev-secondary": {}, "ace-win-1": {}})
    roster = bem.load_roster(cfg)
    assert set(roster) == {"dev-primary", "dev-secondary", "ace-win-1"}


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
    rep = _report("ace-win-1", solvers=_solvers(
        orcaflex="licensed", orcawave="licensed", aqwa="licensed", ansys="licensed"))
    bl = _solver_baseline(orcaflex="licensed", orcawave="licensed", aqwa="licensed", ansys="licensed")
    assert bem.cold_verdict("solvers", rep, bl, TIER1) == "CONFORMS"


def test_solvers_below_baseline_when_licensed_missing():
    # licensed baseline but detected absent → BELOW-BASELINE
    rep = _report("ace-win-1", solvers=_solvers(orcaflex="absent"))
    bl = _solver_baseline(orcaflex="licensed")
    assert bem.cold_verdict("solvers", rep, bl, TIER1) == "BELOW-BASELINE"


def test_solvers_strict_present_does_not_satisfy_licensed():
    # STRICT (decision 1): an install-only `present` must FAIL a `licensed` baseline.
    rep = _report("ace-win-1", solvers=_solvers(orcaflex="present"))
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
    rep = _report("ace-win-1", solvers=_solvers(orcaflex="unknown"))
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
    rep = _report("ace-win-1", solvers=_solvers(orcaflex="absent", orcawave="unknown"))
    bl = _solver_baseline(orcaflex="licensed", orcawave="licensed")
    assert bem.cold_verdict("solvers", rep, bl, TIER1) == "BELOW-BASELINE"


def test_solvers_legacy_v2_report_missing_evidence():
    # a v2 report (no solvers block) against a licensed baseline → MISSING-EVIDENCE, not a crash
    rep = _report("ace-win-1")  # base fixture has no solvers key
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


def test_provider_rows_are_in_display_dims():
    assert "harness:claude:memory:read" in bem.DISPLAY_DIMS
    assert "harness:codex:skills:invoke" in bem.DISPLAY_DIMS
    assert "harness:hermes:workflow:gates" in bem.DISPLAY_DIMS


def test_target_provider_parity_is_reference_based_on_claude_same_machine():
    roster = {"dev-primary": {"status": "active"}}
    codex_absent = {
        "codex": {"memory:read": {"status": "absent", "reason": "runtime_missing"}}
    }
    reports = {"dev-primary": _provider_report("dev-primary", codex_absent)}
    assert bem.verdict_for("harness:codex:memory:read", "dev-primary", reports, {},
                           roster, TIER1) == "DIVERGES"

    claude_absent = {
        "claude": {"memory:read": {"status": "absent", "reason": "claude_memory_missing"}},
        "codex": {"memory:read": {"status": "absent", "reason": "runtime_missing"}},
    }
    reports = {"dev-primary": _provider_report("dev-primary", claude_absent)}
    assert bem.verdict_for("harness:codex:memory:read", "dev-primary", reports, {},
                           roster, TIER1) == "MISSING-EVIDENCE"


def test_gemini_renders_and_skills_is_expected_divergence():
    # #3206: gemini renders in the matrix; its dispatch-unsupported skills cap is
    # EXPECTED-DIVERGENCE (a non-failure), not DIVERGES.
    roster = {"dev-primary": {"status": "active"}}
    reports = {"dev-primary": _provider_report("dev-primary")}
    assert "harness:gemini:memory:read" in bem.DISPLAY_DIMS
    assert bem.verdict_for("harness:gemini:memory:read", "dev-primary", reports, {},
                           roster, TIER1) == "PARITY"
    assert bem.verdict_for("harness:gemini:skills:invoke", "dev-primary", reports, {},
                           roster, TIER1) == "EXPECTED-DIVERGENCE"
    assert bem.verdict_for("harness:gemini:workflow:gates", "dev-primary", reports, {},
                           roster, TIER1) == "PARITY"


def test_provider_absent_yields_absent_not_diverges():
    roster = {"dev-primary": {"status": "active"}}
    reports = {"dev-primary": _provider_report("dev-primary", {
        "codex": {"present": False, "installed": False}
    })}
    assert bem.verdict_for("harness:codex:workflow:gates", "dev-primary", reports, {},
                           roster, TIER1) == "ABSENT"


def test_provider_unknown_capability_yields_missing_evidence_not_absent():
    roster = {"dev-primary": {"status": "active"}}
    reports = {"dev-primary": _provider_report("dev-primary", {
        "claude": {
            "present": False,
            "installed": False,
            "memory:read": {"status": "unknown", "reason": "collector_unavailable"},
        }
    })}

    assert bem.verdict_for("harness:claude:memory:read", "dev-primary", reports, {},
                           roster, TIER1) == "MISSING-EVIDENCE"


def test_expected_divergence_is_explicit_reason_only():
    roster = {"dev-primary": {"status": "active"}}
    reports = {"dev-primary": _provider_report("dev-primary", {
        "hermes": {"skills:invoke": {"status": "expected_divergence",
                                     "reason": "external_skill_dirs_configured"}}
    })}
    assert bem.verdict_for("harness:hermes:skills:invoke", "dev-primary", reports, {},
                           roster, TIER1) == "EXPECTED-DIVERGENCE"

    reports = {"dev-primary": _provider_report("dev-primary", {
        "hermes": {"skills:invoke": {"status": "expected_divergence",
                                     "reason": "arbitrary_reason"}}
    })}
    assert bem.verdict_for("harness:hermes:skills:invoke", "dev-primary", reports, {},
                           roster, TIER1) == "DIVERGES"


def test_legacy_v3_report_provider_rows_missing_evidence():
    roster = {"dev-primary": {"status": "active"}}
    rep = _report("dev-primary")
    rep["schema_version"] = 3
    rep["dimensions"].pop("provider_harness")
    reports = {"dev-primary": rep}
    assert bem.verdict_for("harness:codex:memory:read", "dev-primary", reports, {},
                           roster, TIER1) == "MISSING-EVIDENCE"


def test_stale_checkout_precedence_still_dominates_provider_rows():
    roster = {"dev-primary": {"status": "active"}}
    reports = {"dev-primary": _provider_report("dev-primary", provenance=_prov(dirty=True))}
    assert bem.verdict_for("harness:codex:memory:read", "dev-primary", reports, {},
                           roster, TIER1) == "STALE-CHECKOUT"


def test_matrix_renders_nine_provider_capability_rows_for_four_active_machines(tmp_path, monkeypatch):
    state = tmp_path / "state"
    state.mkdir()
    reports_dir = tmp_path / "reports"
    cfg = tmp_path / "harness-config.yaml"
    machines = {m: {"status": "active"} for m in (
        "dev-primary", "dev-secondary", "ace-win-1", "ace-win-2")}
    cfg.write_text(yaml.safe_dump({"workstations": machines, "tier1_repos": TIER1}))
    for machine in machines:
        (state / f"equality-{machine}.yaml").write_text(
            yaml.safe_dump(_provider_report(machine)))
    monkeypatch.setattr(bem, "STATE", state)
    monkeypatch.setattr(bem, "REPORTS", reports_dir)
    monkeypatch.setattr(bem, "CONFIG", cfg)

    bem.main()

    html = next(reports_dir.glob("*-machine-equality-matrix.html")).read_text()
    for row in (
        "harness:claude:memory:read",
        "harness:claude:skills:invoke",
        "harness:claude:workflow:gates",
        "harness:codex:memory:read",
        "harness:codex:skills:invoke",
        "harness:codex:workflow:gates",
        "harness:hermes:memory:read",
        "harness:hermes:skills:invoke",
        "harness:hermes:workflow:gates",
    ):
        assert f"<th>{row}</th>" in html
    assert html.count("PARITY") >= 32
    assert "EXPECTED-DIVERGENCE" in html


def test_json_emit_returns_verdict_map(tmp_path, monkeypatch, capsys):
    # --json prints {machine: {dim: verdict}} and writes NO HTML (tooling path for
    # reconcile-ecosystem.sh). --machine scopes it to one column.
    state = tmp_path / "state"; state.mkdir()
    reports_dir = tmp_path / "reports"
    cfg = tmp_path / "harness-config.yaml"
    machines = {m: {"status": "active"} for m in ("dev-primary", "dev-secondary")}
    cfg.write_text(yaml.safe_dump({"workstations": machines, "tier1_repos": TIER1}))
    for machine in machines:
        (state / f"equality-{machine}.yaml").write_text(yaml.safe_dump(_provider_report(machine)))
    monkeypatch.setattr(bem, "STATE", state)
    monkeypatch.setattr(bem, "REPORTS", reports_dir)
    monkeypatch.setattr(bem, "CONFIG", cfg)
    monkeypatch.setattr(bem.sys, "argv", ["build-equality-matrix.py", "--json"])

    bem.main()

    import json as _json
    out = _json.loads(capsys.readouterr().out)
    assert set(out) == {"dev-primary", "dev-secondary"}
    assert out["dev-primary"]["compute"] in {
        "CONFORMS", "BELOW-BASELINE", "MISSING-EVIDENCE", "MISSING-BASELINE"}
    assert "harness:claude:memory:read" in out["dev-primary"]
    # --json must not write the HTML alias
    assert not (reports_dir / "machine-equality-matrix.html").exists()


def test_remediate_skips_ok_verdicts():
    for v in ("CONFORMS", "EQUAL", "PARITY", "EXPECTED-DIFF", "UNREACHABLE", "ABSENT"):
        assert bem.remediate("skills", v) is None


def test_remediate_provider_missing_evidence_is_by_design():
    action, owner, by_design = bem.remediate("harness:codex:memory:read", "MISSING-EVIDENCE")
    assert by_design is True and "Hermes-only" in action


def test_remediate_non_provider_missing_evidence_is_actionable():
    action, owner, by_design = bem.remediate("kanban", "MISSING-EVIDENCE")
    assert by_design is False and owner == "this box" and "collector" in action


def test_remediate_solvers_below_baseline_by_design():
    action, owner, by_design = bem.remediate("solvers", "BELOW-BASELINE")
    assert by_design is True and "licence" in action.lower()


def test_remediate_skills_diverges_points_at_symlink_repair():
    action, _, by_design = bem.remediate("skills", "DIVERGES")
    assert by_design is False and "symlink" in action


def test_equivalence_section_renders_with_prompt(tmp_path, monkeypatch):
    state = tmp_path / "state"; state.mkdir()
    reports_dir = tmp_path / "reports"
    cfg = tmp_path / "harness-config.yaml"
    # one reporting machine + one rostered-but-not-reporting → 'Not reporting' card
    cfg.write_text(yaml.safe_dump({"workstations": {
        "dev-primary": {"status": "active", "compute_floor": {"cores_min": 8},
                        "required_data_access": ["digitalmodel"],
                        "solvers_baseline": {"orcaflex": "absent", "orcawave": "absent",
                                             "aqwa": "absent", "ansys": "absent"}},
        "ace-win-1": {"status": "active"}},
        "tier1_repos": TIER1}))
    (state / "equality-dev-primary.yaml").write_text(yaml.safe_dump(
        _report("dev-primary", data_access=[{"repo": "digitalmodel", "mode": "sibling"}],
                solvers=_solvers())))
    monkeypatch.setattr(bem, "STATE", state)
    monkeypatch.setattr(bem, "REPORTS", reports_dir)
    monkeypatch.setattr(bem, "CONFIG", cfg)
    bem.main()
    html = (reports_dir / "machine-equality-matrix.html").read_text()
    assert "Achieving equivalence" in html
    assert "reconcile-ecosystem.sh" in html        # the prompt is embedded
    assert "/reconcile-ecosystem" in html
    assert "Not reporting" in html                 # ace-win-1 has no report


def test_json_emit_machine_scoped(tmp_path, monkeypatch, capsys):
    state = tmp_path / "state"; state.mkdir()
    reports_dir = tmp_path / "reports"
    cfg = tmp_path / "harness-config.yaml"
    machines = {m: {"status": "active"} for m in ("dev-primary", "dev-secondary")}
    cfg.write_text(yaml.safe_dump({"workstations": machines, "tier1_repos": TIER1}))
    for machine in machines:
        (state / f"equality-{machine}.yaml").write_text(yaml.safe_dump(_provider_report(machine)))
    monkeypatch.setattr(bem, "STATE", state)
    monkeypatch.setattr(bem, "REPORTS", reports_dir)
    monkeypatch.setattr(bem, "CONFIG", cfg)
    monkeypatch.setattr(bem.sys, "argv",
                        ["build-equality-matrix.py", "--json", "--machine", "dev-secondary"])

    bem.main()

    import json as _json
    out = _json.loads(capsys.readouterr().out)
    assert set(out) == {"dev-secondary"}


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
    for m in ("dev-primary", "dev-secondary", "ace-win-1", "ace-win-2"):
        assert "compute_floor" in baselines[m] and "required_data_access" in baselines[m]
        # baseline must only name repos the collector actually probes (D2-1)
        assert set(baselines[m]["required_data_access"]) <= set(TIER1)
        # #2849: every active machine declares a solvers baseline over the 4 named solvers
        sb = baselines[m]["solvers_baseline"]
        assert set(sb) == {"orcaflex", "orcawave", "aqwa", "ansys"}
        assert all(v in ("licensed", "present", "absent") for v in sb.values())


def test_wiring_single_source_schedule():
    # DC5: the schedule lives in the ONE canonical source (schedule-tasks.yaml), weekly,
    # all 4 active machines, with a Windows render path. The command routes through the
    # fail-loud wrapper (#2972), which must carry collector + builder + publisher — so
    # the collect/build/publish chain stays single-sourced one hop deeper.
    tasks = yaml.safe_load(
        (REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml").read_text())["tasks"]
    eq = next(t for t in tasks if t["id"] == "equality-report")
    assert eq["schedule"].split()[-1] == "1"            # weekly, Monday
    assert "equality-preflight.sh" in eq["command"]
    preflight = (REPO_ROOT / "scripts" / "readiness" / "equality-preflight.sh").read_text()
    assert "equality-matrix-cron.sh" in preflight
    wrapper = (REPO_ROOT / "scripts" / "readiness" / "equality-matrix-cron.sh").read_text()
    assert "collect-equality.sh" in wrapper
    assert "build-equality-matrix.py" in wrapper
    assert "publish-equality.sh" in wrapper
    for m in ("dev-primary", "dev-secondary", "ace-win-1", "ace-win-2"):
        assert m in eq["machines"]
    assert (REPO_ROOT / "scripts" / "windows" / "equality-report.ps1").exists()
    # The daily dead-man's-switch rebuild routes through the SAME wrapper.
    refresh = next(t for t in tasks if t["id"] == "equality-matrix-refresh")
    assert "equality-preflight.sh" in refresh["command"]


def test_verdict_behavior_is_uniform_not_expected_diff():
    # behavior probes compared across machines; identical → EQUAL (M2: never EXPECTED-DIFF)
    roster = {"dev-primary": {"status": "active"}, "dev-secondary": {"status": "active"}}
    reports = {"dev-primary": _report("dev-primary"), "dev-secondary": _report("dev-secondary")}
    assert bem.verdict_for("behavior", "dev-primary", reports, {}, roster, TIER1) == "EQUAL"


# ── #2851 freshness guard: STALE-CHECKOUT verdict + peer exclusion ───────────
def _prov(**over) -> dict:
    p = dict(FRESH_PROV)
    p.update(over)
    return p


def test_is_stale_fresh_is_not_stale():
    assert bem.is_stale(_report("dev-primary")) is False


def test_is_stale_dirty_true():
    assert bem.is_stale(_report("dev-primary", provenance=_prov(dirty=True))) is True


def test_is_stale_behind_main_positive():
    assert bem.is_stale(_report("dev-primary", provenance=_prov(behind_main=85))) is True


def test_is_stale_ahead_main_positive():
    # local commits NOT on origin/main (unpushed feature checkout) ⇒ non-canonical ⇒ stale
    assert bem.is_stale(_report("dev-primary", provenance=_prov(ahead_main=2))) is True


def test_is_stale_ahead_main_unknown_failclosed():
    assert bem.is_stale(_report("dev-primary", provenance=_prov(ahead_main="unknown"))) is True


def test_is_stale_dirty_missing_failclosed():
    # a provenance block with dirty omitted (garbled / partial) must fail closed, not open
    rep = _report("dev-primary")
    del rep["provenance"]["dirty"]
    assert bem.is_stale(rep) is True


def test_is_stale_behind_main_zero_string_ok():
    # YAML may surface 0 as int or str; both mean "current" → not stale on that axis
    assert bem.is_stale(_report("dev-primary", provenance=_prov(behind_main="0"))) is False


def test_is_stale_negative_age_failclosed():
    # A negative origin_ref_age_h means the ref mtime is in the future (clock skew / NTP) — the
    # freshness signal is unverifiable, so fail CLOSED (must not slip through `age > MAX`).
    assert bem.is_stale(_report("dev-primary", provenance=_prov(origin_ref_age_h=-3))) is True


def test_is_stale_absent_provenance_failclosed():
    # A legacy report with NO provenance block cannot prove freshness → STALE (BC2 fail-closed)
    rep = _report("dev-primary")
    del rep["provenance"]
    assert bem.is_stale(rep) is True


def test_matrix_stale_checkout_verdict_dirty():
    # dirty tree → STALE-CHECKOUT for that machine (any dim)
    roster = {"dev-primary": {"status": "active"}}
    reports = {"dev-primary": _report("dev-primary", provenance=_prov(dirty=True))}
    assert bem.verdict_for("skills", "dev-primary", reports, {}, roster, TIER1) == "STALE-CHECKOUT"
    # cold dims are stale too — the whole machine column is contaminated
    assert bem.verdict_for("compute", "dev-primary", reports, {}, roster, TIER1) == "STALE-CHECKOUT"


def test_matrix_stale_checkout_verdict_behind():
    roster = {"dev-primary": {"status": "active"}}
    reports = {"dev-primary": _report("dev-primary", provenance=_prov(behind_main=85))}
    assert bem.verdict_for("skills", "dev-primary", reports, {}, roster, TIER1) == "STALE-CHECKOUT"


def test_matrix_stale_origin_ref_failclosed():
    # behind_main "unknown" OR origin_ref_age_h unknown/>12 → STALE (BC2 fail-closed)
    roster = {"dev-primary": {"status": "active"}}
    for bad in (_prov(behind_main="unknown"), _prov(origin_ref_age_h="unknown"),
                _prov(origin_ref_age_h=None), _prov(origin_ref_age_h=13)):
        reports = {"dev-primary": _report("dev-primary", provenance=bad)}
        assert bem.verdict_for("skills", "dev-primary", reports, {}, roster, TIER1) == "STALE-CHECKOUT", bad


def test_matrix_origin_ref_at_boundary_is_fresh():
    # age exactly at the 12h trust window is still fresh (boundary inclusive)
    roster = {"dev-primary": {"status": "active"}, "dev-secondary": {"status": "active"}}
    reports = {"dev-primary": _report("dev-primary", provenance=_prov(origin_ref_age_h=12)),
               "dev-secondary": _report("dev-secondary")}
    assert bem.verdict_for("skills", "dev-primary", reports, {}, roster, TIER1) == "EQUAL"


def test_matrix_unreachable_dominates_present_report():
    # BC3: a status:unreachable roster entry stays UNREACHABLE even WITH a present (stale or fresh) report
    roster = {"home-win": {"status": "unreachable"}}
    reports = {"home-win": _report("home-win")}                      # fresh report, but unreachable wins
    assert bem.verdict_for("skills", "home-win", reports, {}, roster, TIER1) == "UNREACHABLE"
    reports_stale = {"home-win": _report("home-win", provenance=_prov(dirty=True))}
    assert bem.verdict_for("compute", "home-win", reports_stale, {}, roster, TIER1) == "UNREACHABLE"


def test_matrix_stale_excluded_one_fresh_pending():
    # 1 fresh + 1 stale → the stale peer is EXCLUDED from the uniform value list, leaving ONE
    # real reporter → PENDING (A2/BC4 — NOT EQUAL).
    roster = {"dev-primary": {"status": "active"}, "dev-secondary": {"status": "active"}}
    reports = {"dev-primary": _report("dev-primary"),
               "dev-secondary": _report("dev-secondary", provenance=_prov(dirty=True))}
    assert bem.verdict_for("skills", "dev-primary", reports, {}, roster, TIER1) == "PENDING"
    assert bem.verdict_for("skills", "dev-secondary", reports, {}, roster, TIER1) == "STALE-CHECKOUT"


def test_matrix_stale_excluded_two_fresh_equal():
    # 2 fresh equal + 1 stale divergent → fresh dims EQUAL (stale value never enters the tally);
    # the stale machine itself reads STALE-CHECKOUT (BC4).
    roster = {"dev-primary": {"status": "active"}, "dev-secondary": {"status": "active"},
              "ace-win-1": {"status": "active"}}
    reports = {"dev-primary": _report("dev-primary", skills={"repo_skill_count": 407}),
               "dev-secondary": _report("dev-secondary", skills={"repo_skill_count": 407}),
               "ace-win-1": _report("ace-win-1", provenance=_prov(behind_main=85),
                                         skills={"repo_skill_count": 999})}
    assert bem.verdict_for("skills", "dev-primary", reports, {}, roster, TIER1) == "EQUAL"
    assert bem.verdict_for("skills", "ace-win-1", reports, {}, roster, TIER1) == "STALE-CHECKOUT"


def test_matrix_stale_not_in_majority():
    # 2 fresh disagree + 1 stale matching one side → NO-MAJORITY (the stale report must NOT
    # break the tie by lending its vote to one side) (BC4). Vehicle is kanban — skills no
    # longer majority-votes (SHA-aware: same-SHA mismatch is DIVERGES regardless of ties).
    roster = {"dev-primary": {"status": "active"}, "dev-secondary": {"status": "active"},
              "ace-win-1": {"status": "active"}}
    reports = {"dev-primary": _report("dev-primary", kanban={"dispatch_queues": "dev-primary,multi"}),
               "dev-secondary": _report("dev-secondary", kanban={"dispatch_queues": "dev-primary"}),
               "ace-win-1": _report("ace-win-1", provenance=_prov(dirty=True),
                                         kanban={"dispatch_queues": "dev-primary,multi"})}
    assert bem.verdict_for("kanban", "dev-primary", reports, {}, roster, TIER1) == "NO-MAJORITY"


def test_matrix_fresh_unaffected():
    # Two clean reports grade normally — the guard is invisible when nothing is stale.
    roster = {"dev-primary": {"status": "active"}, "dev-secondary": {"status": "active"}}
    reports = {"dev-primary": _report("dev-primary"), "dev-secondary": _report("dev-secondary")}
    assert bem.verdict_for("skills", "dev-primary", reports, {}, roster, TIER1) == "EQUAL"


def test_matrix_stale_renders_in_html(tmp_path, monkeypatch):
    # End-to-end: a dirty machine's report renders STALE-CHECKOUT cells in the matrix HTML.
    state = tmp_path / "state"; state.mkdir()
    reports_dir = tmp_path / "reports"
    cfg = tmp_path / "harness-config.yaml"
    cfg.write_text(yaml.safe_dump({"workstations": {
        "dev-primary": {"compute_floor": {"cores_min": 8}, "required_data_access": ["digitalmodel"],
                        "solvers_baseline": {"orcaflex": "absent", "orcawave": "absent",
                                             "aqwa": "absent", "ansys": "absent"}}},
        "tier1_repos": TIER1}))
    rep = _report("dev-primary", provenance=_prov(dirty=True),
                  data_access=[{"repo": "digitalmodel", "mode": "sibling"}])
    (state / "equality-dev-primary.yaml").write_text(yaml.safe_dump(rep))
    monkeypatch.setattr(bem, "STATE", state)
    monkeypatch.setattr(bem, "REPORTS", reports_dir)
    monkeypatch.setattr(bem, "CONFIG", cfg)
    bem.main()
    html = next(reports_dir.glob("*-machine-equality-matrix.html")).read_text()
    assert "stale-checkout" in html               # CSS class present (lowercased verdict)
    assert "STALE-CHECKOUT" in html               # visible cell text


# ── collector-artifact fixes: SHA-aware skills verdict + order-insensitive kanban ──
def _two_box(dim: str, val_a, val_b, prov_b: dict | None = None) -> str:
    roster = {"dev-primary": {"status": "active"}, "dev-secondary": {"status": "active"}}
    ra, rb = _report("dev-primary"), _report("dev-secondary", provenance=prov_b)
    ra["dimensions"][dim] = val_a
    rb["dimensions"][dim] = val_b
    return bem.verdict_for(dim, "dev-primary", {"dev-primary": ra, "dev-secondary": rb},
                           {}, roster, TIER1)


def test_skills_count_mismatch_across_shas_is_expected_diff():
    # Evidence collected days apart sits at different SHAs; a count delta there is
    # checkout skew (the 417/416/415 fleet reading), not divergence.
    verdict = _two_box("skills", {"repo_skill_count": 417}, {"repo_skill_count": 416},
                       prov_b={**FRESH_PROV, "checkout_sha": "def5678"})
    assert verdict == "EXPECTED-DIFF"


def test_skills_count_mismatch_same_sha_diverges():
    # Same SHA, different count = dirty overlay / partial checkout — the real signal.
    verdict = _two_box("skills", {"repo_skill_count": 417}, {"repo_skill_count": 416})
    assert verdict == "DIVERGES"


def test_skills_equal_counts_across_shas_equal():
    verdict = _two_box("skills", {"repo_skill_count": 417}, {"repo_skill_count": 417},
                       prov_b={**FRESH_PROV, "checkout_sha": "def5678"})
    assert verdict == "EQUAL"


def test_skills_mismatch_without_sha_fail_closed_diverges():
    # A mismatch that includes a report with no checkout_sha cannot be attributed to
    # checkout skew — fail closed, never silently EXPECTED-DIFF.
    prov_no_sha = {k: v for k, v in FRESH_PROV.items() if k != "checkout_sha"}
    verdict = _two_box("skills", {"repo_skill_count": 417}, {"repo_skill_count": 416},
                       prov_b=prov_no_sha)
    assert verdict == "DIVERGES"


def test_kanban_queue_order_is_ignored():
    # Locale collation (Linux) vs byte order (Git Bash on Windows) emitted the SAME
    # queue set as differently-ordered strings; membership, not order, is compared.
    verdict = _two_box("kanban",
                       {"dispatch_queues": "dev-primary,home-win,_leader-state"},
                       {"dispatch_queues": "_leader-state,dev-primary,home-win"},
                       prov_b={**FRESH_PROV, "checkout_sha": "def5678"})
    assert verdict == "EQUAL"


def test_kanban_membership_difference_still_diverges():
    roster = {m: {"status": "active"} for m in ("a", "b", "c")}
    reports = {m: _report(m) for m in roster}
    reports["a"]["dimensions"]["kanban"] = {"dispatch_queues": "dev-primary,multi"}
    reports["b"]["dimensions"]["kanban"] = {"dispatch_queues": "dev-primary,multi"}
    reports["c"]["dimensions"]["kanban"] = {"dispatch_queues": "dev-primary,multi,rogue"}
    assert bem.verdict_for("kanban", "a", reports, {}, roster, TIER1) == "DIVERGES"


# ── harness-checkup verdict (#3408) ──────────────────────────────────────────
_HC_CLEAN = {
    "audited_at": "2026-07-09T12:00:00+00:00", "settings_parse_ok": True,
    "install_method": "npm-global", "duplicate_installs": 0, "broken_agents": 0,
    "version_current": True, "auto_mode_default": True, "unused_skills": 3, "unused_plugins": 0,
}


def _hc(**over):
    d = dict(_HC_CLEAN)
    d.update(over)
    return _report("m", harness_checkup=d)


def test_hc_clean_ok():
    assert bem.harness_checkup_verdict(_hc()) == "CHECKUP-OK"


def test_hc_absent_dim_is_missing_evidence():
    assert bem.harness_checkup_verdict(_report("m")) == "MISSING-EVIDENCE"


def test_hc_no_audited_at_missing_evidence():
    d = dict(_HC_CLEAN)
    d.pop("audited_at")
    assert bem.harness_checkup_verdict(_report("m", harness_checkup=d)) == "MISSING-EVIDENCE"


def test_hc_null_core_evidence_missing():
    assert bem.harness_checkup_verdict(_hc(settings_parse_ok=None)) == "MISSING-EVIDENCE"
    assert bem.harness_checkup_verdict(_hc(install_method=None)) == "MISSING-EVIDENCE"


def test_hc_garbled_settings_evidence_fails_closed():
    assert bem.harness_checkup_verdict(_hc(settings_parse_ok="false")) == "MISSING-EVIDENCE"


def test_hc_broken_settings_duplicate_agents():
    assert bem.harness_checkup_verdict(_hc(settings_parse_ok=False)) == "CHECKUP-BROKEN"
    assert bem.harness_checkup_verdict(_hc(duplicate_installs=1)) == "CHECKUP-BROKEN"
    assert bem.harness_checkup_verdict(_hc(broken_agents=2)) == "CHECKUP-BROKEN"


def test_hc_soft_drift():
    assert bem.harness_checkup_verdict(_hc(version_current=False)) == "CHECKUP-DRIFTED"
    assert bem.harness_checkup_verdict(_hc(auto_mode_default=False)) == "CHECKUP-DRIFTED"
    assert bem.harness_checkup_verdict(_hc(unused_skills=16)) == "CHECKUP-DRIFTED"
    assert bem.harness_checkup_verdict(_hc(unused_plugins=1)) == "CHECKUP-DRIFTED"


def test_hc_clutter_boundary_and_unknown_currency_are_ok():
    assert bem.harness_checkup_verdict(_hc(unused_skills=15)) == "CHECKUP-OK"
    assert bem.harness_checkup_verdict(_hc(version_current=None)) == "CHECKUP-OK"


def test_hc_broken_beats_drift():
    assert bem.harness_checkup_verdict(_hc(settings_parse_ok=False, version_current=False)) == "CHECKUP-BROKEN"


def test_hc_registered_in_display_group_severity():
    assert "harness_checkup" in bem.BASE_DISPLAY_DIMS
    assert any("harness_checkup" in dims for _, _, dims in bem.GROUPS)
    assert "CHECKUP-OK" in bem.OK_VERDICTS
    assert bem.ROLLUP_SEVERITY["CHECKUP-BROKEN"] == 6
    assert bem.ROLLUP_SEVERITY["CHECKUP-DRIFTED"] == 5
    assert bem.ROLLUP_SEVERITY["CHECKUP-OK"] == 0


def test_hc_verdict_via_dispatch():
    roster = {"m": {"status": "active"}}
    reports = {"m": _hc(unused_skills=16)}
    assert bem.verdict_for("harness_checkup", "m", reports, {}, roster, TIER1) == "CHECKUP-DRIFTED"
