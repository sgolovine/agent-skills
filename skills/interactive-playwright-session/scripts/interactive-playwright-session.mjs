#!/usr/bin/env node

import { spawn, spawnSync } from "node:child_process";
import { randomBytes, timingSafeEqual } from "node:crypto";
import fs from "node:fs/promises";
import fsSync from "node:fs";
import http from "node:http";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const VERSION = "1";
const DEFAULT_VIEWPORT = { width: 1280, height: 720 };
const DEFAULT_IDLE_MS = 30 * 60 * 1000;
const DEFAULT_BROWSER_CHANNEL = "chrome";
const MAX_REQUEST_BYTES = 1024 * 1024;
const MAX_EVENTS = 200;
const MAX_BATCH_COMMANDS = 50;
const TEXT_LIMIT = 20_000;
const GLOBAL_COMMANDS = new Set(["newtab", "tabs", "tab", "closetab", "status", "clear-events"]);

const scriptPath = fileURLToPath(import.meta.url);
const workspaceRequire = createRequire(path.join(process.cwd(), "package.json"));
const scriptRequire = createRequire(import.meta.url);
let chromium;
let playwrightPackagePath;

async function main() {
  const [command, ...args] = process.argv.slice(2);

  try {
    if (command === "start") {
      await startSession(args);
      return;
    }
    if (command === "daemon") {
      await runDaemon(args);
      return;
    }
    if (command === "status") {
      await printStatus(args);
      return;
    }
    if (command === "stop") {
      await stopSession(args);
      return;
    }
    if (command === "command") {
      await sendCommand(args);
      return;
    }
    if (command === "batch") {
      await sendBatch(args);
      return;
    }

    printUsage();
    process.exitCode = command ? 1 : 0;
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}

function printUsage() {
  const cli = `node ${shellQuote(scriptPath)}`;
  console.log(`Usage:
  ${cli} start --run-dir <run-dir> [--fresh] [--headless] [--channel <chrome|chromium>] [--url <url>]
  ${cli} status --state-file <session.json>
  ${cli} command --state-file <session.json> <command> [args...]
  ${cli} batch --state-file <session.json> --file <commands.json>
  ${cli} stop --state-file <session.json>

Examples:
  ${cli} start --run-dir agent-tests/2026-06-23--1 --fresh
  ${cli} start --run-dir agent-tests/2026-06-23--1 --fresh --url https://app.example.com/login
  ${cli} command --state-file agent-tests/2026-06-23--1/browser-session/session.json newtab http://localhost:8080
  ${cli} command --state-file agent-tests/2026-06-23--1/browser-session/session.json screenshot --tab 1 --path agent-tests/2026-06-23--1/home.png --full-page
`);
}

async function startSession(args) {
  const options = parseOptions(args);
  const stateFile = resolveStateFile(options);
  const sessionDir = path.dirname(stateFile);
  await fs.mkdir(sessionDir, { recursive: true, mode: 0o700 });

  const releaseLock = await acquireStartupLock(`${stateFile}.lock`);
  try {
    const existing = await readStateIfPresent(stateFile);
    if (existing) {
      const health = await fetchHealth(existing).catch(() => null);
      if (health?.ok) {
        if (!options.fresh && !options.replace) {
          throw new Error(`A healthy Playwright session already exists at ${stateFile}. Pass --fresh to replace it.`);
        }
        await requestShutdown(existing).catch(() => undefined);
        await waitForStateRemoval(stateFile, 5_000).catch(() => undefined);
      } else {
        await fs.rm(stateFile, { force: true }).catch(() => undefined);
      }
    }

    const browserChannel = String(options.channel ?? DEFAULT_BROWSER_CHANNEL);
    await loadPlaywright();
    await assertBrowserInstalled(browserChannel);

    const logFile = path.resolve(sessionDir, "daemon.log");
    const daemonArgs = [
      scriptPath,
      "daemon",
      "--state-file",
      stateFile,
      "--url",
      String(options.url ?? "about:blank"),
      "--viewport",
      String(options.viewport ?? `${DEFAULT_VIEWPORT.width}x${DEFAULT_VIEWPORT.height}`),
      "--idle-ms",
      String(options["idle-ms"] ?? DEFAULT_IDLE_MS),
      "--channel",
      browserChannel,
    ];

    if (options.headless) {
      daemonArgs.push("--headless");
    }

    const logFd = fsSync.openSync(logFile, "a");
    const child = spawn(process.execPath, daemonArgs, {
      cwd: process.cwd(),
      detached: true,
      env: {
        ...process.env,
        BROWSER_SESSION_STATE_FILE: stateFile,
        PLAYWRIGHT_SESSION_PACKAGE_PATH: playwrightPackagePath,
      },
      stdio: ["ignore", logFd, logFd],
    });
    child.unref();
    fsSync.closeSync(logFd);

    let result;
    try {
      result = await waitForHealthyState(stateFile, Number(options.timeout ?? 15_000));
    } catch (error) {
      const logTail = await tailFile(logFile, 80);
      const detail = logTail ? `\nDaemon log tail:\n${logTail}` : "";
      throw new Error(`${error instanceof Error ? error.message : String(error)}${detail}`);
    }
    printJson({
      ok: true,
      stateFile,
      logFile,
      pid: result.state.pid,
      port: result.state.port,
      token: result.state.token,
      mode: result.state.mode,
      browserChannel: result.state.browserChannel,
      command: `node ${shellQuote(scriptPath)} command --state-file ${shellQuote(stateFile)}`,
      stop: `node ${shellQuote(scriptPath)} stop --state-file ${shellQuote(stateFile)}`,
      health: result.health,
    });
  } finally {
    await releaseLock();
  }
}

async function printStatus(args) {
  const options = parseOptions(args);
  const stateFile = resolveStateFile(options);
  const state = await readState(stateFile);
  const health = await fetchHealth(state);
  printJson({ ok: true, stateFile, state, health });
}

async function stopSession(args) {
  const options = parseOptions(args);
  const stateFile = resolveStateFile(options);
  const state = await readStateIfPresent(stateFile);
  if (!state) {
    printJson({ ok: true, stopped: false, stateFile });
    return;
  }

  await requestShutdown(state);
  await waitForStateRemoval(stateFile, Number(options.timeout ?? 5_000)).catch(() => undefined);
  printJson({ ok: true, stopped: true, stateFile, pid: state.pid });
}

async function sendCommand(args) {
  const options = parseOptions(args);
  const state = await readState(resolveStateFile(options));
  const [command, ...commandArgs] = options._;
  if (!command) {
    throw new Error("Missing browser command.");
  }

  const body = {
    command,
    args: commandArgs,
    options: commandOptions(options),
  };
  if (options.tab != null) {
    body.tabId = Number(options.tab);
  }

  const result = await postJson(state, "/command", body);
  printJson(result);
}

async function sendBatch(args) {
  const options = parseOptions(args);
  const state = await readState(resolveStateFile(options));
  const file = options.file ? path.resolve(String(options.file)) : null;
  if (!file) {
    throw new Error("Batch mode requires --file <commands.json>.");
  }

  const body = JSON.parse(await fs.readFile(file, "utf8"));
  const result = await postJson(state, "/batch", body);
  printJson(result);
}

async function runDaemon(args) {
  await loadPlaywright();
  const options = parseOptions(args);
  const stateFile = resolveStateFile(options);
  const sessionDir = path.dirname(stateFile);
  const viewport = parseViewport(options.viewport);
  const headless = Boolean(options.headless);
  const browserChannel = String(options.channel ?? DEFAULT_BROWSER_CHANNEL);
  const token = String(options.token ?? randomBytes(32).toString("hex"));
  const idleMs = Number(options["idle-ms"] ?? DEFAULT_IDLE_MS);

  await fs.mkdir(sessionDir, { recursive: true, mode: 0o700 });

  const manager = new BrowserManager({ headless, viewport, browserChannel });
  await manager.launch(String(options.url ?? "about:blank"));

  const server = http.createServer(async (request, response) => {
    try {
      if (request.method === "GET" && request.url === "/health") {
        respondJson(response, 200, {
          ok: true,
          version: VERSION,
          mode: headless ? "headless" : "headed",
          browserChannel,
          pid: process.pid,
          uptimeMs: Math.round(process.uptime() * 1000),
          tabCount: manager.tabCount(),
          activeTabId: manager.activeTabId(),
        });
        return;
      }

      if (request.method !== "POST") {
        respondJson(response, 404, { ok: false, error: "Not found" });
        return;
      }

      if (!authorized(request, token)) {
        respondJson(response, 401, { ok: false, error: "Unauthorized" });
        return;
      }

      if (request.url === "/shutdown") {
        respondJson(response, 200, { ok: true });
        setTimeout(() => shutdown(0), 10);
        return;
      }

      const body = await readRequestJson(request);
      manager.resetIdleTimer();

      if (request.url === "/command") {
        const result = await manager.handleCommand(body);
        respondJson(response, 200, result);
        return;
      }

      if (request.url === "/batch") {
        const commands = Array.isArray(body.commands) ? body.commands : [];
        if (commands.length > MAX_BATCH_COMMANDS) {
          throw new Error(`Batch command limit is ${MAX_BATCH_COMMANDS}.`);
        }
        const results = [];
        for (const command of commands) {
          results.push(await manager.handleCommand(command));
        }
        respondJson(response, 200, { ok: true, results });
        return;
      }

      respondJson(response, 404, { ok: false, error: "Not found" });
    } catch (error) {
      respondJson(response, 500, { ok: false, error: error instanceof Error ? error.message : String(error) });
    }
  });

  let shuttingDown = false;
  let idleTimer = null;

  async function shutdown(code) {
    if (shuttingDown) {
      return;
    }
    shuttingDown = true;
    if (idleTimer) {
      clearTimeout(idleTimer);
    }
    await new Promise((resolve) => server.close(resolve));
    await manager.close();
    await removeOwnedStateFile(stateFile);
    process.exit(code);
  }

  manager.onActivity = () => {
    if (!idleMs || idleMs <= 0 || !headless) {
      return;
    }
    if (idleTimer) {
      clearTimeout(idleTimer);
    }
    idleTimer = setTimeout(() => shutdown(0), idleMs);
  };
  manager.resetIdleTimer();

  process.on("SIGTERM", () => shutdown(0));
  process.on("SIGINT", () => shutdown(0));
  process.on("uncaughtException", async (error) => {
    console.error(error);
    await shutdown(1);
  });
  process.on("unhandledRejection", async (error) => {
    console.error(error);
    await shutdown(1);
  });

  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("Failed to bind Playwright session server.");
  }

  await writeStateFile(stateFile, {
    pid: process.pid,
    port: address.port,
    token,
    startedAt: new Date().toISOString(),
    mode: headless ? "headless" : "headed",
    browserChannel,
    version: VERSION,
    stateFile,
    initialUrl: String(options.url ?? "about:blank"),
  });
}

class BrowserManager {
  constructor({ headless, viewport, browserChannel }) {
    this.headless = headless;
    this.viewport = viewport;
    this.browserChannel = browserChannel;
    this.browser = null;
    this.context = null;
    this.pages = new Map();
    this.pageIds = new WeakMap();
    this.nextTabId = 1;
    this.currentTabId = null;
    this.consoleEvents = [];
    this.networkEvents = [];
    this.dialogEvents = [];
    this.locks = new Map();
    this.onActivity = () => undefined;
  }

  async launch(initialUrl) {
    const launchOptions = {
      headless: this.headless,
      args: chromiumArgs(),
    };
    if (this.browserChannel !== "chromium") {
      launchOptions.channel = this.browserChannel;
    }
    this.browser = await chromium.launch(launchOptions);
    this.context = await this.browser.newContext({
      viewport: this.headless ? this.viewport : null,
      ...(this.headless ? { deviceScaleFactor: 1 } : {}),
    });
    this.context.on("page", (page) => this.registerPage(page));
    await this.newTab(initialUrl);
  }

  resetIdleTimer() {
    this.onActivity();
  }

  tabCount() {
    return this.pages.size;
  }

  activeTabId() {
    return this.currentTabId;
  }

  async handleCommand(body) {
    const command = String(body?.command ?? "");
    if (!command) {
      throw new Error("Missing command.");
    }

    if (GLOBAL_COMMANDS.has(command)) {
      return this.withLock("global", () => this.dispatch(command, body));
    }

    const tabId = body.tabId == null ? this.currentTabId : Number(body.tabId);
    if (!tabId || !this.pages.has(tabId)) {
      throw new Error(`Tab ${tabId} is not available.`);
    }
    return this.withLock(`tab:${tabId}`, () => this.dispatch(command, { ...body, tabId }));
  }

  async dispatch(command, body) {
    const args = Array.isArray(body.args) ? body.args : [];
    const options = body.options && typeof body.options === "object" ? body.options : {};

    if (command === "status") {
      return { ok: true, tabs: this.tabs(), activeTabId: this.currentTabId };
    }

    if (command === "tabs") {
      return { ok: true, tabs: this.tabs(), activeTabId: this.currentTabId };
    }

    if (command === "newtab") {
      return { ok: true, ...(await this.newTab(String(args[0] ?? "about:blank"))) };
    }

    if (command === "tab") {
      const tabId = Number(args[0] ?? body.tabId);
      if (!this.pages.has(tabId)) {
        throw new Error(`Tab ${tabId} is not available.`);
      }
      this.currentTabId = tabId;
      return { ok: true, activeTabId: tabId, url: this.pages.get(tabId).url() };
    }

    if (command === "closetab") {
      const tabId = Number(args[0] ?? body.tabId ?? this.currentTabId);
      const page = this.pages.get(tabId);
      if (!page) {
        throw new Error(`Tab ${tabId} is not available.`);
      }
      await page.close();
      return { ok: true, closedTabId: tabId, activeTabId: this.currentTabId };
    }

    if (command === "clear-events") {
      this.consoleEvents.length = 0;
      this.networkEvents.length = 0;
      this.dialogEvents.length = 0;
      return { ok: true };
    }

    const page = this.page(body.tabId);
    const timeout = Number(options.timeout ?? 30_000);

    if (command === "goto") {
      await page.goto(requiredArg(args, 0, "goto requires a URL."), {
        waitUntil: String(options["wait-until"] ?? "domcontentloaded"),
        timeout,
      });
      return this.pageResult(page, body.tabId);
    }

    if (command === "reload") {
      await page.reload({ waitUntil: String(options["wait-until"] ?? "domcontentloaded"), timeout });
      return this.pageResult(page, body.tabId);
    }

    if (command === "back") {
      await page.goBack({ waitUntil: String(options["wait-until"] ?? "domcontentloaded"), timeout });
      return this.pageResult(page, body.tabId);
    }

    if (command === "forward") {
      await page.goForward({ waitUntil: String(options["wait-until"] ?? "domcontentloaded"), timeout });
      return this.pageResult(page, body.tabId);
    }

    if (command === "wait") {
      await page.waitForTimeout(Number(args[0] ?? 1000));
      return this.pageResult(page, body.tabId);
    }

    if (command === "wait-for") {
      await page.locator(requiredArg(args, 0, "wait-for requires a selector.")).waitFor({
        state: String(options.state ?? "visible"),
        timeout,
      });
      return this.pageResult(page, body.tabId);
    }

    if (command === "title") {
      return { ok: true, tabId: body.tabId, title: await page.title(), url: page.url() };
    }

    if (command === "url") {
      return { ok: true, tabId: body.tabId, url: page.url() };
    }

    if (command === "text") {
      const text = await page.locator(String(args[0] ?? "body")).innerText({ timeout });
      return { ok: true, tabId: body.tabId, url: page.url(), text: truncate(text, Number(options.limit ?? TEXT_LIMIT)) };
    }

    if (command === "click") {
      await page.locator(requiredArg(args, 0, "click requires a selector.")).click({ timeout });
      return this.pageResult(page, body.tabId);
    }

    if (command === "fill") {
      await page.locator(requiredArg(args, 0, "fill requires a selector.")).fill(String(args[1] ?? ""), { timeout });
      return this.pageResult(page, body.tabId);
    }

    if (command === "type") {
      await page.locator(requiredArg(args, 0, "type requires a selector.")).pressSequentially(String(args[1] ?? ""), {
        delay: Number(options.delay ?? 0),
        timeout,
      });
      return this.pageResult(page, body.tabId);
    }

    if (command === "press") {
      await page.locator(requiredArg(args, 0, "press requires a selector.")).press(String(args[1] ?? "Enter"), { timeout });
      return this.pageResult(page, body.tabId);
    }

    if (command === "hover") {
      await page.locator(requiredArg(args, 0, "hover requires a selector.")).hover({ timeout });
      return this.pageResult(page, body.tabId);
    }

    if (command === "select") {
      await page.locator(requiredArg(args, 0, "select requires a selector.")).selectOption(String(args[1] ?? ""), { timeout });
      return this.pageResult(page, body.tabId);
    }

    if (command === "scroll") {
      const x = Number(args[0] ?? 0);
      const y = args[0] === "bottom" ? "bottom" : Number(args[1] ?? 0);
      if (y === "bottom") {
        await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
      } else {
        await page.mouse.wheel(x, y);
      }
      return this.pageResult(page, body.tabId);
    }

    if (command === "setviewport") {
      const viewport = parseViewport(args[0] ?? `${options.width}x${options.height}`);
      await page.setViewportSize(viewport);
      return { ok: true, tabId: body.tabId, viewport };
    }

    if (command === "screenshot") {
      const screenshotPath = options.path ? path.resolve(String(options.path)) : null;
      if (!screenshotPath) {
        throw new Error("screenshot requires --path <file>.");
      }
      await fs.mkdir(path.dirname(screenshotPath), { recursive: true });
      await page.screenshot({
        path: screenshotPath,
        fullPage: Boolean(options["full-page"] ?? options.fullPage),
        timeout,
      });
      return { ok: true, tabId: body.tabId, url: page.url(), path: screenshotPath };
    }

    if (command === "cookies") {
      return { ok: true, cookies: await this.context.cookies() };
    }

    if (command === "storage") {
      return {
        ok: true,
        tabId: body.tabId,
        url: page.url(),
        storage: await page.evaluate(() => ({
          localStorage: Object.fromEntries(Object.entries(window.localStorage)),
          sessionStorage: Object.fromEntries(Object.entries(window.sessionStorage)),
        })),
      };
    }

    if (command === "console") {
      return { ok: true, events: this.filteredEvents(this.consoleEvents, body.tabId, options.limit) };
    }

    if (command === "network") {
      return { ok: true, events: this.filteredEvents(this.networkEvents, body.tabId, options.limit) };
    }

    if (command === "dialogs") {
      return { ok: true, events: this.filteredEvents(this.dialogEvents, body.tabId, options.limit) };
    }

    throw new Error(`Unknown command: ${command}`);
  }

  async newTab(url) {
    if (!this.context) {
      throw new Error("Browser context is not launched.");
    }
    const page = await this.context.newPage();
    const tabId = this.registerPage(page);
    this.currentTabId = tabId;
    if (url && url !== "about:blank") {
      await page.goto(url, { waitUntil: "domcontentloaded" });
    }
    return { tabId, url: page.url() };
  }

  registerPage(page) {
    const existingId = this.pageIds.get(page);
    if (existingId) {
      return existingId;
    }

    const tabId = this.nextTabId;
    this.nextTabId += 1;
    this.pageIds.set(page, tabId);
    this.pages.set(tabId, page);
    this.currentTabId = tabId;

    page.on("close", () => {
      this.pages.delete(tabId);
      if (this.currentTabId === tabId) {
        this.currentTabId = this.pages.keys().next().value ?? null;
      }
    });
    page.on("console", (message) => {
      this.pushEvent(this.consoleEvents, {
        time: new Date().toISOString(),
        tabId,
        type: message.type(),
        text: truncate(message.text(), 2000),
        url: safePageUrl(page),
      });
    });
    page.on("requestfailed", (request) => {
      this.pushEvent(this.networkEvents, {
        time: new Date().toISOString(),
        tabId,
        type: "requestfailed",
        method: request.method(),
        url: truncate(request.url(), 2000),
        resourceType: request.resourceType(),
        error: truncate(request.failure()?.errorText ?? "request failed", 2000),
      });
    });
    page.on("response", (response) => {
      if (response.status() < 400) {
        return;
      }
      this.pushEvent(this.networkEvents, {
        time: new Date().toISOString(),
        tabId,
        type: "response",
        status: response.status(),
        url: truncate(response.url(), 2000),
      });
    });
    page.on("dialog", async (dialog) => {
      this.pushEvent(this.dialogEvents, {
        time: new Date().toISOString(),
        tabId,
        type: dialog.type(),
        message: truncate(dialog.message(), 2000),
        url: safePageUrl(page),
      });
      await dialog.accept("").catch(() => undefined);
    });

    return tabId;
  }

  page(tabId) {
    const page = this.pages.get(Number(tabId));
    if (!page) {
      throw new Error(`Tab ${tabId} is not available.`);
    }
    this.currentTabId = Number(tabId);
    return page;
  }

  pageResult(page, tabId) {
    return { ok: true, tabId, url: page.url() };
  }

  tabs() {
    return [...this.pages.entries()].map(([tabId, page]) => ({
      tabId,
      url: safePageUrl(page),
      closed: page.isClosed(),
    }));
  }

  filteredEvents(events, tabId, limit = 20) {
    const filtered = tabId == null ? events : events.filter((event) => event.tabId === Number(tabId));
    return filtered.slice(-Number(limit ?? 20));
  }

  pushEvent(buffer, event) {
    buffer.push(event);
    while (buffer.length > MAX_EVENTS) {
      buffer.shift();
    }
  }

  async withLock(key, operation) {
    const previous = this.locks.get(key) ?? Promise.resolve();
    let release = () => undefined;
    const gate = new Promise((resolve) => {
      release = resolve;
    });
    const current = previous.catch(() => undefined).then(() => gate);
    this.locks.set(key, current);
    await previous.catch(() => undefined);
    try {
      return await operation();
    } finally {
      release();
      if (this.locks.get(key) === current) {
        this.locks.delete(key);
      }
    }
  }

  async close() {
    await this.context?.close().catch(() => undefined);
    await this.browser?.close().catch(() => undefined);
    this.context = null;
    this.browser = null;
    this.pages.clear();
    this.currentTabId = null;
  }
}

function parseOptions(args) {
  const options = { _: [] };
  for (let index = 0; index < args.length; index += 1) {
    const item = args[index];
    if (!item.startsWith("--")) {
      options._.push(item);
      continue;
    }

    const [rawKey, inlineValue] = item.slice(2).split("=", 2);
    const key = rawKey.trim();
    if (inlineValue != null) {
      options[key] = coerceValue(inlineValue);
      continue;
    }

    const next = args[index + 1];
    if (next == null || next.startsWith("--")) {
      options[key] = true;
      continue;
    }

    options[key] = coerceValue(next);
    index += 1;
  }
  return options;
}

function commandOptions(options) {
  const reserved = new Set(["_", "run-dir", "state-file", "tab"]);
  const result = {};
  for (const [key, value] of Object.entries(options)) {
    if (!reserved.has(key)) {
      result[key] = value;
    }
  }
  return result;
}

function coerceValue(value) {
  if (value === "true") {
    return true;
  }
  if (value === "false") {
    return false;
  }
  return value;
}

function resolveStateFile(options) {
  if (options["state-file"]) {
    return path.resolve(String(options["state-file"]));
  }
  if (process.env.BROWSER_SESSION_STATE_FILE) {
    return path.resolve(process.env.BROWSER_SESSION_STATE_FILE);
  }
  if (options["run-dir"]) {
    return path.resolve(String(options["run-dir"]), "browser-session", "session.json");
  }
  return path.resolve(process.cwd(), ".browser-session", "session.json");
}

function parseViewport(value) {
  if (!value) {
    return DEFAULT_VIEWPORT;
  }
  const [width, height] = String(value).split("x").map((part) => Number(part));
  if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) {
    throw new Error(`Invalid viewport: ${value}`);
  }
  return { width, height };
}

function chromiumArgs() {
  const args = [
    "--disable-dev-shm-usage",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
  ];
  if (!chromiumSandboxEnabled()) {
    args.push("--no-sandbox");
  }
  return args;
}

async function loadPlaywright() {
  if (chromium) {
    return;
  }

  const inheritedPackagePath = process.argv[2] === "daemon"
    ? process.env.PLAYWRIGHT_SESSION_PACKAGE_PATH
    : null;
  if (inheritedPackagePath) {
    const playwright = tryRequirePlaywright(inheritedPackagePath);
    if (playwright) {
      chromium = playwright.chromium;
      playwrightPackagePath = inheritedPackagePath;
      return;
    }
  }

  try {
    const playwright = workspaceRequire("playwright");
    chromium = playwright.chromium;
    playwrightPackagePath = workspaceRequire.resolve("playwright");
    return;
  } catch {
    // Try a global installation next.
  }

  const globalRoots = new Set((process.env.NODE_PATH ?? "").split(path.delimiter).filter(Boolean));
  const globalRootResult = spawnSync("npm", ["root", "-g"], { encoding: "utf8", timeout: 10_000 });
  if (globalRootResult.status === 0 && globalRootResult.stdout?.trim()) {
    globalRoots.add(globalRootResult.stdout.trim());
  }
  for (const root of globalRoots) {
    const packagePath = path.join(root, "playwright");
    const playwright = tryRequirePlaywright(packagePath);
    if (playwright) {
      chromium = playwright.chromium;
      playwrightPackagePath = packagePath;
      return;
    }
  }

  const locator = process.platform === "win32" ? "where playwright" : "command -v playwright";
  const npxResult = spawnSync("npx", ["--yes", "--package=playwright", "--call", locator], {
    cwd: process.cwd(),
    encoding: "utf8",
    timeout: 120_000,
  });
  const executablePath = npxResult.status === 0 ? npxResult.stdout?.trim().split(/\r?\n/)[0] : null;
  const binDirectory = executablePath ? path.dirname(executablePath) : null;
  const npxPackagePath = binDirectory && path.basename(binDirectory) === ".bin"
    ? path.join(path.dirname(binDirectory), "playwright")
    : null;
  const npxPlaywright = npxPackagePath ? tryRequirePlaywright(npxPackagePath) : null;
  if (npxPlaywright) {
    chromium = npxPlaywright.chromium;
    playwrightPackagePath = npxPackagePath;
    return;
  }

  throw new Error("Unable to load Playwright from the target project, a global installation, or npx playwright.");
}

function tryRequirePlaywright(packagePath) {
  try {
    const playwright = scriptRequire(packagePath);
    return playwright?.chromium ? playwright : null;
  } catch {
    return null;
  }
}

async function assertBrowserInstalled(browserChannel) {
  if (browserChannel !== "chromium") {
    return;
  }
  await assertChromiumInstalled();
}

async function assertChromiumInstalled() {
  const executablePath = chromium.executablePath();
  try {
    await fs.access(executablePath, fsSync.constants.X_OK);
  } catch {
    throw new Error(`Playwright Chromium is not installed at ${executablePath}. Run: pnpm exec playwright install chromium`);
  }
}

function chromiumSandboxEnabled() {
  if (process.platform === "win32") {
    return false;
  }
  if (process.env.CI) {
    return false;
  }
  if (process.getuid?.() === 0) {
    return false;
  }
  if (process.env.CHROMIUM_NO_SANDBOX === "1") {
    return false;
  }
  return true;
}

async function acquireStartupLock(lockFile) {
  await fs.mkdir(path.dirname(lockFile), { recursive: true, mode: 0o700 });
  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline) {
    try {
      const handle = await fs.open(lockFile, "wx", 0o600);
      await handle.writeFile(`${process.pid}\n`);
      return async () => {
        await handle.close().catch(() => undefined);
        await fs.rm(lockFile, { force: true }).catch(() => undefined);
      };
    } catch (error) {
      if (error?.code !== "EEXIST") {
        throw error;
      }
      const stat = await fs.stat(lockFile).catch(() => null);
      if (stat && Date.now() - stat.mtimeMs > 30_000) {
        await fs.rm(lockFile, { force: true }).catch(() => undefined);
        continue;
      }
      await sleep(100);
    }
  }
  throw new Error(`Timed out waiting for startup lock: ${lockFile}`);
}

async function readState(stateFile) {
  const state = await readStateIfPresent(stateFile);
  if (!state) {
    throw new Error(`No Playwright session state file found at ${stateFile}`);
  }
  return state;
}

async function readStateIfPresent(stateFile) {
  try {
    return JSON.parse(await fs.readFile(stateFile, "utf8"));
  } catch (error) {
    if (error?.code === "ENOENT") {
      return null;
    }
    throw error;
  }
}

async function writeStateFile(stateFile, state) {
  const tempFile = `${stateFile}.${process.pid}.${Date.now()}.tmp`;
  await fs.writeFile(tempFile, `${JSON.stringify(state, null, 2)}\n`, { mode: 0o600 });
  await fs.rename(tempFile, stateFile);
  await fs.chmod(stateFile, 0o600).catch(() => undefined);
}

async function removeOwnedStateFile(stateFile) {
  const state = await readStateIfPresent(stateFile);
  if (!state || state.pid === process.pid) {
    await fs.rm(stateFile, { force: true }).catch(() => undefined);
  }
}

async function waitForHealthyState(stateFile, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      const state = await readState(stateFile);
      const health = await fetchHealth(state);
      if (health.ok) {
        return { state, health };
      }
    } catch (error) {
      lastError = error;
    }
    await sleep(250);
  }
  throw new Error(`Timed out waiting for Playwright session startup at ${stateFile}: ${lastError?.message ?? "not ready"}`);
}

async function waitForStateRemoval(stateFile, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (!(await readStateIfPresent(stateFile))) {
      return;
    }
    await sleep(100);
  }
}

async function fetchHealth(state) {
  const response = await fetch(`http://127.0.0.1:${state.port}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}

async function requestShutdown(state) {
  return postJson(state, "/shutdown", {});
}

async function postJson(state, endpoint, body) {
  const response = await fetch(`http://127.0.0.1:${state.port}${endpoint}`, {
    method: "POST",
    headers: {
      "authorization": `Bearer ${state.token}`,
      "content-type": "application/json",
    },
    body: JSON.stringify(body ?? {}),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.ok === false) {
    throw new Error(payload.error ?? `Request failed: ${response.status}`);
  }
  return payload;
}

function authorized(request, token) {
  const header = request.headers.authorization ?? "";
  const received = header.startsWith("Bearer ") ? header.slice("Bearer ".length) : "";
  const expectedBuffer = Buffer.from(token);
  const receivedBuffer = Buffer.from(received);
  return receivedBuffer.length === expectedBuffer.length && timingSafeEqual(receivedBuffer, expectedBuffer);
}

async function readRequestJson(request) {
  const chunks = [];
  let total = 0;
  for await (const chunk of request) {
    total += chunk.length;
    if (total > MAX_REQUEST_BYTES) {
      throw new Error("Request body is too large.");
    }
    chunks.push(chunk);
  }
  const text = Buffer.concat(chunks).toString("utf8");
  return text ? JSON.parse(text) : {};
}

function respondJson(response, status, body) {
  response.writeHead(status, { "content-type": "application/json" });
  response.end(`${JSON.stringify(body)}\n`);
}

function printJson(value) {
  console.log(JSON.stringify(value, null, 2));
}

function requiredArg(args, index, message) {
  if (args[index] == null || args[index] === "") {
    throw new Error(message);
  }
  return String(args[index]);
}

function truncate(value, maxLength) {
  const text = String(value ?? "");
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength)}...`;
}

function safePageUrl(page) {
  try {
    return page.url();
  } catch {
    return "";
  }
}

function shellQuote(value) {
  return `'${String(value).replaceAll("'", "'\\''")}'`;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function tailFile(file, lineCount) {
  try {
    const text = await fs.readFile(file, "utf8");
    return text.split(/\r?\n/).slice(-lineCount).join("\n").trim();
  } catch {
    return "";
  }
}

await main();
