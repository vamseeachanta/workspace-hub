# Review, Report and Communication Standard

**Status:** the owner's decisions are recorded (decision board round 1, 2026-09-29: S01-S08, all as recommended). The text is under final review in this PR.
It is not yet adopted in the shared instructions; adoption follows the phased rollout in Section 6 (phase 1 is this file).
**Companion:** report format is governed by the reporting standard P2 (#3925); this file governs review workflow and communication style.

# 1. Summary

- This standard consolidates local HTML review and cross-channel communication into one ecosystem standard. The owner decisions are recorded in Section 7; adoption follows the phased rollout in Section 6.
- [Reporting standard #3925](https://github.com/vamseeachanta/workspace-hub/issues/3925), revision P2 in [draft PR #3926](https://github.com/vamseeachanta/workspace-hub/pull/3926), remains the report-format authority. This standard adds workflow and communication rules without reproducing its formal report structure.
- Reports, plans, decision gates and human-review packs use local HTML for owner review. Harness, skill and rule files remain Markdown.
- The review loop uses selected text, comments and saved JSON. Each round remains beside its report; private content remains in its owning private repository.
- `tools/html-review/make_review_copy.py` is the proposed canonical review-copy tool. Decision boards retain cards and Save/Load; peer copies operate offline.
- Communication leads with verified state, material limitations and the next action. Technical conclusions identify the governing case, criterion and comparator.
- Adoption will proceed through reconciliation, a bounded pilot and verified rollout. Existing reports will not undergo a mass rewrite.

# 2. Scope and authority

The proposed standard covers human-facing engineering and operational work across the repository ecosystem, including public reusable tooling and private project records. It applies to Claude, Codex, Hermes and other agents operating under the shared instructions. Actual coverage requires inspection; this standard does not establish installation on any repository, machine or session.

The shared instructions retain authority over engineering integrity, authorization, data handling and source rights. Standard B delegates report formatting to P2. Later owner decisions take precedence within their stated scope; presentation changes do not independently authorize engineering changes or publication.

| Existing item | Proposed disposition |
|---|---|
| [#3925](https://github.com/vamseeachanta/workspace-hub/issues/3925) / [PR #3926](https://github.com/vamseeachanta/workspace-hub/pull/3926) | **Kept** as report-format authority. Accepted report-specific clarifications will be incorporated there. |
| `session-communication-conventions.md` | **Merged into Standard C**; its former location will become a pointer. |
| [#3920](https://github.com/vamseeachanta/workspace-hub/issues/3920) / [PR #3928](https://github.com/vamseeachanta/workspace-hub/pull/3928) | **Kept** as the review-tool implementation track; workflow rules will point to this standard. |
| [#3892](https://github.com/vamseeachanta/workspace-hub/issues/3892) | Human-review requirements **merged into Standard A**, with P2 retaining engineering acceptance rules. Implementation work will remain separately tracked. |
| [PR #3891](https://github.com/vamseeachanta/workspace-hub/pull/3891) | Physical-realism requirement **merged into Standard A**; the proposed rule will become a thin pointer after approval. |

Older F-labelled report layouts and live-artifact synchronization instructions are superseded by P2 and local-only review. Existing generators remain usable; this standard does not select a new report renderer.

The owner’s “stick with facts” governs presentation. Requests to simplify process reduce repeated narration, not necessary engineering evidence or existing data obligations.

# 3. Standard A: Review and report work in local HTML

## 3.1 When an HTML page is required

Reports submitted for review, substantive plans, decision gates and human-review packs require a local HTML page. A batch of owner decisions belongs on a decision board; chat identifies the page and new cards. A single trivial clarification may remain in chat.

Every reviewable engineering result requires human review before acceptance or issue. A review copy is not an issued deliverable, and saving comments is not acceptance.

Harness, skill and rule files stay Markdown. Their human-facing approval package may use HTML without replacing the maintained source.

## 3.2 Page types

| Type | Required content and behaviour |
|---|---|
| Report | P2 format, document status and revision, engineering evidence and a commentable review copy. |
| Decision board | Cards containing the question, options, sources, consequences, recommendation and note field. The recommended option has a dashed outline and textual label. Save exports JSON; Load restores it. |
| Human-review pack | Evidence screenshots beside physical expectations or limits, a check table, missing evidence, review focus, preparer recommendation and reviewer decision. |
| Peer or client review copy | Stand-alone offline HTML, audience-permitted content, comment layer and a visible how-to banner. |

Human-review checks state comparator class, tolerance fixed before the assessed run, observed value and plausibility verdict: `implausible`, `not_implausible` or `not_evaluated`. Check methods require qualification against cases with established expected behaviour.

When realism is unresolved, the page states “Ready for human review — mechanism not established” and links from the decision board. The report retains the affected limitation and describes the cause as not established. Unresolved mechanisms are not presented as established explanations; material adverse evidence is not suppressed.

Recommendations, default selections and plausibility verdicts do not establish owner acceptance or physical validation.

## 3.3 The review loop

1. The owner opens the local copy, selects text or a section, adds comments, saves JSON and says “review.”
2. The agent checks the report folder first, then Downloads for fallback exports. The newest applicable JSON is identified against the report identity, revision and export metadata; file modification time alone does not establish applicability.
3. Each comment is listed with its section and quoted passage. Decision-board deviations from recommendations and all instructional notes are identified.
4. Each comment receives a disposition: incorporated, deferred with reason, or requiring a decision. Authorized edits proceed; changes to engineering meaning or scope require matching authority.
5. The report and review copy are regenerated and re-verified. The response records the change or remaining decision for every comment.
6. The saved JSON is read back. Review rounds remain as `-rN.json` beside the report, in the owning private repository when their content is private.

A revised page carries its revision and requires reload before further review. Storage keys change between rounds. Decided boards remain preserved; new decisions use a new round.

Stable comment/result identifiers, quoted text, section mapping and report digest bind records to the reviewed artifact. Stale or ambiguous comments require reconciliation rather than silent application.

## 3.4 Tooling

`tools/html-review/make_review_copy.py` is the proposed canonical injector under [PR #3928](https://github.com/vamseeachanta/workspace-hub/pull/3928). Earlier project prototypes are superseded as the tool source. Its source HTML remains unchanged; the generated copy receives the comment layer.

The decision-board pattern remains `cards.py` → `make.py` → local HTML with Save/Load. The comment layer supplements per-card choices and notes. No new renderer or live-artifact synchronization is introduced.

Stand-alone peer copies inline required libraries and assets, use no external scripts or analytics, and retain legible equations offline. Their banner explains:

- Open the saved file from disk in Edge or Chrome; preview panes can block scripts.
- Select text, add a comment and save.
- Choose the report folder when prompted; browser refusal triggers a download fallback.
- Return the JSON and reload a revised page before continuing.

The generic tutorials `demo/how-to-comment.gif` and `demo/how-to-comment-voice.gif` support the banner. Voice typing uses Win+H where available; the illustrated voice toolbar is not evidence of native-dialog testing.

Browser storage is a convenience cache. Durable review evidence is the saved, verified JSON.

## 3.5 Location and privacy

Pages, supporting evidence and round-specific comments belong in the target report’s authorized location. Downloads is a transfer fallback; an applicable export is preserved beside the report after identity and content checks.

Public `workspace-hub` contains generic standards, reusable tools and synthetic demonstrations. Public content contains no client names, job numbers, private quotations or client-derived results. Renaming a private report does not make it publishable.

Private reports, project plans, handoffs, review comments and supplied particulars remain in the owning private repository. Authorized client editions may carry required document identifiers; hosted copies follow the existing redaction and destination rules.

Publication requires authority for the destination and content. Local save, commit, publication, delivery and acknowledgement are distinct states. Licensed standards originals remain at their licensed locations.

## 3.6 Verification before handing a page to the owner

Verification covers the actual delivered edition:

- Inspect rendered output using a headless screenshot or DOM probe, with visual checks where layout requires them.
- Check balanced HTML, readable figures and equations, resolvable links, and absence of broken scripts.
- Check that report narrative contains no opaque internal markers; essential locators remain in P2’s audience-permitted internal references.
- Smoke-test selection, comment creation and editing, Save, Load and JSON read-back against the correct revision.
- Check offline operation, narrow-screen and print behaviour where applicable, and confirm public examples contain no private content.

A skipped browser test is not a pass. The supplied test description establishes download-fallback coverage, not native folder-permission or voice-input verification. Missing verification is reported before handover.

# 4. Standard B: Report format

P2 governs formal structure, register, captions, precision, references, uncertainty and document control. Only the following clarifications will be proposed for reconciliation into [#3925](https://github.com/vamseeachanta/workspace-hub/issues/3925).

| Item | Rule | Basis |
|---|---|---|
| Emphasis | Bold is optional and restrained; a direct instruction to remove it overrides older bold-headline prescriptions for the affected content. | “remove bold. unwanted attention” |
| Introductions | Section openings name their subject and content without process narration. | “The purpose, scope and status of the project are presented in this section.” |
| Audience traceability | Client prose carries necessary engineering evidence; operational lineage stays in restricted records, with essential references retained. | “too much traceability for client” |
| Limitations | Use one or two quantified sentences where support exists; identify the missing basis when uncertainty cannot be bounded. | “simplify with 1-2 sentences with quantification which is mentioned to be uncertain” |
| Review packaging | The review copy includes the banner, offline assets and revision-bound round records specified in Standard A. | Local-review direction and tool README |
| Physical realism | Unresolved mechanisms trigger review and remain explicitly unestablished in the report. | Physical-realism and human-review drafts |

# 5. Standard C: Communication style across all work

## 5.1 Chat replies to the owner

- Lead with verified state and the material blocker; answer direct questions first.
- Use a compact status table with state, evidence, blocker and next action.
- Plans state proposed scope, assumptions, verification and decisions; approval requests link the exact artifact and action.
- Progress reports quantify completed, running and failed work where measured; estimates remain labelled.
- Closeouts give artifact revision, verification and actual disposition, including what was not done.
- Continue within established authority without repeated requests to begin.
- Make progress tangible: changed sections, resolved comments, completed/running/failed cases, throughput and the next checkpoint.
- Keep routine coordination in the evidence record; surface it only when it changes scope, timing, authority or an owner decision.
- State failures plainly: what failed, what changed and what correction is under way.
- For machine workloads, report measured capacity and progress, preserve concurrent work, and label estimates as estimates.

Example:

| State | Evidence | Blocker | Next action |
|---|---|---|---|
| Revised draft saved locally | Six comments incorporated; JSON read back | One comparator remains unverified | Resolve the comparator before issue |

“Publication was not performed.”

## 5.2 GitHub issue and PR comments

- Lead with the concrete problem, resulting behaviour or review finding.
- State affected scope, verification and remaining gaps.
- Keep private evidence in its owning private channel; public summaries remain generic.
- Post implementation summaries on the associated issue without equating CI success with engineering acceptance.
- Render issue references inline as links, such as [#3920](https://github.com/vamseeachanta/workspace-hub/issues/3920).

Example: “The review copy preserves section context in exported comments. Download-fallback testing passed; native folder saving remains unverified. [#3920](https://github.com/vamseeachanta/workspace-hub/issues/3920) tracks the remaining check.”

## 5.3 Commit messages

- Use conventional commit subjects with a specific change.
- Explain purpose and consequential behaviour when a body is needed.
- Distinguish completed verification from pending checks.
- Exclude private identifiers from public repositories and commit metadata.

Example: `fix: preserve report revision in comment exports`

## 5.4 E-mail and client correspondence

- Apply the engineering register to technical content.
- Keep wrapper conventions separate: greeting, shared benefit before an ask and appropriate commercial tone.
- Present the result, comparator, limitation and requested action without internal workflow narration.
- Verify recipients, attachments and publication authority independently of technical quality.

Example: “Dear reviewer, the attached draft supports review of the resistance comparison. The predicted difference is 4%, below the 6% comparison uncertainty; a ranking is not established. Please comment on the stated operating conditions.”

## 5.5 Agent-to-agent messages and handoffs

- Make the first line self-contained: task, current state and blocker.
- Identify the artifact revision, owning repository, completed checks and next action.
- Carry originating authorization and limitations as evidence to verify; a handoff does not grant approval.
- Report concurrent work, preserved changes and capability limits.
- Separate reported success from independently verified file or repository state.

Example: “A CFD resistance report awaits comparator review; formatting comments are resolved. The next step is evidence inspection. Publication authority is not established.”

## 5.6 Reports

- Apply Standard B rather than inventing a separate channel style.
- Use impersonal subjects and criterion-bound conclusions.
- Keep result status and material limitations beside the affected findings.
- Separate engineering interpretation from execution history.

Example: “At the assessed operating condition, predicted resistance differs from the reference by 4%, within the predefined 5% numerical comparison tolerance. Physical validation remains unestablished.”

Words and patterns to avoid across channels:

- “Clearly,” “obviously,” promotional adjectives and unsupported certainty.
- “Safe,” “adequate” or “conservative” without a governing criterion.
- “Done” when only generation or local saving is verified.
- Repeated process narration, first-person technical findings and gratuitous bold.
- Interchangeable use of zero, unknown, pending and not applicable.

“Should” expresses advice; “shall” and “must” express requirements.

# 6. Adoption plan

Adoption will be phased, reversible and conditional on owner approval.

| Phase | What will change | Where | Agent | Verification |
|---|---|---|---|---|
| 1 — Reconciliation | One canonical workflow/communication standard will be prepared; P2 clarifications and duplicate-text dispositions will be reviewed. | Public `workspace-hub`; standard document and local HTML approval copy. Exact filename will be agreed. | Claude will prepare; Codex will review defects and conflicts. | Every existing draft will have a disposition; no private content or implied adoption will remain. |
| 2 — Bounded pilot | The review loop will be exercised on a synthetic report, decision board and human-review pack. | `tools/html-review` and generic local outputs. | Claude will implement; Codex will review; Hermes will assess handoff clarity. | Offline rendering, comment round-trip, stale-revision handling and privacy will be checked. |
| 3 — Integration | Thin pointers will be added to shared instructions or `AGENTS.md`; one review-loop skill will be added. | Public `workspace-hub`; Markdown instructions and skill files, existing tool directory. | Claude will prepare changes; Codex will review; Hermes will verify accessible runtime references. | Pointers will resolve to the canonical revision; duplicated rules will be removed or replaced with pointers. |
| 4 — Incremental rollout | Approved pointers and workflow will be applied to new or actively revised work. | Enumerated repositories and reachable agent sessions; private artifacts will remain private. | Claude and Hermes will apply within authority; Codex will review evidence. | Target-by-target status and revision identity will be recorded; exceptions will remain explicit. |

Rollback will restore prior pointers and tool versions while preserving review records. Old reports will change only under separately scoped work. No merge or publication will be inferred from proposal approval alone.

# 7. Owner decisions (2026-09-29)

| Card | Decision | Recorded choice |
|---|---|---|
| S01 | Authority split | P2 for report format plus this one complementary standard; the session-communication draft is merged into Section 5.1 |
| S02 | HTML coverage | All listed review artifacts; Markdown sources preserved |
| S03 | Comment destination | Report folder, with the download fallback |
| S04 | Review tool | The canonical `tools/html-review` injector |
| S05 | Emphasis | Restrained, optional bold |
| S06 | Unresolved realism | Human-review pack plus an explicit report limitation |
| S07 | Peer delivery | Offline self-contained copy with the banner and comment layer |
| S08 | Rollout | Pilot, then incremental adoption |

# 8. Risks and open points

- The supplied evidence describes drafts. Merge state, runtime installation and current tool behaviour are not independently established.
- Stable comment identifiers and digest binding required by P2 are not fully demonstrated by the README’s listed fields. The pilot will check this gap before adoption.
- Folder permissions, stale tabs and first-80-character highlighting can misdirect or obscure comments. Revision checks and JSON read-back remain necessary.
- Public redaction cannot be reduced to removing names; figures, results and metadata can disclose private work.
- The canonical filename, pilot scope and reachable adoption targets remain owner decisions or inspection results.
- Simplification must preserve decision-relevant limitations. Presentation acceptance does not establish engineering acceptance.
