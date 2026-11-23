# Skill Ecosystem Curation Report — 2026-05-14

Issue: #2703
Worktree: `/mnt/local-analysis/workspace-hub-2703`
Branch: `issue-2703-skill-curation`

## Scope

This pass executed the issue-approved plan for:

1. mining recent Hermes-approved provider session logs for reusable workflow skills; and
2. curating the `.claude/skills/` tree without touching forbidden zones.

Forbidden zones were treated as read-only and were not edited:

- `.claude/skills/_archive/`
- `.claude/skills/_internal/`
- `.claude/skills/_core/`
- `.claude/skills/_runtime/`

## Inputs inspected

- `logs/orchestrator/hermes/skill-patches.jsonl`
- `logs/orchestrator/hermes/session_20260501.jsonl` through `logs/orchestrator/hermes/session_20260514.jsonl`
- `~/.hermes/logs/curator/20260506-081514/`
- `~/.hermes/logs/curator/20260513-081534/`
- `.claude/skills/`
- `.claude/rules/`
- Git history and hooks involved in skill-content scanning

## Skills mined

### 1. `subagent-write-verification`

Path: `.claude/skills/workspace-hub-learned/subagent-write-verification/SKILL.md`
Commit: `e4d8ec075b154e57d18657810aba62af9f7f5273`
Trace entry: `logs/orchestrator/hermes/skill-patches.jsonl`

Reusable pattern:

Subagent summaries that claim files were written are not sufficient evidence. The main session must independently verify claimed paths with filesystem and git checks before committing or referencing them downstream.

Source provenance:

- `logs/orchestrator/hermes/session_20260501.jsonl`: sessions `20260501_133025_de04d9`, `20260501_133730_f4d221`, `20260501_134118_f7e0fb`, `20260501_134503_d51cba`, `20260501_135803_ffeb24`
- Issue #2703 hard rule `feedback_subagent_write_phantom`
- Current #2703 execution: Claude Code drafts were accepted only after independent `ls`, line count, byte count, SHA, git-status, and scanner checks.

### 2. `git-operation-serialization-preflight`

Path: `.claude/skills/workspace-hub-learned/git-operation-serialization-preflight/SKILL.md`
Commit: `d506fd1ec2c17c94e82844f80c51279e091b19b6`
Trace entry: `logs/orchestrator/hermes/skill-patches.jsonl`

Reusable pattern:

Before any mutating git operation in a multi-agent checkout, check for active git writers and lock files; serialize commits to avoid index-lock contention and attribution drift.

Source provenance:

- `logs/orchestrator/hermes/session_20260501.jsonl`: session `20260501_075259_54868f` ran git process and index-lock checks before a skill commit.
- `logs/orchestrator/hermes/session_20260501.jsonl`: sessions `20260501_152122_c2a9d7` and `20260501_153626_bc1b96` repeated the same pattern before committing skill content.
- Issue #2703 hard rule `feedback_multi_agent_commit_serialization`.

### 3. `credential-scanner-safe-skill-authoring`

Path: `.claude/skills/workspace-hub-learned/credential-scanner-safe-skill-authoring/SKILL.md`
Commit: `a8d28b8dfa2cd6c7839ad48f85f68e4dbf306e90`
Trace entry: `logs/orchestrator/hermes/skill-patches.jsonl`

Reusable pattern:

Operational skills can legitimately discuss credentials, env files, and service management, but skill bodies must avoid literal secret-access patterns. The safe convention is to use placeholders such as `${HERMES_HOME}/<env-file>` and route literal commands to runbooks instead of embedding scanner-triggering examples in skills.

Source provenance:

- Issue #2703 hard rule `feedback_skill_content_scanner_docs_tension`.
- `logs/orchestrator/hermes/skill-patches.jsonl`: 2026-05-14 commit `6702bf5ac77d534476a284d99452716c214e51a9` for `operations/telegram-hermes-bot`.
- `logs/orchestrator/hermes/session_20260501.jsonl`: sessions `20260501_152122_c2a9d7` and `20260501_153626_bc1b96` ran scanner/secret checks before skill commits.

Scanner result:

- The file passes the blocking skill-content scanner.
- It intentionally produces one non-blocking medium warning for mentioning privileged/service-management content; this is expected for the skill's subject matter.

## Curation actions taken

### Canonicalized `workspace_hub_learned` into `workspace-hub-learned`

Commit: `21af1fb608cec511a8f4a340459a87fb51226a8e`
Trace entry commit: `4b09223be`

Canonical choice: `workspace-hub-learned`.

Rationale:

- `workspace-hub-learned` already held the active learned-skill corpus.
- `workspace_hub_learned` held only two skills.
- Moving the two underscore-group skills into the hyphenated group removes one near-duplicate top-level namespace without changing skill bodies beyond `category:` frontmatter.

Moved skills:

- `.claude/skills/workspace_hub_learned/gtm-demo-validation-cache-regression-repair/SKILL.md` → `.claude/skills/workspace-hub-learned/gtm-demo-validation-cache-regression-repair/SKILL.md`
- `.claude/skills/workspace_hub_learned/plan-review-prompt-refresh-after-plan-edits/SKILL.md` → `.claude/skills/workspace-hub-learned/plan-review-prompt-refresh-after-plan-edits/SKILL.md`

## Curation audit findings

### Suspected "8 empty top-level dirs" from issue body

The issue body's list was stale by the time execution ran.

Observed state after this pass:

| Directory | State | Action |
|---|---:|---|
| `business_admin` | 1 skill | Left in place; not empty. Still a naming inconsistency because of underscore. |
| `business-finance` | 1 skill | Left in place; not empty. |
| `business-marketing` | 1 skill plus references | Left in place; not empty. |
| `data-science` | 1 skill | Left in place; not empty. |
| `devtools` | 1 skill | Left in place; not empty. |
| `eng` | 8 flat markdown files, 0 `SKILL.md` | Deferred; this is not empty, but it is non-conforming. |
| `_runtime` | reserved forbidden zone | Not touched by hard rule. |
| `session-logs` | missing | No action needed. |

### Other naming and shape findings surfaced, not auto-fixed

- `business_admin` remains as the only non-forbidden top-level group containing an underscore.
- `eng/` contains flat markdown files directly under `.claude/skills/eng/` instead of `skill-name/SKILL.md` directories:
  - `.claude/skills/eng/bsee-field-pipeline.md`
  - `.claude/skills/eng/diffraction-spec-converter.md`
  - `.claude/skills/eng/enigma-safety-analysis.md`
  - `.claude/skills/eng/fatigue-assessment.md`
  - `.claude/skills/eng/hull-analysis-setup.md`
  - `.claude/skills/eng/hull-library-lookup.md`
  - `.claude/skills/eng/orcaflex-template-library.md`
  - `.claude/skills/eng/pipeline-integrity.md`
- No non-forbidden `Skill.md` casing variants were found.
- No non-forbidden `SKILL.md` files missing frontmatter `name:` were found.

## Verification performed

- `gh issue view 2703 --comments` was fetched before execution.
- Claude Code was used for drafting the three new skill bodies; Hermes independently verified the actual files before commit.
- Independent write verification included `ls -l`, line counts, byte counts, SHA-256, and `git status --short`.
- Skill-content scanner passed for all new and moved skill files. Only non-blocking medium warnings were observed for known `sudo_usage` / `uv run` textual mentions.
- Preflight git checks were run before commits:
  - `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)' | head`
  - `.git/index.lock` absence check
- No commits used `--no-verify`.
- No edits were made in `_archive/`, `_internal/`, `_core/`, or `_runtime/`.

## Deferred items needing user decision or a follow-up issue

1. Decide whether `business_admin` should be migrated to `business/admin` or another canonical parent. This may affect discoverability, so it should be planned separately.
2. Decide whether the eight flat `eng/*.md` files should be converted into conforming `engineering/.../<skill>/SKILL.md` entries, archived, or deleted. They appear to be domain-package callable wrappers and should not be bulk-moved without owner review.
3. Decide whether single-skill top-level stragglers such as `corporate-tax-form-fill`, `extract-learnings-to-issues`, `field-dev-code-recon`, `leisure`, `marketing`, `red-teaming`, `smart-home`, and `test-dummy-validation` are intentionally top-level or should be promoted into parent groups.

## Commit summary

- `e4d8ec075b154e57d18657810aba62af9f7f5273` — add `subagent-write-verification`
- `d506fd1ec2c17c94e82844f80c51279e091b19b6` — add `git-operation-serialization-preflight`
- `a8d28b8dfa2cd6c7839ad48f85f68e4dbf306e90` — add `credential-scanner-safe-skill-authoring`
- `50b7a5bbf` — record mined skill trace entries
- `21af1fb608cec511a8f4a340459a87fb51226a8e` — canonicalize `workspace-hub-learned` naming
- `4b09223be` — record curation trace entries
