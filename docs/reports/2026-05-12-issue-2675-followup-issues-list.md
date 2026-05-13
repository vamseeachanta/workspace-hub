# Follow-up issues from plan-2675 (listed, not yet filed)

> **Source plan**: [`docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md`](../plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md)
> **Parent issue**: [#2675](https://github.com/vamseeachanta/workspace-hub/issues/2675) — `feat(ai-orchestration): reverse-prompt repo ecosystem for productive multi-provider work`
> **Status**: 10 follow-ups enumerated below are **listed, not yet filed** per plan §F acceptance criterion #7. File them via `gh issue create` when ready to dispatch each work-stream. 2 harness-bug follow-ups (#2683, #2684) were filed live during plan execution and are already CLOSED.

## How to file

For each row in the table below:

```bash
gh issue create --repo vamseeachanta/workspace-hub \
  --title "<title>" \
  --label "<labels>" \
  --body "$(cat <<'EOF'
<body — see per-issue scope below>
Refs #2675 (parent ecosystem-design plan)
EOF
)"
```

Do not batch all 10 at once: per memory `feedback_parallel_gh_issue_create_reverses_numbers`, parallel `gh issue create &` assigns numbers in apparent reverse arrival order, making cross-references brittle. File sequentially or audit `--json number,title` immediately after each.

## The 10 follow-ups (priority-ordered)

| # | Title | Labels | Scope (one-line) | Why now | Depends on |
|---|---|---|---|---|---|
| 1 | [**#2697**](https://github.com/vamseeachanta/workspace-hub/issues/2697) — `chore(ai-tools): refresh subscriptions.yaml with current Codex paid plan + bump declared totals` | `enhancement`, `priority:high`, `cat:ai-orchestration` | Add Codex $200/mo paid-plan entry; update totals from $156.75 → ~$356.75/mo; bump `last_updated`; cross-check Business Brain | **FILED 2026-05-13** (sequential per `feedback_parallel_gh_issue_create_reverses_numbers`); awaits intake → planning workflow | (independent) |
| 2 | `feat(ai-orchestration): add CODEX.md adapter file + extend coding-style.md enumeration` | `feat`, `priority:high`, `cat:ai-orchestration`, `cat:harness` | Mirror `CLAUDE.md` / `AGENTS.md` / `GEMINI.md`; ≤20 lines. **MUST extend `.claude/rules/coding-style.md:13` enumeration to include `CODEX.md`** in the same PR — otherwise `scripts/enforcement/check-harness-file-size.sh` 20-line check doesn't bind. Reconcile location with #2399's `.codex/CODEX.md` proposal (decide: repo-root vs. hidden-dir). | The repo has 1400+ Codex review results but no adapter entry-point | (independent; resolve location open-question before PR) |
| 3 | `chore(ai-config): audit + extend config/agents/{codex,gemini,hermes}/ to match §B role matrix` | `chore`, `priority:medium`, `cat:ai-orchestration` | Existing minimal content needs auditing against the §B role matrix from `AI_ECOSYSTEM_DESIGN.md`; gaps per provider: Codex (review-only enforcement in `config.toml`), Gemini (`git ls-files` precondition reference), Hermes (preflight contract in `SOUL.md` or `config.yaml.template`). Reference `config/agents/claude/` as the populated template. | The dirs are populated but minimally; behavior-anchored content aligned to the role matrix is missing | #2 (CODEX.md adapter informs codex/ subdir content) |
| 4 | `feat(ai-orchestration): cost/quota model + monthly spend envelope` | `feat`, `priority:medium`, `cat:ai-orchestration` | Deferred from plan-2675. Concrete monthly target per provider with triggers that change routing. Consume `config/ai-tools/usage-tracking.yaml`, `weekly-utilization.json`, `pricing.yaml`. **Critical scope**: define the explicit halt-trigger when Claude (the structural-SPOF per §B) is quota-degraded — graceful halt-and-wait protocol, not auto-fallback. | The §B matrix concentrates 5 of 7 primary roles on Claude as a structural property; no codified halt protocol exists for quota exhaustion | #1 (accurate subscriptions before envelope design) |
| 5 | `feat(ai-orchestration): migration plan for AI_ECOSYSTEM_DESIGN.md adoption` | `feat`, `priority:medium`, `cat:ai-orchestration` | Deferred from plan-2675. Day-1 / month-1 / quarter-1 incremental adoption schedule. What changes day-1 (config/skill touches), what changes by month-1 (workflow surfaces), what changes by quarter-1 (cron/automation reshape). | The durable standards doc landed but adoption isn't sequenced | (independent; can start in parallel with #4) |
| 6 | `feat(ai-orchestration): workflow walkthrough — knowledge/wiki contribution` | `feat`, `priority:medium`, `cat:ai-orchestration` | Deferred from plan-2675 §C (v1 covered planning + adversarial review only). New walkthrough covers `feedback_llm_wiki_*` rules: concept-page sourcing (textbooks/DOIs/public manuals, not LinkedIn-only), hyphen-path patterns, sources/ vendor-derivative deny-list. | Knowledge/wiki is one of §A's 6 owned work classes but lacks a walkthrough in `AI_ECOSYSTEM_DESIGN.md` | (independent) |
| 7 | `feat(ai-orchestration): workflow walkthrough — execution batch run` | `feat`, `priority:medium`, `cat:ai-orchestration` | Deferred from plan-2675 §C. Covers Hermes overnight batch + parallel-agent commit serialization; preflight protocols; merge-race silent revert mitigations (per `feedback_hermes_active_preflight_check`, `feedback_multi_agent_commit_serialization`). | Ops/automation is one of §A's 6 owned work classes but lacks a walkthrough | (independent) |
| 8 | `chore(ai-tools): refresh agent-capability-scores.yaml from 2026-04/05 incident data` | `chore`, `priority:medium`, `cat:ai-orchestration` | Scores at `config/ai-tools/agent-capability-scores.yaml` (`v 2026-03-13`) predate the 2026-04/05 codex/gemini/hermes incident wave captured in memory (`feedback_codex_sandbox_*`, `feedback_gemini_sandbox_overlay_blindness`, `feedback_hermes_active_preflight_check`). Re-score and reference incident memories. | The radar visualization at `config/ai-tools/agent-capability-radar.html` shows pre-incident perception, drifting from operational reality | (independent) |
| 9 | `feat(ai-orchestration): codify "when NOT to cross-review" rule in routing-config.yaml` | `feat`, `priority:medium`, `cat:ai-orchestration` | Add a tier-tier override field; cite `feedback_permission_gate_blocks_cross_review`. Today the routing-config defines `cross_review` per tier (`SIMPLE: false, STANDARD: true, COMPLEX: true, REASONING: true`) but doesn't codify the "permission-gate-blocks-dispatch" exception that sanctions single-author r3 fallback. | The exception was used 3× in plan-2675's own review cycle (wave-2 + wave-3 for #2675; r3 for #2683); operationally important but undocumented | (independent) |
| 10 | `feat(ai-orchestration): "Memory-to-Surface" map maintenance contract` | `feat`, `priority:low`, `cat:ai-orchestration` | Quarterly refresh of the §E table as new memory lessons land; integrate with `learn-extended` skill. **Refresh trigger**: any commit that renames or deletes a `~/.claude/projects/.../memory/feedback_*.md` slug cited in §E must update the row in the same PR (cycle ≤24h, not quarterly; quarterly is the baseline sweep only). | §E maps 20 feedback memories to mitigation surfaces; without a maintenance contract, the map decays as memory files rename (already observed: `feedback_codex_cli_0_124_*` was 24h-stale after #2684 landed) | (independent) |

## Harness follow-ups (filed live during plan-2675 execution)

These 2 issues were filed during wave-1 → wave-2 cross-review when the harness regressions surfaced. **Both CLOSED** as part of plan-2675 execution.

| # | Title | Status | Fix commit | Notes |
|---|---|---|---|---|
| 11 | [#2683](https://github.com/vamseeachanta/workspace-hub/issues/2683) — `bug(harness): Claude SessionEnd hook (codex plugin) times out and crashes plan-review-fanout child claude with rc=124` | **CLOSED** | `b61f2c5a3` | Fix: `CLAUDE_PLUGIN_DIR` override in `scripts/review/plan-review-fanout.sh` claude case branch. Mechanism deviation from approved plan (originally `--bare` flag, found incompatible with keychain auth) documented in the issue's plan file. |
| 12 | [#2684](https://github.com/vamseeachanta/workspace-hub/issues/2684) — `bug(harness): codex-cli 0.130.0 reproduces #2479 stdin-hang pattern in plan-review-fanout despite </dev/null guard` | **CLOSED** | `0cd40c6ab` | Fix: `CLAUDECODE=1` env-guard added to `codex_version_guard_check()`. Working as designed — codex emits UNAVAILABLE fast (~0.033s) instead of hanging for `PLAN_REVIEW_PROVIDER_TIMEOUT_SEC` (default 600s). The env-guard is a mitigation/workaround; underlying upstream `openai/codex#19945` remains. |

## Future-attention captured (not filed; not in §F)

- **Upstream advocacy**: Option 3 from #2684's issue body — re-open `openai/codex#19945` with our 0.130.0 + Claude-Code Bash reproducer. Defer until there's a need (env-guard suffices for current usage); file as standalone when prioritized.
- **`script(1)` PTY wrap spike**: Option 2 from #2684's issue body — retest on 0.130.0 (memory says it failed on 0.124.0–0.122.0). Worth a one-spike investigation if env-guard ever proves insufficient; not currently blocking.

## Cross-reference: which §F items unblock which workflows

| Workflow / consumer | Unblocked by §F items |
|---|---|
| Cost/quota decisions | #1 (accurate subscriptions), #4 (envelope model) |
| Multi-provider config parity | #2 (CODEX.md), #3 (audit/extend config/agents/) |
| Workflow doc completeness | #6 (wiki), #7 (batch) |
| Routing intelligence | #8 (refreshed scores), #9 (no-cross-review rule) |
| Plan-2675 deliverable longevity | #5 (migration), #10 (memory-map maintenance) |
| Cross-review fanout discipline | #11, #12 (both CLOSED; cited as resolved) |
