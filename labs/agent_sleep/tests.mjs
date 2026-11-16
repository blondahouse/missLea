import test from "node:test";
import assert from "node:assert/strict";
import worker, {LabClock} from "./worker.mjs";
import {createExecutorHandler} from "./executor.mjs";

class Storage {
  constructor() { this.map = new Map(); this.alarmTime = null; }
  async get(k) { return structuredClone(this.map.get(k)); }
  async put(k,v) { this.map.set(k,structuredClone(v)); }
  async setAlarm(t) { this.alarmTime = t; }
}
const token = "z".repeat(40);
function request(path, method="GET", body) {
  return new Request(`https://lab.invalid${path}`,{
    method, headers:{authorization:`Bearer ${token}`,"content-type":"application/json"},
    ...(body ? {body:JSON.stringify(body)} : {})
  });
}
test("executor rejects unauthenticated and malformed tasks", async () => {
  const run = createExecutorHandler(token);
  const task = {
    job_id:"aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa:1",
    values:[2,3,5],prior_event_count:1
  };
  const publicHealth = await run(new Request("https://lab.invalid/health"));
  assert.deepEqual(await publicHealth.json(),{role:"synthetic_executor",status:"ready"});
  const good = await run(request("/compute","POST",task));
  assert.equal(good.status,200);
  assert.deepEqual(await good.json(),{
    count:3,sum:10,squares:38,prior_event_count:1
  });
  const anon = await run(new Request("https://lab.invalid/compute",{
    method:"POST",body:JSON.stringify(task)
  }));
  assert.equal(anon.status,401);
  const bad = await run(request("/compute","POST",{...task,values:[2,3,999]}));
  assert.equal(bad.status,400);
});
test("two bounded wakes preserve synthetic memory across restarted instance", async () => {
  const storage = new Storage();
  const env = {
    LAB_ADMIN_TOKEN:token,EXECUTOR_TOKEN:token,
    EXECUTOR_URL:"https://executor.invalid/",
    LAB_CLOCK:{idFromName:x=>x,get:()=>new LabClock({storage},env)}
  };
  const oldFetch = globalThis.fetch;
  globalThis.fetch = (url,options) =>
    createExecutorHandler(token)(new Request(url,options));
  try {
    assert.equal((await worker.fetch(
      new Request("https://lab.invalid/status"),env)).status,401);
    const control = await worker.fetch(new Request("https://lab.invalid/control"),env);
    assert.equal(control.status,200);
    const body = await control.text();
    assert.ok(body.includes('Запустить два пробуждения'));
    assert.ok(!body.includes(token));
    assert.equal((await worker.fetch(
      new Request("https://lab.invalid/health"),env)).status,200);
    assert.equal((await worker.fetch(
      request("/schedule","POST",{delay_seconds:5}),env)).status,202);
    assert.ok(storage.alarmTime);
    assert.equal((await worker.fetch(
      request("/schedule","POST",{delay_seconds:5}),env)).status,409);
    await new LabClock({storage},env).alarm();
    let state = await storage.get("lab");
    assert.equal(state.wakes,1);
    assert.equal(state.events.length,2);
    assert.equal(state.status,"scheduled");
    await new LabClock({storage},env).alarm();
    state = await storage.get("lab");
    assert.equal(state.wakes,2);
    assert.equal(state.events.length,3);
    assert.equal(state.status,"completed");
    assert.equal(state.next_at,null);
    const health = await worker.fetch(new Request("https://lab.invalid/health"),env);
    assert.deepEqual(await health.json(),{
      role:"wake_dispatcher",status:"completed",wakes:2,completed:true
    });
  } finally { globalThis.fetch = oldFetch; }
});
test("provider failures stop after one retry without switching to paid services", async () => {
  const storage = new Storage();
  const env = {EXECUTOR_URL:"https://executor.invalid/",EXECUTOR_TOKEN:token};
  const clock = new LabClock({storage},env);
  assert.equal((await clock.fetch(
    request("/schedule","POST",{delay_seconds:5}))).status,202);
  const oldFetch = globalThis.fetch;
  globalThis.fetch = async()=>new Response("unavailable",{status:503});
  try {
    await clock.alarm();
    assert.equal((await storage.get("lab")).status,"retrying");
    await new LabClock({storage},env).alarm();
    const state = await storage.get("lab");
    assert.equal(state.status,"blocked");
    assert.equal(state.wakes,0);
    assert.equal(state.next_at,null);
  } finally {globalThis.fetch=oldFetch;}
});
