#!/usr/bin/env bash
set -euo pipefail

action="${1:-}"
shift || true

case "$action" in
    check)
        echo "OK"
        ;;
    review)
        # Claude reviews inline via the orchestrator session, not via CLI
        echo "NO_OUTPUT"
        ;;
    execute)
        task_file="${1:?Usage: claude.sh execute <task_file> [--model <model_id>]}"
        shift
        model_id=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --model) model_id="$2"; shift 2 ;;
                *) echo "Unknown arg: $1" >&2; exit 2 ;;
            esac
        done
        if ! command -v claude >/dev/null 2>&1; then
            echo "ERROR: claude CLI not found" >&2
            exit 1
        fi
        if [[ ! -f "$task_file" ]]; then
            echo "ERROR: task file not found: $task_file" >&2
            exit 1
        fi
        # Extract task body — skip frontmatter, take first 80 lines of content
        task_desc=$(awk '/^---$/{if(++c==2){f=1;next}}f' "$task_file" | head -80)
        out=$(mktemp /tmp/claude-out.XXXXXX)
        err=$(mktemp /tmp/claude-err.XXXXXX)
        model_args=()
        [[ -n "$model_id" ]] && model_args+=(--model "$model_id")
        echo "$task_desc" | timeout 300 claude -p "Execute this task:" "${model_args[@]}" >"$out" 2>"$err"
        rc=$?
        echo "output=$out errors=$err exit=$rc"
        ;;
    *)
        echo "OK"
        ;;
esac
