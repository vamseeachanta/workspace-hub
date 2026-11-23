#!/usr/bin/env python3
"""
Sync UV-aware commands to all repositories.

This script copies the updated commands with UV environment support
to all repositories, ensuring all repos can use existing UV environments
instead of creating new virtual environments.
"""

import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Commands to sync with UV support
UV_AWARE_COMMANDS = [
    "test.py",
    "task.py", 
    "spec.py",
    "uv_environment_manager.py",  # The UV manager itself
]

# Additional files that might reference UV
RELATED_FILES = [
    "test_automation_enhanced.py",
    "execute_tasks_enhanced.py",
    "spec_enhanced.py",
]

def sync_commands_to_repo(repo_name: str) -> tuple:
    """Sync UV-aware commands to a single repository."""
    try:
        repo_path = Path(f"/mnt/github/github/{repo_name}")
        
        if not repo_path.exists():
            return (repo_name, False, "Repository not found")
        
        # Skip the main github folder itself
        if repo_name == "github":
            return (repo_name, False, "Skipping source repository")
        
        # Create .agent-os/commands if it doesn't exist
        commands_dir = repo_path / ".agent-os" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        source_dir = Path("/mnt/github/github/.agent-os/commands")
        
        # Copy UV-aware commands
        copied_files = []
        for cmd_file in UV_AWARE_COMMANDS:
            source = source_dir / cmd_file
            if source.exists():
                dest = commands_dir / cmd_file
                shutil.copy2(source, dest)
                # Make executable
                dest.chmod(0o755)
                copied_files.append(cmd_file)
        
        # Copy related files if they exist
        for related_file in RELATED_FILES:
            source = source_dir / related_file
            if source.exists():
                dest = commands_dir / related_file
                shutil.copy2(source, dest)
                dest.chmod(0o755)
                copied_files.append(related_file)
        
        # Create UV config documentation
        uv_doc = repo_path / ".agent-os" / "UV_ENVIRONMENT.md"
        uv_doc_content = """# UV Environment Support

This repository now has UV environment support integrated into all commands.

## What Changed

All test, task, and spec commands now:
1. Automatically detect existing UV environments
2. Use the UV Python interpreter when available
3. Can enhance UV environments with spec-specific dependencies
4. Prevent creation of duplicate virtual environments

## Benefits

- **Faster execution**: No need to create new virtual environments
- **Consistent dependencies**: All commands use the same environment
- **Better resource usage**: Single environment per repository
- **Automatic enhancement**: Specs can add dependencies as needed

## Commands with UV Support

- `/test` - Run tests using UV environment
- `/task` - Execute tasks using UV environment  
- `/spec` - Create specs with UV-aware execution
- `/uv-env` - Manage UV environments directly

## UV Environment Manager

The UV environment manager provides:
- Automatic detection of existing UV environments
- Environment creation if needed
- Dependency management
- Python executable discovery

## Usage

Commands automatically use UV when available. No configuration needed.

To manually manage UV environments:
```bash
/uv-env info        # Show UV environment info
/uv-env ensure      # Ensure UV environment exists
/uv-env sync        # Sync dependencies
/uv-env add PACKAGE # Add a package
```

## Creating UV Environment

If your repo doesn't have UV yet:
```bash
uv init
uv venv
uv sync
```

## Requirements

UV must be installed globally:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---
Last updated: 2024-01-13
"""
        uv_doc.write_text(uv_doc_content)
        
        return (repo_name, True, f"Synced {len(copied_files)} UV-aware files")
        
    except Exception as e:
        return (repo_name, False, str(e))

def main():
    """Sync UV-aware commands to all repositories."""
    # Get all repositories
    repos = []
    github_dir = Path("/mnt/github/github")
    
    for item in github_dir.iterdir():
        if item.is_dir() and (item / '.git').exists():
            repos.append(item.name)
    
    print(f"🔄 Syncing UV-aware commands to {len(repos)} repositories...\n")
    
    success_count = 0
    failed_repos = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(sync_commands_to_repo, repo) for repo in repos]
        
        for future in as_completed(futures):
            repo_name, success, message = future.result()
            
            if success:
                print(f"✅ {repo_name}: {message}")
                success_count += 1
            else:
                if "Skipping" not in message:
                    print(f"❌ {repo_name}: {message}")
                    failed_repos.append(repo_name)
                else:
                    print(f"ℹ️  {repo_name}: {message}")
    
    print(f"\n📊 Summary:")
    print(f"   Successfully synced: {success_count}/{len(repos)-1}")  # -1 for skipped source
    
    if failed_repos:
        print(f"   Failed repositories: {', '.join(failed_repos)}")
    
    if success_count > 0:
        print("\n✨ UV-aware commands synced successfully!")
        print("\n📋 Next Steps:")
        print("   1. All repos can now use existing UV environments")
        print("   2. Test commands will automatically detect UV")
        print("   3. Task execution will use UV Python")
        print("   4. Specs will enhance UV environments as needed")
        print("\n💡 To create UV environment in a repo:")
        print("   cd <repo> && uv init && uv venv && uv sync")

if __name__ == "__main__":
    main()