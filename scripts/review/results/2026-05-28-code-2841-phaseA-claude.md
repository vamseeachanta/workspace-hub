# Code Review — #2841 Phase A — Claude (fresh-context subagent)
- Date: 2026-05-28 · Stage: code (adversarial), commit a3a839cf6 · Verdict: MAJOR → fixed
- Codex/Gemini UNAVAILABLE (CLAUDECODE, #2721/#2715) — single-author+fresh-context fallback.

## Findings (F1/F2 fixed pre-merge; F3/F4 also fixed; F5/F6 addressed)
- F1 [MAJOR] `> $TARGET` truncates before python runs → failed emit leaves 0-byte slice, committed. FIXED: temp-file + mv-on-success; errors no longer swallowed; previous slice kept on failure.
- F2 [MAJOR] `read_text(errors=replace)` uses platform encoding → em-dash mis-decodes on non-UTF-8 (Windows) hosts, dropping the whole index for the Hermes sink. FIXED: explicit `encoding="utf-8"`.
- F3 [MINOR] cap < fixed-overhead returned > cap. FIXED: hard `body[:cap]` clamp + test.
- F4 [MINOR] blanket `git commit` could sweep parallel staged changes. FIXED: pathspec `-- .claude/memory/ config/agents/codex/MEMORY.runtime.md`.
- F5 [MINOR] broad claude-only tokens (mcp_scope/output_style) latent over-drop — left (negative test covers current data); narrow if it bites.
- F6 test gaps — added: regex-with-markdown-link, empty-source, tiny-cap-clamp (13 tests total).

## Verified correct: F1 git-tracked sourcing real; F4/F5 plan-fixes delivered; regex handles `[#N](url)` links; non-owner never stages the slice; determinism (utf-8 fix closes the last cross-machine gap).
