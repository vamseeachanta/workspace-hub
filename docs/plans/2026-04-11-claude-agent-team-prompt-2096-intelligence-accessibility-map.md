# Claude agent-team prompt: #2096 intelligence accessibility map

Use this prompt as a single self-contained handoff to Claude Code for the next execution step after #2209.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Information Architect
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Repo/workflow constraints:
- This repo is plan-gated. Treat `#2096` as execution-ready only if its current GitHub label state still permits execution. Verify live before acting.
- Parent operating model from `#2205` is authoritative.
- Child contracts from `#2207` and `#2209` now exist locally and should be consumed, not redefined.
- This run is for `#2096` only.
- Stay within the approved scope for `#2096`: create the intelligence accessibility map covering llm-wikis, resource intelligence, and document intelligence so weekly review `#2089` can verify discoverability and usability.
- Do NOT implement registry schemas (`#2136`), canonical entry-point design details (`#2104`), workflow retrieval policy (`#2208`), conformance tooling (`#2206`), or `/mnt/ace/acma-codes` integration (`#2216`).
- Do NOT redefine the parent pyramid/layer model from `#2205`.

Primary issue:
- `#2096` https://github.com/vamseeachanta/workspace-hub/issues/2096

Parent / related issues:
- Parent/downstream review context: `#2089`
- Parent operating model: `#2205`
- Sibling contracts already present locally: `#2207`, `#2209`
- Adjacent but out-of-scope for this run: `#2104`, `#2136`, `#2208`, `#2206`, `#2216`

Authoritative artifacts to consume:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`

Relevant context to inspect:
- `knowledge/wikis/**` (durable knowledge surfaces)
- `docs/document-intelligence/**`
- `docs/assessments/document-intelligence-audit.md`
- `docs/README.md`
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`
- `docs/standards/CONTROL_PLANE_CONTRACT.md`
- `docs/modules/ai-native/workspace-hub-structure.md`
- `docs/governance/SESSION-GOVERNANCE.md`
- any existing docs that act as canonical entry points, inventories, indexes, or accessibility surfaces

Allowed write paths for this run:
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `scripts/review/results/2026-04-11-issue-2096-claude-review.md`
- `scripts/review/results/2026-04-11-issue-2096-final-review.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (cross-links only, if truly needed)

Read-only paths:
- `knowledge/wikis/**`
- `docs/**`
- `scripts/review/results/**`
- GitHub issue threads for the related issues above

Forbidden paths:
- `.claude/**`
- `.codex/**`
- `config/**`
- `data/**`
- `scripts/data/**`
- `scripts/knowledge/**`
- `tests/**`
- any unrelated dirty/untracked files already present in the worktree
- issue bodies/comments for issues other than `#2096` unless a minimal backlink/reference is truly necessary

Important git safety rule:
- First inspect `git status --short`.
- The repo currently has unrelated dirty and untracked files.
- Do NOT modify anything outside the allowed write paths above.
- If the worktree is too dirty to proceed safely even within those paths, stop and report that explicitly in the final summary and GitHub comment.

Success condition:
By the end of this run, the repo should contain a finished accessibility-map document for `#2096` that:
- inventories the primary intelligence assets and their canonical locations
- identifies how agents/humans should discover them
- identifies broken or weak accessibility/discoverability patterns
- defines concrete weekly accessibility checks that `#2089` can use
- distinguishes existing assets from future entry-point/registry work owned by `#2104` and `#2136`
- stays fully consistent with `#2205`, `#2207`, and `#2209`
- has been adversarially reviewed within the run
- is summarized back to GitHub issue `#2096`

Required deliverable document structure:
Create or update:
- `docs/document-intelligence/intelligence-accessibility-map.md`

The document must include these sections:
1. Purpose and scope
2. Relationship to parent operating model (`#2205`)
3. Relationship to sibling contracts (`#2207`, `#2209`)
4. Asset classes to map
   - llm-wikis
   - resource/document intelligence docs
   - registries/ledgers/manifests
   - weekly review surfaces
   - execution/planning surfaces that consume intelligence
5. Accessibility-map table
   - asset
   - layer
   - canonical location/path
   - current entry point(s)
   - intended users (human/agent/both)
   - machine/access assumptions
   - discoverability risks/gaps
6. Current broken/weak patterns
   - path drift
   - machine-local only knowledge
   - missing backlinks
   - ambiguous canonical locations
   - trapped intelligence in transient artifacts
7. Weekly accessibility checklist for `#2089`
8. Recommendations for canonical access paths
   - but do NOT fully design `#2104`
9. Boundaries vs `#2104` and `#2136`
10. Likely implementation surfaces (docs/workflow surfaces only)
11. Open questions / residual risks
12. Recommended follow-on sequence

Policy/content requirements:
- Be concrete: list real assets and paths from the repo.
- Explicitly classify whether an asset is already discoverable, partially discoverable, or hard to discover.
- Distinguish between:
  - the asset itself
  - the current entry point to the asset
  - the future ideal canonical access path
- Keep `#2096` as the inventory/map layer, not the final canonical entry-point design (`#2104`) and not the machine-readable registry implementation (`#2136`).
- Include weekly-review checklist items that are directly usable by `#2089`.

Execution steps:

STEP 1 — Read and ground
- Read issue `#2096` live from GitHub.
- Read the parent operating model and sibling contracts.
- Read the weekly review doc and key discoverability/control-plane docs.
- Inspect the actual repo surfaces that function as intelligence assets and entry points.
- Build an inventory of the most important assets first; do not try to exhaustively catalog the entire repo if that dilutes usefulness.

STEP 2 — Draft the accessibility map
- Write the map as a normative/operational doc, not a vague note.
- Use real file paths and artifact classes.
- Focus on where intelligence is, how it is found today, what is weak/broken, and what `#2089` should check weekly.
- Keep recommendations specific but avoid stepping into the full design scope of `#2104` or `#2136`.

STEP 3 — Internal adversarial review
- Create `scripts/review/results/2026-04-11-issue-2096-claude-review.md`.
- Review for:
  - consistency with `#2205`, `#2207`, `#2209`
  - concrete usefulness for humans and agents
  - clear boundary with `#2104` and `#2136`
  - completeness of weekly accessibility checks
  - whether the map identifies real discoverability gaps rather than generic complaints
- If major issues are found, revise the doc before finalizing.

STEP 4 — Final integrator pass
- Create `scripts/review/results/2026-04-11-issue-2096-final-review.md` with final verdict and residual risks.
- Ensure the map is internally consistent and scoped correctly.
- If useful and minimal, add a cross-link from the parent operating-model doc to the new accessibility-map doc, but only if this stays inside allowed write paths.

STEP 5 — GitHub update
- Post a concise summary comment on `#2096` including:
  - document path
  - key asset categories mapped
  - biggest discoverability gaps found
  - weekly checklist summary for `#2089`
  - boundaries preserved vs `#2104` and `#2136`
  - residual risks/open questions
- Do not change labels unless absolutely required by repo policy and clearly justified.

Output requirements for the Claude run:
1. What changed
2. Final review verdict
3. Exact files changed
4. Exact GitHub comment posted
5. Residual blockers or risks

Quality bar:
- Prefer a high-signal operational map over exhaustive clutter.
- Use real repo paths and artifact examples.
- Be explicit about discoverability weaknesses.
- Do not drift into implementing the canonical entry-point system or accessibility registry.
- Produce something that both operators and future agents can use directly.
