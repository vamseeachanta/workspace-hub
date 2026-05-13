# Plan for #2695: /goal use-case catalog for repo ecosystem (claude+codex+hermes)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2695
> **Review artifacts:** scripts/review/results/2026-05-13-plan-2695-claude.md (T1 single-author r3 fits — doc-only change, no provider integration risk per `feedback_always_adversarial_review_scale_depth`)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the `/goal` use-case catalog (issue #2695, design doc commit `752222f11`) into the Claude runtime via a thin rule, fix the stale `.claude/rules/README.md` index, audit Codex/Hermes dispatch templates for catalog-issue injection points, and post the bootstrap weekly picklist comment using the v2 three-role template.

**Architecture:** Doc-only governance addition. One new rule file modeled on `.claude/rules/calc-citation-contract.md` (19 lines, prose + numbered steps + escape valves). One README index repair. One audit task (read-only) for dispatch templates. Two GitHub comments (bootstrap weekly + close-out). No code changes, no test infrastructure, no runtime behavior change beyond rule-discovery by Claude on next session.

**Tech Stack:** Markdown rule files, `gh` CLI for issue comments, standard `git` for commits.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/rules/calc-citation-contract.md` (19 lines) — the canonical pattern for a rule file (frontmatter-style `**When ...**` + `**Why:**` + `**How to apply:**` numbered list + `**Do NOT apply when:**` escape valves). New rule will mirror this shape.
- Found: `.claude/rules/coding-style.md`, `.claude/rules/patterns.md` — other auto-loaded rules; their content does not need to change.
- Found: `.claude/rules/README.md` (2 lines) — index is stale; lists only `coding-style.md, patterns.md` despite `calc-citation-contract.md` existing. Plan repairs this.
- Found: `scripts/ai/task-dispatcher.py`, `scripts/operations/workstation-dispatch.sh`, `scripts/coordination/routing/lib/agent_dispatcher.sh` — dispatch scripts that may or may not need catalog-issue-# awareness. Plan adds an audit task to determine scope before editing.
- Found: `docs/governance/2026-05-13-goal-use-case-catalog-design.md` (commit `752222f11`) — design doc with D1-D7 decisions consumed by this plan.

### Standards
Not applicable — governance/harness change, no engineering standards involved.

### LLM Wiki pages consulted
No relevant wiki pages — this is a harness governance plan.

### Documents consulted
- `docs/plans/_template-issue-plan.md` — Resource Intel evidence-contract format, Artifact Map shape.
- `docs/plans/README.md` — workspace-hub planning workflow (Resource Intel → Reproduce → Plan → Adversarial Review → status:plan-approved → Implement).
- `.claude/rules/calc-citation-contract.md` — canonical rule-file format being mirrored.
- [Hermes Agent provider docs](https://hermes-agent.nousresearch.com/docs/integrations/providers) — three-quota-pool model encoded in D7.
- [Anthropic: Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents) — brain/hands architectural pattern.
- Memory: `feedback_never_offer_to_self_label_plan_approved`, `feedback_multi_agent_commit_serialization`, `feedback_always_adversarial_review_scale_depth`, `feedback_gh_issue_comment`, `feedback_inline_gh_issue_url`.

### Gaps identified
- No existing rule file enforces `/goal` invocation discipline — proposed: `.claude/rules/goal-invocation.md`.
- `.claude/rules/README.md` does not list `calc-citation-contract.md` — index has drifted; plan repairs.
- No bootstrap weekly picklist comment exists on #2695 — plan creates the first one.
- Dispatch-template catalog-# awareness: unknown until audit task runs (Task 3).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-13T18:40Z via `gh issue view`):
- `#2695` — OPEN — feat(harness): /goal use-case catalog for repo ecosystem (claude+codex+hermes)
- `#2696` — OPEN — chore(infra): upgrade Hermes Agent v0.4.0 -> v0.13.0 and audit routing-layer assumptions
- `#2675` — OPEN — feat(ai-orchestration): reverse-prompt repo ecosystem for productive multi-provider work (related, not blocking)

**File existence** (`ls` 2026-05-13T19:00Z):
- EXISTS: `.claude/rules/README.md` (2 lines, stale)
- EXISTS: `.claude/rules/calc-citation-contract.md` (19 lines, canonical pattern)
- EXISTS: `.claude/rules/coding-style.md`, `.claude/rules/patterns.md`
- EXISTS: `docs/governance/2026-05-13-goal-use-case-catalog-design.md` (commit `752222f11`)
- MISSING (this plan creates): `.claude/rules/goal-invocation.md`

**Line excerpts** — current `.claude/rules/README.md`:
```
# Rules
Universal constraints only. Stage-specific rules live in micro-skills (`.claude/skills/workspace-hub/stages/`). Files: coding-style.md, patterns.md
```
(Note: missing `calc-citation-contract.md` from the index — Task 2 fixes.)

**Gap proofs** (`ls .claude/rules/goal-invocation.md 2>&1`):
- "No such file or directory" → confirms the rule file does not yet exist.

**Reproduction proofs:** N/A — governance/doc-only issue. Skip-allowed per template; no runtime failure being repaired.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-13-issue-2695-goal-use-case-catalog-plan.md` |
| Catalog issue | https://github.com/vamseeachanta/workspace-hub/issues/2695 |
| Design doc | `docs/governance/2026-05-13-goal-use-case-catalog-design.md` (commit `752222f11`) |
| Rule (new) | `.claude/rules/goal-invocation.md` |
| Rule index | `.claude/rules/README.md` |
| Plan review — Claude | `scripts/review/results/2026-05-13-plan-2695-claude.md` (single-author r3) |
| Hermes upgrade follow-up | https://github.com/vamseeachanta/workspace-hub/issues/2696 |

---

## Tasks

### Task 1: Create `.claude/rules/goal-invocation.md`

**Files:**
- Create: `.claude/rules/goal-invocation.md`
- Reference: `.claude/rules/calc-citation-contract.md` (pattern model)

- [ ] **Step 1: Verify gap (file does not yet exist)**

Run:
```bash
ls .claude/rules/goal-invocation.md 2>&1
```
Expected output: `ls: cannot access '.claude/rules/goal-invocation.md': No such file or directory`

- [ ] **Step 2: Write the rule file**

Create `.claude/rules/goal-invocation.md` with exact contents:

```markdown
# /goal invocation contract — agent rule

**When a session is about to invoke `/goal` (or the `planning-goal` / `planning-code-goal` skill), first fetch the canonical /goal use-case catalog at [issue #2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) and the latest weekly picklist comment.**

**Why:** `/goal` is the highest-leverage multi-day planning command we have. Without consulting the catalog + weekly comment, invocations drift toward whatever the current chat suggests, which (a) ignores the weekly token-budget allocation, (b) risks duplicating in-flight `/goal` work in another session, and (c) loses the catalog's "anti-pattern" warnings against shapes that have failed before.

**How to apply:**

1. **Before** running `/goal`, `Skill planning-goal`, or `Skill planning-code-goal`:
   - `gh issue view 2695 --repo vamseeachanta/workspace-hub --json body`
   - `gh issue view 2695 --repo vamseeachanta/workspace-hub --comments | tail -200`

2. **Validate** against the catalog:
   - Match to entries 1-23 (generic) or 24-30 (ecosystem-tuned)
   - If no match: name the gap to the user; do NOT silently invoke
   - If match exists but entry is on this week's SKIPPED list: surface and ask whether to override or defer

3. **Check the gate**: `/goal` invocation requires `status:plan-approved` per `feedback_never_offer_to_self_label_plan_approved`. Verify the label is set BEFORE invoking. Never self-approve.

4. **Check runner allocation**: if the weekly picklist names a specific runner (claude / codex / hermes / gemini) and the current session is a *different* runner, surface the mismatch before proceeding (`feedback_multi_agent_commit_serialization`).

4.5. **Brain/hands delegation check** (added per design doc D7): if the catalog entry is `[execution-heavy]` or `[bidirectional]` AND the proposed work has reached planning-complete state (plan exists, `status:plan-approved` is set), surface the option of delegating execution to Hermes (which routes to Claude Code or Codex per cost/quota) instead of running Claude main session end-to-end. The three quota pools (Anthropic Max base, Anthropic Max overage, OpenAI) are consumed *additively*; brain-only invocation wastes layers 3a/3b.

5. **After** invocation completes, post a comment on the catalog issue noting which entry was used and any catalog-vs-reality divergence — feeds the next refresh.

**Do NOT apply when:** the user explicitly overrides ("ignore the catalog this time, just plan X"), OR the catalog issue is unreachable (offline / gh CLI broken). In the unreachable case, surface the gap and proceed with standard `planning-goal` skill flow, noting in the resulting plan that catalog validation was skipped.

**Cross-runtime note:** This rule binds Claude only (it lives in `.claude/rules/`). Codex and Hermes dispatch prompts must include the catalog issue number explicitly — they read the issue body directly via `gh issue view`.

**Pilot reference:** [issue #2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) (the catalog) — bootstrap state as of 2026-05-13: 23 generic + 7 ecosystem-tuned entries, brain/hands tagged; refresh cadence weekly; weekly picklist posted as fresh comments.

**Related:**
- Design doc: `docs/governance/2026-05-13-goal-use-case-catalog-design.md` (D1-D7)
- Hermes upgrade audit: [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696) — verifies routing-layer assumptions for Step 4.5
- Cross-review depth rule: `feedback_always_adversarial_review_scale_depth`
```

- [ ] **Step 3: Verify the file landed with expected size and content**

Run:
```bash
wc -l .claude/rules/goal-invocation.md
grep -c "Step 4.5" .claude/rules/goal-invocation.md
grep -c "2695" .claude/rules/goal-invocation.md
```
Expected: ~30 lines (header + body + escape valves), grep counts ≥1 for "Step 4.5", ≥3 for "2695" (header + step 1 + pilot reference).

- [ ] **Step 4: Commit**

```bash
git add .claude/rules/goal-invocation.md
git commit -m "feat(rules): add /goal invocation contract per #2695

Thin rule (~30 lines) modeled on calc-citation-contract.md. Tells
Claude to fetch issue #2695 body + latest weekly comment before
invoking /goal. Includes Step 4.5 (brain/hands delegation surfacing
per design doc D7) and explicit user-override + unreachable escape
valves.

Refs: #2695"
```

---

### Task 2: Repair `.claude/rules/README.md` (currently stale; missing `calc-citation-contract.md`)

**Files:**
- Modify: `.claude/rules/README.md`

- [ ] **Step 1: Read current content**

Run:
```bash
cat .claude/rules/README.md
```
Expected output (the stale state):
```
# Rules
Universal constraints only. Stage-specific rules live in micro-skills (`.claude/skills/workspace-hub/stages/`). Files: coding-style.md, patterns.md
```

- [ ] **Step 2: Write the corrected README**

Overwrite `.claude/rules/README.md` with:
```markdown
# Rules
Universal constraints only. Stage-specific rules live in micro-skills (`.claude/skills/workspace-hub/stages/`).

Files:
- `coding-style.md` — edit safety, path handling, harness file size
- `patterns.md` — enforcement gradient (prose → script → hook)
- `calc-citation-contract.md` — citation emission for standards-derived constants (per [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481), [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685))
- `goal-invocation.md` — `/goal` invocation contract; consult [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) catalog before invoking
```

- [ ] **Step 3: Verify all four rules appear in README and harness-file-size limit is respected**

Run:
```bash
wc -l .claude/rules/README.md
grep -c "^-" .claude/rules/README.md
```
Expected: ≤20 lines (CLAUDE.md/README harness-file-size rule per `.claude/rules/coding-style.md`), 4 bullet lines (one per rule file).

- [ ] **Step 4: Commit**

```bash
git add .claude/rules/README.md
git commit -m "fix(rules): repair stale README index; add goal-invocation entry

Index was missing calc-citation-contract.md (which has existed since
the citation pilot work). Also adds goal-invocation.md from #2695.

Refs: #2695"
```

---

### Task 3: Audit dispatch templates for catalog-issue-# injection points

**Files:**
- Read-only: `scripts/ai/task-dispatcher.py`, `scripts/operations/workstation-dispatch.sh`, `scripts/coordination/routing/lib/agent_dispatcher.sh`

- [ ] **Step 1: Inspect each dispatch script for a "prompt template" string that mentions issue numbers**

Run:
```bash
for f in scripts/ai/task-dispatcher.py scripts/operations/workstation-dispatch.sh scripts/coordination/routing/lib/agent_dispatcher.sh; do
  echo "=== $f ==="
  grep -nE "(prompt|template|issue|/goal|catalog)" "$f" 2>/dev/null | head -20
done
```
Expected: either (a) the scripts contain user-facing prompt templates where adding `#2695` is straightforward, or (b) they are pure routing/exec logic with no prompt-template surface.

- [ ] **Step 2: Decision branch — record findings inline in this plan**

Edit this plan file under Task 3 Step 2 (this very step) to record the audit verdict in one of these forms:

- **Verdict A (prompt-template surface found):** list the exact line(s) in each script that should have `Consult catalog at #2695 before /goal invocation.` injected. Proceed to Step 3.
- **Verdict B (no prompt-template surface — pure routing):** record "no injection points; Codex/Hermes get the catalog # in dispatch prompts at session start (which is already a human-controlled surface, not a script template)." Proceed to Step 4 (skip Step 3).
- **Verdict C (mixed):** record which scripts fall in A and which in B; plan accordingly.

- [ ] **Step 3 (conditional — only if Verdict A or C):** Add a one-line `Consult #2695 catalog before invoking /goal.` to each identified prompt-template line. Show the exact `Edit` patch for each file. Run a grep to verify the line landed. Commit:

```bash
git add <files-touched>
git commit -m "feat(dispatch): inject /goal catalog #2695 reference into prompt templates

Refs: #2695"
```

- [ ] **Step 4 (Verdict B path or after Step 3): Document the audit outcome on #2695**

```bash
gh issue comment 2695 --repo vamseeachanta/workspace-hub --body "## Step G audit — dispatch template inspection

Audited \`scripts/ai/task-dispatcher.py\`, \`scripts/operations/workstation-dispatch.sh\`, and \`scripts/coordination/routing/lib/agent_dispatcher.sh\` for prompt-template injection points.

**Verdict:** [A | B | C — fill in based on Step 2 finding]

[If A or C: list the lines edited]
[If B: confirm Codex/Hermes get the catalog # at session-start prompt level, not script-template level]
"
```

---

### Task 4: Post bootstrap weekly comment on #2695 using v2 three-role template

**Files:**
- GitHub issue comment on https://github.com/vamseeachanta/workspace-hub/issues/2695 (no local files)

- [ ] **Step 1: Inventory current week's open `status:plan-approved` issues**

Run:
```bash
gh issue list --repo vamseeachanta/workspace-hub --label "status:plan-approved" --state open --limit 30 --json number,title,labels --jq '.[] | {number, title}'
```
Expected: 0-5 issues. The picklist hard-caps at 5 anyway.

- [ ] **Step 2: For each candidate, map to a Tier 1 or Tier 2 catalog entry**

Inspect each result's title and labels. Use the design doc D7 tags (`[planning-heavy]` / `[execution-heavy]` / `[bidirectional]`) to set the role allocation. If zero `status:plan-approved` issues exist, the bootstrap comment will note "no candidates this week — system ready for next week's reset."

- [ ] **Step 3: Post the bootstrap comment**

Construct the comment using this exact template (fill in week DOW based on `date -u +%A` and `+%Y-%m-%d`):

```bash
gh issue comment 2695 --repo vamseeachanta/workspace-hub --body "$(cat <<'EOF'
### Week of 2026-05-13 — /goal picklist (BOOTSTRAP)

Quota windows open this week:
- anthropic max base:   <fill: FRESH | LOW | EXHAUSTED>   (resets <DOW>)
- anthropic max overage: <fill>                            (resets <DOW>)
- openai (codex):       <fill>                             (resets <DOW>)
- gemini free tier:     <fill>                             (resets <DOW>)

Open-issue surface: <N> issues at status:plan-approved | <M> at status:plan-review

PICKLIST (3-5 items max; tag distribution should match open quota windows)

[Fill in 0-5 candidates as: ]
1. [#NNNN](url) — <issue title>
   catalog: #<1-30> (<short pattern name>) [planning-heavy|execution-heavy|bidirectional]
   planning brain:  claude main session
   routing/hands:   <hermes → claude-code | hermes → codex | claude main direct>
   review:          codex T1
   why this week:   <one line>
   gate: status:plan-approved required before /goal can run

SKIPPED (catalog entries deliberately not picked this week)
- [fill or "none — this is the bootstrap week"]

NOTES
- This is the bootstrap comment. Next regular cadence: Monday 2026-05-18.
- Tag-distribution check baseline: <count> planning-heavy / <count> execution-heavy / <count> bidirectional in picklist.
- D7 brain/hands model in effect; routing assumes Hermes v0.13.0 (audit pending in #2696).
EOF
)"
```

- [ ] **Step 4: Verify comment landed**

Run:
```bash
gh issue view 2695 --repo vamseeachanta/workspace-hub --comments --json comments --jq '.comments | last | {createdAt, body: (.body | split("\n")[0:3])}'
```
Expected: shows the just-posted comment's first 3 lines.

---

### Task 5: Tick acceptance criteria on #2695 and post close-out comment

**Files:**
- Edit issue body checkboxes on https://github.com/vamseeachanta/workspace-hub/issues/2695

- [ ] **Step 1: Pull current body, flip the implementation checkboxes from `[ ]` to `[x]`**

Run:
```bash
gh issue view 2695 --repo vamseeachanta/workspace-hub --json body --jq '.body' > /tmp/2695-final-body.md
```

Then edit `/tmp/2695-final-body.md` to flip these specific checkboxes to `[x]`:
- `[ ] .claude/rules/goal-invocation.md references this issue # AND includes Step 4.5` → `[x]`
- `[ ] .claude/rules/README.md lists the new rule` → `[x]`
- `[ ] Bootstrap weekly comment posted` → `[x]`
- `[ ] Design doc updated with D7` → `[x]` (already done in commit `752222f11`)
- `[ ] Formal plan filed at docs/plans/...` → `[x]` (this plan, once committed)
- `[ ] Plan adversarial review completed at T1 minimum` → `[x]` (filled in by reviewer)
- `[ ] status:plan-approved set by user` → `[x]` (filled in by user-approval event)
- `[ ] Follow-up issue filed for Hermes v0.4.0 → v0.13.0 upgrade` → `[x]` (#2696)

Then push:
```bash
gh issue edit 2695 --repo vamseeachanta/workspace-hub --body-file /tmp/2695-final-body.md
```

- [ ] **Step 2: Post close-out comment**

```bash
gh issue comment 2695 --repo vamseeachanta/workspace-hub --body "$(cat <<'EOF'
## Close-out: catalog wired, bootstrap posted

**Implementation complete per Step G of design doc.** Summary:

- \`.claude/rules/goal-invocation.md\` added (commit: <CLAUDE: fill in SHA from Task 1 Step 4>)
- \`.claude/rules/README.md\` repaired + new rule listed (commit: <SHA from Task 2 Step 4>)
- Dispatch-template audit: <Verdict A/B/C from Task 3>
- Bootstrap weekly comment posted (Task 4 — first picklist)
- Issue body checkboxes flipped for completed criteria
- Hermes upgrade audit tracked at #2696

**Next regular cadence:** Monday 2026-05-18 — weekly picklist comment will be posted with current quota windows + candidates.

**Open follow-ups:**
- #2696 — Hermes v0.4.0 → v0.13.0 upgrade audit (verifies D7 routing assumptions)
- v2 cron-driven weekly picklist (deferred until 4-6 weeks of manual cadence prove the format)

Closing this issue is **not** appropriate — it is the durable artifact. Stays OPEN as the catalog's home.
EOF
)"
```

- [ ] **Step 3: Verify final state**

Run:
```bash
gh issue view 2695 --repo vamseeachanta/workspace-hub --json state,labels,body --jq '. | {state, labels: [.labels[].name], checkbox_ticked: (.body | [scan("- \\[x\\]")] | length), checkbox_unticked: (.body | [scan("- \\[ \\]")] | length)}'
```
Expected: state=OPEN, labels includes `status:plan-approved` (once user has set it; expected to already be in place by close-out time), checkbox_ticked ≥ 8 (the criteria flipped in Step 1), checkbox_unticked = 0 or matches deliberately-deferred items.

- [ ] **Step 4: Mark this plan complete**

Add a `STATUS: COMPLETE — 2026-05-13` line at the top of this file under the `**Status:**` header. Commit:

```bash
git add docs/plans/2026-05-13-issue-2695-goal-use-case-catalog-plan.md
git commit -m "chore(plans): mark #2695 catalog plan complete

All Step G implementation tasks landed; bootstrap weekly comment
posted; acceptance criteria flipped on #2695.

Refs: #2695"
```

---

## Out of scope (handled elsewhere or deferred)

- **Hermes v0.4.0 → v0.13.0 upgrade**: tracked at [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696). Implementation here does NOT depend on the upgrade landing; the rule degrades gracefully if Hermes routing is unavailable (Codex/Hermes still get the catalog # at dispatch-prompt level per Task 3).
- **Cron-driven auto-population of the weekly picklist**: deferred to v2 once 4-6 weeks of manual cadence prove the format (per design doc non-goal).
- **Cost/quota numeric model**: deferred. The picklist surfaces quota-window status as `FRESH | LOW | EXHAUSTED` (qualitative); precise token-accounting is a separate follow-up.
- **Replacing #2675's provider role matrix**: that issue handles "WHICH agent does WHAT work"; this plan handles "WHICH work patterns fit `/goal`." Cross-link both once #2675 ships.

---

## Risks & mitigations (delta beyond design-doc risks)

| Risk | Mitigation |
|---|---|
| Task 3 audit finds prompt-template surfaces we don't know how to edit safely | Verdict C path documents partial completion; remaining surface logged as a follow-up issue rather than blocking |
| Bootstrap weekly comment lands with `<N>` placeholders if Task 4 Step 2 inventory fails | Task 4 Step 1 must succeed before Step 3 fires; if `gh issue list` errors, halt and surface to user |
| `gh issue edit --body-file` truncates issue body if encoding is wrong | Task 5 Step 1 uses temp-file roundtrip + Step 3 verifies checkbox counts match expected |
| `.claude/rules/README.md` >20 lines (harness-file-size rule violation) | Task 2 Step 3 explicitly checks `wc -l` ≤ 20 |
| Plan-approval gate not yet set when Task 1 runs | Pre-commit `require-plan-approval.sh` will block. Verify `status:plan-approved` label + `.planning/plan-approved/2695.md` marker BEFORE starting Task 1. |

---

## Adversarial review — T1 single-author r3 (per `feedback_always_adversarial_review_scale_depth`)

T1 is sufficient because:
- Doc-only change; no provider-integration risk
- No new dependencies, no code path changes
- Rule file mirrors a known-good pattern (`calc-citation-contract.md`)
- The 5 main brainstorming sections were already reviewed iteratively by the user during the brainstorming flow

T1 protocol: single Claude reviewer, 3 rounds of self-critique covering (a) plan-vs-design-doc consistency, (b) placeholder/ambiguity scan, (c) acceptance-criteria coverage. Review artifact at `scripts/review/results/2026-05-13-plan-2695-claude.md` once reviewer runs.

---

## Self-review checklist (per writing-plans skill)

- [x] **Spec coverage**: every Step G item in design doc has a task — rule file (Task 1), README index (Task 2), dispatch templates (Task 3), bootstrap weekly comment (Task 4), close-out (Task 5). ✓
- [x] **Placeholder scan**: no TBD/TODO inside task steps; conditional Step 3 in Task 3 is explicitly bounded by Verdict branch with concrete actions per branch. ✓
- [x] **Type consistency**: rule file content matches D4+Step 4.5 wording verbatim; README bullets match rule filenames. ✓
- [x] **Acceptance-criteria coverage**: Task 5 Step 1 enumerates every `- [ ]` on the issue body and maps it to the work that closes it. ✓
