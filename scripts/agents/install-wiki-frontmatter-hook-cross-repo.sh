#!/usr/bin/env bash
# install-wiki-frontmatter-hook-cross-repo.sh — workspace-hub #2778
#
# Installs scripts/enforcement/check-wiki-sibling-frontmatter.{py,sh} into
# each wiki sibling (`llm-wiki` generic + `llm-wiki-<client>` per the
# config/client-wikis.yml registry).
#
# Per wiki repo, this script:
#   1. Vendors the .py + .sh enforcement scripts into the wiki repo's
#      `.workspace-hub/hooks/` directory (NOT .git/hooks — keeping vendored
#      content under a tracked path makes drift auditable).
#   2. Vendors a copy of config/client-wikis.yml to
#      `.workspace-hub/client-wikis.yml` (the script's default registry
#      resolution path; see .claude/rules/wiki-sibling-routing.md).
#   3. Adds `.workspace-hub/` to the wiki repo's .gitignore if not already
#      present (r2-F7 fix from plan adversarial review).
#   4. Wires the check into the wiki repo's pre-commit hook (idempotent —
#      safe to re-run as the manual re-sync procedure).
#   5. Refuses to write into dirty siblings (notice + skip).
#
# DESIGN NOTE (#2778 implementation): the plan originally said "extend the
# existing #2722 cross-repo installer". On implementation, the tier-1 manifest
# (`scripts/agents/tier1-repos.sh`) does not include wiki repos — they're a
# separate category. A dedicated installer that reads `config/client-wikis.yml`
# keeps concerns clean. The cross-repo installer pattern (vendoring, dirty-skip,
# idempotent wiring) is preserved verbatim from #2722.
#
# Manual re-sync procedure (per .claude/rules/wiki-sibling-routing.md):
#   git -C workspace-hub pull && \
#   bash scripts/agents/install-wiki-frontmatter-hook-cross-repo.sh

set -uo pipefail

log() { echo "[install-wiki-frontmatter-hook] $*"; }

WS_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CANONICAL_PY="$WS_ROOT/scripts/enforcement/check-wiki-sibling-frontmatter.py"
CANONICAL_SH="$WS_ROOT/scripts/enforcement/check-wiki-sibling-frontmatter.sh"
REGISTRY="$WS_ROOT/config/client-wikis.yml"

if [[ ! -f "$CANONICAL_PY" ]]; then
  log "ERROR: canonical script not found at $CANONICAL_PY"
  exit 2
fi
if [[ ! -f "$CANONICAL_SH" ]]; then
  log "ERROR: canonical wrapper not found at $CANONICAL_SH"
  exit 2
fi
if [[ ! -f "$REGISTRY" ]]; then
  log "ERROR: client-wikis registry not found at $REGISTRY"
  exit 2
fi

# Build the wiki-repo list:
#   - Always include 'llm-wiki' (generic sibling)
#   - Plus every short_name in client-wikis.yml
WIKIS=("llm-wiki")
mapfile -t CLIENT_WIKIS < <(python3 -c "
import yaml, sys
with open('$REGISTRY') as f:
    data = yaml.safe_load(f) or {}
for w in data.get('wikis', []):
    if isinstance(w, dict) and w.get('short_name'):
        print('llm-wiki-' + w['short_name'])
" 2>/dev/null) || {
  log "ERROR: failed to parse client-wikis registry"
  exit 2
}
WIKIS+=("${CLIENT_WIKIS[@]}")

WIRING_SENTINEL="check-wiki-sibling-frontmatter"
WIRING_BLOCK='
# ── Wiki frontmatter check (workspace-hub#2778) ──
CHECK="${REPO_ROOT:-$(git rev-parse --show-toplevel)}/.workspace-hub/hooks/check-wiki-sibling-frontmatter.sh"
if [[ -f "$CHECK" ]]; then
  bash "$CHECK" || exit 1
fi'

GITIGNORE_ENTRY=".workspace-hub/"
GITIGNORE_COMMENT="# Vendored from workspace-hub (per #2778) — re-sync via scripts/agents/install-wiki-frontmatter-hook-cross-repo.sh"

installed=0
skipped=0
errors=0

for wiki in "${WIKIS[@]}"; do
  repo_path="$WS_ROOT/../$wiki"
  if [[ ! -d "$repo_path/.git" ]] && [[ ! -f "$repo_path/.git" ]]; then
    log "skip $wiki — not a git repo at $repo_path"
    ((skipped++))
    continue
  fi

  # Dirty-sibling skip — match #2722 installer pattern.
  if [[ -n "$(git -C "$repo_path" status --porcelain 2>/dev/null)" ]]; then
    log "skip $wiki — uncommitted changes (commit or stash, then re-run)"
    ((skipped++))
    continue
  fi

  # 1. Vendor enforcement scripts.
  mkdir -p "$repo_path/.workspace-hub/hooks"
  cp "$CANONICAL_PY" "$repo_path/.workspace-hub/hooks/check-wiki-sibling-frontmatter.py"
  cp "$CANONICAL_SH" "$repo_path/.workspace-hub/hooks/check-wiki-sibling-frontmatter.sh"
  chmod +x "$repo_path/.workspace-hub/hooks/check-wiki-sibling-frontmatter."{py,sh}

  # 2. Vendor registry copy.
  cp "$REGISTRY" "$repo_path/.workspace-hub/client-wikis.yml"

  # 3. Add .workspace-hub/ to .gitignore if not already there (r2-F7 fix).
  gitignore="$repo_path/.gitignore"
  if [[ -f "$gitignore" ]] && grep -qxF "$GITIGNORE_ENTRY" "$gitignore"; then
    : # already present
  else
    {
      [[ -f "$gitignore" ]] && [[ -n "$(tail -c1 "$gitignore" 2>/dev/null)" ]] && echo ""
      echo "$GITIGNORE_COMMENT"
      echo "$GITIGNORE_ENTRY"
    } >> "$gitignore"
    log "added .workspace-hub/ to $wiki/.gitignore"
  fi

  # 4. Resolve hooks dir via git-common-dir (worktree-safe per #2722 prior art).
  hooks_dir="$(git -C "$repo_path" rev-parse --git-common-dir 2>/dev/null)/hooks"
  if [[ ! -d "$hooks_dir" ]]; then
    log "ERROR: hooks dir not found at $hooks_dir for $wiki"
    ((errors++))
    continue
  fi

  pre_commit="$hooks_dir/pre-commit"

  # Minimal pre-commit stub if missing (matches #2722 pattern).
  if [[ ! -f "$pre_commit" ]]; then
    cat > "$pre_commit" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
EOF
    chmod +x "$pre_commit"
  fi

  # Idempotent wiring — skip if sentinel already present.
  if grep -q "$WIRING_SENTINEL" "$pre_commit"; then
    : # already wired
  else
    # Insert before final `exit 0` if present, else append.
    if grep -q '^exit 0' "$pre_commit"; then
      tmp="$(mktemp)"
      awk -v block="$WIRING_BLOCK" '
        /^exit 0/ && !inserted { print block; inserted=1 }
        { print }
      ' "$pre_commit" > "$tmp"
      mv "$tmp" "$pre_commit"
    else
      printf '%s\n' "$WIRING_BLOCK" >> "$pre_commit"
    fi
    chmod +x "$pre_commit"
    log "wired check into $wiki/.git/hooks/pre-commit"
  fi

  log "installed in $wiki"
  ((installed++))
done

log ""
log "Summary: installed=$installed skipped=$skipped errors=$errors of ${#WIKIS[@]} wiki repos"

if [[ $errors -gt 0 ]]; then
  exit 1
fi
exit 0
