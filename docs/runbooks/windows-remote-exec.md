# Runbook — give a Windows fleet host an inbound SSH channel

**Applies to:** `ace-win-1`, `ace-win-2` · **Issue:** workspace-hub#3721 · **Related:** #3723, deckhand#579, deckhand#581

**Time:** ~5 minutes per host. **Access:** remote desktop to the box. **Rights:** audit needs none; provisioning needs an elevated PowerShell.

---

## Why you are doing this

Both Windows hosts are in `manual_hosts` in `config/fleet-ssh-hosts.yml`, so no fleet automation can reach them. Consequences already measured:

- The 2026-07-30 fleet branch/worktree sweep covered **3 of 5 machines**; neither Windows host could be swept.
- Equality evidence went **3.5 days** and **11.8 days** stale without anyone noticing (#3724).
- A 17-day heartbeat outage on one host could not be diagnosed remotely.

One SSH service converts each box from "manual, therefore stale" into "swept like everything else".

---

## Step 0 — know which box you are on

Do not assume the fleet token. deckhand#579/#581 are still settling which physical machine each token denotes, and an alias stayed bound to a retired machine for ~18 days undetected. **The audit in Step 1 prints the real identity — read it before doing anything else.**

If the audit reports a hostname you did not expect, stop and report it on #3721 rather than provisioning.

---

## Step 1 — audit (safe, changes nothing, no admin needed)

Open PowerShell, `cd` to the workspace-hub checkout (`D:\workspace-hub` on the Windows boxes), and run:

```
git pull --ff-only
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\enable-remote-exec.ps1
```

You get a section per area — Identity, OpenSSH Server, Authorized keys, Firewall, Default shell, Licensed-run poller — with `[ok]`, `[gap]`, and `[info]` lines, plus an evidence JSON path at the end.

**Expected outcomes:**

| What the audit says | What it means | Next |
|---|---|---|
| `sshd service: Running` and no gaps | This host is already reachable | Skip to Step 4 and just verify |
| `sshd service is absent` | OpenSSH Server not installed | Step 2 |
| `sshd is not running` / `start type is Manual` | Installed but won't survive reboot | Step 2 |
| `tailscale.exe not found` | No private transport — **stop** | Report on #3721; do not open 22 without one |

The audit exits non-zero when gaps remain, so it can later be scheduled as an alarm.

---

## Step 2 — provision (elevated)

Close PowerShell and reopen it as **Run as administrator**. You need the operator public key — get it from ace-linux-1 with `cat ~/.ssh/id_ed25519.pub` (or whichever key you use for the fleet).

```
cd D:\workspace-hub
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\enable-remote-exec.ps1 -Apply -PublicKey "ssh-ed25519 AAAA...REPLACE_ME... operator@ace-linux-1"
```

Every step is idempotent — re-running is safe and does nothing already done.

It will, only as needed: install the `OpenSSH.Server` capability, set `sshd` to Automatic and start it, append your key to the **correct** `authorized_keys` for your account type and lock its ACL, and create a firewall rule scoped to the tailnet range.

**It deliberately does not touch the licensed-run poller.** Whether that should run on a given host is deckhand#579's decision.

---

## Step 3 — password auth stays on until keys are proven

Do **not** disable password authentication yet. Prove key auth works from ace-linux-1 (Step 4) while you still have a working fallback and a remote-desktop session open. Locking yourself out of a box you can only reach by RDP is the one expensive mistake available here.

Once Step 4 passes, disable password and root login by editing `%ProgramData%\ssh\sshd_config`:

```
PasswordAuthentication no
PermitRootLogin no
```

then `Restart-Service sshd`. Keep the RDP session open until you have re-verified Step 4 after the restart.

---

## Step 4 — verify from ace-linux-1

Run these **on ace-linux-1**, not on the Windows box:

```bash
# 1. basic reachability
ssh -o BatchMode=yes <host> 'hostname'

# 2. THE ONE THAT MATTERS — exit code, not just output
ssh -o BatchMode=yes <host> 'exit 7'; echo $?     # must print 7, not 0
```

The second check is the acceptance criterion in #3721. The fleet helpers branch on exit status, and a wrong default shell can return correct stdout while losing the exit code — which reads as success everywhere. If it prints `0`, the channel is not usable for automation even though it looks fine.

---

## Step 5 — take the host out of `manual_hosts`

Once Step 4 passes, `config/fleet-ssh-hosts.yml` is stale for this host. **Do not hand-edit it** — that file being hand-maintained is exactly what caused a wrong issue to be filed (#3720, closed). #3723 tracks deriving it from the generated reachability matrix. Comment your verification evidence on #3721 and reference #3723.

---

## Step 6 — refresh this host's equality evidence

While you are on the box, close the staleness gap (#3724):

```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\equality-report.ps1
```

---

## Agent prompt (if you would rather have Claude drive it on-box)

Both Windows hosts have Claude installed. Paste this into a Claude session **on the Windows box**:

> You are on a Windows fleet host in the workspace-hub ecosystem. Follow
> `docs/runbooks/windows-remote-exec.md` exactly, for workspace-hub#3721.
>
> 1. `cd D:\workspace-hub` and `git pull --ff-only`.
> 2. Run the audit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\enable-remote-exec.ps1`
> 3. **Show me the full audit output and stop.** Do not pass `-Apply` yet.
>
> Rules for this task:
> - Report the identity the audit prints. If the hostname is not what the fleet
>   token implies, STOP and tell me — deckhand#579/#581 are unresolved and an alias
>   was previously bound to a retired machine for ~18 days.
> - If `tailscale.exe` is not found, STOP. Do not open port 22 without a private
>   transport.
> - Never disable password authentication before key auth is proven from
>   ace-linux-1. I will run that verification myself.
> - Do not start, stop, or reconfigure the licensed-run poller — that is
>   deckhand#579's decision, not this task's.
> - Do not hand-edit `config/fleet-ssh-hosts.yml`; #3723 covers it.
> - This is a PUBLIC repo. Never put a physical hostname, client name, tailnet
>   address, or account principal into a commit message, issue comment, or any
>   tracked file. Use the neutral tokens `ace-win-1` / `ace-win-2` only.
>
> After I approve the audit, I will give you the public key and you may re-run with
> `-Apply` in an elevated shell.

The stop-after-audit shape is deliberate: the identity question has to be answered by a human before anything mutates.

---

## If something goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| Key auth refused, key looks right | Admin account, key in the wrong file, or ACL too permissive | Key must be in `%ProgramData%\ssh\administrators_authorized_keys`, ACL Administrators + SYSTEM only. The `-Apply` path does both. |
| `ssh` connects, commands run, exit code always 0 | Default shell mishandles non-interactive exit | Set `HKLM:\SOFTWARE\OpenSSH\DefaultShell` to a predictable shell, restart `sshd`, re-verify Step 4 |
| Connects on LAN, not over tailnet | Firewall rule scoped to the wrong range | Check the audit's Firewall section; the rule should allow `100.64.0.0/10` |
| `Add-WindowsCapability` fails | Not elevated, or WSUS-managed build | Re-open PowerShell as administrator; if it still fails, report the exact error on #3721 |
