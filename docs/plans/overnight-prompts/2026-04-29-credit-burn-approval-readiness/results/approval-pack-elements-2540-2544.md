# Approval-Readiness Pack — Elements Wave #2540–#2544

**Date:** 2026-04-29
**Workdir:** /mnt/local-analysis/workspace-hub
**Scope:** Decide whether the user can promote each of #2540, #2541, #2542, #2543, #2544 to `status:plan-approved` *now*, or what specifically still blocks promotion.
**Authorization boundary:** This pack does NOT label, approve, or close any issue. It only prepares ready-to-paste artifacts for the user.

## TL;DR

- **#2542 and #2543 are already CLOSED `status:done`** — executed in commit `b0dac4608` against user-approval marker `05f7b6921`. No further approval needed; revisit only if the executed metadata pass needs amendment.
- **#2541 (SESA) and #2544 (Woodfibre) are plan-approval-ready right now** for explicitly bounded subsets. The hardening addenda commit `bdafe39cd` plus the cross-provider re-review consensus in `c7fc39fd3` carry the signal. Approval must be worded so it does **not** authorize extraction beyond the bounded subset, and SESA/Woodfibre extraction-tranche execution is still hard-blocked at runtime by separate clearance records that do not yet exist.
- **#2540 (umbrella) is NOT a plan-approval candidate.** It is a coordination/epic tracker with no implementation plan. Its acceptance criteria are already met; it should sit at `status:plan-review` until #2541 and #2544 execute, then close as `status:done`.

## Live state table

| Issue | Live state | Live labels (relevant) | Plan path | Latest valid review verdicts | Legal/clearance gate status | ready_now? |
|---:|---|---|---|---|---|---|
| #2540 | OPEN | priority:high, cat:data-pipeline, domain:knowledge-management, **status:plan-review** | (epic — no plan file; AC tracked in body + synthesis under `scripts/review/results/2026-04-29-plan-2541-2544-rereview-synthesis.md`) | n/a (umbrella, not subject to plan review) | n/a | **NO — not a plan-approval candidate.** Wait for #2541 + #2544 to land, then close as `status:done`. |
| #2541 | OPEN | priority:medium, cat:data-pipeline, domain:marine, domain:knowledge-management, **status:plan-review** | `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` (with `Adversarial Review Resolution Addendum (2026-04-29)` at L238+) | Pre-hardening: Codex MAJOR, Gemini MAJOR (`...plan-2541-2544-codex.md`, `...-gemini.md`). Post-hardening (`bdafe39cd`): **Gemini APPROVE — grounded full read** (`...-gemini-rereview.md` L696–700). Codex MINOR — **degraded grounding (sandbox blocked file reads, addendum-only)** (`...-codex-rereview.md` L165–177). | Required runtime clearance record `docs/governance/sesa-extraction-clearance-2026.md` **does not yet exist** (`ls docs/governance/` confirms). Per addendum this is a HARD BLOCK at execution time, not at plan-approval time. Vendor/TBE rows blocked-by-default. No persisted full-text intermediates. | **YES — plan-approval-ready for the bounded subset only.** Approval does NOT authorize SESA extraction or wiki publication; that remains gated on the missing clearance file. |
| #2542 | **CLOSED** | priority:medium, cat:documentation, domain:knowledge-management, domain:training, **status:done** | `docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md` | Pre-hardening MAJOR; post-hardening Gemini APPROVE / Codex APPROVE. Approval marker `05f7b6921`; execution `b0dac4608`. | Met: metadata-first, no OCR, no full-text dumps, `engineering-standards` namespace; raw-data guard verified empty. | **N/A — already executed.** No further approval action. |
| #2543 | **CLOSED** | priority:medium, cat:documentation, domain:standards-tooling, domain:knowledge-management, **status:done** | `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md` | Pre-hardening MINOR / MINOR; post-hardening Gemini APPROVE / Codex APPROVE. Approval marker `05f7b6921`; execution `b0dac4608`. | Met: metadata-only standards pointers, public-source frontmatter, no copyrighted content; knowledge tests 46 passed. | **N/A — already executed.** |
| #2544 | OPEN | priority:medium, cat:data-pipeline, domain:marine, domain:knowledge-management, **status:plan-review** | `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` (addendum at L322+ splits pointer/scout vs extraction) | Pre-hardening: Codex MAJOR, Gemini APPROVE. Post-hardening: **Gemini APPROVE — grounded full read** (`...-gemini-rereview.md` L703). Codex APPROVE — **degraded grounding (sandbox addendum-only)** (`...-codex-rereview.md` L180). | Required runtime clearance record `docs/governance/woodfibre-extraction-clearance-2026.md` **does not yet exist**. Per addendum, the **pointer/scout pass is the approval-ready subset**; abstract/quote/table/figure extraction is split out and remains blocked pending a separate post-scout plan + ACMA row-level clearance. | **YES — plan-approval-ready for the pointer/scout subset only.** Approval explicitly does NOT authorize document abstract extraction. |

## Cross-provider review grounding caveats

- **Gemini re-review (`scripts/review/results/2026-04-29-plan-2541-2544-gemini-rereview.md`)**: lines 1–693 are 429-retry stack traces (`No capacity available for model gemini-3.1-pro-preview`). Verdict surfaces at L696–704 from a successful retry. Counts as a fully grounded verdict — Gemini reached file content despite the capacity churn.
- **Codex re-review (`scripts/review/results/2026-04-29-plan-2541-2544-codex-rereview.md`)**: file is non-zero-byte and complete, but the runtime explicitly states `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, both via shell wrapper and via `js_repl` fallback. Codex based its verdict only on the addendum excerpts pasted into the prompt — which matches `feedback_codex_sandbox_fallback_paths.md`'s pattern: APPROVE/MINOR in degraded mode is "less risky" (false-pass risk) but should not be treated as a second independent grounding for any MAJOR-blocker decision.
- **Net signal**: one fully grounded reviewer (Gemini) approves the bounded subset for all four post-hardening plans. Codex agrees from a weaker base. The hardened plan files were authored after both providers issued first-pass MAJORs and explicitly resolve those blockers in the addenda. Approval shortlist is honest; user-in-loop gate remains the sole remaining barrier.

## Legal / source / privacy / IP sanity

| Surface | Risk | Mitigation in plan/addendum | Status |
|---|---|---|---|
| Raw client/project data into git | Hard ecosystem rule (`#2534`, raw-data guard) | All four plans persist no raw bytes; addenda forbid full-text intermediates in `.planning/`, `knowledge/`, or any git path | OK |
| SESA confidentiality | Vendor/TBE NDA, project-owner consent | Addendum L242–L262: HARD BLOCK on extraction without `docs/governance/sesa-extraction-clearance-2026.md` or owner comment; vendor/TBE metadata-only by default | OK at plan level; clearance file **must exist before any extraction** |
| Woodfibre / ACMA confidentiality | ACMA project IP, FST-1/FST-2 docs, Capricorn/Taurus subdirs | Addendum L322–L342: split approval — pointer/scout subset is metadata-only; document abstracts/quotes deferred to a separate post-scout plan; row-level clearance schema mandated; DEMOLITION/CAPRICORN/TAURUS excluded | OK at plan level; extraction tranche stays blocked pending clearance |
| Standards copyright | API/ASME/DNV/ISO licensing | #2543 addendum (already executed): metadata-only; no clauses, no figures; revision/source/date frontmatter required from public publisher | OK — already executed cleanly (b0dac4608) |
| Training material IP | Doris University internal authoring | #2542 addendum (already executed): per-artifact IP screen, authored summaries only, no slide/notes/figure copying, no OCR | OK — already executed cleanly (b0dac4608) |
| llm-wiki vendor-derivative deny-list (`.claude/rules/calc-citation-contract.md` rule 7) | `knowledge/wikis/*/wiki/sources/` cannot host standards excerpts | Addenda explicitly route standards content to `engineering-standards/wiki/standards/` per #2471 schema; `sources/*` pages remain pointer-only | OK |
| #2534 retention boundary | Source/staging deletion before 2026-05-28 | All four addenda explicitly carve cleanup out of scope | OK |

## Ready-now command/comment pack

> **User-only execution.** Per `feedback_never_offer_to_self_label_plan_approved.md`, the agent does not run any of the below; this section is a paste-ready bundle for the user when they choose to promote.

### #2541 — SESA (plan-approval, bounded)

```bash
gh issue edit 2541 --remove-label status:plan-review --add-label status:plan-approved
gh issue comment 2541 --body "$(cat <<'EOF'
Approving the bounded subset described by the 2026-04-29 Adversarial Review Resolution Addendum in `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md`.

Scope of approval:
- Curated SESA extraction is authorized **only** after a row-level clearance record is recorded at `docs/governance/sesa-extraction-clearance-2026.md` or as a project/data owner comment on this issue covering each tranche row.
- Vendor/TBE rows remain metadata-only unless their row-level clearance explicitly allows otherwise.
- No full-text intermediate dumps may be persisted in `.planning/`, `knowledge/`, or any git-tracked path.
- LNG-projects wiki updates run sequentially with #2544.

This approval does NOT authorize: any #2534 cleanup/retention deletion, any raw bulk wiki/git ingestion, any persisted full-text dump, any OCR, any standards clause text, or any extraction beyond the clearance gate above.

Re-review consensus: Gemini APPROVE (grounded), Codex MINOR (degraded sandbox grounding — addendum-only). Synthesis at `scripts/review/results/2026-04-29-plan-2541-2544-rereview-synthesis.md`.
EOF
)"
```

### #2544 — Woodfibre (plan-approval, pointer/scout subset only)

```bash
gh issue edit 2544 --remove-label status:plan-review --add-label status:plan-approved
gh issue comment 2544 --body "$(cat <<'EOF'
Approving the **pointer/scout metadata-only subset** described by the 2026-04-29 Adversarial Review Resolution Addendum in `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md`.

Scope of approval:
- Emit only the corpus pointer page and structured metadata pointers; no document abstract extraction, no technical summary extraction, no direct quote, no table extraction, no figure extraction.
- The post-scout extraction tranche stays blocked pending (a) a dedicated extraction plan with its own adversarial review and (b) `docs/governance/woodfibre-extraction-clearance-2026.md` with row-level clearance signed by an explicitly named ACMA project owner / client-authorized reviewer / legal-IP delegate.
- Execute sequentially after #2541 because both touch `knowledge/wikis/lng-projects/wiki/index.md` and `log.md`.

This approval does NOT authorize: any abstract/quote/table/figure extraction, any persisted full-text dump, any OCR, any modification of `/mnt/ace/acma-projects/31522-woodfibre-lng`, or any #2534 cleanup.

Re-review consensus: Gemini APPROVE (grounded), Codex APPROVE (degraded sandbox grounding — addendum-only). Synthesis at `scripts/review/results/2026-04-29-plan-2541-2544-rereview-synthesis.md`.
EOF
)"
```

### #2540 — Umbrella (no label change recommended now)

```bash
# No action recommended yet. Umbrella waits for #2541 and #2544 to execute.
# When both children are CLOSED status:done, then:
#   gh issue edit 2540 --remove-label status:plan-review --add-label status:done
#   gh issue close 2540 --comment "Closed after children #2541-#2544 executed; coordination scope complete."
```

### #2542 / #2543

```bash
# Already CLOSED status:done at b0dac4608. No further action.
```

## Recommended execution order after the user approves

(Per re-review synthesis, restated for completeness.)

1. **#2541** runs next — only after the SESA clearance record lands. LNG-projects wiki updates first (`elements-sesa-*` slugs).
2. **#2544** runs after #2541 lands — pointer/scout output only; uses `woodfibre-` slug prefixes and rebases on `lng-projects/wiki/index.md` + `log.md`.
3. Post-scout Woodfibre extraction is a separately planned issue, not part of this approval.

## Gaps / honest blockers

- **No new replacement review prompts drafted.** Both Codex and Gemini re-review files are non-empty and reached verdicts. Per the prompt's instruction, replacement prompts under `generated/` would only be drafted on zero-byte / 429-failure conditions; that condition is not met. The Codex re-review is degraded but present; the durable mitigation is not a replacement prompt but a sandbox-fixed Codex re-run, which is blocked by the codex-cli 0.124+ upstream regression noted in `feedback_codex_cli_0_124_upstream_regression.md` and `feedback_codex_sandbox_fallback_paths.md`. If the user wants a fully grounded Codex re-read, the next move is to wait for the codex-cli fix (or downgrade to 0.123.0) rather than re-prompt.
- **Clearance records are still pending** for SESA and Woodfibre extraction tranches. They are intentionally outside the plan-approval gate per the addenda; flagging here so the runtime block is visible.
- **Outside-scope plan-review issues #2510 and #2490** were noted in the prompt's fresh issue-review query as also being in `status:plan-review`. They are not in the #2540–#2544 scope of this pack and were not assessed.

## Provenance

- Live issue state captured 2026-04-29 via `gh issue view`.
- Plan files: `docs/plans/2026-04-28-issue-2541*..2544*.md` (commits `bdafe39cd` for hardening, `c7fc39fd3` for re-review).
- Review artifacts: `scripts/review/results/2026-04-29-plan-2541-2544-{codex,gemini,codex-rereview,gemini-rereview,synthesis,rereview-synthesis}.md`.
- Execution evidence for #2542/#2543: commits `05f7b6921` (approval marker) and `b0dac4608` (execution); knowledge test suite 46 passed; raw-data guard empty.
- Memory rules applied: `feedback_never_offer_to_self_label_plan_approved.md`, `feedback_codex_sandbox_fallback_paths.md`, `feedback_attestation_enables_contradiction_detection.md`, `feedback_inline_gh_issue_url.md` (issue refs left as `#NNNN` since this is a markdown artifact for paste-into-issue use, not a chat reply).
