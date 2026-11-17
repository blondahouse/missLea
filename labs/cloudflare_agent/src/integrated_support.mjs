// Public status: never reveal model messages, personal content or D1 record IDs.
import {memoryReceipt} from "../../agent_core/src/memory_cycle.mjs";
const tools=new Set(["memory.remember","memory.recall","memory.revise",
  "memory.reinterpret","environment.inspect","dataset.summarize"]);
export function safeIntegratedStatus(state) {
  const base=memoryReceipt(state);
  const recent=Array.isArray(state.events)?state.events.at(-1):null;
  return {...base,lastTool:tools.has(recent?.tool)?recent.tool:null};
}
