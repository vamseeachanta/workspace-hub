#!/usr/bin/env python
"""
Monitor BSEE migration progress and health
Provides real-time status updates and metrics
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class MigrationMonitor:
    def __init__(self, data_dir: str = "data/modules/bsee"):
        self.data_dir = Path(data_dir)
        self.start_time = datetime.now()
        self.metrics = {
            'files_before': 0,
            'files_after': 0,
            'size_before_mb': 0,
            'size_after_mb': 0,
            'duplicates_removed': 0,
            'files_moved': 0,
            'files_archived': 0,
            'errors': []
        }
        
    def count_files(self, directory: Path) -> int:
        """Count total files in directory"""
        if not directory.exists():
            return 0
        return sum(1 for _ in directory.rglob("*") if _.is_file())
    
    def calculate_size(self, directory: Path) -> float:
        """Calculate total size in MB"""
        if not directory.exists():
            return 0
        total_size = sum(f.stat().st_size for f in directory.rglob("*") if f.is_file())
        return round(total_size / (1024 * 1024), 2)
    
    def check_structure(self) -> Dict:
        """Check if new structure exists"""
        expected_dirs = [
            "current/production",
            "current/wells", 
            "current/completions",
            "current/operations",
            "current/geology",
            "current/reference",
            "archive",
            "raw/binary",
            "raw/compressed"
        ]
        
        structure_status = {}
        for dir_path in expected_dirs:
            full_path = self.data_dir / dir_path
            structure_status[dir_path] = {
                'exists': full_path.exists(),
                'files': self.count_files(full_path) if full_path.exists() else 0
            }
        
        return structure_status
    
    def check_critical_files(self) -> List[Dict]:
        """Check if critical files are accessible"""
        critical_files = [
            "current/production/production.csv",
            "current/wells/well_data.csv",
            "current/wells/well_directional_surveys.csv",
            "current/completions/completion_summary.csv"
        ]
        
        file_status = []
        for file_path in critical_files:
            full_path = self.data_dir / file_path
            status = {
                'path': file_path,
                'exists': full_path.exists()
            }
            if full_path.exists():
                status['size_mb'] = round(full_path.stat().st_size / (1024 * 1024), 2)
            file_status.append(status)
        
        return file_status
    
    def generate_dashboard(self):
        """Generate migration status dashboard"""
        print("\n" + "="*60)
        print("🔍 BSEE MIGRATION MONITOR")
        print("="*60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {datetime.now() - self.start_time}")
        
        # File counts
        current_files = self.count_files(self.data_dir)
        current_size = self.calculate_size(self.data_dir)
        
        print(f"\n📊 Overall Metrics:")
        print(f"  Files: {current_files} (was 666)")
        print(f"  Size: {current_size} MB (was 367.60 MB)")
        print(f"  Reduction: {round((1 - current_files/666) * 100, 1)}% files, "
              f"{round((1 - current_size/367.60) * 100, 1)}% size")
        
        # Structure check
        print(f"\n📁 Directory Structure:")
        structure = self.check_structure()
        for dir_path, status in structure.items():
            icon = "✅" if status['exists'] else "❌"
            files = f"({status['files']} files)" if status['exists'] else ""
            print(f"  {icon} {dir_path} {files}")
        
        # Critical files
        print(f"\n🔑 Critical Files:")
        for file_status in self.check_critical_files():
            icon = "✅" if file_status['exists'] else "❌"
            size = f"({file_status.get('size_mb', 0)} MB)" if file_status['exists'] else ""
            print(f"  {icon} {file_status['path']} {size}")
        
        # Backup status
        backup_dir = Path(f"{self.data_dir}.backup")
        if backup_dir.exists():
            backup_files = self.count_files(backup_dir)
            backup_size = self.calculate_size(backup_dir)
            print(f"\n💾 Backup Status:")
            print(f"  ✅ Backup exists: {backup_files} files, {backup_size} MB")
        else:
            print(f"\n💾 Backup Status:")
            print(f"  ❌ No backup found")
        
        # Legacy status
        legacy_dir = self.data_dir / "legacy"
        if legacy_dir.exists():
            legacy_files = self.count_files(legacy_dir)
            print(f"\n📦 Legacy Directory:")
            print(f"  ⚠️  Still exists with {legacy_files} files (should be archived)")
        else:
            print(f"\n📦 Legacy Directory:")
            print(f"  ✅ Successfully removed/archived")
        
        # Archive status
        archive_dir = self.data_dir / "archive"
        if archive_dir.exists():
            archives = list(archive_dir.glob("*.tar.gz"))
            print(f"\n🗄️ Archives:")
            for archive in archives:
                size_mb = round(archive.stat().st_size / (1024 * 1024), 2)
                print(f"  ✅ {archive.name} ({size_mb} MB)")
        
        print("\n" + "="*60)
    
    def continuous_monitor(self, interval: int = 5):
        """Continuously monitor migration progress"""
        print("Starting continuous monitoring (Ctrl+C to stop)...")
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                self.generate_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
    
    def save_metrics(self):
        """Save metrics to file"""
        metrics_file = Path("specs/modules/bsee/consolidation/migration_metrics.json")
        
        # Gather current metrics
        self.metrics['files_after'] = self.count_files(self.data_dir)
        self.metrics['size_after_mb'] = self.calculate_size(self.data_dir)
        self.metrics['timestamp'] = datetime.now().isoformat()
        self.metrics['structure'] = self.check_structure()
        self.metrics['critical_files'] = self.check_critical_files()
        
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"Metrics saved to {metrics_file}")
    
    def health_check(self) -> bool:
        """Perform health check on migration"""
        issues = []
        
        # Check if backup exists
        if not Path(f"{self.data_dir}.backup").exists():
            issues.append("No backup found - risky state")
        
        # Check if critical directories exist
        critical_dirs = ["current", "raw"]
        for dir_name in critical_dirs:
            if not (self.data_dir / dir_name).exists():
                issues.append(f"Critical directory missing: {dir_name}")
        
        # Check if any critical files are missing
        critical_files = self.check_critical_files()
        missing_files = [f['path'] for f in critical_files if not f['exists']]
        if missing_files:
            issues.append(f"Missing critical files: {missing_files}")
        
        # Report health status
        if issues:
            print("\n⚠️ HEALTH CHECK WARNINGS:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("\n✅ HEALTH CHECK PASSED - All systems normal")
            return True


if __name__ == "__main__":
    import sys
    
    monitor = MigrationMonitor()
    
    if "--continuous" in sys.argv:
        # Continuous monitoring mode
        monitor.continuous_monitor()
    elif "--health" in sys.argv:
        # Health check only
        monitor.generate_dashboard()
        monitor.health_check()
    else:
        # Single run
        monitor.generate_dashboard()
        monitor.save_metrics()
        monitor.health_check()
        
        print("\nOptions:")
        print("  --continuous : Monitor continuously")
        print("  --health     : Health check only")