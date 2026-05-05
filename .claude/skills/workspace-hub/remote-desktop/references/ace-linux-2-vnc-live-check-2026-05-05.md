# ace-linux-2 VNC live check — 2026-05-05

Session learning from preparing ace-linux-2 for direct work handoff.

## Verified live state

From ace-linux-1/current computer:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 ace-linux-2 \
  'hostname; test -d /mnt/local-analysis/workspace-hub && echo WORKSPACE_OK || echo WORKSPACE_MISSING; command -v x11vnc || true; command -v vncserver || true; ss -ltnp 2>/dev/null | awk '\''NR==1 || /:5900|:5901|:5902/'\'''
```

Observed:
- SSH to `ace-linux-2` works.
- `/mnt/local-analysis/workspace-hub` exists.
- `x11vnc` installed at `/usr/bin/x11vnc`.
- `vncserver` installed at `/usr/bin/vncserver`.
- Remote listeners:
  - `127.0.0.1:5900` via `x11vnc`
  - `127.0.0.1:5901` via `Xtigervnc`

Local state:

```bash
command -v xtigervncviewer
ss -ltnp 2>/dev/null | awk 'NR==1 || /:5900|:5901|:5902/'
pgrep -af 'xtigervncviewer|vncviewer|ssh .*5900.*ace-linux-2'
```

Observed:
- Local viewer at `/usr/bin/xtigervncviewer`.
- Active tunnel: `ssh -L 5900:localhost:5900 vamsee@ace-linux-2 -N`.
- Active viewer: `xtigervncviewer localhost:5900`.

## Safe tunnel probe

Use an alternate local port to verify remote VNC without disturbing an existing viewer/tunnel:

```bash
ssh -fN -o ExitOnForwardFailure=yes -o BatchMode=yes -o ConnectTimeout=8 \
  -L 15900:localhost:5900 ace-linux-2

timeout 3 bash -c 'cat < /dev/null > /dev/tcp/127.0.0.1/15900' && echo TCP_CONNECT_OK
pkill -f 'ssh -fN.*15900:localhost:5900.*ace-linux-2' || true
```

## Pitfall

Do not assume the skill/docs script path is current. In this session the loaded skill referenced `scripts/operations/connection/vnc-dev-secondary.sh`, but the actual repo script was `scripts/operations/connection/vnc-ace-linux-2.sh`.
