---
name: analyze-jira-ticket
description: Use when asked to analyze, review, summarize, or understand a Jira ticket or issue, or when given a bare Jira issue key (e.g. PROJ-1234, ABC-987) to look into. Works from any repo or session — fetches the ticket from Jira read-only and produces a type-aware analysis.
---

# Analyze Jira Ticket

## Overview

Fetch one Jira ticket plus its context and produce a readable, **type-aware**
analysis: a plain-language summary first, then the lens that matters for what
*kind* of card it is (Epic/Feature, Story, Bug). Read-only — never writes to
Jira.

## When to use

- "Analyze PROJ-1234" / "what's ABC-987 about?" / "review this Jira card"
- A bare issue key dropped into the conversation to investigate
- Prepping to discuss a ticket with the business or refine it before work

Not for: board/column batch reports, or writing back to Jira (AC, comments,
transitions). This skill is single-ticket and read-only.

## Procedure

1. Run the fetch script. It lives in `scripts/fetch_ticket.py` **beside this
   SKILL.md** — use that same directory's path (the Skill tool gives you this
   skill's base directory; if you reached this file directly, the script is in
   `scripts/` next to it):

   ```bash
   python3 <this-skill-dir>/scripts/fetch_ticket.py PROJ-1234
   ```

   Requires Python 3. If `python3` isn't found (common on Windows), use `python`
   (or `py -3`) instead — the script itself is cross-platform.

   It prints structured markdown: fields, description, **attachment list**,
   subtasks, linked issues, comments, and — for parent-level cards
   (Epic/Feature/Initiative) — a rollup of child issues. Credentials are read
   from env vars, then `~/.config/jira/.env`, then a walked-up `.env`
   (see `reference/credentials-setup.md`).
2. If it exits non-zero, surface the message. Exit `2` = credentials missing
   (point the user to `reference/credentials-setup.md`); exit `1` = ticket not
   found / no access.
3. **Attachment contents are not rendered** — only names/URLs. If the
   description references data that lives in an attachment (a pasted table,
   screenshot, "see attached list"), say so and ask the user for it inline; do
   not silently analyze around the gap.
4. **If a relevant code repo is at hand** (you're in or near the project the
   ticket is about), investigate the code, not just the Jira text — especially
   for Bugs. Reading the implementation to find the actual root cause produces a
   far stronger analysis than ticket text alone.
5. Read the output and produce the analysis below, **in chat**. Only write it to
   a file if the user asks.

## Analysis model

Always lead with the two universal layers, then add the lens for the card type.

### Universal (every card type)

1. **High-level summary** — plain language: what this card is about and why it
   exists. Pitch it so the reader can speak to the business intelligently about
   it, not a restatement of the description.
2. **What's vague / needs clarification** — concrete ambiguities, and the
   specific clarifying questions to ask. Pull signal from comments (decisions
   already made or reversed often live there).

### Type-aware lens

Apply the lens that fits the `Type` field. It's a strong default — include the
sub-points that the card actually warrants, skip ones that don't apply.

| Type | Lens |
|------|------|
| **Epic / Feature / Initiative** (parent-level) | Initiative-level summary using the **child-issue rollup**: the goal, the value, and what's in vs. out of scope. Note child status spread (how much is done/closed vs. open) and any obvious gaps in the breakdown. Frame scope at the initiative level. |
| **Story** | **MVP-alignment / scope-creep check**: given what the ticket calls MVP, is the scope/AC aligned, or has extra crept in? Then propose **Gherkin acceptance criteria** (Given/When/Then), and give a brief **INVEST** read (is it independent, small, testable?). |
| **Bug** | Repro clarity (are steps sufficient?), expected-vs-actual, impact/severity, and what's **missing** to reproduce or to verify the fix. When the code is available, trace the **root cause** in the implementation and distinguish a proper code fix from a workaround. |
| **Other / unknown** | Universal layers only, plus whatever naturally fits. |

## Output shape

Present in chat as markdown: a short summary paragraph, then headed sections for
the universal layers and the type lens. Keep clarifying questions as a numbered
list the user can act on. Link the ticket key to its URL (the script provides
it).

## Common mistakes

- **Restating the description as the "summary."** The summary must add
  understanding, not echo. If a business stakeholder couldn't act on it, rewrite.
- **Forcing every sub-point.** A tiny Story doesn't need a full INVEST essay.
  Apply the lens where it earns its place.
- **Ignoring comments.** Decisions, reversals, and answered ambiguities often
  live in the comment thread — fold them into the analysis.
- **Treating Feature like a Story.** Where a Jira uses Feature/Initiative as
  parent-level types, use the child-issue rollup, not the Story lens.
