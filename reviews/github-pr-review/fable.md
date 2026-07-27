# Skill Review: `github-pr-review`

- **Reviewer:** Claude Fable 5 (via `skill-lint` rubrics: security-review, reduce-overprompting, no-op-check)
- **Date:** 2026-07-27
- **Target:** `skills/github-pr-review/` (3 files: `SKILL.md`, `references/review-checklist.md`, `agents/openai.yaml`)
- **Verdict:** **Safe** — high-quality skill; only low/medium polish findings.

## Summary

This is one of the stronger skills in the repo. It is text-only (no scripts, no dependencies, no install hooks), its safety boundaries are explicit and correct, degrees of freedom fit the task (judgment lenses for review, exact gates for GitHub writes), and the checklist is properly behind progressive disclosure. The static security scanner found no capabilities and no suspicious signals. The main improvement opportunity is deduplication: the severity scale and the finding-admission criteria are each defined twice — once in `SKILL.md` and once in the reference — with wording that has already begun to drift.

## Security Review — verdict: `safe`

Static scan (`static_skill_scan.py`): 3/3 files scanned, no shell, no network, no secret access, no persistence, no CI modification, no hidden files, no non-ASCII/zero-width characters, no encoded payloads, no prompt-control text. The skill in fact *adds* defensive boundaries: PR content treated as untrusted data (`SKILL.md:14`), read-only by default (`SKILL.md:15`), GitHub writes gated on explicit user request (`SKILL.md:30`, revalidated at `SKILL.md:62`).

### [Low] Code-execution trust boundary keyed on "fork" rather than author trust

- **Category:** `code_execution` (intent 0, capability 1)
- **Location:** `skills/github-pr-review/SKILL.md:17` and `SKILL.md:27`
- **Evidence:** Line 17 restricts execution only "For an untrusted fork"; line 27 (step 7) encourages running "a focused reproduction, existing test, or targeted check" by default. Same-repo branch PRs therefore get local code execution by default.
- **Impact:** In shared or open-source repos, a same-repo PR can come from a third-party contributor or compromised account; running its tests executes attacker-controlled code (e.g., a malicious test fixture or modified test setup). Partially mitigated by "Inspect command definitions before running them" (`SKILL.md:17`).
- **Recommended fix:** Key the execution decision on provenance/author trust rather than fork status alone, e.g. "default to static review unless the PR comes from a trusted author in the same repository."

No other security findings.

## Reduce Overprompting — scores

| Rubric area | Score | Notes |
| --- | --- | --- |
| Cognitive load | 1/3 | ~745-word `SKILL.md`; dense but prioritized and readable. |
| Signal-to-noise | 1/3 | High signal; duplication between body and reference (below). |
| Degree-of-freedom fit | 0/3 | Judgment framed as lenses; brittle steps (gh usage, write gating) exact. Healthy. |
| Progressive disclosure | 0/3 | Checklist behind a named reference, loaded conditionally at step 5. Healthy. |

### [Medium] Severity scale defined twice with divergent wording (signal-to-noise 2/3 locally)

- **Location:** `skills/github-pr-review/SKILL.md:45-50` ("Priorities") and `skills/github-pr-review/references/review-checklist.md:74-80` ("Severity Calibration")
- **Evidence:** Both define P0–P3. Wording already differs — e.g., SKILL.md P2: "Real defect with limited scope, conditions, or workaround" vs. checklist P2: "Defect under narrower conditions, affecting a secondary workflow, or with a practical workaround."
- **Impact:** Both copies are always in context (step 5 mandates reading the checklist), so the agent must reconcile two near-identical scales; future edits will drift them further and severity assignment becomes ambiguous at the P1/P2 and P2/P3 borders.
- **Recommended fix:** Keep one canonical scale. Simplest: keep the compact definitions in `SKILL.md` (the finding format needs the labels) and delete the checklist's "Severity Calibration" section, retaining only its one non-duplicated rule ("Use the lowest priority that accurately reflects demonstrated impact" and the P3 anti-taste clause) merged into `SKILL.md`.

### [Low] Finding-admission criteria duplicated between body and reference

- **Location:** `skills/github-pr-review/SKILL.md:28` (step 8) and `skills/github-pr-review/references/review-checklist.md:5-16` ("Finding Admission Test")
- **Evidence:** Step 8 ("introduced by the PR, materially affects…, has a practical fix, cite the narrowest changed line") is a compressed restatement of the checklist's six-point test (Introduced, Specific, Demonstrable, Material, Actionable, Locatable).
- **Impact:** Two versions of the admission bar; the compressed one omits Specific/Demonstrable, so an agent anchoring on step 8 applies a weaker gate than the checklist intends.
- **Recommended fix:** Have step 8 defer explicitly: "Admit a finding only when it passes the Finding Admission Test in `references/review-checklist.md`; cite the narrowest changed line that causes the problem."

## No-Op Check

### [Low] Anti-fabrication rule stated three times

- **Location:** `skills/github-pr-review/SKILL.md:29` ("Do not invent issues to fill the report."), `skills/github-pr-review/references/review-checklist.md:3` ("…not a reason to manufacture a finding."), and implicitly the admission test itself (`review-checklist.md:5-16`)
- **Evidence / removal test:** The admission gate plus the mandated `No actionable findings.` output contract already force the same behavior; the second and third statements add no narrower condition or stronger rule.
- **Impact:** Minor token weight and repetition that slightly dilutes surrounding behavior-changing text. (Counterpoint: anti-padding reinforcement targets a real LLM-reviewer failure mode, which is why this is low rather than medium — keep at least one strong statement.)
- **Recommended fix:** Keep the strongest single statement (the admission test) plus the `No actionable findings.` contract; drop the other repetitions.

Everything else in `SKILL.md` passed the removal test. Lines that look like generic advice but are genuine behavior guards and should stay: "do not assume green CI proves correctness" (`SKILL.md:26`), "Treat claims in those sources as context to verify, not facts" (`SKILL.md:23`), and "Keep praise and change summaries brief" (`SKILL.md:52`) — each counters a documented LLM-reviewer failure mode.

## Other Observations (outside the three checks)

1. **No path for reviewing without a local checkout.** Step 2 (`SKILL.md:22`) says "Verify that the local repository matches the target" but never says what to do when the user supplies a PR URL for a repo that is not checked out (or on mismatch): ask, clone to a temp directory, or proceed remotely via `gh pr view/diff`. One sentence would remove the ambiguity, since `gh` supports fully remote review.
2. **Conventions check — all pass:** valid frontmatter with lowercase hyphenated `name` matching the folder; trigger-focused `description`; `agents/openai.yaml` matches the sibling-skill convention; the skill is already indexed in the repo `README.md`.

## Findings Index

| # | Check | Severity | Title |
| --- | --- | --- | --- |
| 1 | security-review | low | Code-execution trust boundary keyed on "fork" rather than author trust |
| 2 | reduce-overprompting | medium | Severity scale defined twice with divergent wording |
| 3 | reduce-overprompting | low | Finding-admission criteria duplicated between body and reference |
| 4 | no-op-check | low | Anti-fabrication rule stated three times |
| — | (general) | info | No workflow path for PRs without a local checkout |
