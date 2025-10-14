#!/usr/bin/env bash
#
# Examples: Directory Processing with doc-to-context
#

set -e

echo "======================================"
echo "Directory Processing Examples"
echo "======================================"

# Example 1: Simple directory - mirror structure
echo -e "\n1. Simple directory (mirror structure)"
echo "   Input: docs/*.pdf"
echo "   Output: docs/*.context.md (next to originals)"
echo ""
python3 ../src/enhanced_converter.py docs/ --recursive --mirror-structure

# Example 2: Separate output tree
echo -e "\n2. Separate output directory"
echo "   Input: project_docs/"
echo "   Output: context/ (parallel structure)"
echo ""
python3 ../src/enhanced_converter.py project_docs/ \
    --output context/ \
    --recursive \
    --mirror-structure

# Example 3: Combined by directory
echo -e "\n3. Combine documents by directory"
echo "   Input: legal/contracts/2023/*.pdf"
echo "   Output: context/legal_contracts_2023_combined.md"
echo ""
python3 ../src/enhanced_converter.py project_docs/ \
    --output context/ \
    --recursive \
    --combine-by-directory

# Example 4: With index
echo -e "\n4. Create searchable index"
echo "   Input: all_documents/"
echo "   Output: context/ + _index.json"
echo ""
python3 ../src/enhanced_converter.py all_documents/ \
    --output context/ \
    --recursive \
    --mirror-structure \
    --create-index

# Example 5: JSON format for automation
echo -e "\n5. JSON format for automation pipeline"
echo "   Input: reports/"
echo "   Output: json_output/*.json"
echo ""
python3 ../src/enhanced_converter.py reports/ \
    --output json_output/ \
    --recursive \
    --format json

# Example 6: Complete AI-optimized setup
echo -e "\n6. Complete AI-optimized setup"
echo "   - Combines by directory"
echo "   - Creates index"
echo "   - Markdown format"
echo ""
python3 ../src/enhanced_converter.py large_project/ \
    --output ai_context/ \
    --recursive \
    --combine-by-directory \
    --create-index \
    --format markdown

echo -e "\n======================================"
echo "Examples completed!"
echo "======================================"

# Show resulting structure
echo -e "\nExample output structure:"
cat << 'EOF'

Input structure:
project_docs/
├── legal/
│   ├── contracts/
│   │   ├── 2023/
│   │   │   ├── contract_001.pdf
│   │   │   └── contract_002.pdf
│   │   └── 2024/
│   │       └── contract_003.pdf
│   └── compliance/
│       └── audit.docx
└── financial/
    └── quarterly/
        └── q1_2024.xlsx

Output structure (--combine-by-directory):
context/
├── _index.json
├── legal/
│   ├── contracts/
│   │   ├── 2023_combined.md          ← All 2023 contracts
│   │   └── 2024_combined.md          ← All 2024 contracts
│   └── compliance_combined.md         ← Compliance docs
└── financial/
    └── quarterly_combined.md          ← Financial reports

Output structure (--mirror-structure):
context/
├── _index.json
├── legal/
│   ├── contracts/
│   │   ├── 2023/
│   │   │   ├── contract_001.context.md
│   │   │   └── contract_002.context.md
│   │   └── 2024/
│   │       └── contract_003.context.md
│   └── compliance/
│       └── audit.context.md
└── financial/
    └── quarterly/
        └── q1_2024.context.md

EOF
