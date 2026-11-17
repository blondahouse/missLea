import assert from "node:assert/strict";
import {metadata,categories,statuses,nodes,edges} from "./data.mjs";
import {readFileSync} from "node:fs";

const ids=new Set(nodes.map(n=>n.id));
const cats=new Set(categories.map(c=>c.id));
const state=new Set(statuses.map(s=>s.id));
assert.equal(ids.size,nodes.length,"duplicate node ids");
assert.equal(cats.size,4,"four broad domains");
assert.ok(nodes.length>=30);
assert.ok(edges.length>=35);
for(const n of nodes){
 assert.ok(n.id && n.title && n.provider && n.detail && n.source,n.id);
 assert.ok(cats.has(n.stage),n.id+" category");
 assert.ok(state.has(n.status),n.id+" status");
 assert.ok(["internal","external","hybrid","policy"].includes(n.owner),n.id+" owner");
 assert.ok(n.source.startsWith("https://github.com/"),n.id+" source");
}
for(const e of edges){
 assert.ok(ids.has(e.from)&&ids.has(e.to),JSON.stringify(e));
 assert.ok(e.label);
}
assert.equal(metadata.asOf,"2026-11-17");
assert.equal(nodes.find(n=>n.id==="agent-sdk").status,"verified");
assert.equal(nodes.find(n=>n.id==="infisical-root").status,"verified");
assert.equal(nodes.find(n=>n.id==="restore").status,"verified");
const html=readFileSync(new URL("./index.html",import.meta.url),"utf8");
const js=readFileSync(new URL("./app.mjs",import.meta.url),"utf8");
const css=readFileSync(new URL("./style.css",import.meta.url),"utf8");
assert.ok(html.includes('src="./app.mjs"'));
assert.ok(html.includes('href="./style.css"'));
assert.ok(js.includes('new Map(nodes.map'));
assert.ok(css.includes(".graphViewport"));
const memoryHtml=readFileSync(new URL("./memory/index.html",import.meta.url),"utf8");
const memoryDecision=readFileSync(new URL("../docs/memory-concept.md",import.meta.url),"utf8");
const memoryPlan=readFileSync(new URL("../docs/memory-cloudflare-roadmap.md",import.meta.url),"utf8");
assert.ok(memoryHtml.includes('lang="en"'));
assert.ok(memoryHtml.includes('id="exposure"'));
assert.ok(memoryHtml.includes("Unified Living Memory"));
assert.ok(memoryDecision.includes("Adopted primary memory concept"));
assert.ok(memoryPlan.includes("Cloudflare first"));
const pageSources=[html,js,memoryHtml,readFileSync(new URL("./data.mjs",import.meta.url),"utf8")];
for(const src of pageSources) assert.ok(!/[\u0400-\u04FF]/u.test(src),"site must contain English-only content");
console.log("PASS:",nodes.length,"nodes,",edges.length,"evidence-linked edges,",categories.length,"domains");
