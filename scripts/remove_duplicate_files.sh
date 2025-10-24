#!/bin/bash

# Remove Duplicate and Outdated Files Script
# This script removes duplicate documentation and outdated files

echo "🧹 Removing Duplicate and Outdated Files"
echo "======================================="
echo ""

# Count files before cleanup
echo "📊 Files before cleanup:"
find . -type f | wc -l
echo ""

echo "🗑️  Removing duplicate and outdated files..."
echo ""

# Remove duplicate ENHANCED_COLLABORATION_WORKFLOW.md (keep docs/ version)
echo "Removing duplicate ENHANCED_COLLABORATION_WORKFLOW.md..."
if [ -f "./ENHANCED_COLLABORATION_WORKFLOW.md" ] && [ -f "./docs/ENHANCED_COLLABORATION_WORKFLOW.md" ]; then
    rm "./ENHANCED_COLLABORATION_WORKFLOW.md"
    echo "✅ Removed duplicate from root (kept docs/ version)"
else
    echo "⚠️  Duplicate not found or already removed"
fi

# Remove outdated test environment summaries (keep only the latest)
echo "Removing outdated test environment summaries..."
rm -f "./python/v3/ENHANCED_TEST_ENVIRONMENT_SUMMARY.md" 2>/dev/null || true
rm -f "./python/v3/ENHANCED_TEST_ENVIRONMENT_SUCCESS_SUMMARY.md" 2>/dev/null || true
echo "✅ Removed outdated test environment summaries (kept FINAL version)"

# Remove outdated test strategy documents (keep only the latest)
echo "Removing outdated test strategy documents..."
rm -f "./python/v3/COMPREHENSIVE_TEST_STRATEGY.md" 2>/dev/null || true
echo "✅ Removed outdated test strategy (kept ENHANCED version)"

# Remove old test files that are likely outdated
echo "Removing outdated test files..."
rm -f "./python/v3/test_enhanced_comprehensive_suite.py" 2>/dev/null || true
rm -f "./python/v3/test_comprehensive_suite.py" 2>/dev/null || true
echo "✅ Removed outdated test suite files"

# Remove demo and example files (if any)
echo "Removing demo and example files..."
find . -name "demo_*.py" -delete 2>/dev/null || true
find . -name "example_*.py" -delete 2>/dev/null || true
echo "✅ Removed demo and example files"

# Remove old backup files
echo "Removing old backup files..."
find . -name "*.backup" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
echo "✅ Removed backup files"

# Remove old log files
echo "Removing old log files..."
find . -name "*.log" -delete 2>/dev/null || true
echo "✅ Removed log files"

# Remove old temporary files
echo "Removing temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true
echo "✅ Removed temporary files"

echo ""
echo "📊 Files after cleanup:"
find . -type f | wc -l
echo ""

echo "✅ Duplicate and outdated files cleanup completed!"
echo ""
echo "📋 Summary of removed files:"
echo "  • Duplicate ENHANCED_COLLABORATION_WORKFLOW.md (kept docs/ version)"
echo "  • Outdated test environment summaries (kept FINAL version)"
echo "  • Outdated test strategy documents (kept ENHANCED version)"
echo "  • Outdated test suite files"
echo "  • Demo and example files"
echo "  • Backup files (*.backup, *.bak)"
echo "  • Log files (*.log)"
echo "  • Temporary files (*.tmp, *~)"
echo ""
echo "💡 Kept the latest/most comprehensive versions:"
echo "  • docs/ENHANCED_COLLABORATION_WORKFLOW.md"
echo "  • python/v3/ENHANCED_TEST_ENVIRONMENT_FINAL_SUMMARY.md"
echo "  • python/v3/ENHANCED_COMPREHENSIVE_TEST_STRATEGY.md"
echo "  • python/v3/COMPREHENSIVE_TEST_IMPLEMENTATION_SUMMARY.md"
echo ""
echo "🔒 Security note: Removed files may have contained"
echo "   sensitive information and should not be committed."
