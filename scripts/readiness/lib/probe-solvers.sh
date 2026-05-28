#!/usr/bin/env bash
# probe-solvers.sh — shared licensed-solver detection helpers (#2849, #2801 family).
#
# Single source of truth for "which diffraction/FEA solvers are present/licensed here?"
# Sourced by:
#   * scripts/readiness/collect-equality.sh  — emits the `solvers` equality dimension.
# (The standalone nightly R-ANSYS/R-ORCAFLEX checks were removed per #2849 decision 2:
#  the equality matrix `solvers` cell is the single source of truth — no nightly duplication.)
#
# Detection semantics (closed enum on status):
#   licensed = vendor binary/SDK present AND a licensing signal present
#              (import-success for the OrcFxAPI SDK, which a real solve fails-closed without;
#               or a license env var for ANSYS/AQWA).
#   present  = install root / SDK found but no licensing evidence.
#   absent   = neither found.
#   unknown  = the probe could not run (e.g. no python interpreter for an import probe).
#
# Output contract: each probe echoes ONE token on stdout from {licensed, present, absent, unknown}.
# A separate evidence token (how it was detected) is echoed by *_evidence helpers from the
# closed evidence enum {import, env, root, absent, unknown} — NEVER an absolute path
# (matches the collect-equality.sh data_access bare-name rule, no machine-layout leak).
#
# Every probe is failure-swallowing: a missing interpreter or unreadable dir yields a clean
# enum token, never a non-zero exit that would abort the sourcing script.

# Guard against double-sourcing (idempotent).
[[ -n "${__PROBE_SOLVERS_SH:-}" ]] && return 0
__PROBE_SOLVERS_SH=1

_ps_have() { command -v "$1" >/dev/null 2>&1; }

# Resolve a python interpreter for SDK import probes. Prefer a plain `python`
# (Windows Git-Bash convention); fall back to python3. Echoes "" if none.
_ps_python() {
  if _ps_have python; then echo python
  elif _ps_have python3; then echo python3
  else echo ""; fi
}

# ── ANSYS / AQWA: install-root detection (factored from the old nightly R-ANSYS) ──
# Echoes "absent" OR "present:<v252 v251 ...>" (latest last, sorted) — version dirs
# under the Windows ANSYS install root. NO absolute path is echoed (only the bare
# vNNN tokens). Linux/macOS have no such root → "absent".
probe_ansys_root() {
  local root="/c/Program Files/ANSYS Inc"
  [[ -d "$root" ]] || { echo "absent"; return 0; }
  local versions
  versions=$(ls "$root" 2>/dev/null | grep -E '^v[0-9]+$' | sort -V | tr '\n' ' ' | sed 's/ $//')
  [[ -z "$versions" ]] && { echo "absent"; return 0; }
  echo "present:${versions}"
}

# ── OrcaFlex install-root detection (Windows; bare version tokens only) ──────────
# Echoes "absent" OR "present:<11.5 11.6 ...>" — version dirs under the Orcina root.
probe_orcaflex_root() {
  local root="/c/Program Files (x86)/Orcina/OrcaFlex"
  [[ -d "$root" ]] || { echo "absent"; return 0; }
  local versions
  versions=$(ls "$root" 2>/dev/null | grep -E '^[0-9]+\.' | sort -V | tr '\n' ' ' | sed 's/ $//')
  [[ -z "$versions" ]] && { echo "absent"; return 0; }
  echo "present:${versions}"
}

# ── orcaflex solver status ──────────────────────────────────────────────────────
# licensed = `import OrcFxAPI` succeeds (the SDK is the licensed runtime gate);
# present  = install root found but no importable SDK;
# absent   = neither.
probe_orcaflex() {
  local py; py="$(_ps_python)"
  if [[ -n "$py" ]] && "$py" -c "import OrcFxAPI" >/dev/null 2>&1; then
    echo "licensed"; return 0
  fi
  case "$(probe_orcaflex_root)" in
    present:*) echo "present";;
    *)         echo "absent";;
  esac
}
probe_orcaflex_evidence() {
  local py; py="$(_ps_python)"
  if [[ -n "$py" ]] && "$py" -c "import OrcFxAPI" >/dev/null 2>&1; then echo "import"; return 0; fi
  case "$(probe_orcaflex_root)" in present:*) echo "root";; *) echo "absent";; esac
}

# ── orcawave solver status ───────────────────────────────────────────────────────
# OrcaWave shares the OrcFxAPI SDK gate. licensed = SDK import ok + ORCAWAVE_PATH set;
# present  = ORCAWAVE_PATH set (dir exists) but no importable SDK, OR install root found;
# absent   = none.
probe_orcawave() {
  local py; py="$(_ps_python)"
  local env_ok=0
  [[ -n "${ORCAWAVE_PATH:-}" && -d "${ORCAWAVE_PATH:-/nonexistent}" ]] && env_ok=1
  if [[ "$env_ok" == "1" ]] && [[ -n "$py" ]] && "$py" -c "import OrcFxAPI" >/dev/null 2>&1; then
    echo "licensed"; return 0
  fi
  if [[ "$env_ok" == "1" ]]; then echo "present"; return 0; fi
  local root="/c/Program Files (x86)/Orcina/OrcaWave"
  [[ -d "$root" ]] && { echo "present"; return 0; }
  echo "absent"
}
probe_orcawave_evidence() {
  local py; py="$(_ps_python)"
  if [[ -n "${ORCAWAVE_PATH:-}" && -d "${ORCAWAVE_PATH:-/nonexistent}" ]]; then
    if [[ -n "$py" ]] && "$py" -c "import OrcFxAPI" >/dev/null 2>&1; then echo "import"; else echo "env"; fi
    return 0
  fi
  [[ -d "/c/Program Files (x86)/Orcina/OrcaWave" ]] && { echo "root"; return 0; }
  echo "absent"
}

# ── ansys solver status ──────────────────────────────────────────────────────────
# licensed = install root present AND a license env var set (ANSYSLI_SERVERS or
#            ANSYSLMD_LICENSE_FILE); present = root only; absent = no root.
probe_ansys() {
  case "$(probe_ansys_root)" in
    present:*)
      if [[ -n "${ANSYSLI_SERVERS:-}" || -n "${ANSYSLMD_LICENSE_FILE:-}" ]]; then
        echo "licensed"
      else
        echo "present"
      fi;;
    *) echo "absent";;
  esac
}
probe_ansys_evidence() {
  case "$(probe_ansys_root)" in
    present:*)
      if [[ -n "${ANSYSLI_SERVERS:-}" || -n "${ANSYSLMD_LICENSE_FILE:-}" ]]; then echo "env"; else echo "root"; fi;;
    *) echo "absent";;
  esac
}

# ── aqwa solver status ───────────────────────────────────────────────────────────
# AQWA ships inside the ANSYS install; share the ANSYS root + license-env signal.
probe_aqwa() { probe_ansys; }
probe_aqwa_evidence() { probe_ansys_evidence; }
