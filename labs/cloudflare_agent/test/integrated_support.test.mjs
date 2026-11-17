import test from "node:test";
import assert from "node:assert/strict";
import {initialMemoryState} from "../../agent_core/src/memory_cycle.mjs";
import {safeIntegratedStatus,canRestartUnarmedTrial,canStartFreshTrial,scheduledCallbackRejection} from "../src/integrated_support.mjs";
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

test("safe status classifies invalid decisions without revealing model content",()=>{
  const state={...initialMemoryState("format",Date.UTC(2026,10,18,0)),
    status:"blocked",reason:"invalid_decision",modelCalls:2,
    decisionRepairs:1,lastDecisionValidationCode:"invalid_json",
    secret:"secret-from-inference",notes:["private note"]};
  const receipt=safeIntegratedStatus(state),serialized=JSON.stringify(receipt);
  assert.equal(receipt.decisionRepairs,1);
  assert.equal(receipt.lastDecisionValidationCode,"invalid_json");
  assert.equal(serialized.includes("secret-from-inference"),false);
  assert.equal(serialized.includes("private note"),false);
  assert.equal(safeIntegratedStatus({...state,
    decisionRepairs:999,lastDecisionValidationCode:"exception database password"})
    .lastDecisionValidationCode,null);
  assert.equal(safeIntegratedStatus({...state,decisionRepairs:999}).decisionRepairs,0);
});

test("fresh start cannot reset blocked or paused runs, or bypass pending alarms",()=>{
  const state=initialMemoryState("preserve",Date.UTC(2026,10,18,0));
  const initial={...state,status:"not_started",wakes:0,modelCalls:0};
  assert.equal(canStartFreshTrial(initial,0,null,Date.UTC(2026,10,18,1)),true);
  assert.equal(canStartFreshTrial(initial,1,null,Date.UTC(2026,10,18,1)),false);
  assert.equal(canStartFreshTrial(initial,0,Date.now(),Date.UTC(2026,10,18,1)),false);
  for(const status of ["blocked","paused","running"]){
    assert.equal(canStartFreshTrial({...state,status,wakes:4,modelCalls:4},0,null,
      Date.UTC(2026,10,18,1)),false);
  }
});
test("resume status contains only bounded counts and safe timestamps",()=>{
  const state={...initialMemoryState("resume",Date.UTC(2026,10,18,0)),
    status:"scheduled",resumeCount:1,lastResumeAt:"2026-11-18T00:10:00.000Z",
    lastMemoryId:"private_memory_id",notes:["redacted secret"]};
  const out=safeIntegratedStatus(state);
  assert.equal(out.resumeCount,1);
  assert.equal(out.lastResumeAt,"2026-11-18T00:10:00.000Z");
  assert.equal(JSON.stringify(out).includes("private_memory_id"),false);
  assert.equal(JSON.stringify(out).includes("redacted secret"),false);
  const bad=safeIntegratedStatus({...state,resumeCount:100,
    lastResumeAt:"cannot parse secret"});
  assert.equal(bad.resumeCount,0);
  assert.equal(bad.lastResumeAt,null);
});
