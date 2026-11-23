#!/usr/bin/env python3
"""List all available slash commands in the ecosystem."""

import os
from pathlib import Path

def find_slash_commands():
    """Find all valid slash commands."""
    commands = set()
    
    # Check .agent-os/commands directory
    agent_os_dir = Path("/mnt/github/github/.agent-os/commands")
    if agent_os_dir.exists():
        for file in agent_os_dir.glob("*.py"):
            if not file.name.startswith("__"):
                # Read first few lines to check if it's a slash command
                try:
                    with open(file, 'r') as f:
                        content = f.read(500)
                        if 'slash command' in content.lower() or '/execute' in content or '/git' in content or '/create' in content:
                            cmd_name = file.stem.replace('_', '-')
                            commands.add(f"/{cmd_name}")
                except:
                    pass
    
    # Check digitalmodel directory
    dm_dir = Path("/mnt/github/github/digitalmodel")
    if dm_dir.exists():
        for file in dm_dir.glob("*.py"):
            if 'spec' in file.name or 'execute' in file.name or 'slash' in file.name:
                if not file.name.startswith("__"):
                    cmd_name = file.stem.replace('_', '-')
                    commands.add(f"/{cmd_name}")
    
    # Check for command registry or documentation
    for repo_dir in Path("/mnt/github/github").iterdir():
        if repo_dir.is_dir() and (repo_dir / ".agent-os/commands").exists():
            cmd_dir = repo_dir / ".agent-os/commands"
            for file in cmd_dir.glob("*.py"):
                if not file.name.startswith("__"):
                    cmd_name = file.stem.replace('_', '-')
                    commands.add(f"/{cmd_name}")
    
    return sorted(list(commands))

# Find and display commands
commands = find_slash_commands()

print("📚 ALL AVAILABLE SLASH COMMANDS")
print("=" * 50)
print(f"Total: {len(commands)} commands\n")

# Group by category
git_cmds = [c for c in commands if 'git' in c]
spec_cmds = [c for c in commands if 'spec' in c or 'create' in c]
exec_cmds = [c for c in commands if 'execute' in c or 'task' in c]
test_cmds = [c for c in commands if 'test' in c]
other_cmds = [c for c in commands if c not in git_cmds + spec_cmds + exec_cmds + test_cmds]

if git_cmds:
    print("🔧 Git Management:")
    for cmd in git_cmds:
        print(f"  {cmd}")
    print()

if spec_cmds:
    print("📝 Specifications:")
    for cmd in spec_cmds:
        print(f"  {cmd}")
    print()

if exec_cmds:
    print("🚀 Task Execution:")
    for cmd in exec_cmds:
        print(f"  {cmd}")
    print()

if test_cmds:
    print("🧪 Testing:")
    for cmd in test_cmds:
        print(f"  {cmd}")
    print()

if other_cmds:
    print("🌐 Other Commands:")
    for cmd in other_cmds:
        print(f"  {cmd}")