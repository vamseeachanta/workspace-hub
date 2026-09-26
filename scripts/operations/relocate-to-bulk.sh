#!/usr/bin/env bash
# relocate-to-bulk.sh — move a bulk data directory off a work surface onto the
# fleet bulk volume, with copy → verify → delete as a transaction.
#
# Runs ON the machine that owns the source directory. Fails CLOSED: the source
# is deleted ONLY after a checksum verification pass returns zero differences.
#
#   DRY_RUN=1 (default)  plan only, touch nothing
#   DRY_RUN=0            execute
#
# Transports (auto-detected, override with --transport):
#   local  — /mnt/ace is a local mount            (ace-linux-1)
#   nfs    — /mnt/remote/ace-linux-1/ace mounted  (ace-linux-2)
#   ssh    — no mount; rsync over ssh             (gpu-claw)
#
# Sensitivity gate. /mnt/ace is mode 777, NFS-exported rw, AND Samba-shared
# writable+browseable — treat it as LAN-public. Anything not explicitly marked
# --sensitivity public is REFUSED unless --encrypt is supplied with working
# age tooling. This mirrors the owner's own stated policy in
# _ace-preservation/PRESERVATION.md ("lives OFF the /mnt/ace share").
set -uo pipefail

# age lands in a different place on each machine (apt /usr/bin, brew
# /home/linuxbrew/..., conda ~/miniforge3/bin) and none of the non-apt ones are
# on a non-interactive PATH. Do not depend on login-shell config — find it here.
for _d in "$HOME/.local/bin" "$HOME/bin" /home/linuxbrew/.linuxbrew/bin \
          "$HOME/miniforge3/bin" "$HOME/miniconda3/bin" /usr/local/bin; do
  [ -d "$_d" ] && case ":$PATH:" in *":$_d:"*) ;; *) PATH="$_d:$PATH" ;; esac
done
export PATH

SRC=""; DEST_ROOT=""; TRANSPORT=""; SSH_HOST="ace-linux-1"
SENSITIVITY=""; ENCRYPT=0; RECIPIENTS="$HOME/.config/age/recipients.txt"
DRY_RUN="${DRY_RUN:-1}"; ALLOW_REPO=0; PULL_FROM=""

die() { echo "FATAL: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)        SRC="${2:?}"; shift 2 ;;
    --dest-root)   DEST_ROOT="${2:?}"; shift 2 ;;
    --transport)   TRANSPORT="${2:?}"; shift 2 ;;
    --ssh-host)    SSH_HOST="${2:?}"; shift 2 ;;
    --sensitivity) SENSITIVITY="${2:?}"; shift 2 ;;   # public | confidential
    --encrypt)     ENCRYPT=1; shift ;;
    --recipients)  RECIPIENTS="${2:?}"; shift 2 ;;
    --allow-repo)  ALLOW_REPO=1; shift ;;
    --pull-from)   PULL_FROM="${2:?}"; shift 2 ;;
    *) die "unknown arg: $1" ;;
  esac
done

[ -n "$SRC" ] || die "--path is required"
SRC="${SRC%/}"
NAME="$(basename "$SRC")"

# ---------------------------------------------------------------- PULL MODE
# For a source machine that cannot ssh INTO the bulk host (gpu-claw runs as
# 'undi', a user that does not exist on ace-linux-1). Rather than granting a
# shared multi-user box inbound access, run this ON the bulk host and pull.
# Encryption still happens on the SOURCE side, so plaintext never lands on the
# LAN-public share.
if [ -n "$PULL_FROM" ]; then
  RSH="ssh -o BatchMode=yes"
  $RSH "$PULL_FROM" "test -d '$SRC'" || die "$PULL_FROM:$SRC is not a directory"
  [ "$ALLOW_REPO" = 1 ] || ! $RSH "$PULL_FROM" "test -e '$SRC/.git'" \
    || die "$PULL_FROM:$SRC is a git repo — push it, do not relocate"

  echo "=== runtime-reference scan on $PULL_FROM for $SRC ==="
  hits=$($RSH "$PULL_FROM" "
    { crontab -l 2>/dev/null; cat ~/.config/systemd/user/* 2>/dev/null;
      cat ~/.deckhand/*.env ~/.hermes/*.env 2>/dev/null; } | grep -F -- '$SRC' || true")
  if [ -n "$hits" ]; then
    echo "$hits"; die "$SRC is a live runtime dependency on $PULL_FROM — cut the service over first"
  fi
  echo "  clean — no cron/systemd/env reference"

  # LIVE-PROCESS scan. Declared references are not enough: a process started by
  # hand has nothing in cron/systemd/env to find. On 2026-08-02 this exact gap
  # let voice-dictation be relocated out from under a running `voiced.py`
  # (PID 3193, cwd inside the tree, up since Jul 26). On NTFS-FUSE the deletion
  # turned its open files into .fuse_hidden tombstones instead of failing loudly.
  echo "=== live-process scan on $PULL_FROM for $SRC ==="
  live=$($RSH "$PULL_FROM" "
    for p in /proc/[0-9]*; do
      t=\$(readlink \"\$p/cwd\" 2>/dev/null); case \"\$t\" in '$SRC'|'$SRC'/*) echo \"cwd  \$(cat \$p/comm 2>/dev/null) [\${p#/proc/}] -> \$t\";; esac
      t=\$(readlink \"\$p/exe\" 2>/dev/null); case \"\$t\" in '$SRC'|'$SRC'/*) echo \"exe  \$(cat \$p/comm 2>/dev/null) [\${p#/proc/}] -> \$t\";; esac
    done 2>/dev/null | sort -u")
  if [ -n "$live" ]; then
    echo "$live"
    die "process(es) above are LIVE inside $SRC on $PULL_FROM.
Relocating would pull the tree out from under a running program. Stop it first,
then re-run. (Declared-reference scanning cannot see hand-started processes.)"
  fi
  echo "  clean — no process has its cwd or exe inside the tree"

  case "$SENSITIVITY" in
    public) ;;
    confidential) [ "$ENCRYPT" = 1 ] || die "confidential data requires --encrypt (bulk volume is LAN-public)" ;;
    *) die "--sensitivity must be 'public' or 'confidential'" ;;
  esac

  DEST_ROOT="${DEST_ROOT:-/mnt/ace/work-surface-bulk/$PULL_FROM}"
  need=$($RSH "$PULL_FROM" "du -sm '$SRC' | cut -f1")
  avail=$(df -BM --output=avail /mnt/ace | tail -1 | tr -dc '0-9')
  echo "transport=pull($PULL_FROM)  dest=$DEST_ROOT/$NAME  encrypt=$ENCRYPT  size=${need}M  avail=${avail}M"
  [ "$avail" -gt "$need" ] || die "insufficient space (need ${need}M, have ${avail}M)"
  [ "$DRY_RUN" = 1 ] && { echo "DRY-RUN: would pull, verify, then delete $PULL_FROM:$SRC"; exit 0; }

  mkdir -p "$DEST_ROOT"
  if [ "$ENCRYPT" = 1 ]; then
    BUNDLE="$DEST_ROOT/${NAME}.tar.zst.age"
    # tar|zstd|age all run on the SOURCE; only ciphertext crosses and lands.
    $RSH "$PULL_FROM" "export PATH=\$HOME/.local/bin:/home/linuxbrew/.linuxbrew/bin:\$PATH; \
      tar -C '$(dirname "$SRC")' -cf - '$NAME' | zstd -T0 | age -R ~/.config/age/recipients.txt" > "$BUNDLE" \
      || die "encrypted pull failed"
    [ -s "$HOME/.config/age/keys.txt" ] || die "no age identity to verify with — source NOT deleted"
    age -d -i "$HOME/.config/age/keys.txt" "$BUNDLE" | zstd -d | tar -tf - >/dev/null \
      || die "bundle failed to decrypt/list — source NOT deleted"
    echo "encrypted bundle verified: $BUNDLE ($(du -h "$BUNDLE" | cut -f1))"
  else
    mkdir -p "$DEST_ROOT/$NAME"
    rsync -a --protect-args "$PULL_FROM:$SRC/" "$DEST_ROOT/$NAME/" || die "pull failed"
    d=$(rsync -rcni --delete --protect-args "$PULL_FROM:$SRC/" "$DEST_ROOT/$NAME/")
    [ -z "$d" ] || { echo "$d" | head -20; die "checksum verification found differences — source NOT deleted"; }
    echo "checksum verification clean (0 differences)"
  fi
  # FAIL-CLOSED DELETE. The previous form was `rm -rf … && echo OK`, which on a
  # failed delete simply printed nothing and let the caller log success. On
  # NTFS-FUSE, deleting files a process holds open leaves .fuse_hidden tombstones
  # and non-empty directories, so rm exits non-zero — exactly what happened to
  # voice-dictation on 2026-08-02, which was then reported as OK.
  # Verify absence explicitly; never infer it from rm's exit status alone.
  $RSH "$PULL_FROM" "rm -rf -- '$SRC'" || echo "WARN: rm reported failure on $PULL_FROM:$SRC — verifying" >&2
  if $RSH "$PULL_FROM" "test -e '$SRC'"; then
    left=$($RSH "$PULL_FROM" "find '$SRC' -mindepth 1 | wc -l" 2>/dev/null)
    die "SOURCE NOT FULLY REMOVED: $PULL_FROM:$SRC still has $left entries.
The bundle IS written and verified — no data is lost — but this relocation is
INCOMPLETE. Check for live processes holding files open, then remove manually."
  fi
  echo "RELOCATED and removed $PULL_FROM:$SRC"
  exit 0
fi

[ -d "$SRC" ] || die "$SRC is not a directory"

# ---------------------------------------------------------------- gate 1
# Never relocate a git repository. A repo belongs on the work surface or on
# GitHub; moving it to bulk storage strands it.
if [ "$ALLOW_REPO" = 0 ] && [ -e "$SRC/.git" ]; then
  die "$SRC is a git repo/worktree — push it or use git worktree remove, do not relocate. Override with --allow-repo."
fi

# ---------------------------------------------------------------- gate 2
# THE GATE THAT MATTERS. A path referenced by cron, a systemd unit, or a
# service env file is a live runtime dependency. Moving it silently breaks the
# service — this is exactly how gpu-claw lost 8 days of licensed-run service in
# July 2026 (see ws/RELOCATION-ISSUE.md Resolution).
echo "=== runtime-reference scan for $SRC ==="
refs=0
if crontab -l 2>/dev/null | grep -F -- "$SRC" ; then refs=$((refs+1)); fi
for d in "$HOME/.config/systemd/user" /etc/systemd/system; do
  [ -d "$d" ] || continue
  if grep -rlF -- "$SRC" "$d" 2>/dev/null | grep . ; then refs=$((refs+1)); fi
done
for f in "$HOME"/.deckhand/*.env "$HOME"/.hermes/*.env "$HOME"/.config/*.env; do
  [ -f "$f" ] || continue
  if grep -lF -- "$SRC" "$f" 2>/dev/null | grep . ; then refs=$((refs+1)); fi
done
if [ "$refs" -gt 0 ]; then
  die "$SRC is referenced by $refs runtime config(s) shown above.
Relocating it WILL break them. Cut the service over first: stop it, move the
data, update every referencing path, daemon-reload, restart, confirm active."
fi
echo "  clean — no cron/systemd/env reference"

# ---------------------------------------------------------------- gate 2b
# LIVE-PROCESS scan (local). See the pull-mode copy of this gate for the
# incident that motivated it.
echo "=== live-process scan for $SRC ==="
live=""
for p in /proc/[0-9]*; do
  for l in cwd exe; do
    t=$(readlink "$p/$l" 2>/dev/null) || continue
    case "$t" in "$SRC"|"$SRC"/*) live="$live$l  $(cat "$p/comm" 2>/dev/null) [${p#/proc/}] -> $t"$'\n' ;; esac
  done
done
if command -v lsof >/dev/null 2>&1; then
  o=$(lsof +D "$SRC" 2>/dev/null | tail -n +2 | awk '{print "open " $1 " [" $2 "]"}' | sort -u)
  [ -n "$o" ] && live="$live$o"$'\n'
fi
if [ -n "$live" ]; then
  printf '%s' "$live"
  die "process(es) above are LIVE inside $SRC.
Relocating would pull the tree out from under a running program. Stop it first."
fi
echo "  clean — no process has its cwd, exe, or an open file inside the tree"

# ---------------------------------------------------------------- gate 3
case "$SENSITIVITY" in
  public) ;;
  confidential)
    [ "$ENCRYPT" = 1 ] || die "confidential data requires --encrypt (bulk volume is LAN-public: 777 + NFS-rw + Samba-writable)" ;;
  *) die "--sensitivity must be 'public' or 'confidential' — decide explicitly, there is no safe default" ;;
esac
if [ "$ENCRYPT" = 1 ]; then
  command -v age  >/dev/null || die "age not installed — encrypted relocation is blocked. Install age and generate a keypair first."
  command -v zstd >/dev/null || die "zstd not installed"
  [ -s "$RECIPIENTS" ] || die "no age recipients file at $RECIPIENTS"
fi

# ---------------------------------------------------------------- transport
if [ -z "$TRANSPORT" ]; then
  if   [ -d /mnt/ace ] && findmnt -no TARGET /mnt/ace >/dev/null 2>&1;                  then TRANSPORT=local
  elif findmnt -no TARGET /mnt/remote/ace-linux-1/ace >/dev/null 2>&1;                  then TRANSPORT=nfs
  else TRANSPORT=ssh; fi
fi
if [ -z "$DEST_ROOT" ]; then
  case "$TRANSPORT" in
    local) DEST_ROOT=/mnt/ace/work-surface-bulk/$(hostname) ;;
    nfs)   DEST_ROOT=/mnt/remote/ace-linux-1/ace/work-surface-bulk/$(hostname) ;;
    ssh)   DEST_ROOT=/mnt/ace/work-surface-bulk/$(hostname) ;;
  esac
fi
echo "transport=$TRANSPORT  dest=$DEST_ROOT/$NAME  encrypt=$ENCRYPT  mode=$([ "$DRY_RUN" = 1 ] && echo DRY-RUN || echo EXECUTE)"

# ---------------------------------------------------------------- capacity
need=$(du -sm "$SRC" 2>/dev/null | cut -f1)
echo "source size: ${need}M"
# The destination tree may not exist yet, and df cannot stat a missing path.
# Walk up to the nearest existing ancestor (ultimately the mount point).
nearest_existing() { local p="$1"; while [ ! -d "$p" ] && [ "$p" != "/" ]; do p="$(dirname "$p")"; done; printf '%s' "$p"; }
case "$TRANSPORT" in
  local|nfs) avail=$(df -BM --output=avail "$(nearest_existing "$DEST_ROOT")" 2>/dev/null | tail -1 | tr -dc '0-9') ;;
  ssh)       avail=$(ssh -o BatchMode=yes "$SSH_HOST" "df -BM --output=avail /mnt/ace | tail -1 | tr -dc '0-9'") ;;
esac
[ -n "${avail:-}" ] && [ "$avail" -gt "$need" ] || die "insufficient space at destination (need ${need}M, have ${avail:-unknown}M)"

if [ "$DRY_RUN" = 1 ]; then
  echo "DRY-RUN: would copy, verify, then delete $SRC"; exit 0
fi

# ---------------------------------------------------------------- copy
if [ "$ENCRYPT" = 1 ]; then
  BUNDLE="$DEST_ROOT/${NAME}.tar.zst.age"
  case "$TRANSPORT" in
    local|nfs) mkdir -p "$DEST_ROOT"
               tar -C "$(dirname "$SRC")" -cf - "$NAME" | zstd -T0 | age -R "$RECIPIENTS" > "$BUNDLE" || die "encrypt failed" ;;
    ssh)       ssh -o BatchMode=yes "$SSH_HOST" "mkdir -p '$DEST_ROOT'"
               tar -C "$(dirname "$SRC")" -cf - "$NAME" | zstd -T0 | age -R "$RECIPIENTS" \
                 | ssh -o BatchMode=yes "$SSH_HOST" "cat > '$BUNDLE'" || die "encrypt failed" ;;
  esac
  # Verify: the bundle must decrypt and list cleanly. Without a private key we
  # cannot prove this, so refuse rather than assume.
  [ -s "$HOME/.config/age/keys.txt" ] || die "no age identity to verify with — bundle written but source NOT deleted"
  case "$TRANSPORT" in
    local|nfs) age -d -i "$HOME/.config/age/keys.txt" "$BUNDLE" | zstd -d | tar -tf - >/dev/null || die "verify failed — source NOT deleted" ;;
    ssh)       ssh -o BatchMode=yes "$SSH_HOST" "cat '$BUNDLE'" | age -d -i "$HOME/.config/age/keys.txt" | zstd -d | tar -tf - >/dev/null || die "verify failed — source NOT deleted" ;;
  esac
  echo "encrypted bundle verified: $BUNDLE"
else
  case "$TRANSPORT" in
    local|nfs)
      mkdir -p "$DEST_ROOT/$NAME"
      rsync -a --no-owner --no-group --no-perms --protect-args "$SRC/" "$DEST_ROOT/$NAME/" || die "copy failed"
      diff_out=$(rsync -rcni --delete --no-owner --no-group --no-perms --protect-args "$SRC/" "$DEST_ROOT/$NAME/") ;;
    ssh)
      ssh -o BatchMode=yes "$SSH_HOST" "mkdir -p '$DEST_ROOT/$NAME'"
      rsync -a --protect-args "$SRC/" "$SSH_HOST:$DEST_ROOT/$NAME/" || die "copy failed"
      diff_out=$(rsync -rcni --delete --protect-args "$SRC/" "$SSH_HOST:$DEST_ROOT/$NAME/") ;;
  esac
  if [ -n "$diff_out" ]; then
    echo "$diff_out" | head -20
    die "checksum verification found differences — source NOT deleted"
  fi
  echo "checksum verification clean (0 differences)"
fi

# ---------------------------------------------------------------- delete
# Fail-closed delete — see the pull-mode copy above for the incident this fixes.
rm -rf -- "$SRC" || echo "WARN: rm reported failure on $SRC — verifying" >&2
if [ -e "$SRC" ]; then
  die "SOURCE NOT FULLY REMOVED: $SRC still has $(find "$SRC" -mindepth 1 | wc -l) entries.
The bundle IS written and verified — no data is lost — but this relocation is
INCOMPLETE. Check for live processes holding files open, then remove manually."
fi
echo "RELOCATED and removed source: $SRC"
