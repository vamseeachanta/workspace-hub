#!/usr/bin/env bash
#
# Example usage scripts for doc-to-context converter
#

# Example 1: Convert single PDF
echo "Example 1: Converting single PDF document"
../doc2context.sh sample.pdf

# Example 2: Convert with custom output
echo "Example 2: Converting with custom output path"
../doc2context.sh sample.pdf -o custom_context.md

# Example 3: Export as JSON
echo "Example 3: Exporting as JSON"
../doc2context.sh sample.docx -f json

# Example 4: Batch convert all PDFs
echo "Example 4: Batch converting all PDFs in directory"
../doc2context.sh *.pdf -b

# Example 5: Mixed format batch conversion
echo "Example 5: Converting multiple formats"
../doc2context.sh reports/*.pdf documents/*.docx spreadsheets/*.xlsx -b

# Example 6: Integration with Claude Flow
echo "Example 6: Using with Claude Flow for enhanced parsing"
# Initialize Claude Flow swarm for document analysis
npx claude-flow@alpha swarm init --topology mesh --max-agents 3

# Convert document
../doc2context.sh complex_document.pdf

# Use Claude Flow to analyze the generated context
npx claude-flow@alpha task orchestrate \
  --task "Analyze context file and extract key insights" \
  --input "complex_document.context.md"

# Example 7: Pipeline processing
echo "Example 7: Processing documents in a pipeline"
for file in documents/*.pdf; do
    echo "Processing: $file"
    ../doc2context.sh "$file" -o "context/$(basename "$file" .pdf).md"

    # Optionally run AI analysis on each
    # npx claude-flow@alpha task orchestrate --task "Summarize" --input "context/$(basename "$file" .pdf).md"
done

echo "All examples completed!"
