#!/usr/bin/env bash
# Fix npm global prefix to avoid sudo for global installs (e.g. claude update)
# Usage: bash scripts/setup/fix-npm-global.sh
#        sudo bash scripts/setup/fix-npm-global.sh  (to also remove root-owned leftovers)
set -euo pipefail

NPM_GLOBAL="$HOME/.npm-global"

echo "=== npm global prefix fix ==="

# 1. Create user-owned global prefix
if [ ! -d "$NPM_GLOBAL" ]; then
  mkdir -p "$NPM_GLOBAL"
  echo "[+] Created $NPM_GLOBAL"
else
  echo "[ok] $NPM_GLOBAL already exists"
fi

# 2. Set npm prefix
CURRENT_PREFIX=$(npm config get prefix 2>/dev/null)
if [ "$CURRENT_PREFIX" != "$NPM_GLOBAL" ]; then
  npm config set prefix "$NPM_GLOBAL"
  echo "[+] Set npm prefix to $NPM_GLOBAL (was: $CURRENT_PREFIX)"
else
  echo "[ok] npm prefix already set to $NPM_GLOBAL"
fi

# 3. Add to PATH in shell configs
add_to_path() {
  local file="$1"
  local line='export PATH="$HOME/.npm-global/bin:$PATH"'
  if [ -f "$file" ] && grep -qF ".npm-global/bin" "$file"; then
    echo "[ok] PATH entry already in $file"
  elif [ -f "$file" ]; then
    echo "" >> "$file"
    echo "# npm global prefix (no-sudo installs)" >> "$file"
    echo "$line" >> "$file"
    echo "[+] Added PATH entry to $file"
  fi
}

add_to_path "$HOME/.bashrc"
add_to_path "$HOME/.zshrc"
add_to_path "$HOME/.profile"

# 4. Clean up root-owned leftovers (requires sudo)
cleanup_root() {
  local target="$1"
  if [ -e "$target" ]; then
    local owner
    owner=$(stat -c '%U' "$target" 2>/dev/null || stat -f '%Su' "$target" 2>/dev/null)
    if [ "$owner" = "root" ]; then
      rm -rf "$target"
      echo "[+] Removed root-owned $target"
    else
      echo "[skip] $target owned by $owner, not root"
    fi
  fi
}

if [ "$(id -u)" -eq 0 ]; then
  echo ""
  echo "=== Cleaning root-owned leftovers ==="
  cleanup_root /usr/local/bin/claude
  cleanup_root /usr/local/lib/node_modules/@anthropic-ai
else
  echo ""
  echo "=== Root-owned leftovers (re-run with sudo to remove) ==="
  for target in /usr/local/bin/claude /usr/local/lib/node_modules/@anthropic-ai; do
    if [ -e "$target" ]; then
      owner=$(stat -c '%U' "$target" 2>/dev/null || stat -f '%Su' "$target" 2>/dev/null)
      echo "[!] $target (owner: $owner) — run: sudo rm -rf $target"
    fi
  done
fi

echo ""
echo "Done. Open a new terminal or run: source ~/.bashrc"
