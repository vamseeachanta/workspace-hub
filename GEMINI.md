# Workspace Hub — Gemini Adapter
> Canonical instructions: AGENTS.md | Docs: `docs/`
## Gemini-Specific
- Retrieval first — consult `docs/` for reference maps and domain guides before searching
- Wrapper scripts: `scripts/agents/session.sh`, `work.sh`, `plan.sh`, `execute.sh`, `review.sh`
- Cross-review: `echo content | gemini -p "prompt" -y`
- Gate evidence: `scripts/work-queue/verify-gate-evidence.py WRK-NNN`
