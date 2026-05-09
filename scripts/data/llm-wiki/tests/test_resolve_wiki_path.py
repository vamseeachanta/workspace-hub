"""Smoke tests for llm-wiki portable path resolution.

Validates the resolution order:
  1. $LLM_WIKI_DATA_DIR env var
  2. config/llm-wiki.yaml -> data_dir
  3. ${REPO_ROOT}/data/llm-wiki  (local symlink or dir)
  4. ${REPO_ROOT}/knowledge/wikis (git-tracked fallback)

Ref: GH #2140
"""

import importlib
import os
import shutil
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# The module lives in a hyphenated directory (scripts/data/llm-wiki/) which
# cannot be imported as a normal Python package.  Insert the directory into
# sys.path so we can import resolve_wiki_path directly.
_SCRIPT_DIR = Path(__file__).resolve().parent.parent  # scripts/data/llm-wiki/
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import resolve_wiki_path as mod  # noqa: E402


@pytest.fixture()
def tmp_repo(tmp_path):
    """Create a minimal repo-like tree for testing."""
    (tmp_path / "data" / "llm-wiki").mkdir(parents=True)
    (tmp_path / "knowledge" / "wikis").mkdir(parents=True)
    (tmp_path / "config").mkdir(parents=True)
    return tmp_path


@pytest.fixture(autouse=True)
def _clean_env():
    """Remove LLM_WIKI_DATA_DIR from env before each test."""
    old = os.environ.pop("LLM_WIKI_DATA_DIR", None)
    yield
    if old is not None:
        os.environ["LLM_WIKI_DATA_DIR"] = old
    else:
        os.environ.pop("LLM_WIKI_DATA_DIR", None)


# -- 1. Env var override ------------------------------------------------------


class TestEnvVar:

    def test_env_var_takes_priority(self, tmp_path, tmp_repo):
        """$LLM_WIKI_DATA_DIR should win when the path exists."""
        custom = tmp_path / "custom-wiki"
        custom.mkdir()
        os.environ["LLM_WIKI_DATA_DIR"] = str(custom)

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        assert result == custom

    def test_env_var_ignored_when_path_missing(self, tmp_repo):
        """Non-existent env var path should fall through to next candidate."""
        os.environ["LLM_WIKI_DATA_DIR"] = "/nonexistent/does-not-exist"

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        # Should fall through to data/llm-wiki
        assert result == tmp_repo / "data" / "llm-wiki"


# -- 2. Config file ------------------------------------------------------------


class TestConfigFile:

    def test_config_yaml_data_dir(self, tmp_path, tmp_repo):
        """config/llm-wiki.yaml data_dir should be used when present."""
        custom = tmp_path / "yaml-wiki"
        custom.mkdir()

        config_file = tmp_repo / "config" / "llm-wiki.yaml"
        config_file.write_text(f"data_dir: {custom}\n")

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            # Remove data/llm-wiki so config has a chance
            shutil.rmtree(tmp_repo / "data" / "llm-wiki")
            result = mod.resolve_wiki_dir()
        assert result == custom

    def test_config_yaml_skipped_when_missing(self, tmp_repo):
        """No config file should not raise -- falls through gracefully."""
        shutil.rmtree(tmp_repo / "data" / "llm-wiki")

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        # Falls through to knowledge/wikis
        assert result == tmp_repo / "knowledge" / "wikis"


# -- 3. Repo data/llm-wiki ----------------------------------------------------


class TestRepoDataDir:

    def test_data_llm_wiki_dir(self, tmp_repo):
        """data/llm-wiki directory should resolve when it exists."""
        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        assert result == tmp_repo / "data" / "llm-wiki"

    def test_data_llm_wiki_symlink(self, tmp_path, tmp_repo):
        """A symlink at data/llm-wiki should resolve correctly."""
        target = tmp_path / "remote-wiki"
        target.mkdir()
        # Replace the directory with a symlink
        shutil.rmtree(tmp_repo / "data" / "llm-wiki")
        os.symlink(str(target), str(tmp_repo / "data" / "llm-wiki"))

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        assert result == tmp_repo / "data" / "llm-wiki"


# -- 4. Fallback --------------------------------------------------------------


class TestFallback:

    def test_fallback_to_knowledge_wikis(self, tmp_repo):
        """When nothing else exists, knowledge/wikis is the fallback."""
        shutil.rmtree(tmp_repo / "data" / "llm-wiki")

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        assert result == tmp_repo / "knowledge" / "wikis"

    def test_fallback_returned_even_if_absent(self, tmp_repo):
        """Fallback path is returned even when it does not exist on disk."""
        shutil.rmtree(tmp_repo / "data" / "llm-wiki")
        shutil.rmtree(tmp_repo / "knowledge" / "wikis")

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        assert result == tmp_repo / "knowledge" / "wikis"


# -- 4b. Dangling symlink at branch #3 ----------------------------------------


class TestDanglingSymlink:

    def test_dangling_symlink_at_data_llm_wiki_warns_and_falls_through(
        self, tmp_path, tmp_repo, capsys
    ):
        """Broken symlink at data/llm-wiki should warn to stderr and fall through to fallback."""
        target = tmp_path / "nonexistent-nfs-target"  # never created
        # Replace the directory with a broken symlink
        shutil.rmtree(tmp_repo / "data" / "llm-wiki")
        os.symlink(str(target), str(tmp_repo / "data" / "llm-wiki"))

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        captured = capsys.readouterr()
        assert "dangling symlink" in captured.err
        assert "nonexistent-nfs-target" in captured.err
        assert result == tmp_repo / "knowledge" / "wikis"

    def test_no_warning_when_data_llm_wiki_simply_absent(self, tmp_repo, capsys):
        """No symlink + no dir should fall through silently — the warning is reserved for the broken-symlink case."""
        shutil.rmtree(tmp_repo / "data" / "llm-wiki")

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        captured = capsys.readouterr()
        assert "dangling symlink" not in captured.err
        assert result == tmp_repo / "knowledge" / "wikis"


# -- 5. Resolution order -------------------------------------------------------


class TestResolutionOrder:

    def test_env_beats_config_beats_data_dir(self, tmp_path, tmp_repo):
        """Env var wins over config, which wins over data/llm-wiki."""
        env_dir = tmp_path / "env-wiki"
        env_dir.mkdir()
        cfg_dir = tmp_path / "cfg-wiki"
        cfg_dir.mkdir()

        os.environ["LLM_WIKI_DATA_DIR"] = str(env_dir)
        config_file = tmp_repo / "config" / "llm-wiki.yaml"
        config_file.write_text(f"data_dir: {cfg_dir}\n")

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        assert result == env_dir

    def test_config_beats_data_dir_when_no_env(self, tmp_path, tmp_repo):
        """Config file wins over data/llm-wiki when env var is absent."""
        cfg_dir = tmp_path / "cfg-wiki"
        cfg_dir.mkdir()

        config_file = tmp_repo / "config" / "llm-wiki.yaml"
        config_file.write_text(f"data_dir: {cfg_dir}\n")

        # Remove data/llm-wiki so config is reached
        shutil.rmtree(tmp_repo / "data" / "llm-wiki")

        with patch.object(mod, "REPO_ROOT", tmp_repo):
            result = mod.resolve_wiki_dir()
        assert result == cfg_dir
