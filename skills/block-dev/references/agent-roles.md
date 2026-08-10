# Worker Role Contracts

The Supervisor owns orchestration, decisions, branch changes, and quality gates. Each worker completes one assigned role and then returns control.

## Common Contract

Give each worker these items:

- The role name
- The repository root
- The linked worktree path, when applicable
- The run artifact path
- The source artifact paths
- The permitted write scope
- The required checks
- The required output path.

Apply these rules to every worker:

1. Read the applicable repository instructions.
2. Inspect source files directly.
3. Do not start another worker.
4. Do not expand the approved scope.
5. Stop for an unapproved product decision.
6. Stop for an unapproved architecture decision.
7. Before you write prose, read `$technical-english`.
8. Use `$technical-english` in rules-only mode.
9. Report changed files, commands, failures, and residual risks.

## Load the Applicable Contract

Load the common contract and only the role group for the current phase:

| Phase | Contract |
| --- | --- |
| Human gate | [roles/grill.md](roles/grill.md) |
| Specification and block planning | [roles/planning.md](roles/planning.md) |
| Implementation and review | [roles/implementation.md](roles/implementation.md) |
| Publication | [roles/publication.md](roles/publication.md) |

Do not load a later role group before its phase starts.
