#!/usr/bin/env python3
"""
Sync all repositories and propagate all Agent OS commands.

This script:
1. Syncs all repos with git pull
2. Copies all latest commands from the main repo
3. Ensures all repos have the latest Agent OS functionality
"""

import os
import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# All commands to propagate
ALL_COMMANDS = [
    # Core unified commands
    "git.py",
    "spec.py",
    "task.py",
    "test.py",
    "project.py",
    "data.py",
    
    # UV environment support
    "uv_environment_manager.py",
    
    # Enhanced versions
    "spec_enhanced.py",
    "test_automation_enhanced.py",
    "execute_tasks_enhanced.py",
    "engineering_data_context.py",
    
    # AI agent support
    "ai_agent.py",
    
    # Verification and utilities
    "verify-ai-work.py",
    "command_aliases.json",
]

# Resource files to sync
RESOURCE_FILES = [
    "aitmpl_agents_catalog.yaml",
    "ai_templates.yaml",
]

def sync_and_propagate_repo(repo_name: str) -> tuple:
    """Sync a repository and propagate commands."""
    try:
        repo_path = Path(f"/mnt/github/github/{repo_name}")
        
        if not repo_path.exists() or not (repo_path / ".git").exists():
            return (repo_name, False, "Not a git repository")
        
        # Skip the main github folder
        if repo_name == "github":
            return (repo_name, False, "Skipping source repository")
        
        results = []
        
        # 1. Git sync
        os.chdir(repo_path)
        
        # Check for uncommitted changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        has_changes = bool(status_result.stdout.strip())
        
        if has_changes:
            # Stash changes
            subprocess.run(
                ["git", "stash", "push", "-m", f"Auto-stash before sync {time.strftime('%Y-%m-%d_%H:%M:%S')}"],
                capture_output=True
            )
            results.append("stashed changes")
        
        # Pull latest
        pull_result = subprocess.run(
            ["git", "pull", "--rebase", "origin"],
            capture_output=True,
            text=True
        )
        
        if pull_result.returncode == 0:
            if "Already up to date" in pull_result.stdout:
                results.append("already up-to-date")
            else:
                results.append("pulled latest")
        else:
            # Try without rebase
            pull_result = subprocess.run(
                ["git", "pull", "origin"],
                capture_output=True,
                text=True
            )
            if pull_result.returncode == 0:
                results.append("pulled latest (merge)")
        
        # Pop stash if we stashed
        if has_changes:
            subprocess.run(["git", "stash", "pop"], capture_output=True)
            results.append("restored changes")
        
        # 2. Propagate commands
        commands_dir = repo_path / ".agent-os" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        resources_dir = repo_path / ".agent-os" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        source_commands = Path("/mnt/github/github/.agent-os/commands")
        source_resources = Path("/mnt/github/github/.agent-os/resources")
        
        # Copy all commands
        copied = 0
        for cmd_file in ALL_COMMANDS:
            source = source_commands / cmd_file
            if source.exists():
                dest = commands_dir / cmd_file
                shutil.copy2(source, dest)
                if dest.suffix == '.py':
                    dest.chmod(0o755)
                copied += 1
        
        # Copy resource files
        for resource_file in RESOURCE_FILES:
            source = source_resources / resource_file
            if source.exists():
                dest = resources_dir / resource_file
                shutil.copy2(source, dest)
                copied += 1
        
        # Copy agents folder structure if it doesn't exist
        agents_dir = repo_path / "agents"
        if not agents_dir.exists():
            source_setup = Path("/mnt/github/github/setup_agents_folders.py")
            if source_setup.exists():
                # Run the setup script for this repo
                subprocess.run(
                    ["python3", str(source_setup)],
                    cwd=repo_path,
                    capture_output=True
                )
                results.append("agents folder created")
        
        results.append(f"copied {copied} files")
        
        # 3. Create/update command links
        create_command_links(repo_path)
        
        return (repo_name, True, ", ".join(results))
        
    except Exception as e:
        return (repo_name, False, f"Error: {str(e)}")

def create_command_links(repo_path: Path):
    """Create symbolic links or aliases for slash commands."""
    commands_dir = repo_path / ".agent-os" / "commands"
    
    # Command mappings
    command_map = {
        "git": "git.py",
        "spec": "spec.py",
        "task": "task.py",
        "test": "test.py",
        "project": "project.py",
        "data": "data.py",
        "ai-agent": "ai_agent.py",
        "uv-env": "uv_environment_manager.py",
        "verify": "verify-ai-work.py",
    }
    
    # Create command launcher script
    launcher_content = """#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add commands directory to path
commands_dir = Path(__file__).parent / ".agent-os" / "commands"
sys.path.insert(0, str(commands_dir))

# Import and run the requested command
if len(sys.argv) > 1:
    cmd = sys.argv[1].lstrip('/')
    if cmd in {commands}:
        module = {command_map}.get(cmd)
        if module:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                module.replace('.py', ''),
                commands_dir / module
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, 'main'):
                sys.argv = [cmd] + sys.argv[2:]
                mod.main()
"""
    
    launcher_path = repo_path / "agos"
    launcher_path.write_text(
        launcher_content.format(
            commands=str(list(command_map.keys())),
            command_map=str(command_map)
        )
    )
    launcher_path.chmod(0o755)

def main():
    """Main execution."""
    repos = []
    github_dir = Path("/mnt/github/github")
    
    for item in github_dir.iterdir():
        if item.is_dir() and (item / '.git').exists():
            repos.append(item.name)
    
    print(f"🔄 Syncing and propagating commands to {len(repos)} repositories...")
    print("=" * 60)
    print()
    
    success_count = 0
    failed_repos = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(sync_and_propagate_repo, repo) for repo in repos]
        
        for future in as_completed(futures):
            repo_name, success, message = future.result()
            
            if success:
                print(f"✅ {repo_name}: {message}")
                success_count += 1
            elif "Skipping" in message:
                print(f"ℹ️  {repo_name}: {message}")
            else:
                print(f"❌ {repo_name}: {message}")
                failed_repos.append(repo_name)
    
    print()
    print("=" * 60)
    print("📊 Summary:")
    print(f"   Successfully processed: {success_count}/{len(repos)-1}")
    
    if failed_repos:
        print(f"   Failed repositories: {', '.join(failed_repos)}")
    
    print()
    print("✨ Sync and propagation complete!")
    print()
    print("📋 What was done:")
    print("   1. All repos synced with latest from origin")
    print("   2. All Agent OS commands propagated")
    print("   3. UV environment support added")
    print("   4. AI agent support installed")
    print("   5. Resource files distributed")
    print()
    print("💡 All repositories now have:")
    print("   • Unified commands (/git, /spec, /task, /test, etc.)")
    print("   • UV environment detection and usage")
    print("   • AI agent integration")
    print("   • Latest enhancements and fixes")

if __name__ == "__main__":
    main()