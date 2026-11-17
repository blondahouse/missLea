import test from "node:test";
import assert from "node:assert/strict";
import {initialMemoryState} from "../../agent_core/src/memory_cycle.mjs";
import {safeIntegratedStatus} from "../src/integrated_support.mjs";
test("status contains only bounded counters and tool choice, never D1 IDs or content",()=>{
  const state={...initialMemoryState("test",Date.UTC(2026,10,17,16)),
    lastMemoryId:"private_memory_id",
    notes:["Confidential fabricated phrase"],
    events:[{tool:"memory.remember",observation:{saved:true,revision:1}}],
    memoryWrites:1,memoryReads:1,memoryContexts:1
  };
  const out=safeIntegratedStatus(state),text=JSON.stringify(out);
  assert.equal(out.memoryWrites,1);
  assert.equal(out.hasMemoryPointer,true);
  assert.equal(out.lastTool,"memory.remember");
  assert.equal(text.includes("private_memory_id"),false);
  assert.equal(text.includes("Confidential fabricated phrase"),false);
});
