---
name: block-dev
description: Grill a repository change request with a human. Then create a specification, divide it into reviewable blocks, implement each block, and open stacked draft GitHub pull requests. Use when a user wants semi-autonomous development through a supervisor and specialized worker agents.
---

# Block Development

## Operating Principle

Use the human gate to remove material uncertainty. Then, move each block through implementation, review, repair, and publication without more routine questions.

## Required Support

1. Require a Git repository and real subagent support.
2. Stop if the harness cannot spawn subagents.
3. Use the current agent as the **Supervisor**.
4. Keep all source changes serial in the linked worktree.
5. Do not perform a worker role in the Supervisor.
6. Do not let an ordinary worker spawn another worker.
7. Read [agent-roles.md](references/agent-roles.md) before the first worker starts.

Use `$technical-english` in rules-only mode for every generated prose artifact. Do not claim a full-dictionary result.

## Prepare the Run

1. Inspect the repository status, remotes, instructions, code, tests, and documentation.
2. Preserve all unrelated changes in the control checkout.
3. Create `.block-dev/<request-slug>/` in the control checkout.
4. Keep every run artifact uncommitted.
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

Do not stage a file under `.block-dev/`. Repository documents are input unless a finalized block explicitly changes them.

## Complete the Human Gate

1. Spawn the Grill Worker from [grill.md](references/grill.md).
2. Give the worker the request, repository root, and run artifact path.
3. Relay each question batch to the user.
4. Do not answer a question for the user.
5. Return each answer to the same worker when resume support exists.
6. Otherwise, start a replacement Grill Worker from the durable grill documents.
7. Continue until the design frontier is empty.
8. Require the Grill Worker to return the candidate shared understanding.
9. Ask the user to confirm or correct the candidate.
10. Return the user response to the same or replacement Grill Worker.
11. Require the Grill Worker to record the confirmation or apply the corrections.
12. Repeat the interview when a correction reopens the design frontier.
13. Start autonomous work only after the Grill Worker reports that the grill phase is complete.

The Grill Worker can report completion only after it records explicit user confirmation. Keep the user decision in the Supervisor interaction.

Include the stack base in the confirmed understanding. Include important branch conventions and publication constraints when they are not clear.

## Create the Plan Artifacts

After confirmation, create one isolated linked worktree for the complete stack:

1. Fetch the applicable remote refs.
2. Resolve the confirmed base to an immutable commit.
3. Create a detached linked worktree at a unique sibling path.
4. Record the worktree, base branch, base ref, and base commit in `run-state.md`.
5. Use the linked worktree for all repository changes.

Then, create and validate the plan artifacts:

1. Spawn the Specification Writer.
2. Require the writer to create `.block-dev/<request-slug>/SPEC.md`.
3. Spawn the Block Planner after the specification is complete.
4. Require sequential files under `.block-dev/<request-slug>/blocks/`.
5. Use `NN-short-description.md` names with hyphens and two-digit numbers.
6. Spawn the Coverage Auditor after all blocks exist.
7. Send each coverage finding to one Block Reviser.
8. Re-run the Coverage Auditor after each revision round.
9. Stop after three failed repair rounds.
10. Report the remaining gaps and conflicts when the gate fails.

The Coverage Auditor must confirm complete specification coverage. The auditor must also confirm that the blocks have no gaps or conflicts.

## Implement the Stack

Process blocks in file-name order. Complete one block before the next block starts.

For each block:

1. Set the first parent to the confirmed base branch.
2. Set each later parent to the previous block branch.
3. Create the block branch from the recorded parent commit.
4. Follow the repository branch convention when one exists.
5. Otherwise, use `block-dev/<request-slug>/<block-file-stem>`.
6. Spawn one Development Worker for the block.
7. Require applicable tests and repository checks.
8. Run the reviews in [code-review.md](references/code-review.md).
9. Spawn the Standards Reviewer and Block-Plan Reviewer in parallel.
10. Use the parent ref as the fixed point.
11. Store both reports under `reviews/<block-number>/round-<number>/`.
12. Send all concrete findings to one Review Resolver.
13. Re-run both review axes after each repair round.
14. Stop after three failed repair rounds.
15. Report unresolved findings when the review gate fails.
16. Spawn the PR Publisher only after both review axes pass.
17. Follow [open-github-pull-request.md](references/open-github-pull-request.md).
18. Stop if publication fails.
19. Start the next branch from the published branch commit.

Do not merge a pull request. Do not change its draft state, reviewers, or repository settings without explicit authority.

## Handle Blockers

After the human gate, do not ask routine implementation questions. Use the specification and finalized blocks as the authority.

Stop when a worker finds an unapproved product decision or an unrecoverable external blocker. Preserve the worktree, branches, commits, and run artifacts. Report exact evidence for the blocker.

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
