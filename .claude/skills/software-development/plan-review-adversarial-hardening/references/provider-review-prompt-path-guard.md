# Archived Skill: `provider-review-prompt-path-guard`

Original path: `/home/vamsee/.hermes/skills/software-development/provider-review-prompt-path-guard`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/provider-review-prompt-path-guard`
Consolidation date: 2026-04-29

---

---
name: provider-review-prompt-path-guard
description: Prevent adversarial review dispatch failures caused by sandbox/tmp path mismatches and provider CLI working-directory drift when launching Codex or Gemini with prompt files.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [review, codex, gemini, prompt-files, pathing, reliability]
    related_skills: [multi-provider-adversarial-review]
---

# Provider Review Prompt Path Guard

Use this when launching Codex/Gemini adversarial reviews from saved prompt files.

## Problem this solves

Review launches can fail even when the prompt file exists because of two separate pathing traps:

1. Files written via `execute_code` to `/tmp` are sandbox-local and invisible to later `terminal()` shell commands.
2. A `terminal(workdir=...)` launch can still produce provider CLI runs whose effective shell context resolves relative prompt paths unexpectedly.

Observed failure mode:
- `codex exec "$(cat .planning/quick/review-334-prompt.md)"` returned `cat: .planning/quick/review-334-prompt.md: No such file or directory`
- Codex then started in the parent workspace instead of the intended repo directory.

## Reliable pattern

Always do all of the following:

1. Write prompt files onto the real workspace filesystem, not sandbox `/tmp`.
2. Save prompts under the repo, e.g. `.planning/quick/review-<issue>-prompt.md`.
3. Verify prompt file existence with `wc -c /absolute/path/to/prompt.md` before dispatch.
4. Use an absolute path inside `$(cat ...)`.
5. Prefix the provider launch with explicit `cd /repo && ...` in the same shell command.

## Recommended command pattern

```bash
cd /abs/path/to/repo && \
provider exec "$(cat /abs/path/to/repo/.planning/quick/review-<issue>-prompt.md)" \
  2>&1 | tee /abs/path/to/repo/.planning/quick/review-<issue>-<provider>.out
```

Examples:

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata && \
codex exec "$(cat /mnt/local-analysis/workspace-hub/worldenergydata/.planning/quick/review-334-prompt.md)" \
  2>&1 | tee /mnt/local-analysis/workspace-hub/worldenergydata/.planning/quick/review-334-codex.out
```

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata && \
gemini exec "$(cat /mnt/local-analysis/workspace-hub/worldenergydata/.planning/quick/review-334-prompt.md)" \
  2>&1 | tee /mnt/local-analysis/workspace-hub/worldenergydata/.planning/quick/review-334-gemini.out
```

## Verification checklist

Before launching reviewers:
- prompt file exists at an absolute repo path
- `wc -c /abs/path/prompt.md` succeeds
- output path is absolute
- command begins with `cd /repo &&`
- prompt text is self-contained (reviewer should not need local file reads)

After launching:
- inspect raw provider output file, not only process status
- if Gemini hits 429 retries, keep reading — it may still return a substantive review later
- if a provider truly fails, save a canonical artifact documenting `UNAVAILABLE` or failure details

## When to escalate

If Codex/Gemini still cannot read the prompt reliably:
- shorten the prompt
- keep it self-contained
- avoid chained relative paths entirely
- preserve raw logs and create a provider-status artifact
