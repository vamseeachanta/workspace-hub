# Provider session learning transfer — 2026-04-23

## Scope
Assessment of recent or newly unassessed provider-session activity after refreshing:
- `analysis/provider-session-ecosystem-audit.json`
- `docs/reports/provider-session-ecosystem-audit.md`

Refreshed audit timestamp: `2026-04-23T16:20:22Z`.
Previous assessed audit boundary: `2026-04-22T00:19:59Z`.

This bundle separates:
- true post-audit event-time activity
- snapshot/corpus growth caused by export/backfill/classification changes
- repo-ecosystem issue surfaces that should absorb the resulting learnings

## Cross-provider delta summary

### Event-time activity since the prior audit
- Hermes: 22375 post-hook records across 160 runtime sessions
- Claude: 2355 post-hook records across 81 runtime sessions
- Codex: 816 post-hook records across 73 runtime sessions
- Gemini: 25 post-hook records across 4 runtime sessions

Interpretation: unlike the previous transfer, all four providers now have real post-audit event-time activity, but the work is not equally actionable. Hermes and Claude drove the meaningful ecosystem-learning delta; Codex and Gemini added smaller recent slices that still sharpen drift classification.

### Snapshot/corpus change versus event-time activity
- Claude: aligned (`+2355` records delta vs `2355` recent records)
- Gemini: aligned (`+25` records delta vs `25` recent records)
- Codex: positive corpus anomaly (`+1305` records delta vs `816` recent records; reconciliation gap `+489`)
- Hermes: strong positive corpus anomaly (`+29312` records delta vs `22375` recent records; reconciliation gap `+6937`)

Interpretation: Claude and Gemini are clean event-time stories this cycle. Codex and Hermes still need caution when translating raw growth into behavioral conclusions because export/backfill/classification changes are materially inflating the corpus delta.

## Provider assessments

### Claude
Recent/unassessed signal:
- still the highest-priority migration-debt provider (`urgency 80.0`, rank `#1`)
- `2355` post-audit records across `81` runtime sessions
- debt remains concentrated in the stage-transition / work-queue redirect family
- recent event-time work is plan/review/governance heavy
- recent missing reads shifted toward live planning artifacts rather than the legacy hot cluster

Transferable learning:
- the recent Claude slice suggests the active workflow has moved into current planning surfaces, but the historical debt hotspot still dominates the provider risk profile
- keep treating `verify-gate-evidence.py`, `start_stage.py`, and `exit_stage.py` as one redirect family; do not split them into separate cleanup efforts
- Claude prompt/doc hardening should focus on planning-review-governance entrypoints because that is where current sessions are spending time

Recommended repo targets:
- keep `#2310` as the ranked parent backlog anchor
- keep `#2311` as the concrete implementation child for the removed stage-transition family
- use this audit refresh as evidence that current Claude work is healthier than the retained historical debt, so remediation should stay doc/prompt/redirect focused rather than exporter focused

### Codex
Recent/unassessed signal:
- `816` post-audit records across `73` runtime sessions
- recent activity is overwhelmingly read-only inspection (`sed`, `rg`, `nl`, `pwd`) with no writes or edits
- recent missing reads are dominated by non-workspace-hub or sibling-repo paths, especially `worldenergydata` sources and plans
- corpus still grew more than event-time activity (`+489` reconciliation gap)

Transferable learning:
- this is no longer a zero-activity provider, but the new activity is still primarily reconnaissance; it strengthens the case for path-family classification, not behavior remediation
- Codex drift triage should explicitly distinguish sibling-repo reads, generated artifacts, and true workspace-hub stale references before assigning remediation priority
- read-heavy Codex sessions are now providing useful evidence about misclassified drift families; that evidence belongs in the drift-classification lane rather than the legacy redirect lane

Recommended repo target:
- push this cycle’s Codex learning into `#2333`
- note that the recent slice is real but mostly inspection-only, so follow-up should improve classification and reporting rather than constrain Codex workflow behavior

### Hermes
Recent/unassessed signal:
- largest post-audit activity by far: `22375` records across `160` runtime sessions
- recent work is concentrated in provider-audit maintenance, plan editing, review artifact generation, GitHub-heavy orchestration, and cross-provider coordination
- recent Bash mix still shows heavy orchestration families: `gh`, `bash`, `uv run`, `git`, plus direct `codex` invocations
- bare `python3` remains high overall (`2451` vs `2162` `uv run ... python`)
- corpus growth still exceeds event-time growth (`+6937` reconciliation gap)
- recent missing reads highlight unmapped knowledge/wiki and cross-repo/worktree path families rather than the old legacy work-queue cluster

Transferable learning:
- Hermes is still the highest-leverage place to improve ecosystem-wide behavior because it is the coordination layer that launches, audits, and comments across providers and repos
- runtime-policy cleanup remains valid, but the more immediate learning this cycle is classification hygiene: Hermes is generating many meta-orchestration reads that should be separated into knowledge, sibling-repo, and transient worktree families instead of being treated as generic repo drift
- when Hermes corpus growth exceeds event-time growth, downstream issue comments should explicitly describe that as classification/export expansion, not simply “more Hermes work happened”

Recommended repo targets:
- push the continued runtime-policy pressure into `#2332`
- push the stronger classification/worktree/knowledge-path learning into `#2333`

### Gemini
Recent/unassessed signal:
- `25` post-audit records across `4` runtime sessions
- unlike the prior cycle, this run is aligned with event-time activity rather than pure backfill
- recent activity is tiny and almost entirely read/search based, focused on `worldenergydata` disclosure-ingest paths
- historical drift still shows the old local queue / removed wrapper families, but that debt did not dominate the recent slice

Transferable learning:
- Gemini now contributed a small but real current-session slice, and it points more toward cross-repo read classification than toward local queue debt in the immediate term
- the legacy local queue / wrapper redirect work remains valid historically, but the newest Gemini evidence suggests the audit should keep distinguishing “current live reads” from “historical dominant debt cluster” so remediation priorities do not lag behind provider behavior
- because Gemini remains heavily `python3` weighted overall, keep runtime guidance in view, but the newest repo transfer value is still documentation/classification rather than direct provider intervention

Recommended repo targets:
- keep legacy local-queue authority learning tied to `#2312`
- add the new cross-repo/current-slice classification signal to `#2333`

## Repo ecosystem transfer actions
1. Refreshed the canonical provider audit artifacts for the new boundary.
2. Wrote this durable transfer bundle to `docs/reports/2026-04-23-provider-session-learning-transfer.md`.
3. Push Claude redirect-family and governance-surface guidance to `#2310` and `#2311`.
4. Push Hermes runtime-policy pressure to `#2332`.
5. Push Codex/Hermes/Gemini path-classification learnings to `#2333`.
6. Push Gemini legacy-local-queue continuity note to `#2312`.

## Verification points
- Audit artifacts now reflect the `2026-04-23T16:20:22Z` refresh.
- This note captures the assessed delta since `2026-04-22T00:19:59Z`.
- Repo-transfer comments should point maintainers to this bundle so the next implementation session starts from transferred learnings rather than re-mining raw logs.
