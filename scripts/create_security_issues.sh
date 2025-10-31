#!/bin/bash
# Create Critical Security Issues
# This script creates the 5 most critical security issues identified in the audit

set -e

echo "🔐 Creating Critical Security Issues..."
echo ""

# Issue A: Input Validation Missing
echo "=== Creating Issue A: Input Validation Missing ==="
gh issue create \
  --title "[SECURITY] API Input Validation Missing" \
  --label "bug,priority: critical,category: security,component: api" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Security Issue

API endpoints lack proper input validation, creating security vulnerabilities.

**Severity:** Critical  
**Impact:** Potential for injection attacks, system crashes, data corruption

**Affected Components:**
- REST API endpoints
- Configuration inputs
- User inputs via GUI

**Required Actions:**
- [ ] Audit all API endpoints
- [ ] Implement input validation using pydantic
- [ ] Add input sanitization
- [ ] Test with malicious inputs
- [ ] Document validation rules

**Acceptance Criteria:**
- [ ] All inputs validated against schemas
- [ ] Invalid inputs rejected with clear errors
- [ ] Security tests pass
- [ ] Documentation updated

**Priority:** CRITICAL - Must fix before production deployment"

echo "✅ Issue A created"
echo ""

# Issue B: MQTT Authentication
echo "=== Creating Issue B: MQTT Authentication Not Enforced ==="
gh issue create \
  --title "[SECURITY] MQTT Authentication Not Always Enforced" \
  --label "bug,priority: critical,category: security,component: mqtt" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Security Issue

MQTT connections don't consistently enforce authentication.

**Severity:** Critical  
**Impact:** Unauthorized access could control heating system, read sensor data

**Current Behavior:**
- Some connections bypass authentication
- No verification of client certificates
- Weak password policy

**Required Actions:**
- [ ] Enforce authentication on all MQTT connections
- [ ] Implement certificate-based auth
- [ ] Add connection audit logging
- [ ] Test unauthorized access attempts
- [ ] Update security documentation

**Acceptance Criteria:**
- [ ] All MQTT connections require authentication
- [ ] Failed auth attempts logged
- [ ] Security audit passes
- [ ] Documentation updated

**Priority:** CRITICAL - Security vulnerability"

echo "✅ Issue B created"
echo ""

# Issue C: Hardcoded Secrets
echo "=== Creating Issue C: Hardcoded Secrets in Configuration ==="
gh issue create \
  --title "[SECURITY] Hardcoded Secrets in Configuration Files" \
  --label "bug,priority: critical,category: security,component: config" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Security Issue

Configuration files contain hardcoded secrets and passwords.

**Severity:** Critical  
**Impact:** Credentials exposed in git history, potential compromise

**Affected Files:**
- Configuration files with MQTT passwords
- API keys
- Database credentials

**Required Actions:**
- [ ] Move secrets to environment variables
- [ ] Use secrets management (e.g., .env files not in git)
- [ ] Rotate compromised credentials
- [ ] Add .gitignore for secrets
- [ ] Audit git history
- [ ] Document secret management

**Acceptance Criteria:**
- [ ] No hardcoded secrets in code
- [ ] Secrets loaded from environment
- [ ] Old credentials rotated
- [ ] Git history cleaned (if needed)
- [ ] Security guide updated

**Priority:** CRITICAL - Immediate credential rotation needed"

echo "✅ Issue C created"
echo ""

# Issue D: Error Messages
echo "=== Creating Issue D: Error Messages Expose System Info ==="
gh issue create \
  --title "[SECURITY] Error Messages Leak Sensitive System Information" \
  --label "bug,priority: high,category: security,component: logging" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Security Issue

Error messages expose sensitive system information to users.

**Severity:** High  
**Impact:** Reveals file paths, library versions, internal structure

**Examples:**
- Stack traces with full paths
- Database connection strings in errors
- Library versions in exceptions

**Required Actions:**
- [ ] Audit all error messages
- [ ] Sanitize user-facing errors
- [ ] Keep detailed errors in logs only
- [ ] Implement error codes
- [ ] Test error scenarios

**Acceptance Criteria:**
- [ ] No sensitive info in user errors
- [ ] Generic error messages for users
- [ ] Detailed errors only in logs
- [ ] Error code documentation
- [ ] Security review passes

**Priority:** HIGH - Information leakage"

echo "✅ Issue D created"
echo ""

# Issue E: Rate Limiting
echo "=== Creating Issue E: No Rate Limiting on API ==="
gh issue create \
  --title "[SECURITY] API Lacks Rate Limiting" \
  --label "enhancement,priority: high,category: security,component: api" \
  --milestone "v3.1 - Bug Fixes & Stability" \
  --body "## Security Enhancement

API endpoints lack rate limiting, vulnerable to abuse and DoS attacks.

**Severity:** High  
**Impact:** System could be overwhelmed by repeated requests

**Current Behavior:**
- No limits on request frequency
- No throttling mechanism
- No abuse detection

**Proposed Solution:**
- Implement rate limiting per IP/user
- Add request throttling
- Log rate limit violations
- Graceful degradation under load

**Required Actions:**
- [ ] Choose rate limiting strategy
- [ ] Implement rate limiter
- [ ] Add rate limit headers
- [ ] Test under load
- [ ] Document rate limits

**Acceptance Criteria:**
- [ ] Rate limits enforced
- [ ] Appropriate status codes returned (429)
- [ ] Limits documented
- [ ] Load testing passes

**Priority:** HIGH - Prevent abuse and DoS"

echo "✅ Issue E created"
echo ""

echo "🎉 All 5 critical security issues created!"
echo ""
echo "Summary:"
echo "- 3 CRITICAL security issues"
echo "- 2 HIGH priority security issues"
echo "- All assigned to milestone: v3.1 - Bug Fixes & Stability"
echo ""
echo "Next steps:"
echo "1. Review issues: gh issue list --label 'category: security'"
echo "2. Prioritize and assign: gh issue list --milestone 'v3.1 - Bug Fixes & Stability'"
echo "3. Start fixing: @requirements I need to fix [issue]"
echo ""
echo "⚠️  IMPORTANT: These are CRITICAL security issues"
echo "   Address these before production deployment!"

