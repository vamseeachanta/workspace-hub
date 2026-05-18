#!/usr/bin/env bash
set -euo pipefail

SERVICE="${HERMES_GATEWAY_SERVICE:-hermes-gateway.service}"
ENV_FILE="${HERMES_GATEWAY_ENV_FILE:-$HOME/.hermes/.env}"
MIN_TIMEOUT_SEC="${HERMES_GATEWAY_MIN_TIMEOUT_SEC:-210}"
LOG_SINCE="${HERMES_GATEWAY_LOG_SINCE:-30 minutes ago}"
BOT_TOKEN_ENV_KEY="${HERMES_GATEWAY_BOT_TOKEN_ENV_KEY:-TELEGRAM_BOT_TOKEN}"
ALLOWED_USERS_ENV_KEY="${HERMES_GATEWAY_ALLOWED_USERS_ENV_KEY:-TELEGRAM_ALLOWED_USERS}"
FAIL=0
PASS=0

pass() {
  PASS=$((PASS + 1))
  printf 'PASS: %s\n' "$1"
}

fail() {
  FAIL=$((FAIL + 1))
  printf 'FAIL: %s\n' "$1"
}

systemctl_show_value() {
  local property="$1"
  local output=""
  if output="$(systemctl show "$SERVICE" -p "$property" 2>/dev/null)"; then
    printf '%s\n' "$output" | sed -n "s/^${property}=//p" | head -n 1
    return 0
  fi
  return 1
}

require_env_key_present() {
  local key="$1"
  if awk -F= -v key="$key" '{ k = $1; gsub(/^[[:space:]]+|[[:space:]]+$/, "", k); if (k == key) found = 1 } END { exit !found }' "$ENV_FILE"; then
    printf '%s=present\n' "$key"
    pass "$key present in env file"
  else
    fail "$key missing from env file"
  fi
}

normalized_env_value() {
  local key="$1"
  local line=""
  line="$(awk -F= -v key="$key" '{ k = $1; gsub(/^[[:space:]]+|[[:space:]]+$/, "", k); if (k == key) { value = substr($0, index($0, "=") + 1) } } END { if (value != "") print value }' "$ENV_FILE")"
  printf '%s' "$line" \
    | tr -d '[:space:]' \
    | sed -e "s/^['\"]//" -e "s/['\"]$//" \
    | tr '[:upper:]' '[:lower:]'
}

check_allow_all_users() {
  if ! awk -F= '{ k = $1; gsub(/^[[:space:]]+|[[:space:]]+$/, "", k); if (k == "GATEWAY_ALLOW_ALL_USERS") found = 1 } END { exit !found }' "$ENV_FILE"; then
    pass "GATEWAY_ALLOW_ALL_USERS is absent/fail-closed"
    return
  fi

  local value=""
  value="$(normalized_env_value GATEWAY_ALLOW_ALL_USERS)"
  case "$value" in
    false|0|no|off|disabled)
      pass "GATEWAY_ALLOW_ALL_USERS is fail-closed"
      ;;
    *)
      fail "GATEWAY_ALLOW_ALL_USERS must be absent or explicitly false"
      ;;
  esac
}

check_required_environment_file() {
  local configured_env_files="$1"
  if printf '%s\n' "$configured_env_files" | grep -Fqx "$ENV_FILE" \
    || printf '%s\n' "$configured_env_files" | grep -Fq "$ENV_FILE (ignore_errors=no)"; then
    pass "systemd loads required env file"
  elif printf '%s\n' "$configured_env_files" | grep -Fq -- "-$ENV_FILE" \
    || printf '%s\n' "$configured_env_files" | grep -Fq "$ENV_FILE (ignore_errors=yes)"; then
    fail "EnvironmentFile must be fail-closed, not optional"
  else
    fail "systemd EnvironmentFiles does not include env file"
  fi
}

systemd_duration_to_seconds() {
  local raw="$1"
  local total=0
  local matched=0
  if [[ "$raw" =~ ^[0-9]+$ ]]; then
    printf '%s\n' "$((raw / 1000000))"
    return 0
  fi

  while [[ "$raw" =~ ([0-9]+)[[:space:]]*(h|hr|hrs|hour|hours|min|mins|minute|minutes|s|sec|secs|second|seconds|ms|msec|msecs|millisecond|milliseconds|us|usec|usecs|microsecond|microseconds) ]]; do
    value="${BASH_REMATCH[1]}"
    unit="${BASH_REMATCH[2]}"
    matched=1
    case "$unit" in
      h|hr|hrs|hour|hours) total=$((total + value * 3600)) ;;
      min|mins|minute|minutes) total=$((total + value * 60)) ;;
      s|sec|secs|second|seconds) total=$((total + value)) ;;
      ms|msec|msecs|millisecond|milliseconds) total=$((total + value / 1000)) ;;
      us|usec|usecs|microsecond|microseconds) total=$((total + value / 1000000)) ;;
    esac
    raw="${raw#*"${BASH_REMATCH[0]}"}"
  done

  if [ "$matched" = "1" ]; then
    printf '%s\n' "$total"
    return 0
  fi
  return 1
}

printf 'Hermes gateway coordinator verifier\n'
printf 'service=%s\n' "$SERVICE"
printf 'env_file=%s\n' "$ENV_FILE"

if [ -f "$ENV_FILE" ]; then
  pass "env file exists"

  mode="$(stat -c '%a' "$ENV_FILE" 2>/dev/null || true)"
  owner="$(stat -c '%U:%G' "$ENV_FILE" 2>/dev/null || true)"
  if [ "$mode" = "600" ]; then
    pass "env file mode is 600"
  else
    fail "env file mode must be 600"
  fi
  if [ -n "$owner" ]; then
    pass "env file owner resolved"
  else
    fail "env file owner unavailable"
  fi
else
  fail "env file missing"
fi

if [ -f "$ENV_FILE" ]; then
  require_env_key_present "$BOT_TOKEN_ENV_KEY"
  require_env_key_present "$ALLOWED_USERS_ENV_KEY"

  check_allow_all_users
fi

if systemctl is-active "$SERVICE" >/dev/null 2>&1; then
  pass "gateway service active"
else
  fail "gateway service is not active"
fi

configured_env_files="$(systemctl_show_value EnvironmentFiles || true)"
if [ -n "$configured_env_files" ]; then
  check_required_environment_file "$configured_env_files"
else
  fail "systemd EnvironmentFiles does not include env file"
fi

timeout_usec="$(systemctl_show_value TimeoutStopUSec || true)"
timeout_sec=""
if timeout_sec="$(systemd_duration_to_seconds "$timeout_usec")"; then
  if [ "$timeout_sec" -ge "$MIN_TIMEOUT_SEC" ]; then
    pass "TimeoutStopSec >= ${MIN_TIMEOUT_SEC}s"
  else
    fail "TimeoutStopSec must be >=${MIN_TIMEOUT_SEC}s"
  fi
else
  fail "TimeoutStopUSec unavailable"
fi

pid_count="$(pgrep -af 'hermes_cli\.main gateway run|hermes .*gateway run|gateway run --replace' 2>/dev/null | wc -l | tr -d ' ')"
if [ "$pid_count" = "1" ]; then
  pass "exactly one active gateway/polling PID"
else
  fail "exactly one active gateway/polling PID required"
fi

recent_logs="$(journalctl -u "$SERVICE" --since "$LOG_SINCE" -n 200 --no-pager 2>/dev/null || true)"
if printf '%s\n' "$recent_logs" | grep -qiE 'terminated by other getUpdates request|only one bot instance|getUpdates conflict'; then
  fail "duplicate Telegram polling/getUpdates conflict"
else
  pass "no duplicate Telegram polling conflict in recent logs"
fi

printf 'summary: %s passed, %s failed\n' "$PASS" "$FAIL"
exit "$FAIL"
