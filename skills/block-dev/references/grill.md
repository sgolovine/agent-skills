# Grill a Request and Record the Domain Model

Interview the user until all parties share one understanding. Use a design tree, an interview glossary, and short architecture decision records.

Write new grill documents under `<run-path>/grill/`. Treat repository context documents as read-only input.

Use [grill-templates.md](grill-templates.md) only when you create or update its applicable artifact.

## Prepare

1. Inspect the repository for facts that can affect the interview.
2. Read the root `CONTEXT-MAP.md` when it exists.
3. Use the map to find each bounded context.
4. Use the map to find each applicable architecture decision record directory.
5. Otherwise, read the root `CONTEXT.md` when it exists.
6. Treat a repository without a context map as one context.
7. Create an interview context file only after the first term is resolved.
8. Create an interview ADR directory only after the first decision qualifies.

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

Find repository facts before you ask the user. Treat an incomplete investigation as an unsettled prerequisite.

Continue with independent frontier questions during the investigation. The user decides each material choice.

## Make the Domain Language Precise

Apply these checks during each round:

- Show a glossary conflict when one term has different definitions.
- Propose one precise term for a vague or overloaded term.
- Test concrete edge cases that clarify boundaries and relationships.
- Show a conflict when code and the user description disagree.
- Identify the applicable bounded context.
- Ask the user when the applicable context is not clear.

## Update the Interview Glossary

After each resolved domain term, update the applicable interview `CONTEXT.md`.

An interview `CONTEXT.md` contains domain terms only. Apply these rules:

- Select one preferred term for each concept.
- Put prohibited synonyms in `_Avoid_`.
- Use a maximum of two sentences for each definition.
- Define the concept identity, not its behavior.
- Include only project domain terms.
- Do not add implementation details.
- Do not add specifications.
- Do not add programming concepts.
- Do not add design notes.
- Do not add scratch content.
- Add subheadings only when natural term groups exist.
- Keep one flat list when the terms form one group.

## Record Important Architecture Decisions

Offer an interview ADR only when all these conditions apply:

1. A later reversal has a meaningful cost.
2. A future reader will probably ask for the reason.
3. The decision contains a real trade-off between alternatives.

Examples include architecture shape, integration patterns, substantial technology lock-in, boundaries, explicit exclusions, and non-obvious constraints.

Do not create an ADR for an easily reversed choice. Do not create an ADR for a decision without alternatives.

Put each ADR in the applicable `docs/adr/` directory under `<run-path>/grill/`. Increment the highest existing number for its `NNNN-short-slug.md` name.

## Finish the Interview

The interview frontier must be empty before confirmation. No branch can contain a silent assumption.

1. Write the candidate result to `<run-path>/grill/shared-understanding.md`.
2. Include the stack base and applicable publication constraints.
3. Return the candidate to the Supervisor.
4. Apply each correction that the Supervisor returns.
5. Recalculate the frontier after a correction.
6. Record explicit confirmation in `shared-understanding.md`.
7. Report completion only after confirmation is recorded.

Remain responsible for the grill phase. Do not start specification work. Do not implement the design.
