---
name: grill-with-docs-ui
description: Relentlessly interview the user to sharpen a repository plan or design through a persistent local browser form where they click answers, while recording resolved domain language in CONTEXT.md and durable architectural decisions as ADRs. Use when the user asks to grill a plan with a UI, run grill-with-docs-ui, or wants grilling questions answered in a browser form instead of chat.
---

# Grill with Docs UI

Read [grilling.md](references/grilling.md) and [domain-modeling.md](references/domain-modeling.md) completely before starting. Apply both workflows together: use the grilling design tree to drive the interview and the domain-modeling discipline to update repository documentation as terms and decisions resolve.

Read [context-format.md](references/context-format.md) before creating or editing a `CONTEXT.md`. Read [adr-format.md](references/adr-format.md) before offering, creating, or editing an ADR.

Every question goes through the Grill UI, never chat. Read [ui-protocol.md](references/ui-protocol.md) before the first round; it covers starting the UI, the round JSON, and waiting for answers.

Do not treat the interview notes as implementation authorization. Finish only when the decision frontier is empty and the user confirms shared understanding, then run `end` with a short summary.
