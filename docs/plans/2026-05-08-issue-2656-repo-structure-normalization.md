# Plan for #2656: chore(repo-structure): normalize workspace-hub folder/file structure

> **Status:** ready for `status:plan-review` / user approval; implementation blocked
> **Complexity:** T3
> **Date:** 2026-05-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2656
> **Review artifact:** `scripts/review/results/2026-05-08-plan-2656-repo-structure-review-synthesis.md`
> **Parent anchors:** workspace-hub#1962, workspace-hub#2397

---

## Decision Summary

This plan is a **repo-specific planning gate** for `workspace-hub` folder/file structure normalization. It authorizes only a bounded Phase 1 after approval: inventory-backed structure contract, machine-readable exception policy, checker/test harness, and minimal documentation/index updates required to stop new drift.

No broad file moves, generated artifact deletion, package-source reshuffle, docs migration, or runtime behavior change is authorized until this plan is explicitly approved and Phase 1 tests/checkers exist.

- Workspace-hub root contains nested tier-1 repos and operational agent state; implementation must separate control-plane repo files from nested repo working trees and generated state.

## Resource Intelligence Summary

### Existing assets

- Repository: `vamseeachanta/workspace-hub`
- Current issue: https://github.com/vamseeachanta/workspace-hub/issues/2656
- Root directories observed: .SLASH_COMMAND_ECOSYSTEM/, .agents/, .baseline-cache/, .cache/, .claude/, .codex/, .gemini/, .github/, .hermes/, .hive-mind/, .mypy_cache/, .nightly-results/, .planning/, .pytest_cache/, .ruff_cache/, .swarm/, .sync-reports/, .tmp-inspect-2348/, .uv-cache/, .venv-manim/, .venv-test/, .venv/, .vscode/, .worktrees/, CAD-DEVELOPMENTS/, OGManufacturing/, _archive/, aceengineer-admin/, aceengineer-strategy/, aceengineer-website/, achantas-data/, achantas-media/, acma-projects/, admin/, analysis/, assethold/, assets/, assetutilities/, claude_unattended_test_accept/, client_projects/, config/, coordination/, data/, digitalmodel/, dist/, docker/, docs/, doris/, examples/, frontierdeepwater/, generated/, hobbies/, investments/, kaggle-rogii-2026/, knowledge-base/, knowledge/, llm-wiki/, logs/, monitoring-dashboard/, node_modules/ ...
- Root files observed: **Complexity:**, **Date:**, **Issue:**, **Review, **Status:**, .coverage, .cz.toml, .env.example, .gitattributes, .gitignore, .gitleaks.toml, .jscpd.json, .large-files-exclusions.yaml, .legal-deny-list.yaml, .mcp.json, .pre-commit-config.yaml, .test_performance.db, .tmp-build-commit.py, AGENTS.md, CLAUDE.md, Defines, GEMINI.md, MEMORY.md, Planning, README.md, ace_cfp_sending_kit_2026-04-09.md, ace_gmail_triage_2026-04-09.txt, claude_smoke.log, claude_smoke_prompt.txt, daily_gmail_action_digest_2026-04-09.md, docs-reorg-assessment.md, draft_ace_api_cfp_note.md, draft_skestates_1099_followup_email.md, draft_skestates_hoa_transfer_email.md, draft_skestates_pest_exteriors_followup.md, final_skestates_1099_followup_email.md, final_skestates_hoa_transfer_email.md, final_skestates_pest_exteriors_followup.md, gmail_copy_paste_packet_2026-04-09.md, gmail_operator_packet_2026-04-09.md, gmail_presend_checklist_2026-04-09.md, gmail_sendready_status_2026-04-09.md, gmail_thread_reply_map_2026-04-09.md, issue-1839-gh-comment.md, issue-1839-impl.diff, issue-1839-next-slice-impl.diff, issue-1839-next-slice-review.md, issue-1839-review.md, issue-1858-impl.diff, issue-1858-review.md, nohup.out, personal_gmail_triage_2026-04-09.txt, pyproject.toml, sendready_skestates_1099_email.md, sendready_skestates_hoa_email.md, sendready_skestates_pest_email.md, skestates_gmail_triage_2026-04-09.md, terminal-2-impl.diff, terminal-2-review.md, transcript_raw.json, uv.lock, video_summary.txt, youtube_summary.txt
- Standard directory counts:
- `src/`: 151 files in working-tree scan
- `tests/`: 1151 files in working-tree scan
- `docs/`: 1681 files in working-tree scan
- `scripts/`: 3737 files in working-tree scan
- `config/`: 256 files in working-tree scan
- `.github/`: 7 files in working-tree scan
- `output/`: 7 files in working-tree scan
- `reports/`: 147 files in working-tree scan
- `data/`: 19899 files in working-tree scan
- `dist/`: 44 files in working-tree scan

### Tracked root files observed

- `ace_cfp_sending_kit_2026-04-09.md`
- `ace_gmail_triage_2026-04-09.txt`
- `AGENTS.md`
- `CLAUDE.md`
- `claude_smoke_prompt.txt`
- `**Complexity:**`
- `.cz.toml`
- `daily_gmail_action_digest_2026-04-09.md`
- `**Date:**`
- `Defines`
- `docs-reorg-assessment.md`
- `draft_ace_api_cfp_note.md`
- `draft_skestates_1099_followup_email.md`
- `draft_skestates_hoa_transfer_email.md`
- `draft_skestates_pest_exteriors_followup.md`
- `.env.example`
- `final_skestates_1099_followup_email.md`
- `final_skestates_hoa_transfer_email.md`
- `final_skestates_pest_exteriors_followup.md`
- `GEMINI.md`
- `.gitattributes`
- `.gitignore`
- `.gitleaks.toml`
- `gmail_copy_paste_packet_2026-04-09.md`
- `gmail_operator_packet_2026-04-09.md`
- `gmail_presend_checklist_2026-04-09.md`
- `gmail_sendready_status_2026-04-09.md`
- `gmail_thread_reply_map_2026-04-09.md`
- `**Issue:**`
- `issue-1839-gh-comment.md`
- `issue-1839-impl.diff`
- `issue-1839-next-slice-impl.diff`
- `issue-1839-next-slice-review.md`
- `issue-1839-review.md`
- `issue-1858-impl.diff`
- `issue-1858-review.md`
- `.jscpd.json`
- `.large-files-exclusions.yaml`
- `.legal-deny-list.yaml`
- `.mcp.json`
- `MEMORY.md`
- `nohup.out`
- `personal_gmail_triage_2026-04-09.txt`
- `Planning`
- `.pre-commit-config.yaml`
- `pyproject.toml`
- `README.md`
- `**Review`
- `sendready_skestates_1099_email.md`
- `sendready_skestates_hoa_email.md`
- `sendready_skestates_pest_email.md`
- `skestates_gmail_triage_2026-04-09.md`
- `**Status:**`
- `terminal-2-impl.diff`
- `terminal-2-review.md`
- `.tmp-build-commit.py`
- `transcript_raw.json`
- `uv.lock`
- `video_summary.txt`
- `youtube_summary.txt`

### Tracked generated-output candidates observed

- `logs/hooks/.gitkeep`
- `logs/notifications/.gitkeep`
- `logs/orchestrator/README.md`
- `logs/orchestrator/codex/.export-state.json`
- `logs/orchestrator/codex/.last-export-ts`
- `logs/orchestrator/codex/session_20260208.jsonl`
- `logs/orchestrator/codex/session_20260212.jsonl`
- `logs/orchestrator/codex/session_20260213.jsonl`
- `logs/orchestrator/codex/session_20260216.jsonl`
- `logs/orchestrator/codex/session_20260217.jsonl`
- `logs/orchestrator/codex/session_20260218.jsonl`
- `logs/orchestrator/codex/session_20260219.jsonl`
- `logs/orchestrator/codex/session_20260222.jsonl`
- `logs/orchestrator/codex/session_20260223.jsonl`
- `logs/orchestrator/codex/session_20260224.jsonl`
- `logs/orchestrator/codex/session_20260225.jsonl`
- `logs/orchestrator/codex/session_20260226.jsonl`
- `logs/orchestrator/codex/session_20260227.jsonl`
- `logs/orchestrator/codex/session_20260228.jsonl`
- `logs/orchestrator/codex/session_20260301.jsonl`
- `logs/orchestrator/codex/session_20260302.jsonl`
- `logs/orchestrator/codex/session_20260303.jsonl`
- `logs/orchestrator/codex/session_20260304.jsonl`
- `logs/orchestrator/codex/session_20260305.jsonl`
- `logs/orchestrator/codex/session_20260306.jsonl`
- `logs/orchestrator/codex/session_20260307.jsonl`
- `logs/orchestrator/codex/session_20260308.jsonl`
- `logs/orchestrator/codex/session_20260309.jsonl`
- `logs/orchestrator/codex/session_20260310.jsonl`
- `logs/orchestrator/codex/session_20260311.jsonl`
- `logs/orchestrator/codex/session_20260312.jsonl`
- `logs/orchestrator/codex/session_20260313.jsonl`
- `logs/orchestrator/codex/session_20260314.jsonl`
- `logs/orchestrator/codex/session_20260315.jsonl`
- `logs/orchestrator/codex/session_20260316.jsonl`
- `logs/orchestrator/codex/session_20260318.jsonl`
- `logs/orchestrator/codex/session_20260321.jsonl`
- `logs/orchestrator/codex/session_20260322.jsonl`
- `logs/orchestrator/codex/session_20260323.jsonl`
- `logs/orchestrator/codex/session_20260326.jsonl`
- `logs/orchestrator/codex/session_20260330.jsonl`
- `logs/orchestrator/codex/session_20260331.jsonl`
- `logs/orchestrator/codex/session_20260401.jsonl`
- `logs/orchestrator/codex/session_20260402.jsonl`
- `logs/orchestrator/codex/session_20260408.jsonl`
- `logs/orchestrator/codex/session_20260409.jsonl`
- `logs/orchestrator/codex/session_20260410.jsonl`
- `logs/orchestrator/codex/session_20260411.jsonl`
- `logs/orchestrator/codex/session_20260412.jsonl`
- `logs/orchestrator/codex/session_20260414.jsonl`
- `logs/orchestrator/codex/session_20260415.jsonl`
- `logs/orchestrator/codex/session_20260416.jsonl`
- `logs/orchestrator/codex/session_20260417.jsonl`
- `logs/orchestrator/codex/session_20260419.jsonl`
- `logs/orchestrator/codex/session_20260420.jsonl`
- `logs/orchestrator/codex/session_20260421.jsonl`
- `logs/orchestrator/codex/session_20260422.jsonl`
- `logs/orchestrator/codex/session_20260423.jsonl`
- `logs/orchestrator/codex/session_20260424.jsonl`
- `logs/orchestrator/codex/session_20260425.jsonl`
- `logs/orchestrator/codex/session_20260426.jsonl`
- `logs/orchestrator/codex/session_20260427.jsonl`
- `logs/orchestrator/codex/session_20260428.jsonl`
- `logs/orchestrator/codex/session_20260429.jsonl`
- `logs/orchestrator/codex/session_20260430.jsonl`
- `logs/orchestrator/codex/session_20260501.jsonl`
- `logs/orchestrator/codex/session_20260502.jsonl`
- `logs/orchestrator/codex/session_20260503.jsonl`
- `logs/orchestrator/codex/session_20260504.jsonl`
- `logs/orchestrator/codex/session_20260506.jsonl`
- `logs/orchestrator/codex/session_20260507.jsonl`
- `logs/orchestrator/hermes/.last-export-ts`
- `logs/orchestrator/hermes/corrections/session_20260401.jsonl`
- `logs/orchestrator/hermes/corrections/session_20260402.jsonl`
- `logs/orchestrator/hermes/corrections/session_20260403.jsonl`
- `logs/orchestrator/hermes/corrections/session_20260404.jsonl`
- `logs/orchestrator/hermes/corrections/session_20260405.jsonl`
- `logs/orchestrator/hermes/corrections/session_20260406.jsonl`
- `logs/orchestrator/hermes/corrections/session_20260407.jsonl`
- `logs/orchestrator/hermes/corrections/session_20260408.jsonl`

### Related prior work

- Workspace-hub ecosystem anchors: `workspace-hub#1962` and `workspace-hub#2397`.
- `digitalmodel#596` is the template-quality first repo plan and discipline model: contract first, checker second, bounded moves only after approval.
- This plan does not assume previous repo-specific cleanup issues are complete; implementation must re-check live git state before editing.

### Constraints

- Follow workspace-hub hard gates: Issue → Plan → Adversarial Review → `status:plan-review` → explicit user approval → implementation.
- TDD is mandatory before checker or migration code.
- Preserve evidence and rollback ability for every moved/removed tracked path.
- Do not delete or relocate generated-looking tracked files until classified as unauthorized artifact, durable evidence, or temporary durable exception.
- Do not move package/source/runtime/static entrypoints without import/build/deploy proof specific to this repo.

### Gaps

- No approved local structure contract for this normalization tranche.
- Generated-output and root-clutter classification needs a machine-readable allow/deny/exception inventory before cleanup.
- CI/pre-commit enforcement may be absent or insufficient for new root artifacts.

### Risks / unknowns

- Hidden consumers may reference current paths from docs, CI, packaging, static hosting, notebooks, or external scripts.
- Some generated-looking files may be durable evidence or deploy artifacts; deleting them blindly would lose traceability.
- Root-level clutter can include user/session artifacts; implementation must not reset unrelated dirty files.

## Scope Boundaries

### In scope after approval

1. Add/update repo-local structure standard under `docs/standards/repo-structure.md` or closest existing standards surface.
2. Add machine-readable contract such as `config/repo_structure.yml` listing allowed roots, denied generated roots, and temporary durable exceptions.
3. Add checker under `scripts/maintenance/verify_repo_structure.py` or equivalent repo-appropriate maintenance path.
4. Add TDD tests under `tests/repo_structure/` or equivalent test surface.
5. Wire checker into pre-commit/CI if those surfaces exist.
6. Move only low-risk root utility/docs artifacts that have no source/runtime consumers and are covered by tests/checker evidence.
7. Create follow-up issues for broad package/docs/generated-evidence migrations discovered during implementation.

### Out of scope

- Bulk source package reorganization.
- Broad docs tree migration.
- Deletion of generated-looking tracked files without classification and follow-up linkage.
- Notebook/data/report/static deploy relocation unless explicitly classified and tested.
- Any execution before explicit user approval.

## Artifact Map

| Artifact | Path | Purpose |
|---|---|---|
| Canonical plan | `docs/plans/2026-05-08-issue-2656-repo-structure-normalization.md` | Approval gate for this repo |
| Review synthesis | `scripts/review/results/2026-05-08-plan-2656-repo-structure-review-synthesis.md` | Adversarial/readiness findings |
| Structure standard | `docs/standards/repo-structure.md` or existing standard path | Human-readable contract |
| Machine contract | `config/repo_structure.yml` | Checker source of truth |
| Checker | `scripts/maintenance/verify_repo_structure.py` | Enforce root/generated/exception rules |
| Tests | `tests/repo_structure/test_repo_structure_contract.py` | TDD for checker and contract |
| Approval marker after approval only | `.planning/plan-approved/2656.md` | Execution authorization evidence |

## Pseudocode

```text
load config/repo_structure.yml
collect git-tracked paths and working-tree root entries
for each root entry:
    classify as allowed, denied-generated, temporary-exception, or unknown
    if unknown or denied without exception:
        emit deterministic violation with remediation hint
for each temporary exception:
    require owner/category/review-date/follow-up URL/non-placeholder justification
scan moved-file candidates:
    require no references outside approved update set before moving
return nonzero if violations exist
```

## TDD Test List

- RED: checker fails on an unapproved root file/dir fixture.
- RED: checker fails on tracked generated-output root without exception metadata.
- RED: checker fails on exception metadata with placeholder owner/review-date/follow-up URL.
- GREEN: checker accepts current approved roots and explicitly listed exceptions.
- GREEN: reference scan blocks candidate moves with live consumers.
- GREEN: CI/pre-commit invocation path is covered by a smoke test or workflow grep assertion.

## Acceptance Criteria

1. Plan remains planning-only until explicit user approval.
2. Implementation has TDD coverage before checker/migration code lands.
3. Human-readable and machine-readable structure contracts exist.
4. Generated-output candidates are classified, not blindly deleted.
5. CI/pre-commit prevents newly introduced root/generated drift.
6. Any moved paths have reference-scan proof and rollback notes.
7. Follow-up issues are created for broad migrations rather than silently absorbed.

## Follow-up Issue Candidates

- Package/domain module reorganization if inventory shows large package-layout drift.
- Generated evidence relocation/classification for tracked reports/results/build outputs.
- Docs/navigation restructuring if docs references require broader moves.
- Static deploy artifact policy, if applicable, for generated `dist/`, site, sitemap, or public assets.

## Review Readiness Notes

This plan is intentionally conservative and reusable across the tier-1 repo ecosystem. Reviewers should reject implementation attempts that start moving/deleting files before the contract/checker/test layer is approved and green.

## Approval Gate

Execution is not authorized until the user approves this exact plan and implementation records `.planning/plan-approved/2656.md` with the reviewed commit/blob SHA.
