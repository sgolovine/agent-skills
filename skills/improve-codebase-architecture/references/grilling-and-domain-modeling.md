# Grilling and Domain Modeling

## Design-tree interview

Map the selected architecture candidate as a decision tree. Work in rounds. The frontier is every decision whose prerequisites are settled; ask the whole frontier together, but defer questions that depend on an unresolved answer.

For every question:

```md
❓ **Q1 — <title>**: <decision and relevant choices>

➡️ <recommended answer and brief rationale>
```

Recompute the frontier after each response. Inspect the repository for facts instead of asking the user to retrieve them. Ask the user to make value judgments and trade-offs. Finish when the frontier is empty, then ask the user to confirm the shared understanding before implementation.

Cover at least the constraints, dependency category, seam location, interface knowledge, hidden implementation, adapters, migration risk, and tests that should remain at the new interface.

## Domain language

Use `CONTEXT-MAP.md` when present to find context-specific glossaries; otherwise use the root `CONTEXT.md`. Create domain files lazily, only when there is resolved content to record.

- Challenge language that conflicts with the glossary.
- Turn vague or overloaded terms into one canonical domain term.
- Stress-test domain relationships with concrete edge cases.
- Check claims against the code and surface contradictions.
- When a new or sharpened term is resolved, update the relevant `CONTEXT.md` immediately.

Keep `CONTEXT.md` implementation-free. Use this compact shape:

```md
# <Context Name>

<One or two sentence purpose.>

## Language

**Order**:
<One or two sentence domain definition.>
_Avoid_: Purchase, transaction
```

Only record project-specific concepts. Pick one preferred name, list rejected synonyms under `_Avoid_`, and keep definitions to one or two sentences.

## ADR discipline

Offer an ADR only when the decision is hard to reverse, surprising without context, and the result of a real trade-off. A temporary priority or self-evident choice does not qualify.

If the user rejects a candidate for a durable, load-bearing reason, ask whether they want that reason recorded so a future review does not repeat the proposal.

Store ADRs in the applicable `docs/adr/` directory as `<next-number>-<slug>.md`. Create the directory lazily and increment the highest existing number. Default to a title and a one-to-three sentence paragraph covering context, decision, and rationale. Add status, options, or consequences only when they preserve important information.
