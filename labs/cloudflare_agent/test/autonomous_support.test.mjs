import test from "node:test";
import assert from "node:assert/strict";
import { initialState } from "../../agent_core/src/core.mjs";
import {canHandleScheduledWake, safeStatus} from "../src/autonomous_support.mjs";

const base = Date.UTC(2026, 10, 17, 17);
test("callback is tied to the exact run and planned timestamp", () => {
  const s = initialState("run-a", base);
  const valid = {runId: s.runId, scheduledAt: s.nextWakeAt};
  assert.equal(canHandleScheduledWake(s, valid), true);
  assert.equal(canHandleScheduledWake(s, {...valid, runId: "run-b"}), false);
  assert.equal(canHandleScheduledWake(s, {...valid, scheduledAt: new Date(base).toISOString()}), false);
  assert.equal(canHandleScheduledWake({...s, status: "running"}, valid), false);
});
test("public status includes only synthetic metadata", () => {
  const state = {
    ...initialState("run", base),
    intent: "private synthetic intention",
    notes: ["private synthetic thought"],
    events: [{at: new Date(base).toISOString(), tool: "dataset.summarize",
      observation: {count: 3, sum: 10, squares: 38}}],
    toolCalls: 1
  };
  const receipt = safeStatus(state);
  assert.equal(receipt.intentAssigned, true);
  assert.equal(receipt.lastTool, "dataset.summarize");
  assert.equal(JSON.stringify(receipt).includes("private synthetic"), false);
  assert.equal(JSON.stringify(receipt).includes("squares"), false);
});
