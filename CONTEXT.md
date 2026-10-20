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
The thread that drives Factory PRs through review, resolution, and merge. The Factory's schedule and its children's reports wake it up.
_Avoid_: Monitor, merge loop, PR review loop

**Pass**:
One non-blocking run of the Factory loop over every open Factory PR.
_Avoid_: Tick, cycle

**Factory PR**:
An open pull request that carries the `factory` label and so is opted in to review and automatic merge.
_Avoid_: Managed PR

**Round**:
One review of a Factory PR, plus the single Resolve thread that follows it when Open items remain.

**Dev thread**:
A thread that the Dispatch thread starts for one piece of dispatched work. It opens a Factory PR, then takes any corrections the Dispatch thread sends for that PR.
_Avoid_: Worker, dev worker

**Review thread**:
A thread that the Factory loop starts to review one Factory PR at one head commit.

**Resolve thread**:
A thread that the Factory loop starts when Open items remain after a Round's review. It fixes or answers every Open item for that Round.
_Avoid_: Fixer, resolver

**Open item**:
Anything that blocks a merge and that a Resolve thread can fix: an unresolved review thread, an unanchored review finding, a merge conflict, a branch behind its base, or a failing check.

**PR evidence**:
The PR description and the screenshots that show the changed behavior.

**Factory comment**:
A review comment written by a Review thread. The Factory may reject its own comments with evidence, but never a human's.
_Avoid_: Bot comment
