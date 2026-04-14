#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const manifest = JSON.parse(fs.readFileSync(path.join(repoRoot, "release-manifest.json"), "utf8"));

function parseArgs(argv) {
  const args = {
    profile: "base",
    appHome: process.env.SCIBUDY_HOME || process.env.RESEARCH_MCP_HOME || path.join(os.homedir(), ".research-mcp"),
    python: null,
    fromPath: null,
    upgrade: false,
    installCodex: true,
    noPrompt: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--profile") args.profile = argv[++i];
    else if (arg === "--app-home") args.appHome = argv[++i];
    else if (arg === "--python") args.python = argv[++i];
    else if (arg === "--from-path") args.fromPath = argv[++i];
    else if (arg === "--upgrade") args.upgrade = true;
    else if (arg === "--no-prompt") args.noPrompt = true;
    else if (arg === "--no-install-codex") args.installCodex = false;
  }
  return args;
}

function findPython(explicitPython) {
  const candidates = explicitPython ? [explicitPython] : ["python3", "python"];
  for (const candidate of candidates) {
    const result = spawnSync(candidate, ["--version"], { stdio: "ignore" });
    if (result.status === 0) return candidate;
  }
  throw new Error("Python 3.10+ is required but no python executable was found");
}

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    stdio: "inherit",
    env: { ...process.env, ...(options.env || {}) },
    cwd: options.cwd || process.cwd(),
  });
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed with exit code ${result.status}`);
  }
}

function syncUiAssets(appHome) {
  const sourceDist = path.join(repoRoot, "web", "dist");
  if (!fs.existsSync(path.join(sourceDist, "index.html"))) {
    return false;
  }
  const targetDist = path.join(appHome, "ui", "dist");
  fs.mkdirSync(path.dirname(targetDist), { recursive: true });
  fs.rmSync(targetDist, { recursive: true, force: true });
  fs.cpSync(sourceDist, targetDist, { recursive: true });
  return true;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const python = findPython(args.python);
  const runtimeVenv = path.join(args.appHome, "runtime", ".venv");
  const runtimePython = process.platform === "win32"
    ? path.join(runtimeVenv, "Scripts", "python.exe")
    : path.join(runtimeVenv, "bin", "python");

  fs.mkdirSync(path.dirname(runtimeVenv), { recursive: true });
  if (!fs.existsSync(runtimePython)) {
    run(python, ["-m", "venv", runtimeVenv], { env: { RESEARCH_MCP_HOME: args.appHome } });
  }

  run(runtimePython, ["-m", "pip", "install", "--upgrade", "pip"]);
  const requirement = args.fromPath
    ? path.resolve(args.fromPath)
    : `${manifest.python.package_name}==${manifest.python.version}`;
  const pipArgs = ["-m", "pip", "install"];
  if (args.upgrade) pipArgs.push("--upgrade");
  pipArgs.push(requirement);
  run(runtimePython, pipArgs);
  syncUiAssets(args.appHome);

  const cliModuleArgs = [
    "-m",
    "research_mcp.cli",
    "bootstrap",
    "--profile",
    args.profile,
    "--format",
    "table",
  ];
  if (args.installCodex) cliModuleArgs.push("--install-codex");
  else cliModuleArgs.push("--no-install-codex");
  if (args.noPrompt) cliModuleArgs.push("--no-prompt");

  run(runtimePython, cliModuleArgs, {
    env: {
      RESEARCH_MCP_HOME: args.appHome,
      SCIBUDY_HOME: args.appHome,
    },
  });
}

main();
