"""W0 host profile + W1 CPU baseline. Holds no licence seat; runs on any host.

    uv run python scripts/benchmark/fleet-solver-bench/bench_cpu.py --label ace-win-3

W1 workloads:
  matmul-1t   NumPy n x n matmul, BLAS pinned to 1 thread      -> GFLOP/s
  matmul-all  same, BLAS free to use every core                -> GFLOP/s
  fft         complex FFT of 2**k points                        -> seconds
  pyloop      pure-Python loop (interpreter speed, 1 core)      -> seconds

Each matmul variant runs in a child process because BLAS reads its thread count
once, at import time.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    Stopwatch,
    default_out_dir,
    host_profile,
    require_label,
    summarise,
    utc_now,
    write_record,
)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")


def _child_matmul(n: int, repeats: int) -> dict:
    import numpy as np

    rng = np.random.default_rng(0)
    a = rng.standard_normal((n, n))
    b = rng.standard_normal((n, n))
    a @ b  # warm-up
    times = []
    for _ in range(repeats):
        with Stopwatch() as sw:
            a @ b
        times.append(sw.elapsed)
    out = summarise(times)
    raw_median = sorted(times)[len(times) // 2]
    out["gflops"] = round(2 * n**3 / max(raw_median, 1e-9) / 1e9, 2)
    return out


def run_matmul(n: int, repeats: int, threads: int | None) -> dict:
    env = dict(os.environ)
    for var in THREAD_VARS:
        if threads is None:
            env.pop(var, None)
        else:
            env[var] = str(threads)
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child-matmul", str(n), str(repeats)]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise RuntimeError(f"matmul child failed (rc {proc.returncode}): {proc.stderr.strip()[-400:]}")
    result = json.loads(proc.stdout.strip().splitlines()[-1])
    result["threads"] = threads if threads is not None else "all"
    result["n"] = n
    return result


def run_fft(log2_points: int, repeats: int) -> dict:
    import numpy as np

    rng = np.random.default_rng(1)
    x = rng.standard_normal(2**log2_points) + 1j * rng.standard_normal(2**log2_points)
    np.fft.fft(x)
    times = []
    for _ in range(repeats):
        with Stopwatch() as sw:
            np.fft.fft(x)
        times.append(sw.elapsed)
    return {"points": 2**log2_points, **summarise(times)}


def _pyloop(iterations: int) -> int:
    # Reversal counting over a deterministic sawtooth: a stand-in for the
    # pure-Python post-processing loops in the overnight pipelines.
    prev, rising, reversals, value = 0, True, 0, 0
    for i in range(iterations):
        value = (i * 7919) % 1009
        up = value > prev
        if up != rising:
            reversals += 1
            rising = up
        prev = value
    return reversals


def run_pyloop(iterations: int, repeats: int) -> dict:
    _pyloop(iterations // 10)
    times, reversals = [], 0
    for _ in range(repeats):
        with Stopwatch() as sw:
            reversals = _pyloop(iterations)
        times.append(sw.elapsed)
    return {"iterations": iterations, "reversals": reversals, **summarise(times)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", help="approved fleet label of this host (never the physical name)")
    ap.add_argument("--out", type=Path, help="results directory (default ~/fleet-bench-results/<label>)")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--matmul-n", type=int, default=2000)
    ap.add_argument("--fft-log2", type=int, default=22)
    ap.add_argument("--loop-iterations", type=int, default=5_000_000)
    ap.add_argument("--child-matmul", nargs=2, type=int, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    if args.child_matmul:
        print(json.dumps(_child_matmul(*args.child_matmul)))
        return 0
    if not args.label:
        ap.error("--label is required")

    label = require_label(args.label)
    out_dir = args.out or default_out_dir(label)
    out_dir.mkdir(parents=True, exist_ok=True)
    profile = host_profile(label, out_dir)
    write_record(out_dir, "w0-profile", {"workload": "W0", "profile": profile})
    print(f"[W0] {json.dumps(profile)}")

    results = {
        "matmul-1t": run_matmul(args.matmul_n, args.repeats, threads=1),
        "matmul-all": run_matmul(args.matmul_n, args.repeats, threads=None),
        "fft": run_fft(args.fft_log2, args.repeats),
        "pyloop": run_pyloop(args.loop_iterations, args.repeats),
    }
    for name, res in results.items():
        print(f"[W1] {name}: median {res['median_s']} s" + (f", {res['gflops']} GFLOP/s" if "gflops" in res else ""))

    path = write_record(
        out_dir,
        "w1-cpu",
        {
            "workload": "W1",
            "label": label,
            "argv": sys.argv[1:],
            "logical_cores": profile["logical_cores"],
            "repo_commit": profile["repo_commit"],
            "finished_utc": utc_now(),
            "results": results,
        },
    )
    print(f"[W1] written {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
