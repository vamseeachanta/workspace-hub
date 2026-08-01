# Session handoff — dispatch records (#3740) + public-repo hostname sweep

**Date:** 2026-08-01
**Branch:** `feat/3740-dispatch-records`
**PR:** [#3741](https://github.com/vamseeachanta/workspace-hub/pull/3741)
**State at exit:** branch pushed and verified on the remote; working tree DIRTY by design (see §5)

---

## 1. What landed

Six commits on `feat/3740-dispatch-records`, each verified on the remote by content
(auto-sync won the push race six times — `[remote rejected]` was never a failure, but
it must always be confirmed with `git cat-file`, never assumed).

| commit | what |
|---|---|
| `9718f4b3c` | slice 1 — `records.py`, the record as state |
| `4d76047c0` | slices 2 + 4b — `claim.py`, `-IssueRef` on the Windows runner |
| `e008fed2b` | slice 3 — `reconcile.py`, records → labels, one direction |
| `c09fce0d0` | fix — the armed banner described the request, not the gate |
| `a538209be` | slice 4a — `run.sh`, the Linux runner |
| `98c4d364e` | shared-tenancy cap guard |
| `f5e3664e9` | cron identity inventory regeneration (#3728) |
| `14d7c1914` | registry host-identity correction |

**396 dispatch tests + 421 enforcement tests green** at the time of their commits.

---

## 2. The one thing to carry forward

Five separate defects this session shared a single shape: **a check whose name
describes a property it does not actually discriminate.**

- A `Finding` kind absent from `FINDING_KINDS` was counted and never printed. 56 tests green with a whole class of finding invisible.
- `main()` passed `armed=args.apply`, so the report said `WRITES ARMED (…is set)` one line before refusing because it was not set. The test called `format_report(armed=True)` **directly** — correct unit, untested wiring.
- Deleting the runner's entire sibling heartbeat beater left **67/67 green**, because the runner beats once before the child and once after `wait`. That beater is the only thing keeping a five-hour solver run from being reaped at its 90-minute TTL.
- `cancelled` collapsed into `finished` — only cancelling an *already-finished* job was covered.
- `client_infrastructure: []` in `.legal-deny-list.yaml` had been **empty since v2.0**, so the PII gate reported green while 133 files accumulated real hostnames.

The last one ran for months. **An empty rule list and a satisfied rule list produce
the same green tick.** Every one of these was found by mutation, never by the suite
passing.

**Working rule:** before trusting a guard, break it and confirm something fails.

---

## 3. Fleet finding — verified at four layers

`machine:ace-win-1` resolves to a **shared multi-tenant production box**, not the host
`registry.yaml` named (that name is absent from the tailnet entirely). Confirmed by
tailnet membership, `hostname` over SSH, the deckhand policy file present on the box,
and the live licensed-run agent.

Owner decision: **this is the intended steady state; correct the record.** Done in
`14d7c1914`.

The dangerous part was never the stale registry — it was that *"other people's
interactive sessions run here, cap concurrency"* existed only in the operator's head.
`capacity: heavy` is an honest description of the hardware and, read alone, invites
exactly the wrong conclusion. Now `shared_tenancy: true` with
`tests/dispatch/test_shared_tenancy_cap.py` enforcing it (5 tests, 3 mutations killed).

---

## 4. `workspace_root` is stored in THREE places

Correcting one turned "consistently wrong" into "inconsistent" and `sync-agent-configs.sh:947`
exits hard on divergence. All three are now aligned:

1. `config/workstations/registry.yaml`
2. `scripts/readiness/harness-config.yaml` (`ws_hub_path`)
3. `tests/readiness/test_registry_sso_completeness.py` — asserted the **literal**; now asserts the property (root is explicit and under `tier1_repo_root`)

**Note:** that check was ALREADY red before this session, on `macbook-portable`, from an
auto-sync commit. Both divergences are fixed. Because it was already failing, the second
fault changed nothing visible — a pre-existing red hiding a new one.

---

## 5. UNCOMMITTED work in the tree — deliberate, do not discard

~70 modified files. The hostname sweep is **partial**:

| lane | state |
|---|---|
| `docs/` | ✅ COMPLETE — 51 files, ~135 replacements, 0 remaining |
| `scripts/` `tests/` `config/` | ⚠️ PARTIAL — agent stopped mid-run; ~29 files still carry hostnames |
| `.claude/` `.planning/` `queue/` `state/` `data/` | ❌ NOT STARTED — ~38 files |

**The mapping is NOT restated here, on purpose.** It lives in
`.legal-deny-list.yaml` under `client_infrastructure`: each entry carries the real
hostname as its `pattern` and the correct role alias in its `description`. That file
is self-excluded from the scan (`exclusions[0]`), so it is the one place the pair can
be recorded without the record itself being the leak. Two of the three map to
`ace-win-1` and one to `ace-win-2`; read the descriptions for which.

Those entries are at **severity `warn`, deliberately** — arming `block` before the
sweep completes would fail the scan on the very commits that finish it. Flip to
`block` when a repo-wide grep for the three patterns returns nothing; build the grep
from the deny-list patterns rather than typing the hostnames into a script or a
commit message.

---

## 6. Next session — in order

1. **Finish the sweep** (2 lanes above), then flip the deny-list to `block`.
2. **GitHub-side: titles DONE, bodies REMAIN.**
   - ✅ **15 issue titles retitled** 2026-08-01: #34, #37, #52, #637, #677, #848, #860, #998, #1009, #1510, #2926, #3505, #3506, #3524, #3525. Verified by independent re-query — zero titles carry a hostname.
   - **The count was wrong before it was right.** An earlier pass in the same session reported *six*, having searched only two of the three patterns. Adding the third surfaced nine more, all but one CLOSED. **Closed issues are exactly as public and as indexed as open ones** — a scope estimate drawn from a partial search reads as a complete answer.
   - Method worth reusing: read the CURRENT title from the API (never a list captured earlier — a title edited in between would be silently overwritten with stale text), regex-substitute, print a dry run, then `--apply`. Full-token patterns only, so the `ANSYS` in a capability list like `OrcaWave/AQWA/ANSYS` survives as the software name it is.
   - ✅ **25 issue bodies + 13 PR bodies + 1 PR title swept** 2026-08-01. Re-verified: issues and PRs both report **0 titles, 0 bodies** carrying a hostname.
   - **One title needed a human, not a substitution.** PR #3279 originally read *"register &lt;real hostname&gt; as ace-win-1"* — a stated MAPPING, where replacing both sides yields the tautology *"register ace-win-1 as ace-win-1"*. Reworded by hand to *"register the licensed Windows host as ace-win-1"*. Wherever a hostname is the SUBJECT rather than a reference, mechanical replacement destroys the meaning while producing valid-looking output. Dry-run every substitution pass.
   - **Prior art worth knowing:** PR #3149 is `fix(pii): restore machine hostnames over-redacted by bare-ac…` — an earlier PII sweep matched too broadly and had to be reverted. Match on the FULL deny-list patterns, never a bare fragment; that is also why the `ANSYS` in `OrcaWave/AQWA/ANSYS` survives correctly as the software name.
   - **Independent corroboration:** PR #3279's original title confirms the identity mapping derived today from the tailnet.
   - ⚠️ **27 COMMENTS remain** (25 issues, 2 PRs) — the last GitHub surface. Distinct from bodies: GitHub stamps each edit visibly on a conversation record. Sampled authorship is 100% owner or `github-actions`, no third parties, so no one else's words would be rewritten. Awaiting an explicit scope decision.
   - Why this matters beyond tidiness: `config/ai-tools/provider-*.json` are snapshots of issue text that render into `docs/reports/provider-*`. Clean titles remove the main re-poisoning path; bodies may still feed some fields.
   - ✅ The one orphan `wip:` label naming a real host was deleted — 0 issues carried it, and `apply_wip` sets a state rather than a `wip:<host>` label, so nothing regenerates it. Its exact name is deliberately not written here; this document would otherwise reintroduce the string it records removing, which is the trap the docs lane found in an earlier PII-remediation note.
3. **Bare fragments remain** — `ws014`, `RDS02`, `ANSYS05` without the `acma-` prefix, ~75 occurrences. Same hostnames, outside the mapping used. Needs a scope decision.
4. **Mirrors will regress**: `.claude/memory/topics/` mirrors auto-memory living OUTSIDE the repo; `data/document-index/shards/` is generated. Cleaning the copy does not clean the source.
5. **Rename** `docs/session-handoffs/2026-07-14-rdp-microphone-ws014-rds02-exit.md` (hostnames in the filename). Referenced in 5 places, left intact so links do not break before the rename.
6. **65 failures in `tests/readiness/`** — none reference anything changed here, but no baseline was established. Triage.
7. **#3740 slice 5 + pilot drain** — gated behind the #3741 merge, deliberately. Creating `dispatch:active`/`dispatch:done` before anything writes them turns every `chain.py` WALL into a clean-looking `0`.
8. **Correct #3728's numbers** before it closes: the issue says 6 identities added / 4 removed. The real delta is **3 added, 0 removed, 6 re-pointed** — no task was lost.

---

## 7. Open owner decisions

1. **Git history** — the tree gets clean; history keeps the hostnames. Needs `filter-repo` + a force-push an agent cannot perform. *Recommendation: accept.*
2. **Three more identifier classes in the same public repo** — `/Users/krishna` (20 files), `Vamsees-MacBook-Air` (19), `shoerack` (12), `/home/undi` (12). A family member's name is arguably more sensitive than a server name. *Recommendation: sweep all four.*
3. **`digitalmodel` is also public** and not checked out here. *Recommendation: same sweep, separate PR.*
4. **Kanban boards** — retired as a routing input in #3736 and the largest single concentration. *Recommendation: delete rather than sanitize, if nothing consumes them.*

---

## 8. No external actions taken beyond

- Deleted the one orphan GitHub `wip:` label naming a real host (0 issues carried it, nothing regenerates it — `apply_wip` sets a state, not a `wip:<host>` label). Name deliberately not written here.
- Updated PR #3741's title and body.
- Pushed `recover/ace-win-1-autostash-equality-host-privacy` (preserved stash work; the stash on the box was never applied or dropped).

No merge was performed. No issue was retitled. No force-push. Nothing on `main`.
