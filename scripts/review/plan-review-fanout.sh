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
#   codex   — STDIN: `codex exec - < private-payload-file` (#3462).
#             A finite file provides EOF without putting plan text in argv.
#             The existing version guard still rejects known stdin regressions.
#   gemini  — INLINE, and invoked from cwd=/tmp to dodge a local
#             .gemini/agents/*.md permissionMode validation bug in the repo.
#
# Environment knobs (for tests/noninteractive runs):
#   PLAN_REVIEW_RESULTS_DIR — overrides the default results dir (superseded by --output-dir).
#   PLAN_REVIEW_PROVIDER_TIMEOUT_SEC — per-provider timeout in seconds (default: 600).
#   PLAN_REVIEW_PREFLIGHT_TIMEOUT_SEC — timeout for each version/auth probe;
#     defaults to the provider timeout. No probe starts an interactive login.
#   GEMINI_CLI_TRUST_WORKSPACE — defaults to true for noninteractive Gemini runs.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/plan-file-parse.sh"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/provider-preflight.sh"

PROMPT_FILE="$SCRIPT_DIR/plan-review-prompt.md"

# ── Argument parsing ─────────────────────────────────────────────────────
PLAN_FILE=""
OUTPUT_DIR="${PLAN_REVIEW_RESULTS_DIR:-$SCRIPT_DIR/results}"
PROVIDERS="claude,codex,agy"

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

provider_returned_invalid_output() {
  local out="$1"
  local first verdict
  [[ -s "$out" ]] || return 1
  first="$(sed -n '1p' "$out")"
  [[ "$first" == "## Verdict" ]] || return 1
  verdict="$(awk 'NR > 1 && NF { print; exit }' "$out")"
  [[ "$verdict" =~ ^INVALID_OUTPUT([[:space:]\(]|$) ]]
}

provider_returned_structured_review() {
  local out="$1" verdict
  grep -q '^## Verdict$' "$out" && grep -q '^## Retrieval$' "$out" &&
    grep -q '^## Findings$' "$out" && grep -q '^## Blockers$' "$out" || return 1
  verdict="$(awk '/^## Verdict$/ { found=1; next } found && NF { print; exit }' "$out")"
  # plan-review-prompt.md defines the three review verdicts; UNAVAILABLE is
  # explicitly allowed there for incomplete context. Never infer success from
  # arbitrary text that merely contains section headings.
  [[ "$verdict" =~ ^(APPROVE|MINOR|MAJOR|UNAVAILABLE|INVALID_OUTPUT)([[:space:]\(]|$) ]]
}

normalize_provider_output() {
  local prov="$1" rc="$2" out="$3" err="$4"

  if (( rc != 0 )); then
    if provider_returned_invalid_output "$out"; then
      failure_category="INVALID_OUTPUT"
      rm -f "$err"
      return 0
    fi
    provider_failure_reason "$rc" "$out" "$err"
    write_unavailable "$prov" "$rc" "$(provider_diagnostic)" "$out"
    rm -f "$err"
    return 0
  fi

  # Only stdout can supply a final review. Stderr may contain prompt echoes or
  # progress messages, even when they look like a complete structured review.
  if [[ ! -s "$out" ]]; then
    failure_category="INVALID_OUTPUT"
    write_unavailable "$prov" "0" "INVALID_OUTPUT: empty provider output" "$out"
  elif ! provider_returned_structured_review "$out"; then
    failure_category="INVALID_OUTPUT"
    write_unavailable "$prov" "0" "INVALID_OUTPUT: provider did not return structured review sections" "$out"
  fi
  rm -f "$err"
}

invoke_provider() (
  local prov="$1"
  local final_out="$OUTPUT_DIR/${TODAY}-plan-${ISSUE_NUM}-${prov}.md"
  local rc=0
  local timeout_s="${PLAN_REVIEW_PROVIDER_TIMEOUT_SEC:-600}"
  local preflight_timeout_s="${PLAN_REVIEW_PREFLIGHT_TIMEOUT_SEC:-$timeout_s}"
  local work_dir out err cli_version auth_state failure_category invocation_mode
  umask 077
  work_dir="$(mktemp -d)"
  trap 'rm -rf "$work_dir"' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  out="$work_dir/review"
  err="$work_dir/stderr"
  invocation_mode="path-reference"
  [[ "$prov" == codex ]] && invocation_mode="stdin"
  [[ "$prov" == agy || "$prov" == gemini ]] && invocation_mode="temporary-file"
  if ! provider_preflight "$prov" "$work_dir" "$preflight_timeout_s"; then
    write_unavailable "$prov" "1" "$(provider_diagnostic)" "$out"
    append_invocation_metadata "$out" "$cli_version" "$invocation_mode" "$auth_state" "$failure_category"
    mv "$out" "$final_out"
    return 0
  fi

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
      plugin_dir_override="$work_dir/no-plugins"
      mkdir "$plugin_dir_override"
      timeout -k 5s "${timeout_s}s" \
        env CLAUDE_PLUGIN_DIR="$plugin_dir_override" \
        claude -p "@$PROMPT_FILE — review the plan at $PLAN_FILE. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS." \
        > "$out" 2>"$err" </dev/null || rc=$?
      rmdir "$plugin_dir_override" 2>/dev/null || true
      ;;
    codex)
      # Codex CLI reference: exec PROMPT='-' reads stdin. A finite private file
      # keeps argv independent of plan length and preserves trailing newlines.
      # Source: developers.openai.com/codex/cli/reference/ (2026-10-22), #3462.
      cat "$PROMPT_FILE" > "$work_dir/payload"
      printf '\n\n--- PLAN (%s) ---\n' "$PLAN_FILE" >> "$work_dir/payload"
      cat "$PLAN_FILE" >> "$work_dir/payload"
      # shellcheck source=/dev/null
      source "$SCRIPT_DIR/lib/codex-version-guard.sh"
      # #3294: make the codex leg headless. Run the version guard with CLAUDECODE
      # stripped (subshell scope) so its env-branch (codex-version-guard.sh:37-40)
      # does NOT fire — the version-band check then governs. Then run codex exec
      # with CLAUDECODE removed from the subprocess env (env -u CLAUDECODE) so the
      # upstream openai/codex#19945 stdin-hang does not reproduce. The guard's
      # CLAUDECODE safety-net branch is retained for un-migrated direct callers
      # (see scripts/review/tests/test_codex_version_guard.sh). Keep the timeout
      # with finite file stdin. See #3294 / #2684 / #3462.
      local guard_rc=0
      (unset CLAUDECODE; codex_version_guard_check) >/dev/null || guard_rc=$?
      if [[ "$guard_rc" -eq 3 ]]; then
        failure_category="INCOMPATIBLE"
        write_unavailable "$prov" "3" "INCOMPATIBLE: known Codex version regression" "$out"
        append_invocation_metadata "$out" "$cli_version" "$invocation_mode" "$auth_state" "$failure_category"
        mv "$out" "$final_out"
        return 0
      elif (( guard_rc != 0 )); then
        failure_category="VERSION_CHECK_FAILED"
        write_unavailable "$prov" "$guard_rc" "VERSION_CHECK_FAILED: Codex guard could not establish compatibility" "$out"
        append_invocation_metadata "$out" "$cli_version" "$invocation_mode" "$auth_state" "$failure_category"
        mv "$out" "$final_out"
        return 0
      else
        env -u CLAUDECODE timeout -k 5s "${timeout_s}s" codex exec - > "$out" 2>"$err" < "$work_dir/payload" || rc=$?
      fi
      ;;
    agy|gemini)   # 'gemini' = DEPRECATED alias for the agy lane (#3573)
      # Third review lane = agy (Antigravity, Gemini-backed) headless via the
      # #3207 wrapper. AGY_REVIEW_MODE=1: oversize payloads FAIL the dispatch
      # (exit 3) instead of truncating — a truncated review can false-APPROVE.
      REPO_ROOT="$work_dir" AGY_REVIEW_MODE=1 AGY_TIMEOUT_SECONDS="$timeout_s" \
        timeout -k 5s "$((timeout_s + 30))s" \
        bash "$SCRIPT_DIR/submit-to-agy.sh" --file "$PLAN_FILE" \
        --prompt "$(cat "$PROMPT_FILE")" > "$out" 2>"$err" </dev/null || rc=$?
      ;;
    *)
      echo "unknown provider: $prov" >&2
      return 2
      ;;
  esac

  normalize_provider_output "$prov" "$rc" "$out" "$err"
  append_invocation_metadata "$out" "$cli_version" "$invocation_mode" "$auth_state" "$failure_category"
  mv "$out" "$final_out"
)

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
if [[ -f "$SCRIPT_DIR/lib/disagreement-diff.sh" ]]; then  # -f not -x: exec bits are lost on NTFS-FUSE working copies; invoked via bash below
  bash "$SCRIPT_DIR/lib/disagreement-diff.sh" "$OUTPUT_DIR" "$TODAY" "$ISSUE_NUM" > "$DISAGREEMENT_FILE"
fi

echo "wrote artifacts to $OUTPUT_DIR for plan #${ISSUE_NUM} ($TODAY)"
