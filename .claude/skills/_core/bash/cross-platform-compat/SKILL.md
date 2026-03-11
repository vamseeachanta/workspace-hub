---
name: cross-platform-compat
description: Portable bash patterns for Windows Git Bash, Linux, and macOS. Canonical
  replacement table for bc/python3/nproc/sed-i/git-add and OS detection. Use when
  writing or auditing scripts that run across machines.
version: 1.0.0
category: _core/bash
type: skill
trigger: manual
auto_execute: false
platforms: [linux, macos, windows_gitbash]
capabilities:
  - cross_platform
  - windows_gitbash_compat
  - portable_arithmetic
  - python_resolver
  - os_detection
tags: [bash, cross-platform, windows, git-bash, portable, bc, python3, nproc]
related_skills:
  - bash-script-framework
  - bash-cli-framework
see_also:
  - _core/bash/bash-script-framework
---

# Cross-Platform Bash Compatibility

> Canonical replacement patterns for shell constructs that break on Windows Git Bash,
> macOS, or both. Always use these patterns in workspace-hub scripts.

## Quick Reference — Replacement Table

| Broken Pattern | Breaks On | Portable Replacement |
|----------------|-----------|----------------------|
| `echo "$a < $b" \| bc -l` | Git Bash (no bc) | `awk "BEGIN {print ($a < $b) ? 1 : 0}"` |
| `echo "scale=2; $a / $b" \| bc` | Git Bash | `awk "BEGIN {printf \"%.2f\", $a / $b}"` |
| `python3 script.py` | Windows | `$PYTHON script.py` (use resolver below) |
| `nproc` | Git Bash | `nproc 2>/dev/null \|\| getconf _NPROCESSORS_ONLN 2>/dev/null \|\| echo 1` |
| `sed -i "s/..."` | macOS | `sed -i.bak "s/..." && rm file.bak` |
| `git add missing/dir/` | all (set -e) | Guard with `[[ -d path ]] && git add path` |
| `date -v-1d +%Y%m%d` | Linux/Git Bash | `date -d "yesterday" +%Y%m%d 2>/dev/null \|\| date -v-1d +%Y%m%d` |

## Patterns in Detail

### Float Comparison Without bc

```bash
# bc not available on Git Bash Windows
# BAD:  if (( $(echo "$score < 0.6" | bc -l) )); then
# GOOD: awk-based (works everywhere)
float_lt() {
    awk "BEGIN {exit !($1 < $2)}"
}
if float_lt "$score" "0.6"; then echo "below threshold"; fi

# Or integer-multiply trick (score 0.0-1.0 → multiply by 10):
score_int=$(awk "BEGIN {print int($score * 10)}")
if (( score_int < 6 )); then echo "below threshold"; fi
```

### Division / Percentages Without bc

```bash
# BAD:  pct=$(echo "scale=1; $done * 100 / $total" | bc)
# GOOD:
pct=$(awk "BEGIN {printf \"%.1f\", $done * 100 / $total}")
```

### Platform-Aware Python Resolver

```bash
# Add once at top of script; use $PYTHON everywhere else
resolve_python() {
    if command -v python3 &>/dev/null; then
        echo "python3"
    elif command -v python &>/dev/null && python -c "import sys; assert sys.version_info >= (3,8)" 2>/dev/null; then
        echo "python"
    else
        echo "uv run --no-project python"
    fi
}
PYTHON=$(resolve_python)
# Usage: $PYTHON script.py  OR  $PYTHON -c "..."
```

### CPU Count Without nproc

```bash
cpu_count() {
    nproc 2>/dev/null \
        || getconf _NPROCESSORS_ONLN 2>/dev/null \
        || sysctl -n hw.ncpu 2>/dev/null \
        || echo "1"
}
MAX_PARALLEL=$(cpu_count)
```

### Safe git add (Skip Missing Paths)

```bash
# BAD:  git add .claude/state/candidates/ .claude/state/corrections/
#       ^ fatal error + silent skip when dirs don't exist
# GOOD:
git_add_if_exists() {
    local staged=0
    for path in "$@"; do
        if [[ -e "$path" ]]; then
            git add "$path" && staged=1
        fi
    done
    return $(( staged == 0 ? 1 : 0 ))
}
if git_add_if_exists \
    .claude/state/candidates/ \
    .claude/state/corrections/ \
    .claude/state/patterns/; then
    git commit -m "chore: session learnings from $(hostname)"
fi
```

### Portable sed -i (Linux + macOS)

```bash
# BAD:  sed -i "s/old/new/" file      # macOS: requires backup extension
# GOOD:
portable_sed_i() {
    local expr="$1" file="$2"
    if sed --version 2>/dev/null | grep -q GNU; then
        sed -i "$expr" "$file"          # GNU sed (Linux, Git Bash)
    else
        sed -i '' "$expr" "$file"       # BSD sed (macOS)
    fi
}
```

### OS Detection

```bash
# From bash-script-framework utils.sh — canonical pattern:
get_os() {
    case "$(uname -s)" in
        Linux*)              echo "linux" ;;
        Darwin*)             echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)                   echo "unknown" ;;
    esac
}

IS_WINDOWS=false
[[ "$(get_os)" == "windows" ]] && IS_WINDOWS=true
```

## Startup Compatibility Check

Add to scripts that must run cross-platform:

```bash
check_deps() {
    local missing=()
    # jq is required for JSON parsing
    command -v jq &>/dev/null || missing+=("jq (install: https://jqlang.github.io/jq/)")
    # Report clearly — never silently degrade
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "ERROR: missing required tools:" >&2
        printf '  - %s\n' "${missing[@]}" >&2
        exit 1
    fi
}
check_deps
```

## Anti-Patterns (Never Use in Cross-Platform Scripts)

```bash
# NEVER: bc for arithmetic           → use awk
# NEVER: python3 hardcoded           → use $PYTHON resolver
# NEVER: nproc without fallback      → use cpu_count()
# NEVER: git add path/ without guard → use git_add_if_exists()
# NEVER: 2>/dev/null || echo "1"     → hides errors, returns wrong fallback
#         ^-- this is the "silent failure" anti-pattern
```

## WRK Reference

- **WRK-1117**: Fixed `comprehensive-learning.sh` Windows push + `bc` in `guard.sh`
- **WRK-1118**: Systematic sweep of all `bc`/`python3`/`nproc` across 150+ script lines
