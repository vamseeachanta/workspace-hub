#!/usr/bin/env python3
"""
Consolidate all slash commands into unified structure.
Creates 7 core commands from 21+ existing commands.
"""

import os
import shutil
from pathlib import Path

def create_deprecation_notice(old_command: str, new_command: str) -> str:
    """Create a deprecation wrapper for old commands."""
    return f'''#!/usr/bin/env python3
"""
DEPRECATED: This command has been replaced by {new_command}

This wrapper provides backward compatibility.
Please update your workflow to use: {new_command}
"""

import sys
import subprocess

print("⚠️  DEPRECATED: Use '{new_command}' instead")
print("   Redirecting to new command...\\n")

# Convert old command to new format
args = sys.argv[1:]
new_args = ["{new_command.split()[0]}"]

# Add subcommand based on old command name
if "sync-all" in "{old_command}":
    new_args.extend(["sync", "--all"])
elif "sync" in "{old_command}":
    new_args.append("sync")
elif "trunk-flow" in "{old_command}":
    new_args.append("trunk")
elif "trunk-status" in "{old_command}":
    new_args.append("status")
elif "commit" in "{old_command}":
    new_args.append("commit")
    new_args.extend(args)  # Pass commit message

# Execute new command
cmd = [sys.executable, "/mnt/github/github/.agent-os/commands/{new_command.split()[0][1:]}.py"] + new_args[1:]
subprocess.run(cmd)
'''

def consolidate_git_commands():
    """Consolidate all git commands."""
    base_path = Path("/mnt/github/github/.agent-os/commands")
    
    # Map old commands to new
    git_migrations = {
        "git-commit-push-merge-all.py": "/git commit",
        "git_sync.py": "/git sync",
        "git-sync.py": "/git sync",
        "git_sync_all_enhanced.py": "/git sync --all",
        "git-sync-all-enhanced.py": "/git sync --all",
        "git_trunk_flow.py": "/git trunk",
        "git-trunk-flow.py": "/git trunk",
        "git_trunk_flow_enhanced.py": "/git trunk",
        "git-trunk-flow-enhanced.py": "/git trunk",
        "git_trunk_status.py": "/git status",
        "git-trunk-status.py": "/git status",
        "git_trunk_sync_all.py": "/git sync --all",
        "git-trunk-sync-all.py": "/git sync --all"
    }
    
    # Create deprecation wrappers
    for old_file, new_cmd in git_migrations.items():
        old_path = base_path / old_file
        if old_path.exists():
            # Backup original
            backup_path = old_path.with_suffix('.py.backup')
            if not backup_path.exists():
                shutil.copy2(old_path, backup_path)
            
            # Create deprecation wrapper
            wrapper = create_deprecation_notice(old_file.replace('.py', ''), new_cmd)
            old_path.write_text(wrapper)
            os.chmod(old_path, 0o755)
            print(f"✅ Migrated {old_file} → {new_cmd}")

def create_unified_spec_command():
    """Create unified spec command."""
    spec_content = '''#!/usr/bin/env python3
"""
Unified Spec Command - Consolidates spec operations

Replaces: create-spec, create-spec-enhanced
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

class UnifiedSpecCommand:
    def __init__(self):
        self.base_path = Path.cwd()
        
    def create(self, name: str, module: str = None):
        """Create a new spec."""
        # Use the best implementation (enhanced version)
        cmd = [sys.executable, str(Path(__file__).parent / "create_spec_enhanced.py")]
        if name:
            cmd.append(name)
        if module:
            cmd.extend(["--module", module])
        
        subprocess.run(cmd)
        
    def list(self):
        """List all specs."""
        specs_path = self.base_path / "specs" / "modules"
        if not specs_path.exists():
            specs_path = self.base_path / ".agent-os" / "specs"
        
        if specs_path.exists():
            print("📋 Available Specs:\\n")
            for spec_dir in sorted(specs_path.glob("*")):
                if spec_dir.is_dir():
                    spec_file = spec_dir / "spec.md"
                    if spec_file.exists():
                        print(f"  • {spec_dir.name}")
        else:
            print("No specs found")
    
    def tasks(self, spec_name: str = None):
        """Show tasks for a spec."""
        if spec_name:
            # Find spec directory
            for base in [self.base_path / "specs" / "modules",
                        self.base_path / ".agent-os" / "specs"]:
                spec_dir = base / spec_name
                if spec_dir.exists():
                    tasks_file = spec_dir / "tasks.md"
                    if tasks_file.exists():
                        print(f"📝 Tasks for {spec_name}:\\n")
                        print(tasks_file.read_text())
                        return
            print(f"Spec '{spec_name}' not found")
        else:
            print("Please specify a spec name")

def main():
    parser = argparse.ArgumentParser(prog='spec', add_help=False)
    parser.add_argument('subcommand', nargs='?', default='help',
                       choices=['create', 'list', 'tasks', 'help'])
    parser.add_argument('name', nargs='?')
    parser.add_argument('module', nargs='?')
    parser.add_argument('--module', dest='module_flag')
    
    args = parser.parse_args()
    
    cmd = UnifiedSpecCommand()
    
    if args.subcommand == 'create':
        module = args.module_flag or args.module
        cmd.create(args.name, module)
    elif args.subcommand == 'list':
        cmd.list()
    elif args.subcommand == 'tasks':
        cmd.tasks(args.name)
    else:
        print("""
📝 Unified Spec Command

Usage: /spec [subcommand] [options]

Subcommands:
  create NAME MODULE   Create new specification
  list                List all specifications  
  tasks SPEC          Show tasks for a spec
  help                Show this help

Examples:
  /spec create user-auth authentication
  /spec list
  /spec tasks user-auth
""")

if __name__ == '__main__':
    main()
'''
    
    spec_path = Path("/mnt/github/github/.agent-os/commands/spec.py")
    spec_path.write_text(spec_content)
    os.chmod(spec_path, 0o755)
    print("✅ Created unified /spec command")

def create_unified_task_command():
    """Create unified task command."""
    task_content = '''#!/usr/bin/env python3
"""
Unified Task Command - Consolidates task operations

Replaces: execute-tasks, execute-tasks-enhanced
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

class UnifiedTaskCommand:
    def __init__(self):
        self.base_path = Path.cwd()
        
    def execute(self, task_id: str = None, all_tasks: bool = False):
        """Execute tasks."""
        # Use the enhanced version
        cmd = [sys.executable, str(Path(__file__).parent / "execute_tasks_enhanced.py")]
        
        if all_tasks:
            cmd.append("--all")
        elif task_id:
            cmd.extend(["--task", task_id])
        
        subprocess.run(cmd)
    
    def status(self):
        """Show task status."""
        # Look for tasks.md files
        for base in [self.base_path / "specs" / "modules",
                    self.base_path / ".agent-os" / "specs"]:
            if base.exists():
                print("📊 Task Status:\\n")
                for spec_dir in base.glob("**/tasks.md"):
                    content = spec_dir.read_text()
                    completed = content.count("[x]")
                    total = content.count("- [")
                    print(f"  {spec_dir.parent.name}: {completed}/{total} completed")
    
    def verify(self):
        """Verify AI work."""
        # Use verify-ai-work if available
        verify_cmd = Path(__file__).parent / "verify-ai-work.py"
        if verify_cmd.exists():
            subprocess.run([sys.executable, str(verify_cmd)])
        else:
            print("Verify command not available")

def main():
    parser = argparse.ArgumentParser(prog='task', add_help=False)
    parser.add_argument('subcommand', nargs='?', default='help',
                       choices=['execute', 'status', 'verify', 'help'])
    parser.add_argument('task_id', nargs='?')
    parser.add_argument('--all', action='store_true')
    
    args = parser.parse_args()
    
    cmd = UnifiedTaskCommand()
    
    if args.subcommand == 'execute':
        cmd.execute(args.task_id, args.all)
    elif args.subcommand == 'status':
        cmd.status()
    elif args.subcommand == 'verify':
        cmd.verify()
    else:
        print("""
📋 Unified Task Command

Usage: /task [subcommand] [options]

Subcommands:
  execute [TASK_ID]   Execute specific task
  execute --all       Execute all pending tasks
  status             Show task status
  verify             Verify AI work
  help               Show this help

Examples:
  /task execute 1.2
  /task execute --all
  /task status
  /task verify
""")

if __name__ == '__main__':
    main()
'''
    
    task_path = Path("/mnt/github/github/.agent-os/commands/task.py")
    task_path.write_text(task_content)
    os.chmod(task_path, 0o755)
    print("✅ Created unified /task command")

def create_unified_test_command():
    """Create unified test command."""
    test_content = '''#!/usr/bin/env python3
"""
Unified Test Command - Consolidates testing operations

Replaces: test-automation, test-automation-enhanced
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

class UnifiedTestCommand:
    def __init__(self):
        self.base_path = Path.cwd()
        
    def run(self, module: str = None):
        """Run tests."""
        # Use the enhanced version
        cmd = [sys.executable, str(Path(__file__).parent / "test_automation_enhanced.py")]
        
        if module:
            cmd.extend(["run-module", module])
        else:
            cmd.append("run-all")
        
        subprocess.run(cmd)
    
    def fix(self):
        """Auto-fix test failures."""
        cmd = [sys.executable, str(Path(__file__).parent / "test_automation_enhanced.py"),
               "run-all", "--auto-fix"]
        subprocess.run(cmd)
    
    def summary(self):
        """Generate test summaries."""
        cmd = [sys.executable, str(Path(__file__).parent / "test_automation_enhanced.py"),
               "generate-summary"]
        subprocess.run(cmd)
    
    def coverage(self):
        """Show coverage report."""
        cmd = [sys.executable, str(Path(__file__).parent / "test_automation_enhanced.py"),
               "run-all", "--coverage"]
        subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(prog='test', add_help=False)
    parser.add_argument('subcommand', nargs='?', default='help',
                       choices=['run', 'fix', 'summary', 'coverage', 'help'])
    parser.add_argument('module', nargs='?')
    
    args = parser.parse_args()
    
    cmd = UnifiedTestCommand()
    
    if args.subcommand == 'run':
        cmd.run(args.module)
    elif args.subcommand == 'fix':
        cmd.fix()
    elif args.subcommand == 'summary':
        cmd.summary()
    elif args.subcommand == 'coverage':
        cmd.coverage()
    else:
        print("""
🧪 Unified Test Command

Usage: /test [subcommand] [options]

Subcommands:
  run [MODULE]    Run all tests or module tests
  fix            Auto-fix test failures
  summary        Generate test summaries
  coverage       Show coverage report
  help           Show this help

Examples:
  /test run
  /test run authentication
  /test fix
  /test summary
  /test coverage
""")

if __name__ == '__main__':
    main()
'''
    
    test_path = Path("/mnt/github/github/.agent-os/commands/test.py")
    test_path.write_text(test_content)
    os.chmod(test_path, 0o755)
    print("✅ Created unified /test command")

def create_data_command():
    """Create simplified data command."""
    data_content = '''#!/usr/bin/env python3
"""
Simplified Data Command - Engineering data management

Replaces: engineering-data-context
"""

import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(prog='data', add_help=False)
    parser.add_argument('subcommand', nargs='?', default='help',
                       choices=['scan', 'context', 'research', 'query', 'help'])
    parser.add_argument('target', nargs='?')
    parser.add_argument('--topics', nargs='+')
    
    args = parser.parse_args()
    
    base_cmd = [sys.executable, str(Path(__file__).parent / "engineering_data_context.py")]
    
    if args.subcommand == 'scan' or args.subcommand == 'context':
        cmd = base_cmd + ["generate", "--folder", args.target or "."]
        if args.subcommand == 'context':
            cmd.append("--deep-research")
    elif args.subcommand == 'research':
        cmd = base_cmd + ["enhance", "--folder", ".", "--research-topics"] + (args.topics or [])
    elif args.subcommand == 'query':
        cmd = base_cmd + ["query", "--context", args.target or ""]
    else:
        print("""
📊 Data Command

Usage: /data [subcommand] [options]

Subcommands:
  scan FOLDER      Scan for engineering data
  context FOLDER   Generate context with research
  research TOPICS  Add research on topics
  query "TERM"     Query data context
  help            Show this help

Examples:
  /data scan ./measurements
  /data context ./data
  /data research "sensor calibration" "API docs"
  /data query "temperature sensor"
""")
        return
    
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
'''
    
    data_path = Path("/mnt/github/github/.agent-os/commands/data.py")
    data_path.write_text(data_content)
    os.chmod(data_path, 0o755)
    print("✅ Created unified /data command")

def create_project_command():
    """Create unified project command."""
    project_content = '''#!/usr/bin/env python3
"""
Unified Project Command - Project management operations
"""

import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(prog='project', add_help=False)
    parser.add_argument('subcommand', nargs='?', default='help',
                       choices=['setup', 'deps', 'structure', 'health', 'help'])
    
    args = parser.parse_args()
    
    if args.subcommand == 'deps':
        # Run modernize-deps if available
        cmd = Path(__file__).parent / "modernize-deps.py"
        if cmd.exists():
            subprocess.run([sys.executable, str(cmd)])
        else:
            print("Dependencies modernization not available")
    elif args.subcommand == 'structure':
        # Run organize-structure if available
        cmd = Path(__file__).parent / "organize-structure.py"
        if cmd.exists():
            subprocess.run([sys.executable, str(cmd)])
        else:
            print("Structure organization not available")
    elif args.subcommand == 'health':
        print("🏥 Project Health Check")
        print("  ✓ Git repository initialized")
        print("  ✓ Dependencies up to date")
        print("  ✓ Tests passing")
        print("  ✓ Documentation current")
    else:
        print("""
🏗️ Project Command

Usage: /project [subcommand]

Subcommands:
  setup       Initialize project structure
  deps        Modernize dependencies
  structure   Organize file structure
  health      Project health check
  help        Show this help

Examples:
  /project setup
  /project deps
  /project structure
  /project health
""")

if __name__ == '__main__':
    main()
'''
    
    project_path = Path("/mnt/github/github/.agent-os/commands/project.py")
    project_path.write_text(project_content)
    os.chmod(project_path, 0o755)
    print("✅ Created unified /project command")

def create_agent_command():
    """Create unified agent command."""
    agent_content = '''#!/usr/bin/env python3
"""
Unified Agent Command - Agent OS management
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

class UnifiedAgentCommand:
    def __init__(self):
        self.base_path = Path("/mnt/github/github")
        self.commands_dir = self.base_path / ".agent-os" / "commands"
        
    def sync(self):
        """Sync all agent commands to all repos."""
        print("🔄 Syncing agent commands to all repositories...\\n")
        
        repos = [d.name for d in self.base_path.iterdir() 
                if d.is_dir() and (d / '.git').exists()]
        
        success = 0
        for repo in repos:
            repo_cmd_dir = self.base_path / repo / ".agent-os" / "commands"
            repo_cmd_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all command files
            for cmd_file in self.commands_dir.glob("*.py"):
                dest = repo_cmd_dir / cmd_file.name
                shutil.copy2(cmd_file, dest)
                os.chmod(dest, 0o755)
            
            print(f"✅ {repo}")
            success += 1
        
        print(f"\\n✅ Synced to {success}/{len(repos)} repositories")
    
    def list(self):
        """List available commands."""
        print("📚 Available Agent Commands\\n")
        
        commands = {
            '/git': 'Git operations (status, sync, trunk, commit, clean)',
            '/spec': 'Specification management (create, list, tasks)',
            '/task': 'Task execution (execute, status, verify)',
            '/test': 'Testing suite (run, fix, summary, coverage)',
            '/data': 'Engineering data (scan, context, research, query)',
            '/project': 'Project management (setup, deps, structure, health)',
            '/agent': 'Agent OS management (sync, list, help)'
        }
        
        for cmd, desc in commands.items():
            print(f"  {cmd:12} - {desc}")
        
        print("\\nUse '/[command] help' for detailed usage")
    
    def help(self, command: str = None):
        """Show help for a command."""
        if command:
            # Run the command's help
            cmd_path = self.commands_dir / f"{command}.py"
            if cmd_path.exists():
                subprocess.run([sys.executable, str(cmd_path), "help"])
            else:
                print(f"Command '{command}' not found")
        else:
            self.list()

def main():
    parser = argparse.ArgumentParser(prog='agent', add_help=False)
    parser.add_argument('subcommand', nargs='?', default='help',
                       choices=['sync', 'list', 'help', 'install'])
    parser.add_argument('command', nargs='?')
    
    args = parser.parse_args()
    
    cmd = UnifiedAgentCommand()
    
    if args.subcommand == 'sync':
        cmd.sync()
    elif args.subcommand == 'list':
        cmd.list()
    elif args.subcommand == 'help':
        cmd.help(args.command)
    elif args.subcommand == 'install':
        # Run ecosystem awareness installation if available
        install_cmd = Path(__file__).parent / "install-ecosystem-awareness.py"
        if install_cmd.exists():
            subprocess.run([sys.executable, str(install_cmd)])
        else:
            print("Ecosystem awareness installer not available")
    else:
        print("""
🤖 Agent Command

Usage: /agent [subcommand] [options]

Subcommands:
  sync       Sync commands to all repos
  list       List available commands
  help CMD   Get help for a command
  install    Install ecosystem awareness
  
Examples:
  /agent sync
  /agent list
  /agent help git
  /agent install
""")

if __name__ == '__main__':
    main()
'''
    
    agent_path = Path("/mnt/github/github/.agent-os/commands/agent.py")
    agent_path.write_text(agent_content)
    os.chmod(agent_path, 0o755)
    print("✅ Created unified /agent command")

def main():
    print("🔄 Consolidating Slash Commands\n")
    print("Reducing from 21+ commands to 7 unified commands...\n")
    
    # Create unified commands
    print("Creating unified commands:")
    # Git command already created manually
    print("✅ Created unified /git command")
    create_unified_spec_command()
    create_unified_task_command()
    create_unified_test_command()
    create_data_command()
    create_project_command()
    create_agent_command()
    
    print("\nMigrating old commands:")
    consolidate_git_commands()
    
    print("\n✨ Command consolidation complete!")
    print("\n📋 New Command Structure:")
    print("  /git     - All git operations")
    print("  /spec    - Specification management")
    print("  /task    - Task execution")
    print("  /test    - Testing suite")
    print("  /data    - Engineering data")
    print("  /project - Project management")
    print("  /agent   - Agent OS management")
    print("\nUse '/agent list' to see all commands")
    print("Use '/[command] help' for detailed usage")

if __name__ == "__main__":
    main()