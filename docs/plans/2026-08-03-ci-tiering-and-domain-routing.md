# Plan: tier the test lanes and give every tier-1 repo a domain axis

**Status:** plan-review *(label not applied; `status:plan-approved` is the owner's)*
**Lane:** `lane:claude` · **Complexity:** **T3** (cross-repo; changes what gates every push and PR) · **Client:** N/A
**Issues:** to be filed on approval — one per repo plus the workspace-hub harness change.

> Rewritten 2026-08-03. An earlier draft was lost — written untracked on a repo whose
> auto-sync deletes untracked files (#3791). Committed this time.

## Why

The push gate is **broader and slower than CI**, which is backwards:

| Lane | Scope today | Cost |
|---|---|---|
| PR CI (digitalmodel) | touched shards only | minutes |
| **pre-push** | **entire repo suite** | **~32 min** |

`scripts/testing/run-all-tests.sh` accepts `--repo`, `--coverage` and a `live_data`
exclusion — **no domain scoping, no shallow/deep split**. The cheapest stage carries the
heaviest gate. That is why `--no-verify` is routine, and it is the same inversion #3780
fixed inside the pre-push hook itself.

## What already exists — do not rebuild

digitalmodel has the architecture, and it is well designed:

- `tests/DOMAINS.md` — reviewable table, roots backtick-wrapped, **exactly one owning domain per root**
- `scripts/ci/detect_touched_domains.py` — `--mode full|touched`, `--base`, `--head`, `--domains-file`
- `quality-gates-by-domain.yml` — gated PR lane that **reports its own scope** ("the shards we ran passed", not "all shards passed")
- `full-matrix-sweep.yml` — every shard nightly, under **distinct check names**, so a full-sweep failure never posts under the gated lane's names

That last detail is what most teams get wrong. Extend this pattern; do not invent one.

## Measured gap

| Repo | `DOMAINS.md` | detector | test roots |
|---|---|---|---|
| digitalmodel | **yes** | **yes** | reference implementation |
| assetutilities | no | no | 18 |
| worldenergydata | no | no | 58 |
| assethold | no | no | 25 |

Domain routing is **1 of 4**. A shallow tier can be universal from day one.

## Owner decisions (2026-08-02/03)

1. The domain machinery is for **every** repo.
2. The axis is **per-repo** and follows that repo's natural partition — do not copy digitalmodel's engineering-module axis.
3. **worldenergydata partitions by DATA SOURCE, expressed as modules**: rows are sources, roots are the module paths serving them.
4. Unifying principle — **the jurisdiction that publishes the data**: offshore by regulator (BSEE, HSE/UK, Sodir/Norway); onshore wells by country then region/state (US-TX RRC, US-NM OCD).

### worldenergydata — corrected by measurement

An earlier draft called this the largest item, reasoning that the tree mixed axes and needed
reconciling. **Measurement refuted that** — the tree is already organised by jurisdiction:

| Source | files | | Source | files |
|---|---:|---|---|---:|
| `bsee` | **92** | | `sodir` (Norway) | 28 |
| `texas_rrc` | **62** | | `hse` (UK) | 21 |
| `marine_safety` | 50 | | `canada` | 14 |
| `vessel_fleet` | 47 | | `brazil_anp`·`spain`·`ukcs`·`eia_us`·`west_africa` | 7 each |
| `safety_analysis` | 38 | | `kansas_kgs` | 6 |
| `metocean` | 34 | | `mexico_cnh` | 4 |

So item 4 is **write the manifest over existing structure**. Only the subject-shaped roots
(`drilling`, `marine`, `reservoir`) need an owning domain assigned.

## Lane budgets — the design rule

| Stage | Budget | Runs |
|---|---|---|
| pre-commit | **< 2s** | format, syntax, secrets — staged files only |
| pre-push | **< 30s** | shallow tier, touched domains only |
| PR CI | < 10 min | deep tier, touched domains *(exists in digitalmodel)* |
| main + nightly | unbounded | full sweep, integration, solvers *(exists in digitalmodel)* |

## The two rules that make or break this

Both are the failure this codebase keeps hitting: **absence of signal reading as success.**

- **R-A. An unmarked test must fail collection.** Never default into a tier. Unmarked→shallow silently empties the deep tier; unmarked→deep silently empties pre-push. Enforce at collection time, not by convention.
- **R-B. An unmapped path must fail loudly.** Never map to zero domains. Totality must be **proven by a test**, not asserted in review. `DOMAINS.md` already records this happening: 221 cathodic-protection tests "gated by nothing" (#1923).

## Preconditions — both block the acceptance criteria

1. **#3790 — 487 suppressed test files** (240 WED + 165 assetutilities + 82 digitalmodel).
   A totality proof compares *collected* tests against domain roots, so **a suppressed file
   passes trivially** — never collected, therefore never uncovered. The proof would certify a
   tree with 487 invisible files and report green. Must be resolved first.
2. **#3787 — the pytest startup tax.** A 30s shallow tier is unreachable while a fixed
   multi-second-to-multi-minute cost precedes every invocation. Approved and in progress.
3. **The red baseline** (digitalmodel ~193 failures). Tiering a suite where red is normal only
   redistributes noise. Either green it (dm#1850) or pin a per-domain allowed-failure set so
   *new* red is distinguishable.

## Work breakdown

| # | Item | Repo | Depends on |
|---|---|---|---|
| 1 | Per-domain allowed-failure baseline format + tooling | workspace-hub | — |
| 2 | Baseline populated | digitalmodel | 1 |
| 3 | `DOMAINS.md` + detector | assetutilities | #3790 |
| 4 | `DOMAINS.md` + detector (manifest over existing structure) | worldenergydata | #3790 |
| 5 | `DOMAINS.md` + detector | assethold | #3790 |
| 6 | Shallow-tier marker + enforcement (R-A) | each repo | — |
| 7 | `run-all-tests.sh`: `--shallow`, `--touched` | workspace-hub | 3,4,5,6 |
| 8 | pre-push calls `--shallow --touched` | workspace-hub | 7, 2, #3787 |
| 9 | Totality test (R-B) | each repo | 3,4,5 |

Items 3–5 are independent and parallelisable.

## Acceptance criteria

1. `pytest` collection **fails** on an unmarked test in every tier-1 repo (R-A), demonstrated.
2. A path absent from `DOMAINS.md` **fails** the totality test, demonstrated with a decoy path (R-B).
3. Measured pre-push wall-clock **< 30s** on a representative single-domain change, per repo.
4. A **new** failure not in the baseline breaks the build even when the total count went **down**.
5. Baseline entries are removable only by fixing the test — no auto-refresh path exists.
6. The gated lane still reports its own scope; the full sweep keeps distinct check names.

## Risks and closed questions

- **R1** — Tiering can become a way to run fewer tests and feel faster. Everything rests on R-A and R-B being enforced *by tests*. Reviewers should attack these first.
- **R2** — Timing measurements are worthless on a loaded box; measure serially, and gate on *pre-existing* load (the measurement itself raises it).
- **OQ1 — CLOSED.** I claimed `run-all-tests.sh` fails to resolve siblings. Refuted: `resolve_tier1_repo_path` probes `TIER1_REPOS_BASE`, nested, then flat-sibling (`tier1-repos.sh:33`), qualifying on `.git/` or `pyproject.toml` (`:51`); all three resolve, and a failure emits `skipped`, not `repo_missing` (`run-all-tests.sh:67`). That message came from `check-all.sh`. Item 7 unblocked.
- **OQ2 — CLOSED.** uv speed features were largely off (11 setup-uv steps, 1 cached; zero `--frozen`). Fixed and merged independently: wh#3785 (11/11 + frozen), dm#1957 (9/9).
- **OQ3** — worldenergydata and digitalmodel remain unclassified beyond 180s. Forward progress demonstrated, completion within 900s not proven. Their "before" figures are **censored values, not durations**.

## Adversarial review

*T3 (Claude + Codex + Agy) on approval. Default to non-APPROVE.* Attack first:
1. Can R-A or R-B be satisfied in name only? Show an unmarked test or unmapped path that still goes green.
2. Is "last unconditional exit" / "unmarked" decidable by the proposed parsers, or will they fail valid inputs and pass the defect?
3. Does the plan under-state the blast radius of turning four new hard blocks on at push time?
4. Are the preconditions genuinely blocking, or is that an excuse to defer the hard part?
