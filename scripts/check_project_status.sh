#!/bin/bash

# Check GitHub Project Status
echo "🔍 GitHub Project Status Check"
echo "=============================="

# Check if gh is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    exit 1
fi

# Check if logged in
if ! gh auth status &> /dev/null; then
    echo "❌ Not logged in to GitHub CLI"
    exit 1
fi

echo "✅ GitHub CLI is installed and logged in"
echo ""

# Get repository info
REPO_OWNER=$(gh repo view --json owner -q .owner.login)
REPO_NAME=$(gh repo view --json name -q .name)

echo "📁 Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# List projects
echo "📋 Projects:"
gh project list --owner $REPO_OWNER
echo ""

# List issues
echo "📝 Issues:"
gh issue list
echo ""

# List milestones
echo "🎯 Milestones:"
gh api /repos/$REPO_OWNER/$REPO_NAME/milestones --jq '.[] | "\(.title): \(.open_issues) open issues"'
echo ""

# Show project details
echo "📊 Project Details:"
PROJECT_ID=$(gh project list --owner $REPO_OWNER --json number -q '.[0].number')
if [ ! -z "$PROJECT_ID" ]; then
    echo "Project ID: $PROJECT_ID"
    gh project view $PROJECT_ID --owner $REPO_OWNER
else
    echo "No projects found"
fi

echo ""
echo "🔗 Links:"
echo "  • Repository: https://github.com/$REPO_OWNER/$REPO_NAME"
echo "  • Issues: https://github.com/$REPO_OWNER/$REPO_NAME/issues"
echo "  • Milestones: https://github.com/$REPO_OWNER/$REPO_NAME/milestones"
echo "  • Projects: https://github.com/$REPO_OWNER/$REPO_NAME/projects"
