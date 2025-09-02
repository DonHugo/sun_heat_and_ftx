# Collaboration Workflow

This document defines the standard process for working together on the solar heating system project.

## 🎯 **Our Approach: Requirements First, Implementation Second**

We follow a structured approach to ensure we build exactly what you need:

### **Phase 1: Requirements Gathering & Discussion** 📝
**NO CODING YET** - We discuss and plan first

1. **Requirements Description**
   - You describe what you want to achieve
   - What problems you're trying to solve
   - What outcomes you expect

2. **Documentation Review & PRD Update** 📋
   - **Check all existing documentation** to understand current system state
   - **Review PRD** to see what's already implemented vs. what's planned
   - **Identify gaps** between documentation and actual implementation
   - **Update PRD** to reflect current system capabilities and new requirements
   - **Document new requirements** that emerge during discussions
   - **Ensure PRD mirrors** what is done, what is left, and what is newly discovered

3. **Open Discussion**
   - We explore different approaches
   - Discuss trade-offs and alternatives
   - Consider existing system constraints
   - Identify potential challenges

4. **Clarification & Questions**
   - I ask clarifying questions to understand your needs
   - We discuss technical details and options
   - Make sure we're on the same page

5. **Solution Planning**
   - Outline the proposed approach
   - Define what will be built
   - Identify integration points
   - Plan implementation steps

6. **Agreement & Approval**
   - Confirm the approach meets your needs
   - Get your approval before any coding begins
   - Set expectations for timeline and deliverables

### **Phase 2: Implementation** 🔧
**ONLY AFTER AGREEMENT** - Then we build

6. **Implementation**
   - Follow the agreed-upon plan
   - Build incrementally
   - Test as we go
   - Keep you updated on progress

7. **Review & Refinement**
   - Show you what was built
   - Get feedback and make adjustments
   - Ensure it meets your expectations

## 🤝 **Communication Guidelines**

### **What You Should Do:**
- Describe your requirements clearly
- Ask questions if something isn't clear
- Provide feedback on proposed solutions
- Let me know if the approach doesn't feel right

### **What I Will Do:**
- Ask clarifying questions before implementing
- Discuss alternatives and trade-offs
- Explain technical decisions
- Get your approval before coding
- Keep you informed of progress

### **What We Both Agree To:**
- No rushed implementations
- Clear communication about requirements
- Discussion before coding
- Iterative feedback and improvement

## 📋 **Template for New Requirements**

When you have a new requirement, please include:

```
**Requirement:** [Brief description]

**Problem:** [What problem are you trying to solve?]

**Desired Outcome:** [What do you want to achieve?]

**Context:** [Any relevant background information]

**Constraints:** [Any limitations or preferences]

**Questions:** [Any specific questions you have]
```

## 🔄 **Example Workflow**

### **Good Example:**
1. **You:** "I want to monitor water usage patterns to detect leaks"
2. **Documentation Review:** I check existing docs and PRD to understand current system capabilities
3. **PRD Update:** Update PRD to reflect current state and add new leak detection requirements
4. **Discussion:** We talk about different approaches (flow sensors, pressure monitoring, usage patterns)
5. **Clarification:** I ask about your existing sensors, what constitutes a "leak", etc.
6. **Planning:** We agree on monitoring usage patterns and alerting on unusual spikes
7. **Approval:** You confirm this approach works for you
8. **Implementation:** I build the leak detection system
9. **Documentation Update:** Update all relevant docs and PRD to reflect the new feature

### **What We Avoid:**
- Jumping straight into coding without understanding requirements
- Building features that don't solve your actual problems
- Making assumptions about what you want
- Implementing without your approval

## 📁 **Documentation Standards**

### **For Each Feature:**
- **Requirements Document**: What we're building and why
- **Technical Design**: How it will work
- **Implementation Plan**: Step-by-step approach
- **Testing Strategy**: How we'll verify it works
- **User Guide**: How to use the new feature

### **Documentation Maintenance:**
- **Update Existing Docs**: All existing documentation and manuals must be updated if necessary
- **Cross-Reference**: Ensure new features are properly referenced in relevant existing docs
- **Version Control**: Keep track of which documentation versions apply to which system versions
- **Consistency Check**: Verify that all documentation remains consistent and accurate

### **PRD Maintenance Requirements:**
- **Current State Reflection**: PRD must accurately reflect what is currently implemented
- **Gap Identification**: Document what is planned vs. what is actually built
- **New Requirements Capture**: Document any new requirements discovered during discussions
- **Status Updates**: Keep track of implementation progress and completion status
- **Version Alignment**: Ensure PRD version matches current system implementation

### **File Naming:**
- `REQUIREMENTS_[feature_name].md` - Requirements and discussion
- `DESIGN_[feature_name].md` - Technical design
- `IMPLEMENTATION_[feature_name].md` - Implementation details
- `USER_GUIDE_[feature_name].md` - How to use the feature

## 🎯 **Success Criteria**

A successful collaboration means:
- ✅ You get exactly what you need
- ✅ No wasted time on wrong solutions
- ✅ Clear understanding of what was built
- ✅ Easy to maintain and extend
- ✅ All existing documentation and manuals are updated as necessary
- ✅ PRD accurately reflects current system state and requirements
- ✅ Documentation gaps are identified and addressed
- ✅ New requirements discovered during discussions are captured
- ✅ Both of us are satisfied with the process

## 📋 **Ongoing Documentation Maintenance**

### **Before Each New Feature Discussion:**
- **Review Current Documentation**: Check all existing docs to understand current system state
- **PRD Status Check**: Verify PRD reflects what's implemented vs. what's planned
- **Gap Analysis**: Identify any discrepancies between docs and actual implementation
- **Update PRD**: Ensure PRD mirrors current reality before adding new requirements

### **During Feature Discussions:**
- **Capture New Requirements**: Document any new requirements that emerge
- **Update PRD**: Add new requirements to PRD as they are discovered
- **Track Changes**: Note what needs to be updated in existing documentation

### **After Feature Implementation:**
- **Update All Docs**: Ensure all relevant documentation reflects the new feature
- **PRD Completion**: Mark requirements as implemented in PRD
- **Cross-Reference**: Update related documentation to reference new features
- **Version Alignment**: Ensure documentation versions match system implementation

## 📞 **When to Break the Process**

The only times we might skip the full discussion:
- **Bug fixes**: Quick fixes for obvious issues
- **Minor tweaks**: Small adjustments to existing features
- **Emergency fixes**: Critical system issues

**Important**: Even for quick fixes, we still perform the **Documentation Review & PRD Update** phase to ensure all documentation remains accurate and up-to-date.

But even then, we'll discuss the approach briefly before implementing.

---

**Remember:** This document is a living guide. We can update it based on our experience working together. The goal is to make sure we build the right things, the right way, every time.

**Next Steps:** 
1. Review this workflow
2. Let me know if you'd like any changes
3. Use this process for future requirements
4. Keep this document updated as we learn what works best
