#!/usr/bin/env bash
# Tests for pii_safe_snapshot (#3073, epic #3058). Run: bash tests/cron/test_pii_safe_memory_snapshot.sh
set -uo pipefail
ROOT="$(git rev-parse --show-toplevel)"
source "$ROOT/scripts/cron/lib/pii-safe-memory-snapshot.sh"

fail=0
check() { if [ "$1" = "$2" ]; then echo "ok: $3"; else echo "FAIL: $3 (got '$1' want '$2')"; fail=1; fi; }

work="$(mktemp -d)"; src="$work/src"; dest="$work/dest"; mkdir -p "$src" "$dest"
deny="$work/deny.yaml"
printf 'client_references:\n  - pattern: "Acme Field"\n    case_sensitive: false\n' > "$deny"

# generalizable (should copy)
echo "lesson: always verify" > "$src/feedback_verify.md"
echo "see https://x" > "$src/reference_link.md"
echo "# memory" > "$src/MEMORY.md"
# engagement-specific (must NOT copy)
echo "client campaign details" > "$src/project_fdas_corpus.md"
# deny-list match in a non-project file (must NOT copy)
echo "work on the Acme Field project" > "$src/feedback_acme.md"
# pre-existing leak already in dest (must be self-healed away)
echo "stale client" > "$dest/project_old_client.md"

out="$(pii_safe_snapshot "$src" "$dest" "$deny")"
echo "$out"

[ -f "$dest/feedback_verify.md" ]; check "$?" 0 "generalizable feedback_ copied"
[ -f "$dest/reference_link.md" ];  check "$?" 0 "reference_ copied"
[ -f "$dest/MEMORY.md" ];          check "$?" 0 "MEMORY.md copied"
[ ! -f "$dest/project_fdas_corpus.md" ]; check "$?" 0 "project_* NOT copied (structural)"
[ ! -f "$dest/feedback_acme.md" ];       check "$?" 0 "deny-list match NOT copied (defense-in-depth)"
[ ! -f "$dest/project_old_client.md" ];  check "$?" 0 "pre-existing project_* self-healed (removed)"

# missing source dir is safe (returns 0, no error)
pii_safe_snapshot "$work/nonexistent" "$dest" "$deny" >/dev/null; check "$?" 0 "missing src dir is safe"

rm -rf "$work"
if [ "$fail" = 0 ]; then echo "ALL PASS"; else echo "FAILURES"; exit 1; fi
