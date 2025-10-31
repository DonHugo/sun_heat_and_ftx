#!/bin/bash
#
# Dependency Verification Script
# Verifies that all dependencies from requirements.txt are installed in production venv
#
# Usage: ./scripts/verify_deps.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Production environment settings
PROD_VENV="/opt/solar_heating_v3"
PROD_PIP="$PROD_VENV/bin/pip3"
REQUIREMENTS_FILE="python/v3/requirements.txt"

echo "======================================"
echo "Dependency Verification"
echo "======================================"
echo ""

# Check if requirements.txt exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${RED}❌ requirements.txt not found at $REQUIREMENTS_FILE${NC}"
    exit 1
fi

echo "Requirements file: $REQUIREMENTS_FILE"
echo ""

# Check if connected to Pi
echo "Checking connection to Raspberry Pi..."
if command -v ssh &> /dev/null && ssh pi@192.168.0.18 "hostname" &> /dev/null; then
    PI_CONNECTED=true
    echo -e "${GREEN}✅ Connected to Raspberry Pi${NC}"
else
    PI_CONNECTED=false
    echo -e "${YELLOW}⚠️  Not connected to Raspberry Pi${NC}"
    echo "   Will check local environment instead"
fi

echo ""

# Parse requirements.txt and check each package
echo "Checking dependencies..."
echo "--------------------------------------"

TOTAL=0
INSTALLED=0
MISSING=0
MISMATCHED=0

while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    
    # Extract package name and version
    PACKAGE=$(echo "$line" | sed 's/[<>=].*//' | tr -d '[:space:]')
    
    # Skip if package name is empty
    [ -z "$PACKAGE" ] && continue
    
    TOTAL=$((TOTAL + 1))
    
    # Check if package is installed
    if [ "$PI_CONNECTED" = true ]; then
        # Check on Raspberry Pi
        if ssh pi@192.168.0.18 "$PROD_PIP show $PACKAGE" &> /dev/null; then
            INSTALLED_VERSION=$(ssh pi@192.168.0.18 "$PROD_PIP show $PACKAGE 2>/dev/null | grep '^Version:' | awk '{print \$2}'")
            
            # Extract required version if specified
            if [[ "$line" =~ == ]]; then
                REQUIRED_VERSION=$(echo "$line" | sed 's/.*==\s*//' | tr -d '[:space:]')
                
                if [ "$INSTALLED_VERSION" == "$REQUIRED_VERSION" ]; then
                    echo -e "${GREEN}✅ $PACKAGE==$INSTALLED_VERSION${NC}"
                    INSTALLED=$((INSTALLED + 1))
                else
                    echo -e "${YELLOW}⚠️  $PACKAGE installed but version mismatch${NC}"
                    echo "   Required: $REQUIRED_VERSION, Installed: $INSTALLED_VERSION"
                    MISMATCHED=$((MISMATCHED + 1))
                fi
            else
                echo -e "${GREEN}✅ $PACKAGE ($INSTALLED_VERSION installed)${NC}"
                INSTALLED=$((INSTALLED + 1))
            fi
        else
            echo -e "${RED}❌ $PACKAGE NOT installed${NC}"
            MISSING=$((MISSING + 1))
        fi
    else
        # Check locally
        if pip3 show "$PACKAGE" &> /dev/null; then
            LOCAL_VERSION=$(pip3 show "$PACKAGE" 2>/dev/null | grep '^Version:' | awk '{print $2}')
            echo -e "${BLUE}ℹ️  $PACKAGE ($LOCAL_VERSION installed locally)${NC}"
            INSTALLED=$((INSTALLED + 1))
        else
            echo -e "${YELLOW}⚠️  $PACKAGE not found locally${NC}"
            MISSING=$((MISSING + 1))
        fi
    fi
    
done < "$REQUIREMENTS_FILE"

echo "--------------------------------------"
echo ""

# Summary
echo "======================================"
echo "Summary"
echo "======================================"
echo ""
echo "Total packages in requirements.txt: $TOTAL"
echo -e "${GREEN}Installed: $INSTALLED${NC}"
echo -e "${RED}Missing: $MISSING${NC}"
echo -e "${YELLOW}Version mismatches: $MISMATCHED${NC}"
echo ""

# Show installation commands for missing packages
if [ $MISSING -gt 0 ]; then
    echo "======================================"
    echo "How to Install Missing Packages"
    echo "======================================"
    echo ""
    
    if [ "$PI_CONNECTED" = true ]; then
        echo "Run these commands on the Raspberry Pi:"
        echo ""
        echo -e "${BLUE}# Install all missing packages:${NC}"
        echo "ssh pi@192.168.0.18 \"$PROD_PIP install -r ~/solar_heating/$REQUIREMENTS_FILE --break-system-packages\""
        echo ""
        echo -e "${BLUE}# Or install individually:${NC}"
        
        while IFS= read -r line || [ -n "$line" ]; do
            [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
            PACKAGE=$(echo "$line" | sed 's/[<>=].*//' | tr -d '[:space:]')
            [ -z "$PACKAGE" ] && continue
            
            if ! ssh pi@192.168.0.18 "$PROD_PIP show $PACKAGE" &> /dev/null; then
                echo "ssh pi@192.168.0.18 \"$PROD_PIP install '$line' --break-system-packages\""
            fi
        done < "$REQUIREMENTS_FILE"
    else
        echo "Connect to Raspberry Pi first:"
        echo "  ssh pi@192.168.0.18"
        echo ""
        echo "Then run:"
        echo "  $PROD_PIP install -r ~/solar_heating/$REQUIREMENTS_FILE --break-system-packages"
    fi
    
    echo ""
fi

# Show version mismatch resolution
if [ $MISMATCHED -gt 0 ]; then
    echo "======================================"
    echo "How to Fix Version Mismatches"
    echo "======================================"
    echo ""
    echo "Update packages to required versions:"
    echo ""
    
    if [ "$PI_CONNECTED" = true ]; then
        while IFS= read -r line || [ -n "$line" ]; do
            [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
            PACKAGE=$(echo "$line" | sed 's/[<>=].*//' | tr -d '[:space:]')
            [ -z "$PACKAGE" ] && continue
            
            if [[ "$line" =~ == ]]; then
                REQUIRED_VERSION=$(echo "$line" | sed 's/.*==\s*//' | tr -d '[:space:]')
                if ssh pi@192.168.0.18 "$PROD_PIP show $PACKAGE" &> /dev/null; then
                    INSTALLED_VERSION=$(ssh pi@192.168.0.18 "$PROD_PIP show $PACKAGE 2>/dev/null | grep '^Version:' | awk '{print \$2}'")
                    if [ "$INSTALLED_VERSION" != "$REQUIRED_VERSION" ]; then
                        echo "ssh pi@192.168.0.18 \"$PROD_PIP install $PACKAGE==$REQUIRED_VERSION --break-system-packages\""
                    fi
                fi
            fi
        done < "$REQUIREMENTS_FILE"
    else
        echo "Connect to Raspberry Pi to fix version mismatches"
    fi
    
    echo ""
fi

# Final status
echo "======================================"
if [ $MISSING -eq 0 ] && [ $MISMATCHED -eq 0 ]; then
    echo -e "${GREEN}✅ All dependencies satisfied!${NC}"
    exit 0
elif [ $MISSING -gt 0 ]; then
    echo -e "${RED}❌ Missing dependencies detected${NC}"
    echo "   Install missing packages before deploying"
    exit 1
elif [ $MISMATCHED -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Version mismatches detected${NC}"
    echo "   Consider updating to required versions"
    exit 0
fi

