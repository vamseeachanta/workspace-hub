# Provider session learning transfer — 2026-04-24

## Scope
Assessment of recent or newly unassessed provider-session activity after refreshing:
- `analysis/provider-session-ecosystem-audit.json`
- `docs/reports/provider-session-ecosystem-audit.md`

Refreshed audit timestamp: `2026-04-24T01:42:52Z`.
Previous assessed audit boundary: `2026-04-23T16:20:22Z`.

This bundle separates:
- true post-audit event-time activity
- refreshed standing provider risk from the full corpus
- repo-ecosystem issue surfaces that should absorb the resulting learnings

## Cross-provider delta summary

### Event-time activity since the prior audit
- Claude: 179 post-hook records across 6 runtime sessions
- Codex: 0 post-hook records across 0 runtime sessions
- Hermes: 0 post-hook records across 0 runtime sessions
- Gemini: 0 post-hook records across 0 runtime sessions

Interpretation: only Claude has truly new/unassessed event-time work since the previous transfer boundary. Codex, Hermes, and Gemini should not be described as having new post-boundary work in this cycle; their refreshed recommendations come from standing corpus posture and updated audit interpretation only.

### Snapshot/corpus change versus event-time activity
- Claude: aligned (`+179` post records and `179` recent event-time records)
- Codex: aligned (`0` post-record delta and `0` recent event-time records); missing repo reads improved from 435 to 432
- Hermes: aligned (`0` post-record delta and `0` recent event-time records); missing repo reads worsened from 341 to 652 under refreshed classification/reporting
- Gemini: aligned (`0` post-record delta and `0` recent event-time records); historical local-queue/wrapper debt remains unchanged

Interpretation: this cycle is not a broad new-provider activity wave. Treat it as a Claude delta plus a refreshed standing-risk transfer for the remaining providers.

## Provider assessments

### Claude
Recent/unassessed signal:
- still the highest-priority migration-debt provider (`urgency 80.0`, rank `#1`, health `red`)
- `179` post-audit records across `6` runtime sessions
- recent activity is concentrated in `digitalmodel` OrcaFlex/OrcaWave semantic roundtrip and modular-generator evidence, not in the historical work-queue debt cluster
- recent missing repo reads are `none`
- overall missing repo reads still increased from `8390` to `8450`, which the audit frames as path drift worsening despite the recent slice being clean
- recent writes/edits include `digitalmodel/tests/solvers/orcaflex/modular_generator/test_jumper_plet_to_plem_semantic.py`, `digitalmodel/tests/hydrodynamics/diffraction/test_orcawave_semantic_roundtrip.py`, and `.planning/quick/issue-2455-run-test.sh`

Transferable learning:
- the newest Claude slice is healthier than the historical corpus: current work is reading real domain/spec/test files and did not add recent missing repo reads
- do not dilute the Claude remediation lane into the new `digitalmodel` activity; the actionable debt remains the retained legacy stage-transition/work-queue redirect family
- next Claude remediation should update prompts/docs so legacy callers stop looking for `scripts/work-queue/*` and old work-queue skills, while preserving the current domain-test workflow that is now mostly landing on valid files

Recommended repo targets:
- `#2310` remains the parent backlog/ranking anchor for Claude stale-read migration debt
- `#2311` remains the concrete implementation child for removed stage-transition scripts
- new evidence should be framed as: current Claude behavior is improving, but historical prompt/doc debt still dominates the provider risk profile

### Codex
Recent/unassessed signal:
- no post-boundary event-time activity in this cycle
- standing risk improved slightly: missing repo reads dropped from `435` to `432`
- health cooled from red/next-up to yellow/investigate
- top missing reads remain unmapped and look like cross-repo or generated-site path families (`content/demos/index.html`, `src/worldenergydata/...`, `src/assethold/...`, `build.js`, `vercel.json`)

Transferable learning:
- no new Codex behavior needs remediation from this cycle
- the useful transfer is negative evidence: Codex drift did not grow after the previous assessment, so follow-up should remain classification/sample based rather than urgent behavior correction
- keep separating sibling-repo/generated-site reads from true workspace-hub stale references before turning them into remediation work

Recommended repo target:
- `#2333` should absorb the current Codex learning as a drift-classification note, not as a new provider-control issue

### Hermes
Recent/unassessed signal:
- no post-boundary event-time activity in this cycle
- standing health remains yellow, but the watchlist escalated from monitor to investigate because missing repo reads worsened under refreshed reporting/classification
- top missing repo reads are dominated by ecosystem-sync worktree artifacts, client-project workbook paths, hook paths, and knowledge/wiki paths rather than the known legacy work-queue redirect family
- the audit still shows Hermes as the coordination-heavy provider over rolling windows, with high `gh`, `uv run`, `git status`, `git add`, and `bash` command families

Transferable learning:
- do not claim new Hermes work happened after the previous boundary; the transfer is about refreshed classification risk
- Hermes drift triage should focus on classifying ecosystem-sync worktree paths, knowledge/wiki surfaces, and client-project paths into durable-vs-transient families
- runtime guidance remains valid, but this cycle’s stronger action is classification hygiene in `#2333`

Recommended repo targets:
- `#2333` should receive the current Hermes classification escalation
- `#2332` remains the runtime-hygiene destination for standing bare-`python3` pressure, but this cycle adds no new event-time Hermes runtime evidence

### Gemini
Recent/unassessed signal:
- no post-boundary event-time activity in this cycle
- standing risk remains red due to historical local-queue / removed wrapper debt and python3-heavy command hygiene
- top missing repo reads still include `.claude/work-queue/*`, removed `scripts/agents/*`, old work-queue skills, and `scripts/work-queue/verify-gate-evidence.py`
- health/urgency cooled from the prior audit because recent activity dropped to zero

Transferable learning:
- no new Gemini behavior needs remediation from this cycle
- the correct transfer is continuity: the historical local-queue/wrapper redirect problem remains valid, but it should not be presented as fresh activity
- Gemini prompt/workflow hardening should continue steering toward GitHub issues, `.planning/`, `notes/agent-work-queue.md`, `AGENTS.md`, current review/planning scripts, and away from deleted local queue/script wrapper surfaces

Recommended repo targets:
- `#2312` remains the canonical target for the local-queue authority transition
- `#2332` remains the standing runtime-hygiene destination for Gemini python3-heavy command mix

## Repo ecosystem transfer actions
1. Refreshed the canonical provider audit artifacts for the new boundary.
2. Wrote this durable transfer bundle to `docs/reports/2026-04-24-provider-session-learning-transfer.md`.
3. Push Claude current-slice-versus-historical-debt guidance to `#2310` and `#2311`.
4. Push Codex/Hermes classification guidance and negative evidence to `#2333`.
5. Push Gemini continuity guidance to `#2312`.
6. Push runtime-hygiene continuity/no-new-event-time-evidence guidance to `#2332`.

## Verification points
- Audit artifacts now reflect the `2026-04-24T01:42:52Z` refresh.
- This note captures the assessed delta since `2026-04-23T16:20:22Z`.
- Provider claims distinguish true recent event-time activity from refreshed standing corpus posture.
- Repo-transfer comments should point maintainers to this bundle so the next implementation session starts from transferred learnings rather than re-mining raw logs.
