# Pull Request Review Checklist

Use this checklist selectively, applying only the search lenses relevant to the changed behavior.

## Finding Admission Test

Keep a candidate only when all are true:

1. **Introduced:** The PR creates or materially worsens it.
2. **Specific:** A concrete input, state, environment, or sequence triggers it.
3. **Demonstrable:** Code flow, a focused check, documentation, or a test supports the claim.
4. **Material:** It affects required behavior, users, data, security, operations, performance, or compatibility.
5. **Actionable:** The author can address it within the PR or deliberately defer it.
6. **Locatable:** The finding can cite the changed line most responsible for the behavior.

Reject pre-existing defects, broad hypothetical concerns without a plausible trigger, style-only preferences, and duplicate comments. A missing test is normally a finding only when it leaves important changed behavior unverified or violates an explicit project requirement.

## Intent and Coverage

- Does the implementation satisfy the stated requirement across success, failure, and boundary cases?
- Are all call sites, variants, feature flags, platforms, and configuration paths covered?
- Does the PR contain unrelated changes that obscure risk or accidentally alter behavior?
- Do documentation and tests describe the behavior the code actually implements?

## Correctness and State

- Boundary values, empty inputs, nullability, overflow, rounding, encoding, locale, and time-zone behavior
- State transitions, stale state, partial updates, ordering, idempotency, retries, and duplicate delivery
- Concurrency, races, locking, atomicity, transaction boundaries, and cleanup after failure
- Error propagation, fallback behavior, cancellation, timeouts, and resource release
- Incorrect assumptions about mutability, ownership, lifetimes, caching, or initialization order

## Contracts and Compatibility

- API, CLI, event, file-format, and serialization compatibility
- Database migrations, backfills, defaults, constraints, rollback safety, and mixed-version deployments
- Renames or removals consumed by callers, automation, integrations, or persisted data
- Configuration precedence, absent values, environment differences, and safe defaults
- Dependency and lockfile changes that alter runtime or build behavior

## Security and Privacy

- Authentication and authorization at every access boundary
- Injection, unsafe parsing, path traversal, SSRF, open redirects, XSS, CSRF, and command construction
- Sensitive data in logs, errors, telemetry, URLs, caches, client payloads, or generated artifacts
- Secret handling, token scope, cryptographic misuse, insecure randomness, and trust-boundary changes
- Denial-of-service paths such as unbounded input, recursion, allocation, queries, fan-out, or retries
- Dependency provenance and newly exposed network, filesystem, process, or deserialization capability

## Reliability, Performance, and Operations

- Algorithmic regressions on realistic sizes, repeated I/O, N+1 queries, unnecessary serialization, or hot-path allocations
- Leaks of files, sockets, processes, transactions, subscriptions, goroutines, threads, or browser handles
- Retry storms, missing backoff, weak timeout behavior, and failure amplification
- Startup, shutdown, deployment, rollback, and backward/forward compatibility
- Useful error messages, metrics, logs, and alerts for new failure modes without exposing sensitive data

## User-Facing Behavior

- Loading, empty, error, offline, permission-denied, and partial-success states
- Keyboard access, focus, labels, semantic structure, contrast, and screen-reader behavior when UI is changed
- Responsive layout, localization, formatting, and destructive-action safeguards
- Client/server validation consistency and stale-response handling

## Tests and Evidence

- Tests exercise the changed branch and would fail against the buggy behavior, not merely execute the line.
- Failure paths and boundaries receive coverage proportional to their risk.
- Mocks preserve the relevant production semantics rather than hiding integration failures.
- Snapshots and generated outputs were intentionally updated and reviewed.
- CI failures, skipped jobs, flaky checks, and platform gaps are distinguished from verified regressions.
