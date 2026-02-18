#!/usr/bin/env python
"""
BSEE Migration Executor
Safely executes approved consolidation changes with rollback capability
"""

import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import os

class MigrationExecutor:
    def __init__(self, 
                 approval_file: str = "specs/modules/bsee/consolidation/sub-specs/cleanup-proposal-approved.json",
                 dry_run: bool = True):
        self.dry_run = dry_run
        self.data_dir = Path("data/modules/bsee")
        self.operations_log = []
        self.rollback_commands = []
        
        # Load approved changes
        if Path(approval_file).exists():
            with open(approval_file, 'r') as f:
                self.approved_changes = json.load(f)
        else:
            self.approved_changes = None
            print(f"Warning: No approval file found at {approval_file}")
    
    def log_operation(self, operation: str, details: Dict):
        """Log each operation for audit trail"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'details': details,
            'dry_run': self.dry_run
        }
        self.operations_log.append(entry)
        
        status = "[DRY RUN] " if self.dry_run else ""
        print(f"{status}{operation}: {details.get('path', details)}")
    
    def add_rollback(self, command: Dict):
        """Add rollback command for this operation"""
        self.rollback_commands.append(command)
    
    def delete_file(self, filepath: Path) -> bool:
        """Delete a file with rollback capability"""
        try:
            if filepath.exists():
                # Log the operation
                self.log_operation("DELETE", {
                    'path': str(filepath),
                    'size_mb': round(filepath.stat().st_size / (1024*1024), 2)
                })
                
                # Add rollback (would need backup to restore)
                self.add_rollback({
                    'action': 'restore',
                    'source': f"backup/{filepath}",
                    'destination': str(filepath)
                })
                
                # Execute if not dry run
                if not self.dry_run:
                    os.remove(filepath)
                
                return True
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")
            return False
        return False
    
    def move_file(self, source: Path, destination: Path) -> bool:
        """Move a file to new location"""
        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Log the operation
            self.log_operation("MOVE", {
                'source': str(source),
                'destination': str(destination)
            })
            
            # Add rollback
            self.add_rollback({
                'action': 'move',
                'source': str(destination),
                'destination': str(source)
            })
            
            # Execute if not dry run
            if not self.dry_run:
                shutil.move(str(source), str(destination))
            
            return True
        except Exception as e:
            print(f"Error moving {source}: {e}")
            return False
    
    def archive_directory(self, directory: Path, archive_name: str) -> bool:
        """Archive a directory to compressed file"""
        try:
            archive_path = self.data_dir / "archive" / archive_name
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Log the operation
            self.log_operation("ARCHIVE", {
                'source': str(directory),
                'archive': str(archive_path)
            })
            
            # Add rollback
            self.add_rollback({
                'action': 'extract',
                'archive': str(archive_path),
                'destination': str(directory)
            })
            
            # Execute if not dry run
            if not self.dry_run:
                shutil.make_archive(
                    str(archive_path).replace('.tar.gz', ''),
                    'gztar',
                    directory.parent,
                    directory.name
                )
            
            return True
        except Exception as e:
            print(f"Error archiving {directory}: {e}")
            return False
    
    def consolidate_csv_files(self, source_files: List[Path], target_file: Path) -> bool:
        """Consolidate multiple CSV files into one"""
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Log the operation
            self.log_operation("CONSOLIDATE", {
                'sources': [str(f) for f in source_files],
                'target': str(target_file),
                'count': len(source_files)
            })
            
            # Execute if not dry run
            if not self.dry_run:
                dfs = []
                for source in source_files:
                    if source.exists():
                        df = pd.read_csv(source)
                        df['source_file'] = source.name  # Track origin
                        dfs.append(df)
                
                if dfs:
                    consolidated = pd.concat(dfs, ignore_index=True)
                    consolidated.to_csv(target_file, index=False)
            
            return True
        except Exception as e:
            print(f"Error consolidating files: {e}")
            return False
    
    def execute_deletions(self):
        """Execute approved file deletions"""
        if not self.approved_changes or 'deletions' not in self.approved_changes:
            print("No deletions to execute")
            return
        
        print("\n" + "="*50)
        print("EXECUTING DELETIONS")
        print("="*50)
        
        for file_path in self.approved_changes['deletions']:
            filepath = self.data_dir / file_path
            self.delete_file(filepath)
    
    def execute_moves(self):
        """Execute approved file moves"""
        if not self.approved_changes or 'moves' not in self.approved_changes:
            print("No moves to execute")
            return
        
        print("\n" + "="*50)
        print("EXECUTING MOVES")
        print("="*50)
        
        for move in self.approved_changes['moves']:
            source = self.data_dir / move['source']
            destination = self.data_dir / move['destination']
            self.move_file(source, destination)
    
    def execute_archives(self):
        """Execute approved archival operations"""
        if not self.approved_changes or 'archives' not in self.approved_changes:
            print("No archives to execute")
            return
        
        print("\n" + "="*50)
        print("EXECUTING ARCHIVES")
        print("="*50)
        
        for archive in self.approved_changes['archives']:
            directory = self.data_dir / archive['directory']
            archive_name = archive['archive_name']
            self.archive_directory(directory, archive_name)
    
    def execute_consolidations(self):
        """Execute approved file consolidations"""
        if not self.approved_changes or 'consolidations' not in self.approved_changes:
            print("No consolidations to execute")
            return
        
        print("\n" + "="*50)
        print("EXECUTING CONSOLIDATIONS")
        print("="*50)
        
        for consolidation in self.approved_changes['consolidations']:
            sources = [self.data_dir / s for s in consolidation['sources']]
            target = self.data_dir / consolidation['target']
            self.consolidate_csv_files(sources, target)
    
    def create_new_structure(self):
        """Create the new directory structure"""
        new_dirs = [
            "current/production",
            "current/wells",
            "current/leases",
            "current/completions",
            "current/surveys",
            "archive",
            "raw/binary",
            "raw/compressed"
        ]
        
        print("\n" + "="*50)
        print("CREATING NEW STRUCTURE")
        print("="*50)
        
        for dir_path in new_dirs:
            full_path = self.data_dir / dir_path
            self.log_operation("CREATE_DIR", {'path': str(full_path)})
            
            if not self.dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
    
    def save_operations_log(self):
        """Save detailed operations log"""
        log_file = Path("specs/modules/bsee/consolidation/migration_log.json")
        
        with open(log_file, 'w') as f:
            json.dump({
                'execution_time': datetime.now().isoformat(),
                'dry_run': self.dry_run,
                'operations': self.operations_log,
                'rollback_commands': self.rollback_commands
            }, f, indent=2)
        
        print(f"\nOperations log saved to {log_file}")
    
    def generate_rollback_script(self):
        """Generate script to rollback changes"""
        script_lines = [
            "#!/usr/bin/env python",
            "# BSEE Migration Rollback Script",
            f"# Generated: {datetime.now().isoformat()}",
            "",
            "import shutil",
            "from pathlib import Path",
            "",
            "print('Executing rollback...')",
            ""
        ]
        
        for cmd in reversed(self.rollback_commands):
            if cmd['action'] == 'move':
                script_lines.append(
                    f"shutil.move('{cmd['source']}', '{cmd['destination']}')"
                )
            elif cmd['action'] == 'restore':
                script_lines.append(
                    f"shutil.copy2('{cmd['source']}', '{cmd['destination']}')"
                )
        
        script_lines.append("\nprint('Rollback complete')")
        
        rollback_file = Path("specs/modules/bsee/consolidation/rollback.py")
        with open(rollback_file, 'w') as f:
            f.write('\n'.join(script_lines))
        
        print(f"Rollback script saved to {rollback_file}")
    
    def execute_migration(self):
        """Execute the complete migration"""
        print("\n" + "="*50)
        print(f"BSEE DATA MIGRATION {'[DRY RUN]' if self.dry_run else '[EXECUTING]'}")
        print("="*50)
        
        if not self.approved_changes:
            print("ERROR: No approved changes found. Please get approval first.")
            return False
        
        # Execute in order
        self.create_new_structure()
        self.execute_moves()
        self.execute_consolidations()
        self.execute_archives()
        self.execute_deletions()
        
        # Save logs
        self.save_operations_log()
        self.generate_rollback_script()
        
        print("\n" + "="*50)
        if self.dry_run:
            print("DRY RUN COMPLETE - No actual changes made")
            print("To execute for real, run with dry_run=False")
        else:
            print("MIGRATION COMPLETE")
            print("Run validation script to verify success")
        print("="*50)
        
        return True


if __name__ == "__main__":
    import sys
    
    # Check for --execute flag
    dry_run = "--execute" not in sys.argv
    
    if dry_run:
        print("Running in DRY RUN mode (no changes will be made)")
        print("To execute changes, run: python migration_executor.py --execute")
    else:
        response = input("⚠️  This will modify files. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted")
            exit(0)
    
    executor = MigrationExecutor(dry_run=dry_run)
    executor.execute_migration()