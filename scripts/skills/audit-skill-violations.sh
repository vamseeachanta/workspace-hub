#!/usr/bin/env bash
# DEPRECATED: Use audit-skills.py --mode violations instead (single-pass, ~400x faster).
# audit-skill-violations.sh — Check SKILL.md files for structural violations.
#
# Checks per SKILL.md:
#   1. README.md presence in skill dir (v2 anti-pattern)
#   2. SKILL.md word count > 5000
#   3. description: field > 1024 chars
#   4. XML/HTML tags in SKILL.md body
#
# Exit: 0 = clean, 1 = violations found, 2 = usage/script error
# Output: YAML to stdout

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# --- Defaults ---
SKILL_DIR="${REPO_ROOT}/.claude/skills"

# --- Argument parsing ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill-dir)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --skill-dir requires a path argument" >&2
        exit 2
      fi
      SKILL_DIR="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--skill-dir <path>]" >&2
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$SKILL_DIR" ]]; then
  echo "Error: skill dir not found: ${SKILL_DIR}" >&2
  exit 2
fi

# --- Collect SKILL.md files ---
mapfile -t SKILL_FILES < <(find "$SKILL_DIR" -name "SKILL.md" | sort)

if [[ ${#SKILL_FILES[@]} -eq 0 ]]; then
  printf "violations: []\n"
  exit 0
fi

VIOLATIONS=()

for SKILL_FILE in "${SKILL_FILES[@]}"; do
  SKILL_DIRPATH="$(dirname "$SKILL_FILE")"

  # Check 1: README.md present in skill dir (v2 anti-pattern)
  if [[ -f "${SKILL_DIRPATH}/README.md" ]]; then
    VIOLATIONS+=("  - file: ${SKILL_FILE}")
    VIOLATIONS+=("    check: readme_present")
    VIOLATIONS+=("    severity: warn")
    VIOLATIONS+=("    detail: \"README.md found in skill dir (v2 anti-pattern)\"")
  fi

  # Check 2: word count > 5000
  WORD_COUNT=$(wc -w < "$SKILL_FILE")
  if [[ "$WORD_COUNT" -gt 5000 ]]; then
    VIOLATIONS+=("  - file: ${SKILL_FILE}")
    VIOLATIONS+=("    check: word_count_exceeded")
    VIOLATIONS+=("    severity: warn")
    VIOLATIONS+=("    detail: \"SKILL.md has ${WORD_COUNT} words (limit: 5000)\"")
  fi

  # Check 3: description: field > 1024 chars (safe YAML parse via Python)
  DESC_LENGTH=$(uv run --no-project python -c "
import sys, re
try:
    content = open('${SKILL_FILE}').read()
    # Extract frontmatter between first pair of ---
    parts = content.split('---')
    if len(parts) >= 3:
        fm = parts[1]
        # Match description: as block scalar or inline
        # Block scalar: description: >\n  text...
        block = re.search(r'^description:\s*[>|]\n((?:[ \t]+[^\n]*\n?)*)', fm, re.MULTILINE)
        if block:
            # Strip leading whitespace per line and join
            lines = block.group(1).splitlines()
            desc = ' '.join(l.strip() for l in lines if l.strip())
            print(len(desc))
        else:
            # Inline: description: some text
            inline = re.search(r'^description:\s*(.+)', fm, re.MULTILINE)
            if inline:
                print(len(inline.group(1).strip()))
            else:
                print(0)
    else:
        print(0)
except Exception as e:
    print(0)
" 2>/dev/null || echo 0)

  if [[ "$DESC_LENGTH" -gt 1024 ]]; then
    VIOLATIONS+=("  - file: ${SKILL_FILE}")
    VIOLATIONS+=("    check: description_too_long")
    VIOLATIONS+=("    severity: warn")
    VIOLATIONS+=("    detail: \"description field is ${DESC_LENGTH} chars (limit: 1024)\"")
  fi

  # Check 4: XML/HTML tags in SKILL.md body (after frontmatter)
  # Strip frontmatter (between first ---) and check body for <tag> patterns
  HAS_TAGS=$(uv run --no-project python -c "
import re, sys
try:
    content = open('${SKILL_FILE}').read()
    parts = content.split('---', 2)
    body = parts[2] if len(parts) >= 3 else content
    # Strip code blocks to avoid false positives on HTML in examples
    body = re.sub(r'\x60\x60\x60[^\x60]*\x60\x60\x60', '', body, flags=re.DOTALL)
    # Match HTML/XML tags
    tags = re.findall(r'<[a-zA-Z][a-zA-Z0-9_:-]*(?:\s[^>]*)?>|</[a-zA-Z][a-zA-Z0-9_:-]*>', body)
    # Whitelist: standard HTML tags + template placeholders (lowercase single words)
    WHITELIST = {'details', 'summary', 'br', 'hr', 'sub', 'sup', 'kbd', 'img', 'a', 'em', 'strong', 'code', 'pre', 'p', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'thead', 'tbody', 'div', 'span', 'b', 'i', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'dl', 'dt', 'dd', 'head', 'body', 'html', 'meta', 'style', 'script', 'header', 'footer', 'main', 'section', 'nav', 'aside', 'article', 'figure', 'figcaption', 'button', 'input', 'form', 'label', 'select', 'option', 'textarea', 'svg', 'path', 'canvas', 'video', 'audio', 'source', 'link', 'title'}
    non_whitelisted = []
    for t in tags:
        tag_name = re.match(r'</?([a-zA-Z][a-zA-Z0-9_:-]*)', t)
        if not tag_name:
            continue
        name = tag_name.group(1)
        # Skip whitelisted HTML tags
        if name.lower() in WHITELIST:
            continue
        # Skip template placeholders: lowercase single words like <domain>, <pkg>
        if re.match(r'^[a-z][a-z0-9_-]*$', name) and len(name) <= 20:
            continue
        non_whitelisted.append(t)
    print(len(non_whitelisted))
except Exception:
    print(0)
" 2>/dev/null || echo 0)

  if [[ "$HAS_TAGS" -gt 0 ]]; then
    VIOLATIONS+=("  - file: ${SKILL_FILE}")
    VIOLATIONS+=("    check: xml_html_tags_in_body")
    VIOLATIONS+=("    severity: warn")
    VIOLATIONS+=("    detail: \"${HAS_TAGS} XML/HTML tag(s) found in SKILL.md body\"")
  fi
done

# --- Output ---
if [[ ${#VIOLATIONS[@]} -eq 0 ]]; then
  printf "violations: []\n"
  exit 0
fi

printf "violations:\n"
for line in "${VIOLATIONS[@]}"; do
  printf "%s\n" "$line"
done

exit 1
