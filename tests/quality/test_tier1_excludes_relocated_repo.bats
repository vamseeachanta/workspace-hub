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

# --- #3019: the remaining operational scripts must also stay clean ---
@test "no active operational script references the relocated OGManufacturing repo (#3019)" {
  # Gate-relevant + active repo-list scripts cleaned in #3019. The 4 documented
  # LEAVE files (ecosystem-rework-retriage.sh, suggest_model.sh,
  # quality_gap_report.py, check-tier1-repo-baseline.py) and historical
  # data-pipeline scripts are intentionally excluded.
  local cleaned=(
    scripts/testing/run-all-tests.sh
    scripts/cron/broken-windows-sweep.sh
    scripts/cron/coverage-drift-report.sh
    scripts/onboarding/generate-repo-map.py
    scripts/analysis/daily-reflect.sh
    scripts/search/build-symbol-index.py
    scripts/search/cross-repo-search.sh
    scripts/search/find-symbol.sh
    scripts/scaffolding/new-module.sh
    scripts/scaffolding/tests/test_new_module.sh
    scripts/development/ai-review/install-codex-hooks.sh
    scripts/development/ai-review/install-gemini-hooks.sh
  )
  for f in "${cleaned[@]}"; do
    run grep -niE 'ogmanufacturing' "$REPO_ROOT/$f"
    [ "$status" -ne 0 ] || { echo "FAIL: $f still references OGManufacturing:"; echo "$output"; false; }
  done
}
