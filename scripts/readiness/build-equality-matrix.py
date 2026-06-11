#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""build-equality-matrix.py — machine-equality matrix verdict engine + HTML render (#2801).

Joins per-machine .claude/state/equality-<machine>.yaml self-reports into one
machines × dimensions matrix. Two grading families (D2):
  COLD dims  (compute, data_access) → conformance to a DECLARED per-machine baseline
             in harness-config.yaml  → CONFORMS / BELOW-BASELINE / MISSING-BASELINE
  UNIFORM dims (harness, skills, kanban, memory, behavior, scheduler) → equality across
             active machines → EQUAL / DIVERGES / NO-MAJORITY / EXPECTED-DIFF / PENDING
plus MISSING-EVIDENCE / UNREACHABLE. Roster is read from harness-config.yaml (never
hardcoded, M1). Run: uv run --script scripts/readiness/build-equality-matrix.py [--open]
(PEP-723 inline deps above make the cron/standalone path resolve pyyaml — #2972.)
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
COLD_DIMS = {"compute", "data_access", "solvers"}
# Solver verdict acceptance (STRICT, #2849 decision 1): which DETECTED statuses satisfy
# each DECLARED baseline. `licensed` baseline is satisfied ONLY by a `licensed` signal
# (an install-only `present` is NOT enough — licensed work must never route to it).
# `unknown`/missing detection is NEVER an acceptance for any baseline — it grades
# MISSING-EVIDENCE (handled in cold_verdict), so a legacy v2 report with no solvers
# block does not masquerade as CONFORMS on a dev (absent-baseline) machine.
SOLVER_OK = {
    "absent":   {"absent"},
    "present":  {"present", "licensed"},
    "licensed": {"licensed"},
}
# Uniform dims whose cross-machine difference is OS-driven, not a defect:
EXPECTED_DIFF_DIMS = {"python_cmd"}
PROVIDERS = ("claude", "codex", "hermes")
CAPABILITIES = ("memory:read", "skills:invoke", "workflow:gates")
EXPECTED_DIVERGENCE_REASONS = {"external_skill_dirs_configured"}

# #2851 freshness guard: a report whose origin/main ref hasn't been refreshed within this
# many hours can't be trusted to have a meaningful behind_main, so we fail closed. repo-sync
# pulls ~every 4h, so 12h is a generous trust window.
ORIGIN_REF_MAX_H = 12

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
        result = int(raw)
    else:
        m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([KMGTkmgt]i?)?B?\s*", str(raw))
        if not m:
            raise ValueError(f"cannot coerce to MiB: {raw!r}")
        result = int(float(m.group(1)) * _MIB.get((m.group(2) or "").lower(), 1))
    if result < 0:                                  # GC5/MINOR: reject negative as invalid evidence
        raise ValueError(f"negative size is invalid: {raw!r}")
    return result


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
    if dim == "solvers":
        declared = baseline.get("solvers_baseline")
        if not declared:                                 # baseline opted out → fail-closed
            return "MISSING-BASELINE"
        detected = {s["name"]: s.get("status") for s in dims.get("solvers", [])}
        verdict = "CONFORMS"
        for name, want in declared.items():
            got = detected.get(name, "unknown")
            ok = SOLVER_OK.get(want, set())
            # `unknown`/missing detection is NOT evidence for ANY baseline (incl. absent):
            # a legacy v2 report with no solvers block must not pass as CONFORMS.
            if got in (None, "unknown"):
                verdict = "MISSING-EVIDENCE"
                continue
            if got not in ok:
                return "BELOW-BASELINE"                   # any concrete miss dominates
        return verdict
    raise ValueError(f"not a cold dimension: {dim}")


# ── checkout-freshness guard (#2851) ─────────────────────────────────────────
def is_stale(report: dict) -> bool:
    """A report is STALE-CHECKOUT when its tree was dirty, behind main, or generated from
    an unverifiable origin ref. Fail-closed: any field we can't trust ⇒ stale. A report with
    no provenance block at all (legacy / pre-#2851) cannot prove freshness ⇒ stale."""
    p = report.get("provenance")
    if not isinstance(p, dict):
        return True
    if p.get("dirty") is not False:                  # anything but an explicit clean flag ⇒ stale
        return True                                  # (uncommitted changes, OR missing/garbled field)
    if p.get("behind_main") not in (0, "0"):         # behind OR "unknown"/absent ⇒ stale (BC2)
        return True
    if p.get("ahead_main") not in (0, "0"):          # local commits not on origin/main ⇒ non-canonical
        return True
    age = p.get("origin_ref_age_h")
    if age in (None, "unknown"):                     # can't prove the local origin ref is fresh
        return True
    if isinstance(age, bool) or not isinstance(age, (int, float)):
        return True                                  # non-numeric age is not trustworthy evidence
    # Out of the trust window in EITHER direction ⇒ stale (BC2). A negative age means the ref
    # mtime is in the future (clock skew / NTP correction / VM jump) — unverifiable, so fail
    # closed rather than fail open on `age > MAX` alone.
    return not (0 <= age <= ORIGIN_REF_MAX_H)


# ── uniform-dim equality + ties (C1) ─────────────────────────────────────────
def uniform_verdict(dim: str, values: list) -> str:
    real = [v for v in values if v not in (None, "unknown", "n/a")]
    if dim in EXPECTED_DIFF_DIMS:                   # MINOR: evidence precedes expected-diff suppression
        return "EXPECTED-DIFF" if real else "PENDING"
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


def provider_rows() -> list[str]:
    return [f"harness:{provider}:{capability}"
            for provider in PROVIDERS for capability in CAPABILITIES]


def parse_provider_row(dim: str) -> tuple[str, str] | None:
    parts = dim.split(":", 2)
    if len(parts) != 3 or parts[0] != "harness":
        return None
    provider, capability = parts[1], parts[2]
    if provider not in PROVIDERS or capability not in CAPABILITIES:
        return None
    return provider, capability


def provider_capability_verdict(provider: str, capability: str,
                                provider_record: dict, claude_record: dict) -> str:
    if not isinstance(provider_record, dict) or not isinstance(claude_record, dict):
        return "MISSING-EVIDENCE"
    provider_present = provider_record.get("present") is True
    cap = provider_record.get(capability) or {}
    if cap.get("status") == "unknown":
        return "MISSING-EVIDENCE"
    if provider == "claude":
        if not provider_present:
            return "ABSENT"
        return "PARITY" if cap.get("status") == "present" else "MISSING-EVIDENCE"

    claude_cap = claude_record.get(capability) or {}
    if claude_cap.get("status") == "unknown":
        return "MISSING-EVIDENCE"
    if claude_record.get("present") is not True or claude_cap.get("status") != "present":
        return "MISSING-EVIDENCE"
    if not provider_present:
        return "ABSENT"
    status = cap.get("status")
    if status == "present":
        return "PARITY"
    if status == "expected_divergence":
        return ("EXPECTED-DIVERGENCE"
                if cap.get("reason") in EXPECTED_DIVERGENCE_REASONS else "DIVERGES")
    if status == "absent":
        return "DIVERGES"
    return "MISSING-EVIDENCE"


def provider_row_verdict(dim: str, report: dict) -> str:
    parsed = parse_provider_row(dim)
    if parsed is None:
        return "MISSING-EVIDENCE"
    if report.get("schema_version") != 4:
        return "MISSING-EVIDENCE"
    provider, capability = parsed
    harness = report.get("dimensions", {}).get("provider_harness")
    if not isinstance(harness, dict) or harness.get("schema_version") != 1:
        return "MISSING-EVIDENCE"
    providers = harness.get("providers") or {}
    return provider_capability_verdict(
        provider, capability, providers.get(provider), providers.get("claude"))


# ── precedence orchestrator (C3) ─────────────────────────────────────────────
def verdict_for(dim: str, machine: str, reports: dict, baselines: dict,
                roster: dict, probed_repos: list[str]) -> str:
    status = roster.get(machine, {}).get("status", "active")
    # BC3: a status:unreachable roster entry DOMINATES any present report (a stale/old report
    # on an unreachable machine must never grade as STALE-CHECKOUT or get graded on its merits).
    if status == "unreachable":
        return "UNREACHABLE"
    rep = reports.get(machine)
    # CC4: a malformed report (parse error / non-dict / missing dimensions) is NOT evidence.
    valid = isinstance(rep, dict) and "_error" not in rep and isinstance(rep.get("dimensions"), dict)
    if not valid:
        return "MISSING-EVIDENCE"
    # #2851: a contaminated checkout grades STALE-CHECKOUT for EVERY dim of that machine — below
    # unreachable/missing-evidence, above the cold/uniform split.
    if is_stale(rep):
        return "STALE-CHECKOUT"
    if parse_provider_row(dim) is not None:
        return provider_row_verdict(dim, rep)
    if dim in COLD_DIMS:
        return cold_verdict(dim, rep, baselines.get(machine), probed_repos)
    # Stale peers are EXCLUDED from the uniform value list so a stale report can never
    # manufacture a false EQUAL/DIVERGES/NO-MAJORITY for the fresh machines (A2/BC4).
    values = [extract_value(dim, reports[m]) for m in roster
              if roster[m].get("status") == "active"
              and isinstance(reports.get(m), dict) and "_error" not in reports[m]
              and isinstance(reports[m].get("dimensions"), dict)
              and not is_stale(reports[m])]
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


BASE_DISPLAY_DIMS = ["compute", "data_access", "solvers", "harness", "python_cmd", "skills",
                     "kanban", "memory", "behavior", "scheduler"]
DISPLAY_DIMS = BASE_DISPLAY_DIMS + provider_rows()


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
tbody th{{background:#edf2f7}}.conforms,.equal,.parity{{background:#c6f6d5}}
.below-baseline,.diverges{{background:#fed7d7}}.no-majority,.missing-baseline{{background:#feebc8}}
.expected-diff,.expected-divergence{{background:#e9d8fd}}
.pending,.missing-evidence{{background:#fffaf0}}.unreachable,.absent{{background:#f7fafc;color:#a0aec0}}
.stale-checkout{{background:#e2e8f0;color:#4a5568;font-style:italic}}</style></head>
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
