#!/usr/bin/env python3
"""Run host_baseline.py on every host in a run-time host list (#4532).

    python -I scripts/hygiene/fleet_baseline.py --config <private hosts.json>

Config (kept private, beside the output; see fleet_baseline.example.json):
    {"out_dir": "<private dir>",
     "hosts": [{"label": "<fleet label>", "ssh": "<ssh alias or null for this host>",
                "python": "python3", "args": ["--expected", "ws,data"],
                "timeout_s": 7200}]}

Each invocation writes a fresh <out_dir>/<date>T<time>Z/ holding <label>.json (or
<label>.err on failure), summary.md and manifest.json. Files are created exclusively.
Read-only on every host. A failed host is reported in the summary, never dropped.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLLECTOR = HERE / "host_baseline.py"
GB = 1024 ** 3


def build_command(host: dict) -> list[str]:
    args = [*host.get("args", []), "--label", host["label"]]
    if not host.get("ssh"):
        return [host.get("python") or sys.executable, "-I", str(COLLECTOR), *args]
    python = host.get("python", "python3")
    remote = " ".join([shlex.quote(python), "-", *map(shlex.quote, args)])
    return ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", host["ssh"], remote]


LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def validate_hosts(hosts: list[dict]) -> None:
    seen = set()
    for h in hosts:
        label = h.get("label", "")
        if not LABEL_RE.match(label) or ".." in label:
            raise ValueError(f"unsafe host label: {label!r}")
        if label in seen:
            raise ValueError(f"duplicate host label: {label!r}")
        seen.add(label)


def write_new(path: Path, text: str) -> None:
    """Create a new file; never follow or overwrite an existing path."""
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(text)


def run_host(host: dict, run_dir: Path) -> dict:
    label = host["label"]
    try:
        cmd = build_command(host)
        stdin = None if not host.get("ssh") else COLLECTOR.read_text(encoding="utf-8")
        proc = subprocess.run(cmd, input=stdin, capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              timeout=host.get("timeout_s", 7200))
        rc, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = -1, "", "timeout"
    except OSError as exc:  # missing interpreter or ssh: report, do not abort the fleet
        rc, out, err = -1, "", f"launch failed: {exc}"
    if rc == 0:
        try:
            doc = json.loads(out)
            write_new(run_dir / f"{label}.json", out)
            return {"label": label, "ok": True, "doc": doc}
        except json.JSONDecodeError:
            err = "collector printed non-JSON output\n" + err
    write_new(run_dir / f"{label}.err", f"rc={rc}\n{err[-4000:]}")
    return {"label": label, "ok": False, "error": f"rc={rc}: {err.strip()[-300:]}"}


def gb(n) -> str:
    return "-" if n is None else f"{n / GB:,.1f}"


def render_summary(results: list[dict], date: str) -> str:
    lines = [f"# Fleet storage baseline {date}", "",
             "Read-only. Sizes in GB (1024^3 bytes). Produced by "
             "`scripts/hygiene/fleet_baseline.py`.", ""]
    for res in sorted(results, key=lambda r: r["label"]):
        lines.append(f"## {res['label']}")
        if not res["ok"]:
            lines += ["", f"FAILED: {res['error']}", ""]
            continue
        doc = res["doc"]
        lines += ["", f"{doc['os']}, Python {doc['python']}, scan {doc['elapsed_s']} s.", "",
                  "### Disks", "", "| Mount | Total | Free | Free % |", "|---|---:|---:|---:|"]
        lines += [f"| `{d['mount']}` | {gb(d['total_bytes'])} | {gb(d['free_bytes'])} | "
                  f"{d['free_pct']} |" for d in doc["disks"]]
        dirs = sorted((d for s in doc["roots"] for d in s["dirs"]),
                      key=lambda d: -d["bytes"])[:15]
        lines += ["", "### Largest folders", "", "| Folder | GB | Files | Newest file | Git |",
                  "|---|---:|---:|---|---|"]
        lines += [f"| `{d['path']}` | {gb(d['bytes'])} | {d['files']:,} | "
                  f"{(d['newest_utc'] or '-')[:10]} | {d['git'] or '-'} |" for d in dirs]
        if doc["stray"]:
            lines += ["", "### Stray top-level folders", "", "| Folder | Reason | GB | Newest |",
                      "|---|---|---:|---|"]
            lines += [f"| `{s['path']}` | {s['reason']} | {gb(s['bytes'])} | "
                      f"{(s['newest_utc'] or '-')[:10]} |" for s in doc["stray"]]
        if doc["caches"]:
            lines += ["", "### Caches", "", "| Cache | Path | GB |", "|---|---|---:|"]
            lines += [f"| {c['name']} | `{c['path']}` | {gb(c['bytes'])} |"
                      for c in doc["caches"] if c["bytes"] >= 0.1 * GB]
        cos = doc["checkouts"]
        if cos:
            off = [c for c in cos if c.get("head_on_remote") is False]
            dirty = [c for c in cos if c.get("dirty")]
            lines += ["", "### Git checkouts", "",
                      f"{len(cos)} checkouts ({sum(c['kind'] == 'clone' for c in cos)} clones, "
                      f"{sum(c['kind'] == 'worktree' for c in cos)} worktrees); "
                      f"{len(dirty)} with uncommitted files; {len(off)} whose HEAD is in no "
                      f"remote-tracking ref; {sum(1 for c in cos if 'error' in c)} unreadable."]
        lines.append("")
    return "\n".join(lines)


def run(cfg: dict, date: str | None = None) -> Path:
    """One invocation = one fresh directory, so a stale result can never sit beside a new one."""
    hosts = cfg["hosts"]
    validate_hosts(hosts)
    now = datetime.now(timezone.utc)
    date = date or now.strftime("%Y-%m-%d")
    stamp = f"{date}T{now.strftime('%H%M%S')}Z"
    out_root = Path(cfg["out_dir"])
    out_root.mkdir(parents=True, exist_ok=True)
    run_dir = out_root / stamp
    n = 1
    while True:
        try:
            run_dir.mkdir()
            break
        except FileExistsError:
            n += 1
            run_dir = out_root / f"{stamp}-{n}"
    with cf.ThreadPoolExecutor(max_workers=max(1, len(hosts))) as pool:
        results = list(pool.map(lambda h: run_host(h, run_dir), hosts))
    write_new(run_dir / "summary.md", render_summary(results, date))
    write_new(run_dir / "manifest.json", json.dumps({
        "run": run_dir.name, "started_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hosts": [{"label": r["label"], "ok": r["ok"],
                   "file": f"{r['label']}.json" if r["ok"] else f"{r['label']}.err"}
                  for r in results]}, indent=1))
    return run_dir


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Fleet storage baseline (read-only).")
    ap.add_argument("--config", required=True)
    ap.add_argument("--only", nargs="*", help="run only these labels")
    args = ap.parse_args(argv)
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    if args.only:
        cfg["hosts"] = [h for h in cfg["hosts"] if h["label"] in set(args.only)]
    run_dir = run(cfg)
    print(run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
