---
name: overnight-parallel-agent-prompts
description: Design self-contained prompts for 3-5 terminals to run overnight without supervision. Ensures zero git contention, provider-optimal allocation, and a clear morning deliverable summary.
version: 1.2.0
tags: [multi-terminal, overnight, parallel, agent-prompts, productivity]
related_skills: [multi-machine-ai-readiness-and-issue-triage, writing-plans, issue-portfolio-triage]
---

# Overnight Parallel Agent Prompts

## When to Use

- User has 3-5 terminals open and wants maximum overnight productivity
- User wants to burn remaining AI credit on focused work
- Tasks exist that are self-contained and don't need user interaction
- Multiple independent workstreams can run in parallel

## Issue Triage Workflow (do this first)

1. Fetch all open issues: `gh issue list --repo OWNER/REPO --state open --limit 200 --json number,title,labels > /tmp/gh_issues.json`
   - **Important**: Output can be 80KB+ for large repos. Save to file first, then process with a Python heredoc via `terminal("python3 << 'PYEOF' ... PYEOF")`. Do NOT try to parse inside `execute_code` — the `read_file` line-join and terminal output cap both corrupt large JSON.
2. Categorize by label: priority (high/medium/low), category (engineering, doc-intel, automation), domain, machine
3. **Review previous batch results first**: Check `docs/plans/overnight-prompts/` for prior runs, read session-handoff docs, and `git log --oneline -20` to understand what was already completed. Avoid assigning work that was done in the last batch.
4. For repos with enforced plan gates (for example workspace-hub), check whether target issues are actually implementation-ready (`status:plan-approved` or repo-equivalent). If none are ready, either (a) stop and surface the gating gap, or (b) generate a clearly-labeled planning-only execution pack that produces implementation-ready dossiers/prompts instead of code changes.
5. For 6+ parallel sessions, strongly prefer planning-only or audit-only streams unless you have a large pool of already-approved, file-disjoint implementation issues. At 10 sessions, default to one unique result artifact per terminal to avoid git collisions.
6. Group into non-overlapping workstreams by file/directory ownership
7. Assign workstreams to terminals by provider strength (see allocation table)
8. Verify zero file overlap before writing prompts

## Selection Criteria for Overnight Tasks

Each task MUST be:
1. **Self-contained** — all context embedded in the prompt, no user questions
2. **Bounded** — clear start/end, not open-ended exploration
3. **Safe** — no destructive operations, no force pushes, no secret handling
4. **Verifiable** — produces artifacts you can check in the morning
5. **Git-collision-free** — each terminal writes to completely different files

Avoid overnight:
- Tasks requiring RDP/SSH to other machines
- Tasks that might need user judgment calls
- Risky refactors of production code
- Tasks with complex multi-step git merge dependencies

## Prompt Structure (each terminal)

```
We are in /path/to/repo. Execute these N tasks in order.
Use uv run for all Python. Commit to main and push after each.
Do not branch. TDD: write tests before implementation.
Do NOT ask the user any questions.

TASK 1: [Title] (GH issue #NNN)
[Full self-contained description with exact file paths]
[Acceptance criteria]
[Commit message template]

TASK 2: [Title] (GH issue #NNN)
[...]

IMPLEMENTATION CROSS-REVIEW (mandatory):
- After the implementation commit is pushed, capture the committed diff (`git show --stat --patch HEAD`)
- Write a self-contained adversarial review prompt that includes issue context, changed files, verification commands/results, and the exact diff
- Run Codex review on the committed diff for EVERY implementation prompt
- For architecture-heavy / policy-heavy / cross-module streams, also run Gemini review if available
- If review returns MAJOR or clear HIGH-severity findings, fix once, recommit, push, and rerun the reviewer(s) that found them
- Post a brief GH issue comment summarizing implementation, verification, and final review verdict(s)
```

## Provider Allocation Pattern

For 3 terminals:

| Terminal | Provider | Best for |
|----------|----------|----------|
| 1 | Claude | High-context: reading 30+ files, cross-referencing, synthesis, roadmaps |
| 2 | Codex seat 1 | Bounded implementation: scripts, tools, tests |
| 3 | Codex seat 2 or Gemini | Analysis, doc generation, audit reports |

For 5 terminals (scales with user's subscription mix):

| Terminal | Provider | Best for |
|----------|----------|----------|
| 1 | Claude | High-context synthesis: architecture scanning, roadmaps, cross-file analysis |
| 2 | Codex seat 1 | Bounded TDD implementation: tests + paired source code |
| 3 | Codex seat 2 | More bounded TDD: test coverage uplift, package-level work |
| 4 | Gemini | Doc generation: staleness scanning, doc refresh, audit reports |
| 5 | Claude/Hermes | Pipeline/tool building: scripts with tests, integration work |

## Git Contention Avoidance (MANDATORY)

Always produce a contention map at the end:

```
Terminal 1 writes: docs/assessments/, docs/roadmaps/
Terminal 2 writes: scripts/quality/, tests/quality/, docs/CAPABILITIES*.md
Terminal 3 writes: scripts/analysis/, tests/analysis/, docs/reports/
Zero overlap.
```

Rules:
- No two terminals touch the same file
- No two terminals touch the same directory if possible
- If unavoidable overlap (e.g., both add to docs/), stagger commits — put "git pull origin main" before each push in the prompt
- Never have two terminals modify the same GH issue body (comments are OK)

### Negative Write Boundaries (critical for 4+ terminals)

Each prompt MUST include an explicit blocklist of paths owned by OTHER terminals:

```
IMPORTANT: Do NOT write to docs/architecture/, docs/roadmaps/, scripts/analysis/,
digitalmodel/tests/orcawave/, digitalmodel/tests/solver/ — those are owned by
other terminals. Only write to: [your allowed paths].
```

This is stronger than just listing allowed paths — it prevents agents from
"helpfully" fixing something in another terminal's territory. Essential when
scaling to 4-5 terminals where ownership boundaries get tight.

## Prompt Files as Committed Artifacts

Save prompts to `docs/plans/overnight-prompts/<date>/terminal-N-<workstream>.md` (date-grouped
subdirectory, e.g. `2026-04-02/`) and commit them before launching. Also create a master
summary at `docs/plans/<date>-overnight-5-terminal-prompts.md` with the contention map,
issue-to-terminal mapping table, and morning deliverable summary. Benefits:
- Auditable: you can review what each terminal was told
- Reproducible: re-run the same batch if a terminal fails
- Reference: agents can read their own prompt file if context is lost

## Morning Deliverable Summary (MANDATORY)

Always end with a "What you'll have by morning" block:

```
From Terminal 1:
  ✓ [artifact 1]
  ✓ [artifact 2]
From Terminal 2:
  ✓ [artifact 3]
From Terminal 3:
  ✓ [artifact 4]
Issues addressed: #X, #Y, #Z
New tools: N reusable scripts
```

### Issue-to-Terminal Reverse Mapping (include in master plan)

Add a table mapping every issue to its terminal for quick morning triage:

```
| Issue | Title (abbreviated)         | Terminal |
|------:|----------------------------|----------|
| #1586 | Solver queue hardening     | T1       |
| #1587 | Docstring uplift           | T2       |
```

## Task Sizing

- 2-4 tasks per terminal (not more — overnight sessions can hit rate limits)
- Each task: 30-90 minutes of agent work
- Total per terminal: 2-4 hours max
- Front-load the most important task in each terminal
- If Claude quota is only partially available (for example ~50% remaining for the next 24h), prefer bounded 60-90 minute streams over ambitious all-night prompts. Make each terminal useful even if it stops after one implementation+review cycle.

## Common Task Types That Work Well Overnight

1. **Audit/discovery** — scan files, produce report markdown
2. **Tool building** — scripts with TDD (self-verifying)
3. **Doc refresh** — read current state, update stale docs
4. **Roadmap generation** — read skills+code+issues, synthesize
5. **Batch issue creation** — create child issues from a plan
6. **Data pipeline** — generate config files from templates

## Pitfalls

- Don't assume the agent will handle git merge conflicts — keep files disjoint
- Don't put "ask the user" anywhere in overnight prompts
- Don't chain tasks where task 2 depends on task 1's git push being pulled by terminal 2
- Include "Use uv run" explicitly — agents forget without it
- Include commit message templates — agents produce better commits with guidance
- Include "Do NOT ask the user any questions" explicitly in every prompt
- Include "git pull origin main before every push" — with 5 terminals, push races are guaranteed
- For TDD prompts, specify mock strategy: "Mock external dependencies, do NOT require network/licenses/mounts"
- End each prompt with "Post a brief progress comment on GH issues #X, #Y" for traceability
- When workspace-hub is not at ~/workspace-hub, discover it: `find /home -maxdepth 4 -name ".git" -type d` and check `/mnt/local-analysis/workspace-hub` on ace-linux machines
- When the repo owner isn't obvious from `git remote`, use `gh repo list --limit 10 --json name,owner` to find it, then use `--repo OWNER/REPO` flag on all gh commands
- When executing an overnight prompt (not just designing one), check `git log` for each target file BEFORE writing — another terminal or auto-sync may have already completed the work. Check for "Last Updated" dates in docs, committed scanner/test files, etc. Skip completed tasks, only do what's actually missing (e.g., generating a dashboard from an already-committed scanner). This avoids wasted tokens and potential git conflicts.
- **Copilot Gemini returns 403 for CLI**: `hermes chat --provider copilot --model gemini-2.5-pro -q "..."` fails with "PermissionDeniedError [HTTP 403]: Access to this endpoint is forbidden." Copilot's Gemini API blocks non-interactive CLI calls. **Fix**: Use `--provider huggingface --model google/gemini-2.5-pro` or `--provider openrouter --model google/gemini-2.5-pro` instead. Both work for unattended Gemini calls.
- **delegate_task cannot write to nested git repos**: When digitalmodel/ is a separate git repository nested inside workspace-hub (gitignored), subagents spawned via delegate_task cannot commit to it — sandbox isolation blocks cross-repo write access. **Fix**: Implement digitalmodel modules directly via execute_code's write_file + terminal (from within digitalmodel dir), or `cd` into the nested repo and use patch/write_file + terminal for git operations.
- Watch for `.git/index.lock` errors when multiple terminals push concurrently — `rm -f .git/index.lock` and retry
- **Dirty working tree blocks rebase-pull**: If `git pull origin main --rebase` fails with "You have unstaged changes", use `git stash && git pull origin main --rebase && git stash pop` then push. Common when other terminals or auto-sync leave uncommitted changes in the working tree.
- **Claude Code unattended mode requires the right permission mode**: In this environment, `claude -p` with default/auto permissions did NOT reliably allow unattended file writes — the run fell into read-only analysis or asked for approval. Tested working mode: `--permission-mode acceptEdits` for trusted-workspace unattended editing. Use `--permission-mode plan` for read-only/smoke-test runs. Do NOT use `--dangerously-skip-permissions` / bypass modes unless the user explicitly approves.
- **If stdin is closed with `</dev/null>`, pass the prompt as a positional argument, not via stdin**: `claude -p` requires input either from stdin or as a prompt argument. For unattended/background launches you should close stdin so Claude never waits on input, but then you must do `PROMPT=$(< prompt-file.md)` and call `claude -p ... "$PROMPT" </dev/null`. Piping the prompt on stdin and then adding `</dev/null>` causes the redirection to win and Claude errors because no input reaches Claude.
- **Best tested unattended launch pattern for Claude Code**: In a trusted repo, use `PROMPT=$(< prompt-file.md)` then `claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 "$PROMPT" </dev/null | tee logs/<run>.log`. This avoided the 3-second stdin warning and permitted unattended writes while keeping an auditable log.
- **Claude Code unattended runs need explicit non-interactive launch settings**: Naive `claude -p "Read <prompt-file> and execute it exactly."` launches are unreliable overnight. We observed three failure modes: (1) stdin warning / startup weirdness when stdin is left open, (2) `default`/`auto` permission modes silently block writes or fall back to analysis-only, and (3) prompts launched by file-path reference can no-op or produce poor audit trails. **Fix**: for unattended write-capable runs in a trusted workspace, load the prompt file into a shell variable, pass it as the positional prompt argument, and close stdin with `</dev/null>`. Use `--permission-mode acceptEdits` (tested working for unattended writes), `--no-session-persistence`, and log with `tee`. Pattern:
  ```bash
  PROMPT=$(< docs/plans/overnight-prompts/<date>/terminal-N-foo.md)
  claude -p \
    --permission-mode acceptEdits \
    --no-session-persistence \
    --output-format text \
    --max-budget-usd 20 \
    "$PROMPT" </dev/null | tee logs/claude-terminal-N.log
  ```
  For read-only smoke tests, use `--permission-mode plan`. Do **not** combine `</dev/null>` with feeding the prompt on stdin; if stdin is closed, the prompt must be passed as an argument. Do **not** use `--dangerously-skip-permissions` unless the user explicitly approves it.
- **Prompt files should encode rerun mode after first execution**: After an overnight batch actually runs, update the prompt pack so completed streams become "second-pass audit/hardening only" instead of remaining fresh implementation prompts. This prevents wasted reruns on already-complete work and preserves audit trail. Also add blocker-artifact requirements for flaky streams (for example `/tmp/terminal-2-blocker.md`) and an analysis-only fallback for permission-constrained streams.
- **`uv run python3 -c "..."` times out on large payloads**: Inline Python via `terminal("uv run python3 -c '...'")` silently hangs (returns empty after 60s) when processing large log files (e.g., 150K+ JSONL records). The `uv run` wrapper adds overhead that compounds with complex inline scripts. **Fix**: Write the script to `/tmp/phase_X_analysis.py` with `write_file`, then run `uv run python /tmp/phase_X_analysis.py`. This is reliable for arbitrarily large data processing. Same applies to `execute_code`'s `terminal()` — if the inner command uses `uv run python3 -c`, it will also timeout.
- **Prefer `execute_code` over terminal `python3 -c`** for JSON processing: complex f-strings and escaping in `terminal("python3 -c '...'")` can trigger command-deny gates or quoting issues. Save JSON to `/tmp/`, then process it in `execute_code` with `json.load()`. This is more reliable and avoids the terminal stdout cap.
- **Accidental bundling**: If `git status` shows your newly-written files as clean (not modified/untracked), another terminal's `git add .` or broad glob already committed them. Verify with `git ls-files <path>` and `git diff HEAD -- <path>`. If content matches, skip the commit — don't rewrite history. If content is wrong/incomplete, overwrite and commit as a fixup. This commonly happens when Terminal N runs `git add scripts/` and catches Terminal M's files that were written but not yet committed.
- **`execute_code` write_file mangles Python source**: When writing Python files via `execute_code`'s `write_file`, escaped characters in string literals (`\'`, `\"`, `\\n`) get double-escaped. Files end up with literal `\'` instead of `'`, causing `SyntaxError` in f-strings. Similarly, `read_file` inside `execute_code` returns `LINE_NUM|CONTENT` format — if you read-then-write, you get line numbers embedded in source. **Fix**: Use `mcp_write_file` (the direct tool) for all Python source files. Reserve `execute_code`'s `write_file` for data files, configs, and non-Python content. If you must use `execute_code`, construct the content as a raw string variable and pass it — don't use string interpolation with quotes.
- **Nested repos (gitignored subprojects)**: Some directories (e.g. `digitalmodel/`) are separate git repos nested inside the parent, listed in `.gitignore`. `git add -f` from the parent repo silently does nothing. Always check for `.git/` inside the target directory. If present, `cd` into that repo and commit/push there independently. Common sign: `git status` never shows your new files as staged despite `git add -f`.
- **No-Hermes licensed machines**: When a licensed Windows machine has Claude/Codex/Gemini CLIs but no Hermes, design prompts that reference a committed prompts file in the repo (`docs/plans/<machine>-prompts.md`) and use `claude -p "Read <file>, execute PROMPT N..."` pattern. Use `python` not `uv run` on Windows. Include a separate execution guide (`docs/plans/<machine>-execution-guide.md`) documenting which CLI runs in which terminal, since the operator won't have Hermes memory/skills to reference.
- **execute_code sandbox lacks write_file for external repos**: The sandbox used by execute_code has its own isolated filesystem — write_file inside execute_code writes to the sandbox, not the host workspace. **Fix**: Use terminal + heredoc or direct write_file (outside execute_code) for writing to the actual workspace. execute_code is best for: reading files, running commands with processing logic, and conditional branching — NOT for writing files to the host repo.
- **Direct implementation beats subagent delegation for quick wins**: When delegate_task subagents struggle with nested repo access or sandbox isolation, the fastest path is often to implement the module directly using write_file + terminal (patch tests → patch source → run pytest → iterate). This avoids the 10-20 tool-call overhead of subagent context setup and the cross-repo write failure mode entirely.
- **Claude non-interactive logs may stay at 0 bytes until completion**: `claude -p ... > log` can run for minutes with empty logs even while the process is healthy. Do NOT treat a zero-byte log as a failed launch. Verify with `ps`/PID checks and monitor for expected output artifact files instead.
- **Use output-artifact existence as the primary completion signal**: For planning-only Claude worker packs, require each prompt to write exactly one unique result file. In practice, `find docs/plans/.../results -type f` is a much better monitor than reading stdout logs. This is especially important when running 4-10 concurrent Claude workers.
- **Governance hooks can block long-running planning agents from writing final files**: In repos with session-governor/tool-call ceilings, a Claude worker may finish the analysis but fail at the final write step. If the log contains the full intended content, salvage it into the target artifact manually and then tighten the prompt / rerun a smaller worker for any missing deliverable.
- **Claude CLI logs may stay at 0 bytes until completion**: In unattended `claude -p --permission-mode acceptEdits ... </dev/null > log 2>&1` runs, stdout/stderr can remain fully buffered for minutes or the entire run. Do NOT use log growth as the primary health signal. Instead monitor (1) process liveness from PID files and (2) expected output artifact creation under the designated results directory. Result files were the reliable progress signal in the 2026-04-09 10-session and follow-up 4-session planning packs.
- **For plan-gated repos, use a staged Claude-worker cascade**: If no issues are `status:plan-approved`, first launch planning-only workers that each write one dossier/result file. Then, after those complete, launch a second Claude batch to convert approved candidates into execution packs and blocked candidates into issue-refinement drafts. Finally, launch a third ops-oriented batch to generate exact `gh` label/comment/edit command packs and implementation launch prompts. This 3-stage cascade turns ambiguous parallel work into operator-ready execution while preserving zero git contention and respecting hard-stop workflow gates.
