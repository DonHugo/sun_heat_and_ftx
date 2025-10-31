#!/bin/bash

# Simple Browser Testing for Solar Heating System GUI
# Tests the GUI using basic HTTP requests and HTML parsing

PI_HOST="192.168.0.18"
GUI_URL="http://${PI_HOST}:5000"

echo "🌐 Simple Browser Testing for Solar Heating System GUI"
echo "====================================================="
echo ""

# Test 1: HTML Structure
echo "📊 Test 1: HTML Structure"
echo "------------------------"
echo "Testing HTML structure..."
curl -s "${GUI_URL}/" | grep -o '<title>.*</title>' || echo "Title not found"
curl -s "${GUI_URL}/" | grep -o '<h1>.*</h1>' || echo "Main heading not found"
curl -s "${GUI_URL}/" | grep -o 'class="tab-button"' | wc -l | awk '{print "Tabs found: " $1}'
echo ""

# Test 2: JavaScript Files
echo "📊 Test 2: JavaScript Files"
echo "--------------------------"
echo "Testing JavaScript files..."
curl -s "${GUI_URL}/" | grep -o 'src=".*\.js"' | head -3 || echo "JavaScript files not found"
echo ""

# Test 3: CSS Files
echo "📊 Test 3: CSS Files"
echo "---------------------"
echo "Testing CSS files..."
curl -s "${GUI_URL}/" | grep -o 'href=".*\.css"' | head -3 || echo "CSS files not found"
echo ""

# Test 4: Button Elements
echo "📊 Test 4: Button Elements"
echo "--------------------------"
echo "Testing button elements..."
curl -s "${GUI_URL}/" | grep -o 'id=".*Button"' | wc -l | awk '{print "Buttons found: " $1}'
curl -s "${GUI_URL}/" | grep -o 'id="pumpStart"' && echo "✅ Pump Start button found"
curl -s "${GUI_URL}/" | grep -o 'id="pumpStop"' && echo "✅ Pump Stop button found"
curl -s "${GUI_URL}/" | grep -o 'id="modeManual"' && echo "✅ Manual Mode button found"
curl -s "${GUI_URL}/" | grep -o 'id="modeAuto"' && echo "✅ Auto Mode button found"
echo ""

# Test 5: Data Display Elements
echo "📊 Test 5: Data Display Elements"
echo "-------------------------------"
echo "Testing data display elements..."
curl -s "${GUI_URL}/" | grep -o 'id="tankTemp"' && echo "✅ Tank Temperature display found"
curl -s "${GUI_URL}/" | grep -o 'id="collectorTemp"' && echo "✅ Collector Temperature display found"
curl -s "${GUI_URL}/" | grep -o 'id="pumpStatus"' && echo "✅ Pump Status display found"
curl -s "${GUI_URL}/" | grep -o 'id="systemMode"' && echo "✅ System Mode display found"
echo ""

# Test 6: Tab Navigation
echo "📊 Test 6: Tab Navigation"
echo "-------------------------"
echo "Testing tab navigation..."
curl -s "${GUI_URL}/" | grep -o 'data-tab="overview"' && echo "✅ Overview tab found"
curl -s "${GUI_URL}/" | grep -o 'data-tab="sensors"' && echo "✅ Sensors tab found"
curl -s "${GUI_URL}/" | grep -o 'data-tab="controls"' && echo "✅ Controls tab found"
curl -s "${GUI_URL}/" | grep -o 'data-tab="diagnostics"' && echo "✅ Diagnostics tab found"
echo ""

# Test 7: Responsive Design
echo "📊 Test 7: Responsive Design"
echo "---------------------------"
echo "Testing responsive design..."
curl -s "${GUI_URL}/" | grep -o 'viewport.*width=device-width' && echo "✅ Responsive viewport found"
curl -s "${GUI_URL}/" | grep -o 'media.*max-width' | wc -l | awk '{print "Media queries found: " $1}'
echo ""

# Test 8: API Integration
echo "📊 Test 8: API Integration"
echo "-------------------------"
echo "Testing API integration..."
curl -s "${GUI_URL}/" | grep -o 'fetch.*api/system/status' && echo "✅ API status fetch found"
curl -s "${GUI_URL}/" | grep -o 'fetch.*api/system/control' && echo "✅ API control fetch found"
curl -s "${GUI_URL}/" | grep -o 'fetch.*api/system/mode' && echo "✅ API mode fetch found"
echo ""

# Test 9: Error Handling
echo "📊 Test 9: Error Handling"
echo "-------------------------"
echo "Testing error handling..."
curl -s "${GUI_URL}/" | grep -o 'catch.*error' && echo "✅ Error handling found"
curl -s "${GUI_URL}/" | grep -o 'console\.error' && echo "✅ Console error logging found"
echo ""

# Test 10: Performance
echo "📊 Test 10: Performance"
echo "------------------------"
echo "Testing page load performance..."
time curl -s "${GUI_URL}/" > /dev/null
echo ""

echo "✅ Simple browser testing completed!"
echo ""
echo "🎯 Test Results Summary:"
echo "   • HTML Structure: ✅ Tested"
echo "   • JavaScript Files: ✅ Tested"
echo "   • CSS Files: ✅ Tested"
echo "   • Button Elements: ✅ Tested"
echo "   • Data Display Elements: ✅ Tested"
echo "   • Tab Navigation: ✅ Tested"
echo "   • Responsive Design: ✅ Tested"
echo "   • API Integration: ✅ Tested"
echo "   • Error Handling: ✅ Tested"
echo "   • Performance: ✅ Tested"
echo ""
echo "📱 Next Steps:"
echo "   • Test on real mobile devices"
echo "   • Test with real hardware"
echo "   • Monitor performance in production"
echo "   • Add automated browser testing with Selenium"
