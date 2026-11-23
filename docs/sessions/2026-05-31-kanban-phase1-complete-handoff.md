# Session handoff — kanban reorg Phase 1 COMPLETE → cleanups + pillar-(b) + P2-4

**Date:** 2026-05-31 · **Machine:** ace-linux-1 (dev-primary, no OrcaWave license)
**Paste the block below into a fresh session. Full durable state is on GitHub (#2878) + auto-memory `project_kanban_board_domain_reorg.md`; this doc is the entry point.**

---

You are the ORCHESTRATOR continuing two threads. Dirs: `/mnt/local-analysis/digitalmodel`, `/mnt/local-analysis/workspace-hub`. A reusable git worktree from origin/main lives at `/mnt/local-analysis/wshub-phase0` (33K-file checkout — keep it). Read auto-memory `project_kanban_board_domain_reorg.md` first.

## DONE — don't redo

**Kanban board reorg (workspace-hub#2878) — PHASE 1 COMPLETE + APPLIED.**
- Tooling shipped (PR #2895, on main): `scripts/dispatch/route.py` `domain_family` matcher; `scripts/kanban/reconcile.py` board-size report + `--update-counts`; NEW `scripts/kanban/relabel.py` (label-first migration: dry-run default, one-domain enforce, throttle backoff, fail-closed on empty remap). 106 tests, T2 cross-reviewed.
- Pilot (PR #2896): `repo-digitalmodel-hydro-diffraction` board consolidates epic digitalmodel#622's 9-issue OrcaWave cluster — applied + cron-materialized.
- workspace-hub right-sizing: **48 boards (1a #2898=5, 1b #2899=21, 1c #2907=22), all ≤30; ~640 cards relabeled/routed (231 + 408 + ~225 auto-routed), 0 failures.** Base board (2727) drained.
- Ops-stub disposition #2886: 47 content-free WRK-ghosts closed (#164 excluded — had real comments).

**Mechanism (verified, load-bearing — DON'T relearn the hard way):**
- YAML SoT at `.claude/memory/kanban/`; runtime is **one SQLite DB per board** at `~/.hermes/kanban/boards/<slug>/kanban.db` (NOT a shared db). Edit YAML, never SQLite.
- The `*/20` cron (`.github/workflows/kanban-reconcile.yml`) does `git reset --hard origin` + rebuild-cards-from-labels → **card placement is LABEL-FIRST**; hand-edited board YAML is clobbered. Card body regenerates → annotate via GitHub-issue comments, never body edits.
- Add a board = scaffold (board YAML `cards: []` + `manifest.yaml` tier:domain entry + parent `children:` + `domains.yaml`), edited via **TEXT INSERTION not ruamel** (ruamel reformats the whole hand-formatted file). Route cards by **relabel** (not YAML edit).
- Before `relabel.py --apply`: (1) **merge the scaffolding to main first** (cron routes by origin/main manifest); (2) **create the `domain:<x>` GitHub label first** (`gh issue edit --add-label` won't auto-create); then apply; verify 9/N sample carries exactly the target label. Two modes: scaffold-only (cards pre-labeled → auto-route on merge) vs relabel (unlabeled/oversized → `relabel.py --apply`).
- `domain_family: <base>` in routing-rules matches `base` OR `base-*` (precise, not greedy) → splits inherit machine routing. Cross-repo routing is IMPOSSIBLE via labels (cards keyed `gh:<repo>#<n>`); needs `gh issue transfer`.

## IMMEDIATE NEXT — small kanban cleanups (all on #2878)
1. **Vestigial parent boards now empty** after the 1c split: `marine`, `knowledge-management`, `document-intelligence`, `workstations` (1a/1b board files exist) — their cards moved to subdomains; drop the empty board files + manifest/`domains.yaml` entries (one inert PR). (`testing`/`repo-organization`/`skills`/`pipeline` never had parent boards.) Verify each is empty on origin/main first.
2. **11 CLOSE candidates** (test/junk, #2886-style disposition — NEEDS user go before closing): `203 720 1006 1289 1290 1298 1303 1304 1305 1313` (#164 already excluded). Re-verify live, then `gh issue close --reason "not planned"`. Source: `/tmp/classified.txt` (may be gone next session — re-derive from titles if so).
3. `gtm` 32 / `workflow-gates` 31 — marginal; leave unless user wants them split.

## QUEUED — digitalmodel pillar (b) planning round (NOT started — engineering work, distinct from the kanban relabel)
The 9 OrcaWave issues now carry `domain:hydro-diffraction` on the kanban, but their ENGINEERING plan→review→build is undone. All `status:plan-review` except **#500** (`plan-approved`+`dispatch:ready`). Issues: #500,#605,#606,#607,#608,#609,#612,#614 (+ epic #622). Order: #500→#605/#606/#609→#608→#607→#612→#614. **#607 must reconcile with the merged `diffraction resolve` resolver** (PR #650, on digitalmodel main). #610 licensed E2E still OPEN (needs `machine:licensed-win-1`). Flow: plan on issue → adversarial cross-review → USER approval → build (TDD). digitalmodel: branch from origin/main, pathspec-exclude ~27 dirty WIP files, `UV_CACHE_DIR=/tmp/uv-cache uv run`.

## LATER — kanban reorg Phases 2-4
- **P2 ecosystem**: `ecosystem.yaml` cards are `ecosystem_theme` (YAML-only, not GH issues) — can't relabel; route their themes to owning repos needs new GH issues or the cross-repo model.
- **P3 cross-repo transfers**: ~58 mis-filed cards (digitalmodel/worldenergydata/llm-wiki work tracked on wshub boards) → `gh issue transfer` (per-card judgment; trips per-repo `--allow-shrink`).
- **P4 domain×project** (llm-wiki client wikis): full-stack (schema+manifest+loader+dispatch+`config/client-wikis.yml`+slug) — its OWN issue + plan→review→approval gate.

## CONVENTIONS (load-bearing)
Plan-gate: plans on issue → ADVERSARIAL cross-review → USER approval BEFORE build; self-review isn't the gate; **never self-approve, never touch `status:*` labels**. Commit-for-review-then-apply for live label mutations (user merges scaffolding PR, you `relabel.py --apply`). Delegate heavy/parallel work to subagents (fan-out classify) + Codex (`env -u CLAUDECODE codex exec`); review every diff; adversarial review before presenting. Push with `--no-verify` ONLY for the gitleaks-absent env block (review-gate/legal/tests must pass). HTML default for human-facing artifacts. Comment a summary on every issue; render `#NNNN` as links. Post durable state to #2878; update memory `project_kanban_board_domain_reorg.md`.

## POINTERS
- Issue thread: workspace-hub#2878 (all phase comments) · ops-stubs #2886 (closed)
- Memory: `project_kanban_board_domain_reorg.md` (full state + gotchas)
- Worktree: `/mnt/local-analysis/wshub-phase0` (reusable; on merged branch `feat/kanban-wshub-phase1c`)
- Work products: `/tmp/classified.txt`, `/tmp/subsplit-dedup.txt` (CLOSE-list + classification sources; transient)
- Migration remaps (committed): `.claude/memory/kanban/migration/2026-05-30-*.yaml`
