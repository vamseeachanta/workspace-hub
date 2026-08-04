# Plan for #3788: reconcile.py open-only snapshot reports closed dispatch records as label-missing

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-08-03
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3788
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-03-plan-3788-claude.md | scripts/review/results/2026-08-03-plan-3788-codex.md | scripts/review/results/2026-08-03-plan-3788-gemini.md

---

## Resource Intelligence Summary

Planning mode: `single-lane` for the draft artifact. The implementation phase will remain blocked until plan review completes, the user approves, and `status:plan-approved` exists.

### Existing repo code
- `scripts/dispatch/reconcile.py` - `fetch_labels()` will be changed because it currently defaults to `route.fetch_open_issues`, and `reconcile()` will continue to treat an omitted issue key the same as an issue that was fetched with no dispatch labels.
- `scripts/dispatch/route.py` - `fetch_open_issues()` will stay available for write-path/open-issue use, but the reconciler will stop using it as the authoritative label source for record-named issues.
- `tests/dispatch/test_reconcile.py` - new RED coverage will be added near the adapter/CLI tests. Existing tests cover in-sync, label-missing, and label-without-record behavior, but they do not prove that "not returned by the query" differs from "returned with no dispatch label."
- `.claude/dispatch/records/` - the live record corpus names three terminal records: `vamseeachanta/workspace-hub#3757`, `vamseeachanta/workspace-hub#3759`, and `vamseeachanta/deckhand#33`.

### Standards
| Standard | Status | Source |
|---|---|---|
| N/A | not applicable - operational dispatch tooling issue, no engineering standard transfer | `docs/plans/README.md` issue-class guidance defaults this to General/Harness-Infra resource intelligence rather than engineering standards |

### LLM Wiki pages consulted
- No relevant wiki pages will be changed. `docs/document-intelligence/README.md` and `docs/document-intelligence/data-intelligence-map.md` are the relevant intelligence entry points for this plan, and they point to document/registry assets rather than dispatch-reconciler design material.

### Documents consulted
- Issue [#3788](https://github.com/vamseeachanta/workspace-hub/issues/3788) - states that `reconcile.py` treats an open-only label snapshot as complete, gives closed issue examples, and asks for record-targeted label fetching.
- Issue [#3740](https://github.com/vamseeachanta/workspace-hub/issues/3740) - provides the parent dispatch-state context; this issue remains open and `status:plan-approved`, so #3788 will be treated as a focused bug plan rather than a replacement for the parent.
- `docs/plans/_template-issue-plan.md` - defines the required plan sections and embedded evidence requirements.
- `docs/plans/README.md` - defines the #2208 retrieval contract, TDD gate, adversarial review gate, and user-approval hard stop.
- `docs/standards/PARALLEL_FIRST_EXECUTION.md` - classifies this planning work as main-session synthesis, with future implementation gated by plan approval and TDD.
- Drive index search via `scripts/data/drive-index-search/search.py "dispatch reconcile open only snapshot labels" --json --caller plan-resource-intel` - returns token matches in CAD/literature files, but no relevant dispatch, GitHub label, or reconciler design document.

### Gaps identified
- A targeted fetch path for labels on the exact issues named by records will need to be built.
- The reconciler adapter will need an explicit representation for "issue was not fetched / lookup failed" so that a missing query result will not be collapsed into an empty label set.
- The open-only broad list will need to be scoped to the `label-without-record` sweep, if retained, instead of being shared with record reconciliation.
- A regression test will need to fail on the current implementation by proving that a closed, correctly labeled record issue classifies as in-sync only when it is actually fetched.
- The issue currently lacks a `lane:` label even though the plan header will set `Lane: lane:claude`; label reconciliation will need to happen before this plan can move to `status:plan-review`.

### Evidence (embedded verification)

**Issue statuses** (commands captured 2026-08-04T02:15Z):

```
$ gh issue view 3788 --json number,title,state,labels,url
{"labels":[{"name":"bug"},{"name":"priority:high"},{"name":"cat:operations"},{"name":"machine:dev-primary"},{"name":"status:needs-plan"},{"name":"domain:routing"}],"number":3788,"state":"OPEN","title":"bug(dispatch): reconcile.py reads an open-only label snapshot, so every CLOSED issue reports false LABEL-MISSING","url":"https://github.com/vamseeachanta/workspace-hub/issues/3788"}

$ gh issue view 3740 --json number,title,state,labels,url
{"labels":[{"name":"priority:high"},{"name":"cat:operations"},{"name":"machine:dev-primary"},{"name":"status:plan-approved"},{"name":"gate:completeness"},{"name":"domain:routing"}],"number":3740,"state":"OPEN","title":"867 issues cannot leave dispatch:ready - nothing advances dispatch state","url":"https://github.com/vamseeachanta/workspace-hub/issues/3740"}

$ gh issue view 3757 --json number,title,state,labels,url
{"labels":[{"name":"cat:tooling"},{"name":"machine:dev-primary"},{"name":"domain:repo"},{"name":"dispatch:done"}],"number":3757,"state":"CLOSED","title":"pilot: prove the dispatch loop closes end-to-end (#3740 slice 5)","url":"https://github.com/vamseeachanta/workspace-hub/issues/3757"}

$ gh issue view 3759 --json number,title,state,labels,url
{"labels":[{"name":"cat:tooling"},{"name":"domain:repo"},{"name":"machine:licensed-win-1"},{"name":"dispatch:done"}],"number":3759,"state":"CLOSED","title":"pilot: prove the dispatch loop closes on the Windows runner (#3740 follow-on)","url":"https://github.com/vamseeachanta/workspace-hub/issues/3759"}

$ gh issue view 33 --repo vamseeachanta/deckhand --json number,title,state,labels,url
{"labels":[{"name":"bug"},{"name":"feat:capability"},{"name":"domain:capability"},{"name":"lane:claude"},{"name":"priority:high"},{"name":"cat:operations"},{"name":"machine:dev-primary"}],"number":33,"state":"OPEN","title":"[P1] Runtime repairs: ParaView segfault on ace-linux-2, FAL image backend, misc flakes","url":"https://github.com/vamseeachanta/deckhand/issues/33"}
```

**Issue body excerpt**:

```
$ gh issue view 3788 --json title,body --jq '"TITLE: \(.title)\nBODY_HEAD:\n" + (.body | split("\n")[:18] | join("\n"))'
TITLE: bug(dispatch): reconcile.py reads an open-only label snapshot, so every CLOSED issue reports false LABEL-MISSING
BODY_HEAD:
## Summary

`reconcile.py` builds its authoritative label snapshot from `route.fetch_open_issues()`, which queries `--state open`. **Every closed issue is therefore absent from the snapshot**, and the reconciler classifies it as `LABEL-MISSING` - "record says 'done' but the issue carries no dispatch: label" - even when the label is present.
```

**File existence**:

```
$ find .claude/dispatch/records -type f -maxdepth 3 | sort | sed -n '1,80p'
.claude/dispatch/records/vamseeachanta-deckhand#33.json
.claude/dispatch/records/vamseeachanta-workspace-hub#3757.json
.claude/dispatch/records/vamseeachanta-workspace-hub#3759.json

$ find tests -maxdepth 3 -type f | sort | rg 'dispatch|reconcile|route|claim|drain'
tests/dispatch/test_reconcile.py
tests/dispatch/test_route_write_gate.py
tests/dispatch/test_write_preserves_cardinality.py
...
```

**Line excerpts**:

```
$ nl -ba scripts/dispatch/reconcile.py | sed -n '373,415p'
   373  def reconcile(records_root, labels_by_issue=None, now=None) -> Report:
   374      """Reconcile every record under `records_root`. READ-ONLY.
   376      `labels_by_issue` maps `owner/repo#123` -> the issue's current label names.
   380      labels_by_issue = dict(labels_by_issue or {})
   386      for path in sorted(root.glob("*.json")):
   397          seen.add(record["issue"])
   398          outcome = reconcile_issue(record, labels_by_issue.get(record["issue"], ()),
   406      for issue in sorted(set(labels_by_issue) - seen):
   411                  ORPHAN_LABEL, issue,

$ nl -ba scripts/dispatch/reconcile.py | sed -n '699,713p'
   699  def fetch_labels(repo: str, fetch=None) -> dict[str, set[str]]:
   706      fetch = fetch or route.fetch_open_issues
   707      snapshot = fetch(repo)
   708      if snapshot is None:
   713      return {f"{repo}#{number}": set(labels) for number, labels in snapshot.items()}

$ nl -ba scripts/dispatch/route.py | sed -n '787,804p'
   787  def fetch_open_issues(repo: str):
   788      """ONE GraphQL call: map {number -> set(label names)} for all OPEN issues.
   793      out = gh(["issue", "list", "--repo", repo, "--state", "open",
   794                "--limit", str(LIMIT), "--json", "number,labels"])
   804      return {str(it["number"]): {l["name"] for l in it["labels"]} for it in items}

$ nl -ba tests/dispatch/test_reconcile.py | sed -n '224,241p'
   224  def test_an_issue_with_no_dispatch_label_is_its_own_class(tmp_path):
   230      _done(tmp_path)
   231      report = RC.reconcile(tmp_path, {ISSUE: {"machine:m"}}, now=_clock())
   232      assert report.counts()[RC.LABEL_MISSING] == 1
   237  def test_an_agreeing_label_produces_no_write(tmp_path):
   238      _done(tmp_path)
   239      report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:done"}}, now=_clock())
   240      assert report.outcomes[0].writes_labels is False
   241      assert report.counts()[RC.IN_SYNC] == 1
```

**Record excerpts**:

```
$ sed -n '1,140p' .claude/dispatch/records/vamseeachanta-workspace-hub#3757.json
 "issue": "vamseeachanta/workspace-hub#3757",
 "state": "done",

$ sed -n '1,140p' .claude/dispatch/records/vamseeachanta-workspace-hub#3759.json
 "issue": "vamseeachanta/workspace-hub#3759",
 "state": "done",

$ sed -n '1,140p' .claude/dispatch/records/vamseeachanta-deckhand#33.json
 "issue": "vamseeachanta/deckhand#33",
 "state": "done",
```

**Reproduction proofs**:

```
$ uv run python scripts/dispatch/reconcile.py --records .claude/dispatch/records --repo vamseeachanta/workspace-hub
dispatch reconcile - 3 record(s) under .claude/dispatch/records
  labels are a projection of records; no record is ever inferred from a label

  in-sync                    0   label already equals the record - nothing to do
  label-missing              3   record exists, issue carries no dispatch: label at all
  label-without-record     524   label with no record - REPORTED, never adopted as state

  LABEL-MISSING  vamseeachanta/deckhand#33: record says 'done' but the issue carries no dispatch: label - invisible in every board view
  LABEL-MISSING  vamseeachanta/workspace-hub#3757: record says 'done' but the issue carries no dispatch: label - invisible in every board view
  LABEL-MISSING  vamseeachanta/workspace-hub#3759: record says 'done' but the issue carries no dispatch: label - invisible in every board view

  planned: 3 label write(s), 0 record correction(s)
  dry run - no writes. Set DISPATCH_APPLY_ENABLED=1 to arm.
```

Failure mode observed matches issue claim: YES. The current pass reports `workspace-hub#3757` and `workspace-hub#3759` as `LABEL-MISSING` even though GitHub returns `dispatch:done` for both closed issues.

**Open/all dispatch-done search proof**:

```
$ gh issue list --repo vamseeachanta/workspace-hub --state all --label 'dispatch:done' --json number,state,labels --limit 20
[{"number":3759,"state":"CLOSED","labels":[{"name":"dispatch:done"}...]},{"number":3757,"state":"CLOSED","labels":[{"name":"dispatch:done"}...]}]

$ gh issue list --repo vamseeachanta/workspace-hub --state open --label 'dispatch:done' --json number,state,labels --limit 20
[]
```

**Drive-index proof**:

```
$ scripts/data/drive-index-search/search.py "dispatch reconcile open only snapshot labels" --json --caller plan-resource-intel
WARNING: index ace_knowledge last refresh FAILED at 2026-08-02T07:45:52.031691+00:00 -- results may be stale
...
"results": [
  {"canonical_path": "/mnt/ace/digitalmodel/docs/domain/subsea-risers/.../VerdErg Porch Only - 09.02.09 (OPEN)-.SLDPRT", "source_index": "cad_readability"},
  {"canonical_path": "/mnt/dde/Literature/Engineering/open channel flow", "source_index": "dde_literature_catalog"}
]
```

The drive-index hits are token matches on "open"/"only" and are not relevant to dispatch, GitHub labels, or reconciler implementation.

Current distinct source count: 9.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-08-03-issue-3788-reconcile-open-only-snapshot.md` |
| Tests | `tests/dispatch/test_reconcile.py` |
| Implementation | `scripts/dispatch/reconcile.py` |
| Implementation helper, if needed | `scripts/dispatch/route.py` |
| Plan review - Claude | `scripts/review/results/2026-08-03-plan-3788-claude.md` |
| Plan review - Codex | `scripts/review/results/2026-08-03-plan-3788-codex.md` |
| Plan review - Gemini | `scripts/review/results/2026-08-03-plan-3788-gemini.md` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

A reconciler label-fetch path will fetch labels for every record-named issue, including closed issues and cross-repo records, while the optional broad orphan-label sweep will remain open-only and separately scoped.

---

## Pseudocode

```
function record_issue_refs(records_root):
    iterate record json files using existing records.read_record
    skip unreadable records in the same way reconcile() already reports them
    collect each valid record["issue"] as owner/repo#number
    return sorted unique issue refs

function fetch_record_issue_labels(records_root, issue_fetch=None):
    refs = record_issue_refs(records_root)
    for each ref in refs:
        parse owner/repo#number with existing split_issue
        call issue_fetch(repo, number) or gh issue view number --repo repo --json labels
        if lookup fails or returns an unparseable payload:
            raise RuntimeError so record reconciliation will not read absence as empty labels
        store full issue key -> set(label names)
    return labels_by_issue

function fetch_open_orphan_sweep_labels(repo):
    call route.fetch_open_issues(repo)
    if result is None:
        raise RuntimeError using existing fail-closed wording
    return {repo#number: set(labels) for each open issue}

function main(argv):
    if --labels-json:
        keep current offline behavior
    else if --repo:
        record_labels = fetch_record_issue_labels(args.records)
        orphan_labels = fetch_open_orphan_sweep_labels(args.repo)
        labels = orphan_labels merged with record_labels taking precedence
    report = reconcile(args.records, labels)
```

Design constraint: a fetched issue with labels `{machine:m}` will remain a valid `LABEL-MISSING` record outcome. A record issue absent from a query result will be an adapter failure, not an empty label set.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `tests/dispatch/test_reconcile.py` | Add RED tests for closed/targeted record label fetching, query-missing versus no-dispatch-label distinction, cross-repo record fetching, and open-only orphan sweep retention. |
| Modify | `scripts/dispatch/reconcile.py` | Add targeted record issue label fetch, split it from the broad orphan sweep, and keep fail-closed behavior when a record issue cannot be fetched. |
| Modify if needed | `scripts/dispatch/route.py` | Add a small issue-view helper only if keeping GitHub access wrappers in `route.py` fits existing module boundaries better than localizing the helper in `reconcile.py`. |
| Update | `docs/plans/README.md` | Add the #3788 plan index row after the plan has been drafted. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_record_issue_label_fetch_includes_closed_issue` | A record-named issue fetched through the targeted path can classify as in-sync even when a broad open-only fetch would omit it. | Temp record `owner/repo#7` in `done`; targeted fetch returns `dispatch:done`; open sweep returns `{}`. | Report has `in-sync=1`, `label-missing=0`, and no label writes. |
| `test_missing_query_result_is_not_treated_as_no_labels` | Adapter absence will not collapse into "fetched issue has no dispatch label." | Temp record `owner/repo#7`; targeted fetch omits `7` or returns a sentinel missing result. | RuntimeError or explicit fail-closed adapter error before reconcile classifies the record. |
| `test_fetched_issue_with_no_dispatch_label_still_reports_label_missing` | The real no-label condition remains distinct from query omission. | Temp record `owner/repo#7`; targeted fetch returns labels `{"machine:m"}`. | Report has `label-missing=1` and plans `dispatch:done` add. |
| `test_live_record_fetch_groups_by_repo` | Cross-repo record corpus will not be forced through one `--repo` snapshot. | Records for `vamseeachanta/workspace-hub#3757` and `vamseeachanta/deckhand#33`; fake issue fetch records calls. | Fetch calls target both repos with their own issue numbers. |
| `test_orphan_sweep_remains_open_only` | A broad `label-without-record` sweep will keep the open-only semantics when retained. | Open sweep returns one open `dispatch:ready` issue with no record; targeted record fetch returns only record issues. | Report includes one `label-without-record` finding and does not require closed orphan search. |
| `test_cli_repo_mode_merges_record_labels_over_orphan_sweep` | CLI `--repo` mode will use targeted labels for records and open-only labels for orphan sweep. | Temp records plus fake fetchers; record key also appears in open sweep with stale labels. | Record-targeted label set wins for record outcome; unrelated open dispatch label still reports orphan. |
| `test_live_three_record_corpus_after_fix` | The live dry-run target will match the acceptance contract. | `.claude/dispatch/records` with live GitHub fetches. | Record outcomes report 2 `in-sync` and 1 `label-missing`; deckhand#33 remains the genuinely unlabelled record. |

RED command:

```
uv run --with pyyaml --with pytest pytest tests/dispatch/test_reconcile.py -q
```

The first implementation step will add the tests and run the command before production code changes. At least the new closed-issue/query-omission tests will fail on the current tree.

---

## Acceptance Criteria

- [ ] New tests are written first and fail on the current implementation: `uv run --with pyyaml --with pytest pytest tests/dispatch/test_reconcile.py -q`.
- [ ] A record whose issue is closed and correctly labelled classifies as `in-sync`, not `label-missing`.
- [ ] A record whose issue is fetched and genuinely carries no `dispatch:` label still classifies as `label-missing`.
- [ ] A record issue missing from a query result fails closed or is otherwise distinguished from a fetched issue with no dispatch label.
- [ ] The `label-without-record` sweep remains open-only, or any scope change is explicit and covered by tests.
- [ ] Dry-run on the live three-record corpus reports record outcomes of 2 `in-sync` and 1 `label-missing`; `deckhand#33` remains the expected label-missing live fixture.
- [ ] Regression suite for the touched module passes: `uv run --with pyyaml --with pytest pytest tests/dispatch/test_reconcile.py -q`.
- [ ] Legal/security scan passes before implementation closeout: `scripts/legal/legal-sanity-scan.sh`.
- [ ] Plan review artifacts exist under `scripts/review/results/` before the issue moves to `status:plan-review`.
- [ ] The issue carries exactly one `lane:` label matching this plan's `Lane: lane:claude` before `status:plan-review` is applied.

---

## Adversarial Review Summary

Plan review has not run yet. This draft will need the standard adversarial review wave before it can be posted for user approval.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Not run in this plan-only drafting step. |
| Codex | PENDING | Not run in this plan-only drafting step. |
| Gemini | PENDING | Not run in this plan-only drafting step. |

**Overall result:** PENDING

Revisions to make after review:
- Pending.

---

## Risks and Open Questions

- **Risk:** Per-record `gh issue view` calls will be slower than one open-list query if the record corpus grows. The plan will accept that tradeoff now because the current corpus is small and correctness depends on closed and cross-repo issues being visible.
- **Risk:** The current CLI accepts one `--repo`, while records may name multiple repos. The implementation will treat `--repo` as the orphan-sweep repo and the records themselves as authoritative for record-label fetches.
- **Risk:** A private or inaccessible repo in the record corpus could make targeted fetch fail. The adapter will fail closed rather than propose mass label writes from missing evidence.
- **Open:** Whether `fetch_record_issue_labels()` will live in `reconcile.py` or in `route.py` will be settled by the smallest testable change that matches existing module boundaries.

---

## Complexity: T2

**T2** - the change will touch an adapter boundary, CLI behavior, and regression tests, but it will stay within dispatch reconciliation and will not require a new architecture or cross-repo implementation.
