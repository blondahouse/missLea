// Pure gateway checks; no model notes or intents on public endpoints.
import { publicReceipt } from "../../agent_core/src/core.mjs";

export function canHandleScheduledWake(state, payload) {
  return state?.schema === 1 && state?.mode === "synthetic" &&
    state.status === "scheduled" && typeof payload?.runId === "string" &&
    payload.runId === state.runId && typeof payload.scheduledAt === "string" &&
    payload.scheduledAt === state.nextWakeAt;
}
export function safeStatus(state) {
  const receipt = publicReceipt(state);
  const events = Array.isArray(state.events) ? state.events : [];
  const recent = events.length ? events[events.length - 1] : null;
  return {
    ...receipt,
    lab: "synthetic-agent-core-v0",
    intentAssigned: typeof state.intent === "string" && state.intent.length > 0,
    lastTool: ["environment.inspect", "dataset.summarize"].includes(recent?.tool)
      ? recent.tool : null
  };
}
