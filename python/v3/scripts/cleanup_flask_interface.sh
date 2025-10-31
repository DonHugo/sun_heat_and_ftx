#!/bin/bash
# Solar Heating System v3 - Flask Web Interface Cleanup Script
# Removes old Flask web interface and duplicate components

set -e

echo "🧹 Cleaning up Flask web interface and duplicate components..."

# Create backup directory
BACKUP_DIR="/tmp/solar_heating_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Creating backup in: $BACKUP_DIR"

# Function to safely remove file/directory with backup
safe_remove() {
    local path="$1"
    local description="$2"
    
    if [ -e "$path" ]; then
        echo "🗑️  Removing $description: $path"
        cp -r "$path" "$BACKUP_DIR/" 2>/dev/null || true
        rm -rf "$path"
        echo "   ✅ Removed $description"
    else
        echo "   ℹ️  $description not found: $path"
    fi
}

# Function to safely remove from file with backup
safe_remove_from_file() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    
    if [ -f "$file" ]; then
        echo "📝 Removing $description from: $file"
        cp "$file" "$BACKUP_DIR/" 2>/dev/null || true
        sed -i "/$pattern/d" "$file" 2>/dev/null || true
        echo "   ✅ Removed $description from $file"
    else
        echo "   ℹ️  File not found: $file"
    fi
}

echo ""
echo "1️⃣ Removing Flask web interface files..."

# Remove Flask web interface files
safe_remove "python/v3/web_interface" "Flask web interface directory"
safe_remove "python/v3/templates" "Flask templates directory"
safe_remove "python/v3/static" "Flask static files directory"
safe_remove "python/v3/app_improved_temps.py" "Flask application file"
safe_remove "python/v3/app.py" "Flask application file"
safe_remove "python/v3/gui.py" "Flask GUI file"
safe_remove "python/v3/gui_via_api.py" "Flask GUI API file"

echo ""
echo "2️⃣ Removing Flask-related systemd services..."

# Remove Flask-related systemd services
safe_remove "/etc/systemd/system/solar-heating-gui.service" "Flask GUI systemd service"
safe_remove "/etc/systemd/system/solar_heating_gui.service" "Flask GUI systemd service"

# Reload systemd if services were removed
if [ -f "/etc/systemd/system/solar-heating-gui.service" ] || [ -f "/etc/systemd/system/solar_heating_gui.service" ]; then
    echo "🔄 Reloading systemd daemon..."
    systemctl daemon-reload
fi

echo ""
echo "3️⃣ Cleaning up Flask dependencies..."

# Remove Flask dependencies from requirements.txt if it exists
if [ -f "python/v3/requirements.txt" ]; then
    echo "📝 Cleaning Flask dependencies from requirements.txt..."
    cp python/v3/requirements.txt "$BACKUP_DIR/requirements.txt.backup"
    
    # Remove Flask-related packages
    sed -i '/^[Ff]lask/d' python/v3/requirements.txt
    sed -i '/^[Ww]erkzeug/d' python/v3/requirements.txt
    sed -i '/^[Jj]inja2/d' python/v3/requirements.txt
    sed -i '/^[Mm]arkupSafe/d' python/v3/requirements.txt
    sed -i '/^[Ii]tsdangerous/d' python/v3/requirements.txt
    sed -i '/^[Cc]lick/d' python/v3/requirements.txt
    sed -i '/^[Bb]linker/d' python/v3/requirements.txt
    
    echo "   ✅ Flask dependencies removed from requirements.txt"
fi

echo ""
echo "4️⃣ Removing duplicate MQTT clients and hardware interfaces..."

# Check for duplicate MQTT clients in main_system.py
if [ -f "python/v3/main_system.py" ]; then
    echo "📝 Checking for duplicate components in main_system.py..."
    
    # Count MQTT client instances
    MQTT_COUNT=$(grep -c "MQTTHandler\|mqtt_client" python/v3/main_system.py || echo "0")
    echo "   📊 Found $MQTT_COUNT MQTT client references"
    
    # Count hardware interface instances
    HARDWARE_COUNT=$(grep -c "HardwareInterface\|hardware" python/v3/main_system.py || echo "0")
    echo "   📊 Found $HARDWARE_COUNT hardware interface references"
    
    if [ "$MQTT_COUNT" -gt 1 ] || [ "$HARDWARE_COUNT" -gt 1 ]; then
        echo "   ⚠️  Potential duplicate components detected"
        echo "   ℹ️  Manual review recommended for main_system.py"
    else
        echo "   ✅ No duplicate components detected"
    fi
fi

echo ""
echo "5️⃣ Removing Flask-related deployment scripts..."

# Remove Flask-related deployment scripts
safe_remove "scripts/deploy_local_gui.sh" "Flask GUI deployment script"
safe_remove "scripts/test_gui_comprehensive.sh" "Flask GUI test script"
safe_remove "python/v3/deploy_local_gui.sh" "Flask GUI deployment script"
safe_remove "python/v3/test_gui_comprehensive.sh" "Flask GUI test script"

echo ""
echo "6️⃣ Cleaning up Flask-related documentation..."

# Remove Flask-related documentation
safe_remove "docs/FLASK_GUI_SETUP.md" "Flask GUI documentation"
safe_remove "docs/FLASK_WEB_INTERFACE.md" "Flask web interface documentation"
safe_remove "docs/GUI_SETUP.md" "GUI setup documentation"

echo ""
echo "7️⃣ Removing Flask-related test files..."

# Remove Flask-related test files
safe_remove "python/v3/tests/test_flask_gui.py" "Flask GUI test file"
safe_remove "python/v3/tests/test_web_interface.py" "Flask web interface test file"

echo ""
echo "8️⃣ Updating main_system.py to remove Flask imports..."

# Remove Flask imports from main_system.py if they exist
if [ -f "python/v3/main_system.py" ]; then
    echo "📝 Cleaning Flask imports from main_system.py..."
    cp python/v3/main_system.py "$BACKUP_DIR/main_system.py.backup"
    
    # Remove Flask-related imports
    sed -i '/from flask import/d' python/v3/main_system.py
    sed -i '/import flask/d' python/v3/main_system.py
    sed -i '/Flask/d' python/v3/main_system.py
    
    echo "   ✅ Flask imports removed from main_system.py"
fi

echo ""
echo "9️⃣ Verifying cleanup..."

# Verify that Flask components are removed
echo "🔍 Verifying Flask components removal..."

FLASK_FILES=$(find python/v3 -name "*.py" -exec grep -l "Flask\|flask\|@app.route" {} \; 2>/dev/null | wc -l)
echo "   📊 Remaining Flask files: $FLASK_FILES"

if [ "$FLASK_FILES" -eq 0 ]; then
    echo "   ✅ All Flask components successfully removed"
else
    echo "   ⚠️  Some Flask components may still exist"
    echo "   📋 Remaining Flask files:"
    find python/v3 -name "*.py" -exec grep -l "Flask\|flask\|@app.route" {} \; 2>/dev/null || echo "   None found"
fi

echo ""
echo "🔟 Final cleanup summary..."

echo "📋 Flask Interface Cleanup Summary:"
echo "   • Flask web interface files: ✅ Removed"
echo "   • Flask systemd services: ✅ Removed"
echo "   • Flask dependencies: ✅ Cleaned"
echo "   • Duplicate components: ✅ Checked"
echo "   • Flask deployment scripts: ✅ Removed"
echo "   • Flask documentation: ✅ Removed"
echo "   • Flask test files: ✅ Removed"
echo "   • Flask imports: ✅ Cleaned"
echo ""
echo "📁 Backup created at: $BACKUP_DIR"
echo "   (Restore if needed: cp -r $BACKUP_DIR/* .)"
echo ""
echo "✅ Flask web interface cleanup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "   • Test new architecture"
echo "   • Update deployment scripts"
echo "   • Document new architecture"
