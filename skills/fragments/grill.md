# Grill a Plan and Record the Domain Model

Interview the user until you and the user have a shared understanding. Model the discussion as a design tree, maintain the project glossary as terms become clear, and record only important architectural decisions.

## Prepare

1. Inspect the repository for facts that can affect the discussion.
2. Read the root `CONTEXT-MAP.md` if it exists. Use it to find each bounded context, its `CONTEXT.md`, and its ADR directory.
3. Otherwise, read the root `CONTEXT.md` if it exists and treat the repository as one context.
4. Do not create a context file or an ADR directory before there is content to record.

A repository with one context normally has this structure:

```text
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

A repository with multiple contexts normally has this structure:

```text
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          # System-wide decisions
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                 # Context-specific decisions
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## Build and Work the Design Tree

Each decision is a node. Decisions that depend on it are its branches. The **frontier** contains all decisions for which the prerequisites are settled.

Work in rounds:

1. Recompute the frontier after each user response or new fact.
2. Ask all frontier questions that are ready in the current round.
3. Number each question and give a recommended answer.
4. Do not ask a question if its answer depends on an open question in the same round. Ask it in a later round.
5. Wait for the user's answers before you start the next round.

Use this format for each question:

```text
❓ **Q1** - **<question title>**: <question body and, when useful, choices>

➡️ <recommended answer>
```

Find facts yourself. Inspect files and use available tools or subagents instead of asking the user for information that you can obtain. If an investigation is still running, treat its result as an unsettled prerequisite. Continue with independent frontier questions while the investigation runs.

The user decides. Do not silently decide for the user.

## Sharpen the Domain Language During Each Round

Apply these actions as the discussion proceeds:

- **Challenge glossary conflicts.** If the user uses a term differently from its definition in `CONTEXT.md`, show the conflict and ask which meaning is correct.
- **Replace vague or overloaded terms.** Propose one precise canonical term. For example, ask whether "account" means **Customer** or **User**.
- **Test concrete scenarios.** Invent edge cases that make the boundaries and relationships between concepts explicit.
- **Check statements against the code.** If the code contradicts the user's description, show the contradiction and ask which behavior is correct.
- **Select the applicable context.** In a multi-context repository, infer the applicable context. Ask if it is not clear.

## Update the Glossary Immediately

When a domain term is resolved, update the applicable `CONTEXT.md` in the same round. Do not collect resolved terms for a later update. If no context file exists, create the root `CONTEXT.md` when the first term is resolved.

`CONTEXT.md` is only a domain glossary. Do not put implementation details, specifications, general programming concepts, design notes, or scratch content in it.

Use this format:

```md
# {Context Name}

{One or two sentences that describe the context and why it exists.}

## Language

**Order**:
{A one- or two-sentence definition}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

Apply these glossary rules:

- Select one preferred word for each concept. Put synonyms that contributors must not use in `_Avoid_`.
- Keep each definition to one or two sentences. Define what the concept is, not what it does.
- Include only terms that are specific to the project domain.
- Do not include general concepts such as timeouts, error types, or utility patterns.
- Add subheadings only when natural groups of terms emerge. Keep one flat list if the terms form one cohesive group.

For multiple contexts, use a root `CONTEXT-MAP.md` like this:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md) — manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

## Offer ADRs Sparingly

Offer an ADR only when the decision meets all three conditions:

1. **Hard to reverse:** A later change has a meaningful cost.
2. **Surprising without context:** A future reader is likely to ask why the project uses this choice.
3. **A real trade-off:** The team considered genuine alternatives and selected one for specific reasons.

Decisions that can qualify include:

- Architectural shape, such as a monorepo or an event-sourced write model.
- Integration patterns between contexts.
- Technology choices with substantial lock-in, such as a database, message bus, authentication provider, or deployment target.
- Ownership, boundary, and scope decisions, including explicit exclusions.
- Deliberate deviations from an expected solution.
- Constraints that code does not show, such as compliance or external response-time requirements.
- Rejected alternatives when the reason for rejection is not clear.

Do not create an ADR for an easy-to-reverse choice, an obvious choice, or a decision with no genuine alternative.

ADRs belong in the applicable `docs/adr/` directory. Create that directory only when the first ADR is needed. Scan the directory for the highest number and increment it. Use the file name `NNNN-short-slug.md`.

Use this minimal format:

```md
# {Short title of the decision}

{One to three sentences that state the context, the decision, and the reason.}
```

Add an optional section only when it gives useful information:

- Add status frontmatter (`proposed`, `accepted`, `deprecated`, or `superseded by ADR-NNNN`) when the decision can be revisited.
- Add **Considered Options** when rejected alternatives are important to remember.
- Add **Consequences** when the decision has non-obvious downstream effects.

## Finish

The session is complete only when the frontier is empty and no branch contains a silent assumption. State the resulting shared understanding and ask the user to confirm it. Do not implement the plan or design before the user confirms that you have reached a shared understanding.
