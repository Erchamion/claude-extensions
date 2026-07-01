---
description: Gated readiness review of one Jira ticket (analysis + independent critic + reconciled PASS/BLOCKED verdict)
argument-hint: <TICKET-KEY>
---

Use the `gated-ticket-review` skill to run a full gated readiness review of Jira
ticket **$ARGUMENTS**.

Follow the skill exactly:
1. Analyze the ticket (`analyze-jira-ticket`).
2. Dispatch the `review-jira-readiness` critic as a subagent in **Independent
   mode**, **blind** — do not show it the analysis.
3. Reconcile the two into a single verdict (default to BLOCKED on disagreement,
   and surface the disagreement).
4. Present the reconciled readout.

This is a **single-ticket** review — do **not** walk child issues.
