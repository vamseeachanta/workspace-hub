> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-17
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_cli_0_124_upstream_regression.md

---
name: codex-cli-stdin-detection-hang-reopened-2026-05-16-0-130-0-hangs-non-deterministically
description: "Feedback originally 2026-04-24 — codex-cli 0.124.0+ has a stdin-detection regression. 2026-05-11 marked it RESOLVED on 0.130.0; 2026-05-16 reverification proves the hang reproduces non-deterministically on 0.130.0 even with `</dev/null` workaround. Downgrade does NOT help (user-verified). Treat codex as unreliable until upstream investigates the TTY-vs-pty / invocation-context dimension."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c33ac478-fe2b-456e-b884-3c68d71720c2
---

## Current status — 2026-05-16 (TTY-faking + CLAUDECODE-env-unset workarounds identified)

Codex 0.130.0 hangs in non-TTY invocation contexts (cron, background, subshell, Hermes worker, Claude Code Bash with `run_in_background=true`). The hang is **TTY-detection-layer**: codex probes `isatty(0)` and if false, enters a stdin-waiting state that even `</dev/null` does NOT defeat. The reliable workarounds are:

1. **`script -qc 'codex exec "..."' /dev/null`** — provides a pseudo-TTY, defeats `isatty(0)` detection. Wall time ~41s for a simple prompt.
2. **`env -u CLAUDECODE bash <script-invoking-codex>`** — unsetting the `CLAUDECODE=1` env var (auto-set by Claude Code Bash tool) defeats a separate codex-side fast-path that detects "running under Claude Code" and short-circuits to the hang. Empirically validated 2026-05-16 evening session: original `plan-review-fanout.sh` invocation returned UNAVAILABLE with this exact diagnosis string; retrying via `env -u CLAUDECODE bash plan-review-fanout.sh ... --providers=codex` succeeded with a substantive MAJOR review (8 findings, 4911 bytes) in ~3 minutes.

The two workarounds address different sub-paths of the same TTY-detection bug class. `env -u CLAUDECODE` is sufficient for Claude-Code-Bash-invoked codex; `script -qc` is the broader fallback for any non-TTY context (cron, daemon-spawned, etc.) where the CLAUDECODE env isn't the trigger.

The 2026-05-11 "RESOLVED" marker was actually correct for **TTY contexts** (interactive shells, foreground); it just didn't generalize to non-TTY contexts. The 2026-05-15 "auth-layer hang" diagnosis was incorrect — `codex login status` returns instantly when an interactive shell or TTY-faked call is used.

The symptom shape (visible) is a literal "Reading additional input from stdin..." banner printed to stdout, with no further output until timeout. The TTY-emulated form prints the full "OpenAI Codex v0.130.0 / workdir: / model: ..." banner immediately on success.

**Why:** Every `scripts/review/cross-review.sh` / Hermes-dispatched codex call / `/goal` hand-delegation goes through codex exec. Silent hang = silent verdict drop. Per [[feedback_cross_provider_review_payoff]], codex carries unique defect-detection signal — when it falls out, the "consensus MAJOR" pattern weakens to a 2-provider read. Treating codex as DEAD is more honest than treating it as INTERMITTENT.

**How to apply:**

1. **For non-TTY invocations (cron, background, Hermes worker, Claude Code `run_in_background=true`), wrap with `script -qc`**: `timeout 90 script -qc 'codex exec "..."' /dev/null`. This provides a pseudo-TTY and defeats the TTY-detection hang. Wall time ~41s for a simple prompt; budget 300s for review-sized prompts.
2. **Do not retry on hang.** The bug is TTY-detection-layer; retrying with same invocation pattern reproduces the same hang. Switch to `script -qc` before retrying.
3. **`</dev/null` ALONE is NOT sufficient** on 0.130.0. The 2026-04-20 wrapper comment at `submit-to-codex.sh:197-220` claims `</dev/null` is the fix — that was true for 0.121.0 but is stale today. `script -qc` is the necessary condition; `</dev/null` is incidental.
4. **Do not downgrade.** User verified 2026-05-15 that 0.123.0 hangs identically. Memory's pre-2026-05-11 advice to downgrade is OBSOLETE.
5. **Do not invoke `codex login status` to test "is codex broken".** That command currently exits 0 instantly (auth-layer works), which gives a false-positive "codex is fine" signal. Use the actual `codex exec` reproducer.
6. **In adversarial review prompts**, explicitly frame Codex as "currently expected UNAVAILABLE-or-degraded on 0.130.0 — 2-provider consensus (Claude + Gemini) is the operational reality until upstream fix." See [[feedback_cross_provider_review_payoff]].
7. **Do not mark a plan "ready for approval" based solely on Codex UNAVAILABLE + Claude+Gemini clean.** Surface the 2-provider limitation. Per [[feedback_codex_sustained_major_loop]], sustained-MAJOR loop-break should also be evaluated against the possibility that codex was simply unavailable, not actually MAJOR.
8. **Cross-review.sh fallback**: single-author r3 with transparent provenance remains the right fallback per [[feedback_permission_gate_blocks_cross_review]] when codex falls out.
9. **Hermes default profile** routes to `openai-codex` which shells out to `codex exec` per [[feedback_hermes_provider_openai_codex_routes_via_codex_exec]]. Hermes config (as of 2026-05-16) has NO non-codex provider stanza populated: `providers: {}` empty, `fallback_providers: []` empty. Flipping the default would require new provider config work, not just a flag.
10. **Kanban-worker dispatch** through Hermes default profile inherits this hang ([#2718](https://github.com/vamseeachanta/workspace-hub/issues/2718) confirmed 60-minute SIGTERM timeout with 1.5% CPU utilization). Don't dispatch tool-using prompts via the default profile until #2715 closes.

## Diagnostic evidence (2026-05-16)

Strace of `timeout 30 codex exec "Reply..."` (no `</dev/null`):
- 46,668 syscall lines total
- 21× `connect()` to chatgpt.com IPs on port 443 (140.82.114.4, 172.64.155.209, 104.18.32.47, IPv6 equivalents); also to localhost DNS (127.0.0.53:53)
- 36× `sendto()` carrying TLS handshake data
- 11,064× `recvfrom()` reading response data
- Process never emits the "OpenAI Codex v0.130.0" banner; stays at "Reading additional input from stdin..."

So codex IS making network calls and receiving data — it's not network-blocked, not auth-blocked, not locale-blocked. The hang is between successful API call and stdin-state-reconciliation.

Test matrix (`timeout 90 codex exec "Reply with exactly: hello" </dev/null`):
| Invocation context | Result |
|---|---|
| Interactive foreground bash (Claude Code Bash tool, direct) | ✅ exit=0, full banner + completion |
| Subshell bash (Claude Code Bash tool, `run_in_background=true`) | ❌ Hung 90s, only banner printed |
| Subshell bash via `bash -c '...'` | ❌ Hung 30s+ |

Inconsistent. The TTY-vs-pty / inherited-stdin dimension is the suspected next-investigation target.

## Rejected hypotheses (already tested, don't retry)

- ❌ Locale-fix: `LC_ALL=POSIX`, `LANG=C LC_ALL=C` — no effect (user 2026-05-15)
- ❌ Fresh OAuth: `codex login` handshake completes cleanly, but `codex exec` still hangs (user 2026-05-15)
- ❌ Auth-rot: cached token works, `codex login status` returns instantly (verified 2026-05-16)
- ❌ Downgrade to 0.123.0: hangs identically (user 2026-05-15)
- ❌ `setsid`, `script(1)` tty faking (memory pre-2026-05-11) — never defeated the older form
- ❌ Wrapper `--no-interactive` flag (commit 257b47dd9, `fix/codex-stdin-hang`) — addressed different symptom, doesn't fix today's hang

## Relevant upstream issues

- [openai/codex#20919](https://github.com/openai/codex/issues/20919) — "codex exec hangs indefinitely when stdin is non-TTY pipe with no writer" (0.128.0+). Workaround = `< /dev/null`; ask for `--no-stdin` flag. This is the CLOSEST upstream match to today's behavior.
- [openai/codex#19945](https://github.com/openai/codex/issues/19945) — "codex exec silently crashes with no output when stdio is detached from TTY (0.124.0+)"
- [openai/codex#14048](https://github.com/openai/codex/issues/14048) — "Codex CLI hangs indefinitely on all prompts, no response generated"

## Wrapper-side state

Workspace-hub commit `47916445c` raised `CODEX_VERSION_GUARD_CEILING_DEFAULT` to 0.130.0 on 2026-05-11. Given today's findings, that ceiling is **too optimistic**. Consider lowering back until upstream investigates, OR keep ceiling at 0.130.0 but mark all codex calls as best-effort with `</dev/null` + `timeout 90` + result verification.

## History

- **2026-04-24**: First observed on 0.124.0 (#2479). `</dev/null`, `exec 0<&-`, `setsid`, `script(1)` all failed to defeat.
- **2026-05-11**: 0.130.0 verified passing during digitalmodel #515 PR #599 cross-review prep. Earlier 30s probe gave false-positive hang signal — passing tests took ~58s. Wrapper ceiling raised to 0.130.0 (commit `47916445c`, closes #2661).
- **2026-05-15**: User reverified — both 0.130.0 and 0.123.0 hang. Initial diagnosis pointed at auth/login layer; subsequent comments ruled out locale, fresh OAuth, and version-specificity.
- **2026-05-16**: Independent reverification today confirms the hang is stdin-detection-layer (banner is smoking gun) and non-deterministic (1/4 invocations succeeds). `codex login status` works instantly — auth-layer hypothesis from 2026-05-15 ruled out. Issue [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715) stays OPEN.

Cross-references:
- [[project_hermes_codex_quota]] — Hermes quota interactions with codex CLI
- [[feedback_hermes_provider_openai_codex_routes_via_codex_exec]] — Hermes routing chain through codex exec
- [[feedback_permission_gate_blocks_cross_review]] — fallback to single-author r3 when codex falls out
- [[feedback_codex_sustained_major_loop]] — sustained-MAJOR pattern interacts with codex availability
- [[feedback_mock_vs_live_invocation_divergence]] — sister rule: verify live, don't trust prior memory
