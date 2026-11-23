# Decision record — Model parity after Fable 5 loss (Opus-equivalent ecosystem)

- **Date:** 2026-06-14
- **Status:** Accepted (decisions ratified 2026-06-13; flip implemented in #3051 / PR #3088)
- **Epic:** [#3043](https://github.com/vamseeachanta/workspace-hub/issues/3043) · **Harden epic:** [#3058](https://github.com/vamseeachanta/workspace-hub/issues/3058)

## Context

Access to the **Fable 5** model (`claude-fable-5`) — the prior premium, 1M-context primary — was lost. The ecosystem routed its hardest reasoning (Route C planning, cross-review) and large-context work through Fable. The objective: make the ecosystem **Opus-equivalent** so work continues at the same pace and quality, with model selection flowing through the single-source registry (`config/agents/model-registry.yaml`), not scattered hardcodes.

A 193-session analysis of the Fable corpus ([`analysis/2026-06-13-fable5-opus-parity-learning.md`](../../analysis/2026-06-13-fable5-opus-parity-learning.md)) showed the residual risk is **behavioral, not capacity** once the 1M-context gap is closed.

## Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | `latest_models.claude_primary` → **`claude-opus-4-8[1m]`** (1M-context Opus) | Closest Fable equivalent for pace + quality + large-context; closes the capacity gap directly. |
| 2 | Route C `plan` + Route B/C cross-review → **1M-Opus** (via `claude_primary`) | Preserves the "reviewer out-reasons the Sonnet author" gate; complex plans keep full-codebase context. |
| 3 | `claude-fable-5` → **`deprecated: true`**, retained | Keep for audit/history + one-line re-enable; nothing routes to it (`default_priority: 0`). |
| 4 | Routine work stays **`sonnet-4-6`** | Cost discipline; only the heavy lanes ride 1M-Opus. |
| 5 | Compound Engineering review fan-out **12 → 4–6** on Opus | Avoid draining the weekly quota per `/compound` run. |
| 6 | `/fast` mode **manual-only** | Direct "same pace" lever; not auto-routed. |

## Consequences

- **Cost/quality trade (accepted):** cross-review and Route C planning now ride 1M-Opus by default — premium per run, deliberately chosen to hold pace. Routine work is unaffected (Sonnet).
- **Behavioral deltas to watch** (from the corpus analysis, instrumented by #3061): D1 output verbosity (Opus ~3–5× Fable in loop work) and D2/D3 autonomy-confidence + adversarial-stance. The parity sentinel (`scripts/ai/parity-sentinel.sh`) alerts on regression vs the Fable baseline; first live run already flagged a D2 clarification-break increase.
- **Equivalence is enforced, not assumed:** the drift sentinel (#3059) hashes the registry + each provider's `SOUL.runtime.md` (#3074) across machines; the #3060 ratchet guard blocks new hardcoded model IDs.

## Implementation deviations (with cause)

1. **No `claude-fable-5 → claude-opus-4-8[1m]` migration in `update-model-ids.sh`.** Its blanket `sed` (no `config/agents`/`analysis/` exclusion) would corrupt the *intentional* fable references — the deprecated registry entry, `analysis/parity-baseline.json`, and `scripts/ai/transcript-digest.py` model-tagging. The #3060 ratchet guard catches new fable hardcodes non-destructively.
2. **Stale doc-IDs deferred** (`agent-usage-optimizer` `claude-opus-4-6`, `agent-library` `claude-sonnet-4.5`, mlops guidance, and the `provider-capabilities.yaml` horizon narrative) — out of the flip's critical path and outside the #3060 scope; focused follow-up.

## How to swap the primary model next time

See the **Primary Model Swap — Checklist** in [`docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md`](../standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md). The intent of this whole effort: the next swap is a registry edit + a short reader checklist, not archaeology.
