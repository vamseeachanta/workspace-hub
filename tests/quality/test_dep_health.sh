#!/usr/bin/env bash
# test_dep_health.sh — TDD tests for scripts/quality/dep-health.sh (WRK-1090)
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/quality/dep-health.sh"

PASS=0
FAIL=0
ERRORS=()

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1"; ((FAIL++)); ERRORS+=("$1"); }

assert_exit() {
    local label="$1" expected="$2"; shift 2
    local actual; actual=$("$@" 2>&1); local rc=$?
    if [[ $rc -eq $expected ]]; then pass "$label (exit $rc)";
    else fail "$label: expected exit $expected, got $rc"; fi
}

assert_contains() {
    local label="$1" needle="$2" haystack="$3"
    if echo "$haystack" | grep -qi "$needle"; then pass "$label";
    else fail "$label: '$needle' not found in output"; fi
}

# ---------------------------------------------------------------------------
# Fixture setup helpers
# ---------------------------------------------------------------------------
make_fixture_repo() {
    local dir="$1" name="$2"
    mkdir -p "$dir/$name"
    cat > "$dir/$name/pyproject.toml" << 'TOML'
[project]
name = "fixture"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = ["requests>=2.0"]
TOML
    cat > "$dir/$name/uv.lock" << 'LOCK'
version = 1
requires-python = ">=3.9"
LOCK
}

make_mock_dir() {
    local mock_dir="$1"
    mkdir -p "$mock_dir"

    # Mock uv
    cat > "$mock_dir/uv" << 'EOF'
#!/usr/bin/env bash
# Route based on argument patterns
case "$1" in
    lock)
        # uv lock --check [--offline]
        exit "${MOCK_UV_LOCK_EXIT:-0}"
        ;;
    run)
        if [[ "${2:-}" == "--no-project" && "${3:-}" == "python" ]]; then
            # Pass through to real python3 for JSON parsing
            shift 3
            exec python3 "$@"
        fi
        if [[ "${2:-}" == "pip" && "${3:-}" == "list" ]]; then
            echo "${MOCK_UV_PIP_OUTDATED:-[]}"
            exit 0
        fi
        exit 0
        ;;
    export)
        echo "requests==2.28.0"
        exit 0
        ;;
esac
exit 0
EOF
    chmod +x "$mock_dir/uv"

    # Mock uvx
    cat > "$mock_dir/uvx" << 'EOF'
#!/usr/bin/env bash
# uvx pip-audit --format=json ...
echo "${MOCK_UVX_PIPAUDIT:-[]}"
exit "${MOCK_UVX_EXIT:-0}"
EOF
    chmod +x "$mock_dir/uvx"

    # Mock gh-next-id.sh (used for auto-WRK) — returns ID + URL like real script
    mkdir -p "$mock_dir/../scripts/work-queue"
    cat > "$mock_dir/../scripts/work-queue/gh-next-id.sh" << 'EOF'
#!/usr/bin/env bash
echo "99999"
echo "https://github.com/test/issues/99999"
EOF
    chmod +x "$mock_dir/../scripts/work-queue/gh-next-id.sh"
}

# ---------------------------------------------------------------------------
# T1: freshness-check — stale lock exits 1
# ---------------------------------------------------------------------------
echo "T1: freshness-check stale"
{
    TMPDIR_T1=$(mktemp -d)
    trap "rm -rf $TMPDIR_T1" EXIT
    make_fixture_repo "$TMPDIR_T1" assetutilities
    make_fixture_repo "$TMPDIR_T1" digitalmodel
    make_fixture_repo "$TMPDIR_T1" worldenergydata
    make_fixture_repo "$TMPDIR_T1" assethold
    mkdir -p "$TMPDIR_T1/OGManufacturing"
    touch "$TMPDIR_T1/OGManufacturing/pyproject.toml" "$TMPDIR_T1/OGManufacturing/uv.lock"
    MOCK_DIR_T1="$TMPDIR_T1/.mock"
    make_mock_dir "$MOCK_DIR_T1"
    mkdir -p "$TMPDIR_T1/.claude/work-queue/pending" "$TMPDIR_T1/logs/quality"
    OUT=$(QUALITY_REPO_ROOT="$TMPDIR_T1" \
          PATH="$MOCK_DIR_T1:$PATH" \
          SCRIPTS_OVERRIDE="$MOCK_DIR_T1/.." \
          MOCK_UV_LOCK_EXIT=1 \
          bash "$SCRIPT" 2>&1); rc=$?
    if [[ $rc -eq 1 ]]; then pass "T1: stale lock → exit 1";
    else fail "T1: expected exit 1, got $rc"; fi
    assert_contains "T1: STALE in output" "STALE" "$OUT"
    trap - EXIT
    rm -rf "$TMPDIR_T1"
}

# ---------------------------------------------------------------------------
# T2: freshness-check — fresh lock exits 0 (no CVEs)
# ---------------------------------------------------------------------------
echo "T2: freshness-check fresh"
{
    TMPDIR_T2=$(mktemp -d)
    make_fixture_repo "$TMPDIR_T2" assetutilities
    make_fixture_repo "$TMPDIR_T2" digitalmodel
    make_fixture_repo "$TMPDIR_T2" worldenergydata
    make_fixture_repo "$TMPDIR_T2" assethold
    mkdir -p "$TMPDIR_T2/OGManufacturing"
    touch "$TMPDIR_T2/OGManufacturing/pyproject.toml" "$TMPDIR_T2/OGManufacturing/uv.lock"
    MOCK_DIR_T2="$TMPDIR_T2/.mock"
    make_mock_dir "$MOCK_DIR_T2"
    mkdir -p "$TMPDIR_T2/.claude/work-queue/pending" "$TMPDIR_T2/logs/quality"
    OUT=$(QUALITY_REPO_ROOT="$TMPDIR_T2" \
          PATH="$MOCK_DIR_T2:$PATH" \
          SCRIPTS_OVERRIDE="$MOCK_DIR_T2/.." \
          MOCK_UV_LOCK_EXIT=0 \
          bash "$SCRIPT" 2>&1)
    rc=$?
    if [[ $rc -eq 0 ]]; then pass "T2: fresh lock → exit 0";
    else fail "T2: expected exit 0, got $rc"; fi
    rm -rf "$TMPDIR_T2"
}

# ---------------------------------------------------------------------------
# T3: outdated-detection — packages returned → warn only (exit 0 if no CVEs)
# ---------------------------------------------------------------------------
echo "T3: outdated detection warn-only"
{
    TMPDIR_T3=$(mktemp -d)
    make_fixture_repo "$TMPDIR_T3" assetutilities
    make_fixture_repo "$TMPDIR_T3" digitalmodel
    make_fixture_repo "$TMPDIR_T3" worldenergydata
    make_fixture_repo "$TMPDIR_T3" assethold
    mkdir -p "$TMPDIR_T3/OGManufacturing"
    touch "$TMPDIR_T3/OGManufacturing/pyproject.toml" "$TMPDIR_T3/OGManufacturing/uv.lock"
    MOCK_DIR_T3="$TMPDIR_T3/.mock"
    make_mock_dir "$MOCK_DIR_T3"
    mkdir -p "$TMPDIR_T3/.claude/work-queue/pending" "$TMPDIR_T3/logs/quality"
    OUTDATED_JSON='[{"name":"requests","version":"2.28.0","latest_version":"2.31.0"}]'
    OUT=$(QUALITY_REPO_ROOT="$TMPDIR_T3" \
          PATH="$MOCK_DIR_T3:$PATH" \
          SCRIPTS_OVERRIDE="$MOCK_DIR_T3/.." \
          MOCK_UV_LOCK_EXIT=0 \
          MOCK_UV_PIP_OUTDATED="$OUTDATED_JSON" \
          bash "$SCRIPT" 2>&1)
    rc=$?
    if [[ $rc -eq 0 ]]; then pass "T3: outdated packages → exit 0 (warn only)";
    else fail "T3: expected exit 0 for outdated-only, got $rc"; fi
    assert_contains "T3: OUTDATED/WARN in output" "outdated\|warn" "$OUT"
    rm -rf "$TMPDIR_T3"
}

# ---------------------------------------------------------------------------
# T4: CVE-scan — HIGH finding → exit 1
# ---------------------------------------------------------------------------
echo "T4: CVE HIGH finding exits 1"
{
    TMPDIR_T4=$(mktemp -d)
    make_fixture_repo "$TMPDIR_T4" assetutilities
    make_fixture_repo "$TMPDIR_T4" digitalmodel
    make_fixture_repo "$TMPDIR_T4" worldenergydata
    make_fixture_repo "$TMPDIR_T4" assethold
    mkdir -p "$TMPDIR_T4/OGManufacturing"
    touch "$TMPDIR_T4/OGManufacturing/pyproject.toml" "$TMPDIR_T4/OGManufacturing/uv.lock"
    MOCK_DIR_T4="$TMPDIR_T4/.mock"
    make_mock_dir "$MOCK_DIR_T4"
    mkdir -p "$TMPDIR_T4/.claude/work-queue/pending" "$TMPDIR_T4/logs/quality"
    CVE_JSON='[{"name":"requests","version":"2.28.0","vulns":[{"id":"CVE-2023-1234","fix_versions":["2.31.0"],"aliases":[],"description":"test"}]}]'
    OUT=$(QUALITY_REPO_ROOT="$TMPDIR_T4" \
          PATH="$MOCK_DIR_T4:$PATH" \
          SCRIPTS_OVERRIDE="$MOCK_DIR_T4/.." \
          MOCK_UV_LOCK_EXIT=0 \
          MOCK_UVX_PIPAUDIT="$CVE_JSON" \
          MOCK_UVX_EXIT=1 \
          bash "$SCRIPT" 2>&1); rc=$?
    if [[ $rc -eq 1 ]]; then pass "T4: CVE vuln → exit 1";
    else fail "T4: expected exit 1, got $rc"; fi
    assert_contains "T4: CVE/BLOCKING in output" "cve\|blocking\|vuln" "$OUT"
    rm -rf "$TMPDIR_T4"
}

# ---------------------------------------------------------------------------
# T5: CVE-scan — clean scan → exit 0
# ---------------------------------------------------------------------------
echo "T5: CVE clean scan exits 0"
{
    TMPDIR_T5=$(mktemp -d)
    make_fixture_repo "$TMPDIR_T5" assetutilities
    make_fixture_repo "$TMPDIR_T5" digitalmodel
    make_fixture_repo "$TMPDIR_T5" worldenergydata
    make_fixture_repo "$TMPDIR_T5" assethold
    mkdir -p "$TMPDIR_T5/OGManufacturing"
    touch "$TMPDIR_T5/OGManufacturing/pyproject.toml" "$TMPDIR_T5/OGManufacturing/uv.lock"
    MOCK_DIR_T5="$TMPDIR_T5/.mock"
    make_mock_dir "$MOCK_DIR_T5"
    mkdir -p "$TMPDIR_T5/.claude/work-queue/pending" "$TMPDIR_T5/logs/quality"
    OUT=$(QUALITY_REPO_ROOT="$TMPDIR_T5" \
          PATH="$MOCK_DIR_T5:$PATH" \
          SCRIPTS_OVERRIDE="$MOCK_DIR_T5/.." \
          MOCK_UV_LOCK_EXIT=0 \
          MOCK_UVX_PIPAUDIT="[]" \
          MOCK_UVX_EXIT=0 \
          bash "$SCRIPT" 2>&1)
    rc=$?
    if [[ $rc -eq 0 ]]; then pass "T5: clean CVE scan → exit 0";
    else fail "T5: expected exit 0 for clean scan, got $rc"; fi
    rm -rf "$TMPDIR_T5"
}

# ---------------------------------------------------------------------------
# T6: auto-WRK creation — HIGH CVE → pending/WRK-9999.md written
# ---------------------------------------------------------------------------
echo "T6: auto-WRK creation on HIGH CVE"
{
    TMPDIR_T6=$(mktemp -d)
    make_fixture_repo "$TMPDIR_T6" assetutilities
    make_fixture_repo "$TMPDIR_T6" digitalmodel
    make_fixture_repo "$TMPDIR_T6" worldenergydata
    make_fixture_repo "$TMPDIR_T6" assethold
    mkdir -p "$TMPDIR_T6/OGManufacturing"
    touch "$TMPDIR_T6/OGManufacturing/pyproject.toml" "$TMPDIR_T6/OGManufacturing/uv.lock"
    MOCK_DIR_T6="$TMPDIR_T6/.mock"
    make_mock_dir "$MOCK_DIR_T6"
    mkdir -p "$TMPDIR_T6/.claude/work-queue/pending" "$TMPDIR_T6/logs/quality"
    CVE_JSON='[{"name":"requests","version":"2.28.0","vulns":[{"id":"CVE-2023-9999","fix_versions":["2.31.0"],"aliases":[],"description":"test"}]}]'
    QUALITY_REPO_ROOT="$TMPDIR_T6" \
    PATH="$MOCK_DIR_T6:$PATH" \
    SCRIPTS_OVERRIDE="$MOCK_DIR_T6/.." \
    MOCK_UV_LOCK_EXIT=0 \
    MOCK_UVX_PIPAUDIT="$CVE_JSON" \
    MOCK_UVX_EXIT=1 \
    bash "$SCRIPT" 2>&1 || true
    if ls "$TMPDIR_T6/.claude/work-queue/pending/"*.md 2>/dev/null | grep -q .; then
        pass "T6: auto-WRK file created in pending/";
    else
        fail "T6: no WRK file found in $TMPDIR_T6/.claude/work-queue/pending/";
    fi
    rm -rf "$TMPDIR_T6"
}

# ---------------------------------------------------------------------------
# T7: YAML report written with required fields
# ---------------------------------------------------------------------------
echo "T7: YAML report written"
{
    TMPDIR_T7=$(mktemp -d)
    make_fixture_repo "$TMPDIR_T7" assetutilities
    make_fixture_repo "$TMPDIR_T7" digitalmodel
    make_fixture_repo "$TMPDIR_T7" worldenergydata
    make_fixture_repo "$TMPDIR_T7" assethold
    mkdir -p "$TMPDIR_T7/OGManufacturing"
    touch "$TMPDIR_T7/OGManufacturing/pyproject.toml" "$TMPDIR_T7/OGManufacturing/uv.lock"
    MOCK_DIR_T7="$TMPDIR_T7/.mock"
    make_mock_dir "$MOCK_DIR_T7"
    mkdir -p "$TMPDIR_T7/.claude/work-queue/pending" "$TMPDIR_T7/logs/quality"
    QUALITY_REPO_ROOT="$TMPDIR_T7" \
    PATH="$MOCK_DIR_T7:$PATH" \
    SCRIPTS_OVERRIDE="$MOCK_DIR_T7/.." \
    MOCK_UV_LOCK_EXIT=0 \
    bash "$SCRIPT" 2>&1 || true
    REPORT=$(ls "$TMPDIR_T7/logs/quality/dep-health-"*.yaml 2>/dev/null | head -1)
    if [[ -n "$REPORT" && -f "$REPORT" ]]; then
        pass "T7: YAML report created at $REPORT"
        if grep -q "run_at:" "$REPORT"; then pass "T7: report has run_at field";
        else fail "T7: report missing run_at field"; fi
    else
        fail "T7: no dep-health-*.yaml report found in $TMPDIR_T7/logs/quality/"
    fi
    rm -rf "$TMPDIR_T7"
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: $PASS passed, $FAIL failed"
if [[ ${#ERRORS[@]} -gt 0 ]]; then
    echo "Failed tests:"
    for e in "${ERRORS[@]}"; do echo "  - $e"; done
fi
[[ $FAIL -eq 0 ]]
