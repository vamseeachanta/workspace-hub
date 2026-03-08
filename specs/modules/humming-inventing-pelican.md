# WRK-1035 Plan — Beef up user-review stages in work-queue-workflow SKILL

## Context

WRK-1034 revealed that Stage 5 and Stage 7 approval artifacts were written with retroactive
timestamps before the user had explicitly responded in conversation. The current skills say
"user must respond" but do not prohibit writing the artifact before that response arrives.

Session audit of WRK-1017 through WRK-1034 confirms:
- WRK-1017, 1028, 1034: PASS — progressive timestamps, interactive approval evident
- WRK-1019: WARN — Stage 5 and Stage 7 share identical timestamp (2026-03-07T22:30Z); acceptable
  if reviewed in one session but indistinguishable from batch fill
- WRK-1030: WARN — Stage 7 artifact absent, plan-draft timestamp is naive 00:00Z
- WRK-1002–1015: pre-gate era, no plan-review artifacts; not violations
- No explicit retroactive self-fill detected in recent WRKs, but the pattern is undetectable
  from artifact content alone — only a skill rule prevents it

The user also identified that Stage 1 (Capture) must be a human-in-loop gate: agent presents
captured scope and waits for explicit approval before advancing to Stage 2.

## Files to Modify

| File | Change |
|------|--------|
| `.claude/skills/coordination/workspace/work-queue-workflow/SKILL.md` (v1.5.0) | Primary — add Stage 1 gate + timestamp timing rules at Stages 5, 7, 17 |
| `.claude/skills/coordination/workspace/work-queue/SKILL.md` (v1.7.0) | Mirror — same Stage 1 gate + timestamp rule additions to match |
| `.claude/work-queue/pending/WRK-1035.md` | Add Stage 1 Capture AC; update scope description |
| `.claude/work-queue/assets/WRK-1035/evidence/session-audit.md` (new) | Audit findings table from Phase 1 |

## Changes per Stage

### Stage 1 — Capture (both skills)
Add after the existing "Write `## Mission`" bullet:

```
- After writing the WRK file, present the captured scope summary to the user and
  WAIT for explicit approval before advancing to Stage 2.
  ❌ Agent writes WRK then immediately runs resource-intelligence.
  ✅ Agent writes WRK, presents one-paragraph scope summary, user confirms ("looks good",
     "proceed", or requests changes), THEN agent advances.
```

### Stages 5, 7, 17 — timestamp timing rule (both skills)
Add to each stage's exit checklist as the FIRST item:

```
  - [ ] **Timestamp rule**: `confirmed_at` / `reviewed_at` recorded AFTER user's
        in-conversation response — NOT at plan-creation time or before user replies.
        ❌ Agent pre-fills `confirmed_at: "2026-03-08T02:00:00Z"` before user has responded.
        ✅ User says "approve" at 02:30 → agent immediately writes `confirmed_at: "2026-03-08T02:30:00Z"`.
```

Also add a header note to each stage (after the existing HARD GATE notice):

```
> **ARTIFACT TIMING**: Do NOT write the evidence YAML until the user has responded
> in this conversation. The `confirmed_at` timestamp must reflect the moment of the
> user's response, captured immediately after it is received.
```

### Identical-timestamp detection note (Stage 5 + Stage 7)
Add to Stage 5 exit checklist:

```
  - [ ] If Stage 5 and Stage 7 share identical `confirmed_at`, document reason
        (e.g. "user reviewed both draft and final in same interactive session").
```

### Naive-timestamp prohibition (Stages 5, 7, 17)
Add to artifact schema note in each stage:

```
Use full ISO 8601 with seconds and timezone: `2026-03-08T03:30:00Z`.
Never use naive midnight timestamps: ❌ `2026-03-08T00:00:00Z`.
```

## Version Bumps

- `work-queue-workflow/SKILL.md`: v1.5.0 → v1.6.0
- `work-queue/SKILL.md`: v1.7.0 → v1.8.0
- Change notes reference WRK-1034 (retroactive timestamp finding) + WRK-1035 (Stage 1 gate)

## Verification

1. Read both updated SKILL files — confirm Stage 1 has explicit "wait for user" rule.
2. Confirm Stages 5, 7, 17 each have ARTIFACT TIMING notice + timestamp checklist item.
3. Confirm negative + positive examples present at each stage.
4. Confirm `session-audit.md` written with findings table.
5. Run `uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1035`
   (after evidence artifacts created).
