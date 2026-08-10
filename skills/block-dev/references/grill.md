# Grill a Request and Record the Domain Model

Interview the user until all parties share one understanding. Use a design tree, an interview glossary, and short architecture decision records.

Write all new grill documents under `<run-path>/grill/`. Create as many interview documents as the interview needs.

Treat repository context documents as read-only input during this phase.

## Prepare

1. Inspect the repository for facts that can affect the interview.
2. Read the root `CONTEXT-MAP.md` when it exists.
3. Use the context map to find each bounded context and its `CONTEXT.md`.
4. Use the context map to find each applicable architecture decision record (ADR) directory.
5. Otherwise, read the root `CONTEXT.md` when it exists.
6. Treat a repository without a context map as one context.
7. Do not create an interview context file before the first resolved term exists.
8. Do not create an interview ADR directory before the first applicable decision exists.

Use this structure for one context:

```text
<run-path>/grill/
├── CONTEXT.md
├── shared-understanding.md
└── docs/
    └── adr/
        ├── 0001-event-sourced-orders.md
        └── 0002-postgres-for-write-model.md
```

Use this structure for multiple contexts:

```text
<run-path>/grill/
├── CONTEXT-MAP.md
├── shared-understanding.md
├── docs/
│   └── adr/
└── contexts/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## Work the Design Tree

Treat each decision as one node. Treat each dependent decision as a branch.

The **frontier** contains decisions that have all prerequisite answers. Work in interview rounds:

1. Recalculate the frontier after each answer or new repository fact.
2. Ask all ready frontier questions in the current round.
3. Number each question.
4. Give one recommended answer for each question.
5. Delay a question when its answer depends on an open question.
6. Return the question batch to the Supervisor.
7. Wait for the user answers before the next round.

Use this exact question format:

```text
❓ **Q1** - **<question title>**: <question body and, when useful, choices>

➡️ <recommended answer>
```

Find repository facts before you ask the user. Use available inspection tools for this work.

Treat an incomplete investigation as an unsettled prerequisite. Continue with independent frontier questions while the investigation continues.

The user decides each material choice. Do not decide silently for the user.

## Make the Domain Language Precise

Apply these checks during each round:

- Show a glossary conflict when the user gives a term a different definition.
- Propose one precise term when the user gives a vague or overloaded term.
- Test concrete edge cases that clarify boundaries and relationships.
- Show a conflict when code and the user description disagree.
- Identify the applicable bounded context.
- Ask the user when the applicable context is not clear.

For example, ask whether `account` means **Customer** or **User**.

## Update the Interview Glossary

After each resolved domain term, update the applicable interview `CONTEXT.md`. Do not delay the update until the interview ends.

An interview `CONTEXT.md` contains domain terms only. Do not add implementation details, specifications, programming concepts, design notes, or scratch content.

Use this format:

```md
# {Context Name}

{One or two sentences that describe the context and its purpose.}

## Language

**Order**:
{A one-sentence or two-sentence definition}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment that a customer receives after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

Apply these glossary rules:

- Select one preferred term for each concept.
- Put prohibited synonyms in `_Avoid_`.
- Use one sentence or two sentences for each definition.
- Define the concept identity, not its behavior.
- Include only project domain terms.
- Exclude general terms such as timeouts, error types, and utility patterns.
- Add subheadings only when natural term groups exist.
- Keep one flat list when the terms form one group.

For multiple contexts, use an interview `CONTEXT-MAP.md` such as this example:

```md
# Context Map

## Contexts

- [Ordering](./contexts/ordering/CONTEXT.md) — Receives and tracks customer orders
- [Billing](./contexts/billing/CONTEXT.md) — Generates invoices and processes payments
- [Fulfillment](./contexts/fulfillment/CONTEXT.md) — Manages warehouse selection and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced`. Fulfillment receives the event and starts item selection.
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched`. Billing receives the event and generates an invoice.
- **Ordering ↔ Billing**: The contexts share `CustomerId` and `Money` types.
```

## Record Important Architecture Decisions

Offer an interview ADR only when the decision meets all three conditions:

1. A later reversal has a meaningful cost.
2. A future reader will probably ask for the reason.
3. The decision contains a real trade-off between alternatives.

These decisions can qualify:

- The architecture shape, such as a monorepo or an event-sourced write model
- An integration pattern between contexts
- A technology choice that causes substantial lock-in
- An ownership, boundary, or scope decision
- An explicit exclusion
- An intentional change from an expected solution
- A constraint that the code does not show
- A rejected alternative when its rejection reason is not clear.

Do not create an ADR for an easily reversed choice. Do not create an ADR for an obvious choice or a decision without alternatives.

Put interview ADRs in the applicable `docs/adr/` directory under `<run-path>/grill/`. Create that directory only when the first ADR qualifies.

Find the highest number in that directory. Increment the number and use `NNNN-short-slug.md`.

Use this minimum format:

```md
# {Short decision title}

{One to three sentences that give the context, decision, and reason.}
```

Add an optional section only when it gives necessary information:

- Add status frontmatter when the decision can change.
- Use `proposed`, `accepted`, `deprecated`, or `superseded by ADR-NNNN`.
- Add **Considered Options** when rejected alternatives are important.
- Add **Consequences** when the decision has non-obvious effects.

## Finish the Interview

The interview frontier must be empty before the confirmation step. No branch can contain a silent assumption.

Write the candidate result to `<run-path>/grill/shared-understanding.md`. Include the stack base and applicable publication constraints.

Return the candidate shared understanding to the Supervisor. Remain responsible for the grill phase.

The Supervisor asks the user to confirm or correct the candidate. The Supervisor keeps the human decision in the main interaction.

The Supervisor returns the response to the same Grill Worker when resume support exists.

Otherwise, the Supervisor starts a replacement Grill Worker. The replacement reads all durable grill documents before it applies the user response.

When the Supervisor returns the user response, apply each correction. Recalculate the frontier after a correction.

When the user confirms the candidate, record the explicit confirmation in `shared-understanding.md`. Then report that the grill phase is complete.

Do not start specification work before the Grill Worker reports completion. Do not implement the design during the grill phase.
