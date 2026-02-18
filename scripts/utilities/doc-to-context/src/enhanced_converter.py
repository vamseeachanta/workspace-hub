#!/usr/bin/env python3
"""
Enhanced Document to Context Converter
Supports recursive directory processing, indexing, and smart organization
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import argparse

# Import base converter
from doc_to_context import DocumentToContextConverter, DocumentContent


class EnhancedConverter(DocumentToContextConverter):
    """Enhanced converter with directory processing and indexing."""

    def __init__(self):
        super().__init__()
        self.index = {
            'generated': datetime.now().isoformat(),
            'total_documents': 0,
            'total_size_bytes': 0,
            'documents': []
        }

    def process_directory(self,
                         input_dir: str,
                         output_dir: Optional[str] = None,
                         recursive: bool = False,
                         mirror_structure: bool = True,
                         create_index: bool = False,
                         combine_by_directory: bool = False,
                         output_format: str = 'markdown') -> Dict:
        """
        Process entire directory of documents.

        Args:
            input_dir: Source directory
            output_dir: Output directory (None = same as input)
            recursive: Process subdirectories
            mirror_structure: Preserve directory structure
            create_index: Generate index.json
            combine_by_directory: Combine docs in same dir
            output_format: 'markdown' or 'json'

        Returns:
            Processing statistics
        """
        input_path = Path(input_dir)

        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")

        # Determine output strategy
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path  # Mirror mode

        # Find all documents
        pattern = '**/*' if recursive else '*'
        all_files = []

        supported_extensions = {'.pdf', '.docx', '.xlsx', '.xlsm', '.html', '.htm'}

        for file_path in input_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                all_files.append(file_path)

        print(f"Found {len(all_files)} documents to process", file=sys.stderr)

        # Process each file
        stats = {
            'total_files': len(all_files),
            'processed': 0,
            'failed': 0,
            'skipped': 0
        }

        # Group by directory if combining
        if combine_by_directory:
            by_dir = self._group_by_directory(all_files)
            for dir_path, files in by_dir.items():
                self._process_directory_group(
                    files, dir_path, input_path, output_path,
                    output_format, stats
                )
        else:
            for file_path in all_files:
                self._process_single_file(
                    file_path, input_path, output_path,
                    mirror_structure, output_format, stats
                )

        # Create index if requested
        if create_index:
            self._create_index(output_path)

        return stats

    def _group_by_directory(self, files: List[Path]) -> Dict[Path, List[Path]]:
        """Group files by their parent directory."""
        by_dir = {}
        for file_path in files:
            dir_path = file_path.parent
            if dir_path not in by_dir:
                by_dir[dir_path] = []
            by_dir[dir_path].append(file_path)
        return by_dir

    def _process_directory_group(self,
                                 files: List[Path],
                                 dir_path: Path,
                                 input_root: Path,
                                 output_root: Path,
                                 output_format: str,
                                 stats: Dict):
        """Process and combine all files in a directory."""
        print(f"\nProcessing directory: {dir_path}", file=sys.stderr)

        combined_content = []
        combined_tables = []
        combined_formulas = []
        metadata_list = []

        for file_path in files:
            try:
                print(f"  Processing: {file_path.name}", file=sys.stderr)
                content = self._parse_file(file_path)

                combined_content.append(f"\n## Document: {file_path.name}\n")
                combined_content.append(content.text)

                # Add tables with source reference
                for table in content.tables:
                    table['source_file'] = file_path.name
                    combined_tables.append(table)

                # Add formulas with source reference
                for formula in content.formulas:
                    formula['source_file'] = file_path.name
                    combined_formulas.append(formula)

                metadata_list.append(content.metadata)
                stats['processed'] += 1

            except Exception as e:
                print(f"  Error processing {file_path.name}: {e}", file=sys.stderr)
                stats['failed'] += 1

        # Create combined output
        if combined_content:
            relative_dir = dir_path.relative_to(input_root)
            output_dir = output_root / relative_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            # Combined filename based on directory
            combined_name = str(relative_dir).replace('/', '_').replace('\\', '_')
            output_file = output_dir / f"{combined_name}_combined.md"

            self._write_combined_markdown(
                output_file,
                combined_content,
                combined_tables,
                combined_formulas,
                metadata_list
            )

            print(f"  Created: {output_file}", file=sys.stderr)

    def _process_single_file(self,
                            file_path: Path,
                            input_root: Path,
                            output_root: Path,
                            mirror_structure: bool,
                            output_format: str,
                            stats: Dict):
        """Process a single file."""
        try:
            print(f"Processing: {file_path}", file=sys.stderr)

            # Determine output path
            if mirror_structure:
                relative_path = file_path.relative_to(input_root)
                output_dir = output_root / relative_path.parent
                output_dir.mkdir(parents=True, exist_ok=True)

                if output_format == 'markdown':
                    output_file = output_dir / f"{file_path.stem}.context.md"
                else:
                    output_file = output_dir / f"{file_path.stem}.json"
            else:
                if output_format == 'markdown':
                    output_file = output_root / f"{file_path.stem}.context.md"
                else:
                    output_file = output_root / f"{file_path.stem}.json"

            # Convert
            content = self.convert(str(file_path), str(output_file), output_format)

            # Add to index
            self.index['documents'].append({
                'source': str(file_path),
                'output': str(output_file),
                'format': content.metadata.format,
                'size_bytes': content.metadata.size_bytes,
                'page_count': content.metadata.page_count,
                'checksum': content.metadata.checksum
            })

            self.index['total_documents'] += 1
            self.index['total_size_bytes'] += content.metadata.size_bytes

            stats['processed'] += 1

        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            stats['failed'] += 1

    def _parse_file(self, file_path: Path) -> DocumentContent:
        """Parse file without writing output."""
        parser = self.select_parser(file_path)
        if not parser:
            raise ValueError(f"No parser available for {file_path}")
        return parser.parse(file_path)

    def _write_combined_markdown(self,
                                 output_file: Path,
                                 content_parts: List[str],
                                 tables: List[Dict],
                                 formulas: List[Dict],
                                 metadata_list: List):
        """Write combined markdown file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("---\n")
            f.write("# Combined Document Context\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Documents: {len(metadata_list)}\n")
            f.write("---\n\n")

            # Summary
            f.write("## Document Summary\n\n")
            for metadata in metadata_list:
                f.write(f"- **{metadata.filename}** ({metadata.format}, ")
                f.write(f"{metadata.page_count} pages)\n")
            f.write("\n")

            # Combined content
            f.write("## Combined Content\n\n")
            f.write('\n'.join(content_parts))

            # Tables
            if tables:
                f.write("\n\n## Tables\n\n")
                for i, table in enumerate(tables, 1):
                    f.write(f"### Table {i} (from {table['source_file']})\n\n")
                    f.write(table['markdown'])
                    f.write("\n\n")

            # Formulas
            if formulas:
                f.write("\n## Formulas\n\n")
                for formula in formulas:
                    f.write(f"- **{formula['cell']}** ({formula['source_file']}): ")
                    f.write(f"`{formula['formula']}`\n")

    def _create_index(self, output_dir: Path):
        """Create index.json file."""
        index_file = output_dir / '_index.json'

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

        print(f"\nIndex created: {index_file}", file=sys.stderr)


def main():
    """Enhanced CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Enhanced Document to Context Converter with directory support'
    )

    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-f', '--format', choices=['markdown', 'json'],
                       default='markdown', help='Output format')

    # Directory processing options
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Process directories recursively')
    parser.add_argument('--mirror-structure', action='store_true',
                       help='Mirror input directory structure')
    parser.add_argument('--create-index', action='store_true',
                       help='Create index.json file')
    parser.add_argument('--combine-by-directory', action='store_true',
                       help='Combine documents in same directory')

    args = parser.parse_args()

    converter = EnhancedConverter()
    input_path = Path(args.input)

    # Check if input is directory
    if input_path.is_dir():
        stats = converter.process_directory(
            args.input,
            args.output,
            recursive=args.recursive,
            mirror_structure=args.mirror_structure or not args.output,
            create_index=args.create_index,
            combine_by_directory=args.combine_by_directory,
            output_format=args.format
        )

        print("\n" + "="*60)
        print("Processing Complete!")
        print("="*60)
        print(f"Total files: {stats['total_files']}")
        print(f"Processed: {stats['processed']}")
        print(f"Failed: {stats['failed']}")
        print(f"Skipped: {stats['skipped']}")

    else:
        # Single file mode
        converter.convert(args.input, args.output, args.format)


if __name__ == '__main__':
    main()
