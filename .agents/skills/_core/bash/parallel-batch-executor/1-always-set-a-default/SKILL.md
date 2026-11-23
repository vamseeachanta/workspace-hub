---
name: parallel-batch-executor-1-always-set-a-default
description: 'Sub-skill of parallel-batch-executor: 1. Always Set a Default (+4).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Always Set a Default (+4)

## 1. Always Set a Default

```bash
PARALLEL="${PARALLEL:-5}"
```


## 2. Validate Input

```bash
[[ $PARALLEL -gt 0 ]] || die "Parallelism must be positive"
[[ $PARALLEL -le 50 ]] || log_warning "High parallelism may overwhelm system"
```


## 3. Handle Failures Gracefully

```bash
# Don't use set -e with xargs - it will mask failures
# Instead, track failures explicitly
```


## 4. Log Everything

```bash
# Create per-task logs for debugging
log_file="$LOG_DIR/task_$(date +%s)_$$.log"
```


## 5. Clean Up Resources

```bash
trap cleanup EXIT INT TERM
```
