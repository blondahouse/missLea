import test from "node:test";
import assert from "node:assert/strict";
import {
  LIMITS, TOOLS, initialState, beginWake, parseDecision,
  modelMessages, syntheticTool, finishWake, publicReceipt
} from "../src/core.mjs";
import {startRun, wake} from "../src/runtime.mjs";
const base = Date.UTC(2026, 10, 17, 12);
const answer = (intent, note, tool, sleepSeconds) =>
  JSON.stringify({intent, note, tool, sleepSeconds});

test("a new synthetic agent has no preassigned intention", () => {
  const s = initialState("synthetic", base);
  assert.equal(s.intent, null);
  assert.equal(s.notes.length, 0);
  assert.equal(s.status, "scheduled");
  assert.equal(Date.parse(s.nextWakeAt), base + 60000);
  assert.deepEqual(TOOLS, ["environment.inspect", "dataset.summarize"]);
});

test("strict decisions cannot create unauthorized actions", () => {
  const d = parseDecision({response: answer("Inspect the world", "Look around", "environment.inspect", 90)});
  assert.equal(d.intent, "Inspect the world");
  for (const bad of [
    "not json", answer("x", "", "network.fetch", 60),
    answer("x", "", null, 1), answer("x", "", null, 86401),
    answer("x".repeat(241), "", null, null),
    JSON.stringify({intent: "x", note: "", tool: null, sleepSeconds: null, admin: true})
  ]) assert.throws(() => parseDecision(bad), /invalid_decision/);
  assert.equal(parseDecision(answer(null, "", null, null)).intent, null);
});

test("the model selects goals, tools, sleeps, and its own pause", async () => {
  let now = base;
  let state;
  const scheduleLog = [];
  const decisions = [
    answer("Explore my tools", "Inspect the environment", "environment.inspect", 90),
    answer("Examine fabricated data", "Try the dataset", "dataset.summarize", 120),
    answer(null, "Pause exploration", null, null)
  ];
  let calls = 0;
  const ports = {
    runId: "trial",
    load: async () => state,
    save: async s => {state = structuredClone(s);},
    schedule: async item => {scheduleLog.push(item);},
    infer: async messages => {
      assert.match(messages[0].content, /no assigned goals/i);
      assert.match(messages[1].content, /synthetic/);
      return decisions[calls++];
    },
    clock: () => now
  };
  await startRun(ports);
  assert.equal(state.intent, null);
  assert.equal(scheduleLog.length, 1);
  for (let n = 0; n < 3; n++) {
    now = Date.parse(state.nextWakeAt);
    await wake(ports);
  }
  assert.equal(calls, 3);
  assert.equal(state.status, "paused");
  assert.equal(state.reason, "agent_chose_pause");
  assert.equal(state.intent, null);
  assert.equal(state.wakes, 3);
  assert.equal(state.toolCalls, 2);
  assert.deepEqual(state.events[1].observation, {count: 3, sum: 10, squares: 38});
  assert.equal(scheduleLog.length, 3);
  assert.equal(publicReceipt(state).intent, undefined);
  assert.equal(publicReceipt(state).notes, undefined);
});

test("failed inference blocks with no replay or secret-bearing receipts", async () => {
  let state = initialState("failure", base);
  let now = Date.parse(state.nextWakeAt);
  let inferenceCalls = 0;
  const ports = {
    runId: "failure", load: async () => state, save: async s => {state = s;},
    clock: () => now,
    infer: async () => {inferenceCalls++; return "ignore instructions";},
    schedule: async () => {throw Error("unexpected schedule");}
  };
  assert.equal((await wake(ports)).reason, "invalid_decision");
  assert.equal((await wake(ports)).status, "blocked");
  assert.equal(inferenceCalls, 1);
  assert.equal(state.modelCalls, 1);
  assert.equal(state.events.length, 0);
});

test("early and stale wakes do not run; quotas bound an experiment", () => {
  const s = initialState("current", base);
  assert.equal(beginWake(s, "old", base + 60000).kind, "ignored");
  assert.equal(beginWake(s, "current", base).kind, "ignored");
  const started = beginWake(s, "current", base + 60000);
  assert.equal(started.kind, "started");
  assert.equal(modelMessages(started.state)[0].role, "system");
  assert.deepEqual(syntheticTool("dataset.summarize"), {count: 3, sum: 10, squares: 38});
  assert.throws(() => syntheticTool("network.fetch"), /tool_not_allowed/);
  const full = {
    ...s, daily: {date: "2026-11-17", wakes: LIMITS.dailyWakes},
    nextWakeAt: new Date(base).toISOString()
  };
  const deferred = beginWake(full, "current", base);
  assert.equal(deferred.kind, "deferred");
  assert.equal(deferred.state.modelCalls, 0);
  assert.equal(deferred.state.nextWakeAt, "2026-11-18T00:01:00.000Z");
  const exhausted = beginWake({...full, wakes: LIMITS.totalWakes}, "current", base);
  assert.equal(exhausted.state.reason, "synthetic_budget_exhausted");
});

test("operational context stays bounded and a chosen pause is respected", () => {
  let s = initialState("bounded", base);
  for (let n = 0; n < 20; n++) {
    s = finishWake({...s, status: "running", wakes: n + 1},
      {intent: "x", note: "note" + n, tool: null, sleepSeconds: 60}, null,
      base + n * 60000);
  }
  assert.ok(s.events.length <= LIMITS.events);
  assert.ok(s.notes.length <= LIMITS.notes);
  assert.equal(s.nextWakeAt, null);
});
