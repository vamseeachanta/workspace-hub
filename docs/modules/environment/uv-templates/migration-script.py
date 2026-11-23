#!/usr/bin/env python3
"""
UV Migration Script
Automates the migration from pip-based projects to UV.

Usage:
    python migration-script.py [options] <project_path>

Examples:
    python migration-script.py .                    # Migrate current directory
    python migration-script.py --backup ./my-app    # Migrate with backup
    python migration-script.py --dry-run ./my-app   # Preview changes only
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import tomli_w
    import tomllib
except ImportError:
    print("Error: Required packages not found. Install with:")
    print("  pip install tomli-w")
    if sys.version_info < (3, 11):
        print("  pip install tomli")
    sys.exit(1)


class UVMigrator:
    """Handles migration from pip-based projects to UV."""

    def __init__(self, project_path: Path, dry_run: bool = False, backup: bool = True):
        self.project_path = Path(project_path).resolve()
        self.dry_run = dry_run
        self.backup = backup
        self.backup_dir = self.project_path / "uv-migration-backup"

        # Files to analyze
        self.requirements_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-test.txt",
            "dev-requirements.txt",
            "test-requirements.txt",
        ]

        self.existing_files = {
            "setup.py": None,
            "setup.cfg": None,
            "pyproject.toml": None,
            "Pipfile": None,
            "poetry.lock": None,
        }

    def run(self) -> None:
        """Execute the complete migration process."""
        print(f"🚀 Starting UV migration for: {self.project_path}")
        print(f"{'🔍 DRY RUN MODE - No changes will be made' if self.dry_run else '✅ LIVE MODE - Files will be modified'}")

        try:
            # Step 1: Validate environment
            self._validate_environment()

            # Step 2: Analyze current project
            project_info = self._analyze_project()

            # Step 3: Create backup if requested
            if self.backup and not self.dry_run:
                self._create_backup()

            # Step 4: Generate UV configuration
            uv_config = self._generate_uv_config(project_info)

            # Step 5: Write UV files
            self._write_uv_files(uv_config)

            # Step 6: Initialize UV environment
            if not self.dry_run:
                self._initialize_uv()

            # Step 7: Validate migration
            self._validate_migration()

            print("\n✅ Migration completed successfully!")
            self._print_next_steps()

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            if self.backup and self.backup_dir.exists():
                print(f"💾 Backup available at: {self.backup_dir}")
            sys.exit(1)

    def _validate_environment(self) -> None:
        """Validate that UV is installed and project is suitable for migration."""
        print("\n🔍 Validating environment...")

        # Check if UV is installed
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError("UV is not installed or not accessible")
            print(f"✅ UV found: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError("UV is not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")

        # Check if project directory exists
        if not self.project_path.exists():
            raise RuntimeError(f"Project path does not exist: {self.project_path}")

        # Check if already UV project
        if (self.project_path / "uv.lock").exists():
            print("⚠️  Warning: uv.lock already exists. This may be a UV project.")

    def _analyze_project(self) -> Dict:
        """Analyze the current project structure and dependencies."""
        print("\n📊 Analyzing project structure...")

        project_info = {
            "name": self.project_path.name,
            "dependencies": {},
            "dev_dependencies": {},
            "optional_dependencies": {},
            "python_version": None,
            "existing_config": {},
            "package_structure": None,
        }

        # Detect Python version
        python_version_file = self.project_path / ".python-version"
        if python_version_file.exists():
            project_info["python_version"] = python_version_file.read_text().strip()
        else:
            # Try to detect from setup.py or pyproject.toml
            project_info["python_version"] = "3.9"  # Default

        # Analyze existing configuration files
        for filename in self.existing_files:
            filepath = self.project_path / filename
            if filepath.exists():
                self.existing_files[filename] = filepath
                print(f"📋 Found: {filename}")

        # Parse requirements files
        for req_file in self.requirements_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                deps = self._parse_requirements_file(req_path)
                if "dev" in req_file.lower() or "test" in req_file.lower():
                    project_info["dev_dependencies"].update(deps)
                else:
                    project_info["dependencies"].update(deps)
                print(f"📦 Parsed: {req_file} ({len(deps)} dependencies)")

        # Parse existing pyproject.toml if present
        if self.existing_files["pyproject.toml"]:
            existing_config = self._parse_pyproject_toml(self.existing_files["pyproject.toml"])
            project_info["existing_config"] = existing_config

        # Detect package structure
        project_info["package_structure"] = self._detect_package_structure()

        return project_info

    def _parse_requirements_file(self, filepath: Path) -> Dict[str, str]:
        """Parse a requirements.txt file into a dictionary of package -> version."""
        dependencies = {}

        for line in filepath.read_text().splitlines():
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Skip -e and -r lines for now (editable installs and recursive requirements)
            if line.startswith("-e") or line.startswith("-r"):
                continue

            # Parse package specification
            # Handle: package>=1.0.0, package==1.0.0, package~=1.0.0, etc.
            match = re.match(r"([a-zA-Z0-9_-]+)([>=<~!]+.*)?", line)
            if match:
                package = match.group(1)
                version = match.group(2) or ""
                dependencies[package] = version

        return dependencies

    def _parse_pyproject_toml(self, filepath: Path) -> Dict:
        """Parse existing pyproject.toml file."""
        try:
            with open(filepath, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            print(f"⚠️  Warning: Could not parse {filepath}: {e}")
            return {}

    def _detect_package_structure(self) -> Optional[str]:
        """Detect the package structure (src layout vs flat layout)."""
        src_dir = self.project_path / "src"
        if src_dir.exists() and any(src_dir.iterdir()):
            return "src"

        # Look for Python packages in root
        for item in self.project_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                # Skip common non-package directories
                if item.name not in ["tests", "test", "docs", "scripts", "tools"]:
                    return "flat"

        return None

    def _create_backup(self) -> None:
        """Create a backup of important files before migration."""
        print(f"\n💾 Creating backup at: {self.backup_dir}")

        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        self.backup_dir.mkdir()

        # Backup files
        files_to_backup = [
            "requirements*.txt",
            "setup.py",
            "setup.cfg",
            "pyproject.toml",
            "Pipfile*",
            "poetry.lock",
            ".python-version",
        ]

        for pattern in files_to_backup:
            for filepath in self.project_path.glob(pattern):
                if filepath.is_file():
                    shutil.copy2(filepath, self.backup_dir)
                    print(f"   📋 Backed up: {filepath.name}")

    def _generate_uv_config(self, project_info: Dict) -> Dict:
        """Generate UV configuration based on project analysis."""
        print("\n🔧 Generating UV configuration...")

        # Base pyproject.toml structure
        config = {
            "build-system": {
                "requires": ["hatchling>=1.18.0"],
                "build-backend": "hatchling.build",
            },
            "project": {
                "name": project_info["name"],
                "version": "0.1.0",
                "description": f"Migrated project: {project_info['name']}",
                "readme": "README.md",
                "requires-python": f">={project_info['python_version']}",
                "dependencies": list(project_info["dependencies"].keys()),
            },
            "tool": {
                "uv": {
                    "dev-dependencies": list(project_info["dev_dependencies"].keys()),
                }
            }
        }

        # Add optional dependencies if we have dev dependencies
        if project_info["dev_dependencies"]:
            config["project"]["optional-dependencies"] = {
                "dev": list(project_info["dev_dependencies"].keys())
            }

        # Merge existing configuration if available
        if project_info["existing_config"]:
            self._merge_existing_config(config, project_info["existing_config"])

        # Add package structure configuration
        if project_info["package_structure"] == "src":
            config["tool"]["hatch"] = {
                "build": {
                    "targets": {
                        "wheel": {
                            "packages": [f"src/{project_info['name'].replace('-', '_')}"]
                        }
                    }
                }
            }

        return config

    def _merge_existing_config(self, config: Dict, existing: Dict) -> None:
        """Merge existing pyproject.toml configuration with generated config."""
        # Preserve existing project metadata
        if "project" in existing:
            existing_project = existing["project"]

            # Keep existing metadata if available
            for key in ["description", "authors", "license", "keywords", "classifiers"]:
                if key in existing_project:
                    config["project"][key] = existing_project[key]

            # Merge dependencies intelligently
            if "dependencies" in existing_project:
                existing_deps = set(existing_project["dependencies"])
                new_deps = set(config["project"]["dependencies"])
                config["project"]["dependencies"] = list(existing_deps | new_deps)

        # Preserve tool configurations
        if "tool" in existing:
            if "tool" not in config:
                config["tool"] = {}

            # Merge tool configurations (excluding uv which we're regenerating)
            for tool_name, tool_config in existing["tool"].items():
                if tool_name != "uv":
                    config["tool"][tool_name] = tool_config

    def _write_uv_files(self, config: Dict) -> None:
        """Write UV configuration files."""
        print("\n📝 Writing UV configuration files...")

        # Write pyproject.toml
        pyproject_path = self.project_path / "pyproject.toml"
        if not self.dry_run:
            with open(pyproject_path, "wb") as f:
                tomli_w.dump(config, f)
        print(f"   ✅ {'Would write' if self.dry_run else 'Wrote'}: pyproject.toml")

        # Write .python-version if not exists
        python_version_path = self.project_path / ".python-version"
        if not python_version_path.exists():
            python_version = config["project"]["requires-python"].replace(">=", "")
            if not self.dry_run:
                python_version_path.write_text(python_version)
            print(f"   ✅ {'Would write' if self.dry_run else 'Wrote'}: .python-version")

        # Create basic README.md if not exists
        readme_path = self.project_path / "README.md"
        if not readme_path.exists():
            readme_content = f"""# {config['project']['name']}

{config['project']['description']}

## Installation

```bash
uv sync
```

## Development

```bash
# Install with development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check .
```
"""
            if not self.dry_run:
                readme_path.write_text(readme_content)
            print(f"   ✅ {'Would create' if self.dry_run else 'Created'}: README.md")

    def _initialize_uv(self) -> None:
        """Initialize UV environment."""
        print("\n🔄 Initializing UV environment...")

        os.chdir(self.project_path)

        # Generate lock file
        print("   📦 Generating uv.lock...")
        result = subprocess.run(["uv", "lock"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ⚠️  Warning: uv lock failed: {result.stderr}")
        else:
            print("   ✅ Generated uv.lock")

        # Sync dependencies
        print("   🔄 Syncing dependencies...")
        result = subprocess.run(["uv", "sync"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ⚠️  Warning: uv sync failed: {result.stderr}")
        else:
            print("   ✅ Dependencies synced")

    def _validate_migration(self) -> None:
        """Validate that the migration was successful."""
        print("\n✅ Validating migration...")

        # Check that essential files exist
        required_files = ["pyproject.toml"]
        if not self.dry_run:
            required_files.append("uv.lock")

        for filename in required_files:
            filepath = self.project_path / filename
            if filepath.exists():
                print(f"   ✅ {filename} exists")
            else:
                print(f"   ❌ {filename} missing")

        # Try to run uv check
        if not self.dry_run:
            os.chdir(self.project_path)
            result = subprocess.run(["uv", "tree"], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ UV dependency tree validates")
            else:
                print(f"   ⚠️  UV validation warning: {result.stderr}")

    def _print_next_steps(self) -> None:
        """Print next steps for the user."""
        print(f"""
🎉 Migration completed! Next steps:

1. Review the generated pyproject.toml:
   {self.project_path / 'pyproject.toml'}

2. Test your environment:
   cd {self.project_path}
   uv sync
   uv run python -c "import sys; print(sys.path)"

3. Run your tests:
   uv run pytest

4. Update your CI/CD:
   - Replace 'pip install -r requirements.txt' with 'uv sync'
   - Use 'uv run' instead of direct python commands

5. Clean up old files (after testing):
   - requirements*.txt files
   - setup.py/setup.cfg (if migrated to pyproject.toml)

6. Update documentation:
   - Installation instructions
   - Development setup

📚 UV Documentation: https://docs.astral.sh/uv/
""")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate Python projects from pip to UV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migration-script.py .                    # Migrate current directory
  python migration-script.py --backup ./my-app    # Migrate with backup
  python migration-script.py --dry-run ./my-app   # Preview changes only
  python migration-script.py --no-backup ./app    # Skip backup creation
        """
    )

    parser.add_argument(
        "project_path",
        help="Path to the project to migrate"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without making them"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup of original files"
    )

    args = parser.parse_args()

    # Create and run migrator
    migrator = UVMigrator(
        project_path=args.project_path,
        dry_run=args.dry_run,
        backup=not args.no_backup
    )

    migrator.run()


if __name__ == "__main__":
    main()