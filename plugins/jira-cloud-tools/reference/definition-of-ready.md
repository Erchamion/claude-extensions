# Definition of Ready (shared)

Single source of truth for what "Ready" means across the `jira-cloud-tools`
plugin. **Both** skills reference this file so the criteria never drift:

- `analyze-jira-ticket` — *surfaces* unmet criteria as blocking items in the
  decision box, and computes the PASS/BLOCKED readiness verdict from them.
- `review-jira-readiness` — *independently challenges* a ticket against these
  same criteria, hunting for anything the analysis missed.

Same destination (is it Ready?), reached two different ways. Edit the criteria
here and both consumers stay in sync.

## The universal gate

A ticket is **clear** when its decision box is empty:

- **No open blocking decisions** — every question whose answer changes the work
  is resolved (in the ticket: comments, fields, updated AC).
- **No unresolved premise-threatening risk** — no known risk that could
  invalidate this ticket's core premise *at its own level* (see below). Risks that
  are real but belong to the next level down are recorded as **notes**, not
  blockers.

`clear` is necessary at every level. It is not, by itself, sufficient to start
**coding** — see the ladder below.

## Premise-threatening vs. downstream risk

A risk holds the gate only when it could **invalidate the ticket's core premise at
its own level** — the assumption the rest of the work is built on. A risk that is
real but resolvable during the *next* level's work is a **downstream note**.

- **Premise-threatening (blocks).** If true, the ticket is mis-scoped and anything
  built on it would be wrong. *Example (Epic):* the MVP is framed as a "thin
  parallel of Sales BestFit," but the service-tech availability + service-ADS data
  layer it depends on may not exist. If it doesn't, the premise is false — this
  blocks the epic.
- **Downstream (note).** Real, but it lands on a child and can be pinned when that
  child is written; it doesn't change whether *this* level is coherent. *Example
  (Epic):* "ADS" is undefined in the ticket — fine at epic level, must be pinned
  before the ranking *stories* are written.

**Passing a level while still holding open risks is itself a mandatory judgment
call:** state, for each remaining risk, why it is downstream and not
premise-threatening. Never pass silently over an open risk.

**What counts as a dependency being "confirmed or tracked"** (for the Epic gate's
external-dependency item): a **parent, ancestor, or sibling** ticket does **not**
by itself satisfy it. The dependency is *tracked* only via an explicit dependency
link (e.g. "depends on" / "is blocked by") to the specific issue that delivers it,
or an in-ticket statement that the system/data already exists. An inferred or
hierarchical relationship — "it's under the Service Domain epic, so it must be
covered" — is **not** evidence of delivery, and leaning on one is a false PASS.

## Blocking decision vs. tuning note

Not every open question is a blocker. Test each one before it goes in the box:

- A **blocking decision** changes the *shape* of the work — you cannot decompose
  or implement coherently until it's answered.
- A **tuning note** is a value or parameter that can be set (or changed) later
  without reshaping the work. In particular: **a parameter the ticket already
  requires to be _configurable_ is a tuning note, not a blocker.** The story only
  needs to *make it configurable* — which the requirement already mandates — not
  to fix the final value now. The blocker, if any, is *failing to make it
  configurable*, never the pending value.

  *Example:* "Prepaid/Proactive window: 7 or 14 days?" is a tuning note when a
  requirement mandates configurable ranking — decomposition and implementation
  proceed with the window as a config value; the number can land post-MVP.

- **Ordering / precedence between an already-enumerated set** (e.g. which lead
  type wins a tie) is a tuning note *when the set and the resolution mechanism are
  defined and the mechanism is required to be configurable* — only an *undefined*
  set of options, or a precedence that changes *which code paths must exist*, is a
  blocking decision.

When you genuinely can't tell which side a question falls on, **do not silently
decide** — surface it as a question for a human (the `review-jira-readiness`
critic does this explicitly).

## Level / type criteria

Each row lists what must additionally be true for that type to count as clear,
and what a PASS unlocks.

| Type | Clear when… | PASS unlocks |
|------|-------------|--------------|
| **Epic / Feature / Initiative** | Universal gate + children identified (present as linked issues; their *granularity* is judged during decomposition, not at this gate — a single coarse child doesn't block but is surfaced as a decomposition-risk note) + scope (incl. any stated MVP) coherent + **any external system/data the MVP premise depends on is confirmed to exist or tracked as an explicit linked dependency** (an unverified dependency the premise rests on is a premise-threatening blocker). | Decompose into / refine the child features. |
| **Story** | Universal gate + **testable, in-scope acceptance criteria present** (see below). Missing, vague, or out-of-scope AC is itself a blocking item. | Start implementation. |
| **Bug** | Universal gate + reliable repro (expected-vs-actual + sufficient steps) + known impact/severity. No reliable repro is a blocking item. | Start the fix. |
| **Other / unknown** | Universal gate only. | Proceed per context. |

## MVP alignment (cross-cutting)

When the epic states an MVP goal, alignment is a **hard gate at every level**:

- The **epic's** scope is coherent with its own stated MVP — nothing in-scope
  contradicts the MVP framing.
- Each **feature** advances the epic's MVP goal; a feature that only serves
  post-MVP ambition is scope creep and is a blocking item.
- Each **story's** AC stays within the MVP boundary its parent declared; AC that
  reaches beyond MVP is out-of-scope and blocks the story.

Trace the line MVP → epic → feature → story. A break anywhere is a blocker.

## What counts as testable acceptance criteria

AC is "testable" only if all of these hold:

- **Behavioural, not restated requirement** — describes an observable outcome,
  not a paraphrase of the functional requirement.
- **Given/When/Then** (or an equally concrete, verifiable form).
- **Measurable / unambiguous** — a reader can decide pass/fail without guessing;
  no "should be fast", "handle errors gracefully" without a concrete bar.
- **In scope** — tied to this story's slice and inside the MVP boundary.

Note: **functional requirements are not acceptance criteria.** An FR ("the
system shall…") is a capability; AC is the test that proves a specific story
delivered it. An epic may have FRs and *no* AC and still be Ready — AC appears
when FRs are decomposed into stories.

## The implementation-safety ladder

`clear` is required at every level, but you implement **stories**, not epics. So:

- An **Epic** PASS green-lights **decomposition**, never coding.
- The green light to **write code** is a **Story** verdict reading PASS —
  meaning clear **and** testable, in-scope AC present.

This ladder is the whole point of the gate: it tells you *when it is safe to
start implementation work*, and the answer is always "at a Story that passes."
