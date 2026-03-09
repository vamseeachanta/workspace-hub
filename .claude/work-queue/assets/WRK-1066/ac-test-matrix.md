# WRK-1066 AC Test Matrix

| # | AC | Test | Result | Evidence |
|---|-----|------|--------|---------|
| 1 | harness-config.yaml has `linux_reachable: false` on acma-ansys05 | `grep 'linux_reachable: false' scripts/readiness/harness-config.yaml` | PASS | grep returns match |
| 2 | `ai-tools-status.sh` reads harness-config.yaml, uses PATH-explicit SSH | Code review: script reads CONFIG=$REPO_ROOT/scripts/readiness/harness-config.yaml; SSH cmd uses explicit PATH | PASS | scripts/maintenance/ai-tools-status.sh:14,38 |
| 3 | `ai-tools-status.yaml` has `collection_summary` block | `grep 'collection_summary' config/ai_agents/ai-tools-status.yaml` | PASS | output confirmed |
| 4 | Drift computed only over reachable machines | ace-linux-2 offline → all drift shows "only 1 reachable machine" (no false BLOCKs) | PASS | config/ai_agents/ai-tools-status.yaml |
| 5 | Script exits 0 for unreachable machines | `bash scripts/maintenance/ai-tools-status.sh; echo $?` → 0 with ace-linux-2 offline | PASS | exit 0 confirmed |
| 6 | acma-ansys05 row present with `reachable: false` | `grep -A1 'acma-ansys05:' config/ai_agents/ai-tools-status.yaml` | PASS | reachable: false in output |
| 7 | `setup-cron.sh` ENTRIES array has ai-tools-status.sh at 03:15 Sunday | `bash scripts/cron/setup-cron.sh --dry-run \| grep ai-tools` | PASS | "15 3 * * 0" confirmed |
| 8 | `crontab-template.sh` has weekly comment entry | `grep 'ai-tools-status' scripts/cron/crontab-template.sh` | PASS | comment present |
| 9 | npm-channel tools installed on ace-linux-1 | claude=2.1.71, codex=0.111.0, gemini=0.32.1 all present | PASS | ai-tools-status.yaml |
| 10 | YAML schema: `{raw, semver, status}` per tool | `grep 'semver' config/ai_agents/ai-tools-status.yaml` | PASS | fields present for all tools |

PASS: 10 / FAIL: 0

## Deferred ACs (Phase 2)
- acma-ansys05 version collection: requires local Windows session
- ace-linux-2 version collection: machine was offline; will auto-collect on next weekly cron run
