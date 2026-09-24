---
name: single-terminal-gh-issue-prompts
description: Generate live issue-specific Claude prompts for a single terminal, with repo-aware path contracts and plan-gate safety checks.
version: 1.0.0
author: Hermes Agent
category: software-development
license: MIT
tags: [github, prompts, claude, single-terminal, issue-execution, planning-gate]
---

# Single-Terminal GH Issue Prompts

Use when a user asks for issue-specific Claude prompts to execute GitHub issues in a single terminal.

## Why this skill exists

Static prompt templates are not enough for plan-gated repos. Before drafting issue-specific prompts, do a live eligibility pass against the current repo and issue set. If no issues are actually execution-ready, generate assessment-first prompts instead of pretending they are directly executable.

## Trigger conditions

Use this skill when the user asks for any of:
- "issue-specific prompts"
- "10 gh issue prompts"
- "Claude prompts for these issues"
- "single terminal Claude agent-team prompts"
- "prompts for actual repo issues"

## Workflow

1. Identify the live repo
- Run `git remote -v`
- Run `git rev-parse --show-toplevel`
- Use the real owner/repo in all GH calls

2. Fetch live issues
- Run `gh issue list --repo OWNER/REPO --state open --limit 200 --json number,title,labels,updatedAt`
- Do not invent issue numbers or status

3. Check execution readiness
- Count issues with `status:plan-approved` if the repo uses plan gates
- Inspect the repo policy files (`AGENTS.md`, relevant docs) when available
- If `status:plan-approved` count is zero, explicitly say so

4. Pull issue details for the selected set
- For each chosen issue, fetch body/labels via `gh issue view N --repo OWNER/REPO --json number,title,body,labels`
- Use the issue body to extract scope and deliverables

5. Inspect the repo for likely implementation surfaces
- Search likely directories/files before writing prompts
- Prefer existing module/test/doc locations over generic guesses
- Build prompts around real paths found in the repo

6. Choose prompt mode honestly
- If issues are truly execution-ready: generate execution prompts
- If issues are not plan-approved: generate assessment-first / verification-first prompts
- Never present blocked issues as safely executable without caveat

## Prompt construction rules

Each prompt should include:
- repo name
- issue number and exact title
- one-terminal internal role split (Planner, Implementer, Tester, Reviewer, Synthesizer)
- live issue scope summary
- owned paths
- read-only paths
- forbidden paths
- required workflow
- validation commands
- required output format

## Path-contract guidance

Build path contracts from the real repo structure.

Minimum pattern:
- `Owned paths:` exact directories likely to change
- `Read-only paths:` policy/docs/context areas
- `Forbidden paths:` unrelated repos/modules or high-risk shared surfaces

Do not use vague path contracts like "any relevant files." Prefer concrete repo-aware boundaries.

## Assessment-first fallback (important)

If the repo is plan-gated and the selected issues are not plan-approved:
- say that live plan-approved count is zero
- still provide useful issue-specific prompts
- frame them as:
  - verification-first
  - assessment-first
  - operator-ready execution dossiers
- instruct Claude not to implement blindly if approval is missing

Recommended wording:
- "First verify whether this issue is directly executable now. If plan approval is missing or scope is blocked, do not implement blindly; instead produce an operator-ready execution dossier."

## Selection heuristics

Good batches for prompt generation:
- recent issues in the same initiative
- tightly scoped sibling issues
- issues whose bodies clearly define deliverables
- issues whose likely file surfaces can be inferred from the repo

Avoid mixing:
- unrelated domains
- issues with unknown implementation surface
- issues already likely complete without first checking

## Output style

When delivering the prompts to the user:
- include a short live status note first
- mention real repo path and owner/repo if helpful
- clearly state whether prompts are execution-ready or assessment-first
- keep each prompt ready to paste into Claude
- when useful, also save the prompt pack into the repo under `docs/plans/<date>-single-terminal-claude-agent-team-prompts-<issue-range>.md`
- if you also perform read-only triage, save a second handoff doc such as `docs/plans/<date>-top3-issue-assessment-dossiers.md`

## Sequential execution loop for approved issue chains

When you are running a series of related issues one after another in fresh Claude terminals, use this loop:

1. Review the just-finished issue from live artifacts, not only the Claude terminal summary.
   - Read the created docs/review artifacts.
   - Read the live GitHub issue comment/label state.
   - Check repo dirtiness before preparing the next prompt.
2. Decide the next issue from live readiness, not just planned dependency order.
   - Prefer issues already carrying `status:plan-approved`.
   - If the next architectural dependency is not approved, fall back to the next concrete planning-ready issue or generate a planning-only prompt instead of pretending implementation is authorized.
3. Generate a new file-based prompt for the next issue with:
   - exact allowed write paths
   - explicit forbidden paths
   - live sibling/parent references
   - dirtiness warning if the repo has unrelated changes
4. Launch Claude with a file-based prompt and closed stdin.
   - Recommended pattern:
     `PROMPT=$(< docs/plans/<prompt-file>.md)`
     `claude -p --permission-mode acceptEdits --no-session-persistence --output-format text "$PROMPT" </dev/null | tee /tmp/<run>.log`
   - Use `--permission-mode plan` for safety-first read-only planning passes.
5. Monitor the subprocess with watch patterns or polling rather than assuming immediate stdout.
   - Good watch patterns: `APPROVED`, `MAJOR`, `status:plan-review`, `What changed`, `Final review verdict`
6. After completion, repeat the loop.

This pattern is especially useful for architecture/program issues where each completed child artifact becomes authoritative input for the next prompt.

## Delegated adversarial QA pattern

When the user says "continue" or asks you to take the next step after the prompt pack is drafted, use Claude subagents in read-only mode to adversarially review the prompts before finalizing execution advice.

Recommended pattern:
1. Split the issue range into at most 2-3 batches
   - e.g. `#2150-#2154` and `#2155-#2159`
2. Delegate each batch to a Claude subagent with instructions to:
   - inspect the live issue bodies
   - inspect neighboring repo structure
   - identify likely owned/read-only/forbidden paths
   - identify likely blockers and dependency chains
   - recommend exact validation commands
   - explicitly account for missing `status:plan-approved`
3. Merge the findings back into the saved prompt pack

Use this when:
- the issue cluster is non-trivial
- owned paths are not obvious from one quick scan
- you want adversarial review on prompt wording and dependency handling

## Top-3 assessment-dossier follow-up

After writing a full prompt pack, a strong next step is to delegate read-only Claude assessments for the top 3 most promising issues and save the results as a short operator dossier.

Recommended order in plan-gated repos:
1. choose the 2-3 best foundational issues
2. delegate one issue per Claude subagent
3. ask each subagent to return:
   - current approval status
   - likely owned paths
   - likely blockers / dependencies
   - exact first failing tests / validation commands to use after approval
   - verdict: already done / not done / uncertain
4. save the merged result to:
   - `docs/plans/<date>-top3-issue-assessment-dossiers.md`

This is especially useful when live `status:plan-approved` count is zero: it turns a blocked execution wave into an operator-ready approval and launch sequence.

## Example live status note

- `I used the live repo context from /path/to/repo and the current issues in OWNER/REPO.`
- `Open issues with status:plan-approved right now: 0.`
- `So these prompts are issue-specific and real, but they should be used in assessment/verification-first mode until approval is added.`

## Umbrella-issue execution wave pattern

When the user asks for a single Claude prompt to execute the "remaining work" under an umbrella issue, do not treat the umbrella approval as blanket authorization for every child issue.

Use this pattern:
1. Identify the umbrella issue and list all relevant child/follow-on issues from live GitHub state.
2. Separate them into:
   - already completed/closed
   - still open and explicitly approved
   - still open but not explicitly approved
3. Build the prompt around the live dependency state, not the original plan alone.
4. In the prompt, require Claude to verify child approval labels/markers before any write.
5. If a child issue is not approved, instruct Claude to stop short of implementation for that child and instead produce a concise execution dossier / blocker note.
6. Explicitly distinguish:
   - landed artifacts that should be consumed as authoritative inputs
   - stale docs/claims that now need reality-refresh
   - newly discovered adjacent scope that must not be silently absorbed

This is especially important for multi-issue waves where some upstream children are already closed and others remain open.

## Extra grounding rule for ecosystem-strengthening prompts

If the requested work strengthens a repo ecosystem (knowledge, intelligence, navigation, registry, docs), the generated prompt should explicitly consume:
- live GitHub issue state
- landed sibling/parent artifacts
- repo-level entry points (`docs/README.md`, ecosystem overview/capability docs, registry/index surfaces)
- cross-repo context documents when the repo is a control plane for other repos

Do not generate a prompt that acts as if the work is isolated to one directory when the feature is supposed to strengthen discoverability across the broader ecosystem.

## Approval-pack / GH-story follow-up pattern

When the user asks for both a Claude prompt and GH stories for review/approval:
- provide a bounded approval pack that separates:
  - approve-now work on existing issues
  - explicitly deferred scope discovered during reconnaissance
  - optional new follow-on issues for newly discovered breadth
- make the deferred scope concrete (exact issue/story title and why it should stay separate)
- call out any newly discovered assets that should NOT be silently absorbed into the current execution wave

## Live interactive Claude drift-recovery pattern

When you launch an interactive Claude Code execution run in tmux for a gated repo, actively monitor git status during the run instead of trusting the agent's own cleanup claims.

Use this pattern:
1. Before launch, record the initial dirty/untracked state so you know what was pre-existing.
2. During execution, periodically check BOTH:
   - tmux pane output
   - external `git status --short`
3. If Claude drifts into forbidden paths or unrelated files:
   - interrupt the session immediately
   - tell Claude exactly which paths are forbidden and require cleanup
   - independently verify cleanup from outside the session using `git diff --name-only`
4. If forbidden drift reappears after a cleanup claim:
   - hard-stop the session
   - manually delete/revert the forbidden artifacts yourself
   - salvage only the allowed file(s) if they are still good
5. If the issue turns out to be blocked mid-run by missing approvals or missing prerequisite artifacts, do not force implementation. Instead:
   - keep any valid planning/review artifact work
   - create the missing prerequisite issue
   - comment back on the blocked issue and umbrella issue with the exact unblock sequence

This pattern is especially important when using `claude --dangerously-skip-permissions` in tmux: the run may continue productively on the target file while also creating unrelated scripts, tests, config edits, or learned-skill artifacts. Treat external git state as authoritative.

## Pitfalls

- Do not assume issues are executable just because they are open
- Do not assume umbrella-issue approval automatically authorizes all open children
- Do not fabricate file paths without checking the repo
- Do not ignore repo hard gates from AGENTS.md / policy docs
- Do not claim "direct execution" when live eligibility says otherwise
- Do not give generic prompts when the user asked for actual repo/issues
- Do not silently absorb newly discovered adjacent scope into a saved execution prompt
- Do not trust an interactive Claude session's statement that cleanup is complete without verifying from outside the session

## Companion skills

- `gh-work-execution`
- `overnight-parallel-agent-prompts`
