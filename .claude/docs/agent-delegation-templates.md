# Agent Delegation Templates

> Version: 1.0 | WRK-118 Phase 2 | Updated: 2026-02-24
> Empirical role matrix from 70+ archived WRK items (55 claude / 14 codex / 11 gemini).

## Role Matrix

| Task Type    | Primary | Secondary | Tertiary | Quality Gate     |
|--------------|---------|-----------|----------|------------------|
| feature/A    | codex   | —         | —        | codex approve    |
| feature/B    | codex   | claude    | —        | claude approve   |
| feature/C    | claude  | codex     | gemini   | 2-of-3 approve   |
| bugfix       | codex   | claude    | —        | codex approve    |
| refactor     | codex   | gemini    | —        | codex approve    |
| test-writing | codex   | claude    | —        | codex approve    |
| research     | gemini  | claude    | —        | claude approve   |
| docs         | gemini  | claude    | —        | claude approve   |
| architecture | claude  | gemini    | —        | 2-of-3 approve   |
| integration  | claude  | codex     | —        | claude approve   |
| debugging    | codex   | claude    | —        | codex approve    |

**Rationale:** Codex for focused single-file code/test; Claude for multi-module arch/integration;
Gemini for 1M-token research/docs synthesis.

---

## Standard task_agents Maps

### feature/A
```yaml
task_agents:
  phase_1: codex    # implement + tests
  phase_2: codex    # cross-review
```

### feature/B
```yaml
task_agents:
  phase_1: claude   # plan + spec
  phase_2: codex    # implement + test
  phase_3: claude   # review
```

### feature/C
```yaml
task_agents:
  phase_1: claude   # architecture + spec
  phase_2: codex    # implement modules
  phase_3: claude   # integration wiring
  phase_4: gemini   # cross-review + docs
  phase_5: claude   # merge gate
```

### bugfix
```yaml
task_agents:
  phase_1: codex    # diagnose + fix
  phase_2: codex    # regression tests
  phase_3: claude   # review (cross-cutting only)
```

### refactor
```yaml
task_agents:
  phase_1: codex    # restructure
  phase_2: gemini   # change-summary doc
  phase_3: codex    # verify tests green
```

### test-writing
```yaml
task_agents:
  phase_1: codex    # generate tests (TDD)
  phase_2: claude   # review edge-case coverage
```

### research / docs
```yaml
task_agents:
  phase_1: gemini   # gather / draft
  phase_2: claude   # distill / edit for rule compliance
```

### architecture / integration
```yaml
task_agents:
  phase_1: claude   # design + spec
  phase_2: gemini   # cross-check standards   # or codex for integration
  phase_3: claude   # finalize + cross-review
```

---

## Invocation Patterns

| Provider | Command | Input | Output |
|----------|---------|-------|--------|
| Claude | `claude` (interactive) or `cross-review.sh <file> claude` | Markdown spec/diff | Verdict + comments |
| Codex | `codex exec "<task>"` or `codex review --commit <sha>` | NL task + context files | Diff + summary |
| Gemini | `gemini --prompt "<task>"` or `cross-review.sh <file> gemini` | Prompt + files | Markdown / verdict |

Cross-review (all providers):
```bash
bash scripts/review/cross-review.sh <spec-or-diff> all
```

---

## Quality Gate Definitions

**`codex_approve`** — Codex verdict `APPROVE` or `MINOR`. `MAJOR`/`REJECT` hard-blocks.
`NO_OUTPUT` triggers codex_fallback (see `behavior-contract.yaml`).

**`claude_approve`** — Claude verdict `APPROVE` or `MINOR`. `NO_OUTPUT` treated as `MAJOR`.

**`two_of_three_approve`** (feature/C, architecture) — All three providers review;
at least 2 must return `APPROVE`/`MINOR`. One `MAJOR` with the other two `APPROVE` still fails.
Codex `NO_OUTPUT` + Claude+Gemini `APPROVE` → `CONDITIONAL_PASS`.

---

## References

- `config/agents/behavior-contract.yaml` → `task_type_matrix` (canonical role data)
- `config/agents/routing-config.yaml` → tier routing
- WRK-199 → automates task_agents population via task_classifier
- `scripts/coordination/routing/lib/provider_recommender.sh`
