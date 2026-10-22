"""Capture bounded Python replay import evidence; verify an externally pinned receipt.

The observation covers trusted, single-process, single-threaded Python source runs.
It is evidence collection, not a sandbox or a numerical qualification mechanism.
"""
from __future__ import annotations

import _thread
import argparse
import hashlib
import importlib.machinery
import importlib.metadata
import json
import logging
import os
import runpy
import subprocess
import sys
import sysconfig
import threading
from pathlib import Path

SCHEMA = "python-replay/1"
EXCLUDED = {".git", ".venv", "venv", "node_modules", "__pycache__"}
GIT_BINDINGS = {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"}
LIMITATIONS = [
    "Only executed Python import paths are observed; unexecuted branches are not covered.",
    "External dependencies are version observations, not bundled or qualified source.",
    "Native code, child processes and additional threads are outside the supported scope.",
    "Trusted commands only; instrumentation and receipts are not tamper-resistant attestation.",
    "Before/after observations cannot exclude transient source edits restored between checks.",
]


def digest(data):
    """Raw-byte SHA-256, as specified by hashlib's SHA-256 interface."""
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def environment():
    return {**{k: v for k, v in os.environ.items() if k not in GIT_BINDINGS},
            "PYTHONDONTWRITEBYTECODE": "1"}


def head(root):
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, env=environment(),
                            capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def inside(root, name):
    path = root / name
    if Path(name).is_absolute() or path.resolve().is_relative_to(root) is False:
        raise ValueError("evidence path outside checkout")
    return path


def dependency_roots():
    """Interpreter installation roots, including environments with custom names."""
    return {Path(sysconfig.get_path(key)).resolve() for key in ("purelib", "platlib")}


def dependency_source(path, root, dependencies):
    """Match interpreter libraries and the conventional environments scans exclude."""
    if any(path.is_relative_to(directory) for directory in dependencies):
        return True
    return path.is_relative_to(root) and bool(
        {".venv", "venv"}.intersection(path.relative_to(root).parts))


def snapshot(root):
    files = {}
    dependencies = dependency_roots()
    for directory, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED
                         and not dependency_source((Path(directory) / d).resolve(), root, dependencies))
        for name in sorted(names):
            if name.endswith(".py"):
                path = Path(directory) / name
                if not path.resolve().is_relative_to(root):
                    raise ValueError("project source symlink outside checkout")
                files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def package_names(files, command):
    """Derive qualified owners from the search roots installed for this command."""
    roots = {Path("."), Path("src")}
    if command and not command[0].startswith("-"):
        roots.add(Path(command[0]).parent)
    result = set()
    for name in files:
        source = Path(name)
        for search_root in roots:
            if not source.is_relative_to(search_root):
                continue
            parts = source.relative_to(search_root).with_suffix("").parts
            if parts[-1] == "__init__":
                parts = parts[:-1]
            if all(part.isidentifier() for part in parts):
                result.update(".".join(parts[:end]) for end in range(1, len(parts) + 1))
    return result


def worker(root, output, command, names):
    observed, external, errors = {}, {}, set()
    tool_path = Path(__file__).resolve()
    dependencies = dependency_roots()

    def observe(filename, module):
        if not filename or filename.startswith("<"):
            return
        path = Path(filename).resolve()
        if path == tool_path:
            return
        if path.is_relative_to(root) and not dependency_source(path, root, dependencies):
            if path.suffix != ".py":
                errors.add("non-source project module is unsupported")
            elif path.is_file():
                rel = path.relative_to(root).as_posix()
                observed.setdefault(rel, digest(path.read_bytes()))
            else:
                errors.add("executed project source is missing")
        else:
            top = module.split(".")[0]
            if top in names:
                errors.add(f"project import outside checkout: {module}")
            external[module] = str(path)

    def profile(frame, event, arg):
        if event == "call":
            observe(frame.f_code.co_filename, frame.f_globals.get("__name__", ""))

    # SourceFileLoader normally accepts timestamp-valid bytecode. Compile actual
    # project source instead, so a stale .pyc cannot masquerade as reviewed bytes.
    original_code = importlib.machinery.SourceFileLoader.get_code

    def source_code(loader, fullname):
        path = Path(loader.path).resolve()
        if path.is_relative_to(root) and not dependency_source(path, root, dependencies):
            observe(str(path), fullname)
            return loader.source_to_code(loader.get_data(str(path)), str(path))
        return original_code(loader, fullname)

    def audit(event, args):
        if event in {"subprocess.Popen", "os.system", "os.fork", "os.posix_spawn"}:
            errors.add("child process outside supported scope")
        if event == "import" and len(args) > 1 and args[1]:
            observe(str(args[1]), str(args[0]))

    importlib.machinery.SourceFileLoader.get_code = source_code
    original_thread = _thread.start_new_thread

    def start_thread(*args, **kwargs):
        errors.add("additional threads outside supported scope")
        return original_thread(*args, **kwargs)

    _thread.start_new_thread = start_thread
    threading._start_new_thread = start_thread
    sys.addaudithook(audit)
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root))
    sys.setprofile(profile)
    exit_code = 0
    try:
        if len(command) >= 2 and command[0] == "-m":
            sys.argv = command[1:]
            runpy.run_module(command[1], run_name="__main__", alter_sys=True)
        elif command and not command[0].startswith("-"):
            target = inside(root, command[0])
            if target.suffix != ".py":
                raise ValueError("only Python source scripts or -m modules are supported")
            sys.argv = command[:]
            sys.path.insert(0, str(target.parent))
            runpy.run_path(str(target), run_name="__main__")
        else:
            raise ValueError("expected a Python script or -m module command")
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    except (Exception, KeyboardInterrupt) as exc:
        errors.add(f"command raised {type(exc).__name__}")
        logging.getLogger(__name__).exception("replay command failed")
        exit_code = 1
    finally:
        sys.setprofile(None)
        importlib.machinery.SourceFileLoader.get_code = original_code
        _thread.start_new_thread = original_thread
        threading._start_new_thread = original_thread
        for name, module in list(sys.modules.items()):
            observe(getattr(module, "__file__", None), name)
        distributions = importlib.metadata.packages_distributions()
        versions = {}
        for module in external:
            for distribution in distributions.get(module.split(".")[0], []):
                versions[distribution] = importlib.metadata.version(distribution)
        save_json(output, {"sources": observed, "external_modules": external,
                           "external_versions": versions, "python": sys.version,
                           "errors": sorted(errors), "exit_code": exit_code})
    return exit_code


def capture(root, bundle, production, tests, inputs):
    root, bundle = Path(root).resolve(), Path(bundle).resolve()
    if bundle.is_relative_to(root):
        raise ValueError("bundle must be outside checkout")
    for command in (production, tests):
        if not isinstance(command, list) or not command or not all(isinstance(s, str) for s in command):
            raise ValueError("commands must be nonempty JSON arrays of strings")
    before = snapshot(root)
    revision = head(root)
    frozen = {name: inside(root, name).read_bytes() for name in inputs}
    bundle.mkdir(parents=True, exist_ok=False)
    evidence = {}
    for name, data in frozen.items():
        target = inside(bundle / "inputs", name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    runs, errors, sources = {}, [], {}
    for label, command in (("production", production), ("tests", tests)):
        inventory = bundle / f"{label}.inventory.json"
        invocation = [sys.executable, str(Path(__file__).resolve()), "_worker", str(root),
                      str(inventory), json.dumps(command), json.dumps(sorted(package_names(before, command)))]
        with (bundle / f"{label}.stdout").open("wb") as stdout, (bundle / f"{label}.stderr").open("wb") as stderr:
            result = subprocess.run(invocation, cwd=root, env=environment(), stdout=stdout,
                                    stderr=stderr, check=False)
        if not inventory.is_file():
            errors.append(f"{label}: missing runtime inventory")
            observed = {"sources": {}, "errors": [], "exit_code": result.returncode}
        else:
            observed = json.loads(inventory.read_text(encoding="utf-8"))
        errors.extend(f"{label}: {error}" for error in observed["errors"])
        if result.returncode or observed["exit_code"]:
            errors.append(f"{label}: command failed")
        if not observed["sources"]:
            errors.append(f"{label}: no project sources observed")
        for name, value in observed["sources"].items():
            if name not in before or digest(before[name]) != value:
                errors.append(f"{label}: source drift: {name}")
            else:
                sources[name] = value
        runs[label] = {**observed, "command": [sys.executable, *command]}
        for suffix in ("stdout", "stderr", "inventory.json"):
            path = bundle / f"{label}.{suffix}"
            if path.is_file():
                evidence[path.name] = digest(path.read_bytes())
        after = snapshot(root)
        if after != before:
            errors.append(f"{label}: checkout source drift")
        if head(root) != revision:
            errors.append(f"{label}: revision changed")
        for name, data in frozen.items():
            path = inside(root, name)
            if not path.is_file() or path.read_bytes() != data:
                errors.append(f"{label}: frozen input changed: {name}")
    for name in sources:
        target = inside(bundle / "sources", name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(before[name])
    receipt = {"schema": SCHEMA, "revision": revision,
               "recorder_sha256": digest(Path(__file__).read_bytes()),
               "sources": sources, "runs": runs,
               "inputs": {name: digest(data) for name, data in frozen.items()},
               "evidence": evidence, "checkout_sources": {name: digest(data) for name, data in before.items()},
               "exact_current": not errors, "errors": errors, "limitations": LIMITATIONS}
    save_json(bundle / "receipt.json", receipt)
    return receipt


def verify(root, bundle, receipt_sha256):
    root, bundle = Path(root).resolve(), Path(bundle).resolve()
    raw = (bundle / "receipt.json").read_bytes()
    if digest(raw) != receipt_sha256:
        return ["receipt digest mismatch"]
    receipt = json.loads(raw)
    errors = []
    if receipt["schema"] != SCHEMA or not receipt["exact_current"]:
        errors.append("receipt does not establish exact-current observations")
    if head(root) != receipt["revision"]:
        errors.append("revision changed")
    if digest(Path(__file__).read_bytes()) != receipt["recorder_sha256"]:
        errors.append("recorder changed")
    if {name: digest(data) for name, data in snapshot(root).items()} != receipt["checkout_sources"]:
        errors.append("checkout source drift")
    groups = [(bundle, receipt["evidence"]), (bundle / "sources", receipt["sources"]),
              (bundle / "inputs", receipt["inputs"]), (root, receipt["inputs"])]
    for base, entries in groups:
        for name, expected in entries.items():
            path = inside(base, name)
            if not path.is_file() or digest(path.read_bytes()) != expected:
                errors.append(f"missing or changed evidence: {name}")
    union = set().union(*(set(run["sources"]) for run in receipt["runs"].values()))
    if union != set(receipt["sources"]):
        errors.append("runtime closure differs from bundled sources")
    return errors


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "_worker":
        return worker(Path(sys.argv[2]), Path(sys.argv[3]), json.loads(sys.argv[4]), json.loads(sys.argv[5]))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["capture", "verify"])
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--production", type=json.loads)
    parser.add_argument("--tests", type=json.loads)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--receipt-sha256")
    args = parser.parse_args()
    try:
        if args.action == "capture":
            receipt = capture(args.root, args.bundle, args.production, args.tests, args.input)
            print(json.dumps({"exact_current": receipt["exact_current"], "errors": receipt["errors"],
                              "receipt_sha256": digest((args.bundle / "receipt.json").read_bytes())}))
            return 0 if receipt["exact_current"] else 1
        if not args.receipt_sha256:
            raise ValueError("verify requires an independently retained receipt SHA-256")
        errors = verify(args.root, args.bundle, args.receipt_sha256)
        print(json.dumps({"errors": errors}))
        return 1 if errors else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
