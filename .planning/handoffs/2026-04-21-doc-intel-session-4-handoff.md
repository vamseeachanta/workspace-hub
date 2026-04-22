# Next-Session Prompt — Doc-Intel Continuation (2026-04-21, session 4)

> Paste into a fresh session at `/mnt/local-analysis/workspace-hub` to continue the `#2392` re-file effort. Supersedes `.planning/quick/session-4-entry-prompt.md` as the latest state snapshot for this issue.

---

## One-paragraph context

Session 4 focused almost entirely on reopening and repeatedly hardening the preserved plan for `#2392` (`feat(knowledge): wiki coverage-gap detector — inventory × wiki diff per discipline`). The issue was reopened, the plan was rewritten into a draft re-file, and multiple adversarial review waves were run. The plan improved materially — it now has explicit source-vs-coverage boundaries, canonical status enum, cross-domain handling, duplicate wiki-key handling, supplemental-source field mappings, publication-mode rules, and cleaner GitHub state tracking — but it is still not approval-ready. Latest review state remains `MAJOR`; the blocker set is now narrow and architectural rather than broad.

## Current authoritative issue state

- Issue: `#2392`
- URL: `https://github.com/vamseeachanta/workspace-hub/issues/2392`
- Live state: `OPEN`
- Live labels: `enhancement`, `priority:medium`, `cat:data-pipeline`, `cat:documentation`, `domain:document-intelligence`
- Important negative state: **do not add `status:plan-review` yet**

Latest issue comment already summarizes the current blocker cluster:
- `https://github.com/vamseeachanta/workspace-hub/issues/2392#issuecomment-4290955801`

## Primary files to read first

1. `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md`
2. `scripts/review/results/2026-04-21-v11-plan-2392-codex.md`
3. `scripts/review/results/2026-04-21-v9-plan-2392-gemini.md`
4. `scripts/review/results/2026-04-21-v8-plan-2392-gemini.md`
5. `scripts/review/results/2026-04-20-validation-2405-via-plan-2392-codex.md`
6. `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`

## Durable commits relevant to #2392

Recent relevant commit chain for this issue:
- `30bb4a01c` — `docs(plans): reopen #2392 with v4 review wave`
- `6d9688a58` — `docs(plans): continue #2392 adversarial revision wave`
- `252bcd5e7` — `docs(plans): add #2392 v8 review wave`
- `3b54737d2` — `docs(plans): continue #2392 v9-v11 review wave`
- `41bff2f03` — `docs(plans): continue #2392 v9-v11 review wave`

Note: repository `HEAD` may move due to unrelated auto-sync / other issue work. Use file-specific history, not repo-wide HEAD alone, when resuming #2392.

## What session 4 accomplished

### 1. Reopened the issue and preserved draft mode
- `#2392` was reopened.
- It remains OPEN but intentionally **not** in `status:plan-review`.
- The issue has multiple progress/governance comments documenting each review wave.

### 2. Rewrote the plan into a real re-file draft
Main plan file:
- `docs/plans/2026-04-20-issue-2392-wiki-coverage-gap-detector.md`

Major structural improvements added during this session:
- required vs optional inputs split more clearly
- source-side vs wiki-side vs reporting-only surfaces clarified
- canonical source-record status model introduced and repeatedly tightened
- explicit cross-domain coverage behavior added
- duplicate wiki-key handling added
- supplemental-source field contracts expanded (`standards-transfer-ledger`, `dde-standards-inventory`, `promotions`, `index.jsonl`, `code-registry.yaml`)
- publication-mode behavior, exit-code contract, and scheduled-task contract tightened
- approval rule tightened toward `run_status: clean`

### 3. Ran many adversarial review waves
Fresh review artifacts added during session 4 include:
- `scripts/review/results/2026-04-21-v4-plan-2392-codex.md`
- `scripts/review/results/2026-04-21-v4-plan-2392-gemini.md`
- `scripts/review/results/2026-04-21-v5-plan-2392-codex.md`
- `scripts/review/results/2026-04-21-v5-plan-2392-gemini.md`
- `scripts/review/results/2026-04-21-v6-plan-2392-codex.md`
- `scripts/review/results/2026-04-21-v6-plan-2392-gemini.md`
- `scripts/review/results/2026-04-21-v7-plan-2392-codex.md`
- `scripts/review/results/2026-04-21-v7-plan-2392-gemini.md`
- `scripts/review/results/2026-04-21-v8-plan-2392-codex.md`
- `scripts/review/results/2026-04-21-v8-plan-2392-gemini.md`
- `scripts/review/results/2026-04-21-v9-plan-2392-codex.md`
- `scripts/review/results/2026-04-21-v9-plan-2392-gemini.md`
- `scripts/review/results/2026-04-21-v10-plan-2392-codex.md`
- `scripts/review/results/2026-04-21-v11-plan-2392-codex.md`

Notable asymmetry:
- there is no committed `v10 Gemini` or `v11 Gemini` artifact at present; do not assume they exist.

## Current blocker cluster (authoritative next-work scope)

The issue is now narrowed to this blocker set:

1. Scheduler is not truly single-publisher across the declared machine set.
2. Domain-mapping config schema/precedence still needs a fully normative shape.
3. Dedupe contract still needs an explicit policy for sources that may legitimately map to multiple wiki domains.
4. Publication path still needs a repo-clean guarantee for logs/side effects beyond staged report files.
5. Approval gate still needs attested verification for `data/document-index/index.jsonl`.

This is the right next-pass scope. Do not broaden again.

## Recommended next action in the next session

Do one focused v12 pass on only the 5 blockers above.

### Required edits for the next pass

1. **Single-publisher contract**
   - Choose exactly one publishing host.
   - Either:
     - `machines: [dev-primary]` for publication, with `ace-linux-1` removed from publisher role, or
     - explicitly mark `ace-linux-1` as non-publishing/read-only observer.
   - Do not leave ambiguous multi-machine publication plus local `flock`.

2. **Normative config schema**
   - Define exact schema for:
     - `source_root_domain_map`
     - `design_code_domain_defaults`
     - `wiki_domain_rules`
   - Include matching order, tie-break precedence, normalization rules, and ambiguous-config fail behavior.

3. **Multi-domain source policy**
   - Decide whether one canonical source may legitimately emit multiple domain-scoped candidates.
   - If yes: redesign dedupe contract to dedupe by `(doc_key, domain_slug)` not just `doc_key`.
   - If no: state the invariant explicitly and explain why it holds.

4. **Log cleanliness**
   - Move scheduled logs outside repo dirtiness concerns, OR
   - explicitly require and verify `logs/knowledge/*` is ignored and never affects worktree cleanliness.

5. **Attested evidence for index**
   - Add explicit attested/file-evidence for `data/document-index/index.jsonl` in the plan’s evidence/resource-intel story before calling the approval gate complete.

## Suggested prompt for the next session

```text
Continue #2392 from `.planning/handoffs/2026-04-21-doc-intel-session-4-handoff.md`.

Task: do a single narrow pass only on the 5 remaining blockers listed in that handoff:
1) single-publisher scheduler contract
2) fully normative domain-mapping schema
3) multi-domain source policy
4) log-path cleanliness guarantee
5) attested verification of `data/document-index/index.jsonl`

Do not broaden scope.
Do not add `status:plan-review` unless a fresh adversarial wave comes back non-MAJOR.
After patching, run a fresh adversarial review wave and update #2392.
```

## Important guardrails for the next session

- Do NOT self-label `status:plan-review` prematurely.
- Do NOT reopen broader doc-intel planning scope; stay only on #2392.
- Do NOT assume repo-wide `HEAD` history is only about #2392; other work is happening on main.
- Do NOT assume missing review artifacts exist; verify exact files.
- Keep using explicit-path `git add`; working tree has unrelated drift from other workstreams.

## Repository state note at exit

At the moment of this handoff, repo-wide `main` has unrelated modified/untracked files from other streams. That is normal for this repo. For #2392 continuity, rely on:
- exact plan file path
- exact review artifact paths
- issue comment history
- file-specific git log

Do not use blanket staging.

## Exit status

- `#2392` reopened: yes
- draft plan exists: yes
- multiple adversarial review waves captured: yes
- approval-ready: no
- `status:plan-review` ready: no
- next session start point: clear and narrow
