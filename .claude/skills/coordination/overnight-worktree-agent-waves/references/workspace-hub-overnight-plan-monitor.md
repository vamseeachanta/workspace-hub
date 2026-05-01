# Archived Skill: `workspace-hub-overnight-plan-monitor`

Original path: `/home/vamsee/.hermes/skills/workspace-hub/workspace-hub-overnight-plan-monitor`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub/workspace-hub-overnight-plan-monitor`
Consolidation date: 2026-04-29

---

---
name: workspace-hub-overnight-plan-monitor
description: Monitor and reconcile workspace-hub overnight planning or implementation batches, including process status, result artifacts, issue/commit verification, and controlled failed-lane recovery.
triggers:
  - Monitor Claude/Codex/Gemini overnight planning runs in workspace-hub
  - Monitor parallel Claude implementation batches launched by Hermes background process sessions
  - Count completed dossiers under docs/plans/overnight-prompts/*/results or /mnt/local-analysis/overnight-batch-*/results
  - Check which batch terminal processes are still alive from logs/*.pid or Hermes process session IDs
  - Summarize final recommendations from dossier markdown files or implementation lane summaries
  - Reconcile missing central result artifacts when workers wrote `.nightly-results/` inside the repo
  - Convert failed/no-output/max-turn lanes into blocker notes or narrow recovery prompts
---

# Workspace-hub overnight plan monitor

Use this when a cron/job or user asks for a status report on an overnight planning or implementation batch (for example a 10-pack under `logs/.../*.pid` and `docs/plans/overnight-prompts/.../results/*.md`, or a Hermes-launched batch under `/mnt/local-analysis/overnight-batch-*/{logs,prompts,results}`).

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

1a. **Verify expected worktree roots before trusting missing artifacts**
   - For explicit worktree monitoring requests, first test whether each expected root exists and is a git repo/worktree (`Path.exists()`, `.git` file/dir, or `git worktree list --porcelain`).
   - If expected worktree roots are missing, say the run is incomplete at the requested locations and list the launched paths for operator inspection.
   - Use a bounded exact-path fallback in the main checkout (for example `/mnt/local-analysis/workspace-hub/<same-relative-summary-path>` and the same prompt directory) to find central salvage artifacts, but classify them separately from the expected worktree outputs.
   - Avoid broad `rglob`/`search_files` over all of `/mnt/local-analysis` for summary names unless tightly bounded; it can time out on large workspaces.

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

## Worker-claim verification rule

Do not trust a finished worker's stdout summary by itself.

A worker can claim:
- issue moved to `status:plan-review`
- plan file written
- review artifacts present

while one of those local artifacts is actually missing from the monitored worktree.

For every completed worker, verify all three surfaces before reporting success:
1. **Live GitHub issue state**
   - check labels on the issue (`status:plan-review`, `status:plan-approved`, etc.)
   - inspect the most recent comments if the worker claimed a plan-summary or blocker comment
2. **Canonical local plan artifact**
   - confirm the claimed `docs/plans/YYYY-MM-DD-issue-NNN-*.md` file actually exists in the active worktree
3. **Local review artifacts**
   - confirm the claimed `scripts/review/results/*plan-NNN-*` files actually exist in the active worktree

If GitHub state advanced but local artifacts are missing:
- classify the issue as **governance/artifact reconciliation required**
- do not report it as cleanly verified
- say explicitly: label/comment confirmed, local artifact state not confirmed

This prevents false confidence when a worker comment or completion log overstates what landed on disk.

## Implementation-batch reconciliation pattern

When the batch is an implementation/closeout batch rather than a pure plan-review dossier batch, treat stdout as a lead, not proof.

1. **Poll Hermes process sessions if no PID files exist**
   - Use `process(action='poll', session_id=...)` for launches created by `terminal(background=true)`.
   - Record `status`, `exit_code`, and the output preview.
   - A worker can exit successfully while writing its summary to an alternate sandbox path; a worker can also be superseded by another lane while its original process exits `-15`.

2. **Verify GitHub and commit surfaces for every claimed completion**
   - `gh issue view <n> --json state,stateReason,labels,comments,url`
   - `git rev-parse --verify <sha>^{commit}`
   - `git branch -a --contains <sha>` or direct remote containment checks
   - `git show --stat --name-only --oneline <sha>`
   - Classify separately: issue state, remote landed state, local checkout/worktree state.

3. **Reconcile result artifact locations**
   - Workers may be sandboxed to `/mnt/local-analysis/workspace-hub` and unable to write `/mnt/local-analysis/overnight-batch-*/results`.
   - Search for `.nightly-results/<date>-terminal-*-summary.md` in the repo checkout and batch worktrees.
   - If the user expects a central batch directory, mirror/copy the missing summaries into `overnight-batch-*/results/` and note that this is an orchestrator reconciliation action.

4. **Handle failed/no-output/max-turn lanes decisively**
   - Do not relaunch blindly.
   - First inspect the lane log, GitHub issue state, and owned-path diff/status only.
   - If the log is just `Error: Reached max turns (...)` and owned-path status/diff is empty, write a central blocker/current-state note documenting that no owned-path edits landed.
   - Then launch a narrower recovery prompt scoped to the exact owned paths, required validators, and closeout steps.
   - If the lane was intentionally superseded (for example original process exited `-15` but another path completed the issue), preserve both a blocker/supersession note and a completion summary so morning review sees why the raw process status looks failed.

5. **Handle post-reboot ghost completions**
   - After a reboot, Hermes background process state may be gone and the worker log/central summary may be empty or missing even though the implementation commit landed on `origin/main`.
   - If a claimed or discovered commit is already on the intended remote and contains exactly the owned paths, treat this as a **closeout-only reconciliation**, not a rerun trigger.
   - Re-run the prompt's read-only validation block against the committed files and check residual owned-path diffs only for the scoped paths.
   - If validation passes but the issue is still open or still labeled `status:plan-approved`, write the missing central summary artifact, post a closeout comment, close the issue as completed, and move the label to `status:done`.
   - This closeout can be safe even while unrelated interactive agents are active in the repo, provided you do not mutate git state and only touch the external results artifact plus GitHub issue state.

6. **Write an aggregate verification report**
   - Include one row per lane: process result, GitHub state, commit/artifact verification, verdict, and next action.
   - Store it in the central results directory (for example `results/post-batch-verification-YYYY-MM-DD.md`).

## Output checklist

- Result file count
- Completed terminal/issue list
- One-line recommendation per completed dossier or implementation summary
- Alive process count and alive terminal/session list
- For each completed issue: whether GitHub state was confirmed, whether claimed commits are present on the intended remote, whether claimed files appear in the commit, whether local artifacts exist
- Missing or mirrored summary artifacts, including source and destination paths
- Failed-lane classification: max-turn/no-output/superseded/blocked, with blocker path if written
- Recovery session ID/log path if a narrow recovery run was launched
- Explicit `monitoring is complete` statement when either all expected artifacts exist or no processes remain; otherwise name the exact still-running recovery sessions
