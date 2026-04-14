# Agent Delegation Templates

> Reference for `task_agents:` field in WRK frontmatter. Derived from
> `config/agents/behavior-contract.yaml § task_type_matrix`. See
> `scripts/coordination/routing/lib/task_classifier.sh` for automated classification.

## Quick Reference

| Task Type | Route | Primary | Secondary | Tertiary | Gate |
|-----------|-------|---------|-----------|----------|------|
| feature | A | codex | — | — | codex_approve |
| feature | B | codex | claude | — | claude_approve |
| feature | C | claude | codex | gemini | two_of_three_approve |
| bugfix | A/B/C | codex | claude | — | codex_approve |
| refactor | A/B/C | codex | gemini | — | codex_approve |
| test-writing | A/B/C | codex | claude | — | codex_approve |
| research | A/B/C | gemini | claude | — | claude_approve |
| docs | A/B/C | gemini | claude | — | claude_approve |
| architecture | C | claude | gemini | — | two_of_three_approve |
| integration | B/C | claude | codex | — | claude_approve |
| debugging | A/B | codex | claude | — | codex_approve |

## task_agents Frontmatter Maps

Copy the relevant block into the WRK frontmatter `task_agents:` field.

### Feature / Route A (simple, single-file)

```yaml
task_agents:
  phase_10: codex  # implement
  phase_12: codex  # TDD
  phase_13: claude # cross-review
```

### Feature / Route B (medium, 1-2 files)

```yaml
task_agents:
  phase_4: claude  # plan draft
  phase_10: codex  # implement
  phase_12: codex  # TDD
  phase_13: claude # cross-review
```

### Feature / Route C (complex, multi-module)

```yaml
task_agents:
  phase_4: claude  # plan draft (Opus for architecture)
  phase_6: gemini  # plan cross-review
  phase_10: codex  # implement
  phase_12: codex  # TDD
  phase_13: claude # cross-review
  phase_13b: gemini # secondary cross-review
```

### Bug Fix (all routes)

```yaml
task_agents:
  phase_10: codex  # diagnose + fix
  phase_12: codex  # regression tests
  phase_13: claude # cross-review (escalate if systemic)
```

### Refactor

```yaml
task_agents:
  phase_10: codex  # restructure
  phase_11: gemini # change summary doc
  phase_13: claude # cross-review
```

### Test Writing

```yaml
task_agents:
  phase_10: codex  # TDD generation primary
  phase_13: claude # edge-case coverage review
```

### Research / Analysis

```yaml
task_agents:
  phase_2: gemini  # resource intelligence (large-context corpus)
  phase_10: gemini # research synthesis
  phase_10b: claude # findings synthesis
```

### Documentation

```yaml
task_agents:
  phase_10: gemini # draft (large-context sources)
  phase_13: claude # edit for conciseness and rule compliance
```

### Architecture / Design (Route C)

```yaml
task_agents:
  phase_4: claude  # architecture plan
  phase_6: gemini  # plan cross-check vs specs/standards
  phase_10: claude # design implementation
  phase_13: gemini # secondary cross-review
```

### Integration / Wiring

```yaml
task_agents:
  phase_4: claude  # cross-module plan
  phase_10: claude # wiring implementation
  phase_10b: codex # discrete connector implementation
  phase_13: claude # cross-review
```

### Debugging (systematic)

```yaml
task_agents:
  phase_10: codex  # focused code trace
  phase_13: claude # escalate if systemic
```

## Decision Rules

1. **Route A** — prefer Codex for all execution; Claude only for cross-review gate
2. **Route B** — Claude plans; Codex implements; Claude gates
3. **Route C** — Claude architects; Codex implements; Gemini cross-checks; 2-of-3 gate
4. **Research/Docs** — Gemini leads (1M-token context); Claude synthesizes/edits
5. **Quota-aware override**: if Claude quota ≥ 70% (H) → demote Claude to review-only;
   escalate Codex as primary implementer even on Route C

## Automated Classification

```bash
# Classify a task description and get provider recommendation
source scripts/coordination/routing/lib/task_classifier.sh
classify_task "your task description here"
```

Output JSON includes `tier` (simple/standard/complex), `primary_provider`, and `all_scores`.

## References

- `config/agents/behavior-contract.yaml § task_type_matrix` — canonical source of truth
- `scripts/coordination/routing/lib/task_classifier.sh` — automated classification engine
- `scripts/coordination/routing/lib/provider_recommender.sh` — provider selection from classification
- `.claude/state/provider-assessments/` — empirical performance data
