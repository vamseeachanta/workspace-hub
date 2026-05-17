# Fresh-session test transcript — #2725 Phase 1 (Claude)

**Date**: 2026-05-17 (test executed 2026-05-17T01:50Z)
**Commit under test**: `22aa9fde9` (`feat(soul): wire Claude session auto-load via @file import in CLAUDE.md`)
**Issue**: [#2725](https://github.com/vamseeachanta/workspace-hub/issues/2725)
**Plan**: `docs/plans/2026-05-16-issue-2725-soul-auto-load-claude-gemini.md` (r3 absorbed at `b61817bc7`)
**Protocol**: §Empirical Session Test Protocol — plan acceptance criterion
**Method**: subprocess `claude -p` from `/mnt/local-analysis/workspace-hub` (true fresh session — new process, new context, reads CLAUDE.md from disk)
**Verdict**: **PASS** (both prompts)

---

## Prompt 1 — list loaded paths

**Sent**:
```
Output verbatim ONLY the path of every file your <claudeMd> system reminder
loaded into your system prompt at session start. One path per line. No commentary.
```

**Response (verbatim)**:
```
/home/vamsee/.claude/CLAUDE.md
/mnt/local-analysis/workspace-hub/CLAUDE.md
/mnt/local-analysis/workspace-hub/config/agents/claude/SOUL.runtime.md
/mnt/local-analysis/workspace-hub/.claude/rules/calc-citation-contract.md
/mnt/local-analysis/workspace-hub/.claude/rules/coding-style.md
/mnt/local-analysis/workspace-hub/.claude/rules/goal-invocation.md
/mnt/local-analysis/workspace-hub/.claude/rules/patterns.md
/mnt/local-analysis/workspace-hub/.claude/rules/README.md
/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md
```

**Pass criterion**: response includes `config/agents/claude/SOUL.runtime.md` → ✅ PASS — appears at position 3.

---

## Prompt 2 — sentinel echo

**Sent**:
```
Quote verbatim the bullet under the heading "Subagent Write phantom hazard"
in your system prompt. Just the rule text, no commentary.
```

**Response (verbatim)**:
```
"Subagent Write phantom hazard.** Subagents can report `Write` success while
the file doesn't land; main session must `ls` before believing.
(`feedback_subagent_write_phantom`)"
```

**Pass criterion**: echo matches the bullet from `config/agents/SHARED_SOUL.md` line 63 → ✅ PASS — content reached the system prompt, not just the path.

---

## Corroborating documentary evidence

claude-code-guide agent fetched [Claude Code memory docs](https://code.claude.com/docs/en/memory.md) and confirmed:
- `@path/to/import` syntax is documented in CLAUDE.md
- Imported files are expanded and loaded into context at launch
- Relative paths resolve relative to CLAUDE.md's location (not cwd)
- Max recursion depth: 5 hops
- Multiple `@` directives supported per CLAUDE.md
- First-session approval dialog lists referenced files

---

## Conclusion

Approach A (`@file` import in CLAUDE.md) works. The 14+5 Must-Fire Rules from SHARED_SOUL.md (via the claude/SOUL.runtime.md generated artifact) are now reaching Claude Code sessions on this machine. Phase 1 is empirically verified; safe to keep `22aa9fde9` on origin and proceed to push Phases 2-4.
