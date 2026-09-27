# Handoff — client-e proj-b consolidation session exit (2026-06-11)

Fresh-agent pickup doc. Working dir: `/mnt/local-analysis/deckhand`. This session
completed client-e Deckhand onboarding, verified the credential path end-to-end,
consolidated the race-car project record, and opened the work backlog.

## What is DONE and verified (do not redo)

1. **client-e credential path live.** `llm-wiki-client-e` was added to the deckhand-scopes
   GitHub App installation (id 138887856). `python -m deckhand.app_token
   DECKHAND_PAT_client-e` mints; `protect-and-verify.sh verify-pat` passes; route probe
   resolves Telegram group `-5270275602` → `DECKHAND_PAT_client-e` via routes A and B;
   read/write canary on a throwaway branch passed; out-of-scope boundary 404 holds.
   Focused tests: 62 passed / 1 skipped. Background knowledge:
   `~/.claude/projects/-mnt-local-analysis-deckhand/memory/deckhand-scopes-app-installation.md`
   (adding repos to the installation is web-UI-only; API PUT 403s for CLI tokens).
2. **Project record consolidated and PUSHED** to `vamseeachanta/llm-wiki-client-e`
   (commits `8243594`, `7d142b5`): `projects/proj-b/` holds email-thread
   digests, WRK-5082/1362/1364 chute-frame analysis basis + reports, and the
   `T1 Suzuka Aero.zip` manifest. See the project README for the full registry.
3. **Raw zip staged locally** (NDA-covered, out of git per `DATA-CYCLE.md`):
   `/mnt/local-analysis/client-e-raw/T1-Suzuka-Aero.zip` (29.5 MB, Drive id
   `1W_UexKKC-ueg7UH3nBMMMNliseQHRMfb`). Key finding: **no CAD geometry inside** —
   only 2016–2018 wind-tunnel test-note photos + a few XLS/DOC.
4. **Backlog opened:** `llm-wiki-client-e` issues #1–#5 (CFD verdict, stress-assumption
   verification, geometry checks, 285-mph aero study, /mnt/ace/client-e mount).
5. **yq v4.53.3** installed at `~/.local/bin/yq`; workspace-hub
   `check-client-wiki-registry.sh` passes.

## Local commits NOT pushed (ask user before pushing)

| Repo | Commits | Content |
|---|---|---|
| deckhand | `929fdbd` | client-e scope onboarding (scopes.yml, voice map, ONBOARDING) |
| workspace-hub | `371cbf3e7`, `41e064667` | client-wikis client-e entry + handoff doc; proj-b Rule E roster |
| aceengineer-strategy | `1a32690` | client-e outreach/pamphlet/roster package |

deckhand history mostly lands via PRs; the other two take direct main pushes.
Unrelated dirty state in all three repos was deliberately preserved — commit only
explicit client-e pathspecs.

## Most urgent next action

**Issue #1** (https://github.com/vamseeachanta/llm-wiki-client-e/issues/1): the
data-sufficiency verdict owed to the client since ~Jun 5 (client nudged twice).
The analysis is essentially done — zip lacks geometry, so CFD needs a 3D scan or
sourced CAD. Draft the verdict + data-path recommendation + effort estimate and
send via the email thread (Gmail `19e1966b1f6b5865`) or the client-e Telegram channel.
Client contact details are in the digests under
`projects/proj-b/extracted/correspondence/` — do not copy PII here.

## Open observations (not yet actioned)

- **Live canary scorer false-positives:** the only client-e live exchange (2026-06-11,
  an admin/setup ask) FAILs `protocol/probe-confirm` and `protocol/options`
  mechanically, but the probe→options protocol targets engineering questions.
  Candidate carve-out for the deckhand#79 routing-maintenance loop.
- **Bot writes were local-only:** the live bot created the project scaffold in its
  workdir without committing/pushing (now superseded by this session's commits).
  Worth a charter/routing decision: bot should push or say "drafted locally".
- `/mnt/local-analysis` filesystem ignores POSIX perms (chmod no-op) — the staged
  NDA zip cannot be permission-restricted there; factor into issue #5.

## Suggested skills

- `triage` — work the new llm-wiki-client-e issues #1–#5 into priority order / assignments.
- `verify` — re-run the credential canary chain if anything in scopes.yml changes.
- `voice-internals-sweep` — after more live client-e chat accumulates, curate voice
  compliance (and feed the probe-confirm carve-out evidence into #79).
- `writing-shape` — drafting the client-facing verdict letter for issue #1 from
  the manifest + correspondence digests.
