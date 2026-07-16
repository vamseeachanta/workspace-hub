---
name: agy-replaces-gemini-cli
description: "User directive 2026-07-16: AGY (Antigravity CLI) is the Gemini-backed provider surface; use agy for new dispatch/review instead of the legacy gemini CLI."
metadata:
  node_type: memory
  type: feedback
---

# AGY is the Gemini-backed CLI surface

The user confirmed on 2026-07-16 that the ecosystem's Gemini lane has changed to **AGY**. When AGY is installed and authenticated on the target machine, use the Antigravity CLI as `agy` for new provider dispatch and review; do not retry the legacy `gemini` binary and interpret its authentication failure as proof that the Gemini-backed lane is unavailable.

Operational contract:

- Human-facing provider name: **AGY (Gemini-backed)**.
- Headless wrapper: `scripts/review/submit-to-agy.sh`.
- The tracked wrapper records the empirically confirmed direct headless shape as `agy --print "<prompt>" --print-timeout 240s --dangerously-skip-permissions` (`scripts/review/submit-to-agy.sh:7-13`, `:88-95`).
- The tracked wrapper states that the prompt is the value of `--print`, AGY ignores stdin, and input is capped below `ARG_MAX` (`scripts/review/submit-to-agy.sh:7-13`, `:60-66`).
- Internal schemas may retain a `gemini` provider token where the existing routing/config contract requires it. Do not blindly rename persisted keys, historical artifacts, or issue labels.
- Always verify `agy` on the live machine before dispatch. On `ace-win-2` on 2026-07-16, neither PowerShell nor interactive Git Bash could resolve `agy`; `scripts/review/submit-to-agy.sh` exists, but the CLI must be installed and authenticated before it can provide review evidence.

Evidence verified in the tracked tree at commit `7e0ec3f4ab021245c5ea2d441a81f9350a2bfbb9`: `scripts/review/submit-to-agy.sh:2-19`, [#3207](https://github.com/vamseeachanta/workspace-hub/issues/3207), `docs/plans/2026-06-18-issue-3207-agy-headless-dispatch.md:31-33`, and `docs/session-handoffs/2026-06-14-agy-gemini-statusline-rollout.md:7-17`.

Current retrieval limitation: the topic is indexed and `scripts/memory/recall.py agy` returns it, but the capped provider startup slice may omit newer shared `KNOWLEDGE.md` entries after higher-volume auto-memory fills the cap. Follow-up: [#3558](https://github.com/vamseeachanta/workspace-hub/issues/3558).
