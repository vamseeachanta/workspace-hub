#!/usr/bin/env bash
# equivalence-fingerprint.sh — emit THIS box's machine-equivalence fingerprint as JSON.
#
# Part of the machine-equivalence drift sentinel (#3059, harden-ecosystem epic #3058).
# Captures the four dimensions audited manually on 2026-06-13: clone vs origin,
# harness, model-registry hash, and hub learning-cron freshness.
#
# Usage: equivalence-fingerprint.sh [--out <file>]
#   EQUIV_ROLE env overrides role detection (full | contribute | contribute-minimal).
# Degrades gracefully: any field it cannot read is emitted as null, never an error.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
cd "$REPO_ROOT" || exit 1

OUT=""
[ "${1:-}" = "--out" ] && OUT="${2:-}"

host="$(hostname 2>/dev/null || echo unknown)"

# Identity (#3516): env overrides, else resolve machine_id + role from the
# workstation registry (schedule_variant = role). Collision-safe fallback
# unknown-<host> keeps two unregistered boxes from ever sharing a blob name.
role="${EQUIV_ROLE:-}"
machine="${EQUIV_MACHINE:-}"
if [ -z "$role" ] || [ -z "$machine" ]; then
  ident="$(python3 "$REPO_ROOT/scripts/monitoring/equivalence_state.py" resolve-identity \
    --registry "$REPO_ROOT/config/workstations/registry.yaml" --hostname "$host" 2>/dev/null || true)"
  [ -z "$machine" ] && machine="${ident%% *}"
  [ -z "$role" ] && role="${ident##* }"
fi
[ -z "$machine" ] && machine="unknown-$host"
[ -z "$role" ] && role="unknown"

# Clone position vs origin/main (best-effort fetch; soft on network failure).
git fetch -q origin main 2>/dev/null
clone_head="$(git rev-parse --short HEAD 2>/dev/null || echo null)"
behind=null; ahead=null
if counts="$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null)"; then
  behind="$(echo "$counts" | awk '{print $1}')"
  ahead="$(echo "$counts" | awk '{print $2}')"
fi

# Harness version + install method.
hv="$(claude --version 2>/dev/null | awk '{print $1}')"; [ -z "$hv" ] && hv=null
cpath="$(command -v claude 2>/dev/null || true)"
case "$cpath" in
  *.npm-global*) hinstall="npm-global" ;;
  *.local/share*|*claude/local*) hinstall="native" ;;
  "") hinstall=null ;;
  *) hinstall="other" ;;
esac

# Model-registry hash (the equivalence-critical config).
reg="config/agents/model-registry.yaml"
reg_sha="$( [ -f "$reg" ] && sha256sum "$reg" 2>/dev/null | awk '{print $1}' || echo null )"

# Hub learning-cron ages (hours since newest matching log/artifact); null if unknown.
# Only meaningful on role=full; the comparator ignores these for other roles.
cron_age() {
  local pat="$1" newest
  newest="$(find logs .claude/state/learning-reports -type f -name "*${pat}*" -printf '%T@\n' 2>/dev/null | sort -rn | head -1)"
  [ -z "$newest" ] && { echo null; return; }
  python3 -c "import time,sys; print(round((time.time()-float(sys.argv[1]))/3600,1))" "$newest" 2>/dev/null || echo null
}
age_learning="$(cron_age comprehensive-learning)"
age_session="$(cron_age session-analysis)"

# Primary-tree drift dimensions (#3187): is this checkout on main, and is there a
# stale orphan .git/index.lock? The lock age is only reported when NO live git
# process holds it (a live op's lock is not "stale").
cur_branch="$(git symbolic-ref --short HEAD 2>/dev/null || echo DETACHED)"
on_main=false; [ "$cur_branch" = "main" ] && on_main=true
lock="$REPO_ROOT/.git/index.lock"
lock_stale=null
if [ -e "$lock" ] && ! pgrep -x git >/dev/null 2>&1; then
  lock_stale="$(python3 -c 'import os,sys,time; print(round((time.time()-os.path.getmtime(sys.argv[1]))/60,1))' "$lock" 2>/dev/null || echo null)"
fi

# Emit JSON via python for safe quoting.
python3 - "$role" "$host" "$machine" "$clone_head" "$behind" "$ahead" "$hv" "$hinstall" "$reg_sha" "$age_learning" "$age_session" "$on_main" "$lock_stale" <<'PY' > "${OUT:-/dev/stdout}"
import json, sys, hashlib, os
from datetime import datetime, timezone
role, host, machine, head, behind, ahead, hv, hinstall, reg, al, as_, on_main_s, lock_stale_s = sys.argv[1:14]
def fhash(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:16]
    except OSError:
        return None
# Per-provider built-runtime behavior hashes (#3074): equivalent provider
# behavior across machines means these match box-to-box. Behavior files only —
# never secrets/auth.
provider_soul = {
    "hermes": fhash("config/agents/hermes/SOUL.runtime.md"),
    "claude": fhash("config/agents/claude/SOUL.runtime.md"),
    "codex": fhash("config/agents/codex/SOUL.runtime.md"),
    "codex_agents": fhash("config/agents/codex/AGENTS.runtime.md"),
    "gemini": fhash("config/agents/gemini/SOUL.runtime.md"),
}
def num(x):
    if x in ("null", ""): return None
    try: return int(x)
    except ValueError:
        try: return float(x)
        except ValueError: return None
def s(x): return None if x in ("null", "") else x
fp = {
    "fingerprint_version": 1,
    "role": role, "hostname": host, "machine_id": machine,
    "ts": datetime.now(timezone.utc).isoformat(),
    "clone_head": s(head),
    "behind_origin": num(behind), "ahead_origin": num(ahead),
    "harness_version": s(hv), "harness_install": s(hinstall),
    "registry_sha256": s(reg),
    "learning_cron_ages_h": {
        "comprehensive-learning-nightly": num(al),
        "session-analysis": num(as_),
    },
    "provider_soul_hashes": provider_soul,
    "on_main": (on_main_s == "true"),
    "index_lock_stale_min": num(lock_stale_s),
}
print(json.dumps(fp, indent=1))
PY
[ -n "$OUT" ] && echo "wrote fingerprint -> $OUT" >&2
