"""Build disposable signal repositories once per pytest invocation."""
from dataclasses import dataclass
from pathlib import Path
import subprocess

import pytest


FIXTURE_BUILDER = Path(__file__).parent / "fixtures" / "repos" / "build_fixtures.sh"


@dataclass(frozen=True)
class SignalRepos:
    release: Path
    case_study: Path
    readme: Path
    baseline_sha: str


def build_fixture_repos(output: Path, *, builder: Path = FIXTURE_BUILDER) -> SignalRepos:
    """Build or validate existing fixtures, surfacing the builder's diagnostics."""
    try:
        subprocess.run(
            ["bash", str(builder), "--output-dir", str(output)],
            check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as exc:
        diagnostic = (exc.stderr or exc.stdout).strip()
        raise RuntimeError(
            f"Fixture builder failed (exit {exc.returncode}): {diagnostic}"
        ) from exc
    except OSError as exc:
        raise RuntimeError(f"Fixture builder could not start: {exc}") from exc
    return SignalRepos(
        release=output / "repo-with-release",
        case_study=output / "repo-with-casestudy",
        readme=output / "repo-with-readme",
        baseline_sha=(output / "repo-with-casestudy.baseline-sha").read_text().strip(),
    )


@pytest.fixture(scope="session")
def signal_repos(tmp_path_factory):
    return build_fixture_repos(tmp_path_factory.mktemp("signal-repos"))


@pytest.fixture(scope="session")
def release_repo(signal_repos):
    return signal_repos.release


@pytest.fixture(scope="session")
def case_study_repo(signal_repos):
    return signal_repos.case_study


@pytest.fixture(scope="session")
def case_study_baseline(signal_repos):
    return signal_repos.baseline_sha


@pytest.fixture(scope="session")
def readme_repo(signal_repos):
    return signal_repos.readme
