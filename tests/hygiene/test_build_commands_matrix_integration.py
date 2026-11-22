"""Producer/verifier integration using a locally defined synthetic example.

Hand projection: alpha precedes beta; alpha's supplied pass covers build and
test, sorted in that order. Beta has no observation, so it stays unverified
with no evidence references. Both roles permit empty CLI requirements. The full
expected mapping below is literal, never obtained from the producer's functions.
Two verifier runs are a locally chosen repeatability check. Exit codes
follow BUILD_COMMANDS.md, Findings and exit codes. All writes use tmp_path or the
external temporary root supplied to pytest, never the working repository.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

# This file is in tests/hygiene, two directories below the repository root.
ROOT = Path(__file__).resolve().parents[2]
PRODUCER = "scripts/reporting/readiness_matrix_view.py"
CHECKER = ROOT / "scripts/hygiene/check_build_commands.py"
REGISTRY = "synthetic-registry.json"
EVIDENCE = "synthetic-evidence.json"
ARTIFACTS = "artifacts.registry.json"
OUTPUTS = {"json": "docs/reports/matrix.json", "html": "docs/reports/matrix.html"}

# Independent hand calculation from the locally defined synthetic inputs.
EXPECTED = {
    "rows": [
        {
            "role": "alpha",
            "task_classes": ["build", "test"],
            "auth_expectations": ["synthetic authentication"],
            "required_clis": [],
            "verification_refs": ["checks/build", "checks/test"],
            "evidence_status": "pass",
            "evidence_refs": ["checks/build", "checks/test"],
        },
        {
            "role": "beta",
            "task_classes": ["review"],
            "auth_expectations": ["synthetic approval"],
            "required_clis": [],
            "verification_refs": ["checks/review"],
            "evidence_status": "unverified",
            "evidence_refs": [],
        },
    ]
}


def _environment():
    """Use test_build_commands.py's safe disposable-Git setup pattern."""
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def _command(repo, argv, *, code=0, stdout=""):
    """Capture streams without retaining raw child output in assertion diagnostics."""
    result = subprocess.run(
        argv, cwd=repo, env=_environment(), capture_output=True, text=True, check=False,
    )
    status_matches = result.returncode == code
    diagnostics_match = result.stdout == stdout and result.stderr == ""
    assert status_matches, "unexpected command exit status"
    assert diagnostics_match, "unexpected command diagnostics (contents withheld)"


def _git(repo, *args):
    _command(repo, ["git", "-C", str(repo), *args])


def _write_json(repo, path, value):
    (repo / path).write_text(json.dumps(value), encoding="utf-8")


class _Table(HTMLParser):
    """Read actual table rows and cells independently of the producer columns."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.headers = []
        self.rows = []
        self.row = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"}:
            self.current = ""

    def handle_data(self, data):
        if self.current is not None:
            self.current += data

    def handle_endtag(self, tag):
        if tag == "td":
            self.row.append(self.current)
            self.current = None
        elif tag == "th":
            self.headers.append(self.current)
            self.current = None
        elif tag == "tr" and self.row:
            self.rows.append(self.row)


def _assert_projection(repo):
    assert json.loads((repo / OUTPUTS["json"]).read_text(encoding="utf-8")) == EXPECTED
    table = _Table()
    table.feed((repo / OUTPUTS["html"]).read_text(encoding="utf-8"))
    assert table.headers == [
        "Role", "Required task classes", "Authentication expectations", "Required CLIs",
        "Required verification references", "Evidence status", "Evidence references",
    ]
    # Literal mapping insertion order defines the independent HTML column order.
    assert table.rows == [
        [", ".join(value) if isinstance(value, list) else value for value in row.values()]
        for row in EXPECTED["rows"]
    ]


def _snapshot(repo):
    """Include every source, input, reference and Git metadata file, including index."""
    return {
        path.relative_to(repo).as_posix(): path.read_bytes()
        for path in repo.rglob("*") if path.is_file()
    }


def _verify_preserving(repo, *, code=0, stdout="OK\n"):
    before = _snapshot(repo)
    _command(
        repo, [sys.executable, "-I", str(CHECKER), "--repo", ".", "--run"],
        code=code, stdout=stdout,
    )
    unchanged = _snapshot(repo) == before
    assert unchanged, "verifier changed source files or Git metadata"


@pytest.fixture
def matrix_repo(tmp_path):
    repo = tmp_path / "repository"
    repo.mkdir()
    _git(repo, "init", "-q")
    script = repo / PRODUCER
    script.parent.mkdir(parents=True)
    script.write_bytes((ROOT / PRODUCER).read_bytes())
    _write_json(repo, REGISTRY, {
        "beta": {
            "task_classes": ["review"],
            "auth_expectations": ["synthetic approval"],
            "required_clis": [],
            "verification_refs": ["checks/review"],
        },
        "alpha": {
            "task_classes": ["test", "build"],
            "auth_expectations": ["synthetic authentication"],
            "required_clis": [],
            "verification_refs": ["checks/test", "checks/build"],
        },
    })
    _write_json(repo, EVIDENCE, {
        "alpha": {"status": "pass", "verification_refs": ["checks/test", "checks/build"]}
    })
    # Deliberate child output includes an absolute runtime path; none may escape
    # the verifier's discarded streams, even when the command succeeds.
    (repo / "no_output.py").write_text(
        "import sys\nfrom pathlib import Path\n"
        "print('child-output-marker', Path.cwd())\n"
        "print('child-error-marker', Path.cwd(), file=sys.stderr)\n",
        encoding="utf-8",
    )
    (repo / "docs/reports").mkdir(parents=True)
    entries = []
    for format_name, output in OUTPUTS.items():
        argv = [
            "python3", PRODUCER, "--registry", REGISTRY, "--evidence", EVIDENCE,
            "--output", output, "--format", format_name,
        ]
        # Invoke the exact copied producer through its real CLI, using the active
        # interpreter just as the verifier resolves its declared Python alias.
        _command(repo, [sys.executable, *argv[1:]])
        entries.append({
            "path": output,
            "kind": "report",
            "build": {"cwd": ".", "argv": argv},
            "inputs": [PRODUCER, REGISTRY, EVIDENCE],
        })
    # Both formats must match every projected field before any verifier call.
    _assert_projection(repo)
    _write_json(repo, ARTIFACTS, entries)
    _git(repo, "add", "--all")
    return repo


def test_matrix_artifacts_match_independent_projection(matrix_repo):
    _assert_projection(matrix_repo)


def test_declared_matrix_outputs_rebuild_without_source_changes(matrix_repo):
    # Two consecutive runs are a locally chosen repeatability check.
    for _ in range(2):
        _verify_preserving(matrix_repo)


def test_changed_evidence_rejects_stale_matrix_references(matrix_repo):
    _verify_preserving(matrix_repo)
    original = (matrix_repo / EVIDENCE).read_bytes()
    evidence = json.loads(original)
    evidence["alpha"]["status"] = "fail"
    _write_json(matrix_repo, EVIDENCE, evidence)
    # Both declarations consume the changed observation; both references are stale.
    # Literal membership follows those declared inputs, never verifier results.
    _verify_preserving(
        matrix_repo, code=1,
        stdout='NOT_REPRODUCED: "docs/reports/matrix.html"\n'
               'NOT_REPRODUCED: "docs/reports/matrix.json"\n',
    )
    # Restoring only the observation makes the unchanged commands/references pass.
    (matrix_repo / EVIDENCE).write_bytes(original)
    _verify_preserving(matrix_repo)


@pytest.mark.parametrize("missing_format", ["json", "html"])
def test_one_missing_output_cannot_hide_behind_other_success(matrix_repo, missing_format):
    _verify_preserving(matrix_repo)
    entries = json.loads((matrix_repo / ARTIFACTS).read_text(encoding="utf-8"))
    for entry in entries:
        if entry["path"] == OUTPUTS[missing_format]:
            entry["build"]["argv"] = ["python3", "no_output.py"]
            entry["inputs"] = ["no_output.py"]
    _write_json(matrix_repo, ARTIFACTS, entries)
    # The other real producer command still succeeds; only the replaced command's
    # artifact fails. Exact output also excludes OK and raw child diagnostics.
    _verify_preserving(
        matrix_repo, code=1,
        stdout=f'NOT_REPRODUCED: "{OUTPUTS[missing_format]}"\n',
    )
