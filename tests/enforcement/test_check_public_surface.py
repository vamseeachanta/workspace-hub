import json
import subprocess
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "check-public-surface.py"


def run_checker(tmp_path: Path, diff: str, *args: str) -> subprocess.CompletedProcess[str]:
    diff_path = tmp_path / "change.diff"
    diff_path.write_text(textwrap.dedent(diff).lstrip(), encoding="utf-8")
    allowlist_path = tmp_path / "empty-allowlist.yml"
    allowlist_path.write_text(
        "host_ips: []\nhostnames: []\nsecrets: []\nidentifiers: []\n",
        encoding="utf-8",
    )
    return subprocess.run(
        [
            "python",
            str(SCRIPT),
            "--diff-file",
            str(diff_path),
            "--allowlist",
            str(allowlist_path),
            *args,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_blocks_tailnet_and_private_ips_but_allows_documentation_ranges(tmp_path: Path) -> None:
    result = run_checker(
        tmp_path,
        """
        diff --git a/sample.txt b/sample.txt
        --- a/sample.txt
        +++ b/sample.txt
        @@ -0,0 +1,3 @@
        +connect to 100.64.1.2 and 10.20.30.40
        +documentation example 192.0.2.44 and 203.0.113.9
        +public service 8.8.8.8
        """,
    )
    assert result.returncode == 1
    assert "sample.txt:1: host-ip" in result.stdout
    assert "100.***.***.2" in result.stdout
    assert "10.***.***.40" in result.stdout
    assert "192.0.2.44" not in result.stdout
    assert "203.0.113.9" not in result.stdout


def test_allowlist_suppresses_exact_value(tmp_path: Path) -> None:
    allowlist = tmp_path / "allowlist.yml"
    allowlist.write_text("host_ips:\n  - 10.20.30.40\n", encoding="utf-8")
    result = run_checker(
        tmp_path,
        """
        diff --git a/sample.txt b/sample.txt
        --- a/sample.txt
        +++ b/sample.txt
        @@ -0,0 +1 @@
        +allowed endpoint 10.20.30.40
        """,
        "--allowlist",
        str(allowlist),
    )
    assert result.returncode == 0
    assert result.stdout == ""


def test_blocks_denylisted_physical_hostname_but_allows_role_slug(tmp_path: Path) -> None:
    denylist = tmp_path / "hosts.txt"
    denylist.write_text("DESKTOP-[A-Z0-9]{7}\n", encoding="utf-8")
    result = run_checker(
        tmp_path,
        """
        diff --git a/hosts.md b/hosts.md
        --- a/hosts.md
        +++ b/hosts.md
        @@ -0,0 +1,2 @@
        +runner DESKTOP-ABC1234
        +runner ace-linux-1
        """,
        "--host-denylist",
        str(denylist),
    )
    assert result.returncode == 1
    assert "hosts.md:1: physical-hostname" in result.stdout
    assert "DE****1234" in result.stdout
    assert "ace-linux-1" not in result.stdout


def test_blocks_secret_shapes_and_masks_values(tmp_path: Path) -> None:
    github_token = "ghp_" + "abcdefghijklmnopqrstuvwxyz0123456789"
    aws_key = "AKIA" + "IOSFODNN7EXAMPLE"
    private_key_header = "-----BEGIN " + "OPENSSH PRIVATE KEY-----"
    result = run_checker(
        tmp_path,
        f"""
        diff --git a/secrets.txt b/secrets.txt
        --- a/secrets.txt
        +++ b/secrets.txt
        @@ -0,0 +1,3 @@
        +github token {github_token}
        +aws key {aws_key}
        +{private_key_header}
        """,
    )
    assert result.returncode == 1
    assert "secrets.txt:1: github-token" in result.stdout
    assert github_token not in result.stdout
    assert "ghp_****6789" in result.stdout
    assert aws_key not in result.stdout
    assert "AKIA****MPLE" in result.stdout
    assert "private-key" in result.stdout


def test_scans_only_added_lines(tmp_path: Path) -> None:
    github_token = "ghp_" + "abcdefghijklmnopqrstuvwxyz0123456789"
    result = run_checker(
        tmp_path,
        f"""
        diff --git a/sample.txt b/sample.txt
        --- a/sample.txt
        +++ b/sample.txt
        @@ -1,2 +1,2 @@
        -old secret {github_token}
         context 10.20.30.40
        +new clean line
        """,
    )
    assert result.returncode == 0
    assert result.stdout == ""


def test_identifier_mode_writes_masked_markdown_and_exits_zero(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yml"
    registry.write_text(
        """
        wikis:
          - short: client-alpha
            codename: client-a
            identifiers:
              - Alpha Offshore LLC
              - AO-7788
        """,
        encoding="utf-8",
    )
    output = tmp_path / "comment.md"
    result = run_checker(
        tmp_path,
        """
        diff --git a/report.md b/report.md
        --- a/report.md
        +++ b/report.md
        @@ -0,0 +1,2 @@
        +Prepared for Alpha Offshore LLC.
        +Reference AO-7788.
        """,
        "--mode",
        "identifiers",
        "--client-registry",
        str(registry),
        "--markdown-output",
        str(output),
    )
    assert result.returncode == 0
    body = output.read_text(encoding="utf-8")
    assert "report.md:1" in body
    assert "report.md:2" in body
    assert "client-a" in body
    assert "Alpha Offshore LLC" not in body
    assert "AO-7788" not in body
    assert "Al**** LLC" in body
    assert "AO***88" in body


def test_json_output_masks_values(tmp_path: Path) -> None:
    slack_token = "xoxb-" + "123456789012-123456789012-" + "abcdefghijklmnopqrstuvwx"
    result = run_checker(
        tmp_path,
        f"""
        diff --git a/secrets.txt b/secrets.txt
        --- a/secrets.txt
        +++ b/secrets.txt
        @@ -0,0 +1 @@
        +slack {slack_token}
        """,
        "--format",
        "json",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["findings"][0]["kind"] == "slack-token"
    assert slack_token[:18] not in payload["findings"][0]["masked"]


def test_anthropic_key_does_not_double_report_as_openai(tmp_path: Path) -> None:
    anthropic_key = "sk-ant-" + "abcdefghijklmnopqrstuvwxyz0123456789"
    result = run_checker(
        tmp_path,
        f"""
        diff --git a/secrets.txt b/secrets.txt
        --- a/secrets.txt
        +++ b/secrets.txt
        @@ -0,0 +1 @@
        +anthropic {anthropic_key}
        """,
        "--format",
        "json",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert [finding["kind"] for finding in payload["findings"]] == ["anthropic-key"]


def test_git_diff_runs_against_current_working_directory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    (repo / "README.md").write_text("clean\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=repo, check=True)
    subprocess.run(["git", "branch", "main"], cwd=repo, check=True)
    subprocess.run(["git", "checkout", "-qb", "feature"], cwd=repo, check=True)
    (repo / "README.md").write_text("clean\nnew 100.64.9.9\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "add leak"], cwd=repo, check=True)

    allowlist = tmp_path / "empty-allowlist.yml"
    allowlist.write_text(
        "host_ips: []\nhostnames: []\nsecrets: []\nidentifiers: []\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "python",
            str(SCRIPT),
            "--base-ref",
            "main",
            "--head-ref",
            "HEAD",
            "--allowlist",
            str(allowlist),
        ],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "README.md:2: host-ip" in result.stdout
