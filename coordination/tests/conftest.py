# conftest.py - Pytest configuration and shared fixtures

import pytest
import os
import tempfile
from pathlib import Path
from typing import Generator, Any
from unittest.mock import Mock, patch

# Set testing environment
os.environ['TESTING'] = 'true'


# Basic fixtures
@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="function")
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture(scope="function")
def sample_data() -> dict[str, Any]:
    """Sample coordination data for testing."""
    return {
        "id": 1,
        "name": "Test Coordination Task",
        "description": "A test coordination task for testing purposes",
        "active": True,
        "priority": "high",
        "metadata": {
            "created_at": "2025-01-01T00:00:00Z",
            "tags": ["test", "coordination", "sample"],
            "assignee": "test-agent"
        }
    }


# File system fixtures
@pytest.fixture(scope="function")
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file for testing."""
    test_file = temp_dir / "test_file.txt"
    test_file.write_text("Test coordination content")
    yield test_file


@pytest.fixture(scope="function")
def empty_temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create an empty temporary file for testing."""
    test_file = temp_dir / "empty_file.txt"
    test_file.touch()
    yield test_file


# Mock fixtures for coordination
@pytest.fixture(scope="function")
def mock_requests():
    """Mock requests library for HTTP testing."""
    with patch('requests.Session') as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "coordination": "active"}
        mock_response.text = '{"status": "success", "coordination": "active"}'
        mock_session.return_value.get.return_value = mock_response
        mock_session.return_value.post.return_value = mock_response
        yield mock_session


@pytest.fixture(scope="function")
def mock_coordination_service():
    """Mock coordination service for testing."""
    # Create a mock service object directly instead of patching a module
    mock_service = Mock()
    # Configure mock coordination service behavior
    mock_service.connect.return_value = Mock()
    mock_service.assign_task.return_value = {"task_id": "test-123", "status": "assigned"}
    mock_service.get_status.return_value = {"status": "active", "tasks": []}
    mock_service.list_agents.return_value = ["agent1", "agent2", "agent3"]
    yield mock_service


# Environment fixtures
@pytest.fixture(scope="function")
def test_env_vars():
    """Set test environment variables for coordination."""
    test_vars = {
        'TEST_MODE': 'true',
        'DEBUG': 'false',
        'COORDINATION_URL': 'http://localhost:8080',
        'AGENT_TIMEOUT': '30',
        'MAX_AGENTS': '10'
    }

    # Store original values
    original_values = {}
    for key, value in test_vars.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value

    yield test_vars

    # Restore original values
    for key, original_value in original_values.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


# Custom markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "coordination: mark test as coordination-specific")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "agent: mark test as agent-related")
    config.addinivalue_line("markers", "memory: mark test as memory-related")
    config.addinivalue_line("markers", "external: mark test as requiring external services")


# Pytest hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add coordination marker for coordination-specific tests
        if "coordination" in str(item.fspath) or "coord" in str(item.fspath):
            item.add_marker(pytest.mark.coordination)


# Time mocking fixture
@pytest.fixture(scope="function")
def mock_time():
    """Mock time functions for consistent testing."""
    import time
    import datetime

    fixed_time = datetime.datetime(2025, 1, 1, 12, 0, 0)
    fixed_timestamp = fixed_time.timestamp()

    with patch('time.time', return_value=fixed_timestamp), \
         patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        mock_datetime.utcnow.return_value = fixed_time
        yield fixed_time


@pytest.fixture(scope="function")
def captured_logs(caplog):
    """Capture log messages for testing."""
    import logging
    caplog.set_level(logging.DEBUG)
    yield caplog