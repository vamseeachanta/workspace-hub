> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-26
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_verify_against_real_ci_lint_toolchain.md

---
name: feedback_verify_against_real_ci_lint_toolchain
description: "Before pushing, run the repo's ACTUAL CI lint toolchain (same tool, version, config) — a green from a different tool or an absent binary is a false negative"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d8161c1f-2dbe-4020-9d3d-496ca0461f92
---

**Before pushing a branch whose PR gates on a `Lint`/format check, run the repo's EXACT CI lint toolchain locally — same tools, same versions, same config. A "clean" result from a different tool, or from a binary that isn't actually installed, is a false negative that ships a red PR.**

**Why:** live incident 2026-07-04/05 (worldenergydata #723 / PR #821). I ran `ruff check` locally (clean) and a `black --check` that silently no-op'd because **black wasn't in the venv** — so I believed lint was clean and pushed. CI's `Lint` step runs `uv run black --check && isort --check && flake8` and failed twice (first an F401 ruff DID catch but in a file CI doesn't lint; then a black-formatting diff on the test file). Result: two wasted push→CI-red→fix cycles and a merge refused with the opaque "the base branch policy prohibits the merge." A one-line unused-import + a black reformat, discoverable in seconds locally, cost ~4 CI round-trips.

**How to apply:**
1. **Find the CI lint step first**: `grep -A5 -iE "name: Lint|black|isort|flake8|ruff" .github/workflows/*.yml`. Note the exact tools, the paths they target (e.g. `src/ tests/` — NOT `packages/`, so a module under `packages/*/src/` may not even be CI-linted; the file under `tests/` is), and the config source.
2. **Match versions**: read `uv.lock`/lockfile for the pinned tool version (wed pinned `black 25.9.0`); use that exact version. Black reformats differently across major versions — a different local black produces a different diff than CI.
3. **Match config**: flake8 reads `setup.cfg`/`.flake8`/`tox.ini` (`max-line-length`, `extend-ignore`). Run from the repo root so it's picked up; don't pass a guessed `--max-line-length`.
4. **Verify the binary exists** before trusting a pass: `<venv>/bin/black --version`. If a check produces NO output, confirm it actually ran (an absent binary "passes" silently). Sibling venvs often have the tools: `/home/vamsee/.local/bin/black`, `/mnt/local-analysis/digitalmodel/.venv/bin/{isort,flake8}`.
5. **`ruff` is NOT a substitute** for `black`+`isort`+`flake8` — different rules, different formatting. It catches some overlaps (F401) but misses black-format diffs entirely.

**Diagnostic for the opaque merge refusal:** "base branch policy prohibits the merge" = a required check isn't green (it won't say which). `gh pr checks <N> --required` disambiguates: a `fail` is a real defect to fix; a missing/`pending` (e.g. `Test (PR gate)` awaiting the slow domain-tests matrix) is just CI wall-clock.

**Systemic fix filed:** worldenergydata#822 (repo pre-commit) + workspace-hub#3382 (ecosystem rollout + this rule).

Related: [[project_ecosystem_review_2026_07_04]], [[feedback_dependabot_merge_no_rebase_trust_clean]], [[feedback_agent_can_verify_but_not_self_merge_pr]]
