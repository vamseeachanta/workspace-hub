#!/usr/bin/env bash
# bundle-verify-sentinel.sh — scheduled integrity check for the encrypted
# relocation bundles on /mnt/ace.
#
# WHY THIS EXISTS
# The bundles are the ONLY copy of ~110 GB of data whose sources were deleted on
# 2026-08-02. They live under /mnt/ace, which Samba exports as [ace_drive] with
# `guest ok = yes`, `public = yes` AND `force user = vamsee`. Because guests are
# mapped to the owning user, unix permissions do NOT protect these files — any
# LAN device can delete or truncate them. Detection is the available control, so
# this runs on a schedule and shouts when something moves.
#
# MODES
#   fast  (default) — existence + byte size only. Cheap; catches deletion and
#                     truncation, which are the realistic failure modes.
#   full            — also re-computes the SHA-256 of every bundle (~57 GB read,
#                     tens of minutes). Catches silent in-place modification.
#
# Exit status: 0 all good, 1 one or more failures. Cron mails/logs on failure.
set -uo pipefail
MODE="${1:-fast}"
# Overridable so the failure paths can be exercised against a fixture tree.
# A sentinel whose alarm has never been proven to fire is not a sentinel.
BULK="${BULK:-/mnt/ace/work-surface-bulk}"
fail=0; checked=0

ts() { date '+%F %T'; }
echo "[$(ts)] bundle-verify-sentinel start (mode=$MODE)"

shopt -s nullglob
mapfile -t ATT < <(find "$BULK" -name '*.attest' 2>/dev/null | sort)
if [ "${#ATT[@]}" -eq 0 ]; then
  echo "[$(ts)] FAIL: no attestation files found under $BULK — either nothing is"
  echo "        attested or the tree is gone. This is itself an alert."
  exit 1
fi

for a in "${ATT[@]}"; do
  b="${a%.attest}"
  name=$(basename "$b")
  checked=$((checked+1))

  if [ ! -f "$b" ]; then
    echo "[$(ts)] FAIL $name: BUNDLE MISSING (attestation present, file gone)"
    fail=$((fail+1)); continue
  fi

  want_sz=$(awk '/^ciphertext_bytes/{print $2}' "$a")
  got_sz=$(stat -c %s "$b")
  if [ "$want_sz" != "$got_sz" ]; then
    echo "[$(ts)] FAIL $name: SIZE CHANGED expected=$want_sz actual=$got_sz"
    fail=$((fail+1)); continue
  fi

  if [ "$MODE" = full ]; then
    want_cs=$(awk '/^ciphertext_sha256/{print $2}' "$a")
    got_cs=$(sha256sum "$b" | cut -d' ' -f1)
    if [ "$want_cs" != "$got_cs" ]; then
      echo "[$(ts)] FAIL $name: SHA256 MISMATCH — contents modified in place"
      fail=$((fail+1)); continue
    fi
    echo "[$(ts)] ok   $name (size + sha256)"
  else
    echo "[$(ts)] ok   $name (size $got_sz)"
  fi
done

echo "[$(ts)] done — checked=$checked failures=$fail"
[ "$fail" -eq 0 ] || echo "[$(ts)] ALERT: $fail bundle(s) failed verification. These are SOLE COPIES."
exit $([ "$fail" -eq 0 ] && echo 0 || echo 1)
