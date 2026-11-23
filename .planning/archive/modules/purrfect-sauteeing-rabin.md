# Plan: WRK-1014 — Add Stage 4a Plan Mode Ideation to WRK Lifecycle

## Context

Stage 4 currently jumps straight to writing `specs/wrk/WRK-NNN/plan.md` and generating HTML.
Iterating on a wrong approach requires regenerating artifacts repeatedly (wasted disk/context).
Inserting a `EnterPlanMode` / `ExitPlanMode` sub-stage forces the orchestrator to think through
the full scope as text before touching any files — higher quality first drafts, less rework.

Pattern surfaced during WRK-1005: user asked whether EnterPlanMode should gate plan draft.
This WRK implements that answer as a documented lifecycle sub-stage.

---

## Files to Modify

### 1. `.claude/skills/coordination/workspace/work-queue/SKILL.md`

**Canonical 20-Stage Lifecycle list** (lines ~66-74): add `4a` entry:

```
4  Plan Draft (4a: Ideation via EnterPlanMode → 4b: Artifact write)
```

**Stage Contracts table** (lines ~81-102): split Stage 4 row:

| 4a | `EnterPlanMode` → text-only plan draft → `ExitPlanMode` | — |
| 4b | Draft plan spec + HTML artifact | — |

**Stage 5 exit note** (line ~104): no change needed — references to "Stage 4" still valid.

**Tools list in frontmatter** (line 18): add `EnterPlanMode`, `ExitPlanMode` to tools array.

---

### 2. `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`

**Start-to-Finish Chain step 3** (lines ~54-63):

Change step 3 from:
> `3. Ensure plan exists and user approval explicitly names WRK ID.`

To:
> `3. Stage 4a: Enter EnterPlanMode — draft full plan as text, iterate with user, then ExitPlanMode. Stage 4b: write plan spec + generate HTML. Ensure user approval explicitly names WRK ID.`

---

### 3. `.claude/work-queue/process.md`

**Mermaid flowchart** (lines ~24-60): replace `D[Plan Draft]` with two nodes:

```mermaid
D[4a: Plan Mode Ideation] --> D2[4b: Plan Artifact Write]
D2 --> E{...}
```

**Stage 4 contract text** (lines ~85-107): add paragraph:

> **4a — Plan Mode Ideation**: Before writing any artifacts, invoke `EnterPlanMode`. Draft
> the full plan scope as text-only; iterate with the user if needed. Exit with `ExitPlanMode`
> once the text plan is approved. This is a non-blocking sub-stage — no exit artifact required.
>
> **4b — Plan Artifact Creation**: Write plan spec and generate HTML review artifact (existing
> Stage 4 behavior). Proceed to Stage 5 as before.

---

## Verification

This is doc-only. Tests:

1. Read each modified file and confirm 4a/4b split present.
2. Run `uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1014` after
   execution evidence is written — gate verifier must pass.
3. Check SKILL.md stays ≤250 lines (currently 238; net change ~+5 lines → 243).
4. Check process.md mermaid compiles (no syntax error in flowchart node labels).

---

## Non-Goals

- No changes to stage numbers (stages remain 1-20).
- No changes to stage-NN-*.yaml contract files (they describe the outer Stage 4 gate only).
- No code changes — doc/YAML modifications only.
