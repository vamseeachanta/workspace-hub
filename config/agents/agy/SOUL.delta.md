# Agy Provider Delta
> Inherits identity, gates, and must-fire rules from [`../SHARED_SOUL.md`](../SHARED_SOUL.md). This file carries only Agy-specific (Antigravity CLI, Gemini-backed) operating-model differences.
> **Reference artifact only**: [`./SOUL.runtime.md`](./SOUL.runtime.md) — built for review parity by `scripts/agents/build-soul-runtime.sh`. agy loads workspace context from the `GEMINI.md` family, not `SOUL.md`; the operational surface is workspace [`GEMINI.md`](../../../GEMINI.md).

# Agy-Specific Operating Model

## Headless Dispatch Contract (#3207)

- The prompt is the VALUE of `--print` (`--prompt` is an alias): `agy --print "<TEXT>" --print-timeout 240s`. NEVER pass content as a trailing positional.
- `--print-timeout` takes a Go duration (`"240s"`), not integer seconds.
- agy **ignores stdin** — content rides the `--print` value (argv), so payloads are ARG_MAX-bounded (`AGY_MAX_BYTES`, default 1 MB).
- Freeform text out — **no JSON mode**. Review prompts must demand a `VERDICT: APPROVE | MINOR | MAJOR` trailer; `normalize-verdicts.sh` extracts it tolerantly (case/markdown-bold/punctuation).

## Review Lane Rules (#3573)

- Agy is the **third worker/reviewer provider** (Claude + Codex + Agy). Dispatch via `scripts/review/submit-to-agy.sh`.
- `AGY_REVIEW_MODE=1` in review dispatches: an oversize payload **fails the dispatch (exit 3)** instead of truncating — a truncated review can silently false-APPROVE.
- An artifact that exists but fails verdict parsing is `INVALID_OUTPUT` and **blocks** the round; only provider-UNAVAILABLE (429 / non-zero exit with no artifact) degrades T3 → T2.

## Authentication, Settings, and Quota

- Rides the **Google AI Pro** seat via Antigravity OAuth/Code Assist; the agy quota pool is separate from the legacy gemini CLI pool (Gemini 3.1 Pro does not 429 here as of 2026-07).
- Settings live at `~/.gemini/antigravity-cli/settings.json`; the default model is persisted as a **display label** (`"Gemini 3.1 Pro (High)"`) — pinned across machines by `scripts/agents/set-antigravity-default-model.sh` (#3086).
- Self-updates via `agy update` (standalone binary at `~/.local/bin/agy`; no npm package).
- Quota exhaustion (429) is hard-stop: document as `UNAVAILABLE` per `scripts/review/results/` convention; do NOT retry within the reset window.

## Cross-Review Role

Agy is the **3rd-opinion provider** on T3 reviews (Claude orchestrator + Codex executor-reviewer + Agy independent) and the **cheap fallback/delegation lane** under the cost ceiling (#3192). Agy is **not authorized for implementation by default** — review/delegation unless explicitly enabled by the user.
