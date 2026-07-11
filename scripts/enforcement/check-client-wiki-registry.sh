#!/usr/bin/env bash
# Audit the private client-wiki registry without reading raw-source contents.

set -euo pipefail

while IFS='=' read -r name _; do
  [[ "$name" == GIT_* ]] && unset "$name"
done < <(env)
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL=/dev/null

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SELF_DIR/../.." && pwd -P)"
REGISTRY="${REGISTRY_PATH:-${WIKI_SIBLING_REGISTRY_PATH:-}}"
YQ_BIN="${YQ_BIN:-yq}"
UV_BIN="${UV_BIN:-uv}"
GH_BIN="${GH_BIN:-gh}"

if [[ -z "$REGISTRY" ]]; then
  if [[ -f "${REPO_ROOT}/config/.client-wikis.local.yml" ]]; then
    REGISTRY="${REPO_ROOT}/config/.client-wikis.local.yml"
  else
    REGISTRY="${REPO_ROOT}/config/client-wikis.yml"
  fi
fi

if [[ ! -f "$REGISTRY" ]]; then
  echo >&2 "WARN: registry not found at $REGISTRY — skipping (private authority not provisioned)"
  exit 0
fi

REGISTRY_SOURCE="$REGISTRY"
REGISTRY_SNAPSHOT="$(mktemp)"
trap 'rm -f "$REGISTRY_SNAPSHOT"' EXIT
if ! cp -- "$REGISTRY_SOURCE" "$REGISTRY_SNAPSHOT"; then
  echo >&2 "FAIL: registry snapshot could not be created"
  exit 1
fi
chmod 600 "$REGISTRY_SNAPSHOT"
REGISTRY="$REGISTRY_SNAPSHOT"

resolve_tool() {
  local requested="$1" resolved
  if [[ "$requested" == */* ]]; then
    [[ -x "$requested" ]] || return 1
    printf '%s\n' "$requested"
    return 0
  fi
  resolved="$(command -v "$requested" 2>/dev/null || true)"
  [[ -n "$resolved" ]] || return 1
  printf '%s\n' "$resolved"
}

YQ_PATH="$(resolve_tool "$YQ_BIN" || true)"
if [[ -z "$YQ_PATH" ]]; then
  echo >&2 "FAIL: yq v4+ is required"
  exit 2
fi
YQ_VERSION="$($YQ_PATH --version 2>/dev/null || true)"
if [[ ! "$YQ_VERSION" =~ version[[:space:]]+v?4\. ]]; then
  echo >&2 "FAIL: yq major version 4 is required"
  exit 2
fi

yq_value() {
  "$YQ_PATH" -r "$1" "$REGISTRY"
}

if ! VERSION_TAG="$(yq_value '.registry_version | tag')" \
  || ! VERSION="$(yq_value '.registry_version')" \
  || ! RELOCATED_TAG="$(yq_value '.relocated | tag')" \
  || ! RELOCATED="$(yq_value '.relocated // false')" \
  || ! WIKIS_TAG="$(yq_value '.wikis | tag')" \
  || ! WIKIS_LEN="$(yq_value '.wikis | length')" \
  || ! TOP_KEYS="$($YQ_PATH -o=json -I=0 'keys | sort' "$REGISTRY")"; then
  echo >&2 "FAIL: registry is malformed YAML"
  exit 1
fi

EXACT_STUB=0
if [[ "$VERSION_TAG" == "!!str" && "$VERSION" == "0.2" \
  && "$RELOCATED_TAG" == "!!bool" && "$RELOCATED" == "true" \
  && "$WIKIS_TAG" == "!!seq" && "$WIKIS_LEN" == "0" \
  && "$TOP_KEYS" == '["registry_version","relocated","wikis"]' ]]; then
  EXACT_STUB=1
fi
if [[ $EXACT_STUB -eq 1 ]]; then
  echo "INFO: registry at $REGISTRY_SOURCE is the exact relocated public stub — skipping validation."
  exit 0
fi
if [[ "$RELOCATED" == "true" || "$WIKIS_TAG" != "!!seq" || "$WIKIS_LEN" == "0" ]]; then
  echo >&2 "FAIL: malformed public stub or empty authoritative registry"
  exit 1
fi

UV_PATH="$(resolve_tool "$UV_BIN" || true)"
if [[ -z "$UV_PATH" ]]; then
  echo >&2 "FAIL: uv is required for non-empty registry validation"
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}/scripts${PYTHONPATH:+:${PYTHONPATH}}"
if ! "$UV_PATH" run --directory "$REPO_ROOT" --frozen python -c \
  'import client_llm_wiki.bootstrap_contract' >/dev/null 2>&1; then
  echo >&2 "FAIL: locked Python bootstrap contract environment is unavailable"
  exit 2
fi

set +e
VALIDATION_OUTPUT="$($UV_PATH run --directory "$REPO_ROOT" --frozen python -m \
  client_llm_wiki.bootstrap_contract validate-registry --registry "$REGISTRY" 2>&1)"
VALIDATION_RC=$?
set -e
if [[ -n "$VALIDATION_OUTPUT" ]]; then
  printf '%s\n' "$VALIDATION_OUTPUT" >&2
fi
if [[ $VALIDATION_RC -eq 1 ]]; then
  exit 1
elif [[ $VALIDATION_RC -ne 0 ]]; then
  echo >&2 "FAIL: bootstrap contract dependency error (exit $VALIDATION_RC)"
  exit 2
fi

FAILED=0
GH_PATH=""
PUBLIC_WIKI_PATTERN='/llm-wiki(/|$)'

check_live_repo() {
  local short="$1" repo="$2" status="$3" json identity visibility archived archived_tag
  if [[ "$status" != "bootstrapped" && "$status" != "live" ]]; then
    return 0
  fi
  if [[ -z "$GH_PATH" ]]; then
    GH_PATH="$(resolve_tool "$GH_BIN" || true)"
  fi
  if [[ -z "$GH_PATH" ]]; then
    echo >&2 "FAIL: gh is required for bootstrapped/live registry rows"
    return 2
  fi
  if ! json="$($GH_PATH repo view "github.com/$repo" --json nameWithOwner,visibility,isArchived 2>/dev/null)"; then
    echo >&2 "FAIL: $short repo $repo not found on GH"
    return 1
  fi
  if ! identity="$(printf '%s' "$json" | "$YQ_PATH" -r '.nameWithOwner' - 2>/dev/null)" \
    || ! visibility="$(printf '%s' "$json" | "$YQ_PATH" -r '.visibility' - 2>/dev/null)" \
    || ! archived="$(printf '%s' "$json" | "$YQ_PATH" -r '.isArchived' - 2>/dev/null)" \
    || ! archived_tag="$(printf '%s' "$json" | "$YQ_PATH" -r '.isArchived | tag' - 2>/dev/null)"; then
    echo >&2 "FAIL: yq could not parse the live repository response"
    return 2
  fi
  if [[ "$identity" != "$repo" ]]; then
    echo >&2 "FAIL: $short live repository identity does not match the registry"
    return 1
  elif [[ "$visibility" != "PRIVATE" ]]; then
    echo >&2 "FAIL: $short posture=client-private but visibility=$visibility"
    return 1
  fi
  if [[ "$archived_tag" != "!!bool" || "$archived" != "false" ]]; then
    echo >&2 "FAIL: $short status=$status but repo is archived or malformed"
    return 1
  fi
  return 0
}

check_clone() {
  local short="$1" repo="$2" clone="$3" parent output rc
  [[ -n "$clone" && "$clone" != "null" ]] || return 0
  parent="$(dirname "$clone")"
  if [[ ! -d "$parent" ]]; then
    echo >&2 "WARN: $short clone parent unavailable on this host — skipping availability"
    return 0
  fi
  if [[ ! -d "$clone/.git" || -L "$clone" || -L "$clone/.git" ]]; then
    echo >&2 "FAIL: $short clone $clone missing or not a real Git working tree"
    return 1
  fi
  set +e
  output="$($UV_PATH run --directory "$REPO_ROOT" --frozen python -c '
from pathlib import Path
import sys
from client_llm_wiki.bootstrap_git import BootstrapGitError, validate_clone_config
from client_llm_wiki.bootstrap_layout import bind_clone
try:
    with bind_clone(Path(sys.argv[1])) as bound:
        validate_clone_config(bound, sys.argv[2])
except (BootstrapGitError, OSError) as exc:
    print(f"FAIL: clone config/origin semantics are invalid: {exc}", file=sys.stderr)
    raise SystemExit(1)
' "$clone" "$repo" 2>&1)"
  rc=$?
  set -e
  [[ -z "$output" ]] || printf '%s\n' "$output" >&2
  if [[ $rc -eq 0 ]]; then
    return 0
  elif [[ $rc -eq 1 ]]; then
    return 1
  fi
  echo >&2 "FAIL: bootstrap contract dependency error (exit $rc)"
  return 2
}

check_raw_root() {
  local short="$1" root="$2" parent
  if [[ "$root" =~ $PUBLIC_WIKI_PATTERN ]]; then
    echo >&2 "FAIL: $short raw_roots overlaps public llm-wiki (firewall violation)"
    return 1
  fi
  parent="$(dirname "$root")"
  if [[ ! -d "$parent" ]]; then
    echo >&2 "WARN: $short raw-root parent unavailable on this host — skipping availability"
    return 0
  fi
  if [[ ! -d "$root" || -L "$root" ]]; then
    echo >&2 "FAIL: $short raw root must be an existing non-symlink directory"
    return 1
  fi
  return 0
}

if ! INDICES="$(yq_value '.wikis | keys | .[]')"; then
  echo >&2 "FAIL: yq failed while reading validated registry entries"
  exit 2
fi
while IFS= read -r index; do
  [[ -n "$index" ]] || continue
  if ! SHORT="$(yq_value ".wikis[$index].short_name // \"\"")" \
    || ! REPO="$(yq_value ".wikis[$index].repo // \"\"")" \
    || ! POSTURE="$(yq_value ".wikis[$index].posture // \"\"")" \
    || ! STATUS="$(yq_value ".wikis[$index].status // \"\"")" \
    || ! CLONE="$(yq_value ".wikis[$index].local_working_clone // \"\"")"; then
    echo >&2 "FAIL: yq failed while reading validated registry fields"
    exit 2
  fi
  if [[ -z "$SHORT" || -z "$REPO" || "$POSTURE" != "client-private" || -z "$STATUS" ]]; then
    echo >&2 "FAIL: entry index=$index missing required identity/posture/status"
    FAILED=1
    continue
  fi
  set +e
  check_live_repo "$SHORT" "$REPO" "$STATUS"
  LIVE_RC=$?
  set -e
  if [[ $LIVE_RC -eq 2 ]]; then
    exit 2
  elif [[ $LIVE_RC -ne 0 ]]; then
    FAILED=1
  fi
  set +e
  check_clone "$SHORT" "$REPO" "$CLONE"
  CLONE_RC=$?
  set -e
  if [[ $CLONE_RC -eq 2 ]]; then
    exit 2
  elif [[ $CLONE_RC -ne 0 ]]; then
    FAILED=1
  fi
  if ! ROOTS="$(yq_value ".wikis[$index].raw_roots[]")"; then
    echo >&2 "FAIL: yq failed while reading validated raw roots"
    exit 2
  fi
  while IFS= read -r root; do
    [[ -n "$root" ]] || continue
    if ! check_raw_root "$SHORT" "$root"; then
      FAILED=1
    fi
  done <<< "$ROOTS"
done <<< "$INDICES"

exit "$FAILED"
