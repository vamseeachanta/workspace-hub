---
name: "gsd-debug"
description: "Systematic debugging with persistent state across context resets"
metadata:
  short-description: "Systematic debugging with persistent state across context resets"
---

See [references/codex-adapter.md](references/codex-adapter.md) for the Codex skill adapter (AskUserQuestion/Task mapping).

<objective>
Debug issues using scientific method with subagent isolation.

**Orchestrator role:** Gather symptoms, spawn gsd-debugger agent, handle checkpoints, spawn continuations.

**Why subagent:** Investigation burns context fast (reading files, forming hypotheses, testing). Fresh 200k context per investigation. Main context stays lean for user interaction.
</objective>

<context>
User's issue: {{GSD_ARGS}}

Check for active sessions:
```bash
ls .planning/debug/*.md 2>/dev/null | grep -v resolved | head -5
```
</context>

<process>

## 0. Initialize Context

```bash
INIT=$(node "/mnt/local-analysis/workspace-hub/.codex/get-shit-done/bin/gsd-tools.cjs" state load)
if [[ "$INIT" == @file:* ]]; then INIT=$(cat "${INIT#@file:}"); fi
```

Extract `commit_docs` from init JSON. Resolve debugger model:
```bash
debugger_model=$(node "/mnt/local-analysis/workspace-hub/.codex/get-shit-done/bin/gsd-tools.cjs" resolve-model gsd-debugger --raw)
```

## 1. Check Active Sessions

If active sessions exist AND no {{GSD_ARGS}}:
- List sessions with status, hypothesis, next action
- User picks number to resume OR describes new issue

If {{GSD_ARGS}} provided OR user describes new issue:
- Continue to symptom gathering

## 2. Gather Symptoms (if new issue)

Use AskUserQuestion for each:

1. **Expected behavior** - What should happen?
2. **Actual behavior** - What happens instead?
3. **Error messages** - Any errors? (paste or describe)
4. **Timeline** - When did this start? Ever worked?
5. **Reproduction** - How do you trigger it?

After all gathered, confirm ready to investigate.

## 3. Spawn gsd-debugger Agent

See [references/debugger-prompt.md](references/debugger-prompt.md) for the full debugger agent prompt template.

```
Task(
  prompt=filled_prompt,
  subagent_type="gsd-debugger",
  model="{debugger_model}",
  description="Debug {slug}"
)
```

## 4. Handle Agent Return

**If `## ROOT CAUSE FOUND`:**
- Display root cause and evidence summary
- Offer: "Fix now" (spawn fix subagent), "Plan fix" ($gsd-plan-phase --gaps), "Manual fix" (done)

**If `## CHECKPOINT REACHED`:**
- Present checkpoint details to user, get response
- If `human-verify`: user confirms fixed -> finalize; user reports issues -> return to investigation
- Spawn continuation agent (see step 5)

**If `## INVESTIGATION INCONCLUSIVE`:**
- Show what was checked and eliminated
- Offer: "Continue investigating", "Manual investigation", "Add more context"

## 5. Spawn Continuation Agent (After Checkpoint)

See [references/debugger-prompt.md](references/debugger-prompt.md) for the continuation prompt template.

```
Task(
  prompt=continuation_prompt,
  subagent_type="gsd-debugger",
  model="{debugger_model}",
  description="Continue debug {slug}"
)
```

</process>

<success_criteria>
- [ ] Active sessions checked
- [ ] Symptoms gathered (if new)
- [ ] gsd-debugger spawned with context
- [ ] Checkpoints handled correctly
- [ ] Root cause confirmed before fixing
</success_criteria>
