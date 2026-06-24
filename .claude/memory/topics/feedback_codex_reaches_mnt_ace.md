> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-24
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_reaches_mnt_ace.md

---
name: codex-reaches-mnt-ace
description: "codex exec under workspace-write CAN read /mnt/ace corpora — corpus-ingest issues ARE Codex-delegable for access; corrects my wrong \"not Codex-suitable\" triage"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9d5c1253-dc2e-4029-884d-0f22ed116810
---

`codex exec` with the current `-s workspace-write` sandbox **CAN read `/mnt/ace` corpora** (host paths outside the workspace). Verified 2026-05-27: read `/mnt/ace/O&G-Standards/` (32 publisher dirs + `_catalog.json` → 27,343 docs), `/mnt/ace/acma-codes/`, `/mnt/ace/docs/conferences/`. workspace-write restricts *writes* to the workspace but allows filesystem *reads* broadly; network_access=true.

**Why this matters:** I triaged the 8 `agent:codex` corpus-ingest issues (llm-wiki #105/#106/#108/#109/#115/#124/#125/#126) as "not Codex-suitable — sandbox can't reach /mnt/ace." **That was wrong** — the user had fixed sandbox access the day before (relates to [[feedback_codex_sandbox_write_blocked]] #2804). Those `agent:codex` labels are valid.

**How to apply:**
- Don't assume a Codex sandbox is filesystem-isolated from /mnt mounts — **test empirically** (`codex exec -s workspace-write --skip-git-repo-check "ls /mnt/ace/...; report READABLE/BLOCKED"`) before declaring corpus work non-delegable.
- Access ≠ one-shot feasibility: these are 27K+-doc ingests → still need **batched/pipeline dispatch**, not a single `codex exec`. And the per-issue doc counts are inflated (#124 says 54K; catalog says 27,343 — see [[feedback_mnt_ace_corpus_claims_unreliable]]). Re-verify figures from `_catalog.json`/`ls` before planning batches.
- The full loop works: Codex reads /mnt/ace corpus + writes wiki pages into the llm-wiki workspace (workspace-write covers the write target).
