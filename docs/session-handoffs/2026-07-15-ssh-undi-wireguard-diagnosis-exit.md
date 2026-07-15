# Session handoff — `Undi` WireGuard/SSH diagnosis (2026-07-15)

## Active task

Restore SSH connectivity from `ace-linux-1` to
`undi@192.168.184.142` through the NetworkManager WireGuard connection
`Undi`.

## Outcome

SSH was not restored. The failure was isolated below the SSH protocol: the
local WireGuard interface transmits packets but receives no response from its
configured remote peer. Username, SSH keys, host-key verification, and the
remote SSH daemon cannot be evaluated until the tunnel has a working
handshake.

## Evidence

- `ssh -o BatchMode=yes -o ConnectTimeout=8 undi@192.168.184.142 true`
  exited `255` with `Connection timed out` before receiving an SSH banner.
- `ip route get 192.168.184.142` selected interface `Undi` with source
  `10.200.253.11`.
- The route `192.168.184.0/24` is installed through `Undi` with metric `50`.
- ICMP to the target and TCP probes to ports 22, 80, and 443 received no
  response.
- `sudo wg show Undi` reported no `latest handshake`, `0 B received`, and
  transmitted traffic. The peer is configured for an IPv6 endpoint on
  UDP/443; the exact endpoint and peer keys are intentionally omitted here.
- Local public IPv6 is healthy: the Cloudflare IPv6 resolver replied to three
  probes with zero loss. The configured peer endpoint replied to none.

## Root-cause boundary

The verified boundary is the remote WireGuard peer or the path to its UDP/443
endpoint. Remaining causes are:

1. the remote peer is offline;
2. its delegated public IPv6 prefix changed and the local endpoint is stale;
3. WireGuard is not listening on UDP/443 remotely; or
4. a host/router/firewall rule is dropping UDP/443.

The available evidence does not distinguish those remote-side causes.

## Exact next checkpoint

On the remote WireGuard peer, run:

```bash
ip -6 addr show scope global
sudo ss -lunp | grep ':443'
sudo wg show
sudo systemctl --type=service --state=running | grep -Ei 'wg-quick|wireguard|NetworkManager'
```

Compare the remote machine's current public IPv6 with the endpoint shown by
`sudo wg show Undi` on `ace-linux-1`. Correct a stale endpoint or restore the
remote listener/firewall, then reconnect locally:

```bash
nmcli connection down Undi
nmcli connection up Undi
sudo wg show Undi
```

Only retry SSH after `wg show` displays a recent handshake and nonzero received
bytes.

## Separate shell warning

Interactive shells print:

```text
bash: /home/vamsee/.cargo/env: No such file or directory
```

`~/.cargo` is a symlink to `/mnt/ace/build/codex-desktop/.cargo`; that target
does not contain `env`, `cargo`, or `rustup`. Both `~/.profile` and `~/.bashrc`
source `~/.cargo/env` unconditionally. No shell configuration was changed.
If Rust is intentionally absent, guard both source lines with:

```bash
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
```

## Repo and external-action state

- No GitHub issue was opened or changed; this was a local, read-only diagnosis.
- No VPN, SSH, firewall, remote-host, or shell configuration was changed.
- The primary `workspace-hub` checkout was already divergent and contained
  unrelated untracked handoffs. It was not modified by this session.
- This handoff is the only repository artifact created for the diagnosis.

## Suggested skills

- `diagnose` or `superpowers:systematic-debugging` to continue the
  evidence-first network diagnosis.
- `coordination/pre-completion-cleanup-audit` before the next closeout.

## Blocker

Remote-peer access or coordination is required to verify its current public
IPv6 address, WireGuard listener, and UDP/443 firewall path.
