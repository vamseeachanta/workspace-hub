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
# Exit: 0 equivalent/INFO, 1 WARNING, 2 CRITICAL, 3 fingerprint/publish/store
# failure, 4 publish-health persistence failure.
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
cd "$REPO_ROOT" || exit 1
MON="$REPO_ROOT/scripts/monitoring"
export PYTHONPATH="$MON:${PYTHONPATH:-}"
source "$REPO_ROOT/scripts/lib/python-resolver.sh" || exit 3

ts="$(date -u +%Y%m%dT%H%M%SZ)"
fp_local="$REPO_ROOT/.claude/state/equivalence/local-fingerprint.json"
mkdir -p "$(dirname "$fp_local")"
publish_health="$REPO_ROOT/.claude/state/equivalence/publish-health.json"

write_health() {
  local phase="$1" duration="$2" health_rc="$3"
  "${PYTHON_CMD[@]}" "$MON/equivalence_state.py" write-health \
    --health "$publish_health" --phase "$phase" --duration "$duration" --rc "$health_rc"
}

# 1. fingerprint this box
fingerprint_start="$(date +%s)"
if ! bash "$MON/equivalence-fingerprint.sh" --out "$fp_local"; then
  fingerprint_dur="$(( $(date +%s) - fingerprint_start ))"
  write_health fingerprint "$fingerprint_dur" 3 || exit 4
  echo "fingerprint failed" >&2
  exit 3
fi
fingerprint_dur="$(( $(date +%s) - fingerprint_start ))"
if ! "${PYTHON_CMD[@]}" "$MON/equivalence_state.py" prepare \
    --file "$fp_local" --health "$publish_health"; then
  write_health fingerprint "$fingerprint_dur" 3 || exit 4
  echo "fingerprint preparation failed" >&2
  exit 3
fi
role="$("${PYTHON_CMD[@]}" -c "import json,sys;print(json.load(open(sys.argv[1]))['role'])" "$fp_local")"
# #3516: blobs are keyed by machine_id (same-role boxes must not clobber).
machine="$("${PYTHON_CMD[@]}" -c "import json,sys;print(json.load(open(sys.argv[1]))['machine_id'])" "$fp_local")"

# 2. publish to the shared git ref (soft — network/auth issues must not crash the cron)
# Absent sibling repos are EXPECTED on single-repo machines; the underlying
# check emits "ERROR: directory not found" for them. Downgrade that benign token
# here (not in the shared check-all.sh) so cron-health does not false-flag this
# job — real publish failures keep their error wording.
#
# Publish-health (#3502): the publish is timed and recorded so the equality
# matrix can flag a gate-length publish (#3500 signature). The PREVIOUS cycle's
# duration is stamped into this cycle's fingerprint so it travels in the ref
# and is visible fleet-centrally. Preparation above accepts only exact,
# publish-phase prior health and atomically revalidates the enriched fingerprint.
publish_start="$(date +%s)"
"${PYTHON_CMD[@]}" "$MON/equivalence_state.py" publish --repo "$REPO_ROOT" --machine "$machine" --file "$fp_local" 2>&1 \
  | sed -e 's/^/[publish] /' -e 's/ERROR: directory not found:/SKIP (absent sibling):/'
publish_rc="${PIPESTATUS[0]}"
publish_dur="$(( $(date +%s) - publish_start ))"
health_rc="$publish_rc"; [ "$health_rc" -gt 4 ] && health_rc=3
write_health publish "$publish_dur" "$health_rc" || exit 4
if [ "$publish_rc" -ne 0 ]; then
  echo "publish failed (rc=$publish_rc)" >&2
  exit 3
fi

# 3. collect + 4. compare (in one python pass)
report="$REPO_ROOT/.claude/state/equivalence/divergences-latest.json"
"${PYTHON_CMD[@]}" - "$report" "$MON" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[2])
import equivalence_state as store
import equivalence_compare as cmp
try:
    fps = store.collect(".")
    roster = cmp.load_expected_machines("config/workstations/registry.yaml")
    divs = cmp.compare(fps, expected_machines=roster or None)
    with open(sys.argv[1], "w") as handle:
        json.dump({"boxes": len(fps), "divergences": divs}, handle, indent=1)
    print(f"[compare] {len(fps)} box(es), {len(divs)} divergence(s)")
    for d in divs:
        print(f"  [{d['severity']}] {d['code']}: {d['detail']}")
    worst = cmp.worst_severity(divs)
except Exception as exc:
    print(f"[compare] controller failure: {exc}", file=sys.stderr)
    sys.exit(3)
sys.exit(2 if worst == cmp.CRITICAL else (1 if worst == cmp.WARNING else 0))
PY
rc=$?

# 5. alert on WARNING/CRITICAL
if [ "$rc" = "1" ] || [ "$rc" = "2" ]; then
  echo "EQUIVALENCE DRIFT (rc=$rc) at $ts — see $report" >&2
  if [ -n "${EQUIV_ALERT_ISSUE:-}" ] && command -v gh >/dev/null 2>&1; then
    body="$("${PYTHON_CMD[@]}" -c "import json,sys;d=json.load(open(sys.argv[1]));print('\n'.join(f\"- **{x[\"severity\"]}** \`{x[\"code\"]}\`: {x[\"detail\"]}\" for x in d['divergences']))" "$report" 2>/dev/null)"
    printf '## Machine-equivalence drift detected — %s\n\n%s\n' "$ts" "$body" \
      | gh issue comment "$EQUIV_ALERT_ISSUE" --body-file - 2>/dev/null \
      && echo "[alert] posted to #$EQUIV_ALERT_ISSUE" >&2
  fi
fi
exit "$rc"
