# WRK-1015 Plan: Category Grouping for Work Queue

## Route: B (Medium complexity)

## Phase 1 — Inference Engine
1. Create `scripts/work-queue/infer-category.py` with CATEGORY_RULES and SUBCATEGORY_RULES
2. Word-boundary matching for short keywords; title-first inference
3. Returns JSON `{"category": "...", "subcategory": "..."}`

## Phase 2 — Bulk Assignment
4. Create `scripts/work-queue/assign-categories.py` — dry-run by default, `--apply` to write
5. Scoped frontmatter parser to avoid body contamination
6. Apply to all 400+ active WRK items

## Phase 3 — INDEX.md Category View
7. Update `generate-index.py` to emit `## By Category` section
8. HIGH → MEDIUM → LOW sort within each category
9. Two-level: category → subcategory → items

## Phase 4 — /work list flags + session-start
10. Add `--by-category`, `--category <name>`, `--subcategory <sub>` to work-queue/SKILL.md
11. Update session-start to show top-per-category instead of flat top-3

## Phase 5 — Unit Tests + Creation Path Hooks
12. `tests/unit/test_infer_category.py` — 10+ cases covering all 7 categories
13. Update comprehensive-learning Phase 7 + workflow-gatepass Stage 15 to call infer-category.py

## Acceptance Criteria: 14 items (all ✓)
