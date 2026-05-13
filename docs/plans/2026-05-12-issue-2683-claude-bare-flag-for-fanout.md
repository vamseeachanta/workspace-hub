# Plan for #2683: Add `--bare` flag to Claude leg of plan-review-fanout to bypass plugin SessionEnd hook

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-12
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2683
> **Review artifacts:** scripts/review/results/2026-05-12-plan-2683-claude.md | ...-codex.md | ...-gemini.md (will be generated AFTER #2684 is mitigated; until then this plan is hand-reviewed only)

---

## Resource Intelligence Summary

### Existing repo code
- `scripts/review/plan-review-fanout.sh:147` — `claude -p "@$PROMPT_FILE — review..."` is the exact invocation that fails today. No flag controls plugin/hook loading.
- `scripts/review/plan-review-fanout.sh:144-149` — the Claude `case` branch. Self-contained; no shared helper to migrate.
- `~/.claude/plugins/cache/openai-codex/codex/1.0.2/hooks/hooks.json` — registers the `SessionEnd` hook with a 5s timeout (root cause site, but out-of-repo).

### Standards
- Not applicable — harness-tooling change.

### LLM Wiki pages consulted
- No relevant wiki pages.

### Documents consulted
- `scripts/review/results/2026-05-12-plan-2675-summary.md` — synthesis showing both Claude and Codex legs returned UNAVAILABLE on the 2026-05-12 run.
- `scripts/review/results/2026-05-12-plan-2675-claude.md` — verbatim `rc=124` artifact.
- Memory `feedback_codex_cli_0_124_upstream_regression` — sibling-bug context (Codex stdin hang); the Claude-side fix here is independent of the Codex resolution but both must land before fanout is trustworthy again.
- `claude --help` output (verified 2026-05-12): `--bare` flag exists at claude 2.1.140 and explicitly disables hooks, plugin sync, auto-memory, keychain reads, and CLAUDE.md auto-discovery while keeping skills available via `/skill-name` and explicit MCP via `--mcp-config`. This is exactly the scope a plan-review subprocess needs.

### Gaps identified
- The fanout has no escape hatch from third-party plugin hooks. Today's failure is the codex plugin, but any future plugin registering a SessionEnd hook would fail the same way for the same structural reason (5s window + sync stdin read).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-12 via `gh issue view`):
- `#2683` — OPEN — bug(harness): Claude SessionEnd hook (codex plugin) times out...
- `#2684` — OPEN — bug(harness): codex-cli 0.130.0 reproduces #2479 stdin-hang...
- `#2675` — OPEN — parent plan under review when bugs surfaced
- `#2479` — CLOSED — original stdin-hang (related historical context)

**File existence** (verified 2026-05-12):
- EXISTS: `scripts/review/plan-review-fanout.sh`
- EXISTS: `scripts/review/results/2026-05-12-plan-2675-claude.md` (rc=124 artifact)
- EXISTS: `~/.claude/plugins/cache/openai-codex/codex/1.0.2/scripts/session-lifecycle-hook.mjs` (out-of-repo, but the implicated file)

**Line excerpts** (`sed -n 144,150p scripts/review/plan-review-fanout.sh`):
```
    claude)
      # Path reference — no inline body.
      timeout -k 5s "${timeout_s}s" \
        claude -p "@$PROMPT_FILE — review the plan at $PLAN_FILE. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS." \
        > "$out" 2>"$err" || rc=$?
      ;;
```

**Reproduction proofs**:
```
$ scripts/review/plan-review-fanout.sh docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md
# (artifact at scripts/review/results/2026-05-12-plan-2675-claude.md)
## Verdict
UNAVAILABLE (claude CLI failed, rc=124: SessionEnd hook [node "${CLAUDE_PLUGIN_ROOT}/scripts/session-lifecycle-hook.mjs" SessionEnd] failed: Hook cancelled )
```
- Reproduced at: 2026-05-12T16:42:00-05:00
- Failure mode observed matches issue claim: YES

Source count: 3 (issue body + plan-review-fanout.sh source + claude --help output + memory rule) — exceeds the 3-source minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-12-issue-2683-claude-bare-flag-for-fanout.md |
| Implementation | scripts/review/plan-review-fanout.sh (single line modification at line 147) |
| Test | scripts/review/tests/test-fanout-claude-bare.bats (or equivalent — verify what test harness the fanout already uses) |
| Plan review — Claude | scripts/review/results/2026-05-12-plan-2683-claude.md (DEFERRED until fanout works again) |

---

## Deliverable

`scripts/review/plan-review-fanout.sh` invokes the Claude provider with `claude --bare -p ...` instead of `claude -p ...`, so third-party plugin hooks (including the codex plugin's SessionEnd hook) do not load in the child claude session and cannot crash the review with `Hook cancelled` rc=124.

---

## Pseudocode

T1 — trivial. See "Files to Change" below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/plan-review-fanout.sh` (line 147) | Add `--bare` before `-p` flag |
| Create (if test harness exists) | `scripts/review/tests/...` | Regression test that the claude invocation includes `--bare` |
| Update | `docs/plans/README.md` | Add this plan to index |

Exact change at line 147:

```diff
-        claude -p "@$PROMPT_FILE — review the plan at $PLAN_FILE. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS." \
+        claude --bare -p "@$PROMPT_FILE — review the plan at $PLAN_FILE. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS." \
```

Add a comment block above the `claude)` case explaining why `--bare` is required (so future maintainers do not "clean up" the flag thinking it limits Claude's capabilities for the review):

```bash
    claude)
      # `--bare` is REQUIRED: it disables hooks/plugin-sync/auto-memory in the
      # child claude session. Without it, third-party plugin SessionEnd hooks
      # (codex plugin observed 2026-05-12, #2683) race with claude's headless
      # shutdown, hit their 5s timeout, and cause `claude -p` to exit rc=124
      # with `Hook cancelled`. Skills still resolve via /skill-name; explicit
      # MCP via --mcp-config still works. This is the minimal-mode invocation
      # documented in `claude --help`.
```

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_fanout_claude_uses_bare_flag | The claude invocation in the Claude `case` branch includes `--bare` | shell-level inspection of `scripts/review/plan-review-fanout.sh` | grep for `claude --bare -p` returns ≥1 match |
| test_fanout_claude_does_not_hang_under_hostile_plugin | Smoke: a `claude -p` invocation with `--bare` does NOT execute the codex SessionEnd hook (no `Hook cancelled` in stderr) | live invocation with codex plugin installed | rc=0 OR stderr does not contain `Hook cancelled` |

---

## Acceptance Criteria

- [ ] `grep -c 'claude --bare -p' scripts/review/plan-review-fanout.sh` returns 1
- [ ] Live re-run of `scripts/review/plan-review-fanout.sh docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md` produces a Claude leg with a real VERDICT/FINDINGS/BLOCKERS structure (not `UNAVAILABLE rc=124`) — does NOT require Codex to be working for this check
- [ ] No regression in existing fanout tests (whatever harness `scripts/review/tests/` uses today)
- [ ] Plan registered in `docs/plans/README.md`

---

## Adversarial Review Summary

Single-author r3 fallback per `feedback_permission_gate_blocks_cross_review` — T2 fanout cannot review THIS plan because the bugs THIS plan fixes are the very ones blocking fanout. Per `feedback_always_adversarial_review_scale_depth`, T1 scope (single-line shell change) means 1 provider is the correct depth, not a degraded fallback.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (main session, r3) | MINOR | 7 findings: 1 MAJOR-but-non-blocking (cross-machine claude-version assumption), 6 MINOR (comment placement; acceptance-criterion grep too narrow; test-artifact path defers a determined decision; CLAUDE.md auto-discovery risk discussion incomplete; source-count off-by-one; upstream follow-up tracker not named). All 8 affirmative checks pass: ≥3 sources, repro proof present, failure-mode matches claim, complexity T1 defensible, diff mechanically correct, codex-plugin hook timeout/path accurately cited, `--bare` behavior matches `claude --help`, TDD list covers structural+behavioral assertions. |

**Overall result:** **MINOR — can advance to `status:plan-review` for user approval.** Patch is mechanically correct; the 7 findings are refinement suggestions, not defects. Review artifact at `scripts/review/results/2026-05-12-plan-2683-claude-r3.md` with full per-finding rationale and verification evidence.

User has two paths at approval time:
1. **Approve as-is** — findings #1, #3, #4 captured as inline TODOs during execution. Finding #1 (cross-machine version assumption) becomes a follow-up acceptance criterion.
2. **Fold findings in first** — amend this plan to address all 7, then approve the amended version.

---

## Risks and Open Questions

- **Risk:** `--bare` also disables auto-memory and CLAUDE.md auto-discovery. The plan-review prompt is fully self-contained (a path reference + a static prompt file), so this should not degrade review quality — but verify by inspecting the first post-fix review artifact and confirming it still cites repo paths.
- **Risk:** `--bare` also skips skills auto-discovery; skills must be invoked via `/skill-name`. The current plan-review-prompt.md should not depend on auto-loaded skills (the prompt is the contract). Verify on first post-fix run.
- **Open:** Should we apply `--bare` to the entire fanout (Claude, Codex, Gemini) as a discipline, or just Claude? Codex and Gemini are not affected by claude's plugin system, so the answer is: only Claude needs it. Don't widen scope.
- **Open:** Should the codex plugin's SessionEnd hook also be patched upstream (separate from this defensive fix)? Yes — file an upstream issue against `openai/codex-plugin-cc`, but that is OUT OF SCOPE for this plan. Capture as follow-up.

---

## Complexity: T1

**T1** — one-line flag addition to a shell script + brief comment + smoke verification. No new code, no test framework expansion, no design decisions beyond "use the documented flag for its documented purpose." The only reason this is a plan-tracked change rather than a trivial commit is the issue-planning-mode discipline that ALL issues go through Resource Intel → Plan → Approval. The fix itself is mechanical.
