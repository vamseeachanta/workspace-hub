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
from datetime import date, datetime, timezone
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
PROVIDERS = ("claude", "codex", "hermes", "gemini")
CAPABILITIES = ("memory:read", "skills:invoke", "workflow:gates")
# Keep in sync with scripts/readiness/provider_harness_parity.py (#3206 / #3209
# drift note): both copies must carry the same divergence reasons.
EXPECTED_DIVERGENCE_REASONS = {"external_skill_dirs_configured", "gemini_skill_dispatch_unsupported"}

# Session-curation freshness thresholds: the "session analysis & memory curation" line item
# grades on TIME-SINCE-LAST-CURATION, computed at BUILD time vs real now — NOT the COLD/UNIFORM
# model. ≤12h fresh (green), ≤24h stale (orange), >24h expired (red). This is precisely why the
# matrix must rebuild at least DAILY independent of the curation cron: a frozen render would never
# age a dead curation past green (the dead-man's-switch). See schedule-tasks.yaml equality-matrix-refresh.
CURATION_STALE_H = 12
CURATION_EXPIRED_H = 24
# Memory-freshness thresholds (#3255) — keep in sync with audit_memory_freshness.py
# (MEMORY_STALE_H / MEMORY_EXPIRED_H). The daily bridge cadence = 1 missed run at 36h,
# ~3 at 72h. Recomputed at BUILD time (worst surface age + time-since-audit) so a dead audit
# ages the cell past green — the same dead-man's-switch as session_curation.
MEMORY_STALE_H = 36
MEMORY_EXPIRED_H = 72

# Harness-checkup clutter threshold (#3408) — keep in sync with audit_harness_checkup.py
# (CLUTTER_SKILLS). More lifetime-unused user skills than this grades the box's checkup cell
# CHECKUP-DRIFTED (a SOFT signal — extension clutter — never red).
CHECKUP_CLUTTER_SKILLS = 15

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


def skills_verdict(pairs: list) -> str:
    """repo_skill_count is fully determined by the checkout SHA, and machines self-report
    days apart (weekly Windows cadence vs daily Linux), so clones at DIFFERENT SHAs
    legitimately count differently — pure checkout skew that graded DIVERGES forever
    (e.g. 417/416/415 across four boxes). Only a count mismatch at the SAME SHA is real
    divergence (dirty overlay / partial checkout / broken skill links); cross-SHA
    mismatches grade EXPECTED-DIFF. Fail-closed: a mismatch involving a report with no
    checkout_sha cannot be attributed to skew and stays DIVERGES."""
    real = [(sha, count) for sha, count in pairs if count not in (None, "unknown", "n/a")]
    if len(real) < 2:
        return "PENDING"
    if len({count for _, count in real}) == 1:
        return "EQUAL"
    by_sha: dict = {}
    for sha, count in real:
        by_sha.setdefault(sha, set()).add(count)
    if any(len(counts) > 1 for counts in by_sha.values()):
        return "DIVERGES"
    if None in by_sha or "" in by_sha:
        return "DIVERGES"
    return "EXPECTED-DIFF"


# ── session-curation freshness (time-since-last-run, graded at build time) ───
def freshness_verdict(report: dict, now: datetime | None = None) -> str:
    """Grade the session-curation cell by age of `last_curated_at` vs now.
    CURATED-FRESH ≤12h · CURATED-STALE ≤24h · CURATED-EXPIRED >24h · MISSING-EVIDENCE on
    no/garbled/future stamp (fail-closed: an untrustworthy timestamp is never 'fresh')."""
    sc = report.get("dimensions", {}).get("session_curation")
    if not isinstance(sc, dict):
        return "MISSING-EVIDENCE"
    stamp = sc.get("last_curated_at")
    if not isinstance(stamp, str):
        return "MISSING-EVIDENCE"
    try:
        ts = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return "MISSING-EVIDENCE"
    # Compare in UTC. The collector emits an aware UTC stamp; a legacy naive stamp is assumed
    # UTC so a fleet of boxes in different timezones (macbook travels; Windows hosts) can't
    # mask real staleness by grading a remote local stamp against the build box's local clock.
    now = now or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    age_h = (now - ts).total_seconds() / 3600.0
    if age_h < 0:                       # future stamp ⇒ clock skew / untrustworthy ⇒ fail closed
        return "MISSING-EVIDENCE"
    if age_h <= CURATION_STALE_H:
        return "CURATED-FRESH"
    if age_h <= CURATION_EXPIRED_H:
        return "CURATED-STALE"
    return "CURATED-EXPIRED"


# ── skill-currency verdict (cross-provider skill drift vs canonical; #3249) ──
def skill_currency_verdict(report: dict) -> str:
    """Map the audit FACTS (emitted by audit_skill_currency.py) to a verdict. Precedence:
    SKILLS-DRIFTED (unexpected family diff) > SKILLS-INDEX-STALE (index has dangling entries) >
    EXPECTED-DIVERGENCE (only allowlisted provider-specific families differ) > SKILLS-CURRENT.
    Fail-closed (MISSING-EVIDENCE) when the audit couldn't read the tree or a count is garbled —
    an unreadable surface must never grade green."""
    sc = report.get("dimensions", {}).get("skill_currency")
    if not isinstance(sc, dict):
        return "MISSING-EVIDENCE"
    if not isinstance(sc.get("audited_at"), str):
        return "MISSING-EVIDENCE"
    cc = sc.get("canonical_count")
    if not isinstance(cc, int) or isinstance(cc, bool) or cc <= 0:   # tree unreadable ⇒ no evidence
        return "MISSING-EVIDENCE"
    if sc.get("gemini_present"):
        unexpected = sc.get("gemini_unexpected")
        if not isinstance(unexpected, int) or isinstance(unexpected, bool):
            return "MISSING-EVIDENCE"
    else:
        unexpected = 0
    if unexpected > 0:
        return "SKILLS-DRIFTED"
    # Index integrity via dangling-entry count. None ⇒ the index was UNREADABLE while the tree read
    # fine — fail-closed to INDEX-STALE (a broken index needs regeneration), never silently green.
    idx = sc.get("index_dangling")
    if idx is None:
        return "SKILLS-INDEX-STALE"
    if not isinstance(idx, int) or isinstance(idx, bool):
        return "MISSING-EVIDENCE"
    if idx > 0:
        return "SKILLS-INDEX-STALE"
    expected = sc.get("gemini_expected")
    if isinstance(expected, int) and not isinstance(expected, bool) and expected > 0:
        return "EXPECTED-DIVERGENCE"
    return "SKILLS-CURRENT"


# ── memory-freshness verdict (#3255) — recomputed vs now (dead-man's-switch) ──
def memory_freshness_verdict(report: dict, now: datetime | None = None) -> str:
    """Grade memory staleness from the audit's worst (oldest) surface age, RECOMPUTED at build
    time: current_age = worst_age_hours + (now - audited_at). So a dead audit cron ages the cell
    (the frozen state file can't stay falsely green). MEMORY-FRESH ≤36h / MEMORY-STALE ≤72h /
    MEMORY-EXPIRED >72h. Fail-closed MISSING-EVIDENCE on missing/garbled/future evidence."""
    mf = report.get("dimensions", {}).get("memory_freshness")
    if not isinstance(mf, dict):
        return "MISSING-EVIDENCE"
    stamp = mf.get("audited_at")
    worst = mf.get("worst_age_hours")
    if not isinstance(stamp, str) or isinstance(worst, bool) or not isinstance(worst, (int, float)):
        return "MISSING-EVIDENCE"
    try:
        ts = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return "MISSING-EVIDENCE"
    now = now or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    since_audit_h = (now - ts).total_seconds() / 3600.0
    if since_audit_h < 0 or worst < 0:          # future stamp / negative age ⇒ untrustworthy
        return "MISSING-EVIDENCE"
    current_age = worst + since_audit_h
    if current_age <= MEMORY_STALE_H:
        return "MEMORY-FRESH"
    if current_age <= MEMORY_EXPIRED_H:
        return "MEMORY-STALE"
    return "MEMORY-EXPIRED"


# ── skill-link-health verdict (#3251) — are shared-skill links propagated? ───
def skill_link_health_verdict(report: dict) -> str:
    """Map the resync-skill-links.sh facts to a verdict: SKILL-LINKS-DRIFTED when any shared-skill
    link is repairable (dangling/flattened/missing) on a real ecosystem clone — propagate-ecosystem
    needs re-running — else SKILL-LINKS-OK. Fail-closed MISSING-EVIDENCE on missing/garbled facts."""
    slh = report.get("dimensions", {}).get("skill_link_health")
    if not isinstance(slh, dict):
        return "MISSING-EVIDENCE"
    if not isinstance(slh.get("audited_at"), str):
        return "MISSING-EVIDENCE"
    repos = slh.get("repos_total")
    if isinstance(repos, bool) or not isinstance(repos, int) or repos <= 0:
        return "MISSING-EVIDENCE"        # nothing discovered ⇒ no evidence, NOT silently 'healthy'
    repairable = slh.get("repairable")
    if isinstance(repairable, bool) or not isinstance(repairable, int):
        return "MISSING-EVIDENCE"
    return "SKILL-LINKS-DRIFTED" if repairable > 0 else "SKILL-LINKS-OK"


# ── harness-checkup verdict (#3408) — /doctor hygiene per box ────────────────
def harness_checkup_verdict(report: dict) -> str:
    """Map the audit_harness_checkup.py facts to a verdict. Fail-closed MISSING-EVIDENCE on
    missing/garbled facts or absent core evidence (settings_parse_ok / install_method). Mirrors
    the audit's pure checkup_category — hard defects (broken settings / duplicate installs / broken
    agents) → CHECKUP-BROKEN (red); soft drift (behind latest / non-auto default / extension
    clutter) → CHECKUP-DRIFTED (amber). version_current None (no network) is NOT drift."""
    hc = report.get("dimensions", {}).get("harness_checkup")
    if not isinstance(hc, dict) or not isinstance(hc.get("audited_at"), str):
        return "MISSING-EVIDENCE"
    sok = hc.get("settings_parse_ok")
    install = hc.get("install_method")
    if sok is None or not isinstance(install, str) or not install:
        return "MISSING-EVIDENCE"            # could not audit ⇒ never silently green
    dup = hc.get("duplicate_installs")
    bad = hc.get("broken_agents")
    if (sok is False
            or (isinstance(dup, int) and not isinstance(dup, bool) and dup > 0)
            or (isinstance(bad, int) and not isinstance(bad, bool) and bad > 0)):
        return "CHECKUP-BROKEN"
    us = hc.get("unused_skills")
    up = hc.get("unused_plugins")
    if (hc.get("version_current") is False
            or hc.get("auto_mode_default") is False
            or (isinstance(us, int) and not isinstance(us, bool) and us > CHECKUP_CLUTTER_SKILLS)
            or (isinstance(up, int) and not isinstance(up, bool) and up > 0)):
        return "CHECKUP-DRIFTED"
    return "CHECKUP-OK"


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
        q = d.get("kanban", {}).get("dispatch_queues")
        # Canonicalize as a sorted membership list: historical evidence was emitted under
        # locale-dependent collation on Linux vs byte order under Git Bash, so the SAME
        # queue set arrived as differently-ordered strings and graded DIVERGES. Order is
        # a collector artifact; membership is the signal.
        return ",".join(sorted(q.split(","))) if isinstance(q, str) else q
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
    if dim == "session_curation":           # freshness family — graded vs real now, not peers
        return freshness_verdict(rep)
    if dim == "skill_currency":             # cross-provider skill-drift family — per-box facts
        return skill_currency_verdict(rep)
    if dim == "memory_freshness":           # memory-staleness family — recomputed vs now
        return memory_freshness_verdict(rep)
    if dim == "skill_link_health":          # shared-skill-link propagation — per-box facts
        return skill_link_health_verdict(rep)
    if dim == "harness_checkup":            # /doctor hygiene — per-box facts (currency/settings/mode)
        return harness_checkup_verdict(rep)
    if dim in COLD_DIMS:
        return cold_verdict(dim, rep, baselines.get(machine), probed_repos)
    # Stale peers are EXCLUDED from the uniform value list so a stale report can never
    # manufacture a false EQUAL/DIVERGES/NO-MAJORITY for the fresh machines (A2/BC4).
    fresh = [m for m in roster
             if roster[m].get("status") == "active"
             and isinstance(reports.get(m), dict) and "_error" not in reports[m]
             and isinstance(reports[m].get("dimensions"), dict)
             and not is_stale(reports[m])]
    if dim == "skills":
        return skills_verdict([(reports[m].get("provenance", {}).get("checkout_sha"),
                                extract_value(dim, reports[m])) for m in fresh])
    return uniform_verdict(dim, [extract_value(dim, reports[m]) for m in fresh])


# ── load + render ────────────────────────────────────────────────────────────
def load_reports() -> dict[str, dict]:
    out = {}
    for f in sorted(STATE.glob("equality-*.yaml")):
        machine = f.stem[len("equality-"):]
        try:
            out[machine] = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            out[machine] = {"_error": str(e)}
    return out


BASE_DISPLAY_DIMS = ["compute", "data_access", "solvers", "harness", "python_cmd", "skills",
                     "kanban", "memory", "behavior", "scheduler", "session_curation",
                     "skill_currency", "memory_freshness", "skill_link_health", "harness_checkup"]
DISPLAY_DIMS = BASE_DISPLAY_DIMS + provider_rows()

# ── render grouping (#2801 collapsible-rows enhancement) ─────────────────────
# The matrix assesses TWO equivalences on one page — machine equivalence (is each box
# up to its declared hardware/solver baseline?) and repo/harness equivalence (are the
# clones, skills, and runtime config identical across boxes?). Rows are grouped so each
# group collapses to a single per-machine rollup the user can scan first ("what really
# matters / what work is needed where"), then expand for the per-dimension detail.
# Groups don't reorder DISPLAY_DIMS (the verdict engine + tests key off that list);
# they only drive HTML layout. Every BASE_DISPLAY_DIM + provider row lands in exactly
# one group.
GROUPS = [
    ("machine", "Machine equivalence — hardware &amp; solvers", ["compute", "solvers"]),
    ("repo", "Repo equivalence — clones · skills · kanban · memory",
        ["data_access", "skills", "kanban", "memory"]),
    ("config", "Harness equivalence — providers · python · behavior · scheduler",
        ["harness", "python_cmd", "behavior", "scheduler"]),
    ("provider", "Provider capability parity — per runtime", provider_rows()),
    ("curation", "Session analysis &amp; memory curation — daily freshness", ["session_curation"]),
    ("skills-currency", "Skill currency — all providers up to date vs canonical", ["skill_currency"]),
    ("memory-freshness", "Memory freshness — memory surfaces refreshed recently", ["memory_freshness"]),
    ("skill-links", "Skill-link health — shared skills propagated to ecosystem repos", ["skill_link_health"]),
    ("harness-checkup", "Harness checkup — /doctor hygiene per box (version · settings · mode)", ["harness_checkup"]),
]

# Worst-of severity for the collapsed group rollup. Higher = more operator attention.
# A group's rollup cell shows the worst verdict among its dims for that machine; an
# all-good group collapses to a single green "OK" so a clean box reads at a glance.
ROLLUP_SEVERITY = {
    "BELOW-BASELINE": 6, "DIVERGES": 6, "CURATED-EXPIRED": 6, "SKILLS-DRIFTED": 6, "MEMORY-EXPIRED": 6,
    "CHECKUP-BROKEN": 6,
    "MISSING-BASELINE": 5, "NO-MAJORITY": 5, "CURATED-STALE": 5, "SKILLS-INDEX-STALE": 5, "MEMORY-STALE": 5,
    "SKILL-LINKS-DRIFTED": 5, "CHECKUP-DRIFTED": 5,
    "MISSING-EVIDENCE": 4, "PENDING": 4,
    "STALE-CHECKOUT": 3,
    "EXPECTED-DIFF": 1, "EXPECTED-DIVERGENCE": 1, "UNREACHABLE": 1, "ABSENT": 1,
    "CONFORMS": 0, "EQUAL": 0, "PARITY": 0, "CURATED-FRESH": 0, "SKILLS-CURRENT": 0, "MEMORY-FRESH": 0,
    "SKILL-LINKS-OK": 0, "CHECKUP-OK": 0,
}


def rollup_verdict(verdicts: list[str]) -> tuple[str, str]:
    """(label, css_class) for a group's per-machine rollup cell. Unknown verdicts grade
    at MISSING-EVIDENCE severity (fail-soft, never silently 'OK')."""
    if not verdicts:
        return ("n/a", "na")
    worst = max(verdicts, key=lambda v: ROLLUP_SEVERITY.get(v, 4))
    if ROLLUP_SEVERITY.get(worst, 4) == 0:
        return ("OK", "ok")
    return (worst, worst.lower())


# ── remediation playbook (verdict → action) — keep in sync with the verdict→fix table in
#    .claude/skills/workspace-hub/ecosystem-equivalence-reconcile/SKILL.md + reconcile-ecosystem.sh
OK_VERDICTS = {"CONFORMS", "EQUAL", "PARITY", "EXPECTED-DIFF", "EXPECTED-DIVERGENCE",
               "UNREACHABLE", "ABSENT", "CURATED-FRESH", "SKILLS-CURRENT", "MEMORY-FRESH",
               "SKILL-LINKS-OK", "CHECKUP-OK"}


def remediate(dim: str, verdict: str) -> tuple[str, str, bool] | None:
    """(action, owner, by_design) for a non-OK cell; None if the cell needs no action.
    by_design=True means the cell can't/shouldn't reach green — it's expected, not a defect."""
    if verdict in OK_VERDICTS:
        return None
    is_provider = dim.startswith("harness:")
    if verdict == "MISSING-EVIDENCE":
        if is_provider:
            return ("capability not detected — or no Claude baseline on this host "
                    "(a Hermes-only box grades provider rows MISSING-EVIDENCE by design)",
                    "by-design / operator", True)
        return ("no fresh report on this box — run the collector "
                "(equality-matrix-cron.sh; equality-report.ps1 on Windows)", "this box", False)
    if verdict == "STALE-CHECKOUT":
        return ("checkout dirty / behind / stale ref — clean the tree, git fetch origin main, re-collect",
                "this box", False)
    if verdict == "BELOW-BASELINE":
        if dim == "solvers":
            return ("solver licence probe emits 'present', baseline wants 'licensed' — "
                    "Windows licence-probe follow-up", "operator (Windows)", True)
        if dim == "data_access":
            return ("a required tier-1 repo isn't cloned here — clone the missing sibling", "this box", False)
        if dim == "compute":
            return ("under the declared cores/ram/gpu floor — upgrade box or retune harness-config floor",
                    "operator", False)
        return ("below the declared baseline — inspect this box's equality report", "operator", False)
    if verdict in ("DIVERGES", "NO-MAJORITY"):
        if is_provider:
            return ("capability diverges from the Claude baseline — refresh the report; "
                    "if persistent, install/repair that provider on this box", "this box", False)
        if dim == "skills":
            return ("skills count differs — usually a tracked symlink materialized as a text file; "
                    "git config core.symlinks true, then rm + git checkout the symlink paths", "this box", False)
        if dim in ("harness", "behavior"):
            return ("runtime/config drift — rebuild + install the soul runtime, then re-collect", "this box", False)
        if dim == "scheduler":
            return ("cron jobs differ — reconcile via setup-cron.sh --check, then re-collect", "this box", False)
        return ("differs from peers — OFTEN a stale-peer artifact; refresh ALL machines' reports first, "
                "then reconcile any genuine config drift", "all boxes", False)
    if verdict == "MISSING-BASELINE":
        return ("no declared baseline for this dim — add one in harness-config.yaml", "operator", False)
    if verdict in ("CURATED-STALE", "CURATED-EXPIRED"):
        return ("session analysis + memory curation is stale (>12h orange / >24h red) — run "
                "the collector (bash scripts/curation/curate-session-memory.sh; "
                "curate-session-memory.ps1 on Windows) or repair the every-6h cron", "this box", False)
    if verdict == "SKILLS-DRIFTED":
        return ("a provider's skill families UNEXPECTEDLY differ from canonical — reconcile via "
                "scripts/propagate-ecosystem.sh, or if the difference is intended, allowlist it in "
                "harness-config.yaml expected_skill_divergence", "this box", False)
    if verdict == "SKILLS-INDEX-STALE":
        return ("the skills index has dangling entries (paths no longer in the tree) — regenerate "
                ".claude/skills-index.yaml (skills-curation cron / generator)", "this box", False)
    if verdict in ("MEMORY-STALE", "MEMORY-EXPIRED"):
        return ("memory surfaces are stale (>36h orange / >72h red) — run the memory bridge "
                "(scripts/memory/bridge-hermes-claude.sh) or repair its cron", "this box", False)
    if verdict == "SKILL-LINKS-DRIFTED":
        return ("shared-skill links are missing/broken on ecosystem repos (froze at link time) — "
                "re-sync via scripts/skills/resync-skill-links.sh --apply (or propagate-ecosystem.sh "
                "--skills-only)", "this box", False)
    if verdict == "CHECKUP-BROKEN":
        return ("harness hygiene is broken — a settings file fails to parse, there are duplicate "
                "claude installs, or an agent def is broken/colliding; run /doctor on this box and "
                "apply its fixes", "this box", False)
    if verdict == "CHECKUP-DRIFTED":
        return ("harness hygiene drift — behind the latest release, auto mode isn't the default, or "
                "unused skills/plugins have accumulated; run /doctor (claude update; set auto default; "
                "prune unused extensions)", "this box", False)
    return ("investigate this cell's report", "operator", False)


def _short_dim(dim: str) -> str:
    return dim[len("harness:"):] if dim.startswith("harness:") else dim


def equivalence_section(vmap: dict, machines: list[str], roster: dict,
                        reporting_set: set[str]) -> str:
    """Per-machine 'what to do to reach equivalence' cards, generated from live verdicts."""
    cards = []
    for m in machines:
        if roster[m].get("status") != "active":
            continue
        gaps = [(d, vmap[(d, m)]) for d in DISPLAY_DIMS if remediate(d, vmap[(d, m)])]
        role = roster[m].get("role", "—")
        if not gaps:
            cards.append(f'<div class="fix-card ok-card"><b>{m}</b> '
                         f'<small>({role})</small> — ✅ at equivalence, nothing to do.</div>')
            continue
        # A box with NO report at all: every cell is MISSING-EVIDENCE for one reason (no report).
        # One action fixes all of them — don't mislabel its provider rows "by design".
        if m not in reporting_set:
            cards.append(
                f'<div class="fix-card"><b>{m}</b> <small>({role}, {len(gaps)} gaps)</small>'
                f'<div class="head">➤ Not reporting — run the collector once to populate all '
                f'{len(gaps)} cells.</div><ul><li>collector: '
                f'<code>bash scripts/readiness/equality-matrix-cron.sh</code> '
                f'(Windows: <code>scripts\\windows\\equality-report.ps1</code>) <small>[this box]</small>'
                f'</li></ul></div>')
            continue
        # bucket gaps by identical remediation so repeated dims collapse into one line
        bucket: dict[tuple[str, str, bool], list[str]] = {}
        for d, v in gaps:
            bucket.setdefault(remediate(d, v), []).append(d)  # type: ignore[arg-type]
        if any(v in ("DIVERGES", "NO-MAJORITY") for _, v in gaps):
            head = ("Mostly cross-machine divergence — often a stale peer report. "
                    "Refresh EVERY machine's report first, then reconcile any real drift.")
        else:
            head = "Targeted fixes below."
        items = []
        for (action, owner, design), dims in bucket.items():
            shown = [_short_dim(x) for x in dims]
            label = (", ".join(shown) if len(shown) <= 4
                     else f"{len(shown)} rows ({shown[0]} …)")
            tag = ' <i>(by design — not a defect)</i>' if design else ''
            items.append(f'<li class="{"design" if design else ""}"><code>{label}</code> → '
                         f'{action} <small>[{owner}]</small>{tag}</li>')
        cards.append(
            f'<div class="fix-card"><b>{m}</b> <small>({role}, {len(gaps)} gap'
            f'{"s" if len(gaps) != 1 else ""})</small>'
            f'<div class="head">➤ {head}</div><ul>{"".join(items)}</ul></div>')
    return "".join(cards)


def main() -> None:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    roster = load_roster(config)
    baselines = load_baselines(config)
    probed = (config.get("tier1_repos") or TIER1_DEFAULT)
    reports = load_reports()

    machines = list(roster)
    # Compute every verdict once (cells + rollups both consume it).
    vmap = {(dim, m): verdict_for(dim, m, reports, baselines, roster, probed)
            for dim in DISPLAY_DIMS for m in machines}

    # --json: emit the verdict map for tooling (reconcile-ecosystem.sh consumes this
    # instead of scraping HTML). Optionally scope to one machine via --machine <slug>.
    if "--json" in sys.argv:
        only = None
        if "--machine" in sys.argv:
            idx = sys.argv.index("--machine")
            only = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        targets = [only] if only else machines
        emit = {m: {dim: vmap[(dim, m)] for dim in DISPLAY_DIMS}
                for m in targets if m in roster}
        print(json.dumps(emit, indent=2))
        return

    rows = []
    for gid, title, dims in GROUPS:
        # Collapsed group header: per-machine worst-of rollup + twist toggle.
        rollups = "".join(
            (lambda lab, cls: f'<td class="{cls}">{lab}</td>')(
                *rollup_verdict([vmap[(d, m)] for d in dims]))
            for m in machines)
        rows.append(
            f'<tr class="grp" data-group="{gid}">'
            f'<th><span class="twist">&#9654;</span> {title} '
            f'<small>({len(dims)} checks)</small></th>{rollups}</tr>')
        # Detail rows (default collapsed). Per-dimension <th>{dim}</th> kept verbatim
        # so the verdict-engine HTML contract / tests stay stable.
        for dim in dims:
            cells = "".join(f'<td class="{vmap[(dim, m)].lower()}">{vmap[(dim, m)]}</td>'
                            for m in machines)
            rows.append(f'<tr class="detail" data-group="{gid}"><th>{dim}</th>{cells}</tr>')

    cols = "".join(
        f"<th>{m}<br><small>{roster[m].get('role', '—')}<br>{roster[m].get('status')}</small></th>"
        for m in machines)
    reporting = sum(1 for m in roster if roster[m].get("status") == "active" and m in reports)
    active = sum(1 for m in roster if roster[m].get("status") == "active")

    # Per-machine notes (config `notes` field, public-safe role-slug prose). Rendered so
    # the operator can see "what each box is for + what work belongs there" beside the grid.
    machine_notes = "".join(
        f"<li><b>{m}</b> <small>({roster[m].get('role', '—')})</small> — {roster[m]['notes']}</li>"
        for m in machines if roster[m].get("notes"))
    notes_block = f"<ul>{machine_notes}</ul>" if machine_notes else ""

    # "Achieving equivalence" — per-machine actions generated from the live verdicts.
    equiv_cards = equivalence_section(vmap, machines, roster, set(reports))

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Machine-Equality Matrix — #2801</title>
<style>body{{font:14px/1.5 system-ui,sans-serif;margin:2rem;max-width:1100px}}table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:.4rem .6rem;font-size:.8rem;text-align:center}}thead th{{background:#2d3748;color:#fff}}
tbody th{{background:#edf2f7;text-align:left}}.conforms,.equal,.parity,.ok,.curated-fresh,.skills-current,.memory-fresh{{background:#c6f6d5}}.ok{{font-weight:700}}
.below-baseline,.diverges,.curated-expired,.skills-drifted,.memory-expired{{background:#fed7d7}}.no-majority,.missing-baseline,.curated-stale,.skills-index-stale,.memory-stale,.skill-links-drifted{{background:#feebc8}}.skill-links-ok{{background:#c6f6d5}}
.expected-diff,.expected-divergence{{background:#e9d8fd}}
.pending,.missing-evidence{{background:#fffaf0}}.unreachable,.absent,.na{{background:#f7fafc;color:#a0aec0}}
.stale-checkout{{background:#e2e8f0;color:#4a5568;font-style:italic}}
tr.grp{{cursor:pointer}}tr.grp th{{background:#1a202c;color:#fff;border-color:#2d3748}}tr.grp td{{color:#1a202c;border-color:#cbd5e0;font-weight:800;box-shadow:inset 0 0 0 9999px rgba(0,0,0,.04)}}
tr.grp .twist{{color:#90cdf4;font-size:.7rem}}
tr.detail{{display:none}}tr.detail th{{padding-left:1.8rem;font-weight:400}}
.note{{background:#fffaf0;border-left:4px solid #ed8936;padding:.5rem .9rem;margin:.6rem 0;border-radius:4px}}
.legend span{{display:inline-block;padding:.15rem .5rem;margin:.12rem;border-radius:3px;font-size:.72rem;border:1px solid #ccc}}
.prompt{{background:#1a202c;color:#e2e8f0;padding:.6rem .9rem;border-radius:6px;margin:.6rem 0;font-size:.82rem}}
.prompt code{{background:#2d3748;color:#90cdf4;padding:.05rem .3rem;border-radius:3px}}
.genprompt{{background:#ebf8ff;border:1px solid #90cdf4;border-left:4px solid #3182ce;padding:.6rem .9rem;margin:.7rem 0;border-radius:6px;font-size:.85rem}}
.genprompt .cmd{{display:flex;align-items:center;gap:.5rem;margin:.45rem 0}}
.genprompt .cmd>code{{background:#1a202c;color:#90cdf4;padding:.35rem .55rem;border-radius:4px;font-size:.82rem;flex:1;overflow-x:auto;white-space:nowrap}}
.genprompt small code{{background:#dbeafe;color:#1e40af;padding:.02rem .25rem;border-radius:3px}}
.copybtn{{background:#3182ce;color:#fff;border:0;padding:.32rem .75rem;border-radius:4px;cursor:pointer;font-size:.75rem;flex:none}}.copybtn:active{{background:#2c5282}}
.fix-card{{border:1px solid #e2e8f0;border-left:4px solid #ed8936;border-radius:6px;padding:.5rem .8rem;margin:.5rem 0}}
.fix-card.ok-card{{border-left-color:#48bb78}}.fix-card .head{{color:#c05621;font-weight:600;margin:.2rem 0}}
.fix-card ul{{margin:.3rem 0 .1rem;padding-left:1.2rem}}.fix-card li{{margin:.15rem 0}}
.fix-card li.design{{color:#718096}}.fix-card code{{background:#edf2f7;padding:.03rem .25rem;border-radius:3px;font-size:.76rem}}</style>
<noscript><style>tr.detail{{display:table-row}}</style></noscript></head>
<body><h1>Machine &amp; Repo Equivalence Matrix</h1>
<p>#2801 · {date.today().isoformat()} · reporting {reporting}/{active} active machines ·
<small>rows are grouped &amp; <b>collapsed by default</b> — click a dark group row to expand its per-dimension detail.</small></p>
<div class="note"><b>Work policy.</b> All development work — anything requiring OS equivalence — happens on the
<b>Linux boxes</b> (dev-primary, dev-secondary). The Windows hosts (ace-win-1, ace-win-2) are <b>scout-only</b>
(reconnaissance &amp; verification); <b>bug fixes are allowed</b> there, feature development is not. Both are
<b>licensed Windows hosts</b>: <b>ace-win-1</b> primarily runs <b>licensed solver runs</b>; <b>ace-win-2</b> primarily
handles <b>document ingestion, email, marketing &amp; admin</b>. Green/OK = at parity, nothing to do; red/orange =
work needed on that box; purple = intended difference (not a defect).</div>
<div class="genprompt"><b>🔄 Refresh equivalence on ANY machine</b> — paste on the box you are on (from <code>$WORKSPACE_HUB</code>):
<div class="cmd"><code id="genprompt-cmd">cd "$WORKSPACE_HUB" &amp;&amp; git pull --ff-only &amp;&amp; bash scripts/curation/curate-session-memory.sh</code><button class="copybtn" onclick="copyGenPrompt(this)">copy</button></div>
<small>Regenerates this box's session-curation · skill-currency · memory-freshness · skill-link cells and rebuilds this dashboard.
See the whole fleet: <code>uv run --script scripts/curation/curate_session_memory.py --collect</code> ·
Full reconciliation (read-only plan, then <code>--apply</code>): <code>bash scripts/readiness/reconcile-ecosystem.sh</code> ·
Claude Code / Gemini CLI: <code>/reconcile-ecosystem</code>. Works identically on every machine (Linux &amp; Windows Git Bash).</small></div>
<table><thead><tr><th>Group / Dimension</th>{cols}</tr></thead><tbody>{''.join(rows)}</tbody></table>
{f'<h3>Machine notes</h3>{notes_block}' if notes_block else ''}
<h2>Achieving equivalence — what to do</h2>
<div class="prompt"><b>To reconcile a box →</b> from <code>workspace-hub</code> run
<code>git pull --ff-only &amp;&amp; bash scripts/readiness/reconcile-ecosystem.sh</code> (read-only plan),
then <code>--apply</code> for the guard-gated safe fixes, or <code>--apply --equality</code> to refresh that
box's column here. Claude Code / Gemini CLI: <code>/reconcile-ecosystem</code>. Each box reconciles its own column.</div>
<p><small>Cards below are generated from the live verdicts. <b>Most "divergences" are stale-report
artifacts</b> — a single out-of-date report skews the cross-machine vote, so the first move is almost always
to refresh <i>every</i> active machine's report, then re-judge what genuinely differs.</small></p>
{equiv_cards}
<p class="legend"><b>Legend:</b>
<span class="ok">OK / CONFORMS / EQUAL / PARITY</span><span class="below-baseline">BELOW-BASELINE / DIVERGES</span>
<span class="no-majority">NO-MAJORITY / MISSING-BASELINE</span><span class="missing-evidence">PENDING / MISSING-EVIDENCE</span>
<span class="expected-diff">EXPECTED-DIFF / EXPECTED-DIVERGENCE</span><span class="stale-checkout">STALE-CHECKOUT</span>
<span class="curated-fresh">CURATED-FRESH ≤12h</span><span class="curated-stale">CURATED-STALE &gt;12h</span><span class="curated-expired">CURATED-EXPIRED &gt;24h</span>
<span class="skills-current">SKILLS-CURRENT</span><span class="skills-index-stale">SKILLS-INDEX-STALE</span><span class="skills-drifted">SKILLS-DRIFTED</span>
<span class="memory-fresh">MEMORY-FRESH ≤36h</span><span class="memory-stale">MEMORY-STALE &gt;36h</span><span class="memory-expired">MEMORY-EXPIRED &gt;72h</span>
<span class="skill-links-ok">SKILL-LINKS-OK</span><span class="skill-links-drifted">SKILL-LINKS-DRIFTED</span>
<span class="absent">UNREACHABLE / ABSENT / n/a</span></p>
<script>
document.querySelectorAll('tr.grp').forEach(function(h){{
  h.addEventListener('click',function(){{
    var g=h.dataset.group,open=h.classList.toggle('open');
    h.querySelector('.twist').innerHTML=open?'&#9660;':'&#9654;';
    document.querySelectorAll('tr.detail[data-group="'+g+'"]').forEach(function(r){{
      r.style.display=open?'table-row':'none';}});}});}});
function copyGenPrompt(btn){{
  var t=document.getElementById('genprompt-cmd').textContent, done=function(){{
    var o=btn.textContent;btn.textContent='copied!';setTimeout(function(){{btn.textContent=o;}},1200);}};
  if(navigator.clipboard&&navigator.clipboard.writeText){{navigator.clipboard.writeText(t).then(done,done);}}
  else{{var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();
    try{{document.execCommand('copy');}}catch(e){{}}document.body.removeChild(ta);done();}}
}}
</script></body></html>"""

    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / f"{date.today().isoformat()}-machine-equality-matrix.html"
    out.write_text(html, encoding="utf-8")
    # Stable (undated) alias so GitHub Pages serves a fixed "latest" URL that never
    # changes as the dated reports roll over (published by scripts/build_pages.py).
    latest = REPORTS / "machine-equality-matrix.html"
    latest.write_text(html, encoding="utf-8")
    print(f"wrote {out} (+ {latest.name} alias) ({reporting}/{active} active reporting)")
    if "--open" in sys.argv:
        import webbrowser
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
