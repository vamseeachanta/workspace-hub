# Plan: WRK-686 — Canonical HTML Standards for Orchestrator Reviews

## Goal
Establish and enforce a single, professional HTML/CSS standard for all Plan and Implementation Reviews to ensure consistency and scannability across all agents.

## Proposed Changes

### 1. Unified CSS
- Create `assets/shared/orchestrator.css`.
- Define a professional "Workspace-Hub" theme (fonts, colors, spacing).
- Include standard badge styles (APPROVE, REJECT, NO_OUTPUT, PASS, FAIL).

### 2. Standardized Template
- Create `templates/review-standard.html` (base HTML with head, body, and placeholders).
- Structure: Header (Metadata) → Executive Summary → Main Content → Reviewer Synthesis (Claude/Codex/Gemini cards).

### 3. Generator Tool Refactor
- Update `scripts/work-queue/generate-html-review.py`.
- Incorporate `Jinja2` or simple string replacement to inject Markdown content into the new standard template.
- Ensure the tool handles both "Plan" and "Implementation" modes with appropriate section headers.

### 4. Documentation
- Update `AGENTS.md` and `.claude/rules/` to mandate the use of the new generator/template for all gate reviews.

## Verification Plan

### Automated Tests
- None.

### Smoke Tests (Variation Tests)
1. **Regeneration:** Re-generate reviews for `WRK-669`, `WRK-671`, and `WRK-682` and verify they share the exact same styling and structure.
2. **Visual Check:** Confirm that "Final Verdict" badges and "Approve" sections are clear and consistent in a browser.

## Acceptance Criteria
- [ ] A shared CSS file exists.
- [ ] All new plan and review artifacts share the same look and feel.
- [ ] Plan reviews and implementation summaries are consistently scannable.
