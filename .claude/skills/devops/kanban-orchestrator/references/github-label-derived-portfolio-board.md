# GitHub-label-derived portfolio board pattern

Use when a workspace has many existing GitHub issues across tier-1 repos and the user wants Hermes/Kanban to map execution work without creating a separate manual queue.

## Session-proven pattern

1. Resolve canonical repo scope first from durable workspace docs (for example `docs/vision/VISION.md` plus latest tier/readiness report), not from broad repo overviews.
2. Collect issue data per repo and state with `gh issue list`, but redirect large outputs to temp files before parsing:
   ```bash
   gh issue list --repo OWNER/REPO --state open --limit 1000 \
     --json number,title,state,labels,assignees,updatedAt,url > /tmp/gh_REPO_open_issues.json
   gh issue list --repo OWNER/REPO --state closed --limit 500 \
     --json number,title,state,labels,assignees,updatedAt,url > /tmp/gh_REPO_closed_issues.json
   ```
   Do not parse large `gh` JSON directly from captured terminal/tool output; it may be truncated or contain invalid control characters.
3. Treat GitHub labels as the source of truth and generated artifacts as views:
   - `status:plan-approved` + canonical plan evidence + `.planning/plan-approved/<issue>.md` + not `status:working` => `Ready / Plan Approved`
   - `status:plan-approved` but missing plan/marker evidence => `Approved Label Drift / Repair Before Execution`
   - `status:plan-review` => `Plan Review / Needs Approval`
   - no `status:plan-*` => `Planning Needed / Future Backlog`
   - `status:working` => `In Progress / Status Working`
   - blocker labels => `Blocked / Waiting`
   - both `status:plan-review` and `status:plan-approved` => conflict/hygiene lane
4. Emit the core repo-tracked artifacts:
   - machine JSON in `docs/reports/<date>-tier1-gh-issue-kanban-data.json`
   - Markdown board in `docs/reports/<date>-tier1-gh-issue-kanban-board.md`
   - self-contained HTML dashboard in `docs/dashboards/<date>-tier1-gh-issue-kanban.html`
5. When issue volume is high or the user asks for review/refinement surfaces, also emit an index and sliced boards:
   - board index in `docs/reports/<date>-tier1-board-index.md`
   - per-repo Markdown boards in `docs/reports/kanban/<date>-repo-<repo>-kanban.md`
   - special lane boards, at minimum `planning-needed`, `execution-ready`, and `approval-drift`
   - selected top/explicit domain/category boards in `docs/reports/kanban/<date>-domain-<slug>-kanban.md`
   - If a new repo is added to the tier-1 scope, update the durable portfolio/mission doc that defines the tier-1 set (for example `docs/vision/VISION.md`) so future refreshes keep it.
6. Verify before reporting:
   - JSON issue record count, repo counts, and lane counts match the payload
   - Markdown summary/index counts are recomputed from JSON after generation, not copied from an earlier partial run
   - index paths resolve to existing files; wildcard paths are explicitly treated as patterns, not broken links
   - all generated Markdown boards have required headings such as `## Lane counts` and `## Review lanes`
   - HTML embeds the board/data and loads without external secrets
   - targeted credential scan reports zero GitHub tokens, private keys, AWS access keys, or credential assignments
   - `git status --short` shows exactly which artifacts are modified/new/untracked

## Pitfalls

- Broad base64-like secret regexes produce false positives on embedded JSON/HTML dashboards. Use targeted credential scans for token/private-key/assignment patterns, and report the exact scan classes.
- Do not launch workers from a label-only `status:plan-approved` issue. Check plan evidence, approval marker evidence, local branch/worktree hygiene, and `status:working` first.
- Do not flatten the board into one queue. Separate execution, governance repair, planning factory, working-state audit, blocked, and done-review lanes.
- When reporting board counts, distinguish candidate domain/category routes in the full JSON from domain Markdown files actually written. A generator may select only top/explicit domains for human review; reconcile this explicitly to avoid claiming missing files.
- Markdown review boards may cap long lanes for readability. Make that explicit and point to the JSON/HTML dashboard as the uncapped source of truth.
