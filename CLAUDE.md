# Workspace Hub — Claude Adapter
> Canonical instructions: AGENTS.md | Rules: `.claude/rules/` | Docs: `docs/`, `.claude/docs/`
## Claude-Specific
- Retrieval first — consult `docs/`, `.claude/docs/`, `.claude/rules/`, memory before training knowledge
- Workflow: GSD framework (`/gsd:help`, `/gsd:progress`, `/gsd:settings`)
- Skills: `/skills` on-demand | `/ecosystem-terminology` for naming
- Context: Global 2KB + Workspace 4KB + Project 8KB + Local 2KB = 16KB max
## Planning Workflow (ALL issues — mandatory)
- Load `issue-planning-mode` skill before any issue work: `.claude/skills/coordination/issue-planning-mode/SKILL.md`
- Steps: Issue → Resource Intel → Plan → Adversarial Review → `status:plan-review` → USER APPROVES → `status:plan-approved` → Implement
- Template: `docs/plans/_template-issue-plan.md` | Full guide: `docs/plans/README.md`
- Batch agents: only act on `status:plan-approved` issues; never self-approve
