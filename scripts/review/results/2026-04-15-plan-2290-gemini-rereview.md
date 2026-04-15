# Gemini second-wave re-review — plan #2290

Reviewer: Gemini CLI
Date: 2026-04-15
Issue: #2290
Prompt: `.planning/quick/review-2290-gemini-rereview-prompt.md`
Raw log: `.planning/quick/review-2290-gemini-rereview.out`
Verdict: MINOR

Note: Gemini emitted startup agent-loading warnings about unsupported `permissionMode` keys in `.gemini/agents/*.md`, but still produced a substantive review.

1. Verdict: MINOR

2. Strengths
- Excellent catch on 6 of 7 "exact-duplicates" not being byte-identical.
- Smart identification of auxiliary files (`references/`) and the need for directory-level inventory.
- Correctly scoped `operations/devtools/` to avoid deleting a non-empty directory.
- Strong TDD test list covering regressions and structure.

3. Remaining gaps
- Reference cleanup scope (`.claude/`, `.claude/rules/`, `config/`, `scripts/`) should also consider other agent adapter directories (`.codex/`, `.gemini/`, `.hermes/`) plus root documentation/config surfaces like `AGENTS.md` and `.mcp.json`, if they contain references or symlinks to the deleted paths.
- The merge process for divergent Markdown files should explicitly bias toward manual/loss-preventing reconciliation rather than automated editorial rewriting.

4. Risks
- Breaking Codex, Gemini, or Hermes agents due to dangling symlinks or missing references in their specific config files.
- Manual merge of divergent skill files could introduce malformed markdown/frontmatter if not carefully validated.

5. Missing tests
- Add a test verifying no dangling symlinks or deleted-path references exist in `.codex/`, `.gemini/`, and `.hermes/` after cleanup, if those adapter directories participate in skill mapping on this machine.
- Add a test verifying root files such as `AGENTS.md` and `.mcp.json` do not contain deleted-path references.

6. Scope creep concerns
- Manual merging of the 9 non-identical pairs could spiral into deep editorial reviews. The implementation should stick to strict preservation/appending of missing sections rather than rewriting.

7. Weakest assumption and what breaks if false
- Assumption: all references to skills exist only within `.claude/`, `config/`, and `scripts/`.
- If false, other agents (Codex, Gemini, Hermes) may fail to load deleted skills due to broken paths or symlinks.

8. Most likely implementation failure mode
- An automated script attempts to merge divergent `SKILL.md` files and corrupts the YAML frontmatter, or dangling symlinks are left in other agent adapter directories.

9. Most likely test gap
- `test_no_dangling_references` can falsely pass if `.gemini` symlinks or `.codex` config references are not scanned.

10. Future issues suggested
- Run the `cross-agent-skill-audit` after implementation to ensure symlinks and registries remain synced across all four agents.

11. Review confidence
- High. The plan is very close to implementation-ready; the remaining notes are bounded and non-blocking once incorporated.

Operational note
- Gemini could not write its own artifact directly in-session; this durable artifact was written from Hermes using the captured reviewer output.