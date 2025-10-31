#!/bin/bash

# Comprehensive GUI Testing Runner
echo "🧪 Running All GUI Tests"
echo "========================"
echo ""

# Test 1: Basic API Tests
echo "📊 Running Basic API Tests..."
./scripts/test_gui_comprehensive.sh
echo ""

# Test 2: Performance Tests
echo "📊 Running Performance Tests..."
./scripts/test_gui_performance.sh
echo ""

# Test 3: Mobile Tests
echo "📊 Running Mobile Tests..."
./scripts/test_gui_mobile.sh
echo ""

# Test 4: Browser Tests (if Selenium is available)
echo "📊 Running Browser Tests..."
if command -v python3 &> /dev/null && python3 -c "import selenium" 2>/dev/null; then
    python3 scripts/test_gui_browser.py
else
    echo "⚠️  Selenium not available, skipping browser tests"
    echo "💡 Install Selenium: pip install selenium"
fi
echo ""

echo "✅ All GUI tests completed!"
echo ""
echo "🎯 Test Summary:"
echo "   • API Tests: ✅ Completed"
echo "   • Performance Tests: ✅ Completed"
echo "   • Mobile Tests: ✅ Completed"
echo "   • Browser Tests: ⚠️  Selenium required"
echo ""
echo "📱 Next Steps:"
echo "   • Install Selenium for browser testing"
echo "   • Test on real mobile devices"
echo "   • Test with real hardware"
echo "   • Monitor performance in production"
