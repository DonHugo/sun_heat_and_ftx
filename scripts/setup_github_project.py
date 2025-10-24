#!/usr/bin/env python3
"""
GitHub Project Setup Script
Automatiskt sätt upp GitHub Project för solvärmesystemet
"""

import requests
import json
import time
import os
from typing import Dict, List, Optional

class GitHubProjectSetup:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Solar-Heating-System-Setup"
        }
        
    def create_project(self) -> Optional[str]:
        """Skapa GitHub Project"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/projects"
        data = {
            "name": "Solar Heating System Development",
            "body": "Project management for solar heating system development with TDD approach"
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            project_data = response.json()
            print(f"✅ Project created: {project_data['name']} (ID: {project_data['id']})")
            return str(project_data['id'])
        else:
            print(f"❌ Failed to create project: {response.status_code} - {response.text}")
            return None
    
    def create_columns(self, project_id: str) -> Dict[str, str]:
        """Skapa kolumner för projektet"""
        columns = {
            "Backlog": "Planerade funktioner och förbättringar",
            "To Do": "Redo att arbeta med",
            "In Progress": "Aktuellt pågående arbete (max 3)",
            "Review": "Klar för granskning och testning",
            "Testing": "Under testning på Raspberry Pi",
            "Done": "Färdiga och verifierade funktioner"
        }
        
        column_ids = {}
        url = f"{self.base_url}/projects/{project_id}/columns"
        
        for name, description in columns.items():
            data = {"name": name}
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                column_data = response.json()
                column_ids[name] = str(column_data['id'])
                print(f"✅ Column created: {name}")
            else:
                print(f"❌ Failed to create column {name}: {response.status_code}")
                
            time.sleep(0.5)  # Rate limiting
        
        return column_ids
    
    def create_labels(self) -> Dict[str, str]:
        """Skapa labels för issues"""
        labels = {
            # Typ av arbete
            "bug": {"color": "d73a4a", "description": "Något fungerar inte som det ska"},
            "enhancement": {"color": "28a745", "description": "Förbättring av befintlig funktion"},
            "feature": {"color": "0075ca", "description": "Ny funktion"},
            "documentation": {"color": "6f42c1", "description": "Dokumentationsuppdatering"},
            "testing": {"color": "ffc107", "description": "Testrelaterat arbete"},
            
            # Prioritet
            "priority: high": {"color": "d73a4a", "description": "Kritiskt för systemets funktion"},
            "priority: medium": {"color": "ffc107", "description": "Viktigt men inte kritiskt"},
            "priority: low": {"color": "28a745", "description": "Nice-to-have"},
            
            # Komponent
            "component: sensors": {"color": "0075ca", "description": "Temperatursensorer"},
            "component: pumps": {"color": "28a745", "description": "Pumpkontroll"},
            "component: mqtt": {"color": "6f42c1", "description": "MQTT-kommunikation"},
            "component: home-assistant": {"color": "fd7e14", "description": "Home Assistant-integration"},
            "component: watchdog": {"color": "dc3545", "description": "Övervakningssystem"},
            "component: gui": {"color": "17a2b8", "description": "Användargränssnitt"},
            "component: systemd": {"color": "0056b3", "description": "Systemd-tjänster"},
            "component: logging": {"color": "6c757d", "description": "Loggningssystem"},
            
            # Status
            "status: needs-info": {"color": "ffc107", "description": "Behöver mer information"},
            "status: ready": {"color": "28a745", "description": "Redo att arbeta med"},
            "status: blocked": {"color": "dc3545", "description": "Blockerat av annat arbete"}
        }
        
        created_labels = {}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/labels"
        
        for name, config in labels.items():
            data = {
                "name": name,
                "color": config["color"],
                "description": config["description"]
            }
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                created_labels[name] = name
                print(f"✅ Label created: {name}")
            elif response.status_code == 422:
                print(f"⚠️  Label already exists: {name}")
                created_labels[name] = name
            else:
                print(f"❌ Failed to create label {name}: {response.status_code}")
                
            time.sleep(0.3)  # Rate limiting
        
        return created_labels
    
    def create_milestones(self) -> Dict[str, str]:
        """Skapa milestones för versioner"""
        milestones = {
            "v3.1 - Bug Fixes & Stability": {
                "description": "Kritiska bugfixes och stabilitetsförbättringar",
                "state": "open"
            },
            "v3.2 - Enhanced Monitoring": {
                "description": "Förbättrad övervakning och felhantering",
                "state": "open"
            },
            "v3.3 - Advanced Features": {
                "description": "Nya funktioner och förbättringar",
                "state": "open"
            }
        }
        
        milestone_ids = {}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/milestones"
        
        for title, config in milestones.items():
            data = {
                "title": title,
                "description": config["description"],
                "state": config["state"]
            }
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                milestone_data = response.json()
                milestone_ids[title] = str(milestone_data['number'])
                print(f"✅ Milestone created: {title}")
            else:
                print(f"❌ Failed to create milestone {title}: {response.status_code}")
                
            time.sleep(0.5)  # Rate limiting
        
        return milestone_ids
    
    def create_issues(self, milestone_ids: Dict[str, str]) -> List[str]:
        """Skapa initial issues"""
        issues = [
            {
                "title": "MQTT Connection Leak",
                "body": "Systemet skapar för många MQTT-anslutningar över tid. Delvis fixat, behöver verifiering.",
                "labels": ["bug", "priority: high", "component: mqtt"],
                "milestone": milestone_ids.get("v3.1 - Bug Fixes & Stability")
            },
            {
                "title": "Sensor Mapping Issues",
                "body": "Vissa sensorer mappas inte korrekt, förhindrar pumpstart. Fixat i senaste commits, behöver testning.",
                "labels": ["bug", "priority: high", "component: sensors"],
                "milestone": milestone_ids.get("v3.1 - Bug Fixes & Stability")
            },
            {
                "title": "Service Startup Failures",
                "body": "Tjänster startar inte om loggkataloger saknas. Fixat med automatisk katalogskapande.",
                "labels": ["bug", "priority: medium", "component: systemd"],
                "milestone": milestone_ids.get("v3.1 - Bug Fixes & Stability")
            },
            {
                "title": "Enhanced Error Recovery",
                "body": "Förbättrad automatisk återhämtning vid fel. Implementera robustare felhantering.",
                "labels": ["feature", "priority: medium", "component: watchdog"],
                "milestone": milestone_ids.get("v3.2 - Enhanced Monitoring")
            },
            {
                "title": "Advanced Monitoring Dashboard",
                "body": "Utökad övervakningsdashboard i Home Assistant med fler metrics och visualiseringar.",
                "labels": ["feature", "priority: medium", "component: home-assistant"],
                "milestone": milestone_ids.get("v3.2 - Enhanced Monitoring")
            },
            {
                "title": "Energy Usage Analytics",
                "body": "Analys av energianvändning och effektivitet. Implementera datainsamling och rapporter.",
                "labels": ["feature", "priority: low", "component: logging"],
                "milestone": milestone_ids.get("v3.3 - Advanced Features")
            },
            {
                "title": "Improved Test Coverage",
                "body": "Utöka testtäckning för alla komponenter. Implementera omfattande testsuiter.",
                "labels": ["enhancement", "priority: medium", "component: testing"],
                "milestone": milestone_ids.get("v3.1 - Bug Fixes & Stability")
            },
            {
                "title": "Better Logging System",
                "body": "Förbättrat loggningssystem med strukturerade loggar och bättre felhantering.",
                "labels": ["enhancement", "priority: medium", "component: logging"],
                "milestone": milestone_ids.get("v3.2 - Enhanced Monitoring")
            },
            {
                "title": "Configuration Management",
                "body": "Bättre hantering av konfigurationsfiler med validering och backup.",
                "labels": ["enhancement", "priority: low", "component: systemd"],
                "milestone": milestone_ids.get("v3.3 - Advanced Features")
            },
            {
                "title": "User Manual Update",
                "body": "Uppdatera användarmanual med nya funktioner och förbättringar.",
                "labels": ["documentation", "priority: medium", "component: documentation"],
                "milestone": milestone_ids.get("v3.1 - Bug Fixes & Stability")
            }
        ]
        
        created_issues = []
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        
        for issue_data in issues:
            data = {
                "title": issue_data["title"],
                "body": issue_data["body"],
                "labels": issue_data["labels"]
            }
            
            if issue_data.get("milestone"):
                data["milestone"] = int(issue_data["milestone"])
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                issue_response = response.json()
                created_issues.append(str(issue_response['number']))
                print(f"✅ Issue created: #{issue_response['number']} - {issue_data['title']}")
            else:
                print(f"❌ Failed to create issue {issue_data['title']}: {response.status_code}")
                
            time.sleep(0.5)  # Rate limiting
        
        return created_issues
    
    def setup_project(self):
        """Huvudfunktion för att sätta upp hela projektet"""
        print("🚀 Starting GitHub Project Setup...")
        print(f"Repository: {self.owner}/{self.repo}")
        print("-" * 50)
        
        # 1. Skapa projekt
        project_id = self.create_project()
        if not project_id:
            print("❌ Failed to create project. Exiting.")
            return False
        
        # 2. Skapa kolumner
        print("\n📋 Creating project columns...")
        column_ids = self.create_columns(project_id)
        
        # 3. Skapa labels
        print("\n🏷️  Creating labels...")
        labels = self.create_labels()
        
        # 4. Skapa milestones
        print("\n🎯 Creating milestones...")
        milestone_ids = self.create_milestones()
        
        # 5. Skapa issues
        print("\n📝 Creating initial issues...")
        issue_numbers = self.create_issues(milestone_ids)
        
        print("\n" + "=" * 50)
        print("✅ GitHub Project Setup Complete!")
        print(f"📊 Created {len(column_ids)} columns")
        print(f"🏷️  Created {len(labels)} labels")
        print(f"🎯 Created {len(milestone_ids)} milestones")
        print(f"📝 Created {len(issue_numbers)} issues")
        print(f"🔗 Project URL: https://github.com/{self.owner}/{self.repo}/projects")
        print("=" * 50)
        
        return True

def main():
    """Huvudfunktion"""
    print("GitHub Project Setup för Solvärmesystemet")
    print("=" * 50)
    
    # Hämta konfiguration
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token:")
        print("export GITHUB_TOKEN=your_token_here")
        return
    
    owner = "DonHugo"
    repo = "sun_heat_and_ftx"
    
    # Skapa setup-instans
    setup = GitHubProjectSetup(token, owner, repo)
    
    # Kör setup
    success = setup.setup_project()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("You can now view your project at:")
        print(f"https://github.com/{owner}/{repo}/projects")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()
