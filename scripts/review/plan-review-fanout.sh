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
#   codex   — INLINE: `codex exec "<prompt>\n--- PLAN ---\n<body>" </dev/null`
#             Codex drops context when given a path-only argument and falls
#             back to GitHub MCP lookups, producing false MAJORs. The
#             `--no-interactive` flag that this invocation previously used
#             was removed in codex-cli 0.124.0 (unknown argument, rc=2);
#             `codex exec` is already non-interactive by definition, so
#             dropping the flag is correct. See the fresh issue filed after
#             the 2026-04-23 batch regression (supersedes #2406 closure).
#             Stdin is closed with `</dev/null` to prevent codex from
#             waiting on an inherited pipe when invoked from orchestrators.
#   gemini  — INLINE, and invoked from cwd=/tmp to dodge a local
#             .gemini/agents/*.md permissionMode validation bug in the repo.
#
# Environment knobs (for tests/noninteractive runs):
#   PLAN_REVIEW_RESULTS_DIR — overrides the default results dir (superseded by --output-dir).
#   PLAN_REVIEW_PROVIDER_TIMEOUT_SEC — per-provider timeout in seconds (default: 600).
#   GEMINI_CLI_TRUST_WORKSPACE — defaults to true for noninteractive Gemini runs.

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
    *)
      if [[ -z "$PLAN_FILE" ]]; then
        PLAN_FILE="$1"
      else
        echo "unexpected positional arg: $1" >&2
        exit 2
      fi
      shift
      ;;
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
error_excerpt() {
  local err="$1"
  head -c 400 "$err" 2>/dev/null | tr '\n' ' ' | tr -d '\000-\010\013\014\016-\037\177' | sed 's/"/\\"/g'
}

write_unavailable() {
  local prov="$1" rc="$2" reason="$3" out="$4"
  {
    echo "## Verdict"
    echo "UNAVAILABLE (${prov} CLI failed, rc=${rc}: ${reason})"
    echo ""
    echo "## Retrieval"
    echo "(none — invocation failed before the provider could return a usable review)"
    echo ""
    echo "## Findings"
    echo "(none)"
    echo ""
    echo "## Blockers"
    echo "(none — this provider contributed no signal to the review)"
  } > "$out"
}

normalize_provider_output() {
  local prov="$1" rc="$2" out="$3" err="$4"

  if (( rc != 0 )); then
    local reason
    reason="$(error_excerpt "$err")"
    [[ -n "$reason" ]] || reason="no stderr captured"
    write_unavailable "$prov" "$rc" "$reason" "$out"
    rm -f "$err"
    return 0
  fi

  # Some CLIs stream the substantive review to stderr/session output while
  # leaving stdout empty. Promote stderr only after a successful provider exit
  # and only when it contains the minimum structured review sections.
  if [[ ! -s "$out" && -s "$err" ]] && grep -q '^## Verdict' "$err" && grep -q '^## Findings' "$err" && grep -q '^## Blockers' "$err"; then
    mv "$err" "$out"
    return 0
  fi

  if [[ ! -s "$out" ]]; then
    local reason
    reason="empty provider output"
    if [[ -s "$err" ]]; then
      reason="$(error_excerpt "$err")"
    fi
    write_unavailable "$prov" "0" "$reason" "$out"
  fi
  rm -f "$err"
}

invoke_provider() {
  local prov="$1"
  local out="$OUTPUT_DIR/${TODAY}-plan-${ISSUE_NUM}-${prov}.md"
  local err="${out}.err"
  local rc=0
  local timeout_s="${PLAN_REVIEW_PROVIDER_TIMEOUT_SEC:-600}"

  case "$prov" in
    claude)
      # Disable third-party plugin loading for the child claude session (#2683):
      # the codex plugin's SessionEnd hook does a synchronous fs.readFileSync(0)
      # with a 5s timeout that races claude's headless shutdown and causes
      # `claude -p` to exit rc=124 with `Hook cancelled`. Pointing
      # CLAUDE_PLUGIN_DIR at an empty directory disables plugin discovery for
      # THIS invocation only, leaving keychain/OAuth auth intact. (Earlier
      # iteration tried `--bare`, but that also disables keychain reads and
      # requires ANTHROPIC_API_KEY — incompatible with the typical local-dev
      # auth setup. The env-var override is mechanism-narrower and
      # version-independent.)
      local plugin_dir_override
      plugin_dir_override="$(mktemp -d -t claude-no-plugins-XXXXXX)"
      timeout -k 5s "${timeout_s}s" \
        env CLAUDE_PLUGIN_DIR="$plugin_dir_override" \
        claude -p "@$PROMPT_FILE — review the plan at $PLAN_FILE. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS." \
        > "$out" 2>"$err" || rc=$?
      rmdir "$plugin_dir_override" 2>/dev/null || true
      ;;
    codex)
      local combined
      combined="$(printf '%s\n\n--- PLAN (%s) ---\n%s' \
        "$(cat "$PROMPT_FILE")" "$PLAN_FILE" "$(cat "$PLAN_FILE")")"
      # Keep prompt delivery in argv and close stdin. The sibling
      # submit-to-codex.sh regression tests document that `codex exec -` can
      # hang in installed Codex versions, while argv + </dev/null avoids
      # inherited-pipe stalls. #2479 adds a version guard so known-bad Codex
      # installs produce an immediate UNAVAILABLE artifact instead of waiting
      # for provider timeout.
      # shellcheck source=/dev/null
      source "$SCRIPT_DIR/lib/codex-version-guard.sh"
      local guard_msg guard_rc=0
      guard_msg="$(codex_version_guard_check)" || guard_rc=$?
      if [[ "$guard_rc" -eq 3 ]]; then
        printf '%s\n' "$guard_msg" > "$err"
        rc=3
      else
        timeout -k 5s "${timeout_s}s" codex exec "$combined" > "$out" 2>"$err" </dev/null || rc=$?
      fi
      ;;
    gemini)
      local combined
      combined="$(printf '%s\n\n--- PLAN (%s) ---\n%s' \
        "$(cat "$PROMPT_FILE")" "$PLAN_FILE" "$(cat "$PLAN_FILE")")"
      # cwd=/tmp dodges the .gemini/agents/*.md permissionMode validation bug.
      # GEMINI_CLI_TRUST_WORKSPACE avoids noninteractive rc=55 trust prompts.
      ( cd /tmp && GEMINI_CLI_TRUST_WORKSPACE="${GEMINI_CLI_TRUST_WORKSPACE:-true}" \
          timeout -k 5s "${timeout_s}s" gemini -p "$combined" ) > "$out" 2>"$err" || rc=$?
      ;;
    *)
      echo "unknown provider: $prov" >&2
      return 2
      ;;
  esac

  normalize_provider_output "$prov" "$rc" "$out" "$err"
}

# ── Parallel fan-out ─────────────────────────────────────────────────────
IFS=',' read -ra PROV_LIST <<< "$PROVIDERS"
pids=()
cleanup_provider_jobs() {
  local pid
  for pid in "${pids[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
}
trap cleanup_provider_jobs INT TERM EXIT
for prov in "${PROV_LIST[@]}"; do
  invoke_provider "$prov" &
  pids+=($!)
done
for pid in "${pids[@]}"; do
  wait "$pid" || true
done
pids=()
trap - INT TERM EXIT

# ── Disagreement report (stub — fleshed out in next TDD batch) ───────────
DISAGREEMENT_FILE="$OUTPUT_DIR/${TODAY}-plan-${ISSUE_NUM}-disagreement.md"
if [[ -x "$SCRIPT_DIR/lib/disagreement-diff.sh" ]]; then
  bash "$SCRIPT_DIR/lib/disagreement-diff.sh" "$OUTPUT_DIR" "$TODAY" "$ISSUE_NUM" > "$DISAGREEMENT_FILE"
fi

echo "wrote artifacts to $OUTPUT_DIR for plan #${ISSUE_NUM} ($TODAY)"
