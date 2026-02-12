#!/bin/bash
# Frontend Implementation Readiness Check for Issue #44
# Run this before requesting Phase 2 validation

echo "=========================================="
echo "Issue #44 Frontend Implementation Check"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Check 1: Toggle switch in HTML
echo "[1/8] Checking for toggle switch in HTML..."
if grep -q "heater-toggle" python/v3/frontend/index.html; then
    echo "  ✅ PASS: Toggle switch found in HTML"
else
    echo "  ❌ FAIL: Toggle switch NOT found in HTML"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: Emergency stop removed from HTML
echo "[2/8] Checking emergency stop removed from HTML..."
if grep -q "handleEmergencyStop" python/v3/frontend/index.html; then
    echo "  ❌ FAIL: Emergency stop button still present in HTML"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ PASS: Emergency stop button removed from HTML"
fi

# Check 3: controlHeater function in JavaScript
echo "[3/8] Checking for controlHeater function in JavaScript..."
if grep -q "function controlHeater" python/v3/frontend/static/js/dashboard.js; then
    echo "  ✅ PASS: controlHeater function found in JavaScript"
else
    echo "  ❌ FAIL: controlHeater function NOT found in JavaScript"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: handleHeaterToggle function in JavaScript
echo "[4/8] Checking for handleHeaterToggle function in JavaScript..."
if grep -q "function handleHeaterToggle" python/v3/frontend/static/js/dashboard.js; then
    echo "  ✅ PASS: handleHeaterToggle function found in JavaScript"
else
    echo "  ❌ FAIL: handleHeaterToggle function NOT found in JavaScript"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: Emergency stop removed from JavaScript
echo "[5/8] Checking emergency stop removed from JavaScript..."
if grep -q "handleEmergencyStop" python/v3/frontend/static/js/dashboard.js; then
    echo "  ❌ FAIL: Emergency stop handlers still present in JavaScript"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ PASS: Emergency stop handlers removed from JavaScript"
fi

# Check 6: Toggle CSS styling
echo "[6/8] Checking for toggle switch CSS styling..."
if grep -q ".toggle" python/v3/frontend/static/css/style.css; then
    echo "  ✅ PASS: Toggle switch CSS styling found"
else
    echo "  ❌ FAIL: Toggle switch CSS styling NOT found"
    ERRORS=$((ERRORS + 1))
fi

# Check 7: Cache version updated
echo "[7/8] Checking cache version updated..."
if grep -q "dashboard.js?v=5" python/v3/frontend/index.html; then
    echo "  ✅ PASS: Cache version updated to v=5"
else
    echo "  ⚠️  WARNING: Cache version not updated (still v=4 or other)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 8: Backend files present
echo "[8/8] Checking backend implementation..."
if grep -q "heater_start" python/v3/api_models.py && grep -q "heater_start" python/v3/api_server.py; then
    echo "  ✅ PASS: Backend implementation present"
else
    echo "  ❌ FAIL: Backend implementation incomplete"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ READY FOR PHASE 2 VALIDATION"
    echo ""
    echo "Next steps:"
    echo "1. Commit your frontend changes"
    echo "2. Test manually in browser"
    echo "3. Contact @validator for Phase 2 validation"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  MOSTLY READY (with warnings)"
    echo ""
    echo "You can proceed, but address warnings if possible:"
    echo "- Update cache version to v=5 to avoid browser caching issues"
    exit 0
else
    echo "❌ NOT READY FOR PHASE 2"
    echo ""
    echo "Please complete the frontend implementation:"
    echo "- Review: python/v3/docs/validation/ISSUE_44_DEVELOPER_HANDOFF.md"
    echo "- Use code templates from: python/v3/docs/validation/ISSUE_44_VALIDATION_REPORT.md"
    exit 1
fi
