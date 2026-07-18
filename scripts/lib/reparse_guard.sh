# reparse_guard.sh — fail-closed guard against recursive deletion through NTFS
# reparse points (junctions/symlinks) (#3571).
#
# Incident 2026-07-16: a shared-skill link path that had been materialized as a
# junction into workspace-hub/.claude/skills was replaced via a child-enumerating
# delete, which followed the reparse point and emptied the canonical tree
# (4,215 tracked files). The rule: a reparse-point NODE may be removed with
# link-node-only primitives (rmdir / rm of the node itself) — its CHILDREN must
# never be enumerated for deletion, because they belong to the link target.
#
# is_reparse_point <path>   rc 0 = reparse point; rc 1 = not; rc 2 = undetermined
# guarded_rm_rf <path>      rm -rf that refuses (rc 1, loud) on reparse/undetermined
#
# Test seam: REPARSE_GUARD_FAKE is a colon-separated list of absolute paths to
# report as reparse points (hermetic fixtures can't mint real junctions).

is_reparse_point() {
  local p="$1"
  [ -e "$p" ] || [ -L "$p" ] || return 1
  if [ -n "${REPARSE_GUARD_FAKE:-}" ]; then
    # Canonicalize before matching — callers construct paths in different forms
    # (MSYS /c/... vs concatenated) and a string miss would defeat the seam.
    local cp
    cp="$(cd "$(dirname "$p")" 2>/dev/null && pwd)/$(basename "$p")"
    case ":${REPARSE_GUARD_FAKE}:" in
      *":${cp}:"*|*":${p}:"*) return 0 ;;
    esac
    return 1
  fi
  [ -L "$p" ] && return 0
  case "$(uname -s 2>/dev/null)" in
    MINGW*|MSYS*|CYGWIN*)
      local wp attr
      wp="$(cygpath -w "$p" 2>/dev/null)" || return 2
      if command -v powershell.exe >/dev/null 2>&1; then
        attr="$(powershell.exe -NoProfile -Command \
          "(Get-Item -LiteralPath '$wp' -Force).Attributes" 2>/dev/null)"
        if [ -n "$attr" ]; then
          case "$attr" in *ReparsePoint*) return 0 ;; *) return 1 ;; esac
        fi
      fi
      if command -v fsutil >/dev/null 2>&1; then
        if fsutil reparsepoint query "$wp" >/dev/null 2>&1; then return 0; fi
        return 1
      fi
      return 2   # no probe available — caller must fail closed
      ;;
  esac
  return 1
}

guarded_rm_rf() {
  local p="$1" r
  is_reparse_point "$p"
  r=$?
  if [ "$r" -ne 1 ]; then
    echo "reparse-guard: refusing recursive delete of '$p' — reparse point (or probe unavailable); its children belong to the link TARGET. Remove the link node only (rmdir)." >&2
    return 1
  fi
  rm -rf -- "$p"
}
