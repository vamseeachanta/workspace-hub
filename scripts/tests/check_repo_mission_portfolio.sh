#!/usr/bin/env bash
# check_repo_mission_portfolio.sh — validate docs/REPO_MISSION_PORTFOLIO.md against
# data/document-index/repo-portfolio-inventory.yaml.
#
# Implements acceptance criteria C1-C13 from
# docs/plans/2026-05-02-issue-2533-mission-portfolio.md (rev-3).
#
# Modes:
#   --generate    Regenerate docs/REPO_MISSION_PORTFOLIO.md from the YAML registry.
#                 (YAML is hand-edited source-of-truth; markdown is the projection.)
#   --generate-to <path>
#                 Regenerate to a given path instead of the canonical location
#                 (used by C13 parity check).
#   (no flag)     Validate C1-C13 and exit 0 on pass, non-zero with itemized failures.
#
# Dependencies: Mike Farah Go-binary yq (NOT the Python wrapper). The script searches
# common install paths; if not found, exits with install instructions.

set -euo pipefail

# ---------------------------------------------------------------------------
# Locate workspace-hub root
# ---------------------------------------------------------------------------
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

YAML_PATH="data/document-index/repo-portfolio-inventory.yaml"
MD_PATH="docs/REPO_MISSION_PORTFOLIO.md"

# ---------------------------------------------------------------------------
# Locate yq (Mike Farah Go-binary)
# ---------------------------------------------------------------------------
find_yq() {
  local candidate
  for candidate in yq /usr/local/bin/yq /usr/bin/yq "$HOME/.local/bin/yq" "$HOME/bin/yq"; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" --version 2>&1 | grep -q 'mikefarah'; then
        echo "$candidate"
        return 0
      fi
    fi
  done
  return 1
}

YQ="$(find_yq || true)"
if [ -z "$YQ" ]; then
  cat >&2 <<EOF
ERROR: Mike Farah yq (Go binary) is required but not found.

Install one of these ways:
  - Ubuntu/Debian:  sudo apt install yq
  - macOS:          brew install yq
  - Direct binary:  curl -fsSL -o ~/.local/bin/yq \\
                      https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 \\
                      && chmod +x ~/.local/bin/yq

NOTE: The Python "yq" wrapper (pip install yq) has different syntax and is NOT
      compatible with this script. Verify with: yq --version (must show "mikefarah").
EOF
  exit 2
fi

# ---------------------------------------------------------------------------
# C1: YAML and markdown both exist + non-empty
# ---------------------------------------------------------------------------
[ -s "$YAML_PATH" ] || { echo "FAIL C1: $YAML_PATH missing or empty" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------
markdown_escape() {
  # Pipe chars break markdown tables. Escape them.
  sed 's/|/\\|/g'
}

generate_markdown() {
  local target="${1:-$MD_PATH}"
  local count
  count=$("$YQ" '.repos | length' "$YAML_PATH")

  {
    cat <<EOF
# Repo Portfolio Mission

> Source-of-truth registry: \`data/document-index/repo-portfolio-inventory.yaml\`
> Validator + generator: \`scripts/tests/check_repo_mission_portfolio.sh\`
> Issue: [vamseeachanta/workspace-hub#2533](https://github.com/vamseeachanta/workspace-hub/issues/2533)
> Plan: \`docs/plans/2026-05-02-issue-2533-mission-portfolio.md\`
>
> **DO NOT hand-edit this file.** It is regenerated from the YAML registry by
> \`scripts/tests/check_repo_mission_portfolio.sh --generate\`.
> Edits go to the YAML; re-run \`--generate\` to refresh the table.

This artifact answers four questions for any agent or human picking up workspace-hub work:

1. **What is this repo for?** — mission paragraph grounded in the strongest available in-repo source
2. **What work belongs here?** — \`routing_belongs_here\` rule
3. **What work should route elsewhere?** — \`routing_route_elsewhere\` rule
4. **Is the repo active, support, archive, or migrating-out?** — \`tier\` and \`inventory_status\` fields

**Coverage:** ${count} records (Tier-1, Tier-2, Tier-3/support/archive, post-plan additions, and inventory-drift entries).

For Tier-1 routing — issue-type → repo → canonical path matrix — see [\`docs/ROUTING_INDEX.md\`](ROUTING_INDEX.md).
For ecosystem onboarding — owner, machines, providers, GTM loop — see [\`docs/BUSINESS_BRAIN.md\`](BUSINESS_BRAIN.md).

---

## Portfolio Table

| Repo | Tier | Mission | Source | Belongs here when | Route elsewhere when | Overlap notes | Status | Notes |
|---|---|---|---|---|---|---|---|---|
EOF

    local i
    for i in $(seq 0 $((count - 1))); do
      local repo tier mission source_path bh re overlap inv notes
      repo=$("$YQ" ".repos[$i].repo" "$YAML_PATH" | markdown_escape)
      tier=$("$YQ" ".repos[$i].tier" "$YAML_PATH" | markdown_escape)
      mission=$("$YQ" ".repos[$i].mission" "$YAML_PATH" | tr '\n' ' ' | sed 's/  */ /g; s/ $//' | markdown_escape)
      source_path=$("$YQ" ".repos[$i].source_path" "$YAML_PATH" | markdown_escape)
      bh=$("$YQ" ".repos[$i].routing_belongs_here" "$YAML_PATH" | tr '\n' ' ' | sed 's/  */ /g; s/ $//' | markdown_escape)
      re=$("$YQ" ".repos[$i].routing_route_elsewhere" "$YAML_PATH" | tr '\n' ' ' | sed 's/  */ /g; s/ $//' | markdown_escape)
      overlap=$("$YQ" ".repos[$i].overlap_notes" "$YAML_PATH" | tr '\n' ' ' | sed 's/  */ /g; s/ $//' | markdown_escape)
      inv=$("$YQ" ".repos[$i].inventory_status" "$YAML_PATH" | markdown_escape)
      notes=$("$YQ" ".repos[$i].notes" "$YAML_PATH" | tr '\n' ' ' | sed 's/  */ /g; s/ $//' | markdown_escape)
      printf '| %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' \
        "$repo" "$tier" "$mission" "$source_path" "$bh" "$re" "$overlap" "$inv" "$notes"
    done

    cat <<EOF

---

## How to keep this current

1. **Edit the YAML, not the markdown.** Hand-editing the markdown is a no-op — the next
   \`--generate\` will overwrite it. The YAML registry at \`data/document-index/repo-portfolio-inventory.yaml\`
   is the canonical source-of-truth.

2. **Re-run the generator after edits.**
   \`\`\`bash
   scripts/tests/check_repo_mission_portfolio.sh --generate
   \`\`\`

3. **Run validation before commit.**
   \`\`\`bash
   scripts/tests/check_repo_mission_portfolio.sh
   \`\`\`
   Exit 0 means C1-C13 all pass. Non-zero output names the failing criterion.

4. **When a new repo is added to the workspace-hub portfolio:** add a record to the YAML with
   all schema fields, run \`--generate\`, run the validator, and commit both files
   plus this generated markdown.

5. **When BUSINESS_BRAIN.md classification changes:** update the corresponding
   \`tier\` field in the YAML, regenerate, and validate.

For the symmetric-overlap rule (C7) and Tier-1 keyword set (C5), see the validator
script's inline checks — those rules are mechanically enforced.
EOF
  } > "$target"
}

# ---------------------------------------------------------------------------
# --generate / --generate-to dispatch
# ---------------------------------------------------------------------------
if [ "${1:-}" = "--generate" ]; then
  generate_markdown "$MD_PATH"
  echo "Wrote $MD_PATH from $YAML_PATH"
  exit 0
fi
if [ "${1:-}" = "--generate-to" ]; then
  target="${2:?Usage: $0 --generate-to <path>}"
  generate_markdown "$target"
  echo "Wrote $target from $YAML_PATH"
  exit 0
fi

# ---------------------------------------------------------------------------
# Validation mode — C1 through C13
# ---------------------------------------------------------------------------
[ -s "$MD_PATH" ] || { echo "FAIL C1: $MD_PATH missing or empty (run --generate first)" >&2; exit 1; }

fails=()

# --- C2: ≥ 23 records covering all local immediate-child repos ---
record_count=$("$YQ" '.repos | length' "$YAML_PATH")
if [ "$record_count" -lt 23 ]; then
  fails+=("C2: YAML has $record_count records; expected ≥ 23")
fi

# Cross-check: every local immediate-child repo (excluding workspace-hub root, which
# is a record with repo: workspace-hub) is named in the YAML.
local_repos=()
while IFS= read -r d; do
  d="${d#./}"
  d="${d%/.git}"
  [ "$d" = "." ] && continue
  [ "$d" = ".git" ] && continue
  local_repos+=("$d")
done < <(find . -maxdepth 2 -name .git -type d 2>/dev/null | sort)

yaml_repos=$("$YQ" '.repos[] | .repo' "$YAML_PATH")
for r in "${local_repos[@]}"; do
  if ! grep -Fxq "$r" <<<"$yaml_repos"; then
    fails+=("C2: local repo \"$r\" not present in YAML registry")
  fi
done
# workspace-hub special case
if ! grep -Fxq "workspace-hub" <<<"$yaml_repos"; then
  fails+=("C2: workspace-hub record not present in YAML registry")
fi

# --- C3: every record has all required fields, non-empty ---
required_fields=(repo tier mission source_path routing_belongs_here routing_route_elsewhere overlap_notes inventory_status notes)
for i in $(seq 0 $((record_count - 1))); do
  repo=$("$YQ" ".repos[$i].repo" "$YAML_PATH")
  for f in "${required_fields[@]}"; do
    v=$("$YQ" ".repos[$i].$f" "$YAML_PATH")
    if [ -z "$v" ] || [ "$v" = "null" ]; then
      fails+=("C3: record[$i] ($repo) missing required field: $f")
    fi
  done
done

# --- C4: source_path resolves to a real file under workspace-hub, OR is "none",
#         OR is "legacy_source:<path>" pointing to a real file. ---
for i in $(seq 0 $((record_count - 1))); do
  repo=$("$YQ" ".repos[$i].repo" "$YAML_PATH")
  sp=$("$YQ" ".repos[$i].source_path" "$YAML_PATH")
  case "$sp" in
    none)
      mission=$("$YQ" ".repos[$i].mission" "$YAML_PATH")
      if ! grep -q "REVIEW_REQUIRED" <<<"$mission" \
         && ! grep -q "not present in local immediate-child" <<<"$mission" \
         && ! grep -q "not locally present" <<<"$mission" \
         && ! grep -q "Mentioned in" <<<"$mission"; then
        fails+=("C4: $repo has source_path=none but mission lacks REVIEW_REQUIRED or not-present rationale")
      fi
      ;;
    legacy_source:*)
      path="${sp#legacy_source:}"
      if [ ! -f "$path" ]; then
        fails+=("C4: $repo legacy_source path does not resolve: $path")
      fi
      ;;
    *)
      if [ ! -f "$sp" ]; then
        fails+=("C4: $repo source_path does not resolve: $sp")
      fi
      ;;
  esac
done

# --- C5: Tier-1 records carry tier=tier-1 AND mission contains ≥ 2 of the per-repo
#         keyword set (rev-3 spec). ---
check_keywords() {
  local repo="$1"
  shift
  local required="$1"
  shift
  local mission
  mission=$("$YQ" ".repos[] | select(.repo == \"$repo\") | .mission" "$YAML_PATH" | tr '[:upper:]' '[:lower:]')
  local tier
  tier=$("$YQ" ".repos[] | select(.repo == \"$repo\") | .tier" "$YAML_PATH")
  [ "$tier" = "tier-1" ] || fails+=("C5: $repo is not tier=tier-1 (got: $tier)")
  local hits=0
  for kw in "$@"; do
    local kw_lc
    kw_lc=$(echo "$kw" | tr '[:upper:]' '[:lower:]')
    if grep -q -- "$kw_lc" <<<"$mission"; then
      hits=$((hits + 1))
    fi
  done
  if [ "$hits" -lt "$required" ]; then
    fails+=("C5: $repo mission contains only $hits keyword hits (need ≥ $required): looked for one of: $*")
  fi
}
check_keywords workspace-hub 2 "portfolio" "control plane" "harness" "governance" "cross-repo"
check_keywords digitalmodel 2 "numerical" "engineering calculation" "orcawave" "orcaflex" "hydrodynamics" "solver"
check_keywords assetutilities 2 "shared" "python utilities" "engineering" "library"
check_keywords aceengineer-website 2 "public" "website" "marketing" "demos" "calculators" "deployment"

# --- C6: Tier-1 records reference no contract that #2460-#2465 closed differently. ---
# Embedded static constants - the Tier-1 four-repo set per ROUTING_INDEX.md.
tier1_expected=(workspace-hub digitalmodel assetutilities aceengineer-website)
tier1_actual=$("$YQ" '.repos[] | select(.tier == "tier-1") | .repo' "$YAML_PATH" | sort)
tier1_expected_sorted=$(printf '%s\n' "${tier1_expected[@]}" | sort)
if [ "$tier1_actual" != "$tier1_expected_sorted" ]; then
  fails+=("C6: Tier-1 set mismatch with ROUTING_INDEX.md/#2460. Expected: $(echo $tier1_expected_sorted | tr '\n' ' '). Got: $(echo $tier1_actual | tr '\n' ' ')")
fi

# --- C7: Symmetric overlap_notes for every #2533 body overlap pair. ---
declare -a pairs=(
  "investments:assethold"
  "client_projects:acma-projects"
  "client_projects:seanation"
  "client_projects:saipem"
  "client_projects:frontierdeepwater"
  "client_projects:doris"
  "aceengineer-website:aceengineer-strategy"
)
check_symmetry() {
  local a="$1" b="$2"
  local a_notes b_notes
  a_notes=$("$YQ" ".repos[] | select(.repo == \"$a\") | .overlap_notes" "$YAML_PATH")
  b_notes=$("$YQ" ".repos[] | select(.repo == \"$b\") | .overlap_notes" "$YAML_PATH")
  if ! grep -q -- "$b" <<<"$a_notes"; then
    fails+=("C7: $a overlap_notes must name $b")
  fi
  if ! grep -q -- "$a" <<<"$b_notes"; then
    fails+=("C7: $b overlap_notes must name $a")
  fi
}
# Tier-1 ↔ per-repo execution docs pair from issue body
check_symmetry workspace-hub digitalmodel
check_symmetry assetutilities digitalmodel
check_symmetry digitalmodel acma-projects
check_symmetry digitalmodel seanation
check_symmetry digitalmodel saipem
check_symmetry digitalmodel frontierdeepwater
for pair in "${pairs[@]}"; do
  a="${pair%%:*}"
  b="${pair##*:}"
  check_symmetry "$a" "$b"
done

# --- C8: discovery anchors each contain a link to REPO_MISSION_PORTFOLIO.md ---
for anchor in docs/BUSINESS_BRAIN.md docs/ROUTING_INDEX.md docs/README.md; do
  if ! grep -q "REPO_MISSION_PORTFOLIO" "$anchor" 2>/dev/null; then
    fails+=("C8: $anchor does not link to REPO_MISSION_PORTFOLIO.md")
  fi
done

# --- C9: inventory-drift records exist for pdf-large-reader, heavyequipemnt-rag, simpledigitalmarketing ---
for r in pdf-large-reader heavyequipemnt-rag simpledigitalmarketing; do
  status=$("$YQ" ".repos[] | select(.repo == \"$r\") | .inventory_status" "$YAML_PATH")
  if [ "$status" != "not-present-locally" ]; then
    fails+=("C9: $r missing or wrong inventory_status (expected not-present-locally, got: $status)")
  fi
done

# --- C10: assethold notes carries the samdansk2 ownership transfer fact ---
assethold_notes=$("$YQ" '.repos[] | select(.repo == "assethold") | .notes' "$YAML_PATH")
for token in "samdansk2" "ownership" "local origin may be stale"; do
  if ! grep -q -- "$token" <<<"$assethold_notes"; then
    fails+=("C10: assethold notes missing token: $token")
  fi
done

# --- C11: aceengineer-website route_elsewhere mentions aceengineer-strategy;
#         aceengineer-strategy notes flag it as strategic-copy authority. ---
ace_web_re=$("$YQ" '.repos[] | select(.repo == "aceengineer-website") | .routing_route_elsewhere' "$YAML_PATH")
if ! grep -q "aceengineer-strategy" <<<"$ace_web_re"; then
  fails+=("C11: aceengineer-website routing_route_elsewhere must mention aceengineer-strategy")
fi
ace_strat_notes=$("$YQ" '.repos[] | select(.repo == "aceengineer-strategy") | .notes' "$YAML_PATH")
ace_strat_overlap=$("$YQ" '.repos[] | select(.repo == "aceengineer-strategy") | .overlap_notes' "$YAML_PATH")
if ! grep -q "strategic-copy authority" <<<"$ace_strat_notes$ace_strat_overlap"; then
  fails+=("C11: aceengineer-strategy must be flagged as strategic-copy authority in notes or overlap_notes")
fi

# --- C12: no record uses .agent-os/product/mission.md as source_path when AGENTS.md
#         or README.md or docs/README.md exists in the same repo. ---
for i in $(seq 0 $((record_count - 1))); do
  repo=$("$YQ" ".repos[$i].repo" "$YAML_PATH")
  sp=$("$YQ" ".repos[$i].source_path" "$YAML_PATH")
  case "$sp" in
    legacy_source:*)
      # Build repo-relative root
      if [ "$repo" = "workspace-hub" ]; then
        repo_root="."
      else
        repo_root="$repo"
      fi
      # Per CONTROL_PLANE_CONTRACT.md, only the AGENTS.md presence with a mission body
      # disqualifies legacy_source. Pure-pointer AGENTS.md is acceptable to skip.
      # Heuristic: if AGENTS.md contains a "purpose:" frontmatter line, that's a mission body.
      if [ -f "$repo_root/AGENTS.md" ] && grep -q "^purpose:" "$repo_root/AGENTS.md" 2>/dev/null; then
        fails+=("C12: $repo uses legacy_source but $repo_root/AGENTS.md has a purpose: frontmatter")
      fi
      # If README.md exists with non-trivial body (more than 2 non-empty lines), legacy fallback should not be used.
      if [ -f "$repo_root/README.md" ]; then
        readme_lines=$(grep -c -v '^[[:space:]]*$' "$repo_root/README.md" 2>/dev/null || echo 0)
        if [ "$readme_lines" -gt 2 ]; then
          fails+=("C12: $repo uses legacy_source but $repo_root/README.md has substantive content ($readme_lines non-empty lines)")
        fi
      fi
      ;;
  esac
done

# --- C13: regenerate markdown and diff against committed file ---
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
generate_markdown "$tmp"
if ! diff -q "$tmp" "$MD_PATH" >/dev/null 2>&1; then
  fails+=("C13: $MD_PATH does not match YAML projection — run --generate to refresh")
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [ "${#fails[@]}" -eq 0 ]; then
  echo "PASS — C1-C13 all green ($record_count records, $(echo "$tier1_actual" | wc -l) Tier-1)"
  exit 0
fi

echo "FAIL — ${#fails[@]} criterion violation(s):" >&2
for f in "${fails[@]}"; do
  echo "  - $f" >&2
done
exit 1
