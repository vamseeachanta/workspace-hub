# Archived Skill: `canonical-doc-contract-plan-hardening`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/canonical-doc-contract-plan-hardening`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/canonical-doc-contract-plan-hardening`
Consolidation date: 2026-04-29

---

---
name: canonical-doc-contract-plan-hardening
description: Harden a documentation or mission-contract plan so adversarial reviewers cannot reject it for vague validator contracts, wrong artifact authority, or semantic drift gaps.
version: 1.0.1
category: workspace-hub-learned
tags: [planning, adversarial-review, documentation, governance, mission-contract]
---

# Canonical doc-contract plan hardening

Use when drafting or revising a plan for a canonical documentation contract: repo mission, role map, glossary, or cross-doc wording reconciliation.

## Common reviewer failures this prevents

1. Validator contract is too vague
- Reviewers reject plans that say "add a validation script" without listing exact required phrases, forbidden phrases, section expectations, or file-specific rules.

2. Canonical artifact stored in the wrong namespace
- Do not put a normative long-lived contract under a reporting/history path unless that repo explicitly treats the path as authoritative.

3. Phrase-only validation is too weak
- Required/forbidden strings alone are insufficient. Add semantic role-claim checks and file-specific expectations.

4. Artifact status is muddy
- Split artifacts into:
  - existing evidence inputs
  - planned outputs
- Do not mix prior review artifacts with future deliverables in the same ambiguous list.

5. Cross-document terminology drift remains unresolved
- Explicitly distinguish concepts that share similar words. Example:
  - ecosystem control plane
  - workflow control plane inside that ecosystem

## Required hardening pattern

### 1. Put the canonical artifact in a normative location

Prefer a path under a durable standards/contracts namespace or another clearly authoritative docs path.
Avoid using report/history namespaces for the canonical artifact unless the repo already treats them as authoritative.

### 2. Add a "Canonical Terminology Contract" section to the plan

This section should include all of the following:
- exact required phrases for the canonical contract doc
- exact forbidden phrases
- required non-goal bullets
- required glossary terms when the deliverable claims to include a glossary
- file-specific expectations for each reconciled document
- explicit validator semantics:
  - case sensitivity
  - line-ending normalization
  - whitespace handling
  - whether checks are whole-line, substring, or regex-based
- exact plan-index rule if the plan updates a local index table, including full table schema when relevant

Also add explicit migration checks for legacy wording that must be removed, not merely supplemented. Example: if an existing doc says `GSD is the control plane`, add that exact legacy phrase to the forbidden list once the new distinction (`workspace-hub` as ecosystem control plane vs `GSD` as workflow control plane) is introduced.

### 3. Split lexical and semantic checks

Your TDD/validation plan should include both:

- lexical checks
  - phrase presence/absence
  - required section headers
  - required bullets
  - glossary terms when claimed in the deliverable

- semantic checks
  - no non-canonical repo gets assigned the canonical role
  - role statements in secondary docs do not contradict the main contract
  - generic standards docs stay generic and do not absorb repo-specific ownership prose
  - legacy role phrasing is removed where required, not merely coexisting beside the new phrasing
  - related standards/contracts cross-link to each other when the plan introduces two nearby authoritative docs

### 4. Lock constrained entrypoint files explicitly

If a root workflow-contract file is constrained by line count or by role, measure that in Resource Intelligence and make the plan explicit:
- unchanged in this packet
- or changed only under a deterministic rule

Also capture a deterministic baseline when immutability matters:
- current line count (for example via `wc -l`)
- current git blob SHA when possible (`git rev-parse HEAD:path/to/file`)

Use that baseline in the TDD plan so a later `file unchanged` test has a concrete source of truth rather than a vague before/after comparison.

Do not leave edits to a constrained file as an "optional if needed" judgment call.

### 5. Separate existing review evidence from future outputs

Artifact Map should usually have two subsections:

#### Existing evidence inputs
- this plan
- steering docs
- standards docs
- already generated review artifacts

#### Planned outputs
- canonical contract doc
- validation script
- reconciled target docs
- follow-up issue drafts

### 6. If manual validation would rot, draft the CI follow-up now

If the current issue is only for creating the contract plus validator, add a follow-up issue draft for CI enforcement so reviewers can see drift prevention is queued.

Be explicit about whether the follow-up draft is being created or updated. If a draft file already exists, treat it as a modify action, not create, and make the acceptance criterion require concrete contents:
- validator script path
- test file path
- exact test command
- intended CI hook/job

### 7. Review-wave hygiene for iterative plan hardening

When a plan goes through multiple adversarial-review waves:
- keep the review-artifact header in sync with the actual generated files
- keep the artifact map explicit about which waves already exist versus which outputs belong to eventual implementation
- do not leave the plan self-reporting `FAIL` once you have patched the cited blockers; change the summary to something like `pending final delta review` and immediately rerun review
- convert lingering open questions into explicit decisions or explicit deferred follow-up items before asking for approval
- if reviewers keep objecting to semantics rather than mechanism, add the exact regexes, section shapes, or file-specific predicates to the plan itself

### 8. Standards-vs-mission boundary rule

If a new canonical mission contract sits near an existing generic standard:
- keep the mission contract in a normative location
- keep the generic standard generic
- if cross-links are required, specify the exact relative markdown links and the relationship note expected in each file
- do not make a generic cross-repo standard carry repo-specific ownership tables just to satisfy a validator
- most importantly: do not leave the standard's edit status ambiguous. If tests/acceptance require a cross-link or wording change, mark the file as a mandatory generic-only modify everywhere in the plan. Do not call it optional in one section and required in another.

### 9. Validator semantics must be concrete, not inferred

When reviewers keep attacking validator ambiguity, add the exact semantics to the plan itself:
- how fenced code blocks are detected (for example, triple-backtick fences only)
- whether indented code blocks are exempt or not
- whether checks exclude fenced content consistently across required-phrase, forbidden-phrase, and semantic-regex rules
- whether matching is case-sensitive
- whether line endings are normalized
- whether Unicode is normalized (for example NFC)
- whether paragraph line-wraps are collapsed to spaces before matching
- whether a forbidden rule is substring-based or a whole-line regex

If a legacy phrase is being retired, prefer an explicit standalone regex over a vague substring ban.

### 10. Immutable file checks need a reproducible baseline

If the plan says a constrained file must remain unchanged, the test should not rely on a vague before/after claim.
Capture and use a deterministic baseline such as:
- `git rev-parse HEAD:path/to/file` for a blob SHA
- current line count via `wc -l`

Then make the test assert the working-tree blob still matches the recorded SHA when immutability is part of the contract.

### 11. Keep review-wave bookkeeping synchronized

In multi-wave hardening loops:
- if review artifacts are listed in plan metadata, keep the list synchronized with every actual review wave you cite in the summary
- if the Adversarial Review Summary mentions wave N, the artifact map and metadata should also reflect wave N
- if you patch blockers from the latest wave, change the summary status from outright FAIL to a pending-final-delta state only after you have actually made the patches and immediately rerun review
- do not let the plan's self-reported status lag behind the current draft

### 12. Align prose rules with tests verbatim

Common reviewer complaint: the prose says one thing and the test row says another.
Before re-review, cross-check all of these for exact agreement:
- Files to Change
- Artifact Map
- Canonical Terminology Contract
- TDD Test List
- Acceptance Criteria
- Adversarial Review Summary revision notes

Typical drift to catch:
- optional vs mandatory edits
- partial vs full plan-index schema
- create vs modify on already-existing follow-up drafts
- semantic checks applying to reconciled docs but not the canonical contract itself

### 13. Reuse established registry namespaces instead of inventing new ones

For documentation/mission plans that introduce machine-readable inventories, evidence manifests, or routing registries, first inspect the repo's existing registry surfaces and route new files there.

Common workspace-hub pattern:
- durable prose contract: `docs/...`
- machine-readable document/index/mission registry: `data/document-index/...`

Avoid adding a new namespace such as `docs/registry/` unless the repo already treats it as canonical or the plan explicitly creates that architecture with evidence and review scope. Reviewers will correctly flag new registry roots as architectural drift when established registry homes exist.

### 14. Clean legacy authority families, not just one cited file

When a plan deprecates or replaces a legacy authority path, search and handle the whole linked family, not only the first stale link named in the issue.

Example pattern:
- if `docs/README.md` links to `.agent-os/product/mission.md`, also check adjacent `.agent-os/product/tech-stack.md`, `roadmap.md`, and `decisions.md`
- if the entire legacy namespace is non-authoritative, the plan should remove or clearly mark every active-looking link in that namespace
- tests should assert the new canonical artifact is discoverable and that legacy links are absent or confined to an explicit legacy/deprecated section

### 15. Plan-index rows should be create-or-update exactly once

If a plan updates a local plan index, do not assume the row exists unless resource intelligence proves it in the target checkout. Write the contract as:
- create the row if absent
- update the row if present
- assert exactly one row exists after the edit

This avoids false MAJOR findings from reviewers running against a checkout where the row is absent while still preventing duplicate rows.

## Template additions that help approval

Include concrete file-specific expectations like:
- a given top-level doc must contain the canonical role statement
- a strategy/brain doc must preserve its stronger structure while normalizing wording
- a generic standard may only receive generic terminology edits and must not gain repo-specific role tables

Include concrete non-goals like:
- repo does not own engineering computations
- repo does not own shared utility layer
- repo does not own GTM/public website
- repo does not resolve an open architecture decision tracked in another issue

## Example validation dimensions

For a mission/control-plane contract validator, check all of:
- required phrases in canonical contract
- forbidden phrases across reconciled docs
- required non-goal bullets in canonical contract
- file-specific role statements
- semantic no-contradiction checks for named repos
- generic standard remains generic
- local plan index row present with expected schema
- follow-up CI issue draft exists if validator is not yet enforced automatically

## Practical rule

If a reviewer says "the mechanism is specified but the substance is not," add more explicit content to the plan itself rather than only improving the future validator script.

## Outcome to aim for

A plan becomes approval-ready when:
- canonical location is correct
- content contract is explicit in the plan
- validator behavior is mechanically derived from that contract
- semantic contradictions are blocked, not just missing phrases
- artifact status is unambiguous
- any deferred enforcement work is captured in a follow-up issue draft
