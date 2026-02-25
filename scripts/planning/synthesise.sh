#!/usr/bin/env bash
# synthesise.sh <results-dir> [wrk-file]
# Merges 9 agent outputs into synthesis.md using the Claude orchestrator.
# Parses structured output to detect SPLIT decisions and compute consensus score.
#
# Exit codes:
#   0  synthesis complete, score >= 70, no blocking splits
#   1  synthesis failed (Claude error or no valid inputs)
#   2  unresolved SPLIT decisions found (or score < 70)
set -euo pipefail

RESULTS_DIR="${1:?Usage: synthesise.sh <results-dir> [wrk-file]}"
WRK_FILE="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="${SCRIPT_DIR}/prompts"
SYNTHESIS_OUT="${RESULTS_DIR}/synthesis.md"

# Collect valid agent outputs (skip NO_OUTPUT / ERROR stubs / near-empty files)
CONCAT="$(mktemp)"
trap 'rm -f "$CONCAT"' EXIT

valid=0
for f in "${RESULTS_DIR}"/*.md; do
    [[ -f "$f" ]] || continue
    [[ "$(basename "$f")" == "synthesis.md" ]] && continue
    size="$(wc -c < "$f")"
    first_line="$(head -1 "$f" 2>/dev/null || echo "")"
    if [[ $size -lt 80 ]] || [[ "$first_line" == NO_OUTPUT:* ]] || [[ "$first_line" == ERROR:* ]]; then
        echo "    skip $(basename "$f") (${size}B / ${first_line:0:40})" >&2
        continue
    fi
    {
        echo "=== AGENT: $(basename "$f" .md) ==="
        cat "$f"
        echo ""
        echo "--- end $(basename "$f" .md) ---"
        echo ""
    } >> "$CONCAT"
    (( valid++ ))
done

if [[ $valid -eq 0 ]]; then
    echo "ERROR: no valid agent outputs in ${RESULTS_DIR}" >&2
    exit 1
fi
echo "    synthesising ${valid} valid outputs"

# Run Claude synthesis
SYNTH_PROMPT="$(cat "${PROMPTS_DIR}/synthesis.md")"
command -v claude >/dev/null 2>&1 || { echo "ERROR: claude CLI not found for synthesis" >&2; exit 1; }

{
    echo "$SYNTH_PROMPT"
    echo ""
    echo "---"
    echo "AGENT REPORTS (${valid} of 9 had valid output):"
    echo "---"
    cat "$CONCAT"
} | (unset CLAUDECODE; claude -p "Synthesise the agent reports above using the output format in the prompt.") \
    > "$SYNTHESIS_OUT" 2>&1 || { echo "ERROR: claude synthesis call failed" >&2; exit 1; }

# Validate structured output markers are present
if ! grep -q "^SYNTHESIS_START" "$SYNTHESIS_OUT" || ! grep -q "^SYNTHESIS_END" "$SYNTHESIS_OUT"; then
    echo "ERROR: synthesis.md missing required SYNTHESIS_START/END markers" >&2
    echo "       Claude may not have followed the output format. See: $SYNTHESIS_OUT" >&2
    exit 1
fi

# Extract consensus score
score="$(grep "^CONSENSUS_SCORE:" "$SYNTHESIS_OUT" | grep -o '[0-9]\+' | head -1 || echo "")"
if [[ -z "$score" ]]; then
    echo "WARN: could not parse CONSENSUS_SCORE from synthesis.md -- defaulting to 0" >&2
    score=0
fi
echo "    consensus score: ${score}/100"

# Detect unresolved splits (lines like "[SPLIT:NN] ...")
splits="$(grep -c "^\[SPLIT:" "$SYNTHESIS_OUT" 2>/dev/null || echo 0)"

if [[ $splits -gt 0 ]]; then
    echo ""
    echo "SPLIT decisions requiring user input (${splits} found):"
    awk '/^SPLITS_START/{f=1;next} /^SPLITS_END/{f=0} f && !/^NONE$/' "$SYNTHESIS_OUT"
    echo ""
    echo "Resolve the above before writing the ## Plan section."
    exit 2
fi

if [[ $score -lt 70 ]]; then
    echo "WARN: consensus score ${score} < 70 -- low confidence; review synthesis carefully." >&2
fi

echo "Synthesis complete: ${SYNTHESIS_OUT} (score=${score}, splits=0)"
exit 0
