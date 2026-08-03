---
name: feedback-client-pii-gate-scans-commit-messages
description: "Client-PII Gate scans commit messages and PR title/body, not just changed files — redacting the file does not clear it"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c2b08463-0428-41e0-83ad-03ab287f4328
  modified: 2026-08-01T12:21:27.932Z
---

`Client-PII Gate` runs **two** steps: *"Scan PR diff for client identifiers"* AND *"Scan PR
title/body + commit messages for client identifiers."* A client name in a **commit message**
fails the gate even when every changed file is clean.

**Why:** hit live 2026-08-01 on workspace-hub PR #3749. I put a client-owned hostname in a
`schedule-tasks.yaml` comment, the gate failed, I redacted the comment AND the PR body — and it
failed again identically. Every local scan said clean, because the leak was in the commit object,
which `git add` cannot touch. The failure line names the surface explicitly
(`✖ Client identifier found in commit <sha>`), but it is buried under echoed workflow script
lines; the visible summary only says a client identifier was found.

**How to apply:**

1. **Read the failure line, not the summary.** `gh run view --job <id> --log-failed | grep -v 'echo '`.
   `in commit <sha>` means the message; a filename means the diff. They need different fixes.
2. **The gate withholds the matched value** ("public logs would leak it") — by design, since
   workspace-hub is public. Diagnose from your own diff/message, never expect CI to name it.
3. **Fixing a message means replacing the commit object.** When building commits via the GitHub
   Git Data API, reuse the existing tree and create a new commit with a sanitized message, then
   `PATCH git/refs/heads/<branch>` with `force: true`. Content stays byte-identical; only the
   message changes.
4. **Local repro:** `uv run python scripts/legal/check-client-pii.py --staged --strict`. The map is
   `config/agents/.client-codename-map.local.yaml` (CI uses the `LEGAL_CLIENT_MAP` secret).
   ⚠ `--base-ref origin/main` reports "0 changed files" when your work is staged-but-uncommitted —
   that is a vacuous pass, not a clean bill. Use `--staged`, and stage **every** file in the PR:
   API-pushed files that were never `git add`ed are silently excluded from the scan.
5. **Comments count.** `legal-compliance` covers "comments, docstrings, variable names, and config
   values". A client hostname in a YAML comment is a violation, not a note.

**Do NOT** reach for `LEGAL_PII_ALLOW=1` (the gate offers it, labelled discouraged) — see
[[feedback_agent_cannot_enable_security_gate_bypass]].

Related: [[project_claude_md_harness_retired]], [[feedback_absence_of_signal_reads_as_success]].
