# Plan for #3107: fable-mode behavioral adapter (output-style)

> **Status:** blocked-draft (adversarial review MAJOR — mechanism mis-specified for v2.1.177; wrong dependency issue #; efficacy unfalsifiable. See review summary.)
> **Complexity:** T2
> **Date:** 2026-06-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3107
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-15-plan-3107-{claude,codex,gemini}.md

---

## Resource Intelligence Summary

### Existing repo code / infra
- `~/.claude/settings.json:111` + `.claude/settings.json:302` set `outputStyle: "Explanatory"` (a built-in). **No `.claude/output-styles/` dir exists** → custom output-styles are greenfield. Confirmed no existing fable/parity/behavioral adapter (find + grep, 2026-06-15).
- Output-styles are Claude Code's native response-shape mechanism (switch via `/output-style <name>`), content-only — they must NOT override gates (per `SOUL.runtime.md` "Output Style System": "never override the gates and must-fire rules").
- Behaviors to encode are already characterized + out-of-sample-validated: `analysis/2026-06-13-fable5-opus-parity-learning.md` (D1 terse, D2 autonomy, D4 loop-exit, D5 trust-tool-output) and `analysis/2026-06-15-fable5-external-corpus-validation.md` (fanout 0.703, askuser 0.031 confirmed).

### Documents / issues consulted
- #3056 corpus report (behaviors), #3109 external validation, #3112 (the invocation/verbosity signal needed to *measure* this adapter's effect — efficacy validation depends on it), #3055 (playbook — this is its executable form).

### Evidence
- `ls .claude/output-styles/` → absent; `grep outputStyle settings.json` → "Explanatory" (built-in). Confirms greenfield + the activation mechanism.
- Reproduction: N/A — additive artifact, no runtime failure to reproduce. (Step 1.5 skip is intentional.)

### Gaps
- No on-demand way to put the driver into Fable-equivalent posture; #3055's playbook is prose, not switchable.

---

## Deliverable
A custom output-style `.claude/output-styles/fable-mode.md` that, when active, shapes the driver (Opus) toward the corpus-validated Fable behaviors — terse-by-default, autonomous-decision, checkpoint-only, trust-tool-output — while explicitly deferring to all SOUL gates and must-fire rules.

## Adapter content (the artifact, for review)
```
---
name: Fable Mode
description: Terse, autonomous, defect-first operating posture (Fable-5 parity). Defers to all SOUL gates.
---
# Fable Mode — operating posture (NOT a gate override)
This style shapes RESPONSE SHAPE only. It never overrides SOUL.runtime.md hard gates,
the planning/approval flow, TDD, cross-review, or any must-fire rule. On any conflict, the gate wins.

## Output shape (D1)
- Terse by default in triage/loop/implementation work: report state + next action, no preamble/restatement.
- Switch to SYNTHESIS mode (dense, structured) only for adversarial reviews, design docs, and findings — where density earns its tokens.

## Autonomy (D2/D4)
- One-prompt-per-agent: decide marginal calls from the brief; do not pause to confirm reversible, in-scope work.
- Loop-exit: exhaust the slice, then advance — don't declare done early or ask permission mid-batch.
- Pause ONLY for: destructive/irreversible actions, real scope changes, or something only the operator can provide. (This preserves the never-self-approve gate.)

## Tool discipline (D5)
- Trust tool success + prior context; no defensive re-reads in tight TDD/edit loops.
- Bash-first discovery → targeted Read → surgical Edit.

## Stance (reviews)
- Defect-first, non-praise; hold the VERDICT/RETRIEVAL/FINDINGS/BLOCKERS shape across the whole review.
```

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Create | .claude/output-styles/fable-mode.md | the adapter |
| Update | docs/standards/ (or #3055 playbook) | cross-link doc ↔ executable artifact |
| Update | docs/plans/README.md | index row |

## TDD Test List
(Output-style is a prose artifact; "tests" are structural/contract checks.)
| Check | Verifies |
|---|---|
| test_frontmatter_valid | name + description present, parses as an output-style |
| test_gate_deference_clause_present | contains explicit "never override SOUL gates / never-self-approve" language |
| test_activatable | `/output-style fable-mode` resolves the file (manual/smoke) |

## Acceptance Criteria
- [ ] `.claude/output-styles/fable-mode.md` exists, valid frontmatter, activatable via `/output-style`.
- [ ] Contains an explicit gate-deference clause (never overrides SOUL/must-fire/approval).
- [ ] Cross-linked from the #3055 playbook.
- [ ] **Efficacy validation explicitly deferred to #3112** — once the invocation/verbosity signal lands, measure tokens/turn + clarification-break rate under fable-mode vs default against the parity baseline. (Do NOT claim measured improvement now.)

## Adversarial Review Summary
| Provider | Verdict | Findings |
|---|---|---|
| Claude (adversarial subagent) | **MAJOR** | (1) Mechanism mis-specified for installed v2.1.177: `/output-style <name>` activation changed; **`keep-coding-instructions` omitted → defaults false → activating a custom style strips the coding system prompt** the posture needs. (3) Efficacy unfalsifiable; only tautological ACs (file exists/parses). (4) **Cited #3112 as the efficacy signal — wrong issue; it's #3061** (parity verbosity metrics). Output-style-vs-Skill choice never justified (a Skill avoids the system-prompt/keep-coding landmine). |

**Overall result:** FAIL — re-draft. Corrected before any re-attempt: pin to v2.1.177 mechanics; set `keep-coding-instructions: true` (or use a Skill instead); fix dependency #3112→**#3061**; weigh Skill vs output-style on evidence. NOTE: reviewer also claimed a built-in `Proactive` style already ships the autonomy half — **unconfirmed locally** (only `explanatory`+`learning` plugins installed); verify before relying on it.

## Risks and Open Questions
- **Risk — efficacy unmeasurable today.** Like every lever this session, we can't prove the adapter changes behavior until #3112's signal exists. Mitigation: ship it as a codified posture (low-risk, reversible) with validation explicitly deferred; do not overclaim.
- **Risk — gate override.** An autonomy-encouraging style could erode the never-self-approve / planning gates. Mitigation: explicit deference clause + a structural test for it; SOUL gates always win.
- **Risk — Claude-only.** Output-styles are Claude Code-specific; Codex/Gemini/Hermes don't consume them. Open: port the posture into their SOUL deltas later, or keep Claude-only for v1? **User decision.**
- **Open — terse vs Explanatory default.** This session runs Explanatory (verbose by design). fable-mode is the opposite; it's opt-in per task, not a global default. Confirm it shouldn't replace the default.

## Complexity: T2
Single additive artifact + a cross-link + structural tests; low-risk, reversible. Not T3 (no systemic/enforcement change).
