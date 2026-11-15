import test from "node:test";
import assert from "node:assert/strict";
import worker from "../manual_worker/worker.mjs";

const URL = "https://lab.example.test/run";
const SECRET = "a".repeat(48);
const env = { MISSLEA_TASK_SECRET: SECRET };

function request(payload = { task: "sum_squares", values: [2, 3, 5] },
                 token = SECRET, extra = {}) {
  return new Request(URL, {
    method: "POST",
    headers: { "authorization": "Bearer " + token,
               "content-type": "application/json",
               ...extra.headers },
    body: typeof payload === "string" ? payload : JSON.stringify(payload),
  });
}

test("public health endpoint contains no secret", async () => {
  const reply = await worker.fetch(new Request("https://lab.example.test/health"), env);
  assert.equal(reply.status, 200);
  const output = await reply.text();
  assert.equal(JSON.parse(output).status, "ready");
  assert.ok(!output.includes(SECRET));
});

test("authorized synthetic task returns deterministic result", async () => {
  const reply = await worker.fetch(request(), env);
  assert.equal(reply.status, 200);
  assert.deepEqual((await reply.json()).result, {count: 3, sum: 10, squares: 38});
  assert.equal(reply.headers.get("cache-control"), "no-store");
});

test("missing secret on Worker disables execution even with bearer header", async () => {
  const reply = await worker.fetch(request(), {});
  assert.equal(reply.status, 503);
});

test("missing and incorrect bearer secret are denied", async () => {
  for (const token of ["b".repeat(48), "x", ""]) {
    const reply = await worker.fetch(request(undefined, token), env);
    assert.equal(reply.status, 401);
    const text = await reply.text();
    assert.ok(!text.includes(SECRET));
  }
});

test("only a single supported task is accepted", async () => {
  for (const payload of [
    {task: "eval", values: [2, 3, 5]},
    {task: "sum_squares", values: [2], shell: "rm -rf /"},
    {task: "sum_squares", values: []},
    {task: "sum_squares", values: ["4", 1]},
    {task: "sum_squares", values: [1001]},
    {task: "sum_squares", values: Array(17).fill(1)},
    null,
  ]) {
    const reply = await worker.fetch(request(payload), env);
    assert.equal(reply.status, 400);
  }
});

test("malformed and oversized JSON rejected", async () => {
  let reply = await worker.fetch(request("bad-json"), env);
  assert.equal(reply.status, 400);
  reply = await worker.fetch(request(JSON.stringify({
    task: "sum_squares", values: [1], padding: "x".repeat(1000)
  })), env);
  assert.equal(reply.status, 413);
});

test("wrong method, path and content type are rejected", async () => {
  const get = await worker.fetch(new Request(URL), env);
  assert.equal(get.status, 405);
  const wrongPath = await worker.fetch(new Request("https://lab.example.test/admin"), env);
  assert.equal(wrongPath.status, 404);
  const wrongType = await worker.fetch(request(undefined, SECRET,
                              {headers: {"content-type": "text/plain"}}), env);
  assert.equal(wrongType.status, 415);
});

test("secret is never returned in successful response or headers", async () => {
  const reply = await worker.fetch(request(), env);
  assert.ok(!(await reply.text()).includes(SECRET));
  assert.ok(![...reply.headers.values()].some(v => v.includes(SECRET)));
});
