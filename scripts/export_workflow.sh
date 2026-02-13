#!/bin/bash
# Export Multi-Agent Workflow to Another Repository
# Usage: ./export_workflow.sh /path/to/target-repo [minimal|recommended|full]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory (where sun_heat_and_ftx repo is)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_REPO="$(dirname "$SCRIPT_DIR")"

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: Target repository path required${NC}"
    echo "Usage: $0 /path/to/target-repo [minimal|recommended|full]"
    echo ""
    echo "Export levels:"
    echo "  minimal     - Core workflow files only (3 files)"
    echo "  recommended - Core + templates + docs (default)"
    echo "  full        - Everything including scripts and references"
    exit 1
fi

TARGET_REPO="$1"
EXPORT_LEVEL="${2:-recommended}"

# Validate target repo
if [ ! -d "$TARGET_REPO" ]; then
    echo -e "${RED}Error: Target directory does not exist: $TARGET_REPO${NC}"
    exit 1
fi

if [ ! -d "$TARGET_REPO/.git" ]; then
    echo -e "${YELLOW}Warning: Target directory is not a git repository${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Multi-Agent Workflow Export                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Source: ${GREEN}$SOURCE_REPO${NC}"
echo -e "Target: ${GREEN}$TARGET_REPO${NC}"
echo -e "Level:  ${GREEN}$EXPORT_LEVEL${NC}"
echo ""

# Function to copy file with status
copy_file() {
    local src="$1"
    local dst="$2"
    
    if [ -f "$SOURCE_REPO/$src" ]; then
        mkdir -p "$(dirname "$TARGET_REPO/$dst")"
        cp "$SOURCE_REPO/$src" "$TARGET_REPO/$dst"
        echo -e "  ${GREEN}✓${NC} $dst"
    else
        echo -e "  ${YELLOW}⚠${NC} $src not found (skipping)"
    fi
}

# Export core files (always)
echo -e "${BLUE}[1/5] Copying Core Workflow Files...${NC}"
copy_file ".cursorrules" ".cursorrules"
copy_file "MULTI_AGENT_GUIDE.md" "MULTI_AGENT_GUIDE.md"
copy_file "AGENTS_README.md" "AGENTS_README.md"
echo ""

if [ "$EXPORT_LEVEL" = "minimal" ]; then
    echo -e "${GREEN}✓ Minimal export complete!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Customize .cursorrules for your project"
    echo "2. Update examples in MULTI_AGENT_GUIDE.md"
    echo "3. Test: @manager help"
    exit 0
fi

# Export agent templates
echo -e "${BLUE}[2/5] Copying Agent Templates...${NC}"
copy_file "python/v3/docs/agent_templates/MANAGER_TEMPLATE.md" "docs/agent_templates/MANAGER_TEMPLATE.md"
copy_file "python/v3/docs/agent_templates/COACH_TEMPLATE.md" "docs/agent_templates/COACH_TEMPLATE.md"
copy_file "python/v3/docs/agent_templates/REQUIREMENTS_TEMPLATE.md" "docs/agent_templates/REQUIREMENTS_TEMPLATE.md"
copy_file "python/v3/docs/agent_templates/ARCHITECTURE_TEMPLATE.md" "docs/agent_templates/ARCHITECTURE_TEMPLATE.md"
copy_file "python/v3/docs/agent_templates/TEST_PLAN_TEMPLATE.md" "docs/agent_templates/TEST_PLAN_TEMPLATE.md"
copy_file "python/v3/docs/agent_templates/IMPLEMENTATION_TEMPLATE.md" "docs/agent_templates/IMPLEMENTATION_TEMPLATE.md"
copy_file "python/v3/docs/agent_templates/REVIEW_TEMPLATE.md" "docs/agent_templates/REVIEW_TEMPLATE.md"
copy_file "python/v3/docs/agent_templates/VALIDATION_TEMPLATE.md" "docs/agent_templates/VALIDATION_TEMPLATE.md"
echo ""

# Export development docs
echo -e "${BLUE}[3/5] Copying Development Documentation...${NC}"
copy_file "docs/development/PRE_DEPLOYMENT_CHECKLIST.md" "docs/development/PRE_DEPLOYMENT_CHECKLIST.md"
copy_file "docs/development/DEPLOYMENT_RUNBOOK.md" "docs/development/DEPLOYMENT_RUNBOOK.md"
copy_file "docs/development/PRODUCTION_ENVIRONMENT.md" "docs/development/PRODUCTION_ENVIRONMENT.md"
copy_file "docs/development/MULTI_AGENT_ISSUE_WORKFLOW.md" "docs/development/MULTI_AGENT_ISSUE_WORKFLOW.md"
echo ""

if [ "$EXPORT_LEVEL" = "recommended" ]; then
    echo -e "${GREEN}✓ Recommended export complete!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Customize .cursorrules for your project"
    echo "2. Update examples in all templates"
    echo "3. Customize PRE_DEPLOYMENT_CHECKLIST.md for your stack"
    echo "4. Set up GitHub labels: cd scripts && ./create_github_labels.sh"
    echo "5. Configure GitHub project board (see WORKFLOW_EXPORT_GUIDE.md)"
    exit 0
fi

# Export scripts (full mode)
echo -e "${BLUE}[4/5] Copying Helper Scripts...${NC}"
copy_file "scripts/test_production_env.sh" "scripts/test_production_env.sh"
copy_file "scripts/verify_deps.sh" "scripts/verify_deps.sh"
copy_file "scripts/create_github_labels.sh" "scripts/create_github_labels.sh"

# Make scripts executable
if [ -d "$TARGET_REPO/scripts" ]; then
    chmod +x "$TARGET_REPO/scripts"/*.sh 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Made scripts executable"
fi
echo ""

# Export reference docs (full mode)
echo -e "${BLUE}[5/5] Copying Reference Documentation...${NC}"
copy_file "SETUP_COMPLETE.md" "SETUP_COMPLETE.md"
copy_file "COACH_SUMMARY_WORKFLOW_IMPROVEMENTS.md" "COACH_SUMMARY_WORKFLOW_IMPROVEMENTS.md"
copy_file "GITHUB_INTEGRATION_README.md" "GITHUB_INTEGRATION_README.md"
copy_file "WORKFLOW_EXPORT_GUIDE.md" "WORKFLOW_EXPORT_GUIDE.md"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Full Export Complete!                                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Summary
echo -e "${BLUE}📊 Export Summary:${NC}"
echo "   Core Files:        3 files"
echo "   Agent Templates:   8 files"
echo "   Development Docs:  4 files"
echo "   Scripts:           3 files"
echo "   Reference Docs:    4 files"
echo "   ${GREEN}Total: 22 files${NC}"
echo ""

# Next steps
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo ""
echo "1. ${BLUE}Customize for your project:${NC}"
echo "   cd $TARGET_REPO"
echo "   # Edit .cursorrules - replace 'Solar heating' references"
echo "   # Update examples in MULTI_AGENT_GUIDE.md"
echo "   # Customize agent templates in docs/agent_templates/"
echo ""
echo "2. ${BLUE}Set up GitHub integration:${NC}"
echo "   cd $TARGET_REPO/scripts"
echo "   ./create_github_labels.sh"
echo "   # Then configure project board (see WORKFLOW_EXPORT_GUIDE.md)"
echo ""
echo "3. ${BLUE}Test the workflow:${NC}"
echo "   # Open repo in Cursor IDE"
echo "   # Try: @manager help"
echo "   # Try: @coach analyze workflow"
echo ""
echo "4. ${BLUE}Read the full guide:${NC}"
echo "   cat $TARGET_REPO/WORKFLOW_EXPORT_GUIDE.md"
echo ""
echo -e "${GREEN}✨ Ready to use multi-agent workflow in your new repo!${NC}"




