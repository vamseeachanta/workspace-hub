"""W2 statics, W3 dynamics, W4 batch throughput for OrcaFlex. Takes the Orcina seat.

RUN ONLY THROUGH THE SCHEDULED-TASK PATH (.claude/rules/licensed-solver-dispatch.md):
a direct-SSH session cannot complete the FlexNet checkout.

    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/dispatch-run.ps1 \
      -Action submit -Shell bash -JobId bench-<label> \
      -Command "uv run python scripts/benchmark/fleet-solver-bench/bench_orcaflex.py --label <label> --smoke"

The model is generated here — a catenary riser hung from a vessel to a fixed
point — so no client model enters the repository.

Status: the OrcFxAPI calls follow scripts/solver/generate_minimal_sim_fixture.py
but have NOT yet run against a licensed DLL. The first --smoke run is that test.

Correctness checks, tolerances fixed before any run:
  conservation   |End Gz force A| + |End Gz force B| vs submerged line weight, 0.5 %
  cross-host     done by aggregate.py against the reference host
"""

from __future__ import annotations

import argparse
import math
import multiprocessing as mp
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    Stopwatch,
    default_out_dir,
    free_ram_fraction,
    host_profile,
    require_label,
    summarise,
    utc_now,
    write_record,
)

G = 9.80665  # m/s2
CONSERVATION_TOL = 0.005  # relative, fixed before the first run

# Riser definition (OrcaFlex SI units: m, kN, te). ID = 0 so no contents term.
RISER = {
    "water_depth_m": 1500.0,
    "length_m": 1700.0,
    "od_m": 0.30,
    "mass_te_per_m": 0.15,
    "ea_kn": 5.0e6,
    "ei_knm2": 5.0e4,
    "end_a_m": (0.0, 0.0, -10.0),  # relative to the vessel
    "end_b_m": (900.0, 0.0, -1200.0),  # fixed, global; 300 m above the seabed
    "wave_height_m": 6.0,
    "wave_period_s": 10.0,
    "buildup_s": 10.0,
}
SEGMENTS_M = {"S": 10.0, "M": 2.0, "L": 0.5}
RAM_FLOOR = 0.15  # stop the W4 sweep below 15 % free physical memory


# ---------------------------------------------------------------- checks


def submerged_weight_kn(mass_te_per_m: float, od_m: float, length_m: float, sea_density_te_m3: float) -> float:
    displaced = sea_density_te_m3 * math.pi * od_m**2 / 4.0
    return (mass_te_per_m - displaced) * G * length_m


def conservation_check(fz_a_kn: float, fz_b_kn: float, expected_kn: float, tol: float = CONSERVATION_TOL) -> dict:
    total = abs(fz_a_kn) + abs(fz_b_kn)
    rel = abs(total - expected_kn) / abs(expected_kn)
    return {
        "check": "static-vertical-equilibrium",
        "comparator_class": "conservation",
        "end_vertical_sum_kn": round(total, 4),
        "submerged_weight_kn": round(expected_kn, 4),
        "relative_error": rel,
        "tolerance": tol,
        "pass": rel <= tol,
    }


_LMSTAT_RE = re.compile(r"Total of (\d+) licenses? issued;\s+Total of (\d+) licenses? in use", re.I)


def parse_lmstat(text: str) -> tuple[int, int] | None:
    m = _LMSTAT_RE.search(text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def seat_state() -> str:
    """'free', 'busy' or 'unknown'. Needs FLEX_LICENSE_SERVER (e.g. 27002@server) and lmutil on PATH."""
    server = os.environ.get("FLEX_LICENSE_SERVER")
    lmutil = shutil.which("lmutil")
    if not server or not lmutil:
        return "unknown"
    try:
        out = subprocess.run([lmutil, "lmstat", "-c", server, "-f", "Flex"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    counts = parse_lmstat(out.stdout)
    if counts is None:
        return "unknown"
    issued, in_use = counts
    return "busy" if in_use >= issued else "free"


# ---------------------------------------------------------------- model


def build_model(ofx, segment_m: float, sim_s: float):
    """Return (model, line). `ofx` is the OrcFxAPI module (injected for tests)."""
    m = ofx.Model()
    if str(m.general.UnitsSystem) != "SI":
        raise RuntimeError(f"expected SI units (m, kN, te), model reports {m.general.UnitsSystem!r}")
    m.general.StageDuration[0] = RISER["buildup_s"]
    m.general.StageDuration[1] = sim_s

    env = m.environment
    env.WaterDepth = RISER["water_depth_m"]
    env.WaveType = "Airy"
    env.WaveHeight = RISER["wave_height_m"]
    env.WavePeriod = RISER["wave_period_s"]

    m.CreateObject(ofx.ObjectType.Vessel, "FPU")

    lt = m.CreateObject(ofx.ObjectType.LineType, "RiserPipe")
    lt.OD = RISER["od_m"]
    lt.ID = 0.0
    lt.MassPerUnitLength = RISER["mass_te_per_m"]
    lt.EA = RISER["ea_kn"]
    lt.EIx = RISER["ei_knm2"]

    line = m.CreateObject(ofx.ObjectType.Line, "Riser")
    line.EndAConnection = "FPU"
    line.EndAX, line.EndAY, line.EndAZ = RISER["end_a_m"]
    line.EndBConnection = "Fixed"
    line.EndBX, line.EndBY, line.EndBZ = RISER["end_b_m"]
    line.LineType[0] = "RiserPipe"
    line.Length[0] = RISER["length_m"]
    line.TargetSegmentLength[0] = segment_m
    return m, line


def sea_density(model) -> float:
    try:
        return float(model.environment.SeaDensity)
    except Exception:  # noqa: BLE001
        return 1.025


def run_statics(ofx, segment_m: float) -> dict:
    m, line = build_model(ofx, segment_m, sim_s=10.0)
    with Stopwatch() as sw:
        m.CalculateStatics()
    fz_a = float(line.StaticResult("End Gz force", ofx.oeEndA))
    fz_b = float(line.StaticResult("End Gz force", ofx.oeEndB))
    top = float(line.StaticResult("Effective Tension", ofx.oeEndA))
    expected = submerged_weight_kn(RISER["mass_te_per_m"], RISER["od_m"], RISER["length_m"], sea_density(m))
    return {
        "elapsed_s": sw.elapsed,
        "values": {"static_top_tension_kn": top, "end_a_gz_kn": fz_a, "end_b_gz_kn": fz_b},
        "check": conservation_check(fz_a, fz_b, expected),
    }


def run_dynamics(ofx, segment_m: float, sim_s: float) -> dict:
    m, line = build_model(ofx, segment_m, sim_s)
    m.CalculateStatics()
    with Stopwatch() as sw:
        m.RunSimulation()
    th = line.TimeHistory("Effective Tension", ofx.Period(1), ofx.oeEndA)
    peak = float(max(th))
    return {"elapsed_s": sw.elapsed, "values": {"max_dynamic_top_tension_kn": peak}}


# ---------------------------------------------------------------- W4 worker


def _w4_job(args: tuple[float, float]) -> float:
    import OrcFxAPI as ofx  # each worker process imports its own binding

    segment_m, sim_s = args
    t0 = time.perf_counter()
    m, _ = build_model(ofx, segment_m, sim_s)
    m.CalculateStatics()
    m.RunSimulation()
    return time.perf_counter() - t0


def k_sweep(max_k: int) -> list[int]:
    ks, k = [], 1
    while k < max_k:
        ks.append(k)
        k *= 2
    ks.append(max_k)
    return ks


def run_w4(jobs: int, segment_m: float, sim_s: float, max_k: int) -> list[dict]:
    ctx = mp.get_context("spawn")
    rows = []
    for k in k_sweep(max_k):
        free = free_ram_fraction()
        if free is not None and free < RAM_FLOOR:
            rows.append({"k": k, "skipped": f"free RAM {free:.0%} below {RAM_FLOOR:.0%}"})
            break
        with Stopwatch() as sw, ctx.Pool(processes=k) as pool:
            per_job = pool.map(_w4_job, [(segment_m, sim_s)] * jobs)
        rows.append(
            {
                "k": k,
                "jobs": jobs,
                "wall_s": round(sw.elapsed, 3),
                "runs_per_hour": round(jobs / sw.elapsed * 3600, 2),
                "per_job_median_s": round(sorted(per_job)[len(per_job) // 2], 3),
                "free_ram_before": free,
            }
        )
        print(f"[W4] K={k}: {rows[-1]['runs_per_hour']} runs/h")
    return rows


# ---------------------------------------------------------------- main


def timed(fn, repeats: int, warmup: bool = True) -> dict:
    if warmup:
        fn()
    runs = [fn() for _ in range(repeats)]
    out = summarise([r["elapsed_s"] for r in runs])
    out["values"] = runs[-1]["values"]
    if "check" in runs[-1]:
        out["checks"] = [r["check"] for r in runs]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--smoke", action="store_true", help="W2-S and a 20 s W3-S, one repeat, no W4")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--statics-sizes", default="S,M,L")
    ap.add_argument("--dynamics-sizes", default="S,M")
    ap.add_argument("--sim-s", type=float, default=200.0)
    ap.add_argument("--w4-jobs", type=int, default=16)
    ap.add_argument("--w4-sim-s", type=float, default=100.0)
    ap.add_argument("--max-k", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--skip-w4", action="store_true")
    ap.add_argument("--ignore-seat", action="store_true", help="proceed when the seat state is unknown or busy")
    args = ap.parse_args(argv)

    label = require_label(args.label)
    out_dir = args.out or default_out_dir(label)
    out_dir.mkdir(parents=True, exist_ok=True)

    seat = seat_state()
    print(f"[seat] {seat}")
    if seat == "busy" and not args.ignore_seat:
        print("[seat] Flex seat in use elsewhere; aborting rather than queueing", file=sys.stderr)
        return 3

    import OrcFxAPI as ofx

    profile = host_profile(label, out_dir)
    record = {
        "workload": "W2-W4",
        "label": label,
        "argv": sys.argv[1:],
        "smoke": args.smoke,
        "seat_state_at_start": seat,
        "profile": profile,
        "riser": {k: list(v) if isinstance(v, tuple) else v for k, v in RISER.items()},
        "started_utc": utc_now(),
        "w2": {},
        "w3": {},
        "w4": [],
    }

    if args.smoke:
        repeats, warmup, stat_sizes, dyn_sizes, sim_s = 1, False, ["S"], ["S"], 20.0
    else:
        repeats, warmup, sim_s = args.repeats, True, args.sim_s
        stat_sizes = args.statics_sizes.split(",")
        dyn_sizes = args.dynamics_sizes.split(",")

    for size in stat_sizes:
        seg = SEGMENTS_M[size]
        res = timed(lambda seg=seg: run_statics(ofx, seg), repeats, warmup)
        record["w2"][size] = {"segment_m": seg, **res}
        ok = all(c["pass"] for c in res["checks"])
        print(f"[W2] {size}: median {res['median_s']} s, conservation {'pass' if ok else 'FAIL'}")
    for size in dyn_sizes:
        seg = SEGMENTS_M[size]
        res = timed(lambda seg=seg: run_dynamics(ofx, seg, sim_s), repeats, warmup)
        record["w3"][size] = {"segment_m": seg, "sim_s": sim_s, **res}
        print(f"[W3] {size}: median {res['median_s']} s")
    if not (args.smoke or args.skip_w4):
        record["w4"] = run_w4(args.w4_jobs, SEGMENTS_M["M"], args.w4_sim_s, args.max_k)

    record["finished_utc"] = utc_now()
    path = write_record(out_dir, "w2-w4-smoke" if args.smoke else "w2-w4-orcaflex", record)
    print(f"[done] written {path}")
    failed = [s for s, r in record["w2"].items() if not all(c["pass"] for c in r["checks"])]
    return 4 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
