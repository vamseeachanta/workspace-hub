"""Tests for solver queue retry logic with exponential backoff.

ABOUTME: Validates retry_handler.py — transient vs permanent failure classification,
exponential backoff timing, max retry enforcement, JSONL logging, and retry state.
All filesystem operations use temp directories. No external deps.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the module under test
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'solver'))
from retry_handler import (
    RetryConfig,
    RetryHandler,
    get_backoff_delay,
    record_retry,
    should_retry,
)


# ---------------------------------------------------------------------------
# Tests: Transient vs Permanent failure classification
# ---------------------------------------------------------------------------

class TestShouldRetry:
    """Test transient vs permanent failure detection."""

    def test_connection_timeout_is_transient(self):
        """Connection timeouts should be retried."""
        assert should_retry("Connection timed out after 30s") is True

    def test_file_lock_is_transient(self):
        """File lock errors should be retried."""
        assert should_retry("Could not acquire lock on input.owd") is True

    def test_network_unreachable_is_transient(self):
        """Network errors should be retried."""
        assert should_retry("Network is unreachable") is True

    def test_git_conflict_is_transient(self):
        """Git conflicts during push are transient."""
        assert should_retry("error: failed to push some refs") is True

    def test_license_error_is_permanent(self):
        """License errors are not retried — they won't resolve themselves."""
        assert should_retry("License check failed: no valid license found") is False

    def test_invalid_model_is_permanent(self):
        """Invalid model files are permanent failures."""
        assert should_retry("Invalid model file format") is False

    def test_unknown_solver_is_permanent(self):
        """Unknown solver type is permanent."""
        assert should_retry("Unknown solver: foobar") is False

    def test_yaml_parse_error_is_permanent(self):
        """YAML parse errors are permanent — file won't fix itself."""
        assert should_retry("YAML parse error: invalid syntax") is False

    def test_input_file_not_found_is_permanent(self):
        """Missing input file is permanent."""
        assert should_retry("Input file not found: model.dat") is False

    def test_empty_error_is_not_retried(self):
        """Empty error string should not be retried."""
        assert should_retry("") is False


# ---------------------------------------------------------------------------
# Tests: Exponential backoff timing
# ---------------------------------------------------------------------------

class TestGetBackoffDelay:
    """Test exponential backoff delay computation."""

    def test_first_attempt_base_delay(self):
        """First retry (attempt=1) uses base delay."""
        config = RetryConfig(base_delay=1.0, max_delay=60.0)
        delay = get_backoff_delay(1, config)
        assert delay == pytest.approx(1.0, abs=0.5)  # allow jitter

    def test_second_attempt_doubles(self):
        """Second retry (attempt=2) uses 2x base delay."""
        config = RetryConfig(base_delay=1.0, max_delay=60.0)
        delay = get_backoff_delay(2, config)
        assert delay == pytest.approx(2.0, abs=1.0)  # allow jitter

    def test_third_attempt_quadruples(self):
        """Third retry (attempt=3) uses 4x base delay."""
        config = RetryConfig(base_delay=1.0, max_delay=60.0)
        delay = get_backoff_delay(3, config)
        assert delay == pytest.approx(4.0, abs=2.0)  # allow jitter

    def test_delay_capped_at_max(self):
        """Delay never exceeds max_delay."""
        config = RetryConfig(base_delay=1.0, max_delay=60.0)
        delay = get_backoff_delay(100, config)
        assert delay <= 60.0

    def test_custom_base_delay(self):
        """Custom base delay is respected."""
        config = RetryConfig(base_delay=5.0, max_delay=300.0)
        delay = get_backoff_delay(1, config)
        assert delay == pytest.approx(5.0, abs=2.5)

    def test_zero_attempt_returns_zero(self):
        """Attempt 0 (no retry yet) returns 0 delay."""
        config = RetryConfig(base_delay=1.0, max_delay=60.0)
        delay = get_backoff_delay(0, config)
        assert delay == 0.0


# ---------------------------------------------------------------------------
# Tests: Retry state persistence (JSONL log)
# ---------------------------------------------------------------------------

class TestRecordRetry:
    """Test retry event logging to JSONL."""

    def test_creates_log_file(self, tmp_path: Path):
        """record_retry creates the log file if it doesn't exist."""
        log_path = tmp_path / "retry.jsonl"
        record_retry("job-001", 1, "Connection timed out", log_path)
        assert log_path.exists()

    def test_appends_valid_json(self, tmp_path: Path):
        """Each record_retry call appends a valid JSON line."""
        log_path = tmp_path / "retry.jsonl"
        record_retry("job-001", 1, "timeout", log_path)
        record_retry("job-001", 2, "timeout again", log_path)

        lines = log_path.read_text().strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            entry = json.loads(line)
            assert "job_id" in entry
            assert "attempt" in entry
            assert "error" in entry
            assert "timestamp" in entry

    def test_log_contains_correct_data(self, tmp_path: Path):
        """Logged entry contains the job_id, attempt, and error."""
        log_path = tmp_path / "retry.jsonl"
        record_retry("job-xyz", 3, "file locked", log_path)
        entry = json.loads(log_path.read_text().strip())
        assert entry["job_id"] == "job-xyz"
        assert entry["attempt"] == 3
        assert entry["error"] == "file locked"


# ---------------------------------------------------------------------------
# Tests: RetryConfig defaults
# ---------------------------------------------------------------------------

class TestRetryConfig:
    """Test RetryConfig dataclass defaults and override."""

    def test_default_values(self):
        """Default config has max_retries=3, base_delay=1.0, max_delay=60.0."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0

    def test_custom_values(self):
        """Custom config overrides defaults."""
        config = RetryConfig(max_retries=5, base_delay=2.0, max_delay=120.0)
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 120.0


# ---------------------------------------------------------------------------
# Tests: RetryHandler class
# ---------------------------------------------------------------------------

class TestRetryHandler:
    """Test the RetryHandler wrapper class."""

    def test_successful_on_first_try(self, tmp_path: Path):
        """Job that succeeds immediately needs no retry."""
        log_path = tmp_path / "retry.jsonl"
        handler = RetryHandler(config=RetryConfig(), log_path=log_path)
        mock_fn = MagicMock(return_value=True)
        result = handler.execute_with_retry("job-001", mock_fn)
        assert result is True
        assert mock_fn.call_count == 1
        assert not log_path.exists()  # no retries logged

    def test_retries_on_transient_failure(self, tmp_path: Path):
        """Handler retries on transient error, succeeds on second attempt."""
        log_path = tmp_path / "retry.jsonl"
        handler = RetryHandler(
            config=RetryConfig(max_retries=3, base_delay=0.01, max_delay=0.1),
            log_path=log_path,
        )
        mock_fn = MagicMock(side_effect=[
            Exception("Connection timed out"),
            True,
        ])
        result = handler.execute_with_retry("job-002", mock_fn)
        assert result is True
        assert mock_fn.call_count == 2
        # One retry logged
        lines = log_path.read_text().strip().split("\n")
        assert len(lines) == 1

    def test_gives_up_after_max_retries(self, tmp_path: Path):
        """Handler gives up after max_retries transient failures."""
        log_path = tmp_path / "retry.jsonl"
        handler = RetryHandler(
            config=RetryConfig(max_retries=2, base_delay=0.01, max_delay=0.1),
            log_path=log_path,
        )
        mock_fn = MagicMock(side_effect=Exception("Connection timed out"))
        result = handler.execute_with_retry("job-003", mock_fn)
        assert result is False
        # 1 initial + 2 retries = 3 calls
        assert mock_fn.call_count == 3

    def test_no_retry_on_permanent_failure(self, tmp_path: Path):
        """Handler does not retry permanent failures."""
        log_path = tmp_path / "retry.jsonl"
        handler = RetryHandler(
            config=RetryConfig(max_retries=3, base_delay=0.01, max_delay=0.1),
            log_path=log_path,
        )
        mock_fn = MagicMock(side_effect=Exception("License check failed: no valid license"))
        result = handler.execute_with_retry("job-004", mock_fn)
        assert result is False
        assert mock_fn.call_count == 1  # no retries

    def test_successful_retry_resets_state(self, tmp_path: Path):
        """After successful retry, handler reports success."""
        log_path = tmp_path / "retry.jsonl"
        handler = RetryHandler(
            config=RetryConfig(max_retries=3, base_delay=0.01, max_delay=0.1),
            log_path=log_path,
        )
        mock_fn = MagicMock(side_effect=[
            Exception("Connection timed out"),
            Exception("file lock"),
            True,
        ])
        result = handler.execute_with_retry("job-005", mock_fn)
        assert result is True
        assert mock_fn.call_count == 3
