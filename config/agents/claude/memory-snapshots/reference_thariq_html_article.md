---
name: reference-thariq-html-article
description: "Thariq Shihipar's \"Unreasonable Effectiveness of HTML\" article and the examples gallery — load-bearing reference for the workspace-hub HTML-first artifact policy"
metadata: 
  node_type: memory
  type: reference
  originSessionId: e31936cc-d9eb-4150-bdac-f5679e9d5164
---

**Author:** Thariq Shihipar (@trq212), Anthropic — works on Claude Code core
**Article:** "Using Claude Code: The Unreasonable Effectiveness of HTML" (X long-form post, May 2026)
**URL:** https://x.com/trq212/status/2053632475294400084 (login-gated; text captured in workspace-hub session 2026-05-11 if needed for re-read)
**Examples gallery:** https://thariqs.github.io/html-effectiveness/ (public, browsable)

The article is the source for [[feedback-html-default-artifact]] and workspace-hub issues #2663 (rule) and #2664 (PR explainer).

**Use-case taxonomy from the article (for quick recall):**
1. Specs / planning / exploration — including the 6-variant comparison grid pattern
2. Code review & understanding — HTML PR explainer with rendered diffs + inline annotations
3. Design & prototypes — sliders/knobs/copy-as-prompt buttons
4. Reports / research / learning — SVG diagrams (e.g., token-bucket flowchart)
5. Custom throwaway editor UIs — Linear ticket drag-cards, feature-flag editor, prompt tuner
6. Design system HTML reference file (one-time codebase scan)

**Author's explicit anti-pattern:** "I'm a little bit afraid that people will read this article and turn it into a /html skill." Per article, the right surface is a prompt/decision habit, not a slash command.

**Cross-reference:** the X post links to Thariq's earlier playgrounds post (`https://x.com/trq212/status/2017024445244924382`) as the source of the two-way-interaction pattern.
