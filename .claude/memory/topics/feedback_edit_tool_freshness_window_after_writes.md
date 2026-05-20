> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-20
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_edit_tool_freshness_window_after_writes.md

---
name: edit-tool-freshness-window-after-writes
description: "Edit tool's freshness guard can silently invalidate after a long Write chain in the same turn; Edits to a previously-edited file return \"File has not been read yet\" and fail silently — applies most often to index.md / log.md updates batched with content writes"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 72238262-9b25-493d-9731-fc22b67185aa
---

When a single conversation turn executes substantial Write work (~10+ new files) and then in the same turn tries Edit calls on a previously-edited file (commonly the wiki index.md or log.md being incrementally updated across sub-issue ingests), the Edit tool can silently invalidate its freshness tracker for that file and reject Edit calls with `"File has not been read yet."` The Bash commit that includes the (failed-Edit) file will still land — but the file content is unchanged from before the Edits.

**Why this happens (best understood mechanism):** the Edit tool's per-turn freshness state appears to clear after enough intervening Write tool calls. Whether this is by file-count, byte-count, or context-replacement isn't precisely characterized, but the pattern is reproducible at the ~7-10 Write threshold.

**Failure mode:** silent. The Bash `git commit` succeeds and reports the file count, but it's lower than expected. The index/log updates simply didn't make it into the commit. Detection requires either (a) noticing the file-count mismatch in the commit output, or (b) reading the file after commit and seeing the stale state.

**How to apply:**

1. **Before any Edit chain on a previously-edited file when the same turn has done ~7+ Write calls — Read the file fresh.** One Read call costs little; one fixup commit costs more.
2. **Watch the Edit tool output for `"File has not been read yet"` errors.** If you see one, do not proceed with the commit — pause, Read, and retry the Edits.
3. **Audit the commit output.** If a commit was supposed to include `index.md` and `log.md` plus N new files, the file-changed count should be N+2. If it's just N, an Edit failure happened silently. Verify with `grep "^page_count" index.md` or similar before moving on.
4. **Fixup recovery.** When silent-fail is detected post-commit: Read the affected file, apply the missed Edits, commit as `fixup(...): index/log for #N (Edit silent-fail recovery)`. Same-day fixup is fine; the audit trail is preserved.

**Observed instances (2026-05-13 drilling-engineering corpus build-out):**

- Phase 2 sub-issue #58 cementing — commit `a21d1275` landed 8 content files; the 6 index.md / log.md Edits in the same turn all silently failed. Fixup commit `8d2b50b7` recovered. Secondary fixup `6717e568` needed for a stale anchor-string in one further Edit.
- Phase 2 sub-issue #60 well-construction concept pack — commit `0d3f2ac3` landed 7 content files; the 7 index.md / log.md Edits in the same turn all silently failed. Fixup commit `2daa8171` recovered.

**Don't apply when:** the file you're editing was just Read in the same turn. The freshness window is fresh; no precaution needed.

**Cross-references:**

- `project_drilling_engineering_corpus_initiative.md` — the Phase 2 execution where this pattern was first observed.
- `project_llm_wiki_external_post_ingest_workflow.md` — the per-sub-issue commit grain that surfaces this pattern (index.md + log.md updates batched with new-content writes per commit).
