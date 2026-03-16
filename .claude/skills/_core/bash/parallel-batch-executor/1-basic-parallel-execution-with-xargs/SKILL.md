---
name: parallel-batch-executor-1-basic-parallel-execution-with-xargs
description: 'Sub-skill of parallel-batch-executor: 1. Basic Parallel Execution with
  xargs (+2).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Basic Parallel Execution with xargs (+2)

## 1. Basic Parallel Execution with xargs


The fundamental pattern for parallel execution:

```bash
#!/bin/bash
# ABOUTME: Basic parallel execution using xargs
# ABOUTME: Process multiple items concurrently with controlled parallelism

PARALLEL="${PARALLEL:-5}"  # Default to 5 parallel workers

# Process items from stdin in parallel
cat items.txt | xargs -I {} -P "$PARALLEL" bash -c 'echo "Processing: {}"'

# Process with error handling
cat items.txt | xargs -I {} -P "$PARALLEL" bash -c '
    item="{}"
    if process_item "$item"; then
        echo "✓ $item"
    else
        echo "✗ $item" >&2
    fi
'
```


## 2. JSON Array Processing


Process JSON arrays in parallel (from batch_runner.sh):

```bash
#!/bin/bash
# ABOUTME: Process JSON array items in parallel
# ABOUTME: Uses jq for parsing and xargs for parallel execution

set -e

PARALLEL="${1:-5}"
ORCHESTRATOR="./scripts/routing/orchestrate.sh"

# Check dependencies
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed."
    exit 1
fi

echo "Starting batch execution with $PARALLEL parallel workers..."

# Read JSON array from stdin, extract items, process in parallel
jq -r '.[]' | xargs -I {} -P "$PARALLEL" bash -c "$ORCHESTRATOR \"{}\" > /dev/null"

echo "Batch execution complete."
```


## 3. Repository Batch Operations


Execute commands across multiple repositories:

```bash
#!/bin/bash
# ABOUTME: Execute operations across multiple repositories in parallel
# ABOUTME: Pattern from workspace-hub repository_sync

PARALLEL="${PARALLEL:-5}"
REPOS_DIR="/mnt/github"

# Get list of repositories
get_repos() {
    find "$REPOS_DIR" -maxdepth 1 -type d -name "[!.]*" | sort
}

# Execute command in each repository in parallel
batch_repo_command() {
    local command="$1"
    local repos
    repos=$(get_repos)

    echo "$repos" | xargs -I {} -P "$PARALLEL" bash -c "
        repo=\"{}\"
        repo_name=\$(basename \"\$repo\")

        if cd \"\$repo\" 2>/dev/null; then
            result=\$($command 2>&1)
            exit_code=\$?

            if [[ \$exit_code -eq 0 ]]; then
                echo \"✓ \$repo_name: \$result\"
            else
                echo \"✗ \$repo_name: \$result\" >&2
            fi
        else
            echo \"⊘ \$repo_name: Directory not accessible\" >&2
        fi
    "
}

# Usage examples
batch_repo_command "git status --porcelain | head -1"
batch_repo_command "git pull --rebase"
batch_repo_command "git push"
```
