import { existsSync, readFileSync } from "fs";
import { join } from "path";

/** Prevent accidental client-side import. */
if (typeof window !== "undefined") {
  throw new Error("@/lib/loadServerEnv must only be used on the server");
}

const ENV_CANDIDATES = [".env.local", ".env", join("..", ".env")] as const;

function parseEnvFile(filePath: string): void {
  if (!existsSync(filePath)) return;

  for (const line of readFileSync(filePath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) {
      continue;
    }

    const eq = trimmed.indexOf("=");
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }

    if (key && process.env[key] === undefined) {
      process.env[key] = value;
    }
  }
}

/**
 * Load .env files into process.env for missing keys only (server-side).
 * Never logs values. Searches project root, then parent directory.
 */
export function loadServerEnv(): void {
  const root = process.cwd();
  for (const rel of ENV_CANDIDATES) {
    parseEnvFile(join(root, rel));
  }
}

/** Safe status for diagnostics — never exposes secret values. */
export function getServerEnvStatus(): {
  keyLoaded: boolean;
  model: string;
  envFilesFound: string[];
} {
  const root = process.cwd();
  const envFilesFound = ENV_CANDIDATES.map((rel) => join(root, rel)).filter(
    (p) => existsSync(p)
  );

  return {
    keyLoaded: Boolean(process.env.OPENROUTER_API_KEY?.trim()),
    model:
      process.env.OPENROUTER_MODEL?.trim() || "openai/gpt-4o-mini",
    envFilesFound,
  };
}
