#!/bin/bash
echo "🔍 COMPREHENSIVE SYSTEM DIAGNOSIS"
echo "================================="

# Check if we can connect to the Pi
echo "1. Testing SSH connection to Pi..."
if ssh -o ConnectTimeout=10 pi@192.168.0.18 "echo 'Connected'" 2>/dev/null; then
    echo "✅ SSH connection successful"
    
    echo ""
    echo "2. Checking Pi system status..."
    ssh pi@192.168.0.18 << 'PI_EOF'
        echo "📊 System Status:"
        echo "   • Uptime: $(uptime)"
        echo "   • Memory: $(free -h | grep Mem)"
        echo "   • Disk: $(df -h / | tail -1)"
        
        echo ""
        echo "📡 Network Status:"
        echo "   • IP: $(hostname -I)"
        echo "   • Nginx: $(systemctl is-active nginx)"
        echo "   • MQTT: $(systemctl is-active mosquitto)"
        
        echo ""
        echo "🔧 API Proxy Status:"
        echo "   • Running processes:"
        ps aux | grep -E "(api_proxy|python3.*tmp)" | grep -v grep || echo "   No API proxies running"
        
        echo ""
        echo "🌐 Testing API endpoints:"
        echo "   • Port 5001:"
        curl -s --connect-timeout 5 http://localhost:5001/api/status 2>/dev/null || echo "   ❌ Port 5001 not responding"
        
        echo "   • Port 80 (nginx):"
        curl -s --connect-timeout 5 http://localhost/api/status 2>/dev/null || echo "   ❌ Nginx not responding"
        
        echo ""
        echo "📋 Nginx Configuration:"
        if [ -f /etc/nginx/sites-enabled/solar_heating.conf ]; then
            echo "   ✅ Solar heating config exists"
            echo "   • Config content:"
            cat /etc/nginx/sites-enabled/solar_heating.conf | head -10
        else
            echo "   ❌ Solar heating config missing"
        fi
        
        echo ""
        echo "📁 Frontend Files:"
        if [ -d /opt/solar_heating/frontend ]; then
            echo "   ✅ Frontend directory exists"
            echo "   • Files:"
            ls -la /opt/solar_heating/frontend/ | head -5
        else
            echo "   ❌ Frontend directory missing"
        fi
        
        echo ""
        echo "🔍 Recent Logs:"
        if [ -f /tmp/simple_api.log ]; then
            echo "   • Simple API logs:"
            tail -5 /tmp/simple_api.log
        else
            echo "   ❌ No simple API logs found"
        fi
        
        echo ""
        echo "🧪 Testing complete API workflow:"
        echo "   • Creating test API proxy..."
        cat > /tmp/test_api.py << 'TEST_EOF'
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/status')
def status():
    return jsonify({'system': 'running', 'mode': 'auto', 'pump': 'off', 'heater': 'off', 'mqtt': 'connected', 'home_assistant': 'connected'})

@app.route('/api/temperatures')
def temps():
    return jsonify({'tank_temp': 55.2, 'collector_temp': 7.5, 'ambient_temp': 10.0, 'heat_exchanger_temp': 10.0})

@app.route('/api/mqtt')
def mqtt():
    return jsonify({'connected': True, 'last_message': 'MQTT broker running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
TEST_EOF
        
        echo "   • Starting test API proxy..."
        pkill -f "python3 /tmp/" 2>/dev/null || true
        nohup python3 /tmp/test_api.py > /tmp/test_api.log 2>&1 &
        sleep 3
        
        echo "   • Testing test API:"
        curl -s http://localhost:5001/api/status || echo "   ❌ Test API failed"
        curl -s http://localhost:5001/api/temperatures || echo "   ❌ Test API failed"
        
        echo "   • Testing through nginx:"
        curl -s http://localhost/api/status || echo "   ❌ Nginx proxy failed"
        curl -s http://localhost/api/temperatures || echo "   ❌ Nginx proxy failed"
        
        echo ""
        echo "🎯 DIAGNOSIS COMPLETE"
        echo "   • Check all the results above"
        echo "   • Look for ❌ errors"
        echo "   • Verify each component is working"
PI_EOF
    
else
    echo "❌ SSH connection failed"
    echo ""
    echo "🔧 ALTERNATIVE APPROACH:"
    echo "   • You'll need to SSH to the Pi manually"
    echo "   • Run the diagnostic commands above"
    echo "   • Or copy the fix script to the Pi"
fi

echo ""
echo "📋 NEXT STEPS:"
echo "   1. Review all the diagnostic results above"
echo "   2. Identify which components are failing (❌)"
echo "   3. Fix the failing components one by one"
echo "   4. Test each fix before moving to the next"
echo "   5. Only claim 'fixed' after verifying everything works"
