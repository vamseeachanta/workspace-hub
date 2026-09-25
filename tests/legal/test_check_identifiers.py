"""Owner decision C15: a C11-style client-identifier gate for this PUBLIC repo.

workspace-hub had two legal checks and neither covered the current tree:

* ``scripts/legal/check-client-pii.py`` scans only the files a PR changes, and
  only against a private map that CI receives through a secret. Content already
  on ``main`` is never re-read.
* ``scripts/legal/legal-sanity-scan.sh`` matches the plain-text names in
  ``.legal-deny-list.yaml``. A deny list of client names, committed to a public
  repository, is itself a list of clients.

``scripts/legal/check_identifiers.py`` is the digitalmodel #2167 checker
adapted to this repository. It reads ``.legal-identifier-gate.yaml`` -- public
pattern classes and salted name hashes -- plus an optional private list, and
scans the whole tracked tree in CI. Files it cannot read pass only when a
committed baseline lists their path with the same sha256.

**These tests hold no real identifier.** A fixture containing one would be
caught by the gate it tests. Names are exercised through invented tokens hashed
at test time, and every structural input is assembled from fragments at run
time so that this file carries nothing the gate rejects and needs no exclusion.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
CHECKER = REPO / "scripts" / "legal" / "check_identifiers.py"
RULES_NAME = ".legal-identifier-gate.yaml"
RULES = REPO / RULES_NAME
BASELINE = REPO / ".legal-uninspectable-baseline.txt"
WORKFLOW = REPO / ".github" / "workflows" / "legal-identifier-gate.yml"
ENV = "WORKSPACE_HUB_DENY_LIST"
TOKEN = "zzsynthetictestclient"
BS = "\\"

_GIT_BINDINGS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE")


def _installed() -> None:
    if not CHECKER.exists() or not RULES.exists():
        pytest.fail("identifier gate not installed: " f"{CHECKER.name} or {RULES_NAME} missing")


@pytest.fixture()
def gate(tmp_path):
    """An isolated repository root: the checker, a rules file that also denies
    TOKEN by hash, and a home directory with no private list."""
    _installed()
    root = tmp_path / "repo"
    (root / "scripts" / "legal").mkdir(parents=True)
    shutil.copy(CHECKER, root / "scripts" / "legal" / "check_identifiers.py")
    rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    salt = str(rules.get("salt", ""))
    rules["hashed_names"] = list(rules.get("hashed_names") or []) + [
        hashlib.sha256(f"{salt}:{TOKEN}".encode()).hexdigest()
    ]
    (root / RULES_NAME).write_text(yaml.safe_dump(rules), encoding="utf-8")
    home = tmp_path / "home"
    home.mkdir()

    def run(*args, env=None, cwd=None):
        e = {k: v for k, v in os.environ.items() if k not in _GIT_BINDINGS}
        e.pop(ENV, None)
        e.pop("CI", None)
        e.pop("GITHUB_ACTIONS", None)
        e["HOME"] = str(home)
        e["USERPROFILE"] = str(home)
        if env:
            e.update(env)
        return subprocess.run(
            [sys.executable, str(root / "scripts" / "legal" / "check_identifiers.py"), *args],
            cwd=cwd or root,
            capture_output=True,
            text=True,
            env=e,
            encoding="utf-8",
            errors="replace",
        )

    run.root = root
    run.home = home
    return run


def _file(gate, text, name: str = "sample.md") -> str:
    p = gate.root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        p.write_bytes(text)
    else:
        p.write_text(text, encoding="utf-8")
    return str(p)


def _user_path(sep: str = BS) -> str:
    return sep.join(["C:", "Users", "jdoe" + "123", "Documents", "model.yml"])


# --------------------------------------------------------------------------- #
# Every C11 category fails
# --------------------------------------------------------------------------- #
class TestEachCategoryIsDetected:
    """One positive case per category, named by the rule that must fire."""

    @pytest.mark.parametrize(
        "line,rule",
        [
            # operator / client, field / project and vessel names: hashed list
            (f"Prepared for {TOKEN} under the charter.", "denied-name"),
            # field / project: a job code, a CTR number, a document number
            ("see B" + "1234 for the scope", "job-code"),
            ("delivered under CTR" + " 07 of the contract", "ctr-number"),
            ("workbook 3" + "1234-CAL-" + "0001-1 checked", "project-document-number"),
            ("report 12" + "34-rpt-" + "5678-02 issued", "project-document-number"),
            # person / Windows user
            ("contact person" + "@somecompany.example", "foreign-domain-email"),
            (f"fe_folder: {_user_path()}", "windows-user-path"),
            (f"fe_folder: {_user_path('/')}", "windows-user-path"),
            (f"path: {_user_path(BS * 2)}", "windows-user-path"),
            ("# " + "User: " + "jdoe" + "123", "solver-export-user"),
            ("OneDrive" + " - " + "Example Operator Corporation" + BS + "Temp", "onedrive-org"),
            # private path
            ("K:" + BS + "projects" + BS + "run" + BS + "a.dat", "mapped-drive-path"),
            (BS * 2 + "fileserver" + BS + "share" + BS + "a.dat", "unc-share"),
            (BS * 4 + "fileserver" + BS * 2 + "share" + BS * 2 + "a.dat", "unc-share"),
            (BS * 2 + "h" + BS + "share" + BS + "a.dat", "unc-share"),
            # machine hostname
            ("# " + "Machine: " + "WORKSTATION" + "7", "solver-export-machine"),
            ("closeout on " + "abcd-hou-" + "rds" + "07" + " failed", "windows-hostname"),
            ("run it on " + "ABCD-" + "ANSYS" + "09", "windows-hostname"),
        ],
    )
    def test_the_rule_fires(self, gate, line, rule):
        out = gate(_file(gate, line + "\n"))
        assert out.returncode == 1, out.stdout
        assert f"[{rule}]" in out.stdout, out.stdout


class TestPlaceholdersPass:
    """The replacements the cleanup writes must not themselves be findings."""

    @pytest.mark.parametrize(
        "line",
        [
            "# " + "User: (removed)",
            "# " + "Machine: (removed)",
            "fe_folder: <private-data>" + BS + "Temp" + BS + "model.yml",
            "C:" + BS + "Users" + BS + "Public" + BS + "Documents",
            "C:" + BS + "Users" + BS + "<user>" + BS + "AppData",
            "the licensed host ace-win-1 ran the case",
            # C15: the fleet runbooks head sections with the logical label
            "# " + "Machine: ace-linux-1",
            "# " + "Machine: licensed-win-2",
            "# " + "Machine: home-win",
            "# " + "Machine: macbook-portable",
            "job <job-code> and document <document-number>",
            "mail " + "user" + "@example.com about it",
            "The mooring line has twelve anchors on a 2000 m spread.",
            r'exe = r"C:\Program Files\ANSYS Inc\v261\aqwa\bin\winx64\Aqwa.exe"',
            "A JONSWAP spectrum with a peak enhancement factor of 3.3.",
        ],
    )
    def test_no_finding(self, gate, line):
        out = gate(_file(gate, line + "\n"))
        assert out.returncode == 0, out.stdout


class TestWorkspaceHubEmailShapes:
    """C15: two address shapes in this repository name no person.

    ``git@<host>:owner/repo`` is an SSH remote, not a mailbox, and a
    ``noreply``/``no-reply`` sender is a service address (the co-author trailer
    on agent commits). A person at the same domains still fails.
    """

    @pytest.mark.parametrize(
        "line",
        [
            "git clone " + "git" + "@" + "github.com:owner/repo.git",
            "url = " + "git" + "@" + "gitlab.example.org:group/project.git",
            "Co-Authored-By: Claude <" + "noreply" + "@" + "anthropic.com>",
            "From: " + "no-reply" + "@" + "accounts.example.org",
            # a decorator line in a unified diff is not an address
            "+" + "@" + "pytest.fixture",
            # a package@tag file name ends in a file extension, not a domain
            "git rm memory/some-tool" + "@" + "alpha-data.json",
            "cache at pkg" + "@" + "1.2.3/index.yaml",
        ],
    )
    def test_service_shapes_pass(self, gate, line):
        out = gate(_file(gate, line + "\n"))
        assert out.returncode == 0, out.stdout

    @pytest.mark.parametrize(
        "line",
        [
            "ask " + "jdoe" + "@" + "github.com today",
            "cc " + "jdoe" + "@" + "anthropic.com",
            "git" + "@" + "github.com is a mailbox here",
            "reply to " + "noreplyfan" + "@" + "somecompany.com",
        ],
    )
    def test_a_person_at_the_same_domain_still_fails(self, gate, line):
        out = gate(_file(gate, line + "\n"))
        assert out.returncode == 1, out.stdout
        assert "[foreign-domain-email]" in out.stdout


class TestDocumentNumbersAreNotDates:
    @pytest.mark.parametrize(
        "line",
        [
            "issued 2026-09-25 at the review",
            "ISO 13628" + "-7 clause 6",
            "API RP 2" + "RD-2013 section 5",
            "commit 1234" + "abcd-cal-bration",
        ],
    )
    def test_no_finding(self, gate, line):
        out = gate(_file(gate, line + "\n"))
        assert "[project-document-number]" not in out.stdout, out.stdout


# --------------------------------------------------------------------------- #
# Names: salted hashes and the private list
# --------------------------------------------------------------------------- #
class TestDeniedNames:
    def test_a_hashed_name_is_detected(self, gate):
        out = gate(_file(gate, f"The {TOKEN} scope.\n"))
        assert out.returncode == 1, out.stdout
        assert "denied-name" in out.stdout

    @pytest.mark.parametrize(
        "text",
        [f"{TOKEN}-archive", f"old-{TOKEN}", f"{TOKEN}2", f"x_{TOKEN}_y", TOKEN.upper()],
    )
    def test_a_name_joined_to_other_text_is_still_detected(self, gate, text):
        out = gate(_file(gate, f"see {text} here\n"))
        assert out.returncode == 1, out.stdout

    def test_a_denied_name_in_a_file_name_is_caught(self, gate):
        out = gate(_file(gate, b"", name=f"notes_{TOKEN}.md"))
        assert out.returncode == 1, out.stdout
        assert "denied-name" in out.stdout

    def test_the_private_list_extends_the_public_one(self, gate):
        private = gate.home / "private.txt"
        private.write_text("zzprivatevessel\n", encoding="utf-8")
        sample = _file(gate, "moored alongside zzprivatevessel\n")
        assert gate(sample).returncode == 0
        out = gate(sample, env={ENV: str(private)})
        assert out.returncode == 1, out.stdout
        assert "denied-name" in out.stdout

    def test_the_default_private_location_is_read_when_present(self, gate):
        cfg = gate.home / ".config" / "workspace-hub"
        cfg.mkdir(parents=True)
        (cfg / "identifier-deny-list.txt").write_text("zzdefaultlisted\n", encoding="utf-8")
        out = gate(_file(gate, "the zzdefaultlisted field\n"))
        assert out.returncode == 1, out.stdout

    def test_a_private_regex_is_applied_and_never_echoed(self, gate):
        private = gate.home / "private.txt"
        private.write_text("re:zzcode-[0-9]{3}\n", encoding="utf-8")
        out = gate(_file(gate, "job zzcode-481 closed\n"), env={ENV: str(private)})
        assert out.returncode == 1, out.stdout
        assert "private-pattern" in out.stdout
        assert "zzcode-[0-9]" not in out.stdout

    def test_an_invalid_private_regex_is_an_error(self, gate):
        private = gate.home / "private.txt"
        private.write_text("re:(unclosed\n", encoding="utf-8")
        out = gate(_file(gate, "clean\n"), env={ENV: str(private)})
        assert out.returncode not in (0, 1), out.stdout

    def test_a_named_private_list_that_is_absent_is_an_error(self, gate):
        out = gate(_file(gate, "clean\n"), env={ENV: str(gate.home / "absent.txt")})
        assert out.returncode != 0
        assert "Refusing to continue" in (out.stdout + out.stderr)

    def test_a_digit_leading_name_is_caught(self, gate):
        private = gate.home / "private.txt"
        private.write_text("7zzhull\n", encoding="utf-8")
        out = gate(_file(gate, "towed by 7zzhull at dawn\n"), env={ENV: str(private)})
        assert out.returncode == 1, out.stdout

    def test_a_plain_number_is_not_a_name(self, gate):
        out = gate(_file(gate, "the 2000 m spread and 12345 cycles\n"))
        assert out.returncode == 0, out.stdout


class TestExampleSentinel:
    SENTINEL = "identifier-gate: " + "example"

    def test_a_marked_example_line_passes_structural_rules(self, gate):
        line = "K:" + BS + "projects" + BS + "run" + BS + "a.dat"
        out = gate(_file(gate, f"{line}  # {self.SENTINEL}\n"))
        assert out.returncode == 0, out.stdout

    def test_a_marked_line_is_still_checked_for_names(self, gate):
        out = gate(_file(gate, f"{TOKEN}  # {self.SENTINEL}\n"))
        assert out.returncode == 1, out.stdout

    def test_the_marker_covers_only_its_own_line(self, gate):
        line = "K:" + BS + "projects" + BS + "run" + BS + "a.dat"
        out = gate(_file(gate, f"# {self.SENTINEL}\n{line}\n"))
        assert out.returncode == 1, out.stdout


# --------------------------------------------------------------------------- #
# Fail closed
# --------------------------------------------------------------------------- #
PDF = b"%PDF-1.7\n\x00\x01\x02 binary \x00\xff"


class TestTheGateFailsClosed:
    def test_a_clean_file_reports_what_it_scanned(self, gate):
        out = gate(_file(gate, "a clean line\n"))
        assert out.returncode == 0
        assert "scanned 1 file" in out.stdout

    def test_utf16_text_is_read(self, gate):
        out = gate(_file(gate, f"The {TOKEN} scope.\n".encode("utf-16"), name="a.txt"))
        assert out.returncode == 1, out.stdout

    def test_an_office_document_is_read(self, gate):
        import io
        import zipfile

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("[Content_Types].xml", "<Types/>")
            z.writestr(
                "word/document.xml",
                f"<w:document xmlns:w='w'><w:t>Prepared for {TOKEN}</w:t></w:document>",
            )
        out = gate(_file(gate, buf.getvalue(), name="report.docx"))
        assert out.returncode == 1, out.stdout

    def test_an_uninspectable_binary_fails(self, gate):
        out = gate(_file(gate, PDF, name="a.pdf"))
        assert out.returncode == 2, out.stdout

    def test_declared_binary_media_is_reported_not_failed(self, gate):
        png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 32
        out = gate(_file(gate, png, name="img.png"))
        assert out.returncode == 0, out.stdout
        assert "binary media" in out.stdout

    def test_text_renamed_to_a_media_extension_is_read(self, gate):
        out = gate(_file(gate, f"The {TOKEN} scope.\n", name="not-an-image.png"))
        assert out.returncode != 0, out.stdout

    def test_a_named_file_that_does_not_exist_is_an_error(self, gate):
        out = gate(str(gate.root / "missing.md"))
        assert out.returncode != 0, out.stdout

    def test_a_failed_git_enumeration_is_an_error(self, gate, tmp_path):
        bare = tmp_path / "not-a-repo"
        bare.mkdir()
        out = gate("--all", cwd=bare)
        assert out.returncode != 0, out.stdout
        assert "nothing to scan" not in out.stdout

    def test_staged_mode_reads_the_index_not_the_working_tree(self, gate):
        root = gate.root
        env = {k: v for k, v in os.environ.items() if k not in _GIT_BINDINGS}
        for cmd in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "t@example.test"],
            ["git", "config", "user.name", "t"],
        ):
            subprocess.run(cmd, cwd=root, check=True, env=env)
        p = root / "note.md"
        p.write_text(f"The {TOKEN} scope.\n", encoding="utf-8")
        subprocess.run(["git", "add", "note.md"], cwd=root, check=True, env=env)
        p.write_text("clean now\n", encoding="utf-8")
        out = gate()
        assert out.returncode == 1, out.stdout


class TestUninspectableBaseline:
    def _baseline(self, gate):
        return gate.root / "baseline.txt"

    def _accept(self, gate, *paths):
        out = gate(*map(str, paths), "--baseline", str(self._baseline(gate)), "--update-baseline")
        assert out.returncode == 0, out.stdout + out.stderr

    def test_a_listed_unchanged_file_passes(self, gate):
        path = Path(_file(gate, PDF, name="a.pdf"))
        self._accept(gate, path)
        assert hashlib.sha256(PDF).hexdigest() in self._baseline(gate).read_text(encoding="utf-8")
        out = gate(str(path), "--baseline", str(self._baseline(gate)))
        assert out.returncode == 0, out.stdout

    def test_a_changed_listed_file_fails(self, gate):
        path = Path(_file(gate, PDF, name="a.pdf"))
        self._accept(gate, path)
        path.write_bytes(PDF + b"confidential")
        out = gate(str(path), "--baseline", str(self._baseline(gate)))
        assert out.returncode == 2, out.stdout
        assert "changed" in out.stdout

    def test_an_unlisted_file_fails(self, gate):
        a = Path(_file(gate, PDF, name="a.pdf"))
        self._accept(gate, a)
        a.unlink()
        b = _file(gate, PDF, name="b.pdf")
        out = gate(b, "--baseline", str(self._baseline(gate)))
        assert out.returncode == 2, out.stdout
        assert "not in the baseline" in out.stdout

    @pytest.mark.parametrize("var", ["CI", "GITHUB_ACTIONS"])
    def test_update_baseline_refuses_to_run_in_ci(self, gate, var):
        path = _file(gate, PDF, name="a.pdf")
        out = gate(path, "--baseline", str(self._baseline(gate)), "--update-baseline", env={var: "true"})
        assert out.returncode == 3, out.stdout + out.stderr
        assert not self._baseline(gate).exists()


# --------------------------------------------------------------------------- #
# Repository wiring
# --------------------------------------------------------------------------- #
class TestWiring:
    def test_the_gate_rules_are_not_in_the_legacy_deny_list(self):
        """legal-sanity-scan.sh greps every ``- pattern:`` line of
        .legal-deny-list.yaml as a literal. Structural regexes placed there
        would be searched as text; the gate keeps its own rules file."""
        _installed()
        legacy = yaml.safe_load((REPO / ".legal-deny-list.yaml").read_text(encoding="utf-8"))
        assert "structural" not in legacy
        assert "hashed_names" not in legacy

    def test_the_rules_file_has_a_workspace_hub_salt(self):
        _installed()
        rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
        assert str(rules.get("salt", "")).startswith("workspace-hub-")
        assert rules.get("hashed_names"), "no hashed names"
        for h in rules["hashed_names"]:
            assert re.fullmatch(r"[0-9a-f]{64}", str(h)), h

    def test_ci_scans_the_whole_tree_on_push_and_pull_request(self):
        wf = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        on = wf.get("on", wf.get(True))
        assert "push" in on and "pull_request" in on
        text = WORKFLOW.read_text(encoding="utf-8")
        assert "scripts/legal/check_identifiers.py --all" in text
        assert "--baseline .legal-uninspectable-baseline.txt" in text
        steps = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
        assert "--update-baseline" not in steps

    def test_the_pre_commit_hook_runs_in_staged_mode(self):
        cfg = yaml.safe_load((REPO / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
        hooks = [h for r in cfg["repos"] for h in r.get("hooks", []) if h.get("id") == "client-identifier-gate"]
        assert len(hooks) == 1
        assert hooks[0].get("pass_filenames") is False

    def test_the_committed_baseline_has_digests_for_every_entry(self):
        assert BASELINE.exists()
        for ln in BASELINE.read_text(encoding="utf-8").splitlines():
            if ln and not ln.startswith("#"):
                digest, sep, path = ln.partition("  ")
                assert sep and len(digest) == 64 and path, ln

    def test_every_exclusion_carries_a_reason_and_exists(self):
        _installed()
        rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
        tracked = set(
            subprocess.run(
                ["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True
            ).stdout.decode("utf-8", "surrogateescape").split("\0")
        )
        for e in rules.get("exclusions") or []:
            assert str(e.get("reason", "")).strip(), e
            assert e["path"] in tracked, f"exclusion for an untracked path: {e['path']}"


class TestExemptFilesCarryNoValues:
    """The gate skips its own rules file and checker; values must not hide there."""

    @pytest.mark.parametrize("rel", [RULES_NAME, "scripts/legal/check_identifiers.py"])
    def test_no_denied_name_or_job_code_outside_pattern_lines(self, rel):
        _installed()
        rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
        salt = str(rules.get("salt", ""))
        hashed = set(rules.get("hashed_names") or [])
        job = next(r for r in rules["structural"] if r["id"] == "job-code")
        job_rx = re.compile(job["pattern"])
        word = re.compile(r"[A-Za-z][A-Za-z0-9-]{3,}")
        for n, line in enumerate((REPO / rel).read_text(encoding="utf-8").splitlines(), start=1):
            line = re.sub(r"^(\s*pattern:\s*)'(?:[^']|'')*'", r"\1", line)
            for m in job_rx.finditer(line):
                if not re.fullmatch("(?i)b1" + "234", m.group(0)):
                    pytest.fail(f"{rel}:{n}: job code in an exempt file")
            for w in word.findall(line):
                for c in {w.lower(), *re.split(r"[-\d]+", w.lower())}:
                    if len(c) >= 4 and hashlib.sha256(f"{salt}:{c}".encode()).hexdigest() in hashed:
                        pytest.fail(f"{rel}:{n}: denied name in an exempt file")


class TestPrivateListIsCoveredWithoutIt:
    """CI has no private list, so every literal name on it must be caught by a
    public class or a salted hash. Skips on a machine without the list; a
    failure names entry positions only, because CI logs are public."""

    def test_every_literal_entry_is_caught_with_the_private_list_absent(self, gate):
        named = os.environ.get(ENV)
        private = (
            Path(named) if named else Path.home() / ".config" / "workspace-hub" / "identifier-deny-list.txt"
        )
        if not private.exists():
            pytest.skip("no private deny list on this machine")
        names = [
            ln.strip()
            for ln in private.read_text(encoding="utf-8-sig").splitlines()
            if ln.strip() and not ln.strip().startswith(("#", "re:"))
        ]
        escaped = []
        for i, name in enumerate(names, start=1):
            out = gate(_file(gate, f"moored alongside {name} today\n", name=f"entry{i}.md"))
            if not (out.returncode == 1 and "denied-name" in out.stdout):
                escaped.append(f"entry #{i}")
        assert not escaped, "private-list entries CI would miss: " + ", ".join(escaped)


# --------------------------------------------------------------------------- #
# Findings never echo the offending text into a (public) CI log
# --------------------------------------------------------------------------- #


def test_finding_output_does_not_quote_the_line(gate):
    f = _file(gate, f"model at {_user_path()}\nsecond line mentions {TOKEN}\n")
    r = gate(f)
    assert r.returncode == 1
    out = r.stdout + r.stderr
    assert "sample.md:1:" in out and "sample.md:2:" in out
    assert "jdoe123" not in out and TOKEN not in out


def test_show_lines_quotes_locally(gate):
    f = _file(gate, f"model at {_user_path()}\n")
    r = gate("--show-lines", f)
    assert r.returncode == 1 and "jdoe123" in r.stdout


def test_show_lines_is_refused_in_ci(gate):
    f = _file(gate, f"model at {_user_path()}\n")
    r = gate("--show-lines", f, env={"CI": "true"})
    assert r.returncode not in (0, 1)
    assert "jdoe123" not in r.stdout + r.stderr
