#!/bin/bash
# Script to create GitHub labels for solar heating system project
# Requires GitHub CLI (gh) to be installed and authenticated

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Creating GitHub Labels for Solar Heating System..."
echo ""

# Function to create label
create_label() {
    local name=$1
    local color=$2
    local description=$3
    
    echo -n "Creating label: $name... "
    if gh label create "$name" --color "$color" --description "$description" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}already exists${NC}"
    fi
}

# Type Labels
echo "Creating Type Labels..."
create_label "bug" "d73a4a" "Something isn't working"
create_label "enhancement" "a2eeef" "Improvement to existing feature"
create_label "feature" "0e8a16" "New feature request"
create_label "documentation" "0075ca" "Documentation update"
create_label "testing" "fbca04" "Test-related work"

# Priority Labels
echo ""
echo "Creating Priority Labels..."
create_label "priority: critical" "b60205" "System down, data loss, security"
create_label "priority: high" "d93f0b" "Major functionality broken"
create_label "priority: medium" "fbca04" "Important but not urgent"
create_label "priority: low" "0e8a16" "Nice to have"

# Component Labels
echo ""
echo "Creating Component Labels..."
create_label "component: sensors" "1d76db" "Temperature sensors, RTD, MegaBAS"
create_label "component: pumps" "5319e7" "Pump control and logic"
create_label "component: mqtt" "0052cc" "MQTT communication"
create_label "component: home-assistant" "41b883" "Home Assistant integration"
create_label "component: watchdog" "d4c5f9" "Watchdog monitoring system"
create_label "component: gui" "ff6b6b" "Web interface, dashboards"
create_label "component: systemd" "c5def5" "Service management, deployment"
create_label "component: testing" "fbca04" "Test suite, test infrastructure"
create_label "component: logging" "7057ff" "Logging system, log management"
create_label "component: config" "bfd4f2" "Configuration management"
create_label "component: api" "0e8a16" "API server, REST endpoints"
create_label "component: energy" "fef2c0" "Energy calculations, tracking"
create_label "component: control" "5319e7" "Control logic, algorithms"
create_label "component: taskmaster" "e99695" "TaskMaster AI integration"

# Status Labels
echo ""
echo "Creating Status Labels..."
create_label "status: needs-info" "ffc107" "More information needed"
create_label "status: ready" "0e8a16" "Ready to work on"
create_label "status: in-progress" "1d76db" "Currently being worked on"
create_label "status: blocked" "d93f0b" "Blocked by other work"
create_label "status: review" "7057ff" "In code review"
create_label "status: testing" "fbca04" "In testing phase"
create_label "status: duplicate" "cfd3d7" "Duplicate of another issue"
create_label "status: wontfix" "ffffff" "Won't be fixed"

# Category Labels
echo ""
echo "Creating Category Labels..."
create_label "category: security" "b60205" "Security-related"
create_label "category: performance" "ff6b6b" "Performance improvement"
create_label "category: reliability" "0052cc" "Reliability/stability"
create_label "category: usability" "41b883" "User experience"
create_label "category: maintenance" "d4c5f9" "Code maintenance"
create_label "category: integration" "0e8a16" "External integration"
create_label "category: hardware" "fbca04" "Hardware-specific"

# Milestone Labels
echo ""
echo "Creating Milestone Labels..."
create_label "milestone: v3.1" "5319e7" "Bug fixes & stability"
create_label "milestone: v3.2" "1d76db" "Enhanced monitoring"
create_label "milestone: v3.3" "0052cc" "Advanced features"
create_label "milestone: v4.0" "0e8a16" "Major update"

# Special Labels
echo ""
echo "Creating Special Labels..."
create_label "good first issue" "7057ff" "Good for newcomers"
create_label "help wanted" "008672" "Extra attention needed"
create_label "question" "d876e3" "Question or discussion"
create_label "breaking change" "b60205" "Breaks backward compatibility"
create_label "dependencies" "0366d6" "Dependency updates"

echo ""
echo -e "${GREEN}✓ Label creation complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Create milestones with: gh api repos/:owner/:repo/milestones -f title='v3.1' -f due_on='2025-12-01T00:00:00Z'"
echo "2. Start creating issues using the templates in .github/ISSUE_TEMPLATE/"
echo "3. Use labels to categorize issues"


