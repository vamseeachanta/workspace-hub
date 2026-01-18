#!/usr/bin/env python3
"""
ABOUTME: Worker response contract enforcement for hierarchical agent coordination
ABOUTME: Validates that worker agents return summary-only responses to prevent context overflow
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum


class WorkerStatus(Enum):
    """Valid worker response statuses."""
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class WorkerResponse:
    """
    Standardized worker response contract.

    All workers MUST return responses in this format to prevent context overflow.
    Detailed results are written to files, only summaries returned to coordinator.
    """
    worker_id: str
    status: str  # complete, failed, blocked
    summary: str  # 1-2 sentences MAX
    output_file: str  # Path to detailed results
    next_action: str  # Single recommended next step
    key_metrics: Dict[str, Any]  # Compact key=value metrics

    # Optional fields
    error_message: Optional[str] = None
    blocked_reason: Optional[str] = None
    duration_seconds: Optional[float] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

        # Validate status
        valid_statuses = [s.value for s in WorkerStatus]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status '{self.status}'. Must be one of: {valid_statuses}")

        # Validate summary length (max 200 chars recommended)
        if len(self.summary) > 300:
            raise ValueError(f"Summary too long ({len(self.summary)} chars). Max 300 chars for context efficiency.")

        # Validate next_action is single action
        if '\n' in self.next_action or len(self.next_action) > 150:
            raise ValueError("next_action must be a single, concise action (max 150 chars)")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkerResponse':
        """Create WorkerResponse from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'WorkerResponse':
        """Create WorkerResponse from JSON string."""
        return cls.from_dict(json.loads(json_str))


class WorkerContractValidator:
    """
    Validates worker responses against the contract.

    Ensures all workers return summary-only responses for context efficiency.
    """

    # Required fields for all responses
    REQUIRED_FIELDS = ['worker_id', 'status', 'summary', 'output_file', 'next_action', 'key_metrics']

    # Maximum lengths for context efficiency
    MAX_SUMMARY_LENGTH = 300
    MAX_NEXT_ACTION_LENGTH = 150
    MAX_METRICS_COUNT = 10

    def __init__(self, results_dir: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            results_dir: Directory for storing agent results
        """
        if results_dir:
            self.results_dir = Path(results_dir)
        else:
            # Default to .claude/state/agent_results/
            self.results_dir = Path.cwd() / ".claude" / "state" / "agent_results"

        self.results_dir.mkdir(parents=True, exist_ok=True)

    def validate(self, response: Union[Dict, WorkerResponse]) -> tuple[bool, List[str]]:
        """
        Validate a worker response against the contract.

        Args:
            response: Worker response dict or WorkerResponse object

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        if isinstance(response, WorkerResponse):
            data = response.to_dict()
        else:
            data = response

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, errors

        # Validate status
        valid_statuses = [s.value for s in WorkerStatus]
        if data['status'] not in valid_statuses:
            errors.append(f"Invalid status '{data['status']}'. Must be: {valid_statuses}")

        # Validate summary length
        if len(data['summary']) > self.MAX_SUMMARY_LENGTH:
            errors.append(f"Summary too long: {len(data['summary'])} chars (max {self.MAX_SUMMARY_LENGTH})")

        # Validate next_action
        if len(data['next_action']) > self.MAX_NEXT_ACTION_LENGTH:
            errors.append(f"next_action too long: {len(data['next_action'])} chars (max {self.MAX_NEXT_ACTION_LENGTH})")

        if '\n' in data['next_action']:
            errors.append("next_action must be single line (no newlines)")

        # Validate key_metrics
        if not isinstance(data['key_metrics'], dict):
            errors.append("key_metrics must be a dictionary")
        elif len(data['key_metrics']) > self.MAX_METRICS_COUNT:
            errors.append(f"Too many metrics: {len(data['key_metrics'])} (max {self.MAX_METRICS_COUNT})")

        # Validate output_file exists or is valid path
        if data['output_file'] and not data['output_file'].startswith('.claude/'):
            errors.append("output_file should be in .claude/ directory for consistency")

        return len(errors) == 0, errors

    def save_result(self, response: Union[Dict, WorkerResponse]) -> Path:
        """
        Save worker response to results directory.

        Args:
            response: Worker response to save

        Returns:
            Path to saved result file
        """
        if isinstance(response, dict):
            response = WorkerResponse.from_dict(response)

        # Generate filename from worker_id and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{response.worker_id}_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, 'w') as f:
            f.write(response.to_json())

        return filepath

    def load_results(self, worker_id: Optional[str] = None) -> List[WorkerResponse]:
        """
        Load worker results from results directory.

        Args:
            worker_id: Optional filter by worker ID

        Returns:
            List of WorkerResponse objects
        """
        results = []

        for filepath in self.results_dir.glob("*.json"):
            if worker_id and not filepath.name.startswith(worker_id):
                continue

            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    results.append(WorkerResponse.from_dict(data))
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                # Skip invalid files
                continue

        return results

    def aggregate_results(self, results: List[WorkerResponse]) -> Dict[str, Any]:
        """
        Aggregate multiple worker results into a summary.

        Args:
            results: List of worker responses to aggregate

        Returns:
            Aggregated summary dict (for coordinator)
        """
        if not results:
            return {
                "total_workers": 0,
                "status_summary": {},
                "combined_metrics": {},
                "next_actions": []
            }

        # Count by status
        status_counts = {}
        for r in results:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1

        # Combine metrics
        combined_metrics = {}
        for r in results:
            for key, value in r.key_metrics.items():
                if key not in combined_metrics:
                    combined_metrics[key] = []
                combined_metrics[key].append(value)

        # Aggregate numeric metrics
        aggregated_metrics = {}
        for key, values in combined_metrics.items():
            if all(isinstance(v, (int, float)) for v in values):
                aggregated_metrics[key] = {
                    "total": sum(values),
                    "count": len(values),
                    "avg": sum(values) / len(values) if values else 0
                }
            else:
                aggregated_metrics[key] = values

        # Collect next actions
        next_actions = [r.next_action for r in results if r.status != "complete"]

        return {
            "total_workers": len(results),
            "status_summary": status_counts,
            "combined_metrics": aggregated_metrics,
            "next_actions": next_actions[:5],  # Limit to top 5
            "all_complete": all(r.status == "complete" for r in results)
        }


def create_worker_response(
    worker_id: str,
    status: str,
    summary: str,
    output_file: str,
    next_action: str,
    key_metrics: Dict[str, Any],
    **kwargs
) -> WorkerResponse:
    """
    Factory function to create a validated worker response.

    Args:
        worker_id: Unique identifier for the worker
        status: complete, failed, or blocked
        summary: 1-2 sentence result summary (max 300 chars)
        output_file: Path to detailed results file
        next_action: Single recommended next step
        key_metrics: Dictionary of key=value metrics
        **kwargs: Optional fields (error_message, blocked_reason, duration_seconds)

    Returns:
        Validated WorkerResponse object

    Raises:
        ValueError: If response fails validation
    """
    response = WorkerResponse(
        worker_id=worker_id,
        status=status,
        summary=summary,
        output_file=output_file,
        next_action=next_action,
        key_metrics=key_metrics,
        **kwargs
    )

    # Validate
    validator = WorkerContractValidator()
    is_valid, errors = validator.validate(response)

    if not is_valid:
        raise ValueError(f"Invalid worker response: {'; '.join(errors)}")

    return response


# =============================================================================
# CLI Functions
# =============================================================================

def cli_main():
    """CLI entry point for worker contract operations."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: worker_contract.py <command> [args]")
        print("")
        print("Commands:")
        print("  validate <json_file>    Validate a worker response file")
        print("  aggregate               Aggregate all results in agent_results/")
        print("  example                 Show example worker response")
        print("  list                    List all saved worker results")
        sys.exit(1)

    command = sys.argv[1]
    validator = WorkerContractValidator()

    if command == "validate":
        if len(sys.argv) < 3:
            print("Usage: worker_contract.py validate <json_file>")
            sys.exit(1)

        filepath = Path(sys.argv[2])
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

        with open(filepath, 'r') as f:
            data = json.load(f)

        is_valid, errors = validator.validate(data)

        if is_valid:
            print("✓ Valid worker response")
        else:
            print("✗ Invalid worker response:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

    elif command == "aggregate":
        results = validator.load_results()

        if not results:
            print("No worker results found in .claude/state/agent_results/")
            sys.exit(0)

        aggregated = validator.aggregate_results(results)
        print(json.dumps(aggregated, indent=2, default=str))

    elif command == "example":
        example = {
            "worker_id": "pytest-validator-1",
            "status": "complete",
            "summary": "Validated 5 repos: 4 passed, 1 blocked (digitalmodel needs pytest.ini fix)",
            "output_file": ".claude/state/agent_results/pytest-validation-batch1.json",
            "next_action": "Fix digitalmodel pytest.ini markers",
            "key_metrics": {
                "repos_validated": 5,
                "passed": 4,
                "blocked": 1,
                "total_tests": 127
            }
        }
        print("Example worker response (summary-only format):")
        print(json.dumps(example, indent=2))

    elif command == "list":
        results = validator.load_results()

        if not results:
            print("No worker results found")
            sys.exit(0)

        print(f"Found {len(results)} worker results:\n")
        for r in results:
            status_icon = {"complete": "✓", "failed": "✗", "blocked": "⚠"}.get(r.status, "?")
            print(f"  {status_icon} {r.worker_id}: {r.summary[:60]}...")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
