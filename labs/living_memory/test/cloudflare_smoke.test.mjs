import test from "node:test";
import assert from "node:assert/strict";
import app from "../src/cloudflare_smoke.mjs";
const url="https://example.invalid";
const token="synthetic-only-".repeat(3);
test("public endpoints never reveal memory contents",async()=>{
  const r=await app.fetch(new Request(url+"/status"),{});
  assert.equal(r.status,200);
  const data=await r.json();
  assert.equal(data.containsPersonalData,false);
  assert.equal(JSON.stringify(data).includes("cobalt"),false);
});
test("unauthenticated mutation is rejected before database access",async()=>{
  for(const path of ["/trial/remember","/trial/revise","/trial/verify"]) {
    const r=await app.fetch(new Request(url+path,{method:"POST"}),{
      LAB_ADMIN_TOKEN:token});
    assert.equal(r.status,401);
  }
});
test("authorized requests fail closed without dedicated D1 binding",async()=>{
  const r=await app.fetch(new Request(url+"/trial/remember",{
    method:"POST",headers:{authorization:"Bearer "+token}}),{
    LAB_ADMIN_TOKEN:token});
  assert.equal(r.status,503);
});
