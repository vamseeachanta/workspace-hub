# Workspace Hub — Claude Adapter
> Canonical instructions: AGENTS.md | Rules: `.claude/rules/` | Docs: `docs/`, `.claude/docs/`
## Claude-Specific
- Retrieval first — consult `docs/`, `.claude/docs/`, `.claude/rules/`, memory before training knowledge
- Workflow: GSD framework (`/gsd:help`, `/gsd:progress`, `/gsd:settings`)
- Skills: `/skills` on-demand | `/ecosystem-terminology` for naming
- Context: Global 2KB + Workspace 4KB + Project 8KB + Local 2KB = 16KB max
## Planning Workflow (ALL issues)
- Load `.claude/skills/coordination/issue-planning-mode/SKILL.md` before drafting any plan
- Template: `docs/plans/_template-issue-plan.md` — copy per issue to `docs/plans/YYYY-MM-DD-issue-NNN-slug.md`
- Labels: `status:plan-review` (awaiting user approval) → `status:plan-approved` (cleared for implementation)
- Batch execution agents must only act on `status:plan-approved` issues
