"""Banner contract tests derived from issue #3300, not runtime API results.

Expected outcomes are Boolean hand checks: a complete quoted introduction
contains each required contract token; deleting one token fails that requirement.
The ecosystem is the checklist in #3300, not the broader repository registry.
No engineering constants or numerical acceptance tolerances are used.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.marketing.api_readme_banners import CATALOG_URL, REPOSITORIES, audit

BANNER = """# Example

> **Part of the Deckhand API — the API for real-world work.**
> The workflows here are API paths: `POST /api/run` returns a
> **standards-traceable HTML report URL**, deterministic for the same inputs.
> Catalog: https://aceengineer.com/api-catalog.html
> API reference: deckhand `docs/deckhand/API.md`

## Usage
"""
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/marketing/api_readme_banners.py"


def all_readmes(text=BANNER):
    return dict.fromkeys(REPOSITORIES, text)


def test_checklist_matches_issue_scope():
    assert set(REPOSITORIES) == {
        "digitalmodel", "worldenergydata", "deckhand", "deckhand-sandbox",
        "aceengineer-website",
    }


def test_complete_banners_with_declared_live_catalog_pass():
    result = audit(all_readmes(), catalog_status="live")
    assert result["status"] == "PASS"
    assert all(row["status"] == "PASS" for row in result["repositories"])


@pytest.mark.parametrize("token,missing", [
    ("Deckhand", "deckhand_api"),
    ("API paths", "api_path"),
    ("POST /api/run", "run_endpoint"),
    ("standards-traceable HTML report URL", "report_contract"),
    ("deterministic", "determinism"),
    (CATALOG_URL, "catalog_link"),
    ("docs/deckhand/API.md", "api_reference"),
])
def test_missing_contract_element_fails(token, missing):
    result = audit(all_readmes(BANNER.replace(token, "removed")), catalog_status="live")
    assert result["status"] == "FAIL"
    assert missing in result["repositories"][0]["missing"]


@pytest.mark.parametrize("status", ["historical", "unverified"])
def test_catalog_gate_never_passes_non_live_evidence(status):
    result = audit(all_readmes(), catalog_status=status)
    assert result["status"] == "NOT_EVALUATED"
    assert result["catalog"]["status"] == "NOT_EVALUATED"
    assert all(row["status"] == "PASS" for row in result["repositories"])


def test_absent_repository_is_visible_and_not_evaluated():
    readmes = all_readmes()
    del readmes["deckhand-sandbox"]
    result = audit(readmes, catalog_status="live")
    row = next(row for row in result["repositories"] if row["repository"] == "deckhand-sandbox")
    assert row == {"repository": "deckhand-sandbox", "status": "NOT_EVALUATED",
                   "missing": ["readme"]}
    assert result["status"] == "NOT_EVALUATED"


def test_partial_snapshot_does_not_hide_known_failures():
    result = audit({"deckhand": "# Empty\n"}, catalog_status="live")
    assert result["status"] == "FAIL"
    assert {row["status"] for row in result["repositories"]} == {"FAIL", "NOT_EVALUATED"}


def test_banner_below_first_section_does_not_satisfy_top_requirement():
    result = audit(all_readmes("# Example\n\n## Usage\n" + BANNER), catalog_status="live")
    assert result["status"] == "FAIL"


@pytest.mark.parametrize("fence", ["```", "~~~"])
def test_example_fence_is_not_a_published_banner(fence):
    text = f"# Example\n\n{fence}markdown\n{BANNER}\n{fence}\n"
    assert audit(all_readmes(text), catalog_status="live")["status"] == "FAIL"


def test_unquoted_body_text_is_not_a_banner():
    assert audit(all_readmes(BANNER.replace("> ", "")), catalog_status="live")["status"] == "FAIL"


def test_unrelated_quote_can_precede_banner():
    text = "# Example\n\n> Other introduction.\n\n" + BANNER.replace("# Example\n", "")
    assert audit(all_readmes(text), catalog_status="live")["status"] == "PASS"


def test_tokens_spread_across_separate_quotes_do_not_form_one_banner():
    assert audit(all_readmes(BANNER.replace("\n> ", "\n\n> ")),
                 catalog_status="live")["status"] == "FAIL"


@pytest.mark.parametrize("url", [CATALOG_URL + ".invalid", CATALOG_URL + "/unrelated",
                                 CATALOG_URL.replace("https:", "http:")])
def test_wrong_catalog_destination_fails(url):
    result = audit(all_readmes(BANNER.replace(CATALOG_URL, url)), catalog_status="live")
    assert "catalog_link" in result["repositories"][0]["missing"]


def test_markdown_catalog_link_and_redirect_host_are_supported():
    text = BANNER.replace(CATALOG_URL, "[API catalog](https://www.aceengineer.com/api-catalog.html)")
    assert audit(all_readmes(text), catalog_status="live")["status"] == "PASS"


@pytest.mark.parametrize("kwargs", [{"catalog_status": "invented"},
                                    {"catalog_status": "live", "readmes": {"other": BANNER}}])
def test_unknown_status_or_repository_is_rejected(kwargs):
    readmes = kwargs.pop("readmes", all_readmes())
    with pytest.raises(ValueError):
        audit(readmes, **kwargs)


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], check=False,
                          capture_output=True, text=True)


def test_cli_worked_example_and_read_only_files(tmp_path):
    """Five complete inputs give five PASS rows; historical gate prevents PASS.

    The fixture is one complete banner repeated for each checklist member. The
    hand calculation is logical conjunction of the contract requirements per member,
    then the supplied catalog status. Changing only that status cannot authorize
    rollout. Byte equality before and after establishes read-only operation.
    """
    readme = tmp_path / "README.md"
    readme.write_text(BANNER)
    args = ["--readme", f"{REPOSITORIES[0]}={readme}"]
    for repo in REPOSITORIES[1:]:
        args.extend(["--readme", f"{repo}={readme}"])
    passed = run_cli("--catalog-status", "live", *args)
    assert passed.returncode == 0
    assert json.loads(passed.stdout)["status"] == "PASS"
    blocked = run_cli("--catalog-status", "historical", *args)
    assert blocked.returncode == 1
    assert json.loads(blocked.stdout)["status"] == "NOT_EVALUATED"
    assert readme.read_text() == BANNER


def test_cli_unreadable_file_is_reported_without_local_paths(tmp_path):
    missing = tmp_path / "absent.md"
    result = run_cli("--catalog-status", "live", "--readme", f"deckhand={missing}")
    assert result.returncode == 1
    assert str(tmp_path) not in result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("value", ["other=file.md", "deckhand", "deckhand="])
def test_cli_rejects_bad_repository_arguments(value):
    result = run_cli("--catalog-status", "live", "--readme", value)
    assert result.returncode == 2


def test_cli_rejects_duplicate_repository_arguments():
    result = run_cli("--catalog-status", "live", "--readme", "deckhand=a.md",
                     "--readme", "deckhand=b.md")
    assert result.returncode == 2


def test_cli_requires_catalog_status():
    assert run_cli().returncode == 2


def test_blockquoted_code_example_is_not_a_banner():
    text = "# Example\n\n> ```markdown\n" + "\n".join(
        "> " + line for line in BANNER.replace("# Example\n", "").splitlines()
    ) + "\n> ```\n"
    assert audit(all_readmes(text), catalog_status="live")["status"] == "FAIL"


def test_malformed_catalog_url_is_a_failed_check_not_a_crash():
    text = BANNER.replace(CATALOG_URL, "https://[invalid/api-catalog.html")
    assert audit(all_readmes(text), catalog_status="live")["status"] == "FAIL"


@pytest.mark.parametrize("original,replacement,requirement", [
    ("deterministic", "nondeterministic", "determinism"),
    ("POST /api/run", "POST /api/runner", "run_endpoint"),
    ("POST /api/run", "POST /api/run/other", "run_endpoint"),
    ("docs/deckhand/API.md", "docs/deckhand/API.md.invalid", "api_reference"),
])
def test_similar_but_wrong_contract_tokens_do_not_pass(original, replacement, requirement):
    result = audit(all_readmes(BANNER.replace(original, replacement)), catalog_status="live")
    assert requirement in result["repositories"][0]["missing"]


@pytest.mark.parametrize("wrapper", ["indented", "comment"])
def test_hidden_or_indented_example_is_not_a_banner(wrapper):
    quote = BANNER.split("\n\n", 1)[1].split("\n\n##", 1)[0]
    if wrapper == "indented":
        text = "# Example\n\n" + "\n".join("    " + line for line in quote.splitlines())
    else:
        text = "# Example\n\n<!--\n" + quote + "\n-->\n"
    assert audit(all_readmes(text), catalog_status="live")["status"] == "FAIL"
