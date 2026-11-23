# Claude agent-team prompt: #2104 implementation

Use this prompt as a single self-contained handoff to Claude Code for implementation.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Documentation Implementer
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Execution authorization:
- Issue `#2104` has been explicitly user-approved for execution.
- GitHub label `status:plan-approved` is present.
- Local marker exists: `.planning/plan-approved/2104.md`

Primary issue:
- `#2104` https://github.com/vamseeachanta/workspace-hub/issues/2104

Approved plan:
- `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`

Review artifacts:
- `scripts/review/results/2026-04-11-plan-2104-claude.md`
- `scripts/review/results/2026-04-11-plan-2104-final.md`

Authoritative supporting docs to follow, not redefine:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `docs/standards/CONTROL_PLANE_CONTRACT.md`

Critical safety constraints:
- The repo has many unrelated dirty/untracked files.
- Do NOT touch unrelated files.
- Stage and commit ONLY the files explicitly owned by this issue.
- Never use `git add .` or broad globs.
- If you detect unavoidable conflict with unrelated dirty files, stop and report clearly.

Owned implementation paths for #2104 only:
- `docs/README.md`
- `docs/document-intelligence/README.md`
- `knowledge/wikis/engineering/CLAUDE.md`
- `knowledge/wikis/marine-engineering/CLAUDE.md`
- `knowledge/wikis/maritime-law/CLAUDE.md`
- `knowledge/wikis/naval-architecture/CLAUDE.md`
- `knowledge/wikis/personal/CLAUDE.md`
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `docs/document-intelligence/holistic-resource-intelligence.md`
- `docs/document-intelligence/session-handoff-terminal5-2026-04-02.md`
- `docs/document-intelligence/session-handoff-terminal5-2026-04-02-execution.md`
- `docs/handoffs/` (destination only for moved handoff files)

Read-only context paths:
- `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `scripts/review/results/2026-04-11-plan-2104-*.md`

Forbidden paths:
- `data/**`
- `scripts/**`
- `tests/**`
- `.claude/**`
- `.codex/**`
- `config/**`
- any unrelated dirty/untracked file outside the owned paths above

Success condition:
Implement the approved #2104 plan fully and safely.

Required implementation outcomes:
1. Add a concise "Knowledge & Intelligence Ecosystem" section to `docs/README.md`
   - keep it compact (<=15 lines of section body, excluding markdown table separators if used)
   - link to the intelligence landing page, wiki layer, registry reference, design-code registry, and weekly review template
2. Create `docs/document-intelligence/README.md`
   - include reading order for newcomers
   - group links into architecture, knowledge assets, registries/provenance, maps/inventories
   - include back-link to `docs/README.md`
   - clearly label normative vs operational docs where appropriate
3. Add upward architecture links to all 5 wiki `CLAUDE.md` files
   - reference the parent operating model
   - do not otherwise rewrite the files unnecessarily
4. Update `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`
   - add an intelligence ecosystem section mentioning llm-wikis and document-intelligence pipeline
5. Update `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
   - add entry-point validation checks aligned with the approved plan and #2096 checklist
6. Move the two transient handoff files out of `docs/document-intelligence/` into `docs/handoffs/`
   - preserve filenames
7. Add a superseded-by note to `docs/document-intelligence/holistic-resource-intelligence.md`
   - do not destroy useful historical context; add a clear note that #2205 now governs parent architecture
8. Verify all new/updated links resolve
9. Commit only the owned files for this issue
10. Post a GitHub implementation summary comment on #2104

Implementation guidance:
- Prefer minimal, high-signal edits.
- Do not over-redesign docs.
- Use relative links, not absolute paths.
- Respect the plan's <=3-hop discoverability goal.
- Do not invent new provenance facts or metrics.

Required verification before commit:
- confirm `docs/document-intelligence/README.md` exists and is non-empty
- confirm all 5 wiki `CLAUDE.md` files contain the parent operating-model cross-reference
- confirm `docs/README.md` contains the new section
- confirm weekly review template includes entry-point validation checks
- confirm no `session-handoff-*` files remain under `docs/document-intelligence/`
- confirm moved handoff files exist under `docs/handoffs/`
- confirm all changed markdown links point to existing files

Git discipline:
- Stage only these owned files explicitly by path.
- Commit message:
  - `docs(intelligence): add canonical entry points for ecosystem knowledge (#2104)`
- After commit, push to `origin main`.

GitHub closeout:
- Post a concise comment on #2104 summarizing:
  - files changed
  - verification performed
  - any minor deviations from the plan
- If everything is complete and verified, close the issue.

Final return format in the Claude session:
1. What changed
2. Verification performed
3. Exact files committed
4. GitHub comment URL
5. Whether issue was closed
6. Residual risks or follow-ups
