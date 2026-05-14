> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-14
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_html_default_artifact.md

---
name: feedback-html-default-artifact
description: "HTML is the default format for rich human-facing artifacts (plans, specs, reports, PR explainers); markdown stays for agent-facing harness/skill/rule files; reruns regenerate HTML in place"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e31936cc-d9eb-4150-bdac-f5679e9d5164
---

Going forward, generate HTML (not Markdown) for rich human-facing artifacts: implementation plans, specs, reports, PR explainers, design prototypes, throwaway editor UIs. Keep Markdown for agent-facing files: CLAUDE.md / AGENTS.md / MEMORY.md / `.claude/rules/` / `.claude/skills/` / plan-template body / issue bodies / PR descriptions.

**User decision verbatim (2026-05-11):** "let us go with HTML going forward. during reruns, update to htmls"

**Why:** Per Thariq Shihipar's article "The Unreasonable Effectiveness of HTML" — HTML conveys richer information (SVG, CSS, tables, interactivity), is more readable than 100+ line markdown, shares via link without attachment friction, and supports two-way interaction (sliders/copy-as-prompt). Tradeoffs accepted: 2–4× slower generation, noisy git diffs, higher token cost (absorbed by Opus 4.7 1M context).

**How to apply:**
- Default new rich artifacts (plans/specs/reports >100 lines or with diagrams/mockups/data-flow) to HTML
- Regenerating overwrites the existing HTML file in place — combine with `<meta http-equiv="refresh" content="30">` per [[feedback-html-refresh]] so the open browser tab auto-updates; do NOT spawn new tabs with `xdg-open`
- Use SVG for diagrams, not ASCII art or Unicode color hacks
- Surface a share link (S3, gh-pages, local web server) when the audience extends beyond the author
- DO NOT create a `/html` skill — explicit instruction from article author; the rule lives in `.claude/rules/artifact-format.md` (tracked: workspace-hub#2663)
- Markdown remains canonical for plan-vs-live-state contradiction detection ([[feedback-attestation-enables-contradiction-detection]]) and git review-gate diffing; HTML is a companion when present

**Open question:** the "during reruns, update to htmls" phrase is ambiguous between (a) overwrite-in-place during regeneration (default reading) and (b) backfill old markdown artifacts to HTML when next touched. The HTML-rule issue ([workspace-hub#2663](https://github.com/vamseeachanta/workspace-hub/issues/2663)) currently codifies interpretation (a) — "organic adoption only, no backfill PRs." If the user later signals interpretation (b), update the rule and this memory.

Related: [[feedback-html-refresh]], [[project-claude-design-adoption]], workspace-hub#2663 (parent rule), workspace-hub#2664 (PR explainer child)
