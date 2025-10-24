#!/bin/bash

# GitHub Project Setup Script med GitHub CLI (New Projects)
# Automatisk setup av GitHub Project för solvärmesystemet

set -e  # Exit on any error

echo "🚀 GitHub Project Setup för Solvärmesystemet (New Projects)"
echo "============================================================"

# Kontrollera att gh är installerat
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) är inte installerat"
    echo "Installera det med: brew install gh"
    exit 1
fi

# Kontrollera att användaren är inloggad
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

# 1. Skapa GitHub Project (New Projects)
echo "📋 Skapar GitHub Project (New Projects)..."

# Skapa projekt med gh project create
PROJECT_NUMBER=$(gh project create \
    --title "Solar Heating System Development" \
    --body "Project management for solar heating system development with TDD approach" \
    --format json | jq -r '.number')

if [ -z "$PROJECT_NUMBER" ] || [ "$PROJECT_NUMBER" = "null" ]; then
    echo "❌ Kunde inte skapa projekt"
    exit 1
fi

echo "✅ Project skapat med nummer: $PROJECT_NUMBER"

# 2. Skapa kolumner
echo ""
echo "📊 Skapar projektkolumner..."

# Skapa kolumner med gh project column create
gh project column create $PROJECT_NUMBER --name "Backlog" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "To Do" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "In Progress" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "Review" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "Testing" > /dev/null 2>&1 || true
gh project column create $PROJECT_NUMBER --name "Done" > /dev/null 2>&1 || true

echo "✅ Kolumner skapade: Backlog, To Do, In Progress, Review, Testing, Done"

# 3. Skapa labels
echo ""
echo "🏷️  Skapar labels..."

# Typ av arbete
gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="bug" -f color="d73a4a" -f description="Något fungerar inte som det ska" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="enhancement" -f color="28a745" -f description="Förbättring av befintlig funktion" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="feature" -f color="0075ca" -f description="Ny funktion" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="documentation" -f color="6f42c1" -f description="Dokumentationsuppdatering" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="testing" -f color="ffc107" -f description="Testrelaterat arbete" > /dev/null 2>&1 || true

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

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="component: gui" -f color="17a2b8" -f description="Användargränssnitt" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="component: systemd" -f color="0056b3" -f description="Systemd-tjänster" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="component: logging" -f color="6c757d" -f description="Loggningssystem" > /dev/null 2>&1 || true

# Status
gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="status: needs-info" -f color="ffc107" -f description="Behöver mer information" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="status: ready" -f color="28a745" -f description="Redo att arbeta med" > /dev/null 2>&1 || true

gh api -X POST /repos/$REPO_OWNER/$REPO_NAME/labels \
    -f name="status: blocked" -f color="dc3545" -f description="Blockerat av annat arbete" > /dev/null 2>&1 || true

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

# 5. Skapa issues
echo ""
echo "📝 Skapar initial issues..."

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

# Issue 3: Service Startup Failures
gh issue create \
    --title "Service Startup Failures" \
    --body "Tjänster startar inte om loggkataloger saknas. Fixat med automatisk katalogskapande." \
    --label "bug,priority: medium,component: systemd" \
    --milestone $MILESTONE_V31

# Issue 4: Enhanced Error Recovery
gh issue create \
    --title "Enhanced Error Recovery" \
    --body "Förbättrad automatisk återhämtning vid fel. Implementera robustare felhantering." \
    --label "feature,priority: medium,component: watchdog" \
    --milestone $MILESTONE_V32

# Issue 5: Advanced Monitoring Dashboard
gh issue create \
    --title "Advanced Monitoring Dashboard" \
    --body "Utökad övervakningsdashboard i Home Assistant med fler metrics och visualiseringar." \
    --label "feature,priority: medium,component: home-assistant" \
    --milestone $MILESTONE_V32

# Issue 6: Energy Usage Analytics
gh issue create \
    --title "Energy Usage Analytics" \
    --body "Analys av energianvändning och effektivitet. Implementera datainsamling och rapporter." \
    --label "feature,priority: low,component: logging" \
    --milestone $MILESTONE_V33

# Issue 7: Improved Test Coverage
gh issue create \
    --title "Improved Test Coverage" \
    --body "Utöka testtäckning för alla komponenter. Implementera omfattande testsuiter." \
    --label "enhancement,priority: medium,component: testing" \
    --milestone $MILESTONE_V31

# Issue 8: Better Logging System
gh issue create \
    --title "Better Logging System" \
    --body "Förbättrat loggningssystem med strukturerade loggar och bättre felhantering." \
    --label "enhancement,priority: medium,component: logging" \
    --milestone $MILESTONE_V32

# Issue 9: Configuration Management
gh issue create \
    --title "Configuration Management" \
    --body "Bättre hantering av konfigurationsfiler med validering och backup." \
    --label "enhancement,priority: low,component: systemd" \
    --milestone $MILESTONE_V33

# Issue 10: User Manual Update
gh issue create \
    --title "User Manual Update" \
    --body "Uppdatera användarmanual med nya funktioner och förbättringar." \
    --label "documentation,priority: medium,component: documentation" \
    --milestone $MILESTONE_V31

echo "✅ Issues skapade"

# 6. Lägg till issues i projektet
echo ""
echo "📋 Lägger till issues i projektet..."

# Hämta alla issues och lägg till i projektet
ISSUES=$(gh issue list --json number --jq '.[].number')

for issue_num in $ISSUES; do
    # Lägg till issue i projektet
    gh project item-add $PROJECT_NUMBER --owner $REPO_OWNER --number $issue_num > /dev/null 2>&1 || true
done

echo "✅ Issues lagda till projektet"

# 7. Visa resultat
echo ""
echo "=============================================="
echo "✅ GitHub Project Setup Complete!"
echo ""
echo "📊 Vad som skapades:"
echo "  • 1 GitHub Project (New Projects)"
echo "  • 6 kolumner (Backlog → Done)"
echo "  • 16 labels (typ, prioritet, komponent, status)"
echo "  • 3 milestones (v3.1, v3.2, v3.3)"
echo "  • 10 initial issues"
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
