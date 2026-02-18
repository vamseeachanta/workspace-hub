#!/usr/bin/env python3
"""
ABOUTME: Pseudocode diff and comparison tool for workspace-hub
ABOUTME: Generates visual diff reports with impact analysis and test coverage assessment
"""

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Set
import difflib
from html import escape


class PseudocodeDiff:
    """Generates diff reports comparing pseudocode versions."""

    def __init__(self, original_path: Path, updated_path: Path, output_path: Path):
        self.original_path = original_path
        self.updated_path = updated_path
        self.output_path = output_path
        self.original_content = ""
        self.updated_content = ""
        self.original_lines = []
        self.updated_lines = []

    def load_files(self):
        """Load both pseudocode files."""
        try:
            with open(self.original_path, 'r') as f:
                self.original_content = f.read()
                self.original_lines = self.original_content.splitlines(keepends=True)
        except Exception as e:
            print(f"ERROR: Failed to load original file: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(self.updated_path, 'r') as f:
                self.updated_content = f.read()
                self.updated_lines = self.updated_content.splitlines(keepends=True)
        except Exception as e:
            print(f"ERROR: Failed to load updated file: {e}", file=sys.stderr)
            sys.exit(1)

    def extract_components(self, content: str) -> Set[str]:
        """Extract component/function names from pseudocode."""
        components = set()

        # Match common patterns: FUNCTION name, CLASS name, PROCEDURE name, MODULE name
        patterns = [
            r'(?:FUNCTION|PROCEDURE|METHOD)\s+(\w+)',
            r'(?:CLASS|MODULE|COMPONENT)\s+(\w+)',
            r'(?:def|class)\s+(\w+)',  # Python-style
            r'function\s+(\w+)',  # JavaScript-style
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                components.add(match.group(1))

        return components

    def extract_test_references(self, content: str) -> Set[str]:
        """Extract test references and assertions from pseudocode."""
        tests = set()

        # Match test-related patterns
        patterns = [
            r'TEST\s+(\w+)',
            r'ASSERT\s+(\w+)',
            r'VERIFY\s+(\w+)',
            r'(?:test_|Test)(\w+)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                tests.add(match.group(1))

        return tests

    def analyze_impact(self) -> Dict[str, any]:
        """Analyze impact of changes on components and tests."""
        original_components = self.extract_components(self.original_content)
        updated_components = self.extract_components(self.updated_content)

        original_tests = self.extract_test_references(self.original_content)
        updated_tests = self.extract_test_references(self.updated_content)

        added_components = updated_components - original_components
        removed_components = original_components - updated_components
        modified_components = original_components & updated_components

        added_tests = updated_tests - original_tests
        removed_tests = original_tests - updated_tests

        # Calculate diff statistics
        diff = list(difflib.unified_diff(
            self.original_lines,
            self.updated_lines,
            lineterm=''
        ))

        additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))

        return {
            'components': {
                'added': added_components,
                'removed': removed_components,
                'modified': modified_components,
                'total_original': len(original_components),
                'total_updated': len(updated_components)
            },
            'tests': {
                'added': added_tests,
                'removed': removed_tests,
                'total_original': len(original_tests),
                'total_updated': len(updated_tests)
            },
            'changes': {
                'additions': additions,
                'deletions': deletions,
                'total': additions + deletions
            }
        }

    def generate_html_diff(self) -> str:
        """Generate side-by-side HTML diff with highlighting."""
        # Generate unified diff
        differ = difflib.HtmlDiff(wrapcolumn=80)
        html_diff = differ.make_file(
            self.original_lines,
            self.updated_lines,
            fromdesc=f'Original: {self.original_path.name}',
            todesc=f'Updated: {self.updated_path.name}',
            context=True,
            numlines=3
        )

        return html_diff

    def generate_impact_html(self, impact: Dict) -> str:
        """Generate HTML report for impact analysis."""
        html = """
        <div class="impact-analysis">
            <h2>Impact Analysis</h2>

            <div class="summary-cards">
                <div class="card additions">
                    <div class="card-number">{additions}</div>
                    <div class="card-label">Lines Added</div>
                </div>
                <div class="card deletions">
                    <div class="card-number">{deletions}</div>
                    <div class="card-label">Lines Deleted</div>
                </div>
                <div class="card total-changes">
                    <div class="card-number">{total}</div>
                    <div class="card-label">Total Changes</div>
                </div>
            </div>

            <h3>Components Affected</h3>
            <div class="components-section">
                <div class="component-category">
                    <h4>Added Components ({added_count})</h4>
                    <ul>
                        {added_components}
                    </ul>
                </div>
                <div class="component-category">
                    <h4>Removed Components ({removed_count})</h4>
                    <ul>
                        {removed_components}
                    </ul>
                </div>
                <div class="component-category">
                    <h4>Potentially Modified ({modified_count})</h4>
                    <ul>
                        {modified_components}
                    </ul>
                </div>
            </div>

            <h3>Test Coverage Impact</h3>
            <div class="test-section">
                <div class="test-stats">
                    <p><strong>Original Tests:</strong> {original_tests}</p>
                    <p><strong>Updated Tests:</strong> {updated_tests}</p>
                    <p><strong>Added Tests:</strong> {added_tests_count}</p>
                    <p><strong>Removed Tests:</strong> {removed_tests_count}</p>
                </div>
                {test_recommendations}
            </div>

            <div class="recommendations">
                <h3>Recommendations</h3>
                <ul>
                    {recommendations}
                </ul>
            </div>
        </div>
        """.format(
            additions=impact['changes']['additions'],
            deletions=impact['changes']['deletions'],
            total=impact['changes']['total'],
            added_count=len(impact['components']['added']),
            removed_count=len(impact['components']['removed']),
            modified_count=len(impact['components']['modified']),
            added_components=self._format_list(impact['components']['added']) or '<li class="none">None</li>',
            removed_components=self._format_list(impact['components']['removed']) or '<li class="none">None</li>',
            modified_components=self._format_list(impact['components']['modified']) or '<li class="none">None</li>',
            original_tests=impact['tests']['total_original'],
            updated_tests=impact['tests']['total_updated'],
            added_tests_count=len(impact['tests']['added']),
            removed_tests_count=len(impact['tests']['removed']),
            test_recommendations=self._generate_test_recommendations(impact),
            recommendations=self._generate_recommendations(impact)
        )

        return html

    def _format_list(self, items: Set[str]) -> str:
        """Format set of items as HTML list items."""
        if not items:
            return ""
        return "\n".join(f'<li><code>{escape(item)}</code></li>' for item in sorted(items))

    def _generate_test_recommendations(self, impact: Dict) -> str:
        """Generate test coverage recommendations."""
        added_components = len(impact['components']['added'])
        removed_components = len(impact['components']['removed'])
        added_tests = len(impact['tests']['added'])

        recommendations = []

        if added_components > 0 and added_tests == 0:
            recommendations.append(
                '<div class="alert alert-warning">'
                '⚠️ <strong>Warning:</strong> New components detected but no new tests added. '
                'Consider adding test coverage for new functionality.'
                '</div>'
            )

        if removed_components > 0:
            recommendations.append(
                '<div class="alert alert-info">'
                'ℹ️ <strong>Info:</strong> Components were removed. '
                'Verify that associated tests are updated or removed.'
                '</div>'
            )

        if added_tests > 0:
            recommendations.append(
                '<div class="alert alert-success">'
                '✓ <strong>Good:</strong> New tests detected. '
                'Ensure they cover all new functionality.'
                '</div>'
            )

        return "\n".join(recommendations) if recommendations else \
               '<div class="alert alert-info">No specific test coverage concerns detected.</div>'

    def _generate_recommendations(self, impact: Dict) -> str:
        """Generate general recommendations based on impact analysis."""
        recommendations = []

        total_changes = impact['changes']['total']

        if total_changes > 100:
            recommendations.append(
                '<li class="warning">⚠️ Large number of changes detected ({} lines). '
                'Consider breaking this into smaller, incremental updates for easier review.</li>'
                .format(total_changes)
            )

        if len(impact['components']['removed']) > 0:
            recommendations.append(
                '<li class="warning">⚠️ Components removed: {}. '
                'Verify all dependencies are updated and no orphaned references remain.</li>'
                .format(', '.join(f'<code>{c}</code>' for c in sorted(impact['components']['removed'])))
            )

        if len(impact['components']['added']) > 3:
            recommendations.append(
                '<li class="info">ℹ️ Multiple new components added ({}). '
                'Ensure integration points are well-defined and documented.</li>'
                .format(len(impact['components']['added']))
            )

        if len(impact['components']['modified']) > 5:
            recommendations.append(
                '<li class="info">ℹ️ Many components potentially affected ({}). '
                'Run comprehensive integration tests to verify compatibility.</li>'
                .format(len(impact['components']['modified']))
            )

        # Always recommend re-approval
        recommendations.append(
            '<li class="important">🔄 <strong>Re-approval required:</strong> '
            'These changes must be reviewed and approved before proceeding to implementation.</li>'
        )

        return "\n".join(recommendations)

    def generate_report(self):
        """Generate complete HTML diff report."""
        print("Loading pseudocode files...")
        self.load_files()

        print("Analyzing impact...")
        impact = self.analyze_impact()

        print("Generating diff visualization...")
        html_diff = self.generate_html_diff()

        print("Creating impact analysis...")
        impact_html = self.generate_impact_html(impact)

        # Combine into full report with styling
        full_report = self._create_full_report(html_diff, impact_html, impact)

        # Write report
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w') as f:
            f.write(full_report)

        print(f"\n✓ Diff report generated: {self.output_path}")

        # Print summary
        self._print_summary(impact)

    def _create_full_report(self, html_diff: str, impact_html: str, impact: Dict) -> str:
        """Create full HTML report with styling."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pseudocode Diff Report - {self.original_path.stem} vs {self.updated_path.stem}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Pseudocode Diff Report</h1>
            <div class="file-info">
                <div class="file-box original">
                    <strong>Original:</strong> {self.original_path.name}
                </div>
                <div class="arrow">→</div>
                <div class="file-box updated">
                    <strong>Updated:</strong> {self.updated_path.name}
                </div>
            </div>
            <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>

        {impact_html}

        <div class="diff-section">
            <h2>Detailed Diff</h2>
            {html_diff}
        </div>

        <footer>
            <p>Generated by workspace-hub pseudocode_diff.py</p>
        </footer>
    </div>
</body>
</html>"""

    def _get_css_styles(self) -> str:
        """Get CSS styles for the report."""
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        h2 {
            color: #34495e;
            margin: 20px 0 10px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        h3 {
            color: #34495e;
            margin: 15px 0 10px 0;
        }
        h4 {
            color: #7f8c8d;
            margin: 10px 0 5px 0;
        }
        .file-info {
            display: flex;
            align-items: center;
            gap: 15px;
            margin: 15px 0;
        }
        .file-box {
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
        }
        .file-box.original {
            background: #ffe6e6;
            border: 1px solid #ffcccc;
        }
        .file-box.updated {
            background: #e6ffe6;
            border: 1px solid #ccffcc;
        }
        .arrow {
            font-size: 24px;
            color: #3498db;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 10px;
        }
        .impact-analysis, .diff-section {
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card-number {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .card-label {
            font-size: 14px;
            color: #7f8c8d;
        }
        .card.additions {
            background: #d4edda;
            border: 1px solid #c3e6cb;
        }
        .card.additions .card-number { color: #155724; }
        .card.deletions {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        .card.deletions .card-number { color: #721c24; }
        .card.total-changes {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
        }
        .card.total-changes .card-number { color: #0c5460; }
        .components-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 15px 0;
        }
        .component-category {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #dee2e6;
        }
        ul {
            list-style-position: inside;
            margin: 10px 0;
        }
        li {
            padding: 5px 0;
        }
        li.none {
            color: #7f8c8d;
            font-style: italic;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 13px;
        }
        .test-section {
            margin: 15px 0;
        }
        .test-stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .test-stats p {
            margin: 5px 0;
        }
        .alert {
            padding: 12px 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }
        .alert-warning {
            background: #fff3cd;
            border-left-color: #ffc107;
            color: #856404;
        }
        .alert-info {
            background: #d1ecf1;
            border-left-color: #17a2b8;
            color: #0c5460;
        }
        .alert-success {
            background: #d4edda;
            border-left-color: #28a745;
            color: #155724;
        }
        .recommendations {
            margin: 20px 0;
        }
        .recommendations ul {
            list-style: none;
        }
        .recommendations li {
            padding: 10px;
            margin: 8px 0;
            border-radius: 5px;
        }
        .recommendations li.warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }
        .recommendations li.info {
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
        }
        .recommendations li.important {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }
        table.diff {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 13px;
        }
        table.diff td {
            padding: 2px 5px;
            vertical-align: top;
        }
        table.diff .diff_header {
            background: #e9ecef;
            font-weight: bold;
        }
        table.diff .diff_next {
            background: #f8f9fa;
        }
        footer {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            font-size: 14px;
        }
        """

    def _print_summary(self, impact: Dict):
        """Print summary to console."""
        print("\n" + "="*60)
        print("DIFF SUMMARY")
        print("="*60)
        print(f"Changes: {impact['changes']['additions']} additions, "
              f"{impact['changes']['deletions']} deletions")
        print(f"Components: {len(impact['components']['added'])} added, "
              f"{len(impact['components']['removed'])} removed, "
              f"{len(impact['components']['modified'])} potentially modified")
        print(f"Tests: {len(impact['tests']['added'])} added, "
              f"{len(impact['tests']['removed'])} removed")
        print("="*60)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Compare pseudocode versions and generate diff report"
    )

    parser.add_argument(
        "--original",
        type=Path,
        required=True,
        help="Path to original pseudocode file"
    )

    parser.add_argument(
        "--updated",
        type=Path,
        required=True,
        help="Path to updated pseudocode file"
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output HTML diff report"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.original.exists():
        print(f"ERROR: Original file not found: {args.original}", file=sys.stderr)
        return 1

    if not args.updated.exists():
        print(f"ERROR: Updated file not found: {args.updated}", file=sys.stderr)
        return 1

    # Generate diff report
    diff_tool = PseudocodeDiff(args.original, args.updated, args.output)
    diff_tool.generate_report()

    return 0


if __name__ == "__main__":
    sys.exit(main())
