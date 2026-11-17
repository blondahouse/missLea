import test from "node:test";
import assert from "node:assert/strict";
import app,{classifyD1Error} from "../src/cloudflare_smoke.mjs";
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
  for(const path of ["/trial/ready","/trial/remember","/trial/revise","/trial/verify"]) {
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

test("D1 error categories never disclose raw messages or record content",()=>{
  assert.equal(classifyD1Error(new Error("D1_ERROR: database disk image is malformed")), "index_integrity");
  assert.equal(classifyD1Error(new Error("D1_ERROR: no such table: living_memory")), "schema_missing");
  assert.equal(classifyD1Error(new Error("D1_ERROR: quota exceeded")), "resource_limit");
  assert.equal(classifyD1Error(new Error("D1_ERROR: private synthetic record")), "d1_query");
});
test("authenticated live trial returns a bounded failure stage without SQL text",async()=>{
  const env={
    LAB_ADMIN_TOKEN:token,
    MEMORY_DB:{prepare(sql){
      return {bind(){return {run:async()=>{throw Error("D1_ERROR: database disk image is malformed: private-data");}};}}
    }}
  };
  const r=await app.fetch(new Request(url+"/trial/remember",{method:"POST",
    headers:{authorization:"Bearer "+token}}),env);
  assert.equal(r.status,409);
  const data=await r.json();
  assert.deepEqual(data,{error:"memory_trial_failed",stage:"remember_write",category:"index_integrity"});
  assert.equal(JSON.stringify(data).includes("private-data"),false);
});

test("private readiness probe checks current start secret without writing memory",async()=>{
  const auth={LAB_ADMIN_TOKEN:token,MEMORY_DB:{prepare(){throw Error("unexpected database access");}}};
  const authorized=await app.fetch(new Request(url+"/trial/ready",{method:"POST",
    headers:{authorization:"Bearer "+token}}),auth);
  assert.equal(authorized.status,200);
  assert.deepEqual(await authorized.json(),{status:"authorized",databaseBound:true});
  const denied=await app.fetch(new Request(url+"/trial/ready",{method:"POST",
    headers:{authorization:"Bearer old-secret"}}),auth);
  assert.equal(denied.status,401);
});
