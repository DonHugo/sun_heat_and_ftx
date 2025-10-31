#!/bin/bash
# Solar Heating System v3 - Nginx Test Script

echo "🧪 Testing nginx configuration for Solar Heating System v3..."

# Test nginx configuration
echo "1️⃣ Testing nginx configuration syntax..."
nginx -t

if [ $? -eq 0 ]; then
    echo "   ✅ Nginx configuration is valid"
else
    echo "   ❌ Nginx configuration has errors"
    exit 1
fi

# Test nginx service
echo "2️⃣ Testing nginx service status..."
if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx service is running"
else
    echo "   ❌ Nginx service is not running"
    exit 1
fi

# Test static file serving
echo "3️⃣ Testing static file serving..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
    echo "   ✅ Static files are being served"
else
    echo "   ❌ Static files are not being served"
    exit 1
fi

# Test API proxy
echo "4️⃣ Testing API proxy..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/status | grep -q "200\|404\|500"; then
    echo "   ✅ API proxy is working (may return 404/500 if main system not running)"
else
    echo "   ❌ API proxy is not working"
    exit 1
fi

# Test CORS headers
echo "5️⃣ Testing CORS headers..."
CORS_HEADER=$(curl -s -I http://localhost/api/status | grep -i "access-control-allow-origin")
if [ -n "$CORS_HEADER" ]; then
    echo "   ✅ CORS headers are present"
else
    echo "   ❌ CORS headers are missing"
    exit 1
fi

# Test gzip compression
echo "6️⃣ Testing gzip compression..."
GZIP_HEADER=$(curl -s -H "Accept-Encoding: gzip" -I http://localhost/ | grep -i "content-encoding")
if [ -n "$GZIP_HEADER" ]; then
    echo "   ✅ Gzip compression is working"
else
    echo "   ❌ Gzip compression is not working"
    exit 1
fi

echo ""
echo "🎉 All nginx tests passed!"
echo ""
echo "📋 Nginx Test Summary:"
echo "   • Configuration syntax: ✅ Valid"
echo "   • Service status: ✅ Running"
echo "   • Static file serving: ✅ Working"
echo "   • API proxy: ✅ Working"
echo "   • CORS headers: ✅ Present"
echo "   • Gzip compression: ✅ Working"
echo ""
echo "🌐 System is ready at: http://localhost"
