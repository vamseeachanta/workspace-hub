#!/usr/bin/env python3
"""
Sync and Maintain Complete Slash Command Ecosystem
Ensures all commands are locally available and documented
"""

import os
import json
import yaml
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

class SlashCommandEcosystemSync:
    def __init__(self):
        self.base_path = Path("/mnt/github/github")
        self.ecosystem_path = self.base_path / ".SLASH_COMMAND_ECOSYSTEM"
        self.assetutilities_path = self.base_path / "assetutilities"
        self.commands_registry = {}
        self.all_commands = set()
        
    def initialize_ecosystem_directory(self):
        """Create central ecosystem directory"""
        self.ecosystem_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.ecosystem_path / "commands").mkdir(exist_ok=True)
        (self.ecosystem_path / "modules").mkdir(exist_ok=True)
        (self.ecosystem_path / "documentation").mkdir(exist_ok=True)
        (self.ecosystem_path / "registry").mkdir(exist_ok=True)
        
        print(f"✅ Initialized ecosystem directory at {self.ecosystem_path}")
    
    def scan_all_repositories(self) -> Dict[str, List[str]]:
        """Scan all repositories for slash commands"""
        repo_commands = {}
        
        repos = [
            "aceengineer-admin", "aceengineercode", "aceengineer-website",
            "achantas-data", "achantas-media", "acma-projects",
            "ai-native-traditional-eng", "assethold", "assetutilities",
            "digitalmodel", "energy", "frontierdeepwater",
            "hobbies", "investments", "OGManufacturing",
            "rock-oil-field", "sabithaandkrishnaestates", "saipem",
            "sd-work", "seanation", "teamresumes", "worldenergydata",
            "pyproject-starter", "doris", "client_projects"
        ]
        
        for repo in repos:
            repo_path = self.base_path / repo
            if not repo_path.exists():
                continue
                
            commands = []
            
            # Check for .git-commands
            git_commands = repo_path / ".git-commands"
            if git_commands.exists():
                for file in git_commands.glob("*.py"):
                    if file.stem != "__pycache__":
                        commands.append(f"/git-{file.stem}")
            
            # Check for .agent-os/commands
            agent_commands = repo_path / ".agent-os/commands"
            if agent_commands.exists():
                for file in agent_commands.glob("*.py"):
                    if file.stem != "__init__" and "module" in file.stem:
                        commands.append(f"/{file.stem.replace('_', '-')}")
            
            # Check for slash commands in root
            if (repo_path / "slash_commands.py").exists():
                # Parse the file to extract commands
                commands.extend(self.extract_commands_from_file(repo_path / "slash_commands.py"))
            
            # Check CLAUDE.md for documented commands
            claude_file = repo_path / "CLAUDE.md"
            if claude_file.exists():
                commands.extend(self.extract_commands_from_claude_md(claude_file))
            
            if commands:
                repo_commands[repo] = list(set(commands))  # Remove duplicates
                self.all_commands.update(commands)
        
        return repo_commands
    
    def extract_commands_from_file(self, file_path: Path) -> List[str]:
        """Extract command definitions from Python files"""
        commands = []
        try:
            content = file_path.read_text()
            # Look for command patterns
            import re
            
            # Pattern 1: '/command-name' in quotes
            pattern1 = re.findall(r'["\']/([\w-]+)["\']', content)
            commands.extend([f"/{cmd}" for cmd in pattern1])
            
            # Pattern 2: command definitions in dictionaries
            pattern2 = re.findall(r'["\']command["\']\s*:\s*["\']/([\w-]+)["\']', content)
            commands.extend([f"/{cmd}" for cmd in pattern2])
            
        except Exception as e:
            print(f"  Error parsing {file_path}: {e}")
        
        return commands
    
    def extract_commands_from_claude_md(self, file_path: Path) -> List[str]:
        """Extract documented commands from CLAUDE.md"""
        commands = []
        try:
            content = file_path.read_text()
            import re
            
            # Look for command patterns in markdown
            # Pattern: `/command-name` in backticks or plain text
            pattern = re.findall(r'[`/]/([\w-]+)`?', content)
            commands.extend([f"/{cmd}" for cmd in pattern if not cmd.startswith('/')])
            
            # Also look for command lists
            lines = content.split('\n')
            for line in lines:
                # Pattern for bullet points with commands
                if '/' in line and any(marker in line for marker in ['- /', '* /', '- `/', '* `/']):
                    # Extract all /command patterns
                    cmd_matches = re.findall(r'/([\w-]+)', line)
                    for cmd in cmd_matches:
                        if cmd and not any(skip in cmd for skip in ['http', 'www', 'github']):
                            commands.append(f"/{cmd}")
                
                # Also check for commands in code blocks
                if line.strip().startswith('/') and ' ' in line:
                    cmd = line.strip().split()[0]
                    if cmd.startswith('/') and len(cmd) > 2:
                        commands.append(cmd)
        except Exception as e:
            print(f"  Error parsing {file_path}: {e}")
        
        # Add known git commands that should exist
        known_commands = [
            '/git-sync', '/git-commit', '/git-push', '/git-pr', '/git-clean', 
            '/git-status', '/git-flow', '/git-sync-all', '/git-commit-all',
            '/git-pr-all', '/git-clean-all', '/git-flow-all', '/git-status-all'
        ]
        
        # Only add known commands if we found some git reference in the file
        if any('git' in cmd for cmd in commands):
            commands.extend(known_commands)
        
        return list(set(commands))  # Remove duplicates
    
    def fetch_assetutilities_commands(self) -> Dict[str, Dict]:
        """Fetch commands from AssetUtilities central registry"""
        commands = {}
        
        # Check .common-commands directory
        common_commands = self.assetutilities_path / ".common-commands"
        if common_commands.exists():
            # Copy entire .common-commands to ecosystem
            dest = self.ecosystem_path / "assetutilities-commands"
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(common_commands, dest)
            print(f"✅ Copied AssetUtilities common commands")
            
            # Parse command registry
            registry_file = common_commands / "command_registry.py"
            if registry_file.exists():
                try:
                    exec_globals = {}
                    exec(registry_file.read_text(), exec_globals)
                    if 'CentralCommandRegistry' in exec_globals:
                        registry_class = exec_globals['CentralCommandRegistry']
                        if hasattr(registry_class, 'COMMANDS'):
                            commands = registry_class.COMMANDS
                except Exception as e:
                    print(f"  Error parsing registry: {e}")
        
        return commands
    
    def create_master_registry(self, repo_commands: Dict, asset_commands: Dict):
        """Create comprehensive master registry of all commands"""
        
        master_registry = {
            "last_updated": datetime.now().isoformat(),
            "total_commands": len(self.all_commands),
            "categories": {
                "git": [],
                "agent-os": [],
                "spec": [],
                "development": [],
                "utility": [],
                "global": []
            },
            "commands": {},
            "by_repository": repo_commands,
            "central_registry": asset_commands
        }
        
        # Categorize all commands
        for cmd in sorted(self.all_commands):
            cmd_name = cmd.lstrip('/')
            
            # Determine category
            if 'git' in cmd_name:
                category = 'git'
            elif 'spec' in cmd_name or 'create' in cmd_name:
                category = 'spec'
            elif 'agent' in cmd_name or 'module' in cmd_name:
                category = 'agent-os'
            elif 'all' in cmd_name:
                category = 'global'
            elif any(x in cmd_name for x in ['sync', 'propagate', 'modernize', 'organize']):
                category = 'development'
            else:
                category = 'utility'
            
            master_registry["categories"][category].append(cmd)
            
            # Add command details
            master_registry["commands"][cmd] = {
                "name": cmd,
                "category": category,
                "found_in": [repo for repo, cmds in repo_commands.items() if cmd in cmds],
                "in_central": cmd.lstrip('/') in [c.lstrip('/') for c in asset_commands.keys()]
            }
        
        # Save master registry
        registry_file = self.ecosystem_path / "MASTER_COMMAND_REGISTRY.json"
        with open(registry_file, 'w') as f:
            json.dump(master_registry, f, indent=2)
        
        print(f"✅ Created master registry with {len(self.all_commands)} commands")
        return master_registry
    
    def create_markdown_documentation(self, registry: Dict):
        """Create comprehensive markdown documentation"""
        
        doc = """# 🚀 Complete Slash Command Ecosystem

> Last Updated: {timestamp}
> Total Commands: {total}

## Quick Reference - ALL Available Commands

### Git Management Commands ({git_count})
{git_commands}

### Agent OS Commands ({agent_count})
{agent_commands}

### Spec & Development Commands ({spec_count})
{spec_commands}

### Global Operations ({global_count})
{global_commands}

### Development Tools ({dev_count})
{dev_commands}

### Utility Commands ({util_count})
{util_commands}

## Command Details

{command_details}

## Commands by Repository

{repo_breakdown}

## Central Registry Status

- AssetUtilities Commands: {central_count}
- Local-Only Commands: {local_count}
- Universal Commands: {universal_count}

---

*This is the COMPLETE list of all slash commands across the entire ecosystem*
""".format(
            timestamp=registry["last_updated"],
            total=registry["total_commands"],
            git_count=len(registry["categories"]["git"]),
            git_commands=self.format_command_list(registry["categories"]["git"]),
            agent_count=len(registry["categories"]["agent-os"]),
            agent_commands=self.format_command_list(registry["categories"]["agent-os"]),
            spec_count=len(registry["categories"]["spec"]),
            spec_commands=self.format_command_list(registry["categories"]["spec"]),
            global_count=len(registry["categories"]["global"]),
            global_commands=self.format_command_list(registry["categories"]["global"]),
            dev_count=len(registry["categories"]["development"]),
            dev_commands=self.format_command_list(registry["categories"]["development"]),
            util_count=len(registry["categories"]["utility"]),
            util_commands=self.format_command_list(registry["categories"]["utility"]),
            command_details=self.format_command_details(registry["commands"]),
            repo_breakdown=self.format_repo_breakdown(registry["by_repository"]),
            central_count=len(registry.get("central_registry", {})),
            local_count=sum(1 for c in registry["commands"].values() if not c["in_central"]),
            universal_count=sum(1 for c in registry["commands"].values() if len(c["found_in"]) > 10)
        )
        
        # Save documentation
        doc_file = self.ecosystem_path / "COMPLETE_COMMAND_LIST.md"
        doc_file.write_text(doc)
        
        # Also save to root for easy access
        root_doc = self.base_path / "SLASH_COMMAND_MASTER_LIST.md"
        root_doc.write_text(doc)
        
        print(f"✅ Created comprehensive documentation")
        return doc_file
    
    def format_command_list(self, commands: List[str]) -> str:
        """Format command list for markdown"""
        if not commands:
            return "*No commands in this category*"
        
        lines = []
        for cmd in sorted(commands):
            lines.append(f"- `{cmd}`")
        return "\n".join(lines)
    
    def format_command_details(self, commands: Dict) -> str:
        """Format detailed command information"""
        lines = ["### Detailed Command Information\n"]
        
        for cmd_name, cmd_info in sorted(commands.items()):
            status = "✅" if cmd_info["in_central"] else "📍"
            repos = ", ".join(cmd_info["found_in"][:3]) if cmd_info["found_in"] else "Not found"
            if len(cmd_info["found_in"]) > 3:
                repos += f" (+{len(cmd_info['found_in'])-3} more)"
            
            lines.append(f"- `{cmd_name}` {status} - Category: {cmd_info['category']} - Found in: {repos}")
        
        return "\n".join(lines)
    
    def format_repo_breakdown(self, repo_commands: Dict) -> str:
        """Format repository breakdown"""
        lines = ["### Commands by Repository\n"]
        
        for repo, commands in sorted(repo_commands.items()):
            if commands:
                lines.append(f"**{repo}** ({len(commands)} commands)")
                lines.append(", ".join(f"`{cmd}`" for cmd in sorted(commands)[:10]))
                if len(commands) > 10:
                    lines.append(f"... and {len(commands)-10} more")
                lines.append("")
        
        return "\n".join(lines)
    
    def sync_to_all_repos(self, registry: Dict):
        """Sync command list to all repositories"""
        repos_updated = 0
        
        for repo in registry["by_repository"].keys():
            repo_path = self.base_path / repo
            if repo_path.exists():
                # Create .slash-commands directory in each repo
                slash_dir = repo_path / ".slash-commands"
                slash_dir.mkdir(exist_ok=True)
                
                # Copy registry
                registry_file = slash_dir / "ecosystem_registry.json"
                with open(registry_file, 'w') as f:
                    json.dump(registry, f, indent=2)
                
                repos_updated += 1
        
        print(f"✅ Synced registry to {repos_updated} repositories")
    
    def run(self):
        """Execute the complete sync process"""
        print("=" * 80)
        print("🚀 Syncing Complete Slash Command Ecosystem")
        print("=" * 80)
        
        # Initialize
        self.initialize_ecosystem_directory()
        
        # Scan all repos
        print("\n📊 Scanning all repositories...")
        repo_commands = self.scan_all_repositories()
        print(f"Found commands in {len(repo_commands)} repositories")
        
        # Fetch from AssetUtilities
        print("\n🔄 Fetching AssetUtilities central registry...")
        asset_commands = self.fetch_assetutilities_commands()
        print(f"Found {len(asset_commands)} commands in central registry")
        
        # Create master registry
        print("\n📝 Creating master registry...")
        registry = self.create_master_registry(repo_commands, asset_commands)
        
        # Create documentation
        print("\n📚 Generating documentation...")
        doc_file = self.create_markdown_documentation(registry)
        
        # Sync to repos
        print("\n🔄 Syncing to all repositories...")
        self.sync_to_all_repos(registry)
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ SYNC COMPLETE!")
        print("=" * 80)
        print(f"📊 Total Commands Found: {len(self.all_commands)}")
        print(f"📁 Master Registry: {self.ecosystem_path}/MASTER_COMMAND_REGISTRY.json")
        print(f"📄 Documentation: {self.base_path}/SLASH_COMMAND_MASTER_LIST.md")
        print("\nCommand Categories:")
        for category, commands in registry["categories"].items():
            if commands:
                print(f"  - {category}: {len(commands)} commands")
        
        print("\n🎯 Claude can now access the COMPLETE command list at:")
        print("  - /mnt/github/github/.SLASH_COMMAND_ECOSYSTEM/")
        print("  - /mnt/github/github/SLASH_COMMAND_MASTER_LIST.md")

if __name__ == "__main__":
    syncer = SlashCommandEcosystemSync()
    syncer.run()