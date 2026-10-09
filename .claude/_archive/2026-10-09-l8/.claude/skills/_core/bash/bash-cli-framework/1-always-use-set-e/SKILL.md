---
name: bash-cli-framework-1-always-use-set-e
description: 'Sub-skill of bash-cli-framework: 1. Always Use `set -e` (+4).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Always Use `set -e` (+4)

## 1. Always Use `set -e`

Exit immediately if a command exits with non-zero status:
```bash
set -e
# Or for more control:
set -euo pipefail
```


## 2. Quote Variables

Always quote variables to prevent word splitting:
```bash
# Good
echo "$variable"
"$command" "$arg1" "$arg2"

# Bad
echo $variable
$command $arg1 $arg2
```


## 3. Use Meaningful Exit Codes

```bash
# Exit codes
EXIT_SUCCESS=0
EXIT_ERROR=1
EXIT_USAGE=2
EXIT_CONFIG=3
```


## 4. Provide Feedback

Always tell the user what's happening:
```bash
log_info "Starting process..."
# do work
log_info "Process complete (processed $count items)"
```


## 5. Support Dry Run

Let users preview changes:
```bash
if [[ $DRY_RUN == true ]]; then
    log_info "[DRY RUN] Would execute: $command"
else
    eval "$command"
fi
```
