---
name: cross-machine-execution
description: Cross-machine tasks should spawn independent tasks per machine, not use SSH/rsync between them
type: feedback
---

Cross-machine tasks must open a separate task for each machine to execute independently. Do NOT orchestrate cross-machine work via SSH or rsync from one machine to another.

AI harness files (GSD, commands, skills, agents, CLAUDE.md, AGENTS.md, GEMINI.md, .codex/, .claude/, .gemini/) must stay committed and consistent across all machines. Always commit harness changes so every machine gets them on `git pull`.

**Why:** All machines have direct access — no SSH tunneling or config needed. Each machine runs its own Claude session and can pull from the shared repo independently. Harness drift between machines causes confusing behavior differences.

**How to apply:** When a task targets multiple machines, create a sub-task per machine. Each machine picks up its task and executes locally. The shared git repo is the coordination mechanism, not SSH. After any harness/GSD change, commit immediately so other machines stay in sync.
