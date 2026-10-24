#!/usr/bin/env bash
# Shared directory ownership prevents overlap even when callers have different PATHs.
# Policy bounds and status codes: docs/readiness/equality-semantics.html, revision 1.
# flock(1), util-linux 2.43.devel, --nonblock / --conflict-exit-code: use 75 for contention.

acquire_publish_lock() {
  PUBLISH_LOCK_DIR="$1.d"
  PUBLISH_LOCK_OWNED=0
  local stale="${PUBLISH_EQUALITY_LOCK_STALE_SECONDS:-3600}"
  local mode="${PUBLISH_EQUALITY_LOCK:-auto}" now pid started rc probe_error
  [[ "$stale" =~ ^[1-9][0-9]*$ && ${#stale} -le 9 ]] || {
    echo 'publish-equality: invalid stale-lock policy' >&2; return 1;
  }
  case "$mode" in auto|mkdir) ;; *) echo 'publish-equality: invalid lock mode' >&2; return 1;; esac
  now=$(date -u +%s) || return 1
  [[ "$now" =~ ^[0-9]+$ ]] || return 1
  # Serialize acquisition and reclamation; a missing owner never permits takeover.
  mkdir "$PUBLISH_LOCK_DIR.guard" 2>/dev/null || {
    if [[ -d "$PUBLISH_LOCK_DIR.guard" ]]; then
      echo 'publish-equality: another publish in flight' >&2
      return 75
    fi
    echo 'publish-equality: cannot set up lock guard' >&2; return 1;
  }
  if ! mkdir "$PUBLISH_LOCK_DIR" 2>/dev/null; then
    rc=75
    if [[ ! -d "$PUBLISH_LOCK_DIR" || -L "$PUBLISH_LOCK_DIR" ]]; then
      rc=1
    elif [[ -f "$PUBLISH_LOCK_DIR/owner" && ! -L "$PUBLISH_LOCK_DIR/owner" ]]; then
      read -r pid started < "$PUBLISH_LOCK_DIR/owner" || pid=''
      probe_error=''
      if [[ "$pid" =~ ^[1-9][0-9]*$ ]]; then
        probe_error=$(LC_ALL=C kill -0 "$pid" 2>&1) || true
      fi
      if [[ "$pid" =~ ^[1-9][0-9]*$ && "$started" =~ ^[0-9]+$ \
            && ${#started} -le ${#now} ]] \
        && (( now - started > stale )) && [[ "$probe_error" == *'No such process'* ]]; then
        # Only known metadata is removed; unexpected contents fail closed.
        if rm -- "$PUBLISH_LOCK_DIR/owner" && rmdir "$PUBLISH_LOCK_DIR" \
          && mkdir "$PUBLISH_LOCK_DIR"; then
          echo 'publish-equality: reclaimed stale lock with dead owner' >&2
          rc=0
        else
          rc=1
        fi
      fi
    else
      rc=1
    fi
    if (( rc != 0 )); then
      rmdir "$PUBLISH_LOCK_DIR.guard" || return 1
      (( rc == 75 )) && echo 'publish-equality: another publish in flight' >&2
      return "$rc"
    fi
  fi
  PUBLISH_LOCK_TOKEN="$$ $now"
  if ! printf '%s\n' "$PUBLISH_LOCK_TOKEN" > "$PUBLISH_LOCK_DIR/owner"; then
    rmdir "$PUBLISH_LOCK_DIR.guard" || return 1
    return 1
  fi
  PUBLISH_LOCK_OWNED=1
  rmdir "$PUBLISH_LOCK_DIR.guard" || return 1
  if [[ "$mode" == auto ]] && command -v flock >/dev/null 2>&1; then
    if ! exec 9>"$1.flock"; then release_publish_lock; return 1; fi
    flock -n -E 75 9; rc=$?
    if (( rc != 0 )); then
      release_publish_lock || return 1
      (( rc == 75 )) && return 75
      echo 'publish-equality: flock setup failed' >&2
      return 1
    fi
  fi
}

release_publish_lock() {
  [[ "${PUBLISH_LOCK_OWNED:-0}" == 1 ]] || return 0
  local current
  [[ -f "$PUBLISH_LOCK_DIR/owner" && ! -L "$PUBLISH_LOCK_DIR/owner" ]] || return 1
  read -r current < "$PUBLISH_LOCK_DIR/owner" || return 1
  [[ "$current" == "$PUBLISH_LOCK_TOKEN" ]] || return 1
  rm -- "$PUBLISH_LOCK_DIR/owner" && rmdir "$PUBLISH_LOCK_DIR" || return 1
  PUBLISH_LOCK_OWNED=0
  exec 9>&-
}
