# Stage 01: Capture — Gotchas

## No-Bypass Rules
- Stage 1 exit gate (`user-review-capture.yaml`) may not be bypassed; Route A may use `n/a: true` with non-empty `reason` field. Route B/C: field required.
- No implementation before WRK item + plan + explicit WRK approval.

## Operational Lessons
- GitHub issue creation may fail if `gh auth` is unavailable; continue and create issue manually later.
- Always validate frontmatter with `validate-wrk-frontmatter.sh` before exiting.

## Edge Cases
- If parent WRK exists, `blocked_by` must be checked and cleared before proceeding.
