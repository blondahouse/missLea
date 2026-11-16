// Small, portable decision boundary. No provider SDK or credentials in this module.
export const MODEL = "@cf/google/gemma-4-26b-a4b-it";
export const MAX_WAKES = 2;

export function selectedAction(modelResponse, choices) {
  const text = String(modelResponse?.response ?? modelResponse?.choices?.[0]?.message?.content ?? "")
    .trim().replace(/^[\"'`]|[\"'`]$/g, "").trim().toUpperCase();
  return choices.includes(text) ? text : null;
}

export function syntheticTool(action, values) {
  if (action !== "SQUARES" || !Array.isArray(values) ||
      values.length !== 3 || values.some((v, i) => v !== [2, 3, 5][i])) {
    throw new Error("tool_not_allowed");
  }
  return {
    count: values.length,
    sum: values.reduce((total, v) => total + v, 0),
    squares: values.reduce((total, v) => total + v * v, 0)
  };
}

export function freshState(runId) {
  return {
    runId, status: "scheduled", wakes: 0, modelCalls: 0,
    events: [{type:"seed", decision:"Compute squared sum of 2, 3, and 5"}],
    nextAt: new Date(Date.now() + 15000).toISOString(),
    blockedReason: null
  };
}

export function publicReceipt(state) {
  return {
    experiment: "cloudflare-only-free-agent",
    model: MODEL,
    status: state?.status ?? "not_started",
    runId: state?.runId ?? null,
    wakes: state?.wakes ?? 0,
    modelCalls: state?.modelCalls ?? 0,
    nextAt: state?.nextAt ?? null,
    blockedReason: state?.blockedReason ?? null,
    events: (state?.events ?? []).map(event => ({
      type: event.type,
      action: event.action ?? null,
      result: event.result ?? null
    }))
  };
}
