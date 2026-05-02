# Archived Skill: `roadmap-issue-reopen-retarget-balance`

Original path: `/home/vamsee/.hermes/skills/coordination/roadmap-issue-reopen-retarget-balance`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/roadmap-issue-reopen-retarget-balance`
Consolidation date: 2026-04-29

---

---
name: roadmap-issue-reopen-retarget-balance
description: Reopen existing roadmap anchors, close replacement epics, retarget new child issues, and add sequencing/de-dup comments so GitHub roadmap work preserves continuity and execution quality.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, roadmap, issue-management, sequencing, de-duplication]
    related_skills: [github-issues, github-issue-tracker]
---

# Roadmap Issue Reopen / Retarget Balance

Use when a new analysis or planning wave initially creates fresh GitHub issues, but the better structure is to preserve continuity by reopening an existing roadmap issue and retargeting new work under it.

## When to use
- A closed roadmap/epic already exists for the same domain
- New analysis updates the roadmap rather than replacing it
- New child issues are valid, but the umbrella/anchor should be the original roadmap
- There is a risk of fragmented governance across parallel roadmap issues

## Goal
Keep one canonical roadmap anchor while still allowing genuinely new scoped execution issues.

## Recommended pattern
1. Audit existing roadmap and sprint issues first.
   - `gh issue view <id>` for known roadmap issues
   - `gh issue list --state all --search "<domain keywords> roadmap OR sprint OR capability roadmap"`
2. Reopen the existing roadmap anchor if it is the right long-lived parent.
   - `gh issue reopen <roadmap_id>`
3. Comment on the reopened roadmap with:
   - why it was reopened
   - updated analysis focus
   - active existing issue clusters
   - delivered foundations that should no longer be treated as gaps
   - links to the latest roadmap artifact/doc
4. Keep existing active issues in place if they already represent real workstreams.
   Typical buckets:
   - proof/validation
   - hardening/repeatability
   - breadth expansion
   - corpus/input expansion
   - downstream scaling
5. Create new issues only for genuinely missing scoped work.
   Good examples:
   - flagship family validation cases
   - new benchmark-specific promotion tasks
   - narrowly bounded missing proof artifacts
6. If a replacement epic was created prematurely:
   - comment that work is moving back under the reopened roadmap
   - close the replacement epic
   - keep its child issues open if they are still valid
7. Retarget new child issues by editing their bodies.
   Replace parent references like `#<replacement_epic>` with `#<reopened_roadmap>`.
8. Add roadmap-link comments to the major existing issues so future agents see the intended structure.
   Include:
   - role of the issue in the sequence
   - roadmap anchor issue number
   - roadmap document path
   - whether the issue is the canonical anchor for that lane or just a narrow sprint/child tracker
9. Add sequencing comments to the new child issues.
   Make explicit:
   - what phase they belong to
   - which proof issues should land before them
   - what later breadth/scaling issues they should precede
10. Add at least one compact roadmap-governance note back on the reopened anchor.
   Recommended contents:
   - status legend (foundation delivered / proof / hardening / breadth / corpus / scaling)
   - phase map showing the intended execution order
   - compact topology summary naming the single roadmap anchor, the canonical hardening issue, the proof lane, and the bounded new child-wave
11. If two open issues overlap, first do an evidence-based scope comparison instead of immediately forcing closure.
   Compare line by line:
   - deliverables
   - unique scope items
   - parent/anchor role
   - current repo state
   Then comment with a de-dup/re-scope recommendation.
   Preferred wording:
   - compare unique remaining scope
   - if none remains, close as duplicate/superseded
   - otherwise rewrite as a narrow child/sub-scope of the canonical issue
12. When a proof issue is the first execution gate for later child issues, post execution-ready acceptance criteria on that issue.
   Include:
   - fixture/artifact contract
   - live/licensed validation requirement
   - semantic-diff or claim-boundary gate
   - regression/skip behavior on non-licensed machines
   - whether a related issue is a child/follow-on or a peer proof issue
13. Add a reusable proof-template checklist on the reopened roadmap anchor for downstream child issues.
   This should standardize:
   - canonical fixture identification
   - native generation path
   - required evidence artifacts
   - allowed vs blocking difference classes
   - documentation update rule
   - closure rule (do not close on mere generation/template existence)
14. After the proof-standard issue is tightened, add concrete implementation breakdown comments to:
   - the main proof issue
   - its child/follow-on issue
   The breakdown should name likely fixture files, helper/test file targets, artifact filenames, and an execution order so later work becomes mechanical.
15. If you close a duplicate/subsumed issue, add a compact governance-topology note back on the roadmap anchor summarizing the resulting stable structure.
   Recommended contents:
   - single roadmap anchor
   - proof lane
   - hardening lane
   - bounded new child-wave
   - duplicates removed
16. After the proof-standard issue is tightened, bridge governance into implementation scaffolding before launching the family-wave.
   Recommended pattern for fixture/report/snapshot proof work:
   - create a fixture-artifact directory with a README describing provenance, regeneration, review rules, and snapshot scope
   - commit a stable metadata JSON baseline first
   - add helper modules for loading metadata and normalizing snapshots
   - add fixture-backed integration/snapshot test skeletons in the target test package
   - prefer generating the first real snapshot baseline from deterministic code in the same execution pass instead of leaving a placeholder baseline committed long-term
   This keeps the proof-standard issue execution-ready and makes later family-specific issues mechanical rather than re-designed from scratch.
17. Immediately run the narrow targeted tests for the new scaffold and expect one or two structural fixes before it passes.
   Common real-world fixes discovered in this pattern:
   - pytest collection may fail on relative imports inside new test modules; prefer explicit package imports such as `from tests.solvers.orcaflex.reporting...` when the test package is not guaranteed to be imported as a package
   - fixture helper path calculations are easy to get wrong; verify the actual resolved path to `tests/fixtures/reporting/...` and adjust `Path(__file__).resolve().parents[...]` based on the real package depth
   - once a deterministic render path exists, regenerate the snapshot baseline from live code before finalizing; do not keep an outdated hand-written placeholder snapshot if the real render can be produced now
   - keep report-generation dates or similar fields deterministic in helpers if the snapshot depends on them
18. After the proof-standard lane passes, apply the same artifact/test pattern to the first flagship family issue before broadening further.
   Recommended family-proof pattern:
   - identify one authoritative canonical spec, one native monolithic reference, and one generated modular reference set
   - when multiple candidate fixtures exist, prefer a model-library case that already has the full trio (canonical spec + monolithic native + modular generated references) over a bare template-only case; this gives a stronger bounded proof path and cleaner issue evidence
   - derive a bounded family-specific metadata JSON under `tests/fixtures/reporting/`
   - add family-specific fixture integration and snapshot tests using the shared helper modules rather than creating a parallel testing architecture
   - prefer the highest-leverage flagship case first (e.g. a generic-track FPSO/turret model) so the proof pattern is exercised on the most failure-prone family before rolling out to simpler follow-ons
   - once the first family path works, generalize helper modules to support named fixtures (`generate_fixture_report`, `load_fixture_metadata`, fixture-specific path helpers) instead of cloning one-off helper code per family
   - generate the family snapshot baseline from live deterministic code, then run one focused pytest command that includes both the original proof-standard tests and the new family-specific tests
19. Verify final state.
   - roadmap issue open
   - replacement epic closed if superseded
   - new child issues open and retargeted
   - existing major issues linked back to the roadmap
   - duplicates either closed or explicitly narrowed
   - proof-standard and reusable checklist comments posted where needed

## Output structure to aim for
- Reopened roadmap = canonical sequencing anchor
- Existing issues = preserved where they already describe real active tracks
- New issues = only truly missing scoped analyses/features
- Sequencing comments = make proof -> hardening -> breadth -> scaling explicit

## Pitfalls
- Do not leave two competing roadmap umbrellas open for the same domain
- Do not recreate issues that already exist just to match a new plan artifact
- Do not bury new family-specific validation work inside a broad proof issue if it deserves a bounded child issue
- Do not close overlapping issues without leaving a rationale comment and redirect target
- Do not rely on issue bodies alone; add comments that explain the new sequencing and parentage

## Minimal checklist
- [ ] Existing roadmap audited
- [ ] Best anchor reopened if needed
- [ ] Replacement epic closed if superseded
- [ ] New child issues retargeted to reopened anchor
- [ ] Existing core issues linked back to roadmap
- [ ] Sequencing/de-dup comments added
- [ ] Final state verified
