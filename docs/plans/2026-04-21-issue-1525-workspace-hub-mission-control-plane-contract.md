# Plan for #1525: Define canonical repo control-plane contract across workspace ecosystem

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/1525
> **Review artifacts:** `scripts/review/results/20260421T141459Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-claude.md` | `scripts/review/results/20260421T141459Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-codex.md` | `scripts/review/results/20260421T141459Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-gemini.md` | `scripts/review/results/20260421T142328Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-claude.md` | `scripts/review/results/20260421T142328Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-codex.md` | `scripts/review/results/20260421T142328Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-gemini.md` | `scripts/review/results/20260421T143224Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-claude.md` | `scripts/review/results/20260421T143224Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-codex.md` | `scripts/review/results/20260421T143224Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-gemini.md` | `scripts/review/results/20260421T154852Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-claude.md` | `scripts/review/results/20260421T154852Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-codex.md` | `scripts/review/results/20260421T154852Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-gemini.md` | `scripts/review/results/20260421T160111Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-claude.md` | `scripts/review/results/20260421T160111Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-codex.md` | `scripts/review/results/20260421T160111Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-gemini.md` | `scripts/review/results/20260421T161436Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-claude.md` | `scripts/review/results/20260421T161436Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-codex.md` | `scripts/review/results/20260421T161436Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-gemini.md` | `scripts/review/results/20260421T162326Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-claude.md` | `scripts/review/results/20260421T162326Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-codex.md` | `scripts/review/results/20260421T162326Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-gemini.md` | `scripts/review/results/20260421T163248Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-claude.md` | `scripts/review/results/20260421T163248Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-codex.md` | `scripts/review/results/20260421T163248Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `AGENTS.md` — already defines workflow gates, issue-planning sequence, TDD, and review policy, but does not explicitly define `workspace-hub` as the ecosystem control plane or name the downstream repo-role contract.
- Found: `README.md` — describes a repository-management hub with 25 managed repos and modular tooling, but still frames the repo mainly as a multi-repo operations shell rather than the canonical ecosystem control plane.
- Found: `docs/README.md` — describes workspace-hub as the central reference for the workspace and includes knowledge/intelligence ecosystem sections, but mission intent is mixed with documentation-index concerns.
- Found: `docs/BUSINESS_BRAIN.md` — strongest current ecosystem-role document; explicitly identifies tier-1 repos and says GSD is the control plane, but this role is not normalized back into the main repo onboarding surfaces.
- Found: `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` — explicitly says workspace-hub is a centralized repo-management system and “single control plane for 25 repositories,” but this still needs reconciliation with README, AGENTS, and knowledge/llm-wiki language.
- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` — standardizes `AGENTS.md` as canonical repo entry point and treats `.agent-os/` as legacy, but it does not by itself define the mission and non-goals of `workspace-hub` as the root repo.
- Gap: no single canonical mission artifact states what `workspace-hub` owns, what it does not own, how the Wave-1 tier-1 repos (`digitalmodel`, `assetutilities`, `aceengineer-website`) relate to it, and how llm-wiki fits without pre-deciding `#2398`.
- Deferred explicitly: `worldenergydata` role language is Wave-2 scope and is not required to land in this first packet.

### Standards
| Standard | Status | Source |
|---|---|---|
| Control-plane entry-point contract (`AGENTS.md` + provider adapters) | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Mandatory issue-planning workflow | done | `docs/plans/README.md`, `AGENTS.md` |
| Repo-intelligence / llm-wiki operating model | partial / adjacent | `docs/plans/2026-04-20-issue-2398-llm-wiki-spinout-vs-embedded-architecture.md`, issue `#2390` |

### LLM Wiki pages consulted
- No direct wiki page is required for the first mission-contract pass; the relevant llm-wiki dependency is architectural and issue-driven rather than page-content-driven.
- Related architecture evidence is instead captured through issue `#2398` and issue `#2390`, which already frame llm-wiki as a cross-repo durable-knowledge concern.

### Documents consulted
- `docs/BUSINESS_BRAIN.md` — defines tier-1 repos (`workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`) and states “GSD is the control plane.”
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` — defines workspace-hub as a centralized repository management system and explicitly says “Single control plane for 25 repositories.”
- `README.md` — current public-facing repo description, which still emphasizes module layout and multi-repo operations over explicit portfolio mission and non-goals.
- `docs/README.md` — central docs index; includes knowledge/intelligence language that should be consistent with the repo mission.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — formal standard for agent entry points and legacy-path disposition.
- Related issue #2398 — open architecture question on llm-wiki embedded vs spinout boundaries; the mission contract must not pre-empt this decision.
- Related issue #2390 — active llm-wiki strengthening roadmap; shows llm-wiki is operationally important to the repo ecosystem.
- `docs/reports/2026-04-21-repo-mission-revision-sequence.md` — latest steering report recommending `workspace-hub` as the first repo approval packet before revising downstream repo missions.
- `AGENTS.md` line count check (`wc -l AGENTS.md` on 2026-04-21) — current file is exactly 20 lines, so this packet cannot add a mission pointer without first deleting existing workflow content; therefore `AGENTS.md` is effectively no-edit for this packet unless a same-size substitution is explicitly planned.

### Gaps identified
- No single statement defines `workspace-hub` as control plane, with explicit non-goals.
- No normalized downstream-role table states that `digitalmodel` is the engineering computation core, `assetutilities` is the shared utility substrate, and `aceengineer-website` is the GTM layer.
- `worldenergydata` is out of scope for role-definition in this packet; the only required treatment here is an explicit defer note to Wave-2 so later reviewers do not infer omission by accident.
- No top-level mission text explains how llm-wiki participates as a durable cross-repo knowledge layer without prematurely deciding the embedded-vs-spinout question.
- Existing documents overlap in scope and terminology, increasing future issue-triage drift.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view`):
- `#1525` — OPEN — Define canonical repo control-plane contract across workspace ecosystem
- `#2398` — OPEN — feat(knowledge): assess llm-wiki spinout vs embedded workspace-hub architecture
- `#2390` — OPEN — epic(knowledge): llm-wiki strengthening roadmap and execution waves

**File existence** (verified 2026-04-21):
- EXISTS: `README.md`
- EXISTS: `docs/README.md`
- EXISTS: `docs/BUSINESS_BRAIN.md`
- EXISTS: `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`
- EXISTS: `AGENTS.md`
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `docs/reports/2026-04-21-repo-mission-revision-sequence.md`
- EXISTS: `.planning/quick/issue-1525-followup-ci-validator.md`
- MISSING (new — this plan creates): `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`
- MISSING (new — this plan creates): `scripts/validation/check_workspace_hub_mission_contract.py`
- MISSING (new — this plan creates): `tests/validation/test_workspace_hub_mission_contract.py`

**Line-count evidence** (`wc -l AGENTS.md` on 2026-04-21):
- `AGENTS.md` — `20` lines

**Line excerpts**
```text
AGENTS.md
- Hard Gates: Plan ALL issues ... Adversarial Review ... USER APPROVES ... Implement (TDD)
- Workflow: GSD framework ... tasks as GitHub issues

README.md
- A centralized management system for multiple GitHub repositories with modular organization.
- This hub manages 25 independent Git repositories while maintaining their autonomy.

docs/BUSINESS_BRAIN.md
- Tier-1: workspace-hub | Engineering workspace, GSD framework, AI harness
- GSD is the control plane. Do not replace it.

docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md
- Multi-Repository Management: Single control plane for 25 repositories

docs/standards/CONTROL_PLANE_CONTRACT.md
- AGENTS.md is the canonical entry point for every repository.
- .agent-os/ is Legacy ... No new repos should create .agent-os/.
```

**Gap proofs**
- No existing canonical mission contract file for workspace-hub was found under `docs/reports/` or `docs/plans/` using searches for `workspace-hub repo mission`, `ecosystem role contract`, and `mission canonicalization`.

---

## Artifact Map

### Existing evidence inputs

| Artifact | Path | Status in this packet |
|---|---|---|
| This plan | `docs/plans/2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md` | active draft being iterated |
| Steering report input | `docs/reports/2026-04-21-repo-mission-revision-sequence.md` | pre-existing input |
| Cross-repo entrypoint standard input | `docs/standards/CONTROL_PLANE_CONTRACT.md` | pre-existing input |
| Existing review wave 1 artifacts | `scripts/review/results/20260421T141459Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-{claude,codex,gemini}.md` | already generated evidence |
| Existing review wave 2 artifacts | `scripts/review/results/20260421T142328Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-{claude,codex,gemini}.md` | already generated evidence |
| Existing review wave 3 artifacts | `scripts/review/results/20260421T143224Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-{claude,codex,gemini}.md` | already generated evidence |
| Existing review wave 4 artifacts | `scripts/review/results/20260421T154852Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-{claude,codex,gemini}.md` | already generated evidence |
| Existing review wave 5 artifacts | `scripts/review/results/20260421T160111Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-{claude,codex,gemini}.md` | already generated evidence |
| Existing review wave 6 artifacts | `scripts/review/results/20260421T161436Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-{claude,codex,gemini}.md` | already generated evidence |
| Existing review wave 7 artifacts | `scripts/review/results/20260421T162326Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-{claude,codex,gemini}.md` | already generated evidence |
| Existing review wave 8 artifacts | `scripts/review/results/20260421T163248Z-2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md-plan-{claude,codex,gemini}.md` | already generated evidence |

### Planned outputs from the eventual implementation of this approved plan

| Artifact | Path | Status in this packet |
|---|---|---|
| Canonical mission contract (normative, not a report) | `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` | to be created after approval |
| Validation script | `scripts/validation/check_workspace_hub_mission_contract.py` | to be created after approval |
| Updated root README | `README.md` | to be modified after approval |
| Updated docs index | `docs/README.md` | to be modified after approval |
| Updated business brain | `docs/BUSINESS_BRAIN.md` | to be modified after approval |
| Updated repo overview | `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` | to be modified after approval |
| Mandatory generic-only cross-link touch | `docs/standards/CONTROL_PLANE_CONTRACT.md` | must add the generic cross-link/relationship note while remaining free of workspace-hub-specific ownership tables and mission prose |
| No-change evidence for AGENTS cap | `AGENTS.md` | remains unchanged in this packet and in planned implementation |
| Updated plan index row | `docs/plans/README.md` | to be updated after approval |
| Refined CI follow-up issue draft | `.planning/quick/issue-1525-followup-ci-validator.md` | to be refined after approval |

---

## Canonical Terminology Contract

The validation script must enforce these exact phrase rules.

### Required phrases

#### Must appear as a `## Non-goals` section heading in `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`
- `Non-goals`

#### Must appear in `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`
- `workspace-hub is the ecosystem control plane`
- `GSD is the workflow control plane used within workspace-hub`
- `digitalmodel is the engineering computation core`
- `assetutilities is the shared utility substrate`
- `aceengineer-website is the GTM and externalization layer`
- `worldenergydata role definition is deferred to the Wave-2 repo mission packet`
- `llm-wiki is a durable cross-repo knowledge layer`
- `repo-boundary architecture remains under evaluation per #2398`

#### Required non-goals (must appear as bullets in `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`)
- `workspace-hub does not own engineering computations; digitalmodel owns that layer`
- `workspace-hub does not serve as the shared utility library; assetutilities owns that layer`
- `workspace-hub does not own the GTM/public website surface; aceengineer-website owns that layer`
- `workspace-hub does not silently decide the llm-wiki repo boundary before #2398 is resolved`

### Required glossary terms (must appear as a `## Glossary` section in `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` using bullet lines of the form `- term — definition`)
- `ecosystem control plane` — workspace-hub's portfolio-level coordination role
- `workflow control plane` — GSD inside workspace-hub
- `engineering computation core` — digitalmodel's role
- `shared utility substrate` — assetutilities' role
- `GTM and externalization layer` — aceengineer-website's role

### Validator semantics

The validation script and tests must use these matching rules:
- case-sensitive matching for required canonical statements
- normalize CRLF to LF before matching
- normalize Unicode to NFC before matching
- trim trailing whitespace before matching
- treat required non-goal bullets as whole-line matches after markdown bullet prefix normalization
- treat forbidden phrases as regex whole-line matches after line normalization when a rule is marked standalone, otherwise as substring matches after paragraph-whitespace normalization
- treat semantic role-claim checks as regex-based sentence checks against the canonical truth set defined in this plan
- normalize markdown paragraph line-wraps by replacing embedded newlines within paragraph blocks with single spaces before phrase and semantic-regex evaluation
- fenced code blocks are detected only by triple-backtick fences: a fenced block starts at a line matching /^```/ and ends at the next line matching /^```/; nested fences and indented code blocks are not exempt
- required-phrase checks, forbidden-phrase checks, and semantic-regex checks all exclude content inside triple-backtick fenced code blocks

#### File-specific expectations
- `README.md` must contain `workspace-hub is the ecosystem control plane`
- `docs/README.md` must contain `workspace-hub is the ecosystem control plane`
- `docs/BUSINESS_BRAIN.md` must contain both `workspace-hub is the ecosystem control plane` and `GSD is the workflow control plane used within workspace-hub`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` must contain `workspace-hub is the ecosystem control plane`
- `docs/standards/CONTROL_PLANE_CONTRACT.md` must continue to define `AGENTS.md` as the canonical entry point and must not be changed to encode workspace-hub-specific repo-role ownership tables

#### Must appear in each reconciled document
Files:
- `README.md`
- `docs/README.md`
- `docs/BUSINESS_BRAIN.md`
- `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`

Required shared phrase:
- `control plane`

#### Must appear in `AGENTS.md` only if `AGENTS.md` is edited in a separate follow-up issue
- `For repository mission and ecosystem role, see docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`

### Forbidden phrases

The validation script must fail if any reconciled document contains any of the following:
- `llm-wiki will be spun out`
- `llm-wiki is permanently embedded`
- `workspace-hub is the engineering computation core`
- `assetutilities is the control plane`
- `aceengineer-website is the control plane`
- `digitalmodel is the control plane`

### Standalone forbidden regexes

These rules are whole-line regex checks after trimming whitespace and excluding triple-backtick fenced code blocks:
- `(?m)^\s*GSD is the control plane\s*\.?\s*$`

### Semantic alignment contract

The validation script must enforce these exact role-ownership statements as the canonical truth set for this packet:
- `workspace-hub is the ecosystem control plane`
- `digitalmodel is the engineering computation core`
- `assetutilities is the shared utility substrate`
- `aceengineer-website is the GTM and externalization layer`
- `worldenergydata role definition is deferred to the Wave-2 repo mission packet`

Reference regex catalog for `test_role_claims_do_not_contradict_contract`:
- Allowed ecosystem control-plane claim: `(?m)\bworkspace-hub is the ecosystem control plane\b`
- Forbidden ecosystem control-plane claim for non-workspace-hub repos: `(?m)\b(digitalmodel|assetutilities|aceengineer-website|worldenergydata) is the ecosystem control plane\b`
- Allowed engineering-core claim: `(?m)\bdigitalmodel is the engineering computation core\b`
- Forbidden engineering-core claim for non-digitalmodel repos: `(?m)\b(workspace-hub|assetutilities|aceengineer-website|worldenergydata) is the engineering computation core\b`
- Allowed utility-substrate claim: `(?m)\bassetutilities is the shared utility substrate\b`
- Forbidden utility-substrate claim for non-assetutilities repos: `(?m)\b(workspace-hub|digitalmodel|aceengineer-website|worldenergydata) is the shared utility substrate\b`
- Allowed GTM-layer claim: `(?m)\baceengineer-website is the GTM and externalization layer\b`
- Forbidden GTM-layer claim for non-website repos: `(?m)\b(workspace-hub|digitalmodel|assetutilities|worldenergydata) is the GTM and externalization layer\b`

For the reconciled documents in scope (`README.md`, `docs/README.md`, `docs/BUSINESS_BRAIN.md`, `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md`) and for the canonical mission contract itself (`docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`), the validator must fail if any file contains a match for a forbidden regex above outside fenced code blocks.

For `docs/BUSINESS_BRAIN.md`, the validator must allow `GSD is the workflow control plane used within workspace-hub` while still requiring `workspace-hub is the ecosystem control plane`. This packet must not collapse those two layers into one phrase.

A standalone match for `GSD is the control plane` must always fail.

### AGENTS.md contradiction rule

This packet does not edit `AGENTS.md`.
Reason: `AGENTS.md` is currently 20 lines long, which is already at the enforced cap.

Operational rule for this packet:
- `AGENTS.md` must remain unchanged
- if mission-pointer alignment is still desired after this packet lands, create a follow-up issue that first makes room within the 20-line cap or explicitly restructures the file under a separately reviewed plan

### Plan-index rule

`test_plan_index_updated` passes only if `docs/plans/README.md` contains one row in the `## Plan Index` table with all seven populated columns in this schema:
- `Issue #`
- `Title / Slug`
- `Plan File`
- `Date`
- `Status`
- `Complexity`
- `Notes`

For issue `#1525`, the row must include:
- issue number `1525`
- slug `workspace-hub-mission-control-plane-contract`
- plan path `docs/plans/2026-04-21-issue-1525-workspace-hub-mission-control-plane-contract.md`

---

## Deliverable

A canonical workspace-hub mission and ecosystem-role contract at `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`, reflected consistently across the repo’s main onboarding/navigation documents and explicitly naming the control-plane role, non-goals, downstream repo roles, and the current llm-wiki boundary stance.

---

## Pseudocode

```text
collect the current top-level workspace-hub mission statements from README, docs index, business-brain, repo overview, AGENTS, and control-plane standard
extract overlapping claims about repo purpose, control-plane role, knowledge ownership, and downstream repo relationships
write one canonical mission contract that states:
    what workspace-hub owns
    what workspace-hub does not own
    what each Wave-1 tier-1 downstream repo owns
    how llm-wiki fits today without pre-deciding #2398
    that worldenergydata role definition is deferred to Wave-2
    that GSD is the workflow control plane used within workspace-hub while workspace-hub is the ecosystem control plane across the portfolio
use the contract as the source text to reconcile README, docs index, business-brain, and repo overview
validate both lexical and structural alignment:
    required and forbidden phrase sets
    required non-goal bullets
    file-specific role expectations
    no contradictory control-plane ownership claims for non-workspace-hub repos
leave AGENTS.md unchanged because the file is already at the 20-line cap
if generic wording in CONTROL_PLANE_CONTRACT.md conflicts with the canonical contract:
    adjust only the generic terminology, not repo-specific ownership content
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` | canonical mission + non-goals + downstream-role contract in a normative location |
| Create | `scripts/validation/check_workspace_hub_mission_contract.py` | deterministic verification for phrase, section, and file-specific structural expectations across the reconciled docs |
| Create | `tests/validation/test_workspace_hub_mission_contract.py` | executable TDD harness for the validator and representative fixtures |
| Modify | `README.md` | align root repo overview with the approved mission contract |
| Modify | `docs/README.md` | align docs index overview with the canonical role language |
| Modify | `docs/BUSINESS_BRAIN.md` | normalize ecosystem-role wording and distinguish workflow control plane vs ecosystem control plane |
| Modify | `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` | align repo-relationship document to the canonical contract |
| Mandatory generic-only modify | `docs/standards/CONTROL_PLANE_CONTRACT.md` | add the generic cross-link/relationship note while remaining free of workspace-hub-specific ownership tables and mission prose |
| Update | `docs/plans/README.md` | add this plan to the plan index |
| Modify | `.planning/quick/issue-1525-followup-ci-validator.md` | refine the follow-up CI issue draft as the validator contract stabilizes |

---

## TDD Test List

Execution order is mandatory:
1. create failing tests in `tests/validation/test_workspace_hub_mission_contract.py`
2. run the narrow test target and confirm failure
3. implement `scripts/validation/check_workspace_hub_mission_contract.py`
4. rerun the narrow target until green
5. update the target docs until the validator passes
6. run the full validation test file and any targeted doc checks again

Primary red/green command during development:
- `uv run pytest tests/validation/test_workspace_hub_mission_contract.py -q`

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_mission_contract_exists` | canonical mission artifact is created | repo docs tree | `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` exists |
| `test_workspace_hub_role_map_is_explicit` | tier-1 role map is locked for this packet | mission contract text | explicit roles for `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`; explicit defer note for `worldenergydata` |
| `test_non_goals_list_is_explicit` | concrete non-goals are locked and not left to prose interpretation | mission contract text | all required non-goal bullets present |
| `test_glossary_terms_are_explicit` | glossary scope is concrete and testable | mission contract text | all required glossary terms present in a glossary section |
| `test_control_plane_distinction_is_explicit` | workflow-vs-ecosystem control plane ambiguity is resolved | `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`, `docs/BUSINESS_BRAIN.md` | `workspace-hub` named as ecosystem control plane and `GSD` named as workflow control plane within workspace-hub |
| `test_llm_wiki_guardrail_phrase_present` | non-preemption of `#2398` is enforced by literal phrase | mission contract text | contains required phrase `repo-boundary architecture remains under evaluation per #2398` |
| `test_required_phrases_present_in_reconciled_docs` | core control-plane terminology is synchronized | `README.md`, `docs/README.md`, `docs/BUSINESS_BRAIN.md`, `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` | required canonical phrases present per validation script |
| `test_forbidden_phrases_absent_in_reconciled_docs` | stale or overcommitting wording is not reintroduced | same docs plus mission contract | forbidden phrases absent per validation script |
| `test_legacy_gsd_phrase_removed` | old wording is migrated, not merely supplemented | `docs/BUSINESS_BRAIN.md` | standalone phrase `GSD is the control plane` absent |
| `test_role_claims_do_not_contradict_contract` | semantic role drift is blocked beyond simple substring checks | reconciled docs + mission contract | no document assigns control-plane ownership to non-`workspace-hub` tier-1 repos or contradicts the canonical role strings |
| `test_control_plane_contract_stays_generic` | global standard stays generic | `docs/standards/CONTROL_PLANE_CONTRACT.md` | still defines entry-point rules only; no workspace-hub-specific role table added |
| `test_cross_links_exist_between_standards` | the two standards docs are navigably related | both standards docs | `CONTROL_PLANE_CONTRACT.md` contains relative link `[Workspace-Hub Mission Contract](WORKSPACE_HUB_MISSION_CONTRACT.md)` plus one relationship sentence, and `WORKSPACE_HUB_MISSION_CONTRACT.md` contains relative link `[Control-Plane Contract](CONTROL_PLANE_CONTRACT.md)` plus one relationship sentence |
| `test_agents_file_unchanged` | AGENTS cap rule is respected | `git rev-parse HEAD:AGENTS.md`, `AGENTS.md` | working-tree blob matches baseline `b4a14216f383b98ebcd70c9bf98ffed26c3eb1bf` and file remains unchanged in this packet |
| `test_plan_index_updated` | plan index is kept in sync | `docs/plans/README.md` | row for `#1525` exists in the `## Plan Index` table with columns `Issue # \| Title / Slug \| Plan File \| Date \| Status \| Complexity \| Notes` all populated |
| `test_ci_followup_issue_draft_exists` | manual-validator drift is not left untracked | `.planning/quick/issue-1525-followup-ci-validator.md` | follow-up issue draft exists and mentions validator path, test file path, pytest command, and intended CI hook |

---

## Acceptance Criteria

- [ ] `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` exists with mission, non-goals, downstream roles, glossary, and llm-wiki guardrails
- [ ] `scripts/validation/check_workspace_hub_mission_contract.py` exists and deterministically checks required phrases, forbidden phrases, required non-goal bullets, glossary terms, validator semantics, and file-specific role expectations across the reconciled docs
- [ ] `tests/validation/test_workspace_hub_mission_contract.py` exists and is the red/green harness run with `uv run pytest tests/validation/test_workspace_hub_mission_contract.py -q`
- [ ] `README.md`, `docs/README.md`, `docs/BUSINESS_BRAIN.md`, and `docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md` pass the validation script with consistent control-plane terminology
- [ ] `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` explicitly distinguishes `workspace-hub` as the ecosystem control plane from `GSD` as the workflow control plane used within workspace-hub
- [ ] The contract explicitly names `workspace-hub` as the control plane
- [ ] The contract explicitly names `digitalmodel`, `assetutilities`, and `aceengineer-website` roles
- [ ] The contract explicitly defers `worldenergydata` role language to the Wave-2 repo mission packet
- [ ] The contract contains the literal neutrality guardrail phrase `repo-boundary architecture remains under evaluation per #2398`
- [ ] The contract includes all four required non-goal bullets and all five required glossary terms listed in the Canonical Terminology Contract section
- [ ] `docs/BUSINESS_BRAIN.md` no longer contains the standalone legacy phrase `GSD is the control plane`
- [ ] `docs/standards/CONTROL_PLANE_CONTRACT.md` remains generic, links to `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`, and does not gain workspace-hub-specific role tables or repo ownership prose
- [ ] `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md` links back to `docs/standards/CONTROL_PLANE_CONTRACT.md`
- [ ] `AGENTS.md` working-tree blob still matches baseline `b4a14216f383b98ebcd70c9bf98ffed26c3eb1bf`
- [ ] `docs/plans/README.md` contains the row for `#1525` in the existing `## Plan Index` schema with all columns populated
- [ ] `.planning/quick/issue-1525-followup-ci-validator.md` exists as a drafted follow-up issue for CI enforcement of the validator, and names the validator path, the test file path, the command `uv run pytest tests/validation/test_workspace_hub_mission_contract.py -q`, and the intended CI hook
- [ ] Review artifacts from waves 1–8 remain recorded in `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (wave 1) | MAJOR | Worldenergydata scope was inconsistent; AGENTS.md edit rule was ambiguous; verification criteria for cross-document consistency were too subjective; risk mitigations and plan-index acceptance were underspecified |
| Codex (wave 1) | MAJOR | TDD/verification strategy was not executable; llm-wiki non-preemption was intent-only rather than literal guardrail text; downstream scope and AGENTS/standards reconciliation rules were underspecified |
| Gemini (wave 1) | APPROVE | Structure was sound, but recommended explicitly locking worldenergydata scope and considering a concise AGENTS mission pointer |
| Claude (wave 2) | MAJOR | Required/forbidden phrase inventory was still missing; AGENTS 20-line cap and contradiction predicate were underspecified; control-plane standard was outside the reconciliation sweep |
| Codex (wave 2) | MAJOR | Validator contract still lacked explicit phrase inventory; review-artifact status needed to distinguish planned outputs from existing evidence; worldenergydata scope needed one unambiguous rule |
| Gemini (wave 2) | APPROVE | Revised draft was feasible and well-scoped, with only minor concern about future CI enforcement |
| Claude (wave 3) | MAJOR | Semantic consistency checks and explicit non-goal content were still too weak; AGENTS handling and artifact-status language remained muddy |
| Codex (wave 3) | MAJOR | Canonical artifact location and standards-scope were wrong; validator still needed stronger structural guarantees |
| Gemini (wave 3) | NO_OUTPUT | No usable review content returned in this wave |
| Claude (wave 4) | MAJOR | Plan still self-reported FAIL, validator semantics were underdefined, legacy GSD phrase removal was not explicit, and defaults for open questions were still too soft |
| Codex (wave 4) | MAJOR | Concrete TDD harness path, glossary validation, and attested AGENTS line-count evidence were still missing or under-specified |
| Gemini (wave 4) | MINOR | Technical approach was sound; only file-action and artifact-evidence mismatches remained |
| Claude (wave 5) | MAJOR | Plan still self-reported FAIL, regex catalog and artifact/audit wiring needed one more tightening, and open questions needed decisions |
| Codex (wave 5) | MAJOR | Artifact waves, AGENTS immutability baseline, and mandatory-vs-optional standards edits were still internally inconsistent |
| Gemini (wave 5) | MINOR | Only artifact-evidence discrepancies remained |
| Claude (wave 6) | MAJOR | Standards edit optionality, final-review status wording, and artifact/test wiring still needed one more alignment pass |
| Codex (wave 6) | MAJOR | Canonical mission-contract scope and mandatory standards cross-link were still slightly inconsistent, though close to ready |
| Gemini (wave 6) | APPROVE | Plan is exceptionally mature and aligned; only whitespace-normalization resilience was suggested |
| Claude (wave 7) | MAJOR | Final remaining blockers were standards-edit optionality, fence semantics, AGENTS blob enforcement, and wave bookkeeping; all now patched in current draft |
| Codex (wave 7) | MAJOR | Evidence/readiness wording and validator/test coverage still needed final tightening; now patched in current draft |
| Gemini (wave 7) | APPROVE | Plan is exceptionally mature and aligned; no substantive blockers remained |
| Claude (wave 8) | MAJOR | Remaining blockers are purely bookkeeping/spec-clarity around wave counts, fence semantics wording, AGENTS baseline, and final status wording |
| Codex (wave 8) | MAJOR | Remaining blockers are evidence/bookkeeping consistency and the AGENTS/blob baseline model, not core scope or architecture |
| Gemini (wave 8) | APPROVE | Plan remains robust and implementation-ready in substance |

**Overall result:** PENDING FINAL DELTA REVIEW — wave-8 bookkeeping blockers have been patched in the current draft and require one last adversarial confirmation before this plan can be treated as approval-ready.

Revisions made based on review:
- Explicitly deferred `worldenergydata` to the Wave-2 packet and removed mixed in-scope/out-of-scope language
- Added verified existence of `docs/reports/2026-04-21-repo-mission-revision-sequence.md`
- Added attested-style line-count evidence for `AGENTS.md` and locked the file to strict no-edit for this packet using HEAD blob `b4a14216f383b98ebcd70c9bf98ffed26c3eb1bf`
- Split artifact map into existing evidence inputs vs planned outputs with status columns
- Enumerated review artifacts through waves 1–7 in both metadata and artifact tracking
- Moved the canonical contract target from `docs/reports/` to the normative path `docs/standards/WORKSPACE_HUB_MISSION_CONTRACT.md`
- Added an explicit Canonical Terminology Contract with required phrases, forbidden phrases, required non-goal bullets, required glossary terms, validator semantics, file-specific expectations, semantic alignment rules, and deterministic plan-index rule
- Added a literal llm-wiki neutrality guardrail phrase tied to `#2398`
- Added explicit distinction between `workspace-hub` as ecosystem control plane and `GSD` as workflow control plane within workspace-hub`
- Added explicit removal of the legacy standalone phrase `GSD is the control plane`
- Added a concrete regex catalog for semantic role-claim validation and extended the semantic contradiction check to the canonical mission contract itself
- Made `docs/standards/CONTROL_PLANE_CONTRACT.md` a mandatory generic-only cross-link touch and preserved its non-repo-specific role
- Added concrete validator semantics for Unicode normalization, paragraph line-wrap normalization, and triple-backtick fenced-code exclusion across required, forbidden, and semantic checks
- Added a concrete executable TDD harness path at `tests/validation/test_workspace_hub_mission_contract.py` and red/green command `uv run pytest tests/validation/test_workspace_hub_mission_contract.py -q`
- Tightened `test_agents_file_unchanged` to compare against the exact HEAD blob baseline `b4a14216f383b98ebcd70c9bf98ffed26c3eb1bf`
- Changed the CI follow-up artifact from Create to Modify because the draft already exists, and strengthened its expected content
- Added precise cross-link requirements between `CONTROL_PLANE_CONTRACT.md` and `WORKSPACE_HUB_MISSION_CONTRACT.md`
- Converted prior open questions into explicit decisions for this packet
- Aligned the plan-index rule with the full 7-column schema used by `docs/plans/README.md`

---

## Risks and Open Questions

- **Risk:** this issue could accidentally duplicate or conflict with the broader architecture intent of `#2398` if the mission contract tries to resolve repo-boundary questions instead of stating current operational reality.
  - **Mitigation:** require the literal neutrality phrase `repo-boundary architecture remains under evaluation per #2398` and forbid any text that declares llm-wiki permanently embedded or spun out.
- **Risk:** if the contract is written too broadly, it could pre-empt downstream repo-specific mission work before those repos are separately reviewed.
  - **Mitigation:** lock this packet to `workspace-hub` plus Wave-1 tier-1 role naming only, and explicitly defer `worldenergydata` to Wave-2.
- **Risk:** `docs/BUSINESS_BRAIN.md` is currently the strongest ecosystem-role artifact; careless edits could weaken rather than clarify the portfolio model.
  - **Mitigation:** treat `docs/BUSINESS_BRAIN.md` as a source to reconcile, not a source to compress; preserve tier structure and role specificity while normalizing wording.
- **Decision:** `AGENTS.md` stays workflow-only in this packet; any mission pointer is deferred to a separate follow-up issue because the file is already at the 20-line cap.
- **Decision:** the CI follow-up issue drafted in `.planning/quick/issue-1525-followup-ci-validator.md` should be filed immediately after plan approval, not deferred to implementation closeout.

---

## Complexity: T2

**T2** — multiple top-level docs must be reconciled into one mission contract, with bounded architecture/ownership decisions but no code implementation or repo-boundary migration work.