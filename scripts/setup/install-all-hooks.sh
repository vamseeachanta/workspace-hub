#!/usr/bin/env bash
# Install standard Git event wrappers at Git's effective hook path (#3852).
# Protocol: https://git-scm.com/docs/githooks (DESCRIPTION, pre-push),
# accessed 2026-10-22. Helper filenames are not Git events.
# Usage: bash scripts/setup/install-all-hooks.sh [--quiet] [--dry-run|--check]
# Existing foreign hooks are preserved; composition requires maintainer review.
set -euo pipefail

QUIET=0
MODE=install
for arg in "$@"; do
  case "$arg" in
    --quiet) QUIET=1 ;;
    --dry-run|--check)
      [[ "$MODE" == install ]] || { echo "Choose one mode" >&2; exit 2; }
      MODE="${arg#--}" ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(git rev-parse --show-toplevel)" || exit 2
cd "$REPO_ROOT"
# Let Git resolve core.hooksPath and shared worktree metadata, including spaces.
HOOKS_DST="$(git rev-parse --path-format=absolute --git-path hooks)"
SOURCE="scripts/hooks/pre-push.sh"
TARGET="${HOOKS_DST}/pre-push"

# Resolve the source at invocation time, so a shared hook uses the invoking
# worktree's code. exec preserves arguments, ref-line stdin and exit status.
wrapper() {
  cat <<'HOOK'
#!/usr/bin/env bash
# Managed by scripts/setup/install-all-hooks.sh; Git pre-push protocol only.
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
exec bash "${REPO_ROOT}/scripts/hooks/pre-push.sh" "$@"
HOOK
}

[[ -f "$SOURCE" ]] || { echo "Missing source: $SOURCE" >&2; exit 1; }
if [[ -e "$TARGET" || -L "$TARGET" ]]; then
  if [[ -L "$TARGET" || ! -f "$TARGET" ]] || ! cmp -s <(wrapper) "$TARGET"; then
    echo "Existing pre-push preserved; review composition before installation" >&2
    exit 1
  fi
  if [[ -x "$TARGET" ]]; then
    [[ "$QUIET" == 1 ]] || echo "pre-push: current at effective hook path"
    exit 0
  fi
elif [[ "$MODE" == check ]]; then
  echo "pre-push: missing at effective hook path" >&2
  exit 1
fi

case "$MODE" in
  check) echo "pre-push: not executable" >&2; exit 1 ;;
  dry-run) [[ "$QUIET" == 1 ]] || echo "Would install executable pre-push at effective hook path" ;;
  install)
    mkdir -p "$HOOKS_DST"
    wrapper > "$TARGET"
    chmod +x "$TARGET"
    [[ "$QUIET" == 1 ]] || echo "Installed pre-push at effective hook path"
    ;;
esac
