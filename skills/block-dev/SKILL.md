---
name: block-dev
description: Grill a repository change request with a human. Then create a specification, divide it into reviewable blocks, implement each block, and open stacked draft GitHub pull requests. Use when a user wants semi-autonomous development through a supervisor and specialized worker agents.
---

# Block Development

## Operating Principle

Use the human gate to remove material uncertainty. Then move each block through planning, implementation, review, repair, and publication.

## Required Support

1. If the current directory is not a Git repository, stop.
2. If the harness cannot start subagents, stop.
3. Use the current agent as the **Supervisor**.
4. Keep all source changes serial in one linked worktree.
5. Before each phase, load only the applicable worker contracts from [agent-roles.md](references/agent-roles.md).

Use `$technical-english` in rules-only mode for every generated prose artifact. Do not claim a full-dictionary result.

## Prepare the Run

1. Inspect the repository status, remotes, instructions, code, tests, and documentation.
2. Preserve unrelated changes in the control checkout.
3. Create `.block-dev/<request-slug>/` in the control checkout.
4. Keep each run artifact uncommitted.
5. Record run facts in `.block-dev/<request-slug>/run-state.md`.

Use this artifact layout:

```text
.block-dev/<request-slug>/
├── run-state.md
├── grill/
├── SPEC.md
├── blocks/
│   ├── 01-short-description.md
│   └── 02-short-description.md
├── coverage/
│   └── round-01.md
└── reviews/
    └── <block-number>/
        └── round-01/
            ├── standards.md
            └── block-plan.md
```

Repository documents are input unless a finalized block explicitly changes them.

## Complete the Human Gate

1. Start the Grill Worker.
2. Relay each question batch to the user.
3. Return each answer to the same worker when resume support exists.
4. Otherwise, start a replacement worker from the durable grill documents.
5. Continue until the design frontier is empty.
6. Ask the user to confirm or correct the candidate shared understanding.
7. Return the response to the Grill Worker.
8. Repeat the interview if a correction reopens the design frontier.
9. Continue only after the worker records explicit user confirmation.

The confirmed understanding must include the stack base. It must include applicable branch conventions and publication constraints.

## Create the Plan Artifacts

After confirmation, create one linked worktree for the complete stack:

1. Fetch the applicable remote refs.
2. Resolve the confirmed base to an immutable commit.
3. Create a detached linked worktree at a unique sibling path.
4. Record the worktree, base branch, base ref, and base commit in `run-state.md`.
5. Use the linked worktree for all repository changes.

Then run these workers in order:

1. Run the Specification Writer to create `SPEC.md`.
2. Run the Block Planner to create sequential block files.
3. Run the Coverage Auditor after all block files exist.
4. If the review fails, run one Block Reviser.
5. Run the Coverage Auditor again after each repair round.

Run a maximum of three repair rounds. If the final coverage review does not pass, stop. Report the remaining gaps and conflicts.

The coverage gate passes only with complete specification coverage and no block conflicts.

## Implement the Stack

Process block files in file-name order. Complete one block before the next block starts.

For each block:

1. For the first block, record the confirmed base branch and base commit.
2. For each later block, record the previous block branch and commit.
3. Create the block branch from its recorded parent commit.
4. Follow the repository branch convention when one exists.
5. Otherwise, use `block-dev/<request-slug>/<block-file-stem>`.
6. Run one Development Worker.
7. Run the Standards Reviewer and Block-Plan Reviewer in parallel.
8. Use the recorded parent commit as the fixed review point.
9. Store both reports under `reviews/<block-number>/round-<number>/`.
10. If either review fails, run one Review Resolver.
11. Run both reviews again after each repair round.
12. After both reviews pass, run the PR Publisher.
13. Use [open-github-pull-request.md](references/open-github-pull-request.md) as the publication authority.
14. Start the next branch from the published branch commit.

Run a maximum of three repair rounds. If the final implementation review does not pass, stop. Report the unresolved findings.

If publication fails, stop.

## Handle Blockers

After the human gate, do not ask routine implementation questions. Use the specification and finalized blocks as the authority.

Stop when a worker finds an unapproved product decision or an unrecoverable external blocker. Preserve the current run state. Report exact evidence for the blocker.

## Report the Result

Report these results:

- The run artifact path
- The specification path
- The block paths
- The linked worktree path
- The branch stack
- The pull request URLs
- The validation commands and results
- The skipped checks
- The unresolved risks.
