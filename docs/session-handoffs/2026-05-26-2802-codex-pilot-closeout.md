# Session closeout — #2802 Codex-under-Claude pilot (executed + closed)

**Date:** 2026-05-26 · **Orchestrator:** Claude (main session) · **Implementer:** Codex (via broker, autonomous)
**Companion to:** the entry handoff `docs/session-handoffs/2026-05-26-codex-pilot-2802.md` (PR #2812, merged).

## Outcome — DONE

First real-world run of the Codex-under-Claude route (#2804 / merged #2809), end to end:

| Stage | Result |
|---|---|
| Implementation | Codex autonomous in isolated worktree sandbox → PR #2820 **merged** (`ff5f9650`) |
| TDD | commit-pinned RED→GREEN, two rounds (impl `0245583`→`0564a00`; review-fix `f9f2d153`→`82050d25`); 5 tests |
| Code-stage T3 review | Claude r1 + Codex (broker) + Gemini — **unanimous** data-loss BLOCKER caught, fixed, re-verified |
| Completeness gate (#2798) | **86%** evidence-class (≥80), owner-verified; #2802 **CLOSED/COMPLETED**, gate Action ran `success` |
| Provenance | 100% Codex implementation (git-attributed to local identity; no separate Codex git id); Claude orchestration + review only — not mixed-author |

## What the pilot caught (the value)

- **🔴 Data-loss BLOCKER** (all 3 reviewers, independently): an empty-but-successful `gh issue list` deleted every card for a repo. Fixed: fail-closed `RuntimeError` unless `--allow-empty OWNER/REPO`. Plus 3 MAJORs (rebase-under-`set -e` retry loop; cross-repo `GITHUB_TOKEN` scope → `schedule:` disabled until Phase-2 App; `yaml.safe_dump` comment destruction → `ruamel.yaml`).

## Route findings → follow-up #2822 (needs planning)

Worktree dispatch under the Codex broker needs THREE aligned fixes (memory: `feedback_codex_worktree_sandbox_three_layer`):
1. `--cwd <worktree>` on the broker `task` (re-roots the sandbox writable set; `--cd` is not a flag and leaks into the prompt).
2. `[sandbox_workspace_write].writable_roots = ["<main>/.git"]` (worktree git metadata is gitlinked into the main `.git`, outside the sandbox root → commits fail read-only).
3. Restart the broker's shared `serve`/app-server after editing config (it caches `config.toml` at spawn).
Broker jobs are namespaced by workspace root → `status`/`result` need `--cwd <wt>` too.

## Completeness-gate first-close (memory: `feedback_completeness_gate_first_close_sequence`)

#2802 was the gate's first real exercise; surfaced two traps: `COMPLETENESS_OWNERS` repo var must be set first (unset → CONFIG ERROR → reopen), and the record must be stamped BEFORE the owner applies the verified label (stale-label DENY otherwise; a present-but-stale label needs remove→re-add).

## Final state

- **Repos:** workspace-hub main checkout on pre-existing dirty `fix/2795` (UNTOUCHED). PR #2820 merged to main. No stray worktrees.
- **Config:** `~/.codex/config.toml` temporary `writable_roots` grant **reverted** (`network_access` retained). `COMPLETENESS_OWNERS=vamseeachanta` repo variable **set** (intentional — operationalizes the #2798 gate).
- **Issues:** #2802 CLOSED/COMPLETED. #2822 OPEN (route hardening, needs planning + approval).
- **Evidence (machine-local, ace host):** `/mnt/local-analysis/2802-pilot-evidence/` — HTML score card, T3 Codex+Gemini review logs, orchestrator summary.
- **Memory:** `feedback_codex_worktree_sandbox_three_layer`, `feedback_completeness_gate_first_close_sequence`.

## No external actions pending

No merge/close/approval left open by the agent. #2822 awaits normal planning. Human-in-loop gates were all preserved (no self-implement, no self-approve plan-approved, no self-merge, no self-attest completeness).
