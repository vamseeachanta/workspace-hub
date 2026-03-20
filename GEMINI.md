# Workspace Hub — Gemini Adapter
> Canonical instructions: AGENTS.md
## Gemini-Specific
- Wrapper scripts: `scripts/agents/session.sh`, `work.sh`, `plan.sh`, `execute.sh`, `review.sh`
- Cross-review: `echo content | gemini -p "prompt" -y`
- Gate evidence: `scripts/work-queue/verify-gate-evidence.py WRK-NNN`
