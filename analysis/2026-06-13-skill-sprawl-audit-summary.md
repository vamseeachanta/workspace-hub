<!-- Generated 2026-06-13 by scripts/skills/skill_sprawl_audit.py. Epic #3058 / #3062. SANITIZED (no per-skill names — see note). -->
# Skill sprawl audit — summary (2026-06-13)

Non-destructive audit of the skills tree (#3062, harden-ecosystem epic #3058). Nothing moved or deleted; this is the reviewable signal before any retirement.

> **Per-skill candidate names are intentionally omitted here.** Some skill names embed client identifiers (see finding below) and this file is in a public repo. Run `uv run --with pyyaml python scripts/skills/skill_sprawl_audit.py --json` locally for the full named candidate list.

## Scored skills (from `.claude/state/skill-scores.yaml`, generated 2026-04-03)
- **402 scored top-level skills.** Tiers: **hot 100 · warm 152 · cold 45 · dead 105**.
- The live `.claude/skills/` tree holds **~3,113 `SKILL.md` files** (top-level + sub-skills/references).

## Retirement candidates
- **172 candidates** under the approved rule: `baseline_usage_rate < 0.05` AND `calls_in_period < 10`, exempting `framework_usage` and parent skills (structural).
- That's ~43% of scored skills — confirming material sprawl that raises every model's first-token decision cost.
- **Next step (reviewed follow-up):** operator reviews the named list, then a separate change *archives* (reversible — not deletes) the confirmed-dead set.

## Archive-tree consolidation
Three archive trees exist; two appear duplicated:
- `.claude/skills/_archive` — ~2,100 `SKILL.md`
- `.claude/skills-archive` — ~2,100 `SKILL.md` (same count — likely a duplicate of the above)
- `_archive/skills` — ~88 `SKILL.md`

The archives hold **more** `SKILL.md` than the live tree. Recommend consolidating to a single convention with a dated manifest. (Confirm whether the two ~2,100 trees are a symlink or a real duplicate before consolidating.)

## Finding — pre-existing client identifier in a public file
`.claude/skills/data/energy/fdas-economics/SKILL.md` (and its `skill-scores.yaml` entry) embed a client abbreviation, which violates the "workspace-hub is public — no client PII" rule. This predates this audit. **Recommend:** rename to a generic slug or route the skill to a private location, tracked separately from the sprawl cleanup.

## Deferred from v1
Retrieval hit-rate (how often loaded/nudged skills are actually invoked) requires correlating session telemetry with skill loads — a follow-up once the candidate set is pruned.
