#!/usr/bin/env bash
set -euo pipefail

WRK_ID="${1:-}"
if [[ ! "$WRK_ID" =~ ^WRK-[0-9]+$ ]]; then
  echo "Usage: $0 WRK-NNN" >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ASSET_DIR="${ROOT}/.claude/work-queue/assets/${WRK_ID}"
SUMMARY="${ASSET_DIR}/resource-intelligence-summary.md"
RESOURCES="${ASSET_DIR}/resources.yaml"
SOURCES="${ASSET_DIR}/sources.md"
PACK="${ASSET_DIR}/resource-pack.md"

required_files=(
  "${PACK}"
  "${SOURCES}"
  "${ASSET_DIR}/constraints.md"
  "${ASSET_DIR}/domain-notes.md"
  "${ASSET_DIR}/open-questions.md"
  "${RESOURCES}"
  "${SUMMARY}"
)

for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || { echo "Missing required artifact: ${file}" >&2; exit 2; }
done

required_headings=(
  "^## Problem Context$"
  "^## Relevant Documents/Data$"
  "^## Constraints$"
  "^## Assumptions$"
  "^## Open Questions$"
  "^## Domain Notes$"
  "^## Source Paths$"
)

for pattern in "${required_headings[@]}"; do
  grep -Eq "$pattern" "$PACK" || { echo "Missing required heading in resource-pack.md: ${pattern}" >&2; exit 3; }
done

if ! grep -Eq '^[0-9]+\. |^- ' "$SOURCES" && ! grep -Eq 'no_(external_)?sources:[[:space:]]*true' "$RESOURCES"; then
  echo "sources.md must contain at least one source entry or resources.yaml must declare no_external_sources: true" >&2
  exit 4
fi

source_count="$(grep -Ec '^[[:space:]]*-[[:space:]]+id:' "$RESOURCES" || true)"
if [[ "$source_count" -gt 0 ]]; then
  for key in origin license_access retrieval_date canonical_storage_path duplicate_status status; do
    key_count="$(grep -Ec "^[[:space:]]+${key}:" "$RESOURCES" || true)"
    if [[ "$key_count" -lt "$source_count" ]]; then
      echo "resources.yaml must record ${key} for every source entry" >&2
      exit 12
    fi
  done

  unavailable_count="$(grep -Ec '^[[:space:]]+status:[[:space:]]*source_unavailable' "$RESOURCES" || true)"
  if [[ "$unavailable_count" -gt 0 ]]; then
    fallback_count="$(grep -Ec '^[[:space:]]+fallback_evidence:' "$RESOURCES" || true)"
    if [[ "$fallback_count" -lt "$unavailable_count" ]]; then
      echo "resources.yaml must record fallback_evidence for each source_unavailable entry" >&2
      exit 13
    fi
  fi
fi

decision="$(grep -E '^\- `user_decision`:' "$SUMMARY" | sed 's/.*: *//' | tr -d '[:space:]')"
decision="${decision//\`/}"
if [[ "$decision" != "pause_and_revise" && "$decision" != "continue_to_planning" ]]; then
  echo "resource-intelligence-summary.md must set user_decision to pause_and_revise or continue_to_planning" >&2
  exit 5
fi

summary_wrk_id="$(grep -E '^\- `wrk_id`:' "$SUMMARY" | sed 's/.*: *//' | tr -d '[:space:]')"
resources_wrk_id="$(grep -E '^wrk_id:' "$RESOURCES" | sed 's/.*: *//' | tr -d '[:space:]')"
if [[ "$summary_wrk_id" != "$WRK_ID" ]]; then
  echo "resource-intelligence-summary.md wrk_id does not match requested WRK_ID: ${summary_wrk_id}" >&2
  exit 9
fi
if [[ "$resources_wrk_id" != "$WRK_ID" ]]; then
  echo "resources.yaml wrk_id does not match requested WRK_ID: ${resources_wrk_id}" >&2
  exit 10
fi

p1_block="$(awk '
  /^\- `top_p1_gaps`:/ {in_block=1; next}
  in_block && /^\- `/ {in_block=0}
  in_block {print}
' "$SUMMARY")"
p1_has_real_gap=0
while IFS= read -r line; do
  stripped="$(echo "$line" | sed 's/^[[:space:]]*//')"
  [[ -z "$stripped" ]] && continue
  if [[ "$stripped" =~ ^-[[:space:]]+none$ ]]; then
    continue
  fi
  if [[ "$stripped" =~ ^-[[:space:]]+ ]]; then
    p1_has_real_gap=1
    break
  fi
done <<< "$p1_block"

if [[ "$decision" == "continue_to_planning" && "$p1_has_real_gap" -eq 1 ]]; then
  echo "resource-intelligence-summary.md cannot continue_to_planning while top_p1_gaps contains unresolved items" >&2
  exit 11
fi

legal_ref="$(grep -E '^\- `legal_scan_ref`:' "$SUMMARY" | sed 's/.*: *//')"
legal_ref="${legal_ref//\`/}"
legal_ref="${legal_ref#"${legal_ref%%[![:space:]]*}"}"
legal_ref="${legal_ref%"${legal_ref##*[![:space:]]}"}"
if [[ -z "$legal_ref" ]]; then
  echo "resource-intelligence-summary.md must set legal_scan_ref" >&2
  exit 6
fi
if [[ "$legal_ref" != "not_applicable" ]]; then
  [[ -f "${ROOT}/${legal_ref}" ]] || { echo "legal_scan_ref does not resolve to a file: ${legal_ref}" >&2; exit 7; }
fi

index_ref="$(grep -E '^\- `indexing_ref`:' "$SUMMARY" | sed 's/.*: *//')"
index_ref="${index_ref//\`/}"
index_ref="${index_ref#"${index_ref%%[![:space:]]*}"}"
index_ref="${index_ref%"${index_ref##*[![:space:]]}"}"
if [[ -n "$index_ref" && "$index_ref" != "not_applicable" ]]; then
  [[ -f "${ROOT}/${index_ref}" ]] || { echo "indexing_ref does not resolve to a file: ${index_ref}" >&2; exit 8; }
fi

echo "Resource Intelligence artifacts valid for ${WRK_ID}"
