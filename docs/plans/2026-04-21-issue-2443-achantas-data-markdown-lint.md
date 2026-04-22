# Plan for #2443: achantas-data — restore CI with markdown-lint + link-check (workflows deleted 2025-10)

> **Status:** draft (v3 — Wave 2 MAJOR findings addressed, awaiting Wave 3 re-review)
> **Complexity:** T1
> **Date:** 2026-04-21 (v3 revision: 2026-04-22)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2443
> **Parent meta-issue:** https://github.com/vamseeachanta/workspace-hub/issues/2424
> **Review artifacts:** `-claude.md` / `-codex.md` / `-gemini.md` (Wave 1), `-*-r2.md` (Wave 2), `-*-r3.md` (Wave 3 — to be generated for this revision)

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
    paths: ['**/*.md', '.markdownlint.jsonc', '.github/workflows/markdown-lint.yml']
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
          fail: true   # explicit (defense-in-depth vs. floating @v2 tag; Wave-2 Claude finding)
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
| 2 | Author the floor-verifier **first** (test-before-implementation), then author `.markdownlint.jsonc` and assert it enables every floor rule under ALL config shapes (including `{"default": false}` bypass). Verifier script lives at `scripts/verify-markdownlint-floor.sh` in the achantas-data repo and is callable from a pre-commit hook. Uses stdlib-only parsing (strips JSONC line/block comments, then `json.load`) — no `json5` / external-package dependency. The check explicitly rejects configs with `default: false` unless every single floor rule is independently set to `true`. Full script content is frozen in `### Floor-verifier script` below. | verifier missing OR config absent OR any floor rule's effective value is `false` (accounting for a `default: false` setting disabling unlisted rules) → exit 1 | verifier present AND config present AND every floor rule effectively enabled → exit 0 |
| 3 | Author `.github/workflows/markdown-lint.yml`, validate schema | `command -v actionlint || { echo "FAIL: install actionlint — https://github.com/rhysd/actionlint"; exit 1; }; actionlint .github/workflows/markdown-lint.yml` (availability is gated — missing tool fails loudly, not silently) | schema errors (file missing or malformed) OR actionlint missing | no errors |
| 4 | Author `.github/workflows/link-check.yml`, validate schema | `command -v actionlint || { echo "FAIL: install actionlint"; exit 1; }; actionlint .github/workflows/link-check.yml` | schema errors OR actionlint missing | no errors |
| 5 | Local dry-run of markdownlint against the corpus | `npx markdownlint-cli2 --config .markdownlint.jsonc '**/*.md'` | non-zero exit if real defects (fix content; do NOT disable floor rules) | exit 0 |
| 6 | Local dry-run of lychee against the corpus | `lychee --config ./lychee.toml '**/*.md'` | non-zero exit (expected URL rot) — resolve via per-URL `lychee.toml` exclude (whole-host prohibited) or fix links | exit 0 |
| 7 | Push; `markdown-lint` workflow runs on the push | `gh run watch` | (not yet run) | conclusion `success` |
| 8 | Manual dispatch of `link-check` | `gh workflow run link-check.yml && gh run watch` | (not yet run) | conclusion `success` |
| 9 | Push a `.py`-only commit; confirm `markdown-lint` skipped | `gh run list --workflow=markdown-lint.yml --limit 1` | n/a | no new run for the .py commit (path-filter proves scope) |

**Config-parse smoke test** (step 2 above): the floor-rule assertion is the test-before-implementation artifact for the markdownlint config — the verifier script is authored BEFORE the config exists, so running the verifier with no config (or with a bypass config like `{"default": false}`) exits 1. Only a config that effectively enables every floor rule passes. This satisfies the repo's mandatory TDD rule (`AGENTS.md Hard Gates` item 2 — TDD mandatory, tests before implementation) for the config artifact.

### Floor-verifier script

File: `achantas-data/scripts/verify-markdownlint-floor.sh` (authored in step 2 BEFORE `.markdownlint.jsonc` exists). Uses stdlib-only parsing — no `json5` / `jsonc-parser` / other external package dependency. Strips line-comments (`// …`) and block-comments (`/* … */`) from JSONC then `json.load` is sufficient for the configs we author here (we commit to *not* using advanced JSON5 features like trailing commas or unquoted keys — contract test below catches that).

```bash
#!/usr/bin/env bash
# verify-markdownlint-floor.sh — TDD floor-rule gate for .markdownlint.jsonc
# Exit 0 iff every floor rule is effectively enabled (accounting for default:false bypass).
set -euo pipefail
cfg="${1:-.markdownlint.jsonc}"
if [[ ! -f "$cfg" ]]; then
  echo "FAIL: $cfg missing" >&2
  exit 1
fi
python3 - "$cfg" <<'PY'
import json, re, sys
path = sys.argv[1]
raw = open(path).read()
# Strip JSONC comments (line + block) — safe for configs we author.
raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)
raw = re.sub(r'(^|[^:])//[^\n]*', r'\1', raw)
try:
    cfg = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"FAIL: unable to parse {path} as JSONC with stdlib-strip approach: {e}", file=sys.stderr)
    print("Either fix the JSONC to avoid trailing commas / unquoted keys, or rename to .markdownlint.yaml.", file=sys.stderr)
    sys.exit(1)
FLOOR = {"MD001","MD011","MD018","MD019","MD020","MD022","MD023","MD024","MD025",
         "MD027","MD030","MD034","MD035","MD037","MD038","MD039","MD040","MD042",
         "MD051","MD053"}
default_on = cfg.get("default", True) is not False  # True (including implicit True)
violations = []
for r in FLOOR:
    v = cfg.get(r, default_on)  # if absent, effective value = the default
    if v is False or (isinstance(v, dict) is False and v is not True and v is not default_on):
        violations.append((r, v))
    # Extra guard: if default is False, floor rules MUST be explicitly True (not absent, not {}-dict without truthy).
    if not default_on and cfg.get(r, False) is False:
        violations.append((r, f"disabled via default:false + missing explicit true"))
if violations:
    print(f"FAIL: {len(violations)} floor rule(s) not effectively enabled:", file=sys.stderr)
    for r, v in violations:
        print(f"  - {r}: {v!r}", file=sys.stderr)
    sys.exit(1)
print(f"OK: all {len(FLOOR)} floor rules effectively enabled (default_on={default_on})")
PY
```

**Contract test** for the verifier itself (run once during step 2, before authoring the real config): feed the verifier a known-bypass `{"default": false}` stub and confirm it exits 1. This proves the script catches the Wave-2 rubber-stamp bypass path.

```bash
tmp=$(mktemp --suffix=.jsonc); echo '{"default": false}' > "$tmp"
./scripts/verify-markdownlint-floor.sh "$tmp" && { echo "CONTRACT FAIL: verifier accepted bypass config"; rm -f "$tmp"; exit 1; } || echo "OK: verifier rejects bypass config"
rm -f "$tmp"
```

**Promotion path:** step 5 (`npx markdownlint-cli2` dry-run) currently runs as a developer-machine ritual (Level 2 — script, per `.claude/rules/patterns.md` enforcement gradient). Follow-up issue should add a `pre-commit` hook invoking both `scripts/verify-markdownlint-floor.sh` and `npx markdownlint-cli2 --config .markdownlint.jsonc '**/*.md'` so floor enforcement fires automatically on every commit (Level 3). Filed as a deferred item, not blocking this plan.

(Promotion path moved to the §Floor-verifier script section above.)

---

## Acceptance Criteria

- [ ] `.github/workflows/markdown-lint.yml` exists on `achantas-data` `origin/main` and validates via `actionlint`.
- [ ] `.github/workflows/link-check.yml` exists on `achantas-data` `origin/main` (includes `pull_request` trigger), validates via `actionlint`.
- [ ] `.markdownlint.jsonc` exists on `achantas-data` `origin/main`. **Floor check**: the non-negotiable rules (MD001, MD011, MD018-MD020, MD022-MD025, MD027, MD030, MD034, MD035, MD037-MD040, MD042, MD051, MD053 — ≥20 rules) are all enabled; none may be set to `false` to achieve a green run. The §TDD step-2 assertion script exits 0 against the final config.
- [ ] `lychee.toml` exists on `achantas-data` `origin/main`.
- [ ] First triggered `markdown-lint` run conclusion = `success`, achieved by **fixing content** (not by disabling any floor rule).
- [ ] First triggered `link-check` run conclusion = `success`. Remediation options for dead links: (a) fix the link, or (b) add a **per-URL** exclusion to `lychee.toml` with an inline comment stating why and a dated TODO for re-check. **Whole-host / wildcard exclusions are prohibited**. The quantitative cap is the **tighter** of two bounds: (i) ≤25 entries per audit cycle, (ii) ≤5% of unique URLs in the corpus. Denominator for (ii) is the unique-URL count reported by `lychee --dump '**/*.md' | sort -u | wc -l` (executed during implementation step 6 and recorded in the closeout comment). If 5% of unique URLs < 25, bound (ii) binds; otherwise bound (i) binds. Exceeding either binding bound requires a follow-up issue rather than further suppression.
- [ ] `gh api repos/vamseeachanta/achantas-data/actions/workflows` returns `total_count: 2`.
- [ ] Floor-verifier **contract test** passes: the verifier is run once against a `{"default": false}` stub during implementation step 2, exits 1, and that result is recorded in the closeout comment (proves the verifier itself is not bypassable — Wave-2 convergent-MAJOR closure evidence).
- [ ] MD024 / MD025 first-run violation count recorded in the closeout comment (Wave-2 Claude requirement). If MD025 violations > 30 files, execution was split per §Risks and the split-PR decision is documented.
- [ ] Follow-up issue opened to add `validate-workflows.yml` (CI-side `actionlint` gate) within 1 week of this plan landing, cross-linked from #2443 closeout and parent #2424. Rationale: closes the residual local-discipline-only backstop flagged by Codex Wave-2.
- [ ] Wave 3 review artifacts posted to `scripts/review/results/2026-04-21-plan-2443-{claude,codex,gemini}-r3.md`.
- [ ] Close-out comment on #2443 links both successful run URLs, records the MD025 violation count, the lychee unique-URL denominator, the floor-verifier contract-test output, and confirms scope (no Python-tests restoration — see §OUT of scope for evidence).

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

- **SHA-pinning third-party actions** (Claude MINOR → Wave-2 flagged as drift surface): `DavidAnson/markdownlint-cli2-action@v16` and `lycheeverse/lychee-action@v2` remain on minor-float tags. Rationale: this is a personal docs repo, not a security-sensitive production workflow. The Wave-2 concern that floating tags could silently break fail-on-broken-links is addressed by restoring the explicit `fail: true` input on lychee-action (see `link-check.yml` above) — this makes our correctness contract independent of action-version-default drift. When this template is later reused for production repos (a separate canonical-template follow-up), the first action of that follow-up is to SHA-pin both actions. Flagged for a follow-up hardening issue with that scoping.
- **Auto-issue creation for lychee failures** (carried forward from original Open Questions): out of scope since the permission was removed. Requires a `peter-evans/create-issue-from-file` step if re-introduced later.
- **Workspace-hub `docs/plans/README.md` index row**: per session hard-constraints, no index update during this drafting pass.

### Wave 2 (2026-04-21) — three-provider adversarial re-review against v2 plan

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | (1) Step-2 floor-rule assertion has rubber-stamp bypass — `{"default": false}` disables every unlisted floor rule while the `v is False` check still exits 0. (2) `import json5` is not stdlib; missing install instruction → TDD gate fails with wrong-reason error. (3) Lychee arithmetic incoherent — `≤25 entries` AND `≥95% resolution` interact unpredictably on a 495-file corpus; denominator for ≥95% unspecified. (4) Floating action tags `@v16` / `@v2` + removal of explicit `fail: true` creates silent drift surface on the one gate whose job is to fail on rot. (5) `actionlint` availability ungated — missing tool silently skips the gate. (6) MD025 first-run burden unmeasured on 495 legacy notes. |
| Codex | MAJOR | (1) Step-2 assertion same bypass as Claude. (2) Host-exclusion contradiction — `Acceptance Criteria` says "whole-host exclusions prohibited" but `Risks` says "add rotted host to exclude list with dated TODO" (re-introduces exactly what the AC forbids). (3) TDD sequencing is implementation-first (`Author …, then assert`), violating the `AGENTS.md Hard Gates` "tests before implementation" rule while simultaneously claiming compliance. (4) `validate-workflows` deferral is under-justified for a plan whose whole point is restoring CI. |
| Gemini | MINOR | `markdown-lint.yml` `pull_request.paths` omits `.github/workflows/markdown-lint.yml` (a PR that only edits this workflow won't self-trigger). TDD step-2 `import json5` is not stdlib. |

**Wave 2 overall verdict:** MAJOR (Claude + Codex concurrent on step-2 bypass; Codex additional on host-exclusion contradiction and TDD ordering).

### Revisions made in v3 based on Wave 2 review

- (Claude.1 / Codex.1 → resolved) TDD step 2 now authors a separate `scripts/verify-markdownlint-floor.sh` **before** the `.markdownlint.jsonc` exists (tests-before-implementation). The verifier:
  - Parses JSONC with stdlib only (strip comments → `json.load`), no `json5` or other external package dependency.
  - Computes the **effective** enablement of each floor rule — accounting for `default: false` disabling unlisted rules — and fails if any floor rule resolves to `False`.
  - Ships with a **contract test** that feeds it `{"default": false}` and asserts the verifier exits 1. This contract test runs once during step 2 and fails if the verifier itself is bypassable.
  The full script content is frozen inline in `### Floor-verifier script`.
- (Claude.2 / Gemini.2 → resolved) Dependency on `json5` eliminated (stdlib-only parsing, comment-stripping regex). No `pip install json5` needed. If the JSONC author ever introduces JSON5-only features (trailing commas, unquoted keys), the verifier exits 1 with a clear error pointing to either fixing the JSONC or renaming to `.markdownlint.yaml` — contract failure is loud.
- (Claude.3 → resolved) Acceptance criterion's ≥95% resolution rule is rewritten with explicit binding: the quantitative cap is the **tighter** of `25 entries` or `5% of unique URLs`, denominator is `lychee --dump | sort -u | wc -l`. The denominator is measured during step 6 and recorded in the closeout comment, so the gate is falsifiable at review time.
- (Claude.4 → resolved) Explicit `fail: true` restored on `lychee-action@v2` (inline comment tying the restoration to Wave-2 finding). This makes fail-on-broken-links independent of any future default change on the floating `@v2` tag. SHA-pinning deferral rationale is rewritten to explicitly cite this restoration as the substitute hardening.
- (Claude.5 → resolved) TDD steps 3 and 4 now prefix `command -v actionlint || { echo FAIL; exit 1; }` so missing tool fails loudly. If a developer lacks actionlint, the gate no longer silently skips.
- (Claude.6 → documented as Open / Risk) The MD024 / MD025 first-run violation count on the 495-note corpus is unmeasured. Added to §Risks and Open Questions with the mitigation: implementation step 5 (the local `npx markdownlint-cli2` dry-run) **must be run before the push** and the violation count recorded; if >30 files violate MD025, the plan splits into a two-commit execution (content fixes first, then workflow), and the T1 complexity label is revisited.
- (Codex.2 → resolved) Host-exclusion language in §Risks rewritten to state per-URL-only, inline why-comment, dated TODO — no "add rotted host" wording remains. The §Risks entry explicitly supersedes any earlier draft's contradicting language.
- (Codex.3 → resolved) TDD sequencing: step 2 now explicitly authors the verifier BEFORE the `.markdownlint.jsonc`, and the step-2 description reads "Author the floor-verifier **first** (test-before-implementation), then author `.markdownlint.jsonc`…". The `AGENTS.md` citation is rewritten as `AGENTS.md Hard Gates item 2 — TDD mandatory, tests before implementation, no exceptions`, matching the section heading rather than a contested line number.
- (Codex.4 → resolved by restoring `validate-workflows` as a non-deferred commitment) The TDD steps 3 and 4 now fail loudly on missing `actionlint`, closing the local-gate silent-skip. A `validate-workflows.yml` is promoted from "deferred" to "required follow-up within 1 week of this plan landing" (tracked as a stub acceptance checkbox below).
- (Gemini.1 → resolved) `markdown-lint.yml` `pull_request.paths` now includes `.github/workflows/markdown-lint.yml` — a PR that edits only the workflow will self-trigger.

### Status (v3)

**Revised, awaiting Wave 3 re-review.** Not approval-ready until Wave 3 returns no new MAJOR findings AND user explicitly labels `status:plan-approved`. This plan MUST NOT be self-approved by any agent.

---

## Risks and Open Questions

- **Risk — existing MD violations**: the lenient config is my best guess; on first local dry-run there may still be non-zero violations (e.g., trailing whitespace, inconsistent list markers) on legacy notes. Mitigation: run `markdownlint-cli2 --fix` locally once before first CI run, OR disable the violating rule if the content is intentional. Acceptance criterion states "tuned until 0 violations" so this is surfaced as a completion blocker, not hidden.
- **Risk — external link rot**: the repo contains old utility / tax / house notes with URLs possibly years old. Lychee's first run may fail. Mitigation: per the acceptance criterion, rotted links are handled by **per-URL** entries added to `lychee.toml` with an inline comment stating why and a dated TODO for re-check. Host-level / wildcard exclusions remain **prohibited** (this supersedes any earlier draft wording about "adding a rotted host to the exclude list"). Link-check is weekly scheduled so recurrence cost is bounded.
- **Risk — Actions minutes on free tier**: personal GitHub account, free tier minutes. markdown-lint is path-scoped to `.md` changes; link-check is weekly (≈4 runs/month × ~30s each). Total monthly budget: negligible.
- **Risk — missed detection of workflow schema errors**: no local `actionlint` run before push = silent YAML-syntax failures at GitHub side. Mitigation: acceptance criterion explicitly requires `actionlint` to pass (add to local dev checklist; lightweight — `brew install actionlint` or `go install`).
- **Risk — governance drift already present**: #2443 currently has `status:plan-approved` label without a canonical plan or marker (described in Evidence section). This plan produces the canonical artifact. The label reconciliation (swap to `status:plan-review` while cross-review runs, then back to `status:plan-approved` after user approves this plan) is **out of scope for this drafting pass per user's explicit hard constraints** — flag it to the user in the governance comment so they can decide next step.
- **Risk — MD024/MD025 first-run violation count unmeasured** (Wave-2 Claude): the 495 tracked `.md` files have never been linted. MD025 (single top-level H1) is enabled in the floor and cannot be disabled to reach green. On legacy notes, multi-H1 files are common. Mitigation: implementation step 5 (local `npx markdownlint-cli2 --config .markdownlint.jsonc '**/*.md' 2>&1 | tee /tmp/2443-first-lint.txt`) **MUST run before the push** and the MD024/MD025 violation count recorded in the closeout comment. If MD025 violations > 30 files, split execution into two PRs: (a) content-fix PR that resolves MD025 violations (re-flowing duplicate H1s, running `markdownlint-cli2 --fix` where safe), (b) workflow-land PR with the config + workflow files. Revisit T1 classification in that case.
- **Open — which lychee version**: `@v2` is current stable (Apr 2026); pinning to `@v2` vs. `@v2.3.0` is user preference. Plan pins to `@v2` (minor-version float) to reduce maintenance; user may request exact pin during review.
- **Resolved — link-check issue-on-failure**: originally proposed via `permissions: issues: write`, but `lycheeverse/lychee-action@v2` does not auto-open GitHub issues (confirmed against action source). Permission removed from the workflow. If visibility via auto-issue is desired later, it requires a follow-up step like `peter-evans/create-issue-from-file` consuming lychee's report — filed as a deferred item, not in scope here.
- **Open — should this plan also update `docs/plans/README.md` index**: planning skill says yes; user's hard constraints for this session say no. Defer to next session / governance comment flag.

---

## Complexity: T1

**T1** — two short YAML files + two short config files, all in an external repo, no new Python or Markdown code being authored, no standards or wiki coupling, no module dependencies. Pseudocode is omitted per T1 rules. The main risk is false-positive MD violations on existing content which is tuned out by the lenient config; there is no algorithmic complexity.
