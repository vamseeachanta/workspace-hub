# Lane C2 — GTM material packager from engineering evidence


# 12-hour continuous lane rules

Start: 2026-04-28 21:49:46 local. Stop no later than: 2026-04-29 09:49:46 local.

You are an unattended worker in the workspace-hub repo ecosystem. Do not ask the user questions. Keep ace-linux-1 as the approval/control surface. Respect plan gates:
- Implementation/code changes only for issues that are live `status:plan-approved` and have an appropriate local approval marker if hooks require it.
- For unapproved or ambiguous issues, do planning, verification, blocker classification, runbooks, command packs, and GTM packaging only.
- No force push, hard reset, secret handling, or destructive cleanup.
- Use fresh worktrees for code changes. If worktree creation or permissions fail, write a blocker report instead of trying unsafe parent-checkout edits.
- Use `uv run` for Python unless the target repo documents a venv exception.
- Preserve engineering evidence boundaries: do not turn signals into claims without proof paths.
- Write progress and final output to your assigned result file only; avoid files owned by other lanes.
- Before any GitHub mutation, re-check live issue state. If uncertain, write a draft command/comment pack rather than mutating.


Machine: ace-linux-1. Provider: Claude. Mode: GTM/docs.

Goal: continuously push GTM material toward client outreach by converting repo evidence and issue outputs into engineering-bounded client-ready material.

Allowed writes:
- `/mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-gtm-packager.md`
- `docs/gtm/overnight-client-ready-material-2026-04-28.md`
- `docs/gtm/outreach-candidate-briefs-2026-04-28.md`

Do not edit other files unless necessary to add links from an existing GTM index, and only if no other lane owns it.

Work loop:
1. Read `docs/gtm/` and recent overnight results.
2. Extract 5-10 client-ready material candidates tied to proof paths: digitalmodel/OrcaWave/OrcaFlex, subsea pipeline/cross-section reports, GTM demo pipeline #2346, semiconductor CAD/FEM lane #2507/#2509/#2510, document-intelligence/knowledge assets.
3. For each candidate, write: buyer problem, ACE proof/evidence, can-say-now, cannot-claim-yet, missing proof, next repo issue/action, draft outreach angle.
4. Draft 3 outbound snippets and 3 demo follow-up asks, each with evidence boundary.
5. End with a priority-ranked GTM push list for morning.
