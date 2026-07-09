# Project Agent Workflow — Operating Guide

This project uses a team of nine specialist subagents (in `.claude/agents/`).
This file tells you (the main session) what each one is for and when to delegate
to it. Delegate to the right specialist instead of doing their job yourself.

## Golden rules
- **Delegate, don't improvise.** When a task matches an agent's role below, call
  that agent rather than handling it inline.
- **One agent at a time.** Subagents run sequentially and cannot call each other.
  YOU (the main session) are the coordinator: you call one, read its result, then
  call the next. If an agent returns a *plan* (task-router, feature-integration),
  you execute that plan by calling the named agents yourself.
- **Agents have strict lanes.** Most are read-only or advisory. Only the refactor
  agent writes code, and only in isolation. Respect each agent's boundaries.
- **Evidence over claims.** For anything involving tests or merge-safety, require
  the agent to have actually run the tests, not asserted success.

## Safety boundaries (hard rules)
- Never merge to `main` or push to a protected branch without an explicit human OK.
- Anything touching infrastructure or secrets requires human approval first.
- Never put secrets/tokens in prompts or files — use environment variables.
- The refactor agent works only in an isolated worktree; never on the live tree.

---

## The nine agents — roster and triggers

### 1. repo-knowledge-agent  (read-only)
**Call when:** you need to understand THIS repo — structure, where something lives,
how modules depend on each other, what changed recently.
**Triggers:** "how does X work", "where is Y", "map this repo", "what changed".
**Does not:** edit code, approve, or merge.

### 2. branch-approval-agent  (review-only)
**Call when:** a branch/PR is finished and you need to decide if it's safe to merge.
**Triggers:** "review this branch", "is this PR safe to merge", "check these changes".
**Produces:** approve / request_changes / reject, with findings + test evidence.
**Does not:** write or fix the code, or perform the merge.

### 3. cicd-rca-agent  (diagnose-only)
**Call when:** a CI/CD pipeline or build FAILED and you need the root cause.
**Triggers:** "why did the build fail", "diagnose this pipeline failure", a failing log.
**Produces:** root cause + recommended fix + confidence.
**Does not:** edit source, change pipeline config, or rerun anything.

### 4. checklist-monitor-agent  (between-steps tracker)
**Call when:** a multi-step task is running and you want to check progress or catch
a stall. Call it BETWEEN steps — it does not watch a live agent in real time.
**Triggers:** "track progress on this", "are we stuck", after each major step.
**Key value:** flags when the same item fails repeatedly → stop looping, get a human.

### 5. task-router-agent  (planner)
**Call when:** you're unsure which agent(s) should handle a task.
**Triggers:** "which agents should handle X", "plan the approach for Y".
**Produces:** an ordered plan of which agents to call. YOU then call them — the
router does not invoke anyone itself.

### 6. skill-author-agent  (capture)
**Call when:** a non-trivial task finished successfully and the approach is worth
reusing. Invoke explicitly.
**Triggers:** "save this as a skill", "capture how we did this".
**Does not:** write a skill for one-off work — it judges generality first.

### 7. best-practices-advisor  (advisory, read-only)
**Call when:** planning or reviewing, and you want standards guidance on code
structure, architecture, integration, or UI/accessibility.
**Triggers:** "what best practices apply", "how should this be structured".
**Does not:** edit code — it recommends; the author or refactor agent acts.

### 8. feature-integration-agent  (cross-repo planner)
**Call when:** a feature spans multiple repos (e.g. backend + frontend) and the
pieces must agree on a contract.
**Triggers:** "plan this feature across repos", "define the API contract for X".
**Produces:** the contract, build order, and per-repo steps. YOU execute the plan.
**Does not:** write code or invoke other repos' agents itself.

### 9. refactor-agent  (the only writer — isolated)
**Call when:** code needs structural change (rename, extract, restructure) without
changing behavior.
**Triggers:** "refactor X", "restructure this module", "clean up Y safely".
**How it works:** isolated git worktree, one small slice at a time, tests after
each, hands a diff to branch-approval-agent.
**Does not:** merge, force-push, or change behavior under the banner of "refactor".

---

## Typical workflow (how the agents hand off)

```
Plan a feature          → task-router (who does what) / feature-integration (across repos)
Understand the code     → repo-knowledge
Check standards         → best-practices-advisor
Make structural changes → refactor-agent (isolated)
Track progress          → checklist-monitor (between steps)
Finished? review the PR → branch-approval
Build broke?            → cicd-rca
Worth reusing?          → skill-author
```

Each agent owns one moment in the lifecycle. Route to the one whose lane fits,
call them one at a time, and coordinate their handoffs yourself.
