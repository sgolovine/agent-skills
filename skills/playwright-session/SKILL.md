---
name: playwright-session
description: Run browser automation through one shared, reusable Playwright-controlled Chromium daemon instead of separate browser processes. Use when a task needs shared browser state across subagents or repeated checks, stable tab handoff, bounded screenshot/console/network evidence, or explicit session cleanup.
---

# Playwright Session

Run all browser work for a task through one Playwright-controlled Chromium daemon, driven by the bundled script at this skill's `scripts/playwright-session.mjs`. Resolve that path to an absolute path once (from this SKILL.md's location) and reuse it in every command below as `$PLAYWRIGHT_SESSION_SCRIPT`.

## Rules

- One daemon per run. Never start a second daemon, a separate Playwright process, or a raw Chromium process for the same task.
- One browser context. Open multiple tabs for parallel work; never create extra contexts or profiles.
- Headless by default. Pass `--headed` only when the user asks for a visible browser or visual debugging requires one.
- Run all script commands from the target repo's root so Node resolves that repo's installed `playwright` dependency. Do not use `npx` to fetch a transient Playwright copy; if `playwright` (with Chromium) is not installed in the workspace, stop and tell the user rather than installing it silently.
- The daemon binds to `127.0.0.1` and requires a bearer token stored in the state file, so the state file path is the only handle agents need. Treat it as an access handle, not durable browser storage: do not assume cookies, storage, or tabs survive a daemon stop or restart.
- The daemon shuts itself down after 30 minutes without commands (override with `--idle-ms <ms>` on start). If a command fails because the daemon is gone, check `status`, then restart and re-establish tabs.

## Start

Pick a run directory `$RUN_DIR` for this task's artifacts (an existing run/output directory if the workflow has one, otherwise create one, e.g. `.agent-runs/<task>`). The state file will be written to `$RUN_DIR/browser-session/session.json`.

```sh
node "$PLAYWRIGHT_SESSION_SCRIPT" start --run-dir "$RUN_DIR" --fresh --url about:blank
```

Notes:

- Without `--fresh`, start fails if a healthy session already exists at that state file. Reuse the existing session in that case; pass `--fresh` only when you intend to replace it.
- Optional start flags: `--headed`, `--viewport <WxH>` (default 1280x720), `--idle-ms <ms>`, `--timeout <ms>` (startup wait, default 15000).
- On success, start prints JSON with `stateFile`, `logFile`, `pid`, `port`, `mode`, a ready-to-use `command` prefix, and a `stop` command. Record `stateFile` and `logFile` in the run log or handoff notes.

Set the state file variable and health-check before browser work:

```sh
BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"
node "$PLAYWRIGHT_SESSION_SCRIPT" status --state-file "$BROWSER_SESSION_STATE_FILE"
```

## Handoff To Subagents

Give every browser-using subagent:

- the target repo root (its working directory)
- `BROWSER_SESSION_STATE_FILE` (the script also reads this env var, so `--state-file` may be omitted when it is exported)
- the command prefix: `node "$PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE"`
- its assigned tab id, or instructions to create its own tab with `newtab`
- the evidence directory for its screenshots and captures
- the rule that it must not start any other browser session

Give each concurrent agent its own tab and have it pass `--tab <id>` on every command — commands without `--tab` target the daemon's active tab, which changes as tabs open and close. If stable tab ownership can't be maintained, run browser-using agents serially instead.

## Commands

```sh
node "$PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" newtab http://localhost:8080
node "$PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" screenshot --tab 1 --path "$RUN_DIR/screenshots/home.png" --full-page
```

`newtab` returns the new tab's id; use it for all subsequent `--tab` arguments.

- Tabs: `newtab [url]`, `tabs`, `tab <id>` (make active), `closetab [--tab <id>]`, `status`, `clear-events`
- Navigation: `goto <url>`, `reload`, `back`, `forward` (all accept `--wait-until <state>`, default `domcontentloaded`)
- Waiting/inspection: `wait <ms>`, `wait-for <selector> [--state visible|attached|hidden|detached]`, `title`, `url`, `text [selector] [--limit <chars>]`
- Interaction: `click <selector>`, `fill <selector> <value>`, `type <selector> <text>`, `press <selector> <key>`, `hover <selector>`, `select <selector> <value>`, `scroll <x> <y>` (or `scroll bottom`), `setviewport <WxH>`
- Evidence: `screenshot --path <file> [--full-page]`, `cookies`, `storage`, `console [--limit <n>]`, `network [--limit <n>]`, `dialogs [--limit <n>]`

For multi-step sequences, batch commands in one call:

```sh
node "$PLAYWRIGHT_SESSION_SCRIPT" batch --state-file "$BROWSER_SESSION_STATE_FILE" --file commands.json
```

where `commands.json` is `{"commands": [{"command": "goto", "args": ["http://localhost:8080"], "tabId": 1}, ...]}` — each entry takes `command`, `args` (array), optional `tabId`, and optional `options` (the `--flag` values as keys).

## Evidence Limits

- Keep console, network, and dialog captures bounded: use `--limit`, summarize, and store compact JSON/text and screenshots under the run directory.
- Do not dump raw event streams, full browser logs, or unbounded console output into terminal output or run logs.
- If a page emits the same noisy message repeatedly (e.g. dev-server reload loops), record one short summary and stop collecting that message class.

## Cleanup

Stop only the daemon this run started:

```sh
node "$PLAYWRIGHT_SESSION_SCRIPT" stop --state-file "$RUN_DIR/browser-session/session.json"
```

Never kill the user's normal browser or another run's Playwright process by pid. If you can't confirm the daemon belongs to this run, leave it running and report that, along with the state file and daemon log paths.
