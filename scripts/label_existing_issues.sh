#!/bin/bash
# Label Existing GitHub Issues
# This script adds proper labels and milestones to unlabeled issues

set -e

echo "🏷️  Labeling Existing GitHub Issues..."
echo ""

# Critical issues first (19-22)
echo "=== Phase 1: Critical Issues ==="
echo "Issue #19: Energy Calculation Bug"
gh issue edit 19 --add-label "bug,priority: critical,component: energy" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #19 not found or already labeled"

echo "Issue #20: MQTT Connection Stability"
gh issue edit 20 --add-label "bug,priority: high,component: mqtt" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #20 not found or already labeled"

echo "Issue #21: Sensor Reading Errors"
gh issue edit 21 --add-label "bug,priority: high,component: sensors" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #21 not found or already labeled"

echo "Issue #22: Reduce Log Spam"
gh issue edit 22 --add-label "enhancement,priority: high,component: logging" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #22 not found or already labeled"

echo ""
echo "=== Phase 2: Architecture Redesign Issues (HIGH PRIORITY) ==="

echo "Issue #27: Design New REST API Endpoints"
gh issue edit 27 --add-label "feature,component: api,priority: high" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #27 not found or already labeled"

echo "Issue #28: Add REST API Server"
gh issue edit 28 --add-label "feature,component: api,priority: high" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #28 not found or already labeled"

echo "Issue #29: Create Static HTML/JS Frontend"
gh issue edit 29 --add-label "feature,component: gui,priority: high" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #29 not found or already labeled"

echo "Issue #33: Test New Architecture"
gh issue edit 33 --add-label "testing,component: testing,priority: high" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #33 not found or already labeled"

echo "Issue #35: Document New Architecture"
gh issue edit 35 --add-label "documentation,priority: high" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #35 not found or already labeled"

echo ""
echo "=== Phase 3: Architecture Support Issues (MEDIUM PRIORITY) ==="

echo "Issue #30: Set up Nginx"
gh issue edit 30 --add-label "enhancement,component: api,priority: medium" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #30 not found or already labeled"

echo "Issue #31: Remove Flask Web Interface"
gh issue edit 31 --add-label "enhancement,priority: medium" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #31 not found or already labeled"

echo "Issue #34: Update Deployment Scripts"
gh issue edit 34 --add-label "enhancement,priority: medium" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #34 not found or already labeled"

echo "Issue #23: PRD Documentation"
gh issue edit 23 --add-label "documentation,priority: medium" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #23 not found or already labeled"

echo ""
echo "=== Phase 4: Future Enhancement Issues (MEDIUM/LOW PRIORITY) ==="

echo "Issue #32: Implement WebSocket Support"
gh issue edit 32 --add-label "feature,component: api,priority: medium" --milestone "v3.2 - Enhanced Monitoring" || echo "⚠️  Issue #32 not found or already labeled"

echo "Issue #36: Improve Regression Testing"
gh issue edit 36 --add-label "testing,category: performance,priority: medium" --milestone "v3.2 - Enhanced Monitoring" || echo "⚠️  Issue #36 not found or already labeled"

echo "Issue #24: Local Web GUI for Pi"
gh issue edit 24 --add-label "feature,component: gui,priority: medium" --milestone "v3.2 - Enhanced Monitoring" || echo "⚠️  Issue #24 not found or already labeled"

echo "Issue #25: Add Sensors and Controllers Tab"
gh issue edit 25 --add-label "feature,component: gui,priority: low" --milestone "v3.2 - Enhanced Monitoring" || echo "⚠️  Issue #25 not found or already labeled"

echo "Issue #26: Analyze Current Architecture"
gh issue edit 26 --add-label "enhancement,priority: low" --milestone "v3.1 - Bug Fixes & Stability" || echo "⚠️  Issue #26 not found or already labeled"

echo ""
echo "✅ Issue labeling complete!"
echo ""
echo "Summary:"
echo "- 4 critical/high priority bugs labeled (v3.1)"
echo "- 5 high priority architecture issues labeled (v3.1)"
echo "- 4 medium priority support issues labeled (v3.1)"
echo "- 4 enhancement issues labeled (v3.2)"
echo "- 1 low priority issue labeled (v3.1)"
echo ""
echo "Next steps:"
echo "1. View labeled issues: gh issue list --milestone 'v3.1 - Bug Fixes & Stability'"
echo "2. Create security issues: See GITHUB_INTEGRATION_ACTION_PLAN.md Part 2"
echo "3. Start using multi-agent: @requirements [your request]"

