import test from "node:test";
import assert from "node:assert/strict";
import {initialMemoryState} from "../../agent_core/src/memory_cycle.mjs";
import {safeIntegratedStatus,canRestartUnarmedTrial} from "../src/integrated_support.mjs";
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

test("only an overdue unarmed zero-wake trial may be restarted",()=>{
  const now=Date.UTC(2026,10,17,17);
  const base={...initialMemoryState("stale",Date.UTC(2026,10,17,16)),
    status:"scheduled"};
  assert.equal(canRestartUnarmedTrial(base,0,null,now),true);
  assert.equal(canRestartUnarmedTrial({...base,wakes:1},0,null,now),false);
  assert.equal(canRestartUnarmedTrial(base,1,null,now),false);
  assert.equal(canRestartUnarmedTrial(base,0,Date.now(),now),false);
  assert.equal(canRestartUnarmedTrial({...base,status:"running"},0,null,now),false);
  assert.equal(canRestartUnarmedTrial(base,0,null,Date.UTC(2026,10,17,16)),false);
});
