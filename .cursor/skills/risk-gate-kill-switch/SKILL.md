---
name: risk-gate-kill-switch
author: ashmht
status: alpha
description: >-
  Playbook for implementing or reviewing a pre-trade/pre-transaction risk
  gate or kill switch. Use when adding risk controls, position limits, or an
  emergency stop to a trading or money-movement system.
args:
  - name: target
    description: The risk control being added (e.g. "position size cap", "kill switch", "spend limit rule")
    required: true
---

# Risk Gate & Kill Switch

Every risky action (a trade, transfer, or new position) should pass through one
gate that can deny the action but cannot create an unreviewed partial approval.

## When This Skill Applies

- Adding a new risk rule, limit, or approval requirement to an existing
  gate.
- Building a new gate from scratch for a system that moves money, opens
  positions, or executes trades.
- Adding or modifying a kill switch / emergency stop.

## Non-negotiables

1. **Single gate, no bypass.** Every capital-risking or money-moving action
   calls the same gate function — there is no second code path that skips
   it "just for this one case."
2. **Deny-by-default, deny-dominates.** An empty/unconfigured policy denies,
   not allows. If any single rule fails, the action is denied regardless of
   what other rules or pending approvals say. This outcome must be
   invariant under rule reordering — property-test it: shuffle the rule
   evaluation order across many runs and confirm the allow/deny outcome
   never changes.
3. **Evaluate every rule — no short-circuit.** Don't return on the first
   failing rule. The full decision trace (which rules passed, which failed,
   why) is the product, not a debug artifact; a caller or reviewer should
   be able to see the complete reasoning, not just the first blocker.
4. **Kill switch is unconditional and propagates within one cycle.** When
   engaged, it blocks every new risk-taking action immediately — it is not
   "one more rule in the list," it's evaluated before/above everything
   else, and there's a test proving it wins even when other conditions
   would otherwise allow the action.
5. **Exit/stop priority is explicit and total.** If multiple conditions can
   trigger simultaneously (kill switch, stop-loss, take-profit, max-hold,
   policy violation), define and test the priority order so the outcome is
   deterministic when more than one applies at once.
6. **A simulate/dry-run path exists and is identical to the real path**,
   except it doesn't mutate state — useful for both testing and giving
   callers a way to check "would this be allowed" without side effects.
7. **Position/spend sizing never exceeds its cap regardless of
   confidence/conviction inputs.** If the gate takes a confidence or
   conviction score, prove by property test that no value of that input can
   push the resulting size past the hard cap.
8. **Backtest and live share the exact same decision/exit logic.** If
   there's a backtester, it must call the identical function the live loop
   calls — a backtest result computed against different logic than
   production means nothing. Enforce this structurally (one shared
   function/module), not just by convention.
9. **Version-pin decisions against concurrent updates.** If a policy/limit
   can change while an action is in flight (e.g. approval workflows), pin
   the action to the policy version live at receipt, but re-check any
   *cumulative* state (like spend-within-a-window) against current history
   — otherwise two approvals that each individually fit a cap can combine
   to exceed it. This race is easy to miss and worth a dedicated test.

## Workflow

1. **Find the existing gate function** before adding a new rule — new rules
   extend it, they don't create a parallel check elsewhere.
2. **Write the property test for the new rule first**: "no sequence of
   inputs can produce an outcome that violates X," using property/model-based
   testing (fast-check, Hypothesis) over arbitrary interleavings if the rule
   involves state accumulated over time (e.g. spend within a window).
3. **Test the kill switch against the new rule**: confirm the kill switch
   still wins even when the new rule alone would have allowed the action.
4. **Test rule-order invariance**: shuffle rule evaluation order (if the
   gate evaluates a rule list) and confirm the outcome doesn't change.
5. **Confirm the decision trace includes the new rule's result**, pass or
   fail, not just on failure.
