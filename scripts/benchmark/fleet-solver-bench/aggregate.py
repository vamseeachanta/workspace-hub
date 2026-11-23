"""Aggregate per-host benchmark JSON into one Markdown report.

    python scripts/benchmark/fleet-solver-bench/aggregate.py <results-dir> [...] \
        [--reference ace-win-1] [--out report.md]

Reads every *.json under the given directories (w0-profile, w1-cpu, w2-w4-*).
Cross-host checks compare each host with the reference host, using tolerances
fixed before any run:
  static top tension          1e-6 relative
  max dynamic top tension     1e-4 relative
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import is_public_label  # noqa: E402

CROSS_HOST_TOL = {"static_top_tension_kn": 1e-6, "max_dynamic_top_tension_kn": 1e-4}
SATURATION_WITHIN = 0.10  # smallest K within 10 % of peak throughput


def load(dirs: list[Path]) -> dict[str, dict]:
    hosts: dict[str, dict] = {}
    for d in dirs:
        for path in sorted(d.rglob("*.json")):
            rec = json.loads(path.read_text(encoding="utf-8"))
            label = rec.get("label") or rec.get("profile", {}).get("label")
            if not is_public_label(label):
                raise SystemExit(f"{path}: record without an approved fleet label ({label!r})")
            slot = hosts.setdefault(label, {})
            wl = rec.get("workload")
            if wl == "W0":
                slot["profile"] = rec["profile"]
            elif wl == "W1":
                slot["w1"] = rec["results"]
            elif wl == "W2-W4" and not rec.get("smoke"):
                slot["orcaflex"] = rec
                slot.setdefault("profile", rec["profile"])
    return hosts


def saturation_k(rows: list[dict]) -> tuple[int | None, float | None]:
    done = [r for r in rows if "runs_per_hour" in r]
    if not done:
        return None, None
    peak = max(r["runs_per_hour"] for r in done)
    for r in sorted(done, key=lambda r: r["k"]):
        if r["runs_per_hour"] >= (1 - SATURATION_WITHIN) * peak:
            return r["k"], peak
    return None, peak


def cross_host(hosts: dict[str, dict], reference: str) -> list[dict]:
    ref = hosts.get(reference, {}).get("orcaflex")
    if ref is None:
        return []
    findings = []
    for label, slot in sorted(hosts.items()):
        rec = slot.get("orcaflex")
        if rec is None or label == reference:
            continue
        for stage, key in (("w2", "static_top_tension_kn"), ("w3", "max_dynamic_top_tension_kn")):
            for size, res in rec[stage].items():
                ref_res = ref[stage].get(size)
                if ref_res is None:
                    continue
                a, b = res["values"][key], ref_res["values"][key]
                rel = abs(a - b) / abs(b) if b else float("inf")
                findings.append(
                    {
                        "label": label,
                        "quantity": f"{key} ({size})",
                        "relative_diff": rel,
                        "tolerance": CROSS_HOST_TOL[key],
                        "pass": rel <= CROSS_HOST_TOL[key],
                    }
                )
    return findings


def fmt(v, nd=2) -> str:
    return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def render(hosts: dict[str, dict], reference: str) -> str:
    out = ["# Fleet solver benchmark", ""]
    labels = sorted(hosts)

    out += ["## Hosts (W0)", "", "| Host | CPU | Logical cores | RAM (GB) | OrcaFlex DLL | Python | Commit |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for lb in labels:
        p = hosts[lb].get("profile", {})
        out.append(f"| {lb} | {p.get('cpu_model', '-')} | {fmt(p.get('logical_cores'))} | {fmt(p.get('ram_gb'), 1)} | {p.get('orcaflex_dll') or '-'} | {p.get('python', '-')} | {p.get('repo_commit') or '-'} |")

    out += ["", "## CPU baseline (W1)", "", "| Host | matmul 1 thread (GFLOP/s) | matmul all (GFLOP/s) | FFT (s) | Python loop (s) |", "| --- | --- | --- | --- | --- |"]
    for lb in labels:
        w1 = hosts[lb].get("w1")
        if w1:
            out.append(f"| {lb} | {fmt(w1['matmul-1t']['gflops'])} | {fmt(w1['matmul-all']['gflops'])} | {fmt(w1['fft']['median_s'], 3)} | {fmt(w1['pyloop']['median_s'], 3)} |")

    orca = [lb for lb in labels if "orcaflex" in hosts[lb]]
    if orca:
        out += ["", "## OrcaFlex statics and dynamics (W2, W3) — median wall time (s)", ""]
        cols = [f"W2-{s}" for s in ("S", "M", "L")] + [f"W3-{s}" for s in ("S", "M", "L")]
        out += ["| Host | " + " | ".join(cols) + " | Conservation |", "| --- " * (len(cols) + 2) + "|"]
        for lb in orca:
            rec = hosts[lb]["orcaflex"]
            cells = [fmt(rec["w2"].get(s, {}).get("median_s"), 3) for s in ("S", "M", "L")]
            cells += [fmt(rec["w3"].get(s, {}).get("median_s"), 3) for s in ("S", "M", "L")]
            checks = [c for r in rec["w2"].values() for c in r.get("checks", [])]
            cons = "pass" if checks and all(c["pass"] for c in checks) else ("FAIL" if checks else "-")
            out.append(f"| {lb} | " + " | ".join(cells) + f" | {cons} |")

        out += ["", "## Batch throughput (W4)", "", "| Host | Peak runs/h | Saturation K | Sweep (K: runs/h) |", "| --- | --- | --- | --- |"]
        for lb in orca:
            rows = hosts[lb]["orcaflex"].get("w4", [])
            k, peak = saturation_k(rows)
            sweep = ", ".join(f"{r['k']}: {r['runs_per_hour']}" if "runs_per_hour" in r else f"{r['k']}: {r.get('skipped')}" for r in rows)
            out.append(f"| {lb} | {fmt(peak, 1)} | {fmt(k)} | {sweep or '-'} |")

        findings = cross_host(hosts, reference)
        out += ["", f"## Cross-host result equality (reference {reference})", ""]
        if not findings:
            out.append(f"Not evaluated: no full OrcaFlex record for the reference host {reference}.")
        else:
            out += ["| Host | Quantity | Relative difference | Tolerance | Result |", "| --- | --- | --- | --- | --- |"]
            for f in findings:
                out.append(f"| {f['label']} | {f['quantity']} | {f['relative_diff']:.2e} | {f['tolerance']:.0e} | {'pass' if f['pass'] else 'FAIL'} |")
    out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+", type=Path)
    ap.add_argument("--reference", default="ace-win-1")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    hosts = load(args.dirs)
    if not hosts:
        print("no benchmark records found", file=sys.stderr)
        return 2
    text = render(hosts, args.reference)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"written {args.out}")
    else:
        print(text)
    failed = [f for f in cross_host(hosts, args.reference) if not f["pass"]]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
