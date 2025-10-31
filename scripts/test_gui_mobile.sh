#!/bin/bash

# Mobile Testing for Solar Heating System GUI
PI_HOST="192.168.0.18"
GUI_URL="http://${PI_HOST}:5000"

echo "📱 Mobile Testing for Solar Heating System GUI"
echo "============================================="
echo ""

# Test 1: Mobile User Agent
echo "📊 Test 1: Mobile User Agent"
echo "----------------------------"
curl -s -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1" \
  "${GUI_URL}/api/system/status" | jq '.temperatures' 2>/dev/null || echo "Mobile API test failed"
echo ""

# Test 2: Mobile Viewport
echo "📊 Test 2: Mobile Viewport"
echo "--------------------------"
echo "Testing mobile viewport (375x667)..."
curl -s -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1" \
  "${GUI_URL}/" | grep -o "viewport.*width=375" || echo "Mobile viewport not detected"
echo ""

# Test 3: Touch Events
echo "📊 Test 3: Touch Events"
echo "-----------------------"
echo "Testing touch event support..."
curl -s "${GUI_URL}/" | grep -o "touchstart\|touchend\|touchmove" | head -3 || echo "Touch events not detected"
echo ""

# Test 4: Mobile Performance
echo "📊 Test 4: Mobile Performance"
echo "------------------------------"
echo "Testing mobile performance..."
time curl -s -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1" \
  "${GUI_URL}/api/system/status" > /dev/null
echo ""

echo "✅ Mobile testing completed!"
