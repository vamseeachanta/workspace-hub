#!/usr/bin/env bats
# #3023 — single source of truth for the tier-1 Python repo list.
# Verifies the canonical file (config/tier1-python-repos.txt) drives both
# helpers, that overriding it PROPAGATES (proving consumers aren't hardcoded),
# and that the refactored consumers are wired to the helper.

REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
CANON="assetutilities digitalmodel worldenergydata assethold"

setup() {
  TMPDIR=$(mktemp -d)
  # A deliberately different fixture set to prove propagation.
  printf '# fixture\nalpharepo\nbetarepo\n' > "$TMPDIR/fixture.txt"
}
teardown() { rm -rf "$TMPDIR"; }

@test "bash helper reads the canonical 4 repos" {
  run bash -c "REPO_ROOT='$REPO_ROOT' source '$REPO_ROOT/scripts/lib/tier1-repos.sh' && echo \"\${TIER1_PYTHON_REPOS[*]}\""
  [ "$status" -eq 0 ]
  [ "$output" = "$CANON" ]
}

@test "bash helper PROPAGATES an override (consumers aren't hardcoded)" {
  run bash -c "TIER1_REPOS_FILE='$TMPDIR/fixture.txt' source '$REPO_ROOT/scripts/lib/tier1-repos.sh' && echo \"\${TIER1_PYTHON_REPOS[*]}\""
  [ "$status" -eq 0 ]
  [ "$output" = "alpharepo betarepo" ]
}

@test "bash helper fails loudly on an empty/missing list (no silent no-op gate)" {
  printf '# only comments\n' > "$TMPDIR/empty.txt"
  run bash -c "TIER1_REPOS_FILE='$TMPDIR/empty.txt' source '$REPO_ROOT/scripts/lib/tier1-repos.sh'"
  [ "$status" -ne 0 ]
}

@test "python helper reads the canonical 4 repos" {
  run python3 "$REPO_ROOT/scripts/lib/tier1_repos.py"
  [ "$status" -eq 0 ]
  [ "$(echo "$output" | tr '\n' ' ' | sed 's/ $//')" = "$CANON" ]
}

@test "python helper PROPAGATES an override" {
  run env TIER1_REPOS_FILE="$TMPDIR/fixture.txt" python3 "$REPO_ROOT/scripts/lib/tier1_repos.py"
  [ "$status" -eq 0 ]
  [ "$(echo "$output" | tr '\n' ' ' | sed 's/ $//')" = "alpharepo betarepo" ]
}

@test "check-all.sh derives REPO_ORDER from the canonical file (override propagates)" {
  # check-all.sh validates --repo against REPO_ORDER; with the fixture, the
  # canonical repos become unknown and a fixture repo becomes known.
  run env TIER1_REPOS_FILE="$TMPDIR/fixture.txt" bash "$REPO_ROOT/scripts/quality/check-all.sh" --repo digitalmodel
  [[ "$output" == *"Unknown repo"* ]]
}

@test "refactored consumers source the SSoT helper (no second hardcoded list)" {
  local consumers=(
    scripts/quality/check-all.sh scripts/quality/dep-health.sh
    scripts/docs/build-api-docs.sh scripts/testing/run-all-tests.sh
    scripts/cron/broken-windows-sweep.sh scripts/cron/coverage-drift-report.sh
    scripts/cron/daily-cleanup.sh scripts/security/secrets-scan.sh
    scripts/search/find-symbol.sh scripts/search/cross-repo-search.sh
  )
  for f in "${consumers[@]}"; do
    run grep -q 'scripts/lib/tier1-repos.sh' "$REPO_ROOT/$f"
    [ "$status" -eq 0 ] || { echo "FAIL: $f does not source the SSoT helper"; false; }
  done
}
