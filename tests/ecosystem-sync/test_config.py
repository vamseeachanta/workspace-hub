from pathlib import Path
from scripts.ecosystem_sync.config import load_config


FIXTURE = Path(__file__).parent / "fixtures" / "configs" / "minimal.yaml"


def test_load_config_parses_required_fields():
    cfg = load_config(FIXTURE)
    assert cfg.issue_repo == "vamseeachanta/aceengineer-website"
    assert cfg.max_issues_per_run == 20
    assert len(cfg.repos) == 1
    assert cfg.repos[0].name == "demo"
    assert cfg.repos[0].readme_sections == ["Capabilities"]


def test_load_config_missing_file_raises(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nonexistent.yaml")
