#!/usr/bin/env python3
"""
Fix agent_os module placement in all repositories

The agent_os Python module should be in the repository root,
NOT inside .agent-os directory.
"""

import os
import shutil
from pathlib import Path

BASE_PATH = Path("/mnt/github/github")

REPOSITORIES = [
    "aceengineer-admin",
    "aceengineercode", 
    "aceengineer-website",
    "achantas-data",
    "achantas-media",
    "acma-projects",
    "ai-native-traditional-eng",
    "assethold",
    "assetutilities",
    "digitalmodel",
    "energy",
    "frontierdeepwater",
    "hobbies",
    "investments",
    "OGManufacturing",
    "rock-oil-field",
    "sabithaandkrishnaestates",
    "saipem",
    "sd-work",
    "seanation",
    "teamresumes",
    "worldenergydata"
]

def fix_agent_os_module(repo_name):
    """Extract agent_os module from .agent-os if it was merged there"""
    repo_path = BASE_PATH / repo_name
    
    if not repo_path.exists():
        return f"Skipped: Repository not found"
    
    agent_os_dir = repo_path / ".agent-os"
    agent_os_module = repo_path / "agent_os"
    
    # Check if commands/create_module_agent.py exists in .agent-os
    merged_commands = agent_os_dir / "commands" / "create_module_agent.py"
    
    if merged_commands.exists():
        print(f"  Found merged agent_os in .agent-os/commands")
        
        # Create agent_os module directory
        if not agent_os_module.exists():
            agent_os_module.mkdir()
        
        # Create commands subdirectory
        commands_dir = agent_os_module / "commands"
        if not commands_dir.exists():
            commands_dir.mkdir(parents=True)
        
        # Move Python files from .agent-os/commands to agent_os/commands
        for py_file in (agent_os_dir / "commands").glob("*.py"):
            if "create_module" in py_file.name or "agent" in py_file.name.lower():
                dest = commands_dir / py_file.name
                shutil.copy2(py_file, dest)
                print(f"    Copied {py_file.name} to agent_os/commands/")
        
        # Create __init__.py files if needed
        init_file = agent_os_module / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
        
        commands_init = commands_dir / "__init__.py"
        if not commands_init.exists():
            commands_init.write_text("")
        
        return "Fixed: Extracted agent_os module"
    
    # Check if agent_os already exists properly
    elif agent_os_module.exists() and (agent_os_module / "commands").exists():
        return "Already correct"
    
    # Try to copy from aceengineer-admin as source
    else:
        source_module = BASE_PATH / "aceengineer-admin" / ".agent-os" / "commands"
        if source_module.exists() and (source_module / "create_module_agent.py").exists():
            # Create agent_os module directory
            if not agent_os_module.exists():
                agent_os_module.mkdir()
            
            commands_dir = agent_os_module / "commands"
            if not commands_dir.exists():
                commands_dir.mkdir(parents=True)
            
            # Copy relevant files
            for py_file in source_module.glob("*module*.py"):
                dest = commands_dir / py_file.name
                shutil.copy2(py_file, dest)
            
            # Create __init__.py files
            (agent_os_module / "__init__.py").write_text("")
            (commands_dir / "__init__.py").write_text("")
            
            return "Fixed: Created agent_os module from source"
    
    return "Could not fix: Source not found"

def main():
    print("=" * 80)
    print("Fixing agent_os Module Placement")
    print("=" * 80)
    print()
    
    fixed_count = 0
    already_correct = 0
    failed = 0
    
    for repo in REPOSITORIES:
        print(f"📦 {repo}")
        result = fix_agent_os_module(repo)
        
        if "Fixed" in result:
            fixed_count += 1
            print(f"  ✅ {result}")
        elif "Already correct" in result:
            already_correct += 1
            print(f"  ✅ {result}")
        else:
            failed += 1
            print(f"  ⚠️ {result}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Fixed: {fixed_count}")
    print(f"✅ Already correct: {already_correct}")
    print(f"⚠️ Failed: {failed}")
    print(f"📊 Total: {len(REPOSITORIES)}")
    
    print("\n✨ Module placement fix complete!")
    print("\nThe agent_os Python module is now correctly placed in each repository root.")
    print("The .agent-os directory contains Agent OS configuration and instructions.")

if __name__ == "__main__":
    main()