#!/usr/bin/env python3
"""
Propagate the updated git.py command with documentation generation to all repos.
"""

import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def propagate_to_repo(repo_name: str) -> tuple:
    """Copy updated git.py to a repository."""
    try:
        if repo_name == "github":
            return (repo_name, False, "Skipping source repo")
            
        repo_path = Path(f"/mnt/github/github/{repo_name}")
        if not repo_path.exists():
            return (repo_name, False, "Repository not found")
        
        # Create commands directory if needed
        commands_dir = repo_path / ".agent-os" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy updated git.py
        source = Path("/mnt/github/github/.agent-os/commands/git.py")
        dest = commands_dir / "git.py"
        shutil.copy2(source, dest)
        dest.chmod(0o755)
        
        return (repo_name, True, "Updated git.py with doc generation")
        
    except Exception as e:
        return (repo_name, False, str(e))

def main():
    """Propagate updated git command to all repos."""
    repos = []
    github_dir = Path("/mnt/github/github")
    
    for item in github_dir.iterdir():
        if item.is_dir() and (item / '.git').exists():
            repos.append(item.name)
    
    print("📦 Propagating updated git.py command to all repositories...")
    print("=" * 60)
    
    success_count = 0
    failed_repos = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(propagate_to_repo, repo) for repo in repos]
        
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
    print(f"📊 Summary: {success_count} repositories updated")
    
    if failed_repos:
        print(f"   Failed: {', '.join(failed_repos)}")
    
    print()
    print("✨ Updated git.py command features:")
    print("   • Automatic documentation generation")
    print("   • Documentation distribution to all repos")
    print("   • Commands matrix always up-to-date")
    print("   • Triggered by: /git sync --all")
    print()
    print("📚 Documentation locations in each repo:")
    print("   • AGENT_OS_COMMANDS.md (root)")
    print("   • .agent-os/docs/COMMANDS_MATRIX.md")

if __name__ == "__main__":
    main()