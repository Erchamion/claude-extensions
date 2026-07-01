---
name: ready-check-ticket
description: Use when asked whether a Jira ticket is Ready or safe to proceed/implement, to "gate" a ticket, or for an independent second opinion on a ticket's readiness. Runs the FULL gated review of ONE ticket — a type-aware analysis plus a blind independent critic — and reconciles them into a single PASS/BLOCKED verdict. Read-only. NOT for a plain single-ticket summary (use analyze-ticket), and NOT for walking an epic's child issues (that is a separate feature). Triggers on readiness/gate intent, never on a bare "analyze".
---

# Ready-Check Ticket

## Overview

The **runner**: orchestrates the plugin's two review skills into one gated
verdict for a **single** ticket — analyze it, get an *independent* critic's blind
assessment, reconcile the two, and present. Read-only. Does not walk children.

This skill is the reusable unit a future "walk" feature will call once per node;
keep it single-ticket and side-effect-free.

## When to use

- "Is MOD-1234 ready?" / "gate MOD-1234" / "safe to implement MOD-1234?"
- "Give me a second opinion on this ticket's readiness."

Not for: a plain analysis (use `analyze-ticket`); walking an epic's children
(the walk feature); writing back to Jira.

## Procedure

1. **Analyze.** Produce the ticket analysis by following the
   `analyze-ticket` skill end to end (fetch → type-aware analysis → decision
   box → readiness verdict). Hold onto the analysis text and its verdict.

2. **Critique — blind & independent.** Dispatch `challenge-readiness` in
   **Independent mode** as a **subagent**, and **do NOT pass it your analysis** —
   true independence is the whole point. Give the subagent only:
   - the ticket key,
   - the paths to `skills/challenge-readiness/SKILL.md` and
     `reference/definition-of-ready.md` (to read and follow),
   - the fetch-script path.

   It returns a *structured* independent assessment: `verdict`, `blockers[]`,
   `risks[]`, `ac_status`, `judgment_calls[]`, `rubric_feedback[]`.

3. **Reconcile (diff).** Compare the critic's independent assessment against your
   analysis:
   - **Verdict** — agree or not? Disagreement is the headline.
   - **🕳️ Missed** — blockers/risks/AC-gaps the critic raised that your analysis
     lacked.
   - **⚖️ Disputed** — items your analysis had that the critic downgraded.
   - **❓ Judgment calls** / **🔧 Rubric feedback** — pass through for the human.

4. **Present — reconciled readout.** Lead with the **reconciled verdict** block,
   then a short "second opinion" delta (missed / disputed / verdict-diff), then
   the full analysis below. Reuse `analyze-ticket`'s decision-box and section
   emoji conventions so it all reads as one family.

## Reconciled verdict rules

- Both **PASS** → **PASS**.
- Both **BLOCKED** → **BLOCKED** (merge the blocker lists).
- **Disagree** → **⚠️ CONTESTED**: default to **BLOCKED**, and list exactly what
  would flip it (usually the critic's judgment calls). **Never silently take the
  looser verdict** — surface the disagreement for a human to settle.

## Output shape

```
> ## ⚖️ Reconciled readiness: 🔴 BLOCKED
> Analysis said 🔴 · Critic said 🔴 — agreed.   (or: ⚠️ CONTESTED — analysis 🟢, critic 🔴)
> <one-line reconciled reason + what would flip it, if contested>

## 🔎 Second opinion (independent critic)
🕳️ Missed: …   ⚖️ Disputed: …   ❓ Judgment calls: …   🔧 Rubric feedback: …

---
<the full analyze-ticket output>
```

## Common mistakes

- **Leaking the analysis to the critic.** If the critic sees your analysis it
  anchors and echoes. Dispatch it blind, every time.
- **Silently taking the looser verdict.** On disagreement, default to BLOCKED and
  surface why — a false PASS green-lights unsafe work.
- **Walking children.** This skill is single-ticket. Descending into child issues
  is the separate walk feature; do not do it here.
