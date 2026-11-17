import test from "node:test";
import assert from "node:assert/strict";
import {initialMemoryState} from "../../agent_core/src/memory_cycle.mjs";
import {safeIntegratedStatus,canRestartUnarmedTrial,scheduledCallbackRejection} from "../src/integrated_support.mjs";
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

test("scheduled callback rejection categories reveal no payload content",()=>{
  const at=Date.UTC(2026,10,17,17);
  const state=initialMemoryState("run",at);
  assert.equal(scheduledCallbackRejection(state,{runId:"run",scheduledAt:state.nextWakeAt}),null);
  assert.equal(scheduledCallbackRejection(state,null),"payload_missing");
  assert.equal(scheduledCallbackRejection(state,{scheduledAt:state.nextWakeAt}),"run_id_missing");
  assert.equal(scheduledCallbackRejection(state,{runId:"other",scheduledAt:state.nextWakeAt}),"stale_run");
  assert.equal(scheduledCallbackRejection(state,{runId:"run",scheduledAt:"other"}),"time_mismatch");
  const receipt=safeIntegratedStatus({...state,callbackAttempts:2,callbackRejected:1,
    callbackRejectCode:"time_mismatch",secret:"do-not-print"});
  assert.equal(receipt.callbackAttempts,2);
  assert.equal(receipt.callbackRejectCode,"time_mismatch");
  assert.equal(JSON.stringify(receipt).includes("do-not-print"),false);
});

test("safe callback failure phase is retained but arbitrary error text is not",()=>{
  const s=initialMemoryState("fail",Date.UTC(2026,10,17,16));
  const safe=safeIntegratedStatus({...s,status:"blocked",
    callbackFailurePhase:"memory_port"});
  assert.equal(safe.callbackFailurePhase,"memory_port");
  const unsafe=safeIntegratedStatus({...s,callbackFailurePhase:"SQL_ERROR private data"});
  assert.equal(unsafe.callbackFailurePhase,null);
  assert.equal(JSON.stringify(unsafe).includes("SQL_ERROR"),false);
});
