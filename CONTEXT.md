# Agent Skills

Reusable agent skills. This glossary covers the Factory skill set, which turns dispatched development work into merged pull requests with little human involvement.

## Factory

**Factory**:
The running set of threads and the schedule that take development work for one repository from dispatch to a merged PR.
_Avoid_: Pipeline, software factory (as a term for the running instance)

**Factory skills**:
The `factory-*` skill set that runs a Factory. It is separate from the older skills it was based on.

**Dispatch thread**:
The thread where `factory-start` ran and where the user hands the Factory new work.
_Avoid_: Supervisor chat, control thread

**Factory loop**:
The thread that the Factory's schedule wakes up to drive Factory PRs through review, resolution, and merge.
_Avoid_: Monitor, merge loop, PR review loop

**Pass**:
One non-blocking run of the Factory loop over every open Factory PR.
_Avoid_: Tick, cycle

**Factory PR**:
An open pull request that carries the `factory` label and so is opted in to review and automatic merge.
_Avoid_: Managed PR

**Round**:
One review of a Factory PR, plus the single resolve thread that follows it when the review finds anything.

**Dev thread**:
A thread that the Dispatch thread starts for one piece of dispatched work. It ends when it opens a Factory PR.
_Avoid_: Worker, dev worker

**Review thread**:
A thread that the Factory loop starts to review one Factory PR at one head commit.

**Resolve thread**:
A thread that the Factory loop starts after a review that found anything. It fixes every open item on the PR for that Round.
_Avoid_: Fixer, resolver

**Open item**:
Anything that blocks a merge and that a Resolve thread can fix: an unresolved review thread, an unanchored review finding, a merge conflict, or a failing check.

**PR evidence**:
The PR description and the screenshots that show the changed behavior.

**Factory comment**:
A review comment written by a Review thread. The Factory may dismiss its own comments with evidence, but never a human's.
_Avoid_: Bot comment
