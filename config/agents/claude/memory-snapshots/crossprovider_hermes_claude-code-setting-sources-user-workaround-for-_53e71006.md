---
name: crossprovider hermes claude-code-setting-sources-user-workaround-for-
description: Claude Code --setting-sources user workaround for malformed .settings.json
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [claude-code, tooling-quirk, settings-config, workaround]
---

Malformed JSON in .claude/settings.json prevents interactive Claude Code TUI startup. Workaround: launch with `--setting-sources user` flag and pass the task as initial prompt argument instead of pasting after startup (pasting multiline prompts into tmux can accidentally execute as shell commands).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
