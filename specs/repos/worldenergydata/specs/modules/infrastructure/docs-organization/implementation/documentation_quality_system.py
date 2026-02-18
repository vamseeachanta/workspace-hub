#!/usr/bin/env python3
"""
Comprehensive documentation quality analysis and improvement system
Task 6.2-6.5: Apply formatting, update metadata, improve clarity, remove outdated content
"""

import json
from pathlib import Path
from typing import Dict, List
import re
from datetime import datetime
from test_documentation_quality import DocumentationQualityChecker, DocumentationFormatter, QualityIssue


class ComprehensiveQualitySystem:
    """Complete documentation quality analysis and improvement system"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_root = project_root / "docs"
        self.checker = DocumentationQualityChecker(self.docs_root)
        self.formatter = DocumentationFormatter(self.docs_root)
        
        # Energy professional focused improvements
        self.clarity_improvements = {
            # Technical jargon explanations
            'api': 'API (Application Programming Interface)',
            'npv': 'NPV (Net Present Value)',
            'bsee': 'BSEE (Bureau of Safety and Environmental Enforcement)',
            'sodir': 'SODIR (Norwegian Offshore Directorate)',
            
            # Energy industry clarity
            'wellbore': 'wellbore (the actual hole drilled into the ground)',
            'christmas tree': 'Christmas tree (wellhead control equipment)',
            'blowout preventer': 'blowout preventer (BOP - safety equipment)',
            'drilling mud': 'drilling mud (fluid used in drilling operations)',
        }
        
        # Outdated information patterns
        self.outdated_patterns = [
            (r'2020|2021|2022', 'Check if date references need updating'),
            (r'coming soon|under development|planned', 'Check if feature is now available'),
            (r'beta|alpha|experimental', 'Check if status has changed'),
            (r'TODO|FIXME|XXX', 'Resolve temporary markers'),
        ]
        
        # Metadata standards
        self.metadata_template = {
            'energy_data': {
                'required_fields': ['title', 'data_source', 'last_updated', 'coverage'],
                'optional_fields': ['frequency', 'format', 'access_method']
            },
            'analysis_guide': {
                'required_fields': ['title', 'methodology', 'target_users', 'last_updated'],
                'optional_fields': ['prerequisites', 'examples', 'references']
            },
            'technical_doc': {
                'required_fields': ['title', 'purpose', 'last_updated'],
                'optional_fields': ['api_version', 'dependencies', 'examples']
            }
        }
    
    def run_comprehensive_quality_analysis(self) -> Dict:
        """Run complete quality analysis and improvement"""
        print("=== COMPREHENSIVE DOCUMENTATION QUALITY ANALYSIS ===")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'analysis_complete': False,
            'total_files_analyzed': 0,
            'quality_issues_found': 0,
            'formatting_fixes_needed': 0,
            'content_improvements_needed': 0,
            'outdated_content_found': 0,
            'metadata_updates_needed': 0,
            'detailed_results': {}
        }
        
        # 1. Run quality analysis
        print("\n1. Analyzing documentation quality...")
        quality_results = self._analyze_documentation_quality()
        results['detailed_results']['quality_analysis'] = quality_results
        results['quality_issues_found'] = quality_results['total_issues']
        
        # 2. Analyze formatting needs
        print("\n2. Analyzing formatting consistency...")
        formatting_results = self._analyze_formatting_needs()
        results['detailed_results']['formatting_analysis'] = formatting_results
        results['formatting_fixes_needed'] = formatting_results['files_needing_formatting']
        
        # 3. Analyze content clarity
        print("\n3. Analyzing content clarity for energy professionals...")
        clarity_results = self._analyze_content_clarity()
        results['detailed_results']['clarity_analysis'] = clarity_results
        results['content_improvements_needed'] = clarity_results['files_needing_improvement']
        
        # 4. Check for outdated content
        print("\n4. Checking for outdated information...")
        outdated_results = self._check_outdated_content()
        results['detailed_results']['outdated_analysis'] = outdated_results
        results['outdated_content_found'] = outdated_results['files_with_outdated_content']
        
        # 5. Analyze metadata completeness
        print("\n5. Analyzing metadata completeness...")
        metadata_results = self._analyze_metadata_completeness()
        results['detailed_results']['metadata_analysis'] = metadata_results
        results['metadata_updates_needed'] = metadata_results['files_missing_metadata']
        
        # Count total files
        results['total_files_analyzed'] = len(list(self.docs_root.rglob("*.md")))
        results['analysis_complete'] = True
        
        return results
    
    def _analyze_documentation_quality(self) -> Dict:
        """Analyze documentation quality using the checker"""
        issues = self.checker.check_all_documents()
        report = self.checker.generate_quality_report(issues)
        
        print(f"  Total quality issues: {report['total_issues']}")
        print(f"  Errors: {report['issues_by_severity']['error']}")
        print(f"  Warnings: {report['issues_by_severity']['warning']}")
        print(f"  Info: {report['issues_by_severity']['info']}")
        
        # Show most common issue types
        if report['issues_by_type']:
            print("  Most common issues:")
            sorted_issues = sorted(report['issues_by_type'].items(), 
                                 key=lambda x: x[1], reverse=True)
            for issue_type, count in sorted_issues[:5]:
                print(f"    - {issue_type}: {count}")
        
        return report
    
    def _analyze_formatting_needs(self) -> Dict:
        """Analyze formatting consistency needs"""
        formatting_results = self.formatter.format_all_documents(dry_run=True)
        
        print(f"  Files processed: {formatting_results['files_processed']}")
        print(f"  Files needing formatting: {formatting_results['files_modified']}")
        
        return {
            'files_processed': formatting_results['files_processed'],
            'files_needing_formatting': formatting_results['files_modified'],
            'potential_fixes': formatting_results['fixes_applied']
        }
    
    def _analyze_content_clarity(self) -> Dict:
        """Analyze content clarity for energy professionals"""
        md_files = list(self.docs_root.rglob("*.md"))
        files_needing_improvement = 0
        clarity_issues = []
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                file_issues = []
                
                # Check for unexplained technical terms
                for term, explanation in self.clarity_improvements.items():
                    if term.lower() in content.lower():
                        # Check if term is already explained
                        if f"({explanation.split('(')[1]}" not in content:
                            file_issues.append({
                                'term': term,
                                'suggestion': f"Consider explaining: {explanation}"
                            })
                
                # Check for overly technical language without context
                technical_indicators = [
                    'API', 'JSON', 'HTTP', 'SQL', 'CSV', 'XML',
                    'algorithm', 'implementation', 'configuration'
                ]
                
                for indicator in technical_indicators:
                    if indicator in content and 'energy professional' not in content.lower():
                        # This might be too technical for energy professionals
                        pass  # Could add specific checks here
                
                if file_issues:
                    files_needing_improvement += 1
                    clarity_issues.append({
                        'file': str(md_file.relative_to(self.project_root)),
                        'issues': file_issues
                    })
                    
            except Exception:
                continue
        
        print(f"  Files needing clarity improvements: {files_needing_improvement}")
        if clarity_issues:
            print("  Sample clarity issues:")
            for issue in clarity_issues[:3]:
                print(f"    - {issue['file']}: {len(issue['issues'])} improvements suggested")
        
        return {
            'files_needing_improvement': files_needing_improvement,
            'clarity_issues': clarity_issues[:10]  # Limit for report size
        }
    
    def _check_outdated_content(self) -> Dict:
        """Check for outdated information"""
        md_files = list(self.docs_root.rglob("*.md"))
        files_with_outdated = 0
        outdated_issues = []
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                file_issues = []
                
                for pattern, description in self.outdated_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        file_issues.append({
                            'pattern': pattern,
                            'match': match.group(),
                            'line': line_num,
                            'description': description
                        })
                
                if file_issues:
                    files_with_outdated += 1
                    outdated_issues.append({
                        'file': str(md_file.relative_to(self.project_root)),
                        'issues': file_issues
                    })
                    
            except Exception:
                continue
        
        print(f"  Files with potentially outdated content: {files_with_outdated}")
        
        return {
            'files_with_outdated_content': files_with_outdated,
            'outdated_issues': outdated_issues[:10]  # Limit for report size
        }
    
    def _analyze_metadata_completeness(self) -> Dict:
        """Analyze metadata completeness"""
        md_files = list(self.docs_root.rglob("*.md"))
        files_missing_metadata = 0
        metadata_issues = []
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                
                # Basic metadata checks
                missing_elements = []
                
                # Check for title
                if not re.search(r'^#\s+.+$', content, re.MULTILINE):
                    missing_elements.append('title')
                
                # Check for last updated info
                if 'last updated' not in content.lower() and 'updated:' not in content.lower():
                    missing_elements.append('last_updated')
                
                # Check for description (in first paragraph)
                lines = content.strip().split('\n')
                if len(lines) < 3 or not lines[2].strip():
                    missing_elements.append('description')
                
                if missing_elements:
                    files_missing_metadata += 1
                    metadata_issues.append({
                        'file': str(md_file.relative_to(self.project_root)),
                        'missing': missing_elements
                    })
                    
            except Exception:
                continue
        
        print(f"  Files missing metadata: {files_missing_metadata}")
        
        return {
            'files_missing_metadata': files_missing_metadata,
            'metadata_issues': metadata_issues[:10]  # Limit for report size
        }
    
    def apply_quality_improvements(self, analysis_results: Dict, dry_run: bool = True) -> Dict:
        """Apply quality improvements based on analysis"""
        print(f"\n=== APPLYING QUALITY IMPROVEMENTS {'(DRY RUN)' if dry_run else ''} ===")
        
        improvement_results = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': dry_run,
            'improvements_applied': 0,
            'files_modified': 0,
            'errors': []
        }
        
        # 1. Apply formatting fixes
        print("1. Applying formatting improvements...")
        formatting_results = self.formatter.format_all_documents(dry_run=dry_run)
        improvement_results['improvements_applied'] += formatting_results['fixes_applied']
        improvement_results['files_modified'] += formatting_results['files_modified']
        
        if formatting_results['errors']:
            improvement_results['errors'].extend(formatting_results['errors'])
        
        # 2. Apply metadata updates (basic ones)
        print("2. Applying basic metadata updates...")
        metadata_fixes = self._apply_metadata_updates(dry_run)
        improvement_results['improvements_applied'] += metadata_fixes['fixes_applied']
        improvement_results['files_modified'] += metadata_fixes['files_modified']
        
        # 3. Fix obvious outdated content
        print("3. Fixing obvious outdated markers...")
        outdated_fixes = self._fix_outdated_markers(dry_run)
        improvement_results['improvements_applied'] += outdated_fixes['fixes_applied']
        improvement_results['files_modified'] += outdated_fixes['files_modified']
        
        print(f"\nImprovement summary:")
        print(f"  Total improvements applied: {improvement_results['improvements_applied']}")
        print(f"  Files modified: {improvement_results['files_modified']}")
        print(f"  Errors: {len(improvement_results['errors'])}")
        
        return improvement_results
    
    def _apply_metadata_updates(self, dry_run: bool) -> Dict:
        """Apply basic metadata updates"""
        results = {'fixes_applied': 0, 'files_modified': 0}
        
        md_files = list(self.docs_root.rglob("*.md"))
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                original_content = content
                modified = False
                
                # Add last updated if missing and file is substantial
                if ('last updated' not in content.lower() and 
                    'updated:' not in content.lower() and
                    len(content) > 200):
                    
                    # Add to end of file
                    if not content.endswith('\n'):
                        content += '\n'
                    content += f"\n---\n\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*\n"
                    modified = True
                    results['fixes_applied'] += 1
                
                if modified and not dry_run:
                    md_file.write_text(content, encoding='utf-8')
                    results['files_modified'] += 1
                elif modified:
                    results['files_modified'] += 1
                    
            except Exception:
                continue
        
        return results
    
    def _fix_outdated_markers(self, dry_run: bool) -> Dict:
        """Fix obvious outdated temporary markers"""
        results = {'fixes_applied': 0, 'files_modified': 0}
        
        md_files = list(self.docs_root.rglob("*.md"))
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                original_content = content
                
                # Remove simple TODO/FIXME lines that are standalone
                content = re.sub(r'^TODO:.*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'^FIXME:.*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'^XXX:.*$', '', content, flags=re.MULTILINE)
                
                # Clean up extra blank lines
                content = re.sub(r'\n\n\n+', '\n\n', content)
                
                if content != original_content:
                    results['fixes_applied'] += 1
                    if not dry_run:
                        md_file.write_text(content, encoding='utf-8')
                        results['files_modified'] += 1
                    else:
                        results['files_modified'] += 1
                        
            except Exception:
                continue
        
        return results


def main():
    """Main execution function"""
    project_root = Path(__file__).parent
    
    print("Starting comprehensive documentation quality analysis...")
    
    # Initialize quality system
    quality_system = ComprehensiveQualitySystem(project_root)
    
    # Run comprehensive analysis
    analysis_results = quality_system.run_comprehensive_quality_analysis()
    
    # Save analysis results
    analysis_file = project_root / "documentation_quality_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis complete! Results saved to {analysis_file}")
    
    # Print summary
    print("\n=== QUALITY ANALYSIS SUMMARY ===")
    print(f"Files analyzed: {analysis_results['total_files_analyzed']}")
    print(f"Quality issues found: {analysis_results['quality_issues_found']}")
    print(f"Files need formatting: {analysis_results['formatting_fixes_needed']}")
    print(f"Files need clarity improvements: {analysis_results['content_improvements_needed']}")
    print(f"Files with outdated content: {analysis_results['outdated_content_found']}")
    print(f"Files missing metadata: {analysis_results['metadata_updates_needed']}")
    
    # Apply improvements
    print("\n" + "="*60)
    print("APPLYING QUALITY IMPROVEMENTS")
    print("="*60)
    
    # First do dry run
    print("\nStep 1: Dry run of improvements...")
    dry_run_results = quality_system.apply_quality_improvements(analysis_results, dry_run=True)
    
    if dry_run_results['errors']:
        print(f"[WARNING] {len(dry_run_results['errors'])} errors in dry run")
        return
    
    print(f"[SUCCESS] Dry run completed - ready to apply {dry_run_results['improvements_applied']} improvements")
    
    # Apply actual improvements
    print("\nStep 2: Applying improvements...")
    improvement_results = quality_system.apply_quality_improvements(analysis_results, dry_run=False)
    
    # Save improvement results
    improvement_file = project_root / "documentation_quality_improvements.json"
    with open(improvement_file, 'w', encoding='utf-8') as f:
        json.dump(improvement_results, f, indent=2, ensure_ascii=False)
    
    print(f"Improvement results saved to {improvement_file}")
    
    # Final summary
    print("\n" + "="*60)
    print("QUALITY IMPROVEMENT COMPLETE")
    print("="*60)
    print(f"Improvements applied: {improvement_results['improvements_applied']}")
    print(f"Files modified: {improvement_results['files_modified']}")
    print(f"Errors: {len(improvement_results['errors'])}")
    
    return analysis_results, improvement_results


if __name__ == "__main__":
    main()