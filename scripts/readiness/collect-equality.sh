#!/usr/bin/env bash
# collect-equality.sh — per-machine self-report for the machine-equality matrix (#2801).
#
# Emits .claude/state/equality-<machine>.yaml with 8 dimensions. Design (per approved plan):
#   * compute.static (cores/ram_total_mib/gpu) is graded + hashed; compute.headroom
#     (ram_avail/disk_avail) is volatile → display-only, EXCLUDED from the idempotency hash.
#   * data_access emits {repo: bare-name, mode} — no absolute paths (no machine-layout leak).
#   * harness REFERENCES harness-readiness-<machine>.yaml (never re-runs it).
#   * behavior runs a deterministic, SANDBOXED probe corpus (HOME/XDG redirected); enums + hashes.
#   * serialization allowlist: counts/booleans/enums only — never tokens, cron lines, env, abs paths.
#   * commit-on-change: rewrite only when the CANONICAL payload (volatile fields excluded) changes.
#
# Usage: collect-equality.sh [--machine <label>] [--stdout] [--now]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
WS="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." 2>/dev/null && pwd)}"
STATE_DIR="${WS}/.claude/state"
RUN_TS="$(date +%Y-%m-%dT%H:%M:%S 2>/dev/null)"

MACHINE=""; TO_STDOUT=0
for ((i=1; i<=$#; i++)); do
  case "${!i}" in
    --machine) j=$((i+1)); MACHINE="${!j:-}";;
    --stdout)  TO_STDOUT=1;;
    --now)     :;;  # explicit on-demand; behaviour identical (cadence is the caller's concern)
  esac
done

HOST="$(hostname 2>/dev/null | tr '[:upper:]' '[:lower:]')"
case "$(uname -s 2>/dev/null)" in
  Linux) OS="linux";; Darwin) OS="macos";; MINGW*|MSYS*|CYGWIN*) OS="windows";; *) OS="unknown";;
esac
# EQ_OS_OVERRIDE: force the OS branch — TEST SEAM ONLY, double-gated behind the explicit
# EQ_TEST_ENABLE_OS_OVERRIDE=1 flag so ambient production env can NEVER spoof the collector OS.
# (A bare override would let a Linux host misreport os: windows + trusted Windows compute —
# Codex code-review MAJOR.) The collect-equality.ps1 companion runs under Git Bash
# (uname → MINGW → "windows") and never sets the test flag; this exists only so the Linux contract
# test can exercise the windows EQ_* override seam (#2816 W5). Allowlisted values only.
if [[ "${EQ_TEST_ENABLE_OS_OVERRIDE:-}" == "1" ]]; then
  case "${EQ_OS_OVERRIDE:-}" in linux|macos|windows|unknown) OS="$EQ_OS_OVERRIDE";; esac
fi
if [[ -z "$MACHINE" ]]; then
  case "$HOST" in
    ace-linux-1*) MACHINE="dev-primary";; ace-linux-2*) MACHINE="dev-secondary";;
    *macbook*) MACHINE="macbook-portable";;
    ace-win-1*|licensed-win-1*|acma-ansys05*) MACHINE="ace-win-1";;
    ace-win-2*|licensed-win-2*|acma-ws014*) MACHINE="ace-win-2";;
    *)
      if [[ "$OS" == "windows" ]]; then
        echo "collect-equality.sh: unknown Windows host '$HOST'; pass --machine ace-win-1 or ace-win-2" >&2
        exit 1
      fi
      MACHINE="$HOST";;
  esac
fi
have() { command -v "$1" >/dev/null 2>&1; }
PYTHON_CMD=()
if ! source "${SCRIPT_DIR}/../lib/python-resolver.sh" 2>/dev/null; then
  PYTHON_CMD=()
fi
# CC1/GC1: escape a value for a YAML double-quoted scalar (backslash, quote; strip CR/LF).
yesc() { printf '%s' "$1" | tr -d '\r\n' | sed 's/\\/\\\\/g; s/"/\\"/g'; }
# #2816 W5: validate an EQ_* compute override is a clean non-negative integer (counts/MiB/GiB).
# Echoes the validated integer, or "unknown" on empty / non-numeric / negative / newline /
# unit-suffixed input — so a null/failed CIM query in the .ps1 companion can never emit 0/garbage
# into the graded compute cells (the matrix treats "unknown" as MISSING-EVIDENCE, fail-closed).
eqint() {
  local v="${1-}"
  # printf %s + the [[ =~ ]] anchors below reject embedded \n/\r, leading +/-, "16GB", " 5 ",
  # decimals, and empty. Only a pure run of ASCII digits survives.
  [[ "$v" =~ ^[0-9]+$ ]] && printf '%s' "$v" || printf '%s' unknown
}

# ── 1. COMPUTE (static = graded/hashed; headroom = volatile/excluded) ────────
cores="unknown"; ram_total_mib="unknown"; gpu="none"; ram_avail_mib="unknown"; disk_avail_gb="unknown"
case "$OS" in
  linux)
    cores=$(nproc 2>/dev/null || echo unknown)
    ram_total_mib=$(free -m 2>/dev/null | awk '/Mem:/{print $2}'); : "${ram_total_mib:=unknown}"
    ram_avail_mib=$(free -m 2>/dev/null | awk '/Mem:/{print $7}'); : "${ram_avail_mib:=unknown}"
    disk_avail_gb=$(df -BG "$WS" 2>/dev/null | awk 'NR==2{gsub(/G/,"",$4);print $4}'); : "${disk_avail_gb:=unknown}"
    have nvidia-smi && gpu=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1);;
  macos)
    cores=$(sysctl -n hw.ncpu 2>/dev/null || echo unknown)
    ram_total_mib=$(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1048576 ));;
  windows)
    # RAM/disk/gpu are unreliable in bare Git Bash -> "unknown" -> MISSING-EVIDENCE. The
    # collect-equality.ps1 companion (#2816) computes them via CIM and exports EQ_* overrides;
    # honor those when present (W5: each validated to a clean non-negative integer, else "unknown").
    cores="${NUMBER_OF_PROCESSORS:-unknown}"
    [[ -n "${EQ_CORES+x}" ]]          && cores=$(eqint "$EQ_CORES")
    [[ -n "${EQ_RAM_TOTAL_MIB+x}" ]]  && ram_total_mib=$(eqint "$EQ_RAM_TOTAL_MIB")
    [[ -n "${EQ_RAM_AVAIL_MIB+x}" ]]  && ram_avail_mib=$(eqint "$EQ_RAM_AVAIL_MIB")
    [[ -n "${EQ_DISK_AVAIL_GB+x}" ]]  && disk_avail_gb=$(eqint "$EQ_DISK_AVAIL_GB")
    # gpu is a free-form string (not an integer) — escape like any other string scalar; empty -> none.
    [[ -n "${EQ_GPU_MODEL+x}" && -n "$EQ_GPU_MODEL" ]] && gpu="$EQ_GPU_MODEL";;
esac
[[ -z "$gpu" ]] && gpu="none"

# ── 2. DATA ACCESS — {repo: bare-name, mode} (no abs path; MC1/DG3) ──────────
parent="$(dirname "$WS")"
data_yaml=""
for r in assetutilities digitalmodel worldenergydata assethold; do
  if   [[ -e "${WS}/${r}/.git" ]];     then mode="nested"
  elif [[ -e "${parent}/${r}/.git" ]]; then mode="sibling"
  else mode="absent"; fi
  data_yaml+="    - {repo: ${r}, mode: ${mode}}"$'\n'
done

# ── 2b. SOLVERS — licensed-solver capability (#2849); shared probes, no path leak ──
# MUST run BEFORE the behaviour-probe sandbox (which redirects HOME/XDG below) so the
# real-env signals (ORCAWAVE_PATH, ANSYS license vars) are visible. Sourced helper is
# the single source of truth — the standalone nightly R-ANSYS/R-ORCAFLEX checks were
# removed per #2849 decision 2 (the matrix cell IS the answer; no nightly duplication).
solvers_yaml=""
if [[ -f "${SCRIPT_DIR}/lib/probe-solvers.sh" ]]; then
  # shellcheck source=lib/probe-solvers.sh
  source "${SCRIPT_DIR}/lib/probe-solvers.sh"
  for s in orcaflex orcawave aqwa ansys; do
    st=$("probe_${s}" 2>/dev/null || echo unknown); : "${st:=unknown}"
    ev=$("probe_${s}_evidence" 2>/dev/null || echo unknown); : "${ev:=unknown}"
    solvers_yaml+="    - {name: ${s}, status: ${st}, evidence: ${ev}}"$'\n'
  done
else
  for s in orcaflex orcawave aqwa ansys; do
    solvers_yaml+="    - {name: ${s}, status: unknown, evidence: unknown}"$'\n'
  done
fi

# ── 3. HARNESS (reference readiness; gh_auth as ENUM, never the token) ───────
# Cron carries a minimal PATH that hides user-installed provider CLIs (claude in
# ~/.npm-global/bin; uv/codex in ~/.local/bin), so an unattended run reported
# providers as 'absent' that every interactive shell can see — a false NO-MAJORITY
# in the harness row. Append (not prepend: system binaries keep precedence) the
# well-known user bin dirs so cron and interactive collections probe the same PATH.
for _ubin in "${HOME:-}/.npm-global/bin" "${HOME:-}/.local/bin"; do
  [[ -d "$_ubin" && ":$PATH:" != *":$_ubin:"* ]] && PATH="$PATH:$_ubin"
done
export PATH
readiness_file="harness-readiness-${MACHINE}.yaml"
[[ -f "${STATE_DIR}/${readiness_file}" ]] || readiness_file="harness-readiness-${HOST}.yaml"
readiness_overall="missing"
[[ -f "${STATE_DIR}/${readiness_file}" ]] && \
  readiness_overall=$(awk -F': ' '/^overall:/{print $2; exit}' "${STATE_DIR}/${readiness_file}" 2>/dev/null)
gh_auth="absent"; have gh && { gh auth status >/dev/null 2>&1 && gh_auth="ok" || gh_auth="logged-out"; }
py_cmd="python"; [[ "$OS" != "windows" ]] && have uv && py_cmd="uv-run"
prov() { have "$1" && echo present || echo absent; }

# ── 4. SKILLS ────────────────────────────────────────────────────────────────
skills=$(find "${WS}/.claude/skills" -maxdepth 3 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')

# ── 5. KANBAN ────────────────────────────────────────────────────────────────
# LC_ALL=C: locale collation buried '_leader-state' mid-list while PowerShell sorts
# ordinal (underscore first) — same queue set diffed as DIVERGES across OSes. Byte
# order matches the Windows collector's output.
queues=$(find "${WS}/.claude/dispatch" -maxdepth 1 -name '*.yaml' 2>/dev/null | sed 's#.*/##;s#\.yaml$##' | LC_ALL=C sort | paste -sd',' -)
: "${queues:=none}"

# ── 6. MEMORY ────────────────────────────────────────────────────────────────
ctx="${WS}/.claude/memory/context.md"; ctx_mtime="absent"
[[ -f "$ctx" ]] && ctx_mtime=$(date -r "$ctx" +%Y-%m-%dT%H:%M:%S 2>/dev/null || echo unknown)
hermes_home="absent"; [[ -d "${HOME:-/nonexistent}/.hermes" ]] && hermes_home="present"

# ── 6b. SESSION CURATION — freshness of the daily session-analysis + memory curation ──
# References the state written by scripts/curation/curate_session_memory.py (never re-runs it,
# mirroring how harness REFERENCES the readiness file). Missing/garbled file → last_curated_at
# null → the matrix grades MISSING-EVIDENCE. last_curated_at is INTENTIONALLY in the canonical
# payload (not a volatile-exclude) so each fresh curation forces a rewrite carrying the new stamp.
sc_file="${STATE_DIR}/session-curation-${MACHINE}.json"
sc_last="null"; sc_24h=0; sc_provs=""; sc_memchg=0
if [[ -f "$sc_file" ]] && have jq; then
  _scl=$(jq -r '.last_curated_at // empty' "$sc_file" 2>/dev/null)
  [[ -n "$_scl" ]] && sc_last="\"$(yesc "$_scl")\""
  sc_24h=$(jq -r '.sessions_24h // 0' "$sc_file" 2>/dev/null); [[ "$sc_24h" =~ ^[0-9]+$ ]] || sc_24h=0
  sc_provs=$(jq -r '(.providers_active // []) | join(",")' "$sc_file" 2>/dev/null)
  sc_memchg=$(jq -r '.memory_files_changed // 0' "$sc_file" 2>/dev/null); [[ "$sc_memchg" =~ ^[0-9]+$ ]] || sc_memchg=0
fi

# ── 6c. SKILL CURRENCY — cross-provider skill drift vs canonical (#3249) ──────
# References the audit state written by scripts/curation/audit_skill_currency.py (never re-runs it).
# Missing/garbled file -> audited_at null / canonical_count 0 -> matrix grades MISSING-EVIDENCE.
skc_file="${STATE_DIR}/skill-currency-${MACHINE}.json"
skc_audited="null"; skc_cc=0; skc_gp=false; skc_gu=0; skc_ge=0; skc_cp=false; skc_hp=false; skc_dangling="null"
if [[ -f "$skc_file" ]] && have jq; then
  _ska=$(jq -r '.audited_at // empty' "$skc_file" 2>/dev/null)
  [[ -n "$_ska" ]] && skc_audited="\"$(yesc "$_ska")\""
  skc_cc=$(jq -r '.canonical_count // 0' "$skc_file" 2>/dev/null); [[ "$skc_cc" =~ ^[0-9]+$ ]] || skc_cc=0
  skc_gu=$(jq -r '.gemini_unexpected // 0' "$skc_file" 2>/dev/null); [[ "$skc_gu" =~ ^[0-9]+$ ]] || skc_gu=0
  skc_ge=$(jq -r '.gemini_expected // 0' "$skc_file" 2>/dev/null); [[ "$skc_ge" =~ ^[0-9]+$ ]] || skc_ge=0
  skc_gp=$(jq -r 'if .gemini_present then "true" else "false" end' "$skc_file" 2>/dev/null); [[ "$skc_gp" == "true" ]] || skc_gp=false
  skc_cp=$(jq -r 'if .codex_present then "true" else "false" end' "$skc_file" 2>/dev/null); [[ "$skc_cp" == "true" ]] || skc_cp=false
  skc_hp=$(jq -r 'if .hermes_present then "true" else "false" end' "$skc_file" 2>/dev/null); [[ "$skc_hp" == "true" ]] || skc_hp=false
  # index_dangling stays NULL when absent/unreadable so the matrix fails closed (a null index can
  # never grade green). A clean index emits 0; a rotted one emits the dangling count.
  _skd=$(jq -r 'if (.index_dangling|type)=="number" then .index_dangling else "null" end' "$skc_file" 2>/dev/null)
  [[ "$_skd" =~ ^[0-9]+$ ]] && skc_dangling="$_skd"
fi

# ── 6d. MEMORY FRESHNESS — staleness of memory surfaces (#3255) ───────────────
# References the audit state from scripts/curation/audit_memory_freshness.py (never re-runs it).
# audited_at null / worst_age_hours null -> matrix grades MISSING-EVIDENCE. worst_age_hours stays
# in the canonical payload so a refreshed audit forces a rewrite.
mf_file="${STATE_DIR}/memory-freshness-${MACHINE}.json"
mf_audited="null"; mf_worst="null"; mf_fresh="null"
if [[ -f "$mf_file" ]] && have jq; then
  _mfa=$(jq -r '.audited_at // empty' "$mf_file" 2>/dev/null)
  [[ -n "$_mfa" ]] && mf_audited="\"$(yesc "$_mfa")\""
  _mfw=$(jq -r 'if (.worst_age_hours|type)=="number" then .worst_age_hours else "null" end' "$mf_file" 2>/dev/null)
  [[ "$_mfw" =~ ^[0-9]+(\.[0-9]+)?$ ]] && mf_worst="$_mfw"
  _mff=$(jq -r '.freshness // empty' "$mf_file" 2>/dev/null)
  [[ -n "$_mff" ]] && mf_fresh="\"$(yesc "$_mff")\""
fi

# ── 6e. SKILL-LINK HEALTH — shared-skill links propagated to ecosystem repos (#3251) ──
# References resync-skill-links.sh state (never re-runs it). Missing/garbled -> null/0 -> the matrix
# grades MISSING-EVIDENCE. repairable stays in the canonical payload so a fresh audit forces a rewrite.
slh_file="${STATE_DIR}/skill-link-health-${MACHINE}.json"
slh_audited="null"; slh_repos=0; slh_healthy=0; slh_repairable=0; slh_worst="null"
if [[ -f "$slh_file" ]] && have jq; then
  _sla=$(jq -r '.audited_at // empty' "$slh_file" 2>/dev/null)
  [[ -n "$_sla" ]] && slh_audited="\"$(yesc "$_sla")\""
  slh_repos=$(jq -r '.repos_total // 0' "$slh_file" 2>/dev/null); [[ "$slh_repos" =~ ^[0-9]+$ ]] || slh_repos=0
  slh_healthy=$(jq -r '.healthy // 0' "$slh_file" 2>/dev/null); [[ "$slh_healthy" =~ ^[0-9]+$ ]] || slh_healthy=0
  slh_repairable=$(jq -r '.repairable // 0' "$slh_file" 2>/dev/null); [[ "$slh_repairable" =~ ^[0-9]+$ ]] || slh_repairable=0
  _slw=$(jq -r '.worst_state // empty' "$slh_file" 2>/dev/null)
  [[ -n "$_slw" ]] && slh_worst="\"$(yesc "$_slw")\""
fi

# ── 6f. HARNESS CHECKUP — /doctor hygiene facts (#3408) ──────────────────────
# References the audit state from scripts/curation/audit_harness_checkup.py (never re-runs it).
# Missing/garbled file -> audited_at null -> matrix grades MISSING-EVIDENCE. audited_at stays in the
# canonical payload so a fresh audit forces a rewrite. Every field is type-gated on read (boolean/
# number/string as declared, else null) so a malformed audit can never inject garbage into the graded
# cells — allowlist-safe by construction (the audit emits counts/booleans/enums/version strings only).
hc_file="${STATE_DIR}/harness-checkup-${MACHINE}.json"
hc_audited="null"; hc_ver="null"; hc_latest="null"; hc_vcur="null"; hc_install="null"
hc_dupe="null"; hc_sok="null"; hc_bad="null"; hc_uskill="null"; hc_uplug="null"; hc_mode="null"; hc_auto="null"
if [[ -f "$hc_file" ]] && have jq; then
  _hca=$(jq -r '.audited_at // empty' "$hc_file" 2>/dev/null);   [[ -n "$_hca" ]] && hc_audited="\"$(yesc "$_hca")\""
  _hcv=$(jq -r '.cc_version // empty' "$hc_file" 2>/dev/null);   [[ -n "$_hcv" ]] && hc_ver="\"$(yesc "$_hcv")\""
  _hcl=$(jq -r '.cc_latest // empty' "$hc_file" 2>/dev/null);    [[ -n "$_hcl" ]] && hc_latest="\"$(yesc "$_hcl")\""
  _hci=$(jq -r '.install_method // empty' "$hc_file" 2>/dev/null); [[ -n "$_hci" ]] && hc_install="\"$(yesc "$_hci")\""
  _hcm=$(jq -r '.default_mode // empty' "$hc_file" 2>/dev/null); [[ -n "$_hcm" ]] && hc_mode="\"$(yesc "$_hcm")\""
  _hcvc=$(jq -r 'if (.version_current|type)=="boolean" then .version_current else "n" end' "$hc_file" 2>/dev/null); [[ "$_hcvc" == "true" || "$_hcvc" == "false" ]] && hc_vcur="$_hcvc"
  _hcso=$(jq -r 'if (.settings_parse_ok|type)=="boolean" then .settings_parse_ok else "n" end' "$hc_file" 2>/dev/null); [[ "$_hcso" == "true" || "$_hcso" == "false" ]] && hc_sok="$_hcso"
  _hcau=$(jq -r 'if (.auto_mode_default|type)=="boolean" then .auto_mode_default else "n" end' "$hc_file" 2>/dev/null); [[ "$_hcau" == "true" || "$_hcau" == "false" ]] && hc_auto="$_hcau"
  _hcd=$(jq -r 'if (.duplicate_installs|type)=="number" then .duplicate_installs else "n" end' "$hc_file" 2>/dev/null); [[ "$_hcd" =~ ^[0-9]+$ ]] && hc_dupe="$_hcd"
  _hcb=$(jq -r 'if (.broken_agents|type)=="number" then .broken_agents else "n" end' "$hc_file" 2>/dev/null); [[ "$_hcb" =~ ^[0-9]+$ ]] && hc_bad="$_hcb"
  _hcus=$(jq -r 'if (.unused_skills|type)=="number" then .unused_skills else "n" end' "$hc_file" 2>/dev/null); [[ "$_hcus" =~ ^[0-9]+$ ]] && hc_uskill="$_hcus"
  _hcup=$(jq -r 'if (.unused_plugins|type)=="number" then .unused_plugins else "n" end' "$hc_file" 2>/dev/null); [[ "$_hcup" =~ ^[0-9]+$ ]] && hc_uplug="$_hcup"
fi

# ── 7. BEHAVIOR — deterministic, SANDBOXED probe corpus (DG4/DC1) ────────────
# CC3: guard mktemp (never let SBX become /sbx → rm -rf /). GC4: trap-based cleanup.
SBX_PARENT="$(mktemp -d 2>/dev/null)" || { echo "mktemp failed" >&2; exit 1; }
[[ -n "$SBX_PARENT" && -d "$SBX_PARENT" ]] || { echo "mktemp failed" >&2; exit 1; }
trap 'rm -rf "$SBX_PARENT"' EXIT
SBX="${SBX_PARENT}/sbx"; mkdir -p "$SBX"
sandbox() { HOME="$SBX" XDG_CACHE_HOME="$SBX" XDG_CONFIG_HOME="$SBX" XDG_STATE_HOME="$SBX" "$@"; }
b1="n/a"
gate="${WS}/.claude/hooks/plan-approval-gate.sh"
if [[ -f "$gate" ]] && have jq; then
  # Evaluate against a MARKER-FREE temp WORKSPACE_HUB so the gate's has_approval() can't be
  # satisfied by a real .planning/plan-approved/ marker — we are probing the BLOCK behavior,
  # not this machine's current approval state. STRICT mode forces a hard block decision.
  dec=$(printf '{"tool_name":"Write","tool_input":{"file_path":"src/x.py"}}' \
        | WORKSPACE_HUB="$SBX" FORCE_PLAN_GATE_STRICT=1 sandbox bash "$gate" 2>/dev/null \
        | jq -r '.decision // empty' 2>/dev/null)
  [[ "$dec" == "block" ]] && b1="deny" || { [[ -n "$dec" ]] && b1="allow"; }
fi
b2="n/a"; [[ -f "${WS}/.claude/skills/coordination/issue-planning-mode/SKILL.md" ]] && b2="ok"
b3="n/a"; [[ -d "${WS}/.claude/rules" ]] && { grep -rqi 'HTML.*default\|default.*HTML' "${WS}/.claude/rules" 2>/dev/null && b3="html" || b3="other"; }
b4="n/a"; szgate="${WS}/scripts/enforcement/check-harness-file-size.sh"
[[ -f "$szgate" ]] && { sandbox bash "$szgate" >/dev/null 2>&1 && b4="pass" || b4="fail"; }
b5="n/a"; settings="${WS}/.claude/settings.json"
if [[ -f "$settings" ]] && have jq && have sha256sum; then
  b5=$(jq -cS '.permissions // {}' "$settings" 2>/dev/null | tr -d '\r' | sha256sum | cut -c1-16)
  : "${b5:=n/a}"
fi
# (sandbox cleanup handled by the EXIT trap above — CC3/GC4)

# ── 8. SCHEDULER (counts/booleans only; never cron lines, C4) ────────────────
job_count=0; has_sync=false; has_parity=false
if [[ "$OS" != "windows" ]] && have crontab; then
  dump=$(crontab -l 2>/dev/null)
  job_count=$(printf '%s\n' "$dump" | grep -cE '^[[:space:]]*[^[:space:]#]')  # non-blank, non-comment
  printf '%s' "$dump" | grep -q 'repository-sync\|repo-sync' && has_sync=true
  printf '%s' "$dump" | grep -q 'parity-review' && has_parity=true
fi

# ── 9. PROVENANCE — checkout freshness guard (#2851) ─────────────────────────
# Stamped so the matrix can mark a stale/dirty/behind checkout STALE-CHECKOUT and exclude
# it from peer comparison (a stale tree must never manufacture a false divergence — see the
# #2801 b3/skills artifact). Computed read-only, BEFORE the write (A3: the collector's own
# .claude/state output is outside the measured allowlist AND captured pre-write, so it can
# never self-trigger dirty). The collector NEVER fetches (no network side-effect, BC2).
#
# MEASURED-PATH allowlist (BC1): dirty reflects ONLY the paths the collector actually reads,
# NOT `.claude` wholesale — else unrelated state/memory edits would false-STALE a healthy
# machine. Keep this in sync with the dimensions probed above.
MEASURED=(.claude/skills .claude/memory/context.md .claude/memory/agents.md .codex/skills \
          .claude/dispatch .claude/rules AGENTS.md \
          .claude/hooks/plan-approval-gate.sh .claude/settings.json \
          scripts/readiness/harness-config.yaml scripts/readiness/provider_harness_parity.py \
          config/agents/claude/SOUL.runtime.md config/agents/codex/AGENTS.runtime.md \
          config/agents/codex/MEMORY.runtime.md config/agents/hermes/SOUL.runtime.md \
          config/scheduled-tasks/schedule-tasks.yaml)
checkout_sha="unknown"; dirty=false; behind_main="unknown"; ahead_main="unknown"; origin_ref_age_h="unknown"
if git -C "$WS" rev-parse --git-dir >/dev/null 2>&1; then
  checkout_sha=$(git -C "$WS" rev-parse --short HEAD 2>/dev/null); : "${checkout_sha:=unknown}"
  # dirty = TRACKED changes to the measured allowlist only. --untracked-files=no excludes
  # untracked noise (.DS_Store, __pycache__, editor swap files) that would otherwise
  # false-STALE a healthy machine on benign cruft inside a measured directory.
  [[ -n "$(git -C "$WS" status --porcelain --untracked-files=no -- "${MEASURED[@]}" 2>/dev/null)" ]] && dirty=true
  # behind_main / ahead_main = best-effort vs the LOCAL origin/main ref (no fetch). "unknown" if
  # ref absent ⇒ fail-closed downstream (BC2). BOTH directions matter: behind = missing upstream
  # commits (the #2801 stale-tree case); ahead = local commits NOT on origin/main (an unpushed
  # feature checkout whose measured dims are non-canonical). Either ≠0 ⇒ not the canonical tree.
  bm=$(git -C "$WS" rev-list --count HEAD..origin/main 2>/dev/null)
  [[ -n "$bm" ]] && behind_main="$bm"
  am=$(git -C "$WS" rev-list --count origin/main..HEAD 2>/dev/null)
  [[ -n "$am" ]] && ahead_main="$am"
  # origin-ref freshness from the last fetch, WITHOUT fetching (BC2): a stale LOCAL origin/main
  # ref false-negatives behind_main, so record its age and let the matrix fail-closed on it.
  # Use --git-common-dir, NOT --git-dir: in a linked worktree the shared FETCH_HEAD and
  # refs/remotes/origin/main live in the COMMON dir; --git-dir points at the per-worktree dir
  # that holds neither, which would false-STALE every worktree-based collection.
  gd=$(git -C "$WS" rev-parse --git-common-dir 2>/dev/null)
  # Join to WS only when gd is RELATIVE. On Windows (Git Bash) a linked worktree's --git-common-dir
  # is an absolute drive-letter path (e.g. C:/repo/.git) that does NOT begin with "/", so a bare
  # "!= /*" test wrongly treats it as relative and corrupts it (WS/C:/repo/.git) -> FETCH_HEAD not
  # found -> origin_ref_age_h "unknown" -> the matrix false-STALEs every worktree-based collection.
  # winabs matches a Windows drive root (C:/ or C:\); git emits forward slashes here in practice.
  winabs='^[A-Za-z]:[/\]'
  [[ -n "$gd" && "$gd" != /* && ! "$gd" =~ $winabs ]] && gd="${WS}/${gd}"
  # Age-check a fetch that proves origin/main. Prefer FETCH_HEAD only when its content explicitly
  # names branch 'main'; otherwise fall back to the tracked origin/main ref. This handles the
  # Windows wrapper's freshness preflight where origin/main may not move for >12h, while still
  # avoiding unrelated FETCH_HEAD refreshes from other branches.
  ref=""
  origin_main_sha="$(git -C "$WS" rev-parse --verify refs/remotes/origin/main 2>/dev/null || true)"
  if [[ -f "${gd}/FETCH_HEAD" ]] && grep -q "branch 'main' of " "${gd}/FETCH_HEAD" 2>/dev/null; then
    fetch_head_sha="$(awk "/branch 'main' of / {print \$1; exit}" "${gd}/FETCH_HEAD" 2>/dev/null)"
    if [[ -n "$fetch_head_sha" && -n "$origin_main_sha" && "$fetch_head_sha" == "$origin_main_sha" ]]; then
      ref="${gd}/FETCH_HEAD"
    fi
  elif [[ -f "${gd}/refs/remotes/origin/main" ]]; then
    ref="${gd}/refs/remotes/origin/main"
  fi
  if [[ -z "$ref" && -f "${gd}/refs/remotes/origin/main" ]]; then
    ref="${gd}/refs/remotes/origin/main"
  fi
  if [[ -n "$ref" ]]; then
    mt=$(date -r "$ref" +%s 2>/dev/null); now=$(date +%s 2>/dev/null)
    [[ -n "$mt" && -n "$now" ]] && origin_ref_age_h=$(( (now - mt) / 3600 ))
  fi
fi

# ── 9b. PROVIDER HARNESS — provider/capability parity predicates (#2889) ─────
provider_harness_fallback() {
  "${provider_py}" "${SCRIPT_DIR}/provider_harness_parity.py" \
    --workspace "$WS" --home "${HOME:-}" --format yaml 2>/dev/null
}
provider_harness_unknown() {
  cat <<'YAML'
schema_version: 1
providers:
  claude:
    present: false
    installed: false
    "memory:read": {status: unknown, reason: collector_unavailable}
    "skills:invoke": {status: unknown, reason: collector_unavailable}
    "workflow:gates": {status: unknown, reason: collector_unavailable}
  codex:
    present: false
    installed: false
    "memory:read": {status: unknown, reason: collector_unavailable}
    "skills:invoke": {status: unknown, reason: collector_unavailable}
    "workflow:gates": {status: unknown, reason: collector_unavailable}
  hermes:
    present: false
    installed: false
    "memory:read": {status: unknown, reason: collector_unavailable}
    "skills:invoke": {status: unknown, reason: collector_unavailable}
    "workflow:gates": {status: unknown, reason: collector_unavailable}
YAML
}
provider_py=""
if [[ "$OS" == "windows" ]] && have python; then
  provider_py="python"
elif have python3; then
  provider_py="python3"
elif have python; then
  provider_py="python"
fi
if [[ -n "$provider_py" && -f "${SCRIPT_DIR}/provider_harness_parity.py" ]]; then
  provider_harness_yaml="$(provider_harness_fallback || provider_harness_unknown)"
else
  provider_harness_yaml="$(provider_harness_unknown)"
fi
provider_harness_yaml="$(printf '%s\n' "$provider_harness_yaml" | sed 's/^/    /')"

# ── publish_health (#3502): last equivalence-state publish outcome, written by
#    equivalence-sentinel.sh. A gate-length duration or a stale/missing record is
#    the #3500 pre-push-deadlock signature; the matrix renders it per machine.
ph_file="${WS}/.claude/state/equivalence/publish-health.json"
ph_ts="missing"; ph_dur="null"; ph_rc="null"
if [[ -f "$ph_file" && "${#PYTHON_CMD[@]}" -gt 0 ]]; then
  read -r ph_ts ph_dur ph_rc < <("${PYTHON_CMD[@]}" - "$ph_file" "${SCRIPT_DIR}/../monitoring" <<'PY' 2>/dev/null || echo "missing null null"
import json, sys
sys.path.insert(0, sys.argv[2])
from equivalence_state import validate_publish_health
try:
    d = validate_publish_health(open(sys.argv[1]).read())
    print(d["ts"], d["duration_s"], d["rc"])
except Exception:
    print("missing null null")
PY
) || true
fi

# ── emit (generated_at + headroom + mtime + job_count + checkout_sha are EXCLUDED from the
#          hash; dirty + behind_main + origin_ref_age_h ARE hashed — A1/BC5: exclude the pure
#          churn (sha) ONLY, so every freshness-state field stays live in the committed report
#          and a fresh→stale transition always forces a rewrite) ──
read -r -d '' BODY <<YAML || true
schema_version: 4
machine: "$(yesc "$MACHINE")"
host: "$(yesc "$HOST")"
os: ${OS}
status: active
provenance:
  checkout_sha: "$(yesc "$checkout_sha")"
  dirty: ${dirty}
  behind_main: ${behind_main}
  ahead_main: ${ahead_main}
  origin_ref_age_h: ${origin_ref_age_h}
dimensions:
  compute:
    static: {cores: ${cores}, ram_total_mib: ${ram_total_mib}, gpu_model: "$(yesc "$gpu")"}
    headroom: {ram_avail_mib: ${ram_avail_mib}, disk_avail_gb: ${disk_avail_gb}}
  data_access:
${data_yaml}  solvers:
${solvers_yaml}  harness:
    providers: {claude: $(prov claude), codex: $(prov codex), gemini: $(prov gemini), hermes: $(prov hermes)}
    gh_auth: ${gh_auth}
    python_cmd: ${py_cmd}
    readiness_ref: ${readiness_file}
    readiness_overall: ${readiness_overall:-missing}
  skills: {repo_skill_count: ${skills}}
  kanban: {dispatch_queues: "$(yesc "$queues")"}
  memory:
    hermes_home: ${hermes_home}
    context_md_mtime: "$(yesc "$ctx_mtime")"
  provider_harness:
${provider_harness_yaml}
  behavior:
    enums: {b1: ${b1}, b2: ${b2}, b3: ${b3}, b4: ${b4}}
    hashes: {b5: ${b5}}
  scheduler:
    has_repo_sync: ${has_sync}
    has_parity_review: ${has_parity}
    job_count: ${job_count}
  session_curation:
    last_curated_at: ${sc_last}
    sessions_24h: ${sc_24h}
    providers_active: "$(yesc "$sc_provs")"
    memory_files_changed: ${sc_memchg}
  skill_currency:
    audited_at: ${skc_audited}
    canonical_count: ${skc_cc}
    gemini_present: ${skc_gp}
    gemini_unexpected: ${skc_gu}
    gemini_expected: ${skc_ge}
    codex_present: ${skc_cp}
    hermes_present: ${skc_hp}
    index_dangling: ${skc_dangling}
  memory_freshness:
    audited_at: ${mf_audited}
    worst_age_hours: ${mf_worst}
    freshness: ${mf_fresh}
  skill_link_health:
    audited_at: ${slh_audited}
    repos_total: ${slh_repos}
    healthy: ${slh_healthy}
    repairable: ${slh_repairable}
    worst_state: ${slh_worst}
  harness_checkup:
    audited_at: ${hc_audited}
    cc_version: ${hc_ver}
    cc_latest: ${hc_latest}
    version_current: ${hc_vcur}
    install_method: ${hc_install}
    duplicate_installs: ${hc_dupe}
    settings_parse_ok: ${hc_sok}
    broken_agents: ${hc_bad}
    unused_skills: ${hc_uskill}
    unused_plugins: ${hc_uplug}
    default_mode: ${hc_mode}
    auto_mode_default: ${hc_auto}
  publish_health:
    last_publish_at: "$(yesc "$ph_ts")"
    last_publish_duration_s: ${ph_dur}
    last_publish_rc: ${ph_rc}
YAML
FULL="generated_at: \"${RUN_TS}\""$'\n'"${BODY}"

# canonical payload = exclude volatile/meaningless fields (DC4/DG1)
# CC2/GC2: anchor volatile-field exclusion to line start/indent so a value that merely
# CONTAINS "job_count:"/"context_md_mtime:" can't drop its line from the hash.
canonical() { printf '%s\n' "$1" | grep -vE '^(generated_at:)|^[[:space:]]*(headroom|context_md_mtime|job_count|checkout_sha):'; }

if [[ "$TO_STDOUT" == "1" ]]; then
  printf '%s\n' "$FULL"
  exit 0
fi
mkdir -p "$STATE_DIR"
OUT="${STATE_DIR}/equality-${MACHINE}.yaml"
if [[ -f "$OUT" ]] && have sha256sum; then
  old=$(canonical "$(cat "$OUT")" | sha256sum)
  new=$(canonical "$FULL" | sha256sum)
  if [[ "$old" == "$new" ]]; then
    echo "unchanged (canonical payload identical) — ${OUT} left as-is"
    exit 0
  fi
fi
TMP_OUT=""
cleanup_tmp() {
  [[ -n "$TMP_OUT" ]] && rm -f -- "$TMP_OUT"
}
trap cleanup_tmp EXIT
TMP_OUT="$(mktemp "${STATE_DIR}/.equality-${MACHINE}.yaml.tmp.XXXXXX")" \
  || { echo "collect-equality: could not create temporary report" >&2; exit 1; }
printf '%s\n' "$FULL" > "$TMP_OUT" \
  || { echo "collect-equality: could not write temporary report" >&2; exit 1; }
mv -- "$TMP_OUT" "$OUT" \
  || { echo "collect-equality: could not publish report atomically" >&2; exit 1; }
TMP_OUT=""
trap - EXIT
echo "wrote ${OUT} (machine=${MACHINE}, os=${OS})"
