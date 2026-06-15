---
name: spec-to-plan
description: Convert a specification file into a step-by-step implementation plan for agents. Use when the user asks to create a plan, implementation plan, execution plan, or agent-ready plan from a spec path, with an optional custom output path.
---

# Spec To Plan

## Operating Principle

Act as a supervisor: delegate spec understanding, plan writing, and plan validation to subagents, and do not let material ambiguity pass into the plan.

The main thread routes information, asks the user questions, and verifies outputs. It does not perform substantive spec analysis, draft the implementation plan, or validate the plan itself.

## Inputs

- Require a path to the source spec. If no spec path is provided, stop the run and tell the user that a spec path is required.
- If the spec path cannot be read, stop and report the unreadable path.
- Resolve the output path before delegation:
  - default to `plan.md` in the same directory as the spec,
  - if the user provides an alternative directory, write `plan.md` inside it,
  - if the user provides an alternative file path, write to that file.

## Workflow

1. Spawn an understanding subagent. Give it the spec path and instruct it to read the spec, research local project context if needed, and return:
   - its concise understanding of the required outcome,
   - relevant constraints, dependencies, risks, and implied implementation areas,
   - all ambiguities, missing requirements, conflicts, or low-confidence assumptions,
   - clarifying questions where each question includes one recommended action and `2-3` other viable options.
2. Ask the user every clarification question returned by the understanding subagent. Keep the recommended action visible for each question.
3. Pass the user's answers back to the same understanding subagent. Have it re-evaluate its understanding and either:
   - return more follow-up questions using the same recommended-action format, or
   - return a final understanding packet once every material requirement is at `100%` certainty.
4. Repeat the clarification loop until the understanding subagent returns a final understanding packet. Treat `100%` certainty as: every material requirement is explicitly stated in the spec, directly answered by the user, or accepted by the user through a recommended option.
5. Spawn a planning subagent. Give it the spec path, output path, final understanding packet, and accepted clarifications. Instruct it to write the plan directly to the output path.
6. Spawn a validation subagent. Give it the spec path, output path, final understanding packet, and accepted clarifications, and instruct it to read the artifacts, research local project context if needed, and validate that the plan fully adheres to the spec.
7. Resolve validation findings:
   - If the validator finds a gap, ambiguity, conflict, or low-confidence area, it must first check whether the understanding packet or accepted clarifications already answer it.
   - If existing information answers it, send the finding and answer back to the planning subagent for revision.
   - If existing information does not answer it, ask the user for clarification with one recommended action and `2-3` other viable options, then send the answer back through the understanding and planning subagents.
8. Repeat plan revision and validation until the validator reports no unresolved gaps, ambiguities, conflicts, or low-confidence areas.

## Plan Requirements

The planning subagent must create an agent-ready `plan.md` that includes:

- source spec path and output path,
- accepted clarifications and assumptions,
- ordered implementation steps with enough detail for another agent to execute,
- files, modules, systems, or docs likely to be touched when known,
- dependencies, sequencing constraints, and risk areas,
- validation steps, tests, or review checks required before considering the spec implemented.

Do not include unresolved questions in the final plan. If a question remains, continue the clarification loop instead of writing or finalizing the plan.

## Final Response

After validation passes, report the plan path, the subagent passes completed, and that no unresolved spec-to-plan questions remain.
