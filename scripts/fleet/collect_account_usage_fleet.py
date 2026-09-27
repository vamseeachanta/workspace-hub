#!/usr/bin/env python3
"""Fan the account-usage probe over the fleet and publish one per-ACCOUNT view.

Runs on the fleet collector VM (cron, see scripts/fleet/account-usage-cron.sh).
For every host in config/ai-tools/ai-accounts.yaml it pipes
scripts/ai/assessment/collect-account-usage.py over ssh stdin (so remote
checkouts need not be current), then groups the samples by account: an
account's usage is the same from every host logged in as it, so the freshest
successful sample wins. The aggregate ends with a ``recommendation`` per
provider -- which account has the most weekly headroom and which hosts hold it
-- for agents and dispatch to read before starting a marathon.

Outputs (paths relative to the repo root unless absolute):
  --out   config/ai-tools/account-usage-latest.json
  --md    docs/reports/ai-account-usage.md

Public names only (owner decision H01). ai-accounts.yaml is PUBLIC and names
every host by its logical fleet label, including inside an ``ssh`` argv list
(``user@ace-win-2``). The collector resolves those labels to physical names at
run time from the private map of scripts/fleet/fleet_snapshot_labels.py
(--label-map, else $FLEET_LABEL_MAP, else ~/.config/workspace-hub/
fleet-label-map.txt) and never prints or writes the resolved argv. Before
writing, the rendered outputs are checked against that map and the hostname
pattern. Fail closed: a missing map, a config value that is not a label, or an
output that would carry a physical name writes nothing and exits 2.
Diagnostics never print a machine name.

Exit 0 when at least one host answered, 1 when none did (nothing published),
2 on a configuration or labelling error (nothing published).

Usage:
  collect_account_usage_fleet.py [--config PATH] [--out PATH] [--md PATH]
                                 [--hosts a,b] [--ssh-timeout S] [--dry-run]
                                 [--label-map PATH]
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet_snapshot_labels as fsl  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "scripts/ai/assessment/collect-account-usage.py"
DEFAULT_CONFIG = REPO_ROOT / "config/ai-tools/ai-accounts.yaml"
DEFAULT_OUT = REPO_ROOT / "config/ai-tools/account-usage-latest.json"
DEFAULT_MD = REPO_ROOT / "docs/reports/ai-account-usage.md"
PROVIDERS = ("claude", "codex")

# Remote launcher: python3 where it actually RUNS (Linux/macOS), else python
# (Windows Git Bash: python3 is the Microsoft Store redirector stub — it passes
# `command -v` but exits 49 "Python was not found" — so verify execution, not presence).
REMOTE_CMD = ("sh -c 'if python3 -c \"import sys\" >/dev/null 2>&1; then exec python3 - \"$@\"; "
              "else exec python - \"$@\"; fi' _ --json --host {label}")


def load_config(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.stderr.write("PyYAML missing: apt install python3-yaml (or pip install pyyaml)\n")
        sys.exit(2)
    text = path.read_text(encoding="utf-8")
    if fsl.HOSTNAME_SHAPE_RE.search(text):
        sys.stderr.write(f"{path.name}: a hostname-shaped value is present; hosts are named by fleet label only\n")
        sys.exit(2)
    cfg = yaml.safe_load(text) or {}
    for key in ("accounts", "hosts"):
        if not isinstance(cfg.get(key), dict) or not cfg[key]:
            sys.stderr.write(f"{path}: missing or empty '{key}'\n")
            sys.exit(2)
    for label, host in cfg["hosts"].items():
        if not fsl.is_public_label(label):
            sys.stderr.write(f"{path.name}: a host key is not an approved fleet label\n")
            sys.exit(2)
        ssh = (host or {}).get("ssh")
        if isinstance(ssh, str) and not fsl.is_public_label(ssh):
            sys.stderr.write(f"{path.name}: host {label}: ssh alias is not an approved fleet label\n")
            sys.exit(2)
    for label, host in cfg["hosts"].items():
        for prov in PROVIDERS:
            acct = (host or {}).get(prov)
            if acct and acct not in cfg["accounts"]:
                sys.stderr.write(f"{path}: host {label} names unknown account {acct}\n")
                sys.exit(2)
    cfg.setdefault("policy", {})
    return cfg


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def parse_iso(value) -> dt.datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        d = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


# PowerShell-native probe launcher for Windows hosts whose OpenSSH default
# shell (cmd) cannot run the sh-based REMOTE_CMD. Probes python3/python by
# execution (the Microsoft Store python3 stub passes `where` but fails to
# run), then runs the winner with the probe script inherited on stdin.
PS_LAUNCHER = (
    "$ErrorActionPreference='SilentlyContinue';"
    "$py='';foreach($c in 'python3','python'){"
    "& $c -c 'import sys' 2>&1|Out-Null;"
    "if($LASTEXITCODE -eq 0){$py=$c;break}};"
    "if($py -eq ''){Write-Error 'no working python found';exit 3};"
    "& $py - --json --host '{label}'"
)


_SSH_TARGET_RE = re.compile(r"^(?:(?P<user>[^@\s]+)@)?(?P<host>[A-Za-z0-9][A-Za-z0-9.-]*)$")


def _physical_for(label: str, table: dict[str, str]) -> str:
    """The one physical name the private map gives for a fleet label."""
    phys = [k for k, v in table.items() if v == label and k != label.casefold()]
    if len(phys) > 1:
        raise fsl.LabelError("a fleet label maps to more than one physical name")
    if phys:
        return phys[0]
    if table.get(label.casefold()) == label:
        return label  # identity entry: the label is itself the reachable name
    raise fsl.LabelError("a fleet label in an ssh argv is not in the label map")


def resolve_ssh_argv(argv: list, table: dict[str, str]) -> list[str]:
    """Replace every ``label`` / ``user@label`` element with its physical name.

    The config must name hosts by label only: an element that is a physical
    name the map knows is refused. The returned argv is for exec only; it is
    never printed or written.
    """
    out: list[str] = []
    for raw in argv:
        arg = str(raw)
        m = _SSH_TARGET_RE.match(arg)
        if m and fsl.is_public_label(m.group("host")):
            user = m.group("user")
            phys = _physical_for(m.group("host"), table)
            arg = f"{user}@{phys}" if user else phys
        elif m and m.group("host").casefold() in table:
            raise fsl.LabelError("an ssh argv names a physical host; use its fleet label")
        out.append(arg)
    return out


def assert_publishable(text: str, table: dict[str, str]) -> None:
    """Refuse output that carries a mapped physical name, a fragment or a hostname shape."""
    fsl.assert_no_physical(text, table)


def run_probe(label: str, host: dict, ssh_timeout: int, probe_src: bytes,
              table: dict[str, str] | None = None) -> dict:
    """Return the probe record for one host, or a record with reachable=False."""
    if host.get("local"):
        cmd = [sys.executable, str(PROBE), "--json", "--host", label]
        stdin = None
    else:
        ssh_spec = host.get("ssh") or label
        if isinstance(ssh_spec, list):
            # Full argv prefix, e.g. a double-hop through a jump host when the
            # target does not accept this VM's key on a direct path. The config
            # names hosts by label; resolve them from the private map, or do not
            # probe at all.
            if table is None:
                return {"host": label, "reachable": False, "note": "ssh labels unresolved (no label map)"}
            try:
                base = resolve_ssh_argv(ssh_spec, table)
            except fsl.LabelError:
                return {"host": label, "reachable": False, "note": "ssh labels unresolved"}
        else:
            base = ["ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={ssh_timeout}",
                    "-o", "StrictHostKeyChecking=accept-new", ssh_spec]
        remote_cmd = REMOTE_CMD.format(label=shlex.quote(label))
        if host.get("remote_wrap") == "powershell":
            # Powershell-native launcher (see PS_LAUNCHER): the probe script
            # on stdin is inherited by the winning python.
            ps_script = PS_LAUNCHER.replace('{label}', label.replace("'", "''"))
            encoded = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")
            cmd = base + ["powershell", "-NoProfile", "-EncodedCommand", encoded]
        else:
            cmd = base + [remote_cmd]
        stdin = probe_src
    try:
        proc = subprocess.run(cmd, input=stdin, capture_output=True, timeout=ssh_timeout + 40)
    except subprocess.TimeoutExpired:
        return {"host": label, "reachable": False, "note": "timeout"}
    except OSError as exc:
        return {"host": label, "reachable": False, "note": f"{type(exc).__name__}"}
    text = proc.stdout.decode(errors="replace").strip()
    start = text.find("{")
    if proc.returncode != 0 or start < 0:
        err = proc.stderr.decode(errors="replace").strip().splitlines()
        return {"host": label, "reachable": False, "note": f"exit {proc.returncode}",
                "stderr_tail": err[-2:]}
    try:
        rec = json.loads(text[start:])
    except ValueError:
        return {"host": label, "reachable": False, "note": "unparseable probe output"}
    rec["host"] = label
    rec["reachable"] = True
    return rec


def headroom(sample: dict | None) -> float | None:
    if not sample or sample.get("week_pct") is None:
        return None
    try:
        return round(100.0 - float(sample["week_pct"]), 1)
    except (TypeError, ValueError):
        return None


LIVE_SOURCES = ("oauth-api", "app-server-live")
_EPOCH = dt.datetime.min.replace(tzinfo=dt.timezone.utc)


def sample_rank(sample: dict) -> tuple:
    """Order samples of one account: live sources first, then by the sample's own time.

    A live answer (OAuth endpoint, codex app-server) describes the account now.
    A session-log line describes the account at the moment that session last
    ran, so its ``sampled_at`` -- not the probe's ``captured_at`` -- is its age.
    """
    live = 1 if sample.get("source") in LIVE_SOURCES else 0
    when = parse_iso(sample.get("sampled_at")) or parse_iso(sample.get("captured_at")) or _EPOCH
    return (live, when)


def aggregate(cfg: dict, records: list[dict], at: dt.datetime | None = None) -> dict:
    """Pure function: group per-host probe records into the per-account aggregate."""
    at = at or now()
    policy = cfg.get("policy") or {}
    max_age = dt.timedelta(hours=float(policy.get("max_sample_age_hours", 12)))
    tight = float(policy.get("tight_headroom_pct", 10))
    margin = float(policy.get("switch_margin_pct", 15))
    warnings: list[str] = []

    hosts_out: dict[str, dict] = {}
    samples: dict[str, list[dict]] = {a: [] for a in cfg["accounts"]}
    for label, host_cfg in cfg["hosts"].items():
        rec = next((r for r in records if r.get("host") == label), None)
        entry = {"reachable": bool(rec and rec.get("reachable")),
                 "accounts": {p: host_cfg.get(p) for p in PROVIDERS if host_cfg.get(p)}}
        if rec and not rec.get("reachable"):
            entry["note"] = rec.get("note")
        if rec and rec.get("reachable"):
            entry["captured_at"] = rec.get("captured_at")
            entry["fingerprints"] = {}
            for prov in PROVIDERS:
                probe = (rec.get("providers") or {}).get(prov) or {}
                acct = host_cfg.get(prov)
                fp = probe.get("fingerprint")
                if fp:
                    entry["fingerprints"][prov] = fp
                if probe.get("source", "unavailable") == "unavailable":
                    entry.setdefault("unavailable", {})[prov] = probe.get("error", "unavailable")
                if not acct:
                    if probe.get("source", "unavailable") != "unavailable":
                        warnings.append(f"{label}: {prov} is logged in but ai-accounts.yaml maps no account")
                    continue
                expected_fp = (cfg["accounts"][acct] or {}).get("fingerprint")
                if fp and expected_fp and fp != expected_fp:
                    warnings.append(f"{label}: {prov} fingerprint {fp} differs from {acct} ({expected_fp})")
                    continue
                if probe.get("source", "unavailable") == "unavailable":
                    continue
                cap = parse_iso(rec.get("captured_at"))
                if cap and at - cap > max_age:
                    warnings.append(f"{label}: {prov} sample is older than {max_age}")
                    continue
                # A session-log fallback can carry a weekly window that rolled over
                # weeks ago (seen 2026-09-26: ace-linux-2 codex "1% used, resets
                # 2026-08-21"). A past reset means the figure describes a window
                # that no longer exists, so it is not a sample at all.
                reset = parse_iso(probe.get("week_resets_at"))
                if reset and reset < at:
                    warnings.append(f"{label}: {prov} sample's weekly window reset at {reset.isoformat()}; ignored")
                    continue
                samples[acct].append({**probe, "host": label, "captured_at": rec.get("captured_at")})
        hosts_out[label] = entry

    accounts_out: dict[str, dict] = {}
    for acct, meta in cfg["accounts"].items():
        meta = meta or {}
        hosts_for = sorted(l for l, h in cfg["hosts"].items() if any((h or {}).get(p) == acct for p in PROVIDERS))
        fps = sorted({s["fingerprint"] for s in samples[acct] if s.get("fingerprint")})
        if len(fps) > 1:
            warnings.append(f"{acct}: hosts report different fingerprints {fps}; check ai-accounts.yaml")
        best = max(samples[acct], key=sample_rank, default=None)
        row = {
            "provider": meta.get("provider"),
            "holder": meta.get("holder"),
            "access": meta.get("access"),
            "hosts": hosts_for,
            "reachable_hosts": [l for l in hosts_for if hosts_out.get(l, {}).get("reachable")],
            "fingerprint": fps[0] if len(fps) == 1 else meta.get("fingerprint"),
            "source": best.get("source") if best else "unavailable",
        }
        if best:
            row.update({
                "sampled_on": best["host"],
                "captured_at": best.get("captured_at"),
                "tier": best.get("tier") or best.get("plan"),
                "five_hour_pct": best.get("five_hour_pct"),
                "week_pct": best.get("week_pct"),
                "week_resets_at": best.get("week_resets_at"),
                "headroom_pct": headroom(best),
                "buckets": best.get("buckets"),
            })
            if row["headroom_pct"] is not None and row["headroom_pct"] < tight:
                row["tight"] = True
        accounts_out[acct] = row

    recommendation: dict[str, dict] = {}
    for prov in PROVIDERS:
        ranked = sorted(
            ((a, r) for a, r in accounts_out.items() if r["provider"] == prov and r.get("headroom_pct") is not None),
            key=lambda ar: (ar[1]["headroom_pct"], -(ar[1].get("five_hour_pct") or 0)), reverse=True)
        if not ranked:
            recommendation[prov] = {"account": None, "reason": "no live sample for any account"}
            continue
        top, top_row = ranked[0]
        rec = {"account": top, "headroom_pct": top_row["headroom_pct"], "hosts": top_row["reachable_hosts"] or top_row["hosts"]}
        if len(ranked) > 1:
            second, second_row = ranked[1]
            rec["alternative"] = {"account": second, "headroom_pct": second_row["headroom_pct"]}
            if top_row["headroom_pct"] - second_row["headroom_pct"] < margin:
                rec["note"] = f"within {margin:g} pts of {second}: stay on whichever host you are on"
        if top_row.get("tight"):
            rec["note"] = f"every {prov} account is below {tight:g}% weekly headroom; defer marathons"
        recommendation[prov] = rec

    return {
        "schema_version": 1,
        "generated_at": at.isoformat(),
        "generated_by": "fleet-collector collect_account_usage_fleet",
        "policy": {"tight_headroom_pct": tight, "switch_margin_pct": margin},
        "accounts": accounts_out,
        "hosts": hosts_out,
        "recommendation": recommendation,
        "warnings": warnings,
    }


def render_md(agg: dict) -> str:
    lines = ["# AI account usage (fleet)", "",
             f"Generated {agg['generated_at']} by {agg['generated_by']}. "
             "Percentages are USED; headroom = 100 - weekly used. "
             "Source of truth: `config/ai-tools/account-usage-latest.json`.", ""]
    lines += ["## Recommendation", ""]
    for prov, rec in agg["recommendation"].items():
        if rec.get("account"):
            hosts = ", ".join(rec.get("hosts") or []) or "(no reachable host)"
            note = f" -- {rec['note']}" if rec.get("note") else ""
            lines.append(f"- **{prov}**: `{rec['account']}` ({rec['headroom_pct']}% weekly headroom) on {hosts}{note}")
        else:
            lines.append(f"- **{prov}**: {rec.get('reason')}")
    lines += ["", "## Accounts", "",
              "| account | provider | holder | 5h used | week used | headroom | resets | sampled on | source |",
              "|---|---|---|---|---|---|---|---|---|"]
    for name, r in agg["accounts"].items():
        def pct(v):
            return "" if v is None else f"{v:g}%"
        lines.append(f"| {name} | {r['provider']} | {r.get('holder','')} | {pct(r.get('five_hour_pct'))} | "
                     f"{pct(r.get('week_pct'))} | {pct(r.get('headroom_pct'))} | {r.get('week_resets_at') or ''} | "
                     f"{r.get('sampled_on') or ''} | {r.get('source')} |")
    lines += ["", "## Hosts", "", "| host | reachable | claude | codex | note |", "|---|---|---|---|---|"]
    for label, h in agg["hosts"].items():
        acc = h.get("accounts", {})
        unavailable = h.get("unavailable") or {}
        note = h.get("note") or "; ".join(f"{p}: {e}" for p, e in unavailable.items())
        lines.append(f"| {label} | {'yes' if h.get('reachable') else 'no'} | {acc.get('claude','')} | "
                     f"{acc.get('codex','')} | {note} |")
    if agg["warnings"]:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in agg["warnings"]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--md", type=Path, default=DEFAULT_MD)
    p.add_argument("--hosts", default=None, help="comma list of host labels (default: all)")
    p.add_argument("--ssh-timeout", type=int, default=15)
    p.add_argument("--dry-run", action="store_true", help="print the aggregate, write nothing")
    p.add_argument("--label-map", default=None,
                   help=f"private fleet label map (else ${fsl.MAP_ENV}, else {fsl.DEFAULT_MAP})")
    args = p.parse_args(argv)

    cfg = load_config(args.config)
    try:
        table = fsl.load_map(fsl.map_path(args.label_map))
        for label, host in cfg["hosts"].items():
            if isinstance((host or {}).get("ssh"), list):
                resolve_ssh_argv(host["ssh"], table)
    except fsl.LabelError as exc:
        sys.stderr.write(f"collect_account_usage_fleet: {exc}; nothing probed or published\n")
        return 2
    wanted = set(args.hosts.split(",")) if args.hosts else set(cfg["hosts"])
    probe_src = PROBE.read_bytes()
    records = []
    for label, host in cfg["hosts"].items():
        if label not in wanted:
            continue
        rec = run_probe(label, host or {}, args.ssh_timeout, probe_src, table)
        records.append(rec)
        sys.stderr.write(f"{label}: {'ok' if rec.get('reachable') else 'unreachable ' + str(rec.get('note'))}\n")

    agg = aggregate(cfg, records)
    out_text = json.dumps(agg, indent=2, sort_keys=True) + "\n"
    md_text = render_md(agg)
    try:
        assert_publishable(out_text + "\n" + md_text, table)
    except fsl.LabelError as exc:
        sys.stderr.write(f"collect_account_usage_fleet: {exc}; leaving the published files untouched\n")
        return 2
    reachable = [r for r in records if r.get("reachable")]
    if args.dry_run:
        sys.stdout.write(out_text)
        return 0 if reachable else 1
    if not reachable:
        sys.stderr.write("no host answered; leaving the published files untouched\n")
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(out_text, encoding="utf-8")
    args.md.parent.mkdir(parents=True, exist_ok=True)
    args.md.write_text(md_text, encoding="utf-8")
    for prov, rec in agg["recommendation"].items():
        sys.stderr.write(f"recommend {prov}: {rec.get('account')} {rec.get('headroom_pct')}% on {rec.get('hosts')}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
