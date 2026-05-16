# Gemini Provider Delta
> Inherits identity, gates, and must-fire rules from [`../SHARED_SOUL.md`](../SHARED_SOUL.md). This file carries only Gemini-specific operating-model differences.
> Runtime artifact: [`./SOUL.runtime.md`](./SOUL.runtime.md) (built by `scripts/agents/build-soul-runtime.sh`).

# Gemini-Specific Operating Model

## Sandbox Overlay Blindness

**Gemini sandbox cannot see sparse-checkout overlays.** When workspace-hub uses sparse-checkout on `ace-linux-1` (e.g., `~/workspace-hub` overlay), Gemini's `read_file` returns "not found" for files that exist in the canonical mount `/mnt/local-analysis/workspace-hub/`. Symptom: false-positive "file missing" findings (e.g., 54 such findings on the 2026-04-23 batch). (`feedback_gemini_sandbox_overlay_blindness`)

Mitigation: before trusting Gemini's "file missing" assertions, locally verify with `git ls-files <path>` (canonical mount). For cross-review, prefer passing tracked-file SHAs/paths the Gemini sandbox can resolve.

## Authentication and Quota

- **Google AI Pro** subscription ($20/mo) provides the paid Gemini surface via `gemini` CLI.
- **Google CLI (paid)** provides GWS API access (Calendar, Drive, etc.) at the user's seat.
- Quota exhaustion is hard-stop: `TerminalQuotaError` with `code: 429`, reset window typically 8h+ ahead of the failure. Document failures as `UNAVAILABLE` per `scripts/review/results/` convention; do NOT retry within the reset window. (Verified 2026-05-15 r2 attempt on [#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719))

## Cross-Review Role

Gemini is the **3rd-opinion provider** on T3 reviews (Claude orchestrator + Codex executor-reviewer + Gemini independent). Gemini is **not authorized for implementation by default** — review-only unless explicitly enabled by the user.

Invocation pattern:
```bash
cat <prompt> | gemini -p "" -y     # YOLO mode for auto-approve; -p "" since prompt is on stdin
```

## Agent Loading

- Gemini loads agents from `.gemini/agents/*.md` with schema validation.
- Schema mismatches (e.g., `permissionMode` key not recognized) produce loader warnings at startup. Inspect with `gemini` start log.
- Skill conflicts: workspace `.agents/skills/<name>/` overrides `.gemini/skills/<name>/` when both exist.

## Ripgrep Fallback

Gemini's environment may report `Ripgrep is not available. Falling back to GrepTool.` on startup. This is informational; the GrepTool fallback works but is slower. Don't surface this as a defect.

## Known Hazards

- Sandbox model differs from Codex sandbox; both fail differently on local filesystem ops, but Gemini failures are less common (Gemini typically runs cleanly via GH connector when needed).
- YOLO mode (`-y`) bypasses tool-call approval — only use for self-contained review prompts, not for implementation.

## Skill Loader

- `.gemini/skills/` is the Gemini-side skill tree, populated by parallel structure to `.claude/skills/`. Migrations from `.claude/skills/` happen when a skill is generalized.
