#!/usr/bin/env python3
"""
Clean all repositories to ensure consistent trunk-based development.
Merges all branches to master/main and removes stale branches.
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
import concurrent.futures
from typing import Dict, List, Tuple

class TrunkCleaner:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.results = []
        self.max_workers = 5  # Process 5 repos in parallel
        
    def get_all_repos(self) -> List[Path]:
        """Get all git repositories in workspace."""
        repos = []
        for item in self.workspace.iterdir():
            if item.is_dir() and (item / '.git').exists():
                repos.append(item)
        return sorted(repos)
    
    def run_git_command(self, repo: Path, command: str) -> Tuple[bool, str]:
        """Run a git command in the repository."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def get_default_branch(self, repo: Path) -> str:
        """Determine if repo uses main or master."""
        success, output = self.run_git_command(repo, "git branch -r")
        if "origin/main" in output:
            return "main"
        return "master"
    
    def clean_repository(self, repo: Path) -> Dict:
        """Clean a single repository."""
        repo_name = repo.name
        result = {
            'repo': repo_name,
            'status': 'pending',
            'default_branch': '',
            'branches_merged': [],
            'branches_deleted_local': [],
            'branches_deleted_remote': [],
            'errors': []
        }
        
        print(f"\n{'='*60}")
        print(f"🔧 Processing: {repo_name}")
        print(f"{'='*60}")
        
        try:
            # Fetch all remote branches
            print(f"  📡 Fetching remote branches...")
            success, output = self.run_git_command(repo, "git fetch --all --prune")
            if not success:
                result['errors'].append(f"Failed to fetch: {output}")
                
            # Determine default branch
            default_branch = self.get_default_branch(repo)
            result['default_branch'] = default_branch
            print(f"  🎯 Default branch: {default_branch}")
            
            # Checkout and update default branch
            print(f"  📥 Updating {default_branch}...")
            self.run_git_command(repo, f"git checkout {default_branch}")
            self.run_git_command(repo, f"git pull origin {default_branch}")
            
            # Get all local branches
            success, output = self.run_git_command(repo, "git branch")
            local_branches = [b.strip().replace('* ', '') for b in output.strip().split('\n') if b.strip()]
            local_branches = [b for b in local_branches if b != default_branch]
            
            # Get all remote branches
            success, output = self.run_git_command(repo, "git branch -r")
            remote_branches = [b.strip() for b in output.strip().split('\n') if b.strip()]
            remote_branches = [b.replace('origin/', '') for b in remote_branches 
                             if 'origin/' in b and '->' not in b and b.split('/')[-1] != default_branch]
            
            print(f"  📊 Found {len(local_branches)} local branches, {len(remote_branches)} remote branches")
            
            # Merge each branch to default branch
            for branch in set(local_branches + remote_branches):
                if branch == default_branch:
                    continue
                    
                print(f"  🔀 Merging {branch} to {default_branch}...")
                
                # Checkout branch
                if branch in local_branches:
                    success, _ = self.run_git_command(repo, f"git checkout {branch}")
                else:
                    success, _ = self.run_git_command(repo, f"git checkout -b {branch} origin/{branch}")
                
                if success:
                    # Pull latest changes
                    self.run_git_command(repo, f"git pull origin {branch} 2>/dev/null")
                    
                    # Switch back to default branch and merge
                    self.run_git_command(repo, f"git checkout {default_branch}")
                    success, output = self.run_git_command(repo, f"git merge {branch} --no-edit")
                    
                    if success:
                        result['branches_merged'].append(branch)
                        print(f"    ✅ Merged {branch}")
                        
                        # Push the merge
                        self.run_git_command(repo, f"git push origin {default_branch}")
                    else:
                        # Try to abort merge if it failed
                        self.run_git_command(repo, "git merge --abort 2>/dev/null")
                        print(f"    ⚠️ Could not merge {branch} (conflicts or already merged)")
            
            # Delete merged local branches
            print(f"  🗑️ Cleaning local branches...")
            self.run_git_command(repo, f"git checkout {default_branch}")
            
            for branch in local_branches:
                # Check if branch is fully merged
                success, output = self.run_git_command(repo, f"git branch --merged {default_branch}")
                if branch in output or branch in result['branches_merged']:
                    success, _ = self.run_git_command(repo, f"git branch -d {branch}")
                    if success:
                        result['branches_deleted_local'].append(branch)
                        print(f"    🗑️ Deleted local branch: {branch}")
                    else:
                        # Force delete if regular delete fails
                        success, _ = self.run_git_command(repo, f"git branch -D {branch}")
                        if success:
                            result['branches_deleted_local'].append(branch)
                            print(f"    🗑️ Force deleted local branch: {branch}")
            
            # Delete merged remote branches
            print(f"  🌐 Cleaning remote branches...")
            for branch in remote_branches:
                if branch in result['branches_merged'] or branch in ['HEAD']:
                    continue
                    
                # Check if branch is merged
                success, output = self.run_git_command(repo, f"git branch -r --merged origin/{default_branch}")
                if f"origin/{branch}" in output:
                    success, _ = self.run_git_command(repo, f"git push origin --delete {branch}")
                    if success:
                        result['branches_deleted_remote'].append(branch)
                        print(f"    🌐 Deleted remote branch: {branch}")
                    else:
                        print(f"    ⚠️ Could not delete remote branch: {branch}")
            
            # Final cleanup
            print(f"  🧹 Final cleanup...")
            self.run_git_command(repo, "git remote prune origin")
            self.run_git_command(repo, "git gc --aggressive --prune=now")
            
            # Verify clean state
            success, output = self.run_git_command(repo, "git status --porcelain")
            if not output.strip():
                result['status'] = 'clean'
                print(f"  ✅ Repository is clean and on {default_branch}")
            else:
                result['status'] = 'has_changes'
                print(f"  ⚠️ Repository has uncommitted changes")
                
        except Exception as e:
            result['errors'].append(str(e))
            result['status'] = 'error'
            print(f"  ❌ Error: {e}")
        
        return result
    
    def clean_all_repos(self):
        """Clean all repositories in parallel."""
        repos = self.get_all_repos()
        
        print(f"\n🚀 Cleaning {len(repos)} repositories for trunk-based development")
        print(f"{'='*60}\n")
        
        # Process repos in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_repo = {executor.submit(self.clean_repository, repo): repo for repo in repos}
            
            for future in concurrent.futures.as_completed(future_to_repo):
                repo = future_to_repo[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    print(f"❌ Failed to process {repo.name}: {e}")
                    self.results.append({
                        'repo': repo.name,
                        'status': 'error',
                        'errors': [str(e)]
                    })
        
        self.generate_report()
    
    def generate_report(self):
        """Generate a summary report."""
        print(f"\n{'='*60}")
        print("📊 TRUNK CLEANUP SUMMARY")
        print(f"{'='*60}\n")
        
        total_repos = len(self.results)
        clean_repos = sum(1 for r in self.results if r['status'] == 'clean')
        repos_with_changes = sum(1 for r in self.results if r['status'] == 'has_changes')
        error_repos = sum(1 for r in self.results if r['status'] == 'error')
        
        total_merged = sum(len(r.get('branches_merged', [])) for r in self.results)
        total_deleted_local = sum(len(r.get('branches_deleted_local', [])) for r in self.results)
        total_deleted_remote = sum(len(r.get('branches_deleted_remote', [])) for r in self.results)
        
        print(f"📈 Repository Status:")
        print(f"  ✅ Clean: {clean_repos}/{total_repos}")
        print(f"  ⚠️ Has uncommitted changes: {repos_with_changes}/{total_repos}")
        print(f"  ❌ Errors: {error_repos}/{total_repos}")
        
        print(f"\n🔀 Branch Operations:")
        print(f"  📥 Branches merged: {total_merged}")
        print(f"  🗑️ Local branches deleted: {total_deleted_local}")
        print(f"  🌐 Remote branches deleted: {total_deleted_remote}")
        
        print(f"\n📋 Repository Details:")
        for result in sorted(self.results, key=lambda x: x['repo']):
            status_icon = {
                'clean': '✅',
                'has_changes': '⚠️',
                'error': '❌',
                'pending': '⏳'
            }.get(result['status'], '❓')
            
            branch = result.get('default_branch', 'unknown')
            merged = len(result.get('branches_merged', []))
            deleted = len(result.get('branches_deleted_local', [])) + len(result.get('branches_deleted_remote', []))
            
            print(f"  {status_icon} {result['repo']}: {branch} (merged: {merged}, deleted: {deleted})")
            
            if result.get('errors'):
                for error in result['errors']:
                    print(f"     ❌ {error}")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.workspace / f"trunk_cleanup_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'summary': {
                    'total_repos': total_repos,
                    'clean_repos': clean_repos,
                    'repos_with_changes': repos_with_changes,
                    'error_repos': error_repos,
                    'branches_merged': total_merged,
                    'branches_deleted_local': total_deleted_local,
                    'branches_deleted_remote': total_deleted_remote
                },
                'details': self.results
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        print(f"\n✨ Trunk cleanup complete! All repositories are now following trunk-based development.")

def main():
    workspace = Path("/mnt/github/github")
    cleaner = TrunkCleaner(workspace)
    cleaner.clean_all_repos()

if __name__ == "__main__":
    main()