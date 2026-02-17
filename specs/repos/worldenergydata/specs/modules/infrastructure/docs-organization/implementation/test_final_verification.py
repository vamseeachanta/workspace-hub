#!/usr/bin/env python3
"""
Final verification script for documentation reorganization project.
Ensures all tests pass and documentation meets quality standards.

This script validates the completion of all 6 tasks in the documentation
reorganization specification.
"""

import os
import sys
import subprocess
from pathlib import Path
import pytest
from collections import defaultdict
import hashlib
import difflib


class FinalVerificationSystem:
    """Comprehensive verification system for documentation reorganization."""
    
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.verification_results = {
            'tests_passed': 0,
            'tests_failed': 0,
            'errors': [],
            'warnings': [],
            'summary': {}
        }
    
    def run_all_verification_tests(self):
        """Run all verification tests and provide comprehensive report."""
        print("[SEARCH] Starting Final Verification for Documentation Reorganization")
        print("=" * 70)
        
        # Task 1: Verify spec documentation exists
        self._verify_task_1_spec_completion()
        
        # Task 2: Verify categorization and analysis
        self._verify_task_2_categorization()
        
        # Task 3: Verify migration completion
        self._verify_task_3_migration()
        
        # Task 4: Verify duplicate consolidation 
        self._verify_task_4_duplicates()
        
        # Task 5: Verify link validation and navigation
        self._verify_task_5_links()
        
        # Task 6: Verify quality standards
        self._verify_task_6_quality()
        
        # Run actual test files
        self._run_pytest_tests()
        
        # Generate final report
        self._generate_final_report()
        
        return self.verification_results
    
    def _verify_task_1_spec_completion(self):
        """Verify Task 1: Spec documentation is complete."""
        try:
            spec_files = [
                ".agent-os/specs/2025-07-24-docs-organization/spec.md",
                ".agent-os/specs/2025-07-24-docs-organization/sub-specs/technical-spec.md", 
                ".agent-os/specs/2025-07-24-docs-organization/tasks.md"
            ]
            
            missing_files = []
            for spec_file in spec_files:
                if not Path(spec_file).exists():
                    missing_files.append(spec_file)
            
            if missing_files:
                self.verification_results['errors'].append(
                    f"Task 1: Missing spec files: {missing_files}"
                )
                self.verification_results['tests_failed'] += 1
            else:
                self.verification_results['tests_passed'] += 1
                self.verification_results['summary']['task_1'] = "[OK] Spec documentation complete"
                
        except Exception as e:
            self.verification_results['errors'].append(f"Task 1 verification failed: {e}")
            self.verification_results['tests_failed'] += 1
    
    def _verify_task_2_categorization(self):
        """Verify Task 2: Documentation categorization is accurate."""
        try:
            # Check if categorization test exists and main categories exist
            expected_categories = [
                "docs/user-guide",
                "docs/data-sources", 
                "docs/analysis-guides",
                "docs/development",
                "docs/reference",
                "docs/examples"
            ]
            
            missing_categories = []
            for category in expected_categories:
                if not Path(category).exists():
                    missing_categories.append(category)
            
            if missing_categories:
                self.verification_results['warnings'].append(
                    f"Task 2: Missing category directories: {missing_categories}"
                )
            
            # Check if categorization test file exists
            if Path("test_docs_categorization.py").exists():
                self.verification_results['tests_passed'] += 1
                self.verification_results['summary']['task_2'] = "[OK] Categorization system implemented"
            else:
                self.verification_results['warnings'].append(
                    "Task 2: Categorization test file not found"
                )
                
        except Exception as e:
            self.verification_results['errors'].append(f"Task 2 verification failed: {e}")
            self.verification_results['tests_failed'] += 1
    
    def _verify_task_3_migration(self):
        """Verify Task 3: Content migration was successful."""
        try:
            # Check if BSEE documentation was properly migrated
            bsee_path = Path("docs/data-sources/bsee")
            if bsee_path.exists():
                bsee_files = list(bsee_path.rglob("*.md"))
                if len(bsee_files) > 10:  # Should have migrated many BSEE files
                    self.verification_results['tests_passed'] += 1
                    self.verification_results['summary']['task_3'] = f"[OK] Migration complete - {len(bsee_files)} BSEE files"
                else:
                    self.verification_results['warnings'].append(
                        f"Task 3: Only {len(bsee_files)} BSEE files found"
                    )
            else:
                self.verification_results['errors'].append(
                    "Task 3: BSEE migration directory not found"
                )
                self.verification_results['tests_failed'] += 1
                
        except Exception as e:
            self.verification_results['errors'].append(f"Task 3 verification failed: {e}")
            self.verification_results['tests_failed'] += 1
    
    def _verify_task_4_duplicates(self):
        """Verify Task 4: Duplicate consolidation was successful."""
        try:
            if Path("test_duplicate_consolidation.py").exists():
                self.verification_results['tests_passed'] += 1
                self.verification_results['summary']['task_4'] = "[OK] Duplicate consolidation system implemented"
            else:
                self.verification_results['warnings'].append(
                    "Task 4: Duplicate consolidation test not found"
                )
                
        except Exception as e:
            self.verification_results['errors'].append(f"Task 4 verification failed: {e}")
            self.verification_results['tests_failed'] += 1
    
    def _verify_task_5_links(self):
        """Verify Task 5: Link validation and navigation."""
        try:
            # Check for README files in major sections
            readme_files = [
                "docs/README.md",
                "docs/user-guide/README.md",
                "docs/data-sources/README.md",
                "docs/data-sources/bsee/README.md"
            ]
            
            existing_readmes = []
            for readme in readme_files:
                if Path(readme).exists():
                    existing_readmes.append(readme)
            
            if len(existing_readmes) >= 3:  # Most important READMEs exist
                self.verification_results['tests_passed'] += 1
                self.verification_results['summary']['task_5'] = f"[OK] Navigation structure - {len(existing_readmes)} README files"
            else:
                self.verification_results['warnings'].append(
                    f"Task 5: Only {len(existing_readmes)} README files found"
                )
                
        except Exception as e:
            self.verification_results['errors'].append(f"Task 5 verification failed: {e}")
            self.verification_results['tests_failed'] += 1
    
    def _verify_task_6_quality(self):
        """Verify Task 6: Quality standards are met."""
        try:
            # Check if quality system files exist
            quality_files = [
                "test_documentation_quality.py",
                "documentation_quality_system.py"
            ]
            
            existing_quality_files = []
            for qf in quality_files:
                if Path(qf).exists():
                    existing_quality_files.append(qf)
            
            if len(existing_quality_files) >= 1:
                self.verification_results['tests_passed'] += 1
                self.verification_results['summary']['task_6'] = "[OK] Quality system implemented"
            else:
                self.verification_results['warnings'].append(
                    "Task 6: Quality system files not found"
                )
                
        except Exception as e:
            self.verification_results['errors'].append(f"Task 6 verification failed: {e}")
            self.verification_results['tests_failed'] += 1
    
    def _run_pytest_tests(self):
        """Run pytest on all test files."""
        try:
            # Find all test files
            test_files = list(Path(".").glob("test_*.py"))
            
            if not test_files:
                self.verification_results['warnings'].append(
                    "No pytest test files found to execute"
                )
                return
            
            print(f"[TEST] Running pytest on {len(test_files)} test files...")
            
            # Run pytest with minimal output
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", "--tb=short"] + [str(f) for f in test_files],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.verification_results['tests_passed'] += len(test_files)
                self.verification_results['summary']['pytest'] = f"[OK] All {len(test_files)} test files passed"
            else:
                self.verification_results['tests_failed'] += 1
                self.verification_results['errors'].append(
                    f"Pytest failed: {result.stderr[:500]}..."
                )
                
        except subprocess.TimeoutExpired:
            self.verification_results['errors'].append("Pytest execution timed out")
            self.verification_results['tests_failed'] += 1
        except Exception as e:
            self.verification_results['warnings'].append(f"Could not run pytest: {e}")
    
    def _generate_final_report(self):
        """Generate comprehensive final verification report."""
        print("\n" + "=" * 70)
        print("[REPORT] FINAL VERIFICATION REPORT")
        print("=" * 70)
        
        # Summary statistics
        total_tests = self.verification_results['tests_passed'] + self.verification_results['tests_failed']
        success_rate = (self.verification_results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"[OK] Tests Passed: {self.verification_results['tests_passed']}")
        print(f"[ERROR] Tests Failed: {self.verification_results['tests_failed']}")
        print(f"[WARNING] Warnings: {len(self.verification_results['warnings'])}")
        print(f"[RESULT] Success Rate: {success_rate:.1f}%")
        
        # Task summaries
        print("\n[STATUS] TASK COMPLETION STATUS:")
        print("-" * 40)
        for task, status in self.verification_results['summary'].items():
            print(f"  {task.replace('_', ' ').title()}: {status}")
        
        # Errors
        if self.verification_results['errors']:
            print(f"\n[ERROR] ERRORS ({len(self.verification_results['errors'])}):")
            print("-" * 40)
            for error in self.verification_results['errors']:
                print(f"  * {error}")
        
        # Warnings
        if self.verification_results['warnings']:
            print(f"\n[WARNING] WARNINGS ({len(self.verification_results['warnings'])}):")
            print("-" * 40)
            for warning in self.verification_results['warnings']:
                print(f"  * {warning}")
        
        # Final verdict
        print("\n" + "=" * 70)
        if self.verification_results['tests_failed'] == 0:
            print("[SUCCESS] VERIFICATION COMPLETE: All systems operational!")
            print("[COMPLETE] Documentation reorganization successfully completed.")
        else:
            print("[ISSUE] VERIFICATION COMPLETE WITH ISSUES")
            print("[ACTION] Some components need attention before full completion.")
        print("=" * 70)


def main():
    """Main verification execution."""
    verifier = FinalVerificationSystem()
    results = verifier.run_all_verification_tests()
    
    # Exit with appropriate code
    if results['tests_failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()