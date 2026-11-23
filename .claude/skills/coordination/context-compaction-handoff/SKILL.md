---
name: context-compaction-handoff
description: Guardrails for resuming work after context compaction or transcript handoff blocks; prioritize the latest real user request over stale summarized tasks and verify before answering.
---

# Context Compaction Handoff

Use this skill whenever the conversation includes a context-compaction summary, transcript handoff, or other generated summary block that says it is background/reference-only.

## Core rule

A compaction block is background evidence, not the active instruction. Resume from the latest real user message after the compaction marker. If the latest user message conflicts with the summary's `Active Task`, the latest user message wins.

## Procedure

1. **Separate source types**
   - Treat explicit user messages as active instructions.
   - Treat compaction summaries as historical context unless the latest user asks to resume them.

2. **Locate the active request**
   - First scan below the compaction marker for the latest user-authored request.
   - If no real user request exists after the marker, fall back to the latest visible real user request immediately before the compaction block, as long as it has not already been answered.
   - If the compaction block says summary generation was unavailable or contains no reliable active-task section, do not treat old todos/final summaries as active; either continue the last visible unanswered user request or ask for clarification.
   - Never invent a task from the generated summary itself.

3. **Revalidate before acting**
   - If the active request asks for evidence, logs, state, or current facts, inspect the relevant sources before answering.
   - Do not answer from the compaction summary when the user asked for live verification.

4. **Avoid stale closeout leakage**
   - Do not use old todo lists, issue-closeout summaries, or prior final-response wording as the answer to a new post-compaction question.
   - If a todo list was reconstructed from the compaction summary, keep it separate from the latest user request unless the request explicitly matches it.

## Pitfalls

- **Wrong:** A compaction says `Active Task: None`, but the pre-compaction visible user asked a new evidence-gathering question. The agent answers with a completed old closeout summary.
- **Right:** The agent identifies the latest real user request, loads relevant skills, inspects the requested evidence, and answers only that request.

## References

- `references/compaction-latest-user-message-guard.md` — session-specific failure mode and recovery checklist.
