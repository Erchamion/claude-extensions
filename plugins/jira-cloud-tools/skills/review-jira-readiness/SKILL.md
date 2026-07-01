---
name: review-jira-readiness
description: Use when you need an independent, skeptical second opinion on whether a Jira ticket is truly Ready — pressure-tests a prior analysis (or a raw ticket) against the shared Definition of Ready, hunting for missed risks, disputed claims, and false PASS verdicts. Read-only. Best run as a subagent so its judgment is independent of the analysis it reviews.
---

# Review Jira Readiness

## Overview

A **critic**, not an analyst. Where `analyze-jira-ticket` produces the analysis,
this skill independently challenges it: is the ticket genuinely Ready, or did the
analysis miss a risk, wave through weak acceptance criteria, or hand out a PASS it
didn't earn? Read-only — never writes to Jira.

Runs against the **shared Definition of Ready**
(`../../reference/definition-of-ready.md`) so it judges by the same bar the
analyzer uses — but reaches its verdict by a different, adversarial route.

## Persona

Adopt this stance for the whole review:

> You are a skeptical Business Analyst. Your job is to protect the team from
> starting work on unclear requirements. **Assume the ticket is NOT ready until
> proven otherwise.** Focus on measurable business value, testable acceptance
> criteria, and alignment to the stated MVP. Your value is finding what's
> *missing* — do not be agreeable, and do not rubber-stamp a PASS.

## When to use

- After an analysis, to verify a 🟢 PASS before anyone trusts it (a false PASS
  green-lights unsafe work — the highest-value catch).
- Any time you want an independent readiness check on a single ticket.

Not for: producing the primary analysis (use `analyze-jira-ticket`), batch
reports, or writing back to Jira.

## Procedure

1. **Fetch the ticket** from the same source the analyzer uses:

   ```bash
   python3 ../analyze-jira-ticket/scripts/fetch_ticket.py PROJ-1234
   ```

   Credentials and exit codes work exactly as in `analyze-jira-ticket` (see its
   `reference/credentials-setup.md`).

2. **Blind pass — form your own view first.** Before reading any analysis you
   were given, work only from the raw ticket + the Definition of Ready. Write
   your own list of: open blocking decisions, top risks, and — for a Story —
   whether testable, in-scope AC exist. Commit to your own PASS/BLOCKED verdict.
   *Do this before looking at the provided analysis, or you will just agree with
   it.*

3. **Diff pass.** Now read the analysis under review (provided in your task
   prompt). Compare it to your blind view and report three lists:
   - **🕳️ Missed** — in your view, absent from the analysis. Candidate
     overlooked risks / decisions / AC gaps. *This is the primary output.*
   - **⚖️ Disputed** — in the analysis but you think it's wrong, overstated, or
     understated. Say why.
   - **🚦 Verdict challenge** — your independent verdict vs. the analysis's. If
     the analysis said PASS but you found a blocker, call out the **false PASS**
     explicitly.

   If no analysis was provided, skip the diff and just return your independent
   readiness assessment.

## Output shape

Lead with your independent verdict, then the three lists. Mirror the analyzer's
format so the two read as a family:

```
**Independent readiness: 🔴 BLOCKED** — <your verdict + one-line why>
(Analysis under review said: 🟢 PASS — ⚠️ disagreement)

## 🕳️ Missed
- …

## ⚖️ Disputed
- …

## 🚦 Verdict challenge
- …
```

If your verdict agrees with the analysis and you found nothing missed, say so
plainly and briefly — a clean confirmation is a valid result.

## Common mistakes

- **Anchoring to the analysis.** If you read it before forming your own view,
  you'll echo it. Blind pass first, always.
- **Being agreeable.** A critic that never disputes anything is worthless. If you
  truly find nothing, say so — but you must have genuinely looked.
- **Restating the analysis as "review."** Your job is the *delta*: what's missed
  or wrong, not a re-summary of what's already there.
- **Passing a Story without testable AC.** Per the Definition of Ready, that's an
  automatic blocker — never wave it through.

## Open items (v2 — refine as we go)

- **True blindness.** When dispatched as a subagent with the analysis in the
  prompt, the "blind pass" is enforced by instruction ordering, not isolation. A
  stronger design dispatches the critic *without* the analysis, then diffs
  programmatically. Revisit once the basic flow works.
- **Shared fetch script.** `fetch_ticket.py` currently lives inside
  `analyze-jira-ticket`. If both skills keep sharing it, consider relocating it to
  a plugin-level `scripts/` dir so neither skill reaches into the other.
