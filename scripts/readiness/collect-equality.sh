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
if [[ -z "$MACHINE" ]]; then
  case "$HOST" in
    ace-linux-1*) MACHINE="dev-primary";; ace-linux-2*) MACHINE="dev-secondary";;
    *macbook*) MACHINE="macbook-portable";; acma-ws014*) MACHINE="licensed-win-2";;
    *) [[ "$OS" == "windows" ]] && MACHINE="licensed-win-1" || MACHINE="$HOST";;
  esac
fi
have() { command -v "$1" >/dev/null 2>&1; }
# CC1/GC1: escape a value for a YAML double-quoted scalar (backslash, quote; strip CR/LF).
yesc() { printf '%s' "$1" | tr -d '\r\n' | sed 's/\\/\\\\/g; s/"/\\"/g'; }

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
    cores="${NUMBER_OF_PROCESSORS:-unknown}";;  # RAM/disk unreliable in Git Bash -> unknown -> MISSING-EVIDENCE
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

# ── 3. HARNESS (reference readiness; gh_auth as ENUM, never the token) ───────
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
queues=$(find "${WS}/.claude/dispatch" -maxdepth 1 -name '*.yaml' 2>/dev/null | sed 's#.*/##;s#\.yaml$##' | sort | paste -sd',' -)
: "${queues:=none}"

# ── 6. MEMORY ────────────────────────────────────────────────────────────────
ctx="${WS}/.claude/memory/context.md"; ctx_mtime="absent"
[[ -f "$ctx" ]] && ctx_mtime=$(date -r "$ctx" +%Y-%m-%dT%H:%M:%S 2>/dev/null || echo unknown)
hermes_home="absent"; [[ -d "${HOME:-/nonexistent}/.hermes" ]] && hermes_home="present"

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

# ── emit (generated_at + headroom + mtime + job_count are EXCLUDED from the hash) ──
read -r -d '' BODY <<YAML || true
schema_version: 2
machine: "$(yesc "$MACHINE")"
host: "$(yesc "$HOST")"
os: ${OS}
status: active
dimensions:
  compute:
    static: {cores: ${cores}, ram_total_mib: ${ram_total_mib}, gpu_model: "$(yesc "$gpu")"}
    headroom: {ram_avail_mib: ${ram_avail_mib}, disk_avail_gb: ${disk_avail_gb}}
  data_access:
${data_yaml}  harness:
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
  behavior:
    enums: {b1: ${b1}, b2: ${b2}, b3: ${b3}, b4: ${b4}}
    hashes: {b5: ${b5}}
  scheduler:
    has_repo_sync: ${has_sync}
    has_parity_review: ${has_parity}
    job_count: ${job_count}
YAML
FULL="generated_at: \"${RUN_TS}\""$'\n'"${BODY}"

# canonical payload = exclude volatile/meaningless fields (DC4/DG1)
# CC2/GC2: anchor volatile-field exclusion to line start/indent so a value that merely
# CONTAINS "job_count:"/"context_md_mtime:" can't drop its line from the hash.
canonical() { printf '%s\n' "$1" | grep -vE '^(generated_at:)|^[[:space:]]*(headroom|context_md_mtime|job_count):'; }

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
printf '%s\n' "$FULL" > "$OUT"
echo "wrote ${OUT} (machine=${MACHINE}, os=${OS})"
