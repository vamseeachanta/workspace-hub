#!/usr/bin/env bash
# Sync public origin/main Claude memory snapshot blobs into the private archive
# legacy path and write a counts/hash-only verification report.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"

PRIVATE_CLONE="${1:-${CLAUDE_MEMORY_SNAPSHOT_PRIVATE_CLONE:-${HOME}/.local/share/claude-memory-snapshots}}"
PUBLIC_REF="${CLAUDE_MEMORY_SNAPSHOT_PUBLIC_REF:-origin/main}"
SNAPSHOT_PATH="config/agents/claude/memory-snapshots"
DATE_STAMP="$(date +%Y-%m-%d)"
LEGACY_ROOT="$PRIVATE_CLONE/legacy"
VERIFY_FILE="$PRIVATE_CLONE/VERIFY-${DATE_STAMP}.txt"

tmp_public="$(mktemp)"
tmp_private="$(mktemp)"
tmp_missing="$(mktemp)"
cleanup() {
  rm -f "$tmp_public" "$tmp_private" "$tmp_missing"
}
trap cleanup EXIT

git -C "$WORKSPACE_HUB" ls-tree -rz "$PUBLIC_REF" "$SNAPSHOT_PATH" \
  | while IFS=$'\t' read -r -d '' meta path; do
      set -- $meta
      printf '%s\n' "$3"
    done | sort -u > "$tmp_public"

public_count="$(git -C "$WORKSPACE_HUB" ls-tree -r --name-only "$PUBLIC_REF" "$SNAPSHOT_PATH" | wc -l | tr -d ' ')"
public_unique="$(wc -l < "$tmp_public" | tr -d ' ')"

mkdir -p "$LEGACY_ROOT"
if [[ "$public_count" != "0" ]]; then
  git -C "$WORKSPACE_HUB" archive "$PUBLIC_REF" "$SNAPSHOT_PATH" | tar -x -C "$LEGACY_ROOT"
fi

(
  cd "$PRIVATE_CLONE"
  find . -path ./.git -prune -o -type f -print0 \
    | sort -z \
    | xargs -0 -r git hash-object \
    | sort -u
) > "$tmp_private"

private_unique="$(wc -l < "$tmp_private" | tr -d ' ')"
comm -23 "$tmp_public" "$tmp_private" > "$tmp_missing"
missing_count="$(wc -l < "$tmp_missing" | tr -d ' ')"
covered_count="$(( public_unique - missing_count ))"

{
  printf 'public_ref=%s\n' "$PUBLIC_REF"
  printf 'public_files=%s\n' "$public_count"
  printf 'public_unique_blobs=%s\n' "$public_unique"
  printf 'private_unique_blobs=%s\n' "$private_unique"
  printf 'covered_public_unique_blobs=%s\n' "$covered_count"
  printf 'missing_public_unique_blobs=%s\n' "$missing_count"
  printf 'public_blob_hashes_sha1:\n'
  sed 's/^/- /' "$tmp_public"
  if [[ "$missing_count" != "0" ]]; then
    printf 'missing_public_blob_hashes_sha1:\n'
    sed 's/^/- /' "$tmp_missing"
  fi
} > "$VERIFY_FILE"

if [[ "$missing_count" != "0" ]]; then
  echo "ERROR: missing_public_unique_blobs=$missing_count" >&2
  exit 1
fi

printf 'public_files=%s\n' "$public_count"
printf 'public_unique_blobs=%s\n' "$public_unique"
printf 'private_unique_blobs=%s\n' "$private_unique"
printf 'covered_public_unique_blobs=%s\n' "$covered_count"
printf 'verify_file=%s\n' "$VERIFY_FILE"
