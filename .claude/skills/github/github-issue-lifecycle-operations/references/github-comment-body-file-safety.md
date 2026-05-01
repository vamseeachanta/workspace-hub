# Archived Skill: `github-comment-body-file-safety`

Original path: `/home/vamsee/.hermes/skills/github/github-comment-body-file-safety`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/github/github-comment-body-file-safety`
Consolidation date: 2026-04-29

---

---
name: github-comment-body-file-safety
description: Prevent shell-quoting and command-substitution bugs when posting GitHub issue/PR comments or editing bodies with gh CLI.
version: 1.0.0
author: Hermes Agent
license: MIT
triggers:
  - When using `gh issue comment`, `gh pr comment`, `gh issue edit --body`, `gh pr edit --body`, or `gh issue create --body`
  - When comment/body text contains backticks, code spans, file paths, markdown, or dynamic content
  - When a GitHub comment/body is being assembled from plan paths, test names, or command output
tags: [github, gh, shell-safety, comments, quoting]
---

# GitHub Comment Body-File Safety

## Problem

Inline `gh ... --body "..."` looks convenient, but shell parsing happens before GitHub CLI sees the text.
If the body contains backticks, `$()`, code fences, or other shell-significant characters, the shell can:
- execute unintended commands
- strip or mangle content
- turn file paths into failing shell commands
- post broken comments

This happened in live use when a GitHub comment included markdown code spans like `docs/plans/...` and `tests/...` inline; the shell tried to execute those paths.

## Rule

If the body contains any markdown/code formatting or dynamic content, use `--body-file`.
Do not use inline `--body`.

## Safe pattern

```bash
cat > /tmp/gh-comment.md <<'EOF'
Planning update:

- Draft saved at `docs/plans/2026-04-20-issue-2419-skill-markdown-contract-drift.md`
- Index updated in `docs/plans/README.md`
- Next check: `uv run pytest tests/skills/test_repo_skill_parity_merges.py -q`
EOF

gh issue comment 2419 --body-file /tmp/gh-comment.md
```

Also use the same pattern for:
- `gh pr comment ... --body-file`
- `gh issue edit ... --body-file`
- `gh pr edit ... --body-file`
- `gh issue create ... --body-file`

Important: this is not just a comment/edit problem. `gh issue create --body "..."` is equally vulnerable. In live use, an inline create body containing markdown code spans caused bash to try executing repo paths and run IDs, producing a malformed issue body. The safe recovery was to rewrite the intended issue body to a temp markdown file and run `gh issue edit --body-file ...`.

## When body-file is mandatory

Use `--body-file` if the text includes:
- backticks: `` `...` ``
- command substitutions: `$()`
- fenced code blocks
- file paths or commands copied from plans/tests
- multiline markdown
- text generated from tools/scripts
- any user-provided content you did not fully hand-escape

## Recovery pattern

If an inline comment/body was already posted and looks mangled:
1. write the intended text to a temp markdown file
2. re-post or edit using `--body-file`
3. for malformed new issues created via `gh issue create --body`, immediately repair the issue with `gh issue edit --body-file <file>`
4. verify the rendered GitHub comment/body afterward

## Minimal checklist

Before any `gh ... --body` call, ask:
1. Does this text contain backticks or markdown? If yes, use `--body-file`.
2. Was any part of this text produced dynamically? If yes, use `--body-file`.
3. Do I want exact rendering with zero shell interpretation? If yes, use `--body-file`.

## Bottom line

`--body-file` is the safe default.
Inline `--body` is only for truly simple, shell-safe one-liners.
