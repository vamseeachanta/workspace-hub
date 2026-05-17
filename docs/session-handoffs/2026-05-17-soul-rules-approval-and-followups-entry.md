# Entry handoff — SOUL rules approval + 4 follow-on issues + Tier 1/2 carry-forward

Date: 2026-05-17 (or whenever the next session opens; reference date 2026-05-16 evening)
Predecessor: [`2026-05-16-conflict-marker-hook-and-soul-rules-exit.md`](2026-05-16-conflict-marker-hook-and-soul-rules-exit.md)
Scope: 1 plan awaiting approval ([#2724](https://github.com/vamseeachanta/workspace-hub/issues/2724)) + 2 new issues to plan ([#2723](https://github.com/vamseeachanta/workspace-hub/issues/2723), [#2725](https://github.com/vamseeachanta/workspace-hub/issues/2725)) + 5 Tier 1/2 user-applied actions still pending from earlier in 2026-05-16.

---

## Suggested prompt (paste into fresh Claude session)

```
Pick up the SOUL ecosystem work from the 2026-05-16 evening session. The
prior session landed:
- workspace-hub#2722 (pre-commit conflict-marker hook, full T3 review,
  TDD impl, CLOSED via commit 340af0021)
- workspace-hub#2724 (5 SOUL Must-Fire Rules, T3 review absorbed, NOW
  status:plan-review — awaits user approval)
- workspace-hub#2723 NEW (pre-commit dead-code cleanup, low-priority)
- workspace-hub#2725 NEW (SOUL auto-load gap for Claude+Gemini sessions,
  status:needs-plan, architectural)
- feedback_codex_cli memory updated with env -u CLAUDECODE workaround

Tier 1/2 carry-forward from the morning session is still pending:
- gh issue close 2719 + gh issue close 2411 (close-out text drafted)
- 3 sibling PR merges (worldenergydata#415 baseline-red, aceengineer-
  website#15 CLEAN, assethold#51 baseline-red)

Read the exit handoff at docs/session-handoffs/
2026-05-16-conflict-marker-hook-and-soul-rules-exit.md for full state.
Then run the preflight commands below to verify current state. Then
triage what to do next based on the queue.
```

---

## Preflight commands (run before any new work)

```bash
cd /mnt/local-analysis/workspace-hub

# 1. Verify all 5 session-critical commits still on origin/main
for sha in 0e62057d6 122a9bf1f 340af0021 cae347193 1ca99ff5c; do
  git merge-base --is-ancestor $sha origin/main 2>/dev/null \
    && echo "OK $sha" || echo "MISSING $sha"
done

# 2. Verify #2722 implementation still healthy
uv run python -m pytest tests/enforcement/test_check_no_conflict_markers.py -o "addopts="
# Expect: 26 passed

uv run python -m pytest tests/enforcement/ -o "addopts="
# Expect: 88 passed

# 3. Verify conflict-marker hook wired into workspace-hub pre-commit
grep -c "check-no-conflict-markers" .git/hooks/pre-commit
# Expect: 1

# 4. Smoke-test the live hook (read-only)
mkdir -p /tmp/smoketest-$$ && cd /tmp/smoketest-$$ && \
  git init -q -b main && \
  git config user.email t@e.com && git config user.name T && \
  git config commit.gpgsign false && \
  echo init > README.md && git add README.md && \
  git commit -q -m init --no-verify && \
  printf '<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> branch\n' > has-marker.txt && \
  git add has-marker.txt && \
  bash /mnt/local-analysis/workspace-hub/scripts/enforcement/check-no-conflict-markers.sh; \
  echo "expected exit 1; actual exit $?"; \
  cd /mnt/local-analysis/workspace-hub && rm -rf /tmp/smoketest-$$

# 5. SOUL runtime drift check (should be clean)
bash scripts/enforcement/check-soul-runtime-drift.sh
# Expect: "All SOUL runtime artifacts up to date."

# 6. Cross-repo installer drift snapshot (should report 2 unprotected siblings on ace-linux-1)
bash scripts/enforcement/check-pre-commit-hook-drift.sh 2>&1 | head -10
# Expect: digitalmodel + llm-wiki "missing vendored copy" until installer is run

# 7. Live runtime symlinks intact
for f in ~/.hermes/SOUL.md ~/.codex/AGENTS.md; do
  echo "$f -> $(readlink "$f" 2>/dev/null || echo NOT-A-SYMLINK)"
done

# 8. GH state of all OPEN items
gh issue view 2719 --repo vamseeachanta/workspace-hub --json state,labels --jq '{state, labels: [.labels[].name]}'
gh issue view 2411 --repo vamseeachanta/workspace-hub --json state,labels --jq '{state, labels: [.labels[].name]}'
gh issue view 2723 --repo vamseeachanta/workspace-hub --json state,labels --jq '{state, labels: [.labels[].name]}'
gh issue view 2724 --repo vamseeachanta/workspace-hub --json state,labels --jq '{state, labels: [.labels[].name]}'
gh issue view 2725 --repo vamseeachanta/workspace-hub --json state,labels --jq '{state, labels: [.labels[].name]}'
gh pr view 415 --repo vamseeachanta/worldenergydata --json state,mergeStateStatus
gh pr view 15 --repo vamseeachanta/aceengineer-website --json state,mergeStateStatus
gh pr view 51 --repo vamseeachanta/assethold --json state,mergeStateStatus
```

---

## State of play

### OPEN — workspace-hub side

| Issue | Status | Action |
|---|---|---|
| [#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719) | `status:plan-approved` | close (carry-forward; close-out text in prior session's exit handoff) |
| [#2411](https://github.com/vamseeachanta/workspace-hub/issues/2411) | OPEN | close (carry-forward; close-out text in prior session's exit handoff) |
| [#2723](https://github.com/vamseeachanta/workspace-hub/issues/2723) | OPEN, `status:needs-plan`, priority:low | plan if Tier 1/2 carry-forward cleared; otherwise defer |
| [#2724](https://github.com/vamseeachanta/workspace-hub/issues/2724) | OPEN, `status:plan-review` | **approve OR revise** — plan absorbed full T3 review; mechanical impl post-approval |
| [#2725](https://github.com/vamseeachanta/workspace-hub/issues/2725) | OPEN, `status:needs-plan`, priority:medium | plan (architectural; T2 likely) |

### OPEN — sibling repos

| PR | Repo | Merge state | Recommendation |
|---|---|---|---|
| [#415](https://github.com/vamseeachanta/worldenergydata/pull/415) | worldenergydata | BLOCKED (baseline-red, PR-unrelated) | admin-via-ruleset toggle |
| [#15](https://github.com/vamseeachanta/aceengineer-website/pull/15) | aceengineer-website | CLEAN | `gh pr merge 15 --squash --auto` |
| [#51](https://github.com/vamseeachanta/assethold/pull/51) | assethold | UNSTABLE (baseline-red, PR-unrelated) | admin-via-ruleset toggle |

### Local-vs-origin divergence

At session exit (2026-05-16 evening), local `main` is on `1ca99ff5c` matching `origin/main`. No ahead/behind. Working tree has auto-sync state file diffs (none related to session commits).

## Recommended priority queue (ordered)

### Tier 1 — quick close-outs (~5 min total user-applied)

1. **Approve OR revise [#2724](https://github.com/vamseeachanta/workspace-hub/issues/2724)**. If approving: `gh issue edit 2724 --remove-label status:plan-review --add-label status:plan-approved && mkdir -p .planning/plan-approved && echo "Approved by: vamsee 2026-05-16" > .planning/plan-approved/2724.md`. Implementation is mechanical (~15-20 min) — single file edit + rebuild + 30 grep verifications + commit.
2. **Close [#2719](https://github.com/vamseeachanta/workspace-hub/issues/2719) + [#2411](https://github.com/vamseeachanta/workspace-hub/issues/2411)** (carry-forward from morning session; close-out text drafted).

### Tier 2 — sibling-repo merges (~5 min user-applied)

3. **Merge [aceengineer-website#15](https://github.com/vamseeachanta/aceengineer-website/pull/15)** — CLEAN, direct merge.
4. **Merge [worldenergydata#415](https://github.com/vamseeachanta/worldenergydata/pull/415)** — admin-via-ruleset toggle (baseline-red).
5. **Merge [assethold#51](https://github.com/vamseeachanta/assethold/pull/51)** — admin-via-ruleset toggle (baseline-red).

### Tier 3 — implementation / new planning

6. **Implement [#2724](https://github.com/vamseeachanta/workspace-hub/issues/2724)** (if approved Tier 1 step 1): edit `config/agents/SHARED_SOUL.md` to insert 5 verbatim rules (in plan §Rule Texts) → `bash scripts/agents/build-soul-runtime.sh` → drift check → 30 grep verifications → commit + close.
7. **Plan [#2725](https://github.com/vamseeachanta/workspace-hub/issues/2725)** (SOUL auto-load for Claude+Gemini). T2. Approach A (Claude Code `@file` import syntax) is likely simplest; check Gemini's equivalent. Would unlock all 14+5 Must-Fire Rules for the 2 underserved providers.
8. **Run #2722 cross-repo installer**: `bash scripts/agents/install-pre-commit-hook-cross-repo.sh` propagates conflict-marker hook to digitalmodel + llm-wiki on this machine. Sibling repos on other machines pick it up via their own `bootstrap-machine.sh §2.6` runs.

### Tier 4 — deferred (future sessions)

9. **Plan [#2723](https://github.com/vamseeachanta/workspace-hub/issues/2723)** (pre-commit dead-code cleanup) — low-priority T1.
10. **Cross-machine bootstrap dry-run on ace-linux-2** — empirically validates §2.5 (SOUL symlinks) + §2.6 (conflict-marker installer). User-driven per `feedback_cross_machine_execution`.
11. **Per-repo adapter-parity rollout for 5 PARTIAL sibling repos** per [#2411](https://github.com/vamseeachanta/workspace-hub/issues/2411) inventory.
12. **Address [#2715](https://github.com/vamseeachanta/workspace-hub/issues/2715)** codex CLI 0.130 regression — `env -u CLAUDECODE` is the operational workaround documented this session; upstream fix is the long-term answer.

## Gates to respect

- **Never self-apply `status:plan-approved`** per `feedback_never_offer_to_self_label_plan_approved`. If user direct-instruction overrides (as happened for #2722), document explicit attribution in the marker file.
- **Pathspec commits** (`git commit -m "..." -- <file>`) — auto-sync writes constantly; never `git add -A` or sweep.
- **`env -u CLAUDECODE` upfront for codex dispatch** from Claude Code Bash context. Skip the UNAVAILABLE+retry dance.
- **Refetch live issue/plan body before every review dispatch** (`feedback_reviewer_dispatch_refetch_live_body`).
- **T3 review default** for non-trivial work; document UNAVAILABLE explicitly when a provider falls out (Gemini sandbox blindness is a known false-positive class — verify with `git ls-files` per `feedback_gemini_sandbox_overlay_blindness`).
- **Verify before recommending from memory** (auto-memory rules) — memory facts may be stale; check current state for file paths, commits.

## Key reference artifacts

- **Exit handoff (full session state)**: [`docs/session-handoffs/2026-05-16-conflict-marker-hook-and-soul-rules-exit.md`](2026-05-16-conflict-marker-hook-and-soul-rules-exit.md)
- **#2722 final plan (793 lines, r3+r4 absorbed)**: [`docs/plans/2026-05-16-issue-2722-pre-commit-conflict-marker-hook.md`](../plans/2026-05-16-issue-2722-pre-commit-conflict-marker-hook.md)
- **#2722 implementation commit**: [`340af0021`](https://github.com/vamseeachanta/workspace-hub/commit/340af0021) (905 lines: 4 scripts + tests + 2 infra mods)
- **#2722 closeout comment**: [issuecomment-4468402596](https://github.com/vamseeachanta/workspace-hub/issues/2722#issuecomment-4468402596)
- **#2724 final plan (r3-absorbed)**: [`docs/plans/2026-05-16-issue-2724-soul-must-fire-rules-from-2722-review.md`](../plans/2026-05-16-issue-2724-soul-must-fire-rules-from-2722-review.md)
- **#2724 plan summary comment**: [issuecomment-4468460776](https://github.com/vamseeachanta/workspace-hub/issues/2724#issuecomment-4468460776)
- **All review artifacts**: `scripts/review/results/2026-05-16-plan-{2722,2724}-{claude,codex,gemini,disagreement}.md`
- **Updated memory**: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_cli_0_124_upstream_regression.md` (env-u workaround documented)

## What success looks like for the next session

- **Minimal**: clear the Tier 1+2 user-applied actions (~10 min: close 2 issues + merge 3 PRs + approve-or-revise #2724).
- **Full**: + implement #2724 mechanically post-approval (~15-20 min) + run cross-repo installer locally for #2722 propagation (~5 min) = ~45-50 min total.
- **Stretch**: + plan #2725 SOUL auto-load architectural gap (~30-45 min for T2 with full T3 review) so the next-next session can implement it.

## Empirical signals to watch for (drift / regression)

- **#2722 hook firing legitimately** on a commit that has anchored markers at column 0 — expected behavior; confirms hook is alive.
- **#2722 hook false-positives** — would indicate a defect in the regex or per-file/per-line sentinel logic. Capture the case, file as follow-on to #2722.
- **Codex hangs again** despite `env -u CLAUDECODE` — escalate; the workaround is non-deterministic per the memory.
- **Gemini returns substantive findings (not sandbox-blindness)** — note the conditions that worked; the workspace-root sometimes resolves correctly.
- **#2724 implementation reveals build-soul-runtime.sh issue** — the build script hasn't been exercised this session post-edit; first impl run is the empirical test.
