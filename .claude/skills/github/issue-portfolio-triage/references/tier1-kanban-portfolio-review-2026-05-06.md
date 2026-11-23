# Tier-1 Kanban Portfolio Review Example — 2026-05-06

Use this as a compact reference for future multi-repo Kanban/portfolio review tasks.

## Scenario
User asked for a Kanban board across tier-1 repos to review done, pending, future work, additional planning needs, and multiagent orchestration items.

## Scope decision
Use the current active tier-1 / portfolio repo set from authoritative docs, not the larger historical 25-repo overview:

- `workspace-hub`
- `digitalmodel`
- `assetutilities`
- `worldenergydata`
- `assethold`
- `aceengineer-website`

Evidence used:
- `docs/vision/VISION.md` for active repo missions/autonomy levels
- `docs/reports/tier-1-indexing-freshness-latest.md` for latest freshness/readiness scope/status

## Metrics schema
For each repo, collect and summarize:

```json
{
  "repo": "workspace-hub",
  "ghrepo": "vamseeachanta/workspace-hub",
  "branch": "chore/llm-wiki-spinout-cleanup",
  "dirty_count": 6,
  "open_total": 815,
  "closed_sample": 30,
  "plan_review": 7,
  "plan_approved": 22,
  "status_other": 3,
  "planning_needed": 786,
  "claude": 66,
  "codex": 81,
  "gemini": 4,
  "any": 0,
  "conflicting_plan_labels": 0
}
```

## Classification rules used
- `status:plan-approved` → ready / pending execution, but only after plan artifact and approval-marker verification.
- `status:plan-review` → in review / needs user approval; not executable.
- no `status:plan*` label → planning / triage needed.
- both `status:plan-review` and `status:plan-approved` → label conflict / board hygiene blocker.
- recent closed issues → done sample for transactional closeout audit, not exhaustive done accounting unless all closed issues are fetched.

## Snapshot results
Open issue totals in the scoped snapshot:

| Repo | Open | Plan review | Plan approved | Planning needed | Conflicts |
|---|---:|---:|---:|---:|---:|
| `workspace-hub` | 815 | 7 | 22 | 786 | 0 |
| `digitalmodel` | 262 | 0 | 86 | 176 | 0 |
| `assetutilities` | 21 | 1 | 21 | 0 | 1 |
| `worldenergydata` | 61 | 1 | 60 | 0 | 0 |
| `assethold` | 27 | 1 | 27 | 0 | 1 |
| `aceengineer-website` | 5 | 0 | 0 | 5 | 0 |

Key findings:
- Large planning debt concentrated in `workspace-hub` and `digitalmodel`.
- Large approved backlog exists, but should be gated by approval-artifact verification before execution.
- Non-workspace repos lacked `agent:*` routing labels in the scoped snapshot.
- `assetutilities#72` and `assethold#7` had conflicting plan labels.

## Artifact pattern
Create a durable report such as:

`docs/reports/YYYY-MM-DD-tier1-kanban-portfolio-review.md`

Minimum headings:
- Executive summary
- Repo-level board metrics
- Kanban columns
- Additional planning needed
- Multiagent orchestration execution items
- Recommended WIP caps
- Source evidence

## Verification pattern
Before final response:
1. Read the report back.
2. Check required headings.
3. Scan for secret markers such as `ghp_`, `gho_`, `github_pat_`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`.
4. Report git state for the artifact (`??`, modified, tracked).

## Multiagent routing pattern
- Claude: orchestrator, issue decomposition, plan-review synthesis, GitHub authority.
- Codex: bounded verification, tests/scripts, implementation only after approval.
- Gemini: broad issue clustering, dry-run label backfill, research-heavy reconnaissance.

## Follow-up staged approval pattern
After the report was delivered, the user preferred approving next actions one by one rather than launching a batch. Use a compact option menu and one recommendation per turn.

Recommended staged order used:
1. Reconcile blocking board hygiene / conflicting plan-state labels.
2. Audit `status:plan-approved` issues for canonical plan files and approval markers before execution.
3. Create a portfolio spine issue/board if the user wants a live GitHub-native coordination layer.
4. Dry-run `agent:*` routing label backfill.
5. Launch bounded multiagent execution only from clean, approved, non-overlapping issues.

## Conflict reconciliation example
Initial snapshot found `assetutilities#72` and `assethold#7` with both `status:plan-review` and `status:plan-approved`.

Resolution pattern:
1. Re-read live issue labels/comments with `gh issue view`.
2. Locate the actual nested repo paths; do not assume `/mnt/local-analysis/<repo>` if repos are under `/mnt/local-analysis/workspace-hub/<repo>`.
3. Verify canonical plan file and approval marker:
   - `assetutilities/docs/plans/2026-05-05-issue-72-merge-markers-cleanup.md`
   - `assetutilities/.planning/plan-approved/72.md`
   - `assethold/docs/plans/2026-05-05-issue-7-portfolio-value.md`
   - `assethold/.planning/plan-approved/7.md`
4. If evidence supports approval, post an evidence comment, remove stale `status:plan-review`, keep `status:plan-approved`.
5. Patch the report metrics and Kanban rows so the artifact no longer shows stale conflict rows.
6. Re-verify live labels and report content.

If either plan or approval marker is missing, do not normalize to approved; classify as approval-state drift and repair the planning evidence first.

## Pitfalls
- Do not expose `gh auth status` token material; redact any token as `[REDACTED]`.
- Do not treat `status:plan-review` as executable.
- Do not treat `status:plan-approved` as enough by itself; verify canonical plan + local approval marker before execution.
- Do not treat closed issue samples as complete done accounting unless explicitly fetched exhaustively.
- Do not clean dirty repos while producing a portfolio board unless the user specifically asks; dirty counts are risk evidence, not an implicit cleanup request.
- Do not keep offering all recommendations as one batch after the user asks for one-by-one approvals.
