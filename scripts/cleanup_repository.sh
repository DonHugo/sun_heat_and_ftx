#!/bin/bash

# Repository Cleanup Script
# This script removes unnecessary files from the repository

echo "🧹 Repository Cleanup"
echo "===================="
echo ""

# Count files before cleanup
echo "📊 Files before cleanup:"
find . -type f | wc -l
echo ""

echo "🗑️  Removing unnecessary files..."
echo ""

# Remove .DS_Store files (macOS system files)
echo "Removing .DS_Store files..."
find . -name ".DS_Store" -delete
echo "✅ Removed .DS_Store files"

# Remove Python cache files
echo "Removing Python __pycache__ directories..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✅ Removed __pycache__ directories"

# Remove .pyc files
echo "Removing .pyc files..."
find . -name "*.pyc" -delete
echo "✅ Removed .pyc files"

# Remove virtual environments (should not be in git)
echo "Removing virtual environments..."
rm -rf python/v3/venv 2>/dev/null || true
rm -rf python/v3/test_env 2>/dev/null || true
rm -rf .venv 2>/dev/null || true
echo "✅ Removed virtual environments"

# Remove log files
echo "Removing log files..."
find . -name "*.log" -delete
echo "✅ Removed log files"

# Remove backup files
echo "Removing backup files..."
find . -name "*.backup" -delete
find . -name "*.bak" -delete
echo "✅ Removed backup files"

# Remove temporary files
echo "Removing temporary files..."
find . -name "*.tmp" -delete
find . -name "*~" -delete
echo "✅ Removed temporary files"

# Remove node_modules if any
echo "Removing node_modules..."
find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✅ Removed node_modules"

echo ""
echo "📊 Files after cleanup:"
find . -type f | wc -l
echo ""

echo "✅ Repository cleanup completed!"
echo ""
echo "📋 Summary of removed files:"
echo "  • .DS_Store files (macOS system files)"
echo "  • Python __pycache__ directories"
echo "  • .pyc compiled Python files"
echo "  • Virtual environments (venv, test_env)"
echo "  • Log files (*.log)"
echo "  • Backup files (*.backup, *.bak)"
echo "  • Temporary files (*.tmp, *~)"
echo "  • node_modules directories"
echo ""
echo "💡 These files should not be committed to git:"
echo "  • Virtual environments are recreated locally"
echo "  • Cache files are generated automatically"
echo "  • System files (.DS_Store) are OS-specific"
echo "  • Log files are runtime-generated"
echo ""
echo "🔒 Security note: Virtual environments may contain"
echo "   sensitive information and should never be committed."
