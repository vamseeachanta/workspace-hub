Continue 12h continuation Lane feed8 — pure planning draft for workspace-hub issue #2370. Stop target for the overall overnight window is 2026-04-29 09:45 CDT; do not launch subagents or follow-up sessions.

Context and hard boundaries:
- Workdir: `/mnt/local-analysis/workspace-hub` on ace-linux-1 (control surface).
- This is non-destructive planning only. Do NOT implement code. Do NOT run tests beyond read-only discovery commands. Do NOT create `.planning/plan-approved/*` markers. Do NOT mutate GitHub: no `gh issue comment`, no label edits, no PRs, no closes, no merges.
- Follow AGENTS.md hard gates: issue work must stay in planning mode; write a draft plan only, not approval.
- Respect existing dirty state from other lanes; do not overwrite unrelated files.

Task:
Draft a first formal plan for issue #2370, "Closed-issue promotion ledger for engineering wiki", using the repository plan template and resource-intelligence discipline.

Required prerequisite discovery (read-only):
1. Read `docs/plans/_template-issue-plan.md` and any relevant planning docs under `docs/plans/README.md` / hard-stop policy if needed.
2. Inspect issue #2370 read-only with `gh issue view 2370 -R vamseeachanta/workspace-hub --json number,title,body,labels,comments,state,url`.
3. Verify the seed facts from ace2 D2 result §5.5:
   - 74 remaining closed `cat:engineering` issues + 13 remaining closed `cat:engineering-calculations` issues not yet promoted (verify or mark stale/needs-refresh).
   - `knowledge/wikis/engineering/SOURCE_INVENTORY.md` exists and indicates current ingestion coverage.
   - Existing #2236 / #2238 govern future promotions, not necessarily the closed backlog.
4. Inspect relevant files/code only as needed, including:
   - `scripts/knowledge/llm_wiki.py` (look for issue-ingest or wiki generation hooks)
   - `docs/reports/engineering-wiki-skill-ingest-readiness-2039-2042.md` if present
   - `knowledge/wikis/engineering/SOURCE_INVENTORY.md`
   - sample existing engineering wiki pages
   - any docs for #2236 / #2238 / closed-issue citation or promotion workflow

Draft plan output:
- Write `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md`.
- The plan status must be clearly `draft` / `PLAN DRAFT — NOT APPROVED`.
- Include: issue/resource intelligence, scope, out-of-scope, dependencies, implementation approach, TDD/test plan, acceptance criteria, rollback, risks, adversarial-review checklist, and exact files expected to change during a future implementation.
- Proposed implementation should be bounded to a T2 planning-derived slice, likely:
  - `scripts/knowledge/build_closed_issue_promotion_ledger.py`
  - output `data/document-index/closed-issue-promotion-ledger.yaml`
  - shortlist report `docs/reports/closed-issue-promotion-shortlist.md`
  - scoring inputs: reusable methodology, decision durability, evidence richness, overlap with existing wiki page.
- Acceptance criteria should cover: all verified closed issue backlog items scored; shortlisted issue has target wiki domain + extend/create flag; overlap analysis cites specific existing wiki pages; durable YAML output rather than markdown-only table; idempotent generation and manually-reviewable diff.

Result summary:
- Write `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-draft-2370-feed8.md` with concise summary: discoveries, files written, unresolved questions, and next safe action.

Do not commit. Do not self-approve. Do not launch review fanout. Stop after writing the draft plan and result summary.