"""
Smoke tests for coordination repository

Basic tests to verify the testing infrastructure and project setup
"""

import sys
import pytest
from pathlib import Path


class TestSmokeTests:
    """Smoke tests to validate basic project functionality."""

    def test_python_version(self):
        """Test that Python version is supported."""
        assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info}"
        assert sys.version_info < (4, 0), f"Python 4.0+ not supported, got {sys.version_info}"

    def test_project_structure(self, project_root):
        """Test that basic project structure exists."""
        # Check that we have the basic directories
        assert project_root.exists(), "Project root should exist"
        assert (project_root / "tests").exists(), "Tests directory should exist"

        # Check for expected subdirectories
        memory_bank = project_root / "memory_bank"
        orchestration = project_root / "orchestration"
        subtasks = project_root / "subtasks"

        assert memory_bank.exists(), "memory_bank directory should exist"
        assert orchestration.exists(), "orchestration directory should exist"
        assert subtasks.exists(), "subtasks directory should exist"

    def test_imports(self):
        """Test that basic Python imports work."""
        # Test standard library imports
        import json
        import os
        import sys
        import pathlib

        # Test testing framework imports
        import pytest
        import unittest
        from unittest.mock import Mock, patch

        # Verify imports work without errors
        assert json is not None
        assert os is not None
        assert sys is not None
        assert pathlib is not None
        assert pytest is not None
        assert unittest is not None
        assert Mock is not None
        assert patch is not None

    def test_pytest_configuration(self):
        """Test that pytest is configured correctly."""
        # Test that pytest can find and run tests
        import pytest

        # Verify pytest markers are available
        assert hasattr(pytest.mark, 'unit')
        assert hasattr(pytest.mark, 'integration')
        assert hasattr(pytest.mark, 'coordination')
        assert hasattr(pytest.mark, 'slow')

    def test_fixtures_available(self, project_root, sample_data, temp_dir):
        """Test that conftest.py fixtures are available."""
        # Test project_root fixture
        assert isinstance(project_root, Path)
        assert project_root.exists()

        # Test sample_data fixture
        assert isinstance(sample_data, dict)
        assert "id" in sample_data
        assert "name" in sample_data
        assert sample_data["name"] == "Test Coordination Task"

        # Test temp_dir fixture
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()

    def test_test_environment_setup(self, test_env_vars):
        """Test that test environment is configured correctly."""
        import os

        # Check that testing environment is set
        assert os.environ.get('TESTING') == 'true'

        # Check test environment variables from fixture
        assert test_env_vars['TEST_MODE'] == 'true'
        assert test_env_vars['DEBUG'] == 'false'
        assert 'COORDINATION_URL' in test_env_vars
        assert 'AGENT_TIMEOUT' in test_env_vars
        assert 'MAX_AGENTS' in test_env_vars


@pytest.mark.unit
class TestBasicFunctionality:
    """Test basic functionality that should always work."""

    def test_string_operations(self):
        """Test basic string operations work."""
        test_string = "coordination-test"
        assert len(test_string) > 0
        assert "coordination" in test_string
        assert test_string.startswith("coordination")
        assert test_string.endswith("test")

    def test_list_operations(self):
        """Test basic list operations work."""
        test_list = ["agent1", "agent2", "agent3"]
        assert len(test_list) == 3
        assert "agent1" in test_list
        assert test_list[0] == "agent1"
        assert test_list[-1] == "agent3"

    def test_dict_operations(self, sample_data):
        """Test basic dictionary operations work."""
        assert isinstance(sample_data, dict)
        assert len(sample_data) > 0
        assert sample_data.get("name") is not None
        assert sample_data["active"] is True

    def test_file_operations(self, temp_file):
        """Test basic file operations work."""
        assert temp_file.exists()
        content = temp_file.read_text()
        assert "coordination" in content
        assert len(content) > 0

    def test_path_operations(self, project_root, temp_dir):
        """Test basic path operations work."""
        # Test absolute path resolution
        abs_path = project_root.resolve()
        assert abs_path.is_absolute()

        # Test relative path operations
        rel_path = Path("tests")
        test_path = project_root / rel_path
        assert test_path.exists()

        # Test temporary directory operations
        temp_file = temp_dir / "test.txt"
        temp_file.write_text("test")
        assert temp_file.exists()


@pytest.mark.coordination
class TestCoordinationSpecific:
    """Tests specific to coordination functionality."""

    def test_coordination_data_structure(self, sample_data):
        """Test coordination-specific data structures."""
        # Check coordination-specific fields
        assert "priority" in sample_data
        assert sample_data["priority"] in ["low", "medium", "high", "critical"]

        # Check metadata structure
        assert "metadata" in sample_data
        metadata = sample_data["metadata"]
        assert "assignee" in metadata
        assert "tags" in metadata
        assert "coordination" in metadata["tags"]

    def test_mock_coordination_service(self, mock_coordination_service):
        """Test mock coordination service fixture."""
        # Test that mock service is available and working
        assert mock_coordination_service is not None

        # Test mock service methods
        status = mock_coordination_service.get_status.return_value
        assert status["status"] == "active"
        assert "tasks" in status

        agents = mock_coordination_service.list_agents.return_value
        assert len(agents) == 3
        assert "agent1" in agents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])