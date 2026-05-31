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
    *macbook*) MACHINE="macbook-portable";; acma-ws014*) MACHINE="licensed-win-2";;
    *) [[ "$OS" == "windows" ]] && MACHINE="licensed-win-1" || MACHINE="$HOST";;
  esac
fi
have() { command -v "$1" >/dev/null 2>&1; }
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
MEASURED=(.claude/skills .claude/memory/context.md .claude/dispatch .claude/rules \
          .claude/hooks/plan-approval-gate.sh .claude/settings.json \
          scripts/readiness/harness-config.yaml config/scheduled-tasks/schedule-tasks.yaml)
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
  # FETCH_HEAD first: its mtime is the true last-fetch time (best freshness signal); fall back
  # to the loose origin/main ref mtime (set when the ref last moved on fetch).
  for ref in "${gd}/FETCH_HEAD" "${gd}/refs/remotes/origin/main"; do
    if [[ -f "$ref" ]]; then
      mt=$(date -r "$ref" +%s 2>/dev/null); now=$(date +%s 2>/dev/null)
      [[ -n "$mt" && -n "$now" ]] && origin_ref_age_h=$(( (now - mt) / 3600 ))
      break
    fi
  done
fi

# ── emit (generated_at + headroom + mtime + job_count + checkout_sha are EXCLUDED from the
#          hash; dirty + behind_main + origin_ref_age_h ARE hashed — A1/BC5: exclude the pure
#          churn (sha) ONLY, so every freshness-state field stays live in the committed report
#          and a fresh→stale transition always forces a rewrite) ──
read -r -d '' BODY <<YAML || true
schema_version: 3
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
printf '%s\n' "$FULL" > "$OUT"
echo "wrote ${OUT} (machine=${MACHINE}, os=${OS})"
