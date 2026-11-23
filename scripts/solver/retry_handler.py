#!/usr/bin/env python3
"""Retry logic with exponential backoff for solver queue jobs.

ABOUTME: Provides automatic retry for failed solver jobs on licensed-win-1.
Classifies errors as transient (retryable) or permanent (immediate fail).
Uses exponential backoff with jitter. Logs retry events to JSONL.

Usage (standalone):
    uv run python scripts/solver/retry_handler.py

Usage (as library):
    from retry_handler import RetryHandler, RetryConfig
    handler = RetryHandler(config=RetryConfig(max_retries=3))
    success = handler.execute_with_retry("job-001", my_callable)
"""
from __future__ import annotations

import datetime
import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts (default 3).
        base_delay: Base delay in seconds for first retry (default 1.0).
        max_delay: Maximum delay in seconds cap (default 60.0).
    """
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0


# ---------------------------------------------------------------------------
# Transient vs Permanent failure classification
# ---------------------------------------------------------------------------

# Patterns that indicate transient (retryable) failures
TRANSIENT_PATTERNS = [
    "connection timed out",
    "timed out",
    "timeout",
    "could not acquire lock",
    "file lock",
    "lock on",
    "network is unreachable",
    "network unreachable",
    "connection refused",
    "connection reset",
    "temporary failure",
    "resource temporarily unavailable",
    "failed to push",
    "failed to pull",
    "git pull failed",
    "git push failed",
    "service unavailable",
    "502 bad gateway",
    "503 service",
    "disk full",
    "no space left",
]

# Patterns that indicate permanent (non-retryable) failures
PERMANENT_PATTERNS = [
    "license",
    "invalid model",
    "unknown solver",
    "yaml parse error",
    "parse error",
    "invalid syntax",
    "file not found",
    "not found",
    "missing required fields",
    "permission denied",
    "access denied",
    "invalid file format",
]


def should_retry(error: str) -> bool:
    """Classify an error as transient (True) or permanent (False).

    Transient errors are retried (connection timeouts, file locks, network).
    Permanent errors are not retried (license, invalid model, parse errors).

    Args:
        error: Error message string from the failed job.

    Returns:
        True if the error is transient and should be retried.
    """
    if not error or not error.strip():
        return False

    error_lower = error.lower()

    # Check transient patterns first
    for pattern in TRANSIENT_PATTERNS:
        if pattern in error_lower:
            return True

    # Check permanent patterns -- if matched, definitely not transient
    for pattern in PERMANENT_PATTERNS:
        if pattern in error_lower:
            return False

    # Unknown errors: default to not retrying (safer)
    return False


# ---------------------------------------------------------------------------
# Exponential backoff
# ---------------------------------------------------------------------------

def get_backoff_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate the backoff delay for a given retry attempt.

    Uses exponential backoff: delay = base_delay * 2^(attempt-1)
    Adds +/-25% jitter to avoid thundering herd.
    Capped at config.max_delay.

    Args:
        attempt: Retry attempt number (0 = no retry, 1 = first retry).
        config: RetryConfig with base_delay and max_delay.

    Returns:
        Delay in seconds before the retry should be attempted.
    """
    if attempt <= 0:
        return 0.0

    # Exponential: base * 2^(attempt-1)
    raw_delay = config.base_delay * (2 ** (attempt - 1))

    # Cap at max
    raw_delay = min(raw_delay, config.max_delay)

    # Add +/-25% jitter
    jitter = raw_delay * 0.25 * (2 * random.random() - 1)
    delay = max(0.0, raw_delay + jitter)

    return min(delay, config.max_delay)


# ---------------------------------------------------------------------------
# JSONL retry logging
# ---------------------------------------------------------------------------

def record_retry(
    job_id: str,
    attempt: int,
    error: str,
    log_path: Path,
) -> None:
    """Append a retry event to a JSONL log file.

    Args:
        job_id: Unique job identifier.
        attempt: Retry attempt number.
        error: Error message that triggered the retry.
        log_path: Path to the JSONL log file.
    """
    entry = {
        "job_id": job_id,
        "attempt": attempt,
        "error": error,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# RetryHandler class
# ---------------------------------------------------------------------------

class RetryHandler:
    """Wraps job submission with retry + backoff logic.

    Usage:
        handler = RetryHandler(config=RetryConfig(max_retries=3))
        success = handler.execute_with_retry("job-001", submit_fn)
    """

    def __init__(
        self,
        config: Optional[RetryConfig] = None,
        log_path: Optional[Path] = None,
    ):
        self.config = config or RetryConfig()
        self.log_path = log_path or Path("data/retry-log.jsonl")

    def execute_with_retry(
        self,
        job_id: str,
        fn: Callable[[], bool],
    ) -> bool:
        """Execute a job function with retry on transient failures.

        Args:
            job_id: Unique job identifier for logging.
            fn: Callable that returns True on success or raises on failure.

        Returns:
            True if job succeeded, False if all retries exhausted or permanent error.
        """
        last_error = ""

        for attempt in range(self.config.max_retries + 1):
            try:
                result = fn()
                return bool(result)
            except Exception as e:
                last_error = str(e)

                # Check if this is a permanent failure
                if not should_retry(last_error):
                    return False

                # If we've used all retries, give up
                if attempt >= self.config.max_retries:
                    return False

                # Log the retry
                record_retry(
                    job_id=job_id,
                    attempt=attempt + 1,
                    error=last_error,
                    log_path=self.log_path,
                )

                # Wait before retrying
                delay = get_backoff_delay(attempt + 1, self.config)
                if delay > 0:
                    time.sleep(delay)

        return False


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("retry_handler.py -- Solver queue retry logic")
    print(f"  Default config: {RetryConfig()}")
    print(f"  Transient patterns: {len(TRANSIENT_PATTERNS)}")
    print(f"  Permanent patterns: {len(PERMANENT_PATTERNS)}")
    print()
    print("Examples:")
    timeout_result = should_retry("Connection timed out")
    license_result = should_retry("License check failed")
    delay1 = get_backoff_delay(1, RetryConfig())
    delay3 = get_backoff_delay(3, RetryConfig())
    print(f"  should_retry('Connection timed out') = {timeout_result}")
    print(f"  should_retry('License check failed') = {license_result}")
    print(f"  get_backoff_delay(1, RetryConfig()) = {delay1:.2f}s")
    print(f"  get_backoff_delay(3, RetryConfig()) = {delay3:.2f}s")
