#!/usr/bin/env bash
# equivalence-sentinel.sh — detect machine-equivalence drift across boxes and alert.
#
# Flow: fingerprint THIS box -> publish to the `equivalence-state` git ref ->
# collect all boxes' fingerprints -> compare -> alert on WARNING/CRITICAL.
# Part of the drift sentinel (#3059, harden-ecosystem epic #3058).
#
# Env:
#   EQUIV_ROLE         override role detection
#   EQUIV_ALERT_ISSUE  if set, post a comment to this issue # on WARNING/CRITICAL
# Exit: 0 equivalent/INFO, 1 WARNING, 2 CRITICAL, 3 store unavailable.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
cd "$REPO_ROOT" || exit 1
MON="$REPO_ROOT/scripts/monitoring"
export PYTHONPATH="$MON:${PYTHONPATH:-}"
PY="uv run --no-project python"

ts="$(date -u +%Y%m%dT%H%M%SZ)"
fp_local="$REPO_ROOT/.claude/state/equivalence/local-fingerprint.json"
mkdir -p "$(dirname "$fp_local")"

# 1. fingerprint this box
bash "$MON/equivalence-fingerprint.sh" --out "$fp_local" 2>/dev/null || { echo "fingerprint failed"; exit 1; }
role="$($PY -c "import json,sys;print(json.load(open(sys.argv[1]))['role'])" "$fp_local" 2>/dev/null || echo unknown)"

# 2. publish to the shared git ref (soft — network/auth issues must not crash the cron)
# Absent sibling repos are EXPECTED on single-repo machines; the underlying
# check emits "ERROR: directory not found" for them. Downgrade that benign token
# here (not in the shared check-all.sh) so cron-health does not false-flag this
# job — real publish failures keep their error wording.
#
# Publish-health (#3502): the publish is timed and recorded so the equality
# matrix can flag a gate-length publish (#3500 signature). The PREVIOUS cycle's
# duration is stamped into this cycle's fingerprint so it travels in the ref
# and is visible fleet-centrally.
publish_health="$REPO_ROOT/.claude/state/equivalence/publish-health.json"
$PY - "$fp_local" "$publish_health" <<'PY'
import json, sys
fp_path, ph_path = sys.argv[1], sys.argv[2]
try:
    dur = json.load(open(ph_path)).get("duration_s")
except Exception:
    dur = None
if isinstance(dur, (int, float)) and not isinstance(dur, bool):
    fp = json.load(open(fp_path))
    fp["last_publish_duration_s"] = dur
    json.dump(fp, open(fp_path, "w"), indent=1)
PY
publish_start="$(date +%s)"
$PY "$MON/equivalence_state.py" publish --repo "$REPO_ROOT" --role "$role" --file "$fp_local" 2>&1 \
  | sed -e 's/^/[publish] /' -e 's/ERROR: directory not found:/SKIP (absent sibling):/'
publish_rc="${PIPESTATUS[0]}"
publish_dur="$(( $(date +%s) - publish_start ))"
printf '{"ts": "%s", "duration_s": %s, "rc": %s}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$publish_dur" "$publish_rc" > "$publish_health"

# 3. collect + 4. compare (in one python pass)
report="$REPO_ROOT/.claude/state/equivalence/divergences-latest.json"
$PY - "$report" <<'PY'
import json, sys
import equivalence_state as store
import equivalence_compare as cmp
try:
    fps = store.collect(".")
except store.StoreUnavailable as e:
    print(f"[collect] store unavailable: {e}", file=sys.stderr)
    sys.exit(3)
# Roster-aware (#3502): machines that run the daily cron but have no
# fingerprint in the ref are flagged (absence = gate-blocked publish or
# sentinel not installed). Degrades open if the registry is unreadable.
roster = cmp.load_expected_machines("config/workstations/registry.yaml")
divs = cmp.compare(fps, expected_machines=roster or None)
json.dump({"boxes": len(fps), "divergences": divs}, open(sys.argv[1], "w"), indent=1)
print(f"[compare] {len(fps)} box(es), {len(divs)} divergence(s)")
for d in divs:
    print(f"  [{d['severity']}] {d['code']}: {d['detail']}")
worst = cmp.worst_severity(divs)
sys.exit(2 if worst == cmp.CRITICAL else (1 if worst == cmp.WARNING else 0))
PY
rc=$?

# 5. alert on WARNING/CRITICAL
if [ "$rc" = "1" ] || [ "$rc" = "2" ]; then
  echo "EQUIVALENCE DRIFT (rc=$rc) at $ts — see $report" >&2
  if [ -n "${EQUIV_ALERT_ISSUE:-}" ] && command -v gh >/dev/null 2>&1; then
    body="$($PY -c "import json,sys;d=json.load(open(sys.argv[1]));print('\n'.join(f\"- **{x[\"severity\"]}** \`{x[\"code\"]}\`: {x[\"detail\"]}\" for x in d['divergences']))" "$report" 2>/dev/null)"
    printf '## Machine-equivalence drift detected — %s\n\n%s\n' "$ts" "$body" \
      | gh issue comment "$EQUIV_ALERT_ISSUE" --body-file - 2>/dev/null \
      && echo "[alert] posted to #$EQUIV_ALERT_ISSUE" >&2
  fi
fi
exit "$rc"
