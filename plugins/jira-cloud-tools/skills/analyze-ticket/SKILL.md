---
name: analyze-ticket
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

Lead with the **readiness verdict**, then the **decision box**, then the two
universal layers, then the lens for the card type.

### Readiness verdict (first line)

The very first line, directly under the title/ticket line and above the decision
box, is a one-line readiness call — the "is it safe to proceed?" signal:

```
**Readiness: 🟢 PASS** — <why, + what this unlocks>
**Readiness: 🔴 BLOCKED** — <N open decisions, M unresolved risks; what to do>
```

It is **mechanical, not a judgment call**: the verdict is `PASS` if and only if
the decision box is clear — no open blocking decisions and no unresolved top
risk. Otherwise `BLOCKED`, and the message counts what's open and points at the
⚡ box. The loop is: read the verdict → resolve the ⚡ items in Jira → re-run →
the verdict flips once the box empties.

What "clear" requires is **type-aware** — see the shared **Definition of Ready**
(`../../reference/definition-of-ready.md`), the canonical criteria — e.g. a
Story isn't clear until it has testable AC, so missing AC surfaces as a blocking
item in the box and holds the verdict at BLOCKED. The PASS message names what the
pass unlocks for that type (Epic → decompose into features; Story → implement;
Bug → fix).

### Decision box (below the verdict)

The very first thing after the title/ticket line is a scannable "Act on this"
block — a one-look summary of what the reader must do, so they never have to read
the whole analysis to find the signal. Render it as a **markdown blockquote**
(it reflows at any width — do **not** use ASCII-bordered boxes, which misalign):

```
> ## ⚡ Act on this
>
> 🔴 **Top risk** — the single highest-impact risk or hidden scope.
>
> ❓ **Decisions needed (N)**
> 1. The first blocking question…
> 2. …
>
> 📊 **Status** — one-line rollup.
```

Rules:

- **Summary, not a replacement.** The box surfaces only the *blocking* subset.
  The full ambiguity list still lives in *What's vague / needs clarification*
  below — do not duplicate the long content into the box.
- **Type-aware fill** (mirror the lens below): Epic/Feature → scope or
  hidden-scope risk + child-status rollup; Story → MVP scope-creep risk + the
  sharpest INVEST red flag; Bug → repro/root-cause blocker + severity.
- **Caps, to stay scannable:** top risk ≤ ~2 lines, decisions ≤ 4 items, status
  one line.
- **Omit, don't pad.** No notable risk, or nothing genuinely blocking? Drop that
  line rather than inventing one.

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

### Readiness criteria (per type)

The criteria that decide whether the decision box counts as **clear** — and thus
whether the verdict reads PASS — are defined **once**, in the shared
[Definition of Ready](../../reference/definition-of-ready.md). Read it and apply
it; do not restate a private copy here (the `challenge-readiness` skill judges
by the same file, so they must not drift).

In short: any unmet criterion *is* a blocking item — put it in the box and the
verdict stays BLOCKED. And per the file's **implementation-safety ladder**, an
Epic PASS only green-lights decomposition; the green light to write code is a
**Story** verdict reading PASS (clear **and** testable AC present).

## Output shape

Present in chat as markdown, in this fixed order so the reader always knows where
to look:

1. **Title + ticket line** — `# KEY — Summary (Type) — Analysis`, then a compact
   meta line (type, status, parent, assignee/estimate). Link the ticket key to
   its URL (the script provides it).
2. **Readiness verdict** — the one-line `**Readiness: …**` call (see *Analysis
   model*), directly under the title and above the box.
3. **Decision box** — the `> ## ⚡ Act on this` blockquote (see *Analysis model*).
4. **High-level summary**, then the remaining headed sections for the universal
   layers and the type lens.

Keep the full clarifying questions as a numbered list under *What's vague /
needs clarification*; the decision box references only the blocking subset.

### Section headings (fixed emoji legend)

Give every section heading a leading emoji from this legend, so the same glyph
always marks the same kind of content and the reader can find a section by its
icon. Keep bold **sub-labels** inside sections (e.g. **Top risk**, **Gaps**) —
the emoji are for headings only, not inline labels.

| Section | Heading |
|---|---|
| Decision box | `## ⚡ Act on this` |
| High-level summary | `## 📝 High-level summary` |
| Scope & child rollup (Epic/Feature) | `## 🗂️ Scope & child rollup` |
| What's vague / clarification | `## ❓ What's vague / needs clarification` |
| Functional requirements | `## 📋 Functional requirements` |
| *Story* — acceptance criteria | `## ✅ Acceptance criteria` |
| *Story* — INVEST read | `## 💎 INVEST read` |
| *Bug* — reproduction | `## 🔁 Reproduction` |
| *Bug* — root cause | `## 🔍 Root cause` |
| *Bug* — severity / impact | `## 🚦 Severity & impact` |

The `❓` on the clarification section deliberately matches the `❓ Decisions
needed` label in the decision box, so the box's blocking subset and the full list
read as one family. For a section not in this legend, pick a glyph in the same
spirit — one icon, semantically apt, never decorative.

## Common mistakes

- **Restating the description as the "summary."** The summary must add
  understanding, not echo. If a business stakeholder couldn't act on it, rewrite.
- **Forcing every sub-point.** A tiny Story doesn't need a full INVEST essay.
  Apply the lens where it earns its place.
- **Ignoring comments.** Decisions, reversals, and answered ambiguities often
  live in the comment thread — fold them into the analysis.
- **Treating Feature like a Story.** Where a Jira uses Feature/Initiative as
  parent-level types, use the child-issue rollup, not the Story lens.
- **Padding the decision box.** It earns its place by being short and true. Don't
  promote a minor nitpick to "Top risk," and don't list non-blocking questions as
  "Decisions needed" — omit a line before you weaken it. A box that cries wolf
  stops getting the first look, which defeats its whole purpose.
- **Faking the verdict.** Readiness is mechanical: PASS only when the box is
  genuinely clear. Don't soften a BLOCKED to PASS to seem helpful, and never pass
  a Story that lacks testable AC. A wrong PASS green-lights unsafe work.
