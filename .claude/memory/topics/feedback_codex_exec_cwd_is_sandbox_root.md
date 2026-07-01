> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-01
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_exec_cwd_is_sandbox_root.md

---
name: codex-exec-cwd-is-sandbox-write-root
description: codex exec workspace-write sandbox root = the cwd at launch; sibling repos outside that cwd are READ-ONLY → cd into the target clone before dispatching writes
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

`codex exec -s workspace-write` (or default) makes the **launch cwd** the writable sandbox root, plus `/tmp`. **Sibling directories outside that cwd are read-only.**

**Symptom (2026-05-27):** a corrective pass dispatched from `cd /mnt/local-analysis/workspace-hub` failed every write with `OSError: [Errno 30] Read-only file system`; Codex reported "writable roots: /mnt/local-analysis/workspace-hub and /tmp, not llm-wiki." Zero fixes landed — pure dispatch error, not a Codex/quality problem. The earlier successful NORSOK run worked only because it was launched from `cd /mnt/local-analysis/llm-wiki`.

**How to apply:**
- To have Codex WRITE into the canonical wiki clone, **`cd /mnt/local-analysis/llm-wiki` before `codex exec`** (the clone is a SIBLING of workspace-hub, not nested — see [[project_llm_wiki_canonical_clone_location]]).
- Read-only jobs (audits, reviews) can run from anywhere — reads are broad ([[feedback_codex_reaches_mnt_ace]]).
- When a Codex run reports "nothing changed / read-only," first check the launch cwd vs the intended write target before assuming a sandbox/AppArmor problem ([[feedback_codex_worktree_sandbox_three_layer]] is the worktree variant).
