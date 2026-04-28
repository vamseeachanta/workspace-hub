#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSESS="$ROOT/dedupe-merge-assessment"
SUMMARY="$ROOT/dedupe-merge-assessment-summary.tsv"
LOG_SUMMARY="$ROOT/option-d-merge-summary.tsv"
STAMP="$(date -Is)"

mkdir -p "$ASSESS"

# order|bucket|parent|stage
BUCKETS=(
  "01|digitalmodel-suction-pile-sizing|/mnt/ace/digitalmodel/references/suction-pile-sizing|/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements"
  "02|assethold-casa-grande-77017|/mnt/ace/assethold/casa-grande-77017|/mnt/ace/assethold/casa-grande-77017/_from_elements"
  "03|digitalmodel-qgis|/mnt/ace/digitalmodel/tools/qgis|/mnt/ace/digitalmodel/tools/qgis/_from_elements"
  "04|digitalmodel-riser-toolbox|/mnt/ace/digitalmodel/references/riser-toolbox|/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements"
  "05|doris-62092-sesa|/mnt/ace/doris/62092_sesa|/mnt/ace/doris/62092_sesa/_from_elements"
  "06|doris-university|/mnt/ace/doris/training|/mnt/ace/doris/training/_from_elements"
  "07|doris-codes-specs|/mnt/ace/doris/codes|/mnt/ace/doris/codes/_from_elements/codes-doris"
  "08|acma-projects-31522-woodfibre|/mnt/ace/acma-projects/31522-woodfibre-lng|/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements"
)

printf 'timestamp\torder\tbucket\tparent\tstage\tstatus\tlog\n' > "$LOG_SUMMARY"

if [[ ! -f "$SUMMARY" ]]; then
  echo "Missing assessment summary: $SUMMARY" >&2
  exit 1
fi

# Refuse if any assessment found same-path size conflicts.
if awk -F '\t' 'NR>1 && $10 != 0 { bad=1 } END { exit bad ? 0 : 1 }' "$SUMMARY"; then
  echo "Refusing merge: same-path different-size conflicts present in $SUMMARY" >&2
  exit 1
fi

for entry in "${BUCKETS[@]}"; do
  IFS='|' read -r order bucket parent stage <<< "$entry"
  log="$ASSESS/${order}-${bucket}.option-d-hardlink-merge.log"

  echo "=== [$order] $bucket ==="
  echo "Parent: $parent"
  echo "Stage:  $stage"
  echo "Log:    $log"

  [[ -d "$parent" ]] || { echo "Missing parent: $parent" >&2; exit 1; }
  [[ -d "$stage" ]] || { echo "Missing stage: $stage" >&2; exit 1; }

  parent_dev="$(stat -c '%d' "$parent")"
  stage_dev="$(stat -c '%d' "$stage")"
  if [[ "$parent_dev" != "$stage_dev" ]]; then
    echo "Refusing $bucket: parent/stage are not on same device; hardlink merge is unsafe/impossible." >&2
    exit 1
  fi

  {
    echo "# Option D hardlink-preserving merge"
    echo "timestamp_start=$STAMP"
    echo "bucket=$bucket"
    echo "parent=$parent"
    echo "stage=$stage"
    echo "parent_dev=$parent_dev"
    echo "stage_dev=$stage_dev"
    echo "command=rsync -aHAX --ignore-existing --link-dest=$stage $stage/ $parent/"
    echo
    rsync -aHAX --ignore-existing --link-dest="$stage" --itemize-changes --stats "$stage/" "$parent/"
    echo
    echo "timestamp_end=$(date -Is)"
  } | tee "$log"

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date -Is)" "$order" "$bucket" "$parent" "$stage" "MERGED" "$log" >> "$LOG_SUMMARY"
done

echo "Wrote $LOG_SUMMARY"
