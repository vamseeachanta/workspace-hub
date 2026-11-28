# Organisation and team map (generic part)

Source of truth: [`org-team.yaml`](org-team.yaml). Verified 2026-11-27T15:45Z.
Private detail (desk-to-host and seat assignment, schedules, client teams, live
sessions per machine, deviations): fleet-ops `docs/knowledge-maps/org-team.yaml`
(private repository; access is limited to the maintainer's team).

## What the map covers

The map names each role type in the engineering ecosystem, what it may decide,
what it never does, the channels it writes to, and the hand-offs between roles
and between AI providers. People appear by role only. Clients appear only as a
generic "client delivery team" type in this public file.

## Decision rights

| Decided by | Items |
|---|---|
| Owner only | Client-facing emails and messages, and anything sent or posted in the owner's name |
| Owner only | Spending money: paid licences, hosted minutes, purchases, cloud credit |
| Owner only | Items the owner already holds, until the owner answers |
| Owner only | Sign-in, account and banked-reset steps; owner records such as `status:plan-approved` |
| Team | Everything else, irreversible steps included, each logged on the irreversible-step issue before it runs and backed up first |
| Team | Merges on green required checks: pinned squash, no branch delete, never `--admin`, never while BLOCKED |
| Team | Releasing a merge hold after the head is checked against the base branch, then merging, with the owner informed (owner ruling, 27 Nov 2026) |
| Nobody | Handling passwords, tokens, card or bank details; force-push; client names in public repositories |

Table 1. Decision rights. Sources: `AGENTS.md`, `config/agents/SHARED_SOUL.md`
(Authorization), `.claude/rules/merge-authorization.md`.

Owner decisions that need more than one line go on a local HTML decision board
with the recommendation marked (`.claude/rules/human-decision-boards.md`). A
card left undecided is not consent.

## Role types

| Role | Does | Never |
|---|---|---|
| Owner | Direction, rulings, sign-ins, board answers | Is asked routine questions in chat |
| Intake desk | Ids, classes, routes and closes every owner request with evidence | Does the work itself; sends in the owner's name |
| Intake failover desk | Carries Intake while its seat is out, between start and end ledger rows | Touches personal data or the owner's local folders |
| Senior PM desk (coordinator) | Dispatch, supply, review of Codex work, integration, merges on green | `--admin`; merges a client-side agent's PR |
| Road-map execution pass | Takes each stream's next step, briefs Codex, reviews, integrates | Takes owner-held, client-waiting or held steps |
| Train workers (Claude) | Fix and review rounds at the current head | Merges |
| Codex lane jobs | Implementation and fix rounds from a brief; writes a RESULT file | Commits for the desk; drives a licensed solver |
| Codex standby desks | Intake and PM duties when a Claude seat is out | Starts a Claude session |
| Engineering lanes | Product manager rulings, delivery lead, solver manager loop, analysis desks | Sends to a client; puts a model in the licensed chain |
| Machine manager (one per host) | Hourly host verdict and the actions the PM should take; runs queued Agy jobs | Deletes or prunes by hand; pushes; places jobs |
| Agy lane (third provider) | Advisory reviews, plain-English and register passes, files only | Edits, posts, merges or pushes |
| Writers desk and specialist agents | Writer charters, checks from repeated owner comments, review gate | Writes client deliverables; merges |
| Coordinator role agents | scout, builder, gap-checker, explorer, reporter, verifier, two domain specialists | Integrate, push, label or close |
| Stewards | Dashboards, seat pace, article curation, storage | Change permissions or guardrails |
| Host conductor (no model) | Starts due desk slots and signed jobs; writes heartbeats | Judges |
| Licensed solver path (no model) | Scheduled-Task dispatch; one Orcina slot | Has a model in the chain |
| Client delivery team (per client) | One client's road map, topic desk and deliverables in the client's private wiki | Sends to the client; links one client to another |

Table 2. Role types. Full fields per role are in `org-team.yaml` `entries`.

## Hand-off patterns

1. Owner to Intake (chat, review saves, owner inbox) produces one ledger row
   per ask with id, class, owner and due time.
2. Intake routes by class: client work to the client's delivery lead,
   engineering products to the product manager, fleet work to the senior PM,
   business to the business owner, personal work to the personal desk.
3. Senior PM to Codex: a brief file in a worktree; Codex returns a RESULT file
   and a diff, never a commit.
4. Codex writes, Claude reviews at the current head with the tests re-run.
   Claude-authored work gets a Codex review. Author and reviewer always differ.
5. Agy gives a third-provider advisory review from files only; a Claude desk
   checks each finding and posts it. Agy never posts.
6. Desk to machine manager through an act-list, inbox or `machine:<host>`
   issue; manager back to the desk through its host report. Removals run only
   from reviewed manifests.
7. Any desk to the owner only for owner-held items: a board card or one dated
   sentence in the to-owner file.
8. Any irreversible step is logged on the irreversible-step issue before it
   runs, with a backup first.
9. A client-side agent's PR on a client wiki is verified by a review-only Claude
   worker; the client side merges it, the team does not.

Reviews are advisory at every stage: a real bug gets a fix round, and no
verdict is a merge gate (`config/agents/SHARED_SOUL.md`, Cross-Review Routing).

## Channel types

- Ledger rows: one JSON line per event; the channel name states the desk and
  the direction ("... to the Writers desk").
- Issue logs: the irreversible-step and PR-sweep log, the `/goal` catalog
  (workspace-hub#2695), `machine:<host>` issues and idle-check issues.
- Decision boards: local HTML, one card per decision, JSON saved beside the page.
- Desk files: owner inbox, to-owner, outboxes, desk logs, act-lists, host reports.
- PR comments with a fixed first line per reviewer provider.
- Hold registers: basis holds and merge holds, each with hold and release rows.
- Road-map stream file and its page; the seat usage file
  `config/ai-tools/account-usage-latest.json`.

## Host role types

Hosts take one of six role types from `config/agents/host-role-routing.yaml`:
coordinator, lane-runner, tool-runner, overflow, portable, inactive. The
assignment of desks to hosts is private.

## Deviations and open questions

The private detail file lists 20 deviations (roles on a different host or seat
from the routing file, desks with no recent ledger activity, and conflicting
statements of decision rights between files) and 8 open questions. None is
reproduced here.

## Refresh

Weekly, and after any owner ruling on decision rights. Regenerate this file
from the private detail without host, seat, schedule, client or deviation detail.
