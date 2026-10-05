# Models

## Selection order

1. The model the user named for this assignment.
2. A conversation default the user set ("use Codex for everything", "default to Sonnet"). It applies to later launches and leaves running workers alone unless the user says otherwise.
3. The defaults below.

If the chosen model cannot run and the user has not authorized a fallback, report the blocker. Never switch provider families silently. Do not use the `default`, `best`, or `opusplan` aliases.

## Defaults

| Work | Family | Default |
| --- | --- | --- |
| General work | Claude | Newest accessible Opus |
| Specialist work the user asks for | Claude | Fable |
| User asks for Codex, GPT, or OpenAI | Codex | Newest flagship GPT model in the Codex catalog |

Reasoning effort: keep the model's default unless the user asks otherwise or the task is clearly heavy (large refactors or deep debugging call for `high`) or trivial (`low`). State the effort in the dispatch report when it is not the default.

## Finding current models

Model IDs change. Look them up from the live source rather than trusting the examples here.

- **T3 Code:** `orchestrator_capabilities {}`. Use a provider only if `canRunChildTask` is true and `constraints` is empty. Claude is `providerInstanceId: "claudeAgent"` and Codex is `"codex"`. Each model lists `options`: `effort`, `contextWindow`, and `fastMode` for Claude, and `reasoningEffort` and `serviceTier` for Codex, along with the allowed values and defaults.
- **Herdr + Claude:** start from the `opus` or `fable` alias, and check settings for a pinned override. Use an exact ID such as `claude-opus-5-5` only when you can confirm a newer accessible model.
- **Herdr + Codex:** the `model` and `model_reasoning_effort` keys in `~/.codex/config.toml` give the user's default. Otherwise use the newest flagship ID you can confirm, for example from a T3 catalog on the same machine.

Example IDs as of October 2026: Claude `claude-opus-5-5`, `claude-fable-5-1`, `claude-sonnet-5-5`. Codex `gpt-6.1-sol` (flagship), `gpt-6-sol`, `gpt-6-astra`, `gpt-6-luna`. When choosing within a generation, follow the catalog's ordering and labels rather than guessing from names.

## Passing the model

| Host | Claude | Codex |
| --- | --- | --- |
| Herdr | `herdr agent start <name> --kind claude --pane <id> -- --model <model>` | `herdr agent start <name> --kind codex --pane <id> -- --model <model> -c model_reasoning_effort=<effort>` |
| T3 Code | `modelSelection: {"instanceId":"claudeAgent","model":"claude-opus-5-5","options":[{"id":"effort","value":"high"}]}` | `modelSelection: {"instanceId":"codex","model":"gpt-6.1-sol","options":[{"id":"reasoningEffort","value":"high"}]}` |

Leave out `options` to get the model's defaults. The same `providerInstanceId`/`model`/`options` shape goes in `delegate_task.target` when a worker delegates in T3.

## Codex worker notes

- Codex loads skills from its own skill directories (for example `~/.codex/skills`). Name the skills in the brief and have the worker report any it cannot load.
- In T3, Codex reaches T3 tools as `mcp__t3_code__<tool>`, or as `tools.mcp__t3_code__<tool>(...)` in code mode. The T3 brief blocks include both forms and the ACP fallback.
- In Herdr, Codex sub-agents start in tabs with `--kind codex`.
