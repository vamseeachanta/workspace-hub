# Data → Execution → Results Execution Plan

**Repo:** `vamseeachanta/workspace-hub`  
**Prepared:** 2026-05-21T02:37:12Z  
**Parent board:** [`2026-05-20-data-execution-results-kanban.md`](./2026-05-20-data-execution-results-kanban.md)  
**GitHub Project:** https://github.com/users/vamseeachanta/projects/1

## User update folded into scope

- `llm-wiki` is now private.
- ACMA/client data can be stored more fully than originally assumed, with key-information abstractions and less restrictive redaction than public-wiki routing required.
- This changes `#2746/#2747/#2748` from “private target with conservative minimized data” to “private target with maximized useful data, provenance, and abstraction boundaries.”

## Hard gate stance

- Planning, recon, review, board metadata, and prompt generation may run now.
- Implementation may run only for issues already carrying `status:plan-approved` and a durable plan artifact.
- I am not self-applying `status:plan-approved` to any issue.
- For destructive storage moves/deletes, worker prompts must stop at verified dry-run + decision comment unless the approved plan explicitly authorizes the exact destructive step.

## Live issue-gate snapshot

### Data layer

| Issue | Live status | Route | Action now |
|---:|---|---|---|
| `#2731` | `status:needs-plan` | Claude | Draft plan for canonical data/repo location inventory. |
| `#2732` | no status | Claude | Draft dependent mount/folder taxonomy plan after `#2731` assumptions. |
| `#2745` | `status:plan-approved` | Codex | Execute approved freeze/archive posture work; no destructive delete without explicit evidence gate. |
| `#2746` | `status:plan-approved` | Claude | Execute private `llm-wiki` target setup; incorporate private-repo data policy update. |
| `#2747` | no status | Codex/Claude | Draft provenance + confidence scoring plan; implementation trails `#2746/#2389`. |
| `#2748` | no status | Codex | Draft output scaffolding plan; implementation trails `#2747/#2389`. |
| `#2767` | `status:needs-plan` | Gemini | Inventory/dedup planning only. |
| `#2769` | `status:needs-plan` | Gemini | Disposition planning only for 1.8 TB backup. |
| `#2389` | no status | Codex | Draft testable source_doc_key propagation plan. |

### Execution layer

| Issue | Live status | Route | Action now |
|---:|---|---|---|
| `#2738` | `status:plan-approved`, `agent:claude` | Claude | Execute ace-linux-1 coordinator hardening. |
| `#2739` | `status:plan-approved`, `agent:claude` | Claude | Execute ace-linux-2 worker promotion. |
| `#2754` | `status:plan-approved` | Claude | Execute ace-linux-1 throughput lane activation. |
| `#2755` | `status:plan-approved`, `status:working` | Claude | Do not duplicate; monitor/reconcile existing worker state. |
| `#2756` | `status:needs-plan` | Claude | Draft licensed-win-1 lane plan. |
| `#2757` | `status:needs-plan` | Claude | Draft licensed-win-2 lane plan. |
| `#2762` | `status:needs-plan` | Claude | Draft scheduler routing contract plan. |
| `#2763` | `status:needs-plan` | Claude | Draft migration plan after `#2762` contract. |
| `#2710` | `status:plan-approved` | Codex | Execute bounded `/solver-submit` CLI/skill work with TDD. |
| `#2665` | `status:plan-approved` | Claude | Execute provider-credit dashboard/dispatch gates if not already complete. |

### Results/output layer

| Issue | Live status | Route | Action now |
|---:|---|---|---|
| `#2389` | no status | Codex | Plan first; blocks traceable result artifacts. |
| `#2747` | no status | Codex/Claude | Plan first; depends on `#2746/#2389`. |
| `#2748` | no status | Codex | Plan first; depends on `#2747/#2389`. |
| `#2122` | no status | Codex | Draft reporting scorecard plan. |
| `#2147` | no status | Codex | Draft validator plan after schema/scorecard. |
| `#2154` | no status | Codex | Draft renderer plan after scorecard/schema. |
| `#2165` | no status | Codex | Draft asset/path integrity plan. |
| `#2171` | no status | Codex | Draft E2E smoke plan after renderer/assets. |
| `#2768` | `status:plan-approved` | Codex | Approved but cross-repo/data-dependent; verify blockers before execution. |

## Execution waves

### Wave A — planning/recon fan-out now

Purpose: unblock the unapproved data/result layer without bypassing gates.

1. **Claude planning packet:** `#2731/#2732/#2756/#2757/#2762/#2763`.
2. **Gemini inventory packet:** `#2767/#2769/#2392/#2370/#2374`.
3. **Codex planning packet:** `#2389/#2747/#2748/#2122/#2147/#2154/#2165/#2171`.

Expected output: plan drafts or issue comments moving suitable issues toward `status:plan-review`, not implementation.

### Wave B — approved implementation fan-out now

Purpose: start already-approved work that enables the flow.

1. **Codex implementation:** `#2745` and `#2710` in isolated worktrees.
2. **Claude implementation:** `#2746`, `#2738`, `#2739`, `#2754`, `#2665` in isolated worktrees or machine-specific sessions.
3. **Monitor only:** `#2755` because it is already `status:working`.

Expected output: tests first, implementation, commit/push/issue comments, no issue close without verification and cross-review as required.

### Wave C — result-layer execution later

Start only after Wave A plans reach `status:plan-review`, the user approves, and data/provenance contracts are stable.

Recommended order: `#2389` → `#2747` → `#2748` → `#2122` → `#2154/#2147` → `#2165` → `#2171`.

## Worker prompt contract

Every worker prompt must include:

- Re-check live issue labels and comments before action.
- Follow `AGENTS.md` gates and TDD.
- Use isolated worktrees for write-capable work.
- Preserve unrelated dirty root changes.
- Do not add `status:plan-approved` unless explicit user approval exists.
- Post durable issue comments with plan paths, validation evidence, and blockers.
- For destructive filesystem/data changes, stop at dry-run evidence unless exact destructive operation is in an approved plan.

## Execution started 2026-05-21

### Delegated worker outcomes

| Packet | Provider | Outcome |
|---|---|---|
| `#2745` data freeze | Codex | Verified already executed in live state: `vamseeachanta/acma-projects` private+archived, `STATUS-FROZEN.md`, freeze commit `a7727671`, existing closeout comment `#issuecomment-4503822028`. No new implementation commit made. |
| `#2746` private llm-wiki | Claude | Verified main already contains target artifacts and user privacy update. Blocked on run approval for local validation commands in that worker context; no new commit. |
| Execution backbone `#2665/#2738/#2739/#2754` | Claude | Posted evidence comments. `#2665` verified complete/tests pass. `#2738` repo verifier landed but 2 host-side gates remain. `#2739` deferred on `#2755` tier-1 baseline flux. `#2754` partially landed, remaining work blocked by worker worktree-IO mismatch. |
| Result planning `#2389/#2747/#2748/#2122/#2147/#2154/#2165/#2171` | Codex | Sandbox/write path failed; no artifacts created by Codex. Hermes created first-pass plan artifacts for `#2389/#2747/#2748/#2767/#2769` and ran 3-agent adversarial review. |
| Data disposition `#2767/#2769` | Gemini | Produced read-only overlap/disposition review. Identified `#2769` as child/special case of `#2767`; both blocked on `#2731/#2732`; warned against archive/compress on 95%-full `/mnt/ace`. |

### Plan artifacts created and hardened

- `docs/plans/2026-05-21-issue-2389-source-doc-key-promotion-pipeline.md`
- `docs/plans/2026-05-21-issue-2747-acma-private-wiki-promotion-ledger.md`
- `docs/plans/2026-05-21-issue-2748-acma-client-output-scaffolding.md`
- `docs/plans/2026-05-21-issue-2767-unionise-preexisting-data-folders.md`
- `docs/plans/2026-05-21-issue-2769-acma-premove-backup-disposition.md`

Initial adversarial review returned MAJOR/MINOR findings. The plans were hardened with:

- explicit approval-marker preflight checks,
- concrete RED test surfaces,
- deny-by-default private-to-client export gates,
- source identity redaction / no raw path leakage,
- two-tier private evidence vs repo-safe summary rules,
- metadata-only discovery phases for `/mnt/ace` disposition work,
- mount-health guardrails and no destructive operation authority.

## Current root hygiene caveat

The shared root is dirty with unrelated skill, state, plan, report, and review artifacts. Work must be isolated; this execution plan does not claim root cleanup.
