---
name: engineering-issue-workflow
description: Mandatory workflow for engineering-critical GitHub issues — resource intelligence, plan review, TDD, implementation, and 3-provider cross-review.
category: coordination
triggers:
  - When a GitHub issue with cat:engineering, cat:engineering-calculations, cat:engineering-methodology, or cat:data-pipeline is mentioned or assigned
  - When the user asks to implement any engineering calculation, offshore standard, metocean, OrcaFlex, or data-pipeline work
  - When any commit touches digitalmodel/, worldenergydata/, or assetutilities/
version: 1.1.0
---

# Engineering Issue Workflow

**MANDATORY** for all engineering-critical issues.

## Scope

An issue is engineering-critical if it has ANY of:
- Labels: `cat:engineering`, `cat:engineering-calculations`, `cat:engineering-methodology`, `cat:data-pipeline`
- Paths: `digitalmodel/`, `worldenergydata/`, `assetutilities/`
- Topics: offshore engineering standards (DNV, API, ABS, ISO), OrcaFlex, metocean, cathodic protection

Reference: `docs/standards/HARD-STOP-POLICY.md`

## The Workflow (7 Steps)

```
STEP 1: Triage (first turn — classify issue)
STEP 2: Resource Intelligence (automated — search standards, repo, documents)
STEP 3: Write Plan (document what, how, tests, risks)
STEP 4: ◆ HARD STOP — USER APPROVES PLAN ◆ (DO NOT SKIP)
STEP 5: Implement (TDD: tests first, then code)
STEP 6: Cross-Review (Codex + Gemini review implementation against approved plan)
STEP 7: Close (commit, push, close issue with summary)
```

### STEP 1: Triage

On first contact with an engineering issue:
1. Read the **full issue body** — scope, acceptance criteria, references
2. Classify complexity:
   - **T1** (trivial): single-line fix, config, typo → brief plan, still requires approval
   - **T2** (standard): new module, multiple file changes, tests needed → full workflow
   - **T3** (complex): multi-module, architecture change, standards implementation → full workflow + subagents
3. Identify what **standards, modules, test fixtures, and documents** are relevant
4. **TELL THE USER**: "This is engineering-critical. I'm running resource intelligence before writing the plan."

### STEP 2: Resource Intelligence (AUTOMATIC)

Before writing the plan, search ALL available sources. Don't skip this — past sessions that jumped straight to implementation produced wrong code because they didn't check what already existed.

This step implements the **engineering issue-class retrieval bundle** per the retrieval contract (#2208). Engineering issues require the most thorough retrieval of any issue class.

**Search in this order:**

a) **Existing repo code** — is this already implemented?
   - `search_files(pattern="function_or_calc_name", path="digitalmodel/")`
   - `search_files(pattern="module_name", path="worldenergydata/")`
   - `search_files(pattern="related_topic", path="assetutilities/")`

b) **Standards coverage** — does the standard exist in the registry?
   - Read `data/document-index/standards-transfer-ledger.yaml`
   - Look for the standard number (e.g., DNV-RP-C212, API 579, ISO 19901-6)
   - Check if status is "done" or "gap"
   - Read `data/design-codes/code-registry.yaml` for applicable design codes

c) **Document intelligence** — are there relevant indexed documents?
   - Read `data/document-index/online-resource-registry.yaml`
   - Search for document name, topic, or standard
   - Check /mnt/ace/ for local PDFs (if mounted and accessible)

d) **Domain wiki knowledge** — what does the ecosystem already know?
   - Search relevant domain wiki under `knowledge/wikis/` (engineering, marine-engineering, naval-architecture)
   - Check for existing wiki pages covering the calculation, standard, or methodology

e) **Engineering reference data** — what parameters/constants apply?
   - `search_files(pattern="constants", path="digitalmodel/")`
   - `search_files(pattern="parameters", path="digitalmodel/")`
   - Read any relevant reference markdown in docs/

f) **Prior plans and related issues** — what has been tried before?
   - Check `docs/plans/` for related plans
   - Check recent open/closed issues for overlap or conflict

**CRITICAL GOTCHA:** The index.jsonl (647K records) has all records showing `content_type: "unknown"` and `summary_done: false`. The metadata was wiped or regenerated. Use `online-resource-registry.yaml` (247 entries, current) and `standards-transfer-ledger.yaml` (425 standards, 61.9% coverage) for lookups. These are reliable. The index.jsonl metadata is BROKEN.

**Evidence requirements (per #2208 retrieval contract):**
- ≥3 distinct sources must be consulted and recorded in the plan's Resource Intelligence Summary
- Each source must cite a specific file path, standard number, issue number, or registry entry
- Each source must state a concrete finding — not "searched the repo" but "found `digitalmodel/src/cathodic_protection.py` covering X"
- The Gaps sub-section must list what must be built from scratch
- For the full retrieval contract specification, see `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md`

### STEP 3: Write the Plan

Present the plan to the user. Format:

```markdown
## Plan for #ISSUE: Title

### Resource Intelligence Summary
<!-- ≥3 distinct sources required. Cite specific paths and findings. -->
- **Existing code found**: {file paths and what exists, or "no existing implementation"}
- **Standards applicable**: {standard numbers with status from ledger: done/gap, or "not applicable"}
- **Wiki pages consulted**: {wiki page paths with findings, or "no relevant wiki pages"}
- **Documents consulted**: {prior plans, registries, online resources — with specific findings}
- **Gaps identified**: {what must be built from scratch — each gap is a testable claim}

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

### STEP 4: ◆ HARD STOP — USER APPROVAL REQUIRED ◆

**STOP. Do NOT write any code. Do NOT create any files. Do NOT run any tests.**

Wait for the user to respond with one of:
- **APPROVE** / **GO** / **YES** → continue to Step 5
- **REVISE** / **CHANGE** → user provides feedback, re-do Step 3
- **REJECT** → ask what approach the user prefers

**If the user says "just do it" or "go ahead" WITHOUT seeing the plan:**
Present the plan first. Then wait. The approval must come AFTER seeing the plan.

For **overnight/batch sessions** (user not present):
- Write the plan as a **GitHub issue comment** before implementing
- Implementation starts only after the plan comment is posted
- User reviews results the next morning

### STEP 5: Implement (TDD)

After user approval:

1. **Tests FIRST** — write the test file, run it, confirm it FAILS
2. **Implement** — minimum code to make tests pass
3. **Run tests** — confirm they PASS
4. **Full test suite** — `uv run pytest` on the affected repo, confirm no regressions
5. **Self-review** — check the code against the approved plan

**Digitalmodel is a SEPARATE git repo** — commit from within `digitalmodel/` dir, NOT workspace-hub root.

**Use `uv run`** — never bare `python3` or `pip`.

### STEP 6: Adversarial Cross-Review

After implementation passes all tests:

1. Route to **Codex AND Gemini**
2. Each reviewer receives: the approved plan, the diff, test results, acceptance criteria
3. Collect verdicts: APPROVE | MINOR | MAJOR
4. If any MAJOR: present to user, fix, re-test
5. If all APPROVE or MINOR (resolved): proceed to Step 7

### STEP 7: Close

- Conventional commit message referencing the issue
- Push
- Close GitHub issue with summary: implementation done, test results, cross-review verdicts, follow-ups
- **Sources consumed**: list intelligence assets that materially informed implementation (≥1 item, per #2208 contract)
- **Promotion candidates**: note findings worth promoting from transient (L5) to durable knowledge (L3), or state "none" — ask: "Did this issue produce any finding that would help future issues or wiki readers?"

---

## Non-Critical Issues

Issues WITHOUT engineering-critical labels:
- Skip Steps 2-4 (resource intelligence, plan approval, hard stop)
- **TDD is still mandatory** — tests before implementation, always
- Implement → commit → close
- User can request the full workflow by asking for it

---

## Pitfalls & Gotchas (from historical session data)

### Agents Skipping the Workflow

**What happened:** 120+ engineering commits in 14 days, 542 commits since Mar 24, only 1 review artifact. The existing enforcement scripts (cross-review gate, review router, pre-push hook) all default to WARNING mode. Nobody blocked anything.

**How to avoid:** This skill is the new baseline. The plan must be presented BEFORE implementation. The user must approve. If you're unsure whether an issue is engineering-critical, ASK — don't assume.

### User Says "Just Implement It"

**What happened:** User tells the agent to skip planning and go straight to code. Agent complies, producing code without context.

**How to handle:** Show a brief plan first. The user can still approve quickly, but they must SEE the plan. "Here's what I'll do: [3 lines]. OK?" is sufficient.

### Thinking Work Is "Too Trivial" for a Plan

**What happened:** Agent decides a change is simple and skips the plan. Often the "simple" change was actually part of a larger system and broke something.

**How to handle:** Even T1 trivial changes need at least a one-line plan statement and user acknowledgment. No exceptions.

### Digitalmodel Is a Separate Git Repo

**What happened:** Agent commits from workspace-hub root, but `digitalmodel/` is a gitignored separate repo. Commits are lost.

**How to handle:** When touching `digitalmodel/` files, `cd digitalmodel/` before running `git add/commit/push`.

### The Document Index Metadata Is Broken

**What happened:** Agent searches index.jsonl for document metadata — gets `content_type: unknown` for all 647K records, `summary_done: false`. Agent assumes no data is available.

**How to handle:** Use `online-resource-registry.yaml` (247 entries, current) and `standards-transfer-ledger.yaml` (425 standards, 61.9% coverage) for lookups. These are reliable. The index.jsonl metadata was wiped/regenerated.

### Bypass Environment Variables

**What happened:** The enforcement scripts support `SKIP_REVIEW_GATE=1` and `GIT_PRE_PUSH_SKIP=1`. Agents discover and use them to skip checks.

**How to handle:** These are for emergencies only. If you're considering using them, present the reason to the user first and get explicit approval.

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
