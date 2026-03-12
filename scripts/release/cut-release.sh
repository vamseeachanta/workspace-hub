#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

usage() {
  echo "Usage: $0 <repo> <version> [--dry-run]"
  echo "Valid repos: assetutilities digitalmodel worldenergydata assethold OGManufacturing"
  exit 1
}

if [[ $# -lt 2 ]]; then
  usage
fi

repo="$1"
version="$2"
dry_run=0
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then
    dry_run=1
  fi
done

# Validate repo name
valid_repos=("assetutilities" "digitalmodel" "worldenergydata" "assethold" "OGManufacturing")
repo_valid=0
for r in "${valid_repos[@]}"; do
  if [[ "$r" == "$repo" ]]; then
    repo_valid=1
    break
  fi
done
if [[ "$repo_valid" -eq 0 ]]; then
  echo "Unknown repo: $repo" >&2
  exit 1
fi

# Validate semver format
if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid semver: $version (expected X.Y.Z)" >&2
  exit 1
fi

# Resolve repo path
repo_path="$WORKSPACE_ROOT/$repo"
if [[ ! -d "$repo_path" ]]; then
  echo "Repo not found: $repo_path" >&2
  exit 1
fi

# Detect old version
old_version=$(grep '^version = ' "$repo_path/pyproject.toml" | sed 's/version = "\(.*\)"/\1/')

# Detect since-ref
since_ref=$(git -C "$repo_path" describe --tags --abbrev=0 --match "v*.*.*" 2>/dev/null \
  || git -C "$repo_path" log --pretty=format:"%H" | tail -1)

# Generate changelog entry
changelog_entry=$("$WORKSPACE_ROOT/scripts/release/generate-changelog.sh" "$repo_path" "$version" "$since_ref")

# Count commits since ref for dry-run output
commit_count=$(git -C "$repo_path" log "${since_ref}..HEAD" --oneline 2>/dev/null | wc -l || echo "?")

if [[ "$dry_run" -eq 1 ]]; then
  echo "[DRY RUN] Would bump $repo: $old_version → $version"
  echo "[DRY RUN] Would generate CHANGELOG entry ($commit_count commits since $since_ref)"
  echo "[DRY RUN] Would tag: v$version"
  echo "[DRY RUN] Would update release-manifest.yaml"
  echo "[DRY RUN] Would commit in submodule and at hub level"
  exit 0
fi

# Bump version in pyproject.toml
sed -i "s/^version = \"$old_version\"/version = \"$version\"/" "$repo_path/pyproject.toml"

# Prepend changelog entry to CHANGELOG.md
changelog_file="$repo_path/CHANGELOG.md"
if [[ ! -f "$changelog_file" ]]; then
  printf "# Changelog\n\n%s\n" "$changelog_entry" > "$changelog_file"
else
  # Insert after first '# Changelog' line, or after '---' separator if present
  if grep -q '^---' "$changelog_file"; then
    # Insert after the '---' separator line
    sed -i "/^---/a\\
\\
$changelog_entry" "$changelog_file"
  else
    # Insert after the '# Changelog' header line
    sed -i "/^# Changelog/a\\
\\
$changelog_entry" "$changelog_file"
  fi
fi

# Commit in submodule
git -C "$repo_path" add pyproject.toml CHANGELOG.md
git -C "$repo_path" commit -m "chore(release): v$version"

# Tag
git -C "$repo_path" tag "v$version"

# Update release manifest
sed -i "s/$repo: \"$old_version\"/$repo: \"$version\"/" \
  "$WORKSPACE_ROOT/config/releases/release-manifest.yaml"

# Hub commit
git -C "$WORKSPACE_ROOT" add "config/releases/release-manifest.yaml" "$repo"
git -C "$WORKSPACE_ROOT" commit -m "chore(release): $repo v$version"

echo "Released $repo v$version (was $old_version)"
echo "Tagged: v$version"
echo "Changelog updated: $changelog_file"
