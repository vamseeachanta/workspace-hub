# Plan for #2208: Require Intelligence Retrieval Contract in GitHub Issue Planning/Execution/Review

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2208
> **Review artifacts:** scripts/review/results/2026-04-11-plan-2208-claude.md | scripts/review/results/2026-04-11-plan-2208-final.md

---

## Resource Intelligence Summary

### Existing workflow/governance artifacts consulted

| Artifact | Path | Current retrieval requirements | Gap for #2208 |
|---|---|---|---|
| Plan template | `docs/plans/_template-issue-plan.md` | Has "Resource Intelligence Summary" section — free-form, no minimum sources, no evidence format | No required sub-sections, no minimum source count, no verification checkboxes |
| Plans README / workflow | `docs/plans/README.md` | Step 2 says "search all available sources" with 4 bullet points (code, standards, documents, prior plans) | No issue-class differentiation, no evidence placement rules, no measurable checks |
| Engineering issue workflow | `docs/standards/engineering-issue-workflow-skill.md` | Step 2 has detailed 4-part search order (repo code → standards → documents → reference data) | Only applies to engineering-critical issues; no equivalent for doc/harness/knowledge issues |
| Weekly review template | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | Section D checks intelligence accessibility generically | Does not verify that individual issues actually consumed intelligence during their lifecycle |
| Hard-stop policy | `docs/standards/HARD-STOP-POLICY.md` | Requires plan approval before implementation | Does not gate on retrieval evidence quality |

### Parent/sibling artifacts consulted

| Artifact | Issue | Status | Key takeaways for #2208 |
|---|---|---|---|
| Parent operating model | #2205 | Normative | Section 4: L3+L2 feed L5 as evidence. Section 5: L5 must not become durable knowledge. Section 9: #2208 is "child workflow contract" defining how L5 consumes L2/L3. Section 10: #2208 may implement "retrieval hooks for issue planning/execution/review, evidence requirements" but must NOT redefine provenance schema, pyramid ownership, or `doc_key` definition. |
| Provenance contract | #2207 | Normative | Defines `doc_key` identity, reuse-vs-reparse rules, required provenance fields. #2208 must reference provenance outputs (summaries, extractions) as consultable intelligence but must not redefine identity or provenance mechanics. |
| Boundary policy | #2209 | Normative | Section 4.2: Plans and review artifacts are transient (L5). Section 6.1: L3→L5 flow is "evidence consumption" — issue planning reads wikis and registries as evidence. Section 6.2: forbidden to make issues the durable knowledge base. Section 7: promotion criteria for when issue findings become durable knowledge. |
| Accessibility map | #2096 | Normative | Section 5: inventories 26+ assets across 3 discoverability tiers. Section 6: identifies 9 broken/weak patterns. Section 7: weekly checklist for accessibility. Provides the concrete asset inventory that the retrieval contract can reference. |
| Entry points plan | #2104 | Plan-review | Designs 3-tier navigation (docs/README.md → doc-intel/README.md → domain pages). Section on boundaries: "How issue workflows programmatically consume intelligence during planning/execution is #2208's scope." The entry points are the navigation surface; #2208 defines the consumption protocol. |
| Accessibility registry plan | #2136 | Plan-review | Designs `intelligence-accessibility-registry.yaml` with `asset_key`, `query_command`, `machine_scope` fields. Section on boundaries: "Workflow retrieval hooks consuming registry" is #2208's scope. The registry is the lookup surface; #2208 defines what must be looked up and when. |

### LLM Wiki pages consulted

- No existing wiki pages directly address the retrieval contract concept.
- `knowledge/wikis/engineering/wiki/index.md` — verified as one of the intelligence assets that would be consulted under the contract.

### Gaps identified

1. **No minimum retrieval requirement.** The current plan template and workflow docs say "search" but never define what "enough" looks like. An agent can write an empty Resource Intelligence Summary and still pass review.
2. **No issue-class differentiation.** The engineering workflow skill defines retrieval for engineering issues only. Documentation, harness, knowledge, and data-pipeline issues have no retrieval guidance at all.
3. **No evidence placement rules.** There is no specification for where retrieval evidence must appear in plans, review artifacts, or GitHub comments. Evidence is scattered or absent.
4. **No measurable checks.** There is no scorecard, checkbox, or automated test that verifies whether intelligence was actually retrieved and used.
5. **No review-time retrieval verification.** Adversarial reviewers do not currently check whether the plan's Resource Intelligence Summary is adequate. Review templates have no "retrieval adequacy" assessment.
6. **No closeout promotion trigger.** The workflow does not require post-implementation identification of findings worth promoting from L5 to L3.
7. **No progressive dependency on #2104/#2136.** The current workflow cannot consume the entry points or registry because neither exists yet. The contract must work with today's file paths and improve as those siblings deliver.

---

## Current Retrieval Expectations and Gaps

### What exists today

The planning workflow (docs/plans/README.md) defines a 9-step process. Step 2 ("Resource Intelligence") says:

> Before writing anything, search all available sources:
> - Existing code: search relevant repos for prior implementations
> - Standards: `standards-transfer-ledger.yaml`
> - Documents: `online-resource-registry.yaml`
> - Prior plans: `docs/plans/` directory and this index

The engineering-issue-workflow skill extends this for engineering-critical issues with a 4-part search order (repo code → standards coverage → document intelligence → reference data).

The plan template (`_template-issue-plan.md`) includes a "Resource Intelligence Summary" section with sub-headings for existing code, standards, wiki pages, documents, and gaps.

### What is missing (the gap this contract fills)

| Gap | Impact |
|---|---|
| No minimum source count or required sources per issue class | Agents skip retrieval entirely or write placeholder text |
| No definition of "adequate" evidence | Reviewers cannot assess retrieval quality |
| No requirement for evidence in review artifacts | Adversarial reviews miss retrieval failures |
| No requirement for evidence in GitHub comments | Issue history has no record of what intelligence was consumed |
| No measurable compliance check | No way to audit whether retrieval discipline is improving |
| No closeout promotion step | Valuable findings decay in transient L5 artifacts |
| No progressive consumption of #2104/#2136 deliverables | As entry points and registry land, the workflow cannot auto-adopt them |

---

## Proposed Retrieval Contract by Workflow Stage

### Stage 1: INTAKE

**When:** Step 1 of the planning workflow — first contact with the issue.

**Minimum retrieval:**

| Source | Applies to | What to capture |
|---|---|---|
| Issue body | All issues | Scope, acceptance criteria, references, parent/related issues |
| Related/parent issues | All issues with `Related:` or `Parent:` references | Titles, statuses, key decisions — enough to understand context without re-reading each fully |
| Issue labels | All issues | Classify the issue into an issue class (see Section below) for retrieval bundle selection |

**Evidence placement:** None required at intake — this is input gathering for the planning stage.

### Stage 2: PLANNING (Resource Intelligence)

**When:** Step 2-3 of the planning workflow — before and during plan writing.

**This is the primary retrieval stage.** The agent must consult the minimum retrieval bundle for the issue's class (see next section) and record what was found in the plan's Resource Intelligence Summary.

**Minimum retrieval (ALL issues, regardless of class):**

| Source | What to look for | Required evidence in plan |
|---|---|---|
| Prior plans in `docs/plans/` | Related plans, prior attempts at similar work | List plans consulted, or state "no related plans found" |
| Existing code in affected paths | Whether this is new work or extends existing implementation | List file paths found, or state "no existing implementation" |
| Recent issue history | Related open/closed issues that may overlap or conflict | List issue numbers consulted |
| Intelligence entry points | Consult `docs/document-intelligence/README.md` (when available per #2104) or `docs/document-intelligence/data-intelligence-map.md` for relevant assets | Note which intelligence assets were checked |

**Evidence format in the plan:**

The plan's "Resource Intelligence Summary" section must contain at minimum:

1. A sub-section listing **each source consulted** with file path or reference
2. For each source: a one-line finding ("Found X", "Confirmed no existing Y", "Standard Z has gap status")
3. A "Gaps identified" sub-section listing what must be built from scratch
4. Total consulted sources must be ≥3 (issue body counts as 1)

### Stage 3: EXECUTION

**When:** Step 5 of the planning workflow — during TDD implementation.

**Minimum retrieval:**

| Source | What to look for | Required evidence |
|---|---|---|
| Approved plan | Re-read the plan before implementing — verify assumptions still hold | No separate evidence needed; the plan is the contract |
| Intelligence cited in plan | If the plan cited specific wiki pages, standards, or registry entries as design inputs, re-verify they haven't changed since planning | Note any discrepancies in commit messages or implementation comments |

**Evidence placement:** Implementation deviations from cited intelligence should be noted in the PR description or commit message. No separate artifact required.

### Stage 4: REVIEW (Adversarial + Cross-Review)

**When:** Step 4 and Step 6 of the planning workflow — adversarial review of the plan, and cross-review of the implementation.

**Reviewer retrieval requirements:**

| Check | What the reviewer must verify | Required in review artifact |
|---|---|---|
| Retrieval adequacy | Is the Resource Intelligence Summary non-empty, with ≥3 consulted sources? | A "Retrieval Adequacy" line: `adequate` / `insufficient` with specific gaps noted |
| Source relevance | Are the consulted sources appropriate for this issue class? | Note if obvious sources were missed (e.g., standards issue that didn't check the ledger) |
| Evidence specificity | Does the plan cite specific file paths, findings, and gap statements — not just "searched the repo"? | Note vague or placeholder evidence |

**Evidence placement in review artifacts:**

Review files (`scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md`) must include a "Retrieval Adequacy" assessment section. This is a new section — existing review artifacts do not currently contain it.

### Stage 5: CLOSEOUT

**When:** Step 7-8 of the planning workflow — commit, close, and post-implementation summary.

**Minimum retrieval:**

| Source | What to capture | Required evidence |
|---|---|---|
| Intelligence consumed during this issue | Which intelligence assets (wiki pages, standards, registries, prior plans) materially informed the implementation? | GitHub close comment must include a "Sources consumed" list (≥1 item) |
| Promotion candidates | Were any findings produced during this issue that deserve promotion from L5 (transient) to L3 (durable knowledge)? Per #2209 Section 7, promotion requires: reusability, verification, non-redundancy, source traceability, stability. **Prompt:** "Ask: did this issue produce any finding that would help future issues or wiki readers?" | GitHub close comment should note "Promotion candidates: none" or list specific findings with suggested target (wiki page, registry entry) |

**Evidence placement:** GitHub issue close comment.

---

## Proposed Minimum Retrieval Bundles by Issue Class

### Issue class definitions

| Issue class | Matching labels or triggers | Description |
|---|---|---|
| **General** | Any issue without a more specific class match | Default — code changes, bug fixes, config updates |
| **Engineering** | `cat:engineering`, `cat:engineering-calculations`, `cat:engineering-methodology` | Offshore/structural/marine engineering calculations, standards implementation |
| **Data Pipeline** | `cat:data-pipeline` | Document intelligence pipeline, extraction, indexing |
| **Documentation** | `cat:documentation` | Docs, governance, skills, workflow definitions |
| **Harness/Infrastructure** | `cat:harness` | Agent harness config, hooks, enforcement, CI/CD |
| **Knowledge/Intelligence** | Issues under #2205 tree, or touching `knowledge/`, `docs/document-intelligence/` | LLM-wikis, registries, intelligence architecture |

**Default classification rule:** If an issue has no labels or labels do not match any specific class, default to **General**. If an issue matches multiple classes (e.g., has both `cat:engineering` and `cat:documentation`), use the **union** of all matching class bundles — consulting extra sources is never wrong.

### Minimum retrieval bundles

Each bundle specifies the **additional** sources that must be consulted beyond the universal minimum (prior plans, existing code, recent issues, intelligence entry points).

| Issue class | Additional required sources | Rationale |
|---|---|---|
| **General** | None beyond universal minimum | Default class — universal retrieval is sufficient |
| **Engineering** | `data/document-index/standards-transfer-ledger.yaml` (for relevant standard status); `data/design-codes/code-registry.yaml` (for applicable design codes); relevant domain wiki under `knowledge/wikis/` (for existing domain knowledge); `data/document-index/online-resource-registry.yaml` (for online references) | Engineering issues risk re-implementing what standards already cover or duplicating existing wiki knowledge |
| **Data Pipeline** | `data/document-index/registry.yaml` (aggregate stats); pipeline config at `scripts/data/document-index/config.yaml`; `data/document-index/resource-intelligence-maturity.yaml` (maturity state) | Pipeline changes must account for current state and maturity metrics |
| **Documentation** | Existing governance docs in target directory; `docs/standards/CONTROL_PLANE_CONTRACT.md`; `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (#2209) for classification guidance | Documentation changes must respect governance structure and boundary policy |
| **Harness/Infrastructure** | `docs/standards/CONTROL_PLANE_CONTRACT.md`; relevant `config/agents/` settings; `.claude/rules/` or equivalent for current rules | Harness changes must align with control-plane contract and existing rules |
| **Knowledge/Intelligence** | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (#2205); relevant sibling contracts (#2207, #2209); `docs/document-intelligence/intelligence-accessibility-map.md` (#2096); `data/document-index/intelligence-accessibility-registry.yaml` (when available per #2136) | Intelligence-ecosystem issues must operate within the parent architecture and account for sibling contracts |

### Progressive adoption of #2104 and #2136

The retrieval bundles above reference existing file paths that work today. As sibling issues deliver:

| When available | How the contract adapts |
|---|---|
| **#2104 lands** (canonical entry points) | "Intelligence entry points" in the universal minimum becomes: "Start at `docs/document-intelligence/README.md` for navigation to relevant intelligence assets." Replaces ad-hoc file path knowledge. |
| **#2136 lands** (accessibility registry) | Knowledge/Intelligence bundle adds: "Query `data/document-index/intelligence-accessibility-registry.yaml` for `asset_key` matching the issue domain." Agents can look up `query_command` and `machine_scope` for each asset. |
| **Neither available yet** | The contract works with current file paths. Agents consult `docs/document-intelligence/data-intelligence-map.md` or specific files directly. |

---

## Required Evidence Placement in Plan/Review/GitHub Artifacts

### In plan files (`docs/plans/YYYY-MM-DD-issue-NNN-slug.md`)

The "Resource Intelligence Summary" section must contain:

| Required sub-section | Content | Verifiable? |
|---|---|---|
| **Existing repo code** | File paths checked with findings, or "no existing implementation" | Yes — paths can be verified |
| **Standards** (if engineering class) | Standards checked with status from ledger, or "not applicable" | Yes — ledger entries can be verified |
| **LLM Wiki pages consulted** | Wiki page paths checked, or "no relevant wiki pages" | Yes — paths can be verified |
| **Documents consulted** | Prior plans, registries, governance docs checked | Yes — paths can be verified |
| **Gaps identified** | What must be built from scratch | Yes — gaps are testable claims |

Minimum: ≥3 distinct sources listed across all sub-sections (issue body + 2 others).

### In review artifacts (`scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md`)

New required section:

```markdown
## Retrieval Adequacy

| Check | Result | Notes |
|---|---|---|
| Resource Intelligence Summary non-empty | yes/no | |
| ≥3 sources consulted | yes/no | count: N |
| Issue-class-specific sources checked | yes/no | class: X, missing: Y |
| Evidence is specific (file paths, not vague claims) | yes/no | |
| Gaps section present and specific | yes/no | |

**Retrieval verdict:** adequate / insufficient
```

### In GitHub issue comments

**Plan-review comment** (posted when applying `status:plan-review`):
- Must include a "Sources consulted" summary line listing the key intelligence assets checked (≤5 items).

**Close comment** (posted when closing the issue):
- Must include a "Sources consumed" line listing intelligence assets that materially informed the implementation.
- Must include a "Promotion candidates" line: "none" or a list of findings worth promoting to L3 with suggested targets.

---

## Measurable Checks / Scorecard Ideas

### Per-plan checks (can be run at plan-review time)

| # | Check | Pass condition | Enforcement level |
|---|---|---|---|
| RC-1 | Resource Intelligence Summary is non-empty | Section exists and contains ≥1 sub-section with content | Template (today) → linter (future) |
| RC-2 | Minimum source count met | ≥3 distinct sources cited (file paths, issue refs, or registry entries) | Template (today) → script (future) |
| RC-3 | Issue-class-specific sources checked | Each required source for the issue class is addressed (found or "not applicable") | Checklist in plan (today) → automated (future) |
| RC-4 | Evidence is specific | At least one concrete file path, function name, or registry entry cited | Review-time (today) → linter (future) |
| RC-5 | Gaps section present | "Gaps identified" sub-section exists and is non-empty | Template (today) → linter (future) |

### Per-review checks (new section in review artifacts)

| # | Check | Pass condition | Enforcement level |
|---|---|---|---|
| RR-1 | Retrieval Adequacy section present | Review artifact contains "Retrieval Adequacy" heading | Template (today) |
| RR-2 | Retrieval verdict stated | Review contains `adequate` or `insufficient` with reasoning | Template (today) |
| RR-3 | Missing sources flagged | If issue-class sources were missed, reviewer notes them | Convention (today) |

### Per-close checks (closeout verification)

| # | Check | Pass condition | Enforcement level |
|---|---|---|---|
| RCL-1 | Sources consumed listed | Close comment contains ≥1 intelligence source cited | Convention (today) → script (future) |
| RCL-2 | Promotion candidates assessed | Close comment contains "Promotion candidates" line | Convention (today) |

### Aggregate scorecard (for weekly review Section D)

| Metric | How to measure | Target |
|---|---|---|
| Plans with non-empty Resource Intelligence Summary | Count plans in `docs/plans/` with non-empty RIS / total plans | 100% |
| Plans meeting minimum source count (≥3) | Audit recent plans for source count | ≥90% |
| Review artifacts with Retrieval Adequacy section | Count reviews with RA section / total reviews | ≥80% (ramp-up) |
| Close comments with Sources consumed | Audit recent close comments | ≥80% (ramp-up) |

---

## Separation of Discovery Registries, Synthesis Wikis, and Execution State

This contract reinforces the parent model's (#2205) layer separation:

| Layer | Role in retrieval | What the retrieval contract requires |
|---|---|---|
| **L2 — Registry/provenance** | Inventory and identity lookup — "what documents exist, where are they, what's been extracted" | Agents consult registries to find relevant intelligence assets. The contract specifies which registries to check per issue class. Registries are read, not modified, during issue execution. |
| **L3 — Durable knowledge (wikis)** | Synthesized domain understanding — "what does the ecosystem know about this topic" | Agents consult wiki pages for domain context. The contract requires citing wiki pages in the Resource Intelligence Summary when relevant. Wikis are read during execution; findings may be promoted back after closeout. |
| **L4 — Entry points** | Navigation surfaces — "where to start looking" | The contract specifies entry points as the first stop (when available via #2104). Entry points are navigational, not content sources. |
| **L5 — Execution state** | The issue/plan/review lifecycle itself | The contract governs what evidence must appear in L5 artifacts. L5 artifacts are transient per #2209 — they consume L2/L3 intelligence but do not become the durable record of that intelligence. |

**Key rule:** The retrieval contract defines *consumption from L2/L3 into L5*. It does not define *promotion from L5 back to L3* — that is governed by #2209 Section 7. The contract only requires that closeout comments identify promotion candidates; the actual promotion process follows #2209 rules.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md` |
| Plan review — Claude | `scripts/review/results/2026-04-11-plan-2208-claude.md` |
| Plan review — Final | `scripts/review/results/2026-04-11-plan-2208-final.md` |
| **Implementation targets (deferred):** | |
| Plan template update | `docs/plans/_template-issue-plan.md` — tighten Resource Intelligence Summary with required sub-sections and minimum source count |
| Review template creation/update | Review artifact template — add Retrieval Adequacy section |
| Plans README update | `docs/plans/README.md` — update Step 2 with issue-class retrieval bundles |
| Engineering workflow skill update | `docs/standards/engineering-issue-workflow-skill.md` — align with the contract's engineering bundle |
| Issue-planning-mode skill update | `.claude/skills/coordination/issue-planning-mode/SKILL.md` — add retrieval verification step |
| Weekly review Section D enhancement | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — add aggregate retrieval scorecard checks |

---

## Deliverable

A formal intelligence retrieval contract that defines — per workflow stage and issue class — the minimum intelligence sources that must be consulted before planning proceeds, where retrieval evidence must appear in plan/review/GitHub artifacts, and measurable checks for retrieval compliance, all grounded in the #2205 parent operating model and consistent with sibling contracts #2207, #2209, #2096, #2104, and #2136.

---

## Pseudocode / Workflow Logic Sketch

### Retrieval decision logic at planning time

```
function determine_retrieval_bundle(issue):
    # Stage 1: Intake classification
    class = classify_issue(issue.labels, issue.body, issue.paths)
    
    # Stage 2: Assemble retrieval bundle
    bundle = UNIVERSAL_MINIMUM.copy()
    #  UNIVERSAL_MINIMUM = [
    #    "prior plans in docs/plans/",
    #    "existing code in affected paths",
    #    "recent related issues",
    #    "intelligence entry points (docs/document-intelligence/README.md or data-intelligence-map.md)"
    #  ]
    
    if class in CLASS_SPECIFIC_BUNDLES:
        bundle.extend(CLASS_SPECIFIC_BUNDLES[class])
    
    # Progressive: if #2136 registry exists, add registry lookup
    if file_exists("data/document-index/intelligence-accessibility-registry.yaml"):
        bundle.append("query accessibility registry for matching asset_keys")
    
    return bundle

function execute_retrieval(bundle):
    evidence = []
    for source in bundle:
        result = consult(source)  # read file, search code, check registry
        evidence.append({
            "source": source.path,
            "finding": result.summary or "not found / not applicable"
        })
    return evidence

function write_resource_intelligence_summary(evidence):
    # Must contain:
    # - ≥3 distinct sources
    # - Specific file paths or references (not vague claims)
    # - Gaps identified section
    assert len(evidence) >= 3
    for item in evidence:
        assert item.source is not None  # must cite a path
        assert item.finding is not None  # must state what was found
    return format_as_plan_section(evidence)
```

### Retrieval adequacy check at review time

```
function check_retrieval_adequacy(plan, issue_class):
    ris = plan.resource_intelligence_summary
    
    checks = {
        "RC-1: RIS non-empty": ris is not None and len(ris.sources) > 0,
        "RC-2: ≥3 sources": len(ris.sources) >= 3,
        "RC-3: class-specific": all(
            required_source in ris.sources
            for required_source in CLASS_SPECIFIC_BUNDLES.get(issue_class, [])
        ),
        "RC-4: specific evidence": any(
            "/" in source.path  # contains a file path
            for source in ris.sources
        ),
        "RC-5: gaps present": ris.gaps is not None and len(ris.gaps) > 0,
    }
    
    verdict = "adequate" if all(checks.values()) else "insufficient"
    return verdict, checks
```

### Closeout evidence logic

```
function write_closeout_comment(issue, implementation_result):
    sources_consumed = [
        source for source in plan.resource_intelligence_summary.sources
        if source was materially used during implementation
    ]
    
    promotion_candidates = identify_promotion_candidates(
        implementation_result.findings,
        criteria=#2209_section_7  # reusability, verification, non-redundancy, traceability, stability
    )
    
    comment = format_close_comment(
        summary=implementation_result.summary,
        sources_consumed=sources_consumed,  # ≥1 required
        promotion_candidates=promotion_candidates or "none"
    )
    
    post_to_github(issue, comment)
```

---

## Files to Change (Planning Scope Only)

These are the implementation targets. **None of these changes should be made during planning.**

| Action | Path | Reason |
|---|---|---|
| **Modify** | `docs/plans/_template-issue-plan.md` | Tighten Resource Intelligence Summary: add required sub-sections, minimum source count note, issue-class guidance |
| **Modify** | `docs/plans/README.md` | Update Step 2 with issue-class retrieval bundles and evidence requirements; add this plan to index |
| **Modify** | `docs/standards/engineering-issue-workflow-skill.md` | Align Step 2 with the contract's engineering-class bundle; add evidence format requirements |
| **Modify** | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Add retrieval verification checkpoint: after Resource Intelligence Summary is written, verify minimum source count and class-specific sources before proceeding to plan draft |
| **Modify** | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | Add retrieval compliance aggregate checks to Section D |
| **Create** | Review artifact template update (or convention document) | Define the Retrieval Adequacy section format for review artifacts |
| **Update** | `docs/plans/README.md` | Add this plan to the index |

### Likely future implementation surfaces (separate from this issue)

| Surface | Owner issue | Relationship |
|---|---|---|
| Automated retrieval-completeness linter | Future issue or #2206 | Script that parses plan files and checks RC-1 through RC-5 |
| Pre-plan-review gate checking retrieval evidence | Future issue | Hook or script that blocks `status:plan-review` if Resource Intelligence Summary fails checks |
| Registry-powered retrieval (programmatic lookup) | #2136 + future issue | When the accessibility registry exists, retrieval bundles can be assembled by querying `asset_key` values |
| Entry-point-guided retrieval | #2104 + future issue | When canonical entry points exist, the universal minimum changes to "start at the intelligence landing page" |
| Closeout promotion automation | #2209 follow-on | Automated identification of L5→L3 promotion candidates during issue closure |

---

## TDD / Verification List for Future Implementation

Since this is a contract/documentation issue (not code), verification is template-based and convention-based:

| Check | What it verifies | Method |
|---|---|---|
| Plan template has tightened RIS section | Minimum source count and sub-sections are documented | Grep for "≥3 sources" or equivalent in template |
| Plans README Step 2 updated | Issue-class retrieval bundles are documented | Grep for "issue class" or "retrieval bundle" in README |
| Engineering workflow aligned | Step 2 references the contract's engineering bundle | Grep for "retrieval contract" or "minimum retrieval" in skill |
| Issue-planning-mode skill has retrieval checkpoint | Skill mentions retrieval verification before proceeding | Grep for "retrieval" or "RC-" checks in skill |
| Review artifacts have Retrieval Adequacy section | New reviews contain the RA table | Grep recent review files for "Retrieval Adequacy" heading |
| Close comments have Sources consumed | Recent close comments contain the required line | Manual audit of recent issue closures |
| Weekly review Section D has retrieval scorecard | Template includes aggregate retrieval metrics | Grep for "retrieval compliance" in weekly review template |
| Contract consistent with #2205 | Layer consumption rules match parent model | Manual comparison |
| Contract does not redefine #2207 | No provenance schema or `doc_key` redefinition | Manual review |
| Contract does not redefine #2209 | No boundary policy or promotion rule changes | Manual review |

---

## Acceptance Criteria

- [ ] Retrieval contract defines minimum retrieval requirements per workflow stage (intake, planning, execution, review, closeout)
- [ ] Issue classes are defined with matching labels/triggers
- [ ] Minimum retrieval bundles are specified per issue class (general, engineering, data-pipeline, documentation, harness, knowledge/intelligence)
- [ ] Evidence placement rules specify exactly where retrieval evidence must appear in plan files, review artifacts, and GitHub comments
- [ ] Measurable checks (RC-1 through RC-5, RR-1 through RR-3, RCL-1 through RCL-2) are defined with pass conditions and enforcement levels
- [ ] Separation of discovery registries (L2), synthesis wikis (L3), and execution state (L5) is explicit and consistent with #2205
- [ ] Progressive adoption path for #2104 (entry points) and #2136 (registry) is defined without blocking on them
- [ ] Follow-on implementation changes are listed with owner issues
- [ ] Contract does NOT redefine provenance schema (#2207), pyramid ownership (#2205), or boundary policy (#2209)
- [ ] Plan index updated in `docs/plans/README.md`
- [ ] Review artifacts posted to `scripts/review/results/`
- [ ] Summary comment posted to GitHub issue #2208

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self-review) | APPROVE with MINOR notes | See `scripts/review/results/2026-04-11-plan-2208-claude.md` |

**Overall result:** PASS — plan is review-ready

Revisions made based on review:
- Added explicit "default to General if classification is ambiguous" rule and "union of bundles for multi-class issues" in the main contract body (was only in Risks)
- Added concrete promotion prompt ("Ask: did this issue produce any finding that would help future issues or wiki readers?") to the closeout stage

---

## Risks and Open Questions

1. **Risk: Template changes alone may not enforce compliance.** The plan template can require sub-sections, but agents can still write minimal placeholder text. Until automated linting exists, enforcement relies on reviewer discipline. Mitigation: the Retrieval Adequacy section in review artifacts creates a second checkpoint.

2. **Risk: Issue-class classification may be ambiguous.** Some issues may match multiple classes (e.g., an engineering issue that also involves documentation). Mitigation: the contract defines class precedence — if an issue has engineering labels, use the engineering bundle even if it also has documentation labels. The bundles are additive, so consulting extra sources is never wrong.

3. **Risk: Minimum source count (≥3) may be too low or too high.** For T1 trivial issues, even 3 sources may feel excessive. For T3 complex issues, 3 may be insufficient. Mitigation: the count is a floor, not a ceiling. T1 issues can satisfy with: issue body + existing code search + prior plans check. T3 issues will naturally consult more sources. Adjust the floor based on experience.

4. **Open: Should the close comment "Sources consumed" be a formal template section or free-form?** Recommendation: start as a convention (free-form line in close comments) and promote to a structured template if audit shows inconsistency.

5. **Open: How should multi-class issues be handled?** Recommendation: union of all matching class bundles. An issue with both `cat:engineering` and `cat:documentation` must satisfy both the engineering and documentation bundles.

6. **Boundary: #2104 (entry points).** This contract references `docs/document-intelligence/README.md` as a future entry point. Until #2104 creates it, agents fall back to `docs/document-intelligence/data-intelligence-map.md` or individual file paths. No blocking dependency.

7. **Boundary: #2136 (registry).** This contract references `intelligence-accessibility-registry.yaml` as a future lookup surface. Until #2136 creates it, agents consult specific file paths listed in the class bundles. No blocking dependency.

8. **Boundary: Automated enforcement.** This contract defines what must happen and how to check it. It does NOT implement hooks, linters, or gate scripts. Automated enforcement is a follow-on concern for #2206 or a future issue.

9. **What should remain out of scope?** (a) Provenance schema changes — owned by #2207. (b) Boundary policy changes — owned by #2209. (c) Entry-point page design — owned by #2104. (d) Registry schema — owned by #2136. (e) Conformance validation scripts — owned by #2206. (f) Hook/gate implementation — future enforcement issue.

---

## Complexity: T2

**T2** — Multiple documentation files modified (plan template, plans README, engineering workflow skill, issue-planning-mode skill, weekly review template). No code changes. Requires careful coordination with 6 sibling/parent issues. Not T1 because it defines a new contract affecting the core planning workflow. Not T3 because the changes are documentation/template-only with no multi-module code architecture.
