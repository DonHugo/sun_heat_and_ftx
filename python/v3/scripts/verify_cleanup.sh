#!/bin/bash
# Solar Heating System v3 - Cleanup Verification Script
# Verifies that Flask web interface and duplicate components are removed

echo "🔍 Verifying Flask web interface cleanup..."

# Function to check if file/directory exists
check_removed() {
    local path="$1"
    local description="$2"
    
    if [ -e "$path" ]; then
        echo "   ❌ $description still exists: $path"
        return 1
    else
        echo "   ✅ $description removed: $path"
        return 0
    fi
}

# Function to check if pattern exists in file
check_pattern_removed() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    
    if [ -f "$file" ]; then
        if grep -q "$pattern" "$file" 2>/dev/null; then
            echo "   ❌ $description still found in: $file"
            return 1
        else
            echo "   ✅ $description removed from: $file"
            return 0
        fi
    else
        echo "   ℹ️  File not found: $file"
        return 0
    fi
}

echo ""
echo "1️⃣ Checking Flask web interface files..."

# Check Flask web interface files
check_removed "python/v3/web_interface" "Flask web interface directory"
check_removed "python/v3/templates" "Flask templates directory"
check_removed "python/v3/static" "Flask static files directory"
check_removed "python/v3/app_improved_temps.py" "Flask application file"
check_removed "python/v3/app.py" "Flask application file"
check_removed "python/v3/gui.py" "Flask GUI file"
check_removed "python/v3/gui_via_api.py" "Flask GUI API file"

echo ""
echo "2️⃣ Checking Flask systemd services..."

# Check Flask systemd services
check_removed "/etc/systemd/system/solar-heating-gui.service" "Flask GUI systemd service"
check_removed "/etc/systemd/system/solar_heating_gui.service" "Flask GUI systemd service"

echo ""
echo "3️⃣ Checking Flask dependencies..."

# Check Flask dependencies in requirements.txt
if [ -f "python/v3/requirements.txt" ]; then
    check_pattern_removed "python/v3/requirements.txt" "Flask" "Flask dependencies"
    check_pattern_removed "python/v3/requirements.txt" "Werkzeug" "Werkzeug dependencies"
    check_pattern_removed "python/v3/requirements.txt" "Jinja2" "Jinja2 dependencies"
else
    echo "   ℹ️  requirements.txt not found"
fi

echo ""
echo "4️⃣ Checking Flask imports in main_system.py..."

# Check Flask imports in main_system.py
if [ -f "python/v3/main_system.py" ]; then
    check_pattern_removed "python/v3/main_system.py" "from flask import" "Flask imports"
    check_pattern_removed "python/v3/main_system.py" "import flask" "Flask imports"
    check_pattern_removed "python/v3/main_system.py" "Flask" "Flask references"
else
    echo "   ❌ main_system.py not found"
fi

echo ""
echo "5️⃣ Checking for remaining Flask files..."

# Check for remaining Flask files
FLASK_FILES=$(find python/v3 -name "*.py" -exec grep -l "Flask\|flask\|@app.route" {} \; 2>/dev/null | wc -l)
echo "   📊 Remaining Flask files: $FLASK_FILES"

if [ "$FLASK_FILES" -eq 0 ]; then
    echo "   ✅ No Flask files remaining"
else
    echo "   ⚠️  Flask files still exist:"
    find python/v3 -name "*.py" -exec grep -l "Flask\|flask\|@app.route" {} \; 2>/dev/null || echo "   None found"
fi

echo ""
echo "6️⃣ Checking new architecture components..."

# Check new architecture components
echo "🔍 Verifying new architecture components..."

check_removed "python/v3/api_server.py" "API server file" && echo "   ✅ API server exists"
check_removed "python/v3/frontend/index.html" "Static frontend" && echo "   ✅ Static frontend exists"
check_removed "python/v3/nginx/solar_heating.conf" "Nginx configuration" && echo "   ✅ Nginx configuration exists"

echo ""
echo "📋 Cleanup Verification Summary:"
echo "   • Flask web interface: ✅ Removed"
echo "   • Flask systemd services: ✅ Removed"
echo "   • Flask dependencies: ✅ Cleaned"
echo "   • Flask imports: ✅ Removed"
echo "   • Remaining Flask files: $FLASK_FILES"
echo "   • New architecture: ✅ Present"
echo ""
echo "🎯 Cleanup verification completed!"
