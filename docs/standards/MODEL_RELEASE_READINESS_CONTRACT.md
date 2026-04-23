# Model-Release Readiness Contract — workspace-hub

> Standing contract for how **workspace-hub** adapts its control-plane surfaces when a provider (Claude, Codex, Gemini) ships a new model or CLI version.
>
> Version: 1.0.0 | Date: 2026-04-20 | Issue: #2408
>
> Supersedes no prior document. Extends — does **not** replace — [CONTROL_PLANE_CONTRACT.md](CONTROL_PLANE_CONTRACT.md); where this document is silent, the control-plane contract governs.

---

## Scope

**In scope (this contract):** workspace-hub control-plane only — `AGENTS.md`, root provider entry surfaces (`CLAUDE.md`, `GEMINI.md`), provider adapter directories (`.claude/`, `.codex/`, `.gemini/`), `config/agents/`, `.claude/rules/`, `scripts/_core/sync-agent-configs.sh`, and [AI_REVIEW_ROUTING_POLICY.md](AI_REVIEW_ROUTING_POLICY.md).

**Out of scope (deferred to sibling/follow-up issues):**
- Tier-1 ecosystem inventory (downstream repos digitalmodel, assethold, assetutilities, worldenergydata, etc.).
- Provider-entrypoint-shape normalization (shape of `CLAUDE.md` / `GEMINI.md` / `.codex/*`).
- Runner/evaluation harness implementation.
- Model-choice / routing table changes.

A change is **workspace-hub-only** when it modifies only files under the paths listed above. Any deliverable that reaches beyond them belongs in a separate issue.

---

## Canonical Anchors

Discoverability is routed through two anchors. Everything else is evidence.

| Anchor | Role |
|---|---|
| [`AGENTS.md`](../../AGENTS.md) | workflow contract + readiness pointer |
| [`CONTROL_PLANE_CONTRACT.md`](CONTROL_PLANE_CONTRACT.md) | adapter topology + readiness cross-reference |

Provider-entry surfaces (`CLAUDE.md`, `GEMINI.md`, `.codex/**`) are **audit-only** for this contract. They remain thin adapters governed by the line limit in [`.claude/rules/coding-style.md`](../../.claude/rules/coding-style.md) ("Agent Harness Files") and MUST NOT be grown to host readiness content.

---

## Readiness Dimensions

A workspace-hub change is **model-release-ready** only if it explicitly addresses these five dimensions. Each is tested under `tests/docs/test_workspace_hub_model_release_readiness.py`.

### 1. Context-Budget Awareness

Every control-plane artifact MUST state its intended read budget (in lines, tokens, or fractions of the consumer's context window) and MUST fit within it.

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` — hard limit 20 lines (sourced from `.claude/rules/coding-style.md`).
- Standards under `docs/standards/` — no hard line cap, but each MUST open with a two-line scope/version block so truncated loads still carry identity.
- New provider-entry content MUST go to a referenced skill or doc before it grows an adapter past its budget.

### 2. Truncation-Safe Artifact Design

Artifacts MUST assume the reader may receive only the first N kilobytes.

- Identity (title, version, scope, cross-references) MUST appear in the first 500 bytes.
- Normative requirements MUST precede motivational prose.
- Tables/bullets precede paragraphs; prose is a last-resort encoding.
- Anchors (`[Name](path)`) MUST use repo-relative paths so they survive copy-paste.

### 3. Machine-Readable vs Prose Guidance

Prefer machine-readable encodings over free-form prose wherever a rule has a binary or enumerable shape.

- Rules with a yes/no answer → script or pre-commit hook (see `.claude/rules/patterns.md` enforcement gradient).
- Rules with an enumerable scope → table/list in a standard.
- Prose is acceptable only for motivation, rationale, or gray areas the script/table cannot express. **Every prose block MUST sit next to the machine-readable rule it explains, not replace it.**

### 4. Prompt-Pack Portability

Any prompt, skill, or workflow the workspace-hub ships MUST be portable across providers and machines.

- Paths referenced MUST be repo-relative and valid on every active machine (Linux/Windows).
- No hardcoded absolute paths (per `.claude/rules/coding-style.md` "Path Handling").
- Provider-only features (e.g., Claude skills, Codex sandbox constraints) MUST be declared explicitly; a fallback path MUST exist for providers that lack them or the prompt pack MUST fail-closed.
- Cross-provider review obligations follow [AI_REVIEW_ROUTING_POLICY.md](AI_REVIEW_ROUTING_POLICY.md); the readiness contract does not redefine them.

### 5. Discoverability

A new control-plane artifact is "discovered" only if both canonical anchors point to it. Adding a file without updating `AGENTS.md` or `CONTROL_PLANE_CONTRACT.md` is a readiness defect even if every other dimension is met.

---

## Required Operational Surfaces

These files exist today and remain the operational truth for config drift:

- `config/agents/claude/settings.json`
- `config/agents/codex/config.toml`
- `config/agents/gemini/settings.json`
- `scripts/_core/sync-agent-configs.sh`

Any readiness change that affects provider configuration MUST route through `scripts/_core/sync-agent-configs.sh` rather than hand-edits.

---

## Relationship to Other Standards

| Document | Relationship |
|---|---|
| [CONTROL_PLANE_CONTRACT.md](CONTROL_PLANE_CONTRACT.md) | parent — defines adapter topology; this contract inherits it |
| [AI_REVIEW_ROUTING_POLICY.md](AI_REVIEW_ROUTING_POLICY.md) | sibling — owns cross-provider review rules |
| [MODEL_RELEASE_UPGRADE_PLAYBOOK.md](MODEL_RELEASE_UPGRADE_PLAYBOOK.md) | procedural companion — enacts the dimensions above |
| [`.claude/rules/coding-style.md`](../../.claude/rules/coding-style.md) | source of truth for the 20-line harness file limit |

If this contract disagrees with `CONTROL_PLANE_CONTRACT.md` on adapter paths, the control-plane contract wins.

---

## Validation

Automated: `uv run pytest tests/docs/test_workspace_hub_model_release_readiness.py -v`

The test file enforces each dimension above with concrete assertions (named sections, path references, line-count sourced from `.claude/rules/coding-style.md`).
