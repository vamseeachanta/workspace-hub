# Weekly cadence issue wave pattern

Use this reference when the user asks to keep `llm-wiki` current on a recurring cadence and turn the review into GitHub issues.

## Session-derived pattern

A useful first wave separates always-current wiki maintenance into three independently approvable work classes:

1. **Freshness control loop** — weekly offline/default repo-local scan, Markdown report, JSON summary baseline, reason/confidence codes, and recommendation routing.
2. **Agent entrypoint manifests** — root/domain `llms.txt` or equivalent routing surfaces, hand-curated with deterministic validators and smoke tests, so agents navigate cheaply instead of rescanning the repo.
3. **OSS/concept watchlist** — fixture-first weekly watchlist for important LLM/agent/tooling concepts, with static config separated from mutable state and optional bounded live scan.

Defer heavier second-wave work until the first-wave contracts land:
- public-safe knowledge graph / relationship extraction,
- RAG/retrieval evaluation benchmark,
- CLI/MCP query surfaces.

## Approval-sync requirement

When the user approves only a subset of reviewed issues, synchronize all approval surfaces before implementation:

- live GitHub label: `status:plan-approved`,
- plan frontmatter: `status: plan-approved`,
- local marker: `.planning/plan-approved/<issue>.md`,
- `docs/plans/README.md` row,
- GitHub approval-sync comment linking commit, plan, marker, and execution handoff.

Do not infer approval for sibling issues that were merely in the same review packet. Leave unapproved siblings at `status:plan-review`.

## Public-safety boundary

Weekly cadence artifacts should default to public-safe, repo-local, deterministic outputs. Do not commit private/raw/client/vendor material, credentials, path-rich private manifests, or secrets. If live external scans are included, make them bounded, optional, and fixture-backed in tests.

## Recommended sequencing

For implementation after approval, prefer:

1. agent entrypoint manifests,
2. freshness control loop,
3. OSS/concept watchlist.

This order gives later automation a stable navigation contract and lowers recurring token spend.

When the agent-entrypoint manifest issue is already landed/closed, the next logical step is the **freshness control loop** before the OSS/concept watchlist. The freshness loop is the cadence substrate: it defines stale-page detection, report/schema outputs, broken-link checks, and recommendation routing that later watchlist/retrieval work should feed.

For "next logical step" follow-ups, do not re-open broad strategy. Re-check live issue labels and local approval markers, then give a concise priority recommendation:
- execute the first `status:plan-approved` substrate issue that unblocks the cadence;
- keep `status:plan-review` siblings out of execution until explicit user approval;
- name the evidence checked: clean/synced repo state, issue URL, labels, and local `.planning/plan-approved/<issue>.md` marker when relevant.

## Agent entrypoint manifest implementation lessons

When implementing the agent-entrypoint work class, treat `llms.txt` as a tested navigation contract, not a static index:

- Add a root `llms.txt` for repo-level routing plus domain-level `llms.txt` manifests for high-value wiki trees.
- Include only high-signal curated paths: quick-start routes, domain entrypoints, canonical standards/concept pages, validation commands, and freshness expectations.
- Add a deterministic validator that checks every manifest link resolves to an existing file and, where anchors are listed, that the target heading/anchor exists.
- Test domain routing semantically enough to catch dead or renamed routes; adversarial review should look specifically for stale domain links such as a manifest pointing to a missing marine/offshore page.
- Add README guidance explaining when agents should use manifests before broad repo scans and how the weekly cadence refreshes them.
- Verify with targeted tests, the manifest validator, full tests when affordable, `git diff --check`, and adversarial re-review before closeout.
