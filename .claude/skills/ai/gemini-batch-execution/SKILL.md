---
name: gemini-batch-execution
description: Execute Gemini research tasks in efficient batches using hermes router to maximize $20/month quota utilization. Covers toolset config, batch patterns, sandbox pitfalls, and cleanup.
version: 1.0.0
category: ai
type: skill
trigger: manual
auto_execute: false
---

# Gemini Batch Execution

Execute Gemini research tasks in efficient batches to maximize the $20/month subscription. Two execution modes exist — pick based on task type.

## When to Use

- Research/standards mapping tasks
- Literature gathering and textbook acquisition
- Competitive intelligence or market scanning
- Any read-heavy, write-output task that benefits from Gemini's 1M context and web access

## MODE 1: Direct Local Execution (PREFERRED for repo work)

For tasks that touch the local filesystem (cataloging, indexing, running scripts, closing GitHub issues), use `execute_code` + `delegate_task` subagents instead of `h-router-gemini`. This is 5-10x faster with NO sandbox isolation issues.

### Why: Lessons from Overnight Batch (33 issues in one session)

- `delegate_task` with up to 3 parallel subagents runs independent filesystem work concurrently
- Subagents have direct repo access — no git commit failures, no -2 duplicate files, no sandbox state conflicts
- `gh issue close` + `gh issue comment` for cleanup without shell alias escaping issues
- One Hermes CLI session can close 30+ issues by doing lightweight filesystem ops directly

### Pattern: Filesystem Triage + Parallel Subagents

```python
# Step 1: List all gemini-assigned open issues
gh issue list --label "agent:gemini" --state open --json number,title,labels

# Step 2: Categorize by priority and batch (HIGH/MED/LOW)

# Step 3: For independent filesystem tasks, dispatch parallel subagents
delegate_task(tasks=[
    {"goal": "Scan and catalog <source_dir>...", "toolsets": ["terminal", "file"]},
    {"goal": "Triage /path/to/archive/...", "toolsets": ["terminal", "file"]},
    {"goal": "Catalog /path/to/refs/...", "toolsets": ["terminal", "file"]},
])

# Step 4: For tasks executable via existing scripts, run directly
uv run python scripts/document-intelligence/batch-process-standards.py --domain materials

# Step 5: Close issues with results
gh issue close <num> -c "Result summary here."
gh issue comment <num> -b "Detailed findings..."
```

### What NOT to do in local mode:
- Don't run LLM web research — delegate_task subagents can't do web_search
- Don't run tasks needing Gemini's 1M context window — subagents inherit your model, not Gemini
- Don't parallelize tasks that touch the same files — use separate subagents for separate dirs

### When to use Mode 1 vs Mode 2:
| Task Type | Mode |
|-----------|------|
| Filesystem scan/catalog | Mode 1 (direct) |
| Run existing scripts | Mode 1 (direct) |
| Close/update GitHub issues | Mode 1 (direct) |
| Web research, standards lookup | Mode 2 (h-router-gemini) |
| Large doc ingestion (1M context) | Mode 2 (h-router-gemini) |
| Literature gathering with ISBNs | Mode 2 (h-router-gemini) |

## MODE 2: h-router-gemini CLI (for web research)

Execute tasks via the Hermes router for tasks needing web access or Gemini's 1M context. Each session costs ~1-2 queries of the monthly quota — minimize sessions, maximize tasks per session.

## Working Command

```bash
h-router-gemini -t terminal,file,web -q "$(cat /tmp/gemini-task-prompt.txt)"
```

Do NOT use `h-gemini` — its `--base-url` flag syntax is broken in current Hermes versions. `h-router-gemini` (openrouter provider) works correctly.

## Toolset

Always use `-t terminal,file,web`:
- `file`: read_file, write_file, search_files — needed for codebase scanning and file creation
- `terminal`: run commands (git add, git commit, find, head) — needed to persist output
- `web`: web_search, web_extract — needed for live research

**CRITICAL: web_search is unreliable.** In multiple sessions, Gemini reported "I do not have a web_search tool" despite `-t web`. When this happens, Gemini falls back to internal knowledge. For research-heavy tasks, this means:
- Task output will include "Limitation Note: Live web searches could not be performed"
- Content may be stale or incomplete
- Strategy docs and plans are still useful; factual data (ISBNs, prices, URLs) may be placeholder

Workaround: If web_search fails, explicitly instruct Gemini in the prompt to "use known knowledge and document limitations" — otherwise it may loop trying to find the tool.

## Batch Pattern

Write ALL tasks into ONE prompt file. Gemini can handle 5-6 distinct tasks in a single session (each producing a file + commit).

```
/tmp/gemini-batch.txt:
  ┌─────────────────────────────┐
  │ TASK 1: Standards Gap ...   │
  │ TASK 2: SubseaIQ Data ...   │
  │ TASK 3: Textbooks Plan ...  │
  │ TASK 4: Speech-to-Text ...  │
  │ TASK 5: OSS Tools Update..  │
  │ TASK 6: Marine Hydro Ref..  │
  │                              │
  │ RULES:                       │
  │ - Order: 1,2,3,4,5,6        │
  │ - Commit after each         │
  │ - Do NOT git push           │
  │ - Overwrite files in place  │
  │ - No -2 versions            │
  └─────────────────────────────┘
```

## Per-Task Template

Each task in the batch follows this pattern:

```
══════════════════════════════════════════
TASK N: Name and Description (#issue)
══════════════════════════════════════════

1. Read/scan existing codebase or data (use search_files, read_file, terminal find/grep)
2. Research via web_search if needed
3. Create file at: docs/document-intelligence/standards-mapping/filename.md or notes/prep/filename.md
4. Commit: git add <file> && git commit -m "descriptive message (#issue)"

Do NOT push to remote after commits.
```

## Critical Pitfalls

1. **Sandbox isolation**: Gemini executes in an isolated sandbox. Files it creates can be destroyed when the session ends. The ONLY way to persist is for Gemini to successfully run `git commit` before the session terminates. Always verify with `git status --short` and `git log` after the session.

2. **Session timeout**: Sessions can timeout or abort mid-task. Always instruct Gemini to "commit after each task" so partial work is saved. If a session completes 3 of 6 tasks, the first 3 are already committed.

3. **No -2 versions**: Gemini sometimes creates duplicate files (file-2.md) when it cannot write to the original path (sandbox state conflict). If you see -2 versions, move the content to the original and remove the duplicate before committing.

4. **Git commit failures in sandbox**: Even after writing files successfully, Gemini's `git commit` can fail with exit 1 due to sandbox isolation. Always have a fallback plan: if Gemini's commits fail, check the files on disk, and commit them manually via terminal/homes session.

5. **Empty-content crash (FATAL)**: Gemini can hit "Max retries for empty content" errors (think blocks with no actual response) and die completely. When this happens:
   - The session exits immediately, abandoning ALL remaining tasks
   - Files written before the crash ARE committed (if commit succeeded before crash)
   - Remaining tasks are silently skipped — NO error message in the script output beyond the crash log
   - **Detection**: After batch runs, check `tail -100 <logfile>` for "Max retries (3) for empty content exceeded" and verify all issues are closed. Manually complete the remaining tasks immediately — don't retry Gemini.

6. **Alias resolution in scripts**: `h-router-gemini` is a shell alias and WON'T expand in non-interactive bash scripts. Always wrap it as a shell function before calling in scripts:
   ```bash
   h-router-gemini() { hermes chat --provider openrouter -m google/gemini-2.5-pro "$@"; }
   ```

7. **Sequential only**: Multiple Gemini sessions can't commit simultaneously. Run sessions sequentially, not in parallel.

## Nightly Cron Automation (IMPLEMENTED — #1961)

A nightly cron job auto-processes `agent:gemini` issues. No manual batching needed for triage-level work.

### Scripts
- `scripts/cron/gemini-nightly-batch.py` — Python processor (queries issues, classifies, processes/queues)
- `scripts/cron/gemini-nightly-batch.sh` — Bash wrapper (git-safe, workstation guard, state commit)
- Schedule: `0 23 * * *` (23:00 UTC) — declared in `config/scheduled-tasks/schedule-tasks.yaml`

### How the classifier works
- Labels containing `cat:research`, `cat:document-intelligence`, `dark-intelligence`, `domain:marine`, `domain:standards` → Mode 2 (router)
- Everything else → Mode 1 (local triage)
- Self-referencing meta issues (like #1961 itself) are auto-excluded
- Issues sorted by priority label (high → medium → low)
- Capped at 10 issues per run (safety)

### Reports
- JSON batch reports written to `.claude/state/gemini-batch/batch-YYYY-MM-DD.json`
- Reports are gitignored (ephemeral state), but auto-committed by the bash wrapper if not ignored

### Stale tracking issues
When reviewing pending Gemini work, always check if referenced sub-issues are already CLOSED before processing. The #1976 tracking issue listed 4 pending tasks — all were already done. Check with:
```bash
for i in <issue_numbers>; do gh issue view $i --json state --jq '.state'; done
```

## Manual Overnight Batch Execution via Hermes Cron

For tasks that genuinely need Gemini's 1M context or web research (Mode 2), use Hermes cron jobs:

```
cronjob create \
  --name "gemini-overnight-batch-1" \
  --model "google/gemini-2.5-pro" \
  --provider "openrouter" \
  --schedule "0 1 * * *" \
  --deliver "origin" \
  --prompt "<self-contained prompt>"
```

**CRITICAL**: The cron prompt must be fully self-contained (no external file refs, no `$(cat file)`). All file paths must be absolute. The cron session has the same toolset but may not have OPENROUTER_API_KEY in env — if Gemini fails to route, fall back to running `h-router-gemini` via terminal command in the prompt.

Schedule batches 60-75 minutes apart to avoid rate limits and ensure each session completes before the next starts.

## Post-Session Cleanup Checklist

```bash
cd /mnt/local-analysis/workspace-hub
# 1. Verify what Gemini committed
git log --oneline -5
git status --short

# 2. CRITICAL: Clean up duplicate commits from Gemini's retry loops
# Gemini often retries git commit and creates 2x commits for the same work
# Pattern: 5 commits followed by 5 identical commit messages
git reset --soft HEAD~N  # where N = number of duplicate commits
git reset HEAD -- .
git add <files>
git commit -m "clean single commit message (#issue)"

# 3. Check for duplicate files (-2 versions)
find . -name "*-2.*" 2>/dev/null
rm -f notes/prep/*-2.md docs/document-intelligence/*-2.md  # then keep originals

# 4. If Gemini created files but couldn't commit, commit them manually
git add <files>
git commit -m "feat(doc-intel): <description>"

# 5. Close completed issues
gh issue close <num> -c "<brief result summary>"

# 6. Update agent-work-queue.md
./scripts/refresh-agent-work-queue.sh
```

## Critical Pitfall: `uv run` suppresses stdout in sandbox subprocesses

When running scripts via `uv run python script.py`, ALL stdout output from the script is swallowed by the sandbox layer. Print statements, progress messages — all disappear. This causes "silent failures" that appear to succeed.

**Workarounds:**
1. Write progress/results to a log file (NOT stdout) and read it back with `read_file`
2. Use `process()` with `background=true` and `follow_output=true` for long-running tasks
3. Write to a file at each step, then `read_file` to check progress
4. Use `terminal("... > /tmp/log.log 2>&1; cat /tmp/log.log")` to force output via cat

**DO NOT:** rely on print() output from `uv run` scripts — it will vanish.

## Expected Efficiency

- 5-6 research tasks per session
- ~5 minutes per session (600s timeout usually enough)
- ~25-30 tasks for the entire $20/month quota
- Each task produces: 1 file + 1 commit + 1 issue close
- Overnight: schedule 4 cron jobs 60-75 min apart = 20 issues per night