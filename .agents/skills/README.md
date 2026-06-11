# .agents/skills — cross-agent skills surface (NOT dead weight)

**Do not delete.** Live-verified 2026-06-11: the Gemini CLI loads skills from this
directory (it reports "Skill conflict detected ... from .agents/skills/... is
overriding ... .gemini/skills/..." at startup). `.agents/` is the cross-provider
agent surface, analogous to `AGENTS.md`.

Relationship to the other skill trees:

| Tree | Consumer | Notes |
|---|---|---|
| `.claude/skills/` | Claude Code (canonical, freshest) | wins on conflicts per SOUL.delta |
| `.codex/skills` | Codex CLI | symlink → `.claude/skills` (no duplication) |
| `.agents/skills/` | Gemini CLI (+ any AGENTS-convention runtime) | full copy with provider-adapted deltas; drifts |
| `.gemini/skills/` | Gemini CLI (overridden by `.agents/skills` on conflict) | legacy location |

Known hazards:
- This tree is a periodic copy of `.claude/skills/` with mechanical provider rewrites;
  some rewrites are nonsense (e.g., `dspy.Codex(model="Codex-sonnet-...")` is not a real
  API). Treat `.claude/skills/` as authoritative when content disagrees.
- Last bulk sync 2026-05-04. If drift matters for a skill you need under Gemini,
  re-copy that skill family from `.claude/skills/`.

Disposition decision (workspace-hub #3039, 2026-06-11): KEEP + document (this file).
A sync script is deliberately deferred until drift causes a real incident.
