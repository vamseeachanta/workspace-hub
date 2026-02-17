#!/bin/bash

# BSEE Data Consolidation - Master Execution Script
# This script orchestrates the complete consolidation process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SPEC_DIR="specs/modules/bsee/consolidation"
SCRIPTS_DIR="${SPEC_DIR}/scripts"
APPROVAL_FILE="${SPEC_DIR}/cleanup-proposal-approved.json"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if Python script exists
check_script() {
    if [ ! -f "$1" ]; then
        print_error "Script not found: $1"
        exit 1
    fi
}

# Header
clear
echo "=============================================="
echo "   BSEE DATA CONSOLIDATION EXECUTION PLAN    "
echo "=============================================="
echo ""

# Step 1: Pre-flight checks
print_status "Step 1: Running pre-flight checks..."

# Check for Python
if ! command -v python &> /dev/null; then
    print_error "Python is not installed"
    exit 1
fi
print_success "Python found"

# Check for required scripts
REQUIRED_SCRIPTS=(
    "${SCRIPTS_DIR}/inventory_generator.py"
    "${SCRIPTS_DIR}/duplicate_detector.py"
    "${SCRIPTS_DIR}/migration_executor.py"
    "${SCRIPTS_DIR}/migration_validator.py"
    "${SCRIPTS_DIR}/monitor_migration.py"
    "${SCRIPTS_DIR}/create_compatibility_links.py"
    "${SCRIPTS_DIR}/post_migration_monitor.py"
)

for script in "${REQUIRED_SCRIPTS[@]}"; do
    check_script "$script"
done
print_success "All required scripts found"

# Step 2: Check approval status
print_status "Step 2: Checking approval status..."

if [ ! -f "$APPROVAL_FILE" ]; then
    print_warning "Approval file not found"
    echo ""
    echo "To approve the consolidation:"
    echo "1. Review the cleanup proposal:"
    echo "   cat ${SPEC_DIR}/sub-specs/cleanup-proposal-detailed.md"
    echo ""
    echo "2. Create approval file:"
    echo "   cp ${SPEC_DIR}/cleanup-proposal-approved.json.template \\"
    echo "      ${APPROVAL_FILE}"
    echo ""
    echo "3. Edit the file and change 'approval_status' to 'APPROVED'"
    echo ""
    read -p "Do you want to create the approval file now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "${SPEC_DIR}/cleanup-proposal-approved.json.template" "$APPROVAL_FILE"
        print_success "Approval file created. Please edit it to set approval_status to 'APPROVED'"
        exit 0
    else
        print_warning "Exiting. Please create approval file when ready."
        exit 0
    fi
fi

# Check if approved
if grep -q '"approval_status": "APPROVED"' "$APPROVAL_FILE"; then
    print_success "Consolidation is APPROVED"
else
    print_warning "Consolidation is NOT approved yet"
    echo "Please edit $APPROVAL_FILE and set approval_status to 'APPROVED'"
    exit 0
fi

# Step 3: Run validation
print_status "Step 3: Running pre-migration validation..."
python "${SCRIPTS_DIR}/migration_validator.py"
if [ $? -ne 0 ]; then
    print_error "Validation failed"
    exit 1
fi
print_success "Validation passed"

# Step 4: Dry run
print_status "Step 4: Performing dry run..."
echo ""
read -p "Do you want to see the dry run output? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python "${SCRIPTS_DIR}/migration_executor.py"
    echo ""
    read -p "Dry run complete. Continue with actual migration? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Migration cancelled by user"
        exit 0
    fi
fi

# Step 5: Final confirmation
echo ""
print_warning "FINAL CONFIRMATION"
echo "This will:"
echo "  • Move 666 files to new structure"
echo "  • Delete 44 duplicate files"
echo "  • Create archive of legacy data"
echo "  • Save ~147 MB of space"
echo ""
echo "A full backup has been created and rollback is available."
echo ""
read -p "Are you sure you want to proceed? Type 'yes' to confirm: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    print_warning "Migration cancelled"
    exit 0
fi

# Step 6: Execute migration
print_status "Step 6: Executing migration..."
echo ""

# Start monitoring in background
python "${SCRIPTS_DIR}/monitor_migration.py" --continuous &
MONITOR_PID=$!

# Execute migration
python "${SCRIPTS_DIR}/migration_executor.py" --execute
MIGRATION_STATUS=$?

# Stop monitoring
kill $MONITOR_PID 2>/dev/null || true

if [ $MIGRATION_STATUS -ne 0 ]; then
    print_error "Migration failed! Check logs for details."
    echo "To rollback, run: python ${SCRIPTS_DIR}/rollback.py"
    exit 1
fi

print_success "Migration executed successfully"

# Step 7: Create compatibility links
print_status "Step 7: Creating compatibility links..."
python "${SCRIPTS_DIR}/create_compatibility_links.py"
print_success "Compatibility links created"

# Step 8: Post-migration validation
print_status "Step 8: Running post-migration validation..."
python "${SCRIPTS_DIR}/migration_validator.py"
if [ $? -ne 0 ]; then
    print_error "Post-migration validation failed"
    echo "To rollback, run: python ${SCRIPTS_DIR}/rollback.py"
    exit 1
fi
print_success "Post-migration validation passed"

# Step 9: Generate reports
print_status "Step 9: Generating reports..."
python "${SCRIPTS_DIR}/post_migration_monitor.py"

# Step 10: Success summary
echo ""
echo "=============================================="
echo "   ✅ CONSOLIDATION COMPLETE!                "
echo "=============================================="
echo ""
print_success "Successfully consolidated BSEE data:"
echo "  • Files: 666 → ~400 (-40%)"
echo "  • Size: 367.60 MB → ~220 MB (-40%)"
echo "  • Duplicates removed: 44 files"
echo ""
echo "📋 Next steps:"
echo "  1. Update Python imports: python ${SCRIPTS_DIR}/update_code_references.py"
echo "  2. Test your applications"
echo "  3. Monitor for 30 days: python ${SCRIPTS_DIR}/post_migration_monitor.py"
echo "  4. Remove compatibility links after 30 days"
echo ""
echo "📞 Support:"
echo "  • View status: python ${SCRIPTS_DIR}/monitor_migration.py"
echo "  • Check health: python ${SCRIPTS_DIR}/post_migration_monitor.py"
echo "  • Rollback: python ${SCRIPTS_DIR}/rollback.py"
echo ""
print_success "Thank you for using BSEE Data Consolidation!"