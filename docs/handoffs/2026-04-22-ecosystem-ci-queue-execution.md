# Handoff — Ecosystem CI queue execution (session 7)

## Quick prompt for next session

```
Resume ecosystem CI queue execution from
docs/handoffs/2026-04-22-ecosystem-ci-queue-execution.md

#2442 is status:plan-approved (user approved 2026-04-22).
Plan: docs/plans/2026-04-21-issue-2442-assethold-python-tests.md (SHA b8ba1c0f8)

EXECUTE #2442 — assethold CI repair, direct-to-main:

Phase 1 — YAML parse + deprecated actions (7 sites):
  Target: assethold/.github/workflows/python-tests.yml
  1. Quote DATABASE_URL at lines 122, 138:
     sqlite:///:memory:  →  "sqlite:///:memory:"
  2. Bump actions/upload-artifact@v3 → @v4 at lines 153, 166, 345
  3. Bump github/codeql-action/upload-sarif@v2 → @v3 at line 339
  4. Bump codecov/codecov-action@v3 → @v4 at line 144
  Commit P1, push to assethold main, wait for CI.
  Verify: jobs[] != [] (startup unblocked, no more 0s/0-jobs).

Phase 2 — install-step + sibling dep (6 sites):
  Same file: assethold/.github/workflows/python-tests.yml
  5. Replace `uv pip install --system -r requirements.txt` with
     `uv pip install --system -e ../assetutilities` at lines 74, 222, 269
  6. Insert after main checkout in each of 3 dep-installing jobs
     (test, integration-tests, financial-data-tests):
       - name: Clone assetutilities sibling dependency
         run: git clone --depth 1 https://github.com/vamseeachanta/assetutilities.git ../assetutilities
  Existing `uv pip install --system -e .` at lines 79, 224, 271 stays unchanged.
  Commit P2, push to assethold main, wait for CI.
  Verify: py3.11/ubuntu-latest smoke cell green (issue-close criterion).

Phase 3 is FOLLOW-ON — do NOT attempt in this session.

After P2 verified:
  - Post CI green evidence on #2442, close issue
  - Comment on parent #2424 with assethold status update

Then proceed to remaining queue:

  EXECUTE #2433 (worldenergydata) — status:plan-approved
    Plan: docs/plans/2026-04-21-issue-2433-worldenergydata-ci.md
    Read the plan, execute per its instructions, verify CI, close issue.

  EXECUTE #2437 (workspace-hub prune) — status:plan-approved
    Plan: docs/plans/2026-04-21-issue-2437-workspace-hub-prune.md
    Read the plan, execute per its instructions, verify, close issue.

  REVISE #2441 (digitalmodel pylife) — status:plan-review, Wave 2 MAJOR
    Plan: docs/plans/2026-04-21-issue-2441-digitalmodel-pylife.md
    Read Wave 2 reviews: scripts/review/results/2026-04-21-plan-2441-{claude,codex,gemini}-r2.md
    Fix MAJOR findings, commit v3, run Wave 3 cross-review.
    If no MAJOR: post summary, label status:plan-review, wait for user.

  REVISE #2443 (achantas-data) — status:plan-review, Wave 2 MAJOR
    Plan: docs/plans/2026-04-21-issue-2443-achantas-data-ci.md
    Read Wave 2 reviews: scripts/review/results/2026-04-21-plan-2443-{claude,codex,gemini}-r2.md
    Fix MAJOR findings, commit v3, run Wave 3 cross-review.

  REVISE #2444 (aceengineer-admin) — status:plan-review, Wave 2 MAJOR
    Plan: docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md
    Read Wave 2 reviews: scripts/review/results/2026-04-21-plan-2444-{claude,codex,gemini}-r2.md
    Fix MAJOR findings, commit v3, run Wave 3 cross-review.

Cross-cutting rules:
- Do NOT self-approve any plan. User must set status:plan-approved.
- Do NOT clone assethold from stale samdansk2 fork — use vamseeachanta/assethold.
- Do NOT restore scripts/agents/ or scripts/work-queue/ trees.
- Do NOT attempt P3 for #2442 (follow-on scope).
- Separate commits per phase, push sequentially, verify CI between.
- If context exhaustion: write resume handoff to docs/handoffs/.
```

## Issue status summary

| Issue | Repo | Priority | Status | Next action |
|-------|------|----------|--------|-------------|
| #2442 | assethold | HIGH | plan-approved | **Execute P1+P2** |
| #2433 | worldenergydata | Medium | plan-approved | Execute |
| #2437 | workspace-hub | Medium | plan-approved | Execute |
| #2441 | digitalmodel | Medium | plan-review (W2 MAJOR) | Revise v3 |
| #2443 | achantas-data | Low | plan-review (W2 MAJOR) | Revise v3 |
| #2444 | aceengineer-admin | Low | plan-review (W2 MAJOR) | Revise v3 |

## #2442 review wave history (6 waves)

| Wave | Claude | Codex | Gemini | Key fix |
|------|--------|-------|--------|---------|
| 1 | MAJOR | MAJOR | MAJOR | assetutilities sibling dep, codecov, YAML proof |
| 2 | MAJOR | MAJOR | APPROVE | stale uv-sync wording, preconditions verified |
| 3 | MAJOR | MAJOR | APPROVE | execution-strategy contradiction |
| 4 | MAJOR | MAJOR | APPROVE | checkout path blocker (actions/checkout rejects ../) |
| 5 | APPROVE | MAJOR | MAJOR | #2442 closed by mistake + acceptance criteria text |
| 6 | APPROVE | MAJOR | APPROVE | bare python → uv run; Codex sustained-MAJOR (false positive) |

## Key commits this session (session 6+7)

| SHA | Description |
|-----|-------------|
| 6d5afa64e | plan v6 — fix acceptance criteria text + reopen closed issue |
| b8ba1c0f8 | plan v6 amend — bare python → uv run python per repo policy |

## Assethold workflow line map (for executor reference)

```
python-tests.yml key lines:
  122: DATABASE_URL: sqlite:///:memory:        ← P1: quote
  138: DATABASE_URL: sqlite:///:memory:        ← P1: quote
  144: codecov/codecov-action@v3               ← P1: bump to @v4
  153: actions/upload-artifact@v3              ← P1: bump to @v4
  166: actions/upload-artifact@v3              ← P1: bump to @v4
  339: github/codeql-action/upload-sarif@v2    ← P1: bump to @v3
  345: actions/upload-artifact@v3              ← P1: bump to @v4
   74: uv pip install --system -r requirements.txt  ← P2: → -e ../assetutilities
  222: uv pip install --system -r requirements.txt  ← P2: → -e ../assetutilities
  269: uv pip install --system -r requirements.txt  ← P2: → -e ../assetutilities
   79: uv pip install --system -e .            ← P2: KEEP (installs assethold)
  224: uv pip install --system -e .            ← P2: KEEP
  271: uv pip install --system -e .            ← P2: KEEP
  Insert git clone after main checkout in: test, integration-tests, financial-data-tests jobs
```
