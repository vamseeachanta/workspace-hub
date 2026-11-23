---
name: orcawave-orcaflex-semantic-proof-wave-closeout
description: Close out an OrcaWave/OrcaFlex semantic-proof wave after a PR merges, split unrelated CI blockers, and seed the next semantic-proof issue wave without duplicating existing issues.
version: 1.0.0
author: Hermes Agent
tags: [workspace-hub, digitalmodel, orcawave, orcaflex, github, semantic-proof, closeout]
---

# OrcaWave/OrcaFlex Semantic-Proof Wave Closeout

Use this after a digitalmodel OrcaWave/OrcaFlex semantic-proof PR is ready to merge or has just merged, especially when workspace-hub issues track the work.

## Trigger

- A digitalmodel PR implements canonical `spec.yml -> semantically equivalent native solver input` proof coverage.
- Related workspace-hub issues are `status:plan-approved` and should close only after PR merge/acceptance.
- CI may have unrelated red checks that should not be folded into the semantic-proof PR.

## Proven pattern

### 1. Load the domain handoff/operator map first

Read the current handoff and the operator map before acting. For the April 2026 wave:

- `docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md`
- `docs/handoffs/2026-04-24-orcawave-orcaflex-next-wave-closeout.md`
- `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`

### 2. Verify PR and issue state live

Use `gh`, not memory:

```bash
gh pr view 528 --repo vamseeachanta/digitalmodel \
  --json number,state,isDraft,mergeable,headRefName,baseRefName,commits,statusCheckRollup,url,title

for n in 2455 2456 2457; do
  gh issue view "$n" --repo vamseeachanta/workspace-hub \
    --json number,title,state,labels,url,updatedAt
done
```

Also verify branch protection if considering merging with a red check:

```bash
gh api repos/vamseeachanta/digitalmodel/branches/main/protection || true
```

### 3. Split unrelated CI blockers explicitly

If `Run Quality Gates` is red because of unrelated `pylife` missing dependency:

- Treat it as workspace-hub #2441.
- Do not fold it into semantic-proof PRs/issues unless explicitly approved.
- PR #528 was merged with this explicit exception because the diff was limited to semantic-proof files and branch protection did not require green checks.

Recommended PR comment before merge:

```text
Merging with an explicit CI exception: the remaining red `Run Quality Gates` check is the pre-existing unrelated `pylife` dependency failure tracked in vamseeachanta/workspace-hub#2441.

Scope for this PR remains limited to OrcaWave/OrcaFlex semantic-proof backend/tests, and the targeted semantic-proof validation for this wave passed (`35 passed`). Follow-up licensed solver load/run proof and broader fixture coverage remain separate next-wave work.
```

### 4. Merge, then clean closed issue labels

For PR #528 the successful closeout was:

- digitalmodel PR #528 merged 2026-04-24.
- Merge commit: `bbfe994c4841c77329364e84cc9d106bbb714c4d`.
- Closed workspace-hub issues: #2455, #2456, #2457.

After the PR auto-closes issues, remove stale planning labels from closed issues:

```bash
for n in 2455 2456 2457; do
  gh issue edit "$n" --repo vamseeachanta/workspace-hub --remove-label 'status:plan-approved' || true
done
```

### 5. Dedupe before creating next-wave issues

Search existing issues for candidate structures/workflows before creating new issues:

```bash
gh issue list --repo vamseeachanta/workspace-hub --state all --limit 100 \
  --search 'OrcaFlex OR OrcaWave OR CALM OR SPM OR FPSO OR RAO OR hydrodynamic OR reverse-parser OR licensed solver proof'
```

Important dedupe learned:

- Do not create a duplicate FPSO issue if #2454 already exists for flagship/turret-moored FPSO semantic proof.
- Use existing #2454 for that path.

### 6. Seed next-wave issues from the handoff gaps

The April 2026 next-wave issue set created:

- #2472 `feat(canonical-spec): validate CALM/SPM buoy OrcaFlex semantic proof`
- #2473 `feat(canonical-spec): prove OrcaWave-to-OrcaFlex hydrodynamic handoff semantics`
- #2474 `feat(canonical-spec): add OrcaFlex native reverse-parser equivalence proof`
- #2475 `chore(licensed-proof): define OrcaWave/OrcaFlex native load-run proof protocol`
- #2476 `docs(llm-wiki): add canonical spec semantic-equivalence contract and fixture cookbook`

Recommended order:

1. Plan #2476 first so semantic-equivalence contract/cookbook exists before broad fixture expansion.
2. Plan #2475 next or in parallel for licensed-machine evidence protocol.
3. Then plan #2472/#2473/#2474 as implementation waves.
4. Keep #2441 pylife CI health separate.

### 7. Post traceability comments

After issue creation, post a concise traceability comment to:

- parent roadmap #1572
- closed epic #2453
- CI blocker #2441 if a PR was merged despite the known unrelated red check

Use `gh issue comment --body-file`, not inline markdown.

### 8. Write a repo handoff and commit it

Create a dated handoff under `docs/handoffs/` recording:

- merged PR and merge commit
- closed issues and label cleanup
- new next-wave issues
- separate blocker issues
- important boundaries
- suggested next order

For the April 2026 wave:

- `docs/handoffs/2026-04-24-orcawave-orcaflex-next-wave-closeout.md`
- commit `47b39cc70 docs(handoff): record OrcaWave OrcaFlex next-wave closeout`

## Pitfalls

- Do not treat deterministic YAML/roundtrip tests as licensed solver load/run proof.
- Do not close first-wave issues before PR merge/acceptance.
- Do not leave `status:plan-approved` on closed issues.
- Do not create duplicate FPSO issues; check #2454 first.
- Do not let subagent research timeouts block obvious safe closeout actions; recover with direct parent-session `gh`/git verification and record the timeout in the handoff.
- Do not fold `pylife` CI repair into semantic-proof work without explicit approval.

## Current April 2026 state anchors

- PR #528: merged, commit `bbfe994c4841c77329364e84cc9d106bbb714c4d`.
- First wave closed: #2455, #2456, #2457.
- Next wave open: #2472, #2473, #2474, #2475, #2476.
- FPSO existing issue: #2454.
- Unrelated CI blocker: #2441.
