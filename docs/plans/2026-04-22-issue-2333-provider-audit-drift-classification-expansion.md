# Plan for #2333: Provider-audit drift classification expansion

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2333
> **Review artifacts:** pending adversarial review

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/analysis/provider_session_ecosystem_audit.py` — already classifies several path families (`symbolic`, `sibling_repo`, repo-local missing, external), and is the central implementation surface for any further drift-bucketing improvements.
- Found: `tests/analysis/test_provider_session_ecosystem_audit.py` — existing audit coverage is the correct place to encode representative path-family fixtures for generated-site paths, transient/worktree paths, and other bucket-separation rules.
- Found: `docs/reports/provider-session-ecosystem-audit.md` — the refreshed audit now explicitly shows providers with `positive_corpus_growth_beyond_recent_activity`, which means the next classification pass must preserve the distinction between recent event-time behavior and newly surfaced historical/exported coverage.
- Gap: there is still no dedicated plan artifact for `#2333`, despite the issue already being the canonical home for codex/hermes drift-classification expansion.
- Gap: current output still mixes generated-site / other-repo paths into actionable workspace-hub drift for some providers.

### Standards
| Standard | Status | Source |
|---|---|---|
| Deterministic classification and truthful reporting of provider-audit buckets | applicable | issue #2333 + current audit/reporting contract |
| External engineering standards | n/a | harness/reporting issue |

### LLM Wiki pages consulted
- No relevant wiki pages — this is audit/reporting classification work, not domain knowledge work.

### Documents consulted
- Issue #2333 — defines the need to separate transient worktree paths, scratch files, and machine-local reads from actionable repo drift.
- `docs/reports/provider-session-ecosystem-audit.md` — refreshed 2026-04-22 audit shows Codex, Hermes, and Gemini all with `positive_corpus_growth_beyond_recent_activity`, making bucket quality more important before remediation priorities are set.
- `docs/reports/2026-04-20-provider-audit-followup-bundle.md` — prior triage already split Codex/Hermes drift into stale repo paths, cross-repo paths, symbolic URIs, and generated-site style paths, providing a starting taxonomy.
- `docs/reports/2026-04-22-provider-session-learning-transfer.md` — confirms the latest refresh should not be interpreted as all-new provider behavior; a significant share is export/backfill/classification coverage becoming more complete.
- `docs/ops/legacy-claude-reference-map.md` — remains the redirect source for true legacy-path debt, which means classification expansion must avoid weakening the actionable stale-path stream while carving out non-actionable families.

### Gaps identified
- No explicit generated-site / other-repo bucket exists yet for recurring Codex path families such as `content/demos/index.html`, `build.js`, `vercel.json`, and `examples/demos/gtm/output/*.html`.
- No explicit contract yet tells downstream consumers how to interpret corpus-growth anomalies versus recent event-time behavior.
- No plan has yet converted the issue's narrative goal into concrete implementation/test/reporting steps.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2333-provider-audit-drift-classification-expansion.md` |
| Audit engine | `scripts/analysis/provider_session_ecosystem_audit.py` |
| Audit tests | `tests/analysis/test_provider_session_ecosystem_audit.py` |
| Existing follow-up bundle | `docs/reports/2026-04-20-provider-audit-followup-bundle.md` |
| Refreshed audit report | `docs/reports/provider-session-ecosystem-audit.md` |
| Learning-transfer note | `docs/reports/2026-04-22-provider-session-learning-transfer.md` |
| Legacy redirect reference | `docs/ops/legacy-claude-reference-map.md` |

---

## Deliverable

A bounded classification-expansion plan that separates true repo-local stale-path debt from generated-site, sibling-repo, symbolic, transient/worktree, and other non-actionable drift families, with deterministic tests and clearer audit interpretation.

---

## Pseudocode

```text
read current top missing path families from the refreshed provider audit
cluster each family into candidate classes:
    true repo-local stale path
    sibling-repo path
    symbolic/non-filesystem identifier
    transient/worktree/external path
    generated-site or adjacent-other-repo path
encode representative fixtures for each class in audit tests
patch audit classification/report rendering so each class is surfaced separately
preserve actionable legacy-path remediation hints for true workspace-hub drift
rerun the audit and verify that downstream recommendations use the cleaner buckets
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/analysis/provider_session_ecosystem_audit.py` | add/refine drift classification buckets and reporting logic |
| Modify | `tests/analysis/test_provider_session_ecosystem_audit.py` | lock in representative fixtures for generated-site, sibling-repo, symbolic, and transient classes |
| Modify | `docs/reports/provider-session-ecosystem-audit.md` | render cleaner interpretation for drift families and corpus anomalies |
| Modify | `docs/ops/legacy-claude-reference-map.md` if needed | keep true stale-path redirect guidance scoped to the actionable bucket only |
| Update | `docs/plans/README.md` | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_generated_site_paths_do_not_count_as_repo_local_stale_drift` | generated-site / adjacent-project path families are split from workspace-hub stale paths | sample Codex-style path set | generated-site bucket, not repo-local missing drift |
| `test_symbolic_and_sibling_repo_paths_remain_separate_from_actionable_repo_drift` | symbolic URIs and sibling-repo paths do not inflate the actionable stale bucket | representative `github://...` and `digitalmodel/...` samples | classified into their dedicated buckets |
| `test_transient_worktree_paths_are_reported_as_non_actionable_external_noise` | worktree/scratch paths remain visible without polluting canonical drift counts | `/mnt/local-analysis/worktrees/...` / `/tmp/...` sample paths | transient/worktree bucket |
| `test_corpus_growth_anomaly_reporting_is_separate_from_recent_event_time_activity` | report output keeps snapshot-growth anomalies distinct from true recent activity | synthetic provider delta input | separate anomaly interpretation fields |

---

## Acceptance Criteria

- [ ] The plan defines deterministic bucket rules for generated-site, sibling-repo, symbolic, transient/worktree, and true repo-local stale paths
- [ ] Reporting preserves the actionable stale-path stream instead of flattening everything into one missing-path bucket
- [ ] Tests cover representative path families for every newly introduced or clarified bucket
- [ ] The refreshed audit can explain positive corpus growth beyond recent activity without mislabeling it as fresh provider drift
- [ ] Follow-up remediation guidance becomes more precise for Codex/Hermes/Gemini after the classification pass

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | not yet reviewed |
| Codex | PENDING | not yet reviewed |
| Gemini | PENDING | not yet reviewed |

**Overall result:** PENDING

Revisions made based on review:
- none yet

---

## Risks and Open Questions

- **Risk:** Over-broad new buckets could hide true workspace-hub stale-path debt if the classifier is too permissive.
- **Risk:** If the audit/report does not keep recent activity separate from snapshot-growth anomalies, follow-up issues may still overreact to backfilled data.
- **Open:** Should generated-site paths get their own dedicated bucket or be grouped under a broader adjacent-project/non-repo class?
- **Open:** Which downstream issue drafts or playbooks need to consume the cleaner bucket outputs once implemented?

---

## Complexity: T2

**T2** — bounded reporting/classification/test work with multiple bucket decisions and downstream interpretation impacts, but no architecture-scale redesign.
