# Discipline Skill Template: Rationalization Defense Pattern

## When to Use

Add this pattern to any skill that **enforces constraints** -- skills where violation has real consequences (broken builds, data loss, coordination failures, naming collisions). Do NOT add it to guidance-only or reference skills.

Indicators that a skill needs this pattern:
- Contains "must", "never", "always", "required", "mandatory" language
- Defines hard limits, gates, or anti-patterns
- Violations have been observed in production (corrections/ entries, incident history)
- The skill is invoked frequently enough that rationalization pressure is high

## Template

Add these three sections at the **end** of the SKILL.md body, after all existing content:

```markdown
## Iron Law

> [One absolute sentence. No qualifiers, no wiggle room. Format: "No X without Y, ever." or "No X shall Y — ever."]

## Rationalization Defense

| Excuse | Reality |
|--------|---------|
| [Common agent rationalization 1] | [Why it is wrong — specific, blunt] |
| [Common agent rationalization 2] | [Why it is wrong] |
| [Common agent rationalization 3] | [Why it is wrong] |

## Red Flags

These phrases signal you are about to violate the Iron Law:
- [Trigger phrase 1 — something the agent would think/say before violating]
- [Trigger phrase 2]
- [Trigger phrase 3]
```

## Writing Guidelines

**Iron Law**: One sentence. Absolute. No escape clauses. If you find yourself adding "unless" or "except when", the law is too narrow — broaden it.

**Rationalizations**: Draw from real agent failure modes:
- "This is trivial / minor / a special case"
- "I'll do it later / in a follow-up"
- "The user didn't ask for this"
- "Tests already pass"
- "It's probably fine"
- "Just this once"

**Red Flags**: Specific phrases the agent would use right before violating. Not abstract concepts — actual strings of text that appear in agent reasoning.

## Worked Examples

### Example 1: Sync Verification (from `workspace-hub/sync`)

```markdown
## Iron Law

> No sync shall be reported as successful without completing Phase 7 verification and confirming all four success criteria pass — ever.

## Rationalization Defense

| Excuse | Reality |
|--------|---------|
| "All the pushes succeeded so it's done" | Push success does not equal sync success. Detached HEADs, dirty repos, and pointer mismatches are invisible without verification. |
| "Verification is redundant — I watched each step succeed" | Individual step success does not guarantee end-state correctness. Verification checks the final state, not the steps. |
| "I'll skip verification because the user is waiting" | A false-positive "sync complete" causes harder-to-debug failures later. The 10 seconds verification takes prevents hours of debugging. |
| "Only one repo changed, no need for full verification" | Submodule pointers and cross-repo state can break from a single repo change. Always verify all four criteria. |

## Red Flags

These phrases signal you are about to violate the Iron Law:
- "sync looks good" (without running `git submodule status`)
- "all repos pulled successfully, we're done"
- "skipping verification to save time"
- "probably fine — no errors were reported"
```

### Example 2: Clean Code Limits (from `workspace-hub/clean-code`)

```markdown
## Iron Law

> No file shall exceed the hard limit, and no function shall exceed 50 lines — no exceptions, no deferrals, no "I'll refactor later."

## Rationalization Defense

| Excuse | Reality |
|--------|---------|
| "It's only slightly over the limit" | Limits exist at exact thresholds for a reason — 301 lines is a violation, not a rounding error. Split now. |
| "Splitting this file would be premature" | The limit exists precisely because developers always say this. The file is already too large; splitting is overdue, not premature. |
| "I'll refactor after I finish the feature" | Post-feature refactors have a near-zero completion rate. The limit is enforced at write time, not review time. |
| "This function is complex — it needs to be long" | Complex functions need to be decomposed, not excused. Length is a symptom of missing abstractions. |

## Red Flags

These phrases signal you are about to violate the Iron Law:
- "just a few lines over"
- "I'll clean this up in a follow-up"
- "splitting would add unnecessary complexity"
- "this is a one-off / special case"
- "the logic is tightly coupled — it has to stay together"
```
