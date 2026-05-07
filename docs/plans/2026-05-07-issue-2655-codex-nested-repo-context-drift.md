# Plan for #2655: Route Codex nested-repo path drift to owning tier-1 repos

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-05-07
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2655
> **Review state:** r3 review returned Claude MINOR, Codex UNAVAILABLE, and Gemini low-confidence sandbox MAJOR. This r4 plan folds in the Claude MINOR findings; no locally verified unresolved MAJOR blockers remain. Codex remains unavailable due known CLI regression; Gemini sandbox findings that cannot see the repo are recorded but treated as low-confidence unless locally verified.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/analysis/provider_session_ecosystem_audit.py:175-193` already contains the `nested_repo_context_drift` remediation rule with the five currently observed Codex nested-repo patterns and canonical targets:
  - `src/worldenergydata/` → `worldenergydata/src/worldenergydata/`
  - `tests/unit/cost/` → `worldenergydata/tests/unit/cost/`
  - `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md` → `worldenergydata/docs/plans/`
  - `src/assethold/` → `assethold/src/assethold/`
  - `sitemap.xml` → `aceengineer-website/sitemap.xml`
- Found: `scripts/analysis/provider_session_ecosystem_audit.py:197-201` currently matches a rule when `path == pattern or path.startswith(pattern)`. This is correct for directory-prefix patterns but is too broad for singleton-file patterns: `sitemap.xml.gz` and `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md.bak` currently match because of the uniform `startswith` rule. This is now an explicit #2655 behavior gap to fix via RED tests.
- Found: `tests/analysis/test_provider_session_ecosystem_audit.py:1514-1539` already verifies part of the nested-repo rule (`src/worldenergydata/...` and `sitemap.xml`) plus canonical targets. #2655 should therefore be a verification/hardening plan, not a greenfield implementation plan.
- Gap: current tests do not separately assert the `tests/unit/cost/` and `src/assethold/` examples, and they do not encode the singleton-file collision boundary (`sitemap.xml.gz`, `.md.bak`) that currently misroutes under uniform prefix matching.

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue planning workflow | applies | `docs/plans/README.md` requires issue → resource intel → plan → adversarial review → `status:plan-review` → user approval before implementation. |
| Hard-stop / approval gate | applies | `AGENTS.md` and `docs/plans/README.md` require no implementation until user approval. |
| Control-plane/session governance | applies | `docs/standards/CONTROL_PLANE_CONTRACT.md` is in the harness/documentation source bundle for session-context work; implementation must preserve workspace-hub as control plane and avoid recreating sibling repo files under the control-plane root. |

### LLM Wiki pages consulted

- N/A — this is provider-session/audit harness routing work, not wiki content work. LLM-wiki spinout cleanup is explicitly out of scope and already tracked by #2650.

### Documents consulted

- Issue #2655 — defines bounded Codex nested-repo routing scope and explicitly excludes recreating `worldenergydata`, `assethold`, or website files under `workspace-hub`.
- `analysis/provider-session-ecosystem-audit.json` — latest audit evidence generated `2026-05-07T09:37:54Z`; `providers.codex.sessions` is `65`, `providers.codex.missing_repo_reads` is `730`, and `providers.codex.missing_repo_read_remediation_hints` contains `nested_repo_context_drift` with `total_count=61`.
- `docs/reports/provider-session-ecosystem-audit.md` — human report identifies Codex `nested_repo_context_drift` as the Codex primary issue and suggests inspecting/routing examples rather than recreating files.
- `docs/ops/legacy-claude-reference-map.md:184-206` — maps nested tier-1 examples and states: prepend owning repo root and re-resolve durable evidence before classifying a read as missing or recreating files.
- Issue #2333 / `docs/plans/2026-04-22-issue-2333-provider-audit-drift-classification-expansion.md` — prior classifier work for transient worktree/scratch/adjacent-project reads; closed/implemented, so #2655 must not duplicate broad non-repo-artifact classification work.
- Issue #2650 — open LLM-wiki post-spinout cleanup; separates `llm_wiki_spinout_path_drift` from this Codex nested-repo stream.
- Issue #2310 — open umbrella for provider-session migration-debt backlog; #2655 is a child-style concrete stream under the audit evidence.
- Issues #2311/#2312/#2161/#2572/#1901 reviewed during stream selection; none directly duplicate this Codex nested-repo routing plan.

### Gaps identified

- Add missing fixture coverage for the observed but currently under-asserted `tests/unit/cost/` and `src/assethold/` examples.
- Add negative/collision-boundary fixtures: `sitemap.xml.gz`, `sitemap.xml.template`, and `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md.bak` must not be swallowed by `nested_repo_context_drift`; the exact `sitemap.xml` and exact issue-334 plan remain evidence-bound singleton mappings.
- Document a generated-artifact diff-bounding rule before any approved implementation regenerates `analysis/provider-session-ecosystem-audit.json` or `docs/reports/provider-session-ecosystem-audit.md`.
- Avoid any implementation that creates sibling repo paths under `workspace-hub` or mutates sibling repos before explicit approval.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-07 via `gh issue view`):

```text
2310 OPEN   analysis(harness): rank Claude stale-read migration-debt backlog and link remediation issues
2311 CLOSED chore(harness): eliminate stale Claude references to removed stage-transition scripts
2312 OPEN   chore(harness): replace legacy local lifecycle-script guidance with GitHub/.planning authority
2161 OPEN   feat(knowledge): ingest provider-session ecosystem audit reads into seeded accessibility registry
2650 OPEN   chore(knowledge): post-spinout cleanup for llm-wiki migration
2333 CLOSED feat(validation): classify transient worktree and scratch-path session reads separately from actionable repo drift
2655 OPEN   chore(provider-session): route Codex nested-repo path drift to owning tier-1 repos
```

**Latest audit excerpt** (`analysis/provider-session-ecosystem-audit.json`, verified 2026-05-07):

```text
generated_at 2026-05-07T09:37:54Z
providers.codex.sessions 65
providers.codex.missing_repo_reads 730
providers.codex.missing_repo_read_remediation_hints[nested_repo_context_drift].total_count 61
canonical_targets worldenergydata/src/worldenergydata/, worldenergydata/tests/unit/cost/, worldenergydata/docs/plans/, assethold/src/assethold/, aceengineer-website/sitemap.xml
src/worldenergydata/cost/data_collection/calibration_schema.py 9
src/worldenergydata/cost/data_collection/public_dataset.py 8
src/worldenergydata/cost/data_collection/__init__.py 8
docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md 8
src/assethold/signals/watchlist.py 7
sitemap.xml 7
src/worldenergydata/cost/calibration/cost_predictor.py 7
tests/unit/cost/test_proxy_comparison.py 7
guidance Codex/Hermes sessions may run from workspace-hub while inspecting nested tier-1 repos; prepend the owning repo root before treating these reads as missing workspace-hub files.
```

**Existing implementation proof and r2-discovered bug** (`scripts/analysis/provider_session_ecosystem_audit.py:175-201`, verified 2026-05-07):

```text
# Existing singleton-file bug: because line 200 uses startswith for all patterns,
# sitemap.xml.gz and docs/plans/...issue-334....md.bak currently match.
# #2655 implementation should split directory-prefix patterns from exact-file patterns.
175     {
176         "rule_id": "nested_repo_context_drift",
177         "patterns": [
178             "src/worldenergydata/",
179             "tests/unit/cost/",
180             "docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md",
181             "src/assethold/",
182             "sitemap.xml",
...
197 def match_remediation_rule(path: str) -> dict | None:
198     for rule in LEGACY_REMEDIATION_RULES:
199         for pattern in rule["patterns"]:
200             if path == pattern or path.startswith(pattern):
201                 return rule
```

**Existing test proof** (`tests/analysis/test_provider_session_ecosystem_audit.py:1514-1539`, verified 2026-05-07):

```text
1514 def test_build_missing_read_remediation_hints_covers_spinout_worktree_and_nested_repo_drift() -> None:
1519     {"path": "src/worldenergydata/cost/data_collection/public_dataset.py", "count": 4},
1520     {"path": "sitemap.xml", "count": 3},
1534     assert by_rule["nested_repo_context_drift"]["matched_paths"] == [
1535         {"path": "src/worldenergydata/cost/data_collection/public_dataset.py", "count": 4},
1536         {"path": "sitemap.xml", "count": 3},
1538     assert "worldenergydata/src/worldenergydata/" in by_rule["nested_repo_context_drift"]["canonical_targets"]
1539     assert "aceengineer-website/sitemap.xml" in by_rule["nested_repo_context_drift"]["canonical_targets"]
```

**No prior canonical #2655 plan proof** (`git grep -n "2655\|nested_repo_context_drift" -- docs/plans`, verified after creating this plan):

```text
docs/plans/README.md:203:| 2655 | codex-nested-repo-context-drift | `docs/plans/2026-05-07-issue-2655-codex-nested-repo-context-drift.md` | ...
# Before this plan/index insertion, no #2655 canonical plan file existed under docs/plans/.
# The only unrelated 2655 hit was a commit hash fragment in an overnight prompt result.
```

**Duplicate issue search proof** (`gh issue list --state open --search '"nested_repo_context_drift" OR "nested repo context" OR "session-local worktree" in:title,body'`, verified 2026-05-07):

```text
2655 OPEN chore(provider-session): route Codex nested-repo path drift to owning tier-1 repos
```

**Reproduction proofs** (verify-against-repo-state, per issue planning mode):

- N/A by issue-planning Step 1.5 branch — #2655 does not allege a user-facing runtime failure, broken import, or failing test to reproduce. It alleges provider-session audit routing drift. Baseline executable proof is therefore a targeted existing-test run plus RED tests in the approved implementation phase.
- Current baseline proof for the affected test file: `uv run --no-project pytest tests/analysis/test_provider_session_ecosystem_audit.py -q` → `49 passed in 0.63s` on 2026-05-07. This proves the existing rule is already partially implemented; the approved work should be a small guardrail/test-hardening patch, not broad classifier redesign.

**Distinct source count:** 8+ (issue #2655, audit JSON, audit report, source file, test file, legacy map, planning README/template, #2333 plan, related GitHub issues).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-07-issue-2655-codex-nested-repo-context-drift.md` |
| Plan index | `docs/plans/README.md` |
| Existing implementation | `scripts/analysis/provider_session_ecosystem_audit.py` |
| Tests to harden | `tests/analysis/test_provider_session_ecosystem_audit.py` |
| Generated audit JSON | `analysis/provider-session-ecosystem-audit.json` |
| Generated audit markdown | `docs/reports/provider-session-ecosystem-audit.md` |
| Existing routing guidance | `docs/ops/legacy-claude-reference-map.md` |
| Latest plan review disagreement | `scripts/review/results/2026-05-07-plan-2655-disagreement.md` |
| Latest plan review Claude | `scripts/review/results/2026-05-07-plan-2655-claude.md` |
| Latest plan review Codex | `scripts/review/results/2026-05-07-plan-2655-codex.md` |
| Latest plan review Gemini | `scripts/review/results/2026-05-07-plan-2655-gemini.md` |
| Archived prior review waves | `scripts/review/results/issue-2655-r1/`, `scripts/review/results/issue-2655-r2/`, `scripts/review/results/issue-2655-r3/` |

---

## Deliverable

A minimal, test-backed provider-session audit guardrail that verifies existing Codex nested-repo routing for all observed tier-1 examples and prevents those paths from being recreated under `workspace-hub`.

---

## Scope Boundaries

### In scope after user approval

- Add/adjust tests in `tests/analysis/test_provider_session_ecosystem_audit.py` for the under-asserted observed examples: `tests/unit/cost/...` and `src/assethold/...`.
- Add a negative test proving unrelated workspace-hub paths remain non-`nested_repo_context_drift`.
- Modify `scripts/analysis/provider_session_ecosystem_audit.py` only for the approved exact-vs-prefix matcher gap, and add non-#2655 regression assertions for representative neighbouring singleton patterns so the universal matcher behavior change is explicit rather than accidental.
- Regenerate audit outputs only if code output changes, and only commit generated diffs if the semantic diff is confined to #2655-relevant remediation-hint text/ordering/counts.

### Out of scope / follow-up only

- Creating `src/worldenergydata/*`, `tests/unit/cost/*`, `src/assethold/*`, or `sitemap.xml` under `workspace-hub`.
- Modifying sibling tier-1 repos (`worldenergydata`, `assethold`, `aceengineer-website`) as part of this issue.
- Generalizing `docs/plans/*` to all possible worldenergydata plan files; current evidence only supports the exact issue-334 plan path.
- Generalizing all root website artifacts to `aceengineer-website`; current evidence only supports `sitemap.xml`.
- LLM-wiki spinout cleanup (`llm_wiki_spinout_path_drift`), currently separated into #2650.
- Broad lifecycle/work-queue cleanup (#2311/#2312) or accessibility-registry ingestion (#2161).
- Reopening closed #2333 classifier work unless implementation discovers a specific regression in that classifier.

---

## Pseudocode

```text
function match_remediation_rule(path):
    for each legacy remediation rule:
        for each rule pattern:
            if pattern represents a directory prefix ending in /:
                if path starts with pattern: return rule
            else:
                if path equals pattern: return rule
    return none

function nested_repo_context_drift_existing_contract(path):
    src/worldenergydata/* routes to worldenergydata/src/worldenergydata/
    tests/unit/cost/* routes to worldenergydata/tests/unit/cost/
    exact issue-334 annual-disclosure plan routes to worldenergydata/docs/plans/
    src/assethold/* routes to assethold/src/assethold/
    exact sitemap.xml routes to aceengineer-website/sitemap.xml
    sitemap.xml.gz and sitemap.xml.template return no nested_repo_context_drift rule
    docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md.bak returns no nested_repo_context_drift rule
    representative non-#2655 singleton patterns still match exactly and no longer match suffix backups accidentally
    unrelated docs/real-missing-workspace-doc.md returns no nested_repo_context_drift rule

function implementation_phase():
    write RED tests for under-asserted examples and collision boundary
    if tests already pass because existing implementation is complete:
        keep code unchanged and document tests-only outcome
    else:
        apply the smallest classifier/reporting patch needed
    run targeted tests and, if generated outputs changed, compare only #2655-relevant remediation-hint blocks before committing generated files
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-05-07-issue-2655-codex-nested-repo-context-drift.md` | canonical approval-gated plan for #2655 |
| Update | `docs/plans/README.md` | add #2655 to plan index |
| Modify after approval | `tests/analysis/test_provider_session_ecosystem_audit.py` | add missing and negative fixture coverage around existing `nested_repo_context_drift` rule |
| Modify after approval | `scripts/analysis/provider_session_ecosystem_audit.py` | split directory-prefix vs exact-file matching globally; add representative tests for neighbouring singleton rules so the blast radius is intentional and bounded |
| Conditional regenerate after approval | `analysis/provider-session-ecosystem-audit.json` | only if code output changes; commit only bounded #2655-relevant semantic diff |
| Conditional regenerate after approval | `docs/reports/provider-session-ecosystem-audit.md` | only if code output changes; commit only bounded #2655-relevant semantic diff |
| Optional modify after approval | `docs/ops/legacy-claude-reference-map.md` | only if implementation changes the documented routing contract; the exact issue-334 singleton mapping may remain code-only because the human map already documents the tier-1 `docs/plans/*` concept at a higher level |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_codex_nested_worldenergydata_tests_route_to_worldenergydata_tests` | GREEN-on-arrival regression guard: under-asserted Codex cost-test paths route to worldenergydata tests | `tests/unit/cost/test_proxy_comparison.py` | rule `nested_repo_context_drift`, target `worldenergydata/tests/unit/cost/` |
| `test_codex_nested_assethold_paths_route_to_assethold_root` | GREEN-on-arrival regression guard: under-asserted assethold source paths route to assethold | `src/assethold/signals/watchlist.py` | rule `nested_repo_context_drift`, target `assethold/src/assethold/` |
| `test_issue_334_plan_path_routes_exactly_without_suffix_collision` | RED-before-fix: exact observed issue-334 plan path routes, but suffix variants do not | observed `docs/plans/2026-04-21-issue-334-annual-operator-disclosures-dataset.md` plus `.md.bak` / `.md~` variants | exact path gets `nested_repo_context_drift`; suffix variants do not |
| `test_sitemap_singleton_routes_exactly_without_suffix_collision` | RED-before-fix: exact `sitemap.xml` routes, but compressed/template variants remain actionable | `sitemap.xml`, `sitemap.xml.gz`, `sitemap.xml.template` | exact path gets `nested_repo_context_drift`; variants do not |
| `test_unrelated_missing_workspace_hub_path_stays_actionable` | unrelated missing workspace-hub docs remain outside nested-repo drift | `docs/real-missing-workspace-doc.md` | no `nested_repo_context_drift` hint unless another exact rule applies |
| `test_nested_repo_context_drift_report_guidance_is_actionable` | GREEN-on-arrival or small-output-update guard: JSON/Markdown guidance tells agents to prepend owning repo root before classifying/recreating | fixed provider summary with all observed examples | guidance and canonical targets appear in generated output |
| `test_legacy_remediation_singleton_patterns_are_exact_not_prefixes` | RED-before-fix for representative non-#2655 singleton patterns affected by global matcher semantics | e.g. exact `scripts/work-queue/close-item.sh` vs `scripts/work-queue/close-item.sh.bak` | exact path still matches owning rule; backup/suffix path does not |

---

## Acceptance Criteria

- [ ] RED phase includes explicit singleton-collision tests for `sitemap.xml.gz`/`sitemap.xml.template`, issue-334 `.md.bak`/`.md~` variants, and one representative non-#2655 singleton rule affected by global matcher semantics; these fail before code changes and pass after the smallest matcher fix.
- [ ] GREEN-on-arrival regression guards for already-supported `tests/unit/cost/` and `src/assethold/` patterns are identified as such in the implementation notes.
- [ ] All #2655-added test names are uniquely collected with a targeted `-k` or explicit test-id command, then the broader file command also passes: `uv run --no-project pytest tests/analysis/test_provider_session_ecosystem_audit.py -v`.
- [ ] Provider-session audit wrapper still runs if code/output changes: `bash scripts/cron/provider-session-ecosystem-audit.sh`.
- [ ] Generated-artifact diff bounding is enforced with recorded before/after evidence: if audit JSON/Markdown are regenerated, compare the before/after `nested_repo_context_drift` remediation-hint block using a small extraction command/script; if the only delta is `generated_at`, do not commit generated files; stop instead of committing if unrelated provider counts/rule IDs or large timestamp churn dominate the diff.
- [ ] Audit JSON/Markdown continue to contain stable Codex `nested_repo_context_drift` guidance with canonical targets for `worldenergydata`, `assethold`, and `aceengineer-website` examples.
- [ ] No sibling repo path is created under `workspace-hub` as part of this issue.
- [ ] Focused secret scan over changed plan/review/docs/code artifacts reports no high-confidence secrets.
- [ ] Latest valid plan review wave has no unresolved MAJOR findings before moving to `status:plan-review`; if Codex/Gemini/Claude tooling is unavailable, the issue comment must transparently state which providers were unavailable and why.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Surrogate/local r1 disagreement report | MAJOR | Existing code and tests already cover much of the original claimed work; plan needed to shrink to verification/hardening, cite source/test lines, remove misleading review artifact framing, add generated-diff bounding, and cite no-prior-plan proof. Provider artifacts for Claude/Gemini were 0-byte/unavailable, so these are recorded as surrogate findings, not provider-returned findings. |
| Codex r1/r2 | UNAVAILABLE | Codex CLI blocked by known incompatible 0.129.0 range; no review signal. |
| Surrogate/local r2 Claude-style review | MAJOR | Found real singleton prefix-collision bug (`sitemap.xml.gz`, issue-334 `.md.bak`), r1 provenance flattening, weak TDD names, generated timestamp ambiguity, and acceptance criteria that did not require the new tests to run. |
| Claude r3 | MINOR | Verified source/test/audit claims and no blockers; requested explicit global matcher blast-radius tests, RED-vs-GREEN test labels, removal of fabricated `.md.draft`, generated-diff evidence wording, and risk acknowledgement for future workspace-hub-owned matching prefixes. This r4 plan folds those in. |
| Codex r3 | UNAVAILABLE | Codex CLI remains blocked by known incompatible 0.129.0 range; no review signal. |
| Gemini r1/r2/r3 | MAJOR, low-confidence sandbox findings | Gemini could not see repo files in its sandbox and produced false missing-file findings; retain artifact for transparency but verify all Gemini claims locally before treating as blockers. |

**Overall result:** r1/r2 MAJOR findings addressed; r3 valid local/Claude review is MINOR with no blockers, and this r4 folds in the MINOR punch-list. Codex unavailable and Gemini sandbox false-positive file-absence findings are disclosed in the issue comment. Ready for `status:plan-review` pending user approval gate.

Revisions made based on r1 review:
- Reframed #2655 as verification/test-hardening over an existing implementation, not greenfield classifier work.
- Cited exact existing source and test lines.
- Added explicit under-asserted test gaps and negative collision-boundary tests.
- Clarified `providers.codex.sessions` source key.
- Added generated-artifact diff-bounding acceptance criterion.
- Added no-prior-plan/duplicate-search evidence.
- Documented provider review unavailability transparently.
- Added singleton-file prefix-collision tests and matcher fix as the concrete approved implementation delta.
- Added `generated_at`-only generated-artifact no-commit rule and explicit #2655-added test collection criterion.
- Folded in r3 MINOR findings: global matcher regression test, RED-vs-GREEN labels, `.md~` suffix instead of fabricated `.md.draft`, generated-diff evidence wording, and future-prefix collision risk.

---

## Risks and Open Questions

- **Risk:** Generated audit JSON/Markdown can be large and reflect live provider-session churn. Mitigation: compare only #2655-relevant remediation-hint semantics and stop on unrelated large churn.
- **Risk:** `sitemap.xml` is a collision-prone singleton if workspace-hub ever gains a real sitemap. Mitigation: implement exact-file matching for singleton patterns and do not broaden root website routing in #2655.
- **Risk:** The issue-334 plan path is exact and not a generic `docs/plans/*` mapping. Mitigation: implement exact-file matching for the singleton issue-334 pattern and do not generalize without new Codex audit evidence from owning repo context.
- **Risk:** Directory-prefix patterns such as `tests/unit/cost/`, `src/worldenergydata/`, and `src/assethold/` depend on workspace-hub not later owning real code at those same prefixes. Mitigation: keep #2655 evidence-bound to current audit examples and require future audit evidence or rule split if workspace-hub gains legitimate files under those prefixes.
- **Open:** If reviewers agree this is already fully covered by existing code/tests, should #2655 be reduced to an evidence-only closeout after approval? Default answer: yes, prefer the smallest approved change.

---

## Complexity: T2

**T2** — bounded audit-harness verification and test-hardening with generated artifact safeguards and cross-review requirements; small implementation breadth, but non-trivial governance/routing risk because singleton-vs-directory matching must not over-generalize.
