---
name: issue-planning-mode
description: >
  Strict planning mode that runs after issue capture and before any implementation.
  Applies to ALL issues (engineering-critical and non-critical alike).
  Produces a repo-committed plan, adversarial cross-review by 3 frontier models,
  GitHub label + comment, and a hard user approval gate before any code is written.
version: 1.0.0
author: Hermes Agent
category: coordination
triggers:
  - After any GitHub issue is captured or assigned
  - When user says "plan this", "write a plan", or "let's plan issue #N"
  - Before any implementation begins — always
related_skills:
  - engineering-issue-workflow
  - writing-plans
  - multi-provider-adversarial-review
tags: [planning, issue-workflow, hard-stop, adversarial-review, tdd]
---

# Issue Planning Mode

**Mandatory** for ALL issues — engineering-critical and non-critical alike.
This mode runs AFTER issue capture and BEFORE any implementation.

The output of this mode is one artifact: an approved plan that every downstream
agent can execute against without guessing.

---

## The 5 Steps

```
STEP 1: Issue Intake          — read, classify, announce
STEP 2: Resource Intelligence — search all knowledge sources, map artifact locations
STEP 3: Draft the Plan        — pseudocode, file map, tests, acceptance criteria
STEP 4: Adversarial Review    — Claude + Codex + Gemini review the plan
STEP 5: HARD STOP             — post to GitHub, label, wait for user approval
```

---

## STEP 1 — Issue Intake

1. Read the **full issue body** — scope, acceptance criteria, references, labels
2. Classify complexity:
   - **T1** (trivial): single-line fix, config, typo — abbreviated plan still required
   - **T2** (standard): new module, multiple file changes, tests needed
   - **T3** (complex): multi-module, architecture change, standards implementation
3. Announce to user: "Planning issue #N. Running resource intelligence first."

---

## STEP 2 — Resource Intelligence

Read-only. No code written. Search ALL sources in this order:

### a) Repo Code
Is this already partially or fully implemented?
```
search_files(pattern="<function_or_calc_name>", path="digitalmodel/")
search_files(pattern="<module_name>", path="worldenergydata/")
search_files(pattern="<topic>", path="assetutilities/")
```
Record exact file paths and function names found.

### b) Standards Registry
```
docs/data/document-index/standards-transfer-ledger.yaml   # 425 standards, 61.9% coverage
docs/data/document-index/online-resource-registry.yaml    # 247 entries
```
Check gap vs done status for all standards referenced in the issue.

### c) LLM Wiki (primary knowledge base — consult before all else)
```
knowledge/wikis/marine-engineering/wiki/index.md
knowledge/wikis/maritime-law/wiki/index.md
knowledge/wikis/naval-architecture/wiki/index.md
```
Search index.md for entities and concepts relevant to the issue.
Use: `uv run scripts/knowledge/llm_wiki.py query "<keywords>" --wiki <domain>`

### d) Document Index + Local Docs
- `docs/` directory for prior plans, assessments, domain guides
- `/mnt/ace/` for local PDFs (if mounted)

### e) Session Memory
```python
session_search("<topic keywords>")
```
Check if similar work was done in a past session.

### f) Artifact Location Planning
Before drafting the plan, explicitly decide WHERE every output artifact will live:

| Artifact            | Path                                                       |
|---------------------|------------------------------------------------------------|
| Plan file           | docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md                  |
| Test files          | <repo>/tests/path/to/test_<module>.py                      |
| Implementation      | <repo>/src/path/to/<module>.py                             |
| Review artifacts    | scripts/review/results/YYYY-MM-DD-plan-NNN-<provider>.md   |
| Wiki updates        | knowledge/wikis/<domain>/wiki/...                          |
| Docs updates        | docs/<area>/<file>.md                                      |
| Plans index         | docs/plans/README.md                                       |

---

## STEP 3 — Draft the Plan

Save to `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`. Format:

```markdown
## Plan for #NNN: Issue Title

### Resource Intelligence Summary
- Existing code: {file paths and what exists}
- Standards: {list with gap/done status}
- Wiki pages consulted: {links}
- Docs consulted: {list}
- Gaps: {what must be built from scratch}

### Artifact Map
| Artifact          | Path                                     |
|-------------------|------------------------------------------|
| Plan              | docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md|
| Tests             | <repo>/tests/...                         |
| Implementation    | <repo>/src/...                           |
| Review artifacts  | scripts/review/results/...               |
| Wiki updates      | knowledge/wikis/<domain>/wiki/...        |

### Deliverable
One sentence: what will be built or changed.

### Pseudocode
For each new function or module, write 5-15 lines of pseudocode.
This is the design checkpoint — implementation follows this exactly.
T1 issues: may write "trivial — see files to change" instead.

### Files to Change
| Action | Path | Reason |
|--------|------|--------|

### TDD Test List
- Test: <name> -> <what it verifies> (expected input/output)

### Acceptance Criteria
- [ ] All tests pass: `uv run pytest <path>`
- [ ] No regression: `uv run pytest <repo>/` passes
- [ ] {specific numerical or engineering check}
- [ ] Docs updated
- [ ] Wiki updated (if domain knowledge was added)

### Risks and Open Questions

### Complexity: T1 | T2 | T3
```

---

## STEP 4 — Adversarial Plan Review

Send the drafted plan to **three frontier models in parallel** before the user
ever sees it. The goal: catch gaps, wrong approaches, and missing tests before
the user spends review time on a weak plan.

### Dispatch (parallel)
Each reviewer receives:
- Full plan markdown
- Issue body (context)
- Prompt: "Review this implementation plan for completeness, correctness,
  feasibility, and best practices (DRY, YAGNI, TDD). Identify gaps, risks,
  or improvements. Verdict: APPROVE, MINOR (suggestions), or MAJOR (required changes)."

Providers:
- **Claude Code** — via `delegate_task` with `acp_command: claude`
- **Codex** — via `delegate_task` with codex skill
- **Gemini** — via `delegate_task` with gemini-batch-execution skill

### Save Review Artifacts
Each review saved to:
`scripts/review/results/YYYY-MM-DD-plan-NNN-<provider>.md`

### Decision Gate
- **Any MAJOR verdict** → plan FAILS adversarial review
  - Synthesize feedback, revise Step 3, re-run Step 4
  - Loop until no MAJOR verdicts remain
- **All APPROVE or MINOR** (with minor suggestions resolved or noted) → plan PASSES
  - Proceed to Step 5

---

## STEP 5 — Hard Stop: Post to GitHub + Wait for User Approval

**STOP. No code. No files. No tests. Not even a scaffold.**

### Actions before waiting (in order):
1. Save plan file to `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`
2. Commit plan file: `git add docs/plans/ && git commit -m "plan: add plan for #NNN <slug>"`
3. Update `docs/plans/README.md` — add entry to the planning index
4. Post plan as a comment on the GitHub issue (full plan markdown + review summary)
5. Add label `status:plan-review` (orange #FFA500) to the issue
6. **STOP** — wait for user response

### Valid user responses:
| Response                | Action                                                    |
|-------------------------|-----------------------------------------------------------|
| APPROVE / GO / YES      | Remove `status:plan-review`, add `status:plan-approved` (green), proceed to implementation |
| REVISE / CHANGE + notes | Incorporate feedback, re-draft Step 3, re-run adversarial review if plan changed significantly, re-post |
| REJECT                  | Remove label, open discussion on alternative approach     |

### Batch session rule (user offline):
- User reviews and approves ALL plans in a live planning session FIRST
- Approved plans are labeled `status:plan-approved`
- Batch execution ONLY picks up `status:plan-approved` issues
- **No batch execution on `status:plan-review` issues — ever**

---

## Handoff Line (end of planning mode)

After user approval, output:

```
Plan for #NNN approved and saved at docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md
Label updated: status:plan-approved
Proceeding to implementation — TDD first.
```

Then hand off to `engineering-issue-workflow` Step 5 (implement) or the
equivalent implementation workflow for non-engineering issues.

---

## GitHub Labels

Both labels must exist before this skill is used:

| Label                | Color   | Description                                           |
|----------------------|---------|-------------------------------------------------------|
| `status:plan-review`   | #FFA500 | Plan drafted — awaiting adversarial review + user approval |
| `status:plan-approved` | #2EA44F | Plan user-approved — ready for batch/scheduled execution |

Create if missing:
```bash
gh label create "status:plan-review" --description "Plan drafted — awaiting adversarial review and user approval" --color "FFA500"
gh label create "status:plan-approved" --description "Plan user-approved — ready for batch/scheduled execution" --color "2EA44F"
```

---

## Pitfalls

### Skipping adversarial review because "the plan is simple"
Don't. T1 plans take 2 minutes to review in parallel. The value is catching
wrong assumptions before they reach user review time, not just catching complex bugs.

### Running adversarial review sequentially instead of in parallel
All three providers must be dispatched at the same time via parallel delegate_task calls.
Sequential review wastes time and defeats the purpose.

### Posting to GitHub before adversarial review passes
The user should only see a plan that has already survived frontier model scrutiny.
Posting a MAJOR-flagged plan wastes user review time.

### Forgetting to update docs/plans/README.md
This is the index the batch execution agent reads. If it's not in README.md,
the batch agent won't know it's approved.

### Using .hermes/plans/ instead of docs/plans/
All plans go to docs/plans/ — git-tracked in the repo, visible to all agents.
.hermes/plans/ is for personal/offline-only ephemeral plans only.

### Batch-executing a "status:plan-review" issue
Hard rule: status:plan-review means user has NOT approved. Never execute.
Only status:plan-approved issues are batch-safe.
