#!/usr/bin/env bash
# Regression tests for tier-1 repo consumers on sibling layouts (#3127).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PASS=0
FAIL=0

ok() { echo "  ok   $1"; PASS=$((PASS + 1)); }
bad() { echo "  FAIL $1"; echo "       $2"; FAIL=$((FAIL + 1)); }

contains() {
  local name="$1" needle="$2" haystack="$3"
  [[ "$haystack" == *"$needle"* ]] && ok "$name" || bad "$name" "missing: $needle"
}

not_contains() {
  local name="$1" needle="$2" haystack="$3"
  [[ "$haystack" != *"$needle"* ]] && ok "$name" || bad "$name" "unexpected: $needle"
}

MB="$(mktemp -d)"
MOCK="$(mktemp -d)"
trap 'rm -rf "$MB" "$MOCK"' EXIT

HUB="$MB/workspace-hub"
REPO="$MB/assetutilities"
DIGITALMODEL="$MB/digitalmodel"
mkdir -p "$HUB/scripts/lib" "$HUB/scripts/testing" "$HUB/scripts/security" "$HUB/config" "$REPO/tests" "$DIGITALMODEL/tests/contracts"
cp "$ROOT/scripts/lib/tier1-repos.sh" "$HUB/scripts/lib/tier1-repos.sh"
cp "$ROOT/scripts/testing/run-all-tests.sh" "$HUB/scripts/testing/run-all-tests.sh"
cp "$ROOT/scripts/testing/parse_pytest_output.py" "$HUB/scripts/testing/parse_pytest_output.py"
cp "$ROOT/scripts/security/secrets-scan.sh" "$HUB/scripts/security/secrets-scan.sh"
touch "$HUB/scripts/testing/expected-failures.txt" "$HUB/.gitleaks.toml"
printf 'assetutilities\n' > "$HUB/config/tier1-python-repos.txt"
printf '[project]\nname = "assetutilities"\n' > "$REPO/pyproject.toml"
printf '[project]\nname = "digitalmodel"\n' > "$DIGITALMODEL/pyproject.toml"
git -C "$HUB" init -q

UV_CWD_LOG="$MB/uv-cwd.log"
GITLEAKS_SOURCE_LOG="$MB/gitleaks-source.log"
export UV_CWD_LOG GITLEAKS_SOURCE_LOG

cat > "$MOCK/uv" <<'MOCK_UV'
#!/usr/bin/env bash
if [[ "$1" == "run" && "$2" == "python" && "$3" == "-m" && "$4" == "pytest" ]]; then
  pwd >> "$UV_CWD_LOG"
  echo "1 passed in 0.01s"
  exit 0
fi
if [[ "$1" == "run" && "$2" == "--no-project" && "$3" == "python" ]]; then
  shift 3
  python "$@"
  exit $?
fi
echo "mock uv: unsupported args: $*" >&2
exit 1
MOCK_UV
chmod +x "$MOCK/uv"

cat > "$MOCK/gitleaks" <<'MOCK_GITLEAKS'
#!/usr/bin/env bash
while [[ $# -gt 0 ]]; do
  if [[ "$1" == "--source" ]]; then
    echo "$2" >> "$GITLEAKS_SOURCE_LOG"
    shift 2
    continue
  fi
  shift
done
exit 0
MOCK_GITLEAKS
chmod +x "$MOCK/gitleaks"
export PATH="$MOCK:$PATH"

echo "-- run-all-tests resolves sibling repo --"
run_out="$(bash "$HUB/scripts/testing/run-all-tests.sh" --repo assetutilities 2>&1)"
contains "run-all-tests reports ok" "assetutilities" "$run_out"
contains "run-all-tests status ok" "ok" "$run_out"
if [[ -f "$UV_CWD_LOG" && "$(cat "$UV_CWD_LOG")" == "$REPO" ]]; then
  ok "run-all-tests invoked pytest in sibling repo"
else
  bad "run-all-tests invoked pytest in sibling repo" "$(cat "$UV_CWD_LOG" 2>/dev/null || echo '<no pytest invocation>')"
fi
not_contains "run-all-tests --repo does not run unrelated contract tests" "$DIGITALMODEL" "$(cat "$UV_CWD_LOG" 2>/dev/null || true)"

echo "-- secrets-scan resolves sibling repo --"
sec_exit=0
sec_out="$(bash "$HUB/scripts/security/secrets-scan.sh" --repo assetutilities 2>&1)" || sec_exit=$?
[[ "$sec_exit" -eq 0 ]] && ok "secrets-scan exits 0" || bad "secrets-scan exits 0" "$sec_out"
not_contains "secrets-scan no nested missing-repo error" "repository not found: $HUB/assetutilities" "$sec_out"
if [[ -f "$GITLEAKS_SOURCE_LOG" && "$(cat "$GITLEAKS_SOURCE_LOG")" == "$REPO" ]]; then
  ok "secrets-scan invoked gitleaks on sibling repo"
else
  bad "secrets-scan invoked gitleaks on sibling repo" "$(cat "$GITLEAKS_SOURCE_LOG" 2>/dev/null || echo '<no gitleaks invocation>')"
fi

echo
echo "[test_tier1_consumer_layouts] PASS=$PASS FAIL=$FAIL"
[[ "$FAIL" -eq 0 ]]
