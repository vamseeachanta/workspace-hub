"""Workstation registry helpers."""

from .resolver import MachineRecord, WorkstationPathResolver
from . import task_dispatch

__all__ = ["MachineRecord", "WorkstationPathResolver", "task_dispatch"]
