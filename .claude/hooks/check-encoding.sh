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

collect_files() {
    if [[ "$HOOK_NAME" == "pre-commit" ]]; then
        git diff --cached --name-only -z --diff-filter=ACM
    else
        # Exclude specs/repos/ — machine-generated engineering tool outputs
        # (OrcaFlex writes UTF-8 BOM YAML; fatigue docs contain Latin-1 notation)
        # These are reference artifacts, not hand-authored text files.
        git ls-files -z -- \
            '.claude/work-queue' '.claude/skills' 'specs' 'config' \
            ':!specs/repos/'
    fi
}

# Collect files to check (NUL-safe read from git -z output)
FILES=$(while IFS= read -r -d '' f; do
    [[ -f "$REPO_ROOT/$f" ]] || continue
    [[ "$f" =~ \.(md|yaml|yml|json)$ ]] || continue
    printf '%s\n' "$f"
done < <(collect_files))

if [[ -z "$FILES" ]]; then
    exit 0
fi

# Create a temporary python script (trap ensures cleanup on any exit)
PY_SCRIPT=$(mktemp)
trap 'rm -f "$PY_SCRIPT"' EXIT
cat <<'PYEOF' > "$PY_SCRIPT"
import sys, pathlib
root = pathlib.Path(sys.argv[1])
for line in sys.stdin:
    f_rel = line.strip()
    if not f_rel: continue
    f_abs = root / f_rel
    try:
        if not f_abs.exists(): continue
        raw = f_abs.read_bytes()
        if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
            print(f"  utf16: {f_rel}")
        elif raw[:3] == b'\xef\xbb\xbf':
            pass # UTF-8 BOM is currently allowed (just ignored)
        else:
            try:
                raw.decode('utf-8')
            except UnicodeDecodeError:
                print(f"  bad: {f_rel}")
    except Exception:
        pass
PYEOF

# Process all files in a single python invocation to avoid uv overhead per-file
BAD_REPORT=$(echo "$FILES" | uv run --no-project --quiet python "$PY_SCRIPT" "$REPO_ROOT")

[[ -z "$BAD_REPORT" ]] && exit 0

echo ""
echo "check-encoding: BAD ENCODING"
echo "$BAD_REPORT"
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
