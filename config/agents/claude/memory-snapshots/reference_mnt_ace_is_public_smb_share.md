---
name: reference-mnt-ace-is-public-smb-share
description: /mnt/ace (the 7.3T fleet bulk volume) is an unauthenticated guest-writable Samba share — never store client/personal data there in plaintext
metadata: 
  node_type: memory
  type: reference
  originSessionId: 936c9141-f607-4da0-8d22-7339ad27ad80
  modified: 2026-08-02T13:09:25.184Z
---

`/mnt/ace` on ace-linux-1 is **not** private storage. Verified 2026-08-02:

- `stat /mnt/ace` → mode **777**, owner `nobody:nogroup`
- `/etc/exports` → NFS-exported `rw` to ace-linux-2
- `/etc/samba/smb.conf` share `[ace_drive]` → `path = /mnt/ace`, `guest ok = yes`,
  `public = yes`, `writable = yes`, `browseable = yes`; `[global]` has
  `map to guest = bad user`

Net effect: **any device on the LAN can browse and write it with no credentials.**

Consequences for any "move bulk data to /mnt/ace" task:
- Client, personal, voice, and engineering material must be **encrypted** before
  it lands there (see [[reference-fleet-age-encryption-setup]]).
- `/mnt/local-analysis/_ace-preservation/PRESERVATION.md` states in its own header
  that it lives "OFF the /mnt/ace share" because it holds client marketing data —
  that is the owner's stated policy, not an inference.
- A `0700` subdirectory *should* block the guest (`nobody`) user, but this has
  **not** been empirically tested — verifying it needs sudo. Don't rely on it.

Note `/mnt/ace` on ace-linux-2 is a symlink to `/mnt/remote/ace-linux-1/ace`
(the NFS mount), so a path written as `/mnt/ace/...` there lands on the same
public volume.
