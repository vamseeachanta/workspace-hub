#!/usr/bin/env python3
"""
Sync AI resources to all repositories.
"""

import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def sync_resources_to_repo(repo_name: str) -> tuple:
    """Sync resources to a single repository."""
    try:
        source_dir = Path("/mnt/github/github/.agent-os/resources")
        repo_path = Path(f"/mnt/github/github/{repo_name}")
        
        if not repo_path.exists():
            return (repo_name, False, "Repository not found")
        
        # Create resources directory
        dest_dir = repo_path / ".agent-os" / "resources"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all resource files
        for file in source_dir.glob("*"):
            if file.is_file():
                shutil.copy2(file, dest_dir / file.name)
        
        return (repo_name, True, "Resources synced")
        
    except Exception as e:
        return (repo_name, False, str(e))

def main():
    repos = [d.name for d in Path("/mnt/github/github").iterdir() 
             if d.is_dir() and (d / '.git').exists()]
    
    print(f"📚 Syncing AI resources to {len(repos)} repositories...\n")
    
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(sync_resources_to_repo, repo) for repo in repos]
        
        for future in as_completed(futures):
            repo_name, success, message = future.result()
            
            if success:
                print(f"✅ {repo_name}")
                success_count += 1
            else:
                print(f"❌ {repo_name}: {message}")
    
    print(f"\n✅ Resources synced to {success_count}/{len(repos)} repositories")

if __name__ == "__main__":
    main()