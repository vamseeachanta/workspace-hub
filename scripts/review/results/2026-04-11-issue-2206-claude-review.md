# Adversarial Review: #2206 Pyramid Conformance Checks

> **Reviewer role:** Adversarial Reviewer (Role 3 of 4-role agent team)
> **Date:** 2026-04-11
> **Artifact:** `docs/document-intelligence/pyramid-conformance-checks.md`
> **Parent contract:** `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (#2205)

---

## Review Criteria

1. Consistency with #2205 parent operating model
2. Clear boundaries with #2207, #2209, #2096, #2208, #2136
3. Whether checks are concrete and testable (not aspirational)
4. Whether the automatable/manual classification is honest
5. Whether the doc avoids scope creep into actual tooling implementation
6. Whether a future implementation agent could build the checks from this design alone

---

## Finding 1: Consistency with #2205

**Verdict: PASS**

The document correctly inherits all parent rules without redefining them:

- Layer definitions from #2205 Section 2 are consumed as check inputs, not re-specified
- The `doc_key` rule from #2205 Section 3 is validated, not redefined
- Allowed and forbidden flows from #2205 Sections 4-5 are mapped to specific checks (FLOW-1 through FLOW-5)
- The child guardrail table from #2205 Section 10 is validated by GUARD-1 through GUARD-5
- The conflict resolution clause correctly defers to the parent model
- The named exceptions (#2205 Section 6) — audit reads across layers — are correctly not flagged as violations

**Specific verification:** The check matrix's 33 checks all trace to specific sections in #2205, #2207, #2209, or #2096 via Appendix A. No check invents a rule not present in a source contract.

---

## Finding 2: Boundary Clarity with Siblings

**Verdict: PASS**

The document explicitly avoids overlapping with sibling issues:

| Sibling | Boundary respected? | Evidence |
|---|---|---|
| #2207 (provenance) | Yes | Checks validate `doc_key` usage but do not define identity rules, provenance fields, or reuse-vs-reparse logic |
| #2209 (boundary) | Yes | Checks validate durable/transient classification but do not define classification rules, promotion criteria, or retention policies |
| #2096 (accessibility) | Yes | Checks validate discoverability links but do not define accessibility ratings, asset inventories, or weekly checklist content |
| #2208 (retrieval) | Yes | No checks reference retrieval contracts or issue-workflow evidence requirements |
| #2136 (registry) | Yes | Checks note that certain validations "require future tooling" from #2136; no registry schemas are defined |
| #2104 (entry points) | Yes | No entry-point page design or navigation structure is defined |

**One observation:** Check FLOW-1 (No L3 reparsing with L2 evidence) overlaps slightly with #2207's anti-pattern AP-1 (duplicate parsing). However, #2207 *defines* the anti-pattern while #2206 *detects* it — this is correct role separation. The check correctly requires pipeline instrumentation that doesn't exist yet and is classified as Phase 4 (future).

---

## Finding 3: Check Concreteness and Testability

**Verdict: PASS with one MINOR observation**

The check matrix provides for each of 33 checks:
- A unique identifier (OWN-1, ID-1, FLOW-1, etc.)
- A stated purpose
- A type classification (automatable/manual, with "now"/"partial"/"future" qualifiers)
- Specific input artifacts
- Explicit pass and fail signals

**Stress test — can an implementation agent build from this design alone?**
- For automatable checks (e.g., DT-1 Wiki frontmatter completeness): Yes. The inputs are file paths, the check logic is "parse YAML frontmatter, verify required fields exist," and the pass/fail signal is binary. An agent could write the script from this specification.
- For manual checks (e.g., GUARD-4 Child scope stays within guardrails): Yes, as a review checklist item. The check criteria are defined in terms of the #2205 Section 10 table, and the review process is described in Section 8.

**MINOR observation:** Check OWN-2 (Registry is not narrative) uses a "> 200 characters in a single value" threshold. This is a reasonable heuristic but the specific number is arbitrary. An implementation agent might ask: "Does a 199-character value pass? What about a YAML multiline string that happens to be long because it contains a list of paths?"

**Recommendation:** The threshold is fine as a starting heuristic. Implementation can tune it based on actual false positive rates. No document change needed, but implementation issues should note this as a tunable parameter.

---

## Finding 4: Automatable/Manual Classification Honesty

**Verdict: PASS**

The document is disciplined about what is truly automatable:

- 18 checks classified as "Automatable (now)" — all are file-existence, field-presence, or keyword-pattern checks that can be implemented as scripts reading existing repo files
- 3 checks classified as "Automatable (partial)" — correctly noting that they work for some cases but not all (e.g., DT-6 silent-promotion detection works via git diff but can't catch all promotion paths)
- 1 check classified as "Automatable (future)" — FLOW-1 correctly notes it requires pipeline instrumentation
- 10 checks classified as "Manual" — all require semantic judgment that cannot be reduced to pattern matching
- 1 check (ID-5) classified as "Automatable (partial)" correctly noting it requires cross-repo access

**Verification of a specific classification:** Check FLOW-2 (Issue not knowledge base) is classified as "Automatable (now)." Is this honest? The check detects "docs citing closed issues as authoritative domain knowledge." This requires:
1. Grep for issue references (`#NNNN` pattern) in docs/wiki files — automatable
2. Check if the referenced issue is closed — requires `gh` API, but available
3. Determine whether the reference is "authoritative citation" vs "historical mention" — this is a judgment call

The check is honestly classified as "Automatable (now)" because the pass signal is "References to closed issues point to promoted wiki pages, not to issue comments" — this can be detected by checking whether the surrounding text points to a wiki page alongside the issue reference. However, it will have some false positives for legitimate historical mentions of closed issues.

**Recommendation:** No change needed. The phased enforcement approach (reporting-only first, then enforcement after tuning) handles false positive risk.

---

## Finding 5: Scope Creep Assessment

**Verdict: PASS**

The document consistently maintains the design-vs-implementation boundary:

- Section 1 explicitly defines the distinction between "check" (validation rule) and implementation (script/hook)
- Section 7 describes "feasible automation surfaces" but does not define scripts, schemas, or CI pipelines
- Section 10 proposes an implementation sequence but frames each phase in terms of what to build, not how to build it
- Section 9 includes CF-6 (scope creep into implementation) as an explicitly named anti-pattern for the check system itself
- No executable code, YAML schemas, or CI configuration is included

**One observation:** Section 7.1 mentions "A single Python or shell script that reads markdown files and checks for..." followed by a bulleted list of check logic. This is close to implementation detail but remains at the "what the script does" level, not "how the script is written." Acceptable as a design specification.

---

## Finding 6: Coverage Completeness

**Verdict: PASS with one MINOR gap**

The document covers all required conformance targets from the prompt:

| Required target | Covered | Check IDs |
|---|---|---|
| Ownership overlap detection | Yes | OWN-1 through OWN-5 |
| Flow-rule drift detection | Yes | FLOW-1 through FLOW-5 |
| Child-issue guardrail drift | Yes | GUARD-1 through GUARD-5 |
| Discoverability/conformance drift | Yes | ACC-1 through ACC-6 |
| Document identity usage | Yes | ID-1 through ID-6 |
| Durable/transient boundary | Yes | DT-1 through DT-7 |

The document also covers required policy/content elements:

| Required element | Present | Section |
|---|---|---|
| At least one check for duplicate ownership | Yes | OWN-5, ID-2 |
| At least one check for path-only identity leakage | Yes | ID-6 |
| At least one check for wiki/provenance boundary violations | Yes | ID-4, FLOW-3, DT-1 |
| At least one check for transient artifact improper promotion | Yes | FLOW-5, DT-6 |
| At least one check for missing cross-links from child to parent | Yes | ACC-3, ACC-4 |

**MINOR gap:** The prompt asks for explicit coverage of "discoverability/conformance drift" — meaning not just current discoverability state but *drift over time*. Check ACC-6 validates the weekly checklist file targets exist (a snapshot check), but there is no check that compares current discoverability state against a baseline to detect *regression* over time.

**Mitigation:** The weekly review process (#2089) already provides the temporal comparison mechanism — each weekly run can compare results against the previous run. The conformance-check design provides the individual snapshot checks; the weekly review provides the trend analysis. This is architecturally correct role separation. No document change needed.

---

## Finding 7: Open Questions Quality

**Verdict: PASS**

The 10 open questions in Section 11 are genuine residuals:

1. False positive rates — cannot be resolved without running the checks
2. Performance at scale — cannot be resolved without benchmarking
3. Cross-repo boundaries — depends on repo management decisions
4. Retention enforcement vs advisory — correctly separates detection from action
5. Check target stability — inherent to any reference-based system
6. Manual check sustainability — depends on weekly review adherence
7. Interaction with cross-review gate — requires coordination, not design
8. Check freshness — correctly notes dependency on parent model stability
9. Phase 4 dependencies — honest about what may not arrive
10. Unified runner — architecture decision for implementation phase

No fake questions. No questions that should have been answered in this document.

---

## Issues Found

### Minor Issues

**M1: Check ID numbering has a gap in anti-pattern mapping.** Section 9.2 maps 12 anti-patterns (AP-1 through AP-12) to checks. This numbering duplicates with #2209's anti-pattern numbering (AP-1 through AP-8). While the document states these are "the pyramid violations that the check matrix targets," the shared numbering could confuse readers.

**Action:** Acceptable as-is — the numbering is internal to this document and each AP entry cites its source rule. No change needed.

**M2: The "most-durable-owner rule" is referenced in Section 4.1 but no check explicitly validates its application.** The ownership invariant (OWN-5) checks single-layer assignment, but the most-durable-owner rule is a *resolution mechanism* for ambiguous cases, not a checkable property.

**Action:** Correct — the most-durable-owner rule is a decision procedure, not a testable invariant. It is applied during artifact classification, not during conformance checking. No check is needed.

### No Major Issues Found

The document is internally consistent, correctly scoped, produces concrete validation targets, and provides a credible implementation path.

---

## Verdict

**APPROVED — no revisions required.**

The conformance-check design:
- Stays within #2206 scope (validation design, not implementation)
- Does not redefine parent or sibling contracts
- Provides 33 concrete checks with explicit pass/fail signals
- Honestly classifies checks as automatable vs manual
- Prioritizes checks by implementation value and feasibility
- Avoids scope creep into CI hooks, registry schemas, or script implementations
- Provides a 4-phase implementation sequence with clear dependencies
- Identifies 10 genuine open questions
- Is directly usable by a future implementation agent

Minor issues noted above are informational and do not require changes.
