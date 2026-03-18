#!/usr/bin/env bash
# assign-routes.sh — Suggest complexity route (A/B/C) for a WRK item.
# Usage: assign-routes.sh <WRK-NNN>
# Output: suggested route with confidence and reasoning.
# This is a SUGGESTION only — never auto-modifies the WRK file.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "${REPO_ROOT:-.}")"
QUEUE_ROOT="${QUEUE_ROOT:-$REPO_ROOT/.claude/work-queue}"

usage() { echo "Usage: assign-routes.sh <WRK-NNN>" >&2; exit 1; }
[[ $# -ge 1 ]] || usage

WRK_ID="$1"

# Locate the WRK file across queue directories
WRK_FILE=""
for dir in pending working blocked archived; do
  candidate="$QUEUE_ROOT/$dir/$WRK_ID.md"
  [[ -f "$candidate" ]] && WRK_FILE="$candidate" && break
done
[[ -n "$WRK_FILE" ]] || { echo "ERROR: $WRK_ID not found in queue" >&2; exit 1; }

# --- Extract frontmatter and body ---
fm_end=$(awk '/^---$/{n++; if(n==2){print NR; exit}}' "$WRK_FILE")
if [[ -z "$fm_end" ]]; then
  frontmatter=""
  body=$(cat "$WRK_FILE")
else
  frontmatter=$(sed -n "2,$((fm_end - 1))p" "$WRK_FILE")
  body=$(tail -n +"$((fm_end + 1))" "$WRK_FILE")
fi

# --- Signal 1: Description word count ---
word_count=$(echo "$body" | wc -w | tr -d ' ')
if [[ "$word_count" -lt 50 ]]; then
  word_score=1; word_label="A"
elif [[ "$word_count" -le 200 ]]; then
  word_score=2; word_label="B"
else
  word_score=3; word_label="C"
fi

# --- Signal 2: Target repos count ---
repo_count=$(echo "$frontmatter" | grep -cE '^- ' | tr -d ' ' || true)
# Filter to only lines under target_repos
repo_count=$(awk '
  /^target_repos:/{capture=1; next}
  capture && /^- /{count++; next}
  capture && /^[^ -]/{capture=0}
  END{print count+0}
' <<< "$frontmatter")
if [[ "$repo_count" -le 1 ]]; then
  repo_score=1; repo_label="A"
elif [[ "$repo_count" -le 2 ]]; then
  repo_score=2; repo_label="B"
else
  repo_score=3; repo_label="C"
fi

# --- Signal 3: Related WRK count ---
related_count=$(awk '
  /^related:/{capture=1; next}
  capture && /^- /{count++; next}
  capture && /^[^ -]/{capture=0}
  /^related: \[\]/{print 0; found=1}
  END{if(!found) print count+0}
' <<< "$frontmatter")
if [[ "$related_count" -eq 0 ]]; then
  rel_score=1; rel_label="A"
elif [[ "$related_count" -le 3 ]]; then
  rel_score=2; rel_label="B"
else
  rel_score=3; rel_label="C"
fi

# --- Signal 4: Keyword scan ---
title=$(echo "$frontmatter" | grep '^title:' | sed 's/^title: *//' | tr -d '"')
combined="$title $body"
combined_lower=$(echo "$combined" | tr '[:upper:]' '[:lower:]')

kw_score=2; kw_label="none"
route_a_kw="fix|typo|rename|update|bump|simple|minor"
route_c_kw="architect|refactor|redesign|migrate|cross-repo|feature.layer|multi-repo|breaking.change|schema"

if echo "$combined_lower" | grep -qE "$route_c_kw"; then
  kw_score=3; kw_label="C-keyword"
elif echo "$combined_lower" | grep -qE "$route_a_kw"; then
  kw_score=1; kw_label="A-keyword"
fi

# --- Signal 5: Existing complexity field ---
existing=$(echo "$frontmatter" | grep '^complexity:' | sed 's/^complexity: *//' | tr -d ' "' || true)
has_existing=false
if [[ -n "$existing" ]]; then
  has_existing=true
fi

# --- Compute average score ---
total=$((word_score + repo_score + rel_score + kw_score))
count=4
# Use bc for decimal average, then classify
avg=$(echo "scale=2; $total / $count" | bc)

if (( $(echo "$avg < 1.5" | bc -l) )); then
  route="A"; complexity="simple"
elif (( $(echo "$avg < 2.5" | bc -l) )); then
  route="B"; complexity="medium"
else
  route="C"; complexity="complex"
fi

# --- Confidence ---
spread=$((word_score > kw_score ? word_score - kw_score : kw_score - word_score))
max_spread=$((repo_score > rel_score ? repo_score - rel_score : rel_score - repo_score))
[[ $max_spread -gt $spread ]] && spread=$max_spread
if [[ $spread -le 1 ]]; then
  confidence="high"
else
  confidence="medium"
fi

# --- Output ---
echo "$WRK_ID: Route $route ($complexity) — confidence: $confidence"
echo "  Signals: words=$word_count ($word_label), repos=$repo_count ($repo_label), related=$related_count ($rel_label), keywords=$kw_label"

if [[ "$has_existing" == true ]]; then
  echo "  Current complexity field: $existing"
  # Normalize existing to compare
  existing_lower=$(echo "$existing" | tr '[:upper:]' '[:lower:]')
  if [[ "$existing_lower" != "$complexity" ]]; then
    echo "  ⚠ Current complexity '$existing' differs from heuristic suggestion '$complexity'"
  else
    echo "  Current complexity matches suggestion"
  fi
else
  echo "  No complexity field set"
fi

echo ""
echo "  Suggestion: complexity: $complexity"
