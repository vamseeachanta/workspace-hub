# Plan for #3790: resolve the 487 test files excluded from collection

**Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3790
**Status:** plan-review *(label not applied; `status:plan-approved` is the owner's)*
**Lane:** `lane:claude` · **Complexity:** **T3** — three repos, and re-enabling tests changes what CI reports · **Client:** N/A
**Blocks:** the CI-tiering plan (`docs/plans/2026-08-03-ci-tiering-and-domain-routing.md`), which names this a precondition.

## Why this blocks the domain work

The domain-routing totality proof checks that every **collected** test belongs to a domain root. **A suppressed file passes that check trivially** — never collected, therefore never uncoverable. Run against today's tree the proof would certify a codebase with 487 invisible test files and report green.

The proof isn't wrong; it answers a question that excludes the problem. So this is a precondition, not parallel work.

## Measured scope

| repo | suppressed | mechanism |
|---|---:|---|
| `worldenergydata` | **240** min | `pyproject.toml:334` — 16 `testpaths`, 204 `norecursedirs`, 20 `--ignore`; plus hooks from `tests/conftest.py:316`. 1,031 pytest-shaped files, 807 eligible after config. |
| `assetutilities` | **165** | `pytest.ini:3` hides 135 outside `tests/`; platform hook `tests/conftest.py:65` hides 30 more |
| `digitalmodel` | **82** min | `pytest.ini:3`/`:4`; plus 14 `collect_ignore` at `tests/conftest.py:9` |

Counts are **minima** — hook-based exclusions were not exhaustively enumerated. Establishing the true set is step 1, not an assumption.

## Precedent

`digitalmodel/tests/DOMAINS.md` records this happening once already: **221 cathodic-protection tests** "gated by nothing until #1923 — the gate pointed only at `tests/cathodic_protection/`, and `pytest.ini` `norecursedirs` hid the subtree from every shard." That was one directory. This is roughly twice that, across three repos.

A prior audit in this ecosystem also found `collect_ignore` reasons that were each individually plausible and each individually false — "deleted service files" (the files existed), "data files not in git" (generated in memory), "fails with random ordering" (three seeds, all green) — concealing 139 tests of which 113 passed and 2 covered live production crashes.

**So: a suppression's stated reason is a claim, not evidence.**

## Deliverable

Every pytest-shaped file in the three repos is either **collected**, or **excluded for a verified, recorded reason enforced by a marker rather than a path glob** — and a test prevents the next silent hiding.

## Work breakdown

| # | Item | Output |
|---|---|---|
| 1 | **Enumerate exhaustively**, per repo, across all five mechanisms: `testpaths`, `norecursedirs`, `--ignore`, `collect_ignore`, conftest hooks | the actual file set, not a count |
| 2 | **Re-run each candidate** in isolation before judging it | pass / fail / error, measured |
| 3 | **Triage** each into exactly one bucket | obsolete → delete · wrongly hidden → re-enable · legitimately conditional → marker |
| 4 | **Convert legitimate exclusions from path globs to markers** | `-m "not solver"` etc., so the condition is named and checkable |
| 5 | **Recurrence guard** (R-A below) | a test |

Items 1–3 are per-repo and parallelisable; item 5 is shared.

## The rule that makes this durable

**R-A. Every pytest-shaped file must be either collected or explicitly excluded by a marker with a recorded reason.** A path-glob exclusion is invisible at collection time and produces no signal — that is precisely how 487 files accumulated. The guard is a test that enumerates pytest-shaped files, subtracts collected node IDs, and fails on any remainder not carrying a registered exclusion marker.

Without item 5, items 1–4 clear today's debt and the next hidden subtree arrives the same silent way.

## TDD Test List

1. **`test_every_pytest_file_is_collected_or_explicitly_excluded`** — the R-A guard. Must be demonstrated failing against today's tree (it should report ~487), then pass once triage completes.
2. **`test_a_new_hidden_file_fails_the_guard`** — add a decoy test file under a `norecursedirs` path; the guard must fail. **Without this, the guard could silently become a no-op** — the same defect class as the loosened matcher in #3787.
3. **`test_exclusion_markers_carry_a_reason`** — a registered marker without a recorded reason fails.
4. **Per-repo:** re-enabled tests actually run in the lane they were assigned to.

## Acceptance Criteria

1. Tests 1–4 pass; 1 and 2 demonstrated failing beforehand.
2. The enumerated set is **published per repo** (a committed list), so the number is auditable rather than asserted.
3. Every file in that set is dispositioned with a reason that was **verified by re-running it**, not copied from an existing comment.
4. Collected-test count **increases** by the number re-enabled, stated as a number per repo. A flat count means nothing was actually re-enabled.
5. Newly re-enabled failures are **filed, not suppressed** — see R2.

## Risks and Open Questions

### R1 — The obvious shortcut is to broaden the exclusion
If a file is hard to re-enable, the cheap resolution is widening a glob and calling it triaged. **That is the defect, not the fix.** Any case resolved by broadening an exclusion must be reported as such and reviewed. AC3 exists to make the reason checkable.

### R2 — Re-enabling will surface real failures, and that is success
Some of these 487 will fail when re-enabled. Expect the count to go up before it goes down. They must be **filed as defects**, not re-suppressed, and they must not be added to the #3787-adjacent allowed-failure baseline without an owner and an issue. Otherwise this converts invisible tests into invisible failures — the same problem with better bookkeeping.

### R3 — This interacts with the red baseline
digitalmodel is already ~193-red. Re-enabling tests into that noise makes attribution harder. Sequence per repo: enumerate → triage → re-enable → *immediately* file what breaks, before moving to the next repo.

### OQ1 — Is `pytest-shaped` the right universe?
The counts use filename-pattern matching (`test_*.py` / `*_test.py`). A file that defines tests but doesn't match, or matches but defines none, is mis-counted in opposite directions. The enumeration should report both the pattern set **and** the collected set, and reconcile — rather than trusting the pattern alone.

## Adversarial Review

*T3 on approval. Default to non-APPROVE.* Attack first:
1. **Can the R-A guard be satisfied while files stay hidden?** Find the loophole — that is the whole plan.
2. **Is test 2 strong enough** to stop the guard decaying into a no-op?
3. **Does AC4 (count increases) create pressure to re-enable trivial files** and leave hard ones excluded?
4. **Is OQ1 handled, or does the plan trust a filename pattern to define the universe it audits?**
