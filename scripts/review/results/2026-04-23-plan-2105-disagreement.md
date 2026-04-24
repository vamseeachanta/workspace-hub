# Disagreement report — plan #2105 (2026-04-23)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=2: error: unexpected argument '--no-interactive' found    tip: to pass '--no-interactive' as a value, use '-- --no-interactive'  Usage: codex exec [OPTIONS] [PROMPT]        codex exec [OPTIONS] <COMMAND>) |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **Self-invalidating verdict.** Plan §Adversarial Review Summary line 133 asserts `"Overall result: MAJOR — not approval-ready. Keep this issue in status:plan-review until … rewritten and re-reviewed"`, yet §Risks and Open Questions line 148 claims `"Open: none for plan approval readiness; the remaining work is a bounded consolidation/integration task, not a scope-definition problem."` These two statements, in the same file, are mutually exclusive. The plan is being submitted for review while internally marked not approval-ready.
- **Six "required revisions" documented but never applied to the plan body.** Lines 136–141 enumerate six revisions "now required from review" (threshold collision, Knowledge/Intelligence reclassification with #2207/#2209, source-of-truth precedence, scanner-scope decision, exact registry-field changes, #2250 dependency). None of these propagate into the upstream sections that actually drive execution — §Deliverable, §Pseudocode, §Files to Change, §TDD Test List, §Acceptance Criteria are unchanged. A reviewer reading top-to-bottom sees the plan as un-remediated.
- **Threshold vocabulary collision unresolved in the authoritative sections.** §Acceptance Criteria line 118 still requires `"Threshold semantics (current, warn, stale) and ownership are explicitly defined."` The live scanner at `scripts/docs/staleness-scanner.py:37-124` defines constants `FRESH`, `MODERATE`, `STALE` and emits them into `docs/dashboards/doc-freshness-dashboard.md`. The plan proposes a competing taxonomy without a mapping clause or a migration path. This was flagged by Claude 2026-04-15, Codex 2026-04-14, and the overnight 2026-04-16 review and remains unaddressed in the sections that bind execution.
- **Review-artifact header is stale / incomplete.** Plan frontmatter line 7 lists four review artifacts. A fifth exists at `scripts/review/results/2026-04-16-plan-2105-claude-overnight.md` (verdict `MAJOR (unresolved)`, dated two days after the most recent cited review). Omitting it creates the false impression that the latest review is Claude 2026-04-15, understating the freshness of the MAJOR verdict.
- **Canonical matrix is claimed "locked" but does not exist at HEAD.** §Deliverable line 61 states the plan `"locks docs/document-intelligence/freshness-cadence-matrix.md as the canonical freshness/staleness artifact"`. `ls docs/document-intelligence/` returns no such file. §Files to Change line 91 marks it `Create/Update`. "Locked" is the wrong verb for a file that does not exist yet — reviewers will misread this as already-created. Pick one: either the artifact exists (not true) or the plan proposes to create it (then say so and drop "locks" language).
- **Registry field-change surface under-specified.** §Files to Change line 93 says `"align freshness metadata"` in `intelligence-accessibility-registry.yaml` as an optional update. The registry currently carries `freshness_source` and `freshness_cadence` (grep: lines 39-40, 56-57, …). The plan does not state whether a new field (e.g. `freshness_threshold`, `staleness_label`) is added, whether cadence vocabulary is unified with scanner constants, or whether existing `on-demand / monthly` values remain. Codex and Claude both flagged "exact registry-field changes" as a required revision; plan body still says "(if needed)".
- **Scanner-scope decision deferred into "or" language in Files to Change.** §Files to Change line 94 reads `"scripts/docs/staleness-scanner.py or scripts/cron/staleness-scan-weekly.sh"` with "Update (if needed)." The live scanner walks `docs/` only (markdown-scoped). #2105's intelligence-asset scope includes yaml registries (e.g. `resource-intelligence-maturity.yaml`). The plan neither commits to extending the scanner nor formally defers that work. Three reviewers flagged this; the plan still hides the decision behind "or" and "(if needed)".
- **#2250 dependency missing from §Risks.** §Risks and Open Questions line 147 lists a single risk about distributed freshness logic; #2250 (downstream reconciliation) is not named. It appears only inside the review-summary table at line 131, and only as a review-finding description. Per the required-revisions list (line 141), #2250 must be promoted to an explicit dependency/risk in the active sections.
- **TDD list tests existence, not correctness.** §TDD Test List lines 103–108: five of six tests are "section present" / "fields present" / "referenced" existence checks. The Claude and Codex reviews explicitly call these "text-check heavy rather than behavior-check heavy." There is no falsifiable test for threshold-vocabulary consistency between matrix and scanner, no test for end-to-end cadence application, and no test that the registry's `freshness_cadence` values fall inside the matrix-defined set. Acceptance criteria will pass on an empty skeleton.
- **Knowledge/Intelligence retrieval still absent from the section that matters.** §Resource Intelligence Summary §Documents consulted lines 26–35 does not list #2205, #2207, or #2209 despite two review rounds demanding them. The `project_doc_intel_operating_model` memory already flags #2205 as the parent of this governance family. Required-revision #2 (line 137) says add them; plan §Documents consulted remains unchanged.

### codex

- (none)

### gemini

- Plan §"Existing repo code" claims `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` already includes a freshness/staleness checklist, but no such file exists at HEAD.
- Plan §"Existing repo code" claims `data/document-index/intelligence-accessibility-registry.yaml` already contains per-asset freshness metadata fields, but no such file exists at HEAD.
- Plan §"Existing repo code" claims `config/scheduled-tasks/schedule-tasks.yaml` defines an existing `staleness-scan` scheduled task, but no such file exists at HEAD.
- Plan §"Existing repo code" references `scripts/cron/staleness-scan-weekly.sh` and `scripts/docs/staleness-scanner.py` as existing staleness machinery, but neither file exists at HEAD.
- Plan §"Existing repo code" claims `docs/dashboards/doc-freshness-dashboard.md` already implements part of the freshness machinery, but no such file exists at HEAD.
- Plan §"Existing repo code" claims `docs/document-intelligence/intelligence-accessibility-map.md` documents discoverability, but no such file exists at HEAD.
- Plan §"Existing repo code" claims `data/document-index/resource-intelligence-maturity.yaml` is a canonical freshness-sensitive ledger, but no such file exists at HEAD.
- Plan §"Adversarial Review Summary" explicitly states "Overall result: MAJOR — not approval-ready" and lists five concrete "Revisions now required from review" (e.g., adding #2207 and #2209 evidence, resolving threshold naming collisions, addressing #2250 dependency). However, the plan's §"Deliverable", §"Pseudocode", and §"Acceptance Criteria" sections do not incorporate any of these explicitly required revisions, leaving the implementation path fundamentally disconnected from its own review findings.

