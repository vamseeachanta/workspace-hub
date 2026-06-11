# config/agents — AI provider configuration

## Model-selection override hierarchy (#3038)

When a script or agent needs a model ID, resolution order is:

1. **Explicit env override** (e.g. `CODEX_OPUS_MODEL=...`) — always wins.
2. **Local runtime config** — `~/.codex/config.toml`, `~/.hermes/config.yaml`.
   This is the *operational truth* for what Codex/Hermes actually run; it is
   machine-specific and never repo-tracked.
3. **Repo registry** — `model-registry.yaml` `latest_models` + `context_windows_k`.
   Read it via `scripts/lib/model-registry.sh` (`registry_model`, `registry_ctx_k`)
   or the inline regex readers in `session-params.py` / `overnight-batch-planner.py`.
   Scripts MUST NOT hardcode model IDs (behavior-contract.yaml > model_versioning).
4. **In-script fallback constants** — only reached when the registry is absent
   (e.g. a copied script outside the repo).

Drift between layers 2 and 3 is surfaced nightly by the `R-MODEL-DRIFT` check in
`scripts/readiness/nightly-readiness.sh` — when it fails, update
`model-registry.yaml` to match the live config (or vice versa, deliberately).

## File map

| File | Role | Hand-edit? |
|---|---|---|
| `SHARED_SOUL.md` | cross-provider identity/gates source | yes |
| `<provider>/SOUL.delta.md` (`hermes/SOUL.md`) | per-provider delta source | yes |
| `<provider>/SOUL.runtime.md`, `codex/AGENTS.runtime.md` | built artifacts (`scripts/agents/build-soul-runtime.sh`) | **never** |
| `model-registry.yaml` | model IDs, tiers, pricing, context windows, phase routing | yes (keep `last_updated` fresh) |
| `provider-capabilities.yaml` | per-provider strengths/roles/use-cases | yes |
| `routing-config.yaml` | task-type → provider routing spec (not a live router) | yes |
| `behavior-contract.yaml` | cross-provider working agreements | yes |
| `ai-agents-registry.json` | legacy agent registry (dormant automation only) | discouraged |
| `user-profile.yaml` | owner profile/subscriptions | yes |

## Provider quick truth (2026-06-11)

- **Claude** — interactive sessions (Claude Code, Max). Fable 5 / Opus 4.8 / Sonnet 4.6 / Haiku 4.5.
- **Codex** — review lane + delegation target; CLI runs the model in `~/.codex/config.toml` (gpt-5.5).
- **Hermes** — automation engine; runs gpt-5.5 via the openai-codex provider. NOT a Claude wrapper.
- **Gemini** — third review lane; 2.5-pro is the dependable primary (3.1-pro-preview quota-starved on Pro plan).
