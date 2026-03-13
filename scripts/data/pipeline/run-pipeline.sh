#!/usr/bin/env bash
# run-pipeline.sh — Execute a named ETL pipeline
# Usage: run-pipeline.sh <pipeline-name> [--force-refresh]
# Exit codes: 0=success, 1=config error, 2=pipeline error

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

usage() {
    echo "Usage: $0 <pipeline-name> [--force-refresh]"
    echo ""
    echo "Available pipelines: eia_production, bsee_wells, yfinance_prices"
    echo ""
    echo "Options:"
    echo "  --force-refresh  Skip cache freshness check"
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

PIPELINE_NAME="$1"
FORCE_REFRESH=""

shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force-refresh)
            FORCE_REFRESH="--force-refresh"
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            ;;
    esac
    shift
done

# Validate pipeline name
case "${PIPELINE_NAME}" in
    eia_production|bsee_wells|yfinance_prices) ;;
    *)
        echo "Error: unknown pipeline '${PIPELINE_NAME}'" >&2
        echo "Available: eia_production, bsee_wells, yfinance_prices" >&2
        exit 1
        ;;
esac

export PYTHONPATH="${REPO_ROOT}/scripts:${REPO_ROOT}/worldenergydata/src:${REPO_ROOT}/assethold/src"

exec uv run --no-project \
    --with pydantic --with pandas --with pyyaml --with requests \
    python "${REPO_ROOT}/scripts/data/pipeline/run_pipeline_cli.py" \
    "${PIPELINE_NAME}" ${FORCE_REFRESH}
