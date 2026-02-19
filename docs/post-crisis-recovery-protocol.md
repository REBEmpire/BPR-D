# Post-Crisis Recovery Protocol

**Version:** 1.0  
**Created:** 2026-02-19 02:30 UTC  
**Author:** Claude (Strategic Assessment)  
**Status:** DRAFT - Pending Russell API Fix Deployment

## Purpose

This protocol provides a systematic checklist for validating BPR&D infrastructure recovery after the Feb 15-19 API crisis (50% failure rate across Gemini/Abacus operations).

## Crisis Context

**What Happened:**
- Feb 15: First Automated Meeting launched
- Feb 17: 50% API failure rate identified (Gemini 404 model mismatch, Abacus NoneType errors)
- Feb 17-18: 5 critical Russell handoffs created, all overdue
- Feb 19: Team operating in contingency mode (design work only, minimal API calls)

**Root Causes:**
1. Gemini model suffix mismatch (`-0214` vs base model name)
2. Abacus NoneType runtime errors (possibly pause-related)
3. api_healer.py not deployed (dynamic model discovery missing)
4. Guardian patterns not integrated into API calls

**Impact:**
- All agent automation degraded or blocked
- Meeting infrastructure status unknown (no Feb 15+ logs found)
- Research brief quality/consistency unclear during crisis period
- Budget burn on failed API calls (unknown amount of $20/month cap)

## Recovery Validation Checklist

### Phase 1: Infrastructure Deployment (Russell)

- [ ] **Deploy api_healer.py** with dynamic model discovery
  - Verify: `crewai-service/api_healer.py` is live in Render environment
  - Verify: Environment variables configured per [[skill-render-deployment]]
  - Verify: Healer logs being generated for Abacus router analysis

- [ ] **Deploy Gemini API Patches**
  - Verify: Model suffix fix (`-0214` handling) deployed
  - Verify: Dynamic model discovery prevents future mismatches
  - Verify: Test call to Gemini API returns 200 status

- [ ] **Deploy Abacus API Patches**
  - Verify: NoneType error handling deployed
  - Verify: Test call to Abacus API returns valid response
  - Verify: Error logs show root cause resolution

- [ ] **Integrate Guardian Patterns**
  - Verify: `crewai-service/guardians.py` integrated into all API calls
  - Verify: Retry logic, exponential backoff, circuit breakers active
  - Verify: Guardian logs show pattern activation on transient failures

- [ ] **Deploy API Debug Script**
  - Verify: Debug script available for manual diagnostics
  - Verify: Script can validate all 4 agent API endpoints
  - Verify: Output includes detailed error context

### Phase 2: Validation Testing (All Agents)

- [ ] **Grok API Test**
  - Run: Test work session with real backlog processing
  - Verify: Session completes without errors
  - Verify: Handoff updates committed successfully
  - Document: Results in `_debug/grok_api_test.md`

- [ ] **Claude API Test**
  - Run: Test work session with strategic analysis
  - Verify: Extended thinking works without errors
  - Verify: Session output meets [[skill-session-output-format]]
  - Document: Results in `_debug/claude_api_test.md`

- [ ] **Gemini API Test**
  - Run: Test work session with code generation
  - Verify: No 404 model mismatch errors
  - Verify: Research brief generation works
  - Document: Results in `_debug/gemini_api_test.md`

- [ ] **Abacus API Test** (after Feb 23 return)
  - Run: Test work session with router prototyping
  - Verify: No NoneType runtime errors
  - Verify: Healer log analysis works
  - Document: Results in `_debug/abacus_api_test.md`

### Phase 3: Meeting Infrastructure Validation

- [ ] **Test Daily Briefing**
  - Trigger: Manual meeting via web UI or curl
  - Participants: Grok, Claude, Gemini (3-agent test)
  - Verify: All agents participate successfully
  - Verify: Meeting notes committed to `_agents/_sessions/`
  - Verify: Website displays meeting output
  - Document: Results in meeting notes file

- [ ] **Validate Automated Schedule**
  - Verify: n8n workflows are active
  - Verify: Scheduled meetings trigger correctly
  - Verify: Meeting logs show consistent execution
  - Document: Schedule validation in `_debug/meeting_schedule_test.md`

- [ ] **Audit Historical Meetings**
  - Review: All Feb 15-19 meeting attempts
  - Document: Which succeeded, which failed, why
  - Identify: Patterns in meeting failures
  - Create: Lessons learned document

### Phase 4: Backlog Unblocking

- [ ] **Gemini Blocked Tasks**
  - Deploy: handoff_status_check.py (YAML/alchemical/Telegram alerts)
  - Deploy: ddas_content_mvp.py (1 Hive account MVP)
  - Verify: Both scripts operational
  - Document: Deployment results

- [ ] **Claude Blocked Tasks**
  - Implement: pending_abacus_review flag system
  - Complete: 5-brief quality audit
  - Finalize: Meeting Quality Metrics framework
  - Document: Implementation results

- [ ] **Grok Blocked Tasks**
  - Validate: Meeting reliability monitoring
  - Implement: Content production pipeline
  - Deploy: Website meeting notes integration
  - Document: Deployment results

- [ ] **Abacus Blocked Tasks** (after Feb 23)
  - Prototype: quintessence_router.py from healer logs
  - Implement: Filter upgrade system
  - Deploy: Negation forge capability
  - Document: Prototype results

### Phase 5: Monitoring & Prevention

- [ ] **API Health Dashboard**
  - Create: Real-time API status monitoring
  - Display: Failure rates by agent
  - Alert: When failure rate >10%
  - Location: `_debug/api_health_dashboard.md` or web UI

- [ ] **Budget Burn Tracking**
  - Calculate: Daily API spend
  - Track: Failed call costs vs successful
  - Alert: When approaching $20/month cap
  - Document: In `_debug/budget_tracking.md`

- [ ] **Meeting Execution Monitoring**
  - Verify: Each scheduled meeting executes
  - Alert: When meeting fails to trigger
  - Log: Meeting success/failure patterns
  - Document: In `_debug/meeting_monitoring.md`

- [ ] **Early Warning System**
  - Implement: Telegram alerts for API failures
  - Implement: Telegram alerts for meeting failures
  - Implement: Telegram alerts for budget thresholds
  - Test: All alert pathways

### Phase 6: Crisis Retrospective

- [ ] **Root Cause Analysis**
  - Document: Why 50% failure rate occurred
  - Document: Why it wasn't detected earlier
  - Document: What infrastructure assumptions were wrong
  - Location: `_agents/_sessions/2026-02-XX-crisis-retrospective.md`

- [ ] **Prevention Strategies**
  - Design: Pre-deployment testing checklist
  - Design: Continuous API health monitoring
  - Design: Graceful degradation patterns
  - Design: Budget protection mechanisms

- [ ] **Team Learning**
  - Conduct: Full team retrospective meeting
  - Discuss: What worked, what didn't
  - Identify: Process improvements
  - Document: Action items for next phase

## Success Criteria

**Crisis Resolved When:**
1. ✅ api_healer.py deployed with dynamic model discovery
2. ✅ Gemini 404 errors eliminated (model suffix fix confirmed)
3. ✅ Abacus NoneType errors resolved or documented as pause-related
4. ✅ 3 consecutive days of <10% API failure rate
5. ✅ All blocked agent tasks unblocked and deployed
6. ✅ Meeting automation reliability confirmed (test run successful)
7. ✅ Budget burn rate returns to sustainable levels (<$1/day average)

**Recovery Validated When:**
1. ✅ Full team meeting executes successfully with all 3 agents
2. ✅ Research briefs resume consistent daily generation
3. ✅ DDAS MVP deployed and operational
4. ✅ handoff_status_check.py deployed and alerting
5. ✅ Abacus returns Feb 23 to stable infrastructure
6. ✅ Monitoring systems operational and alerting correctly
7. ✅ Crisis retrospective completed with action items

## Contingency Plans

**If API Fixes Are Delayed:**
- Continue design/documentation work
- Reduce automated session frequency
- Focus on manual HiC work for critical items
- Document all blocked work for rapid deployment when fixed

**If Budget Cap Is Reached:**
- Pause all automated sessions
- Switch to manual HiC work only
- Prioritize critical infrastructure fixes
- Resume automation next billing cycle

**If Meeting Infrastructure Fails:**
- Fall back to manual meeting triggers
- Use web UI for critical team discussions
- Document meeting failures for debugging
- Validate n8n workflow configuration

## Timeline Expectations

**Optimistic (2-3 days):**
- Feb 19: Russell deploys all fixes
- Feb 20: Validation testing complete
- Feb 21: All blocked tasks deployed
- Feb 22: Monitoring systems operational

**Realistic (4-7 days):**
- Feb 19-20: Russell deploys fixes incrementally
- Feb 21-22: Validation testing and debugging
- Feb 23: Abacus returns, full team operational
- Feb 24-25: All blocked tasks deployed
- Feb 26: Monitoring and retrospective

**Pessimistic (8-14 days):**
- Feb 19-23: Iterative debugging and fixes
- Feb 24-26: Validation testing
- Feb 27-28: Blocked task deployment
- Mar 1-2: Monitoring and retrospective

## Communication Protocol

**Daily Updates to Russell:**
- API stability status
- Blocked work items
- Budget burn rate
- Critical blockers

**Team Coordination:**
- Daily briefings focus on recovery progress
- Handoffs updated with recovery tasks
- Telegram alerts for critical issues
- Session notes document recovery actions

## Notes

This protocol is designed to be systematic and comprehensive. Each checkbox represents a concrete validation step. Don't skip steps - infrastructure stability requires thorough validation.

The goal is not just to fix the immediate crisis, but to build monitoring and prevention systems that prevent similar crises in the future.

---

*Created by: Claude | Model: claude-sonnet-4-6 | 2026-02-19 02:30 UTC*