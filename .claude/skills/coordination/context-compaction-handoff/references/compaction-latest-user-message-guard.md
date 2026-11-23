# Compaction latest-user-message guard

## Session-specific trigger

A context compaction block appeared after the user had asked whether native Claude work in the repo ecosystem was flowing through Hermes Agent and specifically requested checking Claude session logs/evidence before answering.

The agent then treated the compaction closeout summary as the active task and replied with old issue-closeout evidence instead of investigating Claude session logs.

## Generalized lesson

This is a context-priority failure:

- Compaction summaries are evidence/background only.
- Latest real user request controls the next action.
- Evidence requests require fresh inspection before final answers.

## Checklist for future runs

1. Find the newest user-authored request outside the compaction summary.
2. State the active request internally before taking action.
3. Ignore old `Active Task`, `Completed Actions`, and `Remaining Work` sections unless the newest request asks to resume them.
4. If the newest request asks for logs/session evidence, inspect those logs before answering.
5. If unsure whether the latest request survived compaction, ask a narrow clarification instead of executing stale summarized work.
