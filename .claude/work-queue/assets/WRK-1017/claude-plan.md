# WRK-1017 Claude Plan

Starting from `common-plan-draft.md`. Headings preserved. Extended with Claude's
independent analysis, wording recommendations, and implementation decisions.

## Summary

- WRK: `WRK-1017`
- Problem: agents skip Stage 5 interactive plan review and move ahead without the
  required agent-user planning session.
- Goal: make Stage 5 harder to skip and easier to verify across the workflow contract.
- Route: `B`
- Canonical execution plan location: inline `## Plan` in `WRK-1017.md`

## Problem Frame

- Stage 5 is defined as an interactive agent-user planning session, not a
  one-way HTML drop.
- Current failure mode: agents move from Stage 4 plan creation to Stage 6
  cross-review or Stage 7 without completing the planning dialog, decision
  capture, and evidence logging.
- Root cause (Claude analysis): the original Stage 5 text used advisory language
  ("walk the draft plan section-by-section") with no structural stop signal.
  Agents have a forward-momentum bias — they treat sequential skill steps as a
  checklist and complete each step as fast as possible. Advisory language is
  read as a soft suggestion, not a block.
- Fix principle: the blocking nature of Stage 5 must be expressed as an
  unmistakable imperative at the top of the stage section in every workflow
  contract file, not buried in prose.

## In-Scope Files

- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`

## Required Stage 5 Substeps

1. Create one common draft to seed all planning passes.
2. Run an independent planning pass with `claude`.
3. Document and prepare to exit with mandatory session-log/evidence update.
4. Run an independent planning pass with `codex`.
5. Document and prepare to exit with mandatory session-log/evidence update.
6. Run an independent planning pass with `gemini`.
7. Document and prepare to exit with mandatory session-log/evidence update.
8. Combine the individual plans into one synthesized plan.
9. Rate each model plan during the combine step.
10. Seek user review and approval on the combined plan.

## Required Artifacts

- `.claude/work-queue/assets/WRK-1017/common-plan-draft.md`
- `.claude/work-queue/assets/WRK-1017/claude-plan.md`
- `.claude/work-queue/assets/WRK-1017/codex-plan.md`
- `.claude/work-queue/assets/WRK-1017/gemini-plan.md`
- `.claude/work-queue/assets/WRK-1017/combined-plan.md`
- `.claude/work-queue/assets/WRK-1017/evidence/user-review-plan-draft.yaml`

## Required Contract Changes

- Make Stage 5 visibly blocking in the workflow contract text.
- Express Stage 5 as ordered planning-and-synthesis substeps.
- Require saved artifacts for each model-specific planning pass.
- Require a mandatory session-log/evidence update after each model pass.
- Preserve browser-open and origin-publish requirements.
- Preserve the `user-review-plan-draft.yaml` evidence requirement.
- Preserve explicit user response as a prerequisite for Stage 6.

### Claude-specific wording recommendations

**Hard gate block (identical across all three files, placed at the top of Stage 5):**

```
> **HARD GATE — BLOCKING**: You MUST NOT advance to Stage 6 until the user has
> responded explicitly in this session. Presenting the HTML and waiting is not
> sufficient. Stage 5 is an interactive dialog. Momentum past this point is a
> workflow violation.
```

Rationale: imperative "MUST NOT" signals a prohibition, not a suggestion. The
word "Momentum" directly names the failure mode so agents self-identify it.

**Substep anchor (work-queue-workflow is primary; the other two files reference it):**

- `work-queue-workflow/SKILL.md`: expand Stage 5 in full with the 10-substep
  ordered list, artifact table, exit checklist, and hard gate block.
- `workflow-gatepass/SKILL.md`: Stage 5 row in the stage table should read
  `see work-queue-workflow Stage 5` and the stage prose should include the hard
  gate block plus a forward-reference. Do not duplicate the full substep list —
  keep a summary with a canonical reference.
- `work-queue/SKILL.md`: Stage Contract Stage 5 keeps the hard gate block and
  exit checklist already added in v1.6.3. Add a one-line reference to the
  substep list: `See work-queue-workflow/SKILL.md for the 10-substep interactive
  planning protocol.`

Rationale: duplication risks drift. The full substep list lives once
(work-queue-workflow). The other two files gate-signal and cross-reference.

**Exit checklist wording (identical in all three files):**

```
Stage 5 exit checklist — ALL required before Stage 6:
- [ ] common-plan-draft.md seeded and saved
- [ ] claude-plan.md saved with handoff note + evidence update
- [ ] codex-plan.md saved with handoff note + evidence update
- [ ] gemini-plan.md saved with handoff note + evidence update
- [ ] combined-plan.md produced and quality-rated
- [ ] plan-draft HTML opened in browser (xdg-open)
- [ ] HTML pushed to origin and publish evidence logged
- [ ] Interactive walk-through completed with user on combined plan
- [ ] User has responded explicitly (scope, criteria, risk decisions recorded)
- [ ] user-review-plan-draft.yaml written with decision log
- [ ] Plan artifacts updated from user decisions
```

## HTML and Review Requirements

- The plan-review HTML must include `Plan Quality Eval Comparison`.
- The compare section must show:
  - `claude`, `codex`, and `gemini` plan ratings
  - the combine-step decision
  - why key elements were kept or rejected
- The user review must include the HTML `Gate-Pass Stage Status` section.

## Verification Targets

- Verify all three workflow contract files reflect the same Stage 5 ordering.
- Verify each model pass requires a saved handoff note plus session-log/evidence
  update.
- Verify the plan-review HTML renders `Plan Quality Eval Comparison`.
- Verify the gate text still blocks Stage 6 until user review is completed.
- Verify no Stage 5 checklist requirement is removed while adding the new
  substeps.

### Claude-specific verification commands (no new tooling)

```bash
# 1. Hard gate notice present in all three files
grep -n "HARD GATE" \
  .claude/skills/workspace-hub/work-queue-workflow/SKILL.md \
  .claude/skills/workspace-hub/workflow-gatepass/SKILL.md \
  .claude/skills/coordination/workspace/work-queue/SKILL.md

# 2. user-review-plan-draft.yaml requirement present in all three
grep -n "user-review-plan-draft.yaml" \
  .claude/skills/workspace-hub/work-queue-workflow/SKILL.md \
  .claude/skills/workspace-hub/workflow-gatepass/SKILL.md \
  .claude/skills/coordination/workspace/work-queue/SKILL.md

# 3. Substep list present in work-queue-workflow
grep -n "substep\|common-plan-draft\|claude-plan\|codex-plan\|gemini-plan\|combined-plan" \
  .claude/skills/workspace-hub/work-queue-workflow/SKILL.md

# 4. Exit checklist items count (expect >= 11 lines per file)
grep -c "\- \[ \]" .claude/skills/workspace-hub/work-queue-workflow/SKILL.md

# 5. Artifact files present after execution
ls -1 .claude/work-queue/assets/WRK-1017/*.md | sort
```

## Quality Evaluation Rubric

- Overall rating scale: `strong | adequate | weak`
- Required dimensions:
  - completeness
  - test-eval quality
  - execution clarity
  - risk coverage
  - standards/gate alignment

## Risks and Failure Modes

- Contract drift across the three workflow files.
- Weak wording that still allows agents to interpret Stage 5 as optional.
- A model-specific plan that changes structure and makes synthesis harder.
- Loss of existing gate requirements while adding new substeps.
- Treating saved model plans as the canonical execution plan instead of evidence
  inputs.

### Claude-specific risk mitigations

- **Drift risk**: Put the full substep list in work-queue-workflow only; the
  other two files cross-reference. Reduces drift surface from 3 copies to 1.
- **Weak wording risk**: Use "MUST NOT" and "workflow violation" explicitly.
  Avoid softer phrasing like "should not" or "avoid".
- **Structure deviation risk**: The model-plan rule (preserve common-draft
  headings) is repeated in the common-plan-draft itself and in the substep
  instructions in work-queue-workflow. Agents that read the common draft before
  producing their plan get the structural constraint early.
- **Gate requirement loss**: Before editing, grep for the existing Stage 5
  checklist items in work-queue/SKILL.md. Keep a pre-edit checklist count and
  verify post-edit count is equal or higher.
- **Authority confusion risk**: State explicitly in work-queue-workflow Stage 5
  that model-plan files are evidence inputs, not the execution plan.

## Decisions Already Fixed

- Update all three workflow contract files in the same WRK.
- Keep Route B inline `## Plan` authoritative.
- Use `strong | adequate | weak` for overall plan quality.
- Require mandatory session-log/evidence updates after each model pass.
- Use `claude`, then `codex`, then `gemini` ordering.

## Combine-Step Expectations

- Produce one synthesized plan in `combined-plan.md`.
- Rate each model-specific plan using the common rubric.
- Record why each retained, merged, or rejected element was chosen.
- Normalize the approved combined plan back into `WRK-1017.md` inline `## Plan`.

### Claude combine-step additions

During the combine step, document the following per model plan:

| Dimension | Claude | Codex | Gemini |
|-----------|--------|-------|--------|
| Completeness | | | |
| Test-eval quality | | | |
| Execution clarity | | | |
| Risk coverage | | | |
| Standards/gate alignment | | | |
| **Overall** | | | |

Key decisions to record:
- Which wording from which model plan was adopted for the hard gate block?
- Which verification commands survived into the combined plan?
- Were any substeps reordered or renamed across the three model plans?
- Were any exit-checklist items added or removed relative to common draft?

## Open Questions For Model Planning

- What exact wording best prevents agents from skipping Stage 5?
  (Claude answer: "MUST NOT advance … Momentum past this point is a workflow
  violation." See wording in Required Contract Changes above.)
- Where should the substep list live in each of the three workflow contracts?
  (Claude answer: full list in work-queue-workflow; summary + cross-reference in
  the other two.)
- What is the minimal additional wording needed to avoid redundant or conflicting
  gate language?
  (Claude answer: duplicate only the hard gate block and exit checklist; keep the
  substep list in one canonical location.)
- What verification commands best prove the new requirements without adding new
  tooling?
  (Claude answer: grep-based spot checks; see Verification Targets above.)

## Handoff Note

Claude planning pass complete. Key additions over the common draft:

1. Root cause diagnosed: advisory language + forward-momentum bias.
2. Exact hard gate wording recommended: imperative "MUST NOT" + "workflow
   violation".
3. Authority placement resolved: full substep list in work-queue-workflow;
   cross-reference only in the other two files.
4. Exit checklist expanded to 11 items (includes per-model artifact saves).
5. Verification commands specified using grep only (no new tooling).
6. Combine-step table template added for structured quality rating.

Session-log/evidence update: this file saved at
`.claude/work-queue/assets/WRK-1017/claude-plan.md`. Stage 5 substep 3
(document and prepare to exit) is complete for the Claude pass. Proceed to
substep 4 (codex planning pass).
