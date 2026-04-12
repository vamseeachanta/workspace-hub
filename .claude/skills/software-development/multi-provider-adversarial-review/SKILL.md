---
name: multi-provider-adversarial-review
description: Dispatch parallel adversarial reviews to Codex and Gemini CLIs for plans or code artifacts. Use when the AI Review Routing Policy requires two- or three-provider review — architecture-heavy, security-affecting, cross-module, or high-stakes changes.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [code-review, adversarial, multi-provider, codex, gemini, quality]
    related_skills: [codex, requesting-code-review, github-issues, code-review]
---

# Multi-Provider Adversarial Review

## When to Use

Per [AI Review Routing Policy](docs/standards/AI_REVIEW_ROUTING_POLICY.md):
- **Two-provider** (Codex): default for non-trivial plans and code
- **Three-provider** (Codex + Gemini): architecture-heavy, security-affecting, cross-module, high-stakes, ambiguous requirements, or context-saturated

## Two Review Checkpoints

The user expects adversarial review at BOTH stages — not just implementation:

1. **Checkpoint 1 — Plan review**: before any implementation begins
2. **Checkpoint 2 — Implementation review**: before closing the issue / merging the PR

Do NOT skip the plan review. Do NOT defer all review to implementation.

## Step 1: Prepare Review Material

Write a self-contained review prompt to a temp file. The prompt must include:
- Reviewer role and expectations (be adversarial, no rubber-stamping)
- Full context (the reviewers have zero conversation history)
- The plan or diff to review
- Specific review questions to address
- Expected output format (verdict + severity-ranked findings)

```bash
# For plan review:
cat > /tmp/review-prompt.md << 'EOF'
# Adversarial Review Request: Issue #NNNN

## Your Role
You are an independent adversarial reviewer. Find gaps, risks, missing edge cases, and flawed assumptions. Do NOT rubber-stamp.

## Context
[Full background — what exists, what happened, what triggered this work]

## The Plan
[Complete plan content or issue body]

## Review Questions — Address ALL:
1. [Specific concern]
2. [Specific concern]
...

Provide verdict: APPROVE, MINOR (proceed with notes), or MAJOR (must address).
List every finding with severity (critical/high/medium/low).
EOF

# For implementation review:
# Use git diff instead of the plan
git diff main...HEAD > /tmp/diff-for-review.txt
# Then include the diff content in the review prompt
```

## Step 2: Dispatch Reviewers in Parallel

Use `codex exec` and `gemini exec` via background PTY processes:

```bash
# Codex review
cd /path/to/repo && codex exec "$(cat /tmp/review-prompt.md)" 2>&1 | tee /tmp/codex-review.txt
# Run with: terminal(command=..., pty=true, background=true, timeout=300)

# Gemini review (only if three-provider trigger met)
cd /path/to/repo && gemini exec "$(cat /tmp/review-prompt.md)" 2>&1 | tee /tmp/gemini-review.txt
# Run with: terminal(command=..., pty=true, background=true, timeout=300)
```

Then wait for both:
```
process(action="wait", session_id="<codex_id>", timeout=300)
process(action="wait", session_id="<gemini_id>", timeout=300)
```

Retrieve full output:
```
process(action="log", session_id="<codex_id>", limit=500)
process(action="log", session_id="<gemini_id>", limit=500)
```

## Step 3: Consolidate Findings

Deduplicate across providers. Structure as:

```markdown
## Checkpoint N: [Plan/Implementation] Adversarial Review — Codex + Gemini

### Verdicts
- **Codex**: [VERDICT] (N findings: X critical, Y high, Z medium)
- **Gemini**: [VERDICT] (N findings: ...)

### CRITICAL findings (must fix)
| # | Finding | Codex | Gemini |
|---|---------|-------|--------|
| C1 | [description] | ✓ | ✓ |

### HIGH findings (should fix before implementation)
...

### MEDIUM findings (address during implementation)
...

### LOW findings (nice to have)
...
```

## Step 4: Post to Issue/PR

```bash
gh issue comment NNNN --body-file /tmp/consolidated-review.md
```

## Post-Review: Acting on MAJOR Verdicts

When both reviewers return MAJOR, the plan must be revised before implementation. Typical pattern:

1. **Deduplicate findings** across providers — they often converge on the same core problems independently
2. **Phase the work** — both Codex and Gemini consistently recommend splitting monolith issues into 3-7 independent deliverables when scope is too large
3. **Revise the parent issue body** with findings incorporated, then create child issues for each phase
4. **Post the consolidated review** as an issue comment for traceability
5. **Do NOT proceed to implementation** until CRITICAL and HIGH findings are addressed in the revised plan

Common reviewer recommendations that recur across reviews:
- "Split into phases" (scope creep)
- "X is not a real health/smoke check" (inadequate verification)
- "Rollback is underspecified" (no atomic model)
- "Windows/cross-platform not addressed" (Linux-centric thinking)
- "Logging is not alerting" (passive vs active failure reporting)

## Retroactive Review Pattern

When commits were pushed without review (e.g., overnight batch runs), dispatch retroactive reviews. This was proven end-to-end on 2026-04-02 (40 commits, 0 reviews → 3 MAJOR verdicts, 27 findings, 9 follow-up issues):

1. **Audit**: `git log --oneline --since="..." | grep -vE '^(docs|chore|test|ci|style)'` to find unreviewed feature/fix commits
2. **Group by work stream**: cluster commits by issue number into 2-4 review batches
3. **Embed code in prompts**: Read files via `terminal("cat ...")` (NOT read_file which may cache). Truncate to ~20K chars per prompt. Codex sandbox CANNOT read mounted volumes.
4. **Write prompts to workspace**: Use `terminal("python3 -c \"...open().write()...\"")` to write prompt files to the repo dir where `$(cat .planning/quick/review-X.md)` works in real shell.
5. **Dispatch parallel**: `codex exec "$(cat .planning/quick/review-X.md)"` via `terminal(background=true, pty=true)`
6. **Consolidate**: Save to `scripts/review/results/TIMESTAMP-retroactive-review-codex.md` with tabular findings
7. **Create follow-up issues**: One issue per CRITICAL/HIGH finding (create labels first!)
8. **Comment on parent**: Link all follow-ups from the parent issue

This catches real bugs even after the fact — the 2026-04-02 retroactive review found shell injection, race conditions, schema mismatches, and ToS compliance gaps across solver queue and GTM scanner code.

## Writing Prompt Files for Codex

**The `/tmp/` trap**: Hermes `execute_code` and `write_file` write to a sandbox overlay — NOT the real filesystem. So `$(cat /tmp/review-prompt.md)` in a `terminal()` call will fail with "No such file or directory" because the file only exists in the sandbox.

**The workspace overlay trap**: Even `write_file` or `execute_code`'s `write_file()` targeting the workspace mount (e.g., `/mnt/local-analysis/workspace-hub/.planning/quick/file.md`) goes to sandbox overlay on mounted volumes.

**The fix**: Write prompt files via `terminal()` using Python:
```bash
terminal("cd /mnt/local-analysis/workspace-hub && python3 -c \"
content = '''... your prompt ...'''
with open('.planning/quick/review-prompt.md', 'w') as f:
    f.write(content)
\"")
```
Then dispatch: `codex exec "$(cat .planning/quick/review-prompt.md)"`

Alternatively, for short prompts, embed code content directly in the `$(cat)` heredoc — but beware shell metacharacters in code will break heredocs. The Python `open().write()` approach is most robust.

## Pitfalls

1. **Codex sandbox blocks file reads** — Codex `exec` runs in a bwrap sandbox that may block filesystem access. Pass ALL context in the prompt text itself, not via file references. The prompt must be fully self-contained.

2. **Gemini capacity limits** — `gemini-3.1-pro-preview` can hit 429 MODEL_CAPACITY_EXHAUSTED errors. Gemini CLI retries automatically but may take longer. Allow extra timeout.

3. **Shell escaping** — Long prompts with backticks, single quotes, and parentheses break `gh issue comment --body '...'`. Always use `--body-file` instead. Same for `gh issue edit --body` — always use `--body-file`.

4. **Prompt injection via $(cat)** — Using `$(cat /tmp/file.md)` to inject into CLI args works but the file content must not contain unescaped shell metacharacters that could break the outer command. The temp-file approach is robust.

5. **Review timing** — User expects review at BOTH plan and implementation stages. Do not skip plan review or defer everything to code review. This was explicitly corrected during first use.

6. **Verdict thresholds**:
   - APPROVE: no critical or high findings
   - MINOR: no critical findings, some high/medium — proceed with notes
   - MAJOR: any critical findings, or multiple high findings — must revise before proceeding

7. **Don't fix the issue body inline with shell** — Complex issue bodies with code blocks, backticks, parentheses, and single quotes will break shell heredocs. Always `write_file` to a temp path, then `gh issue edit --body-file /tmp/file.md`.

8. **Gemini exec syntax** — Use `gemini exec "prompt"` not `gemini "prompt"`. Same pattern as `codex exec "prompt"`.

9. **Codex output is duplicated** — Codex `exec` prints the full review twice in the terminal output (once during streaming, once as final summary). When parsing with `process(action="log")`, the review content appears doubled. Extract only the first occurrence or use the tee'd file.

10. **Sandbox filesystem mismatch** — On machines with mounted volumes (e.g., /mnt/local-analysis/), the `write_file` and `patch` tools may write to a sandbox overlay instead of the real mount. Files appear written but don't land on disk. Use `execute_code` with `from hermes_tools import write_file` for mounted filesystems. ALWAYS verify with `terminal("wc -l /path")` after writing. This caused a broken commit where old file content was committed instead of new implementation — the entire Checkpoint 2 review then reviewed stale code, producing false MAJOR findings.

11. **Don't prematurely revert "drift"** — If an AI tool update intentionally modifies files (e.g., Hermes rewrites its shebang to point to the venv Python), reverting that change will break the tool. Always understand WHY a file was modified before reverting. This was a real incident: reverting the Hermes shebang from venv path back to `#!/usr/bin/env python3` caused `ModuleNotFoundError` because system Python lacked venv dependencies.

12. **Stale file content in review prompts** — When preparing Checkpoint 2 (implementation review), `read_file` may serve cached pre-commit content if the file was read earlier in the session. The reviewer then reviews the OLD code, not the new implementation, producing false MAJOR findings ("only 4 tools" when there are actually 7). **Always read files fresh for review prompts** — use `terminal("cat path/to/file")` or `git show HEAD:path/to/file` to get the actual committed content. Verify with `grep -c 'key_function_name'` before sending to reviewers.

13. **Reviewers catch real schema/wiring bugs** — Even when findings about the code itself are based on stale content, reviewers often catch legitimate integration issues (e.g., "the scheduler doesn't consume the new `schedule_by_machine` field"). These downstream wiring bugs are some of the highest-value review findings. Always check whether consumer scripts need updating when you add new config schema fields.

14. **git commit captures staged content, not working tree** — If you `git add` files, then overwrite them with `write_file` (to sandbox), `git commit` captures the OLD staged content. The fix: write via `execute_code` to the real filesystem, THEN `git add`, THEN `git commit`. If you discover this after committing, `git commit --amend` after re-adding the correct files.

15. **execute_code /tmp/ is NOT real /tmp/** — Files written by `execute_code` (including its `write_file()` and `terminal()`) to `/tmp/` exist only in the sandbox overlay. A subsequent `terminal()` call (which runs in the real shell) cannot see them. This caused the first Codex dispatch attempt to fail with "No such file or directory" when `$(cat /tmp/review-prompt.md)` was used. The fix: write review prompt files to the workspace directory via `terminal("python3 -c '...'")` so both Hermes tools and real shell commands can see them. Clean up afterward (`rm .planning/quick/review-*.md`).

16. **Full end-to-end after implementation** — After implementing and getting adversarial review, the next logical step is always: (a) verify the wiring works (run the new script, regenerate crontab, etc.), (b) create follow-up issues for deployment to other machines and for items deferred during review (supply chain hardening, simulated breakage testing, active push notifications), (c) document everything in a closing comment on the parent issue.

17. **Do NOT write long review prompts via shell heredoc inside `terminal()` when they contain markdown code spans/fences** — A real failure mode on 2026-04-12: writing a review prompt with `bash -lc 'cat <<'"'"'EOF' ... EOF'` caused shell interpretation to break and lines from the embedded markdown/code content were executed as commands (`scripts/cron/weekly-hermes-parity-review.sh`, YAML lines, benchmark scripts), producing side effects and a timeout. For long self-contained prompts on mounted filesystems, prefer `execute_code`/`write_file()` to create the prompt file, then verify with `wc -l path/to/prompt.md` before dispatching Codex/Gemini. If you must use shell, avoid embedding backticks/code fences and verify the file content before launching reviewers.

## Post-Review: Batch Follow-Up Issue Creation from Findings

When review findings produce multiple follow-up issues (common with retroactive reviews across multiple streams), create them efficiently:

1. **Create labels first** — `gh issue create` silently fails if ANY label doesn't exist. Check `gh label list | grep <name>` and create missing labels with `gh label create "<name>" --description "..." --color "<hex>"` BEFORE creating issues.
2. **Write body files via `terminal("python3 -c '...open().write()...'")`** — avoids both sandbox overlay and shell escaping issues.
3. **Loop in `execute_code`** — create all issues in one script, collecting URLs.
4. **Comment on parent issue** — link all child issues with a consolidated summary using `gh issue comment <parent> --body-file`.

## Post-Review: Creating Phased Child Issues

When the revised plan splits into phases, create child issues efficiently using `execute_code` with a loop rather than manual `gh issue create` calls. Each child issue should:
- Reference the parent issue number in the title (e.g., `Phase 1: ... (#1668)`)
- Include `## Parent: #NNNN` as the first line of the body
- Use `--body-file /dev/stdin << 'BODY' ... BODY` heredoc pattern to avoid shell escaping issues
- Share the same labels as the parent
- Have independent acceptance criteria that don't depend on other phases

After creating all child issues, update the parent body to link them (replace `#PENDING_N` placeholders with actual issue numbers), then use `gh issue edit --body-file`.

## Consolidating Review into Issue Revision

The full workflow after MAJOR verdicts is:

1. Write consolidated review findings as issue comment (for traceability)
2. Write raw reviewer output as a second comment (in `<details>` blocks)
3. Revise the parent issue body — incorporate all CRITICAL/HIGH findings
4. Create phased child issues
5. Update parent body with child issue links
6. Comment noting the review gate policy (both checkpoints)

Do all issue body edits via `write_file` to temp path + `gh issue edit --body-file`. Never try to pass complex markdown through shell arguments.

## Three-Provider Trigger Checklist

Add Gemini when ANY apply:
- [ ] Architecture-heavy change (cross-module/cross-repo structural)
- [ ] Research-heavy task (synthesizing external sources)
- [ ] Ambiguous requirements (third interpretation reduces risk)
- [ ] High-stakes delivery (production, security, data integrity)
- [ ] Context saturation (Claude's context is full)

Skip Gemini for: routine implementation, standard refactors, test additions, docs-only changes.
