---
name: reference_ace_win_1_headless_verification_via_heartbeat
description: How to verify the ace-win-1 licensed-run agent is running headless from Linux (outbound-only architecture — heartbeat is the only channel)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9e2f9b19-69be-4afc-81f0-45e1882cd8c7
---

Deckhand licensed-run is **outbound-only**: there is NO inbound path from Linux
(ace-linux-1/2) into the Windows licensed host. The ONLY remote health signal is
the agent committing `queue/heartbeat/ace-win-1.json` to the private queue repo
`vamseeachanta/deckhand-licensed-runs-queue` (~every 20 min).

**Verify headless / always-on from Linux** (no host access needed):
- Read heartbeat via `gh api "repos/vamseeachanta/deckhand-licensed-runs-queue/contents/queue/heartbeat/ace-win-1.json?ref=<sha>" -H "Accept: application/vnd.github.raw"` (NOTE: local `base64 -d` is permission-blocked here — use the raw header to get decoded JSON).
- Payload fields: `{host, last_poll_at, pid, polls, schema}`. `polls` ≈ +71 per 20 min (15 s interval).
- **Reboot test** → detect a NEW `pid` (process restarted). **Logoff test** → the PASS signal is the SAME `pid` with `polls` climbing while logged off (process survived session teardown). An ONLOGON/InteractiveToken task DIES at logoff and freezes the heartbeat; Password/S4U survives.
- Single stable pid + monotonic polls = one agent process tree (partial CP2 evidence). Successful heartbeat commits = git pull/push healthy (partial CP4 evidence).

**Gotcha (the root cause):** the committed `scripts/deckhand/activate-ace-win-1.ps1`
registers the task `DeckhandLicensedRunAgent` as `schtasks /Create /SC ONLOGON /RL LIMITED`
(InteractiveToken — DIES at logoff, never runs before login). True always-on
requires **LogonType Password/S4U + an AtStartup trigger** (`Register-ScheduledTask
-Principal (…-LogonType Password) -Trigger (New-ScheduledTaskTrigger -AtStartup)`;
schtasks equiv `/SC ONSTART /RU <user> /RP <pw>`). ONLOGON is why ace-win-2 went
dark ~21h.

**Verified 2026-07-11 (both hosts headless):**
- ace-win-1: survived logoff (pid 12620 held, polls 215→286 logged-off) + reboot
  (re-launched with fresh pid 11784). → #529.
- ace-win-2: recovered from ~21h ONLOGON blackout after re-register as Password+AtStartup
  (headless prompt PR #547, in `docs/deckhand/licensed-run-host-handover-prompts.md`),
  then PASSED reboot test (new pid 10624 at boot → polls 1→77 stable). Close-out on #527.

Host-only literal checks (optional; must run ON the host): exact `Principal.LogonType`,
process count, and `%USERPROFILE%\.deckhand\licensed-run-agent.log` scan — waived here,
remote heartbeat evidence was conclusive. Failed run `lr_mkt-a_cd6fe46df9a4`
(aqwa-diffraction-solve) triaged in #546 (digitalmodel workflow bug, not agent fault).
Open follow-up: harden the canonical activator to default Password/S4U so no future host
repeats the ONLOGON blackout. Relates to [[project_bokalift_diffraction_licensed_run]].
