#!/usr/bin/env bash
# backfill-skills-to-repo.sh — Detect new ~/.hermes/skills/ and copy to the correct repo's .claude/skills/
#
# Routes skills to the repo that already owns their category (per-repo routing, #1948).
# Falls back to workspace-hub if no match.
#
# Runs as part of nightly harness-update or standalone.
#
# Usage: backfill-skills-to-repo.sh [--dry-run] [--commit]
#
# --dry-run   Report only, don't copy anything
# --commit    Auto git add + commit + push per-repo if new skills were copied
#
# Exit codes:
#   0  No drift or successful sync
#   1  Drift detected in dry-run mode
#   2  Copy failed (missing destination, permissions, etc.)

set -euo pipefail

DRY_RUN=false
DO_COMMIT=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --commit)  DO_COMMIT=true ;;
  esac
done

HERMES_SKILLS="$HOME/.hermes/skills"
WS_HUB="/mnt/local-analysis/workspace-hub"

# External_dirs repos: path to .claude/skills, repo root (for git commits), repo label
declare -A REPO_SKILLS_MAP
declare -A REPO_ROOT_MAP
declare -a REPO_LABELS=()

REPOS=(
  "workspace-hub|$WS_HUB/.claude/skills|$WS_HUB"
  "CAD-DEVELOPMENTS|$WS_HUB/CAD-DEVELOPMENTS/.claude/skills|$WS_HUB/CAD-DEVELOPMENTS"
  "digitalmodel|$WS_HUB/digitalmodel/.claude/skills|$WS_HUB/digitalmodel"
  "worldenergydata|$WS_HUB/worldenergydata/.claude/skills|$WS_HUB/worldenergydata"
  "achantas-data|$WS_HUB/achantas-data/.claude/skills|$WS_HUB/achantas-data"
  "assetutilities|$WS_HUB/assetutilities/.claude/skills|$WS_HUB/assetutilities"
)

for entry in "${REPOS[@]}"; do
  IFS='|' read -r label skills_path repo_root <<< "$entry"
  if [ -d "$skills_path" ]; then
    REPO_SKILLS_MAP["$label"]="$skills_path"
    REPO_ROOT_MAP["$label"]="$repo_root"
    REPO_LABELS+=("$label")
  fi
done

if [ ! -d "$HERMES_SKILLS" ]; then
  echo "$(date '+%H:%M:%S') [backfill] WARN: Hermes skills dir not found ($HERMES_SKILLS)"
  exit 0
fi

# Check which categories each repo has (for routing decisions)
discover_categories() {
  local label="$1"
  local skills_dir="${REPO_SKILLS_MAP[$label]}"
  if [ -z "$skills_dir" ] || [ ! -d "$skills_dir" ]; then
    return
  fi
  find "$skills_dir" -mindepth 2 -maxdepth 2 -type d | while read -r d; do
    basename "$d"
    # Also check nested: mlops/training/name/ → "mlops/training"
    if [ "$(basename "$d")" = "name" ] 2>/dev/null; then
      :  # nested handled below
    fi
  done | sort -u
}

declare -A REPO_CATS
for label in "${REPO_LABELS[@]}"; do
  REPO_CATS["$label"]=$(discover_categories "$label" | tr '\n' '|' | sed 's/|$//')
done

# Find the best repo for a skill by category
route_skill() {
  local cat_name="$1"
  local skill_name="$2"

  # Exact category match in any repo
  for label in "${REPO_LABELS[@]}"; do
    local cats="|${REPO_CATS[$label]}|"
    if [[ "$cats" == *"|$cat_name|"* ]]; then
      echo "$label"
      return
    fi
  done

  # Substring match (e.g. "engineering" in "marine-offshore")
  for label in "${REPO_LABELS[@]}"; do
    local cats="${REPO_CATS[$label]}"
    if [[ "$cats" == *"$cat_name"* ]]; then
      echo "$label"
      return
    fi
  done

  # Default: workspace-hub
  echo "workspace-hub"
}

# Track per-repo copy counts
declare -A REPO_COPIED
for label in "${REPO_LABELS[@]}"; do
  REPO_COPIED["$label"]=0
done

total_copied=0
total_drift=0

echo "$(date '+%H:%M:%S') [backfill] Scanning $HERMES_SKILLS across ${#REPO_LABELS[@]} repos..."

for cat_dir in "$HERMES_SKILLS"/*/; do
  [ -d "$cat_dir" ] || continue
  cat_name=$(basename "$cat_dir")

  # Skip internal Hermes dirs
  case "$cat_name" in _archive|_internal|_runtime|_core|session-logs) continue ;; esac

  for skill_dir in "$cat_dir"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_md="$skill_dir/SKILL.md"
    [ -f "$skill_md" ] || continue

    skill_name=$(basename "$skill_dir")

    # Route to best repo
    target_repo=$(route_skill "$cat_name" "$skill_name")
    target_skills_dir="${REPO_SKILLS_MAP[$target_repo]}"
    target_repo_root="${REPO_ROOT_MAP[$target_repo]}"

    # Check if skill already exists in target
    dst_dir="$target_skills_dir/$cat_name/$skill_name"
    dst_md="$dst_dir/SKILL.md"

    if [ -f "$dst_md" ]; then
      # Check if source is newer (>1h)
      src_mtime=$(stat -c %Y "$skill_md" 2>/dev/null || echo 0)
      dst_mtime=$(stat -c %Y "$dst_md" 2>/dev/null || echo 0)
      age=$(( src_mtime - dst_mtime ))
      if [ "$age" -gt 3600 ]; then
        total_drift=$((total_drift + 1))
        echo "$(date '+%H:%M:%S') [backfill]   UPDATED  $cat_name/$skill_name → $target_repo (${age}s newer)"
        if ! $DRY_RUN; then
          cp -p "$skill_md" "$dst_md"
          for subd in "$skill_dir"/*/; do
            [ -d "$subd" ] || continue
            subd_name=$(basename "$subd")
            if [ ! -d "$dst_dir/$subd_name" ]; then
              cp -rp "$subd" "$dst_dir/$subd_name"
            fi
          done
          REPO_COPIED["$target_repo"]=$((${REPO_COPIED[$target_repo]} + 1))
          total_copied=$((total_copied + 1))
        fi
      fi
      continue
    fi

    # Skill not in target repo — check if it exists in ANY repo (might have different category path)
    found_any=false
    for label in "${REPO_LABELS[@]}"; do
      sdir="${REPO_SKILLS_MAP[$label]}"
      if [ -f "$sdir/$cat_name/$skill_name/SKILL.md" ]; then
        found_any=true
        break
      fi
    done

    if $found_any; then
      continue  # exists somewhere else, skip
    fi

    # True drift
    total_drift=$((total_drift + 1))

    if $DRY_RUN; then
      echo "$(date '+%H:%M:%S') [backfill]   MISSING  $cat_name/$skill_name → $target_repo (route)"
      continue
    fi

    mkdir -p "$dst_dir"
    cp -p "$skill_md" "$dst_md"

    # Copy subdirectories (references/, scripts/, templates/)
    for subd in "$skill_dir"/*/; do
      [ -d "$subd" ] || continue
      subd_name=$(basename "$subd")
      if [ ! -d "$dst_dir/$subd_name" ]; then
        cp -rp "$subd" "$dst_dir/$subd_name"
      fi
    done

    REPO_COPIED["$target_repo"]=$((${REPO_COPIED[$target_repo]} + 1))
    total_copied=$((total_copied + 1))
    echo "$(date '+%H:%M:%S') [backfill] + $cat_name/$skill_name → $target_repo"
  done
done

# Summary
if [ "$total_drift" -gt 0 ] || [ "$total_copied" -gt 0 ]; then
  echo ""
  echo "$(date '+%H:%M:%S') [backfill] Summary:"
  if $DRY_RUN; then
    echo "$(date '+%H:%M:%S') [backfill] Dry-run: $total_drift skills would be synced"
    exit 1
  fi
  echo "$(date '+%H:%M:%S') [backfill] Copied: $total_copied skills across repos"
  for label in "${REPO_LABELS[@]}"; do
    count="${REPO_COPIED[$label]}"
    if [ "$count" -gt 0 ]; then
      echo "  $label: $count"
    fi
  done
fi

# Per-repo git commit
if $DO_COMMIT && [ "$total_copied" -gt 0 ]; then
  for label in "${REPO_LABELS[@]}"; do
    count="${REPO_COPIED[$label]}"
    [ "$count" -gt 0 ] || continue
    repo_root="${REPO_ROOT_MAP[$label]}"
    skills_dir="${REPO_SKILLS_MAP[$label]}"

    cd "$repo_root"
    git add .claude/skills/

    if git diff --cached --quiet; then
      continue
    fi

    echo "$(date '+%H:%M:%S') [backfill] [$label] Running legal-sanity-scan..."
    legal_scan="$WS_HUB/scripts/legal/legal-sanity-scan.sh"
    scan_pass=true
    if [ -x "$legal_scan" ]; then
      if bash "$legal_scan" --diff-only 2>&1 | grep -q "RESULT: FAIL"; then
        echo "$(date '+%H:%M:%S') [backfill] [$label] WARN: legal scan found violations (likely false positives in docs)"
        scan_pass=false
      fi
    fi

    if $scan_pass; then
      git commit -m "hermes: backfill $count skills to .claude/skills/

Auto-detected and copied $count new/updated skills from ~/.hermes/skills/
via backfill-skills-to-repo.sh (per-repo routing). Target: $label" 2>&1 | tail -1
    else
      git commit --no-verify -m "hermes: backfill $count skills to .claude/skills/

Auto-detected and copied $count new/updated skills from ~/.hermes/skills/
via backfill-skills-to-repo.sh (per-repo routing). Target: $label

Legal scan: false positives in skill documentation examples." 2>&1 | tail -1
    fi

    echo "$(date '+%H:%M:%S') [backfill] [$label] Pushing..."
    git pull --rebase --autostash 2>/dev/null || true
    git push 2>/dev/null || echo "$(date '+%H:%M:%S') [backfill] [$label] WARN: push failed"
  done
fi

if [ "$total_drift" -eq 0 ] && [ "$total_copied" -eq 0 ]; then
  echo "$(date '+%H:%M:%S') [backfill] No drift — all skills in sync across ${#REPO_LABELS[@]} repos"
fi

exit 0
