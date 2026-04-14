You are executing approved GitHub issues #2242 and #2243 in the workspace-hub repo.

Repository and branch context
- Repo: /mnt/local-analysis/worktrees/workspace-hub-issue-2242-2243
- Issues: #2242 feat(llm-wiki): prioritize external-source queue for token-efficient wiki strengthening
- Issues: #2243 chore(llm-wiki): define token-efficient staged batch packs for broad wiki strengthening
- Related umbrella: #2241
- Architecture constraints: #2205 operating model, #2208 retrieval contract, #2207 provenance/reuse contract, #2209 durable/transient boundary.

Hard requirements
1. Stay inside the approved scope of #2242 and #2243.
2. Use existing registries/reports/docs rather than brute-force rescanning large corpora.
3. Do not touch unrelated provider-routing/config files or other dirty surfaces from main checkout.
4. If you need to post GitHub progress, do it concisely on #2242, #2243, and #2241 only.
5. Work from this clean worktree only.
6. Before coding/writing, verify whether the deliverables already exist; if already done, comment with evidence instead of duplicating work.
7. Keep changes bounded and commit only issue-owned files.

Owned paths
- data/document-index/**
- docs/document-intelligence/**
- docs/reports/**
- docs/README.md only if strictly needed for discoverability

Read-only paths
- knowledge/wikis/**
- docs/handoffs/**
- docs/plans/**
- scripts/**
- state/**
- notes/**

Forbidden paths
- config/**
- tests/**
- .claude/**
- other repo worktrees/checkouts
- package/dependency/CI/tooling files unless absolutely required (if required, stop and explain in issue comment rather than silently editing)

Target deliverables
For #2242
- Create a prioritized external-source queue artifact grounded in existing registries/reports.
- Classify source families by promotion strategy (metadata-first, summary-backed, raw extraction needed, registry-only for now).
- Map each source family to target wiki domains and related execution issues.
- Include an explicit do-not-process-yet list for low-ROI sources.

For #2243
- Create reusable staged batch-pack documentation/templates derived from the #2242 queue.
- Define at least 3 source-family execution slices with owned paths, forbidden paths, verification expectations, and return format.
- Mark which slices are suitable for overnight unattended execution.

Suggested artifact pattern (adjust if repo conventions imply a better nearby path)
- data/document-index/llm-wiki-external-source-priority-queue.yaml
- docs/reports/llm-wiki-external-source-priority-queue.md
- docs/reports/llm-wiki-staged-batch-packs.md

Execution process
1. Inspect #2242/#2243/#2241 issue bodies and comments.
2. Inspect existing registries and intelligence docs that already cover source pools, accessibility, and operating model.
3. Check whether an equivalent queue/batch-pack artifact already exists.
4. If not already done, write the bounded artifacts.
5. Validate by parsing YAML (if created), checking internal consistency against source docs, and confirming references/issue links are real.
6. Commit with a message that references both issues if both are implemented.
7. Report exact changed files, validation commands, and commit hash.

Validation minimums
- YAML parses successfully if you create YAML.
- Any markdown tables/issue references should be checked against real issue numbers and existing paths.
- Run git status before commit to ensure only owned files are staged.

Return format at the end
- What was already present vs newly created
- Exact files changed
- Validation commands/results
- Commit hash
- Any residual risks/follow-up notes for #2241 umbrella
