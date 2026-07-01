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
- **No unresolved top risk** — no known hidden scope or unmitigated risk that
  would derail the work.

`clear` is necessary at every level. It is not, by itself, sufficient to start
**coding** — see the ladder below.

## Level / type criteria

Each row lists what must additionally be true for that type to count as clear,
and what a PASS unlocks.

| Type | Clear when… | PASS unlocks |
|------|-------------|--------------|
| **Epic / Feature / Initiative** | Universal gate + children identified + scope (incl. any stated MVP) coherent. | Decompose into / refine the child features. |
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
