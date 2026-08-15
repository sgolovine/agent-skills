# Architecture Design Reference

Use this vocabulary consistently in findings, diagrams, questions, and designs.

## Vocabulary

- **Module**: anything with an interface and an implementation, from a function to a package or tier-spanning slice. Do not substitute *component*, *service*, or *unit*.
- **Interface**: everything a caller must know to use a module correctly, including types, invariants, ordering, errors, configuration, and performance. Do not substitute *API* or *signature*.
- **Implementation**: behavior hidden inside a module. Use *adapter* instead when discussing a concrete role at a seam.
- **Depth**: leverage at the interface. A deep module hides substantial behavior behind a small interface; a shallow module exposes nearly as much complexity as it contains.
- **Seam**: a place where behavior can change without editing that location; the location of a module's interface. Do not substitute *boundary*.
- **Adapter**: a concrete implementation that satisfies an interface at a seam.
- **Leverage**: capability callers gain per unit of interface they must learn.
- **Locality**: concentration of change, bugs, knowledge, and verification in one place.

Relationships: a module presents one interface; depth is judged against that interface; the interface lives at a seam; adapters satisfy it; depth produces leverage for callers and locality for maintainers.

## Design principles

- Depth belongs to the interface, not to implementation size. A deep module may contain private internal seams without exposing them.
- Apply the deletion test. A useful module's removal redistributes complexity across callers; a pass-through module's removal eliminates complexity.
- Treat the interface as the test surface. Tests that must reach past it indicate a poor module shape.
- One adapter is a hypothetical seam; two justified adapters make it real.
- Accept dependencies instead of constructing them internally.
- Prefer returned results and observable outcomes over hidden side effects.
- Reduce methods, parameters, invariants, ordering constraints, and caller knowledge.

## Dependency categories

Classify dependencies before recommending a deepening:

1. **In-process**: pure computation or in-memory state. Merge shallow modules and test the new interface directly; no adapter is needed.
2. **Local-substitutable**: dependencies with realistic local stand-ins, such as PGLite or an in-memory filesystem. Keep the seam internal and test the deep module with the stand-in.
3. **Remote but owned**: internal services across a network. Define a port at the seam, use a production transport adapter and an in-memory test adapter, and keep domain behavior in the deep module.
4. **True external**: third-party systems. Inject a port and use a controlled mock adapter in tests.

Replace old shallow-module tests with behavior tests at the deepened interface. Assert observable outcomes, not internal state. A test should survive internal refactoring.

## Design It Twice

Use this process only after the user selects a candidate and asks to compare interface designs.

1. Explain the constraints, dependency categories, seam, and behavior that must be hidden. Include a small illustrative sketch that grounds the problem without proposing the answer.
2. If subagents are available, dispatch at least three independent designs in parallel. Give each the relevant files and domain vocabulary, plus a distinct objective:
   - minimize the interface to one to three entry points;
   - maximize flexibility and extension;
   - optimize the most common caller;
   - when relevant, optimize ports and adapters across a remote seam.
3. Require each design to state:
   - methods, parameters, invariants, ordering, and error modes;
   - a caller example;
   - what the implementation hides;
   - dependency and adapter strategy;
   - where leverage is strong or thin.
4. Present the designs sequentially. Compare depth, locality, seam placement, and dependency strategy. Recommend the strongest design or a justified hybrid.
