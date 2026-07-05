# Verify against the real CI lint toolchain — agent rule (#3382)

**When to apply:** before pushing any branch whose PR gates on a `Lint`/format status check (black / isort / flake8 / ruff / mypy), whether you are a human or an agent.

**Why:** a PR that passes local checks but fails CI lint is refused at merge with GitHub's opaque *"the base branch policy prohibits the merge"* — which does not name the failing check. Live incident 2026-07-04/05 (worldenergydata PR #821): the author ran `ruff` locally (clean) and a `black --check` that **silently no-op'd because black was not installed in the venv**, so lint "passed" locally and CI rejected the PR twice on formatting. A pre-commit hook pinned to a **mirror version that had drifted from CI** (black 24.10.0 local vs 25.9.0 CI) is the same failure in hook form (fixed in worldenergydata#822 by switching to local `uv run` hooks).

**How to apply:**

1. **Find the CI lint step first**, don't guess: `grep -A5 -iE "black|isort|flake8|ruff|mypy" .github/workflows/*.yml`. Note (a) the exact tools, (b) the **paths** they lint (e.g. `src/ tests/` — a module under `packages/*/src/` may not be CI-linted at all; a file under `tests/` is), and (c) how they are invoked (`uv run <tool>` pulls the version from `uv.lock`).
2. **Match the version.** Read the pinned version from `uv.lock`/lockfile and use that exact one. Black reformats differently across major versions — a different local black produces a different diff than CI. Prefer running the repo's own env (`uv run <tool>`) over a system binary.
3. **Match the config.** flake8 reads `setup.cfg`/`.flake8`/`tox.ini` (`max-line-length`, `extend-ignore`, `per-file-ignores`); black/isort read `pyproject.toml`. Run from the repo root so these are picked up; don't pass a guessed `--max-line-length`.
4. **Confirm the binary exists before trusting a pass.** `<tool> --version`. A check that produces NO output may be an absent binary "passing" silently, not a clean tree.
5. **`ruff` is NOT a substitute** for `black`+`isort`+`flake8` — different rules and formatting. It overlaps on some (F401) but misses black-format diffs entirely.

**Diagnosing the opaque merge refusal:** "base branch policy prohibits the merge" = a required check is not green (it won't say which). `gh pr checks <N> --required` disambiguates: a `fail` is a real defect you must fix; a missing/`pending` context (e.g. `Test (PR gate)` awaiting the slow domain-tests matrix) is just CI wall-clock — wait, don't re-push.

**Do NOT apply when:** the repo has no PR-gating lint/format check (nothing to match), or the change touches no files under the CI-linted paths.

**Enforcement gradient** (per [`patterns.md`](patterns.md)): this Level-0 prose rule is backed by a Level-3 hook where repos adopt a **format pre-commit that uses the repo's own `uv run` toolchain** (so hook versions can't drift from CI). Reference implementation: worldenergydata#822 (`.pre-commit-config.yaml` local `uv run --extra dev black|isort|flake8` hooks). Ecosystem rollout to the remaining tier-1 Python repos (digitalmodel, assetutilities, assethold) is the follow-on for this issue.

**Related:** [`coding-style.md`](coding-style.md), [`patterns.md`](patterns.md). Memory: `feedback_verify_against_real_ci_lint_toolchain`. Incident: worldenergydata#821/#822.
