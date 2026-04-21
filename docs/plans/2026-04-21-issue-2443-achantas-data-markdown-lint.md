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
- However, the repo **content mix** is overwhelmingly docs: 495 tracked `.md` files vs. 13 tracked `.py` files (git-ls-files count). The active traffic (10+ open issues on personal-data topics in last week, recent commits to `_house/`, `_family/`, `_finance/`) confirms the repo now functions primarily as a markdown knowledge base with legacy Python scaffolding still tracked but idle.
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
- 13 `.py` files tracked (most are `__init__.py`, `conftest.py`, test skeletons)
- 3715 total tracked files (dominated by docs/PDFs)

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
| Create | `.markdownlint.jsonc` | Lenient ruleset: disable `MD013` (line-length), `MD033` (inline HTML), `MD041` (first-line-h1), relax `MD025` (multiple-h1) — personal notes are not published prose |
| Create | `lychee.toml` | Accept 200/206/429, retry once, ignore localhost + example.com + archive.org, max 5 concurrent, 20s timeout |

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
  schedule:
    - cron: '0 13 * * 1'   # Mondays 13:00 UTC = 08:00 CT
  workflow_dispatch:
permissions:
  contents: read
  issues: write            # allow lychee to open summary issue on failure (optional)
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: lychee
        uses: lycheeverse/lychee-action@v2
        with:
          args: --config ./lychee.toml '**/*.md'
          fail: true
```

### Tool choice rationale

- **markdownlint-cli2 (via `DavidAnson/markdownlint-cli2-action`)** over `markdownlint-cli` v1 — cli2 is the maintained successor, faster, and has first-class action support. Over `pymarkdown` / `remark-lint` — markdownlint is the de facto standard in Actions-based repos, config is portable.
- **lychee (via `lycheeverse/lychee-action@v2`)** over `gaurav-nelson/github-action-markdown-link-check` / `tcort/markdown-link-check` — lychee is Rust-based, 10-20× faster on 495-file repos, better retry/accept-code semantics, supports both markdown + HTML + plaintext. node-based link-check tools on 495 MD files routinely timeout.
- **Lenient markdownlint config** rationale: this is a personal-data + issues knowledge base, not public-facing prose. MD013 (line-length) and MD041 (h1-first) fight natural note-taking. MD033 fires on embedded `<br>` / `<details>` which are legitimate. Cost of strict rules = false-positive noise that trains the user to ignore CI. Cost of lenient rules = a few stylistic inconsistencies — acceptable.

---

## TDD Test List

T1 infrastructure — traditional unit tests do not apply. Functional verification criteria:

| Check | How verified | Expected result |
|---|---|---|
| markdown-lint workflow parses | `actionlint .github/workflows/markdown-lint.yml` (or GH push-time schema check) | no schema errors |
| link-check workflow parses | `actionlint .github/workflows/link-check.yml` | no schema errors |
| markdown-lint run green on first push | `gh run watch` after merge | conclusion: `success` |
| link-check run green on manual dispatch | `gh workflow run link-check.yml && gh run watch` | conclusion: `success` |
| No Actions-minutes burn on non-MD commits | push a `.py`-only commit, inspect `gh run list` | no `markdown-lint` run triggered |
| Lenient config does not fail on existing content | run markdownlint locally before push | 0 violations (or known-intentional list documented) |

**Pre-commit local dry-run** (recommended before pushing to achantas-data):
```bash
cd achantas-data
npx markdownlint-cli2 --config .markdownlint.jsonc '**/*.md'
# Expect: exits 0 or lists only rules the config explicitly enables
```

---

## Acceptance Criteria

- [ ] `.github/workflows/markdown-lint.yml` exists on `achantas-data` `origin/main` and validates via `actionlint`.
- [ ] `.github/workflows/link-check.yml` exists on `achantas-data` `origin/main` and validates via `actionlint`.
- [ ] `.markdownlint.jsonc` exists on `achantas-data` `origin/main` with documented lenient ruleset.
- [ ] `lychee.toml` exists on `achantas-data` `origin/main`.
- [ ] First triggered `markdown-lint` run conclusion = `success` (no pre-existing violations OR lenient config tuned until 0 violations).
- [ ] First triggered `link-check` run conclusion = `success` — if external-link rot is found on first run, either (a) fix the link in the same PR, or (b) add the rotted host to `lychee.toml` `exclude` with a dated TODO comment.
- [ ] `gh api repos/vamseeachanta/achantas-data/actions/workflows` returns `total_count: 2`.
- [ ] Review artifacts posted to `scripts/review/results/` (Claude + Codex + Gemini per cross-review policy).
- [ ] Close-out comment on #2443 links both successful run URLs and confirms scope (no Python-tests restoration).

### Explicitly OUT of scope

- **Restoring `python-tests.yml`**. The tracked Python scaffolding (`src/`, `tests/`, `pyproject.toml`) is idle; restoring it would produce failing runs on the first execution (`test_smoke.py` + `test_utils.py` have not been exercised in months and may reference paths that no longer exist). If the user wants Python CI back, file a follow-up issue.
- **Adding `pr-title-lint.yml`** (mentioned as "optional" in issue body). Defer to a future issue if desired.
- **Enforcing markdown-lint on PDF, docx, or `.txt` files**. Out of format scope.
- **Repo-wide style normalization pass** (fixing existing MD violations). The lenient config is chosen *so that* no normalization pass is needed. If violations remain after config tuning, defer a cleanup pass to a follow-up issue.
- **Syncing this template into sibling docs-heavy repos** (achantas-media, etc.). Follow-up after this pair is proven green.
- **Any workspace-hub commit / push / label change / marker creation** during drafting (per user's hard constraints on this session).

---

## Adversarial Review Summary

<!-- To be filled after Step 3 completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (review wave not yet dispatched).

---

## Risks and Open Questions

- **Risk — existing MD violations**: the lenient config is my best guess; on first local dry-run there may still be non-zero violations (e.g., trailing whitespace, inconsistent list markers) on legacy notes. Mitigation: run `markdownlint-cli2 --fix` locally once before first CI run, OR disable the violating rule if the content is intentional. Acceptance criterion states "tuned until 0 violations" so this is surfaced as a completion blocker, not hidden.
- **Risk — external link rot**: the repo contains old utility / tax / house notes with URLs possibly years old. Lychee's first run may fail. Mitigation: acceptance criterion includes "add rotted host to exclude list with dated TODO". Link-check is weekly scheduled so recurrence cost is bounded.
- **Risk — Actions minutes on free tier**: personal GitHub account, free tier minutes. markdown-lint is path-scoped to `.md` changes; link-check is weekly (≈4 runs/month × ~30s each). Total monthly budget: negligible.
- **Risk — missed detection of workflow schema errors**: no local `actionlint` run before push = silent YAML-syntax failures at GitHub side. Mitigation: acceptance criterion explicitly requires `actionlint` to pass (add to local dev checklist; lightweight — `brew install actionlint` or `go install`).
- **Risk — governance drift already present**: #2443 currently has `status:plan-approved` label without a canonical plan or marker (described in Evidence section). This plan produces the canonical artifact. The label reconciliation (swap to `status:plan-review` while cross-review runs, then back to `status:plan-approved` after user approves this plan) is **out of scope for this drafting pass per user's explicit hard constraints** — flag it to the user in the governance comment so they can decide next step.
- **Open — which lychee version**: `@v2` is current stable (Apr 2026); pinning to `@v2` vs. `@v2.3.0` is user preference. Plan pins to `@v2` (minor-version float) to reduce maintenance; user may request exact pin during review.
- **Open — should link-check issue-on-failure be enabled**: `permissions: issues: write` allows lychee to open a GitHub issue summarizing broken links. Creates noise but improves visibility. Default: enabled; user may disable during review.
- **Open — should this plan also update `docs/plans/README.md` index**: planning skill says yes; user's hard constraints for this session say no. Defer to next session / governance comment flag.

---

## Complexity: T1

**T1** — two short YAML files + two short config files, all in an external repo, no new Python or Markdown code being authored, no standards or wiki coupling, no module dependencies. Pseudocode is omitted per T1 rules. The main risk is false-positive MD violations on existing content which is tuned out by the lenient config; there is no algorithmic complexity.
