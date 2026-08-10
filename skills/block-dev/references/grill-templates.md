# Grill Artifact Templates

Use these templates only when the applicable artifact is necessary.

## Artifact Layouts

For one context:

```text
<run-path>/grill/
├── CONTEXT.md
├── shared-understanding.md
└── docs/
    └── adr/
        └── 0001-short-decision.md
```

For multiple contexts:

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

## Question

```text
❓ **Q1** - **<question title>**: <question body and, when useful, choices>

➡️ <recommended answer>
```

## Context Glossary

```md
# {Context Name}

{One or two sentences that describe the context and its purpose.}

## Language

**Order**:
{A definition in one sentence or two sentences.}
_Avoid_: Purchase, transaction
```

## Context Map

```md
# Context Map

## Contexts

- [Ordering](./contexts/ordering/CONTEXT.md) — Receives and tracks customer orders
- [Billing](./contexts/billing/CONTEXT.md) — Generates invoices and processes payments

## Relationships

- **Ordering → Billing**: Ordering sends the confirmed order. Billing generates an invoice.
```

## Architecture Decision Record

```md
# {Short decision title}

{One to three sentences that give the context, decision, and reason.}
```

Add only the necessary optional sections:

- Status frontmatter: `proposed`, `accepted`, `deprecated`, or `superseded by ADR-NNNN`
- **Considered Options** for important rejected alternatives
- **Consequences** for effects that are not clear.
