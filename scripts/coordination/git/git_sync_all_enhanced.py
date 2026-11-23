#!/usr/bin/env python3
"""
Enhanced Git Sync All - Includes Slash Command Ecosystem Sync
Ensures both git repos AND slash commands are fully synchronized
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class EnhancedGitSyncAll:
    def __init__(self):
        self.base_path = Path("/mnt/github/github")
        self.repos = self.get_all_repos()
        self.results = []
        
    def get_all_repos(self):
        """Get list of all git repositories"""
        repos = []
        for item in self.base_path.iterdir():
            if item.is_dir() and (item / ".git").exists():
                repos.append(item.name)
        return sorted(repos)
    
    def sync_slash_commands(self):
        """Sync the complete slash command ecosystem"""
        print("\n" + "=" * 80)
        print("🚀 STEP 1: Syncing Slash Command Ecosystem")
        print("=" * 80)
        
        sync_script = self.base_path / "sync_slash_command_ecosystem.py"
        if sync_script.exists():
            try:
                result = subprocess.run(
                    ["python3", str(sync_script)],
                    capture_output=True,
                    text=True,
                    cwd=self.base_path
                )
                
                if result.returncode == 0:
                    print("✅ Slash command ecosystem synced successfully!")
                    
                    # Read the master list to show summary
                    master_list = self.base_path / "SLASH_COMMAND_MASTER_LIST.md"
                    if master_list.exists():
                        lines = master_list.read_text().split('\n')
                        for line in lines[:5]:  # Show first few lines
                            if 'Total Commands:' in line:
                                print(f"   {line.strip()}")
                else:
                    print(f"⚠️ Slash command sync had issues: {result.stderr}")
                
                return result.returncode == 0
            except Exception as e:
                print(f"❌ Error syncing slash commands: {e}")
                return False
        else:
            print("⚠️ Slash command sync script not found")
            return False
    
    def git_sync_repo(self, repo_name):
        """Sync a single repository"""
        repo_path = self.base_path / repo_name
        
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            branch = branch_result.stdout.strip() or "main"
            
            # Fetch from origin
            fetch_result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            # Pull latest changes
            pull_result = subprocess.run(
                ["git", "pull", "origin", branch],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            # Check status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            has_changes = bool(status_result.stdout.strip())
            
            return {
                "repo": repo_name,
                "branch": branch,
                "status": "success" if pull_result.returncode == 0 else "failed",
                "has_changes": has_changes,
                "message": pull_result.stdout.strip() if pull_result.returncode == 0 else pull_result.stderr
            }
            
        except Exception as e:
            return {
                "repo": repo_name,
                "status": "error",
                "message": str(e),
                "has_changes": False
            }
    
    def sync_all_repos(self):
        """Sync all repositories in parallel"""
        print("\n" + "=" * 80)
        print("🔄 STEP 2: Syncing All Git Repositories")
        print("=" * 80)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.git_sync_repo, repo): repo for repo in self.repos}
            
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
                
                # Print progress
                if result["status"] == "success":
                    status = "✅" if not result["has_changes"] else "📝"
                    print(f"{status} {result['repo']} ({result['branch']})")
                else:
                    print(f"❌ {result['repo']}: {result.get('message', 'Unknown error')}")
    
    def update_command_registry_in_repos(self):
        """Update command registry in repos that need it"""
        print("\n" + "=" * 80)
        print("📚 STEP 3: Updating Command Registries in Repositories")
        print("=" * 80)
        
        master_registry = self.base_path / ".SLASH_COMMAND_ECOSYSTEM/MASTER_COMMAND_REGISTRY.json"
        
        if not master_registry.exists():
            print("⚠️ Master registry not found")
            return
        
        registry_data = json.loads(master_registry.read_text())
        updated_count = 0
        
        for repo in self.repos:
            repo_path = self.base_path / repo
            
            # Update CLAUDE.md with command list if it exists
            claude_file = repo_path / "CLAUDE.md"
            if claude_file.exists():
                content = claude_file.read_text()
                
                # Check if we need to add a command reference section
                if "COMPLETE SLASH COMMAND LIST" not in content:
                    # Add reference to master list
                    addition = """

## 📚 Complete Slash Command Reference

For the COMPLETE list of all available slash commands across the ecosystem, see:
- Master List: @/mnt/github/github/SLASH_COMMAND_MASTER_LIST.md
- Registry: @/mnt/github/github/.SLASH_COMMAND_ECOSYSTEM/

Total Available Commands: {total}
Last Updated: {timestamp}
""".format(
                        total=registry_data["total_commands"],
                        timestamp=registry_data["last_updated"]
                    )
                    
                    claude_file.write_text(content + addition)
                    updated_count += 1
        
        print(f"✅ Updated {updated_count} repositories with command registry reference")
    
    def generate_summary(self):
        """Generate summary report"""
        print("\n" + "=" * 80)
        print("📊 SYNC SUMMARY")
        print("=" * 80)
        
        # Git sync results
        success_count = sum(1 for r in self.results if r["status"] == "success")
        changed_count = sum(1 for r in self.results if r.get("has_changes"))
        failed_count = sum(1 for r in self.results if r["status"] != "success")
        
        print(f"\n🔄 Git Repositories:")
        print(f"  ✅ Synced: {success_count}/{len(self.repos)}")
        print(f"  📝 With local changes: {changed_count}")
        print(f"  ❌ Failed: {failed_count}")
        
        # Slash commands
        master_list = self.base_path / "SLASH_COMMAND_MASTER_LIST.md"
        if master_list.exists():
            lines = master_list.read_text().split('\n')
            for line in lines[:10]:
                if 'Total Commands:' in line:
                    print(f"\n🚀 Slash Commands:")
                    print(f"  {line.strip()}")
                    break
        
        # Show repos with changes
        if changed_count > 0:
            print(f"\n📝 Repositories with uncommitted changes:")
            for result in self.results:
                if result.get("has_changes"):
                    print(f"  - {result['repo']}")
        
        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "git_sync_results": self.results,
            "total_repos": len(self.repos),
            "success_count": success_count,
            "changed_count": changed_count,
            "failed_count": failed_count
        }
        
        report_file = self.base_path / f"git_sync_all_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def run(self):
        """Execute the complete enhanced sync"""
        print("=" * 80)
        print("🚀 ENHANCED GIT SYNC ALL - With Slash Command Ecosystem")
        print("=" * 80)
        print(f"📁 Base Path: {self.base_path}")
        print(f"📊 Total Repositories: {len(self.repos)}")
        
        # Step 1: Sync slash commands
        slash_sync_success = self.sync_slash_commands()
        
        # Step 2: Sync all git repos
        self.sync_all_repos()
        
        # Step 3: Update command registries
        if slash_sync_success:
            self.update_command_registry_in_repos()
        
        # Generate summary
        self.generate_summary()
        
        print("\n✨ Enhanced sync complete!")
        print("\n💡 Your slash command ecosystem is now fully synchronized!")
        print("   Claude can access the complete list at:")
        print("   - /mnt/github/github/SLASH_COMMAND_MASTER_LIST.md")
        print("   - /mnt/github/github/.SLASH_COMMAND_ECOSYSTEM/")

def main():
    """Main entry point for /git-sync-all command"""
    syncer = EnhancedGitSyncAll()
    syncer.run()

if __name__ == "__main__":
    main()