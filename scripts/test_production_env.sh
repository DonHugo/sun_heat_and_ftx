#!/bin/bash
#
# Production Environment Verification Script
# Tests that the production Python environment is properly configured
#
# Usage: ./scripts/test_production_env.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Production environment settings
PROD_VENV="/opt/solar_heating_v3"
PROD_PYTHON="$PROD_VENV/bin/python3"
PROD_PIP="$PROD_VENV/bin/pip3"
REQUIRED_PYTHON_VERSION="3.11"

echo "======================================"
echo "Production Environment Verification"
echo "======================================"
echo ""

# Test 1: Check if running on Raspberry Pi
echo "Test 1: Verifying Raspberry Pi..."
if command -v ssh &> /dev/null && ssh pi@192.168.0.18 "hostname" &> /dev/null; then
    PI_HOSTNAME=$(ssh pi@192.168.0.18 "hostname")
    echo -e "${GREEN}✅ Connected to Raspberry Pi: $PI_HOSTNAME${NC}"
else
    echo -e "${YELLOW}⚠️  Not connected to Raspberry Pi - running local checks only${NC}"
    PI_HOSTNAME="local"
fi

echo ""

# Test 2: Check if production venv exists
echo "Test 2: Checking production virtualenv..."
if [ "$PI_HOSTNAME" != "local" ]; then
    if ssh pi@192.168.0.18 "test -d $PROD_VENV"; then
        echo -e "${GREEN}✅ Production venv exists: $PROD_VENV${NC}"
    else
        echo -e "${RED}❌ Production venv NOT found: $PROD_VENV${NC}"
        echo "   Create it with: python3 -m venv $PROD_VENV"
        exit 1
    fi
else
    if [ -d "$PROD_VENV" ]; then
        echo -e "${GREEN}✅ Production venv exists locally: $PROD_VENV${NC}"
    else
        echo -e "${YELLOW}⚠️  Production venv not found locally${NC}"
        echo "   This is OK if you're not on the Raspberry Pi"
    fi
fi

echo ""

# Test 3: Check Python version
echo "Test 3: Checking Python version..."
if [ "$PI_HOSTNAME" != "local" ]; then
    PYTHON_VERSION=$(ssh pi@192.168.0.18 "$PROD_PYTHON --version 2>&1" | awk '{print $2}')
    PYTHON_MAJOR_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f1,2)
    
    if [ "$PYTHON_MAJOR_MINOR" == "$REQUIRED_PYTHON_VERSION" ]; then
        echo -e "${GREEN}✅ Python version: $PYTHON_VERSION (required: $REQUIRED_PYTHON_VERSION.x)${NC}"
    else
        echo -e "${YELLOW}⚠️  Python version: $PYTHON_VERSION (expected: $REQUIRED_PYTHON_VERSION.x)${NC}"
        echo "   This might still work, but test carefully"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping Python version check (not connected to Pi)${NC}"
fi

echo ""

# Test 4: Check if requirements.txt exists
echo "Test 4: Checking requirements.txt..."
if [ -f "python/v3/requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt found${NC}"
    PACKAGE_COUNT=$(wc -l < python/v3/requirements.txt | tr -d ' ')
    echo "   Packages listed: $PACKAGE_COUNT"
else
    echo -e "${RED}❌ requirements.txt NOT found${NC}"
    exit 1
fi

echo ""

# Test 5: Check if key packages are installed in production venv
echo "Test 5: Checking key packages in production venv..."
if [ "$PI_HOSTNAME" != "local" ]; then
    # Key packages that should be installed
    KEY_PACKAGES=("paho-mqtt" "w1thermsensor" "flask" "pydantic")
    
    for package in "${KEY_PACKAGES[@]}"; do
        if ssh pi@192.168.0.18 "$PROD_PIP list 2>/dev/null | grep -i '^$package '" &> /dev/null; then
            VERSION=$(ssh pi@192.168.0.18 "$PROD_PIP list 2>/dev/null | grep -i '^$package ' | awk '{print \$2}'")
            echo -e "${GREEN}✅ $package installed: v$VERSION${NC}"
        else
            echo -e "${RED}❌ $package NOT installed${NC}"
            echo "   Install with: $PROD_PIP install $package"
        fi
    done
else
    echo -e "${YELLOW}⚠️  Skipping package check (not connected to Pi)${NC}"
fi

echo ""

# Test 6: Test imports with production Python
echo "Test 6: Testing critical imports..."
if [ "$PI_HOSTNAME" != "local" ]; then
    # Test critical imports
    TEST_IMPORTS=(
        "import sys"
        "import paho.mqtt.client"
        "import flask"
        "import pydantic"
    )
    
    for import_cmd in "${TEST_IMPORTS[@]}"; do
        MODULE_NAME=$(echo $import_cmd | awk '{print $2}' | cut -d'.' -f1)
        if ssh pi@192.168.0.18 "$PROD_PYTHON -c '$import_cmd' 2>&1" &> /dev/null; then
            echo -e "${GREEN}✅ $MODULE_NAME imports successfully${NC}"
        else
            echo -e "${RED}❌ $MODULE_NAME import FAILED${NC}"
            ERROR=$(ssh pi@192.168.0.18 "$PROD_PYTHON -c '$import_cmd' 2>&1")
            echo "   Error: $ERROR"
        fi
    done
else
    echo -e "${YELLOW}⚠️  Skipping import test (not connected to Pi)${NC}"
fi

echo ""

# Test 7: Check solar heating directory
echo "Test 7: Checking solar heating directory..."
if [ "$PI_HOSTNAME" != "local" ]; then
    if ssh pi@192.168.0.18 "test -d ~/solar_heating/python/v3"; then
        echo -e "${GREEN}✅ Solar heating directory exists${NC}"
        FILE_COUNT=$(ssh pi@192.168.0.18 "find ~/solar_heating/python/v3 -name '*.py' | wc -l")
        echo "   Python files: $FILE_COUNT"
    else
        echo -e "${RED}❌ Solar heating directory NOT found${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Skipping directory check (not connected to Pi)${NC}"
fi

echo ""

# Test 8: Check systemd service
echo "Test 8: Checking systemd service..."
if [ "$PI_HOSTNAME" != "local" ]; then
    if ssh pi@192.168.0.18 "systemctl status solar_heating_v3.service" &> /dev/null; then
        STATUS=$(ssh pi@192.168.0.18 "systemctl is-active solar_heating_v3.service")
        if [ "$STATUS" == "active" ]; then
            echo -e "${GREEN}✅ Service is running: solar_heating_v3.service${NC}"
        else
            echo -e "${YELLOW}⚠️  Service exists but is not running: $STATUS${NC}"
        fi
    else
        echo -e "${RED}❌ Service NOT found: solar_heating_v3.service${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping service check (not connected to Pi)${NC}"
fi

echo ""

# Test 9: Check disk space
echo "Test 9: Checking disk space..."
if [ "$PI_HOSTNAME" != "local" ]; then
    DISK_USAGE=$(ssh pi@192.168.0.18 "df -h / | tail -1 | awk '{print \$5}' | sed 's/%//'")
    if [ "$DISK_USAGE" -lt 80 ]; then
        echo -e "${GREEN}✅ Disk space OK: ${DISK_USAGE}% used${NC}"
    elif [ "$DISK_USAGE" -lt 90 ]; then
        echo -e "${YELLOW}⚠️  Disk space high: ${DISK_USAGE}% used${NC}"
    else
        echo -e "${RED}❌ Disk space critical: ${DISK_USAGE}% used${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping disk space check (not connected to Pi)${NC}"
fi

echo ""
echo "======================================"
echo "Environment Verification Complete"
echo "======================================"
echo ""

# Summary
if [ "$PI_HOSTNAME" != "local" ]; then
    echo -e "${GREEN}✅ Production environment appears to be properly configured${NC}"
    echo ""
    echo "Quick Reference:"
    echo "  Python: $PROD_PYTHON"
    echo "  Pip: $PROD_PIP"
    echo "  Code: ~/solar_heating/python/v3"
    echo "  Service: solar_heating_v3.service"
else
    echo -e "${YELLOW}⚠️  Local environment checked${NC}"
    echo "   Connect to Raspberry Pi for full verification"
    echo "   Run: ssh pi@192.168.0.18"
fi

echo ""

