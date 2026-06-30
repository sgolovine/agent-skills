---
name: playwright-session
description: Start and coordinate one reusable Playwright-controlled Chromium daemon for browser automation across Codex subagents or repeated local browser checks. Use when a task needs shared browser state, stable tab handoff, bounded screenshot/console/network evidence, or explicit cleanup of a headless or headed Playwright session.
---

# Playwright Session

Use this skill when browser work should run through one reusable Playwright-controlled Chromium daemon instead of starting separate browser processes.

## Session Invariants

- Use exactly one daemon for the run.
- Use the bundled script at this skill's `scripts/playwright-session.mjs`.
- Start headless by default. Use `--headed` only when the user explicitly asks or visual debugging requires it.
- Store daemon state under `$RUN_DIR/browser-session/session.json`.
- Pass `BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"` to every browser-using agent.
- Use one browser context. Create multiple tabs in that context instead of multiple contexts, profiles, Browser plugin sessions, Playwright processes, or Chromium processes.
- Bind command access to `127.0.0.1`; the script stores the bearer token in the state file and protects command and shutdown endpoints with it.
- Use an installed workspace `playwright` dependency. Do not use `npx` to download a transient Playwright copy.
- Treat the state file as command access and ownership state, not as a durable browser storage snapshot. Do not assume cookies, storage, or tabs survive daemon stop or restart unless the script explicitly reports support.

## Locate The Script

Set `PLAYWRIGHT_SESSION_SCRIPT` to the absolute path of the bundled script before giving commands to other agents:

```sh
PLAYWRIGHT_SESSION_SCRIPT="/path/to/playwright-session/scripts/playwright-session.mjs"
```

When this skill is installed from `agent-skills`, the repo copy is:

```sh
PLAYWRIGHT_SESSION_SCRIPT="/home/sgolovine/Projects/agent-skills/skills/playwright-session/scripts/playwright-session.mjs"
```

## Start And Record

Run commands from the target repo root so Node resolves that repo's `playwright` dependency.

Start the session after the run directory exists:

```sh
node "$PLAYWRIGHT_SESSION_SCRIPT" start --run-dir "$RUN_DIR" --fresh --url about:blank
```

Record the JSON output in the run log or handoff notes, including:

- state file path
- daemon log path
- process id
- command string
- stop string
- mode
- active tabs
- cleanup ownership

Health-check the daemon before browser work:

```sh
BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"
node "$PLAYWRIGHT_SESSION_SCRIPT" status --state-file "$BROWSER_SESSION_STATE_FILE"
```

## Handoff Contract

Every browser-using subagent must receive:

- target repo root
- run directory path
- `BROWSER_SESSION_STATE_FILE`
- command prefix: `node "$PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE"`
- assigned tab id or instructions to create one
- viewport assignment
- evidence directory
- lock expectations
- rule that no separate browser session may be created

Allocate separate tabs for independent agents. Use per-tab commands for tab-scoped work and avoid sharing one tab between concurrent agents. If stable tab ownership is unavailable, run browser-using agents serially.

## Commands

Create a tab and capture a screenshot:

```sh
BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"
node "$PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" newtab http://localhost:8080
node "$PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" screenshot --tab 1 --path "$RUN_DIR/screenshots/home.png" --full-page
```

Common command verbs:

- Browser/global: `newtab`, `tabs`, `tab`, `closetab`, `status`, `clear-events`
- Navigation: `goto`, `reload`, `back`, `forward`
- Waiting and inspection: `wait`, `wait-for`, `title`, `url`, `text`
- Interaction: `click`, `fill`, `type`, `press`, `hover`, `select`, `scroll`, `setviewport`
- Evidence: `screenshot`, `cookies`, `storage`, `console`, `network`, `dialogs`
- Batches: `node "$PLAYWRIGHT_SESSION_SCRIPT" batch --state-file "$BROWSER_SESSION_STATE_FILE" --file <commands.json>`

## Evidence Limits

- Keep console, network, and dialog evidence bounded and summarized.
- Store screenshots and compact JSON/text evidence under the run directory.
- Do not mirror raw CDP streams, WebSocket frames, full browser logs, or unbounded console/event dumps into terminal output, run logs, or stack logs.
- If a browser event contains recursive Vite forwarding text, store a short summary and stop collecting that message class for the page.

## Cleanup

Stop only the daemon started for the current run:

```sh
node "$PLAYWRIGHT_SESSION_SCRIPT" stop --state-file "$RUN_DIR/browser-session/session.json"
```

Never close the user's normal browser, an unrelated browser session, or another run's Playwright process. If cleanup cannot confirm ownership, leave the process running and report the uncertainty with the state file and daemon log path.
