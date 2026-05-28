#!/usr/bin/env node

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

function handleCancel(value) {
  if (isCancel(value)) {
    cancel("Installation cancelled.");
    process.exit(0);
  }

  return value;
}

function expandHome(inputPath) {
  if (inputPath === "~") {
    return os.homedir();
  }

  if (inputPath.startsWith("~/")) {
    return path.join(os.homedir(), inputPath.slice(2));
  }

  return inputPath;
}

async function exists(targetPath) {
  try {
    await fs.access(targetPath, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function readSkillName(skillDir) {
  const skillPath = path.join(skillsRoot, skillDir, "SKILL.md");
  const content = await fs.readFile(skillPath, "utf8");
  const nameMatch = content.match(/^name:\s*(.+)$/m);
  return nameMatch?.[1]?.trim() || skillDir;
}

async function discoverSkills() {
  const entries = await fs.readdir(skillsRoot, { withFileTypes: true });
  const skillDirs = [];

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

async function getInstallState(targetDir, skill) {
  const targetPath = path.join(targetDir, skill.dirName);

  try {
    const stat = await fs.lstat(targetPath);

    if (!stat.isSymbolicLink()) {
      return { status: "conflict", targetPath };
    }

    let realTarget;
    let realSource;

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
    if (error.code === "ENOENT") {
      return { status: "missing", targetPath };
    }

    throw error;
  }
}

function labelForSkill(skill, state) {
  if (state.status === "installed") {
    return `${skill.name} (installed)`;
  }

  if (state.status === "conflict") {
    return `${skill.name} (exists)`;
  }

  return skill.name;
}

async function installSkill(skill, state) {
  if (state.status === "installed") {
    return { name: skill.name, status: "already installed" };
  }

  if (state.status === "conflict") {
    return { name: skill.name, status: "skipped: target already exists" };
  }

  await fs.symlink(skill.sourcePath, state.targetPath, "dir");
  return { name: skill.name, status: "installed" };
}

intro("Install agent skills");

const skills = await discoverSkills();

if (skills.length === 0) {
  note(`No skills found in ${skillsRoot}.`, "Nothing to install");
  process.exit(0);
}

const installScope = handleCancel(
  await select({
    message: "Where do you want to install skills?",
    options: [
      {
        value: "global",
        label: "Globally",
        hint: path.join(os.homedir(), ".codex", "skills"),
      },
      {
        value: "project",
        label: "Inside a project folder",
        hint: "<project>/.codex/skills",
      },
    ],
  }),
);

let targetDir = path.join(os.homedir(), ".codex", "skills");

if (installScope === "project") {
  const projectPath = handleCancel(
    await text({
      message: "Project folder path",
      placeholder: process.cwd(),
      validate(value) {
        if (!value.trim()) {
          return "Enter a project folder path.";
        }
      },
    }),
  );

  targetDir = path.join(path.resolve(expandHome(projectPath)), ".codex", "skills");
}

const installStates = new Map();

for (const skill of skills) {
  installStates.set(skill.dirName, await getInstallState(targetDir, skill));
}

const selectedSkills = handleCancel(
  await multiselect({
    message: `Select skills to install into ${targetDir}`,
    options: skills.map((skill) => {
      const state = installStates.get(skill.dirName);

      return {
        value: skill.dirName,
        label: labelForSkill(skill, state),
        hint: state.status === "conflict" ? "will be skipped" : undefined,
      };
    }),
    required: true,
  }),
);

const selected = skills.filter((skill) => selectedSkills.includes(skill.dirName));
const s = spinner();

s.start("Installing selected skills");
await fs.mkdir(targetDir, { recursive: true });

const results = [];

for (const skill of selected) {
  const state = installStates.get(skill.dirName);
  results.push(await installSkill(skill, state));
}

s.stop("Install complete");

note(
  results.map((result) => `${result.name}: ${result.status}`).join("\n"),
  targetDir,
);

outro("Done.");
