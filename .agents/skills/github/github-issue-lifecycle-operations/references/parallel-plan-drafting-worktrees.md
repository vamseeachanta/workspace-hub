# Archived Skill: `parallel-plan-drafting-worktrees`

Original path: `/home/vamsee/.hermes/skills/coordination/parallel-plan-drafting-worktrees`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/parallel-plan-drafting-worktrees`
Consolidation date: 2026-04-29

---

---
name: parallel-plan-drafting-worktrees
description: Draft multiple follow-up GitHub issue plans in parallel using isolated git worktrees plus background Claude Code print-mode runs, while keeping governance-safe boundaries and avoiding shared-file contention.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [planning, github, worktrees, claude-code, parallel, governance]
related_skills:
  - coordination/issue-planning-mode
  - development/git-worktree-workflow
  - autonomous-ai-agents/claude-code
  - github/github-comment-body-file-safety
---

# Parallel plan drafting with worktrees

Use this when multiple new follow-up issues need canonical plan drafts at the same time, but implementation is blocked by the planning gate.

Typical trigger:
- a parent execution wave reveals multiple new follow-up issues
- each follow-up needs a plan, not code
- you want parallel progress without colliding in `docs/plans/README.md` or other shared planning files

## Why this pattern exists

A safe parallel planning wave needs four things together:
1. isolated worktrees per issue
2. explicit planning-only prompts
3. backgroundable Claude runs with durable logs
4. centralized handoff/progress tracking

Running all planning in one checkout risks collisions. Using `delegate_task` risks sandbox write loss. This pattern avoids both.

## Core pattern

### 1. Create one worktree per plan issue

From the canonical repo root:

```bash
git worktree add -b nightly/2448-plan /mnt/local-analysis/worktrees/ws-2448-plan main
git worktree add -b nightly/2451-plan /mnt/local-analysis/worktrees/ws-2451-plan main
```

Rules:
- one issue per worktree
- branch names should encode the issue number and purpose
- verify each worktree is clean before launching Claude

### 2. Post a planning-start comment to each GitHub issue

Use `gh issue comment --body-file`, not inline `--body`, because markdown/code spans can be mangled by shell parsing.

Template:

```markdown
Planning start for #NNNN.

I’m drafting the follow-up plan in an isolated worktree so this can proceed in parallel with other planning lanes. Scope is limited to planning artifacts only: resource intel, candidate fix path, TDD/validation list, acceptance criteria, and risks. No implementation will be started without later user approval.
```

### 3. Write a prompt file per issue

Do not inline long Claude prompts into the shell. Save each prompt to a file, then have the launcher read it.

Prompt requirements:
- identify repo/worktree path explicitly
- identify issue number and target plan file path explicitly
- require reading the issue, relevant predecessor issue, template, and prior plan
- require live resource intelligence against the real target repo/worktree
- forbid implementation and forbid label changes
- if shared files are risky (`docs/plans/README.md`), explicitly forbid editing them in the parallel lane
- ask for a concise stdout summary including created file path and commit SHA if committed

### 4. Use a small launcher script per issue

Pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /mnt/local-analysis/worktrees/ws-2448-plan
mkdir -p tmp/claude-logs
claude -p "$(cat /tmp/plan-2448-prompt.md)" \
  --permission-mode auto \
  --allowedTools 'Read,Edit,Write,Bash' \
  --max-turns 30 \
  2>&1 | tee tmp/claude-logs/2448-plan.log
```

Why this works well:
- prompt remains auditable on disk
- launcher is rerunnable
- output is captured even if Claude returns minimal text
- logs live inside the worktree for later inspection

### 5. Start both launchers as Hermes background processes

Use Hermes background processes rather than shell `&` so you can poll and receive completion notifications.

Track:
- session_id
- worktree path
- log path
- expected plan path

### 6. Write a handoff file immediately

Create a handoff in `docs/handoffs/` that records:
- the active worktrees and branches
- issue numbers
- prompt file paths
- launcher paths
- background process session IDs
- log locations
- already-verified evidence from the parent execution wave
- next recommended monitoring steps

This makes recovery easy if context ends before the background lanes finish.

## Governance rules

- Planning lanes draft plan artifacts only.
- Do not implement any fix while the issue is still only a follow-up needing approval.
- Do not add or change `status:*` labels from the planning lane unless the user explicitly asked.
- Avoid shared-file contention by forbidding edits to `docs/plans/README.md` during parallel drafting; reconcile index updates centrally afterward.
- Use `gh issue comment --body-file` for all progress comments.

## Monitoring pattern

Poll Hermes background processes first:
- if still running, note session_id and keep waiting
- if complete, inspect the corresponding log file

Then verify in the worktree:

```bash
git -C /mnt/local-analysis/worktrees/ws-2448-plan status --short --branch
git -C /mnt/local-analysis/worktrees/ws-2448-plan log --oneline -1
```

Then verify the artifact exists:

```bash
test -f /mnt/local-analysis/worktrees/ws-2448-plan/docs/plans/2026-04-22-issue-2448-...md
```

Do not trust Claude stdout alone; verify file and git state directly.

## After completion

For each completed lane:
1. inspect the plan file
2. inspect the last commit and diff
3. record the commit SHA explicitly — this is useful in the next GitHub comment and later review traceability
4. reconcile any missing central index updates yourself in one controlled session
5. post the next GitHub comment (for example, plan drafted / review dispatch starting) using `--body-file`
6. keep implementation blocked until the normal plan-review flow completes

## Strong continuation pattern: review both newly drafted plans in parallel

Once the parallel drafting wave finishes, a reliable next step is to launch adversarial plan review in parallel as well.

Pattern:
1. verify each planning worktree is clean and the expected plan file exists
2. post a short GitHub comment per issue that cross-provider review is starting
3. dispatch one background `cross-review.sh ... --type plan` process per plan from the canonical repo root
4. track the Hermes background session IDs the same way you tracked the drafting lanes
5. wait for both reviews, then synthesize verdicts centrally before any approval decision

Example:

```bash
bash scripts/review/cross-review.sh /mnt/local-analysis/worktrees/ws-2448-plan/docs/plans/2026-04-22-issue-2448-assethold-smoke-followup.md all --type plan
bash scripts/review/cross-review.sh /mnt/local-analysis/worktrees/ws-2451-plan/docs/plans/2026-04-22-issue-2451-worldenergydata-test-followup.md all --type plan
```

Why this is useful:
- the drafting and review phases stay parallel end-to-end
- each issue gets a clear GitHub audit trail: planning start -> plan drafted -> review dispatch -> verdict summary
- implementation remains gated correctly while momentum stays high

## Multi-wave review loop for parallel plan lanes

A strong extension of this pattern is to keep the review/revision loop parallel too.

When both freshly drafted plans get adversarial review results back:
1. read the provider artifacts in the main session
2. treat any single `MAJOR` as blocking for that issue
3. patch each plan inside its own worktree only
4. commit the revised draft in that same worktree
5. post a short GitHub progress comment explaining what changed in response to review
6. rerun cross-review in parallel again
7. repeat until each issue reaches approval-ready review state

This preserves clean isolation between issues while still letting the orchestrator compare findings centrally.

### What to update after each review wave

Do not only patch the body text that triggered the review finding. Also sync the plan metadata so the artifact stays internally consistent.

For each revised plan, explicitly check and update:
- frontmatter `Review artifacts:` line
- `Artifact Map` review artifact paths
- `Adversarial Review Summary`
- `Path Decision Summary`
- acceptance criteria wording
- any verification commands that reviewers identified as too weak or ambiguous

### Reusable lessons from live use

1. Reviewers frequently catch inconsistencies between the plan body and the summary tables.
   - Example pattern: body says "class-level skip only" but summary says "module-level skip".
   - Fix both, not just the body.

2. Reviewers often attack verification quality rather than implementation scope.
   - Replace weak checks like broad `--collect-only`, global log greps, or split-run proof with job-scoped, runtime, or single-final-run proof when possible.

3. When a plan contains generated review artifact paths, keep them concrete after reruns.
   - If the second review wave produced new timestamped files, update the plan to those paths.
   - Do not leave placeholder or stale first-wave paths in the header or artifact map.

4. Runtime provenance matters.
   - If a reviewer questions whether a local repro really matched CI, run the provenance check now and encode the result into the plan before rerunning review.
   - Example: verifying `uv run --all-extras` can import `pytest_benchmark` changed the preferred decision branch for one plan.

5. Keep GitHub comments brief and wave-oriented.
   - Good pattern: "Wave 2 review issues addressed; rerunning cross-provider review now."
   - Avoid dumping the whole plan diff into the issue thread.

## Common pitfalls

### Pitfall: using delegate_task for plan drafting
Subagent sandboxing can lose writes. Use real worktrees plus Claude Code or direct tools instead.

### Pitfall: inline `gh issue create/edit/comment --body`
Markdown backticks and code spans can trigger shell substitution or mangling. Always use `--body-file`.

### Pitfall: letting multiple planning lanes edit `docs/plans/README.md`
This creates avoidable merge contention. Defer README/index reconciliation to a central cleanup step.

### Pitfall: assuming a quiet Claude run failed
Claude `-p` may produce sparse stdout. Verify via git status, log file, and file existence instead.

## Minimal checklist

- [ ] one isolated worktree per follow-up issue
- [ ] planning-start GitHub comments posted with `--body-file`
- [ ] prompt file written per issue
- [ ] launcher script written per issue
- [ ] Claude runs started as Hermes background processes
- [ ] handoff file written with session IDs and log paths
- [ ] shared planning files excluded from parallel editing
- [ ] post-run verification uses git/file checks, not stdout alone

## Best use case

This pattern is strongest when the user asks for "all three in parallel" but at least some of the work should remain in planning mode rather than immediate code changes.
