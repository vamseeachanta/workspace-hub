# ace-linux-2 — approval-readiness blocker prep packet

> **Generated:** 2026-04-29
> **Agent:** ace-linux-2 (overflow — control plane is ace-linux-1)
> **Authorized scope:** read live issues + local artifacts; classify blockers; emit next-lane prompts. **No GitHub mutations. No implementation.**
> **Output:** this file (one primary result artifact). No supplementary review docs requested.

---

## Repo-state staleness notes (must be acknowledged by next-lane agent)

ace-linux-2 may lag ace-linux-1 on this branch. Concrete signals seen:

1. **Workspace-hub on `main`, no behind-count check possible** (no remote refresh run). Untracked files in `docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/` and `2026-04-29-next-wave-autofeed/` look like overnight-output artifacts that haven't been committed yet — that is an in-flight working tree, not a clean checkpoint.
2. **NFS Glob timeouts** on `**/*sesa*` and `**/*woodfibre*` (20s timeout). Plan files for **#2541** (SESA) and **#2544** (Woodfibre) could not be located within budget. Live issue labels confirm both are `status:plan-approved`, so plans must exist; the next-lane agent should rediscover their paths via `gh issue view <n> --comments` or `ls docs/plans/2026-04-2*-issue-{2541,2544}-*` from ace-linux-1's filesystem before trusting any guesses below.
3. **No `.claude/state/approvals/` directory exists** on this machine. The wave-prompt mentions a "local approval marker" requirement before execution; either the convention lives elsewhere (likely on ace-linux-1 only) or it was never set up. **Do not assume a marker exists** — check ace-1 first, and if no convention is found, escalate to the user before any plan-approved issue is executed.
4. The prior wave's dossier (`docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/ace2-next5-plan-prep.md`) is a load-bearing dependency for this packet's framing; any divergence between that dossier and current live labels means **live labels win** (already verified for all 7 here).

---

## Blocker classification (taxonomy)

| Category | Definition | Issues |
|---|---|---|
| **A — Execution-readiness** | Live label is `status:plan-approved`. The blocker is *not* approval; it's verifying environment, dependencies, and the local-approval-marker convention before dispatch. | #2490, #2510, #2541, #2544 |
| **B — Review fanout missing** | Plan drafted, but the claude/codex/gemini review trio has not been run, so the plan is not eligible for `status:plan-review`. | #2474 |
| **C — Review triage** | Plan drafted, full r0 review trio exists on disk, but findings have not been triaged or applied. | #2378 |
| **D — Plan-draft missing** | No plan file on disk; cannot move toward `status:plan-review` until one is drafted. | #2370 |

Net actions if all four lanes complete: 4 issues advance from approved → executed, 1 from drafted → reviewed, 1 from reviewed → revised, 1 from issue body → drafted.

---

## Per-issue blocker prep packets

> Each entry contains: live state, classification, files to inspect, acceptance criteria, and one self-contained next-lane prompt. **Prompts are read-only / planning-only unless explicitly noted.**

---

### #2490 — digitalmodel Quality Gates coverage-gate blocker

**Live state (verified 2026-04-29T10:02Z):** OPEN · `status:plan-approved` · `priority:medium` · `cat:infrastructure` · `enhancement` · T1 plan
**Classification:** **A — Execution-readiness**
**Why this is the blocker:** Plan is approved, but the plan itself flags a discrepancy in the issue body — the issue claims `pyproject.toml [tool.pytest.ini_options].addopts` already declares `--cov=src`, but the plan verified that `addopts` does NOT contain `--cov=src` (only `--tb=short`, `--strict-markers`, `--strict-config`). That discrepancy is recorded but not reconciled. Execution must not silently paper over it.
**Files to inspect:**
- `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md` — full plan including the discrepancy callout (line ~75).
- `digitalmodel/.claude/quality-gates.yaml:10,20-22,97-100` — tests-gate command, coverage thresholds, strict_mode flag.
- `digitalmodel/src/digitalmodel/workflows/automation/quality_gates.py:285-295` — `_execute_coverage_gate` early-return on missing `coverage.json`.
- `digitalmodel/pyproject.toml` — `[tool.pytest.ini_options].addopts`, `[tool.coverage.run]`, `[tool.coverage.json]`.
**Acceptance criteria for next-lane:**
- [ ] Local approval marker located (or escalation to user if convention missing).
- [ ] Repo state on ace-linux-1 confirmed up-to-date with `main` before any digitalmodel edit.
- [ ] Discrepancy in issue body re-resolved against current `pyproject.toml`.
- [ ] Implementation choice (Option 1 vs Option 2 from issue body) recorded in a per-PR commit message, not silently picked.
- [ ] Quality Gates workflow run on the digitalmodel `main` post-merge shows tests + coverage gates green.

**Next-lane prompt (Category A · execution-readiness):**

```
You are picking up #2490 (digitalmodel Quality Gates coverage-gate blocker), live status:plan-approved.

Pre-execution checklist (do NOT touch code until all six pass):
1. Pull workspace-hub `main` and confirm no behind-count vs origin.
2. Confirm a local approval marker exists for #2490; if `.claude/state/approvals/` doesn't exist on this machine, escalate to user before proceeding.
3. Read `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md` end to end. Note the line ~75 discrepancy (issue body says `addopts` has `--cov=src`; plan verified it does not).
4. Re-verify against the live `digitalmodel/pyproject.toml` `[tool.pytest.ini_options]` block whether the discrepancy still holds today.
5. Choose Option 1 (add `--cov=src --cov-report=json:coverage.json` to the tests-gate command) OR Option 2 (downgrade coverage gate to non-strict). Record the choice in the commit body with one-sentence rationale.
6. Stage the change in a fresh PR branch with no other unrelated diffs. Do not amend prior commits.

Acceptance for the PR (must all pass before merge):
- Quality Gates workflow on the PR shows tests + coverage gates green.
- The discrepancy noted in the plan is explicitly resolved (either "still present, fixed by Option 1" or "issue body was correct, plan was stale").
- No additional gate behavior is silently changed.

Out of scope: refactoring the gate framework, touching other gates, modifying any non-yaml/pyproject file outside the minimum surface required.
```

---

### #2510 — Python layout/CAD automation demo (chip/package geometries)

**Live state (verified 2026-04-29T09:59Z):** OPEN · `status:plan-approved` · `priority:medium` · `cat:engineering` + `cat:tooling` · `domain:semiconductor` + `domain:chip-design` · T2 plan
**Classification:** **A — Execution-readiness**
**Why this is the blocker:** Plan went through 13 review rounds (r1-r13) before approval — convergence was hard-won. The plan headers explicitly pin `gdsfactory==9.40.2`, require KLayout to be invoked **subprocess-only** (license guardrail — KLayout is GPL-3, gdsfactory is MIT), and forbid claims of JEDEC/IPC compliance. Execution can regress any of these silently if the operator skips the plan header.
**Files to inspect:**
- `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` — full plan (header has 13 archived review rounds; r13 patches are the canonical state).
- `scripts/review/results/2026-04-27-plan-2510-{claude,codex,gemini}-r13.md` — the latest review round; confirms what r13 patched.
- `scripts/semiconductor/package_fem_benchmark.py` — established lane convention (scripts/, tests/, data/ layout).
- `tests/semiconductor/test_package_fem_benchmark.py` — pattern reference for SHA256 manifests, CLI tests, deterministic artifact contracts.
**Acceptance criteria for next-lane:**
- [ ] gdsfactory 9.40.2 install verified before any code lands; KLayout invocation is subprocess-only.
- [ ] No PDK-licensed cell or library is bundled.
- [ ] Generated `.gds` artifact (not a stub) lands under `data/semiconductor/layout_cad_demo/` with SHA256 manifest.
- [ ] Demo report frames output as "open-tool layout demo," explicitly *not* tape-out signoff.
- [ ] Tests assert deterministic regeneration (snapshot or hash check).

**Next-lane prompt (Category A · execution-readiness, license-sensitive):**

```
You are picking up #2510 (Python layout/CAD demo), live status:plan-approved after 13 review rounds.

Pre-execution checklist:
1. Read the plan header in full — `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md`. The 13-round review history is part of the contract; do not re-litigate.
2. Confirm local approval marker for #2510. If absent, escalate.
3. Read `scripts/review/results/2026-04-27-plan-2510-{claude,codex,gemini}-r13.md` to understand which patches converged the plan; respect those constraints.
4. Verify the local Python env can install `gdsfactory==9.40.2` cleanly. If a higher version is required for your platform, surface it as a deviation, do not silently bump.
5. KLayout, if used, MUST be invoked via subprocess with no Python-binding linkage (license guardrail — GPL-3 binding into MIT-licensed code is the failure mode). Document the invocation pattern in code comments.

Implementation guardrails (any violation = stop and escalate):
- No PDK-licensed cells or libraries bundled or fetched at runtime.
- No claims of JEDEC/IPC/tape-out compliance in the report or commit messages.
- Generated `.gds` artifact must be a real layout, not a JSON-only or placeholder file.
- All artifacts under `data/semiconductor/layout_cad_demo/` with a SHA256 manifest matching the #2511 lane convention.

Acceptance:
- Plan-conformant artifact + report + tests committed in a single PR.
- CI run shows tests passing including deterministic snapshot/hash check.
- Report frames output as "open-tool layout demo," not signoff.
```

---

### #2474 — OrcaFlex native reverse-parser equivalence proof

**Live state (verified 2026-04-26T21:54Z):** OPEN · `priority:high` · `cat:engineering` · `domain:marine` · **`machine:dev-primary`** · T3 plan · NOT plan-approved
**Classification:** **B — Review fanout missing**
**Why this is the blocker:** Plan is drafted (T3 — large surface, ~80 lines of resource intel and gap analysis already written), but the plan header marks review artifacts as `(TBD)`. T3 plans require the full claude/codex/gemini review trio before `status:plan-review` is justified. Without the trio, the plan cannot move to approval. Issue carries `machine:dev-primary` so this is **ace-linux-1's lane** — ace-linux-2 should not run the review fanout itself.
**Files to inspect:**
- `docs/plans/2026-04-26-issue-2474-orcaflex-reverse-parser.md` — drafted plan (read header for review-artifact slots).
- `scripts/review/plan-review-fanout.sh` — the trio fanout script.
- `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py:387` — `OrcaWaveInputParser` baseline pattern that #2474 mirrors.
- `digitalmodel/src/digitalmodel/solvers/orcaflex/format_converter/single_to_spec.py` — existing best-effort converter that #2474 must extend (not replace).
- `docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md` — handoff line 136-139, the issue's source.
**Acceptance criteria for next-lane:**
- [ ] Review fanout script run; outputs at `scripts/review/results/${TODAY}-plan-2474-{claude,codex,gemini}.md`.
- [ ] All three reviews archived to `-r1.md` suffix per repo convention.
- [ ] Plan header updated with the three filenames.
- [ ] MAJOR findings (if any) patched into the plan; MINOR findings catalogued in a triage doc.
- [ ] Plan re-saved with `Status: plan-review` once trio is clean.

**Next-lane prompt (Category B · review fanout, ace-linux-1 only):**

```
You are picking up #2474 (OrcaFlex reverse-parser equivalence proof) on ace-linux-1 — the issue carries machine:dev-primary so do NOT delegate to ace-linux-2.

Step 1 — Sanity check before fanout:
- Read `docs/plans/2026-04-26-issue-2474-orcaflex-reverse-parser.md` end to end.
- Confirm the plan header still reads `Review artifacts: ... (TBD)`. If reviews already exist, skip to step 3.
- Verify the four EXISTS-marked source files (lines 65-72 of the plan) still exist at the cited line numbers. If they've moved, surface as a stale-plan signal before fanout.

Step 2 — Run the trio fanout:
- `scripts/review/plan-review-fanout.sh 2474`
- Outputs land at `scripts/review/results/${TODAY}-plan-2474-{claude,codex,gemini}.md`.
- Immediately archive each to `-r1.md` suffix to lock the round before any rerun.
- Update the plan header to point at the three archived filenames.

Step 3 — Triage:
- For MAJOR findings: patch the plan in place and note "patched per <reviewer>-r1" in the commit body.
- For MINOR/NIT: catalogue in `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/2474-review-triage.md`, defer to execution.

Step 4 — Status:
- If the trio is clean (no unpatched MAJORs), save the plan as `Status: plan-review`. Do NOT apply any GitHub label — user approval is still required for status:plan-approved.

Out of scope: any code change to digitalmodel; the issue body explicitly defers binary `.sim` parsing (#1652) and full solver execution.
```

---

### #2378 — chunk and paginate canonical marine-engineering wiki index

**Live state (verified 2026-04-20T07:34Z):** OPEN · `priority:high` · `cat:documentation` · `domain:knowledge-management` · T2 plan · NOT plan-approved
**Classification:** **C — Review triage**
**Why this is the blocker:** Plan exists (`docs/plans/2026-04-26-issue-2378-marine-wiki-chunked-index.md`); per the prior wave's dossier (`results/ace2-next5-plan-prep.md` lines 65-69), the r0 review trio is on disk at `scripts/review/results/2026-04-27-plan-2378-{claude,codex,gemini}.md` but no triage has been performed. Two reviewer concerns flagged in that dossier are high-blast-radius and must not be deferred: (a) chunking-key choice (alphabetical vs semantic), (b) `next`/`prev` link fragility. Also, legal sanity per the wave-prompt: chunked layout makes vendor source titles more discoverable per #2482 deny-list — confirm chunk pages contain only titles + links, not source content.
**Files to inspect:**
- `docs/plans/2026-04-26-issue-2378-marine-wiki-chunked-index.md` — plan.
- `scripts/review/results/2026-04-27-plan-2378-claude.md` (and codex / gemini siblings) — the r0 review trio.
- `knowledge/wikis/marine-engineering/wiki/index.md` — the 21,616-line file the plan chunks.
- `.claude/rules/calc-citation-contract.md` (and `#2482` deny-list governance referenced therein) — legal sanity surface.
**Acceptance criteria for next-lane:**
- [ ] Triage table written at `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/2378-review-triage.md` with rows `{reviewer, severity, finding, accept/reject/defer, patch-location}`.
- [ ] Chunking-key decision documented in the plan with explicit rationale (not "alphabetical because easier").
- [ ] `next`/`prev` link contract tested against link-rot scenarios.
- [ ] Legal sanity verdict documented: chunk pages emit titles + URLs only, no source content body, deny-list still holds at chunk-manifest layer.
- [ ] Plan re-saved as `Status: plan-review` once MAJORs are patched.

**Next-lane prompt (Category C · review triage):**

```
You are picking up #2378 (marine-wiki chunked index) review triage. Plan is drafted; trio is on disk; no triage doc exists.

Step 1 — Read the trio in full:
- `scripts/review/results/2026-04-27-plan-2378-claude.md`
- `scripts/review/results/2026-04-27-plan-2378-codex.md`
- `scripts/review/results/2026-04-27-plan-2378-gemini.md`

Step 2 — Build the triage table at:
`docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/2378-review-triage.md`

Columns: reviewer, severity (MAJOR/MINOR/NIT), finding (one-line), accept/reject/defer, patch-location (file:line of the plan or "execution-time").

Step 3 — Pay particular attention to:
- Chunking-key choice (alphabetical vs semantic vs size-bucket). Whichever the plan picks, the rationale must be explicit and resilient — "easier" is not a rationale.
- `next`/`prev` link fragility. Test scenario: source page title alias changes (#2372 lands later) — does the chunk pagination break? If yes, the plan needs a renumbering policy.
- Legal sanity per #2482: chunk pages must emit titles + URLs only, never source page body content. Confirm the plan's chunking writer enforces this.

Step 4 — Apply patches:
- Patch MAJOR findings into the plan in place.
- Defer MINOR/NIT to execution-time TODOs.
- Save the plan as `Status: plan-review`.
- Do NOT apply any GitHub label.

Out of scope: actually running the chunker against marine-engineering/wiki/index.md; that's execution-phase work.
```

---

### #2370 — closed-issue promotion ledger for engineering wiki ingest

**Live state (verified 2026-04-20T07:05Z):** OPEN · `priority:high` · `cat:data-pipeline` · `domain:knowledge-management` · NOT plan-approved · **no plan file on disk**
**Classification:** **D — Plan-draft missing**
**Why this is the blocker:** Per the prior wave's dossier (`ace2-next5-plan-prep.md` line 14), #2370 was excluded from the credit-burn slate explicitly because "no plan file on disk; would require plan-draft from scratch (higher ambiguity than goal allows for this credit-burn)." That ambiguity hasn't been resolved. Until a plan exists, the issue cannot move toward `status:plan-review`. Two upstream artifacts referenced in the issue body (`docs/reports/engineering-wiki-skill-ingest-readiness-2039-2042.md`, `knowledge/wikis/engineering/SOURCE_INVENTORY.md`) are the resource-intel starting points the plan needs.
**Files to inspect:**
- `docs/reports/engineering-wiki-skill-ingest-readiness-2039-2042.md` — reports 74 unpromoted closed `cat:engineering` issues + 13 unpromoted `cat:engineering-calculations`.
- `knowledge/wikis/engineering/SOURCE_INVENTORY.md` — current ingest status.
- Issue siblings #2236 (post-closure promotion workflow), #2238 (closed-issue citation guardrail), #2042 (skill/issue ingest), #2366 (strengthening scorecard) — all referenced by the issue body and likely candidate dependencies.
- `docs/plans/_template-issue-plan.md` — required template per `CLAUDE.md` planning workflow.
**Acceptance criteria for next-lane:**
- [ ] Plan file created at `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md`.
- [ ] Resource intel section cites the two upstream artifacts above with line refs and verified counts.
- [ ] Scoring rubric defined (reusable methodology, stable decision value, evidence richness, overlap risk) — these are listed in the issue body but need operational definitions.
- [ ] Extend-vs-create map shape declared as a YAML or table schema, not prose.
- [ ] Plan declares this a planning-only deliverable (the ledger itself is the artifact, no code beyond a triage script).
- [ ] Plan saved as `Status: draft` (not plan-review yet — review trio comes after).

**Next-lane prompt (Category D · plan draft from scratch):**

```
You are picking up #2370 (closed-issue promotion ledger). No plan file exists on disk — your job is to author the first draft.

Step 1 — Resource intel:
- `gh issue view 2370 --json body,labels` — confirm body and labels match what is summarized below.
- `docs/reports/engineering-wiki-skill-ingest-readiness-2039-2042.md` — extract the actual current counts of unpromoted closed `cat:engineering` and `cat:engineering-calculations` issues. Do NOT trust the issue body's "74 + 13" figures without re-running the count.
- `knowledge/wikis/engineering/SOURCE_INVENTORY.md` — extract the current promoted-vs-unpromoted ratio.
- Read `docs/plans/_template-issue-plan.md` and follow the section structure exactly.

Step 2 — Plan structure (required sections):
1. Resource Intelligence Summary (with embedded counts from step 1)
2. Standards (mark non-applicable; this is a knowledge-management issue, not a calc issue)
3. Documents consulted (issue siblings #2039, #2042, #2236, #2238, #2366)
4. Gaps identified
5. Approach: ranking rubric (operational definitions for the four scoring axes named in the issue body — reusable methodology, stable decision value, evidence richness, overlap risk)
6. Deliverables: ledger schema (YAML or markdown table — declare which); ranked shortlist format; extend-vs-create map shape
7. Acceptance criteria mirroring the issue body's checkboxes
8. Risks: scoring drift, deny-list contamination (#2482), reviewer subjectivity
9. Out of scope: actually promoting any issue; that's a downstream issue.

Step 3 — Write to:
`docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md`
Status: `draft`. Complexity: T2.

Step 4 — Do NOT run review fanout in this lane. Review fanout happens after the plan settles. Do NOT apply any GitHub label.

Out of scope: implementing the ledger script; promoting any issue; touching wiki content.
```

---

### #2541 — curated SESA LNG corpus extraction from Elements

**Live state (verified 2026-04-29T14:31Z):** OPEN · `status:plan-approved` · `priority:medium` · `cat:data-pipeline` · `domain:marine` + `domain:knowledge-management`
**Classification:** **A — Execution-readiness**
**Why this is the blocker:** Live label is `status:plan-approved`, so the plan exists and was user-approved. ace-linux-2 could not locate the plan path within budget (NFS Glob timeouts on `**/*sesa*`). The execution-readiness blockers are all environmental: (a) read access to `/mnt/ace/doris/62092_sesa` from the executing machine, (b) the `#2534` retention boundary, (c) the bound on extraction tranche size (≤20 artifacts), and (d) the raw-data policy: NO raw files copied into git/wiki.
**Files to inspect (next-lane must rediscover plan path):**
- Plan file (path unverified): expected naming `docs/plans/2026-04-2*-issue-2541-elements-sesa-curated-extraction-plan.md`. Confirm via `gh issue view 2541 --comments` (the plan filename is usually pasted into a status-change comment).
- `.planning/intel/elements-overnight-wave/sesa-candidate-dossier.md` — candidate dossier from the plan's deliverables list.
- `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv` — the candidate queue.
- `/mnt/ace/doris/62092_sesa` — raw corpus (read-only access required).
- Sibling closed issues: #2535 (metadata indexing), #2536 (first-pass extraction).
**Acceptance criteria for next-lane:**
- [ ] Plan path located and confirmed before any extraction begins.
- [ ] Local approval marker for #2541 located (or escalation).
- [ ] Read access to `/mnt/ace/doris/62092_sesa` confirmed on the execution machine.
- [ ] Extraction tranche bounded to ≤20 artifacts as specified in the issue body.
- [ ] Each extracted artifact has source path, byte size, rationale, extraction method, target wiki page recorded.
- [ ] Zero raw files copied into git/wiki/raw folders.
- [ ] `#2534` retention boundary held; `/mnt/ace` content unchanged.

**Next-lane prompt (Category A · execution-readiness, ace-1 only — NFS access):**

```
You are picking up #2541 (SESA LNG curated extraction), live status:plan-approved. Run on ace-linux-1 only — ace-linux-2 cannot reliably reach `/mnt/ace/doris/62092_sesa` per current Glob timeouts.

Pre-execution checklist:
1. `gh issue view 2541 --comments` — find the plan filename pasted in the status-change comment. Also check `ls docs/plans/2026-04-2*-issue-2541-*` and `ls docs/plans/2026-04-2*-elements-sesa-*`.
2. Read the plan in full.
3. Confirm local approval marker for #2541. If absent, escalate.
4. `ls /mnt/ace/doris/62092_sesa` — confirm read access from the execution machine. If permission-denied, escalate before any extraction code runs.
5. Read `.planning/intel/elements-overnight-wave/sesa-candidate-dossier.md` and `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv` to ground the tranche selection in what was approved.

Hard guardrails (any violation = stop):
- Tranche bounded to ≤20 artifacts. Do not silently expand.
- Zero raw files copied into git/wiki/raw folders. Extracted *content* may be summarized into wiki pages; raw binaries stay on `/mnt/ace`.
- `#2534` retention boundary held. `/mnt/ace/doris/62092_sesa` is read-only — confirm by mounting check before any write attempt.
- No additional ACMA/client confidentiality content is extracted unless the plan explicitly approved that file.

Acceptance:
- Each extracted artifact lands at its planned wiki target page with provenance recorded.
- Tranche manifest committed under `.planning/intel/elements-overnight-wave/sesa-extracted-tranche-r1.md`.
- Issue body acceptance checklist re-verified before close.
```

---

### #2544 — scout Woodfibre LNG corpus for bounded extraction candidates

**Live state (verified 2026-04-29T14:30Z):** OPEN · `status:plan-approved` · `priority:medium` · `cat:data-pipeline` · `domain:marine` + `domain:knowledge-management`
**Classification:** **A — Execution-readiness**
**Why this is the blocker:** Live label is `status:plan-approved`. Same NFS-Glob-timeout caveat as #2541 — plan path unverified from ace-linux-2. The execution-readiness blockers are sharper than #2541 because Woodfibre is **5,364 files / ~1.879 TB** and the issue explicitly forbids broad text extraction or raw copying. The scout must work from path + metadata only, never opening or duplicating large binaries unless explicitly justified for metadata-only handling. Tranche bound is **≤15 artifacts** (smaller than SESA's 20).
**Files to inspect (next-lane must rediscover plan path):**
- Plan file (path unverified): expected naming `docs/plans/2026-04-2*-issue-2544-elements-woodfibre-scout-plan.md`. Confirm via `gh issue view 2544 --comments`.
- `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md` — scout dossier from the plan's deliverables list.
- `/mnt/ace/acma-projects/31522-woodfibre-lng` — raw corpus (read-only access required).
- Sibling closed issues: #2535, #2536.
**Acceptance criteria for next-lane:**
- [ ] Plan path located.
- [ ] Local approval marker for #2544 located (or escalation).
- [ ] Read access to `/mnt/ace/acma-projects/31522-woodfibre-lng` confirmed.
- [ ] Scout works from `find -type f -printf` style metadata, NOT from opening/extracting large binaries.
- [ ] Candidate tranche bounded to ≤15 artifacts.
- [ ] Tranche includes explicit ACMA/client confidentiality flag per artifact.
- [ ] Zero raw files copied into git/wiki/raw folders.
- [ ] `#2534` retention boundary held; corpus path unchanged.

**Next-lane prompt (Category A · execution-readiness, ace-1 only — NFS access + size-sensitivity):**

```
You are picking up #2544 (Woodfibre LNG scout), live status:plan-approved. Run on ace-linux-1 only.

Pre-execution checklist:
1. `gh issue view 2544 --comments` — find the plan filename. Also `ls docs/plans/2026-04-2*-issue-2544-*` and `ls docs/plans/2026-04-2*-elements-woodfibre-*`.
2. Read the plan in full.
3. Confirm local approval marker for #2544. If absent, escalate.
4. `ls /mnt/ace/acma-projects/31522-woodfibre-lng` — confirm read access. Run `du -sh` once to confirm the ~1.879 TB figure; do NOT recursively `ls` the entire tree.
5. Read `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md` if it exists; if not, you are likely the agent creating it.

Hard guardrails (any violation = stop):
- Scout MUST work from path + file metadata only. Never `cat` or text-extract a large binary unless the plan explicitly approved that artifact.
- Tranche bounded to ≤15 artifacts.
- Each candidate has: path, size, type, rationale, extraction method, expected wiki target, ACMA/client confidentiality flag.
- Zero raw files copied into git/wiki/raw folders.
- `/mnt/ace/acma-projects/31522-woodfibre-lng` is read-only — confirm via mount check.
- If the plan flagged "additional ACMA/client confidentiality review needed before extraction," DO NOT extract; only scout. Surface the gate to the user.

Acceptance:
- Scout dossier landed at `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md`.
- Candidate tranche table committed with all required columns.
- Confidentiality gate, if invoked, is surfaced in the issue with a comment for user decision.

Out of scope: extraction itself; that is a follow-up issue created from this scout.
```

---

## Summary table for ace-linux-1 control plane

| # | Category | Lane | Pre-flight gate | Risk if skipped |
|---|---|---|---|---|
| 2490 | A · execution | either | local approval marker; `addopts` discrepancy resolved | silent CI gate breakage |
| 2510 | A · execution | either | gdsfactory 9.40.2 install; KLayout subprocess-only | GPL-3 license contamination |
| 2474 | B · review fanout | **ace-1 only** (`machine:dev-primary`) | trio fanout script available | plan can't reach plan-review |
| 2378 | C · triage | either | r0 trio readable | high-blast-radius decisions deferred |
| 2370 | D · plan draft | either | template available | issue can't move at all |
| 2541 | A · execution | **ace-1 only** (NFS) | `/mnt/ace/doris/62092_sesa` access; plan path located | retention-boundary breach |
| 2544 | A · execution | **ace-1 only** (NFS, size) | `/mnt/ace/acma-projects/31522-woodfibre-lng` access; plan path located | confidentiality breach |

**Net effect** (if all 7 lanes complete): 4 issues advance approved → executed; 1 advances drafted → reviewed; 1 advances reviewed → revised; 1 advances issue body → drafted. Total: 7 issues unblocked, 4 ready for closure, 3 newly review-ready.

---

## Files this packet expects to be created next (not by ace-2 in this wave)

| Path | Purpose | Owner |
|---|---|---|
| `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md` | First-draft plan for #2370 | next-lane (Category D) |
| `scripts/review/results/${TODAY}-plan-2474-{claude,codex,gemini}-r1.md` | r1 review trio for #2474 | next-lane (Category B), ace-1 |
| `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/2378-review-triage.md` | Triage table for #2378 r0 trio | next-lane (Category C) |
| `.planning/intel/elements-overnight-wave/sesa-extracted-tranche-r1.md` | SESA tranche manifest post-extraction | next-lane (Category A · #2541), ace-1 |
| `.planning/intel/elements-overnight-wave/woodfibre-corpus-scout.md` (if not extant) | Woodfibre scout dossier | next-lane (Category A · #2544), ace-1 |

End of packet.
