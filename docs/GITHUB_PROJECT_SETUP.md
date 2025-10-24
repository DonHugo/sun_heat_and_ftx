# GitHub Project Setup Guide

Detta dokument visar steg-för-steg hur du sätter upp GitHub Project för solvärmesystemet.

## 🎯 **Steg 1: Skapa GitHub Project**

### **1.1 Gå till din GitHub repository**
- Öppna: `https://github.com/DonHugo/sun_heat_and_ftx`
- Klicka på **"Projects"** i menyn
- Klicka på **"New project"**

### **1.2 Välj projekttyp**
- Välj **"Table"** för flexibel projektvy
- Namnge projektet: **"Solar Heating System Development"**
- Beskrivning: **"Project management for solar heating system development"**

## 📋 **Steg 2: Sätt upp kolumner**

### **2.1 Skapa följande kolumner (i ordning):**

#### **Backlog**
- **Beskrivning**: Planerade funktioner och förbättringar
- **Färg**: Grå
- **Syfte**: Issues som väntar på att börja arbeta med

#### **To Do**
- **Beskrivning**: Redo att arbeta med
- **Färg**: Blå
- **Syfte**: Issues som har all nödvändig information

#### **In Progress**
- **Beskrivning**: Aktuellt pågående arbete
- **Färg**: Gul
- **Syfte**: Max 2-3 issues samtidigt
- **Begränsning**: Max 3 issues i denna kolumn

#### **Review**
- **Beskrivning**: Klar för granskning och testning
- **Färg**: Orange
- **Syfte**: Väntar på godkännande

#### **Testing**
- **Beskrivning**: Under testning på Raspberry Pi
- **Färg**: Lila
- **Syfte**: Validering av funktionalitet

#### **Done**
- **Beskrivning**: Färdiga och verifierade funktioner
- **Färg**: Grön
- **Syfte**: Dokumentation uppdaterad

## 🏷️ **Steg 3: Sätt upp Labels (Etiketter)**

### **3.1 Skapa följande labels:**

#### **Typ av arbete:**
- `bug` - Röd (#d73a4a) - Något fungerar inte som det ska
- `enhancement` - Grön (#28a745) - Förbättring av befintlig funktion
- `feature` - Blå (#0075ca) - Ny funktion
- `documentation` - Grå (#6f42c1) - Dokumentationsuppdatering
- `testing` - Gul (#ffc107) - Testrelaterat arbete

#### **Prioritet:**
- `priority: high` - Röd (#d73a4a) - Kritiskt för systemets funktion
- `priority: medium` - Gul (#ffc107) - Viktigt men inte kritiskt
- `priority: low` - Grön (#28a745) - Nice-to-have

#### **Komponent:**
- `component: sensors` - Blå (#0075ca) - Temperatursensorer
- `component: pumps` - Grön (#28a745) - Pumpkontroll
- `component: mqtt` - Lila (#6f42c1) - MQTT-kommunikation
- `component: home-assistant` - Orange (#fd7e14) - Home Assistant-integration
- `component: watchdog` - Röd (#dc3545) - Övervakningssystem
- `component: gui` - Cyan (#17a2b8) - Användargränssnitt
- `component: systemd` - Mörkblå (#0056b3) - Systemd-tjänster
- `component: logging` - Mörkgrå (#6c757d) - Loggningssystem

#### **Status:**
- `status: needs-info` - Gul (#ffc107) - Behöver mer information
- `status: ready` - Grön (#28a745) - Redo att arbeta med
- `status: blocked` - Röd (#dc3545) - Blockerat av annat arbete

## 🎯 **Steg 4: Skapa Milestones**

### **4.1 Skapa följande milestones:**

#### **v3.1 - Bug Fixes & Stability**
- **Deadline**: [Sätt datum 2 veckor framåt]
- **Beskrivning**: Kritiska bugfixes och stabilitetsförbättringar
- **Issues**: #1, #2, #3, #7, #10, #12

#### **v3.2 - Enhanced Monitoring**
- **Deadline**: [Sätt datum 4 veckor framåt]
- **Beskrivning**: Förbättrad övervakning och felhantering
- **Issues**: #4, #5, #8, #13

#### **v3.3 - Advanced Features**
- **Deadline**: [Sätt datum 8 veckor framåt]
- **Beskrivning**: Nya funktioner och förbättringar
- **Issues**: #6, #9, #11

## 📝 **Steg 5: Skapa Issue Templates**

### **5.1 Skapa template-mappar:**
- Gå till repository root
- Skapa mapp: `.github/ISSUE_TEMPLATE/`

### **5.2 Bug Report Template:**
Skapa fil: `.github/ISSUE_TEMPLATE/bug_report.md`
```markdown
---
name: Bug Report
about: Skapa en rapport för att hjälpa oss förbättra systemet
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
[Beskriv problemet tydligt och kortfattat]

## Steps to Reproduce
1. Gå till '...'
2. Klicka på '...'
3. Scrolla ner till '...'
4. Se fel

## Expected Behavior
[En tydlig och kortfattat beskrivning av vad du förväntade dig]

## Actual Behavior
[En tydlig och kortfattat beskrivning av vad som faktiskt hände]

## Environment
- **System**: [Raspberry Pi/Development]
- **Version**: [v3.x.x]
- **Hardware**: [Beskriv hårdvara]
- **OS**: [Raspberry Pi OS version]

## Logs
```
[Klistra in relevanta loggar här]
```

## Additional Context
[Lägg till annan kontext om problemet här]
```

### **5.3 Feature Request Template:**
Skapa fil: `.github/ISSUE_TEMPLATE/feature_request.md`
```markdown
---
name: Feature Request
about: Föreslå en idé för detta projekt
title: '[FEATURE] '
labels: feature
assignees: ''
---

## Feature Description
[Beskriv funktionen tydligt och kortfattat]

## Problem/Use Case
[Vilket problem löser detta? Varför behöver vi denna funktion?]

## Proposed Solution
[Hur föreslår du att lösa det? Beskriv lösningen tydligt]

## Alternatives Considered
[Beskriv alternativ du har övervägt]

## Additional Context
[Lägg till annan kontext eller skärmdumpar om funktionsförslaget här]
```

## 🔄 **Steg 6: Sätt upp Project Filters**

### **6.1 Konfigurera projektvy:**
- **Sortera efter**: Prioritet (High → Medium → Low)
- **Gruppera efter**: Komponent
- **Filtrera**: Aktiva issues (inte stängda)

### **6.2 Skapa sparade vyer:**
- **"High Priority"**: Visa endast `priority: high` issues
- **"In Progress"**: Visa endast issues i "In Progress" kolumn
- **"Ready for Review"**: Visa endast issues i "Review" kolumn

## 📊 **Steg 7: Skapa första Issues**

### **7.1 Skapa issues från listan:**
Använd informationen från `INITIAL_GITHUB_ISSUES.md` för att skapa:

1. **Issue #1**: MQTT Connection Leak
2. **Issue #2**: Sensor Mapping Issues
3. **Issue #3**: Service Startup Failures
4. **Issue #4**: Enhanced Error Recovery
5. **Issue #5**: Advanced Monitoring Dashboard
6. **Issue #6**: Energy Usage Analytics
7. **Issue #7**: Improved Test Coverage
8. **Issue #8**: Better Logging System
9. **Issue #9**: Configuration Management
10. **Issue #10**: User Manual Update
11. **Issue #11**: API Documentation
12. **Issue #12**: Hardware Test Suite
13. **Issue #13**: Performance Testing

### **7.2 Tilldela issues:**
- **Labels**: Använd rätt labels för varje issue
- **Milestones**: Tilldela till rätt milestone
- **Assignees**: Tilldela till dig själv
- **Project**: Lägg till i "Solar Heating System Development" projekt

## 🎯 **Steg 8: Konfigurera Workflow**

### **8.1 Automatiska övergångar:**
- När issue skapas → Flytta till "Backlog"
- När issue tilldelas → Flytta till "To Do"
- När kod pushas → Flytta till "Review"
- När PR mergas → Flytta till "Testing"
- När verifierat → Flytta till "Done"

### **8.2 Veckorapporter:**
- Skapa veckorapport varje fredag
- Visa framsteg mot milestones
- Identifiera blockerare
- Planera nästa veckas fokus

## ✅ **Verifiering**

### **Kontrollera att allt fungerar:**
- [ ] GitHub Project skapat med alla kolumner
- [ ] Alla labels skapade
- [ ] Milestones skapade med deadlines
- [ ] Issue templates fungerar
- [ ] Första issues skapade och tilldelade
- [ ] Projektfilter fungerar
- [ ] Workflow dokumenterat

---

**Nästa steg**: Börja arbeta med högsta prioritet issues och följ workflow för att hålla projektet organiserat!
