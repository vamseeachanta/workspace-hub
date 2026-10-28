"""Real-wheel resolver smoke and adversarial loaded-module placement fixtures.

The command-line recipe uses only the standard library and the existing uv tool.
See docs/testing/installed-wheel-provenance.md for scope and independent oracles.
"""
from __future__ import annotations

import argparse
import importlib
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
import zipfile
from email.parser import Parser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLE = "wheel_provenance_fixture"


def _assert_provenance(inventory, expected, expected_root):
    """Check loaded concrete modules; inventory and route oracle are independent."""
    root = Path(expected_root).resolve()
    prefixes = {name.partition(".")[0] for name in inventory}
    resolved = {}
    violations = {}
    for name, module in sorted(sys.modules.copy().items()):
        if name not in inventory and not any(
            name == prefix or name.startswith(prefix + ".") for prefix in prefixes
        ):
            continue
        file = getattr(module, "__file__", None)
        if file is None:
            spec = getattr(module, "__spec__", None)
            if (spec is not None and spec.origin is None
                    and spec.submodule_search_locations is not None):
                continue  # PEP 420 namespaces have no concrete module file.
            violations[name] = "no concrete file and not a namespace package"
            continue
        path = Path(file).resolve()
        resolved[name] = path
        if not path.is_relative_to(root):
            violations[name] = "outside external purelib"
        elif name not in inventory:
            violations[name] = "absent from wheel module inventory"
        elif path != (root / inventory[name]).resolve():
            violations[name] = "does not match the wheel member"
    assert not violations, f"Module provenance: {violations}"
    assert resolved, "No concrete project modules loaded"
    assert set(expected) <= resolved.keys(), "Expected route modules were not checked"
    return resolved


def _clean_environment():
    return {
        key: value for key, value in os.environ.items()
        if not key.startswith("GIT_")
        and key not in {"PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE", "PYTHONSTARTUP"}
    }


def _run(arguments, cwd, environment):
    result = subprocess.run(
        [str(argument) for argument in arguments], cwd=cwd, env=environment,
        text=True, capture_output=True,
    )
    # POSIX exit status zero denotes success; subprocess.run documents returncode.
    if result.returncode:
        raise AssertionError(
            f"Subprocess failed: {arguments}\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def _module_inventory(members):
    inventory = {}
    for member in members:
        path = Path(member)
        if path.suffix != ".py" or any(part.endswith(".dist-info") for part in path.parts):
            continue
        parts = path.with_suffix("").parts
        if path.stem == "__init__":
            parts = path.parent.parts
        inventory[".".join(parts)] = member
    return inventory


def run_smoke(scratch, uv):
    """Build once, install without transitive dependencies, then probe externally."""
    scratch = Path(scratch).resolve()
    assert not scratch.is_relative_to(REPO_ROOT), "Scratch must be outside the checkout"
    scratch.mkdir(parents=True, exist_ok=True)
    # Refuse reuse rather than silently exercising an earlier wheel or environment.
    source = scratch / "source"
    source.mkdir()
    shutil.copyfile(REPO_ROOT / "pyproject.toml", source / "pyproject.toml")
    shutil.copytree(
        REPO_ROOT / "src", source / "src",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info"),
    )
    metadata = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))
    build_system = metadata["build-system"]
    environment = _clean_environment()
    temporary = scratch / "tmp"
    temporary.mkdir()
    environment["TMPDIR"] = str(temporary)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environments = {}
    for purpose in ("build", "runtime"):
        destination = scratch / purpose
        _run(
            [sys.executable, "-I", "-B", "-m", "venv", "--without-pip", destination],
            scratch, environment,
        )
        executable = destination / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        environments[purpose] = executable
    _run(
        [uv, "pip", "install", "--python", environments["build"],
         *build_system["requires"]], scratch, environment,
    )
    wheels = scratch / "wheels"
    wheels.mkdir()
    backend_code = (
        "import importlib, sys; "
        "_, name, destination = sys.argv; "
        "backend = importlib.import_module(name); backend.build_wheel(destination)"
    )
    _run(
        [environments["build"], "-I", "-B", "-c", backend_code,
         build_system["build-backend"], wheels], source, environment,
    )
    # Tuple unpacking requires exactly one wheel from this backend invocation.
    wheel, = wheels.glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        members = archive.namelist()
        inventory = _module_inventory(members)
        resolver_member, = (
            member for member in members
            if member.endswith("workspace_hub/workstations/resolver.py")
        )
        entry, = (name for name, member in inventory.items() if member == resolver_member)
        metadata_member, = (name for name in members if name.endswith(".dist-info/METADATA"))
        wheel_metadata = Parser().parsestr(archive.read(metadata_member).decode("utf-8"))
        dependency, = (
            requirement for requirement in wheel_metadata.get_all("Requires-Dist", [])
            if re.match(r"(?i)^pyyaml(?:\s|[<>=!~;(]|$)", requirement)
                and not re.search(r"\bextra\s*[!=]", requirement)
        )
    _run(
        [uv, "pip", "install", "--python", environments["runtime"],
         "--no-deps", wheel, dependency], scratch, environment,
    )
    # Static route oracle, independently read from src/__init__.py and the
    # workstations package's local import. Do not infer it from loaded modules.
    expected = {
        "src": "src/__init__.py",
        "src.workspace_hub.workstations": "src/workspace_hub/workstations/__init__.py",
        "src.workspace_hub.workstations.resolver": "src/workspace_hub/workstations/resolver.py",
    }
    assert inventory.items() >= expected.items(), "Wheel changed the bounded route layout"
    probe = (
        "import importlib, importlib.metadata, json, os, site, sys, sysconfig\n"
        "from pathlib import Path\n"
        + inspect.getsource(_assert_provenance)
        + "\n" + inspect.getsource(_external_probe)
        + "\n_, configuration = sys.argv\n"
        "print(json.dumps(_external_probe(json.loads(configuration))))\n"
    )
    configuration = {
        "inventory": inventory, "expected": expected, "entry": entry,
        "checkout": str(REPO_ROOT), "environment": str(environments["runtime"].parent.parent),
    }
    report = json.loads(_run(
        [environments["runtime"], "-I", "-B", "-c", probe, json.dumps(configuration)],
        scratch, environment,
    ))
    (scratch / "report.json").write_text(json.dumps(report, indent=True) + "\n", encoding="utf-8")
    return report


def _external_probe(configuration):
    """Executed only by the wheel environment's isolated interpreter."""
    assert sys.prefix != sys.base_prefix
    assert site.ENABLE_USER_SITE is False
    assert "PYTHONPATH" not in os.environ
    assert not any(key.startswith("GIT_") for key in os.environ)
    checkout = Path(configuration["checkout"]).resolve()
    assert not Path.cwd().resolve().is_relative_to(checkout)
    assert not any(Path(path).resolve().is_relative_to(checkout) for path in sys.path)
    purelib = Path(sysconfig.get_path("purelib")).resolve()
    assert purelib.is_relative_to(Path(configuration["environment"]).resolve())
    distributions = {
        distribution.metadata["Name"].lower().replace("_", "-")
        for distribution in importlib.metadata.distributions()
    }
    assert distributions == {"workspace-hub", "pyyaml"}
    resolver = importlib.import_module(configuration["entry"])
    # After import, the bounded route is entirely in memory. Reject any file read.
    resources = []

    def record_open(event, arguments):
        if event == "open":
            resources.append(str(arguments))

    sys.addaudithook(record_open)
    instance = resolver.WorkstationPathResolver({})
    no_match = instance.resolve_machine("unregistered")
    assert no_match is None
    assert not resources, "The in-memory route unexpectedly opened a file"
    resolved = _assert_provenance(configuration["inventory"], configuration["expected"], purelib)
    namespaces = sorted(
        name for name, module in sys.modules.copy().items()
        if (name == "src" or name.startswith("src."))
        and getattr(module, "__file__", None) is None
    )
    return {
        "entry_module": configuration["entry"], "concrete_modules": sorted(resolved),
        "namespace_modules": namespaces, "resources_read": [], "no_match": no_match,
    }


def test_real_installed_resolver_modules_are_under_external_purelib(real_installation):
    report = real_installation
    assert report["entry_module"] == "src.workspace_hub.workstations.resolver"
    # Independent oracle: wheel files and the static local imports listed in the doc.
    assert set(report["concrete_modules"]) == {
        "src", "src.workspace_hub.workstations",
        "src.workspace_hub.workstations.resolver",
    }
    assert report["namespace_modules"] == ["src.workspace_hub"]
    assert report["resources_read"] == []
    assert report["no_match"] is None


def test_nested_module_outside_root_is_rejected(mixed_layout):
    layout = mixed_layout("outside")
    assert layout["expected"][EXAMPLE].is_relative_to(layout["root"])
    assert not layout["expected"][EXAMPLE + ".nested"].is_relative_to(layout["root"])
    with pytest.raises(AssertionError, match="Module provenance") as failure:
        _assert_provenance(layout["inventory"], layout["expected"], layout["root"])
    assert EXAMPLE + ".nested" in str(failure.value)


def test_similar_directory_prefix_is_not_containment(mixed_layout):
    layout = mixed_layout("similar")
    nested = layout["expected"][EXAMPLE + ".nested"]
    assert str(nested).startswith(str(layout["root"]))
    assert not nested.is_relative_to(layout["root"])
    with pytest.raises(AssertionError, match="Module provenance") as failure:
        _assert_provenance(layout["inventory"], layout["expected"], layout["root"])
    assert EXAMPLE + ".nested" in str(failure.value)


def test_symlinked_module_escape_is_rejected(mixed_layout):
    layout = mixed_layout("symlink")
    imported = sys.modules[EXAMPLE + ".nested"]
    assert Path(imported.__file__).is_symlink()
    assert Path(imported.__file__).resolve() == layout["expected"][EXAMPLE + ".nested"]
    with pytest.raises(AssertionError, match="Module provenance") as failure:
        _assert_provenance(layout["inventory"], layout["expected"], layout["root"])
    assert EXAMPLE + ".nested" in str(failure.value)


def test_unrelated_module_does_not_change_project_membership(mixed_layout):
    layout = mixed_layout("inside")
    before = _assert_provenance(layout["inventory"], layout["expected"], layout["root"])
    assert before == layout["expected"]
    unrelated = importlib.import_module(EXAMPLE + "_extra")
    assert not Path(unrelated.__file__).resolve().is_relative_to(layout["root"])
    assert _assert_provenance(
        layout["inventory"], layout["expected"], layout["root"],
    ) == before


# Script execution must not depend on pytest being installed in either environment.
if __name__ != "__main__":
    import pytest

    @pytest.fixture(scope="module")
    def real_installation(tmp_path_factory):
        scratch = tmp_path_factory.mktemp("real-wheel")
        return run_smoke(scratch, os.environ.get("UV_BIN", "uv"))

    @pytest.fixture
    def mixed_layout(tmp_path, monkeypatch):
        """Import real files before checking provenance; import errors cannot pass."""
        original = {
            name: module for name, module in sys.modules.copy().items()
            if name == EXAMPLE or name.startswith(EXAMPLE + ".")
            or name == EXAMPLE + "_extra"
        }

        def load(placement):
            root = tmp_path / "purelib"
            package = root / EXAMPLE
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "entry.py").write_text(
                "from . import nested\n"
                "def exercise():\n"
                "    from . import lazy\n"
                "    return nested.VALUE, lazy.VALUE\n", encoding="utf-8",
            )
            (package / "lazy.py").write_text("VALUE = 'lazy'\n", encoding="utf-8")
            if placement == "inside":
                nested_parent = package
            else:
                outside = "purelib-extra" if placement == "similar" else "outside"
                nested_parent = tmp_path / outside / EXAMPLE
                nested_parent.mkdir(parents=True)
            nested = nested_parent / "nested.py"
            nested.write_text("VALUE = 'nested'\n", encoding="utf-8")
            if placement == "symlink":
                # An unsupported symlink operation is an acceptance error, never a skip.
                (package / "nested.py").symlink_to(nested)
            monkeypatch.syspath_prepend(str(root))
            top = importlib.import_module(EXAMPLE)
            if placement in {"outside", "similar"}:
                top.__path__.append(str(nested_parent))
            entry = importlib.import_module(EXAMPLE + ".entry")
            assert EXAMPLE + ".lazy" not in sys.modules
            assert entry.exercise() == ("nested", "lazy")
            # Expected membership follows these four file placements, not the checker.
            expected = {
                EXAMPLE: (package / "__init__.py").resolve(),
                EXAMPLE + ".entry": (package / "entry.py").resolve(),
                EXAMPLE + ".nested": nested.resolve(),
                EXAMPLE + ".lazy": (package / "lazy.py").resolve(),
            }
            inventory = {
                EXAMPLE: EXAMPLE + "/__init__.py",
                EXAMPLE + ".entry": EXAMPLE + "/entry.py",
                EXAMPLE + ".nested": EXAMPLE + "/nested.py",
                EXAMPLE + ".lazy": EXAMPLE + "/lazy.py",
            }
            for name, file in expected.items():
                assert Path(sys.modules[name].__file__).resolve() == file
            other_root = tmp_path / "unrelated"
            other_root.mkdir()
            (other_root / (EXAMPLE + "_extra.py")).write_text("", encoding="utf-8")
            monkeypatch.syspath_prepend(str(other_root))
            return {"root": root, "expected": expected, "inventory": inventory}

        yield load
        for name in list(sys.modules):
            if name == EXAMPLE or name.startswith(EXAMPLE + ".") or name == EXAMPLE + "_extra":
                del sys.modules[name]
        sys.modules.update(original)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--uv", default=os.environ.get("UV_BIN", "uv"))
    arguments = parser.parse_args()
    print(json.dumps(run_smoke(arguments.scratch, arguments.uv), indent=True))
