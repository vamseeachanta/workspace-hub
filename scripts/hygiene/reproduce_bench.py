#!/usr/bin/env python3
"""Measure trusted rebuild commands in disposable copies of committed files.

The checked repository is read only. This is process isolation, not a security
sandbox: only run commands already trusted to execute with the caller's access.
See REPRODUCE_BENCH.md for the report contract and the source of policy defaults.
"""

import argparse
import hashlib
import html
import json
import math
import os
import platform
import re
import shutil
import signal
import stat
import statistics
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path, PureWindowsPath

# Issue #4223 establishes the 60-second target. Other performance criteria
# require explicit configuration rather than an unsupported policy default.
DEFAULT_TARGET = 60
# Local report contract, version 1; see REPRODUCE_BENCH.md, "Report schema".
SCHEMA_VERSION = 1
VERDICTS = {"PASS", "SLOW", "NOT_REPRODUCED", "FAILED", "TIMEOUT"}


def positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return value


def parse_config(raw):
    if not isinstance(raw, dict):
        raise TypeError("config must be an object")
    allowed = {
        "target_seconds",
        "repeats",
        "timeout_seconds",
        "clean_checkout",
        "history",
        "history_window",
        "regression_ratio",
    }
    if raw.keys() - allowed:
        raise ValueError("unknown config field")
    for name in ("repeats", "regression_ratio"):
        if name not in raw:
            raise ValueError(f"{name} requires explicit configuration")
    result = {
        "target_seconds": DEFAULT_TARGET,
        "clean_checkout": True,
        **raw,
    }
    for name in ("target_seconds", "timeout_seconds", "regression_ratio"):
        positive(result.get(name), name)
    for name in ("repeats", "history_window"):
        if name in result and (type(result[name]) is not int or result[name] <= 0):
            raise ValueError(f"{name} must be a positive integer")
    if type(result["clean_checkout"]) is not bool:
        raise ValueError("clean_checkout must be boolean")
    if "history" in result and (
        not isinstance(result["history"], str) or not result["history"]
    ):
        raise ValueError("history must be a nonempty path")
    return result


def relative_path(value):
    if (
        not isinstance(value, str)
        or not value
        or "\0" in value
        or Path(value).is_absolute()
        or PureWindowsPath(value).drive
        or "\\" in value
        or ".." in Path(value).parts
        or ".git" in Path(value).parts
    ):
        raise ValueError("expected a repository-relative path without traversal")
    return Path(value)


def git_env():
    # Caller bindings must not redirect fixture/repository commands elsewhere.
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def git(repo, *args):
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], env=git_env(), stderr=subprocess.DEVNULL
    )


def tracked_entries(repo, revision="HEAD"):
    """Select membership, bytes and modes from one committed tree."""
    entries = {}
    for record in git(repo, "ls-tree", "-rz", revision).split(b"\0"):
        if not record:
            continue
        meta, raw_path = record.split(b"\t", 1)
        mode, kind, digest = meta.split()
        path = os.fsdecode(raw_path)
        relative_path(path)
        if kind != b"blob" or mode not in (b"100644", b"100755"):
            raise ValueError(
                "snapshot requires regular tracked files; symlinks/submodules unsupported"
            )
        entries[path] = (mode, digest)
    return entries


def blob(repo, digest):
    return git(repo, "cat-file", "blob", digest.decode("ascii"))


def copy_snapshot(repo, entries, destination):
    """Stream committed blobs without copying .git, ignored files or caches."""
    destination.mkdir(parents=True, exist_ok=True)
    with subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        env=git_env(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    ) as process:
        try:
            for name, (mode, digest) in entries.items():
                process.stdin.write(digest + b"\n")
                process.stdin.flush()
                header = process.stdout.readline().split()
                if len(header) != 3 or header[1] != b"blob":
                    raise ValueError("cannot read committed snapshot")
                remaining = int(header[2])
                target = destination / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("wb") as handle:
                    while remaining:
                        chunk = process.stdout.read(min(remaining, 1024 * 1024))
                        if not chunk:
                            raise ValueError("incomplete snapshot blob")
                        handle.write(chunk)
                        remaining -= len(chunk)
                process.stdout.read(1)  # Git batch protocol's trailing newline.
                target.chmod(0o755 if mode == b"100755" else 0o644)
        finally:
            process.stdin.close()
            process.wait()


def validate_registry(registry, entries):
    if not isinstance(registry, list):
        raise TypeError("registry must be a list")
    seen = set()
    normalized = []
    for item in registry:
        if not isinstance(item, dict):
            raise TypeError("artifact must be an object")
        path = relative_path(item.get("path")).as_posix()
        if path in seen or path not in entries:
            raise ValueError("artifact must be unique and committed")
        seen.add(path)
        build = item.get("build")
        if (
            not isinstance(item.get("kind"), str)
            or not item["kind"]
            or not isinstance(build, dict)
        ):
            raise ValueError("artifact kind and build are required")
        relative_path(build.get("cwd"))
        argv = build.get("argv")
        if (
            not isinstance(argv, list)
            or not argv
            or any(not isinstance(arg, str) or not arg or "\0" in arg for arg in argv)
        ):
            raise ValueError("build argv must be a nonempty list of strings")
        inputs = item.get("inputs")
        if not isinstance(inputs, list):
            raise TypeError("artifact inputs must be a list")
        for name in inputs:
            if relative_path(name).as_posix() not in entries:
                raise ValueError("artifact input must be committed")
        if "budget_seconds" in item:
            positive(item["budget_seconds"], "budget_seconds")
        normalized.append(
            {
                **item,
                "path": path,
                "build": {**build, "cwd": relative_path(build["cwd"]).as_posix()},
                "inputs": [relative_path(name).as_posix() for name in inputs],
            }
        )
    return normalized


def run_process(argv, *, cwd, timeout, env):
    """Discard build output: it may contain credentials or private paths."""
    with subprocess.Popen(
        argv,
        cwd=cwd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=(os.name == "posix"),
    ) as process:
        try:
            return subprocess.CompletedProcess(argv, process.wait(timeout=timeout))
        except subprocess.TimeoutExpired:
            try:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
            except ProcessLookupError:
                pass  # The process exited between timeout detection and cleanup.
            process.wait()
            raise


def summarize(durations):
    # Python 3.11 statistics.median: middle sorted value, mean of middle pair if even.
    return {
        "min_seconds": min(durations),
        "median_seconds": statistics.median(durations),
        "max_seconds": max(durations),
    }


def outside_repository(path, repo):
    path = Path(path).resolve()
    if path.is_relative_to(repo.resolve()):
        raise ValueError(
            "output and temporary paths must be outside the checked repository"
        )
    return path


def unlinked_snapshot_path(path, root):
    """Inspect ancestors first, without following links into external content."""
    relative = path.relative_to(root)
    candidates = [root]
    for part in relative.parts:
        candidates.append(candidates[-1] / part)
    for candidate in candidates:
        try:
            metadata = candidate.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode) or (
            getattr(metadata, "st_file_attributes", 0)
            & stat.FILE_ATTRIBUTE_REPARSE_POINT
        ):
            return False
    return path.resolve().is_relative_to(root.resolve())


def regular_snapshot_output(output, checkout):
    """Reject links and directory reparse points before accepting output bytes."""
    return unlinked_snapshot_path(output, checkout) and output.is_file()


def benchmark(
    repo,
    raw_config,
    *,
    registry=None,
    temp_root=None,
    runner=run_process,
    clock=time.perf_counter,
    anonymise_host=True,
):
    config = parse_config(raw_config)
    repo = Path(repo).resolve()
    if (
        Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel")).strip()).resolve()
        != repo
    ):
        raise ValueError("repo must name the repository root")
    revision = git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    entries = tracked_entries(repo, revision)
    if registry is None:
        if "artifacts.registry.json" not in entries:
            raise ValueError("committed artifact registry is missing")
        registry = json.loads(blob(repo, entries["artifacts.registry.json"][1]))
    registry = validate_registry(registry, entries)
    temp_root = outside_repository(temp_root or tempfile.gettempdir(), repo)
    temp_root.mkdir(parents=True, exist_ok=True)
    descriptors = {
        "source": "Python platform module and os.cpu_count",
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }
    if not anonymise_host:
        descriptors["hostname"] = platform.node()
    report = {
        "schema_version": SCHEMA_VERSION,
        "recorded_at": datetime.now(UTC).isoformat(),
        "revision": revision,
        "machine": descriptors,
        "method": {
            name: config[name]
            for name in (
                "target_seconds",
                "repeats",
                "timeout_seconds",
                "clean_checkout",
            )
        },
        "comparison": {
            "enabled": False,
            "history_window": None,
            "regression_ratio": config["regression_ratio"],
        },
        "artifacts": [],
    }
    for item in registry:
        expected = hashlib.sha256(blob(repo, entries[item["path"]][1])).hexdigest()
        # Bind history to the command, declared inputs and committed artifact bytes.
        basis = {
            "artifact": expected,
            "build": item["build"],
            "inputs": {name: entries[name][1].decode() for name in item["inputs"]},
        }
        fingerprint = hashlib.sha256(
            json.dumps(basis, sort_keys=True).encode()
        ).hexdigest()
        budget = item.get("budget_seconds", config["target_seconds"])
        runs = []
        # TemporaryDirectory owns disposable copies only, never caller data.
        with tempfile.TemporaryDirectory(
            prefix="reproduce-", dir=temp_root
        ) as temporary:
            root = Path(temporary)
            for index in range(config["repeats"]):
                checkout = root / (str(index) if config["clean_checkout"] else "shared")
                if not unlinked_snapshot_path(checkout, root):
                    raise ValueError("linked snapshot path prevents copy or cleanup")
                if not checkout.exists():
                    copy_snapshot(repo, entries, checkout)
                output = checkout / item["path"]
                if not unlinked_snapshot_path(output, root):
                    raise ValueError("linked snapshot path prevents copy or cleanup")
                # Remove the committed artifact every time: a no-op cannot reproduce it.
                if output.is_symlink() or output.is_file():
                    output.unlink()
                elif output.exists():
                    shutil.rmtree(output)
                env_root = root / f"environment-{index}"
                env_root.mkdir()
                env = {
                    key: os.environ[key]
                    for key in ("PATH", "SYSTEMROOT", "WINDIR")
                    if key in os.environ
                }
                env.update(
                    HOME=str(env_root),
                    USERPROFILE=str(env_root),
                    TMPDIR=str(env_root),
                    TMP=str(env_root),
                    TEMP=str(env_root),
                    PYTHONDONTWRITEBYTECODE="1",
                    XDG_CACHE_HOME=str(env_root / "cache"),
                    LC_ALL="C",
                )
                status, exit_status = "FAILED", None
                # Python 3.11 time.perf_counter: includes elapsed sleep; excludes preparation.
                start = clock()
                try:
                    completed = runner(
                        item["build"]["argv"],
                        cwd=checkout / item["build"]["cwd"],
                        timeout=config["timeout_seconds"],
                        env=env,
                    )
                    exit_status = completed.returncode
                    status = "PASS" if exit_status == 0 else "FAILED"
                except subprocess.TimeoutExpired:
                    status = "TIMEOUT"
                except OSError:
                    status = "FAILED"
                duration = clock() - start
                actual = None
                if regular_snapshot_output(output, checkout):
                    actual = hashlib.sha256(output.read_bytes()).hexdigest()
                if status == "PASS" and actual != expected:
                    status = "NOT_REPRODUCED"
                runs.append(
                    {
                        "phase": "cold" if index == 0 else "warm",
                        "seconds": duration,
                        "exit_status": exit_status,
                        "sha256": actual,
                        "status": status,
                    }
                )
        timing = summarize([run["seconds"] for run in runs])
        verdict = next(
            (
                s
                for s in ("TIMEOUT", "FAILED", "NOT_REPRODUCED")
                if any(run["status"] == s for run in runs)
            ),
            "SLOW" if timing["median_seconds"] > budget else "PASS",
        )
        report["artifacts"].append(
            {
                "path": item["path"],
                "kind": item["kind"],
                "expected_sha256": expected,
                "fingerprint": fingerprint,
                "budget_seconds": budget,
                "verdict": verdict,
                "runs": runs,
                "timing": timing,
                "regression": False,
                "baseline_median_seconds": None,
            }
        )
    artifacts = report["artifacts"]
    longest = max(artifacts, key=lambda a: a["timing"]["max_seconds"], default=None)
    report["totals"] = {
        "sum_medians_seconds": sum(a["timing"]["median_seconds"] for a in artifacts),
        "longest_single_artifact": None
        if longest is None
        else {"path": longest["path"], "seconds": longest["timing"]["max_seconds"]},
    }
    validate_report(report)
    return report


def read_history(path):
    if not Path(path).exists():
        return []
    records = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            report = json.loads(line)
            validate_report(report)
            records.append(report)
    return records


def compare_history(report, history, *, window, ratio):
    positive(ratio, "regression_ratio")
    if type(window) is not int or window <= 0:
        raise ValueError("history_window must be a positive integer")
    report["comparison"] = {
        "enabled": True,
        "history_window": window,
        "regression_ratio": ratio,
    }
    for item in report["artifacts"]:
        values = [
            old["timing"]["median_seconds"]
            for previous in history
            for old in previous["artifacts"]
            if old["path"] == item["path"]
            and old["fingerprint"] == item["fingerprint"]
            and old["verdict"] in {"PASS", "SLOW"}
        ]
        baseline = statistics.median(values[-window:]) if values else None
        item["baseline_median_seconds"] = baseline
        item["regression"] = (
            baseline is not None
            and item["verdict"] in {"PASS", "SLOW"}
            and item["timing"]["median_seconds"] > baseline * ratio
        )


def append_history(path, report):
    validate_report(report)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report, allow_nan=False, sort_keys=True) + "\n")


def exit_code(report):
    return int(
        any(
            item["verdict"] != "PASS" or item["regression"]
            for item in report["artifacts"]
        )
    )


def validate_report(report):
    """Validate the closed version-1 schema using only the standard library."""

    def obj(value, fields):
        if not isinstance(value, dict) or set(value) != set(fields):
            raise ValueError("report object fields do not match schema")

    def number(value):
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("report requires finite nonnegative timing")

    def digest(value):
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(
                "invalid SHA-256 digest"
            )  # SHA-256 is 256 bits / 4 bits per hex digit.

    obj(
        report,
        {
            "schema_version",
            "recorded_at",
            "revision",
            "machine",
            "method",
            "comparison",
            "artifacts",
            "totals",
        },
    )
    if (
        type(report["schema_version"]) is not int
        or report["schema_version"] != SCHEMA_VERSION
    ):
        raise ValueError("unsupported report schema version")
    if not isinstance(report["recorded_at"], str) or not isinstance(
        report["revision"], str
    ):
        raise TypeError("invalid report metadata")
    recorded_at = datetime.fromisoformat(report["recorded_at"])
    if (
        recorded_at.tzinfo is None
        or recorded_at.utcoffset().total_seconds() != 0
        or not report["revision"]
    ):
        raise ValueError("report metadata requires UTC timestamp and revision")
    machine = report["machine"]
    if not isinstance(machine, dict):
        raise TypeError("invalid machine descriptors")
    obj(
        machine,
        {"source", "system", "release", "machine", "python_version", "cpu_count"}
        | ({"hostname"} if "hostname" in machine else set()),
    )
    if any(not isinstance(v, str) for k, v in machine.items() if k != "cpu_count"):
        raise ValueError("machine descriptors must be strings")
    if machine["cpu_count"] is not None and (
        type(machine["cpu_count"]) is not int or machine["cpu_count"] <= 0
    ):
        raise ValueError("invalid cpu count")
    obj(
        report["method"],
        {"target_seconds", "repeats", "timeout_seconds", "clean_checkout"},
    )
    comparison = report["comparison"]
    obj(comparison, {"enabled", "history_window", "regression_ratio"})
    parse_config(
        {**report["method"], "regression_ratio": comparison["regression_ratio"]}
    )
    if type(comparison["enabled"]) is not bool:
        raise TypeError("comparison enabled must be boolean")
    window = comparison["history_window"]
    if comparison["enabled"]:
        if type(window) is not int or window <= 0:
            raise ValueError("comparison requires positive history window")
    elif window is not None:
        raise ValueError("disabled comparison must have no history window")
    if not isinstance(report["artifacts"], list):
        raise TypeError("artifacts must be a list")
    seen = set()
    for item in report["artifacts"]:
        obj(
            item,
            {
                "path",
                "kind",
                "expected_sha256",
                "fingerprint",
                "budget_seconds",
                "verdict",
                "runs",
                "timing",
                "regression",
                "baseline_median_seconds",
            },
        )
        relative_path(item["path"])
        if (
            item["path"] in seen
            or not isinstance(item["kind"], str)
            or not item["kind"]
        ):
            raise ValueError("invalid artifact identity")
        seen.add(item["path"])
        digest(item["expected_sha256"])
        digest(item["fingerprint"])
        positive(item["budget_seconds"], "budget_seconds")
        if item["verdict"] not in VERDICTS or type(item["regression"]) is not bool:
            raise ValueError("invalid artifact verdict")
        if item["baseline_median_seconds"] is not None:
            number(item["baseline_median_seconds"])
        obj(item["timing"], {"min_seconds", "median_seconds", "max_seconds"})
        for value in item["timing"].values():
            number(value)
        if (
            not isinstance(item["runs"], list)
            or len(item["runs"]) != report["method"]["repeats"]
        ):
            raise ValueError("run count must match repeats")
        for index, run in enumerate(item["runs"]):
            obj(run, {"phase", "seconds", "exit_status", "sha256", "status"})
            number(run["seconds"])
            if run["phase"] != ("cold" if index == 0 else "warm") or run[
                "status"
            ] not in VERDICTS - {"SLOW"}:
                raise ValueError("invalid run status or phase")
            if run["exit_status"] is not None and type(run["exit_status"]) is not int:
                raise ValueError("invalid exit status")
            if run["sha256"] is not None:
                digest(run["sha256"])
        for run in item["runs"]:
            if run["status"] == "PASS" and (
                run["exit_status"] != 0 or run["sha256"] != item["expected_sha256"]
            ):
                raise ValueError("PASS requires successful exit and matching digest")
            if run["status"] == "NOT_REPRODUCED" and (
                run["exit_status"] != 0 or run["sha256"] == item["expected_sha256"]
            ):
                raise ValueError(
                    "NOT_REPRODUCED requires successful exit and different or absent digest"
                )
        expected_verdict = next(
            (
                s
                for s in ("TIMEOUT", "FAILED", "NOT_REPRODUCED")
                if any(r["status"] == s for r in item["runs"])
            ),
            "SLOW"
            if item["timing"]["median_seconds"] > item["budget_seconds"]
            else "PASS",
        )
        if item["verdict"] != expected_verdict:
            raise ValueError("artifact verdict contradicts observations")
        baseline = item["baseline_median_seconds"]
        expected_regression = (
            comparison["enabled"]
            and baseline is not None
            and item["verdict"] in {"PASS", "SLOW"}
            and item["timing"]["median_seconds"]
            > baseline * comparison["regression_ratio"]
        )
        if item["regression"] != expected_regression or (
            not comparison["enabled"] and baseline is not None
        ):
            raise ValueError("regression contradicts comparison settings")
        if item["timing"] != summarize([r["seconds"] for r in item["runs"]]):
            raise ValueError("timing summary does not match observations")
    obj(report["totals"], {"sum_medians_seconds", "longest_single_artifact"})
    number(report["totals"]["sum_medians_seconds"])
    longest = report["totals"]["longest_single_artifact"]
    if longest is not None:
        obj(longest, {"path", "seconds"})
        relative_path(longest["path"])
        number(longest["seconds"])
    artifacts = report["artifacts"]
    expected_longest = max(
        artifacts, key=lambda a: a["timing"]["max_seconds"], default=None
    )
    expected_total = {
        "sum_medians_seconds": sum(a["timing"]["median_seconds"] for a in artifacts),
        "longest_single_artifact": None
        if expected_longest is None
        else {
            "path": expected_longest["path"],
            "seconds": expected_longest["timing"]["max_seconds"],
        },
    }
    if report["totals"] != expected_total:
        raise ValueError("totals contradict artifact timings")


def render_html(report):
    escape = html.escape
    rows = []
    for item in report["artifacts"]:
        timing = item["timing"]
        # Presentation percentage: 100 percent means median equals stated budget.
        width = min(100, 100 * timing["median_seconds"] / item["budget_seconds"])
        rows.append(
            f'<tr><td>{escape(item["path"])}</td><td><strong class="{item["verdict"]}">'
            f"{item['verdict']}</strong>{' REGRESSION' if item['regression'] else ''}</td>"
            f"<td>{timing['min_seconds']:.3f} / {timing['median_seconds']:.3f} / "
            f"{timing['max_seconds']:.3f}</td><td>{item['budget_seconds']:g} s"
            f'<div class="track"><div style="width:{width:.1f}%"></div></div></td></tr>'
        )
    method = report["method"]
    descriptors = escape(json.dumps(report["machine"], sort_keys=True))
    totals = report["totals"]
    longest = totals["longest_single_artifact"]
    longest_text = (
        "none" if longest is None else f"{longest['path']} ({longest['seconds']:.3f} s)"
    )
    comparison = report["comparison"]
    return f"""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Artifact reproduction benchmark</title><style>
:root {{ color-scheme:light dark; font-family:system-ui,sans-serif; }}
body {{ max-width:75rem; margin:2rem auto; padding:1rem; }}
table {{ border-collapse:collapse; width:100%; }} td,th {{ padding:.6rem; text-align:left;
border-bottom:1px solid GrayText; overflow-wrap:anywhere; }}
strong {{ padding:.2rem .4rem; border:1px solid currentColor; border-radius:.3rem; }}
.PASS {{ color:light-dark(#17642c,#8de7a3); }}
.SLOW,.TIMEOUT,.FAILED,.NOT_REPRODUCED {{ color:light-dark(#963400,#ffb68a); }}
.track {{ background:GrayText; height:.5rem; margin-top:.4rem; }}
.track div {{ background:CanvasText; height:100%; }} pre {{ white-space:pre-wrap; }}
</style><h1>Artifact reproduction benchmark</h1>
<p>{len(report["artifacts"])} artifacts; sum of medians: {totals["sum_medians_seconds"]:.3f} s.
Longest single artifact: {escape(longest_text)}.</p>
<h2>Revision history</h2><table><thead><tr><th>Revision</th><th>Date (UTC)</th>
<th>Change and purpose</th></tr></thead><tbody><tr><td>{escape(report["revision"])}</td>
<td>{escape(report["recorded_at"])}</td><td>Measured committed rebuilds against configured budgets.</td>
</tr></tbody></table>
<h2>Artifacts</h2><table><thead><tr><th>Artifact</th><th>Verdict</th><th>Min / median / max (s)</th>
<th>Budget and median / budget</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<h2>Method</h2><p>Only subprocess wall time is measured with time.perf_counter.
Copying committed tracked files, deleting the prior output, hashing and reporting are excluded.
Clean checkout per repeat: {method["clean_checkout"]}. Repeats: {method["repeats"]}.
First observation is cold; subsequent observations are warm in order only. Operating-system
caches are not flushed. The default 60 s target is the maintainer's stated target in issue #4223;
this run uses {method["target_seconds"]:g} s unless an artifact states its own budget.</p>
<p>History comparison: {comparison["enabled"]}; prior matching records: {comparison["history_window"]};
regression ratio: {comparison["regression_ratio"]:g}.</p>
<h2>Limits</h2><p>Wall time on one machine is not comparable across machines. Commands are trusted
code, not sandboxed. Dependencies outside tracked files are not pinned by this tool.
Descriptors are from Python platform and os.cpu_count. Build output is discarded.</p>
<pre>{descriptors}</pre></html>"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--compare", choices=["history"])
    parser.add_argument(
        "--anonymise-host", action=argparse.BooleanOptionalAction, default=True
    )
    args = parser.parse_args(argv)
    try:
        config = parse_config(json.loads(args.config.read_text(encoding="utf-8")))
        output = outside_repository(args.out, args.repo)
        html_path = outside_repository(output.with_suffix(".html"), args.repo)
        if output == html_path:
            raise ValueError("JSON output must not have an HTML suffix")
        history_path = (
            outside_repository(args.config.parent / config["history"], args.repo)
            if "history" in config
            else None
        )
        if history_path in (output, html_path):
            raise ValueError("history and report paths must differ")
        if args.compare and (history_path is None or "history_window" not in config):
            raise ValueError("history comparison requires history and history_window")
        protected = {args.config.resolve(), output, html_path}
        if len(protected) != 3 or (
            history_path is not None and history_path in protected
        ):
            raise ValueError("config, reports and history must use distinct paths")
        history = read_history(history_path) if history_path else []
        report = benchmark(args.repo, config, anonymise_host=args.anonymise_host)
        if args.compare:
            compare_history(
                report,
                history,
                window=config["history_window"],
                ratio=config["regression_ratio"],
            )
        validate_report(report)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        html_path.write_text(render_html(report), encoding="utf-8", newline="\n")
        if history_path:
            append_history(history_path, report)
        return exit_code(report)
    except (ValueError, TypeError, OSError, RecursionError, subprocess.SubprocessError):
        # Exception text may include paths, commands, or data. Do not echo it.
        parser.exit(
            2,
            "benchmark input or execution setup error; check configuration and committed files\n",
        )


if __name__ == "__main__":
    raise SystemExit(main())
