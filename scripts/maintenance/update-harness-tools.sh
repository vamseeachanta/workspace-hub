#!/usr/bin/env bash
#
# update-harness.sh — Update the key harness CLI programs.
#
#   hermes  -> hermes update
#   claude  -> claude update
#   codex   -> codex update
#   gemini  -> npm install -g @google/gemini-cli@latest
#
# Each step is independent: a failure is reported but does not abort the rest.
# Run with --dry-run to print the commands without executing them.
#
# Post-hermes-update re-apply (deckhand#63):
#   `hermes update` discards working-tree changes on its managed clone before
#   updating ("Discarding working-tree changes on managed clone before
#   update..."), which silently wipes any locally-applied Hermes enforcement
#   patches from ~/.hermes/hermes-agent. On any host where the deckhand
#   installer is present we re-apply those patches immediately after a
#   successful `hermes update`, and FAIL LOUDLY (non-zero exit) if they cannot
#   be re-applied so the cron log surfaces the breakage instead of silently
#   running the gateway without local enforcement.

set -uo pipefail

# Path to the deckhand Hermes-patch installer (idempotent: dry-run checks patch
# drift with `git apply --check`; `--apply` re-applies and exits non-zero on
# failure). Override via env for non-standard checkouts. The guard below skips
# this step entirely on hosts where the installer is absent (multi-machine).
# The absolute default is a cross-repo machine path (deckhand lives outside this
# repo, so $(git rev-parse) can't resolve it); it is env-overridable and the
# step is guarded by an [ -x ] existence check, hence the exemption sentinel.
DECKHAND_HERMES_INSTALLER="${DECKHAND_HERMES_INSTALLER:-/mnt/local-analysis/deckhand/scripts/deckhand/install-hermes-b2.sh}"  # abs-path-allowed
# deckhand#162 — gateway-host patch-health guard (stdlib-only; alerts owner if
# the live gateway is unpatched). Run right after re-apply so a re-apply that
# FAILED (e.g. a patch needs re-fitting for a new hermes) pages within seconds,
# instead of only the loud-but-unwatched log + the hourly guard cron. The
# 2026-06-08 incident ran unpatched for hours because that failure was silent.
DECKHAND_HEALTH_CHECK="${DECKHAND_HEALTH_CHECK:-/mnt/local-analysis/deckhand/scripts/deckhand/patch-health-check.py}"  # abs-path-allowed

# Ensure tool dirs are on PATH. Cron and Windows Task Scheduler launch this with a
# minimal environment, so the npm-global / ~/.local/bin dirs where the CLIs live
# are not on PATH by default. Mirrors scripts/cron/harness-update-windows.sh.
if [[ -n "${APPDATA:-}" ]] && command -v cygpath >/dev/null 2>&1; then
  PATH="$(cygpath "$APPDATA")/npm:${PATH}"   # Windows npm-global (Git Bash / MINGW64)
fi
export PATH="${HOME}/.local/bin:${HOME}/.npm-global/bin:${PATH}"

DRY_RUN=0
[[ "${1:-}" == "--dry-run" || "${1:-}" == "-n" ]] && DRY_RUN=1

# Track results for the summary.
declare -a NAMES=()
declare -a STATUS=()

# Set to 1 if the deckhand patch re-apply step fails — forces a non-zero exit
# even though it is not a `run_step`/STATUS entry (deckhand#63).
REAPPLY_FAILED=0

run_step() {
  local name="$1"; shift
  echo
  echo "==> ${name}: $*"
  NAMES+=("$name")

  if ! command -v "$1" >/dev/null 2>&1; then
    echo "    SKIP: '$1' not found on PATH"
    STATUS+=("skipped (missing)")
    return
  fi

  if (( DRY_RUN )); then
    echo "    (dry-run, not executed)"
    STATUS+=("dry-run")
    return
  fi

  if "$@"; then
    STATUS+=("ok")
  else
    echo "    FAILED (exit $?)"
    STATUS+=("FAILED")
  fi
}

# Return the recorded STATUS of a prior run_step by name (empty if not run).
status_of() {
  local want="$1" i
  for i in "${!NAMES[@]}"; do
    [[ "${NAMES[$i]}" == "$want" ]] && { printf '%s\n' "${STATUS[$i]}"; return; }
  done
}

# Re-apply the deckhand Hermes enforcement patches after `hermes update`.
# `hermes update` discards working-tree changes on the managed clone, wiping the
# locally-applied patches (deckhand#63). The installer is idempotent: with
# --apply it drift-checks each patch (`git apply --check`) then applies it,
# exiting non-zero on any failure. We fail loudly on failure so the cron log and
# the script exit code surface a gateway that would otherwise restart without
# local enforcement. (verify-hermes-b2.sh is NOT wired in here: it needs a test
# session identity + PYTHONPATH + the deckhand python module and asserts ambient
# GH_TOKEN is unset — assumptions that do not hold in the bare cron env. The
# installer's own dry-run drift check below is the cron-appropriate verification.)
reapply_hermes_patches() {
  echo
  echo "==> hermes-patches: re-apply deckhand enforcement patches"
  NAMES+=("hermes-patches")

  if [[ ! -x "$DECKHAND_HERMES_INSTALLER" ]]; then
    echo "    SKIP: installer not present/executable ($DECKHAND_HERMES_INSTALLER)"
    STATUS+=("skipped (no installer)")
    return
  fi

  local hermes_status
  hermes_status="$(status_of hermes)"
  if [[ "$hermes_status" != "ok" ]]; then
    # Only a successful `hermes update` rewrites the managed clone and wipes the
    # patches. If hermes was skipped/failed/dry-run, the tree is untouched, so a
    # re-apply is unnecessary — but it is cheap and idempotent, so still run it
    # to self-heal any pre-existing drift. In dry-run, only report intent.
    if (( DRY_RUN )); then
      echo "    (dry-run, would run: $DECKHAND_HERMES_INSTALLER --apply)"
      STATUS+=("dry-run")
      return
    fi
    echo "    NOTE: hermes step was '${hermes_status:-not-run}'; running re-apply anyway (idempotent)"
  fi

  if (( DRY_RUN )); then
    echo "    (dry-run, would run: $DECKHAND_HERMES_INSTALLER --apply)"
    STATUS+=("dry-run")
    return
  fi

  if "$DECKHAND_HERMES_INSTALLER" --apply; then
    STATUS+=("ok")
    # Post-apply drift verification: re-run the installer in dry-run mode. It
    # exits non-zero if any patch no longer applies cleanly (i.e. did not land).
    if ! "$DECKHAND_HERMES_INSTALLER" >/dev/null 2>&1; then
      echo "    ERROR: post-apply drift check failed — patches did not land cleanly"
      REAPPLY_FAILED=1
      STATUS[-1]="FAILED (drift)"
    fi
  else
    echo "    ERROR: HERMES LOCAL PATCHES FAILED TO RE-APPLY — gateway restart will lose local enforcement patches"
    REAPPLY_FAILED=1
    STATUS+=("FAILED")
  fi
}

echo "Harness update — $(date '+%Y-%m-%d %H:%M:%S')"
(( DRY_RUN )) && echo "(dry-run mode)"

run_step hermes hermes update
reapply_hermes_patches   # deckhand#63 — re-apply patches wiped by `hermes update`
# deckhand#162 — immediately verify patches landed; alert owner on regression.
if [[ -f "$DECKHAND_HEALTH_CHECK" ]] && (( ! DRY_RUN )); then
  echo "==> hermes-patches: verifying gateway is patched (deckhand#162 guard)"
  python3 "$DECKHAND_HEALTH_CHECK" || true   # read-only; alerts owner if unpatched
fi
run_step claude claude update
run_step codex  codex  update
run_step gemini npm install -g @google/gemini-cli@latest

echo
echo "================ Summary ================"
for i in "${!NAMES[@]}"; do
  printf '  %-8s %s\n' "${NAMES[$i]}" "${STATUS[$i]}"
done

# Non-zero exit if any step failed, or if the deckhand patch re-apply failed
# (deckhand#63 — a wiped enforcement patch must break the run, not pass quietly).
if (( REAPPLY_FAILED )); then
  echo
  echo "ERROR: deckhand Hermes enforcement patches were not re-applied — see above."
  # Emit an ACTIVE alert, not just this cron log + the daily cron-health snapshot.
  # That passive surfacing let an UNPATCHED gateway (client-leak risk) sit unnoticed
  # for ~6 days (deckhand#354). notify.sh appends a fail event consumed by the email
  # attention-notify path. Fail-closed is preserved — we still exit 1 below.
  _repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  bash "${_repo_root}/scripts/notify.sh" cron hermes-patches fail \
    "deckhand enforcement patches did not re-apply — gateway attachment gate may be DOWN (client-leak risk); see deckhand#354" 2>/dev/null || true
  exit 1
fi
for s in "${STATUS[@]}"; do
  [[ "$s" == FAILED* ]] && exit 1
done
exit 0
