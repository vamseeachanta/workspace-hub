#!/usr/bin/env bash
# Shared Codex CLI version guard for #2479.
# Source this file and call codex_version_guard_check.

CODEX_KNOWN_BAD_FLOOR="${CODEX_KNOWN_BAD_FLOOR:-0.124.0}"
# 0.130.0 validated 2026-05-11 (#2661): codex exec works in both arg-form
# (58s real-time) and stdin-form (faster); upstream openai/codex#19945 stdin-hang
# regression no longer reproduces. Intermediate versions 0.124.0..0.129.x remain
# in the known-bad band — lower the ceiling only after each is individually
# verified. Probe transcripts: workspace-hub #2661.
CODEX_VERSION_GUARD_CEILING_DEFAULT="${CODEX_VERSION_GUARD_CEILING_DEFAULT:-0.130.0}"
CODEX_PIN_VERSION_DEFAULT="${CODEX_PIN_VERSION_DEFAULT:-0.123.0}"

_codex_ge() {
  [[ "$1" == "$2" ]] && return 0
  [[ "$(printf '%s\n' "$1" "$2" | sort -V | tail -n1)" == "$1" ]]
}

_codex_lt() {
  [[ "$1" == "$2" ]] && return 1
  [[ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" == "$1" ]]
}

codex_version_guard_check() {
  local bin="${CODEX_BIN:-codex}"
  if ! command -v "$bin" >/dev/null 2>&1 && [[ ! -x "$bin" ]]; then
    echo "codex CLI not on PATH"
    return 2
  fi

  # Environment guard (#2684): codex exec hangs from Claude-Code Bash regardless
  # of codex version. The Claude-Code Bash tool provides a non-closeable stdin
  # layer that does not propagate EOF to the codex subprocess (upstream
  # openai/codex#19945). Detect via CLAUDECODE=1 (set by Claude Code in every
  # Bash subprocess) and fail fast with a clear reason so the operator knows
  # how to recover (run from a plain terminal, or unset CLAUDECODE).
  if [[ "${CLAUDECODE:-}" == "1" ]]; then
    echo "INCOMPATIBLE (running under Claude-Code Bash — codex exec stdin-hangs regardless of version; upstream openai/codex#19945; see workspace-hub #2684; dispatch from a plain terminal OR unset the env var via 'env -u CLAUDECODE bash scripts/review/plan-review-fanout.sh ...' for Codex review)"
    return 3
  fi

  local raw ver base prerelease floor ceiling
  if ! raw="$(timeout 5 "$bin" --version 2>/dev/null)"; then
    echo "codex --version failed or timed out"
    return 2
  fi
  ver="$(printf '%s' "$raw" | awk '{print $NF}')"
  if [[ ! "$ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.]+)?$ ]]; then
    echo "codex --version unparseable: $raw"
    return 2
  fi

  base="${ver%%-*}"
  prerelease=""
  [[ "$ver" != "$base" ]] && prerelease="${ver#${base}-}"
  floor="${CODEX_KNOWN_BAD_FLOOR}"
  ceiling="${CODEX_VERSION_GUARD_CEILING:-${CODEX_VERSION_GUARD_CEILING_DEFAULT}}"

  if [[ -n "$prerelease" ]] && _codex_ge "$base" "$floor"; then
    echo "INCOMPATIBLE ($ver — pre-release ($prerelease) at-or-above floor $floor; no alpha is whitelisted; see #2479)"
    return 3
  fi

  if ! _codex_ge "$base" "$floor"; then
    echo "OK ($ver < $floor — pre-regression)"
    return 0
  fi

  if [[ -n "$ceiling" ]] && ! _codex_lt "$base" "$ceiling"; then
    echo "OK ($ver >= $ceiling — past whitelisted regression band)"
    return 0
  fi

  if [[ -n "$ceiling" ]]; then
    echo "INCOMPATIBLE ($ver in known-bad range [$floor, $ceiling) — upstream openai/codex#19945; see workspace-hub #2479)"
  else
    echo "INCOMPATIBLE ($ver in known-bad range [>= $floor) — upstream openai/codex#19945; see workspace-hub #2479; run scripts/install/pin-codex.sh to downgrade)"
  fi
  return 3
}
