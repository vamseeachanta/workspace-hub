"""Tests for scripts/benchmark/fleet-solver-bench.

The fake OrcFxAPI below exercises the harness wiring only. It proves nothing
about OrcaFlex physics: the conservation check against a licensed DLL is the
comparator for that, and it runs on the first --smoke pass.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[2] / "scripts" / "benchmark" / "fleet-solver-bench"
sys.path.insert(0, str(BENCH))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"fleet_bench_{name}", BENCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


common = _load("common")
orca = _load("bench_orcaflex")
agg = _load("aggregate")
cpu = _load("bench_cpu")


# ---------------------------------------------------------------- labels


@pytest.mark.parametrize("label", ["ace-win-1", "ace-win-3", "ace-linux-2", "gpu-claw"])
def test_public_labels_accepted(label):
    assert common.require_label(label) == label


@pytest.mark.parametrize("label", ["WS999", "demo-srv99", "ace-win", "", "ace-win-1; rm"])
def test_physical_or_malformed_labels_refused(label):
    with pytest.raises(SystemExit):
        common.require_label(label)


# ---------------------------------------------------------------- physics helpers


def test_submerged_weight_hand_calc():
    # 0.15 te/m steel-equivalent, 0.3 m OD, 1.025 te/m3 sea water, 1700 m.
    displaced = 1.025 * math.pi * 0.3**2 / 4
    expected = (0.15 - displaced) * 9.80665 * 1700
    assert orca.submerged_weight_kn(0.15, 0.3, 1700, 1.025) == pytest.approx(expected, rel=1e-12)
    assert 1290 < expected < 1300  # ~1294 kN, order-of-magnitude guard on the inputs


def test_conservation_check_can_fail():
    ok = orca.conservation_check(-700.0, -594.0, 1294.0)
    bad = orca.conservation_check(-700.0, -500.0, 1294.0)
    assert ok["pass"] and ok["comparator_class"] == "conservation"
    assert not bad["pass"]
    assert bad["relative_error"] == pytest.approx(94 / 1294)


def test_lmstat_parse_and_busy():
    busy = "Users of Flex:  (Total of 1 license issued;  Total of 1 license in use)"
    free = "Users of Flex:  (Total of 1 license issued;  Total of 0 licenses in use)"
    assert orca.parse_lmstat(busy) == (1, 1)
    assert orca.parse_lmstat(free) == (1, 0)
    assert orca.parse_lmstat("no match here") is None


def test_k_sweep_ends_at_max():
    assert orca.k_sweep(16) == [1, 2, 4, 8, 16]
    assert orca.k_sweep(12) == [1, 2, 4, 8, 12]
    assert orca.k_sweep(1) == [1]


# ---------------------------------------------------------------- fake OrcFxAPI


class _Obj:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _FakeLine(_Obj):
    def __init__(self, gz_a, gz_b):
        super().__init__(LineType=[None], Length=[None], TargetSegmentLength=[None])
        self._gz = {"A": gz_a, "B": gz_b}

    def StaticResult(self, var, end):  # noqa: N802 — OrcFxAPI spelling
        if var == "End Gz force":
            return self._gz[end]
        if var == "Effective Tension":
            return 1500.0
        raise KeyError(var)

    def TimeHistory(self, var, period, end):  # noqa: N802
        return [1400.0, 1650.0, 1500.0]


class _FakeModel:
    def __init__(self, line):
        self.general = _Obj(UnitsSystem="SI", StageDuration=[None, None])
        self.environment = _Obj(SeaDensity=1.025)
        self._line = line
        self.created = []

    def CreateObject(self, kind, name):  # noqa: N802
        self.created.append((kind, name))
        return self._line if kind == "Line" else _Obj()

    def CalculateStatics(self):  # noqa: N802
        pass

    def RunSimulation(self):  # noqa: N802
        pass


def _fake_ofx(gz_a, gz_b):
    line = _FakeLine(gz_a, gz_b)
    return _Obj(
        Model=lambda: _FakeModel(line),
        ObjectType=_Obj(Vessel="Vessel", LineType="LineType", Line="Line"),
        oeEndA="A",
        oeEndB="B",
        Period=lambda n: n,
    ), line


def test_build_model_sets_geometry():
    ofx, line = _fake_ofx(0, 0)
    model, built = orca.build_model(ofx, 2.0, 200.0)
    assert built is line
    assert line.EndAConnection == "FPU" and line.EndBConnection == "Fixed"
    assert (line.EndBX, line.EndBY, line.EndBZ) == orca.RISER["end_b_m"]
    assert line.TargetSegmentLength[0] == 2.0
    assert model.general.StageDuration == [orca.RISER["buildup_s"], 200.0]
    # End B is above the seabed, so no seabed reaction enters the vertical balance.
    assert -orca.RISER["end_b_m"][2] < orca.RISER["water_depth_m"]


def test_build_model_refuses_non_si():
    ofx, _ = _fake_ofx(0, 0)
    original = ofx.Model
    ofx.Model = lambda: (lambda m: (setattr(m.general, "UnitsSystem", "US"), m)[1])(original())
    with pytest.raises(RuntimeError):
        orca.build_model(ofx, 10.0, 10.0)


def test_run_statics_reports_conservation():
    w = orca.submerged_weight_kn(0.15, 0.3, 1700, 1.025)
    ofx, _ = _fake_ofx(-0.55 * w, -0.45 * w)
    res = orca.run_statics(ofx, 10.0)
    assert res["check"]["pass"]
    ofx_bad, _ = _fake_ofx(-0.55 * w, -0.40 * w)
    assert not orca.run_statics(ofx_bad, 10.0)["check"]["pass"]


def test_run_dynamics_peak():
    ofx, _ = _fake_ofx(0, 0)
    assert orca.run_dynamics(ofx, 10.0, 20.0)["values"]["max_dynamic_top_tension_kn"] == 1650.0


# ---------------------------------------------------------------- aggregate


def _write(dirpath: Path, name: str, rec: dict):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / f"{name}.json").write_text(json.dumps(rec))


def _orca_rec(label, top, peak, w4):
    check = {"pass": True}
    return {
        "workload": "W2-W4",
        "label": label,
        "smoke": False,
        "profile": {"label": label, "logical_cores": 16},
        "w2": {"S": {"median_s": 1.0, "values": {"static_top_tension_kn": top}, "checks": [check]}},
        "w3": {"S": {"median_s": 9.0, "values": {"max_dynamic_top_tension_kn": peak}}},
        "w4": w4,
    }


def test_saturation_k():
    rows = [{"k": 1, "runs_per_hour": 10}, {"k": 2, "runs_per_hour": 19}, {"k": 4, "runs_per_hour": 30}, {"k": 8, "runs_per_hour": 31}]
    assert agg.saturation_k(rows) == (4, 31)
    assert agg.saturation_k([]) == (None, None)


def test_aggregate_cross_host_pass_and_fail(tmp_path):
    _write(tmp_path / "ace-win-1", "o", _orca_rec("ace-win-1", 1500.0, 1650.0, []))
    _write(tmp_path / "ace-win-2", "o", _orca_rec("ace-win-2", 1500.0000001, 1650.01, []))
    _write(tmp_path / "ace-win-3", "o", _orca_rec("ace-win-3", 1501.0, 1650.0, []))
    hosts = agg.load([tmp_path])
    found = {(f["label"], f["quantity"]): f["pass"] for f in agg.cross_host(hosts, "ace-win-1")}
    assert found[("ace-win-2", "static_top_tension_kn (S)")] is True
    assert found[("ace-win-2", "max_dynamic_top_tension_kn (S)")] is True
    assert found[("ace-win-3", "static_top_tension_kn (S)")] is False
    report = agg.render(hosts, "ace-win-1")
    assert "FAIL" in report and "ace-win-3" in report
    assert agg.main([str(tmp_path)]) == 1


def test_aggregate_refuses_unlabelled_record(tmp_path):
    _write(tmp_path, "x", {"workload": "W1", "label": "WS999", "results": {}})
    with pytest.raises(SystemExit):
        agg.load([tmp_path])


# ---------------------------------------------------------------- W1 smoke


def test_cpu_bench_small_run(tmp_path):
    pytest.importorskip("numpy")
    rc = cpu.main(["--label", "ace-linux-1", "--out", str(tmp_path), "--repeats", "1", "--matmul-n", "64", "--fft-log2", "10", "--loop-iterations", "1000"])
    assert rc == 0
    rec = json.loads((tmp_path / "w1-cpu.json").read_text())
    assert rec["results"]["matmul-1t"]["threads"] == 1
    assert rec["results"]["pyloop"]["reversals"] > 0
    assert json.loads((tmp_path / "w0-profile.json").read_text())["profile"]["label"] == "ace-linux-1"
