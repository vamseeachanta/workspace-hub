# Inbox / Drive / Feature-Backlog Triage Session — 2026-04-20

> **Status:** approved-design (awaiting user review of written spec)
> **Complexity:** T2 (orchestrated multi-track, read-heavy, gated on user approval for any destructive action)
> **Session scope:** one working session, three sequential tracks
> **Related issues:** #1963, #1968, #1969, #1971, #1986, #1987, #1988, #1991, #2017, #2019, #2024, #2025, #2026, #1476

## 1. Context

The user's request — "create/review existing gh features... review emails via claude-in-chrome... transfer docs to /mnt/ace/<repo>/... clean up mailboxes... identify unsubscribes" — maps almost 1:1 onto an existing backlog of ~15 open email/drive issues (listed above). This session does **not** create new features for work already scoped; it executes a slice of that backlog and proposes consolidation.

Three Gmail accounts in scope: `vamsee.achanta@aceengineer.com`, `achantav@gmail.com`, `skestatesinc@gmail.com`.

Prior triage artifacts (`ace_gmail_triage_2026-04-09.txt`, `daily_gmail_action_digest_2026-04-09.md`, `skestates_gmail_triage_2026-04-09.md` etc.) establish the ACE/personal/skestates pattern. This session produces comparable artifacts as issue comments, not new repo-root files.

## 2. Goal

End the session with:
1. One consolidated-roadmap comment on #2019 naming the next feature (B-candidate).
2. Three per-account triage comments (on #1968, #1969, #1971) with actionable/noise/unsubscribe classifications and drafted replies.
3. One approved `/mnt/ace/` transfer mapping (user-approved before any copy executes).
4. One implementation plan for the B-candidate at `status:plan-review` — user gates implementation.

Nothing destructive happens without per-action user approval.

## 3. Architecture

Three sequential tracks. No parallelism — coherence outweighs speed because C's output names B's target and A's findings validate C's prioritization.

```
C (backlog audit, read-only)
  │ output: roadmap comment on #2019 + named B-candidate
  ▼
A (today's triage, 3 accounts, read-only + drafted actions)
  │ output: 3 account comments + Drive→/mnt/ace mapping table + unsubscribe list
  ▼
B (one feature through planning gate)
  │ output: docs/plans/2026-04-20-<issue>-plan.md at status:plan-review
  ▼ (STOP — user approval required before any B implementation)
```

## 4. Track C — Backlog audit

### Scope
Read the ~15 open email/drive issues. Group by theme. Identify duplicates and the implied dependency graph (which issue unblocks which). Propose a 4-5-item consolidated roadmap.

### Deliverable
One comment on **#2019** ("Consolidate email skill sprawl") containing:
- Consolidated roadmap (4-5 named issues, in order)
- Named B-candidate with rationale (why this one, why now)
- Subsumed-issue list (proposed closures — not executed)

### Non-goals
- Closing any issue. C proposes; closures happen only on user approval.
- Creating new issues. The backlog is already dense enough.

## 5. Track A — Today's triage, 3 accounts

### Per-account scope
Most recent **50 messages** in Inbox (unread + read). Not "since last triage (2026-04-09)" — a bounded count is more predictable and avoids gaps when prior triage missed older unread mail.

### Classification schema
YAML, per the `data_format_guidelines` memory (agent-facing structured data defaults to YAML):

```yaml
- message: <subject>
  from: <sender>
  classification: actionable | data_extract | drive_doc | unsubscribe | archive | noise
  actionable_subtype: needs_reply | needs_decision | needs_forward  # if actionable
  drive_doc_target: /mnt/ace/<repo>/<subdir>/                        # if drive_doc
  data_extract_fields: [vendor, amount, date, ...]                   # if data_extract
  unsubscribe_reason: volume_flood | off_topic | never_engaged        # if unsubscribe
```

### Repo-mapping rule (Drive → /mnt/ace)

| Document type | Destination |
|---|---|
| Public O&G standards (API, DNV, ISO) | `/mnt/ace/O&G-Standards/` |
| Client / proprietary project docs | `/mnt/ace/client_projects/` (gitignored per ecosystem) |
| Personal finance, tax, HOA, pest, 1099 | `/mnt/ace/achantas-data/` |
| ACE business (CFP, strategy, admin) | `/mnt/ace/aceengineer-admin/` |
| Engineering calc artifacts | `/mnt/ace/digitalmodel/` (separate git repo — commits from inside) |
| Can't classify | leave in Drive; flag for user decision |

**Legal guard:** `scripts/legal/legal-sanity-scan.sh` runs on anything destined for a public-origin repo (`digitalmodel/`, `O&G-Standards/`, `aceengineer-admin/`) before any copy executes. `client_projects/` and `achantas-data/` are private/gitignored and skip the scan.

**Classification precedence when multiple apply:** `actionable` > `data_extract` > `drive_doc` > `unsubscribe` > `archive` > `noise`. An invoice that needs a reply classifies as `actionable` (primary) with `data_extract_fields` populated (secondary). Primary drives routing; secondary drives record-keeping.

### Outputs
- Comment on #1971 (ACE), #1968 (achantav), #1969 (skestates) — each with YAML triage table, actionable list, drafted replies (not sent), Drive-transfer proposal.
- Comment on #1991 (Sands flooding) plus one comment per unsubscribe candidate with ≥5% inbox volume share.
- Data-extract findings (invoices, tax docs) attach to the relevant domain issue (e.g., #2025 per-domain templates), not as root-level files.

### What A does NOT do
- No Gmail delete / archive / send without per-account user approval.
- No Drive → /mnt/ace copy without the mapping table approved first.
- No unsubscribe actions — candidates are identified and queued only.

## 6. Track B — One feature through planning gate

Use the `issue-planning-mode` skill (CLAUDE.md-mandated for all issue work): Resource Intel (≥3 sources with inline evidence per #2208) → Plan → Adversarial Review → `status:plan-review`.

**STOP at `plan-review`.** Per the `batch agents never self-approve` memory, this session does not set `status:plan-approved`. That transition is user-only.

## 7. Autonomy ladder

| Autonomous | Requires user approval |
|---|---|
| Read inboxes (all 3 accounts) | Any Gmail delete / archive / send |
| Read Drive docs | Any Drive → `/mnt/ace` copy |
| Classify messages | Any unsubscribe action |
| Draft replies | Any issue close |
| Post issue comments summarizing findings | `status:plan-approved` on B's plan |
| Write the B plan to `status:plan-review` | Any `digitalmodel/` commit |

## 8. Success criteria

- **C:** #2019 has one comment containing a named B-candidate + 4-5-item roadmap + proposed-closure list.
- **A:** Three account-comments posted (#1968/#1969/#1971); unsubscribe list ready; Drive-transfer mapping awaiting approval.
- **B:** One plan file at `docs/plans/2026-04-20-<issue>-plan.md` with adversarial review attached; GH label set to `status:plan-review`.

## 9. Out of scope (YAGNI)

- Executing B (gated on user approval).
- Sending replies or deleting mail (drafts/queued only).
- New email-related issues (use existing — per `no_local_task_IDs` memory).
- Two-way Drive ↔ /mnt/ace sync (one-shot copy only).
- A reusable triage skill (that is what B will design).

## 10. Gates summary

1. **Design gate** (this spec) — user reviews written spec → proceed to C.
2. **Drive-transfer gate** — user approves the mapping table → copies execute.
3. **Gmail-action gate** — user approves per-action lists → deletes/sends/unsubscribes execute.
4. **B-implementation gate** — user sets `status:plan-approved` → B implementation begins in a future session.
