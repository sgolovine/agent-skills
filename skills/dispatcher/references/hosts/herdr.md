# Herdr host

Workers run in their own Herdr workspaces. Agents are addressed by name or pane ID. Responses are JSON; read IDs from them. CLI errors are JSON on stderr.

## Quick reference

| Need | Command |
| --- | --- |
| Environment gate | `test "${HERDR_ENV:-}" = 1 && command -v herdr` |
| Own location | `printf '%s\n' "$HERDR_WORKSPACE_ID" "$HERDR_TAB_ID" "$HERDR_PANE_ID"` |
| Live agents | `herdr agent list` (fields: `name`, `agent`, `agent_status`, `pane_id`, `workspace_id`, `cwd`) |
| Workspaces | `herdr workspace list` (fields: `workspace_id`, `label`, `agent_status`) |
| Name yourself | `herdr agent rename "$HERDR_PANE_ID" supervisor` |
| Rename a workspace | `herdr workspace rename <workspace_id> <label words...>` (own: `"$HERDR_WORKSPACE_ID"`) |
| Rename a tab | `herdr tab rename <tab_id> <label words...>` |
| New task workspace | `herdr workspace create --cwd <dir> --label <task> --no-focus` → `.result.workspace.workspace_id`, `.result.root_pane.pane_id` |
| Start a Claude worker | `herdr agent start <name> --kind claude --pane <pane_id> -- --model <model>` |
| Start a Codex worker | `herdr agent start <name> --kind codex --pane <pane_id> -- --model <model> -c model_reasoning_effort=<effort>` |
| Brief a worker | `herdr agent prompt <name> "<brief>"` (no `--wait`) |
| Check a worker | `herdr agent get <name>` → `.result.agent.agent_status` ∈ `idle`, `working`, `blocked`, `done`, `unknown` |
| Read a worker | `herdr agent read <name> --source recent-unwrapped --lines 120` |
| Drive worker UI | `herdr agent send-keys <name> esc` / `enter` / `ctrl+c` |
| Short bounded wait | `herdr agent wait <name> --until blocked --timeout 15000` |
| Alert the user | `herdr notification show "<title>" --body "<text>" --sound done` |
| Worker sub-agent tab | `herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label <name> --no-focus` → `.result.root_pane.pane_id` |
| Close own workspace | `herdr workspace close <workspace_id>` (only workspaces you created, only on user request) |

`agent start` needs an existing shell pane at its prompt; `workspace create` and `tab create` provide one. Its startup timeout is 30 s by default (`--timeout <ms>`, max 300000). Everything after `--` goes to the agent CLI unchanged. Agent names are unique among live agents.

## Mapping to the dispatcher

- **Location:** workspace ID, tab ID, pane ID. **Your name** is your agent name; **your label** is your workspace label.
- **Other supervisors:** agent names starting with `supervisor` and workspace labels starting with `Supervisor Chat`. Relabel another supervisor's workspace with `workspace rename`.
- **Dispatch:** `workspace create` → `agent start <worker-name>` in the root pane → `agent prompt <worker-name> "<brief>"` without `--wait`. `workspace rename` if the label came back mangled.
- **Confirm execution:** one `agent get`, then one `agent read` if not `working`. On `agent_prompt_stalled`, inspect before resending.
- **Status and messaging:** `agent get`, `agent read`, `agent prompt <target>`. Never use `agent prompt --wait` or long `agent wait` timeouts on workers.
- **Alert:** `herdr notification show` on every verified report.
- **Truncated output:** alternate-screen agents can truncate `agent read`; use the temporary-file request in `SKILL.md`.

## Brief blocks

Fill `<host reporting block>` in the worker brief with:

```
Report by prompting the supervisor's agent; never wait for the supervisor to poll you.
  herdr agent prompt <supervisor-name> "[<worker-name>] BLOCKED: <blocker, what you tried, what you need>"
  herdr agent prompt <supervisor-name> "[<worker-name>] QUESTION: <decision needed, options, your recommendation>"
  herdr agent prompt <supervisor-name> "[<worker-name>] DONE: <result, evidence paths, changed files, checks run, branch/commits/PR, limitations>"
```

Fill `<host delegation block>` with (use `--kind codex` and Codex flags for Codex sub-agents):

```
Delegate through tabs in your own workspace, never new workspaces or splits of your pane:
  herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label <role> --no-focus   # read .result.root_pane.pane_id
  herdr agent start <worker-name>-<role> --kind claude --pane <pane_id> -- --model <model>
  herdr agent prompt <worker-name>-<role> "<self-contained brief including this execution contract>" --wait --timeout <ms>
  herdr agent read <worker-name>-<role> --source recent-unwrapped --lines 120
Sub-agent names must be unique among live agents. Label each tab for its role (research, implement, review); use `herdr tab rename <tab_id> <label>` if a tab's purpose changes. You may wait on your sub-agents. Sub-agents report to you, not to the supervisor. Do not close tabs or panes you did not create.
```

Location line for the brief: `Herdr workspace <workspace_id>, pane <pane_id>`; supervisor address: agent name and pane ID.
