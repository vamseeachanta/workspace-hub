"""Fake-only discovery: unverified cleanup releases Deckhand's seat lock.

Only git show launches a subprocess. No native API, taskkill, queue or task
is invoked. All runtime process and lock filesystem operations are doubles.
"""
import argparse
import ast
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

REVISION = "ea24989c521dcab30ba5428cc5c8f791d273ed36"
RUNTIME = "src/deckhand/licensed_run_agent_runtime.py"
AGENT = "src/deckhand/licensed_run_agent.py"


class FakeProcess:
    pid = 12345
    returncode = None

    def communicate(self, timeout=None):
        raise subprocess.TimeoutExpired("FAKE", timeout)

    def kill(self):
        raise PermissionError("fake denied kill")


class FakePath:
    def __init__(self):
        self.removed = False

    @property
    def parent(self):
        return self

    def mkdir(self, **kwargs):
        pass

    def unlink(self):
        self.removed = True

    def __str__(self):
        return "fake-seat-lock"


def read_source(checkout, name):
    return subprocess.check_output(
        ["git", "-C", str(checkout), "show", REVISION + ":" + name],
        text=True, encoding="utf-8", timeout=15,
    )


def inject_doubles(namespace, process, path, attempts):
    namespace["subprocess"] = SimpleNamespace(
        Popen=lambda *args, **kwargs: process,
        PIPE=-1, CREATE_NEW_PROCESS_GROUP=512,
        TimeoutExpired=subprocess.TimeoutExpired,
        run=lambda *args, **kwargs: attempts.append("taskkill denied")
        or SimpleNamespace(returncode=1),
    )
    namespace["os"] = SimpleNamespace(
        name="nt", environ={}, O_CREAT=1, O_EXCL=2, O_WRONLY=4,
        open=lambda *args: 99, write=lambda *args: None,
        getpid=lambda: 999, close=lambda *args: None,
    )
    namespace["Path"] = lambda *args: path
    namespace["solver_root"] = lambda config: None


def reproduce(checkout):
    source = read_source(checkout, RUNTIME)
    agent_source = read_source(checkout, AGENT)
    namespace = {"__name__": "fake_runtime"}
    exec(compile(source, RUNTIME, "exec"), namespace)
    process, path, attempts = FakeProcess(), FakePath(), []
    inject_doubles(namespace, process, path, attempts)
    node = next(n for n in ast.parse(agent_source).body
                if isinstance(n, ast.FunctionDef) and n.name == "_execute_with_lock")
    function = "from __future__ import annotations\n" + ast.get_source_segment(agent_source, node)
    exec(compile(function, AGENT, "exec"), namespace)
    result = namespace["_execute_with_lock"](
        path, {"lock_path": "fake"}, path, path, None, 0, timeout_seconds=1,
    )
    assert result["returncode"] == 124 and result["timed_out"]
    assert "process tree killed" in result["stderr"]
    assert path.removed and process.returncode is None
    return {
        "source_revision": REVISION,
        "source_files": [RUNTIME, AGENT],
        "method": "pinned source with fake process, OS and filesystem operations",
        "result": result,
        "kill_attempts": attempts,
        "fake_process_still_unreaped": process.returncode is None,
        "seat_lock_removed": path.removed,
        "actual_solver_or_cleanup_processes_spawned": 0,
        "runtime_filesystem_mutations": 0,
        "native_verification": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deckhand-checkout", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = json.dumps(reproduce(args.deckhand_checkout), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
