---
id: GOT-003
type: gotcha
title: "CRLF line endings silently kill bash scripts on MINGW64"
category: tooling
tags: [windows, mingw64, crlf, bash, scripts, line-endings]
repos: [workspace-hub]
confidence: 1.0
created: "2026-02-22"
last_validated: "2026-02-22"
source_type: manual
related: []
status: active
access_count: 0
---

# CRLF Line Endings Silently Kill Bash Scripts on MINGW64

## Symptom

A bash script runs without any output and exits with code 1. Even `set -x` trace appears to run successfully but then the script aborts silently mid-execution. No error message is shown.

## Root Causes (two separate issues found in knowledge-manager)

1. **CRLF in scripts**: The shebang line becomes `#!/usr/bin/env bash\r`, causing the interpreter lookup to fail or behave incorrectly. Even if the script starts, `[[ "$line" == "---" ]]` comparisons fail because `$line` contains `---\r`, not `---`.

2. **`set -euo pipefail` + missing directory**: `find <missing-dir> | wc -l | tr -d '[:space:]'` — `find` returns exit code 1 when directory doesn't exist. With `pipefail`, this kills the script. `2>/dev/null` suppresses the error message but not the exit code.

## Fix

```bash
# Strip CRLF from all bash scripts in a directory
for f in scripts/*.sh; do sed -i 's/\r//' "$f"; done

# For entry/data files read by scripts
find .claude/knowledge/entries -name "*.md" | xargs sed -i 's/\r//'

# Pre-create directories referenced in pipelines
mkdir -p .claude/knowledge/archive
```

## Prevention

- All shell scripts: `#!/usr/bin/env bash`, LF endings, tested on MINGW64
- New directories referenced in scripts should be created at skill install time
- Use `git config core.autocrlf input` in repos containing shell scripts
