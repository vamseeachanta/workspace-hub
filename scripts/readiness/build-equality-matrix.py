#!/usr/bin/env python3
"""build-equality-matrix.py — machine-equality matrix verdict engine + HTML render (#2801).

Joins per-machine .claude/state/equality-<machine>.yaml self-reports into one
machines × dimensions matrix. Two grading families (D2):
  COLD dims  (compute, data_access) → conformance to a DECLARED per-machine baseline
             in harness-config.yaml  → CONFORMS / BELOW-BASELINE / MISSING-BASELINE
  UNIFORM dims (harness, skills, kanban, memory, behavior, scheduler) → equality across
             active machines → EQUAL / DIVERGES / NO-MAJORITY / EXPECTED-DIFF / PENDING
plus MISSING-EVIDENCE / UNREACHABLE. Roster is read from harness-config.yaml (never
hardcoded, M1). Run: uv run python scripts/readiness/build-equality-matrix.py [--open]
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"
REPORTS = REPO / "docs" / "reports"
CONFIG = REPO / "scripts" / "readiness" / "harness-config.yaml"

TIER1_DEFAULT = ["assetutilities", "digitalmodel", "worldenergydata", "assethold"]
UNREACHABLE_DEFAULT = {"home-win", "macbook-portable"}
COLD_DIMS = {"compute", "data_access"}
# Uniform dims whose cross-machine difference is OS-driven, not a defect:
EXPECTED_DIFF_DIMS = {"python_cmd"}

_MIB = {"ki": 1 / 1024, "mi": 1, "gi": 1024, "ti": 1024 * 1024,
        "k": 1 / 1024, "m": 1, "g": 1024, "t": 1024 * 1024}  # treat bare-unit as binary


# ── roster + baselines (single source of truth: harness-config.yaml, M1) ─────
def load_roster(config: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for machine, entry in (config.get("workstations") or {}).items():
        entry = dict(entry or {})
        entry.setdefault("status",
                         "unreachable" if machine in UNREACHABLE_DEFAULT else "active")
        out[machine] = entry
    return out


def load_baselines(config: dict) -> dict[str, dict]:
    return {m: e for m, e in (config.get("workstations") or {}).items()
            if e and ("compute_floor" in e or "required_data_access" in e)}


# ── unit coercion (DG2/DC3/D2-2) ─────────────────────────────────────────────
def coerce_to_mib(raw) -> int:
    """Normalize a memory/size value to MiB. Raises ValueError on un-parseable input."""
    if isinstance(raw, bool):
        raise ValueError(f"bool is not a size: {raw!r}")
    if isinstance(raw, (int, float)):
        return int(raw)
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([KMGTkmgt]i?)?B?\s*", str(raw))
    if not m:
        raise ValueError(f"cannot coerce to MiB: {raw!r}")
    value, unit = float(m.group(1)), (m.group(2) or "").lower()
    return int(value * _MIB.get(unit, 1))


# ── cold-dim conformance (D2) ────────────────────────────────────────────────
def cold_verdict(dim: str, report: dict, baseline: dict | None, probed_repos: list[str]) -> str:
    if baseline is None:
        return "MISSING-BASELINE"
    dims = report.get("dimensions", {})
    if dim == "compute":
        static = dims.get("compute", {}).get("static", {})
        floor = baseline.get("compute_floor", {})
        # cores
        cores = static.get("cores")
        if cores in (None, "unknown", "n/a"):
            return "MISSING-EVIDENCE"
        try:
            if "cores_min" in floor and int(cores) < int(floor["cores_min"]):
                return "BELOW-BASELINE"
            # ram (floor declared in GiB; actual emitted in MiB)
            if "ram_gib_min" in floor:
                actual_mib = coerce_to_mib(static.get("ram_total_mib"))
                if actual_mib < int(floor["ram_gib_min"]) * 1024:
                    return "BELOW-BASELINE"
        except (ValueError, TypeError):
            return "MISSING-EVIDENCE"
        if floor.get("gpu_required") and str(static.get("gpu_model", "")).lower() in ("none", "", "n/a"):
            return "BELOW-BASELINE"
        return "CONFORMS"
    if dim == "data_access":
        required = baseline.get("required_data_access", [])
        if not set(required) <= set(probed_repos):     # D2-1: baseline names an unprobed repo
            return "MISSING-BASELINE"
        accessible = {d["repo"] for d in dims.get("data_access", []) if d.get("mode") != "absent"}
        return "CONFORMS" if set(required) <= accessible else "BELOW-BASELINE"
    raise ValueError(f"not a cold dimension: {dim}")


# ── uniform-dim equality + ties (C1) ─────────────────────────────────────────
def uniform_verdict(dim: str, values: list) -> str:
    if dim in EXPECTED_DIFF_DIMS:
        return "EXPECTED-DIFF"
    real = [v for v in values if v not in (None, "unknown", "n/a")]
    if len(real) < 2:
        return "PENDING"
    counts = Counter(real)
    if len(counts) == 1:
        return "EQUAL"
    top_n = max(counts.values())
    tied = [v for v, c in counts.items() if c == top_n]
    return "NO-MAJORITY" if len(tied) > 1 else "DIVERGES"


# ── value extraction for uniform dims ────────────────────────────────────────
def extract_value(dim: str, report: dict):
    d = report.get("dimensions", {})
    if dim == "python_cmd":
        return d.get("harness", {}).get("python_cmd")
    if dim == "harness":
        return json.dumps(d.get("harness", {}).get("providers", {}), sort_keys=True)
    if dim == "skills":
        return d.get("skills", {}).get("repo_skill_count")
    if dim == "kanban":
        return d.get("kanban", {}).get("dispatch_queues")
    if dim == "memory":
        return d.get("memory", {}).get("hermes_home")
    if dim == "behavior":
        b = d.get("behavior", {})
        return json.dumps({"enums": b.get("enums", {}), "hashes": b.get("hashes", {})}, sort_keys=True)
    if dim == "scheduler":
        s = d.get("scheduler", {})
        return json.dumps({"has_repo_sync": s.get("has_repo_sync"),
                           "has_parity_review": s.get("has_parity_review")}, sort_keys=True)
    return None


# ── precedence orchestrator (C3) ─────────────────────────────────────────────
def verdict_for(dim: str, machine: str, reports: dict, baselines: dict,
                roster: dict, probed_repos: list[str]) -> str:
    status = roster.get(machine, {}).get("status", "active")
    if machine not in reports:
        return "UNREACHABLE" if status == "unreachable" else "MISSING-EVIDENCE"
    if dim in COLD_DIMS:
        return cold_verdict(dim, reports[machine], baselines.get(machine), probed_repos)
    values = [extract_value(dim, reports[m]) for m in roster
              if roster[m].get("status") == "active" and m in reports]
    return uniform_verdict(dim, values)


# ── load + render ────────────────────────────────────────────────────────────
def load_reports() -> dict[str, dict]:
    out = {}
    for f in sorted(STATE.glob("equality-*.yaml")):
        machine = f.stem[len("equality-"):]
        try:
            out[machine] = yaml.safe_load(f.read_text()) or {}
        except yaml.YAMLError as e:
            out[machine] = {"_error": str(e)}
    return out


DISPLAY_DIMS = ["compute", "data_access", "harness", "python_cmd", "skills",
                "kanban", "memory", "behavior", "scheduler"]


def main() -> None:
    config = yaml.safe_load(CONFIG.read_text()) if CONFIG.exists() else {}
    roster = load_roster(config)
    baselines = load_baselines(config)
    probed = (config.get("tier1_repos") or TIER1_DEFAULT)
    reports = load_reports()

    rows = []
    for dim in DISPLAY_DIMS:
        cells = "".join(
            f'<td class="{verdict_for(dim, m, reports, baselines, roster, probed).lower()}">'
            f'{verdict_for(dim, m, reports, baselines, roster, probed)}</td>'
            for m in roster)
        rows.append(f"<tr><th>{dim}</th>{cells}</tr>")
    cols = "".join(f"<th>{m}<br><small>{roster[m].get('status')}</small></th>" for m in roster)
    reporting = sum(1 for m in roster if roster[m].get("status") == "active" and m in reports)
    active = sum(1 for m in roster if roster[m].get("status") == "active")

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Machine-Equality Matrix — #2801</title>
<style>body{{font:14px/1.5 system-ui,sans-serif;margin:2rem}}table{{border-collapse:collapse}}
th,td{{border:1px solid #ddd;padding:.4rem .6rem;font-size:.8rem}}thead th{{background:#2d3748;color:#fff}}
tbody th{{background:#edf2f7}}.conforms,.equal{{background:#c6f6d5}}.below-baseline,.diverges{{background:#fed7d7}}
.no-majority,.missing-baseline{{background:#feebc8}}.expected-diff{{background:#e9d8fd}}
.pending,.missing-evidence{{background:#fffaf0}}.unreachable{{background:#f7fafc;color:#a0aec0}}</style></head>
<body><h1>Machine-Equality Matrix</h1>
<p>#2801 · {date.today().isoformat()} · reporting {reporting}/{active} active machines</p>
<table><thead><tr><th>Dimension</th>{cols}</tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>"""

    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / f"{date.today().isoformat()}-machine-equality-matrix.html"
    out.write_text(html)
    print(f"wrote {out} ({reporting}/{active} active reporting)")
    if "--open" in sys.argv:
        import webbrowser
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
