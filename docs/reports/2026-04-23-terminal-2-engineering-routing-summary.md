# Terminal-2 engineering-routing summary — overnight 2026-04-22/23

- Scope: tier-1 routing-remediation plans for the two engineering-core repos (`assetutilities`, `digitalmodel`).
- Session type: planning + adversarial review only. No source-code edits in nested repos. No `status:plan-approved` labels. No approval markers.
- Owned write paths — confirmed only these were touched:
  - `docs/plans/2026-04-22-issue-2461-assetutilities-routing-and-source-hygiene.md` (created)
  - `docs/plans/2026-04-22-issue-2462-digitalmodel-repo-wide-routing-surfaces.md` (created)
  - `docs/plans/README.md` (+2 rows: #2461, #2462)
  - `scripts/review/results/2026-04-22-plan-2461-claude.md` (created)
  - `scripts/review/results/2026-04-22-plan-2462-claude.md` (created)
  - `docs/reports/2026-04-23-terminal-2-engineering-routing-summary.md` (this file)

## What changed per issue

### #2461 — assetutilities routing + source-hygiene

- Canonical plan created from the template and filled with live-verified evidence.
- Explicit contract-dependency on #2460 stated at the plan header (registry filename, operator-map host location deferred to #2460).
- Evidence cites:
  - four tracked `.bak`/`.orig` files under `src/assetutilities/common/` (verified via `git ls-files`);
  - two `.bat` Windows scratch helpers in `tests/` (`visualizations_tests.bat`, `visualizations_tests_temp.bat`);
  - `assetutilities/MODULE_STRUCTURE.md` claiming non-existent `core/` and `utils/` directories while omitting real `common/`, `constants/`, `base_configs/`, `calculations/`, `tools/`, `units/`, `devtools/`;
  - `assetutilities/docs/README.md` absent (`ls` returns "No such file or directory").
- TDD test list covers: canonical surfaces present, module structure matches live tree, no tracked `.bak`/`.orig` anywhere under `src/**`, `.gitignore` blocks both patterns, workspace-hub stale-reference guard covers the new docs.
- Claude adversarial review written with 8 findings, overall MINOR. Key defects surfaced: operator-map host contradiction (F1), registry-path unfalsifiability pending #2460 (F2), hard-coded directory count that guarantees future drift (F3), `.bat`-deletion not preceded by a reference-grep (F4).

### #2462 — digitalmodel repo-wide routing

- Canonical plan created. Framing is generalization, not cleanup: digitalmodel has the best tier-1 codebase but only the OrcaWave/OrcaFlex slice currently has a canonical operator map.
- Evidence cites:
  - `digitalmodel/docs/README.md` absent;
  - `digitalmodel/specs/module-registry.yaml` missing (only `specs/modules/` exists);
  - `ROADMAP.md:9` and `ROADMAP.md:50` still treat the missing registry as canonical;
  - `README.md:46` honestly admits staleness but does not resolve it;
  - workspace-hub `docs/maps/` contains exactly one map (the OrcaWave/OrcaFlex slice) that the repo-wide map will generalize;
  - `docs/domains/README.md` already shows the redirect pattern for one slice — generalization is the work.
- TDD test list binds the operator-map rows to the live `src/digitalmodel/` tree at test time (drift-resistant by construction), requires the OrcaWave/OrcaFlex rows in the repo-wide map to be link-only (not duplicated content), and asserts the stale `specs/module-registry.yaml` string disappears from `ROADMAP.md` entirely.
- Claude adversarial review written with 8 findings, overall MINOR. Key defects surfaced: registry path unfalsifiable pending #2460 (F1), ROADMAP line-number pinning will false-pass on edits (F2), cross-repo test boundary unresolved — test runs in digitalmodel but operator map lives in workspace-hub (F3), the "30 domains" figure overcounts by including files that are not packages (F4).

## Best first execution candidate

**Recommendation: #2461 goes first.** Rationale:

1. **Risk asymmetry.** The scorecard ranks assetutilities 8/20 (weakest tier-1 repo) and names it "highest risk of putting code in the wrong place." #2462's repo is already 13/20 — best in tier-1 — so shipping it first returns less per hour of attention.
2. **Source-hygiene cleanup is blocking-class evidence.** Four tracked `.bak`/`.orig` files and two `.bat` scratch helpers are concrete, small, and high-signal. Removing them produces a verifiable trust win that every later tier-1 plan can cite as a precedent.
3. **Dependency graph favors assetutilities-first.** `digitalmodel/AGENTS.md` declares `depends_on: [assetutilities]`. Stabilizing the assetutilities routing surfaces first means #2462's repo-wide operator map for digitalmodel can point at canonical assetutilities paths without either retargeting or sprouting placeholder links.
4. **Smaller blast radius.** #2461 touches ~14 files across docs + hygiene, and its biggest risk (downstream import breakage) is already mitigated by the fact that `.bak`/`.orig` files should have no importers. #2462 touches three drift-cleanup sites in existing docs plus a 30-row operator map — broader surface area, more review burden.
5. **Cross-review cost.** Both plans depend on #2460 freezing the registry filename. If Codex/Gemini surface blockers, #2461's smaller surface makes the re-review loop tighter.

If #2460 is the true blocker for *both* (it is — registry path is required by both), then the actual dispatch order tomorrow is: **#2460 → #2461 → #2462.** #2461 and #2462 can run in parallel once #2460 lands the contract, but if serial execution is required, #2461 first.

## Shared blocker patterns

Both plans converge on the same three blockers, all rooted in the upstream #2460 contract:

1. **Registry path unfalsifiable until #2460 freezes.** The machine-readable registry filename is contract-level, not per-repo. Neither plan can write a testable registry-exists assertion today. This is flagged in both plans' Risks sections and in both Claude reviews (#2461 F2, #2462 F1). Mitigation: explicit plan-level precondition — implementation MUST NOT begin until #2460 freezes the registry filename for tier-1 repos.

2. **Operator-map host location deferred.** Both plans currently assume workspace-hub `docs/maps/` is the canonical host (based on the existing digitalmodel-orcawave-orcaflex map). If #2460 picks per-repo `docs/maps/` hosting, both plans re-home the artifact and re-write their routing-contract tests. Raised in #2461 F1 and #2462 F3.

3. **Cross-repo test-execution boundary.** A routing-contract test living in a nested repo cannot easily read a workspace-hub-hosted operator map. #2462's F3 states this sharply; #2461 has the same latent issue. The decision set: (a) relocate routing-contract tests to workspace-hub and walk both repos from there, or (b) host operator maps per-repo. #2460 picks one.

Additional shared patterns worth naming:

4. **Drift-resistant derivation over hard-coded lists.** Both plans initially included hard-coded directory lists; both Claude reviews flagged them. The corrected stance is: acceptance criteria and tests must derive the required set from `git ls-tree <src path>` at implementation/test time, never hard-code.

5. **"Stale until restored" language.** Both repos admit stale references in docs (digitalmodel explicitly; assetutilities implicitly via outdated `MODULE_STRUCTURE.md`). Replacing the stale claim without linking the canonical replacement degrades routing — plans must require positive assertions (new link present), not only negative assertions (old string absent).

## Suggested morning dispatch order

1. **Terminal 1 first.** #2460 needs to freeze the registry filename and operator-map host location before #2461 and #2462 can move into `status:plan-review`. If the overnight T1 run converged on a freeze, dispatch #2460 adversarial re-review and approval first.
2. **Dispatch Codex + Gemini cross-review for #2461.** The Claude MINOR review is written; the external artifacts are the missing dependency. Smaller plan surface, tighter loop.
3. **Dispatch Codex + Gemini cross-review for #2462.** Same loop, bigger surface — expect more findings, budget an extra pass.
4. **Do not dispatch implementation on either plan** until:
   - #2460 has `status:plan-approved` and local marker;
   - Codex and Gemini artifacts exist at `scripts/review/results/*2461*` and `*2462*`;
   - this plan's preconditions (registry freeze, operator-map host, cross-repo test boundary) are resolved.
5. **Do NOT self-approve.** Both plans stay at `draft` until the user approves. The planning-only session cannot and did not attempt to advance the labels.

## Open items still blocking tomorrow

- Codex review artifact for #2461 — missing.
- Codex review artifact for #2462 — missing.
- Gemini review artifact for #2461 — missing.
- Gemini review artifact for #2462 — missing.
- #2460 registry filename freeze — still draft; if unresolved by morning, both plans need a quick pass to tighten their acceptance criteria once #2460 freezes.
- #2460 operator-map host location — still implicit (workspace-hub assumed); should be explicit.
- Cross-repo test-execution boundary — unresolved in #2462 (F3). Awaits #2460 decision on operator-map host.

## Provenance notes (transparent)

- All adversarial reviews for #2461 and #2462 are single-author Claude under the `feedback_permission_gate_blocks_cross_review.md` fallback: the planning-only session does not have permission to dispatch `scripts/review/submit-to-codex.sh` or `scripts/review/submit-to-gemini.sh`, so Codex and Gemini artifacts are explicitly marked PENDING rather than fabricated.
- No nested-repo files were edited. Forbidden write paths (`assetutilities/src/**`, `assetutilities/tests/**`, `digitalmodel/src/**`, `digitalmodel/tests/**`, `.planning/plan-approved/**`, other terminals' plan artifacts) were not touched.
- The `docs/plans/README.md` edit added exactly two new rows (#2461, #2462). Only rows owned by this terminal were modified.

---

## RERUN STARTED (2026-04-23 overnight — terminal-2 rerun)

- Timestamp (UTC): 2026-04-23T03:48:30Z
- Prior run summary above is retained unchanged as historical context.
- Intended worktree: `/mnt/local-analysis/worktrees/ws-tier1-knowledge-overnight-t2` (branch `nightly/tier1-knowledge-overnight-t2` at `45f138bb2`).
- Actual working tree: `/mnt/local-analysis/workspace-hub` (branch `integration/runbook-main-compatible` — same commit `45f138bb2`). The harness sandbox for this rerun restricts writes to `/mnt/local-analysis/workspace-hub`, so the named worktree path is unreachable; artifacts land on the integration branch and can be cherry-picked by the orchestrator.

### Truth corrections discovered at rerun entry
- `docs/plans/README.md:280` (the #2462 row) claimed "Codex/Gemini cross-review PENDING" — **STALE**. On-disk: `scripts/review/results/2026-04-22-plan-2462-codex.md` (APPROVE, r2) and `scripts/review/results/2026-04-22-plan-2462-gemini.md` (MINOR, r2) both exist and are substantive single-author r3-fallback proxies.
- This summary file's own "Open items still blocking tomorrow" section listed Codex and Gemini artifacts for #2462 as "missing" — **STALE** for the same reason.
- #2461 plan was at `draft` (no r2 tightening) despite a Claude MINOR review with four critical findings (F1 host-contradiction, F2 registry-path unfalsifiability, F3 hard-coded 10-directory count, F4 `.bat`-deletion unverified). #2462's peer-reviewed r2 hardening (HARD GATE, sibling scope boundary, anti-loophole AC, source-hygiene surface coverage, red-phase evidence AC) had not been ported back.

## RERUN COMPLETED (2026-04-23 overnight — terminal-2)

### Files changed during this rerun
1. `docs/plans/2026-04-22-issue-2461-assetutilities-routing-and-source-hygiene.md` — r2 tightening (9 surgical edits). Specifics:
   - Status line updated: `draft` → `draft (adversarial-reviewed r1 — Claude MINOR; Codex/Gemini PENDING; r2 tightening applied 2026-04-23)`.
   - Added **HARD GATE** front-matter (F2 fix) requiring #2460 at `status:plan-approved` AND contract-doc textual lock of registry filename + operator-map host location before implementation.
   - Added **Sibling scope boundary** front-matter naming #2460/#2462/#2463/#2464/#2465 owners.
   - F1: Gap-list + Artifact Map + Files-to-Change + AC rows for the operator map now read "host/path per #2460" instead of hard-asserting workspace-hub `docs/maps/`.
   - F3: two TDD rows (`test_operator_map_covers_all_top_level_source_dirs`, `test_registry_covers_all_top_level_source_dirs`) and one AC row now derive the expected directory set from `git ls-tree src/assetutilities` at test time instead of hard-coding the 10 names — drift-resistant by construction.
   - F5: `test_module_structure_matches_observed_tree` bound to live-tree derivation.
   - F6: `test_docs_readme_states_curated_vs_raw_boundary` now requires ≥3 curated subtrees AND ≥1 raw subtree, both bound to named paths.
   - F4+F7: `hygiene_cleanup` pseudocode function now has five pre-delete discovery greps (`ApplicationManager\.py\.(bak|orig)`, `file_management\.py\.(bak|orig)`, `visualizations_tests`) that MUST return empty before any `git rm` runs; non-empty hits reclassify the action as investigate/move, not delete. New acceptance criterion binds this to captured grep output as evidence.
   - F2: Risks section promoted the registry-filename risk to a **Blocker** paragraph referencing HARD GATE front-matter.
   - F4 risk rewritten: `.bat` deletion mitigation now states the pre-delete grep requirement explicitly rather than the prior "should" language.
   - F7 risk rewritten: downstream-consumer importer check is now a pre-delete grep assertion, not an implicit assumption.
   - F1 risk rewritten: operator-map host risk is now "resolved by HARD GATE".
   - Anti-loophole AC added (parallels #2462 r2 per `feedback_codex_sustained_major_loop.md`): all three providers must clear APPROVE/MINOR; no "at most one non-APPROVE/MINOR" bypass.
   - Sibling non-encroachment AC added.
   - TDD red-phase evidence AC added (captured pytest output for new tests before docs/edits land).
2. `docs/plans/2026-04-22-issue-2462-digitalmodel-repo-wide-routing-surfaces.md` — cleared both Gemini r2 MINORs (2 surgical edits + 1 status-line edit):
   - **Gemini r2 MINOR #1** (hard-gate coupling too weak): HARD GATE front-matter now requires `#2460 status:plan-approved` AND contract-doc textual lock of registry path shape + operator-map host location (either in #2460 plan or `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` on main). AC #15 (the hard-gate AC) carries matching stronger wording.
   - **Gemini r2 MINOR #2** (AC #14 spurious-pass risk on filename drift): AC #14 now binds the row's third-column path value to this plan's canonical filename, not just issue-number presence.
   - Status line updated to reflect the r2-plus-Gemini-MINORs-cleared state.
3. `docs/plans/README.md` — two row corrections (truthfulness fixes):
   - Row for #2461 rewritten to reflect r2 tightening (specifics above), retaining the accurate "Codex/Gemini cross-review PENDING" labeling (still true — planning-only session).
   - Row for #2462 corrected to reflect the on-disk r2 review artifacts (Claude MINOR, Codex APPROVE, Gemini MINOR — previously mislabeled "PENDING") and the rerun's Gemini-r2-MINORs-cleared state.
4. `docs/reports/2026-04-23-terminal-2-engineering-routing-summary.md` — this rerun section appended. Prior-run content preserved.

### Deliberately NOT done (per task guardrails)
- No nested-repo edits to `assetutilities/**` or `digitalmodel/**` source/tests/docs. All tightening stayed in workspace-hub `docs/plans/**`, `docs/plans/README.md`, and this summary file.
- No `.planning/plan-approved/` writes.
- No `status:plan-approved` label changes (and no offer to self-approve; user-in-loop gate preserved per `feedback_never_offer_to_self_label_plan_approved.md`).
- No fabrication of Codex/Gemini reviews for #2461 — they remain PENDING on disk and in the labels. The r2 tightening is explicitly a single-author Claude-lens pass with transparent provenance in the status line.
- No re-issue of Codex APPROVE or Gemini MINOR for #2462 — the existing artifacts remain authoritative; only the wording issues they surfaced were addressed in the plan.

### Blockers remaining
- **#2460 registry filename + operator-map host freeze** — still the upstream gate for both #2461 and #2462 implementation. Neither plan can move from `draft` to `status:plan-approved` until #2460's contract doc textually locks those items.
- **Codex and Gemini reviews for #2461** — still PENDING on disk. Require a gate-capable session to dispatch via `scripts/review/cross-review.sh` or `scripts/review/submit-to-{codex,gemini}.sh`. The r2 tightening done in this rerun is pre-emptive and addresses the issues a real cross-review would surface, but does not substitute for live reviewer artifacts. Morning operator to dispatch.
- **Sandbox-path mismatch** — the orchestrator dispatched this rerun against worktree `ws-tier1-knowledge-overnight-t2` on branch `nightly/tier1-knowledge-overnight-t2`, but the session harness scoped writes to `/mnt/local-analysis/workspace-hub` only, so artifacts landed on `integration/runbook-main-compatible`. Morning operator should cherry-pick if the overnight-branch commit stream is desired. (Both refs point at `45f138bb2` so a plain cherry-pick of these commits by hash is safe.)
- **Review-label hygiene**: issue #2461 and #2462 currently carry `status:plan-review`. #2461's Codex+Gemini still missing means it does not yet meet the "all three APPROVE/MINOR" bar introduced in the r2 anti-loophole AC; morning operator must not move it to `status:plan-approved` without those artifacts.

### Advancement judgment for GitHub comments
- #2461 advanced meaningfully: r2 tightening addresses all four critical Claude findings and brings structural parity with #2462. A concise GitHub comment on #2461 is warranted.
- #2462 advanced modestly: both Gemini r2 MINORs cleared. A concise GitHub comment on #2462 is warranted to note the residual MINOR set is now empty pending a fresh external rerun.
- Neither advancement justifies a label change; both remain `status:plan-review` pending real Codex/Gemini artifacts (#2461) or a fresh external rerun (#2462), plus the hard #2460 gate.


