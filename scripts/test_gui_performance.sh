#!/bin/bash

# Performance Testing for Solar Heating System GUI
PI_HOST="192.168.0.18"
GUI_URL="http://${PI_HOST}:5000"

echo "⚡ Performance Testing for Solar Heating System GUI"
echo "=================================================="
echo ""

# Test 1: Response Time
echo "📊 Test 1: API Response Time"
echo "---------------------------"
for i in {1..5}; do
    echo "Request $i:"
    time curl -s "${GUI_URL}/api/system/status" > /dev/null
    echo ""
done

# Test 2: Concurrent Requests
echo "📊 Test 2: Concurrent Requests"
echo "------------------------------"
echo "Testing 10 concurrent requests..."
for i in {1..10}; do
    curl -s "${GUI_URL}/api/system/status" > /dev/null &
done
wait
echo "✅ 10 concurrent requests completed"

# Test 3: Load Testing
echo "📊 Test 3: Load Testing"
echo "-----------------------"
echo "Testing 50 requests in sequence..."
start_time=$(date +%s)
for i in {1..50}; do
    curl -s "${GUI_URL}/api/system/status" > /dev/null
done
end_time=$(date +%s)
duration=$((end_time - start_time))
echo "✅ 50 requests completed in ${duration} seconds"
echo "📊 Average response time: $((duration * 1000 / 50))ms"

# Test 4: Memory Usage
echo "📊 Test 4: Memory Usage"
echo "-----------------------"
ssh pi@192.168.0.18 "ps aux | grep python3 | grep app_fixed_mode.py | awk '{print \$6, \$11}' | head -1"
echo ""

# Test 5: CPU Usage
echo "📊 Test 5: CPU Usage"
echo "---------------------"
ssh pi@192.168.0.18 "top -bn1 | grep python3 | grep app_fixed_mode.py | awk '{print \$9, \$10, \$11}' | head -1"
echo ""

echo "✅ Performance testing completed!"
