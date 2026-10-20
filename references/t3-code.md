# T3 Code

Shared T3 Code host reference for skills that run threads, schedules, or subagents in T3 Code. Threads are addressed by `threadId`. Each top-level thread is bound to one workspace (the project root or a worktree) when it launches.

## Gate and tool names

- Gate: `orchestrator_capabilities {}` must answer. If the T3 tools are not listed, call it once directly before concluding T3 is absent; MCP servers can attach lazily. If T3 is absent, report `<skill> requires T3 Code.` and stop.
- Claude Code: `mcp__t3-code__<tool>` (load deferred schemas with ToolSearch `select:` first).
- Codex: `mcp__t3_code__<tool>`; in code mode `tools.mcp__t3_code__<tool>({...})`.
- ACP fallback, when the tools are missing but `T3_ACP_MCP_NODE` is set:
  `ELECTRON_RUN_AS_NODE=1 "$T3_ACP_MCP_NODE" ${T3_ACP_MCP_ENTRYPOINT:+"$T3_ACP_MCP_ENTRYPOINT"} acp-mcp-call <tool> '<json args>'`

## Quick reference

| Need | Call |
| --- | --- |
| Own location | `t3_thread_configuration {}` → `threadId`, `modelSelection`, `runtimeMode`; `t3_thread_list {limit:1}` → `projectId` |
| Model catalog | `orchestrator_capabilities {}` → `providers[]` with `providerInstanceId`, `canRunChildTask`, `constraints`, `models[].id`, `models[].options` |
| Rename a thread | `t3_thread_update {action:"rename", title}` for yourself; add `threadId` for another thread |
| Find threads | `t3_thread_list {titleContains, settled, limit:100, cursor}` (fields: `threadId`, `title`, `status`, `providerInstanceId`, `model`, `parentThreadId`, `relationshipToParent`, `linkedPullRequest`). Delegated tasks appear too, with their `title` and `relationshipToParent:"subagent"`. `settled:false` and `settled:true` are separate lists; follow `cursor` until it is empty |
| Thread status | `status` ∈ `preparing`, `queued`, `starting`, `running`, `waiting`, `completed`, `interrupted`, `failed`, `cancelled`, `rolled_back`, `idle` |
| Read a thread | `t3_thread_read {threadId, view:"messages"}` for final answers and reports; `view:"activity", limit:30` for recent work |
| Launch a thread | `t3_thread_launch {title, workspaceStrategy, modelSelection, interactionMode:"default", message}` → `threadId` |
| Change a thread's model | `t3_thread_configure {threadId, modelSelection}`, within the same provider only (see Models) |
| Message a thread | `t3_thread_send {threadId, mode:"queue", clientRequestId, message}` |
| Pending questions | `t3_pending_request_list {threadId}` → `t3_pending_request_respond` |
| Flag for the user | `t3_thread_organize {action:"mark_unread", threadId}` |
| Archive | `t3_thread_organize {action:"archive", threadId}` |
| Link a PR | `link_pull_request {url}` (links to the calling thread unless `threadId` is given) |
| Worktree inventory | `t3_worktree_list {query}` → refs and checkout paths |
| Schedules | `schedule_task`, `list_scheduled_tasks` (id, prompt, schedule, enabled, bound thread, next run), `update_scheduled_task {scheduledTaskId, ...}`, `delete_scheduled_task {scheduledTaskId}` |
| Delegate | `delegate_task {title, role, mode:"async", clientRequestId, target, task}` → `taskId`, `childThreadId`; `task_status {taskId}` → `status`, `workState` (`working`, `waiting_for_children`, `result_available`), `summary`; `task_cancel {taskId}` |

`schedule_task` binds runs to the calling thread, and each run uses that thread's model. A thread can schedule only itself.

## Delegated tasks

- `delegate_task` starts a child on any provider and model, with only the task prompt as context. It is T3's recommended way to combine harnesses.
- `clientRequestId` makes the launch idempotent; reuse it only for retries of the same launch. A finished child wakes the parent with its final answer as `summary`, batched with others. End the turn instead of polling.
- A child runs in the parent's workspace; there is no workspace option. Give it an explicit directory to work in. Delegated children can use the browser preview tools.
- Only the parent can call `task_status` or `task_cancel`. Any thread can read a child with `t3_thread_list` and `t3_thread_read {threadId:<childThreadId>, view:"messages"}`.
- Subagent threads are read-only: never `t3_thread_send` to a `childThreadId`. A new assignment or round is a new `delegate_task`.
- Stopping a thread in T3 also stops its delegated tasks and pull request watches.

## Thread lifecycle

- With **Continue threads after restarts** on, an `interrupted` thread can continue on its own. A thread stopped by a usage limit shows as Limited in the app and can resume at reset. Before relaunching an interrupted thread, read its last activity (`view:"activity", limit:5`) and wait if it hit a usage limit or is resuming.
- Queued messages survive restarts, but after a restart the queue waits for a human to resume it. Design reports so that a missed message is recovered from thread state.
- Agents cannot approve permission requests. Only questions can be answered with `t3_pending_request_respond`.

## Models

Look up IDs with `orchestrator_capabilities {}` each session; never trust example IDs. A provider is usable only if `canRunChildTask` is true and `constraints` is empty. Claude is `claudeAgent`; Codex is `codex`. A model the user names wins. Never switch provider families silently.

Changing model or options within one provider keeps the session. Switching provider mid-thread is lossy: the new provider gets a budgeted selection of messages, without reasoning, tool results, or attachments. To move a thread to another provider, launch a fresh thread instead.

`modelSelection`: `{"instanceId":"<providerInstanceId>","model":"<model id>","options":[{"id":"<option id>","value":"<value>"}]}`. Omit `options` for model defaults. `delegate_task.target` takes the same fields as `providerInstanceId`, `model`, `options`.

## Launching threads

- `t3_thread_launch` has no retry key. Keep the returned `threadId`. If a call errors or its response is lost, check `t3_thread_list {titleContains:"<title>"}` before retrying.
- `interactionMode:"default"`; plan mode stops at a plan.
- Omit `runtimeMode` so the child inherits yours. `t3_thread_send` refuses a target whose permissions are broader than the caller's.
- Omit `projectId` to use your own project.
- `workspaceStrategy`: `{"type":"root"}` for the project checkout; `{"type":"worktree","baseRef":"<ref>","branch":"<new branch>","startFromOrigin":<bool>}` for a new worktree. Omitting it means root.
- Never tell a thread to `git worktree add` or `cd` elsewhere. That does not move its T3 binding. Say the thread is already an isolated worktree and must use it.
- The `message` is delivered after workspace preparation. Confirm the launch with one status check and, if it is not working, one activity read. Never create a duplicate.
