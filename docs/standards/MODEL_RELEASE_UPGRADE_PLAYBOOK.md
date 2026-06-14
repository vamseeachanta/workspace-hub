# Model-Release Upgrade Playbook — workspace-hub

> Concrete, ordered steps for adopting a new provider/model release (Claude, Codex, or Gemini) **inside workspace-hub only**.
>
> Version: 1.0.0 | Date: 2026-04-20 | Issue: #2408 | Contract: [MODEL_RELEASE_READINESS_CONTRACT.md](MODEL_RELEASE_READINESS_CONTRACT.md)
> Read budget: procedural companion — opening block identifies scope/contract; numbered steps carry the executable content.

This playbook enacts the five readiness dimensions defined in the contract. It does **not** cover tier-1 downstream repos or provider-entrypoint-shape normalization — those belong to sibling issues.

---

## Step 0 — Classify the Drift

Every release produces two drift categories. Handle them on separate branches of this playbook; they never share a commit.

### Provider-Owned Drift

Changes that originate in the provider's release notes and the workspace-hub repo merely *accepts*:

- New model ID (e.g., `claude-opus-4-8`, `gemini-3.0-pro`).
- New CLI flag, deprecation, or breaking syntax change.
- New prompt-cache/limits behavior.
- New framework-specific skill or tool.

These drifts are tracked by the provider. Workspace-hub's response is only to *reconcile* `config/agents/<provider>/` and `AGENTS.md` routing, not to invent behavior.

### Repo-Owned Drift

Changes that originate inside workspace-hub regardless of provider release:

- New control-plane surface (standard, rule, skill).
- New routing policy or review obligation.
- New machine-readable enforcement (hook, script).
- New entry in `config/agents/ai-agents-registry.json`.

These drifts require a plan, tests, and explicit cross-review per [AI_REVIEW_ROUTING_POLICY.md](AI_REVIEW_ROUTING_POLICY.md).

**Mixing the two in one PR is a review-blocker.** Split by drift category before proceeding.

---

## Step-by-Step — Provider-Owned Drift

1. Read the upstream release notes. Record the effective date, model ID changes, CLI changes, and any caching/context-window deltas in the upgrade issue.
2. Update provider config under `config/agents/<provider>/` — **not** the root entry surfaces. Only the provider directory owns model identity.
3. Run `bash scripts/_core/sync-agent-configs.sh --dry-run` to preview sync actions from `config/agents/` templates into the machine-local provider targets (`$HOME/.claude/settings.json`, `$HOME/.codex/config.toml`, etc.). Fix divergence by editing the `config/agents/` templates and re-running without `--dry-run`; never hand-edit the machine-local targets.
4. Audit `CLAUDE.md`, `GEMINI.md`, and `.codex/**` for stale references (old model IDs, removed flags). Apply a single-site edit per stale reference; do not rewrite the adapter.
5. Verify each harness-capped adapter file remains within the line limit in `.claude/rules/coding-style.md`. Today that policy applies to `CLAUDE.md` and `GEMINI.md` (and other named harness files), not to the entire `.codex/**` tree. If an upgrade would push a harness-capped adapter past the limit, migrate the new content to a skill or `docs/` doc first.
6. Run `uv run pytest tests/docs/test_workspace_hub_model_release_readiness.py -v` and the adapter-specific suite under `scripts/_core/tests/`.
7. Open the PR with the issue number, a "provider-owned" label, and explicit "no repo-owned changes" note in the description.

---

## Step-by-Step — Repo-Owned Drift

1. Open an issue and follow the standard plan workflow (`docs/plans/_template-issue-plan.md`). Readiness changes are never skipped to "fast track."
2. Classify the artifact against the five contract dimensions (Context-Budget, Truncation-Safe, Machine-Readable vs Prose, Prompt-Pack Portability, Discoverability). Record which dimension each file serves.
3. For every new machine-readable rule, decide its enforcement tier against `.claude/rules/patterns.md` (prose / micro-skill / script / hook). Default toward stronger tiers.
4. Write tests first. If the change affects `AGENTS.md` or `CONTROL_PLANE_CONTRACT.md` anchors, extend `tests/docs/test_workspace_hub_model_release_readiness.py`; otherwise add a targeted doc test alongside the change.
5. Update both canonical anchors (`AGENTS.md`, `CONTROL_PLANE_CONTRACT.md`) in the same commit that introduces the new artifact. An artifact without both anchors MUST NOT merge.
6. Run `uv run pytest tests/docs/` and any surface-specific validators referenced in `AGENTS.md`.
7. Send the PR through the cross-provider review required by [AI_REVIEW_ROUTING_POLICY.md](AI_REVIEW_ROUTING_POLICY.md); do not bypass MINOR/MAJOR resolution.

---

## Prompt-Pack Portability Checks

Every new prompt, skill, or workflow MUST satisfy these before merge:

- Uses repo-relative paths resolved from `$(git rev-parse --show-toplevel)` or `${REPO_ROOT}`; no absolute paths outside tool-required parameters.
- Does not assume a single provider's capability without a declared fallback.
- Does not rely on machine-local state (`~/.claude/`, personal memory snapshots) — provider/machine-local files MUST have a checked-in equivalent under `config/agents/`.
- Passes a round-trip test: copying the prompt text into an unrelated provider session produces actionable behavior or a clear "not supported here" failure, not silent misbehavior.

---

## Rollback

If a release triggers regressions:

1. Revert the last-known-good sha for `config/agents/<provider>/` and rerun `scripts/_core/sync-agent-configs.sh`.
2. File a follow-up issue that lists the observed failure modes; do not silently leave the upgrade half-applied.
3. Restore adapter files from `git show HEAD~1:<path>` rather than hand-editing; hand-edits during rollback risk line-limit drift.

---

## Primary Model Swap — Checklist (worked example: #3051, Fable 5 → Opus 4.8 1M)

When the **default Claude model changes** (a provider deprecates one, or a better tier ships), the swap is a single-source registry edit + its readers. Follow in order; everything keys off `config/agents/model-registry.yaml`. Decision record: [`docs/governance/2026-06-14-model-parity-decision.md`](../governance/2026-06-14-model-parity-decision.md).

1. **Registry — `config/agents/model-registry.yaml`** (the single source):
   - Add the new tier block under `providers.claude.models` (`model_id`, `capability_tier`, context, `recommended_use`). For a context variant, the id carries a suffix, e.g. `claude-opus-4-8[1m]`.
   - Set `latest_models.claude_primary` to the new id.
   - Add the new id to `context_windows_k`.
   - Mark the outgoing model `deprecated: true` + `default_priority: 0` — **keep the entry** for audit; do not delete.
   - Point `work_queue_routing.route_c.plan` at the new tier; refresh `cross_review` comments (it tracks `claude_primary`, no logic change).
   - Leave `default_model: sonnet-4-6` (routine work) unless that too is changing.
2. **Propagate to the readers** (verified set):
   - `scripts/ai/session-params.py` — `FALLBACK_CTX_MAP` + `ALIAS_MAP` (add the new alias; forward deprecated aliases to the new primary). The `[Nm]` suffix parser already yields the window.
   - `scripts/ai/overnight-batch-planner.py` — the `_registry_model(..., "<fallback>")` literal.
   - `config/agents/behavior-contract.yaml` — the `# Today: <id>` comment.
   - `config/agents/provider-capabilities.yaml` — `model_ids.primary` + `context_window.primary`.
3. **Verify (gate 2):**
   - `python -c "import yaml; yaml.safe_load(open('config/agents/model-registry.yaml'))"` parses (bracketed ids are fine as quoted strings).
   - `source scripts/lib/model-registry.sh && registry_model claude_primary` returns the new id (the `sed` extracts `[^"]+`, so `[1m]` is safe).
   - `session-params.py` `ctx_k(<new id>)` returns the right window.
   - The #3060 model-id-sourcing guard is green — annotate any new literal with `# model-id-ok` (it's a deliberate registry fallback/alias).
4. **DO NOT add the old→new pair to `scripts/maintenance/update-model-ids.sh`.** That script does a blanket `sed` across the whole tree (no `config/agents` or `analysis/` exclusion), so it would corrupt the *intentional* references to the deprecated id: the deprecated registry block, `analysis/parity-baseline.json`, and `scripts/ai/transcript-digest.py` model-tagging. Reintroduction of a stale hardcode is already caught **non-destructively** by the #3060 ratchet guard.
5. **Sentinel inheritance:** the equivalence sentinel (#3059) hashes `model-registry.yaml` + each provider's `SOUL.runtime.md` (#3074) across machines — no change needed; it will flag if a box doesn't pick up the swap. The behavioral baseline (#3061, `analysis/parity-baseline.json`) is the *old* model's profile — leave it as the comparison reference; regenerate only when establishing a new baseline.

---

## Reference

- Contract dimensions — [MODEL_RELEASE_READINESS_CONTRACT.md](MODEL_RELEASE_READINESS_CONTRACT.md)
- Adapter topology — [CONTROL_PLANE_CONTRACT.md](CONTROL_PLANE_CONTRACT.md)
- Cross-review obligations — [AI_REVIEW_ROUTING_POLICY.md](AI_REVIEW_ROUTING_POLICY.md)
- Path & edit rules — [`.claude/rules/coding-style.md`](../../.claude/rules/coding-style.md)
- Enforcement gradient — [`.claude/rules/patterns.md`](../../.claude/rules/patterns.md)
- Config sync — `scripts/_core/sync-agent-configs.sh`
- Registry — `config/agents/ai-agents-registry.json`
