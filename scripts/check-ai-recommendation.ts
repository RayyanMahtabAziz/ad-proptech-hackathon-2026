/**
 * Check AI recommendation layer for Al Ghadeer.
 *
 * Always validates deterministic fallback (must pass).
 * Tests OpenRouter when OPENROUTER_API_KEY is set.
 * Never prints API keys.
 *
 * Run: npm run check:ai
 */

import { existsSync, readFileSync } from "fs";
import { join, resolve } from "path";
import { fallbackRecommendation } from "../lib/fallbackRecommendation";
import {
  getServerEnvStatus,
  loadServerEnv,
} from "../lib/loadServerEnv";
import type { CommunityGapOutputs, DistrictRecommendation } from "../lib/communityGapTypes";

const ROOT = resolve(__dirname, "..");
const DATA_PATH = join(ROOT, "processed", "community_gap_outputs.json");
const DISTRICT_NAME = "Al Ghadeer";

const REQUIRED_KEYS: (keyof DistrictRecommendation)[] = [
  "district_summary",
  "main_gap",
  "recommended_intervention",
  "why_this_matters",
  "confidence_note",
  "uncertainty_note",
];

function validateOutput(rec: DistrictRecommendation, label: string): void {
  const missing = REQUIRED_KEYS.filter((k) => !(k in rec));
  if (missing.length > 0) {
    throw new Error(`${label}: missing keys: ${missing.join(", ")}`);
  }

  const empty = REQUIRED_KEYS.filter((k) => !rec[k]?.trim());
  if (empty.length > 0) {
    throw new Error(`${label}: empty fields: ${empty.join(", ")}`);
  }
}

function validateAlGhadeerWording(
  rec: DistrictRecommendation,
  label: string
): void {
  const summary = rec.district_summary.toLowerCase();
  if (!summary.includes("top priority in the current dataset")) {
    throw new Error(`${label}: missing top-priority wording for Al Ghadeer`);
  }
  if (summary.includes("high gap")) {
    throw new Error(`${label}: must not call Al Ghadeer a High gap`);
  }
  if (!summary.includes("medium")) {
    throw new Error(`${label}: should reflect gap_level Medium`);
  }
}

function printResult(rec: DistrictRecommendation, source: string): void {
  console.log(`\n=== ${DISTRICT_NAME} (${source}) ===`);
  console.log(JSON.stringify(rec, null, 2));
}

async function main(): Promise<number> {
  loadServerEnv();
  const envStatus = getServerEnvStatus();

  console.log("Env check:");
  console.log(`  project root: ${ROOT}`);
  console.log(
    `  env files found: ${envStatus.envFilesFound.length > 0 ? envStatus.envFilesFound.join(", ") : "(none)"}`
  );
  console.log(`  OPENROUTER_API_KEY loaded: ${envStatus.keyLoaded}`);
  console.log(`  OPENROUTER_MODEL: ${envStatus.model}`);

  const { generateRecommendation } = await import("../lib/aiRecommendation");

  if (!existsSync(DATA_PATH)) {
    console.error(`ERROR: missing ${DATA_PATH}`);
    return 1;
  }

  const payload = JSON.parse(
    readFileSync(DATA_PATH, "utf8")
  ) as CommunityGapOutputs;

  const district = payload.districts.find((d) => d.district === DISTRICT_NAME);
  if (!district) {
    console.error(`ERROR: district not found in JSON: ${DISTRICT_NAME}`);
    return 1;
  }

  console.log(`\nLoaded community_gap_outputs.json — checking ${DISTRICT_NAME}`);

  let fallbackPassed = false;
  let openRouterPassed = false;

  const fallbackRec = fallbackRecommendation(district);
  validateOutput(fallbackRec, "fallback");
  validateAlGhadeerWording(fallbackRec, "fallback");
  printResult(fallbackRec, "fallback");

  if (
    fallbackRec.recommended_intervention !==
    district.classification.recommended_intervention_category
  ) {
    throw new Error("fallback recommended_intervention does not match pipeline");
  }

  console.log("\nFallback check: PASSED");
  fallbackPassed = true;

  if (!envStatus.keyLoaded) {
    console.log(
      "\nOpenRouter check: SKIPPED (OPENROUTER_API_KEY not loaded — check .env in project root)"
    );
  } else {
    console.log("\nTesting OpenRouter path...");
    const { recommendation, source } = await generateRecommendation(district);
    validateOutput(recommendation, `openrouter (${source})`);
    validateAlGhadeerWording(recommendation, `openrouter (${source})`);
    printResult(recommendation, source);

    if (source === "llm") {
      console.log("\nOpenRouter check: PASSED (llm)");
      openRouterPassed = true;
    } else {
      console.error(
        "\nOpenRouter check: FAILED (key loaded but source was fallback — see server warnings above)"
      );
      return 1;
    }
  }

  console.log("\nSummary:");
  console.log(`  Fallback: ${fallbackPassed ? "PASSED" : "FAILED"}`);
  console.log(
    `  OpenRouter: ${openRouterPassed ? "PASSED" : envStatus.keyLoaded ? "FAILED" : "SKIPPED"}`
  );
  console.log("\nAll required checks passed.");
  return 0;
}

main()
  .then((code) => process.exit(code))
  .catch((err) => {
    console.error("CHECK FAILED:", err instanceof Error ? err.message : err);
    process.exit(1);
  });
