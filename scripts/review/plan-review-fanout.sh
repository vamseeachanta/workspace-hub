#!/usr/bin/env bash
# plan-review-fanout.sh — #2323
# Run an adversarial plan review across Claude + Codex + Gemini in parallel and
# write one canonical artifact per provider under scripts/review/results/ (or a
# caller-supplied --output-dir).
#
# Usage:
#   plan-review-fanout.sh <plan-file> [--providers=claude,codex,gemini] [--output-dir=<dir>]
#
# Per-provider invocation shape (empirically tuned, see docs/plans/...2323...md):
#   claude  — path reference: `claude -p "@<prompt> — review plan at <path>..."`
#             Claude resolves @-sigils natively; passing by path keeps token
#             budget tight and the plan fresh on disk.
#   codex   — INLINE: `codex exec --no-interactive "<prompt>\n--- PLAN ---\n<body>"`
#             Codex drops context when given a path-only argument and falls
#             back to GitHub MCP lookups, producing false MAJORs.
#   gemini  — INLINE, and invoked from cwd=/tmp to dodge a local
#             .gemini/agents/*.md permissionMode validation bug in the repo.
#
# Environment knobs (for tests):
#   PLAN_REVIEW_RESULTS_DIR — overrides the default results dir (superseded by --output-dir).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/plan-file-parse.sh"

PROMPT_FILE="$SCRIPT_DIR/plan-review-prompt.md"

# ── Argument parsing ─────────────────────────────────────────────────────
PLAN_FILE=""
OUTPUT_DIR="${PLAN_REVIEW_RESULTS_DIR:-$SCRIPT_DIR/results}"
PROVIDERS="claude,codex,gemini"

usage() {
  sed -n '2,20p' "${BASH_SOURCE[0]}" >&2
}

while (( $# > 0 )); do
  case "$1" in
    --providers=*)  PROVIDERS="${1#*=}"; shift ;;
    --providers)    PROVIDERS="${2:?--providers requires a value}"; shift 2 ;;
    --output-dir=*) OUTPUT_DIR="${1#*=}"; shift ;;
    --output-dir)   OUTPUT_DIR="${2:?--output-dir requires a value}"; shift 2 ;;
    -h|--help)      usage; exit 0 ;;
    --)             shift; break ;;
    -*)             echo "unknown flag: $1" >&2; usage; exit 2 ;;
    *)              [[ -z "$PLAN_FILE" ]] && PLAN_FILE="$1" || { echo "unexpected positional arg: $1" >&2; exit 2; }; shift ;;
  esac
done

[[ -n "$PLAN_FILE" ]] || { usage; exit 2; }
[[ -f "$PLAN_FILE" ]] || { echo "plan file not found: $PLAN_FILE" >&2; exit 2; }

ISSUE_NUM="$(extract_issue_num "$PLAN_FILE")" || {
  echo "plan filename must match YYYY-MM-DD-issue-NNNN-<slug>.md; got: $PLAN_FILE" >&2
  exit 2
}
TODAY="$(date +%Y-%m-%d)"
mkdir -p "$OUTPUT_DIR"

# ── Per-provider invocation ──────────────────────────────────────────────
# Writes to $OUTPUT_DIR/$TODAY-plan-$ISSUE_NUM-<provider>.md. On CLI failure,
# writes an UNAVAILABLE-verdict stub instead (graceful degradation).
invoke_provider() {
  local prov="$1"
  local out="$OUTPUT_DIR/${TODAY}-plan-${ISSUE_NUM}-${prov}.md"
  local err="${out}.err"
  local rc=0

  case "$prov" in
    claude)
      # Path reference — no inline body.
      claude -p "@$PROMPT_FILE — review the plan at $PLAN_FILE. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS." \
        > "$out" 2>"$err" || rc=$?
      ;;
    codex)
      local combined
      combined="$(printf '%s\n\n--- PLAN (%s) ---\n%s' \
        "$(cat "$PROMPT_FILE")" "$PLAN_FILE" "$(cat "$PLAN_FILE")")"
      codex exec --no-interactive "$combined" > "$out" 2>"$err" || rc=$?
      ;;
    gemini)
      local combined
      combined="$(printf '%s\n\n--- PLAN (%s) ---\n%s' \
        "$(cat "$PROMPT_FILE")" "$PLAN_FILE" "$(cat "$PLAN_FILE")")"
      # cwd=/tmp dodges the .gemini/agents/*.md permissionMode validation bug.
      ( cd /tmp && gemini -p "$combined" ) > "$out" 2>"$err" || rc=$?
      ;;
    *)
      echo "unknown provider: $prov" >&2
      return 2
      ;;
  esac

  if (( rc != 0 )); then
    local reason
    reason="$(head -c 200 "$err" 2>/dev/null | tr '\n' ' ' | sed 's/"/\\"/g')"
    {
      echo "## Verdict"
      echo "UNAVAILABLE (${prov} CLI failed, rc=${rc}: ${reason})"
      echo ""
      echo "## Retrieval"
      echo "(none — invocation failed before the provider could read the plan)"
      echo ""
      echo "## Findings"
      echo "(none)"
      echo ""
      echo "## Blockers"
      echo "(none — this provider contributed no signal to the review)"
    } > "$out"
  fi
  rm -f "$err"
}

# ── Parallel fan-out ─────────────────────────────────────────────────────
IFS=',' read -ra PROV_LIST <<< "$PROVIDERS"
pids=()
for prov in "${PROV_LIST[@]}"; do
  invoke_provider "$prov" &
  pids+=($!)
done
for pid in "${pids[@]}"; do
  wait "$pid" || true
done

# ── Disagreement report (stub — fleshed out in next TDD batch) ───────────
DISAGREEMENT_FILE="$OUTPUT_DIR/${TODAY}-plan-${ISSUE_NUM}-disagreement.md"
if [[ -x "$SCRIPT_DIR/lib/disagreement-diff.sh" ]]; then
  bash "$SCRIPT_DIR/lib/disagreement-diff.sh" "$OUTPUT_DIR" "$TODAY" "$ISSUE_NUM" > "$DISAGREEMENT_FILE"
fi

echo "wrote artifacts to $OUTPUT_DIR for plan #${ISSUE_NUM} ($TODAY)"
