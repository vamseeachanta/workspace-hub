#!/usr/bin/env python3
"""
Setup all slash commands in the root github folder by copying from existing repositories.
"""
import os
import shutil
import json
from pathlib import Path

def setup_all_commands():
    """Copy all command files from repositories to root .agent-os/commands/"""
    
    root_dir = Path("/mnt/github/github")
    commands_dir = root_dir / ".agent-os" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Read the master command registry to get all commands
    registry_file = root_dir / ".SLASH_COMMAND_ECOSYSTEM" / "MASTER_COMMAND_REGISTRY.json"
    
    # Define command to filename mappings
    command_mappings = {
        # Git commands
        "/git-clean": "git_clean.py",
        "/git-clean-all": "git_clean_all.py",
        "/git-commit": "git_commit.py",
        "/git-commit-all": "git_commit_all.py",
        "/git-flow": "git_flow.py",
        "/git-flow-all": "git_flow_all.py",
        "/git-git_manager": "git_manager.py",
        "/git-pr": "git_pr.py",
        "/git-pr-all": "git_pr_all.py",
        "/git-push": "git_push.py",
        "/git-slash_commands": "git_slash_commands.py",
        "/git-status": "git_status.py",
        "/git-status-all": "git_status_all.py",
        "/git-sync": "git_sync.py",
        "/git-sync-all": "git_sync_all.py",
        "/git-trunk-flow": "git_trunk_flow.py",
        "/github": "github.py",
        
        # Agent OS commands
        "/check-module-boundaries": "check_module_boundaries.py",
        "/create-module-agent": "create_module_agent.py",
        "/create-module-agent-backup-20250810-104956": "create_module_agent_backup_20250810_104956.py",
        "/create-spec": "create_spec.py",
        
        # Development commands
        "/modernize-deps": "modernize_deps.py",
        "/organize-structure": "organize_structure.py",
        "/propagate-commands": "propagate_commands.py",
        
        # Utility commands
        "/analyze-product": "analyze_product.py",
        "/command-name": "command_name.py",
        "/config": "config.py",
        "/docs": "docs.py",
        "/execute-tasks": "execute_tasks.py",
        "/mnt": "mnt.py",
        "/orcaflex-sim": "orcaflex_sim.py",
        "/orcaflex-universal": "orcaflex_universal.py",
        "/path": "path.py",
        "/plan-product": "plan_product.py",
        "/tests": "tests.py",
        "/tools": "tools.py",
        
        # Global commands
        "/install-ecosystem-awareness": "install_ecosystem_awareness.py",
        "/sync-all-commands": "sync_all_commands.py",
    }
    
    # Source repositories to check for commands
    source_repos = [
        "aceengineer-admin",
        "aceengineercode", 
        "aceengineer-website",
        "assetutilities",
        "digitalmodel",
        "achantas-data",
        "OGManufacturing",
        "frontierdeepwater",
        "saipem"
    ]
    
    copied_commands = []
    missing_commands = []
    
    for command, filename in command_mappings.items():
        target_file = commands_dir / filename
        
        # Skip if already exists
        if target_file.exists():
            print(f"✓ {command} already exists as {filename}")
            copied_commands.append(command)
            continue
            
        # Try to find the file in source repositories
        found = False
        for repo in source_repos:
            # Try different possible source paths
            possible_paths = [
                root_dir / repo / ".agent-os" / "commands" / filename,
                root_dir / repo / ".agent-os" / "commands" / filename.replace("_", "-"),
                root_dir / repo / ".agent-os" / "commands" / filename.replace("-", "_"),
                # Try without prefix for git commands
                root_dir / repo / ".agent-os" / "commands" / filename.replace("git_", ""),
            ]
            
            for source_file in possible_paths:
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
                    print(f"✓ Copied {command} from {repo} as {filename}")
                    copied_commands.append(command)
                    found = True
                    break
            
            if found:
                break
        
        if not found:
            # Create a placeholder command file
            create_placeholder_command(target_file, command)
            print(f"⚠ Created placeholder for {command} as {filename}")
            missing_commands.append(command)
    
    # Create the main git.py orchestrator if it doesn't exist
    create_git_orchestrator(commands_dir)
    
    print(f"\n📊 Summary:")
    print(f"   ✓ {len(copied_commands)} commands ready")
    print(f"   ⚠ {len(missing_commands)} placeholder commands created")
    
    if missing_commands:
        print(f"\nPlaceholder commands that need implementation:")
        for cmd in missing_commands:
            print(f"   - {cmd}")
    
    return copied_commands, missing_commands

def create_placeholder_command(filepath, command_name):
    """Create a placeholder command file"""
    content = f'''#!/usr/bin/env python3
"""
Placeholder for {command_name} command.
This command needs to be implemented or copied from a source repository.
"""

import sys
import os

def main():
    print(f"🚧 {command_name} command is not yet implemented")
    print("This is a placeholder that needs to be replaced with the actual implementation.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    filepath.write_text(content)
    os.chmod(filepath, 0o755)

def create_git_orchestrator(commands_dir):
    """Create the main git.py orchestrator that handles all git-* commands"""
    git_py = commands_dir / "git.py"
    
    if not git_py.exists():
        content = '''#!/usr/bin/env python3
"""
Git command orchestrator - Routes git-* slash commands to appropriate handlers.
"""
import sys
import os
import subprocess
from pathlib import Path

def main():
    # Get the command from the first argument
    if len(sys.argv) < 2:
        print("Usage: /git-<subcommand> [args...]")
        print("Available subcommands: status, commit, push, pull, sync, flow, pr, clean")
        return 1
    
    # Extract subcommand from /git-<subcommand>
    command = sys.argv[1]
    if command.startswith("/git-"):
        subcommand = command[5:]  # Remove "/git-" prefix
    else:
        subcommand = command
    
    # Map subcommands to handler files
    command_map = {
        "status": "git_status.py",
        "status-all": "git_status_all.py",
        "commit": "git_commit.py",
        "commit-all": "git_commit_all.py",
        "push": "git_push.py",
        "pull": "git_pull.py",
        "sync": "git_sync.py",
        "sync-all": "git_sync_all.py",
        "flow": "git_flow.py",
        "flow-all": "git_flow_all.py",
        "pr": "git_pr.py",
        "pr-all": "git_pr_all.py",
        "clean": "git_clean.py",
        "clean-all": "git_clean_all.py",
        "trunk-flow": "git_trunk_flow.py",
    }
    
    # Find the handler
    if subcommand in command_map:
        handler_file = Path(__file__).parent / command_map[subcommand]
        if handler_file.exists():
            # Execute the handler
            result = subprocess.run([sys.executable, str(handler_file)] + sys.argv[2:])
            return result.returncode
        else:
            print(f"Handler {command_map[subcommand]} not found for /git-{subcommand}")
            return 1
    else:
        print(f"Unknown git subcommand: {subcommand}")
        print("Available: " + ", ".join(command_map.keys()))
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        git_py.write_text(content)
        os.chmod(git_py, 0o755)
        print("✓ Created git.py orchestrator")

if __name__ == "__main__":
    setup_all_commands()