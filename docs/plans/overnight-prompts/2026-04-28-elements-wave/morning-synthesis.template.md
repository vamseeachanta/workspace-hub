# Morning synthesis — overnight Elements planning wave (YYYY-MM-DD)

> **Wave:** 2026-04-28-elements-wave (umbrella [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540))
> **Synthesis run:** YYYY-MM-DDTHH:MM:SSZ
> **Author:** main session (do NOT delegate this synthesis to a subagent — approval-readiness is a user-in-loop call)

> Use this as a copy-on-write template. Replace each `<...>` placeholder. Do not delete unanswered sections — leave a `BLOCKED:` note instead.

---

## 1. Stream results review

For each stream, read the result summary and confirm the artifacts exist on disk and in the latest `origin/main`.

| Stream | Issue | Result file | Plan file | Intel artifacts | All paths exist? |
|---|---|---|---|---|---|
| sesa-lng | [#2541](https://github.com/vamseeachanta/workspace-hub/issues/2541) | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-1-sesa.md` | `docs/plans/2026-04-28-issue-2541-elements-sesa-curated-extraction-plan.md` | `.planning/intel/elements-overnight-wave/sesa-*` | YES / NO |
| doris-university | [#2542](https://github.com/vamseeachanta/workspace-hub/issues/2542) | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-2-doris-university.md` | `docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md` | `.planning/intel/elements-overnight-wave/doris-university-*` | YES / NO |
| doris-codes | [#2543](https://github.com/vamseeachanta/workspace-hub/issues/2543) | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-3-doris-codes.md` | `docs/plans/2026-04-28-issue-2543-elements-doris-codes-standards-plan.md` | `.planning/intel/elements-overnight-wave/doris-codes-*` | YES / NO |
| woodfibre-lng | [#2544](https://github.com/vamseeachanta/workspace-hub/issues/2544) | `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-4-woodfibre.md` | `docs/plans/2026-04-28-issue-2544-elements-woodfibre-scout-plan.md` | `.planning/intel/elements-overnight-wave/woodfibre-*` | YES / NO |

### Per-stream evidence

For each stream copy the result-file's "Files written" table and verify with `test -s <path>`.

```bash
test -s <result-path>
test -s <plan-path>
test -s <dossier-path>
test -s <tsv-path>
```

### Boundary-violation check

Run these guards before approving anything:

```bash
git diff --name-only origin/main..HEAD | grep -E '^/mnt/ace/' && echo "VIOLATION: /mnt/ace write" || echo "OK: no /mnt/ace writes"
git diff --name-only origin/main..HEAD | grep -E '^knowledge/wikis/.+/raw/' && echo "VIOLATION: raw bulk into wiki" || echo "OK: no raw wiki writes"
gh issue view 2540 --json labels | grep '"name": "status:plan-approved"' && echo "VIOLATION: umbrella self-approved" || echo "OK: umbrella not self-approved"
for n in 2541 2542 2543 2544; do
  gh issue view $n --json labels --jq '.labels[].name' | grep -q 'status:plan-approved' \
    && echo "VIOLATION: #$n self-approved overnight" \
    || echo "OK: #$n not self-approved"
done
```

---

## 2. Approval-readiness assessment

Each stream advances to one of: `approval-candidate`, `needs-rereview`, `blocked`, `redo`.

| Stream | Codex verdict | Gemini verdict | Claude verdict | Synthesis | Recommendation |
|---|---|---|---|---|---|
| sesa-lng | <APPROVE / MINOR / MAJOR> | <verdict> | <verdict> | <one-line> | approval-candidate / needs-rereview / blocked / redo |
| doris-university | <verdict> | <verdict> | <verdict> | <one-line> | <recommendation> |
| doris-codes | <verdict> | <verdict> | <verdict> | <one-line> | <recommendation> |
| woodfibre-lng | <verdict> | <verdict> | <verdict> | <one-line> | <recommendation> |

Hardening criteria checklist (must be satisfied before any `approval-candidate`):

- [ ] No persisted full-text dump in `.planning/`, `docs/`, or git
- [ ] Standards-namespace contract honored ([#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) frontmatter, [#2482](https://github.com/vamseeachanta/workspace-hub/issues/2482) deny-list)
- [ ] Confidentiality / clearance gates explicit where applicable (SESA, Woodfibre)
- [ ] `lng-projects` index/log contention noted if both SESA and Woodfibre are on the candidate list
- [ ] No `status:plan-approved` label currently applied to any child issue

---

## 3. Blocked-item list

List items requiring user input or external clearance before they can advance. Do not advance any blocked item without explicit user action.

| Item | Stream | Why blocked | Required action | Owner |
|---|---|---|---|---|
| <blocker> | <stream> | <reason> | <e.g., user clearance, external review> | <user / external> |

If empty, write `(no blockers — all streams ready for next gate)`.

---

## 4. Next-execution recommendation

Recommend the *single* next bounded action and order any candidate sequencing:

1. **First action:** <e.g., user-approve a bounded subset of streams X+Y for execution>
2. **Sequencing:** <e.g., #2543 first (independent), #2542 second, #2541 third (with clearance), #2544 last (pointer-only)>
3. **Sequential vs parallel:** <flag any shared-write contention, e.g., `lng-projects` index/log between SESA and Woodfibre>
4. **Cleanup gate:** [#2534](https://github.com/vamseeachanta/workspace-hub/issues/2534) retention remains blocked until 2026-05-28; do NOT bundle cleanup with extraction approval.

---

## 5. Approval-not-given confirmation

This synthesis does NOT label any issue `status:plan-approved`. Approval requires the user, separately, after reviewing this synthesis and the underlying plans. Subagents and batch agents must NOT self-approve.

---

## 6. Synthesis sign-off

- Synthesis author: <main-session-runner>
- Synthesis commit: <SHA after this file is committed>
- Umbrella comment posted: <link to #2540 comment summarizing this synthesis>
