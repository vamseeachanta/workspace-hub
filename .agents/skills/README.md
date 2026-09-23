# .agents/skills — cross-agent skills surface (NOT dead weight)

**Do not delete.** Live-verified 2026-06-11: the Gemini CLI loads skills from this
directory (it reports "Skill conflict detected ... from .agents/skills/... is
overriding ... .gemini/skills/..." at startup). `.agents/` is the cross-provider
agent surface, analogous to `AGENTS.md`.

Relationship to the other skill trees:

| Tree | Consumer | Notes |
|---|---|---|
| `.claude/skills/` | Claude Code (canonical, freshest) | wins on conflicts per SOUL.delta |
| `.codex/skills` | Historical Codex adapter pointer | The inspected Windows checkout contains a 17-byte regular path file, not a working filesystem link; no repair is performed by this materializer. |
| `.agents/skills/` | Codex native project discovery; historical Gemini consumer | Shared copy surface with provider-adapted deltas; drifts. Codex CLI 0.154.0 discovery was observed on 2026-09-14; current Gemini execution is unverified. |
| `.gemini/skills/` | Gemini CLI (overridden by `.agents/skills` on conflict) | legacy location |

Known hazards:
- This tree is a periodic copy of `.claude/skills/` with mechanical provider rewrites;
  some rewrites are nonsense (e.g., `dspy.Codex(model="Codex-sonnet-...")` is not a real
  API). Treat `.claude/skills/` as authoritative when content disagrees.
- Last bulk sync 2026-05-04. If drift matters for a skill you need under Gemini,
  re-copy that skill family from `.claude/skills/`.

Disposition decision (workspace-hub #3039, 2026-06-11): KEEP + document (this file).
Full-tree synchronization remains deferred. The bounded Foundation materializer,
`scripts/skills/materialize_profile.py`, consumes the existing profile's separate
`adapters.repository_installation` mapping. It owns exactly four skill files and
two reference files beneath the existing `data`, `research`, and `coordination`
families. It does not synchronize this full tree, repair `.codex/skills`, change
Gemini ownership, or alter plugins, hooks or user settings. Source ownership stays
with `.claude/skills`; historical flat pilot fixture layouts remain separate.

Default report/dry-run writes JSON to stdout only. Explicit apply requires the
exact source/target roots, source revision and actual profile/payload digests, plus
an external same-volume transaction directory and root-orchestrated coordination.
An installed copy is not proof of native runtime behavior or provider parity.
