#!/bin/bash

# Analyze Cleanup Candidates Script
# This script identifies files that might not be valuable to keep

echo "🔍 Analyzing Repository for Cleanup Candidates"
echo "=============================================="
echo ""

echo "📊 Repository Statistics:"
echo "========================"
echo "Total files: $(find . -type f | wc -l)"
echo "Total directories: $(find . -type d | wc -l)"
echo "Total size: $(du -sh . | cut -f1)"
echo ""

echo "📝 Documentation Analysis:"
echo "========================="
echo "Markdown files: $(find . -name "*.md" | wc -l)"
echo ""

echo "🔍 Potential Duplicate Documentation:"
echo "====================================="
echo "Enhanced/Comprehensive files:"
find . -name "*.md" | grep -E "(ENHANCED|COMPREHENSIVE|FINAL|SUCCESS)" | while read file; do
    echo "  📄 $file ($(wc -l < "$file") lines, $(du -h "$file" | cut -f1))"
done
echo ""

echo "🧪 Test Files Analysis:"
echo "======================"
echo "Test files: $(find . -name "*.py" | grep -E "(test_|demo_|example_)" | wc -l)"
echo ""

echo "🔍 Large Files (>100KB):"
echo "========================"
find . -type f -size +100k | while read file; do
    echo "  📄 $file ($(du -h "$file" | cut -f1))"
done
echo ""

echo "📋 Potential Cleanup Candidates:"
echo "==============================="
echo ""

echo "1. 📝 Duplicate Documentation:"
echo "   - ENHANCED_COLLABORATION_WORKFLOW.md (root vs docs/)"
echo "   - Multiple test strategy documents"
echo "   - Multiple test environment summaries"
echo ""

echo "2. 🧪 Test Files (35 files):"
echo "   - test_*.py files in python/v3/"
echo "   - demo_*.py files"
echo "   - example_*.py files"
echo ""

echo "3. 📊 Large Files:"
echo "   - main_system.py (main system file - keep)"
echo "   - Git pack files (normal - keep)"
echo ""

echo "4. 🔄 Potential Duplicates:"
echo "   - Multiple README files in different directories"
echo "   - Similar documentation in different locations"
echo ""

echo "💡 Recommendations:"
echo "==================="
echo ""
echo "✅ KEEP (Essential):"
echo "  • main_system.py (core system)"
echo "  • All .py files except test/demo files"
echo "  • Main README.md files"
echo "  • Core documentation"
echo ""
echo "❓ CONSIDER REMOVING:"
echo "  • Duplicate ENHANCED_COLLABORATION_WORKFLOW.md"
echo "  • Multiple test strategy documents (keep latest)"
echo "  • Multiple test environment summaries (keep latest)"
echo "  • Old test files that are no longer used"
echo ""
echo "🧪 TEST FILES TO REVIEW:"
echo "======================="
find . -name "*.py" | grep -E "(test_|demo_|example_)" | head -10 | while read file; do
    echo "  📄 $file"
done
echo ""

echo "📝 DUPLICATE DOCS TO REVIEW:"
echo "============================"
echo "  📄 ./ENHANCED_COLLABORATION_WORKFLOW.md"
echo "  📄 ./docs/ENHANCED_COLLABORATION_WORKFLOW.md"
echo "  📄 ./python/v3/ENHANCED_TEST_ENVIRONMENT_FINAL_SUMMARY.md"
echo "  📄 ./python/v3/ENHANCED_TEST_ENVIRONMENT_SUCCESS_SUMMARY.md"
echo "  📄 ./python/v3/ENHANCED_TEST_ENVIRONMENT_SUMMARY.md"
echo ""

echo "🔍 Next Steps:"
echo "=============="
echo "1. Review duplicate documentation files"
echo "2. Check if test files are still needed"
echo "3. Consolidate similar documentation"
echo "4. Remove outdated test strategies"
echo "5. Keep only the latest versions of summaries"
