/**
 * Datask JS/TS SDK — Basic examples.
 * Run: DATASK_API_KEY=dtsk_live_... npx tsx examples/js_basic.ts
 */
import { DataskClient } from "../packages/sdk-js/src/index";

async function main() {
  const client = new DataskClient();

  // Layer 1: Fetch
  console.log("=== Fetch ===");
  const content = await client.fetch("https://example.com");
  console.log(content.slice(0, 500));

  // Layer 2: Extract with schema
  console.log("\n=== Extract (Layer 2) ===");
  const data = await client.extract("https://example.com", {
    schema: { title: "string", description: "string" },
  });
  console.log(data);

  // Layer 3: Natural language (requires OPENAI_API_KEY on server)
  // console.log("\n=== Extract (Layer 3) ===");
  // const nlData = await client.extract("https://example.com", {
  //   prompt: "Extract the main heading and description",
  // });
  // console.log(nlData);
}

main().catch(console.error);
