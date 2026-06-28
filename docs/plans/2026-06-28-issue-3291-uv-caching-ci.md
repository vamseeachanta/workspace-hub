# Plan for #3291: seamless(ci) — uv caching across assetutilities / assethold / digitalmodel test workflows

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3291
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-28-plan-3291-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

This is a CI-only change: add uv dependency caching to the uv-based test workflows of three sibling
repos (`assetutilities`, `assethold`, `digitalmodel`) by copying the already-correct pattern from
`worldenergydata` `ci.yml` and the reusable `workspace-hub` `domain-matrix.yml`. The reference is a
literal copy target — `enable-cache: true` + `cache-dependency-glob: "uv.lock"` on every
`astral-sh/setup-uv` invocation, pinned to `@v7`.

> **Scope is set by owner decision D2 (2026-06-28), applied verbatim below.** D2 narrows the
> digitalmodel edit set to four per-domain `*-tests.yml` files (the uv-based ones), KEEPS the
> existing `cache: 'pip'` on the five plain-pip digitalmodel workflows (no package-manager swap),
> and adds caching only where it is genuinely missing. The earlier draft's "normalize all nine
> digitalmodel workflows / swap pip→uv" Phase-2 and the `quality-gates*.yml` targets are
> **descoped** per D2 (see Files to Change and Risks).

### Owner decision D2 (settled — verbatim)

> **D2 CI CACHING (#3291):** KEEP `cache: 'pip'` on the 5 plain-pip dm workflows
> (catenary-riser, orcaflex, hydrodynamics, gmsh-meshing, viv-analysis) — do NOT swap pip→uv.
> ADD caching ONLY where missing: assetutilities `tests.yml`, assethold, and the 4 dm
> setup-uv files (aqwa / diffraction / mooring-analysis / structural-analysis). No
> package-manager swap.

### Existing repo code (re-verified against live files 2026-06-28)

- **Reference (copy this) — `worldenergydata/.github/workflows/ci.yml`**: every job runs
  ```yaml
        - name: Install uv
          uses: astral-sh/setup-uv@v7
          with:
            enable-cache: true
            cache-dependency-glob: "uv.lock"
  ```
  The reusable `workspace-hub/.github/workflows/domain-matrix.yml:139-142` carries the identical
  block (re-verified). This exact 3-line `with:` block on `@v7` is the pattern to propagate.

- **assetutilities `tests.yml`** — single `tests` job, `astral-sh/setup-uv@v4` at line 24 with
  **no `with:` block** (no `enable-cache`). The install step is `uv sync --group test` (line 28) —
  fully lockfile-driven, so this repo gets the **highest** cache value of the set. Triggers are
  `push`/`pull_request` to `main` (lines 4-7, **no `paths:` filter**) plus `workflow_dispatch`
  (line 8, re-verified). Because there is **no path filter**, a PR that edits only `tests.yml`
  itself **does** fire `pull_request` — so a cache hit is genuinely observable pre-merge on this
  file (the first run is a cold miss that saves, a second run on the same PR branch restores). This
  repo is therefore one of the two **pre-merge cache-hit demonstration** targets (see Acceptance).
  One job, one edit site.

- **assethold `ci.yml`** — **no edit (re-verified).** This file is only a *caller* of the reusable
  `vamseeachanta/workspace-hub/.github/workflows/domain-matrix.yml@main` (line 39), passing
  `python-setup: setup-python` (line 45). It contains **zero `astral-sh/setup-uv` steps of its own**.
  The reusable workflow's `setup-uv@v7` install step (lines 139-142) is **unconditional** — it is NOT
  gated by `python-setup` (only the *Python-provisioning* step at lines 150/154 is gated). Therefore
  assethold `ci.yml` **already inherits uv caching**; the warm `~/.cache/uv` accelerates its
  subsequent `uv pip install --system`. **No change.**

- **assethold `python-tests.yml`** — the comprehensive multi-OS / multi-Python matrix. Uses
  `astral-sh/setup-uv@v1` with `version: "latest"` and **no cache** at **four** sites (re-verified):
  lines **75** (`test` matrix job, 3 OS × 4 Python), **213** (`integration-tests`), **255**
  (`financial-data-tests`), **305** (`security`). `setup-uv@v1` predates the `enable-cache` input —
  the version **must** be bumped (adding `enable-cache` to `@v1` is a silent no-op). Triggers include
  `workflow_dispatch` (line 32) and `pull_request` on `[main, develop]` whose `paths:` filter
  **explicitly lists `.github/workflows/python-tests.yml`** (re-verified, lines 19-30) — so a PR that
  edits only `python-tests.yml` itself **does** fire `pull_request`. This repo is therefore the
  second **pre-merge cache-hit demonstration** target. Install is via
  `uv pip install --system` (not `uv sync`), so the cache warms `~/.cache/uv` but is keyed by
  `uv.lock` as a proxy (real but smaller value than a pure `uv sync` — see Risks).

- **digitalmodel — the 4 uv-based per-domain workflows (D2 targets):**
  `aqwa-tests.yml`, `diffraction-tests.yml`, `mooring-analysis-tests.yml`,
  `structural-analysis-tests.yml` each use `astral-sh/setup-uv@v3` **bare (no `with:`)** at **two**
  sites (re-verified): the `test` job (line 34) and the `lint`/quality job (line 71 for diffraction,
  line 75 for the other three). Install is `uv pip install -e .` + a few tools (not `uv sync`).
  **Trigger gap (re-verified 2026-06-28, the Round-2 MAJOR):** each file's `on:` block is
  `push` on `[main, develop]` with `paths:` = `src/digitalmodel/modules/<m>/**`,
  `tests/domains/<m>/**`, **and `.github/workflows/<m>-tests.yml`**; and `pull_request` on
  `[main, develop]` with `paths:` = `src/.../<m>/**` and `tests/domains/<m>/**` **but NOT the
  workflow YAML**. There is **no `workflow_dispatch`**. Consequence: a feature-branch PR that edits
  *only* the workflow YAML (which is exactly what this cache change is) fires **neither** trigger
  pre-merge — `pull_request` excludes the YAML from its `paths:`, and `push` is branch-filtered to
  `main`/`develop` (a PR feature branch is neither). The workflow only runs **post-merge** (the
  `push`-to-`main` `paths:` filter *does* include the YAML). Therefore these four files **cannot
  self-verify a cache hit pre-merge** through their own triggers, and the prior draft's claim of "two
  PR-branch runs" was wrong. **Fix (this revision):** in addition to the cache block + `@v3`→`@v7`
  bump, **add a `workflow_dispatch:` trigger** to each of the four `on:` blocks so they become
  manually runnable via `gh workflow run <file>`. (Pre-merge cache-hit *evidence* for AC#8 is
  demonstrated on assetutilities + assethold, whose triggers DO fire on their own cache edit; the dm
  four are verified by `workflow_dispatch` — see the GitHub default-branch caveat in Risks. D2 is a
  caching change, not a package-manager swap — uv stays uv, the install commands are untouched.)

- **digitalmodel — the 5 plain-pip per-domain workflows (KEEP, do NOT touch):**
  `catenary-riser-tests.yml`, `orcaflex-tests.yml`, `hydrodynamics-tests.yml`,
  `gmsh-meshing-tests.yml`, `viv-analysis-tests.yml` use `actions/setup-python@v5` with
  `cache: 'pip'` and install via plain `pip install` (re-verified). **Per D2 these are left exactly
  as-is** — `cache: 'pip'` stays, no pip→uv swap. (Observed but out-of-scope: a few of these have a
  third job — integration/build — that lacks `cache: 'pip'`; D2 does not enumerate them for edits, so
  they are not touched here. Noted as a follow-on candidate, not part of #3291.)

- **digitalmodel `workflow-automation-tests.yml`** — already correct: `setup-uv@v5` +
  `enable-cache: true` (line 31-33; note it sets `enable-cache` only, no `cache-dependency-glob`).
  No change.

### Descoped per D2 (digitalmodel `quality-gates*.yml`)

The earlier draft named `quality-gates.yml` and `quality-gates-by-domain.yml` as Phase-1 targets.
D2's add-list is explicit (`"ADD caching ONLY where missing: assetutilities tests.yml, assethold,
and the 4 dm setup-uv files"`) and does **not** include either file. Both are therefore **out of
scope for #3291**:

- `quality-gates.yml` installs uv via **raw `curl -LsSf https://astral.sh/uv/install.sh | sh`**
  (lines 30-32). Converting that to `setup-uv@v7` is an **install-method change**, which D2's
  "No package-manager swap" directive deliberately avoids. Excluded.
- `quality-gates-by-domain.yml` uses `setup-uv@v5` (no `enable-cache`) at three sites (lines 31, 72,
  100). The mechanical edit here would be **identical** to the 4 dm targets, but the owner did not
  enumerate it in D2. Excluded; **recommended as a fast-follow issue** (see Risks/Open Questions).

### Standards

Not applicable — CI/infra change, no engineering standard involved.

### LLM Wiki pages consulted

No relevant wiki pages — this change touches no wiki content (Client: N/A).

### Documents consulted

- Issue #3291 body (Evidence block dated 2026-06-27) — cited line ranges re-verified against the
  live files. One premise (assethold `ci.yml` "no cache, re-clones assetutilities per leg") is
  **inaccurate**: that file delegates caching to the already-cached reusable workflow.
- Owner decision **D2** (2026-06-28) — settles the digitalmodel scope and the pip-vs-uv question.
- Parent epic #3290 (Theme A, CI speed) — referenced in the issue header.
- `worldenergydata/.github/workflows/ci.yml` — the sanctioned reference pattern.
- `workspace-hub/.github/workflows/domain-matrix.yml` — the reusable workflow assethold `ci.yml`
  inherits caching from (re-verified unconditional).

### Gaps identified

- No way to observe a real cache hit by static inspection — a hit/miss only appears in the GitHub
  Actions log of a *second* run on an unchanged `uv.lock`. **Pre-merge** cache-hit verification is
  possible **only on the two repos whose triggers fire on their own cache edit**: assetutilities
  `tests.yml` (`pull_request` to `main`, **no `paths:` filter**) and assethold `python-tests.yml`
  (`pull_request` `paths:` **explicitly lists** `.github/workflows/python-tests.yml`); both also
  carry `workflow_dispatch`. On those two, the first PR run is a cold miss that *saves* the cache and
  a second run on the same PR branch (a no-op follow-up push or a `workflow_dispatch` re-run)
  *restores* it. The **four digitalmodel `*-tests.yml` files CANNOT** be cache-hit-verified pre-merge
  through their own triggers — their `pull_request` `paths:` exclude the workflow YAML and their
  `push` is branch-filtered to `main`/`develop` (see the dm-four bullet above). This revision adds a
  `workflow_dispatch:` trigger to the four so they are manually runnable; the binding pre-merge
  cache-hit AC (#8) is demonstrated on **assetutilities + assethold**, with the dm four verified via
  `workflow_dispatch` (subject to the GitHub default-branch caveat in Risks). Post-merge confirmation
  on `main` (where the dm-four `push` `paths:` filter *does* match the YAML) is secondary (see
  Acceptance).
- `astral-sh/setup-uv` version skew across the fleet (v1/v3/v4/v5/v7). The version-pin policy is now
  **settled** (see below): bump every touched site to `@v7`. This eliminates the `@v1` silent-no-op
  hazard and removes any uncertainty about whether `@v3`/`@v4` honor `enable-cache`, by matching the
  pin already proven in `worldenergydata/ci.yml` and `domain-matrix.yml`.

### Settled decision — version-pin policy (was an Open Question)

Bump **all touched** `setup-uv` sites to `@v7`:
- **Mandatory** for assethold `python-tests.yml` (`@v1` cannot cache at all).
- **Chosen** for assetutilities (`@v4`) and the 4 dm files (`@v3`) to guarantee `enable-cache`
  support and match the sanctioned reference (`worldenergydata` + `domain-matrix` both pin `@v7`).
- This is a **version-pin bump of the same action** (uv stays uv; install commands, matrix, and
  triggers are untouched) — NOT the package-manager swap D2 prohibits. Rejected alternative: "keep
  each existing pin, add only the flag" — leaves a real risk that `@v3`/`@v4` silently ignore
  `enable-cache`, which is exactly the failure mode being fixed.

### Evidence (embedded verification)

**Issue status** (verified 2026-06-28 via `gh issue view 3291`):
- `#3291` — OPEN — "seamless(ci): uv caching across assetutilities / assethold / digitalmodel test workflows"

**File existence** (`ls -la`, 2026-06-28):
- EXISTS: `worldenergydata/.github/workflows/ci.yml` — reference
- EXISTS: `assetutilities/.github/workflows/tests.yml` (995 B)
- EXISTS: `assethold/.github/workflows/ci.yml` (2973 B) — caller, no-change
- EXISTS: `assethold/.github/workflows/python-tests.yml` (11473 B)
- EXISTS: `digitalmodel/.github/workflows/{aqwa,diffraction,mooring-analysis,structural-analysis}-tests.yml`
- EXISTS: `digitalmodel/.github/workflows/{catenary-riser,orcaflex,hydrodynamics,gmsh-meshing,viv-analysis}-tests.yml` — pip, KEEP
- EXISTS: `digitalmodel/.github/workflows/{quality-gates,quality-gates-by-domain}.yml` — descoped per D2
- EXISTS: `workspace-hub/.github/workflows/domain-matrix.yml` — reusable
- EXISTS: `uv.lock` in all four repos (assetutilities 6458, assethold 7635, digitalmodel 7792,
  worldenergydata 7948 lines) — confirms `cache-dependency-glob: "uv.lock"` resolves a real file in
  every target.

**Line excerpts** (re-verified via Read/grep 2026-06-28):
```
worldenergydata/ci.yml (reference):
      - name: Install uv
        uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

assetutilities/tests.yml:23-24
      - name: Install uv
        uses: astral-sh/setup-uv@v4        # <-- no `with:` block ; install = `uv sync --group test`

assethold/python-tests.yml: setup-uv@v1 + version:"latest" at :75, :213, :255, :305  # <-- @v1 predates enable-cache

digitalmodel/aqwa-tests.yml:34,75            setup-uv@v3 (bare)   # install = uv pip install -e .
digitalmodel/diffraction-tests.yml:34,71     setup-uv@v3 (bare)
digitalmodel/mooring-analysis-tests.yml:34,75 setup-uv@v3 (bare)
digitalmodel/structural-analysis-tests.yml:34,75 setup-uv@v3 (bare)

digitalmodel/{catenary-riser,orcaflex,hydrodynamics,gmsh-meshing,viv-analysis}-tests.yml
      uses: actions/setup-python@v5 ; with: { cache: 'pip' } ; install = plain `pip install`  # <-- KEEP per D2

workspace-hub/domain-matrix.yml:139-142  (UNCONDITIONAL — assethold ci.yml inherits this)
      uses: astral-sh/setup-uv@v7
      with:
        enable-cache: true
        cache-dependency-glob: "uv.lock"
```

**Gap proof** (assethold ci.yml has no setup-uv of its own):
- `grep -c astral-sh/setup-uv assethold/.github/workflows/ci.yml` → `0` → confirms ci.yml cannot add
  caching locally; it inherits from the reusable workflow.

**Reproduction proofs:**
- Reproduction: **N/A** — pure CI-yaml change. There is no runtime/behavioral failure to reproduce;
  the "defect" is the *absence* of a `with:` cache block on uv-based steps, verified by direct file
  inspection above. A real cache hit is observed in the Actions log of a second run (see Acceptance).
  Verified by inspecting the actual yaml files, not a convenient proxy.

<!-- Distinct sources: issue #3291, worldenergydata/ci.yml, assetutilities/tests.yml, assethold/ci.yml,
     assethold/python-tests.yml, digitalmodel/{aqwa,diffraction,mooring-analysis,structural-analysis}-tests.yml,
     workspace-hub/domain-matrix.yml = 8+ distinct sources (≥3 required). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-28-issue-3291-uv-caching-ci.md |
| Edit | assetutilities/.github/workflows/tests.yml |
| Edit | assethold/.github/workflows/python-tests.yml |
| Edit (cache block + `@v7` + add `workflow_dispatch:`) | digitalmodel/.github/workflows/aqwa-tests.yml |
| Edit (cache block + `@v7` + add `workflow_dispatch:`) | digitalmodel/.github/workflows/diffraction-tests.yml |
| Edit (cache block + `@v7` + add `workflow_dispatch:`) | digitalmodel/.github/workflows/mooring-analysis-tests.yml |
| Edit (cache block + `@v7` + add `workflow_dispatch:`) | digitalmodel/.github/workflows/structural-analysis-tests.yml |
| No change (documented) | assethold/.github/workflows/ci.yml (inherits cache from domain-matrix.yml@main) |
| No change (KEEP, per D2) | digitalmodel/.github/workflows/{catenary-riser,orcaflex,hydrodynamics,gmsh-meshing,viv-analysis}-tests.yml (keep `cache: 'pip'`) |
| Descoped (per D2) | digitalmodel/.github/workflows/{quality-gates,quality-gates-by-domain}.yml |
| Plan review — Claude | scripts/review/results/2026-06-28-plan-3291-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-28-plan-3291-codex.md |
| Plan review — Gemini | scripts/review/results/2026-06-28-plan-3291-gemini.md |

---

## Deliverable

Every uv-based `astral-sh/setup-uv` invocation in the six in-scope files (assetutilities `tests.yml`,
assethold `python-tests.yml`, and the four digitalmodel per-domain `*-tests.yml` named in D2) will be
pinned to `@v7` and will carry `enable-cache: true` + `cache-dependency-glob: "uv.lock"` (copied from
`worldenergydata` `ci.yml` / `domain-matrix.yml`), so a second CI run on an unchanged lockfile
restores the uv cache instead of resolving/downloading cold. In addition, each of the four
digitalmodel `*-tests.yml` files will gain a `workflow_dispatch:` trigger in its `on:` block — these
four are **not** runnable pre-merge by a YAML-only PR (their `pull_request` `paths:` filter excludes
the workflow file and their `push` is branch-filtered to `main`/`develop`), so `workflow_dispatch`
gives them a manual run handle (`gh workflow run <file>`). The binding pre-merge cache-hit evidence
(AC#8) is demonstrated on assetutilities `tests.yml` + assethold `python-tests.yml`, whose triggers
DO fire on their own cache edit; the dm four are verified via `workflow_dispatch` (subject to the
GitHub default-branch caveat in Risks). The five plain-pip digitalmodel
workflows keep their existing `cache: 'pip'` unchanged (D2: no package-manager swap). assethold
`ci.yml` is unchanged (it already inherits caching from the reusable workflow).

---

## Pseudocode

```
# Six in-scope files; 13 total setup-uv edit sites.
for each in-scope file:
    for each `astral-sh/setup-uv@<ver>` step:
        set pin to @v7                                  # bump from @v1/@v3/@v4
        ensure the step has a `with:` block containing:
            enable-cache: true
            cache-dependency-glob: "uv.lock"
        drop now-stale `with:` keys made redundant by the bump
            (assethold @v1 `version: "latest"` is dropped on bump to @v7)

# Additionally, for the 4 digitalmodel files ONLY (they cannot self-verify pre-merge —
# pull_request paths exclude the workflow YAML, push is branch-filtered to main/develop):
for f in [aqwa, diffraction, mooring-analysis, structural-analysis]-tests.yml:
    add to the `on:` block a top-level:
        workflow_dispatch:
    # gives `gh workflow run <f>` as a manual run handle; does NOT alter push/pull_request
    # paths, branches, matrix, or install commands.

# Per-file site counts (re-verified):
#   assetutilities/tests.yml ................ 1 site  (line 24)
#   assethold/python-tests.yml .............. 4 sites (75, 213, 255, 305)
#   digitalmodel/aqwa-tests.yml ............. 2 sites (34, 75)
#   digitalmodel/diffraction-tests.yml ...... 2 sites (34, 71)
#   digitalmodel/mooring-analysis-tests.yml . 2 sites (34, 75)
#   digitalmodel/structural-analysis-tests.yml 2 sites (34, 75)

# Do NOT touch (per D2):
#   - the 5 plain-pip dm workflows: keep `cache: 'pip'`, keep plain `pip install`.
#   - digitalmodel quality-gates.yml / quality-gates-by-domain.yml (descoped).
#   - assethold ci.yml (inherits cache; has no setup-uv step).
# Do NOT change: test selection, matrix, install commands (`uv sync` / `uv pip install`),
#   run steps, or existing push/pull_request triggers (branches + paths).
#   The ONLY trigger change permitted is ADDING `workflow_dispatch:` to the 4 dm files
#   (no removal/edit of their existing push/pull_request blocks). Caching + version pin +
#   the dm-four workflow_dispatch addition only.
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `assetutilities/.github/workflows/tests.yml` | bump setup-uv `@v4`→`@v7` + add `with: {enable-cache, cache-dependency-glob}` (1 site, line 24) |
| Modify | `assethold/.github/workflows/python-tests.yml` | bump setup-uv `@v1`→`@v7` + add cache block at 4 sites (75, 213, 255, 305); drop `version: "latest"` |
| Modify | `digitalmodel/.github/workflows/aqwa-tests.yml` | bump `@v3`→`@v7` + add cache block (2 sites: 34, 75) **+ add `workflow_dispatch:` to `on:` block** (enables pre/post-merge manual run; the `pull_request` `paths:` filter excludes this YAML so it has no other manual trigger) |
| Modify | `digitalmodel/.github/workflows/diffraction-tests.yml` | bump `@v3`→`@v7` + add cache block (2 sites: 34, 71) **+ add `workflow_dispatch:` to `on:` block** |
| Modify | `digitalmodel/.github/workflows/mooring-analysis-tests.yml` | bump `@v3`→`@v7` + add cache block (2 sites: 34, 75) **+ add `workflow_dispatch:` to `on:` block** |
| Modify | `digitalmodel/.github/workflows/structural-analysis-tests.yml` | bump `@v3`→`@v7` + add cache block (2 sites: 34, 75) **+ add `workflow_dispatch:` to `on:` block** |
| No change | `assethold/.github/workflows/ci.yml` | already inherits cache from `domain-matrix.yml@main` (reusable workflow, setup-uv@v7 unconditional, lines 139-142) — documented, not edited |
| No change (KEEP) | `digitalmodel/.github/workflows/{catenary-riser,orcaflex,hydrodynamics,gmsh-meshing,viv-analysis}-tests.yml` | D2: keep existing `cache: 'pip'`; no pip→uv swap |
| Descoped | `digitalmodel/.github/workflows/{quality-gates,quality-gates-by-domain}.yml` | not in D2's add-list; `quality-gates.yml` raw-curl conversion = install-method change avoided; `quality-gates-by-domain.yml` recommended as fast-follow issue |

---

## TDD Test List

CI-yaml changes have no unit-test surface; the "tests" are mechanical verification checks run
pre-merge plus one pre-merge cache-hit observation on a PR branch. Each row is a concrete pass/fail
check applied to the **six in-scope files only**.

| Check | What it verifies | Command | Expected |
|---|---|---|---|
| yaml-parse | each edited file is still valid YAML | `python -c "import yaml; yaml.safe_load(open(f))"` per file | exit 0, no exception |
| actionlint | no GitHub Actions schema/expression errors | `actionlint <file>` (if available) | exit 0 |
| grep-enable-cache | every setup-uv site in-scope now has the cache flag | `grep -c "enable-cache: true" <file>` | == count of setup-uv steps in that file |
| grep-dep-glob | cache key bound to lockfile | `grep -c 'cache-dependency-glob: "uv.lock"' <file>` | == count of setup-uv steps |
| version-floor | no `setup-uv@v1` remains in assethold | `grep -c "setup-uv@v1" assethold/.github/workflows/python-tests.yml` | 0 |
| version-pin | every touched site pinned to `@v7` | `grep -cE "setup-uv@v[1-6]" <file>` | 0 in each in-scope file |
| pip-cache-untouched | the 5 plain-pip dm files are byte-unchanged | `git diff --stat -- digitalmodel/.github/workflows/{catenary-riser,orcaflex,hydrodynamics,gmsh-meshing,viv-analysis}-tests.yml` | empty (no diff) |
| descope-untouched | quality-gates* unchanged | `git diff --stat -- digitalmodel/.github/workflows/quality-gates*.yml` | empty (no diff) |
| dm-workflow-dispatch-added | each of the 4 dm files has a `workflow_dispatch:` trigger | `grep -c "^  workflow_dispatch:" digitalmodel/.github/workflows/{aqwa,diffraction,mooring-analysis,structural-analysis}-tests.yml` | == 1 per file |
| dm-trigger-paths-unchanged | the 4 dm files' existing `push`/`pull_request` `branches:`+`paths:` are byte-unchanged (only `workflow_dispatch:` added) | `git diff` review of the `on:` block per dm file | no edit to existing push/pull_request branches/paths; only a new `workflow_dispatch:` line |
| caching-pin-and-dispatch-only-diff | only cache lines + `@v7` pins + (dm-four) `workflow_dispatch:` changed | `git diff` review per file | no change to matrix, install-cmd, run steps, or existing push/pull_request triggers |
| pre-merge cache-hit (assetutilities + assethold) | 2nd PR-branch run restores cache on a repo whose trigger fires on the cache edit | open PR editing the cache file → 1st run (cold, saves) → no-op push or `workflow_dispatch` re-run → read 2nd run's setup-uv log | "uv cache restored" / cache-hit reported, pre-merge, on assetutilities `tests.yml` AND/OR assethold `python-tests.yml` |
| dm-four cache-hit (workflow_dispatch) | the dm four restore cache when manually run | `gh workflow run <file>` twice on an unchanged `uv.lock` (1st cold/saves, 2nd restores) → read 2nd run's setup-uv log | cache-hit reported; note GitHub requires `workflow_dispatch:` to be present on the default branch before dispatch is accepted (see Risks) — so this runs post-merge or after a default-branch carrier commit |

---

## Acceptance Criteria

- [ ] All six in-scope files parse as valid YAML and pass `actionlint` (where available).
- [ ] Every `astral-sh/setup-uv` step in the six in-scope files is pinned `@v7` and carries
      `enable-cache: true` + `cache-dependency-glob: "uv.lock"`.
- [ ] No `astral-sh/setup-uv@v1` (or any `@v1`–`@v6`) remains in any in-scope file (caching would
      silently no-op on `@v1`).
- [ ] The five plain-pip digitalmodel workflows are **byte-unchanged** — `cache: 'pip'` retained, no
      pip→uv swap (D2).
- [ ] `digitalmodel/quality-gates.yml` and `quality-gates-by-domain.yml` are **byte-unchanged**
      (descoped per D2).
- [ ] assethold `ci.yml` is documented as unchanged (cache inherited from the reusable workflow) —
      no edit applied.
- [ ] Each of the four digitalmodel `*-tests.yml` files has a `workflow_dispatch:` trigger added to
      its `on:` block; the existing `push`/`pull_request` `branches:` + `paths:` are otherwise
      byte-unchanged.
- [ ] `git diff` confirms caching + `@v7`-pin changes + (dm-four) the added `workflow_dispatch:`
      only — no edits to matrix, install commands, run steps, or the existing push/pull_request
      branches/paths.
- [ ] **Pre-merge cache-hit observed (on the two repos whose triggers fire on the cache edit):** on
      the PR branch, a second CI run on an unchanged `uv.lock` shows a cache hit in the `setup-uv`
      step log of **assetutilities `tests.yml` AND/OR assethold `python-tests.yml`** (cite the run
      URLs and the before/after `setup-uv` restore line from `gh run view`). First run is the
      expected cold miss that saves the cache; the second run restores it. assetutilities
      (`pull_request` to `main`, no `paths:` filter) and assethold (`pull_request` `paths:` lists the
      workflow YAML) both fire on their own cache edit and both also support `workflow_dispatch` for
      an explicit re-run. **The four digitalmodel files are NOT claimed to self-verify pre-merge** —
      their `pull_request` `paths:` exclude the workflow YAML and their `push` is branch-filtered, so
      a YAML-only PR triggers neither.
- [ ] **dm-four cache-hit verified via `workflow_dispatch`:** each of the four digitalmodel files
      shows a cache hit on a second `gh workflow run <file>` over an unchanged `uv.lock` (cite run
      URLs). Note GitHub only accepts a `workflow_dispatch` run once the trigger exists on the
      **default branch** (see Risks); this verification therefore runs post-merge (or after a
      default-branch carrier commit), not on the feature-branch PR.
- [ ] *(Secondary, post-merge confirmation — not blocking)* a subsequent `push`-to-`main` run of a
      dm-four workflow (whose `push` `paths:` filter DOES match the workflow YAML) on an unchanged
      lockfile also shows the cache restored.
- [ ] Review artifacts posted to scripts/review/results/.

---

## Adversarial Review Summary

| Round | Provider(s) | Verdict | Key findings |
|---|---|---|---|
| Round 1 | Claude + Codex + Gemini (consolidated) | **MAJOR (5 findings)** | (1) scope contradicted D2 — Phase-2 proposed swapping pip→uv on the 5 plain-pip dm files; (2) `quality-gates*.yml` included as targets but not in the owner's add-list (and `quality-gates.yml` raw-curl conversion = install-method change); (3) version-pin left as an unresolved Open Question; (4) self-verify-impossible — cache-hit AC was post-merge-only; (5) "behavior-neutral" overclaim given `setup-uv` major-version bumps |
| Round 2 | (dispatched re-review) | **MAJOR (1 finding) — now addressed** | The 4 dm `*-tests.yml` have `pull_request` `paths:` filters covering only `src/digitalmodel/modules/<m>/**` and `tests/domains/<m>/**` (NOT the workflow YAML) and no `workflow_dispatch`, while `push` is branch-filtered to `main`/`develop` — so a PR editing only those YAMLs triggers neither push nor pull_request pre-merge. The plan's stated two-run pre-merge cache-hit verification did not exist for the dm four; they would have merged with zero pre-merge CI validation. |
| Round 3 | (this re-review) | **PENDING** | — |

**Overall result:** PENDING (Round-3 adversarial review not yet run).

Revision made based on the Round-2 MAJOR (trigger / path-filter gap):
- **dm-four pre-merge verification honesty:** re-verified the actual `on:` blocks of all four dm
  `*-tests.yml` (2026-06-28) — confirmed `pull_request` `paths:` exclude the workflow YAML and `push`
  is branch-filtered, so a YAML-only PR fires neither pre-merge. Fixed throughout: (a) added a
  `workflow_dispatch:` trigger to each of the four (Files to Change, Pseudocode, TDD, AC) so they are
  manually runnable via `gh workflow run`; (b) moved the binding pre-merge cache-hit AC (#8) onto
  assetutilities `tests.yml` + assethold `python-tests.yml`, whose triggers DO fire on their own
  cache edit (assetutilities has no `paths:` filter; assethold's `paths:` lists the workflow YAML);
  (c) the dm four are verified via `workflow_dispatch` + the post-merge `push`-to-`main` run, with an
  explicit Risk documenting GitHub's default-branch requirement (a new `workflow_dispatch` is not
  dispatchable until it lands on `main`, so the dm-four dispatch verification is post-merge). No
  workflow is now claimed to self-verify through a trigger its own path filter excludes.

Revisions made based on Round-1 findings:
- **(1) + (2) scope:** applied D2 verbatim. digitalmodel edit set narrowed to the four uv-based
  per-domain files (aqwa/diffraction/mooring-analysis/structural-analysis); the five plain-pip
  workflows KEEP `cache: 'pip'` (no swap); `quality-gates.yml` and `quality-gates-by-domain.yml`
  descoped (the latter recommended as a fast-follow). Removed the "Phase 1 / Phase 2" framing.
- **(3) version pin:** settled — bump every touched site to `@v7` (mandatory for assethold `@v1`;
  chosen for the rest to match the sanctioned reference and guarantee `enable-cache` support).
  Removed from Open Questions; added a `version-pin` test row and AC.
- **(4) self-verify:** cache-hit AC reworked to a **pre-merge** two-run observation. *(Superseded by
  the Round-2 fix above: the "every target triggers on `pull_request`" assumption was wrong for the
  dm four — their `pull_request` `paths:` exclude the workflow YAML. The binding pre-merge AC now
  rests on assetutilities + assethold; the dm four use `workflow_dispatch` + post-merge runs.)*
  Post-merge confirmation demoted to a non-blocking secondary AC.
- **(5) honesty:** dropped the "behavior-neutral" claim; the change is "caching + `@v7` version-pin
  bump" with install commands/matrix/triggers untouched. Added explicit notes that the dm four and
  assethold install via `uv pip install` (not `uv sync`), so cache value is real but smaller than a
  pure `uv sync` repo.

---

## Risks and Open Questions

- **Risk (premise correction — assethold ci.yml):** the issue says assethold `ci.yml` lacks cache and
  "re-clones assetutilities per leg." In reality `ci.yml` delegates to the reusable
  `domain-matrix.yml@main`, whose `setup-uv@v7` install step caches **unconditionally** (lines
  139-142, re-verified — not gated by `python-setup`). Editing `ci.yml` to add a setup-uv step would
  be wrong (it has none). **Mitigation:** leave `ci.yml` untouched; document the inheritance.
- **Risk (dm-four trigger gap — the Round-2 MAJOR, now addressed):** the four digitalmodel
  `*-tests.yml` files trigger `pull_request` only when files under `src/digitalmodel/modules/<m>/**`
  or `tests/domains/<m>/**` change — the workflow YAML itself is **excluded** from the
  `pull_request` `paths:` — and `push` is branch-filtered to `main`/`develop`. So a feature-branch PR
  that edits *only* the cache lines (exactly this change) fires **neither** trigger pre-merge; the
  earlier draft's "two PR-branch runs" verification was impossible. **Mitigation:** (1) add a
  `workflow_dispatch:` trigger to each of the four so they are manually runnable; (2) move the
  binding pre-merge cache-hit AC onto assetutilities + assethold (whose triggers DO fire on their own
  cache edit); (3) verify the dm four via `workflow_dispatch` + the post-merge `push`-to-`main` run
  (whose `paths:` filter *does* include the YAML). No workflow is claimed to self-verify through a
  trigger its own path filter excludes.
- **Risk (GitHub `workflow_dispatch` default-branch requirement):** GitHub only exposes / accepts a
  `workflow_dispatch` run once the trigger is present on the repository's **default branch**. Because
  these four files do not yet carry `workflow_dispatch` on `main`, `gh workflow run <file> --ref
  <pr-branch>` will be **rejected until the trigger lands on `main`** (i.e., at/after merge, or via a
  separate default-branch carrier commit). **Consequence:** the dm-four `workflow_dispatch`
  cache-hit check is a **post-merge** verification, not a pre-merge one — which is why the binding
  pre-merge AC#8 rests on assetutilities + assethold. The dm four still also get a natural post-merge
  `push`-to-`main` run because that event's `paths:` filter includes the workflow YAML. **Acceptable
  and documented; no pre-merge claim is made for the dm four.**
- **Risk (silent no-op on @v1):** adding `enable-cache` to `setup-uv@v1` (assethold python-tests.yml)
  does nothing — the input postdates v1. **Mitigation:** bump the four sites to `@v7`; verify via the
  `version-floor` + `version-pin` checks.
- **Risk (major-version bump behavior):** bumping `@v1`/`@v3`/`@v4` → `@v7` is a same-action version
  jump, not strictly byte-for-byte behavior-neutral. `@v7` is the pin already running successfully in
  `worldenergydata/ci.yml` and `domain-matrix.yml`, and the install steps in each target are explicit
  (`uv sync` / `uv pip install`), so setup-uv only provisions the binary + cache. **Mitigation:**
  rely on `actionlint` + the pre-merge two-run observation to catch any provisioning regression
  before merge.
- **Risk (cache value for `uv pip install` installs):** assethold `python-tests.yml` and the four dm
  files install via `uv pip install` (not `uv sync`), so `cache-dependency-glob: "uv.lock"` is a
  reasonable *key proxy* rather than the exact installed set; the cache warms `~/.cache/uv` (avoids
  re-downloads) but is smaller than a pure `uv sync` repo's. assetutilities (`uv sync --group test`)
  gets the full value. **Acceptable** — still a real speedup; documented.
- **Risk (assethold cross-OS cache):** `python-tests.yml` runs on `windows-latest` and
  `macos-latest`. setup-uv caching is cross-OS-aware (separate cache per runner OS), so no key
  collision. Low.
- **Open Question (fast-follow for quality-gates-by-domain.yml):** the mechanical edit for
  `quality-gates-by-domain.yml` (`setup-uv@v5` → `@v7` + cache block at lines 31/72/100) is identical
  to the four dm targets and clearly beneficial, but it is **not** enumerated in D2 so it is excluded
  from #3291. **Recommendation:** file a follow-on issue to add caching there (and to evaluate the
  raw-curl `quality-gates.yml` and the un-cached third jobs in the plain-pip workflows). Decision
  deferred to the owner; **not** a blocker for this plan.

---

## Complexity: T2

**T2** — mechanical but multi-file and multi-repo (6 files / 13 edit sites across 3 repos), a
mandatory version-pin bump with a real silent-no-op hazard, a corrected premise requiring judgment
(assethold `ci.yml` no-op), and an owner-set scope boundary (D2) that deliberately leaves the
plain-pip workflows and `quality-gates*.yml` untouched. Not T1 (more than a single trivial
one-liner); not T3 (no logic, no cross-provider systemic design).
