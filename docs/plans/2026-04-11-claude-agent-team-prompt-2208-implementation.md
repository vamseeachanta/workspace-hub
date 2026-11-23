# Claude agent-team prompt: #2208 implementation

Use this prompt as a single self-contained handoff to Claude Code for implementation.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Workflow/Docs Implementer
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Execution authorization:
- Issue `#2208` has been explicitly user-approved for execution.
- GitHub label `status:plan-approved` is present.
- Local marker exists: `.planning/plan-approved/2208.md`

Primary issue:
- `#2208` https://github.com/vamseeachanta/workspace-hub/issues/2208

Approved plan:
- `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md`

Review artifacts:
- `scripts/review/results/2026-04-11-plan-2208-claude.md`
- `scripts/review/results/2026-04-11-plan-2208-final.md`

Authoritative supporting docs to follow, not redefine:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`
- `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md`
- `docs/plans/_template-issue-plan.md`
- `docs/plans/README.md`
- `docs/standards/engineering-issue-workflow-skill.md`

Critical safety constraints:
- The repo has many unrelated dirty/untracked files.
- Do NOT touch unrelated files.
- Stage and commit ONLY the files explicitly owned by this issue.
- Never use `git add .` or broad globs.
- If you detect unavoidable conflict with unrelated dirty files, stop and report clearly.

Owned implementation paths for #2208 only:
- `docs/plans/_template-issue-plan.md`
- `docs/plans/README.md`
- `docs/standards/engineering-issue-workflow-skill.md`

Optional owned path only if absolutely necessary and minimal:
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`

Read-only context paths:
- `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`
- `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md`
- `scripts/review/results/2026-04-11-plan-2208-*.md`

Forbidden paths:
- `scripts/**`
- `tests/**`
- `data/**`
- `knowledge/**`
- `.claude/**`
- `.codex/**`
- `config/**`
- any unrelated dirty/untracked file outside the owned paths above

Success condition:
Implement the approved #2208 plan fully and safely.

Required implementation outcomes:
1. Tighten `docs/plans/_template-issue-plan.md`
   - strengthen Resource Intelligence Summary into a clearer evidence contract
   - ensure required sub-sections align with the approved retrieval contract
   - require specific evidence, not vague prose
2. Update `docs/plans/README.md`
   - document the retrieval contract by workflow stage at a practical level
   - define minimum retrieval expectations and evidence placement
   - keep the document coherent and concise
3. Update `docs/standards/engineering-issue-workflow-skill.md`
   - align it with the new retrieval contract
   - make retrieval adequacy expectations explicit for engineering-critical issues
   - avoid redefining broader parent architecture
4. If truly necessary and minimal, update the weekly review template with a very small note on retrieval compliance metrics; otherwise leave it untouched
5. Verify that the updated docs are internally consistent and mutually aligned
6. Commit only the owned files for this issue
7. Post a GitHub implementation summary comment on #2208
8. Close the issue if fully complete and verified

Implementation guidance:
- Keep this as a docs/workflow implementation, not a tooling implementation.
- Do not add hooks, scripts, or linters in this issue.
- Be explicit about evidence placement in plans/reviews/GitHub comments.
- Preserve current workflow structure where possible; tighten rather than rewrite wholesale.
- Keep boundaries with #2104 and #2136 explicit: this issue defines the consumption contract, not navigation or registry schema.

Required verification before commit:
- confirm the plan template now clearly requires retrieval evidence sections
- confirm `docs/plans/README.md` reflects the retrieval contract and minimum source expectations
- confirm `engineering-issue-workflow-skill.md` aligns with the new retrieval rules
- confirm no forbidden paths were modified
- manually cross-check that the three docs do not contradict each other on minimum retrieval bundles, evidence placement, or issue-class logic

Git discipline:
- Stage only the owned paths explicitly by path.
- Commit message:
  - `docs(workflow): add intelligence retrieval contract to issue planning workflow (#2208)`
- After commit, push to `origin main`.

GitHub closeout:
- Post a concise comment on #2208 summarizing:
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
