import { cp, mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";

await mkdir("dist", { recursive: true });
await cp("public", "dist/public", { recursive: true });

// Emit .js versions of the .ts files (MV3 service workers / content scripts
// don't run through a bundler in this minimal build, so we use the TS source
// as-is and rely on `chrome` globals). For real shipping you'd add esbuild.
async function emitJs(src, dest) {
  const text = await readFile(src, "utf8");
  // Strip the import of CSS and module specifiers we can't resolve at runtime
  const cleaned = text
    .replace(/^import\s+["'][^"']+\.css["'];?\s*$/gm, "")
    .replace(/^import\s+["'][^"']+["'];?\s*$/gm, "");
  await writeFile(dest, cleaned);
}

if (existsSync("src/background/service-worker.ts")) {
  await emitJs("src/background/service-worker.ts", "dist/src/background/service-worker.js");
}
if (existsSync("src/content/content-script.ts")) {
  await emitJs("src/content/content-script.ts", "dist/src/content/content-script.js");
}
if (existsSync("src/popup/popup.ts")) {
  await emitJs("src/popup/popup.ts", "dist/src/popup/popup.js");
}
if (existsSync("src/popup/debate.ts")) {
  await emitJs("src/popup/debate.ts", "dist/src/popup/debate.js");
}
if (existsSync("src/options/options.ts")) {
  await emitJs("src/options/options.ts", "dist/src/options/options.js");
}
if (existsSync("src/content/overlay.css")) {
  await cp("src/content/overlay.css", "dist/src/content/overlay.css");
}
if (existsSync("src/popup/popup.css")) {
  await cp("src/popup/popup.css", "dist/src/popup/popup.css");
}
if (existsSync("src/popup/popup.html")) {
  await cp("src/popup/popup.html", "dist/src/popup/popup.html");
}
if (existsSync("src/popup/debate.css")) {
  await cp("src/popup/debate.css", "dist/src/popup/debate.css");
}
if (existsSync("src/popup/debate.html")) {
  await cp("src/popup/debate.html", "dist/src/popup/debate.html");
}
if (existsSync("src/options/options.html")) {
  await cp("src/options/options.html", "dist/src/options/options.html");
}

// Patch manifest.json to point at the emitted .js
const manifest = JSON.parse(await readFile("manifest.json", "utf8"));
if (manifest.background?.service_worker?.endsWith(".ts")) {
  manifest.background.service_worker = manifest.background.service_worker.replace(/\.ts$/, ".js");
  manifest.background.type = "module";
}
for (const cs of manifest.content_scripts ?? []) {
  for (let i = 0; i < (cs.js ?? []).length; i++) {
    if (cs.js[i].endsWith(".ts")) cs.js[i] = cs.js[i].replace(/\.ts$/, ".js");
  }
}
for (const cs of manifest.content_scripts ?? []) {
  if (cs.css) {
    cs.css = cs.css.map((p) => p);
  }
}
await writeFile("dist/manifest.json", JSON.stringify(manifest, null, 2));
console.log("extension built -> dist/ (manifest + assets + .js shims)");
