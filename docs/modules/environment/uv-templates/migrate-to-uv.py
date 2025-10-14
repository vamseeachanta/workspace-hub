#!/usr/bin/env python3
"""
UV Migration Script - Automated migration from pip/Poetry to UV
Author: Engineering Team
Date: 2025-09-28
Version: 1.0.0
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import tomli
except ImportError:
    print("Installing tomli for TOML parsing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tomli"])
    import tomli

try:
    import tomli_w
except ImportError:
    print("Installing tomli_w for TOML writing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tomli_w"])
    import tomli_w


class UVMigrator:
    """Migrate Python projects to UV package manager."""

    def __init__(self, project_path: Path, verbose: bool = False):
        self.project_path = Path(project_path).resolve()
        self.verbose = verbose
        self.pyproject_path = self.project_path / "pyproject.toml"
        self.uv_toml_path = self.project_path / "uv.toml"
        self.requirements_path = self.project_path / "requirements.txt"
        self.requirements_dev_path = self.project_path / "requirements-dev.txt"
        self.poetry_lock_path = self.project_path / "poetry.lock"

    def log(self, message: str, level: str = "INFO"):
        """Log messages with level."""
        if self.verbose or level != "DEBUG":
            prefix = f"[{level}]"
            print(f"{prefix:10} {message}")

    def detect_package_manager(self) -> str:
        """Detect current package manager."""
        if self.poetry_lock_path.exists():
            return "poetry"
        elif self.pyproject_path.exists():
            with open(self.pyproject_path, "rb") as f:
                data = tomli.load(f)
                if "tool" in data and "poetry" in data["tool"]:
                    return "poetry"
                elif "project" in data and "dependencies" in data["project"]:
                    return "pyproject"
        elif self.requirements_path.exists():
            return "pip"
        elif self.uv_toml_path.exists():
            return "uv"
        return "unknown"

    def backup_files(self):
        """Create backups of existing configuration files."""
        self.log("Creating backups of existing files...")

        files_to_backup = [
            self.pyproject_path,
            self.uv_toml_path,
            self.requirements_path,
            self.poetry_lock_path,
        ]

        for file_path in files_to_backup:
            if file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                shutil.copy2(file_path, backup_path)
                self.log(f"Backed up {file_path.name} → {backup_path.name}", "DEBUG")

    def parse_requirements_txt(self, file_path: Path) -> Dict[str, str]:
        """Parse requirements.txt file."""
        deps = {}
        if not file_path.exists():
            return deps

        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Handle different requirement formats
                    match = re.match(r"([a-zA-Z0-9_-]+)(.*)$", line)
                    if match:
                        package = match.group(1)
                        version_spec = match.group(2).strip()
                        deps[package] = version_spec if version_spec else "*"

        return deps

    def parse_poetry_dependencies(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Parse Poetry dependencies from pyproject.toml."""
        deps = {}
        dev_deps = {}

        if not self.pyproject_path.exists():
            return deps, dev_deps

        with open(self.pyproject_path, "rb") as f:
            data = tomli.load(f)

        poetry_section = data.get("tool", {}).get("poetry", {})

        # Parse main dependencies
        for package, version_spec in poetry_section.get("dependencies", {}).items():
            if package.lower() != "python":
                if isinstance(version_spec, dict):
                    # Complex dependency specification
                    version = version_spec.get("version", "*")
                    deps[package] = version
                else:
                    deps[package] = version_spec

        # Parse dev dependencies
        dev_groups = ["dev-dependencies", "group.dev.dependencies"]
        for group in dev_groups:
            if "." in group:
                parts = group.split(".")
                section = poetry_section
                for part in parts:
                    section = section.get(part, {})
                dev_deps.update(section)
            else:
                dev_deps.update(poetry_section.get(group, {}))

        return deps, dev_deps

    def parse_pyproject_dependencies(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Parse standard pyproject.toml dependencies."""
        deps = {}
        dev_deps = {}

        if not self.pyproject_path.exists():
            return deps, dev_deps

        with open(self.pyproject_path, "rb") as f:
            data = tomli.load(f)

        project = data.get("project", {})

        # Parse main dependencies
        for dep_spec in project.get("dependencies", []):
            match = re.match(r"([a-zA-Z0-9_-]+)(.*)$", dep_spec)
            if match:
                package = match.group(1)
                version_spec = match.group(2).strip()
                deps[package] = version_spec if version_spec else "*"

        # Parse optional dependencies
        optional_deps = project.get("optional-dependencies", {})
        for group_name, group_deps in optional_deps.items():
            if group_name in ["dev", "test", "development", "testing"]:
                for dep_spec in group_deps:
                    match = re.match(r"([a-zA-Z0-9_-]+)(.*)$", dep_spec)
                    if match:
                        package = match.group(1)
                        version_spec = match.group(2).strip()
                        dev_deps[package] = version_spec if version_spec else "*"

        return deps, dev_deps

    def get_python_version(self) -> str:
        """Get Python version requirement."""
        if self.pyproject_path.exists():
            with open(self.pyproject_path, "rb") as f:
                data = tomli.load(f)

            # Check Poetry section
            poetry_python = data.get("tool", {}).get("poetry", {}).get("dependencies", {}).get("python")
            if poetry_python:
                return poetry_python

            # Check standard project section
            project_python = data.get("project", {}).get("requires-python")
            if project_python:
                return project_python

        # Default to modern Python
        return ">=3.9"

    def initialize_uv(self):
        """Initialize UV in the project."""
        self.log("Initializing UV...")

        # Check if UV is installed
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("UV is not installed. Please install it first:", "ERROR")
            self.log("  curl -LsSf https://astral.sh/uv/install.sh | sh", "ERROR")
            sys.exit(1)

        # Initialize UV (creates uv.toml if not exists)
        result = subprocess.run(
            ["uv", "init", "--no-workspace"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0 and "already exists" not in result.stderr:
            self.log(f"UV initialization failed: {result.stderr}", "ERROR")
            sys.exit(1)

    def add_dependencies(self, deps: Dict[str, str], dev: bool = False):
        """Add dependencies using UV."""
        if not deps:
            return

        dep_type = "dev" if dev else "main"
        self.log(f"Adding {len(deps)} {dep_type} dependencies...")

        for package, version_spec in deps.items():
            # Format dependency specification
            if version_spec and version_spec != "*":
                dep_spec = f"{package}{version_spec}"
            else:
                dep_spec = package

            # Build UV command
            cmd = ["uv", "add"]
            if dev:
                cmd.append("--dev")
            cmd.append(dep_spec)

            self.log(f"  Adding {dep_spec}...", "DEBUG")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self.log(f"  Warning: Failed to add {dep_spec}: {result.stderr}", "WARN")

    def update_pyproject_toml(self):
        """Update pyproject.toml with modern configuration."""
        self.log("Updating pyproject.toml configuration...")

        if not self.pyproject_path.exists():
            return

        with open(self.pyproject_path, "rb") as f:
            data = tomli.load(f)

        # Remove Poetry section if it exists
        if "tool" in data and "poetry" in data["tool"]:
            del data["tool"]["poetry"]
            self.log("  Removed Poetry configuration", "DEBUG")

        # Update Python version requirement
        if "project" in data:
            data["project"]["requires-python"] = ">=3.9"
            self.log("  Updated Python requirement to >=3.9", "DEBUG")

        # Add modern tool configurations if not present
        if "tool" not in data:
            data["tool"] = {}

        # Add pytest configuration
        if "pytest" not in data["tool"]:
            data["tool"]["pytest"] = {
                "ini_options": {
                    "testpaths": ["tests"],
                    "python_files": ["test_*.py"],
                    "addopts": "--strict-markers --strict-config"
                }
            }

        # Add ruff configuration
        if "ruff" not in data["tool"]:
            data["tool"]["ruff"] = {
                "target-version": "py39",
                "line-length": 88,
                "lint": {
                    "select": ["E", "W", "F", "I", "B", "UP"],
                    "ignore": ["E501"]
                }
            }

        # Write updated configuration
        with open(self.pyproject_path, "wb") as f:
            tomli_w.dump(data, f)

    def add_uv_scripts(self):
        """Add useful UV scripts to pyproject.toml."""
        self.log("Adding UV scripts...")

        if not self.pyproject_path.exists():
            return

        with open(self.pyproject_path, "rb") as f:
            data = tomli.load(f)

        # Ensure tool.uv.scripts section exists
        if "tool" not in data:
            data["tool"] = {}
        if "uv" not in data["tool"]:
            data["tool"]["uv"] = {}
        if "scripts" not in data["tool"]["uv"]:
            data["tool"]["uv"]["scripts"] = {}

        # Add standard scripts
        scripts = {
            "test": "pytest tests/ -v",
            "test-cov": "pytest tests/ --cov=src --cov-report=term-missing",
            "lint": "ruff check . && black --check .",
            "format": "ruff check . --fix && black .",
            "typecheck": "mypy src/",
            "clean": "rm -rf build dist *.egg-info .coverage htmlcov .pytest_cache"
        }

        for name, command in scripts.items():
            if name not in data["tool"]["uv"]["scripts"]:
                data["tool"]["uv"]["scripts"][name] = command
                self.log(f"  Added script: {name}", "DEBUG")

        # Write updated configuration
        with open(self.pyproject_path, "wb") as f:
            tomli_w.dump(data, f)

    def generate_lock_file(self):
        """Generate UV lock file."""
        self.log("Generating UV lock file...")

        result = subprocess.run(
            ["uv", "lock"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            self.log(f"Lock file generation failed: {result.stderr}", "WARN")
        else:
            self.log("  Lock file generated successfully", "DEBUG")

    def cleanup_old_files(self):
        """Remove old package manager files."""
        self.log("Cleaning up old files...")

        files_to_remove = [
            self.poetry_lock_path,
            self.project_path / "Pipfile",
            self.project_path / "Pipfile.lock",
        ]

        for file_path in files_to_remove:
            if file_path.exists():
                file_path.unlink()
                self.log(f"  Removed {file_path.name}", "DEBUG")

    def migrate(self, clean: bool = False):
        """Perform the migration."""
        self.log(f"Starting migration for {self.project_path.name}")

        # Detect current package manager
        current_pm = self.detect_package_manager()
        self.log(f"Detected package manager: {current_pm}")

        if current_pm == "uv":
            self.log("Project already uses UV!", "SUCCESS")
            return

        # Backup existing files
        self.backup_files()

        # Parse dependencies based on current package manager
        deps = {}
        dev_deps = {}

        if current_pm == "poetry":
            deps, dev_deps = self.parse_poetry_dependencies()
        elif current_pm == "pyproject":
            deps, dev_deps = self.parse_pyproject_dependencies()
        elif current_pm == "pip":
            deps = self.parse_requirements_txt(self.requirements_path)
            dev_deps = self.parse_requirements_txt(self.requirements_dev_path)
        else:
            self.log("Unknown package manager, attempting basic migration...", "WARN")

        self.log(f"Found {len(deps)} main dependencies and {len(dev_deps)} dev dependencies")

        # Initialize UV
        self.initialize_uv()

        # Add dependencies
        self.add_dependencies(deps, dev=False)
        self.add_dependencies(dev_deps, dev=True)

        # Update pyproject.toml
        self.update_pyproject_toml()

        # Add UV scripts
        self.add_uv_scripts()

        # Generate lock file
        self.generate_lock_file()

        # Cleanup old files if requested
        if clean:
            self.cleanup_old_files()

        self.log(f"Migration completed successfully for {self.project_path.name}!", "SUCCESS")
        self.log("Next steps:")
        self.log("  1. Review the generated uv.lock file")
        self.log("  2. Test dependency installation: uv sync")
        self.log("  3. Run tests: uv run test")
        self.log("  4. Commit changes to version control")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate Python projects to UV package manager"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to project directory (default: current directory)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-c", "--clean",
        action="store_true",
        help="Remove old package manager files after migration"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode: migrate multiple projects"
    )
    parser.add_argument(
        "--repos",
        nargs="+",
        help="List of repository names for batch migration"
    )

    args = parser.parse_args()

    if args.batch:
        # Batch migration mode
        base_path = Path(args.path).resolve()
        repos = args.repos or []

        if not repos:
            # Default repositories to migrate
            repos = [
                "investments",
                "achantas-data",
                "assetutilities",
                "assethold"
            ]

        print(f"Starting batch migration for {len(repos)} repositories...")
        print("-" * 50)

        for repo in repos:
            repo_path = base_path / repo
            if repo_path.exists():
                migrator = UVMigrator(repo_path, verbose=args.verbose)
                try:
                    migrator.migrate(clean=args.clean)
                except Exception as e:
                    print(f"[ERROR] Migration failed for {repo}: {e}")
                print("-" * 50)
            else:
                print(f"[SKIP] Repository not found: {repo_path}")

        print("Batch migration completed!")
    else:
        # Single project migration
        migrator = UVMigrator(args.path, verbose=args.verbose)
        migrator.migrate(clean=args.clean)


if __name__ == "__main__":
    main()