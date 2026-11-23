# Follow-up draft (H2) — Drain-ready-queue command pack

> **Status:** DRAFT. Not filed. Per #2557 report's duplicate-of analysis, H2 is "new issue if not covered by [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519)". Verify before filing.
>
> **Plan #2557 r1 review caveat (Finding 3):** the report's underlying ready-queue numbers are stale — claims "8 Codex ready / 17 routed" but live `docs/reports/provider-work-queue.md` shows `18 ready / 41 routed`. The hack is still valid (eliminate the daily "what to dispatch next" decision), but the example issue list and time-savings estimate must be re-derived from a fresh regeneration before this is filed.

## Title (if filed as new issue)

`feat(queue): drain-ready dispatch command pack — one-click next-3-per-provider`

## Body

### Summary

Add a `scripts/queue/drain-ready.sh` that prints (does NOT execute) the next 3 `status:plan-approved` issues per provider with the canonical launch command for each. Surface the output in the existing daily-readiness cron output. The owner picks/runs; this hack only removes the daily 15-min "what should I dispatch next" overhead, not the dispatch decision itself.

### Why this is bounded

- One new script (`scripts/queue/drain-ready.sh`).
- One existing cron extension (the daily-readiness cron that already runs `python -m gtm.reports …` per `project_daily_readiness_cron.md`).
- Reads from `docs/reports/provider-work-queue.md` — no new data source.
- Output is a comment-class artifact; safe per H4's allowlist (no GitHub mutation).

### Implementation sketch

```bash
# scripts/queue/drain-ready.sh
set -euo pipefail
QUEUE_FILE="${1:-docs/reports/provider-work-queue.md}"
[[ -f "$QUEUE_FILE" ]] || { echo "queue file not found: $QUEUE_FILE" >&2; exit 1; }

# For each provider section, print the first 3 rows where Ready=yes,
# then emit a launch command. Pure parse — no network, no mutation.
awk '
  /^## (claude|codex|gemini)/ { provider = $2; ready_count = 0; print "\n=== " provider " (next 3 ready) ===" }
  /^\| #/ {
    if (provider == "" || ready_count >= 3) next
    if ($0 ~ /\| yes \|/) {
      issue = $2
      sub(/^\| /, "", issue)
      print "  " issue
      ready_count++
    }
  }
' "$QUEUE_FILE"

cat <<EOF

Launch templates (paste into a separate terminal):
  Codex     : bash scripts/dispatch/codex-impl.sh <ISSUE_NUM>
  Claude    : bash scripts/dispatch/claude-impl.sh <ISSUE_NUM>
  Gemini    : bash scripts/dispatch/gemini-research.sh <ISSUE_NUM>
EOF
```

### Acceptance criteria

- [ ] `scripts/queue/drain-ready.sh` exists and emits 3 ready candidates per provider (or fewer with an explicit "no ready candidates" line).
- [ ] No GitHub mutation; pure read + print.
- [ ] Daily-readiness cron reads `drain-ready.sh` output into its summary block.
- [ ] Operator runbook documents the script in `docs/playbooks/`.
- [ ] Numbers regenerated against fresh `docs/reports/provider-work-queue.md` (not stale snapshot).

## Duplicate-of check (2026-04-29)

- [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519) — `feat(hermes): orchestrate AI provider usage and workstation dispatch` — OPEN, `priority:critical`. Hermes-orchestration umbrella; H2 is a tactical drain script, may be a sub-task of #2519. **Verify whether #2519's scope already covers a one-click drain helper before filing.**
- [#2523](https://github.com/vamseeachanta/workspace-hub/issues/2523) — Hermes preflight readiness checker — possibly related, verify scope.
- [#2524](https://github.com/vamseeachanta/workspace-hub/issues/2524) — machine-aware dispatch ledger — possibly related, verify scope.

Verdict: AMBIGUOUS — `#2519` may absorb this. **Recommended action: comment on #2519 with the H2 sketch and ask whether it should be filed as a sub-issue or absorbed into #2519's plan.**
