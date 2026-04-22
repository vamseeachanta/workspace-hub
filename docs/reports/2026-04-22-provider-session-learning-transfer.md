# Provider session learning transfer — 2026-04-22

## Scope
Assessment of recent or newly surfaced provider-session activity after refreshing `analysis/provider-session-ecosystem-audit.json` and `docs/reports/provider-session-ecosystem-audit.md` at `2026-04-22T00:19:59Z`.

Previous assessed audit boundary: `2026-04-20T21:46:16Z`.

This bundle separates:
- true post-audit event-time activity
- corpus growth caused by export/backfill/classification changes
- the repo issue surfaces that should absorb the resulting learnings

## Cross-provider delta summary

### Event-time activity since the prior audit
- Claude: 2351 post-hook records across 62 runtime sessions
- Hermes: 589 post-hook records across 3 runtime sessions
- Codex: 10 post-hook records across 3 runtime sessions
- Gemini: 0 post-hook records across 0 runtime sessions

### Snapshot/corpus growth beyond event-time activity
- Claude: aligned with event-time activity (`+2351` records delta vs `2351` recent records)
- Codex: positive corpus anomaly (`+526` records delta vs `10` recent records)
- Hermes: strong positive corpus anomaly (`+12777` records delta vs `589` recent records)
- Gemini: positive corpus anomaly (`+65` records delta vs `0` recent records)

Interpretation: only Claude and Hermes materially changed through new event-time work. Codex and Gemini mainly need classification/export follow-up, not urgent session-behavior intervention.

## Provider assessments

### Claude
Recent/unassessed signal:
- highest post-audit activity volume in the ecosystem
- urgency jumped from `55.23` to `80.0`
- known migration debt increased from `972` to `1739` mapped stale reads
- top hotspot expanded to `legacy_work_queue_transition` with `1015` mapped reads
- top stale-path cluster now includes `scripts/work-queue/verify-gate-evidence.py` in addition to the prior `start_stage.py` / `exit_stage.py` family

Recent-session behavior:
- recent work is overwhelmingly plan/review/governance heavy (`docs/plans/*`, issue-planning skill loads, GitHub-heavy Bash usage)
- recent slice shows no new missing-repo reads, which suggests the fresh event-time work itself is healthier than the accumulated corpus
- the debt increase is therefore best interpreted as the audit surfacing more historical/stale guidance, not current sessions actively worsening the same path family on every turn

Transferable learning:
- the next repo-hardening pass should target the expanded stage-transition cluster as one family, not treat `verify-gate-evidence.py` as separate noise
- issue-planning and review surfaces are now the dominant live Claude workflows, so stale redirect fixes should be concentrated in governance/review docs, prompts, and templates that those workflows still teach indirectly

Recommended repo target:
- use `#2310` as the ranked parent backlog anchor
- refresh child scope in `#2311` to explicitly include `scripts/work-queue/verify-gate-evidence.py` alongside the removed stage-transition executables

### Codex
Recent/unassessed signal:
- only `10` post-audit event-time records across `3` sessions
- all recent activity is read-only shell inspection (`sed`, `nl`, `pwd`)
- corpus still grew by `526` records and missing repo reads rose by `62`
- top unmapped paths remain generated-site or non-workspace-hub surfaces such as `content/demos/index.html`, `build.js`, `vercel.json`, `package.json`, and `examples/demos/gtm/output/*.html`

Transferable learning:
- current Codex activity does not justify a behavior-change intervention; the main learning is that export/classification coverage is surfacing more historical drift than the recent-session slice would suggest
- generated-site and other-repo path families should be split from true workspace-hub stale-path debt before they drive remediation priorities

Recommended repo target:
- keep `#2333` as the canonical home for Codex drift-classification expansion
- explicitly record that this audit refresh showed positive corpus growth beyond recent activity, so future triage should not overinterpret the tiny post-audit event-time slice

### Hermes
Recent/unassessed signal:
- `589` post-audit records across `3` runtime sessions
- recent work concentrated on provider-audit/test hardening and plan edits
- corpus grew by `12777` records while event-time activity accounted for only `589`
- recent Bash family mix still shows `python3` (`33`) materially ahead of `uv run` (`5`)
- recent Bash mix also includes direct `codex` and `gemini` command families, reinforcing that Hermes is acting as a coordination/orchestration surface rather than only a single-provider executor

Transferable learning:
- Hermes remains the highest-leverage place to enforce runtime-policy cleanup because it keeps generating orchestration-heavy command traffic and still leaks bare `python3` at meaningful density
- recent Hermes work is meta-ecosystem work (audit/tests/plans/comments), so runtime-policy fixes here will propagate across many future repo-maintenance sessions
- the large positive corpus anomaly means follow-up issue comments should distinguish backfilled/exported history from true new event-time work

Recommended repo targets:
- push the runtime-policy learning into `#2332`
- push the corpus-anomaly/classification learning into `#2333`

### Gemini
Recent/unassessed signal:
- no post-audit event-time sessions
- corpus still grew by `65` records and missing repo reads by `23`, indicating export/backfill or newly captured historical coverage
- top stale families remain local work-queue items and removed wrapper surfaces:
  - `.claude/work-queue/WRK-149.md`
  - `.claude/work-queue/working`
  - `scripts/agents/lib/workflow-guards.sh`
  - `scripts/agents/execute.sh`
  - `.claude/skills/coordination/workspace/work-queue/SKILL.md`
  - `scripts/work-queue/verify-gate-evidence.py`
- python runtime hygiene is still poor overall (`291` bare `python3` vs `39` `uv run ... python`)

Transferable learning:
- there is no urgent Gemini session to review, but the refreshed exporter is still surfacing historical guidance drift that should be redirected into GitHub/.planning and current governance surfaces
- Gemini drift remains dominated by compatibility-era local queue and wrapper paths, so fixes should stay doc/workflow-focused rather than exporter-only

Recommended repo targets:
- route local queue authority learning into `#2312`
- keep wrapper-path normalization notes tied to `docs/ops/legacy-claude-reference-map.md` and the classification work tracked by `#2333`

## Transfer actions for the repo ecosystem
1. Update the tracked provider audit artifacts by rerunning the audit wrapper.
2. Record the Claude migration-debt escalation and expanded hotspot family on `#2310`.
3. Record Codex/Hermes corpus-anomaly and classification guidance on `#2333`.
4. Record Hermes runtime-policy pressure on `#2332`.
5. Record Gemini local-queue authority evidence on `#2312`.

## Verification points
- Refreshed audit artifacts exist and show the new `2026-04-22T00:19:59Z` timestamp.
- This transfer bundle captures the actionable provider deltas in one durable repo note.
- Issue comments should link back to this bundle so the next implementation session starts from the transferred learning instead of re-mining raw logs.
