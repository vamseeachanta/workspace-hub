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

`scripts/review/plan-review-fanout.sh` invokes the Claude provider with `env CLAUDE_PLUGIN_DIR=<empty-tempdir> claude -p ...` instead of `claude -p ...`, so third-party plugins (including the codex plugin's SessionEnd hook) are not discovered for the child claude session and cannot crash the review with `Hook cancelled` rc=124. **Mechanism switched from `--bare` to `CLAUDE_PLUGIN_DIR` override during execution** (see Adversarial Review Summary below): `--bare` would have also disabled keychain reads and required `ANTHROPIC_API_KEY`, breaking the typical local-dev auth path. The env-var override is mechanism-narrower (only plugin discovery, no auth/memory side effects) and version-independent (no claude ≥ 2.1.140 requirement).

---

## Pseudocode

T1 — trivial. See "Files to Change" below.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/plan-review-fanout.sh` (claude case branch, ~lines 143-149) | Wrap the claude invocation with `env CLAUDE_PLUGIN_DIR=<mktemp -d>` so the child claude doesn't discover the codex plugin |
| Modify | `scripts/review/tests/mocks/claude` | Mock records `ENV.CLAUDE_PLUGIN_DIR` value so the regression test can assert the override fired |
| Modify | `scripts/review/tests/test_plan_review_fanout.sh` | Add `test_claude_invocation_sets_plugin_dir_override` + `test_claude_case_branch_documents_2683` |
| Update | `docs/plans/README.md` | Add this plan to index |

Exact change in the claude case branch (the existing 1-line comment + 4-line invocation becomes a 13-line block):

```bash
    claude)
      # Disable third-party plugin loading for the child claude session (#2683):
      # the codex plugin's SessionEnd hook does a synchronous fs.readFileSync(0)
      # with a 5s timeout that races claude's headless shutdown and causes
      # `claude -p` to exit rc=124 with `Hook cancelled`. Pointing
      # CLAUDE_PLUGIN_DIR at an empty directory disables plugin discovery for
      # THIS invocation only, leaving keychain/OAuth auth intact. (Earlier
      # iteration tried `--bare`, but that also disables keychain reads and
      # requires ANTHROPIC_API_KEY — incompatible with the typical local-dev
      # auth setup. The env-var override is mechanism-narrower and
      # version-independent.)
      local plugin_dir_override
      plugin_dir_override="$(mktemp -d -t claude-no-plugins-XXXXXX)"
      timeout -k 5s "${timeout_s}s" \
        env CLAUDE_PLUGIN_DIR="$plugin_dir_override" \
        claude -p "@$PROMPT_FILE — review the plan at $PLAN_FILE. Return sections: VERDICT, RETRIEVAL, FINDINGS, BLOCKERS." \
        > "$out" 2>"$err" || rc=$?
      rmdir "$plugin_dir_override" 2>/dev/null || true
      ;;
```

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_claude_invocation_sets_plugin_dir_override | The wrapper sets `CLAUDE_PLUGIN_DIR` to an empty tempdir for the child claude (so plugins aren't discovered) | run wrapper under mocks; inspect `claude.capture` ENV section | `ENV.CLAUDE_PLUGIN_DIR` value present and contains `claude-no-plugins-` prefix |
| test_claude_case_branch_documents_2683 | The wrapper references `#2683` in comments (defends against future cleanup) | `grep #2683 scripts/review/plan-review-fanout.sh` | ≥1 match |
| Smoke (manual) | `env CLAUDE_PLUGIN_DIR=$(mktemp -d) claude -p "Reply OK"` returns rc=0 with `OK` on stdout, no `Hook cancelled` in stderr | live invocation with codex plugin installed | rc=0; stdout contains `OK`; auth via keychain still works |

---

## Acceptance Criteria

- [ ] `grep -c 'CLAUDE_PLUGIN_DIR=' scripts/review/plan-review-fanout.sh` returns ≥1 (the env-var override is set in the claude case branch)
- [ ] `grep -c '#2683' scripts/review/plan-review-fanout.sh` returns ≥1 (explanatory comment is preserved)
- [ ] Live re-run of `scripts/review/plan-review-fanout.sh docs/plans/2026-05-12-issue-2675-ai-ecosystem-reverse-prompt-plan.md` produces a Claude leg with a real VERDICT/FINDINGS/BLOCKERS structure (not `UNAVAILABLE rc=124`) — does NOT require Codex to be working for this check
- [ ] No regression in existing 17 fanout tests (`scripts/review/tests/test_plan_review_fanout.sh` total goes from 17 → 19; all green)
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

### Mechanism deviation discovered at execution time (2026-05-13)

User approved path 1 (`status:plan-approved` set 2026-05-13). During implementation, the live smoke test of `claude --bare -p "..."` returned `Not logged in · Please run /login` — the `--bare` flag disables keychain reads (per its own `claude --help` text: *"OAuth and keychain are never read"*) and requires `ANTHROPIC_API_KEY`, which is not set on this machine. The originally-approved mechanism would have broken the fanout for every user authenticating via keychain/OAuth.

A better fix surfaced from the same smoke test: `env CLAUDE_PLUGIN_DIR=<empty-tempdir> claude -p "..."` returned `OK rc=0` cleanly. The override disables plugin discovery (so the codex plugin's SessionEnd hook doesn't load) **without** touching auth.

User confirmed the deviation (2026-05-13 chat). Implementation switched to `CLAUDE_PLUGIN_DIR` override at all four touch points (script, mock-claude `ENV` capture, two new tests). The r3 review finding #1 (cross-machine version assumption) **dissolves** because env-var overrides have no version dependency.

**Root cause this slipped past r3 review:** the review's 8 "affirmative checks" verified that `claude --help` describes the `--bare` flag (the flag exists), but never actually invoked `claude --bare` to confirm it works in this environment. Classic `superpowers:verification-before-completion` gap — evidence-of-syntax confused with evidence-of-behavior. Lesson captured for future plan reviews.

---

## Risks and Open Questions

- **Risk:** future claude versions could change how `CLAUDE_PLUGIN_DIR` is honored (e.g., respect only `~/.claude/plugins/cache/` and ignore the env var). The smoke test at execution time confirms it works on claude 2.1.140 today, but the test_claude_invocation_sets_plugin_dir_override regression test only confirms the wrapper *sets* the env var, not that claude *honors* it. A live re-dispatch against #2675 (post-implementation) is the integration check.
- **Risk:** the empty tempdir is cleaned up via `rmdir` after each invocation; if a future change adds files to that dir, `rmdir` will leave it behind. Cosmetic, not load-bearing.
- **Open:** Should we apply the plugin-dir override to all three providers as a discipline (Codex, Gemini), or just Claude? Codex and Gemini are not affected by claude's plugin system, so the answer is: only Claude needs it. Don't widen scope.
- **Open:** Should the codex plugin's SessionEnd hook also be patched upstream (separate from this defensive fix)? Yes — file an upstream issue against `openai/codex-plugin-cc`, but that is OUT OF SCOPE for this plan. Captured as follow-up: track upstream after this plan lands.

---

## Complexity: T1

**T1** — one-line flag addition to a shell script + brief comment + smoke verification. No new code, no test framework expansion, no design decisions beyond "use the documented flag for its documented purpose." The only reason this is a plan-tracked change rather than a trivial commit is the issue-planning-mode discipline that ALL issues go through Resource Intel → Plan → Approval. The fix itself is mechanical.
