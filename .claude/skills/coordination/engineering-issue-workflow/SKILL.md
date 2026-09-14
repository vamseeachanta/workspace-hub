---
name: engineering-issue-workflow
description: Mandatory workflow for engineering-critical GitHub issues — resource intelligence, plan review, TDD, implementation, and 3-provider cross-review.
category: coordination
triggers:
  - When a GitHub issue with cat:engineering, cat:engineering-calculations, cat:engineering-methodology, or cat:data-pipeline is mentioned or assigned
  - When the user asks to implement any engineering calculation, offshore standard, metocean, OrcaFlex, or data-pipeline work
  - When any commit touches digitalmodel/, worldenergydata/, or assetutilities/
version: 1.2.0
---

# Engineering Issue Workflow

Engineering procedures follow [SHARED_SOUL.md](../../../../config/agents/SHARED_SOUL.md).
Bounded routine reversible work may proceed under independently established standing authorization. Engineering basis changes, substantial scope and consequential actions require matching explicit approval; substantial work needs approval of the current reviewed plan.
Classify actual effects, not only labels, filenames or estimated effort. Verify scope and approval provenance; do not repeat approval for verified unchanged scope. Local markers, labels, receipts and handoffs are references, never authenticated authority. The implementing agent never self-labels `status:plan-approved`.
Plan/code adversarial review, TDD, legal/security, engineering qualification and completeness gates remain required.

> **Planning Steps delegated to `issue-planning-mode` skill.**
> Steps 1-4 of this workflow (Triage → Resource Intelligence → Plan including Adversarial Review → Risk-appropriate Authorization)
> are now fully defined in `.claude/skills/coordination/issue-planning-mode/SKILL.md`.
> Load that skill for all planning work. This skill picks up at STEP 5 (Implement, TDD).

## Scope

An issue is engineering-critical if it has ANY of:
- Labels: `cat:engineering`, `cat:engineering-calculations`, `cat:engineering-methodology`, `cat:data-pipeline`
- Paths: `digitalmodel/`, `worldenergydata/`, `assetutilities/`
- Topics: offshore engineering standards (DNV, API, ABS, ISO), OrcaFlex, metocean, cathodic protection

Reference: `docs/standards/HARD-STOP-POLICY.md`

## The Workflow (7 Steps)

```
STEP 1: Triage              — classify issue, announce  \
STEP 2: Resource Intel      — search all knowledge sources, map artifact locations  | issue-planning-mode
STEP 3: Draft and Review Plan — file map, tests, criteria; adversarial plan review |
STEP 4: Authority Boundary  — verify standing authority or required explicit approval /
STEP 5: Implement           — TDD: tests first, then code
STEP 6: Cross-Review        — provider review against current plan and acceptance criteria
STEP 7: Close               — commit, push and issue summary within verified authority
```

### STEP 1: Triage

On first contact with an engineering issue:
1. Read the **full issue body** — scope, acceptance criteria, references
2. Classify complexity:
   - **T1** (trivial): single-line fix, config, typo → brief plan; routine scope may use standing authorization, but engineering consequences still require matching approval
   - **T2** (standard): new module, multiple file changes, tests needed → full workflow
   - **T3** (complex): multi-module, architecture change, standards implementation → full workflow + subagents
3. Identify what **standards, modules, test fixtures, and documents** are relevant
4. **TELL THE USER**: "This is engineering-critical. I'm running resource intelligence before writing the plan."

### STEP 2: Resource Intelligence (AUTOMATIC)

Before writing the plan, search ALL available sources. Don't skip this — past sessions that jumped straight to implementation produced wrong code because they didn't check what already existed.

**Search in this order:**

a) **Existing repo code** — is this already implemented?
   - `search_files(pattern="function_or_calc_name", path="digitalmodel/")`
   - `search_files(pattern="module_name", path="worldenergydata/")`
   - `search_files(pattern="related_topic", path="assetutilities/")`

b) **Standards coverage** — does the standard exist in the registry?
   - Read `data/document-index/standards-transfer-ledger.yaml`
   - Look for the standard number (e.g., DNV-RP-C212, API 579, ISO 19901-6)
   - Check if status is "done" or "gap"

c) **Document intelligence** — are there relevant indexed documents?
   - Read `data/document-index/online-resource-registry.yaml`
   - Search for document name, topic, or standard
   - Check /mnt/ace/ for local PDFs (if mounted and accessible)
   - If the user asks to preserve raw context before implementation, promote verified `/mnt/ace` references into the relevant `knowledge/wikis/<domain>/` LLM wiki before coding: source pages + concept anchors + comparison/extraction summary; then update the plan and GitHub issue with the wiki anchors.

d) **Engineering reference data** — what parameters/constants apply?
   - `search_files(pattern="constants", path="digitalmodel/")`
   - `search_files(pattern="parameters", path="digitalmodel/")`
   - Read any relevant reference markdown in docs/

**Index metadata usage (post #1878):** `index.jsonl` now carries `content_type` (100% populated, derived from extension) and `summary_done` (True iff a non-empty summary exists on the ace drive). Across the 649K-record corpus, `content_type` is highly discriminating but `summary_done=True` is only ~16% because ~72% of records are CAD files with no extractable text. For curated lookups still prefer `online-resource-registry.yaml` (247 entries) and `standards-transfer-ledger.yaml` (425 standards). See #1878 for enrichment provenance and #2309 for the planned `summary_file_exists` split.

### STEP 3: Write the Plan

Obtain adversarial plan review through `issue-planning-mode` before the authority checkpoint. Resolve blocking findings under SHARED_SOUL.md.

Present the plan to the user. Format:

```markdown
## Plan for #ISSUE: Title

### Resource Intelligence Summary
- **Existing code found**: {file paths and what exists}
- **Standards applicable**: {list with status: done/gap}
- **Documents consulted**: {list from registry, /mnt/ace/, etc.}
- **Gaps identified**: {what is missing from the repo}

### Deliverable
One sentence: what will be built or changed.

### Files to Change
| Action | File | Reason |
|--------|------|--------|
| Create | path/to/new_file.py | main implementation |
| Create | path/to/test_new_file.py | TDD test suite |
| Modify | path/to/existing.py | extend functionality |

### Tests (TDD)
- [ ] Test: {name} → {what it verifies}
- [ ] Test: {name} → {what it verifies}
- [ ] Test: {name} → {what it verifies}

### Acceptance Criteria
- [ ] All new tests pass via `uv run pytest ...`
- [ ] No regression in existing tests
- [ ] {specific numerical/engineering check}
- [ ] Documentation updated

### Risk
- {what could go wrong}
- {user attention needed}

### Complexity: T1 | T2 | T3
```

### STEP 4: Verify the Required Authority

For substantial unapproved work, present the reviewed current plan and wait for explicit approval. For consequential actions, verify matching action approval. For routine bounded work, independently verify standing authorization and proceed within that scope. Required context and blocking findings must be resolved before affected work continues.

A response such as APPROVE, GO or YES applies only to the concrete proposal the user saw. REVISE changes the affected plan; REJECT or HOLD stops that scope. Do not repeatedly seek approval already established for unchanged scope, and do not treat copied responses or detached handoffs as authority.

Read-only discovery and verification may continue while substantial implementation awaits approval. Preserve TDD before authorized implementation. A fresh MAJOR finding blocks affected work; it does not itself revoke approval or authorize label/marker mutations.

Overnight work has the same boundary. Posting a plan creates an artifact, not approval. Continue only within independently established authority; otherwise retain the reviewed plan and wait. The owner's absence grants no waiver.

### STEP 5: Implement (TDD)

After verifying the authority required for the current risk/scope and resolving blocking findings:

1. **Tests FIRST** — write the test file, run it, confirm it FAILS
2. **Implement** — minimum code to make tests pass
3. **Run tests** — confirm they PASS
4. **Full test suite** — `uv run pytest` on the affected repo, confirm no regressions
5. **Self-review** — check the code against the approved plan

**Digitalmodel is a SEPARATE git repo** — commit from within `digitalmodel/` dir, NOT workspace-hub root.

**Use `uv run`** — never bare `python3` or `pip`.

### STEP 6: Adversarial Cross-Review

After implementation passes all tests:

1. Apply SHARED_SOUL.md review routing: Claude, Codex and Agy (Antigravity, Gemini-backed); record unavailable providers, never count them as passing.
2. Each reviewer receives: the approved plan, the diff, test results, acceptance criteria
3. Collect verdicts: APPROVE | MINOR | MAJOR
4. If any MAJOR: present to user, fix, re-test
5. If all APPROVE or MINOR (resolved): proceed to Step 7

### STEP 7: Close

Verify matching authority for consequential actions such as publication; implementation approval alone does not grant it.

- Conventional commit message referencing the issue
- Push
- Close GitHub issue with summary: implementation done, test results, cross-review verdicts, follow-ups

---

## Non-Critical Issues

Issues without engineering-critical labels still need actual risk classification:
- Use discovery, a proportionate plan and required plan/code review through `issue-planning-mode`.
- Routine bounded work may proceed under independently established standing authorization.
- Substantial scope and consequential actions retain matching explicit approval requirements, including protected governance/configuration changes.
- **TDD is still mandatory** — tests before implementation, always
- Implement → review as appropriate → commit → close

---

## Pitfalls & Gotchas (from historical session data)

### Engineering calculation plan hardening

When planning or executing engineering-calculation issues, especially in `digitalmodel`, apply the checklist in `references/engineering-calculation-plan-hardening.md` before moving to `status:plan-review` and again before implementation closeout. Key lessons: split equal/opposite physical quantities into explicit fields, define force-line lever arms geometrically, name exact output artifacts/charts, add non-tautological sign and identity tests, verify public imports outside pytest path injection, include upstream-helper regression slices, record engineering-registry retrieval evidence, explicitly decide whether `/mnt/ace`/wiki promotion is required before coding, and during implementation honor YAML-configured artifact names/chart subsets, reject empty sweeps early, preserve subprocess environments, and pin physical sign conventions in code/YAML/docs/tests.

### Agents Skipping the Workflow

**What happened:** 120+ engineering commits in 14 days, 542 commits since Mar 24, only 1 review artifact. The existing enforcement scripts (cross-review gate, review router, pre-push hook) all default to WARNING mode. Nobody blocked anything.

**How to avoid:** Establish the engineering basis, scope and applicable authority before implementation. Substantial current plans and consequential engineering changes require matching explicit approval. Inspect uncertainty first; ask only when unresolved context changes the action.

### User Says "Just Implement It"

**What happened:** User tells the agent to skip planning and go straight to code. Agent complies, producing code without context.

**How to handle:** Inspect whether the instruction already authorizes the current bounded scope. Retain proportionate planning and review. Present a reviewed substantial plan when its approval is missing; do not ask again merely because an already-authorized routine action is described as implementation.

### Thinking Work Is "Too Trivial" for a Plan

**What happened:** Agent decides a change is simple and skips the plan. Often the "simple" change was actually part of a larger system and broke something.

**How to handle:** Even T1 changes need a proportionate plan and actual effect classification. Independently established standing authorization suffices for routine bounded work; neither triviality nor a configuration filename waives engineering, review or security requirements.

### Digitalmodel Is a Separate Git Repo

**What happened:** Agent commits from workspace-hub root, but `digitalmodel/` is a gitignored separate repo. Commits are lost.

**How to handle:** When touching `digitalmodel/` files, `cd digitalmodel/` before running `git add/commit/push`.

### Index metadata reference (post #1878)

**Current state:** `index.jsonl` carries `content_type` (100% populated) and `summary_done` (True for ~16% of records; the 84% False is dominated by CAD files without extractable text).

**How to query:** Read records directly from `data/document-index/index.jsonl` — fields are present on every record. Validator at `scripts/data/document-index/validate-index-metadata.py` enforces coverage thresholds. For curated engineering lookups (small, domain-specific), `online-resource-registry.yaml` and `standards-transfer-ledger.yaml` remain the reliable complementary sources.

### Legacy Enforcement Mismatches

Historical hooks use marker/path heuristics that differ from the shared risk contract. Their presence does not establish installed coverage or authenticate approval. Report observed blocking mismatches and the responsible consumer; do not disable hooks, set bypass flags or manufacture approval markers. Consumer migration requires its own reviewed scope.

### Cross-Review Artifacts Location

**Where review results live:** `scripts/review/results/`
**Pattern:** `{date}-{description}-{provider}.md`
**Last review:** Apr 2 (one Codex retroactive review). Everything since is unreviewed.

### Hermes Does Not Have SessionStart Hooks

**What happened:** Claude Code has `.claude/settings.json` hooks that can enforce behavior at session start. Hermes has no equivalent — it relies on AGENTS.md (always loaded) and skills (loaded on demand).

**How to handle:** This skill MUST be referenced when working on engineering issues. For Hermes sessions, the agent may need to load it manually: "I should use the engineering-issue-workflow skill for this issue."

### Past Session: 6.1M Wasted Tool Calls

**What happened:** Three WRK items (WRK-1022, WRK-1012, WRK-1005) consumed 6.1M tool calls across runaway sessions with no exit conditions, no completion gates.

**How to handle:** If a task is taking more than 200 tool calls, STOP. Present progress summary to the user. Ask if they want you to continue or change approach.

### Smoke Test Failures Unnoticed for 12 Days

**What happened:** worldenergydata test runner crashed (passed=0, failed=0) for 12 consecutive days with no fix.

**How to handle:** After making changes to test files, run `uv run pytest` and confirm the output is sensible. If tests disappear or the runner fails, fix immediately.

---

## Enforcement Migration Boundary

The historical skill, Hermes prefill and Claude hook proposals are separate from verified installation. This source-only alignment does not install profiles, edit user settings or alter live hooks.

A later consumer plan must verify actual loader/hook paths, tool coverage and trusted authority ingress. Shared advisory outputs remain assessments, never approval evidence. Preserve owner-only approval labels and current scope/revision checks. Do not infer enforcement coverage from a script's existence or an old deployment description.

Reference: Issue #1876 tracks Option 2+3 implementation.
