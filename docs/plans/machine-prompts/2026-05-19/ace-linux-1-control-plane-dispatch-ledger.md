# ace-linux-1 control-plane dispatch ledger — dry run

> Generated: 2026-05-19T20:16:58Z  
> Control issue: [#2738](https://github.com/vamseeachanta/workspace-hub/issues/2738)  
> Host: `dev-primary` / `ace-linux-1`  
> Mode: dry-run / no background lane launched

## Verdict

`ace-linux-1` can resolve a local workstation dispatch target, but it is **not dispatchable yet** because the workspace-hub control-plane checkout is dirty.

The next safe action is to reconcile/commit/preserve the existing workspace state, then rerun the readiness probe. Do not launch long-running cross-provider work from this ledger until `scripts/readiness/telegram-hermes-readiness.sh --host dev-primary` returns `overall_status: pass`.

## Inventory evidence

### Dispatch/readiness scripts found

| Artifact | Role | Dry-run evidence |
|---|---|---|
| `scripts/readiness/telegram-hermes-readiness.sh` | Fail-closed Telegram/Hermes host readiness wrapper | Ran for `dev-primary`; returned `overall_status: fail` only because workspace root is dirty. |
| `scripts/readiness/telegram_hermes_readiness.py` | Python implementation behind readiness wrapper | Help confirms `--registry`, `--host`, and `--evidence-dir`. |
| `scripts/operations/workstation-dispatch.sh` | Local/remote workstation dispatch helper | Dry-run target resolution succeeded for `dev-primary`. |
| `scripts/ai/provider-dispatch-loop.py` | Provider dispatch planner / lease loop | Help confirms `--dry-run`, `--morning-qa`, leader host, and promotion token options. |
| `scripts/ai/task-dispatcher.py` | Provider/model recommendation helper | Help confirms task+tier routing output. |
| `scripts/operations/agent-execution/ace2-readiness.sh` | Overflow worker readiness probe | Available for later ace-linux-2 validation. |

### Provider queue artifacts refreshed/read

| Artifact | Generated at / status | Key finding |
|---|---|---|
| `config/ai-tools/provider-utilization-weekly.json` | refreshed by `bash scripts/cron/provider-utilization-refresh.sh` | Alerts show underutilization: Claude 2.7%, Codex 1.1%, Gemini 0.0% at the time of the refresh input read. |
| `config/ai-tools/provider-routing-scorecard.json` | 2026-05-19T17:20:10Z before final refresh read | Recommended provider order: Gemini, Codex, Claude. |
| `config/ai-tools/provider-work-queue.json` | 2026-05-19T17:20:12Z before final refresh read | Claude: 21 execution-ready, Codex: 2 execution-ready, Gemini: 1 execution-ready. |
| `config/ai-tools/provider-kanban.json` | 2026-05-19T17:20:14Z before final refresh read | 200 cards; all currently classified as planning-feedstock by the Kanban artifact. |
| `docs/reports/provider-*.md/html` | present | Human-readable dashboards exist for operator review before launch. |

## Commands run

```bash
gh issue view 2738 --json number,title,url,state,labels,body
bash scripts/readiness/telegram-hermes-readiness.sh --host dev-primary
bash scripts/operations/workstation-dispatch.sh --requires ai-orchestration,github --command 'echo dry-run-control-plane' --machine ace-linux-1 --dry-run
bash scripts/cron/provider-utilization-refresh.sh
```

Readiness result excerpt:

```json
{
  "overall_status": "fail",
  "hosts": {
    "dev-primary": {
      "dispatchable": false,
      "status": "fail",
      "failures": [
        "workspace_root has uncommitted or untracked git changes"
      ],
      "workspace_root": "/mnt/local-analysis/workspace-hub",
      "telegram_mode": "coordinator"
    }
  }
}
```

Workstation dispatch dry-run result:

```text
[dispatch] Target: dev-primary (local=True)

DRY RUN — would execute on dev-primary:
  echo dry-run-control-plane
```

## First controlled lanes

These are **candidate lanes only**. They are intentionally not launched from this ledger.

| Lane | Issue | Mode | Machine | Provider/tool | Approval state | Why first | Launch gate | Evidence on completion |
|---|---|---|---|---|---|---|---|---|
| A | [#2738](https://github.com/vamseeachanta/workspace-hub/issues/2738) — harden ace-linux-1 Telegram gateway as dispatch coordinator | validation / hardening | `ace-linux-1` | Hermes + shell probes | `status:plan-approved` | This is the blocking control-plane hardening issue for any dispatch. | Workspace clean/preserved; readiness re-run returns pass or only named expected residue. | GitHub comment on #2738 with readiness output, systemd/env evidence redacted, and exact remaining blocker if any. |
| B | [#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754) — choose tier-1 repo placement for ace-linux-1 | planning / user decision | `ace-linux-1` | Hermes main session | planning-feedstock / decision issue | Establishes repo placement decision surface for the control host before normalizing worker machines. | No implementation; only read live filesystem and prepare decision options. | Decision-ready comment/body update listing candidate tier-1 repos and recommended placement policy. |
| C | [#2733](https://github.com/vamseeachanta/workspace-hub/issues/2733) — make Hermes memory canonical across all AI providers | research/recon batch | `ace-linux-1` | Gemini or Claude, per refreshed queue | queue artifact reports Gemini has 1 execution-ready candidate | Good low-risk provider-throughput lane after control-plane readiness because it is planning/recon heavy. | Readiness pass; no overlapping session; prompt/output path bounded under `docs/plans/machine-prompts/2026-05-19/`. | Report artifact plus issue comment; no GitHub label mutation from worker lane. |

## Stop conditions

- `telegram-hermes-readiness` reports `fail` for any reason other than a consciously named expected residue bucket.
- `git status --short` shows unclassified workspace-hub drift.
- A candidate issue lacks the required lifecycle label for its mode.
- A provider lane would mutate GitHub from a worker context instead of the `ace-linux-1` control surface.
- A lane requires Windows/licensed-solver access; that belongs to later licensed host issues, not this dry run.

## Next validation checkpoint

1. Classify current workspace-hub dirty state as expected vs unexpected.
2. Preserve or commit intended changes with serialized pathspec commits; do not sweep unrelated residue.
3. Re-run:
   ```bash
   bash scripts/readiness/telegram-hermes-readiness.sh --host dev-primary
   ```
4. If pass, run only the lane A validation/hardening path first and post evidence back to [#2738](https://github.com/vamseeachanta/workspace-hub/issues/2738).
