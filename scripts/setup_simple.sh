#!/bin/bash

# Enkel GitHub setup för solvärmesystemet
echo "🚀 Enkel GitHub Setup för Solvärmesystemet"
echo "==========================================="

# Kontrollera att gh är installerat och inloggad
if ! gh auth status &> /dev/null; then
    echo "❌ Du är inte inloggad i GitHub CLI"
    echo "Logga in med: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI är installerat och du är inloggad"
echo ""

# Hämta repository info
REPO_OWNER=$(gh repo view --json owner -q .owner.login)
REPO_NAME=$(gh repo view --json name -q .name)

echo "📁 Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# 1. Skapa GitHub Project
echo "📋 Skapar GitHub Project..."
PROJECT_NUMBER=$(gh project create --title "Solar Heating System Development" --owner $REPO_OWNER --format json | jq -r '.number')

if [ -z "$PROJECT_NUMBER" ] || [ "$PROJECT_NUMBER" = "null" ]; then
    echo "❌ Kunde inte skapa projekt"
    exit 1
fi

echo "✅ Project skapat med nummer: $PROJECT_NUMBER"

# 2. Skapa kolumner
echo ""
echo "📊 Skapar projektkolumner..."

gh project column create $PROJECT_NUMBER --name "Backlog" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "To Do" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "In Progress" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "Review" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "Testing" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "Done" > /dev/null 2>&1 || true

echo "✅ Kolumner skapade"

# 3. Skapa viktiga labels
echo ""
echo "🏷️  Skapar labels..."

# Typ av arbete
gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="bug" -f color="d73a4a" -f description="Något fungerar inte som det ska" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="feature" -f color="0075ca" -f description="Ny funktion" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="enhancement" -f color="28a745" -f description="Förbättring av befintlig funktion" > /dev/null 2>&1 || true

# Prioritet
gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="priority: high" -f color="d73a4a" -f description="Kritiskt för systemets funktion" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="priority: medium" -f color="ffc107" -f description="Viktigt men inte kritiskt" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="priority: low" -f color="28a745" -f description="Nice-to-have" > /dev/null 2>&1 || true

# Komponent
gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="component: sensors" -f color="0075ca" -f description="Temperatursensorer" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="component: pumps" -f color="28a745" -f description="Pumpkontroll" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="component: mqtt" -f color="6f42c1" -f description="MQTT-kommunikation" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="component: home-assistant" -f color="fd7e14" -f description="Home Assistant-integration" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="component: watchdog" -f color="dc3545" -f description="Övervakningssystem" > /dev/null 2>&1 || true

echo "✅ Labels skapade"

# 4. Skapa milestones
echo ""
echo "🎯 Skapar milestones..."

MILESTONE_V31=$(gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/milestones \
    -f title="v3.1 - Bug Fixes & Stability" \
    -f description="Kritiska bugfixes och stabilitetsförbättringar" \
    --jq '.number')

MILESTONE_V32=$(gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/milestones \
    -f title="v3.2 - Enhanced Monitoring" \
    -f description="Förbättrad övervakning och felhantering" \
    --jq '.number')

MILESTONE_V33=$(gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/milestones \
    -f title="v3.3 - Advanced Features" \
    -f description="Nya funktioner och förbättringar" \
    --jq '.number')

echo "✅ Milestones skapade: v3.1, v3.2, v3.3"

# 5. Skapa några viktiga issues
echo ""
echo "📝 Skapar viktiga issues..."

# Issue 1: MQTT Connection Leak
gh issue create \
    --title "MQTT Connection Leak" \
    --body "Systemet skapar för många MQTT-anslutningar över tid. Delvis fixat, behöver verifiering." \
    --label "bug,priority: high,component: mqtt" \
    --milestone $MILESTONE_V31

# Issue 2: Sensor Mapping Issues
gh issue create \
    --title "Sensor Mapping Issues" \
    --body "Vissa sensorer mappas inte korrekt, förhindrar pumpstart. Fixat i senaste commits, behöver testning." \
    --label "bug,priority: high,component: sensors" \
    --milestone $MILESTONE_V31

# Issue 3: Enhanced Error Recovery
gh issue create \
    --title "Enhanced Error Recovery" \
    --body "Förbättrad automatisk återhämtning vid fel. Implementera robustare felhantering." \
    --label "feature,priority: medium,component: watchdog" \
    --milestone $MILESTONE_V32

# Issue 4: Improved Test Coverage
gh issue create \
    --title "Improved Test Coverage" \
    --body "Utöka testtäckning för alla komponenter. Implementera omfattande testsuiter." \
    --label "enhancement,priority: medium,component: testing" \
    --milestone $MILESTONE_V31

echo "✅ Issues skapade"

# 6. Lägg till issues i projektet
echo ""
echo "📋 Lägger till issues i projektet..."

# Hämta alla issues och lägg till i projektet
ISSUES=$(gh issue list --json number --jq '.[].number')

for issue_num in $ISSUES; do
    gh project item-add $PROJECT_NUMBER --owner $REPO_OWNER --number $issue_num > /dev/null 2>&1 || true
done

echo "✅ Issues lagda till projektet"

# 7. Visa resultat
echo ""
echo "=============================================="
echo "✅ GitHub Project Setup Complete!"
echo ""
echo "📊 Vad som skapades:"
echo "  • 1 GitHub Project"
echo "  • 6 kolumner (Backlog → Done)"
echo "  • 10 labels (typ, prioritet, komponent)"
echo "  • 3 milestones (v3.1, v3.2, v3.3)"
echo "  • 4 initial issues"
echo ""
echo "🔗 Länkar:"
echo "  • Project: https://github.com/$REPO_OWNER/$REPO_NAME/projects"
echo "  • Issues: https://github.com/$REPO_OWNER/$REPO_NAME/issues"
echo "  • Milestones: https://github.com/$REPO_OWNER/$REPO_NAME/milestones"
echo ""
echo "🎯 Nästa steg:"
echo "  1. Gå till projektet och organisera issues"
echo "  2. Börja arbeta med högsta prioritet issues"
echo "  3. Följ workflow: Backlog → To Do → In Progress → Review → Testing → Done"
echo "=============================================="
