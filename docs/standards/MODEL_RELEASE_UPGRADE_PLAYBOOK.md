# Model-Release Upgrade Playbook — workspace-hub

> Concrete, ordered steps for adopting a new provider/model release (Claude, Codex, or Gemini) **inside workspace-hub only**.
>
> Version: 1.0.0 | Date: 2026-04-20 | Issue: #2408 | Contract: [MODEL_RELEASE_READINESS_CONTRACT.md](MODEL_RELEASE_READINESS_CONTRACT.md)

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
5. Verify each adapter file remains within the line limit in `.claude/rules/coding-style.md`. If an upgrade would push an adapter past the limit, migrate the new content to a skill or `docs/` doc first.
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

## Reference

- Contract dimensions — [MODEL_RELEASE_READINESS_CONTRACT.md](MODEL_RELEASE_READINESS_CONTRACT.md)
- Adapter topology — [CONTROL_PLANE_CONTRACT.md](CONTROL_PLANE_CONTRACT.md)
- Cross-review obligations — [AI_REVIEW_ROUTING_POLICY.md](AI_REVIEW_ROUTING_POLICY.md)
- Path & edit rules — [`.claude/rules/coding-style.md`](../../.claude/rules/coding-style.md)
- Enforcement gradient — [`.claude/rules/patterns.md`](../../.claude/rules/patterns.md)
- Config sync — `scripts/_core/sync-agent-configs.sh`
- Registry — `config/agents/ai-agents-registry.json`
