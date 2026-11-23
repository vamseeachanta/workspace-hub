# Provider routing system handoff — 2026-04-13

## Status
The provider-routing control plane is now operational and refreshed on a recurring basis.

Implemented artifacts:
- `config/ai-tools/provider-utilization-weekly.json`
- `docs/reports/provider-utilization-weekly.md`
- `config/ai-tools/provider-routing-scorecard.json`
- `docs/reports/provider-routing-scorecard.md`
- `config/ai-tools/provider-work-queue.json`
- `docs/reports/provider-work-queue.md`
- `config/ai-tools/provider-autolabel-candidates.json`
- `docs/reports/provider-autolabel-candidates.md`

Supporting scripts:
- `scripts/ai/credit-utilization-tracker.py`
- `scripts/ai/provider-routing-scorecard.py`
- `scripts/ai/provider-work-queue.py`
- `scripts/ai/provider-autolabel.py`
- `scripts/cron/provider-utilization-refresh.sh`

Recurring schedule:
- `provider-utilization-refresh` in `config/scheduled-tasks/schedule-tasks.yaml`
- installed into local crontab at `20 */4 * * *`

## Current live routing posture
Recommended provider order from the latest scorecard:
1. Gemini
2. Codex
3. Claude

Interpretation:
- Gemini should receive batched research/recon work first when confidence is sufficient.
- Codex should receive bounded implementation/test/refactor work.
- Claude should stay focused on adversarial review, planning, synthesis, and architecture-heavy work.

## Conservative auto-labeling state
High-confidence auto-labeling is now available with guardrails:
- only issues without existing `agent:*` labels are considered
- only candidates with confidence >= 0.90 are eligible
- apply mode is limited and conservative

Live apply performed on 2026-04-13:
- `#2227` -> `agent:codex`
- `#2248` -> `agent:claude`
- `#2129` -> `agent:claude`

## Future issues created
New follow-on GitHub issues:
- `#2252` — `feat(provider-routing): add explanatory comments for high-confidence auto-label actions`
- `#2253` — `feat(provider-routing): harden Gemini auto-label confidence with research-readiness signals`
- `#2254` — `fix(provider-telemetry): improve Claude and Gemini quota observability for exact weekly targeting`

Related existing issues worth consulting:
- `#1838` — AI credit utilization governance
- `#2052` — queue refresh / focus and dependency-chain generation
- `#2089` — weekly Hermes + AI provider settings review

## Exit-ready operating instructions
Refresh everything:
```bash
bash scripts/cron/provider-utilization-refresh.sh
```

View latest routing recommendations:
```bash
read_file docs/reports/provider-routing-scorecard.md
read_file docs/reports/provider-work-queue.md
read_file docs/reports/provider-autolabel-candidates.md
```

Dry-run auto-label review:
```bash
uv run --no-project python scripts/ai/provider-autolabel.py
```

Conservative live apply:
```bash
uv run --no-project python scripts/ai/provider-autolabel.py --apply --limit 3
```

## Remaining guardrails
- Claude weekly utilization is still heuristic when quota remains unavailable.
- Gemini utilization remains partly heuristic until better telemetry is implemented.
- Auto-labeling should remain conservative until `#2253` and `#2254` are complete.
- Existing explicit `agent:*` labels continue to override heuristic routing.
