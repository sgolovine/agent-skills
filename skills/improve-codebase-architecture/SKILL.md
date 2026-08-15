---
name: improve-codebase-architecture
description: Scan a codebase for architectural friction and deepening opportunities, present candidates in a visual HTML report, then interview the user to refine a selected design. Use when asked to review, improve, simplify, deepen, or redesign a repository's architecture, module interfaces, seams, testability, or AI navigability.
---

# Improve Codebase Architecture

Find refactors that turn shallow modules into deep ones: more behavior behind a smaller interface, placed at a clean seam, testable through that interface. Optimize for leverage, locality, and testability.

Before scanning, read [architecture-design.md](references/architecture-design.md). Read [html-report.md](references/html-report.md) before creating the report. After the user selects a candidate, read [grilling-and-domain-modeling.md](references/grilling-and-domain-modeling.md).

## 1. Scope the review

Respect repository instructions and preserve unrelated work.

- If the user names a module, subsystem, or pain point, review that scope.
- Otherwise, inspect a meaningful stretch of `git log --oneline` and changed paths to find hot spots. Widen the scan only when history is scattered or unavailable.
- Read the relevant `CONTEXT.md`, or use `CONTEXT-MAP.md` to locate the right context. Treat its terms as canonical domain language.
- Read relevant ADRs before proposing changes. Do not re-litigate recorded decisions without evidence of current friction.

## 2. Explore the codebase

If subagents are available, delegate an independent codebase walk after defining the scope. Continue inspecting locally while it runs. Give the agent paths and domain context, but not suspected findings.

Explore organically. Record evidence for:

- concepts spread across many small modules;
- shallow modules whose interface nearly matches their implementation;
- pure functions extracted for testability while bugs remain in their orchestration;
- tightly coupled modules that leak across seams;
- behavior that is untested or hard to test through the current interface.

Apply the deletion test to each suspected shallow module: if deleting it merely spreads its complexity across callers, it earns its place; if its complexity disappears, it is probably pass-through indirection.

Classify each candidate's dependencies using the categories in `architecture-design.md`. Do not recommend a seam without justified adapters.

## 3. Present candidates

Create a fresh single-file HTML report at `<temp-directory>/architecture-review-<timestamp>.html`. Resolve the operating-system temp directory from `$TMPDIR`, `/tmp`, or `%TEMP%`. Do not write report artifacts into the repository.

For every candidate include:

- involved files and modules;
- the architectural friction, supported by code evidence;
- a plain-language deepening proposal;
- locality, leverage, and testing benefits;
- a before-and-after visualization;
- recommendation strength: `Strong`, `Worth exploring`, or `Speculative`;
- a clear warning when the proposal conflicts with an ADR.

End with the strongest recommendation and why it should go first. Use project domain terms and the exact architecture vocabulary from `architecture-design.md`.

Open the report with the platform command (`xdg-open`, `open`, or `start`) when a graphical session is available. Always give the user the absolute path. Do not propose detailed interfaces yet. Ask: “Which of these would you like to explore?”

## 4. Refine the selected candidate

After the user chooses, interview them using the design-tree workflow in `grilling-and-domain-modeling.md`. Resolve constraints, dependencies, seam placement, what belongs behind the interface, and which tests should survive. Find repository facts yourself; ask the user for decisions.

Update domain documentation inline only when terminology or durable decisions genuinely crystallize. Do not modify the architecture until the user confirms shared understanding.

When the user wants alternative interfaces, use the Design It Twice workflow in `architecture-design.md`. Compare designs by depth, locality, seam placement, and dependency strategy, then make a clear recommendation.
