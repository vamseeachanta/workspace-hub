# Provider skill discovery surface

The authored source is [`.claude/skills`](../../.claude/skills).
This directory contains provider-facing copies and, where migrated, thin adapters.
Source ownership does not determine runtime discovery precedence.

Codex repository discovery uses `.agents/skills` between the working directory and
repository root. Duplicate names are not merged by the loader. See the
[official skill documentation](https://learn.chatgpt.com/docs/build-skills).
Other consumers require their own current runtime evidence.

| Tree | Role and evidence |
|---|---|
| `.claude/skills/` | Canonical authored source; ownership does not override loader precedence. |
| `.agents/skills/` | Documented Codex discovery root; Gemini loading was historically observed. |
| `.codex/skills` | Legacy compatibility link referenced by repository tooling; not proof of native loading. |
| `.gemini/skills/` | Historical Gemini skill location; current configuration and precedence require inspection. |

The June 2026 Gemini record reported: `Skill conflict detected ... from .agents/skills/... is overriding ... .gemini/skills/...`.
That startup signal can be checked in a bounded native trial; it was not reproduced
by this documentation cleanup.

## Migration

- Use one canonical skill and focused references; keep provider adapters thin.
- Before retiring a copy, inspect its differences and migrate unique requirements
  and active callers. Verify the replacement path and reference resolution.
- Do not mechanically replace provider names throughout skill bodies.
- Do not bulk-delete this discovery tree before replacing verified consumers.
- Preserve native system skills, plugins, credentials and unrelated user settings.
- A task profile selects intended skills; it does not install or configure discovery.

The historical [retention decision](https://github.com/vamseeachanta/workspace-hub/issues/3039)
recorded Gemini loading this directory in June 2026. That explains why unqualified
deletion is inappropriate; it does not establish current fleet loading or justify
permanent duplicate authorities. The current
[cleanup decision record](../../docs/reports/2026-09-13-issue-3615-ecosystem-cleanup.html#operating-decisions)
requires verified consolidation and retirement.

The tracked `.codex/skills` compatibility link may be materialized as a text file
on Windows. Its existence is not proof of Codex loading; repository tooling still
references it, so its retirement requires caller migration.
