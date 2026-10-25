---
name: deckhand-api-presence-sync
description: Compare the API catalog weekly and prepare public presence changes for draft review.
---

# Weekly API presence sync

This procedure keeps recent-work bullets, LinkedIn Featured/About drafts, website
API catalog rows and README catalog-link counts aligned with reviewed public
report evidence. The helper reads local files and emits JSON. Every proposed
surface change requires human review in a DRAFT PR; publication and merge require
separate maintainer action.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Restore the scheduled comparison after removal of its executable; require report evidence before public claims. |
| 1 | 2026-10-24 | Use consistent private evidence for comparisons and advancement; distinguish unavailable evidence from a reviewed withdrawal. |

## Plan-lite and basis

- Slice 1 will restore catalog parsing, a seeded snapshot and deterministic deltas.
- Slice 2 will prepare surface instructions and require reviewed report evidence.
- Slice 3 will repair the schedule target and require draft PR evidence for state updates.
- Files will remain under this directory, `tests/marketing/` and the existing schedule catalog.
- New paths = current identifiers minus previous identifiers; removed paths use the inverse.
- Status changes compare shared identifiers. Counts are set cardinalities.
- These definitions come from issue 3302 and the prior helper; no physical equations,
  empirical constants or engineering acceptance limits apply.
- The canonical-first format comes from issue 3305 and the published catalog schema.
- The worked example below supplies independent hand calculations for regression tests.
- A second-provider review remains required before merge; this helper cannot supply it.

## Procedure

1. **Read the catalog.** Prefer `docs/deckhand/api-catalog.json` from an authorized
   local catalog checkout. Use `--source canonical --canonical <catalog.json>` to
   force it. `auto` prefers canonical and falls back to
   `config/deckhand/routing/domain-workflows.yaml` only when canonical is absent.
   Malformed canonical input fails instead of silently switching source. Optional
   environment inputs are `DECKHAND_REPO`, `DECKHAND_API_CATALOG` and
   `DECKHAND_CATALOG`; explicit CLI paths take precedence. No network fetch occurs.
   Keep raw inputs and output in an approved private working directory.
2. **Compare the snapshot.** Run the helper without a write flag, or use
   `--emit-current`. It emits only whitelisted public/roadmap fields; private and
   internal rows become a combined count. Missing snapshots compare as empty;
   malformed snapshots fail. The committed empty seed is deliberately uninitialized,
   not a claim that the catalog is empty. Restore reviewed prior state privately if
   available; otherwise review the entire first delta.
3. **Draft the surfaces.** Supply `--evidence <reviewed-reports.json>` and use
   `--draft-packet` to obtain a review packet for resume, LinkedIn, website and
   README edits. Inspect removed rows, withdrawals and metadata changes as well
   as additions. Open the current locked messaging source linked from issue 3302
   before writing copy. If unavailable, mark messaging review NOT_EVALUATED and
   stop the affected public copy. A packet is instructions and evidence, not an
   automatic edit to another repository. Keep LinkedIn proposals in a reviewed
   document; do not post them. Count only evidence-backed catalog workflow rows,
   never nested analytical operations or roadmap entries.
4. **Review rights, personal data and secrets.** Verify each public report is
   accessible without authentication, belongs to the intended workflow, and has
   publication rights. An example URL or a residency label is insufficient.
   Inspect every proposed line for identifying or restricted information and run
   the destination repository's current secret/content checks. The retired
   identifier scanner is not reintroduced (see `config/agents/SHARED_SOUL.md`).
   Keep evidence and receipts private. Unknown rights, unavailable messaging or
   unresolved content findings block that proposal and snapshot advancement.
5. **Open DRAFT PRs, then advance state.** Prepare a separate branch in each
   authorized destination repository, run its checks and open one DRAFT PR per
   repository. Confirm each remotely as open and draft immediately before recording
   its URL/state. Cover all four surfaces, including no-change dispositions in
   review text. Only then supply `--update-snapshot --review-receipt <receipt.json>`
   with the same catalog and evidence inputs. The helper requires matching current
   and previous digests, recorded content review and coverage for every surface.
   Failed receipt validation leaves state unchanged. Commit the snapshot through
   its own reviewed change. If a PR fails to open, leave state unchanged and retry
   the same comparison. Do not publish, merge, or push to a default branch.

## Evidence and receipt inputs

Reviewed report evidence is keyed by catalog identifier:

```json
{
  "screen": {
    "public_report_url": "https://example.org/report.html",
    "reviewed": true
  }
}
```

The example URL is synthetic. Supply an actual reviewed public report when used.
Only `live_public` rows with this evidence become `claimable_public: true`.
Without it, `claim_check` is `NOT_EVALUATED`. Roadmap/private/internal rows are
never claimable. HTTPS locators with credentials, parameters or placeholders are
rejected. URL syntax checks do not establish public access, report validity or rights;
the reviewer establishes those facts. Invalid evidence does not fall back to
the catalog's `claimable_public` flag or `report_url_example` hint.

The comparison output includes `current_digest` and `previous_digest`. Copy them
into a private review receipt with this structure:

```json
{
  "current_digest": "copy the current digest",
  "previous_digest": "copy the previous digest",
  "content_reviewed": true,
  "draft_prs": [
    {
      "url": "https://github.com/example/surfaces/pull/1",
      "isDraft": true,
      "state": "OPEN",
      "surfaces": ["resume", "linkedin", "website", "readme"]
    }
  ]
}
```

The pull request number is a synthetic example. Use one record per actual
repository PR and distribute the covered surfaces accordingly. A receipt is
recorded evidence, not authenticated authority: the helper does not query remote
PRs, establish reviewer identity or detect later PR closure. Maintainers must
verify current remote state. Snapshot writes atomically replace an existing
regular file; they do not merge concurrent changes. Serialize updates.

## Worked example

Synthetic previous state: `screen` is roadmap, `old` is live_public with reviewed
report evidence. Current state: `screen` is live_public with reviewed evidence,
`future` is roadmap, and `old` is absent.

Method: previous identifiers = `{old, screen}`; current = `{future, screen}`.
Their differences give new = `{future}` and removed = `{old}`. The common
identifier `screen` changes from roadmap to live_public. Evidence-backed public
identifiers change from `{old}` to `{screen}`. Therefore one public addition and
one withdrawal require review. Current public count is one; roadmap contributes
zero. Without report evidence, the evaluated public count is unavailable (null),
and the comparison is NOT_EVALUATED. These are hand-calculated set operations, not outputs reused as
test expectations. Tests encode additions, removals, promotion, demotion,
unchanged reruns and independent count expectations.

```bash
uv run --no-project --with pyyaml python scripts/marketing/deckhand-api-presence-sync/catalog_delta.py --source canonical --canonical catalog.json --snapshot previous.json --evidence reviewed-reports.json --draft-packet
```

## Schedule and operational limits

Issue 3302 specifies Sunday at 05:00 UTC (`0 5 * * 0`). The declaration remains
in `config/scheduled-tasks/schedule-tasks.yaml`. Operator-managed installation
uses `scripts/cron/setup-cron.sh`; its transactional preview/apply procedure is
documented in `docs/ops/scheduled-tasks.md`. Review the preview before changing a
live crontab and verify its timezone is UTC. The helper neither installs nor
changes schedules. The cron command only reports a delta; maintainers execute
the review procedure when additions, withdrawals or metadata changes occur.
No live scheduling or cross-repository publication is performed by this change.

Set `DECKHAND_API_EVIDENCE` in the scheduler environment to the privately held
reviewed-reports JSON file. The scheduled command supplies that file through
`--evidence`; manual comparison and advancement use the same environment default,
or an explicit `--evidence` override. Keep the file outside public version control.
Configure the variable as an environment assignment in the installed crontab;
shell profile exports alone do not configure cron. Confirm its value privately
in the installation preview. No private location is stored in the declaration.

Missing or unreadable evidence produces `claim_check: NOT_EVALUATED`, a stated
reason and a null public count. Evidence-dependent additions, withdrawals and
metadata changes are not inferred. Catalog removals and demotions still withdraw
previously reviewed claims, and catalog changes are included in draft packets.
Snapshot advancement requires an available evidence mapping and a matching review
receipt. Malformed evidence fails closed. An available empty mapping explicitly
records no reviewed claims and can produce withdrawals; it differs from an
unavailable file. The comparison-level EVALUATED state means that the evidence
mapping was read; each row still requires its own reviewed report to be claimable.
A row without that proof remains NOT_EVALUATED. Evidence expiration is a review decision; there is no inferred
age limit. An unchanged comparison needs no snapshot write.

## Sources

- Issue 3302: cadence, four presence surfaces, draft PR ordering and status policy.
- Issue 3305: canonical catalog preference and privacy projection requirements.
- Published catalog: `deckhand/docs/deckhand/api-catalog.json`, inspected during
  implementation; routing basis: `config/deckhand/routing/domain-workflows.yaml`.
- Messaging and career cadence: the linked source issues named in issue 3302;
  consult their current authorized content before preparing destination copy.
- Repository data rules: `docs/architecture/agent-data-handling-contract.md`.

## Later slices

Destination-specific editors, remote PR authentication, automated source fetches
and authenticated report probes remain outside this read-and-propose helper.
They require destination access and separate tests before automation is claimed.
