#!/usr/bin/env -S tsx

import {
  cancel,
  intro,
  isCancel,
  multiselect,
  note,
  outro,
  select,
  spinner,
  text,
} from "@clack/prompts";
import { constants } from "node:fs";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..");
const skillsRoot = path.join(repoRoot, "skills");
const helpFlags = new Set(["-h", "--help"]);

type Skill = {
  dirName: string;
  name: string;
  sourcePath: string;
};

type InstallStatus = "conflict" | "installed" | "missing";
type Action = "install" | "manage";
type Harness = "codex" | "pi";

type InstallState = {
  status: InstallStatus;
  targetPath: string;
};

function isNodeError(error: unknown): error is NodeJS.ErrnoException {
  return error instanceof Error;
}

function handleCancel<T>(value: T | symbol): T {
  if (isCancel(value)) {
    cancel("Cancelled.");
    process.exit(0);
  }

  return value;
}

function expandHome(inputPath: string): string {
  if (inputPath === "~") {
    return os.homedir();
  }

  if (inputPath.startsWith("~/")) {
    return path.join(os.homedir(), inputPath.slice(2));
  }

  return inputPath;
}

async function exists(targetPath: string): Promise<boolean> {
  try {
    await fs.access(targetPath, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function readSkillName(skillDir: string): Promise<string> {
  const skillPath = path.join(skillsRoot, skillDir, "SKILL.md");
  const content = await fs.readFile(skillPath, "utf8");
  const nameMatch = content.match(/^name:\s*(.+)$/m);
  return nameMatch?.[1]?.trim() || skillDir;
}

async function discoverSkills(): Promise<Skill[]> {
  const entries = await fs.readdir(skillsRoot, { withFileTypes: true });
  const skillDirs: string[] = [];

  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }

    const skillPath = path.join(skillsRoot, entry.name, "SKILL.md");
    if (await exists(skillPath)) {
      skillDirs.push(entry.name);
    }
  }

  const skills = await Promise.all(
    skillDirs.sort().map(async (dirName) => ({
      dirName,
      name: await readSkillName(dirName),
      sourcePath: path.join(skillsRoot, dirName),
    })),
  );

  return skills;
}

async function getInstallState(targetDir: string, skill: Skill): Promise<InstallState> {
  const targetPath = path.join(targetDir, skill.dirName);

  try {
    const stat = await fs.lstat(targetPath);

    if (!stat.isSymbolicLink()) {
      return { status: "conflict", targetPath };
    }

    let realTarget: string;
    let realSource: string;

    try {
      [realTarget, realSource] = await Promise.all([
        fs.realpath(targetPath),
        fs.realpath(skill.sourcePath),
      ]);
    } catch {
      return { status: "conflict", targetPath };
    }

    return {
      status: realTarget === realSource ? "installed" : "conflict",
      targetPath,
    };
  } catch (error) {
    if (isNodeError(error) && error.code === "ENOENT") {
      return { status: "missing", targetPath };
    }

    throw error;
  }
}

function labelForSkill(skill: Skill, state: InstallState): string {
  if (state.status === "installed") {
    return `${skill.name} (installed)`;
  }

  if (state.status === "conflict") {
    return `${skill.name} (exists)`;
  }

  return skill.name;
}

async function installSkill(
  skill: Skill,
  state: InstallState,
): Promise<{ name: string; status: string }> {
  if (state.status === "installed") {
    return { name: skill.name, status: "already installed" };
  }

  if (state.status === "conflict") {
    return { name: skill.name, status: "skipped: target already exists" };
  }

  await fs.symlink(skill.sourcePath, state.targetPath, "dir");
  return { name: skill.name, status: "installed" };
}

async function removeSkill(
  skill: Skill,
  state: InstallState,
): Promise<{ name: string; status: string }> {
  if (state.status !== "installed") {
    return { name: skill.name, status: "skipped: not installed" };
  }

  await fs.unlink(state.targetPath);
  return { name: skill.name, status: "removed" };
}

function getKnownInstallState(
  installStates: Map<string, InstallState>,
  skill: Skill,
): InstallState {
  const state = installStates.get(skill.dirName);

  if (!state) {
    throw new Error(`Missing install state for ${skill.dirName}`);
  }

  return state;
}

function printHelp(): void {
  console.log(`Install or manage agent skills.

Usage:
  npm run install:skills

Options:
  -h, --help  Show this help message.`);
}

if (process.argv.slice(2).some((arg) => helpFlags.has(arg))) {
  printHelp();
  process.exit(0);
}

intro("Install or manage agent skills");

const skills = await discoverSkills();

if (skills.length === 0) {
  note(`No skills found in ${skillsRoot}.`, "Nothing to install");
  process.exit(0);
}

const action = handleCancel(
  await select<Action>({
    message: "What do you want to do?",
    options: [
      {
        value: "install",
        label: "Install new skills",
      },
      {
        value: "manage",
        label: "Manage installed skills",
      },
    ],
  }),
);

const harness = handleCancel(
  await select<Harness>({
    message: "Which coding harness do you want to install skills for?",
    options: [
      {
        value: "codex",
        label: "Codex CLI",
      },
      {
        value: "pi",
        label: "Pi",
      },
    ],
  }),
);

const harnessPaths = {
  codex: {
    global: [".codex", "skills"],
    project: [".codex", "skills"],
  },
  pi: {
    global: [".pi", "agent", "skills"],
    project: [".pi", "skills"],
  },
} satisfies Record<Harness, Record<"global" | "project", string[]>>;

const installScope = handleCancel(
  await select<"global" | "project">({
    message: "Which skill context do you want to use?",
    options: [
      {
        value: "global",
        label: "Globally",
        hint: path.join(os.homedir(), ...harnessPaths[harness].global),
      },
      {
        value: "project",
        label: "Inside a project folder",
        hint: path.join("<project>", ...harnessPaths[harness].project),
      },
    ],
  }),
);

let targetDir = path.join(os.homedir(), ...harnessPaths[harness].global);

if (installScope === "project") {
  const projectPath = handleCancel(
    await text({
      message: "Project folder path",
      placeholder: process.cwd(),
      validate(value) {
        if (!value?.trim()) {
          return "Enter a project folder path.";
        }

        return undefined;
      },
    }),
  );

  targetDir = path.join(
    path.resolve(expandHome(projectPath)),
    ...harnessPaths[harness].project,
  );
}

const installStates = new Map<string, InstallState>();

for (const skill of skills) {
  installStates.set(skill.dirName, await getInstallState(targetDir, skill));
}

const selectableSkills = skills.filter((skill) => {
  const state = getKnownInstallState(installStates, skill);
  return action === "install"
    ? state.status !== "installed"
    : state.status === "installed";
});

if (selectableSkills.length === 0) {
  const title = action === "install" ? "Nothing to install" : "Nothing to manage";
  const message =
    action === "install"
      ? `All available skills are already installed in ${targetDir}.`
      : `No managed skills are installed in ${targetDir}.`;

  note(message, title);
  process.exit(0);
}

const selectedSkills = handleCancel(
  await multiselect<string>({
    message:
      action === "install"
        ? `Select skills to install into ${targetDir}`
        : `Select installed skills to remove from ${targetDir}`,
    options: selectableSkills.map((skill) => {
      const state = getKnownInstallState(installStates, skill);
      const option = {
        value: skill.dirName,
        label: labelForSkill(skill, state),
      };

      if (state.status === "conflict") {
        return {
          ...option,
          hint: "will be skipped",
        };
      }

      return option;
    }),
    required: true,
  }),
);

const selected = selectableSkills.filter((skill) => selectedSkills.includes(skill.dirName));
const s = spinner();

s.start(action === "install" ? "Installing selected skills" : "Removing selected skills");

if (action === "install") {
  await fs.mkdir(targetDir, { recursive: true });
}

const results = [];

for (const skill of selected) {
  const state = getKnownInstallState(installStates, skill);
  results.push(
    action === "install"
      ? await installSkill(skill, state)
      : await removeSkill(skill, state),
  );
}

s.stop(action === "install" ? "Install complete" : "Removal complete");

note(
  results.map((result) => `${result.name}: ${result.status}`).join("\n"),
  targetDir,
);

outro("Done.");
