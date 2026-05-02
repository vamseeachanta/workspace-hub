# Approval Promotion Command Pack — DRAFT, USER-EXECUTED ONLY

> **Generated:** 2026-04-29 by next-wave-autofeed synthesis lane
> **Companion:** `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/approval-synthesis-10.md`
> **Authorization:** This file contains only **draft** `gh` commands and comment text. **None of these have been executed.** The synthesis lane is forbidden from `gh issue edit`, `gh issue comment`, label changes, and approval-marker writes.
> **Operator instructions:** Read each section against the synthesis table before pasting. Do not run §A blindly — §A reconciles a provenance gap and the user must first decide write-marker vs. revert-label per issue.

---

## Section A — Provenance reconciliation for already-promoted candidates

These 5 issues already carry `status:plan-approved` on GitHub, but **no `.planning/plan-approved/<n>.md` marker exists** and **no comment records the approval action**. Decide per-issue whether to (option-1) cement the existing label by writing the marker + posting bounded-scope comment, OR (option-2) revert the label to `status:plan-review`. Do NOT do both for the same issue.

### A.1 — #2540 (epic) — RECOMMEND OPTION-2 (revert)

```bash
# OPTION-2 (recommended): revert; epics should not carry status:plan-approved independently.
gh issue edit 2540 --remove-label status:plan-approved --add-label status:plan-review
gh issue comment 2540 --body-file - <<'EOF'
Reverting `status:plan-approved` → `status:plan-review`. This is an epic/coordination tracker with no implementation plan of its own; child plans #2541 and #2544 carry the executable scope. Will close as `status:done` after both children execute.

Provenance reconciliation per `feedback_attestation_enables_contradiction_detection.md`: the prior label flip happened without a `.planning/plan-approved/2540.md` marker.
EOF
```

```bash
# OPTION-1 (only if you intentionally approved the epic): write a marker (do NOT run gh comment then).
cat > .planning/plan-approved/2540.md <<'EOF'
# Approval marker — #2540 (epic)

Approved: 2026-04-29 by vamsee.achanta@aceengineer.com (manual reconciliation)
Scope: epic-only coordination; no implementation plan of its own; child issues #2541 and #2544 carry the executable scope.
Reviewer evidence: n/a (epic, not subject to plan-review).
Marker rationale: reconciles label set on GitHub without prior marker artifact.
EOF
git add .planning/plan-approved/2540.md
git commit -m "chore(planning): reconcile #2540 epic approval marker"
```

### A.2 — #2541 (SESA, bounded) — RECOMMEND OPTION-1 (cement with bounded wording)

```bash
# OPTION-1: cement the existing label by posting the bounded-scope comment + writing the marker.
gh issue comment 2541 --body-file - <<'EOF'
Approving the bounded subset described by the 2026-04-29 Adversarial Review Resolution Addendum in `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` (hardening commit `bdafe39cd`).

Scope of approval:
- Curated SESA extraction is authorized **only** after a row-level clearance record is recorded at `docs/governance/sesa-extraction-clearance-2026.md` or as a project/data owner comment on this issue covering each tranche row.
- Vendor/TBE rows remain metadata-only unless their row-level clearance explicitly allows otherwise.
- No full-text intermediate dumps may be persisted in `.planning/`, `knowledge/`, or any git-tracked path.
- LNG-projects wiki updates run sequentially with #2544.

This approval does NOT authorize: any #2534 cleanup/retention deletion, any raw bulk wiki/git ingestion, any persisted full-text dump, any OCR, any standards clause text, or any extraction beyond the clearance gate above.

Re-review consensus: Gemini APPROVE (grounded), Codex MINOR (degraded sandbox grounding — addendum-only). Synthesis at `scripts/review/results/2026-04-29-plan-2541-2544-rereview-synthesis.md`.

Provenance reconciliation: prior `status:plan-approved` label was set without a `.planning/plan-approved/2541.md` marker. Marker now written.
EOF

cat > .planning/plan-approved/2541.md <<'EOF'
# Approval marker — #2541

Approved: 2026-04-29 by vamsee.achanta@aceengineer.com
Scope: bounded SESA-curated-extraction subset per Adversarial Review Resolution Addendum at `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` L238+.
Hardening commit: `bdafe39cd`
Re-review synthesis: `scripts/review/results/2026-04-29-plan-2541-2544-rereview-synthesis.md`
Reviewer verdicts: Gemini APPROVE (grounded full read); Codex MINOR (degraded sandbox grounding — addendum-only).
HARD RUNTIME GATE (separate from approval): execution must NOT proceed until `docs/governance/sesa-extraction-clearance-2026.md` exists with row-level clearance.
Excluded from approval: any extraction beyond the clearance gate; any raw wiki/git ingestion; any full-text intermediate; any OCR; any standards clause text; any #2534 cleanup.
EOF
git add .planning/plan-approved/2541.md
git commit -m "chore(planning): reconcile #2541 approval marker with bounded scope"
```

### A.3 — #2544 (Woodfibre, scout-only) — RECOMMEND OPTION-1 (cement with scout-only wording)

```bash
gh issue comment 2544 --body-file - <<'EOF'
Approving the **pointer/scout metadata-only subset** described by the 2026-04-29 Adversarial Review Resolution Addendum in `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` (hardening commit `bdafe39cd`).

Scope of approval:
- Emit only the corpus pointer page and structured metadata pointers; no document abstract extraction, no technical summary extraction, no direct quote, no table extraction, no figure extraction.
- The post-scout extraction tranche stays blocked pending (a) a dedicated extraction plan with its own adversarial review and (b) `docs/governance/woodfibre-extraction-clearance-2026.md` with row-level clearance signed by an explicitly named ACMA project owner / client-authorized reviewer / legal-IP delegate.
- Execute sequentially after #2541 because both touch `knowledge/wikis/lng-projects/wiki/index.md` and `log.md`.

This approval does NOT authorize: any abstract/quote/table/figure extraction, any persisted full-text dump, any OCR, any modification of `/mnt/ace/acma-projects/31522-woodfibre-lng`, or any #2534 cleanup.

Re-review consensus: Gemini APPROVE (grounded), Codex APPROVE (degraded sandbox grounding — addendum-only).

Provenance reconciliation: prior `status:plan-approved` label was set without a `.planning/plan-approved/2544.md` marker. Marker now written.
EOF

cat > .planning/plan-approved/2544.md <<'EOF'
# Approval marker — #2544

Approved: 2026-04-29 by vamsee.achanta@aceengineer.com
Scope: pointer/scout metadata-only subset per Adversarial Review Resolution Addendum at `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` L322+.
Hardening commit: `bdafe39cd`
Re-review synthesis: `scripts/review/results/2026-04-29-plan-2541-2544-rereview-synthesis.md`
Reviewer verdicts: Gemini APPROVE (grounded); Codex APPROVE (degraded sandbox grounding).
HARD RUNTIME GATE: post-scout extraction stays blocked pending a separate extraction plan + `docs/governance/woodfibre-extraction-clearance-2026.md` with row-level clearance.
Sequencing: execute AFTER #2541; both touch `knowledge/wikis/lng-projects/wiki/index.md` and `log.md`.
Excluded from approval: any abstract/quote/table/figure extraction; full-text dumps; OCR; modifications of `/mnt/ace/acma-projects/31522-woodfibre-lng`; #2534 cleanup.
EOF
git add .planning/plan-approved/2544.md
git commit -m "chore(planning): reconcile #2544 approval marker with scout-only scope"
```

### A.4 — #2490 (T1 deferred-review path) — RECOMMEND OPTION-1 (cement)

```bash
gh issue comment 2490 --body-file - <<'EOF'
Approving the T1 coverage-gate fix per `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md`. T1 deferred-review path is accepted: no external adversarial review will be run, the user accepts the convention. Internal CI gate; no external surface; no legal exposure.

Provenance reconciliation: prior `status:plan-approved` label was set without a `.planning/plan-approved/2490.md` marker. Marker now written.
EOF

cat > .planning/plan-approved/2490.md <<'EOF'
# Approval marker — #2490

Approved: 2026-04-29 by vamsee.achanta@aceengineer.com (T1 deferred-review path)
Scope: digitalmodel Quality Gates coverage gate blocker fix per `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md`.
Reviewer evidence: none by design (T1 path; user-accepted convention).
Surface: internal CI only.
EOF
git add .planning/plan-approved/2490.md
git commit -m "chore(planning): reconcile #2490 approval marker (T1 deferred-review)"
```

### A.5 — #2510 (CAD demo, sustained-MAJOR loop) — RECOMMEND OPTION-2 (revert) PENDING r14

```bash
# OPTION-2 (recommended): revert until r14 fanout is fresh.
gh issue edit 2510 --remove-label status:plan-approved --add-label status:plan-review
gh issue comment 2510 --body-file - <<'EOF'
Reverting `status:plan-approved` → `status:plan-review`. The latest cross-provider review on disk is r13 (Apr-27): Codex MAJOR + Gemini MAJOR + Claude UNAVAILABLE — 13 review rounds without convergence, which matches the sustained-MAJOR-loop anti-pattern recorded in `feedback_codex_sustained_major_loop.md` and the `#2045/#2289` precedent.

The Approval Pack #2 §4.1 cited a "feed7 patch" addressing A1–A7, but feed7 was not committed and no r14 review exists on disk to confirm convergence.

Next step: commit feed7 patch (verify against working tree first), then run r14 fanout from a user terminal:

    bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md

Re-promote only if r14 returns MINOR-or-better from at least Codex + Gemini.
EOF
```

---

## Section B — Forward promotion drafts (after fanout / decision)

These 5 issues are not yet at `status:plan-approved`. Each requires user decision + (where applicable) cross-provider review fanout from a user terminal session before promotion. Pasted below in dependency order.

### B.1 — #2378 (marine wiki chunked index) — FANOUT THEN APPROVE

```bash
# Step 1: terminal-only (this lane cannot dispatch; permission-gated)
GEMINI_CLI_TRUST_WORKSPACE=true bash scripts/review/plan-review-fanout.sh \
    docs/plans/2026-04-28-issue-2378-plan-draft.md

# Step 2: only if Codex AND Gemini return MINOR-or-better
gh issue edit 2378 --add-label status:plan-review
gh issue comment 2378 --body-file - <<'EOF'
Plan polished after feed5 MINOR review; cross-provider fanout completed (see scripts/review/results/2026-04-29-plan-2378-{codex,gemini}-feed6.md). Awaiting user approval gate.
EOF

# Step 3: after user reads and approves
gh issue edit 2378 --remove-label status:plan-review --add-label status:plan-approved
gh issue comment 2378 --body-file - <<'EOF'
Approving plan per `docs/plans/2026-04-28-issue-2378-plan-draft.md`. Internal wiki chunking; standards namespace respected; sources-deny-list honored. Cross-provider review consensus: <CODEX_VERDICT> + <GEMINI_VERDICT>.
EOF
cat > .planning/plan-approved/2378.md <<'EOF'
# Approval marker — #2378
Approved: 2026-04-29 by vamsee.achanta@aceengineer.com
Scope: chunk and paginate the canonical marine-engineering wiki index.
Plan: docs/plans/2026-04-28-issue-2378-plan-draft.md
Reviewer evidence: scripts/review/results/2026-04-29-plan-2378-{codex,gemini}-feed6.md
Surface: internal wiki only.
EOF
git add .planning/plan-approved/2378.md
git commit -m "chore(planning): approve #2378 marine wiki chunked index"
```

### B.2 — #2370 (closed-issue promotion ledger) — DECISION + COMMIT + LABEL

```bash
# Step 1: commit feed10 patch (currently unstaged per feed11 evidence)
git status --porcelain docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md
git add docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md
git commit -m "docs(plan-2370): apply feed10 patch addressing feed9 MINORs"

# Step 2 — USER DECISION:
# (a) Run REAL Codex+Gemini fanout from user terminal:
GEMINI_CLI_TRUST_WORKSPACE=true bash scripts/review/plan-review-fanout.sh \
    docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md
# (b) OR accept "single-author r3 with transparent provenance" per
#     feedback_permission_gate_blocks_cross_review.md and skip to Step 3.

# Step 3: apply plan-review label (use HONEST framing — do NOT cite feed12 as Gemini)
gh issue edit 2370 --add-label status:plan-review
gh issue comment 2370 --body-file - <<'EOF'
Plan patched feed10; feed9 Claude MINOR addressed. Second-provider status: <choose one of the two below>
- "Cross-provider fanout completed; see scripts/review/results/2026-04-29-plan-2370-{codex,gemini}-r3.md"
- "Single-author r3 acceptance per `feedback_permission_gate_blocks_cross_review.md`; feed11 Codex and feed12 Gemini lanes were both blocked by the unattended-permission gate and feed12 is Claude-authored independent analysis (not a Gemini verdict)."
Awaiting user approval gate.
EOF

# Step 4: after user reads and approves (template, fill in chosen path)
gh issue edit 2370 --remove-label status:plan-review --add-label status:plan-approved
gh issue comment 2370 --body-file - <<'EOF'
Approving plan per `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md`. Doc-intel meta-tooling; no public artifact.
EOF
cat > .planning/plan-approved/2370.md <<'EOF'
# Approval marker — #2370
Approved: 2026-04-29 by vamsee.achanta@aceengineer.com
Scope: closed-issue promotion ledger for engineering wiki ingest.
Plan: docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md
Reviewer evidence: <fill in based on Step-2 path>
EOF
git add .planning/plan-approved/2370.md
git commit -m "chore(planning): approve #2370 closed-issue promotion ledger"
```

### B.3 — #2375 (WRK completions normalize) — PATCH + FANOUT + LABEL

```bash
# Step 1: patch F1 + F2 from feed14 MINOR (cross-plan compatibility) before label flip
# (User edits the plan file here per feed14 §F1/§F2 — no automated step.)

# Step 2: commit the patch
git add docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md
git commit -m "docs(plan-2375): apply F1/F2 cross-plan patches per feed14"

# Step 3: terminal-only fanout
GEMINI_CLI_TRUST_WORKSPACE=true bash scripts/review/plan-review-fanout.sh \
    docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md

# Step 4: only if MINOR-or-better
gh issue edit 2375 --add-label status:plan-review
gh issue comment 2375 --body-file - <<'EOF'
Plan F1/F2 patched per feed14; cross-provider fanout completed. Awaiting user approval gate.
EOF

# Step 5: after user approval
gh issue edit 2375 --remove-label status:plan-review --add-label status:plan-approved
cat > .planning/plan-approved/2375.md <<'EOF'
# Approval marker — #2375
Approved: 2026-04-29 by vamsee.achanta@aceengineer.com
Scope: normalize WRK completions into structured seeds and wiki-candidate corpus.
Plan: docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md
Reviewer evidence: scripts/review/results/2026-04-29-plan-2375-{codex,gemini}-feed15.md
EOF
git add .planning/plan-approved/2375.md
git commit -m "chore(planning): approve #2375 WRK completions normalize"
```

### B.4 — #2552 (external contributor runbook, T1) — DECISION + APPROVE

```bash
# Decision: T1 deferred-review (faster) OR cross-provider fanout (slower, higher confidence).

# OPTION-A — T1 deferred:
gh issue edit 2552 --remove-label status:plan-review --add-label status:plan-approved
gh issue comment 2552 --body-file - <<'EOF'
Approving T1 deferred-review path per `docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md`. Pure docs/policy; cross-references `docs/governance/TRUST-ARCHITECTURE.md`. No external surface; runbook generic about external commenter (no PII exposure).
EOF
cat > .planning/plan-approved/2552.md <<'EOF'
# Approval marker — #2552
Approved: 2026-04-29 by vamsee.achanta@aceengineer.com (T1 deferred-review path)
Scope: external contributor and unsolicited paid-help response runbook.
Plan: docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md
Surface: internal docs only.
EOF
git add .planning/plan-approved/2552.md
git commit -m "chore(planning): approve #2552 external contributor runbook (T1 deferred)"

# OPTION-B — fanout-first (drop into your terminal):
GEMINI_CLI_TRUST_WORKSPACE=true bash scripts/review/plan-review-fanout.sh \
    docs/plans/2026-04-29-issue-2552-external-contributor-runbook.md
# then proceed analogous to OPTION-A with reviewer-evidence citation.
```

### B.5 — #2550 (interaction-limit renewal scheduled task, T2) — FANOUT + APPROVE

```bash
# T2 plans are NOT eligible for T1-deferred path. Cross-provider review required.

# Step 1: terminal-only fanout
GEMINI_CLI_TRUST_WORKSPACE=true bash scripts/review/plan-review-fanout.sh \
    docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md

# Step 2: patch any MAJORs (manual, plan-by-plan).

# Step 3: only if MINOR-or-better from BOTH Codex AND Gemini
gh issue edit 2550 --remove-label status:plan-review --add-label status:plan-approved
gh issue comment 2550 --body-file - <<'EOF'
Approving T2 plan per `docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md`. Cross-provider review consensus: <CODEX_VERDICT> + <GEMINI_VERDICT>. Codifies in-production Hermes cron `d9b2d1c2270d` into the canonical `config/scheduled-tasks/schedule-tasks.yaml` registry; renewal API call already in production via Hermes — plan is the canonicalisation, not net-new exposure.
EOF
cat > .planning/plan-approved/2550.md <<'EOF'
# Approval marker — #2550
Approved: 2026-04-29 by vamsee.achanta@aceengineer.com
Scope: codify public-repo interaction-limit renewal in canonical scheduled-task registry.
Plan: docs/plans/2026-04-29-issue-2550-interaction-limit-renewal-scheduled-task.md
Reviewer evidence: scripts/review/results/2026-04-29-plan-2550-{codex,gemini}.md
Production state: Hermes cron `d9b2d1c2270d` already in production; this plan codifies the renewal task into `config/scheduled-tasks/schedule-tasks.yaml`.
EOF
git add .planning/plan-approved/2550.md
git commit -m "chore(planning): approve #2550 interaction-limit renewal scheduled task"
```

---

## Section C — Pre-flight checks before running anything in §A or §B

```bash
# 1. Verify codex-cli pinned to 0.123.0 (not 0.124+ which has the stdin regression #2479).
codex --version
# Expected: codex-cli/0.123.0
# If newer: npm install -g @openai/codex@0.123.0

# 2. Verify Gemini trust-env is set in the runtime that will dispatch.
echo "$GEMINI_CLI_TRUST_WORKSPACE"   # expected: true

# 3. Verify no parallel rebase/cleanup is mid-flight (Hermes preflight).
pgrep -af 'git (rebase|stash push|merge|reset)' || echo "no contending git ops"

# 4. Verify clean working tree before label changes.
git -C /mnt/local-analysis/workspace-hub status -sb
```

---

## Section D — What this lane intentionally did NOT do

- **No `gh issue edit` executed.** All commands above are paste-ready drafts, not run.
- **No `gh issue comment` executed.** All comment bodies are drafts.
- **No `.planning/plan-approved/<n>.md` markers written.** Drafts only.
- **No `git commit` executed.** This file plus the synthesis are the only artifacts written by this lane (and they are committed by the lane operator, not by `gh issue` flows).
- **No cross-review fanout dispatched.** Permission-gate constrained per `feedback_permission_gate_blocks_cross_review.md`; user must run from a terminal session.
- **No labels applied to #2370/#2375/#2378/#2552/#2550.** Per `feedback_never_offer_to_self_label_plan_approved.md`, no batch agent in this wave self-applies `status:plan-review` or `status:plan-approved`.

---

## Provenance

- Companion synthesis: `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/approval-synthesis-10.md`
- Source approval packs: `docs/plans/overnight-prompts/2026-04-29-credit-burn-approval-readiness/results/{approval-pack-elements-2540-2544.md, approval-pack-additional-5.md, adversarial-readiness-review.md}`
- Live state captured 2026-04-29 via `gh issue view` and `gh issue list --label status:plan-review`.
- Approval-marker file existence verified directly under `.planning/plan-approved/`.
