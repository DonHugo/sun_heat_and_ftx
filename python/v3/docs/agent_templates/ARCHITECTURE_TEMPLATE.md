# Architecture Design: [Feature Name]

**Date:** [YYYY-MM-DD]  
**Status:** [Draft | In Review | Approved | Implemented]  
**Agent:** @architect  
**Requirements Doc:** [Link to requirements document]  
**Version:** [Version number]

---

## 📋 Overview

### Purpose
[High-level description of what this architecture achieves]

### Goals
- [Goal 1 - What we're trying to accomplish]
- [Goal 2]
- [Goal 3]

### Non-Goals
- [What this architecture specifically does NOT address]
- [What is out of scope]

---

## 🏗️ System Architecture

### High-Level Architecture

```
[ASCII diagram or description of overall architecture]

Example:
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Component │─────▶│   Component │─────▶│   Component │
│      A      │      │      B      │      │      C      │
└─────────────┘      └─────────────┘      └─────────────┘
       │                     │                     │
       └─────────────────────┴─────────────────────┘
                             │
                      ┌──────▼──────┐
                      │   Storage   │
                      └─────────────┘
```

### Context Diagram
[Show how this feature fits into the larger system]

---

## 🔧 Components

### Component 1: [Component Name]

**Responsibility:**  
[What this component does - single responsibility]

**Location:**  
- **File:** `path/to/file.py`
- **Class:** `ClassName`
- **Module:** `module_name`

**Dependencies:**
- [Dependency 1 - what it needs to function]
- [Dependency 2]

**Interfaces:**
```python
class ComponentName:
    def method_1(self, param1: Type, param2: Type) -> ReturnType:
        """[Brief description]"""
        pass
    
    def method_2(self, param: Type) -> ReturnType:
        """[Brief description]"""
        pass
```

**State Management:**
- [What state it maintains]
- [How state is persisted]

**Error Handling:**
- [How errors are handled]
- [What exceptions are raised]

---

### Component 2: [Component Name]

[Same structure as Component 1]

---

### Component 3: [Component Name]

[Same structure as Component 1]

---

## 📊 Data Flow

### Primary Flow
```
1. [Step 1: Data enters system]
   ↓
2. [Step 2: Data is processed by Component A]
   ↓
3. [Step 3: Data flows to Component B]
   ↓
4. [Step 4: Result is produced]
```

### Data Structures

#### Structure 1: [Name]
```python
class DataStructure:
    """[Purpose of this data structure]"""
    
    attribute1: Type  # [Description]
    attribute2: Type  # [Description]
    attribute3: Type  # [Description]
```

**Validation Rules:**
- [Rule 1]
- [Rule 2]

---

## 🔄 Interaction Patterns

### Pattern 1: [Pattern Name]
**When:** [When this pattern is used]  
**How:** [How components interact]

```
Component A  ──[request]──▶  Component B
    │                            │
    │                            │
    │◀─────[response]────────────┘
```

**Example:**
```python
# Example code showing the interaction
```

---

### Pattern 2: [Pattern Name]
[Same structure as Pattern 1]

---

## 🔌 Integration Points

### Integration 1: [System/Component Name]
**Type:** [MQTT | REST API | File System | Database | etc.]  
**Direction:** [Inbound | Outbound | Bidirectional]

**Interface:**
```python
# API definition or protocol specification
```

**Data Format:**
```json
{
  "example": "data format"
}
```

**Error Handling:**
- [How integration errors are handled]

---

## 💾 Data Management

### Data Storage
**Type:** [JSON files | Database | In-memory | etc.]  
**Location:** [Path or connection info]  
**Schema:**
```json
{
  "schema": "definition"
}
```

### Data Lifecycle
1. [Creation]
2. [Update]
3. [Retention]
4. [Deletion]

### Data Migration
[How existing data will be migrated, if applicable]

---

## ⚡ Performance Considerations

### Performance Requirements
- **Response Time:** [Target response time]
- **Throughput:** [Target throughput]
- **Resource Usage:** [CPU, Memory limits]

### Optimization Strategy
- [Optimization 1]
- [Optimization 2]

### Bottlenecks
- [Potential bottleneck 1]
- [Mitigation strategy]

---

## 🛡️ Error Handling & Resilience

### Error Categories
1. **[Error Type 1]**
   - **Detection:** [How we detect this error]
   - **Recovery:** [How we recover]
   - **Fallback:** [Fallback behavior]

2. **[Error Type 2]**
   - **Detection:** [How we detect this error]
   - **Recovery:** [How we recover]
   - **Fallback:** [Fallback behavior]

### Retry Logic
- [When retries are used]
- [Retry strategy]
- [Backoff policy]

### Circuit Breakers
[If circuit breakers are used, describe them]

---

## 📝 Logging & Monitoring

### Logging Strategy
- **Level:** [INFO | DEBUG | WARNING | ERROR]
- **Format:** [Log format]
- **Location:** [Where logs are stored]

**Key Log Points:**
1. [Log point 1 - when/what to log]
2. [Log point 2]

### Metrics
- **Metric 1:** [What to measure]
- **Metric 2:** [What to measure]

### Alerts
- **Alert 1:** [Condition and threshold]
- **Alert 2:** [Condition and threshold]

---

## 🧪 Testing Strategy

### Unit Testing
- [What components need unit tests]
- [Mock/stub strategy]

### Integration Testing
- [What integrations need testing]
- [Test environment requirements]

### Hardware Testing
- [What hardware tests are needed]
- [How to run on Raspberry Pi]

### E2E Testing
- [End-to-end test scenarios]

---

## 🔀 Technology Choices

### Choice 1: [Technology/Library/Pattern]
**Purpose:** [Why we need this]

**Options Considered:**

| Option | Pros | Cons | Score |
|--------|------|------|-------|
| Option A | [Pros] | [Cons] | [X/10] |
| Option B | [Pros] | [Cons] | [X/10] |
| Option C | [Pros] | [Cons] | [X/10] |

**Decision:** [Chosen option]  
**Rationale:** [Why this option was chosen]

---

### Choice 2: [Technology/Library/Pattern]
[Same structure as Choice 1]

---

## ⚖️ Trade-offs & Alternatives

### Trade-off 1: [Description]
**Chosen Approach:** [What we're doing]  
**Alternative Approach:** [What we're not doing]

**Pros of Chosen:**
- [Pro 1]
- [Pro 2]

**Cons of Chosen:**
- [Con 1]
- [Con 2]

**Why Chosen:** [Justification]

---

## 🚧 Constraints & Limitations

### Technical Constraints
- **Hardware:** [Raspberry Pi 4 - CPU, Memory limitations]
- **Python Version:** [Version constraints]
- **Libraries:** [Available libraries]
- **Network:** [Network limitations]

### System Constraints
- [Real-time requirements]
- [Reliability requirements]
- [Integration constraints]

### Known Limitations
1. [Limitation 1] - Workaround: [Workaround]
2. [Limitation 2] - Workaround: [Workaround]

---

## 📈 Scalability & Extensibility

### Scalability
**Current Scale:** [Current requirements]  
**Future Scale:** [Expected growth]  
**Scaling Strategy:** [How system will scale]

### Extensibility Points
1. [Extension point 1 - how to extend the system]
2. [Extension point 2]

---

## 🔐 Security Considerations

### Authentication
[If applicable - how authentication works]

### Authorization
[If applicable - how authorization works]

### Data Protection
- [Sensitive data handling]
- [Encryption]

### Input Validation
- [Where validation happens]
- [What is validated]

---

## 🚀 Deployment Considerations

### Installation
- [Installation requirements]
- [Setup steps]

### Configuration
- [Configuration files]
- [Environment variables]

### Dependencies
```python
# requirements.txt additions
library1==1.2.3
library2==4.5.6
```

### Service Management
- [Systemd service changes, if any]
- [Service dependencies]

---

## 📚 References & Resources

### Related Documentation
- [Reference 1]
- [Reference 2]

### External Resources
- [Library documentation]
- [Design pattern references]

### Similar Implementations
- [Examples from other projects]

---

## 🔄 Migration & Backward Compatibility

### Breaking Changes
- [Breaking change 1]
- [Migration path]

### Backward Compatibility
- [What remains compatible]
- [Deprecation strategy]

### Data Migration
- [How existing data migrates]
- [Migration script location]

---

## ✅ Architecture Review Checklist

- [ ] All requirements addressed
- [ ] Components have single responsibilities
- [ ] Dependencies are minimal and clear
- [ ] Error handling is comprehensive
- [ ] Performance requirements met
- [ ] Testing strategy is complete
- [ ] Security considerations addressed
- [ ] Documentation is complete
- [ ] Reviewed by: _______________

---

## 📝 Open Questions

1. **Q:** [Question that needs resolution]  
   **A:** [Answer when available]

2. **Q:** [Question that needs resolution]  
   **A:** [Answer when available]

---

## 🔄 Next Steps

1. [ ] Architecture review and approval
2. [ ] Hand off to @tester for test specification
3. [ ] Create architecture diagrams (if needed)
4. [ ] Update system documentation

---

## 📋 Approval

**Reviewed by:** _______________  
**Approved by:** _______________  
**Date:** _______________

---

**Next Agent:** @tester  
**Hand-off Notes:** [Summary for the tester about test requirements and critical areas to focus on]


