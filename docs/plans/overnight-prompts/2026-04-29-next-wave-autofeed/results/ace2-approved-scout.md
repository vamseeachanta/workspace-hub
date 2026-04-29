# ace-linux-2 Approved-Scout — 2026-04-29 (next-wave overflow)

**Scope:** triage currently `status:plan-approved` + `state:OPEN` issues for **verify/close**, **execution-ready after marker check**, and **blocked/stale approval**. Overflow lane on ace-linux-2; ace-linux-1 is control plane.

**Authority:** scouting only. No GH mutation, no code changes performed in this run. Where mutation is needed, the recommendation is included as a Hermes/user decision packet.

**Live snapshot:** `gh issue list --label "status:plan-approved" --state open --limit 50` returned **39 issues** (up from 33 in the 2026-04-29 credit-burn wave). Authentication: gh works on this machine — no auth limitation. Snapshot taken 2026-04-29 ≈18:00Z.

**Local approval marker convention:** `.planning/plan-approved/<issue>.md` (109 markers present today). Most plan-approved issues do **not** carry a marker; minting requires explicit human approval per `feedback_never_offer_to_self_label_plan_approved`.

**Deduplication:** prior ace1 scouts already classified ~33 of these into A/B/C tiers in `2026-04-29-credit-burn-approval-readiness/results/ace2-approved-execution-scout.md`. This artifact focuses on (a) **delta** issues new since that scout (#2490, #2510, #2515, #2540, #2541, #2544) and (b) **state changes** worth flagging — particularly label conflicts that produce hook-gate ambiguity.

---

## Bucket 1 — Verify/close (label conflict or stale approval; resolution = relabel or close, not implement)

These three issues all carry `status:plan-approved` together with another label that contradicts execution-ready intent. Each is a candidate for a **labels-only audit pass** with a follow-up Hermes decision: keep approval and clear the conflicting label, or revoke approval and move back to `status:plan-review`/`status:blocked`.

| # | Issue | Conflicting labels | Marker | Plan file | Why this is a verify/close candidate |
|---|---|---|---|---|---|
| **V1** | [#2433](https://github.com/vamseeachanta/workspace-hub/issues/2433) chore(ci-health): worldenergydata main CI — 22+ collection errors blocking 5 Dependabot PRs | `status:blocked` **AND** `status:plan-approved` | ✅ `2433.md` | ✅ `docs/plans/2026-04-21-issue-2433-worldenergydata-ci.md` | Plan + marker were minted 2026-04-21 with explicit Path-1 scope (expand `pytest_ignore_collect`, black reformat, soften type-check). Approval is internally consistent for *that* path. The `status:blocked` label was added later — its meaning is unclear: is it blocked on dependency? On user revisit? Hermes decision: **either** clear `status:blocked` and queue execution (the plan is bounded), **or** revoke `status:plan-approved` if the blocker is intentional. Cannot remain in superposition. |
| **V2** | [#2055](https://github.com/vamseeachanta/workspace-hub/issues/2055) feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts | `status:needs-data` + `dark-intelligence` + `status:working` + `status:plan-approved` (4 conflicting state labels) | ✅ `2055.md` | ❌ **No `docs/plans/*-issue-2055-*.md`** found | Marker file at `.planning/plan-approved/2055.md` says only "Approved by user via Hermes chat 2026-04-13". No plan reference. This is a structural anomaly: a marker without a plan violates the marker-is-pointer-to-plan invariant assumed by hook gates. Plus `needs-data` + `dark-intelligence` + Hermes-context flag indicate this should be in the SubseaIQ legal-sanity holding pattern, not approved-for-execution. Hermes decision: **revoke marker** (return to plan drafting) or **point marker at the actual plan if it exists outside `docs/plans/`**. |
| **V3** | [#2402](https://github.com/vamseeachanta/workspace-hub/issues/2402) feat(doc-intel): build embeddings index L2+L3 + query CLI | `status:working` + `status:plan-approved` (and prior governance-drift incident on this issue) | ✅ `2402.md` | ✅ `docs/plans/2026-04-20-issue-2402-embeddings-build-index.md` | Per `.planning/handoffs/2026-04-20-doc-intel-session-2-handoff.md`, `status:plan-approved` was once removed from #2402 for premature approval, then re-applied. Depends on #2403 measurement spike. Verify with user that current approval is intentional and depends-on chain is satisfied; if #2403 has not been measured, this label is stale and should be downgraded until the measurement gate clears. |

---

## Bucket 2 — Execution-ready after marker check (plan exists, marker missing — Hermes/user must mint)

Plan files exist, hook gates need markers, and scope is bounded. Listed in **lowest-risk-first** order so the user can pick the smallest commit if budget is tight.

| # | Issue | Plan file | Marker | Risk class | Notes |
|---|---|---|---|---|---|
| **E1** | [#2046](https://github.com/vamseeachanta/workspace-hub/issues/2046) Audit compliance of strict issue planning workflow | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | ❌ | **Lowest** — read-only audit emitting a report artifact | Audit-style: enumerates GH issues against template/workflow checklists. No code mutation. Output goes to `scripts/review/results/`. Already C3 in ace1 scout. |
| **E2** | [#2070](https://github.com/vamseeachanta/workspace-hub/issues/2070) Guard Claude state sync against oversized session-signal files | `docs/plans/2026-04-16-issue-2070-state-size-guard.md` | ❌ | **Low** — single pre-commit hook addition, T1 complexity | One hook + a check script. Bounded scope. Already C2 in ace1 scout. |
| **E3** | [#2490](https://github.com/vamseeachanta/workspace-hub/issues/2490) chore(ci-health): digitalmodel Quality Gates coverage gate blocker | `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md` | ❌ | **Low/Med** — touches digitalmodel CI workflow + coverage threshold config | **Newest** plan in this bucket (drafted 2026-04-27). Split from parent #2441 which already shipped. Single repo target. No conflicting labels. |

> The remaining no-marker-yet issues from the credit-burn scout's Tier C (#2364 Batch Pack 1, #2368 faceted portal, #2369 Batch Pack 2, #2515 cable umbilical, #2510 CAD demo, #2017 Email-as-Queue) are still queued there and have not been re-evaluated tonight — they retain the citation/legal-sanity caveats called out in that artifact.

---

## Bucket 3 — Blocked/stale approval (approval label does not reflect current state; do **not** queue tonight)

| # | Issue | Why blocked/stale |
|---|---|---|
| **B1** | [#2152](https://github.com/vamseeachanta/workspace-hub/issues/2152) test(reporting): golden fixture corpus for weekly review run artifacts | Has `status:blocked` together with `status:plan-approved`. Same conflict shape as V1 #2433 but with no urgency (not on a CI critical path) — recommend resolving in the same triage pass that handles V1. |
| **B2** | [#2227](https://github.com/vamseeachanta/workspace-hub/issues/2227) feat(acma-codes): OCIMF Tandem Mooring + CSA Z276 wiki promotion | Has `status:needs-data` together with `status:plan-approved` — the OCIMF/CSA source acquisition has not landed (per ace1 scout). The plan file exists (`docs/plans/2026-04-12-issue-2227-…`) but cannot execute until the standards are licensed/acquired. **Recommend:** revert to `status:needs-data`-only or move to `status:plan-review` until source acquisition is confirmed. |

> Also stale per ace1 credit-burn scout (not re-listed in detail to avoid duplication): #2125, #2126, #2124 (Orcina vendor-derivative deny-list — #2482), #1962/#1782 (Tier-1 epics with no plan files), #1583/#2327/#2373 (no plan files), #2229 (machine:licensed-win-1 only).

---

## Cross-cutting findings worth surfacing tonight

1. **Label-conflict pattern is repeating** — three issues (#2433, #2152, #2227) carry simultaneous `status:plan-approved` + a blocking-state label (`status:blocked` or `status:needs-data`). The label vocabulary admits this contradiction silently. Existing issue [#2129](https://github.com/vamseeachanta/workspace-hub/issues/2129) (drift audit, Tier A in prior scout) is the natural place to emit a check rule for "plan-approved AND blocking-state" combos. Recommend adding that rule to its execution prompt when #2129 launches.
2. **Marker-without-plan inversion** (#2055) — the marker convention assumed every marker pointed at a `docs/plans/` file. The check could be enforced by `scripts/enforcement/` as a fail-closed lint at pre-commit time, similar to the abs-paths and harness-file-size checks already in place per `.claude/rules/patterns.md`.
3. **Newly approved Elements wave (#2540, #2541, #2544)** has plan-approved label but **no plan files** in `docs/plans/`. This is **expected** — the *deliverable* of these issues IS a plan (per #2541's body: "Draft an approval-ready plan for a later bounded extraction implementation"). Hook gates should treat planning-output issues differently from implementation issues; the current marker-required-for-implementation rule does not apply because no implementation is being committed. Recommend documenting "plan-output issue" semantics in `.claude/rules/` so future scouts don't mis-classify.

---

## Top 3 safe lanes — exact next prompt text

These are dispatch-ready prompts for the **next** Claude Code run on either machine. All three are non-mutating-by-default (write artifacts, no GH label change, no code commit) and respect the global rules of this wave.

### Safe Lane 1 — Label-conflict triage report (verify/close bucket; ace1 or ace2)

Single-pass audit of the three label-conflict issues. Output is a Hermes decision packet, no GH mutation.

```
Workspace: /mnt/local-analysis/workspace-hub. Read-only on GH; do not change labels or comment.

Task: produce a label-conflict resolution packet for issues #2433, #2055, #2152, #2227, #2402.

Steps:
1. For each issue, run: gh issue view <N> --json number,title,state,labels,body,comments,updatedAt and capture into the artifact.
2. Identify the specific conflicting label pair (e.g. status:plan-approved + status:blocked).
3. Read the plan file under docs/plans/ if present, AND the local marker .planning/plan-approved/<N>.md if present.
4. For each issue, write one of three recommendations and justify in <=4 lines:
   - KEEP-APPROVAL-CLEAR-CONFLICT (the conflicting label is stale; remove it)
   - REVOKE-APPROVAL-RESTORE-PRIOR-STATE (the approval is stale; demote to plan-review or blocked)
   - HOLD-FOR-USER (genuine ambiguity needing human judgment)
5. For #2055 specifically, surface the marker-without-plan inversion as a separate finding and propose either pointing the marker at an existing plan or revoking it.

Deliverable: write exactly one artifact at docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/label-conflict-triage.md. Do not modify any other file. Do not run gh issue edit. Cite each gh API call's timestamp so Hermes can re-run with confidence the data is fresh.

Forbidden: do not apply or remove labels, do not close issues, do not commit, do not mint or remove approval markers.
```

### Safe Lane 2 — #2046 planning compliance audit dry-run (execution-ready bucket; ace1 or ace2; produces report only)

This is the **safest** of the three execution-ready candidates because the deliverable is a read-only audit artifact. Hermes can review it before deciding to mint a marker and re-launch for the implementation pass (if any).

```
Workspace: /mnt/local-analysis/workspace-hub.

Task: dry-run the audit specified in docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md against the current GH issue corpus, producing the audit artifact ONLY. Do NOT commit any source-code or workflow changes; do NOT mint a local approval marker.

Constraint: this is a planning/review/synthesis run, not an implementation run. The plan describes an audit script under scripts/review/ — for this dry-run, execute the analysis logic inline without committing the script. If the analysis logic is non-trivial (>200 lines), stop after writing a scaffold and request explicit re-launch with marker minted.

Steps:
1. Read the plan in full and extract its checklist of strict-issue-planning-workflow conformance signals (e.g. plan file present, status:plan-review used before plan-approved, plan-approved marker minted, adversarial review captured under scripts/review/results/, etc.).
2. For each open issue with status:plan-approved (gh issue list --label status:plan-approved --state open --limit 100 --json number,title,labels,createdAt), evaluate the checklist. Cap at 50 issues to bound runtime.
3. Emit a per-issue scorecard: PASS / PARTIAL / FAIL with the specific failing checklist items.
4. Surface aggregate metrics: how many plan-approved issues are missing local markers, how many lack plan files, how many skipped plan-review, etc.

Deliverable: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/2046-audit-dryrun.md.

Forbidden: any GH mutation, any code commit, any marker mint. If the plan demands implementation, stop and emit a Hermes decision packet instead.
```

### Safe Lane 3 — #2541 SESA LNG corpus dossier (Bucket 3-adjacent / planning-output deliverable; ace1 preferred; ace2 acceptable for I/O-bound triage)

#2541 is *already* `status:plan-approved`, **and** its declared deliverable is a planning artifact (dossier + draft plan), not implementation code. Therefore the wave's "implementation forbidden without marker" rule does **not** restrict this lane — its output IS the plan. Recommend ace-linux-1 because it has fast access to the LLM-wiki indexes already built by prior waves, but ace-linux-2 can do the file triage if dev-secondary is reachable.

```
Workspace: /mnt/local-analysis/workspace-hub. Issue: #2541 (status:plan-approved).

Task: deliver the two artifacts named in #2541's acceptance criteria — a SESA candidate dossier and an approval-ready bounded-extraction plan. This is a planning-output run, not an implementation run; no extraction is performed against /mnt/ace contents.

Inputs of record:
- Raw corpus: /mnt/ace/doris/62092_sesa  (read-only; do not copy files into git)
- Existing metadata page from #2535: bucket-level Elements source/catalog page in knowledge/wikis/lng-projects/
- Candidate queue: .planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv

Steps:
1. Enumerate the SESA corpus by directory and file family (path, byte size, modified-date) using a single ls/find pass — write the raw inventory to .planning/intel/elements-overnight-wave/sesa-raw-inventory.tsv. If /mnt/ace is not mounted on this machine, stop and emit a "needs-mount" handoff artifact instead.
2. Group artifacts by engineering theme: reference studies, free-span/metocean, material specs/datasheets, subsea valves/TBE, logistics/project deliverables, plus any other dominant theme that surfaces.
3. Deduplicate obvious revision/path repeats by metadata only (do not open files).
4. Select a first extraction tranche of <=20 source artifacts. For each: source path, byte size, rationale, proposed extraction method (text / OCR / structured-table), target wiki page(s).
5. Emit:
   - .planning/intel/elements-overnight-wave/sesa-candidate-dossier.md
   - docs/plans/2026-04-29-issue-2541-elements-sesa-curated-extraction-plan.md (approval-ready plan; status:plan-review on first commit, NOT plan-approved)
6. After writing artifacts, post a comment summary on issue #2541 with `gh issue comment 2541 --body-file <summary.md>` referencing both deliverable paths. Comment OK; label change forbidden.

Forbidden: copying files from /mnt/ace into git or wiki raw folders, running text extraction, modifying /mnt/ace contents, applying status:plan-approved to the new plan (user must approve), citing wiki sources/ pages (use standards/ or concepts/ per .claude/rules/calc-citation-contract.md).

Output budget: 1 dossier + 1 plan + 1 comment. Cap dossier at 200 lines; cap plan at 150 lines.
```

---

## Closing notes

- **No GH mutation** was performed in this scout run. All findings are advisory.
- **No code or label changes** were made.
- **Authentication was available** — no auth limitation encountered. Live data is fresh as of 2026-04-29 ≈18:00Z.
- The three safe-lane prompts above are intentionally non-mutating-or-minimally-mutating; if Hermes wants to escalate any of them to full execution (marker mint + commit), that requires a separate prompt with explicit user approval per the wave's global rules.
- See sibling artifact `ace2-approved-execution-scout.md` (2026-04-29 credit-burn wave) for the broader Tier-A/B/C ranking that this scout deliberately does not duplicate.
