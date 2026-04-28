#!/usr/bin/env bash
set -euo pipefail

# Elements ingest helper for workspace-hub#2526.
# This script intentionally copies only into _from_elements staging folders.
# It does NOT merge staged files into parent folders and does NOT delete source files.

DEVICE="${DEVICE:-/dev/sdi1}"
SRC="/mnt/elements"
LOG_DIR="/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest"
mkdir -p "$LOG_DIR" "$SRC"

echo "== Remount Elements read-only =="
findmnt "$SRC" -o TARGET,SOURCE,FSTYPE,OPTIONS || true
if findmnt "$SRC" >/dev/null 2>&1; then
  sudo umount "$SRC"
fi
sudo ntfs-3g -o ro,big_writes,uid=$(id -u),gid=$(id -g),umask=022 "$DEVICE" "$SRC"
findmnt "$SRC" -o TARGET,SOURCE,FSTYPE,OPTIONS | tee "$LOG_DIR/mount-after-remount.txt"
if ! findmnt -no OPTIONS "$SRC" | grep -qw ro; then
  echo "ERROR: $SRC is not mounted read-only; refusing to continue" >&2
  exit 2
fi

echo "== Source inventory =="
find "$SRC" -maxdepth 1 -mindepth 1 -printf '%f\t%y\t%s\n' | sort | tee "$LOG_DIR/source-top-level-inventory.tsv"
find "$SRC" -type f -printf '%P\t%s\n' | sort > "$LOG_DIR/source-file-size-manifest.tsv"

# Checksums can be long; leave enabled because it is required by the safety plan.
(cd "$SRC" && find . -type f -size -100M -print0 | sort -z | xargs -0 sha256sum) > "$LOG_DIR/source-sha256-under-100mb.txt"

copy_one() {
  local source_rel="$1"
  local dest="$2"
  local tag="$3"
  if [[ ! -e "$SRC/$source_rel" ]]; then
    echo "MISSING: $SRC/$source_rel" | tee -a "$LOG_DIR/missing-sources.txt"
    return 0
  fi
  mkdir -p "$dest"
  echo "== DRY RUN: $source_rel -> $dest =="
  rsync -aHAXn --info=progress2 --stats "$SRC/$source_rel/" "$dest/" 2>&1 | tee "$LOG_DIR/rsync-dry-run-${tag}.log"
  echo "== COPY: $source_rel -> $dest =="
  rsync -aHAX --info=progress2 --stats "$SRC/$source_rel/" "$dest/" 2>&1 | tee "$LOG_DIR/rsync-copy-${tag}.log"
  {
    echo "## Elements ingest: $source_rel"
    echo
    echo "- Source drive label: Elements"
    echo "- Source device: $DEVICE"
    echo "- Source path: $SRC/$source_rel/"
    echo "- Destination staging path: $dest/"
    echo "- Ingest timestamp: $(date -Is)"
    echo "- Manifest: $LOG_DIR/source-file-size-manifest.tsv"
    echo "- Checksums <100MB: $LOG_DIR/source-sha256-under-100mb.txt"
    echo "- Dry-run log: $LOG_DIR/rsync-dry-run-${tag}.log"
    echo "- Copy log: $LOG_DIR/rsync-copy-${tag}.log"
    echo "- Related issue: https://github.com/vamseeachanta/workspace-hub/issues/2526"
    echo "- Post-copy action: staged only; manual dedupe-merge still required."
    echo
  } >> "$(dirname "$dest")/MOVE-LOG.md"
}

copy_one "62092  SESA FLNG Terminal Project" "/mnt/ace/doris/62092_sesa/_from_elements" "doris-62092-sesa"
copy_one "casa_grande_77017" "/mnt/ace/assethold/casa-grande-77017/_from_elements" "assethold-casa-grande-77017"
copy_one "Codes and Specs" "/mnt/ace/doris/codes/_from_elements/codes-doris" "doris-codes-specs"
copy_one "Doris University" "/mnt/ace/doris/training/_from_elements" "doris-university"
copy_one "qgis" "/mnt/ace/digitalmodel/tools/qgis/_from_elements" "digitalmodel-qgis"
copy_one "Riser Toolbox" "/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements" "digitalmodel-riser-toolbox"
copy_one "Suction Pile Sizing" "/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements" "digitalmodel-suction-pile-sizing"
copy_one "Woodfibre" "/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements" "acma-projects-31522-woodfibre"

# Codes & Regulations is intentionally not copied; verify-only per issue.
{
  echo "Codes & Regulations was not copied. Per issue #2526 it is verify-only against /mnt/ace/acma-codes unless missing content is proven."
  date -Is
} | tee "$LOG_DIR/codes-regulations-skip-note.txt"

echo "== DONE: staged copy only; no merge and no source deletion performed =="
