# Plan for #2443: achantas-data — restore CI with markdown-lint + link-check (workflows deleted 2025-10)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2443
> **Parent meta-issue:** https://github.com/vamseeachanta/workspace-hub/issues/2424
> **Review artifacts:** scripts/review/results/2026-04-21-plan-2443-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code (achantas-data)

- Remote repository: `https://github.com/vamseeachanta/achantas-data` — currently has **no** `.github/workflows/` directory on `main` (confirmed below).
- Local checkout at `/mnt/local-analysis/workspace-hub/achantas-data/` is on `main`, tracking `origin/main`. No in-flight `.github/` tree locally.
- **Correction to issue body**: The issue body asserts "no `pyproject.toml`, no `src/`, no `tests/`". This is **partially inaccurate**. On current `origin/main`:
  - `pyproject.toml` EXISTS (4133 bytes, declares `[project] name = "achantas-data"`, pytest + black + isort + mypy config).
  - `src/achantas_data/` EXISTS with `__init__.py` and `utils.py`.
  - `tests/` EXISTS with `conftest.py`, `test_smoke.py`, `unit/test_family_tree.py`, `unit/test_utils.py`.
- However, the repo **content mix** is overwhelmingly docs: 495 tracked `.md` files vs. 12 tracked `.py` files (`git ls-files | grep -c '\.py$'` = 12, verified 2026-04-21). The active traffic (10+ open issues on personal-data topics in last week, recent commits to `_house/`, `_family/`, `_finance/`) confirms the repo now functions primarily as a markdown knowledge base with legacy Python scaffolding still tracked but idle.
- Implication: the issue body's recommendation (markdown-lint + link-check, skip Python tests) is still correct, but the **justification must be stated truthfully** — "Python scaffolding is tracked but unused; active traffic is markdown; restoring Python-tests workflow would add noise without value". Not "there is no Python code".

### Standards

Not applicable — infrastructure/CI issue, no engineering standards ledger involvement.

### LLM Wiki pages consulted

No relevant wiki pages — this is repo infrastructure, not domain knowledge.

### Documents consulted

- **Issue #2443 body** (this issue) — investigation agent's verdict H1 confirmed by two GitHub API calls: `contents/.github` → 404, `actions/workflows` → `total_count: 0`. Session-entry prompt already specifies markdown-lint + link-check scope.
- **Parent meta-issue #2424** (`chore(ci-health): cross-repo CI audit — 6 of 7 ecosystem repos have red main CI`) — state `OPEN`, label `status:plan-approved` + `cat:infrastructure`. #2443 is one of the child repos in the audit.
- **Sibling-repo workflow templates** (`/mnt/local-analysis/workspace-hub/` siblings inspected):
  - `workspace-hub/.github/workflows/`: `baseline-check.yml`, `claude-code-review.yml`, `claude.yml`, `enforcement-gate.yml`, `multi-ai-review.yml`, `skills-validation.yml` — **none** are markdown-lint or link-check templates.
  - `digitalmodel/.github/workflows/`: domain test suites + `docs.yml` (mkdocs build) + `quality-gates.yml` — no markdown-lint or link-check.
  - `assethold/.github/workflows/`: only `docs.yml` + `python-tests.yml`.
  - **Gap confirmed**: no markdown-lint or lychee workflow exists anywhere in the workspace-hub ecosystem to copy. This plan authors the first such template. Reusing it across other docs-heavy repos (achantas-media, etc.) is a future follow-up, not in scope here.
- **Memory: `reference_achantas_data.md`** — confirms achantas-data is the personal-data repo where data + travel are tracked as GitHub issues; supports lenient markdown-lint posture (strict style rules would fight natural note-taking).
- **Issue body investigation** — last CI commit `6853c860` (2025-10-04) is unreachable from current `main` (`compare/6853c860...main` → "No common ancestor"); confirms branch rewrite orphaned `.github/` along with other history.

### Gaps identified

- No `.github/workflows/markdown-lint.yml` exists on achantas-data.
- No `.github/workflows/link-check.yml` exists on achantas-data.
- No `.markdownlint.jsonc` (or `.markdownlint.yaml`) config exists to define the lenient ruleset.
- No `lychee.toml` or equivalent link-check config exists.
- No ecosystem-wide template exists to copy — this plan produces the first canonical pair.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view`):
- `#2443` — OPEN — `chore(ci-health): achantas-data — restore CI with markdown-lint + link-check (workflows deleted 2025-10, repo now docs-only)` — labels: `cat:infrastructure`, `status:plan-approved`.
  - **Governance note**: `status:plan-approved` is on the issue but **no canonical plan file** and **no `.planning/plan-approved/2443.md` marker** exist. This is the drift condition described in the planning skill's "state drift items / missing-plan" triage rule. This plan corrects the drift by producing the canonical artifact. Labels and marker are out of scope for this drafting pass per the user's hard constraints.
- `#2424` — OPEN — `chore(ci-health): cross-repo CI audit — 6 of 7 ecosystem repos have red main CI` — parent meta-issue, confirmed.

**File existence on achantas-data main** (`gh api repos/vamseeachanta/achantas-data/contents/...` 2026-04-21):
- MISSING: `.github/` → HTTP 404 (workflows directory absent)
- `GET /repos/.../actions/workflows` → `{"total_count":0,"workflows":[]}`
- EXISTS: `pyproject.toml` (4133 bytes, sha `0e6d6f42b3...`)
- EXISTS: `src/achantas_data/` (with `__init__.py`)
- EXISTS: `tests/` (with `__init__.py`, `conftest.py` 5725 bytes, `test_smoke.py` 5461 bytes, `unit/`, `integration/`)

**Tracked-file mix** (`git ls-files | grep -c` on local checkout 2026-04-21):
- 495 `.md` files tracked
- 12 `.py` files tracked (`create-module-agent.py`, `modules/reporting/templates/plotly_report_template.py`, `modules/reporting/utils/path_utils.py`, `src/achantas_data/__init__.py`, `src/achantas_data/utils.py`, `tests/__init__.py`, `tests/conftest.py`, `tests/integration/__init__.py`, `tests/test_smoke.py`, `tests/unit/__init__.py`, `tests/unit/test_family_tree.py`, `tests/unit/test_utils.py`) — six are `__init__.py`/`conftest.py` scaffolding; three are test skeletons; three are legacy utilities.
- 3715 total tracked files (dominated by docs/PDFs)

**Python-CI exclusion evidence** (verified 2026-04-21, supports the §OUT-of-scope decision not to restore `python-tests.yml`):
- `git log -1 --format="%ai %s" -- tests/ src/ pyproject.toml` → `2026-03-25 19:16:48 -0500 chore(sync): auto-sync 2026-03-25` (last touch was an auto-sync commit, not active development).
- `git log -1 --format="%ai %s" -- '*.md'` → `2026-04-20 21:33:22 -0500 docs(house): pause enrollment at Revolution Step 2 (#40)` (markdown touched 26 days later, in active PR flow).
- `pyproject.toml` declares pytest/black/isort/mypy but the repo has not run any of them in CI since 2025-10; the test files reference modules (`achantas_data.utils`) that themselves have no behavioural exercise. The last 10 commits on `main` touch `_house/`, `_family/`, `_finance/` markdown exclusively — zero `.py` diffs.
- Conclusion: restoring `python-tests.yml` would fire on every commit (or at minimum on `**/*.py` changes which do not occur), burn CI minutes, and almost certainly produce failing runs on first execution because the test code is stale relative to current content. The evidence supports deferring Python CI to a separate issue rather than bundling into this CI-restoration scope.

**Gap proofs**:
- `ls /mnt/local-analysis/workspace-hub/achantas-data/.github/` → "No such file or directory"
- `gh api repos/vamseeachanta/achantas-data/contents/.github` → `{"message":"Not Found", "status":"404"}`
- `grep -l markdownlint workspace-hub/.github/` → no matches (no existing template to copy)

*Source count: issue body + parent issue + sibling workflow survey (3 repos) + memory note + GitHub API file-existence probes = 5+ distinct sources.*

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2443-achantas-data-markdown-lint.md` |
| Implementation — markdown-lint workflow | `achantas-data/.github/workflows/markdown-lint.yml` (NEW in external repo) |
| Implementation — link-check workflow | `achantas-data/.github/workflows/link-check.yml` (NEW in external repo) |
| Implementation — markdownlint config | `achantas-data/.markdownlint.jsonc` (NEW in external repo) |
| Implementation — lychee config | `achantas-data/lychee.toml` (NEW in external repo) |
| Plan review — Claude | `scripts/review/results/2026-04-21-plan-2443-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-21-plan-2443-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-21-plan-2443-gemini.md` |
| README index | `docs/plans/README.md` (row added during normal workflow — NOT in this drafting pass per task constraint) |

Note: implementation artifacts land in the **external `achantas-data` repo**, not in workspace-hub. Execution requires `cd achantas-data/` and a separate commit/push in that repo.

---

## Deliverable

Two minimal, scoped GitHub Actions workflows on `achantas-data` `main` that produce green CI on the next `.md`-touching push and on a weekly schedule: `markdown-lint.yml` (PR-gate on markdown changes) and `link-check.yml` (scheduled + on-demand external-link rot detection). Both are scoped tightly so personal-data commits that do not touch `.md` do not burn Actions minutes, and the markdownlint ruleset is tuned lenient so natural note-taking does not produce false failures.

---

## Pseudocode

T1 — trivial. See "Files to Change" for exact contents. No algorithm to sketch.

---

## Files to Change

All changes land in the **external `achantas-data` repo** (`/mnt/local-analysis/workspace-hub/achantas-data/`), not in workspace-hub.

| Action | Path (inside achantas-data) | Reason |
|---|---|---|
| Create | `.github/workflows/markdown-lint.yml` | PR gate on markdown changes, runs `DavidAnson/markdownlint-cli2-action` |
| Create | `.github/workflows/link-check.yml` | Weekly + dispatch external-link rot scan via `lycheeverse/lychee-action@v2` |
| Create | `.markdownlint.jsonc` | Two-layer ruleset. **Non-negotiable floor (cannot be disabled during tuning)**: `MD001` (heading-increment), `MD011` (reversed-link-syntax), `MD018-MD020` (ATX heading spacing), `MD022` (blanks-around-headings), `MD023` (heading-start-left), `MD024` (duplicate-heading — keep enabled; catches concatenation bugs), `MD027` (multiple-spaces-after-blockquote), `MD030` (list-marker-space), `MD034` (no-bare-urls), `MD035` (hr-style), `MD037-MD040` (emphasis/fence hygiene), `MD042` (no-empty-links), `MD051` (link-fragments), `MD053` (link-image-reference-definitions) — **minimum 20 rules enabled**. Rationale source: [markdownlint rule catalogue](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md) — the listed rules are the correctness-adjacent subset (broken syntax, broken links, structural defects) as opposed to the stylistic subset. **Convenience layer (disabled)**: `MD013` (line-length), `MD033` (inline HTML), `MD041` (first-line-h1) — stylistic, fight natural note-taking. **MD025 remains enabled** with `{ "level": 1 }` (single top-level H1 enforced per file — only override per-file via inline directive when structurally necessary, not globally). |
| Create | `lychee.toml` | Accept 200/206/429, retry once, ignore localhost + example.com + archive.org, max 5 concurrent, 20s timeout. **Exclusion policy**: per-URL exclusions only, each with an inline comment explaining *why* excluded and a dated TODO for re-check. Whole-host / wildcard excludes are prohibited. Exclusion list capped at 25 entries per audit cycle; exceeding the cap requires a follow-up issue. |

**Workspace-hub side** (this repo) — only this plan file is written in this drafting pass. Per explicit task constraint: no `docs/plans/README.md` edit, no `.planning/plan-approved/2443.md` marker, no label change.

### Workflow specifics

**`.github/workflows/markdown-lint.yml`** (target shape):
```yaml
name: markdown-lint
on:
  push:
    branches: [main]
    paths: ['**/*.md', '.markdownlint.jsonc', '.github/workflows/markdown-lint.yml']
  pull_request:
    paths: ['**/*.md', '.markdownlint.jsonc']
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: markdown-lint-${{ github.ref }}
  cancel-in-progress: true
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DavidAnson/markdownlint-cli2-action@v16
        with:
          globs: '**/*.md'
          config: '.markdownlint.jsonc'
```

**`.github/workflows/link-check.yml`** (target shape):
```yaml
name: link-check
on:
  pull_request:
    paths: ['**/*.md', 'lychee.toml', '.github/workflows/link-check.yml']
  schedule:
    - cron: '0 13 * * 1'   # Mondays 13:00 UTC = 08:00 CT
  workflow_dispatch:
permissions:
  contents: read           # no issues:write — lychee-action@v2 does not auto-open issues
concurrency:
  group: link-check-${{ github.ref }}
  cancel-in-progress: true
jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 10    # bound PR-trigger runtime; scheduled runs inherit same ceiling
    steps:
      - uses: actions/checkout@v4
      - name: lychee
        uses: lycheeverse/lychee-action@v2
        with:
          args: --config ./lychee.toml '**/*.md'
          # fail defaults to true on lychee-action@v2; no explicit override needed
```

### Tool choice rationale

- **markdownlint-cli2 (via `DavidAnson/markdownlint-cli2-action`)** over `markdownlint-cli` v1 — cli2 is the maintained successor, faster, and has first-class action support. Over `pymarkdown` / `remark-lint` — markdownlint is the de facto standard in Actions-based repos, config is portable.
- **lychee (via `lycheeverse/lychee-action@v2`)** over `gaurav-nelson/github-action-markdown-link-check` / `tcort/markdown-link-check` — lychee is the actively maintained Rust-based alternative with better retry/accept-code semantics, and it supports markdown + HTML + plaintext in one pass. node-based link-checkers are widely reported to struggle on large markdown corpora; no specific benchmark is cited here, pick the Rust implementation on maintenance grounds.
- **Lenient markdownlint config (convenience layer only)** rationale: this is a personal-data + issues knowledge base, not public-facing prose. MD013 (line-length) and MD041 (h1-first) fight natural note-taking. MD033 fires on embedded `<br>` / `<details>` which are legitimate. The **non-negotiable floor** (MD001, MD011, MD018-MD020, MD022-MD025, MD027, MD030, MD034, MD035, MD037-MD040, MD042, MD051, MD053 — 20 rules) guards structural and link correctness and must stay enabled even if the first run surfaces violations (fix the content, don't disable the rule).

---

## TDD Test List

Per `AGENTS.md` line 7 (`TDD mandatory — tests before implementation; no exceptions`), this plan defines a red → green sequence for the workflow/config artifacts. Infrastructure code is tested by (a) config-parse assertions executed locally before the workflow exists, and (b) an expected-failing state captured before the config is tuned.

**Red/green sequence (execute in order, commit only after each step verifies):**

| # | Step | Command | Red state (before) | Green state (after) |
|---|---|---|---|---|
| 1 | Baseline: no workflows exist | `gh api repos/vamseeachanta/achantas-data/actions/workflows` | `total_count: 0` | still 0 — proves starting point |
| 2 | Author `.markdownlint.jsonc`, then assert it parses and enables ≥20 floor rules | `python3 -c "import json5, sys; cfg=json5.load(open('.markdownlint.jsonc')); floor={'MD001','MD011','MD018','MD019','MD020','MD022','MD023','MD024','MD025','MD027','MD030','MD034','MD035','MD037','MD038','MD039','MD040','MD042','MD051','MD053'}; disabled={k for k,v in cfg.items() if v is False}; missing=floor & disabled; sys.exit(1 if missing else 0)"` | exits 1 (file missing / floor rule disabled) | exits 0 — floor rules present and not disabled |
| 3 | Author `.github/workflows/markdown-lint.yml`, validate schema | `actionlint .github/workflows/markdown-lint.yml` | schema errors (file missing or malformed) | no errors |
| 4 | Author `.github/workflows/link-check.yml`, validate schema | `actionlint .github/workflows/link-check.yml` | schema errors | no errors |
| 5 | Local dry-run of markdownlint against the corpus | `npx markdownlint-cli2 --config .markdownlint.jsonc '**/*.md'` | non-zero exit if real defects (fix content; do NOT disable floor rules) | exit 0 |
| 6 | Local dry-run of lychee against the corpus | `lychee --config ./lychee.toml '**/*.md'` | non-zero exit (expected URL rot) — resolve via per-URL `lychee.toml` exclude (whole-host prohibited) or fix links | exit 0 |
| 7 | Push; `markdown-lint` workflow runs on the push | `gh run watch` | (not yet run) | conclusion `success` |
| 8 | Manual dispatch of `link-check` | `gh workflow run link-check.yml && gh run watch` | (not yet run) | conclusion `success` |
| 9 | Push a `.py`-only commit; confirm `markdown-lint` skipped | `gh run list --workflow=markdown-lint.yml --limit 1` | n/a | no new run for the .py commit (path-filter proves scope) |

**Config-parse smoke test** (step 2 above): the floor-rule assertion is the test-before-implementation artifact for the markdownlint config — it fails before the file exists and before the config is correctly authored, and only passes once the non-negotiable floor is present. This satisfies the repo's mandatory TDD rule for the config artifact.

**Promotion path (per `.claude/rules/patterns.md` enforcement gradient)**: step 5 currently runs as a developer-machine ritual (Level 2 — script). Follow-up issue should promote the `markdownlint-cli2` local dry-run to a pre-commit hook (Level 3) so step 5 fires automatically on every commit. Filed as a deferred item, not blocking this plan.

---

## Acceptance Criteria

- [ ] `.github/workflows/markdown-lint.yml` exists on `achantas-data` `origin/main` and validates via `actionlint`.
- [ ] `.github/workflows/link-check.yml` exists on `achantas-data` `origin/main` (includes `pull_request` trigger), validates via `actionlint`.
- [ ] `.markdownlint.jsonc` exists on `achantas-data` `origin/main`. **Floor check**: the non-negotiable rules (MD001, MD011, MD018-MD020, MD022-MD025, MD027, MD030, MD034, MD035, MD037-MD040, MD042, MD051, MD053 — ≥20 rules) are all enabled; none may be set to `false` to achieve a green run. The §TDD step-2 assertion script exits 0 against the final config.
- [ ] `lychee.toml` exists on `achantas-data` `origin/main`.
- [ ] First triggered `markdown-lint` run conclusion = `success`, achieved by **fixing content** (not by disabling any floor rule).
- [ ] First triggered `link-check` run conclusion = `success`. Remediation options for dead links: (a) fix the link, or (b) add a **per-URL** exclusion to `lychee.toml` with an inline comment stating why and a dated TODO for re-check. **Whole-host / wildcard exclusions are prohibited**. Exclusion list must resolve ≥95% of discovered links (i.e., total excludes ≤5% of unique URLs in the corpus), and must not exceed 25 entries per audit cycle — exceeding either threshold requires a follow-up issue rather than further suppression.
- [ ] `gh api repos/vamseeachanta/achantas-data/actions/workflows` returns `total_count: 2`.
- [ ] Review artifacts posted to `scripts/review/results/` (Claude + Codex + Gemini per cross-review policy).
- [ ] Close-out comment on #2443 links both successful run URLs and confirms scope (no Python-tests restoration — see §OUT of scope for evidence).

### Explicitly OUT of scope

- **Restoring `python-tests.yml`**. The tracked Python scaffolding (`src/`, `tests/`, `pyproject.toml`) is idle; restoring it would produce failing runs on the first execution (`test_smoke.py` + `test_utils.py` have not been exercised in months and may reference paths that no longer exist). If the user wants Python CI back, file a follow-up issue.
- **Adding `pr-title-lint.yml`** (mentioned as "optional" in issue body). Defer to a future issue if desired.
- **Enforcing markdown-lint on PDF, docx, or `.txt` files**. Out of format scope.
- **Repo-wide style normalization pass** (fixing existing MD violations). The lenient config is chosen *so that* no normalization pass is needed. If violations remain after config tuning, defer a cleanup pass to a follow-up issue.
- **Syncing this template into sibling docs-heavy repos** (achantas-media, etc.). Follow-up after this pair is proven green.
- **Any workspace-hub commit / push / label change / marker creation** during drafting (per user's hard constraints on this session).

---

## Adversarial Review Summary

### Wave 1 (2026-04-21)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | Rubber-stamp CI risk (no non-negotiable lint floor); dead `issues: write` permission; .py count drift (13 vs 12); floating action tags; redundant `fail: true`; uncited "10-20×" claim; no `concurrency:` group; MD025 over-relaxed. |
| Codex | MAJOR | TDD hard-rule violation ("traditional unit tests do not apply"); Python-CI exclusion under-evidenced; link-check escape hatch permits whole-host exclusion. |
| Gemini | MAJOR | `link-check.yml` missing `pull_request` trigger; `issues: write` granted without `GITHUB_TOKEN` env (and the action does not auto-open issues anyway); MD024 omitted from disabled/kept list; first-run failure burden on legacy links. |

**Wave 1 overall result:** MAJOR (convergent blockers across 2+ providers on lint-floor, permission-vs-behavior, and escape-hatch breadth).

### Revisions made (Wave 1 → Wave 2)

- **Removed `issues: write` permission** from `link-check.yml` (Claude + Gemini). lychee-action@v2 does not auto-open issues; permission is dead. No `GITHUB_TOKEN` env added since the permission itself is gone.
- **Tightened link-check escape hatch** (Codex + Gemini). Acceptance criterion now prohibits whole-host / wildcard exclusions, requires per-URL excludes with inline why-comments and dated re-check TODOs, caps the exclusion list at 25 entries per audit cycle, and demands ≥95% link resolution.
- **Added `pull_request` trigger** to `link-check.yml` (Gemini). Scoped to `**/*.md`, `lychee.toml`, and the workflow file itself. `timeout-minutes: 10` added to bound PR-trigger runtime.
- **Removed "traditional unit tests do not apply"** language; replaced §TDD Test List with a 9-step red→green sequence including a config-parse assertion script that fails before the floor rules are present (satisfies `AGENTS.md` line 7 — "TDD mandatory — tests before implementation; no exceptions"). Also cites `.claude/rules/patterns.md` enforcement-gradient for the pre-commit-hook promotion path.
- **Added non-negotiable lint floor** (Claude). 20-rule minimum listed (MD001, MD011, MD018-MD020, MD022-MD025, MD027, MD030, MD034, MD035, MD037-MD040, MD042, MD051, MD053), cited against the markdownlint rule catalogue. Floor rules cannot be disabled during tuning to achieve green.
- **MD024 enabled** (Gemini). MD025 kept enabled with `{ "level": 1 }` (single top-level H1 per file), only per-file inline overrides allowed.
- **Python-CI exclusion evidence strengthened** (Codex). Added git-log timestamps (Python last touched 2026-03-25 via auto-sync; markdown last touched 2026-04-20 in active PR flow), enumerated the 12 `.py` files, and stated the stale-test reasoning.
- **Deleted uncited "10-20× faster" claim**; softened to maintenance-grounds justification.
- **Added `concurrency:` group** with `cancel-in-progress: true` to both workflows.
- **Reconciled .py file count** to 12 (was 13) in two places.
- **Removed redundant `fail: true`** from the link-check YAML (default in lychee-action@v2), replaced with a comment noting the default.

### Revisions deferred (with rationale)

- **SHA-pinning third-party actions** (Claude MINOR): `DavidAnson/markdownlint-cli2-action@v16` and `lycheeverse/lychee-action@v2` remain on minor-float tags. Rationale: this is a personal docs repo, not a security-sensitive production workflow; SHA-pin maintenance cost exceeds the supply-chain risk for a doc-only CI. Flagged for a follow-up hardening issue if the template is later reused for production repos.
- **`validate-workflows` CI job running `actionlint`** (Claude MINOR): adds a third workflow just to validate the first two. Current plan runs `actionlint` locally as part of the TDD step 3/4 sequence. Defer self-hosting the check until the ecosystem has >3 workflows per repo.
- **Auto-issue creation for lychee failures** (carried forward from original Open Questions): out of scope since the permission was removed. Requires a `peter-evans/create-issue-from-file` step if re-introduced later.
- **Workspace-hub `docs/plans/README.md` index row**: per session hard-constraints, no index update during this drafting pass.

### Status

**Revised, awaiting Wave 2 re-review.**

---

## Risks and Open Questions

- **Risk — existing MD violations**: the lenient config is my best guess; on first local dry-run there may still be non-zero violations (e.g., trailing whitespace, inconsistent list markers) on legacy notes. Mitigation: run `markdownlint-cli2 --fix` locally once before first CI run, OR disable the violating rule if the content is intentional. Acceptance criterion states "tuned until 0 violations" so this is surfaced as a completion blocker, not hidden.
- **Risk — external link rot**: the repo contains old utility / tax / house notes with URLs possibly years old. Lychee's first run may fail. Mitigation: acceptance criterion includes "add rotted host to exclude list with dated TODO". Link-check is weekly scheduled so recurrence cost is bounded.
- **Risk — Actions minutes on free tier**: personal GitHub account, free tier minutes. markdown-lint is path-scoped to `.md` changes; link-check is weekly (≈4 runs/month × ~30s each). Total monthly budget: negligible.
- **Risk — missed detection of workflow schema errors**: no local `actionlint` run before push = silent YAML-syntax failures at GitHub side. Mitigation: acceptance criterion explicitly requires `actionlint` to pass (add to local dev checklist; lightweight — `brew install actionlint` or `go install`).
- **Risk — governance drift already present**: #2443 currently has `status:plan-approved` label without a canonical plan or marker (described in Evidence section). This plan produces the canonical artifact. The label reconciliation (swap to `status:plan-review` while cross-review runs, then back to `status:plan-approved` after user approves this plan) is **out of scope for this drafting pass per user's explicit hard constraints** — flag it to the user in the governance comment so they can decide next step.
- **Open — which lychee version**: `@v2` is current stable (Apr 2026); pinning to `@v2` vs. `@v2.3.0` is user preference. Plan pins to `@v2` (minor-version float) to reduce maintenance; user may request exact pin during review.
- **Resolved — link-check issue-on-failure**: originally proposed via `permissions: issues: write`, but `lycheeverse/lychee-action@v2` does not auto-open GitHub issues (confirmed against action source). Permission removed from the workflow. If visibility via auto-issue is desired later, it requires a follow-up step like `peter-evans/create-issue-from-file` consuming lychee's report — filed as a deferred item, not in scope here.
- **Open — should this plan also update `docs/plans/README.md` index**: planning skill says yes; user's hard constraints for this session say no. Defer to next session / governance comment flag.

---

## Complexity: T1

**T1** — two short YAML files + two short config files, all in an external repo, no new Python or Markdown code being authored, no standards or wiki coupling, no module dependencies. Pseudocode is omitted per T1 rules. The main risk is false-positive MD violations on existing content which is tuned out by the lenient config; there is no algorithmic complexity.
