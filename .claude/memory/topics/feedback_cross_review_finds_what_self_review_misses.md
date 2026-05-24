> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_cross_review_finds_what_self_review_misses.md

---
name: cross-review-finds-what-self-review-misses
description: "Code-stage adversarial cross-review consistently finds defects that the implementing session's self-review misses — never skip the cross-review gate post-implementation, even when feeling confident"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 301086a5-63fe-4d73-a934-dd43ff2f9c0d
---

Cross-review at the code stage catches defects that the implementing session's self-review reliably misses. Never skip the cross-review gate, even when implementation feels solid.

**Why:** 2026-05-21 close-out of digitalmodel#617 + worldenergydata#429: implementation landed feeling clean — tests passing, plan acceptance criteria met, end-to-end live-resolver verification successful. Dispatched 4 parallel code-reviewer subagents (2 per issue, different focus angles). Both verdicts came back **MAJOR**, not the expected MINOR. Findings the implementing session had not surfaced:

- **Public-repo client identifier leak** (`worldenergydata-wiki:MIGRATION_MANIFEST.md:46` mentioned `B1528, SIROCCO, acma-projects` verbatim in a public repo deny-row — even as a "what NOT to include" example, the identifiers were exposed in CC-BY-4.0 prose);
- **LICENSE paraphrase failing GitHub detection** (the LICENSE file was a hand-written summary rather than the canonical CC-BY-4.0 legalcode.txt; `spdx_id: NOASSERTION` blocked the green badge and CC-license filters);
- **Duplicated resolver logic** in `digitalmodel:mooring_design.py:_default_repo_root` — parallel 6-level chain that silently bypassed the canonical resolver's DeprecationWarning + known-local-clones fallback; users of the legacy env var would never see the migration nudge;
- **Asymmetric env-var error handling** (LLM_WIKI_PATH=invalid raised hard while DIGITALMODEL_REPO_ROOT=invalid silently fell through);
- **Routing-rule §6 self-contradiction** (one line said "route to public sibling worldenergydata-wiki", another line on the same rule said methodology content "can live in public llm-wiki" — but llm-wiki is now PRIVATE);
- **Migration-manifest factual error** (manifest claimed no pre-existing BSEE-derived wiki pages; reviewer found a substantive 100+ line BSEE analysis at `llm-wiki:wikis/asset-management/wiki/sources/bsee-2024-deepwater-dynamic-pipeline-riser-life-extension.md`);
- **OR-disjunction test fences** that mask refactoring regressions (`"X" in reason or "Y" in reason` accepted both branches, removing the regression-fence on the distinct stale-clone branch);
- **GitHub repo `hasWikiEnabled: true`** by default — contradicted the plan's "regular repo with wiki/ directory NOT GitHub Wiki feature" decision.

**How to apply:**

- After implementation lands but BEFORE claiming close-out, dispatch parallel code-reviewer agents with explicit focus angles (correctness, security, back-compat, governance, license). Default verdict expectation: MINOR, not APPROVE. If verdicts come back APPROVE, ask whether the reviewers actually defect-hunted.
- Cross-review depth scales with issue complexity: T1=1 angle, T2=2 angles, T3=3 angles per AGENTS.md AI Review Policy. For single-provider sessions, single-provider-multi-angle (per `feedback_permission_gate_blocks_cross_review`) is the fallback — still better than no review.
- Public-repo defects (client-identifier leak, LICENSE detection) are the most important class to catch; once they ship to a public repo, MIT/CC-BY licenses on the published content are effectively irrevocable per `project_llm_wiki_privacy_flip`.
- Cross-review findings split cleanly into (a) fix-in-session-before-close and (b) file-as-follow-on. MAJOR public-disclosure / correctness defects go in bucket (a); MINOR architectural debt + nice-to-haves go in bucket (b).
- This pattern is the operational evidence for [[feedback_cross_provider_review_payoff]] applied to single-provider-multi-angle dispatch — Claude-self-review finds different defects than Claude-as-adversarial-subagent.

**Related:**
- [[feedback_cross_provider_review_payoff]] — the broader pattern this reinforces
- [[feedback_adversarial_review_stance]] — every review prompt must force defect-hunting, not charitable reading
- [[feedback_always_adversarial_review_scale_depth]] — never skip; dial depth to scope
- [[feedback_permission_gate_blocks_cross_review]] — single-provider fallback acceptable when full T3 dispatch unavailable
- [[feedback_pre_completion_cleanup_audit_gate]] — cleanup audit + cross-review are the two final gates before close
