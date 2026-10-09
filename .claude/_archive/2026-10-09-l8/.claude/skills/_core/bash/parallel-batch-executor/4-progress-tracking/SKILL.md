---
name: parallel-batch-executor-4-progress-tracking
description: 'Sub-skill of parallel-batch-executor: 4. Progress Tracking (+2).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 4. Progress Tracking (+2)

## 4. Progress Tracking


Track progress during parallel execution:

```bash
#!/bin/bash
# ABOUTME: Parallel execution with progress tracking
# ABOUTME: Shows real-time progress and summary statistics

PARALLEL="${PARALLEL:-5}"
PROGRESS_FILE=$(mktemp)
TOTAL=0
SUCCESS=0
FAILED=0

# Initialize progress file
echo "0" > "$PROGRESS_FILE"

# Track progress atomically
track_progress() {
    local status="$1"
    local item="$2"

    # Use flock for atomic updates
    (
        flock -x 200
        local current=$(cat "$PROGRESS_FILE")
        echo $((current + 1)) > "$PROGRESS_FILE"

        if [[ "$status" == "success" ]]; then
            echo "S" >> "${PROGRESS_FILE}.status"
        else
            echo "F" >> "${PROGRESS_FILE}.status"
        fi
    ) 200>"${PROGRESS_FILE}.lock"
}

process_with_tracking() {
    local items=("$@")
    local total=${#items[@]}

    echo "Processing $total items with $PARALLEL workers..."
    echo ""

    printf '%s\n' "${items[@]}" | xargs -I {} -P "$PARALLEL" bash -c "
        item=\"{}\"

        # Process item
        if process_item \"\$item\" 2>/dev/null; then
            echo \"success \$item\"
        else
            echo \"failed \$item\"
        fi
    " | while read status item; do
        track_progress "$status" "$item"

        local current=$(cat "$PROGRESS_FILE")
        local pct=$((current * 100 / total))

        # Update progress line
        printf \"\\r[%3d%%] Processed %d/%d items\" \$pct \$current \$total
    done

    echo ""
    echo "Complete!"

    # Show summary
    local success=$(grep -c "S" "${PROGRESS_FILE}.status" 2>/dev/null || echo 0)
    local failed=$(grep -c "F" "${PROGRESS_FILE}.status" 2>/dev/null || echo 0)
    echo "Success: $success, Failed: $failed"

    # Cleanup
    rm -f "$PROGRESS_FILE" "${PROGRESS_FILE}.lock" "${PROGRESS_FILE}.status"
}
```


## 5. Error Collection


Collect and report errors from parallel execution:

```bash
#!/bin/bash
# ABOUTME: Parallel execution with centralized error collection
# ABOUTME: Aggregates errors for reporting after batch completion

ERROR_LOG=$(mktemp)
SUCCESS_LOG=$(mktemp)

cleanup() {
    rm -f "$ERROR_LOG" "$SUCCESS_LOG"
}
trap cleanup EXIT

parallel_with_errors() {
    local command="$1"
    shift
    local items=("$@")

    printf '%s\n' "${items[@]}" | xargs -I {} -P "$PARALLEL" bash -c "
        item=\"{}\"
        output=\$($command \"\$item\" 2>&1)
        exit_code=\$?

        if [[ \$exit_code -eq 0 ]]; then
            echo \"\$item\" >> \"$SUCCESS_LOG\"
        else
            echo \"\$item: \$output\" >> \"$ERROR_LOG\"
        fi
    "

    # Report results
    local success_count=$(wc -l < "$SUCCESS_LOG" 2>/dev/null || echo 0)
    local error_count=$(wc -l < "$ERROR_LOG" 2>/dev/null || echo 0)

    echo ""
    echo "Results: $success_count succeeded, $error_count failed"

    if [[ $error_count -gt 0 ]]; then
        echo ""
        echo "Errors:"
        cat "$ERROR_LOG" | while read line; do
            echo "  ✗ $line"
        done
        return 1
    fi

    return 0
}
```


## 6. GNU Parallel Alternative


For more advanced parallelism:

```bash
#!/bin/bash
# ABOUTME: Advanced parallel execution using GNU Parallel
# ABOUTME: Provides job control, logging, and resume capabilities

# Check for GNU Parallel
if command -v parallel &> /dev/null; then
    USE_GNU_PARALLEL=true
else
    USE_GNU_PARALLEL=false
fi

parallel_execute() {
    local command="$1"
    local jobs="${2:-5}"

    if [[ "$USE_GNU_PARALLEL" == true ]]; then
        # GNU Parallel with job log
        parallel --jobs "$jobs" \
                 --joblog /tmp/parallel_joblog.txt \
                 --bar \
                 "$command" {}
    else
        # Fallback to xargs
        xargs -I {} -P "$jobs" bash -c "$command \"{}\""
    fi
}

# Usage
cat files.txt | parallel_execute "process_file" 10
```
