#!/usr/bin/env bash
# Bounded, non-interactive diagnostics for plan-review-fanout.sh.
# Sources: Codex CLI reference, `exec` and `login status`;
# Claude Code CLI reference, `auth status` (JSON), retrieved 2026-10-22.
# Raw probe output stays in the caller's private temporary directory.

provider_preflight() {
  local prov="$1" work="$2" timeout_s="$3"
  local bin="$prov" probe_rc=0 raw_version
  [[ "$prov" == gemini ]] && bin="${AGY_CMD:-agy}"
  [[ "$prov" == agy ]] && bin="${AGY_CMD:-agy}"
  cli_version="NOT_REPORTED"
  auth_state="NOT_EVALUATED"
  failure_category=""
  failure_reason=""
  if ! command -v "$bin" >/dev/null 2>&1; then
    failure_category="CLI_MISSING"
    failure_reason="provider executable is unavailable"
    return 1
  fi
  env -u CLAUDECODE timeout -k 5s "${timeout_s}s" "$bin" --version > "$work/version" 2>/dev/null </dev/null || probe_rc=$?
  # Retain the exact version line only in a recognized version format. Arbitrary
  # version output could contain paths, credentials or terminal control bytes.
  raw_version="$(cat "$work/version")"
  if (( probe_rc == 0 )) && [[ "$raw_version" =~ ^(codex-cli\ |agy\ |gemini\ )?[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.]+)?(\ \(Claude\ Code\))?$ ]]; then
    cli_version="$raw_version"
  else
    failure_category="VERSION_CHECK_FAILED"
    failure_reason="provider version probe failed or returned an unrecognized version"
    return 1
  fi

  probe_rc=0
  case "$prov" in
    claude)
      timeout -k 5s "${timeout_s}s" claude auth status > "$work/auth" 2>/dev/null </dev/null || probe_rc=$?
      auth_state="$(python3 -c '
import json, sys
try:
    value = json.load(sys.stdin).get("loggedIn")
    print("AUTHENTICATED" if value is True else "AUTH_REQUIRED" if value is False else "UNKNOWN")
except (ValueError, AttributeError):
    print("UNKNOWN")
' < "$work/auth")"
      if [[ "$auth_state" == AUTH_REQUIRED && "$probe_rc" -eq 1 ]]; then
        failure_category="AUTH_REQUIRED"
        failure_reason="authentication required; run claude auth login"
        return 1
      fi
      ;;
    codex)
      env -u CLAUDECODE timeout -k 5s "${timeout_s}s" codex login status > "$work/auth" 2>&1 </dev/null || probe_rc=$?
      if (( probe_rc == 0 )) && grep -q '^Logged in' "$work/auth"; then
        auth_state="AUTHENTICATED"
      elif (( probe_rc == 1 )) && grep -qi '^Not logged in' "$work/auth"; then
        auth_state="AUTH_REQUIRED"
        failure_category="AUTH_REQUIRED"
        failure_reason="authentication required; run codex login"
        return 1
      else
        auth_state="UNKNOWN"
      fi
      ;;
    agy|gemini)
      # The existing adapter has no documented non-interactive auth-status API.
      # Do not guess a credential-file layout or interpret key presence as auth.
      # Its bounded headless invocation remains the only available observation.
      return 0
      ;;
  esac
  if (( probe_rc != 0 )) || [[ "$auth_state" != AUTHENTICATED ]]; then
    auth_state="UNKNOWN"
    failure_category="AUTH_CHECK_FAILED"
    failure_reason="authentication status could not be established; check provider auth status"
    return 1
  fi
}

provider_failure_reason() {
  local rc="$1" out="$2" err="$3"
  failure_category="RUNTIME_FAILURE"
  failure_reason="provider exited unsuccessfully; raw diagnostics withheld"
  # GNU timeout documents 124 as timeout, 137 when KILL is required. These
  # codes are also used by the existing provider timeout contract (#3294).
  if (( rc == 124 || rc == 137 )); then
    failure_category="TIMEOUT"
    failure_reason="provider exceeded its configured timeout"
  elif grep -Eqi 'not logged in|authentication required|please log in|claude auth login|codex login|unauthenticated' "$out" "$err"; then
    auth_state="AUTH_REQUIRED"
    failure_category="AUTH_REQUIRED"
    failure_reason="provider requires authentication; use the provider login command"
  fi
}

provider_diagnostic() {
  printf '%s: %s' "$failure_category" "$failure_reason"
}

append_invocation_metadata() {
  local out="$1" version="${2:-$cli_version}" mode="$3" auth="$4" diagnostic="$5"
  {
    printf '\n## Invocation\n'
    printf 'CLI version: %s\n' "$version"
    printf 'Delivery mode: %s\n' "$mode"
    printf 'Authentication: %s\n' "$auth"
    printf 'Diagnostic: %s\n' "${diagnostic:-NONE}"
  } >> "$out"
}
