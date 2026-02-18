#!/usr/bin/env python3
"""
Copy actual git command implementations from source repositories.
"""
import os
import shutil
from pathlib import Path

def copy_git_commands():
    """Find and copy actual git command implementations"""
    
    root_dir = Path("/mnt/github/github")
    target_dir = root_dir / ".agent-os" / "commands"
    
    # Search for git commands in aceengineer-admin which seems to have them
    source_repo = root_dir / "aceengineer-admin" / ".agent-os" / "commands"
    
    # Map of commands to possible file names in source
    git_commands = {
        "git_clean.py": ["git-clean.py", "git_clean.py"],
        "git_clean_all.py": ["git-clean-all.py", "git_clean_all.py"],
        "git_commit.py": ["git-commit.py", "git_commit.py"],
        "git_commit_all.py": ["git-commit-all.py", "git_commit_all.py", "git-commit-push-merge-all.py"],
        "git_flow.py": ["git-flow.py", "git_flow.py"],
        "git_flow_all.py": ["git-flow-all.py", "git_flow_all.py"],
        "git_pr.py": ["git-pr.py", "git_pr.py"],
        "git_pr_all.py": ["git-pr-all.py", "git_pr_all.py"],
        "git_push.py": ["git-push.py", "git_push.py"],
        "git_status.py": ["git-status.py", "git_status.py", "git-trunk-status.py"],
        "git_status_all.py": ["git-status-all.py", "git_status_all.py"],
        "git_sync_all.py": ["git-sync-all.py", "git_sync_all.py", "git-sync-all-enhanced.py", "git-trunk-sync-all.py"],
    }
    
    copied = []
    not_found = []
    
    # Also check other repos
    repos_to_check = [
        root_dir / "aceengineer-admin" / ".agent-os" / "commands",
        root_dir / "aceengineercode" / ".agent-os" / "commands",
        root_dir / "digitalmodel" / ".agent-os" / "commands",
        root_dir / "assetutilities" / ".agent-os" / "commands",
    ]
    
    for target_name, possible_sources in git_commands.items():
        target_file = target_dir / target_name
        found = False
        
        for repo_path in repos_to_check:
            if not repo_path.exists():
                continue
                
            for source_name in possible_sources:
                source_file = repo_path / source_name
                if source_file.exists():
                    # Copy the file
                    shutil.copy2(source_file, target_file)
                    os.chmod(target_file, 0o755)
                    print(f"✓ Copied {source_name} → {target_name} from {repo_path.parent.parent.name}")
                    copied.append(target_name)
                    found = True
                    break
            
            if found:
                break
        
        if not found:
            not_found.append(target_name)
    
    # Look for other utility commands
    utility_commands = {
        "execute_tasks.py": ["execute_tasks.py", "execute-tasks.py", "execute-tasks-enhanced.py"],
        "analyze_product.py": ["analyze_product.py", "analyze-product.py"],
        "plan_product.py": ["plan_product.py", "plan-product.py"],
        "command_name.py": ["command_name.py", "command-name.py"],
        "config.py": ["config.py"],
        "docs.py": ["docs.py"],
        "tests.py": ["tests.py"],
        "tools.py": ["tools.py"],
        "mnt.py": ["mnt.py"],
        "path.py": ["path.py"],
        "github.py": ["github.py"],
    }
    
    for target_name, possible_sources in utility_commands.items():
        target_file = target_dir / target_name
        
        # Skip if already exists and is not a placeholder
        if target_file.exists():
            content = target_file.read_text()
            if "placeholder" not in content.lower():
                continue
        
        found = False
        for repo_path in repos_to_check:
            if not repo_path.exists():
                continue
                
            for source_name in possible_sources:
                source_file = repo_path / source_name
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
                    os.chmod(target_file, 0o755)
                    print(f"✓ Copied {source_name} → {target_name} from {repo_path.parent.parent.name}")
                    copied.append(target_name)
                    found = True
                    break
            
            if found:
                break
        
        if not found and target_name not in not_found:
            not_found.append(target_name)
    
    print(f"\n📊 Summary:")
    print(f"   ✓ Copied {len(copied)} command implementations")
    if not_found:
        print(f"   ⚠ {len(not_found)} commands still need implementations:")
        for cmd in not_found:
            print(f"      - {cmd}")
    
    return copied, not_found

if __name__ == "__main__":
    copy_git_commands()