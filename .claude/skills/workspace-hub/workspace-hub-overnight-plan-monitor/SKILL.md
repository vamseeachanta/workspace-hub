---
name: workspace-hub-overnight-plan-monitor
description: Read-only monitoring workflow for workspace-hub overnight planning batches using PID files and dossier result markdowns.
triggers:
  - Monitor Claude/Codex/Gemini overnight planning runs in workspace-hub
  - Count completed dossiers under docs/plans/overnight-prompts/*/results
  - Check which batch terminal processes are still alive from logs/*.pid
  - Summarize final recommendations from dossier markdown files
---

# Workspace-hub overnight plan monitor

Use this when a cron/job asks for a status report on an overnight planning batch (for example a 10-pack under `logs/.../*.pid` and `docs/plans/overnight-prompts/.../results/*.md`).

## Why this skill exists

A few practical quirks showed up during monitoring:

1. `read_file()` prefixes lines with `N|`, which can corrupt naive PID parsing if you just regex the first number.
2. `search_files(target='files')` may return results under `files`, not `matches`, so handle both shapes.
3. Cached/deduped file reads can be awkward for tiny PID files; direct Python file reads from `terminal`/`execute_code` are often more reliable for read-only monitoring.
4. Dossier markdowns are not uniform; extract recommendations from the `Final Recommendation` section with tolerant parsing.

## Recommended workflow

1. **List PID files and result files**
   - Use `search_files(target='files')` on the exact batch directories.
   - For file listings, read from `result.get('files', [])` first and fall back only if needed.

2. **Check live processes with direct Python/OS calls**
   - Prefer a short Python script via `terminal` or `execute_code`:
     - `Path.glob('*.pid')`
     - `pf.read_text().strip()`
     - `os.kill(pid, 0)` to test liveness
   - This avoids line-number prefixes from `read_file()`.

3. **Count completed dossiers from the results directory**
   - Count `*.md` files in the exact `results/` folder.
   - Do not infer completion from prompts outside `results/`.

4. **Map dossier to terminal/issue**
   - Terminal name usually comes from the result filename stem.
   - Issue number is best extracted from the markdown metadata table row.
   - Handle both plain and emphasized field labels, for example:
     - `| Issue | #2053 |`
     - `| **Issue** | #2055 |`
     - or `| Issue | WRK-1113 |`
   - Prefer this table over generic regexes, because the body often references dependency issues too.
   - If the value is a markdown link like `[ #2063 ](url)` or `[ #2063](url)`, normalize it to just `#2063` in the report.

5. **Extract a one-line recommendation**
   - Parse from the `## ... Final Recommendation` section.
   - Normalize formatting first:
     - strip leading `###`
     - remove surrounding `**...**`
     - collapse repeated whitespace
   - Use this priority:
     1. Explicit `RECOMMENDATION:` line
     2. First status heading/line in the section (often bold or `###`)
     3. First substantive explanatory sentence or bullet after that heading
   - Skip boilerplate lead-ins when choosing the explanatory text, such as:
     - `Rationale:` / `**Rationale:**`
     - `Action required:` / `Action needed:`
     - `Required before implementation:`
     - `Pre-implementation actions required:`
   - Good outputs look like:
     - `READY AFTER LABEL UPDATE — scaffold is complete and tested`
     - `NEEDS ISSUE REFINEMENT — required source data is missing`
     - `ALREADY MOSTLY DONE — only thin wrapper/test work remains`

6. **Completion rule for reporting**
   - If all expected dossiers exist, monitoring is complete.
   - If no batch PIDs remain alive, monitoring is also complete even if some dossiers are missing.
   - Otherwise report incomplete status and identify the still-running terminals.

## Reference Python pattern

```python
from pathlib import Path
import os, re

pid_dir = Path('/mnt/local-analysis/workspace-hub/logs/claude-2026-04-09-10pack')
result_dir = Path('/mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-09-10claude/results')

result_files = sorted(result_dir.glob('*.md'))

alive = []
for pf in sorted(pid_dir.glob('*.pid')):
    m = re.search(r'\d+', pf.read_text().strip())
    pid = int(m.group(0)) if m else None
    is_alive = False
    if pid is not None:
        try:
            os.kill(pid, 0)
            is_alive = True
        except OSError:
            pass
    if is_alive:
        alive.append(pf.stem)
```

## Pitfalls

- Do **not** parse PID files with a regex against raw `read_file()` output unless you strip the `N|` prefix first.
- Do **not** count prompt files outside `results/` as completed dossiers.
- Do **not** grab the first `#205x`/`WRK-xxxx` in the document body; dependency references can mislead issue extraction.
- Keep the task read-only: no file writes, no repo modifications.

## Output checklist

- Result file count
- Completed terminal/issue list
- One-line recommendation per completed dossier
- Alive process count and alive terminal list
- Explicit `monitoring is complete` statement when either all dossiers exist or no processes remain
