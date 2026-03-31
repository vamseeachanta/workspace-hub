# Legacy Notice

**Status:** Legacy — frozen. Do not extend or build new workflows here.

This directory contains the slash command ecosystem (command registry, modules, documentation), which has been superseded by the minimal harness operating model. Slash commands are treated as optional frontends, not the core architecture.

## What replaced it

- **Orchestration:** Claude Code (`.claude/` — skills, rules, hooks)
- **Execution:** Codex (`.codex/` adapter)
- **Research:** Gemini (`.gemini/` adapter)
- **Contract:** [AGENTS.md](../AGENTS.md) is the canonical entry point

## References

- [Control-Plane Contract](../docs/standards/CONTROL_PLANE_CONTRACT.md)
- [AI Review Routing Policy](../docs/standards/AI_REVIEW_ROUTING_POLICY.md)
- [Minimal Harness Operating Model](../docs/modules/ai/MINIMAL_HARNESS_OPERATING_MODEL_2026-03.md)

## Disposition

This directory may be removed in a future cleanup pass. Do not add new commands, modules, or registry entries here.
