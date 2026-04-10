# Workspace Hub — Gemini Adapter
> Canonical instructions: AGENTS.md | Docs: `docs/`
## Gemini-Specific
- Retrieval first — consult `docs/` for reference maps and domain guides before searching
- Wrapper scripts: `scripts/agents/session.sh`, `work.sh`, `plan.sh`, `execute.sh`, `review.sh`
- Cross-review: `echo content | gemini -p "prompt" -y`
- Gate evidence: use current workflow anchors in `AGENTS.md`, `docs/work-queue-workflow.md`, and `docs/governance/SESSION-GOVERNANCE.md` (the old `scripts/work-queue/verify-gate-evidence.py` path is legacy only; see `docs/ops/legacy-claude-reference-map.md`)
