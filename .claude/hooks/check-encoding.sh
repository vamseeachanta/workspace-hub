#!/usr/bin/env bash
# check-encoding.sh — encoding guard (pre-commit / post-merge / post-checkout)
#
# Requires: uv  (https://docs.astral.sh/uv/ — install once, works everywhere)
# Setup:    bash scripts/operations/setup-hooks.sh

set -euo pipefail

HOOK_NAME="$(basename "$0")"
REPO_ROOT="$(git rev-parse --show-toplevel)"

command -v uv >/dev/null 2>&1 || {
    echo "check-encoding: uv not found. Run: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
}

# Scan files using uv-managed Python — no system python dependency
check_file() {
    uv run --no-project --quiet python - "$1" <<'PYEOF'
import sys, pathlib
raw = pathlib.Path(sys.argv[1]).read_bytes()
if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
    print('utf16')
elif raw[:3] == b'\xef\xbb\xbf':
    print('utf8bom')
else:
    try:
        raw.decode('utf-8')
    except UnicodeDecodeError:
        print('bad')
PYEOF
}

BAD=()

collect_files() {
    if [[ "$HOOK_NAME" == "pre-commit" ]]; then
        git diff --cached --name-only --diff-filter=ACM
    else
        # Exclude specs/repos/ — machine-generated engineering tool outputs
        # (OrcaFlex writes UTF-8 BOM YAML; fatigue docs contain Latin-1 notation)
        # These are reference artifacts, not hand-authored text files.
        git ls-files -- \
            '.claude/work-queue' '.claude/skills' 'specs' 'config' \
            ':!specs/repos/'
    fi
}

while IFS= read -r f; do
    [[ -f "$REPO_ROOT/$f" ]] || continue
    [[ "$f" =~ \.(md|yaml|yml|json)$ ]] || continue
    result=$(check_file "$REPO_ROOT/$f")
    [[ "$result" == "utf16" || "$result" == "bad" ]] && BAD+=("  $result: $f")
done < <(collect_files)

[[ ${#BAD[@]} -eq 0 ]] && exit 0

echo ""
echo "check-encoding: BAD ENCODING"
for msg in "${BAD[@]}"; do echo "$msg"; done
echo ""
echo "Fix: save the file as UTF-8 (no BOM) from your editor, or run:"
echo "  uv run --no-project python -c \""
echo "    import pathlib, sys; f=pathlib.Path(sys.argv[1]);"
echo "    f.write_text(f.read_bytes().decode('utf-16').replace(chr(13),''),encoding='utf-8')"
echo "  \" <file>"
echo ""
[[ "$HOOK_NAME" == "pre-commit" ]] && { echo "Commit BLOCKED."; exit 1; }
echo "WARNING: fix and commit these files."
exit 0
