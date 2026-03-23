# Stage 15: Future Work Synthesis — Gotchas

## Stage 15 to Stage 17 Rule
- Before Stage 17, any "next work" discovered must be captured as updated WRK or new WRK.
- Must be recorded in `evidence/future-work.yaml` using canonical template.
- Category is mandatory: run `infer-category.py` before writing WRK frontmatter.
- Use table with explicit `Captured` column (yes/no) — all must be `yes` before Stage 17.

## Operational Lessons
- Don't skip future-work capture even for "obvious" items — they get lost.
- Default to `uncategorised` only if `infer-category.py` is unavailable.

## Edge Cases
- If no future work discovered, write future-work.yaml with empty items list and reason.
