# Conversation-review skill update mode

Use when the user explicitly asks to review the conversation and update the skill library.

## Operating rule

This is a bounded skill-maintenance action, not the heavyweight comprehensive-learning pipeline. Act inside the skill library directly.

## Target shape

Prefer class-level skills with:

- a rich `SKILL.md` containing triggers, sequence, pitfalls, and verification rules;
- concise support files under `references/` for session-specific detail or condensed knowledge banks;
- `templates/` only for copy-and-modify starter artifacts;
- `scripts/` only for deterministic re-runnable probes or helpers.

Avoid one-session-one-skill sprawl. If the proposed skill name only makes sense for today's task, patch an existing umbrella instead.

## Patch order

1. Patch a skill that was loaded or consulted in the current session if it governs the lesson.
2. Otherwise patch an existing class-level umbrella skill.
3. Add a support file under that umbrella when the lesson is detailed, evidence-heavy, or session-specific.
4. Create a new class-level umbrella only when no existing skill covers the class.

## Signals that warrant action

Treat any of these as first-class skill signals:

- user corrected style, tone, format, legibility, verbosity, or workflow sequence;
- a non-trivial technique, workaround, closeout pattern, or tool-use sequence emerged;
- a loaded skill was incomplete, stale, or missing a pitfall;
- hooks/tooling created follow-up metadata dirt that required another closeout loop;
- a task exposed a reusable distinction such as external-action status vs repo-side verification.

## Do not encode

Do not harden transient setup failures or negative tool claims into durable skills. If setup failed, capture the fix under an existing setup/troubleshooting skill. If a retry worked, capture the retry or verification pattern, not the temporary failure.

## Closeout

After skill edits, report:

- skill(s) updated;
- support files added;
- memory changes, if any;
- overlaps noticed for curator consolidation;
- whether no external action was performed.
