---
name: reference_squash_merge_reachability_false_orphan
description: "To check if a merged PR's work is really on main, compare CONTENT — not mergeCommit reachability (squash-merge makes that a false \"orphaned\" signal)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4acd88b0-1acd-4909-803f-a9a0d2187f13
---

**Verifying whether a "merged" PR's work is actually present on `main`: use content, not merge-commit reachability.**

`gh pr view <n> --json mergeCommit` returns an ephemeral oid that, under **squash-merge** (digitalmodel/wed default), is NOT an ancestor of `origin/main` even though the squashed content landed fine. So `git merge-base --is-ancestor <mergeCommit> origin/main` reports **false "orphaned"** for perfectly-merged PRs. On 2026-07-05 this falsely flagged 18/25 recent digitalmodel PRs as lost; content spot-checks (`git cat-file -e origin/main:<file>`, path-independent basename search for reorg'd repos) proved the work was present.

**Reliable check:** does the PR's introduced file content exist in `origin/main` (exact path, then basename for reorg'd repos like worldenergydata's `src/→packages/` move), and `git log origin/main --follow -- <path>`.

**Real casualty found the same way:** digitalmodel **#989** (DNV-OS-F101 submarine-pipeline design: local-buckling/collapse + S-lay %SMYS) merged 2026-06-22 but its module + git history are genuinely absent from `main` — most likely the late-June `.git` history slim ([[project_dm_1142_repo_health]]) rewound `main` past the merge. Re-landed via **PR #1435** (`feat/reland-dnv-os-f101`, cherry of orphan `f9379b4b`, 31 tests, black/isort/ruff clean) — **MERGED**. NOT the same as DNV-**RP**-F101 (corroded-pipelines FFS, `asset_integrity/dnv_rp_f101.py`) which survived — coincidental DNV numbering.

**Full late-June audit done 2026-07-05 (all 202 PRs merged 06-15..06-30, content-checked):** the slim was NOT mass-loss — it collapsed history to **8 commits** (dropping PR-refs from the log, hence log-reference heuristics are useless here) but preserved the tree. 197/202 fully intact. Only casualties: #989 (re-landed) + #970 `fatigue/sn_endurance.py` (absent but **superseded** by main's `sn_library_api.calculate_endurance()` + `sn_curves.get_sn_curve()`, nothing imports it — no re-land needed). #897 example decks + #1048/50/52 demo outputs are regenerable (generators + `data/vessels/` present). Recent capabilities/motion_forecast work all intact. **No further re-lands needed.**

**Root cause fixed (wshub PR #3386):** the `slim-git-history` skill's Step-6 verify (`du`/`fsck`/smoke-clone) never checked that no tracked deliverable was dropped — a rewrite that silently loses a merged file passes all three. Added a **content-parity gate** to `analyze-repo-bloat.sh --verify-parity <pre-rewrite-backup> <post-rewrite-live>`: a GONE-blob strip must leave `HEAD^{tree}` byte-identical; any diff names the dropped paths + exits 1 to gate the operator force-push. Would have caught #989. (Note: touching any `.claude/skills/` file re-triggers the Skill-Index Coherence determinism gate #3208 → must `uv run python scripts/ai/build_skill_index.py` + commit `config/agents/skill-index-full.yaml`; recurring baseline-red, cf #3277/#3344.) Companion: [[feedback_equality_wedge_vs_drift_recovery]].
