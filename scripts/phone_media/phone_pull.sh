#!/usr/bin/env bash
# phone_pull.sh - copy an iPhone camera roll (DCIM) off the phone at full
# quality, verify it, back it up to Google Drive and write a verified list of
# what is safe to delete from the phone. Issues #3584, #3586 (epic #3589).
#
# Runs on the archive host (Linux, gvfs AFC). It never deletes or changes
# anything on the phone and never overwrites an archive file. Reports name
# private media and stay under <root>/<phone>/reports/ on the archive host;
# terminal output carries counts and report paths only.
#
# Typical use (phone plugged in, unlocked, trusted, Auto-Lock = Never):
#   scripts/phone_media/phone_pull.sh --phone iphone-<name>
# Dry run with no phone (fake DCIM, fake Drive folder under /tmp):
#   scripts/phone_media/phone_pull.sh --dry-run
# Agent guide: .claude/skills/phone-media-pull/SKILL.md
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER="$HERE/phone_pull.py"
LIVE_ROOT="/mnt/ace/ws/phone-media"

PHONE=""; UDID=""; ROOT="$LIVE_ROOT"; REMOTE="gdrive:backups/phone-media"
STEPS="preflight,pull,verify,backup,safe-list"
DRY_RUN=0; FAKE_DCIM=""; JPEG=0; YOUTUBE=0; HASH_PHONE=0; FORCE_BACKUP=0
YT_MIN_MB=500; YT_MIN_MIN=10; SIM_MISSING=0; TPSLIMIT=4; ROOT_SET=0; REMOTE_SET=0

usage() {
  cat <<'EOF'
Usage: phone_pull.sh --phone NAME [options]
  --phone NAME            archive folder name, e.g. iphone-14 (lowercase, digits, -)
  --udid UDID             pick the phone when more than one is attached
  --root DIR              archive root (default /mnt/ace/ws/phone-media)
  --remote REMOTE         backup root (default gdrive:backups/phone-media)
  --steps LIST            comma list from: preflight,pull,verify,backup,safe-list,
                          jpeg,youtube-plan (default: the first five)
  --jpeg                  also make JPEG copies of HEIC in <phone>/usb-jpeg/
                          (originals untouched; needs uv to fetch pillow-heif)
  --youtube-plan          also write a YouTube upload plan (never uploads)
  --youtube-min-mb N      plan videos >= N MB (default 500)
  --youtube-min-minutes N or >= N minutes long (default 10; needs ffprobe)
  --hash-phone            re-read every phone file and compare SHA-256 (slower)
  --force-backup          run the backup even if preflight found Drive short
  --tpslimit N            rclone transactions per second (default 4)
  --dry-run               no phone, no Drive: fake DCIM and a fake Drive folder
                          in a new /tmp folder (never the live archive)
  --fake-dcim DIR         dry run: use this DCIM folder instead of a generated one
  --simulate-drive-missing N
                          dry run: drop N files from the fake Drive after the
                          copy, to show they are kept off the safe list
EOF
}

die() { echo "ERROR: $*" >&2; exit "${2:-1}"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --phone) PHONE="${2:?}"; shift 2 ;;
    --udid) UDID="${2:?}"; shift 2 ;;
    --root) ROOT="${2:?}"; ROOT_SET=1; shift 2 ;;
    --remote) REMOTE="${2:?}"; REMOTE_SET=1; shift 2 ;;
    --steps) STEPS="${2:?}"; shift 2 ;;
    --jpeg) JPEG=1; shift ;;
    --youtube-plan) YOUTUBE=1; shift ;;
    --youtube-min-mb) YT_MIN_MB="${2:?}"; shift 2 ;;
    --youtube-min-minutes) YT_MIN_MIN="${2:?}"; shift 2 ;;
    --hash-phone) HASH_PHONE=1; shift ;;
    --force-backup) FORCE_BACKUP=1; shift ;;
    --tpslimit) TPSLIMIT="${2:?}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --fake-dcim) FAKE_DCIM="${2:?}"; shift 2 ;;
    --simulate-drive-missing) SIM_MISSING="${2:?}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; die "unknown option: $1" 2 ;;
  esac
done
[ "$JPEG" = 1 ] && STEPS="$STEPS,jpeg"
[ "$YOUTUBE" = 1 ] && STEPS="$STEPS,youtube-plan"
has_step() { case ",$STEPS," in *",$1,"*) return 0 ;; *) return 1 ;; esac; }

# ------------------------------------------------------------------ setup
RCLONE="$(command -v rclone || true)"
[ -z "$RCLONE" ] && [ -x "$HOME/.local/bin/rclone" ] && RCLONE="$HOME/.local/bin/rclone"
PY="$(command -v python3 || true)"
[ -n "$PY" ] || die "python3 not found"
command -v rsync >/dev/null || die "rsync not found (sudo apt install rsync)"

if [ "$DRY_RUN" = 1 ]; then
  BASE="$(mktemp -d /tmp/phone-pull-dryrun.XXXXXX)" || die "mktemp failed"
  touch "$BASE/.phone-pull-dryrun"
  [ "$ROOT_SET" = 1 ] || ROOT="$BASE/archive"
  [ "$REMOTE_SET" = 1 ] || REMOTE="$BASE/fake-drive"
  [ -n "$PHONE" ] || PHONE="iphone-dryrun"
  case "$(realpath -m "$ROOT")/" in
    "$(realpath -m "$LIVE_ROOT")/"*) die "dry run refuses the live archive root" ;;
  esac
  case "$REMOTE" in /*) ;; *) die "dry run needs a local folder as --remote" ;; esac
  mkdir -p "$ROOT" "$REMOTE"
  echo "DRY RUN in $BASE (no phone, no Google Drive)"
fi
[ -n "$PHONE" ] || { usage >&2; die "--phone is required" 2; }
[[ "$PHONE" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "--phone must be lowercase letters, digits and -"
[ -n "$RCLONE" ] || die "rclone not found (expected on PATH or ~/.local/bin/rclone)"

USB="$ROOT/$PHONE/usb"
REPORTS="$ROOT/$PHONE/reports"
DEST="$REMOTE/$PHONE/usb"
case "$REMOTE" in /*) REMOTE_ROOT="$REMOTE" ;; *) REMOTE_ROOT="${REMOTE%%:*}:" ;; esac
STAMP="$(date +%Y-%m-%d-%H%M)"
mkdir -p "$REPORTS" || die "cannot create $REPORTS"
if has_step preflight || has_step pull; then
  RUN="$REPORTS/run-$STAMP"
  mkdir -p "$RUN" && echo "run-$STAMP" > "$REPORTS/LATEST"
else
  [ -f "$REPORTS/LATEST" ] || die "no earlier run in $REPORTS; include preflight,pull"
  RUN="$REPORTS/$(cat "$REPORTS/LATEST")"
fi
RC=0
note_rc() { [ "$1" -gt "$RC" ] && RC="$1"; return 0; }
RCLONE_FILTER=(--exclude ".*" --exclude ".*/**")

# ------------------------------------------------------------ find phone
find_dcim() {
  if [ "$DRY_RUN" = 1 ]; then
    if [ -z "$FAKE_DCIM" ]; then
      FAKE_DCIM="$BASE/phone/DCIM"
      if has_step jpeg && command -v uv >/dev/null; then
        # real (tiny) HEIC files so the JPEG step has something to convert
        uv run --no-project --quiet --with pillow-heif python "$HELPER" make-fake-dcim \
          --dcim "$FAKE_DCIM" --seed-conflict "$USB" || return 1
      else
        "$PY" "$HELPER" make-fake-dcim --dcim "$FAKE_DCIM" --seed-conflict "$USB" || return 1
      fi
    fi
    DCIM="$FAKE_DCIM"; return 0
  fi
  command -v gio >/dev/null || { echo "gio not found (sudo apt install gvfs-backends gvfs-fuse)" >&2; return 1; }
  : "${DBUS_SESSION_BUS_ADDRESS:=unix:path=/run/user/$(id -u)/bus}"
  export DBUS_SESSION_BUS_ADDRESS
  local gvfs ids
  gvfs="/run/user/$(id -u)/gvfs"
  if [ -z "$UDID" ]; then
    ids="$( { ls "$gvfs" 2>/dev/null | sed -n 's/^afc:host=\([^,]*\).*/\1/p'
              gio mount -li 2>/dev/null | grep -o 'afc://[^/ ]*' | sed 's#afc://##'; } \
            | sort -u)"
    case "$(printf '%s\n' "$ids" | grep -c .)" in
      0) echo "No iPhone found. Plug it in with a data cable, unlock it, tap Trust" >&2
         echo "and enter the passcode, then run again." >&2; return 1 ;;
      1) UDID="$ids" ;;
      *) echo "More than one iPhone attached; rerun with --udid <one of>:" >&2
         printf '  %s\n' $ids >&2; return 1 ;;
    esac
  fi
  gio mount "afc://$UDID/" 2>/dev/null || true   # already mounted is fine
  DCIM="$gvfs/afc:host=$UDID/DCIM"
  if [ ! -d "$DCIM" ] || [ -z "$(ls -A "$DCIM" 2>/dev/null)" ]; then
    echo "Phone seen but its photos are not visible. Unlock it, keep it unlocked," >&2
    echo "tap Trust This Computer if asked, then run again." >&2
    return 1
  fi
}

# ----------------------------------------------------------------- steps
step_preflight() {
  echo "== preflight"
  if [ "$DRY_RUN" = 0 ]; then
    cat <<'EOF'
Phone checklist:
  - data cable (not charge-only); phone unlocked; tap "Trust This Computer" and
    enter the passcode if asked
  - Settings > Display & Brightness > Auto-Lock > Never for the pull (iOS hides
    photos over USB once it locks); set it back afterwards
  - Settings > Photos: if iCloud Photos is on with "Optimize iPhone Storage",
    the phone holds only small copies of older items; switch to "Download and
    Keep Originals" and let it finish first, or accept that those items are
    not pulled at full quality
EOF
  fi
  find_dcim || return 3
  "$PY" "$HELPER" scan --source "$DCIM" --out "$RUN/phone-scan.json" || return 3
  local free; free="$(df -B1 --output=avail "$ROOT" | tail -1 | tr -d ' ')"
  "$RCLONE" about "$REMOTE_ROOT" --json > "$RUN/remote-about.json" 2> "$RUN/remote-about.log" \
    || { echo "Drive not reachable: rclone about failed (log in $RUN)" >&2; return 5; }
  "$RCLONE" size "$DEST" --json > "$RUN/remote-size.json" 2>/dev/null || : > "$RUN/remote-size.json"
  "$PY" "$HELPER" preflight --scan "$RUN/phone-scan.json" --local-free "$free" \
    --about "$RUN/remote-about.json" --remote-size "$RUN/remote-size.json" \
    --out "$RUN/preflight.json"
  local rc=$?
  rm -f "$RUN/BACKUP_BLOCKED"
  grep -q '"drive_ok": false' "$RUN/preflight.json" && touch "$RUN/BACKUP_BLOCKED"
  return $rc
}

step_pull() {
  echo "== pull (rsync, new files only; progress in $RUN/rsync.log)"
  [ -n "${DCIM:-}" ] || find_dcim || return 3
  mkdir -p "$USB"
  rsync -rt --no-perms --no-owner --no-group --ignore-existing --exclude='.*' \
    --info=progress2,stats1 "$DCIM/" "$USB/" > "$RUN/rsync.log" 2>&1
  local rc=$?
  [ $rc -eq 0 ] || echo "rsync exit $rc (details in $RUN/rsync.log); reconcile reports what is missing"
  "$PY" "$HELPER" reconcile --phone-dir "$DCIM" --local-dir "$USB" --out "$RUN/pull-map.json"
}

step_verify() {
  echo "== verify"
  [ -n "${DCIM:-}" ] || find_dcim || return 3
  local extra=()
  [ "$HASH_PHONE" = 1 ] && extra+=(--hash-phone)
  "$PY" "$HELPER" verify --map "$RUN/pull-map.json" --phone-dir "$DCIM" \
    --local-dir "$USB" --manifest "$RUN/manifest.tsv" "${extra[@]}"
  local rc=$?
  echo "manifest: $RUN/manifest.tsv"
  return $rc
}

step_backup() {
  echo "== backup to $DEST"
  if [ -f "$RUN/BACKUP_BLOCKED" ] && [ "$FORCE_BACKUP" = 0 ]; then
    echo "Drive has too little free space for this phone (see preflight)." >&2
    echo "Backup skipped; nothing will be listed as safe to delete. Free space or" >&2
    echo "buy storage (#3586), then rerun with --steps backup,safe-list." >&2
    return 8
  fi
  [ "$DRY_RUN" = 1 ] && mkdir -p "$DEST"
  "$RCLONE" copy "$USB" "$DEST" "${RCLONE_FILTER[@]}" --tpslimit "$TPSLIMIT" \
    --stats 1m --stats-one-line --log-file "$RUN/rclone-copy.log" --log-level INFO
  local rc=$?
  [ $rc -eq 0 ] || { echo "rclone copy exit $rc (details in $RUN/rclone-copy.log)"; rc=11; }
  if [ "$DRY_RUN" = 1 ] && [ "$SIM_MISSING" -gt 0 ]; then
    "$PY" "$HELPER" simulate-missing --dest "$DEST" --count "$SIM_MISSING"
  fi
  echo "-- rclone check, size only"
  "$RCLONE" check "$USB" "$DEST" --one-way --size-only "${RCLONE_FILTER[@]}" \
    --combined "$RUN/check-size.txt" --log-file "$RUN/check-size.log"
  local rs=$?
  echo "   exit $rs (0 = all present with the same size)"
  echo "-- rclone check, hash (MD5 on Google Drive)"
  "$RCLONE" check "$USB" "$DEST" --one-way "${RCLONE_FILTER[@]}" \
    --combined "$RUN/check-hash.txt" --log-file "$RUN/check-hash.log"
  local rh=$?
  echo "   exit $rh (0 = all present with the same hash)"
  if [ $rs -ne 0 ] || [ $rh -ne 0 ]; then
    echo "Drive copy incomplete or different; those files stay off the safe list."
    echo "Rerun later with --steps backup,safe-list to retry the upload."
    [ $rc -ne 0 ] || rc=10
  fi
  return $rc
}

step_safe_list() {
  echo "== safe-to-delete list"
  local args=(--phone "$PHONE" --manifest "$RUN/manifest.tsv" --out-dir "$REPORTS"
              --stamp "$STAMP")
  [ -f "$RUN/check-size.txt" ] && args+=(--size-check "$RUN/check-size.txt")
  [ -f "$RUN/check-hash.txt" ] && args+=(--hash-check "$RUN/check-hash.txt" --hash-log "$RUN/check-hash.log")
  "$PY" "$HELPER" safe-list "${args[@]}"
}

step_jpeg() {
  echo "== JPEG copies of HEIC (originals untouched)"
  command -v uv >/dev/null || { echo "uv not found; JPEG step skipped" >&2; return 7; }
  uv run --no-project --quiet --with pillow-heif python "$HELPER" jpeg \
    --manifest "$RUN/manifest.tsv" --local-dir "$USB" --out-dir "$ROOT/$PHONE/usb-jpeg"
}

step_youtube() {
  echo "== YouTube plan (prepared, NOT run)"
  "$PY" "$HELPER" youtube-plan --manifest "$RUN/manifest.tsv" --local-dir "$USB" \
    --out "$REPORTS/youtube-plan-$STAMP" --min-mb "$YT_MIN_MB" --min-minutes "$YT_MIN_MIN"
}

# ------------------------------------------------------------------- run
DCIM=""
if has_step preflight; then step_preflight; r=$?; note_rc $r
  [ $r -eq 0 ] || { echo "Preflight failed (exit $r); nothing copied."; exit $r; }
fi
if has_step pull; then step_pull; note_rc $?; fi
if has_step verify; then step_verify; note_rc $?; fi
if has_step backup; then step_backup; note_rc $?; fi
if has_step safe-list; then step_safe_list; note_rc $?; fi
if has_step jpeg; then step_jpeg; note_rc $?; fi
if has_step youtube-plan; then step_youtube; note_rc $?; fi

echo "== done (exit $RC). Reports: $REPORTS"
[ "$DRY_RUN" = 0 ] && echo "Set Auto-Lock back on the phone (Settings > Display & Brightness)."
exit "$RC"
