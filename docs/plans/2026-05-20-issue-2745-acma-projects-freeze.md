# Plan for #2745: freeze acma-projects and move to local-only archive posture

> **Status:** draft (r1 + r2 review applied; r2-codex MAJOR resolved inline)
> **Complexity:** T2
> **Date:** 2026-05-20
> **Revision history:**
> - 2026-05-20 r1-claude — MAJOR (95% disk vs 85% trigger); resolved by scoping backup disposition out + filing [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769)
> - 2026-05-20 r2-codex — MAJOR; 7 blockers resolved inline: (1) missing guard/checker (issue acceptance requirement), (2) missing execution-stage adversarial review task, (3) backup-unchanged verification underspecified, (4) STATUS-FROZEN.md contradicts scope (backup-disposition section), (5) STATUS-FROZEN.md dangling "revisit criteria below" pointer, (6) missing legal-sanity scan task, (7) push-block test ordering after archive could give false-success; also: (8) #2746 completion gate not concretely verifiable, (9) missing "check parallel work" precondition
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2745
> **Paired plan:** [`docs/plans/2026-05-20-issue-2746-llm-wiki-acma.md`](2026-05-20-issue-2746-llm-wiki-acma.md)
> **Brainstorming spec:** [`docs/governance/2026-05-20-client-llm-wiki-feature-and-acma-instance-design.md`](../governance/2026-05-20-client-llm-wiki-feature-and-acma-instance-design.md) (commit `277a855ee`)
> **Review artifacts:** `scripts/review/results/2026-05-20-plan-2745-claude.md` | `...-codex.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `vamseeachanta/acma-projects` — PRIVATE GitHub remote, ~2 GB on GH, **not archived**, last pushed 2026-05-05; default branch `main`; description "Share high level project data and action lists"
- Found: `/mnt/ace/acma-projects/` — 73 GB git-tracked local working copy; remote = origin = `vamseeachanta/acma-projects`; HEAD at `105c9ce8 chore(B1528): add SIROCCO moored-current PDF report` per session-start fetch
- Found: `/mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928/` — 1.8 TB pre-move backup created today; contains `31522-woodfibre-lng/` and likely other client project subdirectories (full inventory deferred)
- Found: `gh repo archive` subcommand available (confirmed by `gh --help` 2026-05-20)
- Gap: no `STATUS-FROZEN.md` exists in `/mnt/ace/acma-projects/` to declare frozen posture
- Gap: no formal freeze documentation on the working copy

### Standards
Not applicable (operational/data-pipeline issue; no engineering calculation standards).

### LLM Wiki pages consulted
No relevant pages.

### Documents consulted
- `docs/governance/2026-05-20-client-llm-wiki-feature-and-acma-instance-design.md` §5.2 — freeze depth chosen: archive GH remote + keep local 1.8 TB; 3 options for backup disposition
- Parent epic [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) — "acma-projects is a mash-bash of selected project data and should stop receiving new data"
- Paired plan [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) — creates the private llm-wiki successor target
- [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) D3 — raw/client/source/bulk data stays under `/mnt/ace/<bucket>/` (canonical; the freeze preserves this)
- Adjacent [#2767](https://github.com/vamseeachanta/workspace-hub/issues/2767) — chore(data-layout): unionise preexisting data folders with content dedup; opened today; may generalize the 1.8 TB disposition pattern across clients (out of scope here)
- `feedback_autosync_silent_pusher` — auto-sync may push silently; verify reflog after `[rejected]` instead of retrying
- `feedback_admin_flag_vs_rulesets_api` — `gh repo archive` should work; `--admin` flag pattern not needed for archive operation
- `feedback_pre_completion_cleanup_audit_gate` — run cleanup audit before declaring complete

### Gaps identified
- GH remote not archived (must be done)
- `STATUS-FROZEN.md` doesn't exist (must be created with freeze-rationale + revisit criteria)
- 1.8 TB backup disposition not decided (this plan picks option A — retain with revisit criteria)
- Local repo `origin` may or may not need push-permission removal (belt-and-suspenders; this plan adds it)

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-20T18:30Z via `gh issue view`):
- `#2744` — OPEN — parent epic
- `#2745` — OPEN, `status:needs-plan` — this issue
- `#2746` — OPEN, `status:needs-plan` — paired plan target

**GH remote state** (`gh repo view vamseeachanta/acma-projects` 2026-05-20T18:30Z):
- visibility: PRIVATE; isArchived: false; pushedAt: 2026-05-05T10:08:38Z; diskUsage: 2048971 KB

**Local repo state** (`git log --oneline -3` in `/mnt/ace/acma-projects/` 2026-05-20T18:30Z):
- `105c9ce8 chore(B1528): add SIROCCO moored-current PDF report`
- `99cd4072 chore(B1528): refresh SIROCCO time-trace PDF (regenerated 2026-05-04)`
- `cf4d5a62 chore(sync): track durable agent/codex configs and B1528 SIROCCO PDF`

**Backup directory state** (`du -sh` 2026-05-20T12:50Z):
- `/mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928/`: 1.8 TB

## Artifact Map

### New files in `vamseeachanta/acma-projects` (separate repo, post-archive)
| Path | Purpose |
|---|---|
| `STATUS-FROZEN.md` | Declares frozen posture, freeze date, revisit criteria, link to successor `vamseeachanta/llm-wiki-acma` |

### Local-only configuration change
| Path | Operation | Purpose |
|---|---|---|
| `/mnt/ace/acma-projects/.git/config` | Modify `remote.origin.url` → push-disabled URL (or `remote.origin.pushurl` → `no_push`) | Belt-and-suspenders against accidental local push |

### No workspace-hub artifacts modified
This plan touches only the external repo `vamseeachanta/acma-projects` and local FS state. No `workspace-hub` files are created or modified.

### Backup disposition (deferred to dedicated issue)

**Scoped OUT of this plan** following the 2026-05-20 r1 adversarial review (MAJOR finding: `/mnt/ace` already at 95% disk usage when this plan was drafted, exceeding the originally-documented 85% revisit trigger).

The 1.8 TB pre-move backup `/mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928/` is **retained AS-IS by this plan**, with disposition planning deferred to [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769). This plan's only obligation toward the backup is to leave it untouched (verified in T6).

## Deliverable

`vamseeachanta/acma-projects` GH remote archived (read-only). Local working copy `/mnt/ace/acma-projects/` preserved as read-mostly archive with declared frozen status. The adjacent 1.8 TB pre-move backup is untouched; its disposition is deferred to [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769).

## Scope Boundaries

**IN scope:**
- Archive `vamseeachanta/acma-projects` on GitHub (reversible)
- Write `STATUS-FROZEN.md` in the local working copy with freeze rationale + successor pointer (no backup-disposition content)
- Configure local `remote.origin.pushurl` to no-push as belt-and-suspenders
- Commit the `STATUS-FROZEN.md` to `vamseeachanta/acma-projects` BEFORE archiving (so it's visible on the now-frozen GH remote)
- Verify the 1.8 TB pre-move backup is untouched (T6) — disposition planning is [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769)'s scope, not this plan's

**OUT of scope:**
- Deleting any file from `/mnt/ace/acma-projects/` (raw data preserved)
- Compressing or moving the 73 GB working copy
- **Disposition (retain/tar/delete) of the 1.8 TB pre-move backup** — deferred to [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769) (separate plan-gated decision under the standard hard gate; 95% disk pressure makes this a near-term decision but not part of this freeze plan)
- Cross-client generalization of the freeze pattern — that's [#2767](https://github.com/vamseeachanta/workspace-hub/issues/2767)'s scope
- Importing any content from `/mnt/ace/acma-projects/` into `vamseeachanta/llm-wiki-acma` — that's a post-[#2747](https://github.com/vamseeachanta/workspace-hub/issues/2747) operation
- Renaming or deleting the GH remote (archive is reversible; deletion is not)

## Patch Shape

| Task | Files | Net LOC | Repo/Location |
|---|---|---|---|
| T0 — Parallel-work precondition check | 0 | n/a | runtime (pgrep, hermes sessions) |
| T0.5 — Backup pre-snapshot (file count + top-dir listing) | 2 tmp files | n/a | local FS |
| T1 — RED: verify pre-state | 0 | n/a | local FS + GH check |
| T2 — Write STATUS-FROZEN.md (GREEN) | 1 new file | ~50 | `vamseeachanta/acma-projects` repo |
| T3 — Commit + push STATUS-FROZEN.md | n/a | n/a | `vamseeachanta/acma-projects` repo |
| T4 — Local push-disable + verify push-blocked (re-ordered BEFORE archive) | `.git/config` mod | ~2 | `/mnt/ace/acma-projects/` |
| T5 — Add freeze pre-commit hook | `.git/hooks/pre-commit` | ~8 | `/mnt/ace/acma-projects/` |
| T6 — Archive GH remote | 0 | n/a | GitHub API |
| T7 — Verification + strict backup-unchanged diff | 0 | n/a | runtime |
| T8 — Legal-sanity scan | 0 | n/a | scripts/legal/legal-sanity-scan.sh |
| T9 — Execution-stage adversarial review (T2) | 2 review artifacts | ~250 | `scripts/review/results/` |
| T10 — Concrete #2746 state check + comment + close | n/a | n/a | GitHub |

## Pseudocode

### `STATUS-FROZEN.md` content (verbatim core)

```markdown
# STATUS: FROZEN (read-only archive)

> **Frozen:** 2026-05-20 (per workspace-hub #2745)
> **Successor target:** `vamseeachanta/llm-wiki-acma` (private; per workspace-hub #2746)
> **Successor type:** curated private llm-wiki layer for client work

## Why this repo is frozen

Per the workspace-hub data-cycle epic (#2744), `acma-projects` was a mixed-data repo
that should stop receiving new data. New client knowledge work now flows through
the structured pipeline:

  raw source (/mnt/ace/acma-projects/) → readable derivative → private wiki
  (vamseeachanta/llm-wiki-acma) → reviewed/sanitized derivative → public llm-wiki
  (if appropriate)

See `vamseeachanta/llm-wiki-acma/DATA-CYCLE.md` for the full contract.

## What this means

- **No new commits** should land on this repo's `main` branch.
- The GitHub remote is **archived** (read-only on GitHub).
- The local working copy at `/mnt/ace/acma-projects/` is **read-mostly**:
  - Existing files preserved as historical archive
  - `remote.origin.pushurl` set to `no_push` to prevent accidental push
- The adjacent pre-move backup directory `/mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928/`
  is **untouched** by this freeze. Disposition planning is workspace-hub#2769's
  scope, NOT this freeze's. See [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769) for the disposition decision and any
  revisit criteria.

## Reversal

This freeze is reversible:
- `gh repo unarchive vamseeachanta/acma-projects` reactivates the GH remote
- Edit local `.git/config` to restore push permissions
- Update or delete this file with a new STATUS-* declaration

## Successor

For new ACMA client knowledge work, use:
- `vamseeachanta/llm-wiki-acma` (PRIVATE; per workspace-hub #2746 / #2744)
- Local working clone at `/mnt/local-analysis/llm-wiki-acma/`
```

### Local push-disable (`.git/config` modification)

```bash
cd /mnt/ace/acma-projects
git config --local remote.origin.pushurl "no_push://vamseeachanta/acma-projects (frozen per workspace-hub#2745)"
# Verify:
git config --local --get remote.origin.pushurl
git config --local --get remote.origin.url   # fetch URL stays intact
```

### GH archive command

```bash
gh repo archive vamseeachanta/acma-projects --yes
# Verify:
gh repo view vamseeachanta/acma-projects --json isArchived,pushedAt -q '"archived=" + (.isArchived|tostring) + " pushedAt=" + .pushedAt'
# Expect: archived=true
```

## Files to Change

### Tasks (TDD-ordered; "test" here is verify-state since this is operational, not code)

**T1 — Verify pre-state (RED equivalent)**
- Check `STATUS-FROZEN.md` does NOT exist in `/mnt/ace/acma-projects/`:
  - `[[ ! -f /mnt/ace/acma-projects/STATUS-FROZEN.md ]] && echo "RED: absent (expected)"`
- Check GH remote NOT archived:
  - `gh repo view vamseeachanta/acma-projects --json isArchived -q .isArchived` → `false`
- Check local push permission still active:
  - `git -C /mnt/ace/acma-projects config --local --get remote.origin.pushurl` → empty/error (no pushurl override set)

**T2 — Write STATUS-FROZEN.md (GREEN)** (in `vamseeachanta/acma-projects` repo)
- `cd /mnt/ace/acma-projects`
- Create `STATUS-FROZEN.md` with the verbatim content above
- Verify: `[[ -f STATUS-FROZEN.md ]] && wc -l STATUS-FROZEN.md` → ~60 lines

**T3 — Commit + push STATUS-FROZEN.md** (single pathspec commit)
- `cd /mnt/ace/acma-projects`
- `git add STATUS-FROZEN.md`
- `git commit -m "chore: declare repo frozen per workspace-hub#2745" -- STATUS-FROZEN.md`
- `git push origin main`
- Verify: `git log -1 --pretty=oneline` → shows the freeze commit
- Verify on GH: `gh api repos/vamseeachanta/acma-projects/contents/STATUS-FROZEN.md -q .name` → `STATUS-FROZEN.md`

**T0 — Pre-execution parallel-work check** (r2-codex finding 9, must-fire rule `feedback_check_parallel_work`)
- Run `pgrep -af "claude|codex|hermes" | grep -v grep` to inventory in-flight agent sessions
- Scan `~/.hermes/sessions/` for active session_ids touching `/mnt/ace/acma-projects/`
- If any session is actively writing to acma-projects, ABORT and coordinate; otherwise proceed
- Capture inventory snapshot for the T9 evidence comment

**T0.5 — Pre-execution backup-state snapshot** (r2-codex finding 3, strengthened verification)
- Capture file count BEFORE any work: `find /mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928 -type f | wc -l > /tmp/acma-backup-precount.txt`
- Capture top-level dir listing: `ls -1 /mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928/ | sort > /tmp/acma-backup-pretopdirs.txt`
- These snapshots are the invariants T7 must match exactly (file count + top-dir listing); `du -sh` alone is insufficient because it can mask material mutation

**T4 — Local push-disable** (re-ordered before archive per r2-codex finding 7)
- `cd /mnt/ace/acma-projects`
- `git config --local remote.origin.pushurl "no_push://vamseeachanta/acma-projects-frozen"`
- Verify pushurl set: `git config --local --get remote.origin.pushurl` → returns the no_push URL
- Verify fetch URL intact: `git config --local --get remote.origin.url` → `https://github.com/vamseeachanta/acma-projects` (or `.git`)
- **Test push-block BEFORE archive** (so failure is pushurl-attributable, not archive-attributable): `git push --dry-run origin main 2>&1 | tee /tmp/acma-pushblock-evidence.txt | grep -i "could not resolve\|no_push"` → must match; capture the evidence line for T9

**T5 — Add freeze-pre-commit hook in acma-projects** (r2-codex finding 1, epic #2744 acceptance "guard/checker that fails if new files are staged")
- `cd /mnt/ace/acma-projects`
- Create `.git/hooks/pre-commit` (executable):
  ```bash
  #!/usr/bin/env bash
  echo "ERROR: acma-projects is FROZEN per workspace-hub#2745."
  echo "New data should go to vamseeachanta/llm-wiki-acma instead."
  echo "See STATUS-FROZEN.md."
  echo "To override (rare ops only): git commit --no-verify"
  exit 1
  ```
- `chmod +x .git/hooks/pre-commit`
- Verify: `touch /tmp/dummy && cp /tmp/dummy /mnt/ace/acma-projects/.test-guard-fires && cd /mnt/ace/acma-projects && git add .test-guard-fires && git commit -m "test" 2>&1 | grep "FROZEN" && git restore --staged .test-guard-fires && rm .test-guard-fires` → expects guard message
- Note: local hooks are NOT under version control (`.git/hooks/` is in `.gitignore` by default); the hook persists per-clone only. Document in STATUS-FROZEN.md that clones should add the same hook.

**T6 — Archive GH remote**
- `gh repo archive vamseeachanta/acma-projects --yes`
- Verify: `gh repo view vamseeachanta/acma-projects --json isArchived -q .isArchived` → `true`
- Verify: web UI shows "This repository has been archived by the owner" banner

**T7 — Verification: state checks all green**
- All T1 RED checks now GREEN:
  - `[[ -f /mnt/ace/acma-projects/STATUS-FROZEN.md ]] && echo "GREEN: present"`
  - `gh repo view vamseeachanta/acma-projects --json isArchived -q .isArchived` → `true`
  - `git -C /mnt/ace/acma-projects config --local --get remote.origin.pushurl` → returns no_push URL
- **Strict backup-unchanged verification** (r2-codex finding 3):
  - Re-count files: `find /mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928 -type f | wc -l > /tmp/acma-backup-postcount.txt`
  - Re-list top-dirs: `ls -1 /mnt/ace/acma-projects.preexisting-before-repo-move-20260520-075928/ | sort > /tmp/acma-backup-posttopdirs.txt`
  - Match invariants from T0.5: `diff /tmp/acma-backup-precount.txt /tmp/acma-backup-postcount.txt && diff /tmp/acma-backup-pretopdirs.txt /tmp/acma-backup-posttopdirs.txt` → must be silent (zero diff). If non-empty, ABORT — backup mutation under freeze is unexpected.

**T8 — Legal-sanity scan** (r2-codex finding 6)
- Run `bash scripts/legal/legal-sanity-scan.sh` from `/mnt/local-analysis/workspace-hub/` repo root (scoped to workspace-hub, the repo where the plan + STATUS-FROZEN.md text content originated; `vamseeachanta/acma-projects` is the target of the freeze action but the new content `STATUS-FROZEN.md` is committed there and is short-label-only — re-scan there too)
- Run the same script with `--repo=/mnt/ace/acma-projects` if it supports per-repo invocation; otherwise document that STATUS-FROZEN.md content was scanned via grep prior to commit
- Expected: exit 0 (no client legal names, no deny-list patterns, no secrets)

**T9 — Execution-stage adversarial review** (r2-codex finding 2; required by `SHARED_SOUL.md` adversarial-review-at-both-stages)
- After T0–T8 execute successfully, dispatch T2 cross-review on the *executed work* (not the plan):
  - Provider review prompts target: the freeze commit SHA, archive evidence, pushurl config output, pre-commit hook content, backup invariant verification, legal-sanity output
- Land outputs at `scripts/review/results/2026-05-20-execute-2745-{claude,codex}.md`
- Reviews must reach APPROVE / MINOR-NITS from both providers before T10 close

**T10 — Verify #2746 paired completion before close** (r2-codex finding 8, was "T7 paired completion confirmed")
- Concrete checks required before closing #2745:
  - `gh issue view 2746 --json state -q .state` → `OPEN` is acceptable (siblings can close independently); plan-approved status implies in-progress, OK
  - `gh issue view 2746 --json labels | jq -r '[.labels[].name]'` → must NOT contain `status:plan-review` or earlier (i.e., #2746 must have already progressed past plan-review)
  - If #2746 is still at `status:needs-plan` or `status:plan-review`, PAUSE this close until #2746 catches up to at least `status:plan-approved`
- Post evidence comment on #2745 with: STATUS-FROZEN.md commit SHA, GH archive timestamp, local pushurl config, backup-unchanged diff output, legal-sanity scan exit, T9 review URLs, #2746 state at close-time
- Close #2745 with `gh issue close 2745 --comment "<evidence>"` per `feedback_gh_issue_comment`

## TDD Test List

This issue is operational (no code module produced), so "TDD" here = state-verification checks executed against runtime. Each is paired RED (pre-state) and GREEN (post-state).

| # | Check | RED (pre-state) | GREEN (post-state) |
|---|---|---|---|
| 1 | `STATUS-FROZEN.md` exists in repo | absent | present, ≥40 lines |
| 2 | GH remote archived | `isArchived: false` | `isArchived: true` |
| 3 | Local `remote.origin.pushurl` override | unset | `no_push://...` |
| 4 | Local `remote.origin.url` (fetch) preserved | `https://github.com/...` | unchanged |
| 5 | Local push attempt blocked | succeeds | fails (no_push host) |
| 6 | Backup `/mnt/ace/acma-projects.preexisting-*` present | ~1.8 TB | ~1.8 TB unchanged |
| 7 | STATUS-FROZEN.md visible on GH | 404 | 200, file content matches local |
| 8 | `/mnt/ace/acma-projects/` working tree clean post-freeze | (variable) | clean (only freeze commit landed) |

## Acceptance Criteria

- [ ] T0 parallel-work check completed; in-flight session inventory captured for T10 evidence comment
- [ ] `STATUS-FROZEN.md` committed and pushed to `vamseeachanta/acma-projects:main` BEFORE archive (so visible on archived repo)
- [ ] `STATUS-FROZEN.md` content matches plan §Pseudocode: freeze date, successor repo (`vamseeachanta/llm-wiki-acma`), reversal procedure, link to [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769) for backup-disposition planning; does NOT contain backup-disposition decision content (r2-codex finding 4)
- [ ] Local repo `/mnt/ace/acma-projects/` has `remote.origin.pushurl` set to `no_push://...` (T4); push-dry-run failure attributable to pushurl, NOT archive (T4 runs BEFORE T6 per r2-codex finding 7)
- [ ] Local fetch URL preserved (still `vamseeachanta/acma-projects`)
- [ ] Freeze pre-commit hook installed at `/mnt/ace/acma-projects/.git/hooks/pre-commit` and verified rejecting test commits (T5; epic #2744 acceptance "guard/checker fails on new data ingestion" per r2-codex finding 1)
- [ ] `vamseeachanta/acma-projects` has `isArchived: true` on GitHub (T6)
- [ ] Backup directory file count + top-dir listing match T0.5 pre-snapshot exactly (T7 strict invariant per r2-codex finding 3; `du -sh` alone is insufficient)
- [ ] Legal-sanity scan runs at T8 on workspace-hub AND captures STATUS-FROZEN.md content scan; exit 0 (r2-codex finding 6)
- [ ] T9 execution-stage adversarial review: outputs at `scripts/review/results/2026-05-20-execute-2745-{claude,codex}.md`; both APPROVE / MINOR-NITS (r2-codex finding 2; required per `SHARED_SOUL.md` review-at-both-stages)
- [ ] T10 concrete #2746 state check before close: #2746 must be at `status:plan-approved` or later (r2-codex finding 8)
- [ ] Comment posted on [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) with T10 evidence package: commit SHA, archive timestamp, pushurl config, hook verification, backup-unchanged diff output, legal-sanity exit, T9 review URLs, #2746 state at close-time
- [ ] [#2745](https://github.com/vamseeachanta/workspace-hub/issues/2745) closed with `gh issue close --comment "<evidence>"` per `feedback_gh_issue_comment`
- [ ] Pre-completion cleanup audit per `coordination/pre-completion-cleanup-audit` skill: CLEAN or EXPECTED only; no UNEXPECTED residue

## Adversarial Review Summary

(To be filled by reviewers; T2 default = Claude + Codex)

**Claude review (drafting agent):** TBD after plan posted
**Codex review:** TBD after plan posted
**Gemini review (optional T3 escalation):** UNAVAILABLE / OPTIONAL — degrade per `feedback_gemini_sandbox_overlay_blindness` if quota out

Specific defect-hunt prompts for reviewers:
- Is `gh repo archive` reversible without history loss? (Yes per GitHub docs; verify reviewer concurs)
- Does the `no_push://` pushurl trick work on all git versions in use? (Test on 2.40+ via dry-run)
- Does the STATUS-FROZEN.md cover all revisit triggers a future operator would care about?
- Does the 1.8 TB option-A pick (retain) under-commit when option C (selective delete) is genuinely cheap?

## Risks and Open Questions

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `gh repo archive` requires admin auth that operator session lacks | Low | Medium | Pre-check `gh auth status` and `gh api user --jq .login`; pause if not admin |
| Pushurl trick `no_push://...` is git-version-sensitive | Low | Low | T5 verifies via dry-run; if `--dry-run` succeeds (push allowed), fall back to `git config branch.main.pushRemote no_push` |
| 1.8 TB backup disposition stalls in [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769) while disk pressure grows | Medium | Medium | [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769) is `priority:high`; surface in `/whats-next` if stalled past 2026-06-03 (2-week soft deadline) |
| Auto-sync pushes the STATUS-FROZEN.md commit silently before archive | Low | Low | Plan sequences T3 (push) BEFORE T4 (archive) by design; auto-sync only accelerates T3 |
| Concurrent commit lands on `acma-projects:main` between T2 and T3 | Very low | Low | Repo is on freeze posture; user is the only writer; commit before archive locks the state |
| Backup directory accidentally deleted by another agent's cleanup pass | Low | High | `pre-completion-cleanup-audit` defends; STATUS-FROZEN.md names the backup as EXPECTED residue per `feedback_pre_completion_cleanup_audit_gate` |

**Open questions (deferred to implementation or follow-on):**
- Should the freeze commit be co-signed/tagged for extra historical weight? Default: no, single chore commit is sufficient.
- Should we also add a CODEOWNERS or branch-protection rule on the archived repo for belt-and-suspenders? Archive already blocks pushes; redundant.

## Complexity: T2

T2 justification: external-state changes affecting a shared GitHub repo (archive is reversible but visible to all collaborators); cross-references workspace-hub#2746 paired completion; 1.8 TB disposition decision warrants peer review. Below T3 because the operational steps are bounded (7 tasks, all reversible within minutes).

## Implementation Notes for Future Approved Work

- T1–T6 execute in sequence; T7 (close issue) only after [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) implementation is also done. Closing both children near-simultaneously keeps the [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) epic audit clean.
- Backup disposition is now [#2769](https://github.com/vamseeachanta/workspace-hub/issues/2769)'s scope. If that issue stalls, surface in `/whats-next` rather than reopening this freeze plan.
- The STATUS-FROZEN.md format established here is a candidate pattern for the broader `llm-wiki-<client>` freeze handling. If a second client wiki (Phase 4–5 from [#2746](https://github.com/vamseeachanta/workspace-hub/issues/2746) spec) ever needs source-repo freeze, this STATUS-FROZEN.md template can be lifted.
