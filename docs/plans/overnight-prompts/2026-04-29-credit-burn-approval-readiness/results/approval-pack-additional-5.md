# Approval-Readiness Pack — 5 additional candidates beyond #2540–#2544

> **Generated:** 2026-04-29 (ace-linux-1, control surface)
> **Window:** credit-burn approval-readiness mining
> **Mode:** planning/review only — no GitHub mutations performed; commands below are *operator-runnable* drafts gated on user decision.
> **Authorization gate:** none of the candidates below are pre-authorized for `status:plan-approved`. Promotion to `status:plan-review` is also user-gated; no labels were touched by this lane.
> **Already covered (per prompt):** #2540, #2541, #2542 (CLOSED status:done), #2543 (CLOSED status:done), #2544.

---

## 1. Method

Inputs inspected:

- `gh issue list --label status:plan-review` (live)
- `gh issue list --label status:plan-draft` (live — empty)
- Hint set: #2370 #2375 #2378 #2363 #2538 #2474 #2509 #2490 #2510
- `docs/plans/overnight-prompts/2026-04-28-12h-continuation/{results,generated}/*` (lane artifacts feed2…feed13)
- `scripts/review/results/*2363* *2370* *2375* *2378* *2474* *2490* *2509* *2510*` (multi-provider verdicts)
- `docs/plans/2026-04-2[6-9]-issue-{candidate}-*.md` (plan drafts)
- `git log` and `git status` for each candidate plan file

Effort-to-ready scale (lower is better):

| Tier | Meaning | What blocks it |
|---|---|---|
| **A** | Already at `status:plan-review`. Effort = user decision only. | Pure user gate. |
| **B** | Plan + ≥1 MINOR review on disk; uncommitted polish; legal gate clear. | One commit + one label move. |
| **C** | Plan exists but missing 2nd-provider review OR has uncommitted draft. | One review wave (≤1 hr) + commit. |
| **D** | Plan in MAJOR state, reviewer flagged structural defects. | Plan rewrite, then re-review. |
| **E** | No plan or review fanout incomplete (UNAVAILABLE providers). | Full draft + full fanout. |

Legal-gate sanity is required for any candidate touching: standards extracts, llm-wiki, public artifacts, GTM, demo reports, PII, or third-party imagery.

---

## 2. Ranked candidate table (≥8 candidates)

| Rank | Issue | Title (truncated) | Plan revision on disk | Latest review verdict | Plan-review label? | Tier | Legal-gate | Top blocker |
|---|---|---|---|---|---|---|---|---|
| 1 | [#2510](https://github.com/vamseeachanta/workspace-hub/issues/2510) | feat(cad): build Python layout/CAD automation demo… | `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` (feed7-patched 2026-04-29) | r13 → C3 hardener → feed7 patch (all 7 findings A1–A7 resolved; binding r14 governance rule embedded) | **YES** | A | ✅ Open PDKs (Sky130/GF180MCU); no PDK redistribution; no calc-citation; semiconductor demo only | **User decision** — feed7 patch uncommitted but plan-review label already applied |
| 2 | [#2490](https://github.com/vamseeachanta/workspace-hub/issues/2490) | chore(ci-health): digitalmodel Quality Gates coverage gate | `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md` | T1 — adversarial review explicitly deferred to user gate per plan header | **YES** | A | ✅ Pure CI infra; no external data | **User decision** only |
| 3 | [#2378](https://github.com/vamseeachanta/workspace-hub/issues/2378) | feat(knowledge): chunk and paginate canonical marine wiki index | `docs/plans/2026-04-28-issue-2378-plan-draft.md` (feed6-polished 2026-04-29) | feed5 Claude **MINOR** → feed6 polish addresses all 4 MINORs (N1–N4, verified by re-read) | NO | B | ✅ Internal wiki chunking; no standards extract; sources-deny-list respected | feed6 polish UNCOMMITTED in working tree; needs commit + label |
| 4 | [#2370](https://github.com/vamseeachanta/workspace-hub/issues/2370) | feat(knowledge): closed-issue promotion ledger for engineering wiki ingest | `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md` (feed10-patched) | feed9 Claude **MINOR** → feed10 patch → feed12 single-author independent **MINOR** (Codex feed11 + Gemini feed12 BOTH could not execute due to permission gate) | NO | B/C | ✅ Doc-intel data pipeline; no public artifact | True 2nd-provider review never ran (permission gate); user must accept independent review **OR** run manual cross-review pack at `scripts/review/results/2026-04-29-plan-2370-{codex-feed11,gemini-feed12}.md` |
| 5 | [#2375](https://github.com/vamseeachanta/workspace-hub/issues/2375) | feat(knowledge): normalize WRK completions into structured seeds | `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md` (feed13 draft 2026-04-29) | none yet | NO | C | ✅ Internal seed corpus; no external data | UNCOMMITTED draft; needs review fanout (Claude+Codex+Gemini) before label |
| 6 | [#2363](https://github.com/vamseeachanta/workspace-hub/issues/2363) | feat(doc-intel): materialize wiki_refs reverse lookup | `docs/plans/2026-04-26-issue-2363-wiki-refs-reverse-lookup.md` | Claude r1 **MAJOR** (5 MAJORs: missing CLI subcommands, 1.03M→649k row-count error, doc_key/source_doc_key semantic conflation, registry.yaml scope drop, vacuous v1 ACs) | NO | D | ✅ Doc-intel only | Plan needs structural rewrite; #2360 dependency framed but ACs unhonest |
| 7 | [#2474](https://github.com/vamseeachanta/workspace-hub/issues/2474) | feat(canonical-spec): OrcaFlex native reverse-parser equivalence proof | `docs/plans/2026-04-26-issue-2474-orcaflex-reverse-parser.md` | Claude r1 **MAJOR** (3 MAJOR: pseudocode contradicts ModularModelGenerator API, schema-version pinning unverified, tautology risk in round-trip closure) | NO | D | ⚠️ Borderline — confirm no licensed Orcina OrcaFlex examples committed; plan claims Python-generated artifacts only | TDD pseudocode rewrite required; mandatory negative-test fixture (real OrcaFlex export) needed |
| 8 | [#2509](https://github.com/vamseeachanta/workspace-hub/issues/2509) | feat(eda): reproducible OpenLane/OpenROAD RTL-to-GDS demo report | `docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md` | Claude review absent from `scripts/review/results/`; Codex r0 **UNAVAILABLE** (codex-cli stdin regression #2479); Gemini r0 **UNAVAILABLE** (rc=55 trust-workspace, since-fixed) | NO | E | ✅ Open PDKs only; #2508 KB explicitly forbids JEDEC/IPC compliance claims | Full review fanout needed; legal posture documented but no signal yet |
| 9 | [#2538](https://github.com/vamseeachanta/workspace-hub/issues/2538) | ace2: lifetime property imagery timelapse for 11511 Piping Rock | none | n/a | NO | E | 🚫 **GATE BLOCKER** — real residential address (PII surface), third-party imagery (Google/USGS/Maxar) license terms unverified, output is a public-shareable artifact | No plan exists; legal review required first before any agent drafts a plan |

---

## 3. Top-5 selection — issues that can move fastest after user decision

### Selection rationale
The user's question is "what can move fastest?" — so the top-5 prioritizes Tier A and Tier B over Tier C, and excludes anything Tier D/E. #2363/#2474 (MAJOR) and #2509 (no signal) are deferred. #2538 has a hard legal-gate that must clear before any planning lane touches it.

| Rank | Issue | Tier | Exact missing steps to reach `status:plan-approved` | Legal-gate verdict |
|---|---|---|---|---|
| 1 | **#2510** | A | (1) Commit feed7 patch (`docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2510-feed7.md` already on disk; feed7 modified the plan but plan was last committed at `f8a96de2c`). (2) User reads the C3-hardener-resolved plan and either flips to `status:plan-approved` or runs r14. | ✅ CLEAR — open-PDK demo, no standards extract, no PII |
| 2 | **#2490** | A | (1) User reads plan; T1 has no adversarial review by design. (2) User flips to `status:plan-approved`. | ✅ CLEAR — internal CI |
| 3 | **#2378** | B | (1) Commit feed6 polish edits to `docs/plans/2026-04-28-issue-2378-plan-draft.md` (currently dirty in working tree per feed6 result). (2) Apply `status:plan-review` label. (3) User reviews and approves. | ✅ CLEAR — internal wiki chunking |
| 4 | **#2370** | B/C | (1) Commit feed10 patch. (2) **User decision:** accept feed12 independent MINOR as 2nd review **OR** run manual cross-review using command pack at `scripts/review/results/2026-04-29-plan-2370-codex-feed11.md` / `…-gemini-feed12.md`. (3) Apply `status:plan-review` label. (4) User approves. | ✅ CLEAR — doc-intel only |
| 5 | **#2375** | C | (1) Commit feed13 draft (`docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`). (2) Run review fanout: `scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`. (3) If MINOR-only, apply `status:plan-review` label. (4) User approves. | ✅ CLEAR — internal seed corpus |

### Common across the top-5
- None require new code; all are pure-planning gates.
- All five plans are idempotent: re-reading by user adds no risk.
- No legal review has flagged a blocker. (Caveat: #2538 *would* have been a top-5 candidate by complexity but the PII/imagery-licensing gate disqualifies it for credit-burn fast-paths.)

---

## 4. Operator command pack — gated on user decision

> **None of these run in this lane.** They are draft snippets the user can paste into a privileged terminal after deciding which path to take. Lane is forbidden from GitHub mutation.

### 4.1 #2510 — promotion to plan-approved
```bash
# Optional: commit the feed7 patch (plan file is already at the patched revision in working tree
#   per feed7 result, but feed7 lane did not commit. Verify dirty state first.)
git -C /mnt/local-analysis/workspace-hub status -s docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md

# If user approves after reading: (HERMES-CONTROL ONLY — do not run unsupervised)
# gh issue comment 2510 --body "User-approved 2026-04-29 after feed7 C3-hardener patches; r14 not required."
# gh issue edit 2510 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

### 4.2 #2490 — promotion to plan-approved
```bash
# T1, no review fanout required by plan design.
# If user approves:
# gh issue comment 2490 --body "User-approved 2026-04-29; T1 coverage-gate fix per plan."
# gh issue edit 2490 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

### 4.3 #2378 — promotion from MINOR to plan-review
```bash
# Step 1: commit feed6 polish (currently uncommitted per feed6 result, line 36 conflict-check passed)
git -C /mnt/local-analysis/workspace-hub add docs/plans/2026-04-28-issue-2378-plan-draft.md
git -C /mnt/local-analysis/workspace-hub commit -m "docs(plan-2378): apply feed6 polish addressing 4 feed5 MINORs"

# Step 2 (HERMES-CONTROL ONLY):
# gh issue edit 2378 --add-label "status:plan-review"
# gh issue comment 2378 --body "Plan polished after feed5 MINOR review; ready for user gate."
```

### 4.4 #2370 — promotion from feed12 to plan-review
```bash
# Step 1: commit feed10 patch (working tree already carries patched plan)
git -C /mnt/local-analysis/workspace-hub status -s docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md
git -C /mnt/local-analysis/workspace-hub add docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md
git -C /mnt/local-analysis/workspace-hub commit -m "docs(plan-2370): apply feed10 patch addressing feed9 MINORs"

# Step 2 (USER DECISION): accept feed12 independent review OR run cross-review.
# To run real Gemini cross-review:
GEMINI_CLI_TRUST_WORKSPACE=true gemini --skip-trust < /mnt/local-analysis/workspace-hub/scripts/review/results/2026-04-29-plan-2370-gemini-feed12.md
# (Codex command pack is at scripts/review/results/2026-04-29-plan-2370-codex-feed11.md.)

# Step 3 (HERMES-CONTROL ONLY):
# gh issue edit 2370 --add-label "status:plan-review"
# gh issue comment 2370 --body "Plan patched feed10; feed12 independent MINOR. Awaiting user gate."
```

### 4.5 #2375 — promotion from draft to plan-review
```bash
# Step 1: commit feed13 draft (currently untracked per `git status`)
git -C /mnt/local-analysis/workspace-hub add docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md \
    docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-draft-2375-feed13.md \
    docs/plans/overnight-prompts/2026-04-28-12h-continuation/generated/ace1-plan-draft-2375-feed13.md
git -C /mnt/local-analysis/workspace-hub commit -m "docs(plan-2375): feed13 draft for WRK completions normalization"

# Step 2: run cross-review fanout (verify codex-cli is on 0.123.0 NOT 0.124+)
scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md

# Step 3 (HERMES-CONTROL ONLY, only if all reviews return MINOR or below):
# gh issue edit 2375 --add-label "status:plan-review"
# gh issue comment 2375 --body "Plan drafted feed13; cross-review fanout completed. Awaiting user gate."
```

---

## 5. Notes for next mining lane (deferred candidates)

- **#2363** — re-baseline plan addressing the 5 MAJORs (especially `doc_key` vs `source_doc_key` and the missing `update`/`delete` subcommands). Estimate: ~1 day of plan work then full re-review.
- **#2474** — rewrite TDD pseudocode against actual `ModularModelGenerator.from_spec` API (init.py:73-86); add mandatory real-export negative-test fixture; resolve schema-version pinning ambiguity. Estimate: ~1 day.
- **#2509** — re-run review fanout (codex-cli 0.123 + Gemini with `GEMINI_CLI_TRUST_WORKSPACE=true`); both prior failures are now-fixed environment issues per `feedback_codex_cli_0_124_upstream_regression.md` and `feedback_gemini_trust_env_blocks_reviews.md`. Estimate: ~1 hour fanout.
- **#2538** — requires legal posture decision before plan: (a) confirm imagery license for Maxar/Google/USGS/historical aerials; (b) decide whether real address is acceptable in a public artifact or whether to genericize; (c) determine output distribution surface. Estimate: blocked on user.

---

## 6. Provenance and constraints honored

- ✅ No GitHub mutations made (no `gh issue edit`, no labels touched, no comments posted).
- ✅ No implementation launched.
- ✅ No approval markers created (`.planning/plan-approved/*` not touched).
- ✅ Single output file written: `docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/approval-pack-additional-5.md`.
- ✅ All issue numbers verified against live `gh issue view` (titles and labels read 2026-04-29 ~05:30 CDT).
- ✅ All review verdicts cited from `scripts/review/results/` artifacts on disk.
- ✅ Legal-gate column populated for every candidate per prompt rule.
