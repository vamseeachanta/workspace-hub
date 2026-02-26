#!/usr/bin/env bash
# =============================================================================
# gmsh_openfoam_orcaflex.sh — Shell wrapper for the multi-physics pipeline.
#
# Accepts geometry parameters and drives gmsh_openfoam_orcaflex.py.
# Sources OpenFOAM environment if available; falls back to stub mode when
# OpenFOAM or OrcFxAPI are absent.
#
# Usage:
#   ./gmsh_openfoam_orcaflex.sh [OPTIONS]
#
# Options:
#   --diameter FLOAT     Cylinder diameter in metres (required)
#   --length FLOAT       Cylinder length in metres (required)
#   --velocity FLOAT     Free-stream velocity in m/s (required)
#   --work-dir PATH      Working directory (default: /tmp/pipeline_<timestamp>)
#   --stub-mode          Force stub mode (no solver license required)
#   --json               Print full JSON result to stdout
#   -h, --help           Show this help message
#
# Examples:
#   ./gmsh_openfoam_orcaflex.sh --diameter 1.0 --length 5.0 --velocity 1.5
#   ./gmsh_openfoam_orcaflex.sh --diameter 0.5 --length 3.0 --velocity 2.0 --stub-mode
#
# Environment variables:
#   PIPELINE_STUB_MODE=1  Force stub mode (same as --stub-mode)
#   OF_ENV_SCRIPT         Path to OpenFOAM environment script
#                         (default: /usr/lib/openfoam/openfoam2312/etc/bashrc)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DIAMETER=""
LENGTH=""
VELOCITY=""
WORK_DIR="/tmp/pipeline_$(date +%Y%m%d_%H%M%S)"
STUB_MODE="${PIPELINE_STUB_MODE:-0}"
JSON_OUTPUT=0
OF_ENV_SCRIPT="${OF_ENV_SCRIPT:-/usr/lib/openfoam/openfoam2312/etc/bashrc}"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --diameter)    DIAMETER="$2"; shift 2 ;;
        --length)      LENGTH="$2";   shift 2 ;;
        --velocity)    VELOCITY="$2"; shift 2 ;;
        --work-dir)    WORK_DIR="$2"; shift 2 ;;
        --stub-mode)   STUB_MODE=1;   shift ;;
        --json)        JSON_OUTPUT=1; shift ;;
        -h|--help)
            sed -n '2,50p' "$0" | grep '^#' | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            exit 2
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Validate required arguments
# ---------------------------------------------------------------------------
if [[ -z "$DIAMETER" || -z "$LENGTH" || -z "$VELOCITY" ]]; then
    echo "ERROR: --diameter, --length, and --velocity are required." >&2
    echo "Run with --help for usage." >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# Locate the Python script (relative to this shell script)
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_PY="${SCRIPT_DIR}/gmsh_openfoam_orcaflex.py"

if [[ ! -f "$PIPELINE_PY" ]]; then
    echo "ERROR: Pipeline script not found: ${PIPELINE_PY}" >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# Optionally source OpenFOAM environment
# ---------------------------------------------------------------------------
if [[ "$STUB_MODE" -eq 0 ]] && [[ -f "$OF_ENV_SCRIPT" ]]; then
    echo "[pipeline.sh] Sourcing OpenFOAM environment: $OF_ENV_SCRIPT"
    # shellcheck source=/dev/null
    source "$OF_ENV_SCRIPT"
else
    if [[ "$STUB_MODE" -eq 0 ]]; then
        echo "[pipeline.sh] OpenFOAM env script not found: $OF_ENV_SCRIPT"
        echo "[pipeline.sh] Enabling stub mode automatically."
        STUB_MODE=1
    fi
fi

# ---------------------------------------------------------------------------
# Build Python command
# ---------------------------------------------------------------------------
PYTHON_CMD=(
    python3 "$PIPELINE_PY"
    --diameter "$DIAMETER"
    --length   "$LENGTH"
    --velocity "$VELOCITY"
    --work-dir "$WORK_DIR"
)

if [[ "$STUB_MODE" -eq 1 ]]; then
    PYTHON_CMD+=(--stub-mode)
fi

if [[ "$JSON_OUTPUT" -eq 1 ]]; then
    PYTHON_CMD+=(--json)
fi

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
echo "[pipeline.sh] Work directory : $WORK_DIR"
echo "[pipeline.sh] Parameters     : D=${DIAMETER}m  L=${LENGTH}m  U=${VELOCITY}m/s"
echo "[pipeline.sh] Stub mode      : $STUB_MODE"
echo ""

export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"
export PIPELINE_STUB_MODE="$STUB_MODE"

exec "${PYTHON_CMD[@]}"
