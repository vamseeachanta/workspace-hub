# Ecosystem Architecture Candidate → Planning Issue Expansion

Use when an architecture review produces multiple candidates and the user asks to process "all" candidates "one by one".

## Pattern

1. Treat each candidate as a separate planning issue, not an implementation task.
2. Verify GitHub target before side effects:
   - `gh repo view --json nameWithOwner --jq .nameWithOwner`
   - `git branch --show-current`
   - `gh auth status`
3. Check existing issues broadly by candidate nouns and parent initiative terms. Exact-title duplicate checks are useful only after a broad search; do not let a failed exact-title query block the run without independent verification.
4. Audit label taxonomy before issue creation and reuse existing labels. For workspace-hub style plan-gated work, default intake state is `status:needs-plan`.
5. Create issues one by one with `--body-file`; avoid inline multiline shell bodies.
6. After each issue, verify title/URL/labels/state with `gh issue view`.
7. If a parent issue exists, add a single sequencing comment listing all child issues in recommended execution/planning order and explicitly stating that implementation is blocked until each issue reaches `status:plan-approved` by user approval.
8. Save a restart-safe temp index such as `/tmp/architecture-deepening-issues-<timestamp>.tsv` containing issue number, title, and URL.

## Body shape

- Summary
- Evidence basis, including whether exploration was bounded/partial
- Problem / architecture friction
- Proposed deepening direction using Module/Interface/Seam/Adapter language
- Scope
- Out of scope
- Deliverables
- Acceptance criteria
- Mandatory plan-gate workflow
- Related report/parent issue links

## Pitfalls

- Do not convert architecture candidates directly into implementation approval.
- Do not apply `status:plan-approved`; only the user approves plans.
- Do not rerun broad unbounded subagent scans after timeouts. Salvage from bounded inventory and mark partial evidence.
- Keep issue creation artifacts outside repos unless the user asks for tracked artifacts.
