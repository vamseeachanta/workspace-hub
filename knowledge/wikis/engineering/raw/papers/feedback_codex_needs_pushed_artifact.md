> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_needs_pushed_artifact.md

---
name: Codex CLI cannot read local files — push artifacts before review
description: Codex CLI sandbox denies bwrap shell access; it only retrieves files via GitHub MCP tools. Plan files must be committed and pushed to a branch Codex can fetch BEFORE dispatching adversarial review.
type: feedback
originSessionId: b431943f-0498-4574-ae77-b6fc779722da
---
Codex CLI (`codex exec`) on Linux runs inside a bwrap sandbox that denies even read-only `bash`/`sed`/`cat` for local files. Its only file-retrieval surface is the `github_fetch_file` MCP tool, which requires the target path to exist on a reachable branch of the GitHub repo.

**Why:** observed 2026-04-17 on assethold #39 v1 + v2 review dispatches. Plan was written locally and not pushed; Codex spent 5+ minutes spinning on `github_search` / `github_fetch_file` retries trying to find the plan, returned MAJOR with "retrieval insufficient" rather than substantive findings. For #38 v2 review, pushing the plan to `main` before dispatching let Codex actually verify claims; v2.1 re-review against pushed v2.1 returned MINOR-grade findings.

**How to apply:** when running adversarial review across multiple AI providers and Codex is one of them, ALWAYS commit + push the plan file (and any cited source the reviewer needs to verify) to a branch reachable on GitHub BEFORE calling `codex exec`. Otherwise Codex's verdict will be retrieval-blocked, not substantive — wasted minutes and tokens. This applies to plans, design docs, and any artifact under `docs/reports/` or `docs/plans/`. Claude subagent reviews don't have this constraint (full filesystem access via Read tool); Codex review does.
