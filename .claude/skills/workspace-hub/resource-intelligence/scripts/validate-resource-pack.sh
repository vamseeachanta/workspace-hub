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

resolve_repo_ref() {
  local ref="$1"
  local resolved
  resolved="$(realpath -m "${ROOT}/${ref}")"
  if [[ "$resolved" != "${ROOT}" && "$resolved" != "${ROOT}/"* ]]; then
    echo "Reference must resolve inside repository root: ${ref}" >&2
    return 1
  fi
  printf '%s\n' "$resolved"
}

normalize_yaml_scalar() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  if [[ "$value" == \"*\" && "$value" == *\" ]]; then
    value="${value:1:${#value}-2}"
  fi
  if [[ "$value" == \'*\' && "$value" == *\' ]]; then
    value="${value:1:${#value}-2}"
  fi
  printf '%s\n' "$value"
}

get_registry_field() {
  local source_id="$1"
  local field="$2"
  awk -v sid="$source_id" -v wanted="$field" '
    /^[[:space:]]*-[[:space:]]+source_id:[[:space:]]*/ {
      current=$0
      sub(/^[[:space:]]*-[[:space:]]+source_id:[[:space:]]*/, "", current)
      in_target=(current == sid)
      next
    }
    in_target && /^[[:space:]]+[A-Za-z0-9_]+:[[:space:]]*/ {
      line=$0
      sub(/^[[:space:]]+/, "", line)
      key=line
      sub(/:.*/, "", key)
      if (key == wanted) {
        sub(/^[^:]+:[[:space:]]*/, "", line)
        print line
        exit
      }
    }
  ' "$registry_file"
}

path_matches_registry() {
  local actual="$1"
  local expected="$2"
  if [[ "$expected" == *"<workstation>"* ]]; then
    local prefix="${expected%%<workstation>*}"
    local suffix="${expected#*<workstation>}"
    [[ "$actual" == "$prefix"*"$suffix" ]] || return 1
    local after_prefix="${actual#"$prefix"}"
    local workstation_segment="${after_prefix%%"$suffix"*}"
    [[ -n "$workstation_segment" && "$workstation_segment" != */* ]] || return 1
    local base="${prefix}${workstation_segment}${suffix}"
    [[ "$actual" == "$base" || "$actual" == "$base"/* ]]
    return
  fi
  [[ "$actual" == "$expected" || "$actual" == "$expected"/* ]]
}

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

if ! grep -Eq '^[0-9]+\. |^- ' "$SOURCES"; then
  echo "sources.md must contain at least one source entry" >&2
  exit 4
fi

no_external_sources_flag=0
if grep -Eq '^[[:space:]]*no_external_sources:[[:space:]]*true' "$RESOURCES"; then
  no_external_sources_flag=1
fi

if grep -Eq '^[[:space:]]*sources:[[:space:]]*$' "$RESOURCES"; then
  scalar_source_count="$(grep -Ec '^[[:space:]]*-[[:space:]]+[^:]+$' "$RESOURCES" || true)"
  if [[ "$scalar_source_count" -gt 0 ]]; then
    echo "resources.yaml sources[] must use structured mappings with id/origin/license_access/retrieval_date/canonical_storage_path/duplicate_status/status" >&2
    exit 14
  fi
fi

source_count="$(grep -Ec '^[[:space:]]*-[[:space:]]+[a-z_]+:' "$RESOURCES" || true)"
if [[ "$source_count" -eq 0 ]]; then
  echo "resources.yaml must contain at least one structured source entry" >&2
  exit 15
fi

if [[ "$source_count" -gt 0 ]]; then
  registry_file="${ROOT}/data/document-index/mounted-source-registry.yaml"
  registry_ids=""
  if [[ -f "$registry_file" ]]; then
    registry_ids="$(grep -E '^[[:space:]]*-[[:space:]]+source_id:|^[[:space:]]+source_id:' "$registry_file" | sed 's/.*: *//')"
  fi

  current_source_id=""
  current_source_type=""
  current_origin=""
  current_license_access=""
  current_retrieval_date=""
  current_storage_path=""
  current_duplicate_status=""
  current_status=""
  current_fallback=""
  current_seen=0

  validate_current_source() {
    [[ "$current_seen" -eq 1 ]] || return 0
    for value_name in current_source_id current_source_type current_origin current_license_access current_retrieval_date current_storage_path current_duplicate_status current_status; do
      if [[ -z "${!value_name}" ]]; then
        echo "resources.yaml must record ${value_name#current_} for every source entry" >&2
        exit 12
      fi
    done
    if [[ "$current_source_type" != "registry" && "$current_source_type" != "additive" ]]; then
      echo "resources.yaml source_type must be registry or additive for every source entry" >&2
      exit 17
    fi
    if [[ "$current_source_type" == "registry" ]]; then
      if [[ ! -f "$registry_file" ]]; then
        echo "mounted-source-registry.yaml is required when resources.yaml declares registry sources" >&2
        exit 21
      fi
      if [[ -z "$registry_ids" ]]; then
        echo "mounted-source-registry.yaml must contain at least one source_id when resources.yaml declares registry sources" >&2
        exit 22
      fi
      if ! grep -Fxq "$current_source_id" <<< "$registry_ids"; then
        echo "resources.yaml registry source id is not present in mounted-source-registry.yaml: ${current_source_id}" >&2
        exit 16
      fi
      registry_mount_root="$(get_registry_field "$current_source_id" mount_root)"
      registry_mount_root_example="$(get_registry_field "$current_source_id" mount_root_example)"
      registry_environment_specific="$(get_registry_field "$current_source_id" environment_specific)"
      path_prefix="$registry_mount_root"
      if [[ "$registry_environment_specific" == "true" && -n "$registry_mount_root_example" ]]; then
        path_prefix="$registry_mount_root_example"
      fi
      if [[ -n "$path_prefix" && "$path_prefix" != "<resolved via env:"* ]]; then
        if ! path_matches_registry "$current_origin" "$path_prefix"; then
          echo "resources.yaml registry source origin must align with mounted-source-registry.yaml mount root: ${current_source_id}" >&2
          exit 26
        fi
        if ! path_matches_registry "$current_storage_path" "$path_prefix"; then
          echo "resources.yaml registry source canonical_storage_path must align with mounted-source-registry.yaml mount root: ${current_source_id}" >&2
          exit 27
        fi
      fi
    fi
    if [[ "$current_status" != "available" && "$current_status" != "source_unavailable" ]]; then
      echo "resources.yaml status must be available or source_unavailable for every source entry" >&2
      exit 29
    fi
    if [[ "$no_external_sources_flag" -eq 1 && "$current_source_type" == "additive" ]]; then
      echo "resources.yaml cannot declare additive sources when no_external_sources is true" >&2
      exit 28
    fi
    if [[ "$current_status" == "source_unavailable" && -z "$current_fallback" ]]; then
      echo "resources.yaml must record fallback_evidence for each source_unavailable entry" >&2
      exit 13
    fi
  }

  assign_source_field() {
    local key="$1"
    local value="$2"
    value="$(normalize_yaml_scalar "$value")"
    case "$key" in
      id) current_source_id="$value" ;;
      source_type) current_source_type="$value" ;;
      origin) current_origin="$value" ;;
      license_access) current_license_access="$value" ;;
      retrieval_date) current_retrieval_date="$value" ;;
      canonical_storage_path) current_storage_path="$value" ;;
      duplicate_status) current_duplicate_status="$value" ;;
      status) current_status="$value" ;;
      fallback_evidence) current_fallback="$value" ;;
    esac
  }

  # Scope parsing to the 'sources:' block only — stop at next top-level key
  in_sources=0
  while IFS= read -r line; do
    # Detect top-level keys (no leading spaces)
    if [[ "$line" =~ ^([a-z_]+):[[:space:]]* ]]; then
      [[ "${BASH_REMATCH[1]}" == "sources" ]] && in_sources=1 || in_sources=0
      continue
    fi
    [[ "$in_sources" -eq 0 ]] && continue
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+([a-z_]+):[[:space:]]*(.*)$ ]]; then
      validate_current_source
      first_key="${BASH_REMATCH[1]}"
      first_value="${BASH_REMATCH[2]}"
      current_source_id=""
      current_source_type=""
      current_origin=""
      current_license_access=""
      current_retrieval_date=""
      current_storage_path=""
      current_duplicate_status=""
      current_status=""
      current_fallback=""
      current_seen=1
      assign_source_field "$first_key" "$first_value"
      continue
    fi
    [[ "$current_seen" -eq 0 ]] && continue
    if [[ "$line" =~ ^[[:space:]]+([a-z_]+):[[:space:]]*(.*)$ ]]; then
      assign_source_field "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    fi
  done < "$RESOURCES"
  validate_current_source

  # Extract source ids from within the 'sources:' block only
  declared_sources=()
  in_sources_block=0
  while IFS= read -r line; do
    if [[ "$line" =~ ^([a-z_]+): ]]; then
      [[ "${BASH_REMATCH[1]}" == "sources" ]] && in_sources_block=1 || in_sources_block=0
      continue
    fi
    [[ "$in_sources_block" -eq 0 ]] && continue
    if [[ "$line" =~ ^[[:space:]]+id:[[:space:]]*(.+)$ ]]; then
      source_id="$(normalize_yaml_scalar "${BASH_REMATCH[1]}")"
      [[ -n "$source_id" ]] && declared_sources+=("$source_id")
    fi
  done < "$RESOURCES"

  for sid in "${declared_sources[@]}"; do
    if ! grep -Fq "$sid" "$SOURCES"; then
      echo "sources.md must reference each resources.yaml source id: missing ${sid}" >&2
      exit 33
    fi
  done
fi

for field in wrk_id summary top_p1_gaps top_p2_gaps top_p3_gaps user_decision reviewed_at reviewer legal_scan_ref indexing_ref; do
  if ! grep -Eq "^\- \`${field}\`:" "$SUMMARY"; then
    echo "resource-intelligence-summary.md is missing required field: ${field}" >&2
    exit 18
  fi
  field_count="$(grep -Ec "^\- \`${field}\`:" "$SUMMARY" || true)"
  if [[ "$field_count" -ne 1 ]]; then
    echo "resource-intelligence-summary.md must record ${field} exactly once" >&2
    exit 23
  fi
done

for scalar_field in summary reviewed_at reviewer; do
  scalar_value="$(grep -E "^\- \`${scalar_field}\`:" "$SUMMARY" | sed 's/.*: *//')"
  scalar_value="${scalar_value//\`/}"
  scalar_value="$(normalize_yaml_scalar "$scalar_value")"
  if [[ -z "$scalar_value" ]]; then
    echo "resource-intelligence-summary.md must set ${scalar_field} to a non-empty value" >&2
    exit 32
  fi
done

decision="$(grep -E '^\- `user_decision`:' "$SUMMARY" | sed 's/.*: *//')"
decision="${decision//\`/}"
decision="$(normalize_yaml_scalar "$decision")"
if [[ "$decision" != "pause_and_revise" && "$decision" != "continue_to_planning" ]]; then
  echo "resource-intelligence-summary.md must set user_decision to pause_and_revise or continue_to_planning" >&2
  exit 5
fi

summary_wrk_id="$(grep -E '^\- `wrk_id`:' "$SUMMARY" | sed 's/.*: *//')"
summary_wrk_id="${summary_wrk_id//\`/}"
summary_wrk_id="$(normalize_yaml_scalar "$summary_wrk_id")"
resources_wrk_id="$(grep -E '^wrk_id:' "$RESOURCES" | sed 's/.*: *//')"
resources_wrk_id="$(normalize_yaml_scalar "$resources_wrk_id")"
if [[ "$summary_wrk_id" != "$WRK_ID" ]]; then
  echo "resource-intelligence-summary.md wrk_id does not match requested WRK_ID: ${summary_wrk_id}" >&2
  exit 9
fi
if [[ "$resources_wrk_id" != "$WRK_ID" ]]; then
  echo "resources.yaml wrk_id does not match requested WRK_ID: ${resources_wrk_id}" >&2
  exit 10
fi

p_extract_gap_block() {
  local field="$1"
  awk -v target="$field" '
    $0 ~ "^- `" target "`:" {in_block=1; next}
    in_block && /^- `/ {in_block=0}
    in_block {print}
  ' "$SUMMARY"
}

ensure_gap_block_shape() {
  local field="$1"
  local inline
  inline="$(grep -E "^\- \`${field}\`:" "$SUMMARY" | sed 's/.*: *//')"
  inline="${inline//\`/}"
  inline="${inline#"${inline%%[![:space:]]*}"}"
  inline="${inline%"${inline##*[![:space:]]}"}"
  if [[ -n "$inline" ]]; then
    echo "resource-intelligence-summary.md must record ${field} as a multiline bullet list" >&2
    exit 20
  fi
}

ensure_gap_block_shape top_p1_gaps
ensure_gap_block_shape top_p2_gaps
ensure_gap_block_shape top_p3_gaps

p1_block="$(p_extract_gap_block top_p1_gaps)"
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
legal_ref="$(normalize_yaml_scalar "$legal_ref")"
if [[ -z "$legal_ref" ]]; then
  echo "resource-intelligence-summary.md must set legal_scan_ref" >&2
  exit 6
fi
if [[ "$legal_ref" != "not_applicable" ]]; then
  legal_path="$(resolve_repo_ref "$legal_ref")" || exit 24
  [[ -f "$legal_path" ]] || { echo "legal_scan_ref does not resolve to a file: ${legal_ref}" >&2; exit 7; }
  [[ -s "$legal_path" ]] || { echo "legal_scan_ref resolves to an empty file: ${legal_ref}" >&2; exit 19; }
fi

index_ref="$(grep -E '^\- `indexing_ref`:' "$SUMMARY" | sed 's/.*: *//')"
index_ref="${index_ref//\`/}"
index_ref="$(normalize_yaml_scalar "$index_ref")"
if [[ -n "$index_ref" && "$index_ref" != "not_applicable" ]]; then
  index_path="$(resolve_repo_ref "$index_ref")" || exit 25
  [[ -f "$index_path" ]] || { echo "indexing_ref does not resolve to a file: ${index_ref}" >&2; exit 8; }
  index_rel="${index_path#${ROOT}/}"
  if [[ "$index_rel" != data/document-index/* ]]; then
    echo "indexing_ref must point to a document-index artifact inside data/document-index/: ${index_ref}" >&2
    exit 30
  fi
  if [[ "$index_rel" == "data/document-index/registry.yaml" ]]; then
    echo "indexing_ref must point to an indexing output artifact, not the static registry: ${index_ref}" >&2
    exit 31
  fi
fi

echo "Resource Intelligence artifacts valid for ${WRK_ID}"
