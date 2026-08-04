---
name: reference-fleet-age-encryption-setup
description: "age encryption for fleet bulk storage — one keypair, private key on ace-linux-1 only, plus the per-machine install paths and PATH gotcha"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 936c9141-f607-4da0-8d22-7339ad27ad80
  modified: 2026-08-02T13:09:41.260Z
---

Set up 2026-08-02 so bulk data can be relocated to the LAN-public
[[reference-mnt-ace-is-public-smb-share]] without exposing it.

**Design:** ONE keypair. Public key (`~/.config/age/recipients.txt`) on all three
machines so any can encrypt; private key (`~/.config/age/keys.txt`, `0600`) on
**ace-linux-1 only**, so decryption is centralized.

**Install paths differ per machine** — no passwordless sudo except gpu-claw:
- ace-linux-1 → conda-forge, `~/miniforge3/bin/age`
- ace-linux-2 → Homebrew, `/home/linuxbrew/.linuxbrew/bin/age` (no sudo available)
- gpu-claw → apt, `/usr/bin/age` (passwordless sudo works here)

**PATH gotcha:** only gpu-claw's `age` is on a non-interactive shell's PATH.
Scripts must locate it themselves rather than relying on login-shell config —
same thing the ace-linux-2 crontab already does with `PATH=$HOME/.local/bin:$PATH`.
On ace-linux-2, `~/.local/bin` is *not* on the default non-interactive PATH.

**Verify a rotation is real** with a negative test, not just a round-trip: the
old identity must fail to decrypt new-key ciphertext
(`age: error: no identity matched any of the recipients`).

**Backup problem, unresolved as of 2026-08-02:** ace-linux-1 is headless
(`DISPLAY`/`WAYLAND_DISPLAY` unset) so `xclip` has no server and `wl-copy` isn't
installed; `age -p` fails with "standard input is not a terminal, and /dev/tty is
not available". Getting a secret off that box without putting it in the session
transcript requires either a real terminal or `rclone` to `gdrive:`.
Never `cat` a private key — it lands in the Claude Code transcript.
