#!/bin/bash

# Comprehensive GUI Testing Framework
# Tests the Solar Heating System Local GUI

PI_HOST="192.168.0.18"
PI_USER="pi"
GUI_URL="http://${PI_HOST}:5000"

echo "🧪 Comprehensive GUI Testing Framework"
echo "======================================"
echo ""

# Test 1: Service Status
echo "📊 Test 1: Service Status"
echo "-------------------------"
ssh "${PI_USER}@${PI_HOST}" "sudo systemctl status solar-heating-gui.service --no-pager -l | head -5"
echo ""

# Test 2: API Endpoints
echo "📊 Test 2: API Endpoints"
echo "------------------------"
echo "Testing system status..."
curl -s "${GUI_URL}/api/system/status" | jq '.service_status, .mqtt_status, .hardware_status' 2>/dev/null || echo "Status check failed"
echo ""

# Test 3: Mode Control
echo "📊 Test 3: Mode Control"
echo "------------------------"
echo "Testing manual mode..."
curl -s -X POST "${GUI_URL}/api/system/mode" \
  -H "Content-Type: application/json" \
  -d '{"mode": "manual"}' | jq '.'
echo ""

echo "Testing auto mode..."
curl -s -X POST "${GUI_URL}/api/system/mode" \
  -H "Content-Type: application/json" \
  -d '{"mode": "auto"}' | jq '.'
echo ""

# Test 4: Pump Control
echo "📊 Test 4: Pump Control"
echo "------------------------"
echo "Testing pump start..."
curl -s -X POST "${GUI_URL}/api/system/control" \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start"}' | jq '.'
echo ""

echo "Testing pump stop..."
curl -s -X POST "${GUI_URL}/api/system/control" \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_stop"}' | jq '.'
echo ""

# Test 5: Temperature Data
echo "📊 Test 5: Temperature Data"
echo "---------------------------"
curl -s "${GUI_URL}/api/system/status" | jq '.temperatures' 2>/dev/null || echo "Temperature check failed"
echo ""

# Test 6: System State
echo "📊 Test 6: System State"
echo "-----------------------"
curl -s "${GUI_URL}/api/system/status" | jq '.system_state' 2>/dev/null || echo "System state check failed"
echo ""

# Test 7: Response Time
echo "📊 Test 7: Response Time"
echo "------------------------"
time curl -s "${GUI_URL}/api/system/status" > /dev/null
echo ""

# Test 8: Error Handling
echo "📊 Test 8: Error Handling"
echo "-------------------------"
echo "Testing invalid mode..."
curl -s -X POST "${GUI_URL}/api/system/mode" \
  -H "Content-Type: application/json" \
  -d '{"mode": "invalid"}' | jq '.'
echo ""

echo "Testing invalid control action..."
curl -s -X POST "${GUI_URL}/api/system/control" \
  -H "Content-Type: application/json" \
  -d '{"action": "invalid"}' | jq '.'
echo ""

echo "✅ Comprehensive GUI Testing Complete!"
echo ""
echo "🎯 Test Results Summary:"
echo "   • Service Status: Check if GUI service is running"
echo "   • API Endpoints: Test all API endpoints"
echo "   • Mode Control: Test mode switching"
echo "   • Pump Control: Test pump start/stop"
echo "   • Temperature Data: Test temperature readings"
echo "   • System State: Test system state updates"
echo "   • Response Time: Test API response speed"
echo "   • Error Handling: Test error responses"
echo ""
echo "📱 Next Steps:"
echo "   • Run automated browser tests"
echo "   • Test on mobile devices"
echo "   • Test with real hardware"
echo "   • Performance testing"
