#!/usr/bin/env python
"""
Post-Migration Monitoring Dashboard
Tracks migration success and ongoing health metrics
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class PostMigrationMonitor:
    def __init__(self, data_dir: str = "data/modules/bsee"):
        self.data_dir = Path(data_dir)
        self.migration_date = self.get_migration_date()
        self.metrics_file = Path("specs/modules/bsee/consolidation/post_migration_metrics.json")
        self.issues_log = Path("specs/modules/bsee/consolidation/issues_log.json")
        
    def get_migration_date(self) -> datetime:
        """Get the migration execution date from validation report"""
        validation_report = Path("specs/modules/bsee/consolidation/validation_report.md")
        if validation_report.exists():
            with open(validation_report) as f:
                for line in f:
                    if "Generated:" in line:
                        date_str = line.split("Generated:")[1].strip()
                        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return datetime.now()
    
    def calculate_days_since_migration(self) -> int:
        """Calculate days since migration"""
        return (datetime.now() - self.migration_date).days
    
    def check_data_integrity(self) -> Dict:
        """Verify data integrity post-migration"""
        integrity = {
            'status': 'healthy',
            'checks': [],
            'warnings': []
        }
        
        # Check critical directories exist
        critical_dirs = [
            "current/production",
            "current/wells",
            "current/completions",
            "archive"
        ]
        
        for dir_path in critical_dirs:
            full_path = self.data_dir / dir_path
            if full_path.exists():
                file_count = sum(1 for _ in full_path.rglob("*") if _.is_file())
                integrity['checks'].append({
                    'directory': dir_path,
                    'status': 'exists',
                    'files': file_count
                })
            else:
                integrity['status'] = 'warning'
                integrity['warnings'].append(f"Missing directory: {dir_path}")
        
        return integrity
    
    def check_compatibility_links(self) -> Dict:
        """Check status of compatibility symbolic links"""
        days_since = self.calculate_days_since_migration()
        removal_date = self.migration_date + timedelta(days=30)
        
        compatibility = {
            'days_active': days_since,
            'removal_date': removal_date.strftime('%Y-%m-%d'),
            'days_remaining': max(0, 30 - days_since),
            'links': []
        }
        
        # Check for symlinks
        legacy_paths = [
            "analysis_data/combined_data_for_analysis",
            "legacy/data_for_analysis"
        ]
        
        for path in legacy_paths:
            full_path = self.data_dir / path
            if full_path.exists() and full_path.is_symlink():
                target = full_path.resolve()
                compatibility['links'].append({
                    'path': str(path),
                    'target': str(target.relative_to(self.data_dir)),
                    'active': True
                })
        
        return compatibility
    
    def measure_performance(self) -> Dict:
        """Measure current performance metrics"""
        import time
        
        performance = {
            'file_access': {},
            'directory_traversal': {},
            'size_metrics': {}
        }
        
        # Measure file access time
        test_file = self.data_dir / "current/production/production.csv"
        if test_file.exists():
            start = time.time()
            with open(test_file) as f:
                _ = f.readline()
            performance['file_access']['time_ms'] = round((time.time() - start) * 1000, 2)
        
        # Measure directory traversal
        start = time.time()
        file_count = sum(1 for _ in self.data_dir.rglob("*") if _.is_file())
        performance['directory_traversal'] = {
            'time_ms': round((time.time() - start) * 1000, 2),
            'files_found': file_count
        }
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in self.data_dir.rglob("*") if f.is_file())
        performance['size_metrics'] = {
            'total_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count,
            'avg_file_size_kb': round((total_size / file_count) / 1024, 2) if file_count > 0 else 0
        }
        
        return performance
    
    def check_code_updates(self) -> Dict:
        """Check for code files still using old paths"""
        outdated_references = []
        
        # Search for Python files using old paths
        project_root = Path(".")
        old_patterns = [
            "analysis_data/combined_data_for_analysis",
            "legacy/data_for_analysis",
            "data_for_analysis"
        ]
        
        for py_file in project_root.rglob("*.py"):
            if "specs/modules/bsee" in str(py_file):
                continue  # Skip our own scripts
            
            try:
                with open(py_file) as f:
                    content = f.read()
                    for pattern in old_patterns:
                        if pattern in content:
                            outdated_references.append({
                                'file': str(py_file),
                                'pattern': pattern
                            })
                            break
            except:
                pass
        
        return {
            'outdated_count': len(outdated_references),
            'files': outdated_references[:10]  # Limit to first 10
        }
    
    def load_issues(self) -> List[Dict]:
        """Load reported issues from log"""
        if self.issues_log.exists():
            with open(self.issues_log) as f:
                return json.load(f)
        return []
    
    def generate_dashboard(self):
        """Generate comprehensive monitoring dashboard"""
        days_since = self.calculate_days_since_migration()
        
        print("\n" + "="*70)
        print("📊 POST-MIGRATION MONITORING DASHBOARD")
        print("="*70)
        print(f"Migration Date: {self.migration_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"Days Since Migration: {days_since}")
        print(f"Monitoring Phase: {self.get_phase(days_since)}")
        
        # Data Integrity
        print("\n🔍 Data Integrity Check:")
        integrity = self.check_data_integrity()
        status_icon = "✅" if integrity['status'] == 'healthy' else "⚠️"
        print(f"  Status: {status_icon} {integrity['status'].upper()}")
        for check in integrity['checks']:
            print(f"  ✓ {check['directory']}: {check['files']} files")
        for warning in integrity['warnings']:
            print(f"  ⚠️ {warning}")
        
        # Compatibility Links
        print("\n🔗 Compatibility Links:")
        compatibility = self.check_compatibility_links()
        if compatibility['days_remaining'] > 0:
            print(f"  Status: Active ({compatibility['days_remaining']} days remaining)")
            print(f"  Removal Date: {compatibility['removal_date']}")
            for link in compatibility['links']:
                print(f"  ✓ {link['path']} → {link['target']}")
        else:
            print("  Status: Ready for removal")
            print("  ⚠️ Run remove_compatibility_links.py to clean up")
        
        # Performance Metrics
        print("\n⚡ Performance Metrics:")
        performance = self.measure_performance()
        print(f"  File Access: {performance['file_access'].get('time_ms', 'N/A')} ms")
        print(f"  Directory Traversal: {performance['directory_traversal']['time_ms']} ms")
        print(f"  Total Size: {performance['size_metrics']['total_mb']} MB")
        print(f"  File Count: {performance['size_metrics']['file_count']} files")
        
        # Code Updates
        print("\n📝 Code Reference Updates:")
        code_updates = self.check_code_updates()
        if code_updates['outdated_count'] == 0:
            print("  ✅ All code references updated")
        else:
            print(f"  ⚠️ {code_updates['outdated_count']} files still using old paths")
            for ref in code_updates['files'][:3]:
                print(f"    - {ref['file']}: '{ref['pattern']}'")
        
        # Issues Log
        print("\n📋 Reported Issues:")
        issues = self.load_issues()
        if not issues:
            print("  ✅ No issues reported")
        else:
            print(f"  Total: {len(issues)} issues")
            for issue in issues[-3:]:  # Show last 3
                print(f"    - [{issue['date']}] {issue['description']}")
        
        # Phase-Specific Actions
        print("\n🎯 Recommended Actions:")
        actions = self.get_recommended_actions(days_since)
        for action in actions:
            print(f"  • {action}")
        
        print("\n" + "="*70)
        
        # Save metrics
        self.save_metrics(integrity, compatibility, performance, code_updates)
    
    def get_phase(self, days: int) -> str:
        """Determine current monitoring phase"""
        if days < 7:
            return "Initial Monitoring (Week 1)"
        elif days < 30:
            return "Transition Period (Weeks 2-4)"
        elif days < 45:
            return "Stabilization (Days 30-45)"
        elif days < 60:
            return "Final Validation (Days 45-60)"
        else:
            return "Completed"
    
    def get_recommended_actions(self, days: int) -> List[str]:
        """Get phase-specific recommended actions"""
        actions = []
        
        if days < 7:
            actions.append("Monitor for immediate issues")
            actions.append("Begin updating code references")
            actions.append("Collect team feedback")
        elif days < 30:
            actions.append("Complete code reference updates")
            actions.append("Test all critical workflows")
            actions.append("Prepare for link removal")
        elif days == 30:
            actions.append("🔴 Remove compatibility links TODAY")
            actions.append("Final code verification")
            actions.append("Update documentation")
        elif days < 45:
            actions.append("Perform final validation")
            actions.append("Optimize based on metrics")
            actions.append("Document lessons learned")
        elif days < 60:
            actions.append("Archive legacy structure")
            actions.append("Close migration project")
            actions.append("Celebrate success! 🎉")
        else:
            actions.append("Migration complete - normal operations")
        
        return actions
    
    def save_metrics(self, integrity, compatibility, performance, code_updates):
        """Save metrics to file for tracking"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'days_since_migration': self.calculate_days_since_migration(),
            'integrity': integrity,
            'compatibility': compatibility,
            'performance': performance,
            'code_updates': code_updates
        }
        
        # Append to metrics history
        history = []
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                history = json.load(f)
        
        history.append(metrics)
        
        # Keep only last 30 days of metrics
        if len(history) > 30:
            history = history[-30:]
        
        with open(self.metrics_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def continuous_monitor(self, interval: int = 300):
        """Run continuous monitoring (default 5 minutes)"""
        print("Starting continuous post-migration monitoring...")
        print(f"Refresh interval: {interval} seconds")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                self.generate_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")


if __name__ == "__main__":
    import sys
    
    monitor = PostMigrationMonitor()
    
    if "--continuous" in sys.argv:
        # Continuous monitoring
        interval = 300  # 5 minutes default
        if "--interval" in sys.argv:
            idx = sys.argv.index("--interval")
            if idx + 1 < len(sys.argv):
                interval = int(sys.argv[idx + 1])
        monitor.continuous_monitor(interval)
    else:
        # Single run
        monitor.generate_dashboard()
        
        print("\nOptions:")
        print("  --continuous       : Run continuous monitoring")
        print("  --interval <sec>   : Set refresh interval (default 300)")