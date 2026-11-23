#!/usr/bin/env python3
"""
ABOUTME: Approval log tracking system for workspace-hub
ABOUTME: Manages approval workflow across all SPARC phases
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import yaml


PHASES = [
    "specification",
    "pseudocode",
    "architecture",
    "implementation",
    "deployment"
]

APPROVAL_STATUS = [
    "PROPOSED",
    "APPROVED",
    "REJECTED",
    "NEEDS_REVISION"
]


class ApprovalTracker:
    """Manages approval logs for specifications."""

    def __init__(self, spec_name: str, workspace_root: Path = Path(".")):
        self.spec_name = spec_name
        self.workspace_root = workspace_root
        self.spec_dir = workspace_root / ".agent-os" / "specs" / spec_name
        self.approval_log_path = self.spec_dir / "approval_log.md"

    def ensure_spec_directory(self):
        """Ensure spec directory exists."""
        self.spec_dir.mkdir(parents=True, exist_ok=True)

    def create_approval_log(self):
        """Create initial approval log file."""
        self.ensure_spec_directory()

        template = f"""# Approval Log - {self.spec_name}

> **Spec:** {self.spec_name}
> **Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

This log tracks all approvals and reviews for the {self.spec_name} specification through all SPARC phases.

### Approval Phases
1. **Specification** - Requirements and spec document
2. **Pseudocode** - Algorithm design and pseudocode
3. **Architecture** - System architecture and design
4. **Implementation** - Code implementation and tests
5. **Deployment** - Deployment approval and sign-off

---

"""

        with open(self.approval_log_path, 'w') as f:
            f.write(template)

        print(f"✓ Created approval log: {self.approval_log_path}")

    def add_approval_entry(
        self,
        phase: str,
        version: str,
        approver: str,
        status: str,
        changes: list,
        comments: str,
        conditions: list = None
    ):
        """Add approval entry to log."""
        if not self.approval_log_path.exists():
            self.create_approval_log()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = f"""
## [{phase.title()}] - Version {version}
**Date:** {timestamp}
**Approver:** {approver}
**Status:** {status}

### Changes from Previous Version
"""

        for change in changes:
            entry += f"- {change}\n"

        entry += f"\n### Review Comments\n{comments}\n"

        if conditions:
            entry += "\n### Conditions/Requirements\n"
            for condition in conditions:
                entry += f"- {condition}\n"

        entry += f"\n### Approval Decision\n**{status}**\n"

        if status == "APPROVED":
            entry += "\n✓ **Approved** - May proceed to next phase\n"
        elif status == "REJECTED":
            entry += "\n✗ **Rejected** - Revisions required\n"
        elif status == "NEEDS_REVISION":
            entry += "\n⚠ **Needs Revision** - Address comments and resubmit\n"

        entry += "\n---\n"

        # Append to log
        with open(self.approval_log_path, 'a') as f:
            f.write(entry)

        print(f"✓ Added {phase} approval entry (Status: {status})")

    def get_phase_status(self, phase: str) -> Optional[str]:
        """Get current status of a phase."""
        if not self.approval_log_path.exists():
            return None

        with open(self.approval_log_path, 'r') as f:
            content = f.read()

        # Find last status for this phase
        phase_section = f"[{phase.title()}]"
        if phase_section not in content:
            return None

        # Extract status from last occurrence
        last_section = content.split(phase_section)[-1].split("---")[0]
        for status in APPROVAL_STATUS:
            if f"**{status}**" in last_section or f"Status:** {status}" in last_section:
                return status

        return None

    def get_all_statuses(self) -> Dict[str, Optional[str]]:
        """Get status of all phases."""
        return {
            phase: self.get_phase_status(phase)
            for phase in PHASES
        }

    def can_proceed_to_phase(self, phase: str) -> bool:
        """Check if can proceed to given phase."""
        phase_index = PHASES.index(phase)

        # First phase always allowed
        if phase_index == 0:
            return True

        # Check if previous phase is approved
        previous_phase = PHASES[phase_index - 1]
        previous_status = self.get_phase_status(previous_phase)

        return previous_status == "APPROVED"

    def print_status_summary(self):
        """Print summary of all phase statuses."""
        print(f"\n{'='*60}")
        print(f"Approval Status Summary - {self.spec_name}")
        print(f"{'='*60}\n")

        statuses = self.get_all_statuses()

        for i, phase in enumerate(PHASES, 1):
            status = statuses[phase]

            if status is None:
                status_icon = "⚪"
                status_text = "NOT STARTED"
            elif status == "APPROVED":
                status_icon = "✓"
                status_text = "APPROVED"
            elif status == "REJECTED":
                status_icon = "✗"
                status_text = "REJECTED"
            elif status == "NEEDS_REVISION":
                status_icon = "⚠"
                status_text = "NEEDS REVISION"
            else:
                status_icon = "?"
                status_text = status

            print(f"{i}. {status_icon} {phase.upper():.<30} {status_text}")

        print(f"\n{'='*60}\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Track approval workflow for specifications"
    )

    parser.add_argument(
        "--spec",
        type=str,
        required=True,
        help="Specification name"
    )

    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("."),
        help="Workspace root directory"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create approval log")

    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit for approval")
    submit_parser.add_argument("--phase", type=str, required=True, choices=PHASES)
    submit_parser.add_argument("--version", type=str, required=True)
    submit_parser.add_argument("--approver", type=str, required=True)
    submit_parser.add_argument("--status", type=str, required=True, choices=APPROVAL_STATUS)
    submit_parser.add_argument("--changes", type=str, nargs="+", required=True)
    submit_parser.add_argument("--comments", type=str, required=True)
    submit_parser.add_argument("--conditions", type=str, nargs="*")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show approval status")
    status_parser.add_argument("--phase", type=str, choices=PHASES, help="Show specific phase")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check if can proceed to phase")
    check_parser.add_argument("--phase", type=str, required=True, choices=PHASES)

    args = parser.parse_args()

    tracker = ApprovalTracker(args.spec, args.workspace)

    if args.command == "create":
        tracker.create_approval_log()

    elif args.command == "submit":
        tracker.add_approval_entry(
            phase=args.phase,
            version=args.version,
            approver=args.approver,
            status=args.status,
            changes=args.changes,
            comments=args.comments,
            conditions=args.conditions or []
        )

    elif args.command == "status":
        if args.phase:
            status = tracker.get_phase_status(args.phase)
            print(f"{args.phase.title()}: {status or 'NOT STARTED'}")
        else:
            tracker.print_status_summary()

    elif args.command == "check":
        can_proceed = tracker.can_proceed_to_phase(args.phase)
        if can_proceed:
            print(f"✓ Can proceed to {args.phase} phase")
            return 0
        else:
            print(f"✗ Cannot proceed to {args.phase} phase - previous phase not approved")
            return 1

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
