---
name: "gsd-research-phase"
description: "Research how to implement a phase (standalone - usually use $gsd-plan-phase instead)"
metadata:
  short-description: "Research how to implement a phase (standalone - usually use $gsd-plan-phase instead)"
---

See [references/codex-adapter.md](references/codex-adapter.md) for the Codex skill adapter (AskUserQuestion/Task mapping).

<objective>
Research how to implement a phase. Spawns gsd-phase-researcher agent with phase context.

**Note:** This is a standalone research command. For most workflows, use `$gsd-plan-phase` which integrates research automatically.

**Use this command when:**
- You want to research without planning yet
- You want to re-research after planning is complete
- You need to investigate before deciding if a phase is feasible

**Orchestrator role:** Parse phase, validate against roadmap, check existing research, gather context, spawn researcher agent, present results.

**Why subagent:** Research burns context fast (WebSearch, Context7 queries, source verification). Fresh 200k context for investigation. Main context stays lean for user interaction.
</objective>

<context>
Phase number: {{GSD_ARGS}} (required)

Normalize phase input in step 0 before any directory lookups.
</context>

<process>

## 0. Initialize Context

```bash
INIT=$(node "/mnt/local-analysis/workspace-hub/.codex/get-shit-done/bin/gsd-tools.cjs" init phase-op "{{GSD_ARGS}}")
if [[ "$INIT" == @file:* ]]; then INIT=$(cat "${INIT#@file:}"); fi
```

Extract from init JSON: `phase_dir`, `phase_number`, `phase_name`, `phase_found`, `commit_docs`, `has_research`, `state_path`, `requirements_path`, `context_path`, `research_path`.

Resolve researcher model:
```bash
RESEARCHER_MODEL=$(node "/mnt/local-analysis/workspace-hub/.codex/get-shit-done/bin/gsd-tools.cjs" resolve-model gsd-phase-researcher --raw)
```

## 1. Validate Phase

```bash
PHASE_INFO=$(node "/mnt/local-analysis/workspace-hub/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase "${phase_number}")
```

**If `found` is false:** Error and exit. **If `found` is true:** Extract `phase_number`, `phase_name`, `goal` from JSON.

## 2. Check Existing Research

```bash
ls .planning/phases/${PHASE}-*/RESEARCH.md 2>/dev/null
```

**If exists:** Offer: 1) Update research, 2) View existing, 3) Skip.
**If doesn't exist:** Continue.

## 3. Gather Phase Context

Use paths from INIT (do not inline file contents in orchestrator context):
- `requirements_path`
- `context_path`
- `state_path`

Present summary with phase description and what files the researcher will load.

## 4. Spawn gsd-phase-researcher Agent

Research modes: ecosystem (default), feasibility, implementation, comparison.

See [references/researcher-prompt.md](references/researcher-prompt.md) for the full researcher agent prompt template.

```
Task(
  prompt=filled_prompt,
  subagent_type="gsd-phase-researcher",
  model="{researcher_model}",
  description="Research Phase {phase}"
)
```

## 5. Handle Agent Return

**`## RESEARCH COMPLETE`:** Display summary, offer: Plan phase, Dig deeper, Review full, Done.

**`## CHECKPOINT REACHED`:** Present to user, get response, spawn continuation.

**`## RESEARCH INCONCLUSIVE`:** Show what was attempted, offer: Add context, Try different mode, Manual.

## 6. Spawn Continuation Agent

See [references/researcher-prompt.md](references/researcher-prompt.md) for the continuation prompt template.

```
Task(
  prompt=continuation_prompt,
  subagent_type="gsd-phase-researcher",
  model="{researcher_model}",
  description="Continue research Phase {phase}"
)
```

</process>

<success_criteria>
- [ ] Phase validated against roadmap
- [ ] Existing research checked
- [ ] gsd-phase-researcher spawned with context
- [ ] Checkpoints handled correctly
- [ ] User knows next steps
</success_criteria>
