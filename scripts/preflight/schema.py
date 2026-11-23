"""Constants for Hermes preflight report schema v1."""

from __future__ import annotations


SCHEMA_VERSION = "1"
CHECK_STATUSES = ("pass", "warn", "block")
ENGINEERING_TOOLS = (
    "openfoam",
    "gmsh",
    "paraview",
    "calculix",
    "orcaflex",
)
CORE_TOOLS = ("hermes", "codex", "claude", "gemini", "gh", "git", "uv")

