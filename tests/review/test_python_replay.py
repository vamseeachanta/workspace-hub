"""Synthetic import graphs, independently enumerated in each test; no solver evidence."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/review/python_replay.py"


def tool():
    spec = importlib.util.spec_from_file_location("python_replay", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "checkout"
    root.mkdir()
    write(root, "sample/__init__.py", "")
    write(root, "sample/helper.py", "VALUE = 7\n")
    write(root, "sample/main.py", "def run():\n    from .helper import VALUE\n    print(VALUE)\nrun()\n")
    write(root, "test_run.py", "import importlib\nassert importlib.import_module('sample.helper').VALUE == 7\n")
    write(root, "input.json", '{"synthetic": true}\n')
    return root


def capture(project, tmp_path, production=None, tests=None):
    return tool().capture(project, tmp_path / "bundle", production or ["-m", "sample.main"],
                          tests or ["test_run.py"], ["input.json"])


def test_separate_actual_closures_and_retained_bytes(project, tmp_path):
    """By inspection: main calls helper; test imports helper; both load the initializer."""
    receipt = capture(project, tmp_path)
    assert receipt["exact_current"] is True, receipt["errors"]
    assert set(receipt["runs"]["production"]["sources"]) == {
        "sample/__init__.py", "sample/main.py", "sample/helper.py"}
    assert set(receipt["runs"]["tests"]["sources"]) == {
        "test_run.py", "sample/__init__.py", "sample/helper.py"}
    bundle = tmp_path / "bundle"
    for name, digest in receipt["sources"].items():
        assert hashlib.sha256((bundle / "sources" / name).read_bytes()).hexdigest() == digest
    assert (bundle / "production.stdout").read_bytes() == b"7\n"
    assert receipt["inputs"]["input.json"] == hashlib.sha256(b'{"synthetic": true}\n').hexdigest()
    pin = hashlib.sha256((bundle / "receipt.json").read_bytes()).hexdigest()
    assert tool().verify(project, bundle, pin) == []


@pytest.mark.parametrize("missing", ["sample/helper.py", "sample/__init__.py"])
def test_bundle_cannot_omit_helper_or_parent(project, tmp_path, missing):
    """Both files are required by the literal import graph in the fixture."""
    capture(project, tmp_path)
    bundle = tmp_path / "bundle"
    pin = hashlib.sha256((bundle / "receipt.json").read_bytes()).hexdigest()
    (bundle / "sources" / missing).unlink()
    assert tool().verify(project, bundle, pin)


def test_dynamic_import_removed_from_sys_modules_is_retained(project, tmp_path):
    write(project, "sample/ephemeral.py", "VALUE = 11\n")
    write(project, "test_run.py", "import importlib, sys\nimportlib.import_module('sample.ephemeral')\ndel sys.modules['sample.ephemeral']\n")
    receipt = capture(project, tmp_path)
    assert receipt["exact_current"]
    assert "sample/ephemeral.py" in receipt["runs"]["tests"]["sources"]


def test_source_change_during_run_refuses_current(project, tmp_path):
    write(project, "test_run.py", "from pathlib import Path\nPath('sample/helper.py').write_text('VALUE = 8\\n')\n")
    receipt = capture(project, tmp_path)
    assert not receipt["exact_current"]
    assert any("source drift" in error for error in receipt["errors"])


def test_source_drift_after_capture_refuses_verify(project, tmp_path):
    capture(project, tmp_path)
    bundle = tmp_path / "bundle"
    pin = hashlib.sha256((bundle / "receipt.json").read_bytes()).hexdigest()
    write(project, "sample/helper.py", "VALUE = 9\n")
    assert tool().verify(project, bundle, pin)


def test_import_from_other_checkout_refuses_current(project, tmp_path):
    outside = tmp_path / "other"
    write(outside, "sample/__init__.py", "")
    write(outside, "sample/helper.py", "VALUE = 7\n")
    write(project, "test_run.py", f"import sys\nsys.path.insert(0, {str(outside)!r})\nimport sample.helper\n")
    receipt = capture(project, tmp_path)
    assert not receipt["exact_current"]
    assert any("outside checkout" in error for error in receipt["errors"])


@pytest.mark.parametrize("target", ["tests.stdout", "inputs/input.json", "tests.inventory.json"])
def test_evidence_tampering_is_rejected(project, tmp_path, target):
    capture(project, tmp_path)
    bundle = tmp_path / "bundle"
    pin = hashlib.sha256((bundle / "receipt.json").read_bytes()).hexdigest()
    (bundle / target).write_bytes(b"tampered")
    assert tool().verify(project, bundle, pin)


def test_receipt_edit_cannot_remove_inventory_entry(project, tmp_path):
    capture(project, tmp_path)
    bundle = tmp_path / "bundle"
    pin = hashlib.sha256((bundle / "receipt.json").read_bytes()).hexdigest()
    receipt = json.loads((bundle / "receipt.json").read_text())
    receipt["sources"].pop("sample/helper.py")
    (bundle / "receipt.json").write_text(json.dumps(receipt))
    assert tool().verify(project, bundle, pin) == ["receipt digest mismatch"]


def test_failed_tests_refuse_current(project, tmp_path):
    write(project, "test_run.py", "raise SystemExit(1)\n")
    assert not capture(project, tmp_path)["exact_current"]


def test_worker_clears_inherited_git_bindings(project, tmp_path, monkeypatch):
    caller = tmp_path / "unrelated"
    sentinel = write(caller, ".git/sentinel", "caller metadata\n")
    target_metadata = write(project, ".git/sentinel", "target metadata\n")
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        monkeypatch.setenv(key, str(caller / ".git"))
    before = (project / "sample/main.py").read_bytes()
    assert capture(project, tmp_path)["exact_current"]
    assert (project / "sample/main.py").read_bytes() == before
    assert sentinel.read_bytes() == b"caller metadata\n"
    assert target_metadata.read_bytes() == b"target metadata\n"


def test_cli_capture_and_verify(project, tmp_path):
    bundle = tmp_path / "bundle"
    result = subprocess.run([sys.executable, str(SCRIPT), "capture", "--root", str(project),
                             "--bundle", str(bundle), "--production", '["-m", "sample.main"]',
                             "--tests", '["test_run.py"]', "--input", "input.json"],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    pin = json.loads(result.stdout)["receipt_sha256"]
    checked = subprocess.run([sys.executable, str(SCRIPT), "verify", "--root", str(project),
                              "--bundle", str(bundle), "--receipt-sha256", pin],
                             capture_output=True, text=True, check=False)
    assert checked.returncode == 0, checked.stderr


def test_actual_pytest_command_is_retained(project, tmp_path):
    """One test, one direct import, and the two package files are enumerated by inspection."""
    write(project, "test_run.py", "def test_value():\n    from sample.helper import VALUE\n    assert VALUE == 7\n")
    args = ["-m", "pytest", "test_run.py", "-q", "-p", "no:cacheprovider",
            "--basetemp=" + str(tmp_path / "pytest-temp")]
    receipt = capture(project, tmp_path, tests=args)
    assert receipt["exact_current"], receipt["errors"]
    assert receipt["runs"]["tests"]["command"][1:] == args
    assert set(receipt["runs"]["tests"]["sources"]) == {
        "test_run.py", "sample/__init__.py", "sample/helper.py"}
    assert "pytest" in receipt["runs"]["tests"]["external_versions"]
    assert b"1 passed" in (tmp_path / "bundle/tests.stdout").read_bytes()


def test_transient_source_change_at_import_is_rejected(project, tmp_path):
    """The helper changes 7 to 8 for execution, then restores its original bytes."""
    write(project, "test_run.py", "from pathlib import Path\np = Path('sample/helper.py')\nold = p.read_bytes()\np.write_text('VALUE = 8\\n')\nimport sample.helper\np.write_bytes(old)\n")
    receipt = capture(project, tmp_path)
    assert not receipt["exact_current"]
    assert any("source drift: sample/helper.py" in error for error in receipt["errors"])


def test_joined_thread_refuses_current(project, tmp_path):
    write(project, "test_run.py", "import threading\nt = threading.Thread(target=lambda: None)\nt.start()\nt.join()\n")
    receipt = capture(project, tmp_path)
    assert not receipt["exact_current"]
    assert any("threads" in error for error in receipt["errors"])


def test_child_process_refuses_current(project, tmp_path):
    write(project, "test_run.py", "import subprocess, sys\nsubprocess.run([sys.executable, '-c', 'pass'], check=True)\n")
    receipt = capture(project, tmp_path)
    assert not receipt["exact_current"]
    assert any("child process" in error for error in receipt["errors"])


def test_bundle_cannot_overwrite_checkout(project):
    with pytest.raises(ValueError, match="outside checkout"):
        tool().capture(project, project / "output", ["-m", "sample.main"], ["test_run.py"], [])


def test_input_path_cannot_escape(project, tmp_path):
    with pytest.raises(ValueError, match="outside checkout"):
        tool().capture(project, tmp_path / "bundle", ["-m", "sample.main"], ["test_run.py"], ["../other"])


def test_low_level_thread_refuses_current(project, tmp_path):
    write(project, "test_run.py", "import _thread, threading\ndone = threading.Event()\n_thread.start_new_thread(done.set, ())\ndone.wait()\n")
    receipt = capture(project, tmp_path)
    assert not receipt["exact_current"]
    assert any("threads" in error for error in receipt["errors"])


def test_revision_drift_refuses_current(project, tmp_path, monkeypatch):
    recorder = tool()
    revisions = iter(["before", "after", "after"])
    monkeypatch.setattr(recorder, "head", lambda root: next(revisions))
    receipt = recorder.capture(project, tmp_path / "bundle", ["-m", "sample.main"], ["test_run.py"], [])
    assert not receipt["exact_current"]
    assert any("revision changed" in error for error in receipt["errors"])


def test_empty_project_closure_refuses_current(project, tmp_path):
    receipt = capture(project, tmp_path, production=["-m", "this"])
    assert not receipt["exact_current"]
    assert any("no project sources" in error for error in receipt["errors"])


def test_script_imports_sibling_helper(project, tmp_path):
    write(project, "bin/helper.py", "VALUE = 7\n")
    write(project, "bin/run.py", "from helper import VALUE\nprint(VALUE)\n")
    receipt = capture(project, tmp_path, production=["bin/run.py"])
    assert receipt["exact_current"], receipt["errors"]
    assert set(receipt["runs"]["production"]["sources"]) == {"bin/run.py", "bin/helper.py"}


@pytest.mark.parametrize("layout", ["", "src/"])
def test_qualified_json_coexists_with_standard_library(tmp_path, layout):
    project = tmp_path / "layout-checkout"
    write(project, "input.json", "{}")
    write(project, layout + "sample/__init__.py", "")
    write(project, layout + "sample/json.py", "VALUE = 13\n")
    command = "import json, sample.json\nassert json.loads('13') == sample.json.VALUE\n"
    write(project, "run.py", command)
    receipt = capture(project, tmp_path, production=["run.py"], tests=["run.py"])
    assert receipt["exact_current"], receipt["errors"]
    for run in receipt["runs"].values():
        assert run["exit_code"] == 0
        assert layout + "sample/json.py" in run["sources"]
        assert "json" in run["external_modules"]


@pytest.mark.parametrize("layout", ["", "src/"])
def test_qualified_json_still_rejects_foreign_package(tmp_path, layout):
    project = tmp_path / "layout-checkout"
    write(project, "input.json", "{}")
    write(project, "run.py", "import sample.json\n")
    write(project, layout + "sample/__init__.py", "")
    write(project, layout + "sample/json.py", "VALUE = 13\n")
    outside = tmp_path / "foreign"
    write(outside, "sample/__init__.py", "")
    write(outside, "sample/json.py", "VALUE = 13\n")
    write(project, "test_run.py", f"import sys\nsys.path.insert(0, {str(outside)!r})\nimport sample.json\n")
    receipt = capture(project, tmp_path, production=["run.py"])
    assert receipt["runs"]["tests"]["exit_code"] == 0
    assert not receipt["exact_current"]
    assert "tests: project import outside checkout: sample.json" in receipt["errors"]


def test_sibling_names_apply_only_to_the_script_context(project, tmp_path):
    write(project, "bin/json.py", "VALUE = 13\n")
    write(project, "test_run.py", "import json\nassert json.loads('13') == 13\n")
    receipt = capture(project, tmp_path)
    assert receipt["exact_current"], receipt["errors"]


def test_script_context_rejects_foreign_sibling(project, tmp_path):
    write(project, "bin/helper.py", "VALUE = 13\n")
    outside = tmp_path / "foreign"
    write(outside, "helper.py", "VALUE = 13\n")
    write(project, "bin/run.py", f"import sys\nsys.path.insert(0, {str(outside)!r})\nimport helper\n")
    receipt = capture(project, tmp_path, production=["bin/run.py"])
    assert receipt["runs"]["production"]["exit_code"] == 0
    assert "production: project import outside checkout: helper" in receipt["errors"]


@pytest.mark.parametrize("environment_dir", [".venv", "venv"])
def test_environment_dependency_is_external(project, tmp_path, environment_dir):
    dependency = environment_dir + "/deps/vendor_dep.py"
    write(project, dependency, "VALUE = 13\n")
    command = (f"import sys\nsys.path.insert(0, {str(project / environment_dir / 'deps')!r})\n"
               "import vendor_dep\nassert vendor_dep.VALUE == 13\n")
    write(project, "run.py", command)
    receipt = capture(project, tmp_path, production=["run.py"], tests=["run.py"])
    assert receipt["exact_current"], receipt["errors"]
    assert dependency not in receipt["checkout_sources"]
    for run in receipt["runs"].values():
        assert run["exit_code"] == 0
        assert set(run["sources"]) == {"run.py"}
        assert run["external_modules"]["vendor_dep"] == str(project / dependency)
    assert not (tmp_path / "bundle/sources" / dependency).exists()


@pytest.mark.parametrize("environment_dir", [".venv", "runtime"])
def test_local_interpreter_dependency_versions(project, tmp_path, environment_dir):
    environment = project / environment_dir
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(environment)], check=True)
    executable = environment / "bin/python"
    result = subprocess.run([str(executable), "-c",
                             "import sysconfig; print(sysconfig.get_path('purelib'))"],
                            capture_output=True, text=True, check=True)
    library = Path(result.stdout.strip())
    dependency = write(library, "vendor_dep.py", "VALUE = 13\n")
    write(library, "synthetic_dependency-1.2.dist-info/METADATA",
          "Metadata-Version: 2.1\nName: synthetic-dependency\nVersion: 1.2\n")
    write(library, "synthetic_dependency-1.2.dist-info/top_level.txt", "vendor_dep\n")
    write(project, "run.py", "import vendor_dep\nassert vendor_dep.VALUE == 13\n")
    bundle = tmp_path / "bundle"
    result = subprocess.run([str(executable), str(SCRIPT), "capture", "--root", str(project),
                             "--bundle", str(bundle), "--production", '["run.py"]',
                             "--tests", '["run.py"]'], capture_output=True, text=True, check=False)
    receipt = json.loads((bundle / "receipt.json").read_text())
    assert result.returncode == 0, receipt["errors"]
    assert receipt["exact_current"]
    assert dependency.relative_to(project).as_posix() not in receipt["checkout_sources"]
    for run in receipt["runs"].values():
        assert set(run["sources"]) == {"run.py"}
        assert run["external_modules"]["vendor_dep"] == str(dependency)
        assert run["external_versions"]["synthetic-dependency"] == "1.2"
    pin = json.loads(result.stdout)["receipt_sha256"]
    checked = subprocess.run([str(executable), str(SCRIPT), "verify", "--root", str(project),
                              "--bundle", str(bundle), "--receipt-sha256", pin],
                             capture_output=True, text=True, check=False)
    assert checked.returncode == 0, checked.stdout


def test_arbitrary_project_dependency_retains_closure_checks(project, tmp_path):
    write(project, "lib/vendor_dep.py", "VALUE = 13\n")
    write(project, "run.py", "import sys\nsys.path.insert(0, 'lib')\nimport vendor_dep\n")
    receipt = capture(project, tmp_path, production=["run.py"], tests=["run.py"])
    assert receipt["exact_current"], receipt["errors"]
    assert "lib/vendor_dep.py" in receipt["sources"]
    bundle = tmp_path / "bundle"
    pin = hashlib.sha256((bundle / "receipt.json").read_bytes()).hexdigest()
    write(project, "lib/vendor_dep.py", "VALUE = 17\n")
    assert "checkout source drift" in tool().verify(project, bundle, pin)


def test_environment_cannot_supply_foreign_project_package(project, tmp_path):
    outside = project / ".venv/deps"
    write(outside, "sample/__init__.py", "")
    write(outside, "sample/helper.py", "VALUE = 7\n")
    write(project, "test_run.py", f"import sys\nsys.path.insert(0, {str(outside)!r})\nimport sample.helper\n")
    receipt = capture(project, tmp_path)
    assert not receipt["exact_current"]
    assert "tests: project import outside checkout: sample.helper" in receipt["errors"]
