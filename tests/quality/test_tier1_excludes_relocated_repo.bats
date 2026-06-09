#!/usr/bin/env bats
# Regression guard (#3012): OGManufacturing was relocated to /mnt/ace and is no
# longer an active tier-1 sibling. It must not reappear in any active tier-1
# repo list / gate script, or pre-push check-all fails ("Unknown repo") and
# forces a GIT_PRE_PUSH_SKIP bypass. Keeps the cleanup from silently drifting back.

REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"

GATE_SCRIPTS=(
  scripts/quality/check-all.sh
  scripts/quality/dep-health.sh
  scripts/docs/build-api-docs.sh
  scripts/release/cut-release.sh
  scripts/security/secrets-scan.sh
  scripts/cron/daily-cleanup.sh
)

@test "no active tier-1 gate script references the relocated OGManufacturing repo" {
  for f in "${GATE_SCRIPTS[@]}"; do
    run grep -niE 'ogmanufacturing' "$REPO_ROOT/$f"
    [ "$status" -ne 0 ] || { echo "FAIL: $f still references ogmanufacturing:"; echo "$output"; false; }
  done
}

@test "check-all.sh REPO_ORDER is exactly the 4 active tier-1 repos" {
  run bash -c "grep -E '^REPO_ORDER=' '$REPO_ROOT/scripts/quality/check-all.sh'"
  [ "$status" -eq 0 ]
  [[ "$output" == *"assetutilities digitalmodel worldenergydata assethold)"* ]]
  [[ "$output" != *"ogmanufacturing"* ]]
}

@test "check-all.sh rejects --repo ogmanufacturing as unknown" {
  run bash "$REPO_ROOT/scripts/quality/check-all.sh" --repo ogmanufacturing
  [ "$status" -ne 0 ]
  [[ "$output" == *"Unknown repo"* ]]
}
