import { cp, mkdir } from "node:fs/promises";
await mkdir("dist", { recursive: true });
await cp("public", "dist/public", { recursive: true });
await cp("src", "dist/src", { recursive: true });
await cp("manifest.json", "dist/manifest.json");
console.log("extension built -> dist/");
