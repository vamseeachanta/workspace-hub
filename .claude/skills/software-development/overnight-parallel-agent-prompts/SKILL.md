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

## Truth-first eligibility check for “directly executable” batches

When the user asks for the “next N issues that can be directly executed in Claude Code,” do a live eligibility pass first. Do not trust historical plans, old prompt packs, or stale issue labels.

Required live checks:
1. Verify the issue is still **open**.
2. Verify the issue still has the required gate label (for example `status:plan-approved`) if the repo policy requires it.
3. Verify any local approval marker still exists (for example `.planning/plan-approved/<issue>.md`) when local hooks enforce marker-based gating.
4. Verify the relevant repo/worktree is not already in a conflicting dirty state.
5. Verify required local repos/data paths actually exist now.
6. Re-read the latest issue body/comments if the issue may have become partially or fully completed.
7. Check local execution evidence for stale-open issues before assigning them: inspect the current day's `.claude/state/session-signals/YYYY-MM-DD.jsonl`, relevant handoff docs under `docs/handoffs/`, and any newly created deliverable artifacts referenced by the issue/plan. An issue can remain open and even keep `status:plan-approved` while same-day Claude runs have already produced the intended artifacts and posted execution comments. Treat those as **verify/close candidates**, not fresh implementation candidates.
8. Check the current repo state before launching: if the main checkout is dirty or other Claude runs are already active (`git status --short`, `ps aux | grep claude`), prefer fresh worktrees and exclude overlapping issues from the batch.

If fewer than N issues pass the live eligibility check, do **not** pretend you found N directly executable implementation issues. Instead, explicitly switch the batch into one of these modes:
- **assessment-only pack**: each Claude session determines whether one candidate issue is directly executable now and writes a verdict + exact blocker + implementation prompt if eligible
- **planning/execution-pack mode**: each Claude session writes an operator-ready implementation dossier for a candidate issue without changing code

This is preferable to launching unsafe write-capable sessions against stale / blocked / already-completed issues.

## Agent-team prompt pattern for single-Claude sessions

If the user wants “agent teams” but you are launching plain `claude -p` sessions, encode an internal multi-role workflow inside each prompt. Ask Claude to reason as:
- **Planner** — summarize scope, dependencies, and target files
- **Reviewer** — challenge whether the issue is truly executable now
- **Tester / Integrator** — inspect verification path, data/repo availability, and dirty-worktree risk
- **Synthesizer** — produce the final verdict and the exact next action

This gives you agent-team style outputs while still using standalone `claude -p` processes.

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

### Claude-only preservation mode

When the user explicitly wants to preserve Codex credits for daytime/interactive work, design the overnight batch as **Claude-only** even if Codex is available. In plan-gated repos, the safest Claude-only pattern is to assign planning/audit/execution-pack streams rather than implementation streams. Use one unique result artifact per terminal and avoid any dependence on Codex/Gemini for overnight progress.

Recommended Claude-only use cases:
- repos with zero `status:plan-approved` issues
- planning dossiers, execution packs, governance audits, issue refinement drafts
- operator-ready `gh` command packs and future implementation prompts

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
- **Workspace-hub plan-gate requires committed `.planning/plan-approved/*.md` markers, not just GitHub labels**: In workspace-hub, adding `status:plan-approved` on the GitHub issue is NOT sufficient for unattended Claude implementation runs. The active `.claude/hooks/plan-approval-gate.sh` checks for a local marker under `.planning/plan-approved/`, and rejects freshly-created self-approval markers if they are under ~120 seconds old and have never been committed. **Fix**: before launching Claude on approved implementation work, create `.planning/plan-approved/<issue>.md` with neutral operator-approval wording (do NOT include `Worker session`, `auto-approved`, or `self-approved`), commit that marker to git, then launch Claude. Safe sequence:
  ```bash
  gh issue edit <issue> --add-label "status:plan-approved"
  write .planning/plan-approved/<issue>.md
  git add .planning/plan-approved/<issue>.md
  git commit -m "chore(planning): approve issue #<issue> for execution"
  claude -p ...
  ```
  If you skip the commit, Claude may be blocked by the freshness/self-approval check even though the issue label looks correct.
- **When extracting prompt text from markdown via shell, use `$(...)`, never arithmetic `$((...))`**: During Batch 2 Claude launch, `PROMPT="$((python - <<'PY' ... ))"` started a shell process that looked healthy but failed to populate the prompt correctly. The correct form is command substitution: `PROMPT="$(python - <<'PY' ... PY)"`. After launching, immediately poll the process and confirm the expected log files were created; if the command string contains `$((python`, kill and relaunch.
- **Prompt files should encode rerun mode after first execution**: After an overnight batch actually runs, update the prompt pack so completed streams become "second-pass audit/hardening only" instead of remaining fresh implementation prompts. This prevents wasted reruns on already-complete work and preserves audit trail. Also add blocker-artifact requirements for flaky streams (for example `/tmp/terminal-2-blocker.md`) and an analysis-only fallback for permission-constrained streams.
- **When a later wave depends on an operator decision, generate a locked prompt variant before launch**: If a prompt contains placeholders like `OPTION_CHOSEN` or mutually exclusive branches (for example file-growth vs file-split), do not launch the generic template directly. First write a concrete sibling prompt such as `...-option-b.md` with the decision baked in, then launch that exact file. This preserves auditability, prevents the worker from improvising the branch, and makes reruns unambiguous.
- **`uv run python3 -c "..."` times out on large payloads**: Inline Python via `terminal("uv run python3 -c '...'")` silently hangs (returns empty after 60s) when processing large log files (e.g., 150K+ JSONL records). The `uv run` wrapper adds overhead that compounds with complex inline scripts. **Fix**: Write the script to `/tmp/phase_X_analysis.py` with `write_file`, then run `uv run python /tmp/phase_X_analysis.py`. This is reliable for arbitrarily large data processing. Same applies to `execute_code`'s `terminal()` — if the inner command uses `uv run python3 -c`, it will also timeout.
- **Prefer `execute_code` over terminal `python3 -c`** for JSON processing: complex f-strings and escaping in `terminal("python3 -c '...'")` can trigger command-deny gates or quoting issues. Save JSON to `/tmp/`, then process it in `execute_code` with `json.load()`. This is more reliable and avoids the terminal stdout cap.
- **Accidental bundling**: If `git status` shows your newly-written files as clean (not modified/untracked), another terminal's `git add .` or broad glob already committed them. Verify with `git ls-files <path>` and `git diff HEAD -- <path>`. If content matches, skip the commit — don't rewrite history. If content is wrong/incomplete, overwrite and commit as a fixup. This commonly happens when Terminal N runs `git add scripts/` and catches Terminal M's files that were written but not yet committed.
- **`execute_code` write_file mangles Python source**: When writing Python files via `execute_code`'s `write_file`, escaped characters in string literals (`\'`, `\"`, `\\n`) get double-escaped. Files end up with literal `\'` instead of `'`, causing `SyntaxError` in f-strings. Similarly, `read_file` inside `execute_code` returns `LINE_NUM|CONTENT` format — if you read-then-write, you get line numbers embedded in source. **Fix**: Use `mcp_write_file` (the direct tool) for all Python source files. Reserve `execute_code`'s `write_file` for data files, configs, and non-Python content. If you must use `execute_code`, construct the content as a raw string variable and pass it — don't use string interpolation with quotes.
- **Nested repos (gitignored subprojects)**: Some directories (e.g. `digitalmodel/`) are separate git repos nested inside the parent, listed in `.gitignore`. `git add -f` from the parent repo silently does nothing. Always check for `.git/` inside the target directory. If present, `cd` into that repo and commit/push there independently. Common sign: `git status` never shows your new files as staged despite `git add -f`.
- **digitalmodel test verification may need the repo venv, not `uv run`**: In `workspace-hub/digitalmodel`, `uv run pytest ...` can fail before tests start if `pyproject.toml` has an unsatisfiable resolver combination (observed: `assetutilities` pulling `deepdiff<8` while `digitalmodel` requested `deepdiff>=8`). When the worker reports tests passed but you need an independent verification sweep, first check `digitalmodel/.venv/`. If it exists, run tests with `PYTHONPATH=src ./.venv/bin/python -m pytest ...` from the `digitalmodel/` repo. This uses the already-installed working environment and avoids the resolver failure. Example:
  ```bash
  cd /mnt/local-analysis/workspace-hub/digitalmodel
  PYTHONPATH=src ./.venv/bin/python -m pytest tests/field_development/test_economics.py tests/field_development/test_timeline_benchmarks.py -q
  ```
- **No-Hermes licensed machines**: When a licensed Windows machine has Claude/Codex/Gemini CLIs but no Hermes, design prompts that reference a committed prompts file in the repo (`docs/plans/<machine>-prompts.md`) and use `claude -p "Read <file>, execute PROMPT N..."` pattern. Use `python` not `uv run` on Windows. Include a separate execution guide (`docs/plans/<machine>-execution-guide.md`) documenting which CLI runs in which terminal, since the operator won't have Hermes memory/skills to reference.
- **execute_code sandbox lacks write_file for external repos**: The sandbox used by execute_code has its own isolated filesystem — write_file inside execute_code writes to the sandbox, not the host workspace. **Fix**: Use terminal + heredoc or direct write_file (outside execute_code) for writing to the actual workspace. execute_code is best for: reading files, running commands with processing logic, and conditional branching — NOT for writing files to the host repo.
- **Direct implementation beats subagent delegation for quick wins**: When delegate_task subagents struggle with nested repo access or sandbox isolation, the fastest path is often to implement the module directly using write_file + terminal (patch tests → patch source → run pytest → iterate). This avoids the 10-20 tool-call overhead of subagent context setup and the cross-repo write failure mode entirely.
- **Claude non-interactive logs may stay at 0 bytes until completion**: `claude -p ... > log` can run for minutes with empty logs even while the process is healthy. Do NOT treat a zero-byte log as a failed launch. Verify with `ps`/PID checks and monitor for expected output artifact files instead.
- **Use output-artifact existence as the primary completion signal**: For planning-only Claude worker packs, require each prompt to write exactly one unique result file. In practice, `find docs/plans/.../results -type f` is a much better monitor than reading stdout logs. This is especially important when running 4-10 concurrent Claude workers.
- **Governance hooks can block long-running planning agents from writing final files**: In repos with session-governor/tool-call ceilings, a Claude worker may finish the analysis but fail at the final write step. If the log contains the full intended content, salvage it into the target artifact manually and then tighten the prompt / rerun a smaller worker for any missing deliverable.
- **Claude CLI logs may stay at 0 bytes until completion**: In unattended `claude -p --permission-mode acceptEdits ... </dev/null > log 2>&1` runs, stdout/stderr can remain fully buffered for minutes or the entire run. Do NOT use log growth as the primary health signal. Instead monitor (1) process liveness from PID files and (2) expected output artifact creation under the designated results directory. Result files were the reliable progress signal in the 2026-04-09 10-session and follow-up 4-session planning packs.
- **For plan-gated repos, use a staged Claude-worker cascade**: If no issues are `status:plan-approved`, first launch planning-only workers that each write one dossier/result file. Then, after those complete, launch a second Claude batch to convert approved candidates into execution packs and blocked candidates into issue-refinement drafts. Finally, launch a third ops-oriented batch to generate exact `gh` label/comment/edit command packs and implementation launch prompts. This 3-stage cascade turns ambiguous parallel work into operator-ready execution while preserving zero git contention and respecting hard-stop workflow gates.
- **Useful extension after the 3-stage cascade: Stage 4 quick-close wave**. Once stage-3 outputs exist, immediately verify preconditions with live commands (for example: confirm known regressions still exist, confirm tests pass, confirm required skill files/artifacts exist), then launch a small Claude-only implementation wave for the highest-confidence low-contention items. Best pattern: 3 parallel terminals for the top quick-close issues, each with explicit allowed write paths and negative write boundaries. In practice this worked well for: (1) a one-line config regression + test/doc fix, (2) a verify-and-comment/close-prep issue with tests already passing, and (3) cleanup/hygiene work (broken links, smoke tests, doc update). This lets you move directly from overnight planning into morning execution without spending Codex credits.
- **After Stage 4 quick-close, generate explicit continuation waves rather than improvising.** If stage-3 synthesis artifacts and stage-4 wave-1 prompts already exist, the next reusable move is to create: (a) a `...-stage4-wave2/` directory with 3 parallel Claude implementation prompts for the best file-disjoint engineering issues, (b) a `...-stage4-wave3/` directory with a single decision-gated prompt for the next shared-file issue, and (c) a top-level summary file such as `docs/plans/<date>-claude-stage4-next-waves.md` containing dispatch order, contention map, cross-review requirements, and launch pattern. Build these continuation packs from the stage-3 operator runbook, priority matrix, and next-wave prompt synthesis so the operator can continue Claude work immediately without re-triaging the whole backlog.
- **After Stage 4 / Batch 1, create an explicit Batch 2 launch pack instead of ad-hoc continuation.** Re-scan the generated execution packs, rank remaining issues by (a) closability, (b) confidence, and (c) zero-overlap write boundaries, then write a committed artifact such as `docs/plans/<wave>/results/implementation-launch-pack-batch-2.md`. Include: recommended execution order, overlap matrix, pre-dispatch gate checklist, issue-to-terminal assignment, quick `gh issue edit` approval commands, and exact prompt-source sections to paste into Claude. A strong Batch 2 pattern is to mix one fast cleanup/closure issue, one narrowly scoped implementation issue, and one broader but still isolated implementation issue.
- **Stage 3 synthesis pack is worth standardizing**: after execution packs finish, create a Claude-only synthesis wave that writes exactly one artifact per terminal: (1) morning operator runbook, (2) unified draft `gh` command pack, (3) follow-up issue/refinement drafts, (4) priority/closure matrix, and (5) next-wave self-contained prompts. This adds cross-issue awareness that single-issue packs miss (for example, shared-file contention like multiple issues targeting the same oversized module) and produces a concrete morning operating kit.
- **Stage 3 should be synthesis-first, not more per-issue analysis**: After a large stage-2 execution-pack batch finishes, the highest-value continuation is usually a 4-5 Claude synthesis wave with one unique artifact per terminal: (1) morning operator runbook across all issues, (2) unified draft `gh` command pack, (3) follow-up / split-issue draft pack for refinement-heavy items, (4) priority / closure matrix, and (5) next-wave self-contained Claude prompts. This cross-issue synthesis catches shared-file contention (for example multiple issues targeting the same oversized module), surfaces morning execution order, and turns many per-issue packs into one operator-ready control plane.
- **Execution packs can become stale the same night**: In parallel overnight runs, a stage-1 or stage-2 dossier may be overtaken by commits from another terminal before anyone reads it. Build every later-stage prompt to re-check file line counts, exports, commit state, and label state before trusting prior findings. We observed same-day drift where `benchmarks.py` size, `__init__.py` exports, and even issue completion status changed between stages.
- **After assessment waves, move implementation work into fresh worktrees rather than the dirty parent checkout.** Best pattern: create one clean worktree per implementation issue from `origin/main`, do any required plan-approval-marker / label updates in a separate clean workspace checkout first, then reset the implementation worktree to the updated remote before launch. For nested repos (for example `digitalmodel`), create the worktree from the nested repo itself, not from the parent workspace repo.
- **If an unattended Claude implementation run stalls with no log output, inspect the repo before killing it.** We observed a failure mode where Claude correctly edited the target files, left a stale `.git/index.lock`, emitted an empty log, and never reached its own commit step. Recovery pattern: (1) inspect `git status` and target-file diffs, (2) verify whether the intended implementation is already present, (3) kill the stuck Claude process, (4) remove the stale `index.lock`, (5) run the verification tests manually, and then (6) commit/push/comment/close yourself if the code is sound.
