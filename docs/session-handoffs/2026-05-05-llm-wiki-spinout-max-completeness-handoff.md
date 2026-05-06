# Handoff: llm-wiki spinout — maximize practical wiki completeness

Date: 2026-05-05
Source session: Hermes / workspace-hub
Primary repos:
- `vamseeachanta/llm-wiki` — public spinout repo for wiki artifacts/content/issues
- `vamseeachanta/workspace-hub` — control plane, pipeline scripts, planning docs, document-index/intelligence

## Why this handoff exists

The llm-wiki artifact store was spun out from `workspace-hub` into the public repository `vamseeachanta/llm-wiki`. Relevant wiki-content GitHub issues were transferred to the new repo. Another session should now start from the spinout repo and set a goal to achieve as much llm-wiki completeness as practically possible with current model capabilities, without violating raw-data or plan-approval boundaries.

## Verified current state

`vamseeachanta/llm-wiki`:
- URL: https://github.com/vamseeachanta/llm-wiki
- Public repo
- Default branch: `main`
- Issues enabled
- Not archived
- Description: `Engineering knowledge wikis — multi-domain corpus extracted from public engineering standards. Spun out from workspace-hub 2026-05-05.`

Authoritative spinout tracker:
- `workspace-hub#2647`: https://github.com/vamseeachanta/workspace-hub/issues/2647
- Relocation summary comment: https://github.com/vamseeachanta/workspace-hub/issues/2647#issuecomment-4383561339

New llm-wiki roadmap umbrella:
- `llm-wiki#13`: https://github.com/vamseeachanta/llm-wiki/issues/13
- Relocation summary comment: https://github.com/vamseeachanta/llm-wiki/issues/13#issuecomment-4383561522

## Relocated issue map

The following issues were transferred from `workspace-hub` to `llm-wiki` and verified open:

| Old `workspace-hub` | New `llm-wiki` |
|---:|---:|
| #2390 | #13 |
| #2541 | #14 |
| #2631 | #15 |
| #2637 | #16 |
| #2638 | #17 |
| #2639 | #18 |
| #2644 | #19 |
| #2629 | #20 |
| #2630 | #21 |
| #2368 | #22 |
| #2360 | #23 |
| #2522 | #24 |
| #2364 | #25 |
| #2373 | #26 |
| #2388 | #27 |
| #2378 | #28 |
| #2372 | #29 |
| #2371 | #30 |
| #2365 | #31 |
| #2010 | #32 |
| #51 | #33 |
| #2039 | #34 |
| #2044 | #35 |
| #2011 | #36 |
| #2366 | #37 |
| #2375 | #38 |
| #2042 | #39 |

Important currently approval-ready / plan-review issues in `llm-wiki`:
- `llm-wiki#14` — curated SESA LNG corpus extraction from Elements
- `llm-wiki#15` — standards-routing for maritime-law / lng-projects / acma-projects
- `llm-wiki#16` — engineering classification-society entity pages
- `llm-wiki#17` — marine-engineering P1 standards/concept backfill
- `llm-wiki#18` — marine-engineering P2 platform/entity overview refresh
- `llm-wiki#19` — offshore raw-source-family wiki backfill candidates from `/mnt/ace-data`

Important working / plan-approved issues in `llm-wiki`:
- `llm-wiki#22` — faceted portal pages for large LLM-wiki domains
- `llm-wiki#25` — Batch Pack 1 API/standards-portal metadata promotion
- `llm-wiki#26` — Batch Pack 4 non-ACMA standards summary promotion

Important harness/scorecard issue:
- `llm-wiki#37` — llm-wiki strengthening scorecard and prioritized action queue

## Stay-behind workspace-hub issues

These should generally remain in `workspace-hub` unless further review proves their primary deliverable is wiki artifact content:

- `workspace-hub#2643` — metadata-only `/mnt/ace-data` raw-like source coverage triage; status `plan-review`.
- `workspace-hub#2632` — rebind stuck approval markers; status `plan-review`.
- `workspace-hub#2392` — inventory × wiki diff detector.
- `workspace-hub#2647` — spinout tracking / heads-up.
- `workspace-hub#2650` — post-spinout cleanup.
- Likely harness/control-plane/integration: `#2040`, `#2067`, `#2068`, `#2103`, `#2123`, `#2124`, `#2125`, `#2141`, `#2293`, `#2363`, `#2370`, `#2374`, `#2382`, `#2484`, `#2485`.

## Raw-data and governance boundaries

Do not violate these:

1. Raw data stays in `/mnt/ace` / `/mnt/ace-data`.
2. `llm-wiki`/git receive only approved summaries, metadata, wiki pages, indices, and source-record links.
3. `/mnt/ace-data/raw data` literal path was missing; `/mnt/ace-data` resolves to `/mnt/ace`.
4. Metadata-only raw-like coverage planning was created as `workspace-hub#2643`; offshore wiki candidate follow-up moved to `llm-wiki#19`.
5. Stop at `status:plan-review` unless the user explicitly approves.
6. Do not self-approve or add approval markers.
7. Future llm-wiki content issues should be filed in `vamseeachanta/llm-wiki` after duplicate checks. Pipeline/control-plane issues stay in `workspace-hub`.
8. All GitHub issue bodies/comments with Markdown must use `--body-file`.
9. Do not edit `knowledge/wikis/` or `knowledge/seeds/` in `workspace-hub`; they were moved/are unstable under spinout cleanup.

## Future GH issue guidance

No additional future GH issues were created in this exit handoff because `llm-wiki#13` and `llm-wiki#37` already provide durable roadmap/scorecard anchors, while multiple scoped transferred issues are already open. The next session should create new issues only after checking `llm-wiki#13`, `llm-wiki#37`, and open issues `#14`–`#39` for duplicates.

If the next session finds true uncovered work, create issues directly in `vamseeachanta/llm-wiki`, with:

```bash
gh issue create \
  --repo vamseeachanta/llm-wiki \
  --title '<bounded title>' \
  --label 'status:needs-plan' \
  --label 'llm-wiki' \
  --body-file /tmp/<issue-body>.md
```

Recommended new-issue criteria:
- one issue per bounded domain/completion family;
- do not create broad duplicate epics while `llm-wiki#13` exists;
- add dependency links to `llm-wiki#13` in the body;
- if the work depends on metadata-only `/mnt/ace-data` routing, backlink `workspace-hub#2643`;
- if the work changes pipeline/control-plane tooling, file in `workspace-hub`, not `llm-wiki`.

## Copy/paste handoff prompt for next session

Use this prompt to start another session:

```text
You are working on the public spinout repo `vamseeachanta/llm-wiki`.

Goal: set up and drive the next bounded goal to make the llm-wiki corpus as complete as practically possible with current model capabilities, while preserving raw-data, public-repo, and plan-approval boundaries.

Start by loading relevant skills: research/llm-wiki, coordination/llm-wiki-roadmap-integration, github/github-issue-lifecycle-operations, and any repo/handoff/planning skills that apply.

Primary repo and issue anchors:
- `vamseeachanta/llm-wiki`: https://github.com/vamseeachanta/llm-wiki
- Roadmap umbrella: `llm-wiki#13` — https://github.com/vamseeachanta/llm-wiki/issues/13
- Strengthening scorecard/action queue: `llm-wiki#37` — https://github.com/vamseeachanta/llm-wiki/issues/37
- Spinout tracker in control-plane repo: `workspace-hub#2647` — https://github.com/vamseeachanta/workspace-hub/issues/2647
- Metadata-only raw-source triage in control-plane repo: `workspace-hub#2643` — https://github.com/vamseeachanta/workspace-hub/issues/2643

First actions:
1. Inspect `vamseeachanta/llm-wiki` repo state, branch, labels, and issue list.
2. Read `llm-wiki#13` and `llm-wiki#37` before creating anything.
3. Review transferred open issues `llm-wiki#14`–`#39`, especially plan-review issues `#14`–`#19` and working/plan-approved issues `#22`, `#25`, `#26`.
4. Confirm whether the repo contains current wiki artifacts, seeds, cross-links, and tests after the spinout cleanup.
5. Build a completion scorecard: domains, current pages, source pages, cross-link/index status, known gaps, and priority order.
6. Identify the highest-leverage next bounded goal. Prefer using or updating an existing issue over creating duplicates.
7. If a true new gap exists, create a new GitHub issue in `vamseeachanta/llm-wiki` using `--body-file`, label it `status:needs-plan`, and link it to `llm-wiki#13`. Do not file wiki-content issues in `workspace-hub`.
8. If the work is pipeline/control-plane/document-index routing, create or update the relevant `workspace-hub` issue instead.
9. Draft or update canonical plans to `status:plan-review` only; never self-approve and never move anything to `status:plan-approved` without explicit user approval.

Critical boundaries:
- Raw data stays in `/mnt/ace` / `/mnt/ace-data`; do not copy/promote raw content into git/wiki without separate approval per gap.
- The literal path `/mnt/ace-data/raw data` was missing; `/mnt/ace-data` resolves to `/mnt/ace`.
- Use metadata/summaries/source-record links only unless a specific deep extraction has been approved.
- Use `--body-file` for all GitHub issue bodies/comments.
- Do not edit old `workspace-hub/knowledge/wikis` or `workspace-hub/knowledge/seeds` content unless spinout cleanup explicitly says it is safe.

Transferred issue map to keep in mind:
`workspace-hub#2390 -> llm-wiki#13`, `#2541 -> #14`, `#2631 -> #15`, `#2637 -> #16`, `#2638 -> #17`, `#2639 -> #18`, `#2644 -> #19`, `#2629 -> #20`, `#2630 -> #21`, `#2368 -> #22`, `#2360 -> #23`, `#2522 -> #24`, `#2364 -> #25`, `#2373 -> #26`, `#2388 -> #27`, `#2378 -> #28`, `#2372 -> #29`, `#2371 -> #30`, `#2365 -> #31`, `#2010 -> #32`, `#51 -> #33`, `#2039 -> #34`, `#2044 -> #35`, `#2011 -> #36`, `#2366 -> #37`, `#2375 -> #38`, `#2042 -> #39`.

Deliverable for the session:
- A concise completion status report for `llm-wiki`.
- A prioritized next-goal recommendation tied to existing issue(s) where possible.
- Any truly missing future GitHub issues created in `vamseeachanta/llm-wiki` with body-file safety and duplicate checks.
- If planning work is done, stop at `status:plan-review` and report the approval queue to the user.
```

## Exit status

This handoff is docs-only. It does not create new GH issues by itself. It prepares the next session to create future issues only after dedupe against the new `llm-wiki` issue portfolio.
