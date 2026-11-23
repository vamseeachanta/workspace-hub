#!/usr/bin/env bash
# aggregate-machine-status.sh — Fleet-wide harness-parity assessment.
# Issue: vamseeachanta/workspace-hub#2751 (Phase 3, G9 control-plane aggregator)
#
# Reads all config/machine-baselines/*.yaml and emits docs/reports/fleet-harness-status.md
# with per-dimension status across the fleet and per-dimension coverage summary.
#
# Intended runner: ace-linux-1 (control plane), per `feedback_cross_machine_execution`
# pattern. Each machine self-emits its baseline via emit-machine-status.sh and pushes;
# control plane pulls and runs this aggregator to surface drift.
#
# Usage:
#   bash scripts/setup/aggregate-machine-status.sh                # uses git rev-parse root
#   bash scripts/setup/aggregate-machine-status.sh <repo_root>    # explicit (tests)

set -uo pipefail

REPO_ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[[ -z "$REPO_ROOT" || ! -d "$REPO_ROOT" ]] && { echo "[aggregate] cannot resolve repo root" >&2; exit 1; }

BASELINES_DIR="${REPO_ROOT}/config/machine-baselines"
REPORT_DIR="${REPO_ROOT}/docs/reports"
REPORT="${REPORT_DIR}/fleet-harness-status.md"

mkdir -p "$REPORT_DIR"

# --- Collect machine baselines -----------------------------------------------

shopt -s nullglob
yaml_files=("${BASELINES_DIR}"/*.yaml)
shopt -u nullglob

if [[ ${#yaml_files[@]} -eq 0 ]]; then
    cat > "$REPORT" <<EMPTYEOF
# Fleet harness-parity status

> Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
> Source: \`scripts/setup/aggregate-machine-status.sh\` (issue #2751 G9)
> Operational tracker: #2753

## No machines registered

The \`config/machine-baselines/\` directory contains no \`*.yaml\` files. Run
\`bash scripts/setup/emit-machine-status.sh\` on each machine in the fleet and
commit the resulting file under \`config/machine-baselines/<token>.yaml\`.
EMPTYEOF
    echo "[aggregate] emitted empty-fleet report at $REPORT"
    exit 0
fi

# --- Parse each YAML — extract hostname, os, last_updated, and 22 dimension values ---
# Lightweight YAML parsing via awk (no yq dependency). Each YAML follows the
# exact format from emit-machine-status.sh, so structure is predictable.

DIMS=(soul_contracts skills rules bridged_memory claude_global_pointer \
      codex_agents_symlink hermes_soul_symlink claude_cli_auth codex_cli_auth \
      gh_cli_auth gemini_cli_auth hermes_can_boot raw_session_state \
      submodules_initialized git_hooks_installed shell_profile_wired \
      npm_global_prefix scheduler_entries ssh_key_present env_file_present \
      uv_or_python_available git_bash_available)

# Build markdown table header
{
    echo "# Fleet harness-parity status"
    echo ""
    echo "> Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "> Source: \`scripts/setup/aggregate-machine-status.sh\` (issue #2751 G9)"
    echo "> Operational tracker: #2753"
    echo "> Machines registered: ${#yaml_files[@]}"
    echo ""
    echo "## Per-machine status"
    echo ""
    # Header
    printf "| Machine | OS | Last-updated"
    for d in "${DIMS[@]}"; do printf " | %s" "$d"; done
    printf " |\n"
    printf "|---|---|---"
    for _ in "${DIMS[@]}"; do printf "|---"; done
    printf "|\n"
} > "$REPORT"

# Accumulator: per-dimension PASS count across machines
declare -A pass_count
declare -A fail_count
declare -A warn_count
for d in "${DIMS[@]}"; do pass_count[$d]=0; fail_count[$d]=0; warn_count[$d]=0; done
total_machines=${#yaml_files[@]}

drift_found=0

# Per-machine rows
for yaml_file in "${yaml_files[@]}"; do
    machine_token=$(basename "$yaml_file" .yaml)
    os=$(awk -F': ' '/^os:/ {gsub(/"/,"",$2); print $2; exit}' "$yaml_file")
    updated=$(awk -F': ' '/^last_updated:/ {gsub(/"/,"",$2); print $2; exit}' "$yaml_file")

    printf "| %s | %s | %s" "$machine_token" "$os" "$updated" >> "$REPORT"

    for d in "${DIMS[@]}"; do
        # Extract value for this dimension (lines with leading spaces under "dimensions:")
        val=$(awk -v key="$d" '
            /^dimensions:/ { in_dims=1; next }
            /^[^[:space:]]/ { in_dims=0 }
            in_dims && $1 == key":" { gsub(/"/, "", $2); print $2; exit }
        ' "$yaml_file")
        val="${val:-?}"

        # Tally
        case "$val" in
            PASS)                            pass_count[$d]=$((pass_count[$d] + 1)) ;;
            FAIL)                            fail_count[$d]=$((fail_count[$d] + 1)); drift_found=1 ;;
            WARN)                            warn_count[$d]=$((warn_count[$d] + 1)); drift_found=1 ;;
            machine-local-by-design|n/a)     pass_count[$d]=$((pass_count[$d] + 1)) ;;
        esac

        # Cell rendering: emoji-flagged so eye-scanning is fast
        case "$val" in
            PASS)                            cell="✅" ;;
            FAIL)                            cell="❌" ;;
            WARN)                            cell="⚠️" ;;
            machine-local-by-design)         cell="•" ;;
            n/a)                             cell="—" ;;
            *)                               cell="?" ;;
        esac
        printf " | %s" "$cell" >> "$REPORT"
    done
    printf " |\n" >> "$REPORT"
done

# Per-dimension coverage summary
{
    echo ""
    echo "## Per-dimension coverage"
    echo ""
    echo "| Dimension | PASS | WARN | FAIL | Coverage |"
    echo "|---|---|---|---|---|"
    for d in "${DIMS[@]}"; do
        p="${pass_count[$d]}"
        w="${warn_count[$d]}"
        f="${fail_count[$d]}"
        coverage="${p} of ${total_machines} machines"
        printf "| %s | %d | %d | %d | %s |\n" "$d" "$p" "$w" "$f" "$coverage"
    done

    echo ""
    if [[ "$drift_found" == "1" ]]; then
        echo "## Drift detected"
        echo ""
        echo "One or more dimensions show WARN/FAIL on at least one machine. See the"
        echo "per-machine table above for the affected cells, then run"
        echo "\`bash scripts/setup/new-machine-setup.sh\` on those machines to remediate."
    else
        echo "## All machines pass all dimensions ✅"
    fi
    echo ""
    echo "## How to update"
    echo ""
    echo "Run on each machine:"
    echo "\`\`\`"
    echo "bash scripts/setup/emit-machine-status.sh"
    echo "git add config/machine-baselines/ && git commit -m 'chore(setup): refresh machine baseline'"
    echo "git push"
    echo "\`\`\`"
    echo ""
    echo "Then on the control plane (\`ace-linux-1\`):"
    echo "\`\`\`"
    echo "git pull"
    echo "bash scripts/setup/aggregate-machine-status.sh"
    echo "\`\`\`"
} >> "$REPORT"

echo "[aggregate] emitted fleet status report at $REPORT  (${#yaml_files[@]} machine(s))"
