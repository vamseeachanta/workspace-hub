#!/usr/bin/env bash
set -euo pipefail

action="${1:-}"
shift || true

case "$action" in
    check|review)
        if command -v gemini >/dev/null 2>&1; then
            echo "OK"
        else
            [[ "$action" == "review" ]] && echo "NO_OUTPUT" || echo "ERROR"
        fi
        ;;
    execute)
        task_file="${1:?Usage: gemini.sh execute <task_file>}"
        if ! command -v gemini >/dev/null 2>&1; then
            echo "ERROR: gemini CLI not found" >&2
            exit 1
        fi
        if [[ ! -f "$task_file" ]]; then
            echo "ERROR: task file not found: $task_file" >&2
            exit 1
        fi
        # Extract task body — skip frontmatter, take first 80 lines of content
        task_desc=$(awk '/^---$/{if(++c==2){f=1;next}}f' "$task_file" | head -80)
        out=$(mktemp /tmp/gemini-out.XXXXXX)
        err=$(mktemp /tmp/gemini-err.XXXXXX)
        echo "$task_desc" | timeout 300 gemini -p "Execute the following task and report results:" -y >"$out" 2>"$err"
        rc=$?
        echo "output=$out errors=$err exit=$rc"
        ;;
    *)
        if command -v gemini >/dev/null 2>&1; then
            echo "OK"
        else
            echo "ERROR"
        fi
        ;;
esac
