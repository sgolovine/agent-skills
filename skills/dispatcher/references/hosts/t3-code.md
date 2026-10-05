# T3 Code host

Workers run as ordinary top-level T3 threads, each bound to its own workspace (usually a fresh worktree). Threads are addressed by `threadId`. Invoking the dispatcher counts as the user asking for separate top-level threads, so `t3_thread_launch` is the right tool. `create_threads` is wrong here because it cannot choose a workspace, and so is `delegate_task`, which makes child tasks of the supervisor.

## Calling T3 tools

The tools come from the `t3-code` MCP server. Their names depend on the harness:

- Claude Code: `mcp__t3-code__<tool>` (load deferred schemas with ToolSearch `select:` first).
- Codex: `mcp__t3_code__<tool>`. In code mode: `tools.mcp__t3_code__<tool>({...})`.
- If the tools do not appear in an initial scan, make one direct call to `orchestrator_capabilities` before concluding T3 is absent. MCP servers can attach lazily.
- ACP fallback, for when the tools are missing but `T3_ACP_MCP_NODE` is set: `ELECTRON_RUN_AS_NODE=1 "$T3_ACP_MCP_NODE" ${T3_ACP_MCP_ENTRYPOINT:+"$T3_ACP_MCP_ENTRYPOINT"} acp-mcp-call <tool> '<json args>'`.

## Quick reference

| Need | Call |
| --- | --- |
| Environment gate | `orchestrator_capabilities {}` succeeds |
| Own location | `t3_thread_configuration {}` → `threadId`, `modelSelection`, `runtimeMode`; `t3_thread_list {limit:1}` → `projectId` |
| Model catalog | `orchestrator_capabilities {}` → `providers[]` with `providerInstanceId`, `models[].id`, `models[].options`, `constraints` |
| Live threads | `t3_thread_list {settled:false}` (fields: `threadId`, `title`, `status`, `providerInstanceId`, `model`, `runtimeMode`, `parentThreadId`, `linkedPullRequest`) |
| Other projects | `t3_project_list {}`, then `t3_thread_list {projectId, settled:false}` |
| Find a thread | `t3_thread_search {query}` or `t3_thread_list {titleContains}` |
| Name yourself | `t3_thread_update {action:"rename", title:"Supervisor Chat"}` |
| Rename a thread | `t3_thread_update {action:"rename", threadId, title}` |
| Branch inventory | `t3_worktree_list {query}` → refs and checkout paths |
| New worker thread | `t3_thread_launch {title, workspaceStrategy, modelSelection, interactionMode:"default", message:"<brief>"}` → `threadId` |
| Check a worker | `t3_thread_list {titleContains}` → `status` ∈ `preparing`, `queued`, `starting`, `running`, `waiting`, `completed`, `interrupted`, `failed`, `cancelled`, `idle` |
| Read a worker | `t3_thread_read {threadId, view:"activity", limit:30}`; final answers: `view:"messages"`; long items: `itemId` + `textOffset` |
| Message a worker | `t3_thread_send {threadId, message, mode:"queue", clientRequestId}` (`steer` for an in-flight correction, `restart` to interrupt and redo) |
| Pending questions | `t3_pending_request_list {threadId}` → answer with `t3_pending_request_respond` |
| Interrupt | `t3_thread_interrupt {threadId, reason}` |
| Short bounded wait | `t3_thread_wait {threadId, timeoutMs:15000}` (does not interrupt work) |
| Flag for the user | `t3_thread_organize {action:"mark_unread", threadId}` or `{action:"pin", threadId}` |
| Close own thread | `t3_thread_organize {action:"settle"|"archive", threadId}` (only threads you created, only on user request) |

## Launching a worker

`t3_thread_launch` has no retry key. Keep the returned `threadId`. If a call errors or its response is lost, check `t3_thread_list {titleContains:"<label>"}` before retrying. The calling thread must be full-access or default.

- `title`: the worker label from Naming.
- `projectId`: omit to use the supervisor's project. For another repository, take the ID from `t3_project_list`. If the directory is not a registered project, ask the user before creating one. Set `scratch:true` instead for work that needs no repository.
- `workspaceStrategy`:
  - Repository changes: `{"type":"worktree","baseRef":"<default branch>","branch":"<worker-name or repo-convention branch>","startFromOrigin":true}`. Use `startFromOrigin:false` and a local `baseRef` when stacking on unpushed work.
  - Continuing on an existing branch: `{"type":"existing_worktree","worktreePath":"<abs path>","branch":"<branch>"}`. Get paths from `t3_worktree_list`.
  - Read-only research in the repository: `{"type":"root"}`. Omitting the strategy also means root, not your worktree.
  - Never tell a worker to `git worktree add` or `cd` elsewhere. That does not move the T3 binding. When a development workflow wants its own worktree, the brief says the thread is already an isolated worktree on `<branch>` and that the workflow should use it.
- `modelSelection`: `{"instanceId":"<providerInstanceId>","model":"<model id>","options":[{"id":"<option id>","value":"<value>"}]}`. See `references/models.md`.
- `runtimeMode`: omit so the worker inherits yours. `t3_thread_send` refuses a target whose permissions are broader than the caller's, so if the worker's mode differs from yours, one of you may not be able to message the other.
- `interactionMode:"default"`. Plan mode stops at a plan.
- `message`: the full brief. It is delivered after workspace preparation, so launching and briefing happen in one call.

To confirm the launch, the thread should move through `preparing` and `starting` to `running`. Read its activity once to check that it is doing the task. If it shows `waiting`, check `t3_pending_request_list`. If preparation fails, read the thread, report the failure, and do not relaunch blind.

## Mapping to the dispatcher

- **Location:** your `threadId` and `projectId`. **Your name** is the `supervisor` slug used in reports; **your label** is your thread title.
- **Other supervisors:** thread titles starting with `Supervisor Chat`. Relabel another supervisor's thread with `t3_thread_update`.
- **Live threads to report:** unsettled top-level threads (`parentThreadId: null`) other than yours. Mention child subagents only when asked.
- **Status and messaging:** `t3_thread_list`, `t3_thread_read`, `t3_thread_send`. Do not use long `t3_thread_wait` calls or loops on workers.
- **Alert:** a worker report already shows up in this thread. When a worker thread needs the user's review, mark it unread.
- **PRs:** if T3's `link_pull_request` is available, register worker PRs with this thread as well when you report them.

## Brief blocks

Fill `<host reporting block>` in the worker brief with:

```
Report by sending a message to the supervisor's T3 thread; never wait for the supervisor to poll you.
Tool: t3_thread_send (Claude Code: mcp__t3-code__t3_thread_send; Codex: mcp__t3_code__t3_thread_send).
  {"threadId":"<supervisor threadId>","mode":"queue","clientRequestId":"<worker-name>-<kind>-<n>","message":"[<worker-name>] BLOCKED: <blocker, what you tried, what you need>"}
  ... "message":"[<worker-name>] QUESTION: <decision needed, options, your recommendation>"
  ... "message":"[<worker-name>] DONE: <result, evidence paths, changed files, checks run, branch/commits/PR, limitations>"
Use a new clientRequestId for each report and keep it stable across retries of that report. Link any PR you open to your own thread with link_pull_request.
If the T3 tools are not listed, call orchestrator_capabilities once directly. If that fails and T3_ACP_MCP_NODE is set, run:
  ELECTRON_RUN_AS_NODE=1 "$T3_ACP_MCP_NODE" ${T3_ACP_MCP_ENTRYPOINT:+"$T3_ACP_MCP_ENTRYPOINT"} acp-mcp-call t3_thread_send '<json above>'
```

Fill `<host delegation block>` with:

```
Delegate inside your own thread with T3 delegated tasks. Never launch top-level threads (no t3_thread_launch or create_threads).
  orchestrator_capabilities {}                      # pick providerInstanceId, model, options
  delegate_task {"title":"<role>","role":"research|implementation|review|test|design|general","mode":"async",
                 "target":{"providerInstanceId":"<id>","model":"<model>"},"clientRequestId":"<worker-name>-<role>-<n>",
                 "task":"<self-contained brief including this execution contract>"}
  task_status {"taskId":"<taskId>"}                 # only when you need the result mid-turn
Native sub-agent tools are fine when they support the chosen model. Async completions wake your thread, so do not poll or spawn watchers. For each new review round, call delegate_task again with the full context; never t3_thread_send to a childThreadId. Title each task for its role (research, implement, review). Sub-agents report to you, not to the supervisor.
```

Location line for the brief: `T3 thread <worker threadId> in project <projectId>, workspace <worktree path or root>, branch <branch>`; supervisor address: name and supervisor `threadId`. A worker learns its own `threadId` from `t3_thread_configuration {}` after launch, so the brief may leave it as `your own thread`.
