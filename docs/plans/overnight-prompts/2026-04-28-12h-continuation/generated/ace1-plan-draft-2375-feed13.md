Continue 12h continuation Lane feed13 — pure planning draft for workspace-hub issue #2375. Stop target for the overall overnight window is 2026-04-29 09:45 CDT; do not launch subagents or follow-up sessions.

Context and hard boundaries:
- Workdir: `/mnt/local-analysis/workspace-hub` on ace-linux-1 (control surface).
- This is non-destructive planning only. Do NOT implement code. Do NOT run tests beyond read-only discovery commands. Do NOT create `.planning/plan-approved/*` markers. Do NOT mutate GitHub: no `gh issue comment`, no label edits, no PRs, no closes, no merges.
- Follow AGENTS.md hard gates: issue work must stay in planning mode; write a draft plan only, not approval.
- Respect existing dirty state from other lanes; do not overwrite unrelated files.
- If required evidence is inaccessible, mark it as a gap in the plan rather than inventing facts.

Task:
Draft a first formal plan for issue #2375, "normalize WRK completions into structured seeds" (or current issue title if GitHub differs), using the repository plan template and resource-intelligence discipline.

Required prerequisite discovery (read-only):
1. Read `docs/plans/_template-issue-plan.md`, `docs/plans/README.md`, and `docs/standards/HARD-STOP-POLICY.md` as needed.
2. Inspect issue #2375 read-only with `gh issue view 2375 -R vamseeachanta/workspace-hub --json number,title,body,labels,comments,state,url`.
3. Verify the seed facts from ace2 D2 result §5.2:
   - `knowledge-base/wrk-completions.jsonl` exists but is raw-string oriented; inspect a small sample/schema only.
   - Proposed structured target from prior architecture is likely `knowledge/seeds/wrk-completions.yaml`; verify whether that path exists or should be proposed.
   - Related issues/docs: archive synthesis #103, knowledge-persistence architecture #894, transient-promotion #2374, closed-issue ledger #2370.
4. Inspect relevant files/code only as needed, including:
   - `knowledge-base/wrk-completions.jsonl` schema/sample rows.
   - Search for existing references to `wrk-completions`, `wrk_id`, and `knowledge/seeds` in repo scripts/docs.
   - `docs/document-intelligence/intelligence-accessibility-map.md` if present.
   - Any existing plans/docs for #103, #894, #2374, #2370 that clarify boundaries.

Draft plan output:
- Write `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`.
- The plan status must be clearly `draft` / `PLAN DRAFT — NOT APPROVED`.
- Include: issue/resource intelligence, scope, out-of-scope, dependencies, implementation approach, TDD/test plan, acceptance criteria, rollback, risks, adversarial-review checklist, and exact files expected to change during a future implementation.
- Proposed implementation should be bounded to a T2 planning-derived slice, likely:
  - `scripts/knowledge/normalize_wrk_seeds.py`
  - output `knowledge/seeds/wrk-completions.yaml`
  - companion projection `data/document-index/wrk-wiki-candidates.yaml`
  - append-flow guidance `docs/document-intelligence/wrk-seed-policy.md`
- Acceptance criteria should cover:
  - each raw row produces at least one structured row OR is logged in a could-not-normalize report with reason;
  - projection identifies at least 10 high-confidence wiki-candidate rows for first promotion sweep, if the corpus has enough rows;
  - append flow keeps new completions structured-by-default;
  - explicit non-duplication boundary versus #103 and downstream feed relationships to #2374/#2370.

Result summary:
- Write `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-draft-2375-feed13.md` with concise summary: discoveries, files written, unresolved questions, and next safe action.

Do not commit. Do not self-approve. Do not launch review fanout. Stop after writing the draft plan and result summary.
