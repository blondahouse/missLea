// Public status: never reveal model messages, personal content or D1 record IDs.
import {memoryReceipt} from "../../agent_core/src/memory_cycle.mjs";
const tools=new Set(["memory.remember","memory.recall","memory.revise",
  "memory.reinterpret","environment.inspect","dataset.summarize"]);
export function safeIntegratedStatus(state) {
  const base=memoryReceipt(state);
  const recent=Array.isArray(state.events)?state.events.at(-1):null;
  return {...base,lastTool:tools.has(recent?.tool)?recent.tool:null,
    callbackAttempts:Number.isSafeInteger(state.callbackAttempts)?state.callbackAttempts:0,
    callbackRejected:Number.isSafeInteger(state.callbackRejected)?state.callbackRejected:0,
    callbackRejectCode:["not_scheduled","payload_missing","run_id_missing",
      "stale_run","time_missing","time_mismatch"].includes(state.callbackRejectCode)
      ?state.callbackRejectCode:null};
}

export function canRestartUnarmedTrial(state,jobCount,alarmAt,now){
  return state?.schema===1 && state?.mode==="synthetic" &&
    state.status==="scheduled" && state.wakes===0 &&
    state.modelCalls===0 && jobCount===0 && alarmAt===null &&
    typeof state.nextWakeAt==="string" &&
    Number.isFinite(Date.parse(state.nextWakeAt)) &&
    Date.parse(state.nextWakeAt)<=now-60000;
}

export function scheduledCallbackRejection(state,payload){
  if(state?.schema!==1 || state?.mode!=="synthetic" ||
    state.status!=="scheduled")return "not_scheduled";
  if(!payload || typeof payload!=="object")return "payload_missing";
  if(typeof payload.runId!=="string")return "run_id_missing";
  if(payload.runId!==state.runId)return "stale_run";
  if(typeof payload.scheduledAt!=="string")return "time_missing";
  if(payload.scheduledAt!==state.nextWakeAt)return "time_mismatch";
  return null;
}
